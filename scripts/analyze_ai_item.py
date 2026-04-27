"""AI 명목 사업의 통계목(CITM/EITM) 단위 비용 구조 분해.

가설: AI 사업의 직접비(자산취득비/연구개발비)는 적고
      간접비(연구용역비/운영비/업무추진비)가 많을 것이다.
"""
import os, sys, io, duckdb

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
con = duckdb.connect(os.path.join(ROOT, 'data', 'warehouse.duckdb'), read_only=True)

AI_PATTERN = ("(SACTV_NM ILIKE '%AI%' OR SACTV_NM ILIKE '%인공지능%' OR "
              "SACTV_NM ILIKE '%머신러닝%' OR SACTV_NM ILIKE '%딥러닝%' OR "
              "SACTV_NM ILIKE '%LLM%' OR SACTV_NM ILIKE '%GPT%' OR "
              "SACTV_NM ILIKE '%초거대%' OR SACTV_NM ILIKE '%지능형%')")

def show(title, sql):
    print(f'\n{"="*80}\n{title}\n{"="*80}')
    print(con.execute(sql).fetchdf().to_string(index=False, max_rows=40))

# 1. AI 사업의 편성목 분포 (2026 본예산)
show('1) AI 사업의 CITM_NM 분포 (2026 본예산, 금액 기준)', f"""
    SELECT CITM_NM,
           round(sum(Y_YY_DFN_KCUR_AMT)/1e6, 1) AS amt_eok,
           round(sum(Y_YY_DFN_KCUR_AMT)*100.0 /
                 (SELECT sum(Y_YY_DFN_KCUR_AMT) FROM expenditure_item
                  WHERE FSCL_YY=2026 AND SBUDG_DGR=0 AND {AI_PATTERN}), 1) AS pct
    FROM expenditure_item
    WHERE FSCL_YY=2026 AND SBUDG_DGR=0 AND {AI_PATTERN}
    GROUP BY CITM_NM
    ORDER BY amt_eok DESC
""")

# 2. 비-AI 동분야 비교 (정보통신 분야 + 과학기술 R&D 등)
show('2) 비-AI vs AI 사업 — CITM_NM 비율 비교 (2026 본예산)', f"""
    WITH ai_sum AS (
        SELECT CITM_NM, sum(Y_YY_DFN_KCUR_AMT) AS amt
        FROM expenditure_item
        WHERE FSCL_YY=2026 AND SBUDG_DGR=0 AND {AI_PATTERN}
        GROUP BY CITM_NM
    ),
    ai_total AS (SELECT sum(amt) AS tot FROM ai_sum),
    all_sum AS (
        SELECT CITM_NM, sum(Y_YY_DFN_KCUR_AMT) AS amt
        FROM expenditure_item
        WHERE FSCL_YY=2026 AND SBUDG_DGR=0
        GROUP BY CITM_NM
    ),
    all_total AS (SELECT sum(amt) AS tot FROM all_sum)
    SELECT a.CITM_NM,
           round(a.amt/1e6, 1) AS ai_eok,
           round(a.amt * 100.0 / (SELECT tot FROM ai_total), 2) AS ai_pct,
           round(b.amt * 100.0 / (SELECT tot FROM all_total), 2) AS all_pct,
           round(
             (a.amt * 100.0 / (SELECT tot FROM ai_total)) -
             (b.amt * 100.0 / (SELECT tot FROM all_total)), 2
           ) AS gap_pp
    FROM ai_sum a
    LEFT JOIN all_sum b USING (CITM_NM)
    ORDER BY ai_eok DESC
""")

# 3. AI 사업의 EITM_NM(편성세목) — 더 세부
show('3) AI 사업 — EITM_NM(편성세목) 상세 Top 25 (2026 본예산)', f"""
    SELECT CITM_NM, EITM_NM,
           round(sum(Y_YY_DFN_KCUR_AMT)/1e6, 1) AS amt_eok,
           count(DISTINCT SACTV_NM) AS sactv_n
    FROM expenditure_item
    WHERE FSCL_YY=2026 AND SBUDG_DGR=0 AND {AI_PATTERN}
    GROUP BY CITM_NM, EITM_NM
    ORDER BY amt_eok DESC
    LIMIT 25
""")

