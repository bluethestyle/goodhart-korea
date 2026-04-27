"""열린재정 OPEN API → DuckDB 웨어하우스 구축.

테이블:
  - expenditure_budget : 세출 세부사업 (본예산 + 추경 모든 회차)  ★ 메인
  - revenue_budget     : 세입 (본예산 + 추경 모든 회차)
  - debt_monthly       : 월별 국가채무
  - debt_yearly        : 연도별 국가채무 (D1)

raw JSON 백업: data/budget/raw/{table}/{key}.json
DuckDB 파일:   data/warehouse.duckdb
"""
import os, json, sys, io, time, urllib.request, urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
import duckdb

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(ROOT, 'data', 'budget', 'raw')
DB_PATH = os.path.join(ROOT, 'data', 'warehouse.duckdb')
KEY = os.environ.get('OPENFISCAL_KEY')
if not KEY:
    sys.exit('환경변수 OPENFISCAL_KEY 가 필요합니다.  예: export OPENFISCAL_KEY=...')
BASE = 'https://openapi.openfiscaldata.go.kr'
H = {'User-Agent': 'Mozilla/5.0'}
PSIZE = 1000

def fetch_page(api, page, **params):
    p = {'Key': KEY, 'Type': 'json', 'pIndex': str(page), 'pSize': str(PSIZE), **params}
    url = f'{BASE}/{api}?{urllib.parse.urlencode(p)}'
    req = urllib.request.Request(url, headers=H)
    with urllib.request.urlopen(req, timeout=60) as r:
        d = json.loads(r.read().decode('utf-8'))
        if isinstance(d, str): d = json.loads(d)
    return d

def fetch_all(api, label, **params):
    """모든 페이지 수집. (year, dgr) 등의 조합별 라벨로 캐싱."""
    out_dir = os.path.join(RAW_DIR, api)
    os.makedirs(out_dir, exist_ok=True)
    cache = os.path.join(out_dir, f'{label}.json')
    if os.path.exists(cache) and os.path.getsize(cache) > 5:
        return json.load(open(cache, encoding='utf-8'))
    all_rows = []
    for pi in range(1, 50):
        d = fetch_page(api, pi, **params)
        if api in d and len(d[api]) >= 2:
            head = d[api][0].get('head') or []
            cnt = next((h.get('list_total_count') for h in head if isinstance(h, dict) and 'list_total_count' in h), 0)
            rows = d[api][1].get('row') or []
        elif 'RESULT' in d:
            cnt, rows = 0, []
        else:
            cnt, rows = 0, []
        all_rows.extend(rows)
        if not rows or len(rows) < PSIZE:
            break
        time.sleep(0.1)
    json.dump(all_rows, open(cache, 'w', encoding='utf-8'), ensure_ascii=False)
    return all_rows

def fetch_combo(api, label, **params):
    rows = fetch_all(api, label, **params)
    for r in rows:
        r['_label'] = label
    return label, rows

# Plan ----------------------------------------------------------------------
EXPENDITURE_API = 'ExpenditureBudgetAdd7'
REVENUE_API = 'BudgetRevenuesAdd2'

YEARS = [str(y) for y in range(2020, 2027)]   # 2020~2026
DGRS = ['0','1','2','3']                        # 본예산 + 추경 1~3

def collect_panel(api):
    """(year × dgr) 조합 모두 수집."""
    print(f'\n>>> {api} 수집 시작')
    combos = [(y, d) for y in YEARS for d in DGRS]
    results = {}
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(fetch_combo, api, f'{y}_{d}', FSCL_YY=y, SBUDG_DGR=d): (y, d) for y, d in combos}
        for f in as_completed(futs):
            label, rows = f.result()
            if rows:
                results[label] = rows
                print(f'  {label}: {len(rows):>6,} rows')
    total = sum(len(v) for v in results.values())
    print(f'  >> {api} 합계: {total:,} rows')
    return results

def collect_debt_monthly():
    api = 'GovernmentDebtMonth'
    print(f'\n>>> {api} 수집 시작')
    out = []
    for yr in range(2015, 2027):
        for m in range(1, 13):
            label = f'{yr}_{m:02d}'
            try:
                rows = fetch_all(api, label, OJ_YY=str(yr), OJ_M=str(m))
            except Exception as e:
                rows = []
            if rows:
                out.extend(rows)
    print(f'  rows={len(out)}')
    return out

def collect_debt_yearly():
    api = 'GovernmentDebtYear'
    print(f'\n>>> {api} 수집 시작')
    out = []
    for yr in range(2010, 2027):
        try:
            rows = fetch_all(api, str(yr), OJ_YY=str(yr))
        except: rows=[]
        if rows: out.extend(rows)
    print(f'  rows={len(out)}')
    return out

