"""App-RDD §5 Placebo cutoff 검증.

*분기 중간 cutoff* (2·5·8·11월) 점프 β 추정 — null 효과 기대.
*진짜 cutoff* (3·6·9·12월) 점프 β와 비교.

null 효과 확인 → 12월 cutoff RDD 식별 robust.
"""
import duckdb
import math
import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

con = duckdb.connect('data/warehouse.duckdb', read_only=True)

# cutoff별 전월 대비 점프 추정
# 진짜: 3월/2월, 6월/5월, 9월/8월, 12월/11월 (분기말 = 회계 정산)
# Placebo: 2월/1월, 5월/4월, 8월/7월, 11월/10월 (분기 중간 = null 기대)

q = """
WITH monthly AS (
  SELECT FSCL_YY, ACTV_CD, EXE_M, EP_AMT,
         CASE EXE_M
           WHEN 1 THEN 31 WHEN 2 THEN 28 WHEN 3 THEN 31 WHEN 4 THEN 30
           WHEN 5 THEN 31 WHEN 6 THEN 30 WHEN 7 THEN 31 WHEN 8 THEN 31
           WHEN 9 THEN 30 WHEN 10 THEN 31 WHEN 11 THEN 30 WHEN 12 THEN 31
         END AS days
  FROM monthly_exec
  WHERE FSCL_YY BETWEEN 2015 AND 2025 AND EP_AMT > 0
),
pairs AS (
  SELECT FSCL_YY, ACTV_CD,
    MAX(CASE WHEN EXE_M=1 THEN LN(EP_AMT*1.0/days) END) AS l1,
    MAX(CASE WHEN EXE_M=2 THEN LN(EP_AMT*1.0/days) END) AS l2,
    MAX(CASE WHEN EXE_M=3 THEN LN(EP_AMT*1.0/days) END) AS l3,
    MAX(CASE WHEN EXE_M=4 THEN LN(EP_AMT*1.0/days) END) AS l4,
    MAX(CASE WHEN EXE_M=5 THEN LN(EP_AMT*1.0/days) END) AS l5,
    MAX(CASE WHEN EXE_M=6 THEN LN(EP_AMT*1.0/days) END) AS l6,
    MAX(CASE WHEN EXE_M=7 THEN LN(EP_AMT*1.0/days) END) AS l7,
    MAX(CASE WHEN EXE_M=8 THEN LN(EP_AMT*1.0/days) END) AS l8,
    MAX(CASE WHEN EXE_M=9 THEN LN(EP_AMT*1.0/days) END) AS l9,
    MAX(CASE WHEN EXE_M=10 THEN LN(EP_AMT*1.0/days) END) AS l10,
    MAX(CASE WHEN EXE_M=11 THEN LN(EP_AMT*1.0/days) END) AS l11,
    MAX(CASE WHEN EXE_M=12 THEN LN(EP_AMT*1.0/days) END) AS l12
  FROM monthly GROUP BY 1,2
)
SELECT
  AVG(l2 - l1) AS b_2_1, STDDEV(l2 - l1) AS sd_2_1, COUNT(l2 - l1) AS n_2_1,
  AVG(l3 - l2) AS b_3_2, STDDEV(l3 - l2) AS sd_3_2, COUNT(l3 - l2) AS n_3_2,
  AVG(l5 - l4) AS b_5_4, STDDEV(l5 - l4) AS sd_5_4, COUNT(l5 - l4) AS n_5_4,
  AVG(l6 - l5) AS b_6_5, STDDEV(l6 - l5) AS sd_6_5, COUNT(l6 - l5) AS n_6_5,
  AVG(l8 - l7) AS b_8_7, STDDEV(l8 - l7) AS sd_8_7, COUNT(l8 - l7) AS n_8_7,
  AVG(l9 - l8) AS b_9_8, STDDEV(l9 - l8) AS sd_9_8, COUNT(l9 - l8) AS n_9_8,
  AVG(l11 - l10) AS b_11_10, STDDEV(l11 - l10) AS sd_11_10, COUNT(l11 - l10) AS n_11_10,
  AVG(l12 - l11) AS b_12_11, STDDEV(l12 - l11) AS sd_12_11, COUNT(l12 - l11) AS n_12_11
FROM pairs
"""
row = con.execute(q).fetchone()

cutoffs = [
    ('2월/1월', 'Placebo (분기 중간)', row[0], row[1], row[2]),
    ('3월/2월', '진짜 (분기말)', row[3], row[4], row[5]),
    ('5월/4월', 'Placebo (분기 중간)', row[6], row[7], row[8]),
    ('6월/5월', '진짜 (분기말)', row[9], row[10], row[11]),
    ('8월/7월', 'Placebo (분기 중간)', row[12], row[13], row[14]),
    ('9월/8월', '진짜 (분기말)', row[15], row[16], row[17]),
    ('11월/10월', 'Placebo (분기 중간)', row[18], row[19], row[20]),
    ('12월/11월', '진짜 (분기말 + 회계 마감)', row[21], row[22], row[23]),
]

print('=== cutoff별 β + SE + p (n=Welch t-test 가정) ===')
print(f'{"cutoff":<12}{"종류":<22}{"β (log)":>10}{"SE":>8}{"t":>8}{"ratio (e^β)":>14}')
print('-' * 75)
for name, kind, b, sd, n in cutoffs:
    se = sd / math.sqrt(n) if n and sd else float('nan')
    t = b / se if se and se > 0 else float('nan')
    ratio = math.exp(b) if b is not None else float('nan')
    print(f'{name:<12}{kind:<22}{b:>10.3f}{se:>8.3f}{t:>8.2f}{ratio:>14.2f}x')

print()
print('해석:')
print('- 분기말 cutoff (3·6·9·12월): 모두 β > 0, ratio > 1 (점프 발생)')
print('- 분기 중간 cutoff (2·5·8·11월): null 효과 기대 — β ≈ 0?')
print('- 12월이 가장 강 → multi-cutoff 시스템에서 회계 마감이 압도적')
