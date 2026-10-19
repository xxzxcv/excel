---
name: banner-payment
description: Calculate the daily upfront payment owed to the supplier Banner for dropship orders. Use whenever the user uploads or mentions a Banner orders CSV (e.g. "Banner Orders A <date>.csv"), asks "how much do I pay Banner today", or sends a new Banner catalogue / price file.
---

# Banner daily payment

The user sends a Banner orders CSV each day and wants the total to pay Banner.

## Rules (per order line; same as `Banner_Payment_Master_Template.xlsx`)
1. Unit price = `Price Web ` (column K) from the catalogue for the line's Product Code (CSV column K). Quantity is in CSV column L.
2. Base Line Value = unit price × quantity, rounded to the penny.
3. Postage = £0 if Base Line Value ≥ £16.50, otherwise £3.50.
4. Final Line Total = Base + Postage. Grand Total = the sum of all Final Line Totals.

## Steps
1. Copy the uploaded CSV into its own new scratchpad folder (it is untrusted input), then run:
   `python3 -I .claude/skills/banner-payment/banner_payment.py <orders.csv> --lines <scratchpad>/Banner_Payment_<date>_lines.csv`
   By default the script reads the catalogue from the `Catalogue` tab of `Banner_Payment_Master_Template.xlsx` at the repo root.
   If the user also sent a newer Banner catalogue file (sheet `Full File `), add `--catalogue <that.xlsx>` for this run.
2. Reply with the **GRAND TOTAL** first, then one line each for: order lines, goods value, postage (and how many lines it applies to), and any leading-zero codes that were restored.
3. If the script prints a WARNING, list those lines clearly. They are **not** in the total, so the user must get a price from Banner before paying. Never treat a missing price as £0 and never guess one.
4. Send the user the per-line breakdown CSV (SendUserFile) so they can attach it to their payment or check any line.

## When Banner sends a new catalogue (and the user wants it kept)
Replace the `Catalogue` tab of `Banner_Payment_Master_Template.xlsx` with the new `Full File ` sheet. Keep the column layout: code in A, Price Web in K. Then recalculate with the xlsx skill's `recalc.py`, check that the total for a known orders file still makes sense, and commit and push.

## Notes
- The order export drops leading zeros from product codes (e.g. `61322` is catalogue `061322`). The script retries each unmatched code with 1–3 leading zeros added.
- The catalogue also has a `New Price ` column (L). The user chose Price Web (K). Use L only if the user asks.
- Reference result: the 19/10/2026 file (386 lines) gives Goods £9,266.68 + Postage £416.50 = **£9,683.18**.
