"""KOSIS 다운로드 데이터를 분야별 outcome으로 정규화 → indicator_panel 적재.

처리:
  - 보건 → DT_1B41 간이생명표 → 0세 기대수명 (life_expectancy)
  - 문화관광 → DT_113_STBL_1027329 → 방한 횟수 합계 (tourists_total)
  - 산업·중기 → DT_1JH20201 → 전산업생산지수 (전산업) (industry_production_index)
"""
import os, sys, io, json, duckdb
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, 'data', 'warehouse.duckdb')

con = duckdb.connect(DB)

# 기존 outcome 모두 비우기 (재실행 가능)
con.execute("DELETE FROM indicator_panel WHERE source LIKE 'KOSIS_%'")
con.execute("DELETE FROM indicator_metadata WHERE category='outcome'")

added_panel = []
added_meta  = []

# === 1. 보건 — DT_1B41 간이생명표 → 기대수명 (전체, 0세) ===
data = json.load(open(os.path.join(ROOT, 'data','external','kosis_data','life_expectancy.json'), encoding='utf-8'))
# ITM_NM '기대여명' / C1 '0' (0세) / 전체 (남녀 합계)
# 0세 기대여명 (전체) — C1='0' (0세), ITM_NM에 '기대여명' + '(전체)' 포함
le_rows = [r for r in data
           if r.get('ITM_NM') == '기대여명(전체)' and r.get('C1_NM') == '0']
print(f'[보건] life_expectancy 행수: {len(le_rows)}')
for r in le_rows:
    try:
        added_panel.append(('보건', int(r['PRD_DE']), 'life_expectancy', float(r['DT']), 'KOSIS_DT_1B41', '세'))
    except: pass
added_meta.append(('life_expectancy', '0세 기대수명', 'outcome',
                   '0세 기대여명(전체) — 간이생명표(5세별)',
                   'https://kosis.kr/statHtml/statHtml.do?orgId=101&tblId=DT_1B41', -1))

# === 2. 문화관광 — DT_113_STBL_1027329 방한 횟수 → 사례수 합계 ===
data = json.load(open(os.path.join(ROOT, 'data','external','kosis_data','tourists.json'), encoding='utf-8'))
# C1='131021219211.001' = 전체 분류, ITM_NM='사례수'
tt_rows = [r for r in data if r.get('C1')=='131021219211.001' and r.get('ITM_NM')=='사례수']
print(f'[문화·관광] tourists_total 행수: {len(tt_rows)}')
for r in tt_rows:
    try:
        added_panel.append(('문화및관광', int(r['PRD_DE']), 'tourists_sample', float(r['DT']), 'KOSIS_DT_113_STBL_1027329', '명'))
    except: pass
added_meta.append(('tourists_sample', '방한 외래관광객 표본수', 'outcome',
                   '외래관광객조사 — 전체 표본 사례수',
                   'https://kosis.kr/statHtml/statHtml.do?orgId=113&tblId=DT_113_STBL_1027329', -1))

# === 3. 산업·중기 — DT_1JH20201 전산업생산지수 (전산업) ===
data = json.load(open(os.path.join(ROOT, 'data','external','kosis_data','industrial_production.json'), encoding='utf-8'))
# C1='0' = 전산업
ip_rows = [r for r in data if r.get('C1')=='0' and r.get('ITM_NM')=='원지수']
print(f'[산업·중기] industrial_production_index 행수: {len(ip_rows)}')
for r in ip_rows:
    try:
        added_panel.append(('산업·중소기업및에너지', int(r['PRD_DE']), 'industry_production_index', float(r['DT']), 'KOSIS_DT_1JH20201', 'index_2020=100'))
    except: pass
added_meta.append(('industry_production_index', '전산업생산지수 (원지수)', 'outcome',
                   '전산업생산지수, 2020=100',
                   'https://kosis.kr/statHtml/statHtml.do?orgId=101&tblId=DT_1JH20201', -1))

# 적재
con.executemany(
    "INSERT INTO indicator_panel (fld_nm, year, metric_code, value, source, unit) VALUES (?, ?, ?, ?, ?, ?)",
    added_panel
)
con.executemany(
    "INSERT INTO indicator_metadata (metric_code, metric_nm, category, description, source_url, expected_sign) VALUES (?, ?, ?, ?, ?, ?)",
    added_meta
)
print(f'\n적재: panel {len(added_panel)} 행, metadata {len(added_meta)} 항목')

# 검증
print('\n=== outcome 패널 확인 ===')
df = con.execute("""
    SELECT p.fld_nm, p.year, p.metric_code, p.value, p.unit, p.source
    FROM indicator_panel p
    JOIN indicator_metadata m USING (metric_code)
    WHERE m.category='outcome'
    ORDER BY metric_code, year
""").fetchdf()
print(df.to_string(index=False))
con.close()
