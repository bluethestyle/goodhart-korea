"""VWFOEM 월별 지출집행 2007~2019 추가 다운로드.

fetch_monthly_exec.py의 확장: 기존 monthly_exec 테이블을 DROP하지 않고
2007~2019 데이터만 추가로 fetch + INSERT.

사용:
  export OPENFISCAL_KEY=...
  python scripts/fetch_monthly_exec_2007_2019.py

캐시: data/budget/raw/VWFOEM/{year}_{month:02d}_{offc_cd}.json
DB:   data/warehouse.duckdb (monthly_exec append)
"""
import os, sys, io, json, time, urllib.request, urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
import duckdb

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(ROOT, 'data', 'budget', 'raw', 'VWFOEM')
CODE_FILE = os.path.join(ROOT, 'data', 'budget', 'raw', 'codes', 'offc_codes.json')
DB_PATH = os.path.join(ROOT, 'data', 'warehouse.duckdb')
os.makedirs(RAW_DIR, exist_ok=True)

KEY = os.environ.get('OPENFISCAL_KEY')
if not KEY:
    sys.exit('OPENFISCAL_KEY 필요. export OPENFISCAL_KEY=... 후 재시도.')

H_API = {'User-Agent': 'Mozilla/5.0'}
H_PORTAL = {
    'User-Agent': 'Mozilla/5.0',
    'Content-Type': 'application/json; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://www.openfiscaldata.go.kr/op/ko/sd/UOPKOSDA01',
}

YEARS_NEW = list(range(2007, 2020))   # 2007~2019

def get_offc_codes(year):
    body = json.dumps({'opKoCmItgFiCdList':[{'condType':'YR_OFFC_CD','acntYr':str(year)}]}).encode('utf-8')
    req = urllib.request.Request(
        'https://www.openfiscaldata.go.kr/op/ko/cm/selectItgFiCdList.do',
        data=body, headers=H_PORTAL, method='POST')
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.loads(r.read().decode('utf-8'))
    return {it['condCd']: it['condNm'] for it in d['itgCdList'][0]}

def call_vwfoem(year, month, offc_cd, pIndex=1, pSize=1000, retries=3):
    params = {'Key': KEY, 'Type':'json', 'pIndex':str(pIndex), 'pSize':str(pSize),
              'FSCL_YY':str(year), 'EXE_M':str(month), 'OFFC_CD':offc_cd}
    url = f'https://openapi.openfiscaldata.go.kr/VWFOEM?{urllib.parse.urlencode(params)}'
    for _ in range(retries):
        try:
            req = urllib.request.Request(url, headers=H_API)
            with urllib.request.urlopen(req, timeout=60) as r:
                d = json.loads(r.read().decode('utf-8'))
                if isinstance(d, str): d = json.loads(d)
            return d
        except Exception as e:
            last_err = e
            time.sleep(2)
    raise last_err

def fetch_combo(year, month, offc_cd):
    cache = os.path.join(RAW_DIR, f'{year}_{month:02d}_{offc_cd}.json')
    if os.path.exists(cache) and os.path.getsize(cache) > 5:
        return json.load(open(cache, encoding='utf-8'))
    rows = []
    for pi in range(1, 50):
        try:
            d = call_vwfoem(year, month, offc_cd, pIndex=pi)
        except Exception as e:
            return [{'_err':str(e),'year':year,'month':month,'offc_cd':offc_cd}]
        if 'VWFOEM' in d:
            page_rows = d['VWFOEM'][1].get('row') or []
            if not page_rows: break
            rows.extend(page_rows)
            if len(page_rows) < 1000: break
        else:
            break
        time.sleep(0.05)
    json.dump(rows, open(cache,'w',encoding='utf-8'), ensure_ascii=False)
    return rows

def main():
    # 기존 코드 사전 로드 또는 새로 받기
    if os.path.exists(CODE_FILE):
        codes_all = {int(k):v for k,v in json.load(open(CODE_FILE,encoding='utf-8')).items()}
    else:
        codes_all = {}

    print('>>> 부처 코드 사전 (2007~2019)')
    for yr in YEARS_NEW:
        if yr in codes_all and codes_all[yr]:
            print(f'  {yr}: {len(codes_all[yr])}개 (캐시)')
            continue
        try:
            c = get_offc_codes(yr)
            codes_all[yr] = c
            print(f'  {yr}: {len(c)}개')
        except Exception as e:
            print(f'  {yr}: ERR {e} → 2010 코드로 대체')
            codes_all[yr] = codes_all.get(2010) or codes_all.get(2020) or {}
    json.dump(codes_all, open(CODE_FILE,'w',encoding='utf-8'), ensure_ascii=False, indent=2)

    combos = []
    for yr in YEARS_NEW:
        codes = codes_all.get(yr, {})
        for month in range(1, 13):
            for cd in codes.keys():
                combos.append((yr, month, cd))
    print(f'>>> 총 {len(combos):,} 조합 (2007~2019)')

    new_rows = []
    done = 0
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(fetch_combo, y, m, c): (y,m,c) for y,m,c in combos}
        for f in as_completed(futs):
            y, m, c = futs[f]
            rs = f.result()
            done += 1
            if rs and not (isinstance(rs[0], dict) and rs[0].get('_err')):
                new_rows.extend(rs)
            if done % 500 == 0 or done == len(combos):
                print(f'  {done:,}/{len(combos):,}  cum_rows={len(new_rows):,}')

    print(f'>>> 신규 행: {len(new_rows):,}')

    # warehouse 적재 — 기존 monthly_exec에 append (2007~2019만)
    con = duckdb.connect(DB_PATH)
    existing_cols = [r[0] for r in con.execute("DESCRIBE monthly_exec").fetchall()]
    print(f'>>> 기존 monthly_exec 컬럼: {len(existing_cols)}')

    tmp = os.path.join(ROOT, 'tmp', 'monthly_exec_2007_2019.json')
    os.makedirs(os.path.dirname(tmp), exist_ok=True)
    json.dump(new_rows, open(tmp,'w',encoding='utf-8'), ensure_ascii=False)
    con.execute(f"""CREATE TEMP TABLE _new AS
                    SELECT * FROM read_json_auto('{tmp.replace(os.sep,'/')}',
                    maximum_object_size=200000000)""")
    # 컬럼 정렬 후 INSERT
    new_cols = [r[0] for r in con.execute("DESCRIBE _new").fetchall()]
    common = [c for c in existing_cols if c in new_cols]
    sel = ','.join([f"TRY_CAST({c} AS {dt}) AS {c}" if c in ('FSCL_YY','EXE_M') else c
                    for c, dt in zip(existing_cols, ['INTEGER' if c in ('FSCL_YY','EXE_M') else 'VARCHAR'
                                                      for c in existing_cols])])
    # 단순 모드: 공통 컬럼만 INSERT
    common_sel = ','.join(common)
    con.execute(f"INSERT INTO monthly_exec ({common_sel}) SELECT {common_sel} FROM _new")
    n = con.execute("SELECT COUNT(*) FROM monthly_exec").fetchone()[0]
    n_new = con.execute("SELECT COUNT(*) FROM monthly_exec WHERE FSCL_YY BETWEEN 2007 AND 2019").fetchone()[0]
    print(f'>>> 적재 후: monthly_exec 총 {n:,} rows (2007~2019: {n_new:,})')
    con.close()

if __name__ == '__main__':
    main()
