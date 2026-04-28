"""H7: 환경·교통·국토 등 미매핑 분야 outcome 후보 발굴.

기존: 16분야 중 5분야만 outcome 매핑 (사회복지/보건/과기/산업/문화관광)
목표: 환경·교통·국토·교육·통신·농림·국방·공공질서까지 매핑 → 분야 단위 표본 5→13개

방법:
  1. kosis_tables (64,996건)에서 분야별 키워드로 후보 통계표 검색
  2. 거시 지표성·연단위·전국·시계열 길이 ≥10년인 표만 필터
  3. 메타데이터(ITM/OBJ) 조회 → 사용 가능 항목 확인
  4. 데이터 받아서 indicator_panel에 적재

이번 H7은 "후보 발굴 + 메타 확인"까지. 실제 데이터 적재는 후속.
"""
import os, sys, io, urllib.request, urllib.parse, json, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
from _env import load_env
load_env()
import duckdb
import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, 'data', 'warehouse.duckdb')
KEY = os.environ['KOSIS_KEY']

con = duckdb.connect(DB, read_only=True)

# 분야별 outcome 키워드 (산업·인구·시계열 가능한 거시 지표만)
FLD_KEYWORDS = {
    '환경': [
        ('폐기물 발생', None),
        ('대기오염 배출', None),
        ('온실가스 배출', None),
        ('미세먼지', None),
        ('수질 BOD', None),
    ],
    '교통및물류': [
        ('교통사고 사망', None),
        ('교통사고 발생', None),
        ('자동차 등록', None),
        ('항만 물동', None),
        ('컨테이너 처리', None),
    ],
    '국토및지역개발': [
        ('주택보급률', None),
        ('주택가격지수', None),
        ('지가변동', None),
        ('주택 준공', None),
    ],
    '교육': [
        ('학업성취도', None),
        ('대학 진학률', None),
        ('교원 1인당', None),
        ('학생 1인당', None),
    ],
    '통신': [
        ('이동전화 가입', None),
        ('인터넷 이용', None),
        ('초고속인터넷', None),
    ],
    '농림수산': [
        ('식량자급률', None),
        ('농가 소득', None),
        ('어획량', None),
        ('농산물 가격', None),
    ],
    '국방': [
        ('국방비', None),
        ('병력', None),
    ],
    '공공질서및안전': [
        ('범죄 발생', None),
        ('형법범', None),
        ('교정시설 수용', None),
    ],
    '일반·지방행정': [
        ('지방세', None),
        ('지방재정', None),
    ],
}

# ============================================================
# Step 1: kosis_tables에서 키워드 매칭
# ============================================================
print('='*70)
print('Step 1: kosis_tables 키워드 검색')
print('='*70)

candidates = []
for fld, kws in FLD_KEYWORDS.items():
    print(f'\n[{fld}]')
    for kw, _ in kws:
        # 거시·연단위·시계열 ≥10년만
        rs = con.execute(f"""
            SELECT tbl_nm, source, period, path_kor, tbl_id, list_id_path
            FROM kosis_tables
            WHERE tbl_nm ILIKE '%{kw}%'
              AND (period ILIKE '%연%' OR period ILIKE '%년%')
              AND tbl_nm NOT ILIKE '%사회조사%'
              AND tbl_nm NOT ILIKE '%인식%'
              AND tbl_nm NOT ILIKE '%조사%'
              AND path_kor NOT ILIKE '%사회조사%'
            ORDER BY length(period) DESC
            LIMIT 5
        """).fetchdf()
        for _, r in rs.iterrows():
            # 시계열 길이 추출
            per = r['period'] or ''
            yrs = []
            import re
            for m in re.findall(r'(\d{4})', per):
                yrs.append(int(m))
            ts_len = (max(yrs) - min(yrs) + 1) if len(yrs) >= 2 else 0
            candidates.append({
                'fld': fld, 'kw': kw,
                'tbl_id': r['tbl_id'],
                'tbl_nm': r['tbl_nm'],
                'period': per,
                'ts_len': ts_len,
                'source': r['source'],
                'path': r['path_kor'][:80] if r['path_kor'] else '',
            })
        print(f'  [{kw}] {len(rs)} 후보')

cand_df = pd.DataFrame(candidates)
# ts_len ≥ 10 우선
cand_df = cand_df[cand_df['ts_len'] >= 10].sort_values(['fld','ts_len'], ascending=[True, False])
print(f'\n총 후보: {len(cand_df)} (시계열 ≥10년)')

