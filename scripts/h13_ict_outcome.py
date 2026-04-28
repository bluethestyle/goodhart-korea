"""H13: 한은 ECOS 정보통신산업 부가가치 적재 — 통신 분야 outcome.

소스: ECOS 200Y158 (정보통신산업 원계열 실질 연간)
  - 2010~2025 연 단위
  - ITEM=정보통신산업 (한국 ICT 산업 부가가치, 단위 십억원)

분야: 통신
metric: ict_value_added

분야 매핑 11→12.
"""
import os, sys, io, json, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _env import load_env
load_env()
import duckdb
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, 'data', 'warehouse.duckdb')
RAW = os.path.join(ROOT, 'data', 'external', 'bok_data')
KEY = os.environ['BOK_KEY']

# Step 1: fetch
cache = os.path.join(RAW, 'ict_value_added.json')
if os.path.exists(cache) and os.path.getsize(cache) > 100:
    rows = json.load(open(cache, encoding='utf-8'))
    print(f'cached: {len(rows)} rows')
else:
    url = f'https://ecos.bok.or.kr/api/StatisticSearch/{KEY}/json/kr/1/500/200Y158/A/1990/2025/'
    with urllib.request.urlopen(url, timeout=30) as r:
        d = json.loads(r.read().decode('utf-8'))
    rows = d.get('StatisticSearch',{}).get('row',[])
    json.dump(rows, open(cache,'w',encoding='utf-8'), ensure_ascii=False)
    print(f'fetched: {len(rows)} rows')

# Step 2: 정보통신산업 ITEM만 추출
ict_rows = [r for r in rows if r.get('ITEM_NAME1') == '정보통신산업']
print(f'정보통신산업: {len(ict_rows)}, 연도 {ict_rows[0]["TIME"]}~{ict_rows[-1]["TIME"]}')

# Step 3: indicator_panel 적재
con = duckdb.connect(DB)
con.execute("DELETE FROM indicator_panel WHERE metric_code='ict_value_added'")
con.execute("DELETE FROM indicator_metadata WHERE metric_code='ict_value_added'")

records = []
for r in ict_rows:
    yr = int(r['TIME'])
    val = float(r['DATA_VALUE'])
    records.append(('통신', yr, 'ict_value_added', val, 'BOK_200Y158', '십억원'))
con.executemany("INSERT INTO indicator_panel (fld_nm, year, metric_code, value, source, unit) VALUES (?,?,?,?,?,?)", records)
con.execute("""
    INSERT INTO indicator_metadata (metric_code, metric_nm, category, description, source_url, expected_sign)
    VALUES ('ict_value_added', '정보통신산업 부가가치 (실질, 원계열)', 'outcome',
            '한은 ECOS 200Y158 — 정보통신산업 연간 실질 부가가치',
            'https://ecos.bok.or.kr/api/...', 1)
""")
print(f'적재: {len(records)} rows')

v = con.execute("""
    SELECT year, value FROM indicator_panel WHERE metric_code='ict_value_added' ORDER BY year
""").fetchdf()
print(v.to_string(index=False))
con.close()
print('완료.')
