-- 굿하트 가설 검증을 위한 SQL EDA
-- 데이터: monthly_exec (단위사업×월별 집행)
-- 핵심 변수:
--   ANEXP_BDG_CAMT     예산 (해당 월 기준 예산 — 일반적으로 연간 본예산)
--   EP_AMT             당월집행액
--   THISM_AGGR_EP_AMT  누계집행액 (1월~해당월)
-- 따라서:
--   12월 EP_AMT       = 12월 한달 집행
--   12월 THISM_AGGR_EP_AMT = 연간 총 집행
--   12월 집중도       = 12월 EP_AMT / 연간 총 집행

-- ============================================================
-- 1) 데이터 점검
-- ============================================================
SELECT FSCL_YY, count(DISTINCT EXE_M) AS months,
       count(DISTINCT OFFC_CD) AS offc_n,
       count(DISTINCT ACTV_CD) AS actv_n,
       count(*) AS rows
FROM monthly_exec
GROUP BY FSCL_YY ORDER BY FSCL_YY;

-- ============================================================
-- 2) 정부 전체 12월 집중도 시계열
-- ============================================================
WITH yearly AS (
  SELECT FSCL_YY, OFFC_CD, ACTV_CD,
         max(CASE WHEN EXE_M=12 THEN EP_AMT END) AS dec_amt,
         max(CASE WHEN EXE_M=12 THEN THISM_AGGR_EP_AMT END) AS annual_amt
  FROM monthly_exec
  GROUP BY FSCL_YY, OFFC_CD, ACTV_CD
)
SELECT FSCL_YY,
       round(sum(dec_amt) / nullif(sum(annual_amt), 0) * 100, 2) AS dec_concentration_pct,
       round(sum(annual_amt) / 1e9, 1) AS annual_billion_won
FROM yearly
WHERE annual_amt > 0
GROUP BY FSCL_YY ORDER BY FSCL_YY;

-- ============================================================
-- 3) 분야별 12월 집중도 (2024)
-- ============================================================
WITH yearly AS (
  SELECT FSCL_YY, FLD_NM, OFFC_CD, ACTV_CD,
         max(CASE WHEN EXE_M=12 THEN EP_AMT END) AS dec_amt,
         max(CASE WHEN EXE_M=12 THEN THISM_AGGR_EP_AMT END) AS annual_amt
  FROM monthly_exec WHERE FSCL_YY=2024
  GROUP BY FSCL_YY, FLD_NM, OFFC_CD, ACTV_CD
)
SELECT FLD_NM,
       round(sum(dec_amt) / nullif(sum(annual_amt), 0) * 100, 2) AS dec_concentration_pct,
       round(sum(annual_amt) / 1e9, 1) AS billion_won,
       count(DISTINCT ACTV_CD) AS actv_n
FROM yearly
WHERE annual_amt > 0
GROUP BY FLD_NM
ORDER BY dec_concentration_pct DESC;

-- ============================================================
-- 4) 부처별 12월 집중도 (2024) — 상위 30
-- ============================================================
WITH yearly AS (
  SELECT FSCL_YY, OFFC_CD, OFFC_NM, ACTV_CD,
         max(CASE WHEN EXE_M=12 THEN EP_AMT END) AS dec_amt,
         max(CASE WHEN EXE_M=12 THEN THISM_AGGR_EP_AMT END) AS annual_amt
  FROM monthly_exec WHERE FSCL_YY=2024
  GROUP BY FSCL_YY, OFFC_CD, OFFC_NM, ACTV_CD
)
SELECT OFFC_NM,
       round(sum(dec_amt) / nullif(sum(annual_amt), 0) * 100, 2) AS dec_concentration_pct,
       round(sum(annual_amt) / 1e9, 1) AS billion_won,
       count(DISTINCT ACTV_CD) AS actv_n
FROM yearly
WHERE annual_amt > 0
GROUP BY OFFC_NM
HAVING sum(annual_amt) > 1e10
ORDER BY dec_concentration_pct DESC
LIMIT 30;

