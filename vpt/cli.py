"""
CLI for the Vertical Procurement Toolkit.

Usage:
    vpt analyze --supplier-file invoice.csv --catalog catalog.csv [--output results.json]
    vpt adapters                          # list available adapters
    vpt detect --supplier-file file.csv   # detect supplier from filename + content
    vpt --version

Examples:
    # Run a savings analysis end-to-end, output JSON to stdout
    vpt analyze -s sample_data/auburn_dental_benco.csv -c sample_data/dental_catalog.csv

    # Use a specific adapter (skip auto-detect)
    vpt analyze -s invoice.csv -c catalog.csv --adapter Benco

    # Use the generic adapter with explicit column mapping
    vpt analyze -s invoice.csv -c catalog.csv --adapter generic \\
        --map sku=ItemNum description=ProductName unit_price=Price quantity=Qty
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__, load_catalog, get_adapter, ADAPTERS, auto_detect, match_invoice


def cmd_analyze(args: argparse.Namespace) -> int:
    supplier_path = Path(args.supplier_file)
    if not supplier_path.exists():
        print(f"error: supplier file not found: {supplier_path}", file=sys.stderr)
        return 2

    catalog_path = Path(args.catalog)
    if not catalog_path.exists():
        print(f"error: catalog file not found: {catalog_path}", file=sys.stderr)
        return 2

    file_bytes = supplier_path.read_bytes()
    filename = supplier_path.name

    # Adapter selection
    if args.adapter == "auto":
        adapter_name = auto_detect.detect(file_bytes, filename)
        if adapter_name == "Unknown":
            print(
                "error: could not auto-detect supplier. "
                "Use --adapter <name> or --adapter generic with --map column overrides.",
                file=sys.stderr,
            )
            return 3
    else:
        adapter_name = args.adapter

    if args.verbose:
        print(f"using adapter: {adapter_name}", file=sys.stderr)

    # Load the right UOM vocabulary for this vertical (auto from adapter, or --vertical override)
    vertical = args.vertical
    if vertical is None:
        from engine.adapters import ADAPTER_VERTICAL
        vertical = ADAPTER_VERTICAL.get(adapter_name)
    if vertical:
        try:
            from .uom import apply_to_engine
            apply_to_engine(vertical)
            if args.verbose:
                print(f"loaded UOM table: {vertical}", file=sys.stderr)
        except FileNotFoundError:
            if args.verbose:
                print(f"no UOM table for vertical {vertical!r}, using defaults", file=sys.stderr)

    # Parse
    if adapter_name == "generic":
        from .generic_adapter import parse_generic
        col_map = _parse_kv_list(args.map or [])
        invoice_df = parse_generic(file_bytes, filename, column_map=col_map)
    else:
        adapter = get_adapter(adapter_name)
        invoice_df = adapter(file_bytes, filename)

    if args.verbose:
        print(f"parsed {len(invoice_df)} line items", file=sys.stderr)

    # Catalog
    catalog = load_catalog(catalog_path)

    # Match
    results_df = match_invoice(invoice_df, catalog)

    # Summary
    summary = {
        "input_file": str(supplier_path),
        "adapter": adapter_name,
        "catalog_file": str(catalog_path),
        "total_lines": int(len(results_df)),
        "auto_accept": int((results_df["status"] == "AUTO-ACCEPT").sum()),
        "review_suggested": int((results_df["status"] == "REVIEW-SUGGESTED").sum()),
        "force_review": int((results_df["status"] == "FORCE-REVIEW").sum()),
        "no_match": int((results_df["status"] == "NO-MATCH").sum()),
        "total_annual_spend": float(results_df["annual_spend"].sum()),
        "total_savings": float(results_df["total_savings"].fillna(0).sum()),
    }

    output = {
        "summary": summary,
        "line_items": results_df.to_dict(orient="records"),
    }

    out_json = json.dumps(output, default=str, indent=2 if args.pretty else None)

    if args.output:
        Path(args.output).write_text(out_json)
        print(f"wrote {args.output}", file=sys.stderr)
    else:
        print(out_json)

    return 0


def cmd_adapters(args: argparse.Namespace) -> int:
    print("Available adapters:")
    for name in sorted(ADAPTERS.keys()):
        print(f"  - {name}")
    print("  - generic  (provide --map column overrides)")
    return 0


def cmd_compare(args: argparse.Namespace) -> int:
    """Compare prices for the same items across multiple supplier files."""
    from .compare import compare_suppliers, comparison_summary

    catalog_path = Path(args.catalog)
    if not catalog_path.exists():
        print(f"error: catalog file not found: {catalog_path}", file=sys.stderr)
        return 2

    supplier_files = []
    for sf in args.supplier_files:
        p = Path(sf)
        if not p.exists():
            print(f"error: supplier file not found: {p}", file=sys.stderr)
            return 2
        file_bytes = p.read_bytes()
        adapter_name = auto_detect.detect(file_bytes, p.name)
        if adapter_name == "Unknown":
            print(f"error: could not auto-detect supplier for {p.name}", file=sys.stderr)
            return 3
        supplier_files.append((adapter_name, file_bytes, p.name))

    catalog = load_catalog(catalog_path)
    comparison = compare_suppliers(supplier_files, catalog)

    if comparison.empty:
        print("No overlapping items found across the supplied files.", file=sys.stderr)
        return 0

    summary = comparison_summary(comparison)

    if args.json:
        output = {"summary": summary, "items": comparison.to_dict(orient="records")}
        print(json.dumps(output, default=str, indent=2 if args.pretty else None))
    else:
        print(f"Compared {summary['items_compared']} items across {len(supplier_files)} suppliers.")
        print(f"Items carried by >1 supplier: {summary['multi_supplier_items']}")
        print(f"Total potential savings (always buy cheapest): ${summary['total_potential_savings']:,.2f}")
        if summary.get("biggest_spread_item"):
            print(f"Biggest price spread: {summary['biggest_spread_item']} (${summary['biggest_spread']:,.2f})")
        print()
        cols = ["sc_description", "cheapest_supplier", "cheapest_price", "price_spread", "suppliers_carrying"]
        print(comparison[cols].head(args.top).to_string(index=False))

    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    """Validate a catalog CSV: required columns, numeric prices, no duplicate SKUs."""
    import pandas as pd

    catalog_path = Path(args.catalog)
    if not catalog_path.exists():
        print(f"error: catalog file not found: {catalog_path}", file=sys.stderr)
        return 2

    try:
        df = pd.read_csv(catalog_path)
    except Exception as e:
        print(f"FAIL: could not read CSV: {e}", file=sys.stderr)
        return 1

    problems: list[str] = []
    warnings: list[str] = []

    required = ["sc_sku", "description", "unit_price"]
    recommended = ["manufacturer", "mfg_sku", "unit_of_measure", "pack_size"]

    for col in required:
        if col not in df.columns:
            problems.append(f"missing required column: {col!r}")

    for col in recommended:
        if col not in df.columns:
            warnings.append(f"missing recommended column: {col!r} (matching quality will be lower)")

    if "sc_sku" in df.columns:
        dupes = df["sc_sku"][df["sc_sku"].duplicated()].unique()
        if len(dupes):
            problems.append(f"{len(dupes)} duplicate sc_sku value(s): {list(dupes)[:5]}")
        n_blank = df["sc_sku"].isna().sum()
        if n_blank:
            problems.append(f"{n_blank} row(s) with blank sc_sku")

    if "unit_price" in df.columns:
        prices = pd.to_numeric(
            df["unit_price"].astype(str).str.replace("$", "", regex=False).str.replace(",", "", regex=False),
            errors="coerce",
        )
        n_bad = prices.isna().sum()
        if n_bad:
            problems.append(f"{n_bad} row(s) with non-numeric unit_price")
        n_zero = (prices == 0).sum()
        if n_zero:
            warnings.append(f"{n_zero} row(s) with unit_price == 0")

    print(f"Catalog: {catalog_path}")
    print(f"Rows: {len(df)}  Columns: {len(df.columns)}")
    for w in warnings:
        print(f"  WARN  {w}")
    for p in problems:
        print(f"  FAIL  {p}")

    if problems:
        print(f"\n{len(problems)} problem(s) found.", file=sys.stderr)
        return 1
    print("\nOK — catalog is valid." + (f" ({len(warnings)} warning(s))" if warnings else ""))
    return 0


def cmd_detect(args: argparse.Namespace) -> int:
    supplier_path = Path(args.supplier_file)
    if not supplier_path.exists():
        print(f"error: file not found: {supplier_path}", file=sys.stderr)
        return 2
    detected = auto_detect.detect(supplier_path.read_bytes(), supplier_path.name)
    print(detected)
    return 0


def _parse_kv_list(kvs: list[str]) -> dict[str, str]:
    """Parse ['supplier_sku=ItemNum', 'raw_description=Name'] into a dict."""
    out = {}
    for kv in kvs:
        if "=" not in kv:
            raise SystemExit(f"--map entries must be key=value, got: {kv}")
        k, v = kv.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="vpt",
        description="Vertical Procurement Toolkit — supplier-invoice savings analysis.",
    )
    parser.add_argument("--version", action="version", version=f"vpt {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    # analyze
    p_an = sub.add_parser("analyze", help="Run a savings analysis on a supplier file")
    p_an.add_argument("-s", "--supplier-file", required=True, help="Path to supplier CSV/export")
    p_an.add_argument("-c", "--catalog", required=True, help="Path to reference catalog CSV")
    p_an.add_argument(
        "-a", "--adapter",
        default="auto",
        help="Adapter name (default: auto-detect). Use 'generic' for column-mapped CSVs.",
    )
    p_an.add_argument(
        "-m", "--map",
        nargs="+",
        metavar="K=V",
        help="Column mapping for generic adapter, e.g. supplier_sku=ItemNum raw_description=Name",
    )
    p_an.add_argument(
        "--vertical",
        default=None,
        help="UOM vocabulary to load (dental/vet/hvac/restaurant). Default: inferred from adapter.",
    )
    p_an.add_argument("-o", "--output", help="Write JSON to file instead of stdout")
    p_an.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    p_an.add_argument("-v", "--verbose", action="store_true", help="Verbose logs to stderr")
    p_an.set_defaults(func=cmd_analyze)

    # adapters
    p_ad = sub.add_parser("adapters", help="List available adapters")
    p_ad.set_defaults(func=cmd_adapters)

    # detect
    p_dt = sub.add_parser("detect", help="Auto-detect the supplier of a file")
    p_dt.add_argument("-s", "--supplier-file", required=True)
    p_dt.set_defaults(func=cmd_detect)

    # validate
    p_va = sub.add_parser("validate", help="Validate a catalog CSV")
    p_va.add_argument("-c", "--catalog", required=True, help="Path to catalog CSV to validate")
    p_va.set_defaults(func=cmd_validate)

    # compare
    p_cmp = sub.add_parser("compare", help="Compare prices for the same items across multiple supplier files")
    p_cmp.add_argument("-s", "--supplier-files", required=True, nargs="+", help="Two or more supplier files")
    p_cmp.add_argument("-c", "--catalog", required=True, help="Reference catalog CSV")
    p_cmp.add_argument("--json", action="store_true", help="Output JSON instead of a table")
    p_cmp.add_argument("--pretty", action="store_true", help="Pretty-print JSON (with --json)")
    p_cmp.add_argument("--top", type=int, default=20, help="Rows to show in table output (default 20)")
    p_cmp.set_defaults(func=cmd_compare)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
