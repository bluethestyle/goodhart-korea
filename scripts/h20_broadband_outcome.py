"""H20: 통신 outcome 교체 — 초고속인터넷 가입자 (e-나라지표 idx_cd=1348).

소스: 과학기술정보통신부 (통신사업자 보고자료)
시계열: 1999~2025 (27년)

분야: 통신
metric: broadband_subscribers   가입자수 (천명)
        broadband_per_100       100명당 가입자수 (보급률)
        broadband_growth        전년대비 증감율 (%)

교체 대상: ict_value_added (자기 인과 — 통신 출연 → ICT 부가가치)
신규: 보급률은 정책 효과의 직접 지표
"""
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import duckdb

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, 'data', 'warehouse.duckdb')

years = list(range(1999, 2026))

data = {
    'broadband_subscribers': [
        278, 3870, 7806, 10405, 11178, 11921, 12190, 14043, 14710, 15475,
        16349, 17224, 17860, 18253, 18738, 19199, 20025, 20556, 21196, 21286,
        21906, 22327, 22944, 23537, 24098, 24722, 25224],
    'broadband_per_100': [
        0.6, 8.2, 16.5, 21.8, 23.3, 24.7, 25.4, 29.1, 30.4, 31.8,
        33.5, 35.3, 35.9, 36.5, 37.3, 38.1, 39.6, 40.1, 41.3, 41.2,
        42.4, 43.1, 44.4, 45.8, 47.0, 48.3, 49.0],
    'broadband_growth': [  # 1999는 NaN, 첫 값은 1292.1
        None, 1292.1, 101.7, 33.3, 7.4, 6.6, 2.3, 15.2, 4.7, 5.2,
        5.6, 5.1, 3.7, 2.2, 2.7, 2.5, 4.3, 2.7, 3.1, 1.4,
        2.9, 2.0, 2.8, 2.6, 2.4, 2.6, 2.0],
}
unit_map = {'broadband_subscribers':'천명','broadband_per_100':'명/100인','broadband_growth':'%'}
nm_map = {
    'broadband_subscribers': '초고속인터넷 가입자수',
    'broadband_per_100':     '100명당 초고속인터넷 가입자수',
    'broadband_growth':      '초고속인터넷 가입자 전년대비 증감율',
}

con = duckdb.connect(DB)
codes = "', '".join(data.keys())
con.execute(f"DELETE FROM indicator_panel WHERE metric_code IN ('{codes}')")
con.execute(f"DELETE FROM indicator_metadata WHERE metric_code IN ('{codes}')")

records = []
for code, vals in data.items():
    for y, v in zip(years, vals):
        if v is None: continue
        records.append(('통신', y, code, float(v), 'eNaraJiPyo_idx1348', unit_map[code]))

con.executemany("INSERT INTO indicator_panel (fld_nm, year, metric_code, value, source, unit) VALUES (?,?,?,?,?,?)", records)
meta = [(code, nm_map[code], 'outcome',
         f'과학기술정보통신부 — {nm_map[code]} (e-나라지표 1348)',
         'https://www.index.go.kr/unity/potal/main/EachDtlPageDetail.do?idx_cd=1348', 1)
        for code in data.keys()]
con.executemany("INSERT INTO indicator_metadata (metric_code, metric_nm, category, description, source_url, expected_sign) VALUES (?,?,?,?,?,?)", meta)

print(f'적재: panel {len(records)}, meta {len(meta)}')
v = con.execute(f"""
SELECT metric_code, COUNT(*) n, MIN(year) y0, MAX(year) y1, ROUND(AVG(value),2) avg
FROM indicator_panel WHERE metric_code IN ('{codes}') GROUP BY 1 ORDER BY 1
""").fetchdf()
print(v.to_string(index=False))
con.close()
