"""분야×연도×지표 long-format 통합 패널 구축.

스키마:
  indicator_panel
    fld_nm       VARCHAR    16대 분야명 (또는 'ALL')
    year         INTEGER
    metric_code  VARCHAR    지표 코드 ('amp_12m_norm','rd_total',...)
    value        DOUBLE
    source       VARCHAR    'internal_FFT' | 'KOSIS_DT_xxx' | 'OECD_xxx'
    unit         VARCHAR
    loaded_at    TIMESTAMP

  indicator_metadata
    metric_code   VARCHAR PK
    metric_nm     VARCHAR
    category      VARCHAR    'gaming' | 'budget' | 'outcome'
    description   VARCHAR
    source_url    VARCHAR
    expected_sign INTEGER    H2: outcome일 때 game과의 상관 기대 부호

소스:
  monthly_exec     → 게임화 지표 (amp_12m, dec_pct, q1_pct, q4_pct, hhi, gini)
  expenditure_budget → 분야 예산 규모, 변화율
  expenditure_item   → 출연·자치단체이전 비중
  외부 (KOSIS 등)    → 결과 변수 (사용자 URL 받은 후 추가)
"""
import os, sys, io, duckdb
import numpy as np
import pandas as pd
from scipy import fft as scfft

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, 'data', 'warehouse.duckdb')
con = duckdb.connect(DB)

# ============================================================
# 1) 스키마 생성
# ============================================================
con.execute("DROP TABLE IF EXISTS indicator_panel")
con.execute("""
    CREATE TABLE indicator_panel (
        fld_nm       VARCHAR,
        year         INTEGER,
        metric_code  VARCHAR,
        value        DOUBLE,
        source       VARCHAR,
        unit         VARCHAR,
        loaded_at    TIMESTAMP DEFAULT current_timestamp
    )
""")
con.execute("DROP TABLE IF EXISTS indicator_metadata")
con.execute("""
    CREATE TABLE indicator_metadata (
        metric_code   VARCHAR PRIMARY KEY,
        metric_nm     VARCHAR,
        category      VARCHAR,
        description   VARCHAR,
        source_url    VARCHAR,
        expected_sign INTEGER
    )
""")
print('스키마 생성: indicator_panel, indicator_metadata')

# 회계거래 식별용 (CITM 기반과 키워드 기반 둘 다 후보지만 일단 키워드)
PURE_ACCT = """(
    ACTV_NM ILIKE '%전출금%' OR ACTV_NM ILIKE '%타계정%' OR ACTV_NM ILIKE '%여유자금%'
 OR ACTV_NM ILIKE '%국고예탁%' OR ACTV_NM ILIKE '%기금예탁%' OR ACTV_NM ILIKE '%국고예치%'
 OR ACTV_NM ILIKE '%회계간거래%' OR ACTV_NM ILIKE '%회계간전출%'
 OR ACTV_NM ILIKE '%회계기금간%' OR ACTV_NM ILIKE '%여유자금운용%'
)"""

# ============================================================
# 2) 분야×연도 게임화 지표 (정책사업만)
# ============================================================
print('\n[1/4] 분야×연도 게임화 지표 산출')
df = con.execute(f"""
    SELECT FSCL_YY AS year, EXE_M AS month, FLD_NM AS fld_nm, sum(EP_AMT) AS amt
    FROM monthly_exec
    WHERE EXE_M BETWEEN 1 AND 12 AND NOT {PURE_ACCT}
      AND FSCL_YY BETWEEN 2015 AND 2025
    GROUP BY FSCL_YY, EXE_M, FLD_NM
""").fetchdf()

records = []
for (year, fld), g in df.groupby(['year', 'fld_nm']):
    g = g.sort_values('month')
    arr = np.zeros(12)
    for _, r in g.iterrows():
        arr[int(r['month']) - 1] = r['amt']
    total = arr.sum()
    if total <= 0: continue
    pct = arr / total
    # FFT (1년 12개월 단위)
    yf = scfft.fft(arr - arr.mean())
    amp_12m = abs(yf[1]) * 2 / 12  # k=1: 1cycle per year
    amp_12m_norm = amp_12m / (total / 12)
    amp_6m = abs(yf[2]) * 2 / 12
    amp_6m_norm = amp_6m / (total / 12)
    # HHI 시점
    hhi = (pct ** 2).sum()
    # Gini
    s = np.sort(arr)
    gini = 2 * np.sum((np.arange(1, 13)) * s) / (12 * s.sum()) - 13 / 12 if s.sum() > 0 else 0
    # 분기
    q1 = pct[:3].sum()
    q4 = pct[9:12].sum()
    dec = pct[11]
    metrics = {
        'amp_12m_norm': amp_12m_norm,
        'amp_6m_norm':  amp_6m_norm,
        'hhi_period':   hhi,
        'gini_period':  gini,
        'q1_pct':       q1,
        'q4_pct':       q4,
        'dec_pct':      dec,
        'annual_amt':   total,
    }
    for code, val in metrics.items():
        records.append((str(fld), int(year), str(code), float(val), 'internal_FFT_FLD', 'ratio' if code != 'annual_amt' else 'KRW_thousand'))