-- ============================================================
-- 5) 분기 집중도 (Q4 vs Q1Q2Q3)
-- ============================================================
WITH per_actv AS (
  SELECT FSCL_YY, OFFC_NM, FLD_NM, ACTV_CD,
         sum(CASE WHEN EXE_M IN (1,2,3)   THEN EP_AMT ELSE 0 END) AS q1,
         sum(CASE WHEN EXE_M IN (4,5,6)   THEN EP_AMT ELSE 0 END) AS q2,
         sum(CASE WHEN EXE_M IN (7,8,9)   THEN EP_AMT ELSE 0 END) AS q3,
         sum(CASE WHEN EXE_M IN (10,11,12) THEN EP_AMT ELSE 0 END) AS q4,
         max(CASE WHEN EXE_M=12 THEN THISM_AGGR_EP_AMT END) AS annual
  FROM monthly_exec
  GROUP BY FSCL_YY, OFFC_NM, FLD_NM, ACTV_CD
)
SELECT FSCL_YY,
       round(sum(q1)/nullif(sum(annual),0)*100, 1) AS q1_pct,
       round(sum(q2)/nullif(sum(annual),0)*100, 1) AS q2_pct,
       round(sum(q3)/nullif(sum(annual),0)*100, 1) AS q3_pct,
       round(sum(q4)/nullif(sum(annual),0)*100, 1) AS q4_pct
FROM per_actv WHERE annual > 0
GROUP BY FSCL_YY ORDER BY FSCL_YY;

-- ============================================================
-- 6) 단위사업 사이즈별 12월 집중도 (잘게 쪼갠 사업의 게임화?)
-- ============================================================
WITH yearly AS (
  SELECT FSCL_YY, OFFC_NM, ACTV_CD,
         max(CASE WHEN EXE_M=12 THEN EP_AMT END) AS dec_amt,
         max(CASE WHEN EXE_M=12 THEN THISM_AGGR_EP_AMT END) AS annual_amt
  FROM monthly_exec WHERE FSCL_YY=2024
  GROUP BY FSCL_YY, OFFC_NM, ACTV_CD
),
binned AS (
  SELECT *,
    CASE
      WHEN annual_amt < 1e9 THEN '1. <10억'
      WHEN annual_amt < 1e10 THEN '2. 10~100억'
      WHEN annual_amt < 1e11 THEN '3. 100억~1천억'
      WHEN annual_amt < 1e12 THEN '4. 1천억~1조'
      ELSE '5. 1조 이상'
    END AS size_bin
  FROM yearly WHERE annual_amt > 0
)
SELECT size_bin,
       count(*) AS actv_n,
       round(sum(dec_amt)/nullif(sum(annual_amt),0)*100, 2) AS dec_concentration_pct,
       round(sum(annual_amt)/1e9, 0) AS billion_won
FROM binned
GROUP BY size_bin ORDER BY size_bin;

-- ============================================================
-- 7) 정보통신/과학기술 부문 vs 나머지 (2024)
-- ============================================================
WITH yearly AS (
  SELECT
    CASE WHEN FLD_NM IN ('과학기술','통신') THEN 'AI·통신·과기'
         ELSE '기타 분야' END AS grp,
    OFFC_NM, ACTV_CD,
    max(CASE WHEN EXE_M=12 THEN EP_AMT END) AS dec_amt,
    max(CASE WHEN EXE_M=12 THEN THISM_AGGR_EP_AMT END) AS annual_amt
  FROM monthly_exec WHERE FSCL_YY=2024
  GROUP BY FLD_NM, OFFC_NM, ACTV_CD
)
SELECT grp,
       count(*) AS actv_n,
       round(sum(dec_amt)/nullif(sum(annual_amt),0)*100, 2) AS dec_concentration_pct,
       round(sum(annual_amt)/1e9, 0) AS billion_won
FROM yearly WHERE annual_amt > 0
GROUP BY grp;
