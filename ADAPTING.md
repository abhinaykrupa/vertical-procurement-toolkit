# Adapting this toolkit to your vertical

The bundled example is **dental supply** (Benco, Henry Schein, Darby, Base86, Patterson). The same engine works for any fragmented-supplier vertical — vet, HVAC, restaurant, auto repair, independent pharmacy, salon supply, agricultural inputs, anything.

This guide walks you through adapting it to a new vertical. Total time: **30–60 minutes** for a basic working version, more for production polish.

---

## What you need before you start

1. **A reference catalog** — your "negotiated prices" file. CSV format with at minimum: SKU, description, manufacturer (optional), unit price, pack/UOM (optional but recommended).
2. **A sample export** from at least one supplier in your vertical. This is what users will upload to be analyzed against your catalog.
3. **Working knowledge of your industry's SKU conventions** — manufacturer prefixes, common pack sizes, typical UOM vocabulary ("box", "case", "tube", "gallon", "drum", "each", etc.).

---

## Step 1 — Swap the catalog

Replace `sample_data/sourceclub_catalog.csv` with your vertical's catalog. Match the column structure:

```csv
sc_sku,description,manufacturer,unit_price,pack_size,uom
CAT-001,"Nitrile Gloves, Medium, Powder-Free",Microflex,6.10,100,box
...
```

Required columns:
- `sc_sku` — your catalog's internal SKU (rename `sc_` prefix if you want, but the engine looks for `sc_sku` by default)
- `description` — human-readable product name
- `unit_price` — your negotiated price
- `manufacturer` — optional but boosts match accuracy
- `pack_size` + `uom` — optional; without these, UOM checks are skipped

Save it under `sample_data/<your-catalog>.csv` and update the path in [`app/main.py`](./app/main.py) where the catalog loads.

---

## Step 2 — Add a supplier adapter

Adapters live in [`app/engine/adapters/`](./app/engine/adapters/). Each adapter parses one supplier's export format into the canonical schema:

| Canonical field | Type | Required |
|---|---|---|
| `supplier_sku` | string | ✅ |
| `raw_description` | string | ✅ |
| `manufacturer_name` | string | recommended |
| `manufacturer_sku` | string | recommended |
| `quantity` | number | ✅ |
| `unit_price` | number | ✅ |
| `annual_spend` | number | computed if missing |
| `supplier_name` | string | ✅ |
| `customer_name` | string | ✅ |
| `report_period` | string | ✅ |

Use [`app/engine/adapters/benco.py`](./app/engine/adapters/benco.py) as your template — it's ~40 lines.

### Minimal adapter template

Create `app/engine/adapters/<your_supplier>.py`:

```python
import pandas as pd
import io

COLUMN_MAP = {
    # Their column name → canonical name
    "Their SKU Column": "supplier_sku",
    "Their Description Column": "raw_description",
    "Their Mfr Column": "manufacturer_name",
    "Their Mfr SKU Column": "manufacturer_sku",
    "Their Qty Column": "quantity",
    "Their Unit Price Column": "unit_price",
    "Their Extended Price Column": "annual_spend",
}

def parse(file_bytes: bytes, filename: str) -> pd.DataFrame:
    raw = pd.read_csv(io.BytesIO(file_bytes), skiprows=0)  # adjust skiprows for header rows
    raw = raw.dropna(subset=["Their SKU Column"])
    raw = raw.rename(columns=COLUMN_MAP)
    raw["supplier_name"] = "<Your Supplier Name>"
    raw["customer_name"] = "<extract from file or hardcode>"
    raw["report_period"] = "<extract or hardcode>"
    keep = list(COLUMN_MAP.values()) + ["supplier_name", "customer_name", "report_period"]
    raw = raw[[c for c in keep if c in raw.columns]]
    # numeric cleanup — strip $, commas, etc.
    raw["unit_price"] = pd.to_numeric(
        raw["unit_price"].astype(str).str.replace("$", "").str.replace(",", "").str.strip(),
        errors="coerce"
    ).fillna(0)
    return raw.reset_index(drop=True)
```

### Real-world export chaos

Real supplier exports are messy. Look at [`app/engine/adapters/patterson.py`](./app/engine/adapters/patterson.py) for an example of handling:

- `$`-prefixed prices
- Embedded commas in numbers
- Blank rows / footer rows
- Mixed UOM formats
- Header rows that aren't column headers

