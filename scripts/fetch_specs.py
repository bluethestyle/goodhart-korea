"""167개 데이터셋에 대해 selectSrvDtlInfoList + selectAcolViewList 호출하여 API 명세/응답구조 수집.

Outputs:
- data/api_specs_raw.json   원시 응답 모음
- data/api_specs.json       정제된 명세
- logs/fetch_specs.log
"""
import json, sys, io, time, os, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIST_PATH = os.path.join(ROOT, 'data', 'all_apis.json')
RAW_OUT = os.path.join(ROOT, 'data', 'api_specs_raw.json')
CLEAN_OUT = os.path.join(ROOT, 'data', 'api_specs.json')
LOG_PATH = os.path.join(ROOT, 'logs', 'fetch_specs.log')

BASE = 'https://www.openfiscaldata.go.kr'
H = {
    'Content-Type': 'application/json; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': BASE + '/op/ko/ds/UOPKODSA06',
    'User-Agent': 'Mozilla/5.0',
}

def post_json(path, payload):
    body = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(BASE + path, data=body, headers=H, method='POST')
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode('utf-8'))

def fetch_one(item):
    odt_id = item['odtId']
    odt_nm = item.get('odtNm')
    out = {'odtId': odt_id, 'odtNm': odt_nm, 'srvDtl': None, 'acol': None, 'error': None}
    try:
        srv = post_json('/op/ko/sd/dtsStats/selectSrvDtlInfoList.do',
                        {'opKoSdDtsStatsDVO': {'odtId': odt_id}})
        out['srvDtl'] = srv
        # find odtSvSeq for rlsSvTyCd == 'A' (API)
        api_seq = None
        for s in (srv.get('selectSrvInfoList') or []):
            if s.get('rlsSvTyCd') == 'A':
                api_seq = s.get('odtSvSeq')
                break
        if api_seq is None:
            out['error'] = 'no API service found (rlsSvTyCd=A)'
            return out
        acol = post_json('/op/ko/sd/dtsStatsAcol/selectAcolViewList.do',
                         {'odtId': odt_id, 'rlsSvTyCd': 'A', 'odtSvSeq': str(api_seq),
                          'odtNm': odt_nm, 'paramVO': {'odtNm': odt_nm}})
        out['acol'] = acol
    except Exception as e:
        out['error'] = repr(e)
    return out

def main():
    items = json.load(open(LIST_PATH, encoding='utf-8'))
    print(f'fetching specs for {len(items)} datasets...')
    results = [None] * len(items)
    log_lines = []
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(fetch_one, it): i for i, it in enumerate(items)}
        done_n = 0
        for f in as_completed(futs):
            idx = futs[f]
            r = f.result()
            results[idx] = r
            done_n += 1
            status = 'OK' if not r['error'] else f"ERR({r['error'][:60]})"
            line = f"[{done_n:3}/{len(items)}] {r['odtId']} {r['odtNm'][:40]:40} {status}"
            log_lines.append(line)
            if done_n % 20 == 0 or done_n == len(items):
                print(line)
    json.dump(results, open(RAW_OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    open(LOG_PATH, 'w', encoding='utf-8').write('\n'.join(log_lines))

    # Build clean structure
    clean = []
    by_id = {it['odtId']: it for it in items}
    for r in results:
        base = by_id.get(r['odtId'], {})
        srv = (r.get('srvDtl') or {}).get('selectSrvDtlInfo') or {}
        acol = r.get('acol') or {}
        api_res = acol.get('selectApiRes') or {}
        req_vars = acol.get('selectApiReqVarList') or []
        out_vars = acol.get('selectApiOutputValList') or []
        clean.append({
            'odtId': r['odtId'],
            'odtNm': r['odtNm'],
            'description': base.get('odtEpl') or srv.get('odtEpl'),
            'category': srv.get('allDtaClsNm'),
            'subCategory': srv.get('dtaClsNm'),
            'dtaClsId': base.get('dtaClsId'),
            'producer': base.get('ofdMngOgNm') or srv.get('ofdMngOgNm'),
            'sourceSystem': srv.get('ognSysNm'),
            'license': srv.get('odtAvdvCndNm'),
            'updateCycleCode': base.get('dtaLoadPrdCd'),
            'serviceTypes': base.get('rlsSvIxNm'),
            'opeDt': srv.get('opeDt'),
            'apiUrl': api_res.get('dmndUrl'),
            'dailyLimit': api_res.get('apiDdDdSvLmCnt'),
            'requestParams': [
                {
                    'name': v.get('dsColId'),
                    'koName': v.get('dpColHgNm'),
                    'description': v.get('colEpl'),
                    'type': v.get('reqType'),
                    'required': '필수' in (v.get('reqType') or ''),
                } for v in req_vars
            ],
            'responseFields': [
                {
                    'order': v.get('otptOrd'),
                    'name': v.get('dsColId'),
                    'koName': v.get('dpColHgNm'),
                    'description': v.get('colEpl'),
                } for v in out_vars
            ],
            'error': r.get('error'),
        })
    json.dump(clean, open(CLEAN_OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

    ok = sum(1 for c in clean if not c['error'])
    print(f'\n완료: {ok}/{len(clean)} 성공')
    print(f'  raw  → {RAW_OUT}')
    print(f'  clean→ {CLEAN_OUT}')
    print(f'  log  → {LOG_PATH}')

if __name__ == '__main__':
    main()