con.executemany(
    "INSERT INTO indicator_panel (fld_nm, year, metric_code, value, source, unit) VALUES (?, ?, ?, ?, ?, ?)",
    records
)
print(f'  적재: {len(records):,} 행 (분야×연도×지표)')

# ============================================================
# 3) 분야×연도 예산·구조 지표 (expenditure_budget·expenditure_item)
# ============================================================
print('\n[2/4] 예산 규모·증가율 (expenditure_budget)')
budget_records = con.execute("""
    WITH base AS (
      SELECT FSCL_YY AS year, FLD_NM AS fld_nm, sum(Y_YY_DFN_KCUR_AMT) AS budget
      FROM expenditure_budget WHERE SBUDG_DGR=0
      GROUP BY FSCL_YY, FLD_NM
    ),
    growth AS (
      SELECT year, fld_nm, budget,
             100.0 * (budget - LAG(budget) OVER (PARTITION BY fld_nm ORDER BY year))
                   / nullif(LAG(budget) OVER (PARTITION BY fld_nm ORDER BY year), 0) AS yoy_growth
      FROM base
    )
    SELECT fld_nm, year, 'budget_total' AS metric_code, budget AS value,
           'OPENFISCAL_expenditure' AS source, 'KRW_thousand' AS unit
    FROM growth
    UNION ALL
    SELECT fld_nm, year, 'budget_yoy_growth_pct' AS metric_code, yoy_growth AS value,
           'OPENFISCAL_expenditure' AS source, 'pct' AS unit
    FROM growth WHERE yoy_growth IS NOT NULL
""").fetchall()
con.executemany(
    "INSERT INTO indicator_panel (fld_nm, year, metric_code, value, source, unit) VALUES (?, ?, ?, ?, ?, ?)",
    budget_records
)
print(f'  적재: {len(budget_records):,} 행')

print('\n[3/4] 출연·이전 비중 (expenditure_item)')
item_records = con.execute("""
    WITH t AS (
      SELECT FSCL_YY AS year, FLD_NM AS fld_nm,
             sum(Y_YY_DFN_KCUR_AMT) AS total,
             sum(CASE WHEN CITM_NM IN ('일반출연금','연구개발출연금','출연금')
                      THEN Y_YY_DFN_KCUR_AMT ELSE 0 END) AS chooyeon,
             sum(CASE WHEN CITM_NM = '자치단체이전'
                      THEN Y_YY_DFN_KCUR_AMT ELSE 0 END) AS local_transfer,
             sum(CASE WHEN CITM_NM IN ('인건비')
                      THEN Y_YY_DFN_KCUR_AMT ELSE 0 END) AS personnel,
             sum(CASE WHEN CITM_NM IN ('운영비','업무추진비','여비','직무수행경비')
                      THEN Y_YY_DFN_KCUR_AMT ELSE 0 END) AS operating,
             sum(CASE WHEN CITM_NM IN ('자산취득비','유형자산','무형자산','건설비')
                      THEN Y_YY_DFN_KCUR_AMT ELSE 0 END) AS direct_invest
      FROM expenditure_item WHERE SBUDG_DGR=0
      GROUP BY FSCL_YY, FLD_NM
    )
    SELECT fld_nm, year, 'chooyeon_pct' AS metric_code, chooyeon*1.0/nullif(total,0) AS value,
           'OPENFISCAL_item' AS source, 'ratio' AS unit
    FROM t
    UNION ALL
    SELECT fld_nm, year, 'local_transfer_pct', local_transfer*1.0/nullif(total,0),
           'OPENFISCAL_item', 'ratio' FROM t
    UNION ALL
    SELECT fld_nm, year, 'personnel_pct', personnel*1.0/nullif(total,0),
           'OPENFISCAL_item', 'ratio' FROM t
    UNION ALL
    SELECT fld_nm, year, 'operating_pct', operating*1.0/nullif(total,0),
           'OPENFISCAL_item', 'ratio' FROM t
    UNION ALL
    SELECT fld_nm, year, 'direct_invest_pct', direct_invest*1.0/nullif(total,0),
           'OPENFISCAL_item', 'ratio' FROM t
""").fetchall()
con.executemany(
    "INSERT INTO indicator_panel (fld_nm, year, metric_code, value, source, unit) VALUES (?, ?, ?, ?, ?, ?)",
    item_records
)
print(f'  적재: {len(item_records):,} 행')

