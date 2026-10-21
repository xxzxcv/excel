#!/usr/bin/env python3
"""Update Amazon repricer unit costs from a Banner/Sim price-increase file.

Rules:
  new cost = round(Supplier New Price ex VAT * pack multiplier * (1 + VAT), 2)   (half-up, to the penny)
  VAT defaults to 0: the repricer applies VAT itself through its vat_rate column, so costs stay ex VAT.
  Only rows Sellerboard labels '#BANNER' are updated. '#InHouse' rows are never touched, even when their
  SKU contains a Banner code. Anything uncertain goes to the Review sheet instead of the upload file.

SKU grammar accepted for an automatic update (case-insensitive, after dropping trailing . - _ and spaces):
  CODE                          exact supplier code (all-digit codes may have lost 1-3 leading zeros)
  CODE [PRIME|NON PRIME]        listing variants of the same single item
  N x CODE / NX CODE / N BOXES CODE / NX BOXES CODE      multipack prefix
  CODE NX / CODE N BOXES / CODE PRIME NX / CODE NX PRIME  multipack suffix

Usage: repricer_cost_update.py REPRICER.csv SIM.xlsx SELLERBOARD.xlsx --out DIR
         [--catalogue Banner_Payment_Master_Template.xlsx] [--vat 0] [--approve-review]
"""
import argparse, os, re, sys
from decimal import Decimal, ROUND_HALF_UP
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CATALOGUE = os.path.normpath(os.path.join(HERE, "..", "..", "..", "Banner_Payment_Master_Template.xlsx"))
PENNY = Decimal("0.01")

MULT = r"(\d{1,3})\s*(?:X\s*(?:BOXES|BOX)?|BOXES|BOX)"
PREFIX = re.compile(rf"^{MULT}\s*[-_]?\s*(?P<rest>.+)$")
SUFFIX = re.compile(rf"^(?P<rest>.+?)\s*[-_ ]\s*{MULT}$")
VARIANT = re.compile(r"\s+(?:NON\s+PRIME|PRIME)$")
# Current cost vs (old supplier price x multiplier) outside this band suggests a wrong pack size
SANITY = (0.40, 2.50)


def money(x):
    return Decimal(str(x)).quantize(PENNY, rounding=ROUND_HALF_UP)


def load_sim(path):
    df = pd.read_excel(path, dtype=str)
    df.columns = [c.strip() for c in df.columns]
    df = df.dropna(subset=["Product Code"])
    df["code"] = df["Product Code"].str.strip().str.upper()
    if df["code"].duplicated().any():
        dups = df.loc[df["code"].duplicated(keep=False), "code"].unique()
        sys.exit(f"ERROR: duplicate product codes in supplier file: {list(dups)[:20]}")
    sim = {}
    for code, desc, old, new in zip(df["code"], df["Product Description"], df["Price"], df["New Price"]):
        try:
            old_d, new_d = Decimal(old), Decimal(new)
        except Exception:
            sys.exit(f"ERROR: non-numeric price for supplier code {code}: {old!r} / {new!r}")
        if new_d <= 0:
            sys.exit(f"ERROR: zero/negative new price for supplier code {code}")
        # Strip float noise (e.g. 7.800000000000001) without changing real prices
        sim[code] = (str(desc).strip(), old_d, new_d.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP))
    return sim


def load_labels(path):
    df = pd.read_excel(path, dtype=str)
    df["SKU"] = df["SKU"].astype(str).str.strip()
    labels = {}
    for sku, lab in zip(df["SKU"], df["Labels"].fillna("")):
        kind = "BANNER" if "#BANNER" in lab.upper() else "INHOUSE" if "#INHOUSE" in lab.upper() else "OTHER"
        labels[sku] = kind if labels.get(sku, kind) == kind else "CONFLICT"
    return labels


def load_catalogue_codes(path):
    if not path or not os.path.exists(path):
        return set()
    wb = load_workbook(path, read_only=True)
    names = {n.strip().lower(): n for n in wb.sheetnames}
    ws = wb[names.get("catalogue") or names["full file"]]
    return {str(r[0]).strip().upper() for r in ws.iter_rows(min_row=2, max_col=1, values_only=True) if r[0] is not None}


def find_code(base, codes):
    """Exact code, else (for all-digit codes) 1-3 restored leading zeros. Returns (code|None, ambiguous)."""
    hits = [base] if base in codes else []
    if base.isdigit():
        hits += [p + base for p in ("0", "00", "000") if p + base in codes]
    return (hits[0] if len(hits) == 1 else None), len(hits) > 1


