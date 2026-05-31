"""Print formatted table rows for the SVG."""
import csv, math, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

path = r"d:\workspace\재정자료분석\data\results\H23_mediation_estimates.csv"

def fmt(v, decimals=3):
    try:
        f = float(v)
        if math.isnan(f): return "N/A"
        if abs(f) >= 1e6:
            return f"{f:,.0f}"
        if abs(f) >= 1000:
            return f"{f:,.1f}"
        return f"{f:.{decimals}f}"
    except:
        return str(v) if v else "N/A"

with open(path, encoding='utf-8-sig') as fh:
    reader = csv.DictReader(fh)
    for row in reader:
        keys = list(row.keys())
        fld_key = keys[0]
        if 'POOLED' in row.get(fld_key,''):
            continue
        name = row.get('fld_short', row.get(fld_key,''))
        a    = fmt(row.get('a',''), 3)
        se_a = fmt(row.get('se_a',''), 3)
        b    = fmt(row.get('b',''), 3)
        se_b = fmt(row.get('se_b',''), 3)
        c    = fmt(row.get('c',''), 3)
        cp   = fmt(row.get('c_prime',''), 3)
        ab   = fmt(row.get('ab',''), 3)
        ab_b = fmt(row.get('ab_boot',''), 3)
        lo   = fmt(row.get('ab_lo95',''), 3)
        hi   = fmt(row.get('ab_hi95',''), 3)
        sz   = fmt(row.get('sobel_z',''), 3)
        sp   = fmt(row.get('sobel_p',''), 4)
        mr   = fmt(row.get('mediation_ratio',''), 3)
        print(f"{name}|{a}|{se_a}|{b}|{se_b}|{c}|{cp}|{ab}|{ab_b}|{lo}|{hi}|{sz}|{sp}|{mr}")
