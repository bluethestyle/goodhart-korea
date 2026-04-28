"""KOSIS statisticsList.do 트리 재귀 탐색 → 통계표 사전 구축.

7개 vwCd (서비스뷰):
  MT_ZTITLE      국내통계 주제별
  MT_OTITLE      국내통계 기관별
  MT_GTITLE01    e-지방지표(주제별)
  MT_GTITLE02    e-지방지표(지역별)
  MT_RTITLE      국제통계
  MT_TM1_TITLE   대상별통계
  MT_TM2_TITLE   이슈별통계

각 vw에서 parentId='A'(또는 이외) 시작점부터 재귀 — LIST_ID 있으면 분류, 없으면 통계표.

산출:
  data/external/kosis_catalog.json       전체 트리 + 통계표
  warehouse.duckdb / kosis_tables 테이블  검색 가능한 통계표 사전
"""
import os, sys, io, json, time, urllib.request, urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
import duckdb

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'external'); os.makedirs(OUT_DIR, exist_ok=True)
DB = os.path.join(ROOT, 'data', 'warehouse.duckdb')

KEY = os.environ.get('KOSIS_KEY') or 'ZTBmMWE5NDZlYjQ3MzkyZTg0YWFjOWNmNDBhNTIxZjc='
H = {'User-Agent': 'Mozilla/5.0'}

VW_CODES = {
    'MT_ZTITLE':    '국내통계 주제별',
    'MT_OTITLE':    '국내통계 기관별',
    'MT_GTITLE01':  'e-지방지표 주제별',
    'MT_GTITLE02':  'e-지방지표 지역별',
    'MT_RTITLE':    '국제통계',
    'MT_TM1_TITLE': '대상별통계',
    'MT_TM2_TITLE': '이슈별통계',
}

def call_list(vwCd, parentId, retries=3):
    # 핵심: 파라미터명은 'parentListId' (parentId 아님)
    p = {'method': 'getList', 'apiKey': KEY, 'vwCd': vwCd, 'parentListId': parentId,
         'format': 'json', 'jsonVD': 'Y'}
    qs = urllib.parse.urlencode(p)
    url = f'https://kosis.kr/openapi/statisticsList.do?{qs}'
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers=H)
            with urllib.request.urlopen(req, timeout=30) as r:
                d = json.loads(r.read().decode('utf-8'))
            return d
        except Exception as e:
            if i == retries-1: return {'_err': str(e)}
            time.sleep(2)
    return {'_err': 'unknown'}

DEFAULT_START_IDS = (
    'A','B','C','D','E','F','G',
    'H','H1','H2','H3',
    'I','I1','I2','I3',
    'J','J1','J2','J3',
    'K','K1','K2',
    'L','L1','L2',
    'M','M1','M2',
    'N','N1','N2','N3',
    'O','P','Q','R','S','T','U','V','W','X','Y','Z',
)
def crawl(vwCd, start_ids=DEFAULT_START_IDS):
    """vwCd별 트리 재귀 탐색."""
    seen_lists = set()
    tables = []  # (TBL_ID, ORG_ID, TBL_NM, path)
    queue = [(s, '') for s in start_ids]
    visited = set()

    while queue:
        # 동시 4 worker
        batch = queue[:8]; queue = queue[8:]
        with ThreadPoolExecutor(max_workers=4) as ex:
            futs = {ex.submit(call_list, vwCd, pid): (pid, path) for pid, path in batch if pid not in visited}
            for f in as_completed(futs):
                pid, path = futs[f]
                visited.add(pid)
                d = f.result()
                if not isinstance(d, list):
                    continue
                for item in d:
                    list_id = item.get('LIST_ID')
                    list_nm = item.get('LIST_NM')
                    tbl_id  = item.get('TBL_ID')
                    tbl_nm  = item.get('TBL_NM')
                    org_id  = item.get('ORG_ID')
                    if list_id and list_id not in seen_lists:
                        seen_lists.add(list_id)
                        new_path = f'{path} > {list_nm}' if path else list_nm
                        queue.append((list_id, new_path))
                    if tbl_id:
                        tables.append({
                            'vwCd': vwCd, 'TBL_ID': tbl_id, 'ORG_ID': org_id,
                            'TBL_NM': tbl_nm, 'path': path,
                        })
    return tables

def main():
    print(f'KEY: {KEY[:20]}...')
    print('vwCd 7종 트리 탐색 시작\n')
    all_tables = []
    for vw, vw_nm in VW_CODES.items():
        t0 = time.time()
        print(f'[{vw}] {vw_nm} 시작...')
        try:
            tables = crawl(vw)
            all_tables.extend(tables)
            print(f'  {vw}: {len(tables):,} 통계표 ({time.time()-t0:.0f}s)')
        except Exception as e:
            print(f'  {vw}: ERR {e}')

    # 중복 제거 (TBL_ID + ORG_ID)
    seen = set()
    unique = []
    for t in all_tables:
        k = (t['ORG_ID'], t['TBL_ID'])
        if k in seen: continue
        seen.add(k)
        unique.append(t)
    print(f'\n중복 제거: {len(all_tables):,} → {len(unique):,}')

    # 저장
    out_path = os.path.join(OUT_DIR, 'kosis_catalog.json')
    json.dump(all_tables, open(out_path, 'w', encoding='utf-8'), ensure_ascii=False)
    print(f'JSON 저장: {out_path}')

    # warehouse 적재
    con = duckdb.connect(DB)
    con.execute("DROP TABLE IF EXISTS kosis_tables")
    tmp = os.path.join(ROOT, 'tmp', 'kosis_tables_load.json')
    os.makedirs(os.path.dirname(tmp), exist_ok=True)
    json.dump(unique, open(tmp,'w',encoding='utf-8'), ensure_ascii=False)
    con.execute(f"CREATE TABLE kosis_tables AS SELECT * FROM read_json_auto('{tmp.replace(os.sep,'/')}', maximum_object_size=200000000)")
    n = con.execute("SELECT count(*) FROM kosis_tables").fetchone()[0]
    print(f'warehouse 적재: kosis_tables {n:,} rows')

    # vwCd 분포
    print('\nvwCd 분포:')
    for r in con.execute("SELECT vwCd, count(*) FROM kosis_tables GROUP BY vwCd ORDER BY count(*) DESC").fetchall():
        print(f'  {r[0]}: {r[1]:,}')

    con.close()

if __name__ == '__main__':
    main()
