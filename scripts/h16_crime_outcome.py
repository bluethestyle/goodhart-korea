"""H16: 공공질서 outcome — 총범죄 발생 및 검거 (e-나라지표 idx_cd=1606).

소스: 경찰청 「범죄통계」, e-나라지표 정적 게재.
시계열: 1996~2024 (29년)
주석: 2024부터 해양경찰청 입건 사건 미포함.

분야: 공공질서및안전
metric: crime_occurrence    범죄 발생 건수
        crime_arrest        범죄 검거 건수
        crime_arrest_rate   검거율 (%)

분야 매핑 13→14.
"""
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import duckdb

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, 'data', 'warehouse.duckdb')

years = list(range(1996, 2025))
data = {
    'crime_occurrence': [
        1419811, 1536652, 1712233, 1654064, 1739558, 1860687, 1833271, 1894762, 1968183, 1733122,
        1719075, 1836496, 2064646, 2020209, 1784953, 1752598, 1793400, 1857276, 1778966, 1861657,
        1849450, 1662341, 1580751, 1611906, 1587866, 1429826, 1482433, 1520200, 1583108],
    'crime_arrest': [
        1287260, 1398384, 1579728, 1574902, 1543219, 1642118, 1694342, 1679249, 1761590, 1512247,
        1483011, 1615093, 1813229, 1811917, 1514098, 1382463, 1370121, 1420658, 1392112, 1500234,
        1552455, 1413717, 1328609, 1342854, 1289129, 1136665, 1133788, 1185985, 1222482],
    'crime_arrest_rate': [
        90.7, 91.0, 92.3, 95.2, 88.7, 88.3, 92.4, 88.6, 89.5, 87.3,
        86.3, 87.9, 87.8, 89.7, 84.8, 78.9, 76.4, 76.5, 78.3, 80.6,
        83.9, 85.0, 84.0, 83.3, 81.2, 79.5, 76.5, 78.0, 77.2],
}
unit_map = {'crime_occurrence':'건','crime_arrest':'건','crime_arrest_rate':'%'}
nm_map = {
    'crime_occurrence':  '범죄 발생 건수',
    'crime_arrest':      '범죄 검거 건수',
    'crime_arrest_rate': '범죄 검거율',
}
sign_map = {'crime_occurrence': -1, 'crime_arrest': 1, 'crime_arrest_rate': 1}

con = duckdb.connect(DB)
codes = "', '".join(data.keys())
con.execute(f"DELETE FROM indicator_panel WHERE metric_code IN ('{codes}')")
con.execute(f"DELETE FROM indicator_metadata WHERE metric_code IN ('{codes}')")

records = []
for code, vals in data.items():
    for y, v in zip(years, vals):
        records.append(('공공질서및안전', y, code, float(v),
                        'eNaraJiPyo_idx1606', unit_map[code]))

con.executemany("INSERT INTO indicator_panel (fld_nm, year, metric_code, value, source, unit) VALUES (?,?,?,?,?,?)", records)

meta = [(code, nm_map[code], 'outcome',
         f'경찰청 범죄통계 — {nm_map[code]} (e-나라지표 1606)',
         'https://www.index.go.kr/unity/potal/main/EachDtlPageDetail.do?idx_cd=1606', sign_map[code])
        for code in data.keys()]
con.executemany("INSERT INTO indicator_metadata (metric_code, metric_nm, category, description, source_url, expected_sign) VALUES (?,?,?,?,?,?)", meta)

print(f'적재: panel {len(records)}, meta {len(meta)}')
print('\n=== 검증 ===')
v = con.execute(f"""
SELECT metric_code, COUNT(*) n, MIN(year) y0, MAX(year) y1, ROUND(AVG(value),0) avg
FROM indicator_panel WHERE metric_code IN ('{codes}') GROUP BY 1 ORDER BY 1
""").fetchdf()
print(v.to_string(index=False))
con.close()
