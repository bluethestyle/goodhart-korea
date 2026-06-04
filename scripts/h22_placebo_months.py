# H2 RDD placebo — 마감월(3·6·9·12) vs 비마감월 월전이 점프 배수 비교
# 목적: 12월 점프(×1.91)가 일반 계절성이 아니라 회계연도/분기 마감의 제도효과임을
#       비(非)마감 월전이에서 점프가 없음(≈배경추세 수준)을 보여 입증(placebo).
# 방법: 활동(ACTV_CD)×연도별 월 daily-avg(=EP_AMT/월일수)의 m/m-1 로그비 풀링,
#       exp(평균)=배수. 활동코드 클러스터 SE. 2015~2025(2026 부분연도 제외).
import duckdb, calendar, math
import pandas as pd

con = duckdb.connect('data/warehouse.duckdb', read_only=True)
df = con.execute("""
  SELECT FSCL_YY yr, EXE_M m, ACTV_CD cd, SUM(EP_AMT) ep
  FROM monthly_exec
  WHERE FSCL_YY BETWEEN 2015 AND 2025 AND EXE_M BETWEEN 1 AND 12
  GROUP BY 1,2,3
""").df()

df['days'] = [calendar.monthrange(int(y), int(m))[1] for y, m in zip(df.yr, df.m)]
df['davg'] = df.ep / df.days
df = df[df.ep > 0].copy()

piv = df.pivot_table(index=['yr', 'cd'], columns='m', values='davg')

rows = []
for m in range(2, 13):
    if m in piv.columns and (m - 1) in piv.columns:
        sub = piv[[m - 1, m]].dropna()
        lr = sub[m].apply(math.log) - sub[m - 1].apply(math.log)
        mult = math.exp(lr.mean())
        n = len(lr)
        se = lr.std() / (n ** 0.5)
        typ = 'deadline' if m in (3, 6, 9, 12) else 'placebo'
        rows.append((f'{m}/{m-1}', m, round(mult, 3), n, round(se, 4), typ))

out = pd.DataFrame(rows, columns=['transition', 'month', 'multiple', 'n', 'se_logratio', 'type'])
out.to_csv('data/results/H22_placebo_months.csv', index=False, encoding='utf-8-sig')

dl = out[out.type == 'deadline']
pl = out[out.type == 'placebo']
plmax_i = pl.multiple.idxmax()
with open('data/results/H22_placebo_summary.txt', 'w', encoding='utf-8') as f:
    f.write(out.to_string(index=False))
    f.write('\n\n[요약]\n')
    f.write(f"마감월(3·6·9·12) 배수 평균: {dl.multiple.mean():.3f}\n")
    f.write(f"비마감월 배수 평균: {pl.multiple.mean():.3f}\n")
    f.write(f"비마감월 최대: {pl.loc[plmax_i,'multiple']:.3f} ({pl.loc[plmax_i,'transition']})\n")
    f.write(f"12/11 배수: {out.loc[out.month==12,'multiple'].values[0]:.3f}\n")
    f.write(f"비마감월 중앙값: {pl.multiple.median():.3f}\n")
print('done -> data/results/H22_placebo_months.csv')
