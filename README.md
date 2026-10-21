# Banner Dropship – Daily Supplier Payment Master Template

`Banner_Payment_Master_Template.xlsx` is ready to use. It already contains Banner's catalogue and the
sample orders for 19/10/2026, so you can see it working straight away.

**Sample result for 19/10/2026: 386 order lines → Goods £9,266.68 + Postage £416.50 (119 lines) = Grand Total £9,683.18** (at the prices before 21/10/2026)

**Price update 21/10/2026:** Banner's "Sim Price Increases - October 26" file is applied. For the 42,726 codes it lists, Price Web is now Banner's New Price (+20%), rounded to the penny. It also added 4,835 codes that were only in that file. Catalogue column N keeps the previous price and column O notes the change. The same 19/10 orders at the new prices come to **£11,530.29** (Goods £11,250.29 + Postage £280.00 on 80 lines).

---

## 1. Daily routine

1. **Orders** tab → click the select-all square (top-left of the grid) → press **Delete**.
2. Open today's Banner CSV in Excel → **Ctrl+A**, **Ctrl+C**.
3. Click **Orders!A1** → **Ctrl+V**. Headers go in row 1 and orders start in row 2.
4. **Summary!C18** shows the **Grand Total**. Check that **Summary!C19** says *All lines priced*.
5. (Optional) Use *File → Save As* to keep a dated copy, e.g. `Banner Payment 2026-10-19.xlsx`.

Always clear the Orders tab first (step 1). If you skip it, yesterday's extra rows stay on the
sheet whenever today's file is shorter.

---

## 2. Workbook structure

| Tab | Purpose | You edit it? |
|---|---|---|
| **Summary** | Settings (yellow cells) and results, including the Grand Total | Only the yellow cells |
| **Orders** | Paste area for the daily CSV, using the CSV's own layout (Product Code = **K**, Quantity = **L**) | Yes – paste daily |
| **Calculations** | One formula row per order line. Rows 2–5001 cover up to 5,000 lines a day | No |
| **Catalogue** | Copy of Banner's `Full File ` sheet (Product Code = **A**, Price Web = **K**) | Only when Banner sends a new price file |
| **How To Use** | The instructions above, kept inside the workbook | No |

### Summary tab settings (yellow input cells)

| Cell | Value | Meaning |
|---|---|---|
| C5 | 19/10/2026 | Order date (for your records only) |
| C6 | 16.50 | Free-postage threshold (£) |
| C7 | 3.50 | Postage fee per line (£) |

---

## 3. The exact formulas

### Calculations tab (row 2 shown; copied down to row 5001)

| Col | Header | Formula in row 2 |
|---|---|---|
| A | Order Number | `=IF(Orders!$K2="","",Orders!$A2)` |
| B | Product Code | `=IF(Orders!$K2="","",TRIM(Orders!$K2&""))` |
| C | Quantity | `=IF(B2="","",IFERROR(Orders!$L2*1,"?"))` |
| D | Catalogue Row | `=IF(B2="","",IFERROR(MATCH(B2,Catalogue!$A:$A,0),IFERROR(MATCH("0"&B2,Catalogue!$A:$A,0),IFERROR(MATCH("00"&B2,Catalogue!$A:$A,0),IFERROR(MATCH("000"&B2,Catalogue!$A:$A,0),"")))))` |
| E | Description | `=IF(D2="","",INDEX(Catalogue!$B:$B,D2))` |
| F | **Unit Price** (step 1) | `=IF(D2="","",INDEX(Catalogue!$K:$K,D2))` |
| G | **Base Line Value** (step 2) | `=IF(J2<>"OK","",ROUND(F2*C2,2))` |
| H | **Postage** (step 3) | `=IF(G2="","",IF(G2>=Summary!$C$6,0,Summary!$C$7))` |
| I | **Final Line Total** (step 4) | `=IF(G2="","",G2+H2)` |
| J | Status | `=IF(B2="","",IF(D2="","CODE NOT IN CATALOGUE",IF(NOT(ISNUMBER(C2)),"CHECK QUANTITY",IF(C2<=0,"CHECK QUANTITY","OK"))))` |

