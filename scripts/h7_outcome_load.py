"""H7 적재: 신규 outcome 5개 분야 indicator_panel append.

추가 분야:
  환경     → 폐기물 발생량 (1일 1인당)        110/DT_11001N_2013_A054 (2009~2020)
  교통및물류 → 자동차 등록대수                  110/DT_11001N_2013_A033 (2009~2020)
  국토및지역개발 → 주택보급률                   116/DT_MLTM_2100        (2005~2024)
  일반·지방행정 → 1인당 지방세 부담액            110/DT_11001N_2013_A012 (2009~2020)
  교육     → 학생 1인당 사교육 참여시간         101/DT_1PE103           (2007~2025)

기존 5분야 (사회복지/보건/과기/산업/문화관광)와 합쳐 10분야 매핑.
이로써 H6 분야 단위 표본이 5→10으로 2배 증가.
"""
import os, sys, io, json, urllib.request, urllib.parse, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _env import load_env
load_env()
import duckdb
import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, 'data', 'warehouse.duckdb')
RAW_DIR = os.path.join(ROOT, 'data', 'external', 'kosis_data')
os.makedirs(RAW_DIR, exist_ok=True)
KEY = os.environ['KOSIS_KEY']

# 신규 outcome 매핑
NEW_OUTCOMES = [
    {'fld':'환경',         'metric':'waste_per_capita',
     'org':'110','tbl':'DT_11001N_2013_A054',
     'metric_nm':'1일 1인당 폐기물 발생량',
     'unit':'kg/cap/day', 'expected_sign': -1,  # 폐기물 ↓ = outcome 좋음
     'cache':'waste_per_capita.json',
     'agg': 'national_mean'},  # C1=시도 → 평균
    {'fld':'교통및물류',    'metric':'vehicle_reg',
     'org':'110','tbl':'DT_11001N_2013_A033',
     'metric_nm':'자동차 등록대수',
     'unit':'대','expected_sign': +1,
     'cache':'vehicle_reg.json',
     'agg': 'national_sum'},
    {'fld':'국토및지역개발', 'metric':'housing_supply',
     'org':'116','tbl':'DT_MLTM_2100',
     'metric_nm':'주택보급률',
     'unit':'%','expected_sign': +1,
     'cache':'housing_supply.json',
     'agg': 'national_mean'},
    {'fld':'일반·지방행정', 'metric':'local_tax_per_capita',
     'org':'110','tbl':'DT_11001N_2013_A012',
     'metric_nm':'1인당 지방세 부담액',
     'unit':'원/인','expected_sign': +1,
     'cache':'local_tax.json',
     'agg':'national_mean'},
    {'fld':'교육',         'metric':'private_edu_hours',
     'org':'101','tbl':'DT_1PE103',
     'metric_nm':'학생 1인당 주당 사교육 참여시간',
     'unit':'시간','expected_sign': +1,  # 사교육 시간이 늘면 공교육 KPI 게임화 가능성
     'cache':'private_edu.json',
     'agg':'national_mean'},
]

H = {'User-Agent':'Mozilla/5.0'}

def fetch_kosis(orgId, tblId, n_periods=25):
    p = {'method':'getList','apiKey':KEY,'format':'json','jsonVD':'Y',
         'orgId':orgId,'tblId':tblId,'prdSe':'Y','newEstPrdCnt':str(n_periods),
         'objL1':'ALL','itmId':'ALL'}
    url = 'https://kosis.kr/openapi/Param/statisticsParameterData.do?' + urllib.parse.urlencode(p)
    with urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=60) as r:
        return json.loads(r.read().decode('utf-8'))

# ============================================================
# Step 1: 데이터 fetch + 캐시
# ============================================================
print('='*70)
print('Step 1: KOSIS 호출 (5개 통계표)')
print('='*70)
all_data = {}
for spec in NEW_OUTCOMES:
    cache_path = os.path.join(RAW_DIR, spec['cache'])
    if os.path.exists(cache_path) and os.path.getsize(cache_path) > 100:
        d = json.load(open(cache_path, encoding='utf-8'))
        print(f'  [{spec["metric"]}] cached: {len(d)} rows')
    else:
        d = fetch_kosis(spec['org'], spec['tbl'])
        json.dump(d, open(cache_path,'w',encoding='utf-8'), ensure_ascii=False)
        print(f'  [{spec["metric"]}] fetched: {len(d) if isinstance(d,list) else "ERR"} rows')
        time.sleep(0.5)
    all_data[spec['metric']] = d

# ============================================================
# Step 2: 분야 단위 시계열로 변환
# ============================================================
print('\n' + '='*70)
print('Step 2: 분야 단위 시계열 변환 (전국 평균/합산)')
print('='*70)

records = []  # (fld, year, metric, value, source, unit)