# Main ----------------------------------------------------------------------
def main():
    exp = collect_panel(EXPENDITURE_API)
    rev = collect_panel(REVENUE_API)
    debt_m = collect_debt_monthly()
    debt_y = collect_debt_yearly()

    # Flatten panels
    exp_rows = [r for v in exp.values() for r in v]
    rev_rows = [r for v in rev.values() for r in v]

    # Build DuckDB
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    con = duckdb.connect(DB_PATH)

    def load(name, rows):
        if not rows:
            print(f'[skip] {name}: 빈 데이터')
            return
        # JSON → DataFrame via duckdb itself
        tmp = os.path.join(ROOT, 'tmp', f'{name}_load.json')
        os.makedirs(os.path.dirname(tmp), exist_ok=True)
        json.dump(rows, open(tmp, 'w', encoding='utf-8'), ensure_ascii=False)
        con.execute(f"CREATE TABLE {name} AS SELECT * FROM read_json_auto('{tmp.replace(os.sep,'/')}', maximum_object_size=200000000)")
        n = con.execute(f"SELECT count(*) FROM {name}").fetchone()[0]
        cols = [c[0] for c in con.execute(f"DESCRIBE {name}").fetchall()]
        print(f'[load] {name}: {n:,} rows, {len(cols)} cols')

    load('expenditure_budget', exp_rows)
    load('revenue_budget',     rev_rows)
    load('debt_monthly',       debt_m)
    load('debt_yearly',        debt_y)

    # 메타 카탈로그 — 이미 수집된 JSON 그대로 적재
    api_specs_path = os.path.join(ROOT, 'data', 'api_specs.json').replace(os.sep,'/')
    kodas_path     = os.path.join(ROOT, 'data', 'kodas_catalog.json').replace(os.sep,'/')
    if os.path.exists(api_specs_path):
        con.execute(f"CREATE TABLE openapi_catalog AS SELECT * FROM read_json_auto('{api_specs_path}', maximum_object_size=200000000)")
        n = con.execute("SELECT count(*) FROM openapi_catalog").fetchone()[0]
        print(f'[load] openapi_catalog: {n:,} rows  (167개 Open API 명세)')
    if os.path.exists(kodas_path):
        con.execute(f"CREATE TABLE kodas_catalog AS SELECT * FROM read_json_auto('{kodas_path}', maximum_object_size=200000000)")
        n = con.execute("SELECT count(*) FROM kodas_catalog").fetchone()[0]
        print(f'[load] kodas_catalog: {n:,} rows  (KODAS 데이터 카탈로그 메타)')

    # 정수형 변환 (FSCL_YY / SBUDG_DGR)
    for tbl in ['expenditure_budget', 'revenue_budget']:
        if con.execute(f"SELECT count(*) FROM information_schema.tables WHERE table_name='{tbl}'").fetchone()[0]:
            con.execute(f"ALTER TABLE {tbl} ALTER FSCL_YY TYPE INTEGER USING TRY_CAST(FSCL_YY AS INTEGER)")
            con.execute(f"ALTER TABLE {tbl} ALTER SBUDG_DGR TYPE INTEGER USING TRY_CAST(SBUDG_DGR AS INTEGER)")

    # 인덱스용 view
    con.execute("""
        CREATE OR REPLACE VIEW v_panel_summary AS
        SELECT FSCL_YY, SBUDG_DGR, count(*) AS rows, sum(Y_YY_DFN_KCUR_AMT)/1e9 AS total_chowon
        FROM expenditure_budget
        GROUP BY FSCL_YY, SBUDG_DGR
        ORDER BY FSCL_YY, SBUDG_DGR
    """)
    print('\n=== expenditure_budget 패널 요약 ===')
    for r in con.execute("SELECT * FROM v_panel_summary").fetchall():
        print(f'  {r[0]} 회차{r[1]}: {r[2]:>6,} rows  {r[3]:>7.1f} 조원')

    print('\n=== revenue_budget 패널 요약 ===')
    rev_sum = con.execute("""
        SELECT FSCL_YY, SBUDG_DGR, count(*) AS rows
        FROM revenue_budget GROUP BY FSCL_YY, SBUDG_DGR ORDER BY FSCL_YY, SBUDG_DGR
    """).fetchall()
    for r in rev_sum:
        print(f'  {r[0]} 회차{r[1]}: {r[2]:>6,} rows')

    print(f'\n월별 채무 행 수: {con.execute("SELECT count(*) FROM debt_monthly").fetchone()[0]}')
    print(f'연도별 채무 행 수: {con.execute("SELECT count(*) FROM debt_yearly").fetchone()[0]}')

    print(f'\nDB 경로: {DB_PATH} ({os.path.getsize(DB_PATH)/1e6:.1f} MB)')
    con.close()

if __name__ == '__main__':
    main()
