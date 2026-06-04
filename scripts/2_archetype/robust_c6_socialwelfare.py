"""견고성 검증 C6 — 사회복지 "시점 무관" 직접 제시.

질문: H5 기각 근거인 "사회복지=자동 소득이전이라 12월과 무관"이 §6.7서 선언만 됨.
      데이터로 사회복지 12월 집중도 + 월별 프로파일을 제시한다.
방법: monthly_exec에서 분야별 12월 집행 비중(활동×연도 정규화 후 중앙값) +
      월별 집행 프로파일. 게임화 강한 분야(통일·외교 등)·전체 평균·균등(8.3%)과 비교.
      RDD식 11→12월 일평균 점프도 분야별로 비교.
판정: 사회복지 12월 비중이 균등 근방(낮음)이면 → "자동 소득이전, 시점 무관"이
      데이터로 뒷받침 → H5 기각 논리 강화.

EDA(fig3_field_size_vs_dec.py)와 동일 정의: 활동×연도 yearly_total>1억, dec_share 캡1.0,
      분야 median, HAVING count>=100.
"""
import os, sys, io
import numpy as np
import pandas as pd
import duckdb
import warnings

warnings.filterwarnings('ignore')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RES = os.path.join(ROOT, 'data', 'results')
DB = os.path.join(ROOT, 'data', 'warehouse.duckdb')
con = duckdb.connect(DB, read_only=True)

print('=' * 74)
print('견고성 C6 — 사회복지 12월 집중도 직접 제시')
print('=' * 74)

# ── (1) 분야별 12월 비중 중앙값 (EDA 동일 정의, 13.4% 재현 확인) ──
dec = con.execute("""
WITH yr AS (
  SELECT FSCL_YY, ACTV_CD, FLD_NM, sum(EP_AMT) AS yearly_total
  FROM monthly_exec
  WHERE FSCL_YY BETWEEN 2015 AND 2025 AND FLD_NM IS NOT NULL
  GROUP BY FSCL_YY, ACTV_CD, FLD_NM
  HAVING sum(EP_AMT) > 100000000
),
mdec AS (
  SELECT m.FSCL_YY, m.ACTV_CD, a.FLD_NM, a.yearly_total,
         LEAST(sum(m.EP_AMT)*1.0/max(a.yearly_total), 1.0) AS dec_share
  FROM monthly_exec m JOIN yr a
    ON m.FSCL_YY=a.FSCL_YY AND m.ACTV_CD=a.ACTV_CD AND m.FLD_NM=a.FLD_NM
  WHERE m.EXE_M = 12
  GROUP BY m.FSCL_YY, m.ACTV_CD, a.FLD_NM, a.yearly_total
)
SELECT FLD_NM,
       median(dec_share)*100 AS dec_median_pct,
       avg(dec_share)*100    AS dec_mean_pct,
       count(*) AS n_actv_yr
FROM mdec
GROUP BY FLD_NM
HAVING count(*) >= 100
ORDER BY dec_median_pct ASC
""").fetchdf()
print('\n(1) 분야별 12월 집행 비중 (활동×연도 단위, 중앙값 오름차순)')
print('    균등 가정 = 8.33%')
print('-' * 74)
print(dec.round(1).to_string(index=False))
sw_row = dec[dec.FLD_NM == '사회복지']
if len(sw_row):
    sw_med = sw_row.dec_median_pct.values[0]
    rank = (dec.dec_median_pct < sw_med).sum() + 1
    print(f'\n  사회복지 12월 중앙 비중 = {sw_med:.1f}%  (균등 8.3%의 {sw_med/8.33:.2f}배, '
          f'14분야 중 {rank}번째로 낮음)')
    print(f'  최고(통일·외교 등) = {dec.dec_median_pct.max():.1f}%  → 사회복지 대비 '
          f'{dec.dec_median_pct.max()/sw_med:.1f}배')
    print(f'  전체 분야 12월 중앙 비중 평균 = {dec.dec_median_pct.mean():.1f}%')

