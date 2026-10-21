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
