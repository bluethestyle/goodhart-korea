"""H11: 자동차등록 CSV 적재 (천단위 콤마 vs 분리자 콤마 재조립).

입력: 자동차등록현황보고_자동차등록대수현황 시도별 (201101 ~ 202603).csv
  - cp949 인코딩
  - 23 컬럼 (월/시도/시군구/차종5×관용·자가·영업·계4)
  - 천단위 콤마가 분리자 콤마와 충돌 → 토큰 재조립

출력:
  - data/external/molit/motor_registration_sido.csv (정제 시도×연도 시계열)
  - indicator_panel append (vehicle_per_capita 또는 vehicle_total)
"""
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import re
import pandas as pd
import duckdb

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_FILES = [
    '자동차등록현황보고_자동차등록대수현황 시도별 (201101 ~ 201512).csv',
    '자동차등록현황보고_자동차등록대수현황 시도별 (201601 ~ 202012).csv',
    '자동차등록현황보고_자동차등록대수현황 시도별 (202101 ~ 202512).csv',
    '자동차등록현황보고_자동차등록대수현황 시도별 (202601 ~ 202603).csv',
]
OUT_DIR = os.path.join(ROOT, 'data', 'external', 'molit')
os.makedirs(OUT_DIR, exist_ok=True)

# 23 컬럼 (헤더 2줄 multilevel)
SUB_HEADER = ['월','시도','시군구',
              '승용_관용','승용_자가용','승용_영업용','승용_계',
              '승합_관용','승합_자가용','승합_영업용','승합_계',
              '화물_관용','화물_자가용','화물_영업용','화물_계',
              '특수_관용','특수_자가용','특수_영업용','특수_계',
              '총계_관용','총계_자가용','총계_영업용','총계_계']
NCOL = len(SUB_HEADER)

def reassemble(tokens):
    """천단위 결합 — 각 셀 최대 1회 결합 + 결합 후 토큰 수가 셀 수와 일치.
       자동차 등록은 보통 100만 이하라 한 번 결합(예: 218,432)으로 충분.
    """
    if len(tokens) < 3:
        return None
    out = list(tokens[:3])
    rest = [t.strip() for t in tokens[3:]]
    n_cells = NCOL - 3   # 20
    n_combine_total = len(rest) - n_cells  # 총 결합 횟수
    if n_combine_total < 0 or n_combine_total > n_cells:
        return None
    # 각 셀당 0 또는 1회 결합. 어느 셀이 결합할지를 정해야.
    # 그리디: 결합 가능한 위치(현재 토큰이 1~3자리, 다음이 3자리) 중 앞에서부터 n_combine_total개.
    # 단 결합 후 남은 토큰이 남은 셀과 정확히 일치해야 함.
    combined = []
    i = 0
    combines_used = 0
    while i < len(rest) and len(combined) < n_cells:
        cur = rest[i]; i += 1
        # 한 번만 결합 시도
        if (combines_used < n_combine_total
            and i < len(rest)
            and cur.isdigit() and rest[i].isdigit() and len(rest[i]) == 3):
            # 결합해도 남은 토큰이 남은 셀에 맞는지
            remaining_tokens_after = len(rest) - i - 1
            remaining_cells_after = n_cells - len(combined) - 1
            if remaining_tokens_after >= remaining_cells_after:
                cur = cur + rest[i]; i += 1
                combines_used += 1
        combined.append(cur)
    if len(combined) != n_cells or i != len(rest) or combines_used != n_combine_total:
        return None
    out.extend(combined)
    return out

# Step 1: 4개 파일 모두 파싱
records = []
total_bad = 0
for src in SRC_FILES:
    path = os.path.join(ROOT, src)
    if not os.path.exists(path):
        print(f'[skip] {src} (not found)')
        continue
    with open(path, 'rb') as f:
        raw = f.read().decode('cp949', errors='replace')
    lines = [l.rstrip() for l in raw.split('\n') if l.strip()]
    file_bad = 0
    file_n = 0
    for line in lines[2:]:
        tokens = line.split(',')
        rec = reassemble(tokens)
        if rec is None:
            file_bad += 1
            continue
        records.append(rec)
        file_n += 1
    print(f'[{src[:50]}] data={len(lines)-2}, parsed={file_n}, bad={file_bad}')
    total_bad += file_bad
