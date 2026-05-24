"""C0 인건비형 클러스터 전체 vs 노인일자리지원 단일 — 월별 분포 비교."""
import duckdb
import pandas as pd
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

con = duckdb.connect('data/warehouse.duckdb', read_only=True)

# H3 임베딩 결과에서 C0 클러스터 활동 목록
h3 = pd.read_csv('data/results/H3_activity_embedding_11y.csv')
print(f'H3 전체 활동 = {len(h3):,}')
print(h3['cluster'].value_counts().sort_index().to_string())
print()

c0_acts = h3[h3['cluster'] == 0]['ACTV_NM'].tolist()
print(f'C0 활동 수 = {len(c0_acts)}')
print(f'C0 샘플 활동 10개:')
for a in c0_acts[:10]:
    print(f'  - {a}')
print()

# C0 전체 월별 평균 (각 활동 연-비중 평균)
placeholders = ','.join(['?'] * len(c0_acts))
q = f"""
WITH ay AS (
  SELECT FSCL_YY, ACTV_NM, EXE_M, SUM(EP_AMT) AS s
  FROM monthly_exec
  WHERE ACTV_NM IN ({placeholders}) AND FSCL_YY BETWEEN 2015 AND 2025
  GROUP BY 1, 2, 3
),
yt AS (SELECT FSCL_YY, ACTV_NM, SUM(s) AS yr FROM ay GROUP BY 1, 2 HAVING yr > 0)
SELECT EXE_M, AVG(s*1.0/yr)*100 AS pct, STDDEV(s*1.0/yr)*100 AS sd
FROM ay JOIN yt USING (FSCL_YY, ACTV_NM)
GROUP BY EXE_M ORDER BY EXE_M
"""
rows = con.execute(q, c0_acts).fetchall()

print('=== C0 클러스터 전체 — 월별 평균 비중 ===')
print('균등 가정 = 8.33%')
print('-' * 70)
for m, pct, sd in rows:
    bar = '█' * int(pct * 2)
    flag = ' ← 분기 첫달' if m in (1,4,7,10) else (' ← 12월' if m == 12 else '')
    print(f'{m:2d}월 {pct:5.2f}% (sd={sd:4.1f}) {bar}{flag}')

q1 = [r[1] for r in rows if r[0] in (1,4,7,10)]
oth = [r[1] for r in rows if r[0] not in (1,4,7,10)]
sd12 = (sum((r[1]-100/12)**2 for r in rows)/12)**0.5
print('-' * 70)
print(f'분기 첫달(1·4·7·10) 평균: {sum(q1)/4:.2f}%')
print(f'나머지 8개월 평균        : {sum(oth)/8:.2f}%')
print(f'12개월 표준편차          : {sd12:.2f}%p   (균등이면 0에 가까움)')
print(f'12월 비중                : {rows[11][1]:.2f}%')

# 후보: C0 안에서 가장 "균등"한 활동 (개별 12개월 sd 작은 것)
print()
print('=== C0 내 가장 균등한 활동 Top 10 (12개월 표준편차 작은 순) ===')
q2 = f"""
WITH ay AS (
  SELECT FSCL_YY, ACTV_NM, EXE_M, SUM(EP_AMT) AS s
  FROM monthly_exec
  WHERE ACTV_NM IN ({placeholders}) AND FSCL_YY BETWEEN 2015 AND 2025
  GROUP BY 1, 2, 3
),
yt AS (SELECT FSCL_YY, ACTV_NM, SUM(s) AS yr FROM ay GROUP BY 1, 2 HAVING yr > 0),
mp AS (SELECT FSCL_YY, ACTV_NM, EXE_M, s*1.0/yr AS p FROM ay JOIN yt USING (FSCL_YY, ACTV_NM)),
ms AS (SELECT ACTV_NM, EXE_M, AVG(p)*100 AS pct FROM mp GROUP BY 1, 2)
SELECT ACTV_NM,
       STDDEV(pct) AS sd_p,
       MAX(CASE WHEN EXE_M = 12 THEN pct END) AS dec_p,
       SUM(CASE WHEN EXE_M IN (1,4,7,10) THEN pct END) AS q1_sum
FROM ms
GROUP BY ACTV_NM
HAVING COUNT(*) = 12
ORDER BY sd_p ASC
LIMIT 10
"""
df = con.execute(q2, c0_acts).fetchdf()
print(df.to_string(index=False))