# ============================================================
# 4) indicator_metadata 사전
# ============================================================
print('\n[4/4] indicator_metadata 사전 구축')
meta = [
    # 게임화 지표
    ('amp_12m_norm',  '연주기 진폭(정규화)', 'gaming', '월별 집행 시계열의 12개월 주기 FFT amplitude / 연 평균', 'internal', None),
    ('amp_6m_norm',   '반기주기 진폭(정규화)', 'gaming', '6개월 주기 FFT amplitude / 연 평균', 'internal', None),
    ('hhi_period',    '시점 HHI',         'gaming', '월별 집행 비중의 허핀달지수 (균등=0.083, 단일월=1)', 'internal', None),
    ('gini_period',   '월별 Gini',       'gaming', '월별 집행 분포의 Gini 계수', 'internal', None),
    ('q1_pct',        'Q1 집중도',        'gaming', '1~3월 집행 / 연간 (균등=0.25)', 'internal', None),
    ('q4_pct',        'Q4 집중도',        'gaming', '10~12월 집행 / 연간 (균등=0.25)', 'internal', None),
    ('dec_pct',       '12월 집중도',       'gaming', '12월 집행 / 연간 (균등=0.083)', 'internal', None),
    ('annual_amt',    '연간 집행액',       'gaming', '월별 집행 합계 (스케일 참조)', 'internal', None),
    # 예산 규모
    ('budget_total',          '본예산 총액',      'budget', '분야 본예산 회차0 합계',                'OPENFISCAL', None),
    ('budget_yoy_growth_pct', '본예산 전년대비',   'budget', '본예산 전년대비 증가율(%)',             'OPENFISCAL', None),
    # 사업비 구성
    ('chooyeon_pct',         '출연금 비중',      'budget', '편성목 출연금(일반+R&D)/총예산',        'OPENFISCAL', None),
    ('local_transfer_pct',   '자치단체이전 비중',  'budget', '편성목 자치단체이전/총예산',             'OPENFISCAL', None),
    ('personnel_pct',        '인건비 비중',       'budget', '편성목 인건비/총예산',                  'OPENFISCAL', None),
    ('operating_pct',        '운영비 비중',       'budget', '편성목 운영비·여비·업무추진비/총예산',  'OPENFISCAL', None),
    ('direct_invest_pct',    '직접투자 비중',     'budget', '편성목 자산취득·건설비/총예산',         'OPENFISCAL', None),
]
con.executemany(
    "INSERT INTO indicator_metadata (metric_code, metric_nm, category, description, source_url, expected_sign) VALUES (?, ?, ?, ?, ?, ?)",
    meta
)
print(f'  적재: {len(meta)} 메타')

# ============================================================
# 검증 쿼리
# ============================================================
print('\n=== 검증: 분야×연도 game·budget 지표 일부 ===')
df = con.execute("""
    SELECT fld_nm, year, metric_code, round(value, 4) AS value
    FROM indicator_panel
    WHERE year IN (2020, 2024) AND fld_nm IN ('과학기술','국방','환경','교육')
      AND metric_code IN ('amp_12m_norm','dec_pct','chooyeon_pct','direct_invest_pct')
    ORDER BY fld_nm, metric_code, year
""").fetchdf()
print(df.to_string(index=False))

print('\n=== 패널 통계 ===')
stats = con.execute("""
    SELECT category, count(DISTINCT m.metric_code) AS metric_n,
           count(p.value) AS rows
    FROM indicator_metadata m
    LEFT JOIN indicator_panel p USING (metric_code)
    GROUP BY category ORDER BY category
""").fetchdf()
print(stats.to_string(index=False))

print(f'\n=== 분야 unique ({len(con.execute("SELECT DISTINCT fld_nm FROM indicator_panel ORDER BY fld_nm").fetchall())}개) ===')
for r in con.execute("SELECT DISTINCT fld_nm FROM indicator_panel ORDER BY fld_nm").fetchall():
    print(f'  {r[0]}')

con.close()
print(f'\nDB: {DB}')