# 분야별 상위 3 보여주기
print('\n=== 분야별 상위 후보 ===')
for fld in cand_df['fld'].unique():
    sub = cand_df[cand_df['fld']==fld].head(5)
    print(f'\n[{fld}]')
    for _, r in sub.iterrows():
        print(f'  ts={r["ts_len"]:>3d}년  {r["tbl_id"]:25s} {r["tbl_nm"][:50]}')
        print(f'             period={r["period"]}, source={r["source"]}')

# 저장
os.makedirs(os.path.join(ROOT, 'tmp'), exist_ok=True)
cand_df.to_csv(os.path.join(ROOT, 'tmp', 'H7_outcome_candidates.csv'),
                index=False, encoding='utf-8-sig')
print(f'\n저장: tmp/H7_outcome_candidates.csv')

# ============================================================
# Step 2: ORG_ID 추정 + 메타 조회 (상위 후보 1개/분야)
# ============================================================
print('\n' + '='*70)
print('Step 2: 상위 후보 메타데이터 조회 (분야 1순위)')
print('='*70)

H = {'User-Agent': 'Mozilla/5.0'}

def parse_orgid(list_id_path):
    """list_id_path에서 'NNN_XXX' 패턴의 ORG_ID 3자리 추출."""
    if not list_id_path: return None
    import re
    m = re.search(r'(\d{3})_', list_id_path)
    return m.group(1) if m else None

def get_meta(orgId, tblId):
    url = ('https://kosis.kr/openapi/Param/statisticsParameterData.do?'
           f'method=getList&apiKey={KEY}&itmId=&objL1=&objL2=&objL3=&objL4=&'
           f'objL5=&objL6=&objL7=&objL8=&format=json&jsonVD=Y&prdSe=Y&'
           f'newEstPrdCnt=1&orgId={orgId}&tblId={tblId}')
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=30) as r:
            return json.loads(r.read().decode('utf-8'))
    except Exception as e:
        return {'_err': str(e)}

# kosis_tables에서 list_id_path 가져와서 ORG 1차 추출
con2 = duckdb.connect(DB, read_only=True)
path_map = con2.execute(f"""
    SELECT tbl_id, list_id_path FROM kosis_tables
    WHERE tbl_id IN {tuple(cand_df['tbl_id'].tolist())}
""").fetchdf().set_index('tbl_id')['list_id_path'].to_dict()
con2.close()

ORG_GUESSES = ['101','110','116','117','113','114','118','120','127','132','142',
               '143','154','155','156','159','161','164','228','305','310','315',
               '350','383','385','388','110','550']

# 분야별 상위 1~2개 시도
ok_list = []
print('\n=== 메타 조회 (ORG 추정) ===')
top_per_fld = cand_df.groupby('fld').head(2)
for _, r in top_per_fld.iterrows():
    print(f'\n[{r["fld"]}] {r["tbl_id"]} {r["tbl_nm"][:50]}')
    # 1차: list_id_path에서 추출
    orgs_to_try = []
    p = path_map.get(r['tbl_id'])
    parsed = parse_orgid(p)
    if parsed: orgs_to_try.append(parsed)
    # 2차: 일반 후보
    orgs_to_try += [o for o in ORG_GUESSES if o not in orgs_to_try]

    found = False
    for og in orgs_to_try[:25]:  # 너무 많은 호출 방지
        d = get_meta(og, r['tbl_id'])
        if isinstance(d, list) and d:
            print(f'   OK org={og}: {len(d)} rows')
            print(f'      sample: {{itm={d[0].get("ITM_NM","?")[:20]}, prd={d[0].get("PRD_DE","?")}, val={d[0].get("DT","?")}}}')
            ok_list.append({'fld': r['fld'], 'tbl_id': r['tbl_id'],
                            'tbl_nm': r['tbl_nm'], 'org_id': og, 'n_rows': len(d),
                            'period': r['period']})
            found = True
            break
        time.sleep(0.02)
    if not found:
        print(f'   no ORG match (tried {len(orgs_to_try[:25])})')

ok_df = pd.DataFrame(ok_list)
ok_df.to_csv(os.path.join(ROOT, 'tmp', 'H7_outcome_metadata.csv'),
             index=False, encoding='utf-8-sig')
print(f'\n메타 확인 완료: {len(ok_df)} 분야')

con.close()
