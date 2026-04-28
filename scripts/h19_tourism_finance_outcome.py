"""H19: 관광 + 행정 outcome 교체.

(1) 문화관광 — 방한 외래관광객 (e-나라지표 idx_cd=1653)
    소스: 한국관광통계(한국관광공사)
    시계열: 1990~2024 (35년)
    metric: foreign_tourists_total (천명), foreign_tourists_growth (%)
    교체 대상: tourists_sample (표본수, 부적절)

(2) 일반·지방행정 — 지방자치단체 재정자립도 (e-나라지표 idx_cd=2458)
    소스: 행정안전부「2025년도 예산 및 기금 개요」
    시계열: 1997~2025 (29년)
    metric: fiscal_indep_natl (전국평균),
            fiscal_indep_metro/province/city/county/district (구분별)
    교체 대상: local_tax_per_capita (징세, 행정 outcome 부적절)
"""
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import duckdb

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, 'data', 'warehouse.duckdb')

# (1) 외래관광객 1990~2024
years_t = list(range(1990, 2025))
tourists = [2959,3196,3231,3331,3580,3753,3684,3908,4250,4660,
            5322,5147,5347,4753,5818,6023,6155,6448,6891,7818,
            8798,9795,11140,12176,14202,13232,17242,13336,15347,17503,
            2519,967,3198,11032,16370]
tourist_growth = [8.5,8.0,1.1,3.1,7.5,4.8,-1.8,6.1,8.8,9.6,
                  14.2,-3.3,3.9,-11.1,22.4,3.5,2.2,4.8,6.9,13.4,
                  12.5,11.3,13.7,9.3,16.6,-6.8,30.3,-22.7,15.1,14.0,
                  -85.6,-61.6,230.7,245.0,48.4]

# (2) 재정자립도 1997~2025
years_f = list(range(1997, 2026))
fiscal = {
    'fiscal_indep_natl':     [63.0,63.4,59.6,59.4,57.6,54.8,56.3,57.2,56.2,54.4,53.6,53.9,53.6,52.2,
                              51.9,52.3,51.1,50.3,50.6,52.5,53.7,53.4,51.4,50.4,48.7,49.9,50.1,48.6,48.6],
    'fiscal_indep_metro':    [89.4,90.0,81.8,84.8,82.9,79.8,82.2,81.4,80.3,78.5,73.9,73.8,72.7,68.3,
                              68.6,69.1,66.8,64.8,65.8,66.6,67.0,65.7,62.7,60.9,58.9,61.0,61.2,57.7,56.7],
    'fiscal_indep_province': [42.5,42.1,38.3,37.9,35.6,34.6,39.4,41.3,36.6,36.1,34.9,39.5,33.3,31.6,
                              33.0,34.8,34.1,33.2,34.8,35.9,38.3,39.0,36.9,39.4,36.5,40.0,39.2,36.6,36.6],
    'fiscal_indep_city':     [53.3,54.1,52.0,50.6,43.4,40.2,38.0,38.8,40.6,39.4,39.5,40.7,40.7,40.0,
                              38.0,37.1,36.8,36.5,35.9,37.4,39.2,37.9,36.8,33.5,32.3,31.9,32.3,31.5,31.6],
    'fiscal_indep_county':   [21.2,22.9,23.4,22.0,18.1,17.4,16.3,16.6,16.5,16.1,16.6,17.2,17.8,18.0,
                              17.1,16.4,16.1,16.6,17.0,18.0,18.8,18.5,18.3,17.3,17.3,15.9,16.6,17.2,17.7],
    'fiscal_indep_district': [51.6,49.7,52.3,46.9,45.0,45.1,42.3,42.6,44.3,40.5,37.5,37.1,37.3,35.4,
                              36.6,36.0,33.9,31.1,29.2,29.7,30.8,30.3,29.8,29.0,28.5,28.3,29.0,28.1,27.4],
}

con = duckdb.connect(DB)
new_codes = ['foreign_tourists_total','foreign_tourists_growth'] + list(fiscal.keys())
codes_str = "', '".join(new_codes)
con.execute(f"DELETE FROM indicator_panel WHERE metric_code IN ('{codes_str}')")
con.execute(f"DELETE FROM indicator_metadata WHERE metric_code IN ('{codes_str}')")

records = []
for y, v in zip(years_t, tourists):
    records.append(('문화및관광', y, 'foreign_tourists_total', float(v),
                    'eNaraJiPyo_idx1653', '천명'))
for y, v in zip(years_t, tourist_growth):
    records.append(('문화및관광', y, 'foreign_tourists_growth', float(v),
                    'eNaraJiPyo_idx1653', '%'))
for code, vals in fiscal.items():
    for y, v in zip(years_f, vals):
        records.append(('일반·지방행정', y, code, float(v),
                        'eNaraJiPyo_idx2458', '%'))

con.executemany("INSERT INTO indicator_panel (fld_nm, year, metric_code, value, source, unit) VALUES (?,?,?,?,?,?)", records)

meta = [
    ('foreign_tourists_total', '방한 외래관광객 (총)', 'outcome',
     '한국관광공사 한국관광통계 (e-나라지표 1653)',
     'https://www.index.go.kr/unity/potal/main/EachDtlPageDetail.do?idx_cd=1653', 1),
    ('foreign_tourists_growth', '방한 외래관광객 전년대비 증가율', 'outcome',
     '한국관광공사 한국관광통계 (e-나라지표 1653)',
     'https://www.index.go.kr/unity/potal/main/EachDtlPageDetail.do?idx_cd=1653', 1),
]
fiscal_meta = {
    'fiscal_indep_natl':     '재정자립도 (전국평균)',
    'fiscal_indep_metro':    '재정자립도 (특·광역시)',
    'fiscal_indep_province': '재정자립도 (도)',
    'fiscal_indep_city':     '재정자립도 (시)',
    'fiscal_indep_county':   '재정자립도 (군)',
    'fiscal_indep_district': '재정자립도 (자치구)',
}
for code, nm in fiscal_meta.items():
    meta.append((code, nm, 'outcome',
                 f'행정안전부 「2025년도 예산 및 기금 개요」 — {nm} (e-나라지표 2458)',
                 'https://www.index.go.kr/unity/potal/main/EachDtlPageDetail.do?idx_cd=2458', 1))

con.executemany("INSERT INTO indicator_metadata (metric_code, metric_nm, category, description, source_url, expected_sign) VALUES (?,?,?,?,?,?)", meta)

print(f'적재: panel {len(records)}, meta {len(meta)}')
print('\n=== 검증 ===')
v = con.execute(f"""
SELECT metric_code, COUNT(*) n, MIN(year) y0, MAX(year) y1, ROUND(AVG(value),2) avg
FROM indicator_panel WHERE metric_code IN ('{codes_str}') GROUP BY 1 ORDER BY 1
""").fetchdf()
print(v.to_string(index=False))
con.close()
