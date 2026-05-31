"""분기말 cutoff별 점프 비교 (3·6·9·12월 vs 직전월). archetype별 분해.

사용자 질문 (2026-05-21): "12월만 보지 말고 분기말 다 봐야 하는 거 아닌가?"
→ 분기말 cycle baseline 대비 12월이 가장 강한지 검증.
"""
import duckdb
import math
import sys
sys.stdout.reconfigure(encoding='utf-8')

con = duckdb.connect('data/warehouse.duckdb', read_only=True)
q = """
WITH cluster_map AS (
  SELECT * FROM read_csv_auto('data/results/H3_activity_embedding_11y.csv')
),
monthly AS (
  SELECT m.FSCL_YY, m.ACTV_CD, m.ACTV_NM, m.OFFC_NM, m.FLD_NM, m.PGM_NM, m.EXE_M, m.EP_AMT,
         CASE m.EXE_M
           WHEN 1 THEN 31 WHEN 2 THEN 28 WHEN 3 THEN 31 WHEN 4 THEN 30
           WHEN 5 THEN 31 WHEN 6 THEN 30 WHEN 7 THEN 31 WHEN 8 THEN 31
           WHEN 9 THEN 30 WHEN 10 THEN 31 WHEN 11 THEN 30 WHEN 12 THEN 31
         END AS days
  FROM monthly_exec m
  WHERE m.FSCL_YY BETWEEN 2015 AND 2025 AND m.EP_AMT > 0
),
joined AS (
  SELECT mo.*, c.cluster
  FROM monthly mo
  LEFT JOIN cluster_map c
    ON mo.FLD_NM=c.FLD_NM AND mo.OFFC_NM=c.OFFC_NM
    AND mo.PGM_NM=c.PGM_NM AND mo.ACTV_NM=c.ACTV_NM
),
pairs AS (
  SELECT FSCL_YY, ACTV_CD, cluster,
    MAX(CASE WHEN EXE_M=2 THEN LN(EP_AMT*1.0/days) END) AS l_feb,
    MAX(CASE WHEN EXE_M=3 THEN LN(EP_AMT*1.0/days) END) AS l_mar,
    MAX(CASE WHEN EXE_M=5 THEN LN(EP_AMT*1.0/days) END) AS l_may,
    MAX(CASE WHEN EXE_M=6 THEN LN(EP_AMT*1.0/days) END) AS l_jun,
    MAX(CASE WHEN EXE_M=8 THEN LN(EP_AMT*1.0/days) END) AS l_aug,
    MAX(CASE WHEN EXE_M=9 THEN LN(EP_AMT*1.0/days) END) AS l_sep,
    MAX(CASE WHEN EXE_M=11 THEN LN(EP_AMT*1.0/days) END) AS l_nov,
    MAX(CASE WHEN EXE_M=12 THEN LN(EP_AMT*1.0/days) END) AS l_dec
  FROM joined GROUP BY 1,2,3
)
SELECT 'A_전체' AS grp,
       AVG(l_mar - l_feb) AS b_3_2,
       AVG(l_jun - l_may) AS b_6_5,
       AVG(l_sep - l_aug) AS b_9_8,
       AVG(l_dec - l_nov) AS b_12_11,
       COUNT(*) AS n
FROM pairs
UNION ALL
SELECT 'B_C0인건비형', AVG(l_mar - l_feb), AVG(l_jun - l_may),
       AVG(l_sep - l_aug), AVG(l_dec - l_nov), COUNT(*)
FROM pairs WHERE cluster=0
UNION ALL
SELECT 'C_C1자산취득형', AVG(l_mar - l_feb), AVG(l_jun - l_may),
       AVG(l_sep - l_aug), AVG(l_dec - l_nov), COUNT(*)
FROM pairs WHERE cluster=1
UNION ALL
SELECT 'D_C2출연금형', AVG(l_mar - l_feb), AVG(l_jun - l_may),
       AVG(l_sep - l_aug), AVG(l_dec - l_nov), COUNT(*)
FROM pairs WHERE cluster=2
UNION ALL
SELECT 'E_C3정상사업', AVG(l_mar - l_feb), AVG(l_jun - l_may),
       AVG(l_sep - l_aug), AVG(l_dec - l_nov), COUNT(*)
FROM pairs WHERE cluster=3
ORDER BY grp
"""
df = con.execute(q).fetchdf()

print('=== cutoff별 log 점프 β (전월 → 분기말) ===')
print(df.to_string(index=False))
print()
print('=== ratio 환산 (e^β = 점프 배율) ===')
print(f'{"그룹":<18}{"3월/2월":>10}{"6월/5월":>10}{"9월/8월":>10}{"12월/11월":>12}{"n":>10}')
print('-' * 70)
for _, r in df.iterrows():
    grp = r['grp'][2:]  # prefix 제거
    r32 = math.exp(r['b_3_2'])
    r65 = math.exp(r['b_6_5'])
    r98 = math.exp(r['b_9_8'])
    r1211 = math.exp(r['b_12_11'])
    n = int(r['n'])
    print(f'{grp:<18}{r32:>9.2f}x{r65:>9.2f}x{r98:>9.2f}x{r1211:>11.2f}x{n:>10}')
print()
print('해석:')
print('- 12월이 가장 큰 cutoff인지 / archetype별로 어느 cutoff가 강한지 직접 비교 가능')