### Summary tab results

| Cell | Label | Formula |
|---|---|---|
| C10 | Order lines in today's file | `=COUNTIF(Calculations!$J$2:$J$5001,"?*")` |
| C11 | Lines priced OK | `=COUNTIF(Calculations!$J$2:$J$5001,"OK")` |
| C12 | Lines NOT priced | `=COUNTIF(Calculations!$J$2:$J$5001,"<>OK")-COUNTBLANK(Calculations!$J$2:$J$5001)` |
| C13 | Total items | `=SUM(Calculations!$C$2:$C$5001)` |
| C14 | Goods value | `=SUM(Calculations!$G$2:$G$5001)` |
| C15 | Lines charged postage | `=COUNTIF(Calculations!$H$2:$H$5001,">0")` |
| C16 | Postage total | `=SUM(Calculations!$H$2:$H$5001)` |
| **C18** | **GRAND TOTAL** (step 5) | `=SUM(Calculations!$I$2:$I$5001)` |
| C19 | Check | Shows *All lines priced*, or a red WARNING if a line can't be priced or more than 5,000 lines were pasted |

---

## 4. Design notes and why

- **Dynamic row count.** The Calculations formulas are pre-filled for 5,000 rows. A row only
  calculates when Orders column K holds a product code; otherwise it returns blank and the SUMs ignore
  it. Pasting 50 lines or 3,000 lines needs no changes to the formulas.
- **Leading zeros are restored automatically.** Banner's order export drops leading zeros from product
  codes. In the sample file, `61322` is catalogue code `061322`, and `738650`, `614897` and
  `749803` are `0738650`, `0614897` and `0749803`. Six of the 386 sample lines are affected.
  Column D first looks for the code exactly as given. If that fails, it tries again with 1, 2 and then
  3 leading zeros added. I checked the whole catalogue: no padded code can match two different
  products.
- **Number vs text codes.** Excel turns codes like `1109550` into numbers when it opens a CSV, but the
  catalogue stores every code as text. `&""` in column B converts the code back to text so the lookup
  matches.
- **Missing products are never silently £0.** If a code isn't in the catalogue, the line is marked
  `CODE NOT IN CATALOGUE` (red), left out of the total, and Summary!C19 shows a warning. You then add
  the product to the bottom of the Catalogue tab or confirm the price with Banner.
- **Rounding.** Base Line Value is rounded to the penny before the £16.50 test, so floating-point
  noise can't make a line that is exactly £16.50 pay postage.
- **Postage is per line**, as specified. Two separate lines on the same order are each tested
  against £16.50 on their own.

---

## 5. Maintenance

- **New catalogue from Banner:** clear the Catalogue tab, then copy the whole `Full File ` sheet from the
  new file and paste it into Catalogue!A1. Codes must stay in column A and Price Web in column K.
  Note that the current catalogue also has a **"New Price "** column (L), which is filled in for about
  300 products. The template uses **Price Web (K)**, as requested. If Banner bills at the new price,
  change `Catalogue!$K:$K` in Calculations column F to `Catalogue!$L:$L`, or tell me and I'll add a
  "use New Price when present" rule.
- **More than 5,000 lines a day:** select Calculations row 5001 and fill it down further. Then change
  `5001` in the Summary formulas to the new last row.
- **Google Sheets / LibreOffice:** every formula uses only standard functions (INDEX, MATCH, IFERROR,
  COUNTIF, SUM), so the template works unchanged in both.

---

## Repricer cost update (Banner/Sim price files)

`.claude/skills/repricer-cost-update/repricer_cost_update.py` turns a Banner/Sim price-increase file into a repricer
upload. New cost = round(New Price ex VAT × pack quantity × 1.20, 2). Only SKUs Sellerboard labels `#BANNER` are
updated, and `#InHouse` SKUs are never touched. Anything uncertain goes to the **Review** sheet of
`Supplier_Price_Analysis.xlsx` instead of the upload. See the skill's `SKILL.md` for the SKU formats it accepts.
