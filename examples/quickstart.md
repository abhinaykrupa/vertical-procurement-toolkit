# Quickstart — your first savings analysis in 60 seconds

Three ways to run the same analysis. Pick the one that fits your workflow.

## 1. CLI (fastest)

```bash
git clone https://github.com/abhinaykrupa/vertical-procurement-toolkit
cd vertical-procurement-toolkit
pip install pandas PyYAML

# Vet vertical (Vetcove sample, 30 lines, multi-distributor)
python -m vpt.cli analyze \
  -s sample_data/sample_clinic_vetcove.csv \
  -c sample_data/vet_catalog.csv \
  --pretty
```

You should see something like:

```json
{
  "summary": {
    "input_file": "sample_data/sample_clinic_vetcove.csv",
    "adapter": "Vetcove",
    "catalog_file": "sample_data/vet_catalog.csv",
    "total_lines": 30,
    "auto_accept": 30,
    "review_suggested": 0,
    "force_review": 0,
    "no_match": 0,
    "total_annual_spend": 14168.5,
    "total_savings": 1868.0
  },
  "line_items": [
    {
      "customer_name": "Riverside Animal Hospital",
      "supplier_sku": "PV-12891",
      "raw_description": "Canine DAPP Vaccine 25-Dose",
      "sc_sku": "VG-VAC-DAPP-25",
      "current_unit_price": 98.5,
      "sc_unit_price": 89.0,
      "unit_savings": 9.5,
      "total_savings": 76.0,
      "savings_pct": 9.6,
      "status": "AUTO-ACCEPT",
      "match_method": "Deterministic",
      "confidence": 1.0
    },
    ...
  ]
}
```

## 2. Python API

```python
from vpt import match_invoice, load_catalog, get_adapter

# Load reference catalog
catalog = load_catalog("sample_data/vet_catalog.csv")

# Parse the supplier export with the right adapter
parse = get_adapter("Vetcove")
with open("sample_data/sample_clinic_vetcove.csv", "rb") as f:
    invoice = parse(f.read(), "vetcove.csv")

# Run the 3-stage matcher
results = match_invoice(invoice, catalog)

# Look at savings
print(results[["sc_sku", "raw_description", "status", "confidence", "total_savings"]].head(10))

# Total annual savings
print(f"Total: ${results['total_savings'].fillna(0).sum():,.0f}")
```

## 3. Generic adapter — any CSV, no per-supplier code needed

```python
from vpt.generic_adapter import parse_generic, suggest_column_map
from vpt import match_invoice, load_catalog

with open("mystery_supplier.csv", "rb") as f:
    file_bytes = f.read()

# Heuristic column suggestion — useful for interactive workflows
suggestions = suggest_column_map(file_bytes, "mystery.csv")
print(suggestions)
# {'supplier_sku': ['ItemNumber'], 'raw_description': ['ProductName'], ...}

# Provide the column mapping explicitly
column_map = {
    "supplier_sku": "ItemNumber",
    "raw_description": "ProductName",
    "manufacturer_name": "Brand",
    "quantity": "Quantity",
    "unit_price": "Price",
    "annual_spend": "ExtendedTotal",
}

invoice = parse_generic(
    file_bytes, "mystery.csv",
    column_map=column_map,
    supplier_name="MysteryVendor",
    customer_name="Acme Co",
)

catalog = load_catalog("sample_data/vet_catalog.csv")
results = match_invoice(invoice, catalog)
```

## Real LLM Stage 3 (optional)

By default the matcher uses a rule-based mock for Stage 3 so the demo runs offline. To use real Claude or GPT:

```bash
export LLM_JUDGE_PROVIDER=anthropic   # or 'openai'
export ANTHROPIC_API_KEY=sk-ant-...
```

Then in code:

```python
from vpt.llm_judge import judge_with_llm
import engine.matcher

# Replace the mock with the real LLM
engine.matcher.stage3_llm_judge = judge_with_llm
```

The real judge falls back to the mock when no API key is present, so you can ship this in production code without breaking offline development.

## Switching verticals

```python
from vpt.uom import apply_to_engine, list_available

print(list_available())  # ['dental', 'hvac', 'restaurant', 'vet']

apply_to_engine("vet")
# Now the matcher uses vet UOM vocabulary (ml, dose, vial, tab, etc.)
```

## Next steps

- **Adapting to your vertical?** Read [ADAPTING.md](../ADAPTING.md)
- **Contributing?** Read [CONTRIBUTING.md](../CONTRIBUTING.md)
- **Production deployment?** Read [PRODUCTION_ARCHITECTURE.md](../PRODUCTION_ARCHITECTURE.md)
- **Security posture?** Read [SECURITY.md](../SECURITY.md) and [SECURITY_REVIEW.md](../SECURITY_REVIEW.md)
