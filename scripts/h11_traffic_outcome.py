"""H11 (continued): 도로교통공단 lgStat에서 전국 교통사고 시계열 추출.

응답에 tot_acc_cnt, tot_dth_dnv_cnt 같은 전국 합계가 들어있음.
한 시도(서울 1100) × 11년치 호출로 전국 시계열 확보.

outcome:
  traffic_deaths       전국 교통사고 사망자수 (전체사고)
  traffic_accidents    전국 교통사고 발생건수 (전체사고)

분야: 교통및물류
"""
import os, sys, io, urllib.request, urllib.parse, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _env import load_env
load_env()
import duckdb
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, 'data', 'warehouse.duckdb')
RAW_DIR = os.path.join(ROOT, 'data', 'external', 'data_go_kr')
os.makedirs(RAW_DIR, exist_ok=True)
KEY = os.environ['DATA_GO_KR_KEY_ENC']

def fetch_year(year, sido='1100'):
    """한 해, 한 시도 호출. 응답에서 전국 합계만 사용.
       guGun=& (빈값) 필수 파라미터로 추가."""
    url = (f'http://apis.data.go.kr/B552061/lgStat/getRestLgStat?'
           f'serviceKey={KEY}&searchYearCd={year}&siDo={sido}&guGun='
           f'&type=json&numOfRows=300&pageNo=1')
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'}), timeout=30) as r:
            return json.loads(r.read().decode('utf-8'))
    except Exception as e:
        return {'_err': str(e)}

records = []
print('=== fetch 2015~2025 ===')
for yr in range(2015, 2026):
    cache = os.path.join(RAW_DIR, f'traffic_{yr}.json')
    if os.path.exists(cache) and os.path.getsize(cache) > 100:
        d = json.load(open(cache, encoding='utf-8'))
    else:
        d = fetch_year(yr)
        json.dump(d, open(cache,'w',encoding='utf-8'), ensure_ascii=False)
        time.sleep(0.3)
    items = d.get('items', {}).get('item', [])
    # 전체사고 분류 첫 행에서 전국 합계 추출
    natl = next((i for i in items if i.get('acc_cl_nm')=='전체사고'), None)
    if not natl:
        print(f'  {yr}: no 전체사고 row, items={len(items)}')
        continue
    tot_acc = int(natl.get('tot_acc_cnt', 0))
    tot_dth = int(natl.get('tot_dth_dnv_cnt', 0))
    tot_inj = int(natl.get('tot_injpsn_cnt', 0))
    print(f'  {yr}: 사고 {tot_acc:,}, 사망 {tot_dth:,}, 부상 {tot_inj:,}')
    records.append({'year': yr, 'accidents': tot_acc, 'deaths': tot_dth, 'injured': tot_inj})

import pandas as pd
df = pd.DataFrame(records)
df.to_csv(os.path.join(RAW_DIR, 'traffic_national_yearly.csv'), index=False, encoding='utf-8-sig')
print(f'\n저장: traffic_national_yearly.csv ({len(df)} years)')

# indicator_panel 적재
con = duckdb.connect(DB)
con.execute("DELETE FROM indicator_panel WHERE metric_code IN ('traffic_deaths','traffic_accidents')")
con.execute("DELETE FROM indicator_metadata WHERE metric_code IN ('traffic_deaths','traffic_accidents')")

panel = []
for _, r in df.iterrows():
    panel.append(('교통및물류', int(r['year']), 'traffic_deaths', float(r['deaths']), 'KOROAD_lgStat', '명'))
    panel.append(('교통및물류', int(r['year']), 'traffic_accidents', float(r['accidents']), 'KOROAD_lgStat', '건'))
con.executemany("INSERT INTO indicator_panel (fld_nm, year, metric_code, value, source, unit) VALUES (?,?,?,?,?,?)", panel)
con.executemany("INSERT INTO indicator_metadata (metric_code, metric_nm, category, description, source_url, expected_sign) VALUES (?,?,?,?,?,?)", [
    ('traffic_deaths', '교통사고 사망자수 (전국)', 'outcome',
     '도로교통공단 지자체별 대상 교통사고 통계정보 — 전체사고 전국 합계',
     'https://www.data.go.kr/data/15056770/openapi.do', -1),
    ('traffic_accidents', '교통사고 발생건수 (전국)', 'outcome',
     '도로교통공단 lgStat — 전체사고 전국 합계',
     'https://www.data.go.kr/data/15056770/openapi.do', -1),
])
print(f'적재: panel {len(panel)}, meta 2')

print('\n=== 검증 ===')
v = con.execute("""
    SELECT year, metric_code, value FROM indicator_panel
    WHERE metric_code IN ('traffic_deaths','traffic_accidents')
    ORDER BY year, metric_code
""").fetchdf()
print(v.to_string(index=False))
con.close()
