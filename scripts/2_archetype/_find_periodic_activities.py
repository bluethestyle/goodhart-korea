"""C2 클러스터 안에서 진짜 분기/반기 주기성이 강한 활동 search.

12개월 비중 vector를 DFT 분해:
  - freq 1 (period 12): 연주기 (1월 집중 또는 12월 집중)
  - freq 2 (period 6): 반기 (6·12월 또는 1·7월)
  - freq 4 (period 3): 분기 (1·4·7·10 또는 3·6·9·12)

각 활동의 freq별 magnitude를 클러스터 내에서 비교.
"""
import duckdb
import numpy as np
import pandas as pd
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

con = duckdb.connect('data/warehouse.duckdb', read_only=True)
h3 = pd.read_csv('data/results/H3_activity_embedding_11y.csv')

# C2 클러스터 활동 리스트 (실제 cluster=2)
c2_acts = h3[h3['cluster'] == 2]['ACTV_NM'].tolist()
print(f'C2 활동 수 = {len(c2_acts)}')

# 각 활동 12개월 평균 비중 fetch
ph = ','.join(['?'] * len(c2_acts))
q = f"""
WITH ay AS (
  SELECT FSCL_YY, ACTV_NM, EXE_M, SUM(EP_AMT) AS s
  FROM monthly_exec
  WHERE ACTV_NM IN ({ph}) AND FSCL_YY BETWEEN 2015 AND 2025
  GROUP BY 1, 2, 3
),
yt AS (SELECT FSCL_YY, ACTV_NM, SUM(s) AS yr FROM ay GROUP BY 1, 2 HAVING yr > 0),
mp AS (SELECT FSCL_YY, ACTV_NM, EXE_M, s*1.0/yr AS p FROM ay JOIN yt USING (FSCL_YY, ACTV_NM)),
pa AS (SELECT ACTV_NM, EXE_M, AVG(p)*100 AS pct, SUM(yr) AS yr_total FROM mp JOIN yt USING (FSCL_YY, ACTV_NM) GROUP BY 1, 2)
SELECT ACTV_NM, EXE_M, pct, yr_total FROM pa
"""
df = con.execute(q, c2_acts).fetchdf()
piv = df.pivot_table(index='ACTV_NM', columns='EXE_M', values='pct', fill_value=0)
piv = piv.reindex(columns=range(1, 13), fill_value=0)
yr_avg = df.groupby('ACTV_NM')['yr_total'].max() / 11 / 1e8  # 억원

# DFT 분해 — 각 활동의 mean-centered vector
results = []
for actv in piv.index:
    v = piv.loc[actv].values
    v_centered = v - v.mean()
    F = np.fft.fft(v_centered)
    mag = np.abs(F)
    # mag[0] = DC (=0 after centering), mag[1] = freq1 (period 12),
    # mag[2] = freq2 (period 6 = 반기), mag[4] = freq4 (period 3 = 분기)
    results.append({
        'ACTV_NM': actv,
        'mag_annual': mag[1],
        'mag_half': mag[2],
        'mag_q': mag[4],
        'mag_total': mag[1:7].sum(),  # 의미 있는 주파수 전체
        'sd': v.std(),
        'dec': v[11],
        'jan': v[0],
        'q1_sum': v[[0,3,6,9]].sum(),
        'q3_sum': v[[2,5,8,11]].sum(),
        'yr_avg_kw': yr_avg.get(actv, 0),
    })
rdf = pd.DataFrame(results)

# 반기 주기성 강한 활동 (freq 2 magnitude 큼)
print('\n=== C2 안에서 반기(6개월) 주기성 강한 활동 Top 10 ===')
top_half = rdf.nlargest(10, 'mag_half')[['ACTV_NM', 'mag_half', 'mag_annual', 'mag_q', 'sd', 'dec', 'yr_avg_kw']]
print(top_half.to_string(index=False))

# 분기 주기성 강한 활동 (freq 4 magnitude 큼)
print('\n=== C2 안에서 분기(3개월) 주기성 강한 활동 Top 10 ===')
top_q = rdf.nlargest(10, 'mag_q')[['ACTV_NM', 'mag_q', 'mag_annual', 'mag_half', 'sd', 'dec', 'yr_avg_kw']]
print(top_q.to_string(index=False))

# 반기/분기 비율이 연주기보다 큰 활동 — "사이클이 주기적"
rdf['cycle_ratio'] = (rdf['mag_half'] + rdf['mag_q']) / (rdf['mag_annual'] + 1e-6)
print('\n=== C2 안에서 (반기+분기)/(연주기) 비율 가장 큰 Top 10 — 진짜 cycle ===')
top_cyc = rdf.nlargest(10, 'cycle_ratio')[['ACTV_NM', 'cycle_ratio', 'mag_annual', 'mag_half', 'mag_q', 'sd', 'yr_avg_kw']]
print(top_cyc.to_string(index=False))

# 한국산업인력공단출연 자기 위치
print('\n=== 한국산업인력공단출연 자기 분해 ===')
my_row = rdf[rdf['ACTV_NM'] == '한국산업인력공단출연'].iloc[0]
print(f'  연주기 magnitude (freq 1) = {my_row["mag_annual"]:.2f}')
print(f'  반기 magnitude (freq 2)   = {my_row["mag_half"]:.2f}')
print(f'  분기 magnitude (freq 4)   = {my_row["mag_q"]:.2f}')
print(f'  cycle_ratio (반기+분기)/(연주기) = {my_row["cycle_ratio"]:.3f} ← <1이면 연주기가 주된 성분')

# C2 전체 활동의 cycle_ratio 분포
print(f'\n=== C2 클러스터 전체 cycle_ratio 분포 ===')
print(f'  중앙값: {rdf["cycle_ratio"].median():.3f}')
print(f'  p75:    {rdf["cycle_ratio"].quantile(0.75):.3f}')
print(f'  p90:    {rdf["cycle_ratio"].quantile(0.90):.3f}')
print(f'  최대:   {rdf["cycle_ratio"].max():.3f}')
print(f'  cycle_ratio > 1 (주기성이 연주기보다 강한 활동) = '
      f'{(rdf["cycle_ratio"] > 1).sum()} / {len(rdf)}개')

# C2 평균 vector 자체의 분해
mean_v = piv.mean(axis=0).values
mean_v_c = mean_v - mean_v.mean()
F_mean = np.fft.fft(mean_v_c)
mag_mean = np.abs(F_mean)
print('\n=== C2 클러스터 평균 vector 분해 ===')
print(f'  연주기 magnitude (freq 1) = {mag_mean[1]:.2f}')
print(f'  반기 magnitude (freq 2)   = {mag_mean[2]:.2f}')
print(f'  분기 magnitude (freq 4)   = {mag_mean[4]:.2f}')
print(f'  cycle_ratio = {(mag_mean[2]+mag_mean[4])/(mag_mean[1]+1e-6):.3f}')
print(f'  → 클러스터 평균 자체가 cycle_ratio < 1이면 "분기·반기 사이클" narrative는 평균에서 도출된 게 아님')