def parse_sku(sku, codes):
    """Return (code, multiplier, how) for the strict grammar, or (None, None, reason)."""
    s = re.sub(r"\s+", " ", sku.strip().upper())
    s = re.sub(r"[\s.\-_]+$", "", s)
    if not s:
        return None, None, "blank"
    code, amb = find_code(s, codes)
    if code or amb:
        return (code, 1, "exact" if code == s else "leading zeros restored") if code else (None, None, "ambiguous leading zeros")
    s = VARIANT.sub("", s)
    candidates = []
    m = PREFIX.match(s)
    if m:
        candidates.append((m.group("rest"), int(m.group(1)), "multipack prefix"))
    m = SUFFIX.match(s)
    if m:
        candidates.append((m.group("rest"), int(m.group(2)), "multipack suffix"))
    candidates.append((s, 1, "variant suffix"))
    for rest, mult, how in candidates:
        rest = VARIANT.sub("", re.sub(r"[\s.\-_]+$", "", rest))
        code, amb = find_code(rest, codes)
        if amb:
            return None, None, "ambiguous leading zeros"
        if code and mult >= 1:
            return code, mult, how
    return None, None, "no supplier code"


def loose_code(sku, codes):
    """Any supplier code appearing as a token anywhere in the SKU (for the Review sheet only)."""
    for tok in re.findall(r"[A-Z0-9]+(?:-[A-Z0-9]+)*", sku.upper()):
        code, _ = find_code(tok, codes)
        if code and len(tok) >= 5:
            return code
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repricer")
    ap.add_argument("sim")
    ap.add_argument("sellerboard")
    ap.add_argument("--catalogue", default=DEFAULT_CATALOGUE)
    ap.add_argument("--vat", default="0")
    ap.add_argument("--approve-review", action="store_true",
                    help="also upload Review rows that have a supplier code (pack quantity 1 if the SKU format is unrecognised)")
    ap.add_argument("--out", default=".")
    a = ap.parse_args()
    vat = Decimal(a.vat)

    rep = pd.read_csv(a.repricer, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    sim = load_sim(a.sim)
    labels = load_labels(a.sellerboard)
    catalogue = load_catalogue_codes(a.catalogue)
    codes = set(sim)

    audit, upload_idx, new_costs = [], [], {}
    for i, row in rep.iterrows():
        sku = row["sku"]
        label = labels.get(sku.strip(), "NOT IN SELLERBOARD")
        code, mult, how = parse_sku(sku, codes)
        cur = Decimal(row["unit_cost"] or "0")
        rec = {"Amazon_SKU": sku, "Merchant_ID": row["merchant_id"], "ASIN": row["asin"], "Title": row["title"],
               "Sellerboard_Label": label, "Base_Supplier_SKU": code or "", "Match_Rule": how,
               "Pack_Quantity": mult or "", "Old_Repricer_Cost": float(cur)}
        loose = None if code else loose_code(sku, codes)
        if not code and loose and label != "INHOUSE":
            code, mult = loose, 1
        if code:
            desc, old, new = sim[code]
            new_ex = money(new * mult)
            new_inc = money(new * mult * (1 + vat))
            expected_old = old * mult
            ratio = float(cur / expected_old) if cur > 0 else None
            rec.update({"Supplier_Description": desc, "Supplier_Old_Price_Ex_VAT": float(old),
                        "Supplier_New_Price_Ex_VAT": float(new), "New_Cost_Ex_VAT": float(new_ex),
                        "New_Repricer_Cost": float(new_inc), "Pack_Quantity": mult,
                        "Change_vs_Current": float(new_inc - cur) if cur > 0 else None,
                        "Current_vs_Old_Supplier": round(ratio, 2) if ratio else None})
            if label == "INHOUSE":
                status, note = "SKIPPED - IN-HOUSE", "Sellerboard says #InHouse, so cost not touched"
            elif loose:
                status, note = "REVIEW", "SKU contains a Banner code but not in a recognised format: confirm code and pack size"
            elif label != "BANNER":
                status, note = "REVIEW", f"Matches a Banner code but Sellerboard label is {label}"
            elif ratio is not None and not SANITY[0] <= ratio <= SANITY[1]:
                status, note = "REVIEW", f"Current cost is {ratio:.2f}x old supplier price x {mult}: check pack size"
            else:
                status, note = "UPDATE", ""
            # A Banner price far below the current cost (e.g. £0.03 loan dispensers) is never auto-approved:
            # a near-zero cost would let the repricer sell at a loss
            if status == "REVIEW" and a.approve_review and not (ratio and ratio > SANITY[1]):
                status = "UPDATE - APPROVED REVIEW"
            if status.startswith("UPDATE"):
                upload_idx.append(i)
                new_costs[i] = f"{new_inc:.2f}"
            rec["Base_Supplier_SKU"] = code
        else:
            stripped = re.sub(r"[\s.\-_]+$", "", sku.strip().upper())
            if how == "ambiguous leading zeros":
                status, note = "REVIEW", "Code matches more than one supplier code once leading zeros are restored"
            elif label == "INHOUSE":
                status, note = "SKIPPED - IN-HOUSE", ""
            elif label == "BANNER":
                in_cat = find_code(stripped, catalogue)[0] if catalogue else None
                status = "BANNER - NO INCREASE LISTED" if in_cat else "BANNER - CODE NOT FOUND"
                note = ("Code is in the Banner catalogue but not in the price-increase file; cost left as is"
                        if in_cat else "Labelled #BANNER but no supplier code found; cost left as is")
            else:
                status, note = "IGNORED - NOT SUPPLIER", ""
        rec["Status"], rec["Note"] = status, note
        audit.append(rec)

    audit = pd.DataFrame(audit)
    os.makedirs(a.out, exist_ok=True)

    upload = rep.loc[upload_idx].copy()
    upload["unit_cost"] = [new_costs[i] for i in upload_idx]
    up_path = os.path.join(a.out, "Repricer_Upload_Updated_Costs.csv")
    upload.to_csv(up_path, index=False, encoding="utf-8", lineterminator="\r\n")

    xl_path = os.path.join(a.out, "Supplier_Price_Analysis.xlsx")
    write_workbook(xl_path, audit, a, vat)

    counts = audit["Status"].value_counts()
    print(f"Repricer rows:            {len(rep)}")
    for k, v in counts.items():
        print(f"  {k:<30} {v}")
    print(f"Upload rows written:      {len(upload)}  -> {up_path}")
    print(f"Analysis workbook:        {xl_path}")


COLUMNS = ["Status", "Note", "Amazon_SKU", "Merchant_ID", "ASIN", "Sellerboard_Label", "Base_Supplier_SKU",
           "Match_Rule", "Pack_Quantity", "Supplier_Description", "Old_Repricer_Cost", "Supplier_Old_Price_Ex_VAT",
           "Supplier_New_Price_Ex_VAT", "New_Cost_Ex_VAT", "New_Repricer_Cost", "Change_vs_Current",
           "Current_vs_Old_Supplier", "Title"]
MONEY_COLS = {"Old_Repricer_Cost", "Supplier_Old_Price_Ex_VAT", "Supplier_New_Price_Ex_VAT", "New_Cost_Ex_VAT",
              "New_Repricer_Cost", "Change_vs_Current"}


def write_workbook(path, audit, a, vat):
    audit = audit.reindex(columns=COLUMNS)
    order = ["UPDATE", "UPDATE - APPROVED REVIEW", "REVIEW", "SKIPPED - IN-HOUSE", "BANNER - NO INCREASE LISTED", "BANNER - CODE NOT FOUND",
             "IGNORED - NOT SUPPLIER"]
    sheets = {
        "Updated": audit[audit.Status.str.startswith("UPDATE")],
        "Review": audit[audit.Status == "REVIEW"],
        "In-House Skipped": audit[audit.Status == "SKIPPED - IN-HOUSE"],
        "Banner Not Updated": audit[audit.Status.isin(order[4:6])],
        "All SKUs": audit,
    }
    upd = sheets["Updated"]
    summary = [("Supplier price analysis", ""), ("", ""),
               ("Repricer file", os.path.basename(a.repricer)), ("Supplier file", os.path.basename(a.sim)),
               ("Sellerboard file", os.path.basename(a.sellerboard)), ("VAT added", f"{vat * 100:.0f}%"),
               ("Formula", "round(Supplier New Price ex VAT x Pack Quantity x (1 + VAT), 2)"), ("", ""),
               ("Status", "Rows")]
    summary += [(s, int((audit.Status == s).sum())) for s in order]
    summary += [("Total repricer rows", len(audit)), ("", ""),
                ("Updated rows that had £0 cost before", int((upd.Old_Repricer_Cost == 0).sum())),
                ("Updated rows that are multipacks", int((upd.Pack_Quantity.astype(float) > 1).sum())),
                ("", ""), ("Only UPDATE rows (including approved Review rows) are in Repricer_Upload_Updated_Costs.csv.", ""),
                ("REVIEW rows need a decision before their cost can change.", "")]
    with pd.ExcelWriter(path, engine="openpyxl") as xw:
        pd.DataFrame(summary).to_excel(xw, sheet_name="Summary", index=False, header=False)
        for name, df in sheets.items():
            df.to_excel(xw, sheet_name=name, index=False)
    wb = load_workbook(path)
    ws = wb["Summary"]
    ws["A1"].font = Font(bold=True, size=14)
    ws["A9"].font = ws["B9"].font = Font(bold=True)
    ws.column_dimensions["A"].width, ws.column_dimensions["B"].width = 42, 60
    widths = {"Status": 26, "Note": 50, "Amazon_SKU": 26, "Title": 60, "Supplier_Description": 36}
    head = PatternFill("solid", fgColor="1F4E78")
    for name in sheets:
        ws = wb[name]
        ws.freeze_panes = "D2"
        ws.auto_filter.ref = ws.dimensions
        for j, col in enumerate(COLUMNS, 1):
            c = ws.cell(1, j)
            c.font, c.fill, c.alignment = Font(bold=True, color="FFFFFF"), head, Alignment(wrap_text=True)
            ws.column_dimensions[get_column_letter(j)].width = widths.get(col, 14)
            if col in MONEY_COLS:
                for cell in ws.iter_cols(min_col=j, max_col=j, min_row=2):
                    for x in cell:
                        x.number_format = '£#,##0.00;-£#,##0.00'
    wb.save(path)


if __name__ == "__main__":
    main()
