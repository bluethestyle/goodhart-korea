"""H12: GIR 국가 온실가스 인벤토리 적재 — 환경 분야 outcome.

소스: data/external/gir/ghg_inventory_1990_2023.csv
  - 1990~2023 (34년)
  - 행: 분야·연료별 세분 + 총배출량/순배출량
  - 컬럼: 연도 1990~2023

추출:
  ghg_total       총배출량(kt CO2-eq)  분야=환경
  ghg_net         순배출량(kt CO2-eq)  분야=환경
  ghg_energy      에너지 부문 배출량   분야=환경 (참고용)

분야 매핑 10 → 11.
"""
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import pandas as pd
import duckdb

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'data', 'external', 'gir',
                    'ghg_inventory_1990_2023.csv')
DB = os.path.join(ROOT, 'data', 'warehouse.duckdb')

df = pd.read_csv(SRC, encoding='utf-8')
print(f'shape: {df.shape}')

# 추출할 행
ROWS = {
    'ghg_total':  '총배출량(kt CO2-eq)',
    'ghg_net':    '순배출량',
    'ghg_energy': '에너지',
}
year_cols = [c for c in df.columns if c.isdigit() and 1990 <= int(c) <= 2025]
print(f'year cols: {year_cols[0]}~{year_cols[-1]} ({len(year_cols)})')

records = []
meta_rows = []
for code, label in ROWS.items():
    sub = df[df['분야 및 연도']==label]
    if sub.empty:
        # 부분 매칭 시도
        sub = df[df['분야 및 연도'].str.contains(label, regex=False, na=False)]
        if sub.empty:
            print(f'[{code}] no row matching "{label}"')
            continue
        sub = sub.head(1)
    row = sub.iloc[0]
    v0 = pd.to_numeric(row[year_cols[0]], errors='coerce')
    v1 = pd.to_numeric(row[year_cols[-1]], errors='coerce')
    print(f'[{code}] row "{row["분야 및 연도"]}": {year_cols[0]}={v0:.1f}, {year_cols[-1]}={v1:.1f}')
    for y in year_cols:
        try:
            v = float(row[y])
            records.append(('환경', int(y), code, v, 'GIR_inventory', 'kt CO2-eq'))
        except (ValueError, TypeError):
            pass
    sign = -1  # 배출량 ↓ = outcome 좋음
    meta_rows.append((code, ROWS[code], 'outcome',
                      f'국가 온실가스 인벤토리 — {label}',
                      'https://www.gir.go.kr', sign))

print(f'\n총 records: {len(records)}')

# 적재
con = duckdb.connect(DB)
codes = "', '".join(ROWS.keys())
con.execute(f"DELETE FROM indicator_panel WHERE metric_code IN ('{codes}')")
con.execute(f"DELETE FROM indicator_metadata WHERE metric_code IN ('{codes}')")
con.executemany("INSERT INTO indicator_panel (fld_nm, year, metric_code, value, source, unit) VALUES (?,?,?,?,?,?)", records)
con.executemany("INSERT INTO indicator_metadata (metric_code, metric_nm, category, description, source_url, expected_sign) VALUES (?,?,?,?,?,?)", meta_rows)

# 검증
v = con.execute(f"""
SELECT metric_code, COUNT(*) n, MIN(year) y0, MAX(year) y1, ROUND(MIN(value),0) v_min, ROUND(MAX(value),0) v_max
FROM indicator_panel WHERE metric_code IN ('{codes}') GROUP BY 1
""").fetchdf()
print(v.to_string(index=False))
con.close()
print('\n완료.')