# 4. 1위 사업 "AI컴퓨팅 자원 활용 기반 강화" 통계목 분해
show('4) ★ AI컴퓨팅 자원 활용 기반 강화 (2,108억) — 통계목 단위 분해', """
    SELECT CITM_NM, EITM_NM,
           round(sum(Y_YY_DFN_KCUR_AMT)/1e6, 1) AS amt_eok,
           round(sum(Y_YY_DFN_KCUR_AMT)*100.0/
                 (SELECT sum(Y_YY_DFN_KCUR_AMT) FROM expenditure_item
                  WHERE FSCL_YY=2026 AND SBUDG_DGR=0
                    AND SACTV_NM='AI컴퓨팅 자원 활용 기반 강화'), 2) AS pct
    FROM expenditure_item
    WHERE FSCL_YY=2026 AND SBUDG_DGR=0
      AND SACTV_NM='AI컴퓨팅 자원 활용 기반 강화'
    GROUP BY CITM_NM, EITM_NM
    ORDER BY amt_eok DESC
""")

# 5. 시계열: AI 사업 편성목 비율 변화 (2020~2026)
show('5) AI 사업 CITM_NM 비율 시계열 (직접비 vs 간접비)', f"""
    WITH categorized AS (
        SELECT FSCL_YY,
               CASE
                 WHEN CITM_NM IN ('자산취득비','유형자산','무형자산','건설비',
                                  '자체연구개발비','기술료','연구개발비')
                   THEN '직접투자(자산/R&D)'
                 WHEN CITM_NM IN ('연구용역비','정책연구비','일반용역비')
                   THEN '용역비'
                 WHEN CITM_NM IN ('운영비','업무추진비','여비','특수활동비',
                                  '직무수행경비','일용임금','인건비')
                   THEN '운영·경비·인건'
                 WHEN CITM_NM IN ('민간이전','일반출연금','보전금','민간경상보조',
                                  '민간자본보조','출연금','보조금')
                   THEN '이전·출연·보조'
                 ELSE '기타'
               END AS bucket,
               Y_YY_DFN_KCUR_AMT AS amt
        FROM expenditure_item
        WHERE SBUDG_DGR=0 AND {AI_PATTERN}
    ),
    yearly AS (
        SELECT FSCL_YY, bucket, sum(amt) AS amt
        FROM categorized GROUP BY FSCL_YY, bucket
    ),
    total AS (SELECT FSCL_YY, sum(amt) AS tot FROM yearly GROUP BY FSCL_YY)
    SELECT y.FSCL_YY, y.bucket,
           round(y.amt/1e6, 1) AS amt_eok,
           round(y.amt*100.0/t.tot, 1) AS pct
    FROM yearly y JOIN total t USING (FSCL_YY)
    ORDER BY FSCL_YY, amt_eok DESC
""")

# 6. 같은 분석을 동일 분야(과학기술/SW) 비-AI 사업과 비교
show('6) 동일 영역(과기정통부 R&D) — AI vs 비-AI 직접비/간접비 비율 (2026 본예산)', f"""
    WITH base AS (
        SELECT CASE WHEN {AI_PATTERN} THEN 'AI' ELSE '비-AI' END AS grp,
               CASE
                 WHEN CITM_NM IN ('자산취득비','유형자산','무형자산','건설비',
                                  '자체연구개발비','기술료','연구개발비')
                   THEN '직접투자'
                 WHEN CITM_NM IN ('연구용역비','정책연구비','일반용역비')
                   THEN '용역비'
                 WHEN CITM_NM IN ('운영비','업무추진비','여비','직무수행경비','인건비')
                   THEN '운영·경비'
                 ELSE '기타'
               END AS bucket,
               Y_YY_DFN_KCUR_AMT AS amt
        FROM expenditure_item
        WHERE FSCL_YY=2026 AND SBUDG_DGR=0
          AND OFFC_NM='과학기술정보통신부'
    ),
    sums AS (SELECT grp, bucket, sum(amt) AS amt FROM base GROUP BY grp, bucket),
    totals AS (SELECT grp, sum(amt) AS tot FROM sums GROUP BY grp)
    SELECT s.grp, s.bucket,
           round(s.amt/1e6, 1) AS amt_eok,
           round(s.amt*100.0/t.tot, 1) AS pct
    FROM sums s JOIN totals t USING (grp)
    ORDER BY grp, amt_eok DESC
""")

con.close()