for spec in NEW_OUTCOMES:
    d = all_data[spec['metric']]
    if not isinstance(d, list) or not d:
        print(f'  [{spec["metric"]}] no data, skip')
        continue
    df = pd.DataFrame(d)
    # 표준 컬럼명 PRD_DE = 연도, DT = 값, C1_OBJ_NM = 시도, ITM_ID/NM = 항목
    if 'PRD_DE' not in df.columns or 'DT' not in df.columns:
        print(f'  [{spec["metric"]}] cols={df.columns.tolist()[:6]}, skip')
        continue
    df['year'] = pd.to_numeric(df['PRD_DE'], errors='coerce')
    df['value'] = pd.to_numeric(df['DT'], errors='coerce')
    df = df.dropna(subset=['year','value'])

    # 항목 다양 → 가장 빈도 높은 ITM_ID 또는 사용자 지정
    # 일반적으로 "전국" / "총" 항목을 골라야 함.
    if 'C1_OBJ_NM' in df.columns:
        # 전국·계 같은 키워드 우선, 없으면 시도 평균
        is_natl = df['C1_OBJ_NM'].str.contains('전국|계$|^전체', regex=True, na=False)
        if is_natl.any():
            df_natl = df[is_natl]
            print(f'  [{spec["metric"]}] using "전국" rows: {len(df_natl)}')
        else:
            # 시도별 평균
            df_natl = df.groupby(['year']).agg(value=('value','mean')).reset_index()
            print(f'  [{spec["metric"]}] no national row, sido mean: {len(df_natl)}')
    else:
        df_natl = df

    # 항목(ITM_ID)도 여러 개일 수 있음 — 가장 적절한 것 선택
    if 'ITM_NM' in df_natl.columns:
        items = df_natl['ITM_NM'].value_counts()
        print(f'    ITM_NM 후보: {items.head(5).to_dict()}')
        # 일반적인 첫번째 항목 선택
        if len(items) > 0:
            primary_itm = items.index[0]
            df_natl = df_natl[df_natl['ITM_NM'] == primary_itm]
            print(f'    선택: {primary_itm}')

    # 연도별 평균 (중복 처리)
    ts = df_natl.groupby('year')['value'].mean().reset_index()
    print(f'    최종 시계열: {len(ts)}개 연도, {int(ts["year"].min())}~{int(ts["year"].max())}')
    print(f'    값 범위: {ts["value"].min():.2f} ~ {ts["value"].max():.2f}')

    for _, r in ts.iterrows():
        records.append((spec['fld'], int(r['year']), spec['metric'],
                        float(r['value']), f"KOSIS_{spec['tbl']}", spec['unit']))

print(f'\n  총 record: {len(records)}')

# ============================================================
# Step 3: indicator_panel append
# ============================================================
print('\n' + '='*70)
print('Step 3: indicator_panel append + indicator_metadata')
print('='*70)
con = duckdb.connect(DB)

# 기존 동일 metric_code 삭제 (재실행 안전)
metric_codes = [s['metric'] for s in NEW_OUTCOMES]
codes_sql = "', '".join(metric_codes)
deleted = con.execute(f"""
    DELETE FROM indicator_panel WHERE metric_code IN ('{codes_sql}')
    RETURNING 1
""").fetchall()
print(f'  기존 동일 metric 삭제: {len(deleted)}')

con.executemany(
    "INSERT INTO indicator_panel (fld_nm, year, metric_code, value, source, unit) VALUES (?, ?, ?, ?, ?, ?)",
    records
)
print(f'  적재: {len(records)} rows')

# metadata
deleted_m = con.execute(f"""
    DELETE FROM indicator_metadata WHERE metric_code IN ('{codes_sql}')
    RETURNING 1
""").fetchall()

meta = [(s['metric'], s['metric_nm'], 'outcome', s['metric_nm'],
         f"KOSIS_{s['org']}_{s['tbl']}", s['expected_sign']) for s in NEW_OUTCOMES]
con.executemany(
    "INSERT INTO indicator_metadata (metric_code, metric_nm, category, description, source_url, expected_sign) VALUES (?, ?, ?, ?, ?, ?)",
    meta
)

# 검증
print('\n=== 검증 ===')
v = con.execute(f"""
    SELECT metric_code, count(*) n, min(year) y0, max(year) y1, avg(value) avg_v
    FROM indicator_panel WHERE metric_code IN ('{codes_sql}')
    GROUP BY metric_code ORDER BY metric_code
""").fetchdf()
print(v.round(3).to_string(index=False))

# 최종 outcome 매핑 표
print('\n=== 전체 outcome 매핑 ===')
all_oc = con.execute("""
    SELECT p.fld_nm, p.metric_code, count(*) n_year, min(year) y0, max(year) y1,
           m.metric_nm
    FROM indicator_panel p
    JOIN indicator_metadata m USING (metric_code)
    WHERE m.category = 'outcome'
    GROUP BY p.fld_nm, p.metric_code, m.metric_nm
    ORDER BY p.fld_nm
""").fetchdf()
print(all_oc.to_string(index=False))

con.close()
print('\n완료.')
