"""AI 명목 예산의 부대비용 점유 가설 — 1차 시그널 점검."""
import os, sys, io, duckdb

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
con = duckdb.connect(os.path.join(ROOT, 'data', 'warehouse.duckdb'), read_only=True)

# AI 관련 세부사업 식별 — 사업명에 핵심 키워드
AI_PATTERN = "(SACTV_NM ILIKE '%AI%' OR SACTV_NM ILIKE '%인공지능%' OR SACTV_NM ILIKE '%머신러닝%' OR SACTV_NM ILIKE '%딥러닝%' OR SACTV_NM ILIKE '%LLM%' OR SACTV_NM ILIKE '%GPT%' OR SACTV_NM ILIKE '%초거대%' OR SACTV_NM ILIKE '%지능형%' OR PGM_NM ILIKE '%인공지능%' OR PGM_NM ILIKE '%AI%')"

print('='*80)
print('1) AI 키워드 매칭 세부사업 — 본예산 회차0만 (연도별)')
print('='*80)
df = con.execute(f"""
    SELECT FSCL_YY,
           count(DISTINCT SACTV_NM) AS distinct_sactv,
           count(*) AS rows,
           round(sum(Y_YY_DFN_KCUR_AMT)/1e6, 1) AS amt_eok
    FROM expenditure_budget
    WHERE SBUDG_DGR=0 AND {AI_PATTERN}
    GROUP BY FSCL_YY ORDER BY FSCL_YY
""").fetchdf()
print(df.to_string(index=False))

print('\n'+'='*80)
print('2) AI 매칭 사업의 BZ_CLS_NM 비율 vs 전체 평균 (2026 본예산)')
print('='*80)
ai_dist = con.execute(f"""
    SELECT BZ_CLS_NM,
           count(*) AS rows,
           round(sum(Y_YY_DFN_KCUR_AMT)/1e6, 1) AS amt_eok,
           round(sum(Y_YY_DFN_KCUR_AMT) * 100.0 /
                 (SELECT sum(Y_YY_DFN_KCUR_AMT) FROM expenditure_budget
                  WHERE FSCL_YY=2026 AND SBUDG_DGR=0 AND {AI_PATTERN}), 1) AS pct
    FROM expenditure_budget
    WHERE FSCL_YY=2026 AND SBUDG_DGR=0 AND {AI_PATTERN}
    GROUP BY BZ_CLS_NM ORDER BY amt_eok DESC
""").fetchdf()
print('AI 사업:')
print(ai_dist.to_string(index=False))

all_dist = con.execute("""
    SELECT BZ_CLS_NM,
           round(sum(Y_YY_DFN_KCUR_AMT) * 100.0 /
                 (SELECT sum(Y_YY_DFN_KCUR_AMT) FROM expenditure_budget
                  WHERE FSCL_YY=2026 AND SBUDG_DGR=0), 1) AS pct
    FROM expenditure_budget
    WHERE FSCL_YY=2026 AND SBUDG_DGR=0
    GROUP BY BZ_CLS_NM ORDER BY pct DESC
""").fetchdf()
print('\n정부 전체 평균:')
print(all_dist.to_string(index=False))

print('\n'+'='*80)
print('3) AI 사업 Top 20 (2026 본예산, 금액순) — 진짜 AI인지 명목 AI인지')
print('='*80)
df = con.execute(f"""
    SELECT OFFC_NM, PGM_NM, SACTV_NM, BZ_CLS_NM,
           round(Y_YY_DFN_KCUR_AMT/1e6, 1) AS amt_eok
    FROM expenditure_budget
    WHERE FSCL_YY=2026 AND SBUDG_DGR=0 AND {AI_PATTERN}
    ORDER BY Y_YY_DFN_KCUR_AMT DESC
    LIMIT 20
""").fetchdf()
print(df.to_string(index=False))

print('\n'+'='*80)
print('4) AI 매칭 사업이 속한 단위사업(ACTV) Top 10 — "이름만 AI" 사업이 끼어드는 단위사업')
print('='*80)
df = con.execute(f"""
    SELECT OFFC_NM, ACTV_NM,
           count(DISTINCT SACTV_NM) AS sactv_n,
           round(sum(Y_YY_DFN_KCUR_AMT)/1e6, 1) AS amt_eok
    FROM expenditure_budget
    WHERE FSCL_YY=2026 AND SBUDG_DGR=0 AND {AI_PATTERN}
    GROUP BY OFFC_NM, ACTV_NM
    ORDER BY amt_eok DESC LIMIT 10
""").fetchdf()
print(df.to_string(index=False))

print('\n'+'='*80)
print('5) "지원/운영/관리/기반/체계/생태계" 키워드 비중 — 부대비용 의심 지표')
print('='*80)
SUSPECT = "(SACTV_NM ILIKE '%지원%' OR SACTV_NM ILIKE '%운영%' OR SACTV_NM ILIKE '%관리%' OR SACTV_NM ILIKE '%기반%' OR SACTV_NM ILIKE '%체계%' OR SACTV_NM ILIKE '%생태계%' OR SACTV_NM ILIKE '%활성화%' OR SACTV_NM ILIKE '%센터%')"
df = con.execute(f"""
    SELECT '전체 AI 사업' AS bucket,
           round(sum(Y_YY_DFN_KCUR_AMT)/1e6, 1) AS amt_eok,
           count(*) AS rows
    FROM expenditure_budget
    WHERE FSCL_YY=2026 AND SBUDG_DGR=0 AND {AI_PATTERN}
    UNION ALL
    SELECT 'AI + 부대키워드' AS bucket,
           round(sum(Y_YY_DFN_KCUR_AMT)/1e6, 1) AS amt_eok,
           count(*) AS rows
    FROM expenditure_budget
    WHERE FSCL_YY=2026 AND SBUDG_DGR=0 AND {AI_PATTERN} AND {SUSPECT}
""").fetchdf()
print(df.to_string(index=False))

print('\n'+'='*80)
print('6) AI 사업 시계열 추이 + 부처별 분포 (2020~2026 본예산)')
print('='*80)
df = con.execute(f"""
    SELECT FSCL_YY, OFFC_NM,
           round(sum(Y_YY_DFN_KCUR_AMT)/1e6, 0) AS amt_eok
    FROM expenditure_budget
    WHERE SBUDG_DGR=0 AND {AI_PATTERN}
    GROUP BY FSCL_YY, OFFC_NM
    HAVING sum(Y_YY_DFN_KCUR_AMT) > 0
    ORDER BY FSCL_YY DESC, amt_eok DESC
""").fetchdf()
# show 2026 then 2020
print('2026:')
print(df[df.FSCL_YY==2026].head(10).to_string(index=False))
print('\n2020:')
print(df[df.FSCL_YY==2020].head(10).to_string(index=False))

con.close()