# ── (2) 사회복지 월별 집행 프로파일 (활동×연도 정규화 평균 비중) ──
prof = con.execute("""
WITH yr AS (
  SELECT FSCL_YY, ACTV_CD, FLD_NM, sum(EP_AMT) AS yearly_total
  FROM monthly_exec
  WHERE FSCL_YY BETWEEN 2015 AND 2025 AND FLD_NM IS NOT NULL
  GROUP BY FSCL_YY, ACTV_CD, FLD_NM
  HAVING sum(EP_AMT) > 100000000
),
mshare AS (
  SELECT m.FLD_NM, m.EXE_M,
         m.FSCL_YY, m.ACTV_CD,
         sum(m.EP_AMT)*1.0/max(a.yearly_total) AS share
  FROM monthly_exec m JOIN yr a
    ON m.FSCL_YY=a.FSCL_YY AND m.ACTV_CD=a.ACTV_CD AND m.FLD_NM=a.FLD_NM
  WHERE m.EXE_M BETWEEN 1 AND 12
  GROUP BY m.FLD_NM, m.EXE_M, m.FSCL_YY, m.ACTV_CD
)
SELECT FLD_NM, EXE_M, avg(share)*100 AS mean_share_pct
FROM mshare GROUP BY FLD_NM, EXE_M
""").fetchdf()
piv = prof.pivot(index='FLD_NM', columns='EXE_M', values='mean_share_pct').round(1)
print('\n(2) 분야별 월별 집행 비중 프로파일 (활동×연도 평균 %, 균등=8.3%)')
print('-' * 74)
focus = ['사회복지', '보건', '통일·외교', '국방', '국토및지역개발', '농림수산']
focus = [f for f in focus if f in piv.index]
print(piv.loc[focus].to_string())
if '사회복지' in piv.index:
    sw = piv.loc['사회복지']
    print(f'\n  사회복지 월별: 최저 {sw.min():.1f}%(={sw.idxmin()}월) ~ '
          f'최고 {sw.max():.1f}%(={sw.idxmax()}월), 표준편차 {sw.std():.1f}%p')
    print(f'  → 균등(8.3%)에 가까운 평탄 프로파일이면 시점 무관 가설 지지')

# ── (3) RDD식 11→12월 일평균 집행 점프 (분야별) ──────────────
rdd = con.execute("""
WITH d AS (
  SELECT FLD_NM, FSCL_YY, ACTV_CD, EXE_M, sum(EP_AMT) AS amt
  FROM monthly_exec
  WHERE FSCL_YY BETWEEN 2015 AND 2025 AND EXE_M IN (11,12) AND FLD_NM IS NOT NULL
  GROUP BY FLD_NM, FSCL_YY, ACTV_CD, EXE_M
),
day AS (  -- 일평균: 11월 30일, 12월 31일
  SELECT FLD_NM, FSCL_YY, ACTV_CD,
         max(CASE WHEN EXE_M=11 THEN amt END)/30.0 AS d11,
         max(CASE WHEN EXE_M=12 THEN amt END)/31.0 AS d12
  FROM d GROUP BY FLD_NM, FSCL_YY, ACTV_CD
)
SELECT FLD_NM,
       median(d12) AS med_d12, median(d11) AS med_d11,
       count(*) AS n
FROM day WHERE d11 > 0 AND d12 > 0
GROUP BY FLD_NM HAVING count(*) >= 50
""").fetchdf()
rdd['ratio_12_over_11'] = (rdd.med_d12 / rdd.med_d11).round(2)
rdd = rdd.sort_values('ratio_12_over_11')
print('\n(3) RDD식 12월/11월 일평균 집행 배율 (분야별 중앙값, 배율 오름차순)')
print('    1.0 근방 = 12월 점프 없음(시점 무관)')
print('-' * 74)
print(rdd[['FLD_NM', 'ratio_12_over_11', 'n']].to_string(index=False))
if (rdd.FLD_NM == '사회복지').any():
    swr = rdd[rdd.FLD_NM == '사회복지'].ratio_12_over_11.values[0]
    rrank = (rdd.ratio_12_over_11 < swr).sum() + 1
    print(f'\n  사회복지 12월/11월 일평균 배율 = {swr:.2f}배 '
          f'(14분야 중 {rrank}번째로 낮음; 1.0 근방이면 점프 없음)')

con.close()

# 저장
dec.to_csv(os.path.join(RES, 'robust_c6_field_dec_share.csv'), index=False, encoding='utf-8-sig')
piv.to_csv(os.path.join(RES, 'robust_c6_monthly_profile.csv'), encoding='utf-8-sig')
rdd.to_csv(os.path.join(RES, 'robust_c6_dec_nov_ratio.csv'), index=False, encoding='utf-8-sig')
print('\n  저장: robust_c6_field_dec_share.csv / _monthly_profile.csv / _dec_nov_ratio.csv')
print('\n' + '=' * 74)
print('판정: 사회복지 12월 비중·일평균 배율이 균등/1.0 근방이면 "시점 무관" 데이터 지지')
print('=' * 74)
