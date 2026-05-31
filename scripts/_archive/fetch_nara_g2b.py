"""나라장터 공공데이터개방표준서비스 OPEN API 수집기.

키 활성화 확인 후 IITP 등 출연기관 발주 5년치 수집 → DuckDB.

Usage:
  export NARA_KEY='<encoded key>'   # data.go.kr serviceKey (encoded form)
  python scripts/fetch_nara_g2b.py --probe         # 1건 호출 검증
  python scripts/fetch_nara_g2b.py --recipient IITP    # IITP 발주 풀세트
"""
import os, sys, io, time, json, argparse, urllib.request, urllib.parse
from datetime import datetime, timedelta

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(ROOT, 'data', 'g2b', 'raw')
os.makedirs(RAW_DIR, exist_ok=True)

KEY = os.environ.get('NARA_KEY')
if not KEY:
    sys.exit('NARA_KEY 환경변수 필요. data.go.kr 발급 키(인코딩 형식).')

BASE = 'https://apis.data.go.kr/1230000/ao/PubDataOpnStdService'
H = {'User-Agent': 'Mozilla/5.0'}

OPS = {
    'bid':    'getDataSetOpnStdBidPblancInfo',     # 입찰공고
    'scsbid': 'getDataSetOpnStdScsbidInfo',        # 낙찰결과
    'cntrct': 'getDataSetOpnStdCntrctInfo',        # 계약체결
}

def call(op, **params):
    """data.go.kr는 serviceKey 인코딩 형태를 그대로 URL에 박아 보냄."""
    qs = urllib.parse.urlencode(params)
    url = f'{BASE}/{op}?serviceKey={KEY}&{qs}'
    req = urllib.request.Request(url, headers=H)
    with urllib.request.urlopen(req, timeout=60) as r:
        body = r.read().decode('utf-8')
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return {'_raw': body[:500]}

def probe():
    """1건 호출 → 활성화 검증."""
    print(f'BASE: {BASE}')
    print(f'KEY (앞 20자): {KEY[:20]}...\n')
    for label, op in OPS.items():
        try:
            d = call(op, pageNo='1', numOfRows='1', type='json',
                     inqryDiv='1',
                     inqryBgnDt='202604010000', inqryEndDt='202604020000')
            print(f'  [{label}] {op}: OK — keys={list(d.keys()) if isinstance(d,dict) else type(d).__name__}')
            print(f'    snippet: {json.dumps(d, ensure_ascii=False)[:300]}')
        except urllib.error.HTTPError as e:
            print(f'  [{label}] {op}: HTTP {e.code} — {e.reason}')
        except Exception as e:
            print(f'  [{label}] {op}: ERR {e}')

def fetch_period(op, bgn_yyyymmdd, end_yyyymmdd, **filters):
    """기간 분할(월 단위) 수집. data.go.kr는 보통 1개월 이상은 잘림."""
    start = datetime.strptime(bgn_yyyymmdd, '%Y%m%d')
    end = datetime.strptime(end_yyyymmdd, '%Y%m%d')
    all_rows, page_n = [], 0
    cur = start
    while cur <= end:
        nxt = min(cur + timedelta(days=30), end)
        bgn_str = cur.strftime('%Y%m%d') + '0000'
        end_str = nxt.strftime('%Y%m%d') + '2359'
        for pi in range(1, 100):
            d = call(op, pageNo=str(pi), numOfRows='999', type='json',
                     inqryDiv='1', inqryBgnDt=bgn_str, inqryEndDt=end_str,
                     **filters)
            page_n += 1
            try:
                items = d['response']['body']['items']
                if isinstance(items, dict): items = items.get('item', [])
            except (KeyError, TypeError):
                break
            if not items:
                break
            all_rows.extend(items)
            if len(items) < 999:
                break
            time.sleep(0.05)
        print(f'  {bgn_str[:8]}~{end_str[:8]}: cum={len(all_rows)}')
        cur = nxt + timedelta(days=1)
    return all_rows

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--probe', action='store_true')
    ap.add_argument('--op', default='cntrct', choices=list(OPS))
    ap.add_argument('--bgn', default='20210101')
    ap.add_argument('--end', default='20260427')
    ap.add_argument('--keyword', default=None,
                    help='발주기관/제목 키워드 — API 파라미터에 따라 후필터 적용')
    ap.add_argument('--out', default=None)
    args = ap.parse_args()

    if args.probe:
        probe()
        return

    op = OPS[args.op]
    print(f'>>> {op}  {args.bgn}~{args.end}')
    rows = fetch_period(op, args.bgn, args.end)
    if args.keyword:
        kw = args.keyword
        before = len(rows)
        rows = [r for r in rows
                if kw in (str(r.get('dminsttNm') or '') + str(r.get('bidNtceNm') or '')
                          + str(r.get('cntrctNm') or '') + str(r.get('cntrctInsttNm') or ''))]
        print(f'키워드 "{kw}" 필터: {before} → {len(rows)}')

    out = args.out or os.path.join(RAW_DIR, f'{args.op}_{args.bgn}_{args.end}.json')
    json.dump(rows, open(out, 'w', encoding='utf-8'), ensure_ascii=False)
    print(f'저장: {out} ({len(rows)} rows)')

if __name__ == '__main__':
    main()
