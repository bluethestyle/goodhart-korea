"""H15: 통일·외교 outcome — 한국 ODA 원조규모 (e-나라지표 idx_cd=1687).

소스: OECD Data Explorer 기반, e-나라지표 정적 게재.
시계열: 2001~2024 (24년)
단위: 백만불
주석: 2017년까지 순지출기준, 2018년부터 증여등가액기준 / 2024 잠정치

분야: 통일·외교
metric: oda_total          ODA 총액
        oda_gni_ratio      ODA/GNI 비율
        oda_bilateral      양자 ODA
        oda_multilateral   다자 ODA

분야 매핑 12→13.
"""
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import duckdb

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, 'data', 'warehouse.duckdb')

# 사용자 제공 (e-나라지표 idx_cd=1687, 2026-04-28 발췌)
years = list(range(2001, 2025))
data = {
    'oda_total':       [265, 279, 366, 423, 752, 455, 696, 802, 816, 1174, 1325, 1597, 1755, 1857,
                         1915, 2246, 2201, 2355, 2463, 2250, 2873, 2810, 3160, 3943],
    'oda_gni_ratio':   [0.06, 0.06, 0.06, 0.06, 0.10, 0.05, 0.07, 0.09, 0.10, 0.12, 0.12, 0.14,
                         0.13, 0.13, 0.14, 0.16, 0.14, 0.14, 0.15, 0.14, 0.16, 0.17, 0.17, 0.21],
    'oda_bilateral':   [172, 207, 245, 331, 463, 376, 491, 539, 581, 901, 990, 1183, 1310, 1396,
                         1469, 1549, 1615, 1731, 1857, 1751, 2168, 2221, 2325, 3186],
    'oda_multilateral':[93, 72, 121, 93, 289, 79, 206, 263, 235, 273, 335, 414, 446, 461,
                         447, 698, 586, 624, 606, 499, 704, 589, 835, 756],
}
unit_map = {'oda_total':'백만불','oda_gni_ratio':'%','oda_bilateral':'백만불','oda_multilateral':'백만불'}
nm_map = {
    'oda_total':       '한국 공적개발원조(ODA) 총액',
    'oda_gni_ratio':   'GNI 대비 ODA 비율',
    'oda_bilateral':   '양자 ODA',
    'oda_multilateral':'다자 ODA',
}

# 적재
con = duckdb.connect(DB)
codes = "', '".join(data.keys())
con.execute(f"DELETE FROM indicator_panel WHERE metric_code IN ('{codes}')")
con.execute(f"DELETE FROM indicator_metadata WHERE metric_code IN ('{codes}')")

records = []
for code, vals in data.items():
    for y, v in zip(years, vals):
        records.append(('통일·외교', y, code, float(v),
                        'eNaraJiPyo_idx1687', unit_map[code]))

con.executemany("INSERT INTO indicator_panel (fld_nm, year, metric_code, value, source, unit) VALUES (?,?,?,?,?,?)", records)

meta = [(code, nm_map[code], 'outcome',
         f'한국 ODA — {nm_map[code]} (e-나라지표 1687, OECD Data Explorer 기반)',
         'https://www.index.go.kr/unity/potal/main/EachDtlPageDetail.do?idx_cd=1687', 1)
        for code in data.keys()]
con.executemany("INSERT INTO indicator_metadata (metric_code, metric_nm, category, description, source_url, expected_sign) VALUES (?,?,?,?,?,?)", meta)

print(f'적재: panel {len(records)}, meta {len(meta)}')
print('\n=== 검증 ===')
v = con.execute(f"""
SELECT metric_code, COUNT(*) n, MIN(year) y0, MAX(year) y1, ROUND(AVG(value),2) avg
FROM indicator_panel WHERE metric_code IN ('{codes}') GROUP BY 1 ORDER BY 1
""").fetchdf()
print(v.to_string(index=False))
con.close()
