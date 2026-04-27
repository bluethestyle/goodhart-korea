"""DuckDB 웨어하우스 기본 점검 쿼리 모음.

Usage:
  python scripts/query_warehouse.py
"""
import os, sys, io, duckdb

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT, 'data', 'warehouse.duckdb')

con = duckdb.connect(DB_PATH, read_only=True)

def show(title, sql):
    print(f'\n=== {title} ===')
    print(con.execute(sql).fetchdf().to_string(index=False, max_rows=30))

# 1. 테이블 일람
show('테이블 목록', """
    SELECT table_name, estimated_size FROM duckdb_tables()
    WHERE schema_name='main' ORDER BY table_name
""")

# 2. 패널 요약 (세출)
show('세출 패널 (FSCL_YY × SBUDG_DGR)', """
    SELECT FSCL_YY, SBUDG_DGR,
           count(*) AS rows,
           round(sum(Y_YY_DFN_KCUR_AMT)/1e9, 1) AS total_chowon
    FROM expenditure_budget
    GROUP BY FSCL_YY, SBUDG_DGR
    ORDER BY FSCL_YY, SBUDG_DGR
""")

# 3. 추경 신규 사업 (2026 본예산 → 1차 추경)
show('2026 추경에서 신규 등장한 세부사업', """
    WITH base AS (
        SELECT DISTINCT OFFC_NM, FSCL_NM, PGM_NM, ACTV_NM, SACTV_NM
        FROM expenditure_budget WHERE FSCL_YY=2026 AND SBUDG_DGR=0
    ),
    add1 AS (
        SELECT DISTINCT OFFC_NM, FSCL_NM, PGM_NM, ACTV_NM, SACTV_NM,
               Y_YY_DFN_KCUR_AMT
        FROM expenditure_budget WHERE FSCL_YY=2026 AND SBUDG_DGR=1
    )
    SELECT a.OFFC_NM, a.FSCL_NM, a.PGM_NM, a.SACTV_NM,
           round(a.Y_YY_DFN_KCUR_AMT/1e6, 1) AS amt_eok
    FROM add1 a
    LEFT JOIN base b USING (OFFC_NM, FSCL_NM, PGM_NM, ACTV_NM, SACTV_NM)
    WHERE b.SACTV_NM IS NULL
    ORDER BY a.Y_YY_DFN_KCUR_AMT DESC
    LIMIT 20
""")

# 4. 5년간 추경 단골 사업 (2020~2026, 추경에 매년 등장)
show('5년 추경 단골 후보 (추경 회차 2회 이상 등장 사업)', """
    WITH addons AS (
        SELECT DISTINCT FSCL_YY, OFFC_NM, FSCL_NM, PGM_NM, ACTV_NM, SACTV_NM
        FROM expenditure_budget
        WHERE SBUDG_DGR > 0
    ),
    in_base AS (
        SELECT DISTINCT FSCL_YY, OFFC_NM, FSCL_NM, PGM_NM, ACTV_NM, SACTV_NM
        FROM expenditure_budget WHERE SBUDG_DGR = 0
    ),
    pure_addons AS (
        SELECT a.* FROM addons a
        LEFT JOIN in_base b
          ON a.FSCL_YY=b.FSCL_YY AND a.OFFC_NM=b.OFFC_NM AND a.FSCL_NM=b.FSCL_NM
         AND a.PGM_NM=b.PGM_NM AND a.ACTV_NM=b.ACTV_NM AND a.SACTV_NM=b.SACTV_NM
        WHERE b.SACTV_NM IS NULL
    )
    SELECT OFFC_NM, PGM_NM, SACTV_NM, count(DISTINCT FSCL_YY) AS years
    FROM pure_addons
    GROUP BY OFFC_NM, PGM_NM, SACTV_NM
    HAVING count(DISTINCT FSCL_YY) >= 2
    ORDER BY years DESC, SACTV_NM
    LIMIT 30
""")

# 5. 월별 채무 시계열 끝값
show('월별 국가채무 — 최근 12개월', """
    SELECT OJ_YY, OJ_M, GOD_SUM_AMT
    FROM debt_monthly
    ORDER BY OJ_YY DESC, CAST(OJ_M AS INTEGER) DESC
    LIMIT 12
""")

# 6. 카탈로그
print(f"\nopenapi_catalog 행 수: {con.execute('SELECT count(*) FROM openapi_catalog').fetchone()[0]}")
print(f"kodas_catalog 행 수:   {con.execute('SELECT count(*) FROM kodas_catalog').fetchone()[0]}")

con.close()