That adapter is the showcase — it strips all of it.

---

## Step 3 — Register your adapter

Update [`app/engine/adapters/auto_detect.py`](./app/engine/adapters/auto_detect.py) to recognize your supplier from filename or file content:

```python
if "yoursupplier" in filename_lower:
    return "YourSupplier"
```

And wire the new adapter into the dispatch logic in [`app/main.py`](./app/main.py) (search for where existing adapters are imported and routed).

---

## Step 4 — Tweak the UOM normalizer

UOM/pack-size detection is the hardest problem in vertical procurement. The bundled regex tables in [`app/engine/matcher.py`](./app/engine/matcher.py) are dental-flavored — they understand "box", "case", "tube", "carton", "syringe", etc.

For your vertical, you'll likely need to add domain vocabulary. Examples:

- **HVAC:** "lb" (refrigerant), "gallon", "drum", "pallet", "linear ft" (ductwork), "EA" (each)
- **Restaurant:** "lb", "oz", "case", "gallon", "#10 can", "5-gal pail", "bushel"
- **Vet:** similar to dental but add "ml", "L", "dose", "vial", "100-tab bottle"
- **Auto:** "qt", "gallon", "drum", "pallet", "EA", "set", "kit"

Search [`app/engine/matcher.py`](./app/engine/matcher.py) for the UOM aliases dictionary and the pack-size regex patterns. Add your vertical's vocabulary.

---

## Step 5 — Update the UI (light touch)

In [`app/main.py`](./app/main.py):

- Update page title and any vertical-specific copy
- Update the sample-file dropdown to point at your new test files
- Adjust dashboard labels ("practices" → "shops" / "clinics" / "contractors" / etc.)

The dashboard logic itself is generic. Most edits are string swaps.

---

## Step 6 — Test it

1. `streamlit run app/main.py`
2. Pick your new sample file from the dropdown
3. Watch the 3-stage pipeline run
4. Inspect the matches, the review queue, and the no-match bucket
5. Iterate on the UOM regex and adapter logic until match rate looks reasonable

**Target match rates** (rough heuristic):
- ≥85% auto-accept when the prospect's file has clean manufacturer SKUs
- 60–80% auto-accept when SKUs are absent and matching relies on description + UOM
- The review queue catches the rest — that's the spec, not a bug

---

## Where the engine generalizes well — and where it doesn't

### Generalizes well
- Any vertical where small businesses buy from 3+ distributors
- Any vertical where the same physical product has different SKUs/descriptions across distributors
- Any vertical where pack-size/UOM differences create matching pain
- Any vertical where the savings analysis is itself a sales artifact (showing the prospect their savings)

### Doesn't generalize well
- Verticals where SKUs are already standardized (NDC for pharma, UPC for retail) — Stage 1 deterministic match is too easy, no AI needed
- Verticals where the product catalog changes per-customer (custom manufacturing, build-to-order)
- Verticals dominated by long-term contracts where price comparison happens at RFP time, not invoice time
- Verticals where one distributor dominates (≥80% share) — no comparison to do

---

## Examples worth contributing

Highest-value adapters to add (open issues if you want a starter task):

| Vertical | Top suppliers to adapt | Estimated time |
|---|---|---|
| Vet | Patterson Vet, Covetrus, MWI, Henry Schein Vet | 4–6 hours per adapter |
| HVAC | Ferguson, Carrier, Trane, Lennox, R.E. Michel | 4–6 hours per adapter |
| Restaurant | Sysco, US Foods, PFG, Restaurant Depot | 4–6 hours per adapter |
| Auto repair | NAPA, AutoZone Commercial, O'Reilly Pro, WorldPac | 4–6 hours per adapter |
| Independent pharmacy | McKesson, Cardinal, Cencora (AmerisourceBergen) | 4–6 hours per adapter |
| Optometry | VSP, Essilor, Hoya, Marchon | 4–6 hours per adapter |

See [CONTRIBUTING.md](./CONTRIBUTING.md) for the contribution process.

---

## Questions / stuck?

Open a [GitHub issue](https://github.com/abhinaykrupa/vertical-procurement-toolkit/issues) with:
- Your vertical
- A redacted sample of the supplier export (column structure)
- What's not working

The maintainers and community will help.
