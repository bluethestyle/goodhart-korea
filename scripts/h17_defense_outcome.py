"""H17: 국방 outcome — 방산지정업체 경영분석 (e-나라지표 idx_cd=1703).

소스: 한국방위산업진흥회 '2024 방산지정업체경영분석조사', e-나라지표 정적.
시계열: 1995~2023 (29년) — 영업이익률은 1995~, 가동률 1995~ 모두 포함.
주석: 2024 방산통계는 2025년 4분기 업데이트 예정.

분야: 국방
metric: defense_revenue        방산업체 매출액 (억원)
        defense_op_profit      방산업체 영업이익 (억원)
        defense_op_margin      방산업체 영업이익률 (%)
        defense_op_margin_mfg  제조업 평균 영업이익률 (%) — 비교용
        defense_util_rate      방산업체 가동률 (%)
        defense_util_rate_mfg  제조업 평균 가동률 (%) — 비교용

분야 매핑 14→15.
"""
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import duckdb

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, 'data', 'warehouse.duckdb')

years = list(range(1995, 2024))

# None = 결측
data = {
    'defense_revenue': [
        25840, 30132, 34402, 33876, 31211, 33359, 37013, 43447, 42681, 46440,
        53165, 54517, 61955, 72351, 87691, 93303, 93095, 93429, 104651, 119883,
        142651, 148163, 127611, 136493, 144521, 153517, 158801, 168300, 201951],
    'defense_op_profit': [
        1186, 1473, 2619, 2030, 1559, 2130, 1617, 1545, 1543, 1413,
        2500, 2673, 2629, 3626, 5338, 6897, 5323, 4230, 2435, 5352,
        4710, 5033, 602, 3252, 4875, 5675, 7229, 10517, 18629],
    'defense_op_margin': [
        4.6, 4.9, 7.6, 6.0, 5.0, 6.4, 4.4, 3.6, 3.6, 3.0,
        4.7, 5.0, 4.2, 5.0, 6.1, 7.4, 5.7, 4.5, 2.3, 4.5,
        5.1, 3.4, 0.5, 2.4, 3.4, 3.7, 4.6, 6.3, 9.2],
    'defense_op_margin_mfg': [
        6.9, 5.4, 6.5, 4.9, 5.0, 6.8, 5.4, 6.2, 6.7, 7.2,
        6.1, 5.0, 5.8, 5.9, 6.1, 6.9, 5.6, 5.1, 5.2, 4.2,
        3.3, 6.0, 7.6, 7.3, 4.4, 4.6, 6.8, 5.7, 3.3],
    'defense_util_rate': [
        56.0, 55.7, 56.9, 52.8, 50.8, 48.5, 50.3, 54.5, 57.3, 56.1,
        57.8, 61.0, 59.8, 60.3, 61.8, 59.5, 59.4, 59.0, 61.4, 66.8,
        68.6, 83.0, 69.2, 71.2, 72.0, 72.9, 81.4, 75.6, 77.0],
    'defense_util_rate_mfg': [
        81.6, 81.4, 79.9, 71.1, 76.6, 78.3, 75.3, 78.3, 78.3, 80.3,
        79.8, 81.0, 80.3, 77.2, 74.6, 81.2, 79.9, 78.1, 76.2, 76.1,
        74.3, 72.6, 72.6, 73.5, 73.2, 71.3, 74.4, 74.8, 71.9],
}
unit_map = {
    'defense_revenue':       '억원',
    'defense_op_profit':     '억원',
    'defense_op_margin':     '%',
    'defense_op_margin_mfg': '%',
    'defense_util_rate':     '%',
    'defense_util_rate_mfg': '%',
}
nm_map = {
    'defense_revenue':       '방산업체 매출액',
    'defense_op_profit':     '방산업체 영업이익',
    'defense_op_margin':     '방산업체 영업이익률',
    'defense_op_margin_mfg': '제조업 평균 영업이익률 (비교용)',
    'defense_util_rate':     '방산업체 가동률',
    'defense_util_rate_mfg': '제조업 평균 가동률 (비교용)',
}
sign_map = {  # +1 = 높을수록 outcome 좋음
    'defense_revenue': 1,
    'defense_op_profit': 1,
    'defense_op_margin': 1,
    'defense_op_margin_mfg': 0,  # 비교용
    'defense_util_rate': 1,
    'defense_util_rate_mfg': 0,
}

con = duckdb.connect(DB)
codes = "', '".join(data.keys())
con.execute(f"DELETE FROM indicator_panel WHERE metric_code IN ('{codes}')")
con.execute(f"DELETE FROM indicator_metadata WHERE metric_code IN ('{codes}')")

records = []
for code, vals in data.items():
    for y, v in zip(years, vals):
        if v is None: continue
        records.append(('국방', y, code, float(v),
                        'eNaraJiPyo_idx1703', unit_map[code]))

con.executemany("INSERT INTO indicator_panel (fld_nm, year, metric_code, value, source, unit) VALUES (?,?,?,?,?,?)", records)

meta = [(code, nm_map[code], 'outcome',
         f'한국방위산업진흥회 방산지정업체경영분석 — {nm_map[code]} (e-나라지표 1703)',
         'https://www.index.go.kr/unity/potal/main/EachDtlPageDetail.do?idx_cd=1703', sign_map[code])
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
