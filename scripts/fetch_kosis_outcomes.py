"""KOSIS 통계표 사전(kosis_tables)에서 분야별 결과변수 매칭 → 데이터 다운로드 → indicator_panel 적재.

전제: scripts/fetch_kosis_catalog.py 실행으로 warehouse.duckdb의 kosis_tables 테이블 구축됨.

흐름:
  1. 분야별 키워드로 kosis_tables 검색 → 후보 통계표 식별
  2. 사용자 검토용 후보 리스트 출력 (선택은 수동 또는 자동 best-N)
  3. 선택된 통계표마다 statisticsParameterData.do 호출 → 시계열 다운로드
  4. 분야×연도×지표 형태로 변환 → indicator_panel 적재
"""
import os, sys, io, json, time, urllib.request, urllib.parse
import duckdb

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, 'data', 'warehouse.duckdb')
KEY = os.environ.get('KOSIS_KEY')
if not KEY: sys.exit('KOSIS_KEY 환경변수 필요')
H = {'User-Agent': 'Mozilla/5.0'}

# 분야별 검색 키워드 (TBL_NM 또는 path 매칭)
FIELD_KEYWORDS = {
    '과학기술':       ['연구개발활동조사','연구개발비','특허 등록','특허 출원','SCI 논문'],
    '국토·지역':      ['지역내총생산','GRDP','1인당 지역','지역소득'],
    '환경':           ['대기오염물질','미세먼지 농도','PM2.5','온실가스 배출'],
    '보건':           ['기대수명','생명표','건강수명'],
    '문화·관광':       ['외래관광객','방한 관광','한국관광통계'],
    '교통·물류':       ['국가물류비','교통량','수송실적','화물수송'],
    '산업·중기':       ['제조업 부가가치','광공업동향','전산업생산','제조업 사업체'],
    '사회복지':       ['상대적 빈곤율','지니계수','소득분배지표'],
}

def search_candidates():
    con = duckdb.connect(DB, read_only=True)
    by_field = {}
    for fld, kws in FIELD_KEYWORDS.items():
        cond = ' OR '.join([f"TBL_NM ILIKE '%{k}%'" for k in kws])
        rows = con.execute(f"""
            SELECT vwCd, ORG_ID, TBL_ID, TBL_NM, path
            FROM kosis_tables
            WHERE {cond}
            ORDER BY length(TBL_NM)
            LIMIT 20
        """).fetchdf()
        by_field[fld] = rows
    con.close()
    return by_field

def call_data(orgId, tblId, prdSe='Y', newEstPrdCnt='10', objL1='ALL', itmId='ALL'):
    """statisticsParameterData.do 호출 — 통계표 데이터 다운로드."""
    p = {
        'method':'getList', 'apiKey':KEY, 'format':'json', 'jsonVD':'Y',
        'orgId': orgId, 'tblId': tblId,
        'prdSe': prdSe, 'newEstPrdCnt': newEstPrdCnt,
        'objL1': objL1, 'itmId': itmId,
    }
    qs = urllib.parse.urlencode(p)
    url = f'https://kosis.kr/openapi/Param/statisticsParameterData.do?{qs}'
    req = urllib.request.Request(url, headers=H)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode('utf-8'))

if __name__ == '__main__':
    print('=== 분야별 통계표 후보 검색 (kosis_tables) ===')
    by_field = search_candidates()
    for fld, df in by_field.items():
        print(f'\n[{fld}] 후보 {len(df)}개')
        if not df.empty:
            for _, r in df.head(5).iterrows():
                print(f"  [{r['ORG_ID']}/{r['TBL_ID']}] {r['TBL_NM'][:50]}")
                print(f"    path: {r['path'][:60]}")
