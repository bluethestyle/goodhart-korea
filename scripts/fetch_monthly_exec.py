"""VWFOEM 월별 지출집행 5년치 다운로드 + warehouse 적재.

5년 × 12월 × 63 부처 ≈ 3,780 호출 (쿼터 1만 내).
사업 단위: 단위사업(ACTV_NM), 코드(ACTV_CD)까지.
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
    sys.exit('OPENFISCAL_KEY 필요')
H_API = {'User-Agent': 'Mozilla/5.0'}
H_PORTAL = {
    'User-Agent': 'Mozilla/5.0',
    'Content-Type': 'application/json; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://www.openfiscaldata.go.kr/op/ko/sd/UOPKOSDA01',
}

def get_offc_codes(year):
    """포털 통합코드 조회로 연도별 부처 코드 사전 받기."""
    body = json.dumps({'opKoCmItgFiCdList': [{'condType':'YR_OFFC_CD','acntYr':str(year)}]}).encode('utf-8')
    req = urllib.request.Request(
        'https://www.openfiscaldata.go.kr/op/ko/cm/selectItgFiCdList.do',
        data=body, headers=H_PORTAL, method='POST')
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.loads(r.read().decode('utf-8'))
    return {it['condCd']: it['condNm'] for it in d['itgCdList'][0]}

def call_vwfoem(year, month, offc_cd, pIndex=1, pSize=1000, retries=3):
    params = {'Key': KEY, 'Type': 'json', 'pIndex': str(pIndex), 'pSize': str(pSize),
              'FSCL_YY': str(year), 'EXE_M': str(month), 'OFFC_CD': offc_cd}
    url = f'https://openapi.openfiscaldata.go.kr/VWFOEM?{urllib.parse.urlencode(params)}'
    last_err = None
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
    """한 (연도,월,부처) 조합의 모든 페이지 수집."""
    cache = os.path.join(RAW_DIR, f'{year}_{month:02d}_{offc_cd}.json')
    if os.path.exists(cache) and os.path.getsize(cache) > 5:
        return json.load(open(cache, encoding='utf-8'))
    rows = []
    for pi in range(1, 50):
        try:
            d = call_vwfoem(year, month, offc_cd, pIndex=pi)
        except Exception as e:
            return [{'_err': str(e), 'year':year,'month':month,'offc_cd':offc_cd}]
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
    print('>>> 부처 코드 사전 수집')
    codes_all = {}
    for yr in range(2020, 2027):
        try:
            c = get_offc_codes(yr)
            codes_all[yr] = c
            print(f'  {yr}: {len(c)}개')
        except Exception as e:
            print(f'  {yr}: ERR {e}')
    os.makedirs(os.path.dirname(CODE_FILE), exist_ok=True)
    json.dump(codes_all, open(CODE_FILE,'w',encoding='utf-8'), ensure_ascii=False, indent=2)

    # 모든 (year, month, offc) 조합 생성
    combos = []
    for yr in range(2020, 2027):
        codes = codes_all.get(yr, {})
        max_month = 12
        for month in range(1, max_month+1):
            for cd in codes.keys():
                combos.append((yr, month, cd))
    print(f'>>> 총 {len(combos):,} 조합. 시작.')

    all_rows = []
    done = 0
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(fetch_combo, y, m, c): (y,m,c) for y,m,c in combos}
        for f in as_completed(futs):
            y, m, c = futs[f]
            rs = f.result()
            done += 1
            if rs and not (isinstance(rs[0], dict) and rs[0].get('_err')):
                all_rows.extend(rs)
            if done % 200 == 0 or done == len(combos):
                print(f'  {done:,}/{len(combos):,}  cum_rows={len(all_rows):,}')

    print(f'>>> 총 행: {len(all_rows):,}')

    # warehouse 적재
    con = duckdb.connect(DB_PATH)
    con.execute("DROP TABLE IF EXISTS monthly_exec")
    tmp = os.path.join(ROOT, 'tmp', 'monthly_exec_load.json')
    os.makedirs(os.path.dirname(tmp), exist_ok=True)
    json.dump(all_rows, open(tmp,'w',encoding='utf-8'), ensure_ascii=False)
    con.execute(f"CREATE TABLE monthly_exec AS SELECT * FROM read_json_auto('{tmp.replace(os.sep,'/')}', maximum_object_size=200000000)")
    n = con.execute("SELECT count(*) FROM monthly_exec").fetchone()[0]
    print(f'>>> 적재: monthly_exec {n:,} rows')

    # 정수 변환
    con.execute("ALTER TABLE monthly_exec ALTER FSCL_YY TYPE INTEGER USING TRY_CAST(FSCL_YY AS INTEGER)")
    con.execute("ALTER TABLE monthly_exec ALTER EXE_M TYPE INTEGER USING TRY_CAST(EXE_M AS INTEGER)")
    con.close()
    print(f'>>> DB: {DB_PATH}')

if __name__ == '__main__':
    main()
