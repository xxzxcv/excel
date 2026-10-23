"""Set repricer_name to a new rule for Banner SKUs that have no rule ("Off") in a repricer essentials export.
Banner/in-house classification comes from Fix_Audit_All_SKUs.csv (loss_fix.py run on the latest export):
in-house, non-Banner and £0-cost Banner rows are excluded. Raw lines are copied; only repricer_name changes."""
import csv, re, sys, collections
src, audit_path, out_path, rule = sys.argv[1:5]
cls = {}
for r in csv.DictReader(open(audit_path, encoding='utf-8-sig')):
    k = (r['sku'], r['merchant_id'], r['asin'])
    cls[k] = ('INHOUSE' if r['note'] == 'In-house' else 'NOT_BANNER' if r['note'] == 'Not a Banner SKU'
              else 'BANNER_ZERO_COST' if r['note'].startswith('Banner, no cost') else 'BANNER')
TOKEN = re.compile(r'"(?:[^"]|"")*"|[^,]*')
def split_raw(line):
    toks, pos = [], 0
    while True:
        m = TOKEN.match(line, pos); toks.append(m.group(0)); pos = m.end()
        if pos >= len(line): return toks
        assert line[pos] == ','; pos += 1
lines = open(src, encoding='utf-8', newline='').read().split('\n'); assert lines[-1] == ''
hdr = next(csv.reader([lines[0]])); RN = hdr.index('repricer_name')
out, stats = [lines[0]], collections.Counter()
for line in lines[1:-1]:
    f = next(csv.reader([line])); toks = split_raw(line)
    assert len(toks) == len(f) == len(hdr) and next(csv.reader([','.join(toks)])) == f
    c = cls.get((f[0], f[2], f[5]), 'NOT IN AUDIT')
    has_rule = f[RN].strip() not in ('', 'Off')
    stats[(c, 'has rule' if has_rule else 'no rule')] += 1
    if c == 'BANNER' and not has_rule:
        toks[RN] = '"' + rule.replace('"', '""') + '"'
        out.append(','.join(toks))
open(out_path, 'w', encoding='utf-8', newline='').write('\n'.join(out) + '\n')
for k, v in sorted(stats.items()): print(k, v)
print('rows written', len(out) - 1)
