---
name: repricer-cost-update
description: Update Amazon repricer unit costs from a Banner/Sim price-increase file. Use when the user sends a repricer SKU export (e.g. "repricer amazon skus.csv") together with a Banner/Sim price file and wants new costs for the repricer upload.
---

# Repricer cost update (Banner/Sim)

## Inputs
1. Repricer export CSV (columns `sku`, `merchant_id`, `unit_cost`, ...).
2. Banner/Sim price-increase xlsx (`Product Code`, `Product Description`, `Price `, `New Price `), prices ex VAT.
3. Sellerboard SKU export xlsx (`SKU`, `Labels`). `#BANNER` = dropship from Banner, `#InHouse` = our warehouse stock.

## Rules
- New cost = round(New Price ex VAT x pack quantity, 2), rounded half-up to the penny. Costs stay **ex VAT**: the
  repricer applies VAT itself through its `vat_rate` column (user decision 21/10/2026).
- Only rows Sellerboard labels `#BANNER` are updated. `#InHouse` rows are never touched, even when their SKU
  contains a Banner code (e.g. `9150014-`, `896-9872`, `CHP412 8x`).
- Exact supplier codes match first, so real codes that end in X (`05994X`, `12801X`) are not read as multipacks.
- All-digit codes may have lost 1-3 leading zeros (`73024` -> `0073024`); two possible matches go to Review.
- Multipacks: `N x CODE`, `NX CODE`, `N Boxes CODE`, `CODE NX`, `CODE N BOXES`, with optional `Prime` / `Non Prime`
  and trailing `.`, `-`, `_` listing-variant marks.
- Review (not uploaded): a code match where the SKU is not in Sellerboard or has conflicting labels, a SKU with a code
  plus other words (`Q-Connect BOX 9150016`), or a current cost outside 0.40x-2.50x of old supplier price x pack
  quantity (usually a wrong pack size or a special buy price).

## Steps
1. Copy the uploads into a new scratchpad folder (untrusted input), then run:
   `python3 -I .claude/skills/repricer-cost-update/repricer_cost_update.py <repricer.csv> <sim.xlsx> <sellerboard.xlsx> --out <scratchpad>/out`
   Add `--approve-review` once the user has approved the Review rows. It uploads them too (pack quantity 1 for an
   unrecognised SKU format), except rows whose Banner price is far below the current cost (e.g. £0.03 loan
   dispensers), which stay in Review.
2. Send the user `Repricer_Upload_Updated_Costs.csv` (UPDATE rows only, original columns and order, only
   `unit_cost` changed) and `Supplier_Price_Analysis.xlsx` (Summary, Updated, Review, In-House Skipped,
   Banner Not Updated, All SKUs).
3. Report the status counts and anything in Review that needs a decision.

## Notes
- The October 2026 Sim file's New Price is exactly Price x 1.2 for every code. The user confirmed this is Banner's
  flat 20% increase and both columns are ex VAT.
- `--vat 0.20` would add VAT to costs; do not use it unless the user changes the repricer VAT setup. `--catalogue` (default: the master template) only labels Banner SKUs that have
  no increase listed.

## Loss check on a fresh repricer export (`loss_fix.py`)
Use when the user sends a full repricer export (15 columns incl. `shipping_cost`, `vat_rate`) and reports losses:
`python3 -I .claude/skills/repricer-cost-update/loss_fix.py <export.csv> <sim.xlsx> <sellerboard.xlsx> Banner_Payment_Master_Template.xlsx <outdir> [taxcat.csv ...]`
- Writes `Repricer_Upload_1_SKUs_Starting_With_0.csv`, `Repricer_Upload_2_All_Other_Banner_SKUs.csv` (only rows that
  change; raw lines kept so leading zeros and quoting survive) and `Fix_Audit_All_SKUs.csv`.
- £3.50 shipping is added when Banner's line value is under £16.50 and is never removed in this pass.
- VAT 0 becomes 20 unless the Amazon tax category says otherwise. Get categories from Sellerboard `products`
  (ASIN batches of 35) into CSVs with columns `sku,vat_category`. In Oct 2026 every SKU starting with 0 was
  `A_GEN_STANDARD`; tea, coffee, milk, sugar and cereal were `A_FOOD_TEA` (kept at 0).
- Banner codes not in the Sim file: cost = max(current, Price Web + 20%). The user's own export already carried the
  +20% on 361 of these.
- 22/10/2026 finding: losses came from £0 shipping on items under £16.50 and VAT 0 on standard-rated items, not
  from wrong costs. The user uploads the CSV without opening it in Excel (Excel strips leading zeros).

## Assigning a repricer rule (`rule_assign.py`)
For a Repricer "essentials" export (`sku,...,price_min,price_max,repricer_name,sales_rule`):
`python3 -I .claude/skills/repricer-cost-update/rule_assign.py <essentials.csv> <Fix_Audit_All_SKUs.csv> <out.csv> "<rule name>"`
- "No rule" shows as `Off` in `repricer_name` (never blank). Only Banner rows with `Off` are written.
- Banner/in-house comes from the latest `loss_fix.py` audit; in-house, non-Banner and £0-cost Banner rows are left out
  (a £0 cost would let the rule's automatic min price go to £0).
- Listings without a rule have `price_min`/`price_max` = 0; the repricer fills them in once a rule is assigned.
- The rule already used for Banner is named `Lowest Price for SIM Banner ` (with a trailing space).
