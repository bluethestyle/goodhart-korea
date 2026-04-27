"""KODAS 제공 데이터 목록 1,707건 수집 + 정제."""
import json, sys, io, os, urllib.request, csv

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_OUT = os.path.join(ROOT, 'data', 'kodas_catalog_raw.json')
CLEAN_OUT = os.path.join(ROOT, 'data', 'kodas_catalog.json')
CSV_OUT = os.path.join(ROOT, 'data', 'kodas_catalog.csv')

URL = 'https://www.openfiscaldata.go.kr/op/ko/sb/selectCatalogList.do'
HEADERS = {
    'Content-Type': 'application/json; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://www.openfiscaldata.go.kr/op/ko/sb/UOPKOSBZ01',
    'User-Agent': 'Mozilla/5.0',
}

def main():
    body = json.dumps({'pageIndex': '1', 'pageSize': '5000', 'totalCnt': '0'}).encode('utf-8')
    req = urllib.request.Request(URL, data=body, headers=HEADERS, method='POST')
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.loads(r.read().decode('utf-8'))
    print(f'수집: {len(data)}건 (pageTotCnt={data[0].get("pageTotCnt") if data else None})')
    json.dump(data, open(RAW_OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

    clean = []
    for it in data:
        clean.append({
            'dtaCtlgId': it.get('dtaCtlgId'),
            'dtaCtlgNm': it.get('dtaCtlgNm'),
            'dsDivId': it.get('dsDivId'),
            'dsId': it.get('dsId'),
            'dsHgNm': it.get('dsHgNm'),
            'dsHgEpl': it.get('dsHgEpl'),
            'instNm': it.get('instNm'),
            'alyDataDtaPrdDes': it.get('alyDataDtaPrdDes'),
            'dtaLoadCnt': it.get('dtaLoadCnt'),
            'lastMdfcnTdtTxt': it.get('lastMdfcnTdtTxt'),
        })
    json.dump(clean, open(CLEAN_OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

    with open(CSV_OUT, 'w', encoding='utf-8-sig', newline='') as fp:
        w = csv.writer(fp)
        w.writerow(['dtaCtlgNm(분류)', 'dsHgNm(데이터명)', 'instNm(자료제공처)', 'alyDataDtaPrdDes(분석기간)',
                    'lastMdfcnTdtTxt(최종수정)', 'dsId', 'dsHgEpl(설명)'])
        for d in clean:
            w.writerow([d['dtaCtlgNm'], d['dsHgNm'], d['instNm'], d['alyDataDtaPrdDes'],
                        d['lastMdfcnTdtTxt'], d['dsId'], (d['dsHgEpl'] or '').replace('\\n', ' ').strip()])
    print(f'저장: {CLEAN_OUT}, {CSV_OUT}')

    # Stats
    from collections import Counter
    print('\n분류별 건수:')
    for k, v in Counter(d['dtaCtlgNm'] for d in clean).most_common():
        print(f'  {k}: {v}')
    print('\n자료제공처 Top 15:')
    for k, v in Counter(d['instNm'] for d in clean).most_common(15):
        print(f'  {k}: {v}')

if __name__ == '__main__':
    main()
