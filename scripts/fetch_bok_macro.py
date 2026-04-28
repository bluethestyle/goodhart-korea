"""한은 ECOS에서 거시 통제변수 fetch — H6 외생 cycle 통제용.

수집:
  - CPI (소비자물가지수)         901Y009 / ITEM=0 / Annual / 1965~2025
  - 경제성장률 (실질 GDP)        200Y001 또는 다른 코드 / Annual
  - 환율 (원/달러 연평균)        731Y001 / Annual
"""
import os, sys, io, json, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _env import load_env
load_env()
import duckdb, pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, 'data', 'external', 'bok_data')
os.makedirs(RAW, exist_ok=True)
DB = os.path.join(ROOT, 'data', 'warehouse.duckdb')
KEY = os.environ['BOK_KEY']

def fetch(stat_code, cycle, start, end, item_code='0'):
    url = (f'https://ecos.bok.or.kr/api/StatisticSearch/{KEY}/json/kr/1/1000/'
           f'{stat_code}/{cycle}/{start}/{end}/{item_code}/')
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.loads(r.read().decode('utf-8'))

# 1. CPI 연단위 1990~2025
print('=== CPI (901Y009 / ITEM=0 / A) ===')
d = fetch('901Y009', 'A', '1990', '2025', '0')
rows = d.get('StatisticSearch',{}).get('row',[])
print(f'  rows: {len(rows)}')
if rows:
    print(f'  first: TIME={rows[0].get("TIME")}, DATA_VALUE={rows[0].get("DATA_VALUE")}, UNIT_NAME={rows[0].get("UNIT_NAME")}')
    print(f'  last:  TIME={rows[-1].get("TIME")}, DATA_VALUE={rows[-1].get("DATA_VALUE")}')
json.dump(d, open(f'{RAW}/cpi_annual.json','w',encoding='utf-8'), ensure_ascii=False)

# 2. 환율 731Y001 (원/달러 연단위)
print('\n=== 환율 (731Y001 / 연) ===')
d = fetch('731Y001', 'A', '1990', '2025', '0000001')  # USD = 0000001 가능성
rows = d.get('StatisticSearch',{}).get('row',[])
if not rows:
    # fall back: ITEM=0 시도
    d = fetch('731Y001', 'A', '1990', '2025', '0')
    rows = d.get('StatisticSearch',{}).get('row',[])
print(f'  rows: {len(rows)}')
if rows:
    print(f'  first: {rows[0]}')
json.dump(d, open(f'{RAW}/exchange_rate.json','w',encoding='utf-8'), ensure_ascii=False)

# 3. GDP 성장률 — 200Y005 또는 200Y010 시도
print('\n=== GDP 성장률 ===')
for code in ['200Y005','200Y010','200Y013','111Y008','100Y001','111Y007']:
    try:
        d = fetch(code, 'A', '1990', '2025', '0')
        rows = d.get('StatisticSearch',{}).get('row',[])
        if rows:
            print(f'  [{code}] rows={len(rows)}, first: {rows[0].get("ITEM_NAME1","")} {rows[0].get("TIME")}={rows[0].get("DATA_VALUE")}')
            json.dump(d, open(f'{RAW}/gdp_{code}.json','w',encoding='utf-8'), ensure_ascii=False)
            break
    except Exception as e:
        print(f'  [{code}] err: {e}')

# 4. 보강 — 200Y001 항목 정확히 알기 위해 기간 정보 활용
print('\n=== 통계 검색 (성장률 키워드) ===')
url = f'https://ecos.bok.or.kr/api/StatisticTableList/{KEY}/json/kr/1/100/'
with urllib.request.urlopen(url, timeout=20) as r:
    d = json.loads(r.read().decode('utf-8'))
tables = d.get('StatisticTableList',{}).get('row',[])
gdp_tables = [t for t in tables if '성장률' in (t.get('STAT_NAME','') or '') or 'GDP' in (t.get('STAT_NAME','') or '')]
print(f'  GDP 관련 table: {len(gdp_tables)}')
for t in gdp_tables[:10]:
    print(f'    {t.get("STAT_CODE"):12s}  {t.get("STAT_NAME","")[:60]}  CYCLE={t.get("CYCLE")}')