print(f'\n전체 parsed: {len(records)}, bad: {total_bad}')

df = pd.DataFrame(records, columns=SUB_HEADER)
# 숫자 컬럼 변환
num_cols = SUB_HEADER[3:]
for c in num_cols:
    df[c] = pd.to_numeric(df[c], errors='coerce')
df = df.dropna(subset=['총계_계'])
print(f'유효 행: {len(df)}, 시도 unique: {df["시도"].nunique()}, 월 unique: {df["월"].nunique()}')
print(f'시도 sample: {df["시도"].unique()[:5]}')
print(f'월 범위: {df["월"].min()} ~ {df["월"].max()}')

# Step 2: 시도 합계 행만 사용 (시군구='계')
df_sido = df[df['시군구']=='계'].copy()
print(f'\n시도 합계 행 (시군구=계): {len(df_sido)}')
print('월 unique:', df_sido['월'].nunique(), '시도 unique:', df_sido['시도'].nunique())
sido_month = df_sido[['월','시도','총계_계']].copy()
print(f'\n시도×월 cells: {len(sido_month)}')
print(sido_month.head(5).to_string(index=False))

# Step 3: 연도 평균 (월별 평균이 아니라 12월 말 누적이 자연스러움)
sido_month['year'] = sido_month['월'].str[:4].astype(int)
sido_year = sido_month.groupby(['year','시도'])['총계_계'].mean().reset_index()
sido_year.columns = ['year','sido','total_vehicles']
print(f'\n시도×연도: {len(sido_year)}, 연도: {sido_year["year"].min()}~{sido_year["year"].max()}')

# 전국 합계 (시도 합)
natl = sido_year.groupby('year')['total_vehicles'].sum().reset_index()
natl.columns = ['year','total_vehicles_natl']
print('\n전국 연 합계:')
print(natl.tail(10).to_string(index=False))

# Step 4: 저장
sido_year.to_csv(os.path.join(OUT_DIR, 'motor_registration_sido_year.csv'),
                 index=False, encoding='utf-8-sig')
natl.to_csv(os.path.join(OUT_DIR, 'motor_registration_national.csv'),
            index=False, encoding='utf-8-sig')
print(f'저장: {OUT_DIR}/')

# Step 5: indicator_panel 적재
con = duckdb.connect(os.path.join(ROOT, 'data', 'warehouse.duckdb'))
con.execute("DELETE FROM indicator_panel WHERE metric_code='vehicle_total'")
con.execute("DELETE FROM indicator_metadata WHERE metric_code='vehicle_total'")

records_p = []
for _, r in natl.iterrows():
    records_p.append(('교통및물류', int(r['year']), 'vehicle_total',
                       float(r['total_vehicles_natl']),
                       'MOLIT_motor_registration', '대'))
con.executemany("INSERT INTO indicator_panel (fld_nm, year, metric_code, value, source, unit) VALUES (?,?,?,?,?,?)",
                records_p)
con.execute("""
    INSERT INTO indicator_metadata (metric_code, metric_nm, category, description, source_url, expected_sign)
    VALUES ('vehicle_total', '자동차 등록대수 (전국 합계)', 'outcome',
            '국토교통부 자동차등록현황보고 시도별 → 전국 합계',
            'https://stat.molit.go.kr/portal/cate/statView.do?hRsId=58&hFormId=5498', 1)
""")
print(f'\nindicator_panel 적재: {len(records_p)} rows')

# 검증
v = con.execute("""
    SELECT year, value FROM indicator_panel
    WHERE metric_code='vehicle_total' ORDER BY year
""").fetchdf()
print(v.to_string(index=False))
con.close()
