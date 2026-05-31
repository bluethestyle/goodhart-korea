"""archetype × 집행액 비중 + cluster별 대표 사업 추출. Slide 14/15/20 KPI·예시 보강."""
import pandas as pd
import sys
sys.stdout.reconfigure(encoding='utf-8')

df = pd.read_csv('data/results/H3_activity_embedding_11y.csv')
print('전체 활동 수:', len(df))
print()
cnt = df['cluster'].value_counts().sort_index()
print('=== cluster별 활동 수 ===')
for c, n in cnt.items():
    print(f'  C{c}: {n} ({n/len(df)*100:.1f}%)')
print()

agg = df.groupby('cluster')['total_budget'].agg(['sum', 'count', 'median'])
total = df['total_budget'].sum()
print('=== cluster별 집행액 비중 ===')
for c, row in agg.iterrows():
    n_v = int(row['count'])
    s_t = row['sum'] / 1e12
    pct = row['sum'] / total * 100
    med_eok = row['median'] / 1e8
    print(f'  C{c}: n={n_v}, 총집행 {s_t:.1f}조원 ({pct:.1f}%), 활동당 중앙값 {med_eok:.1f}억원')
print()

c1c2_n = cnt[1] + cnt[2]
c1c2_sum = agg.loc[1, 'sum'] + agg.loc[2, 'sum']
print('=== 분석 대상 C1 + C2 ===')
print(f'  활동 수: {c1c2_n}/{len(df)} = {c1c2_n/len(df)*100:.1f}%')
print(f'  집행액: {c1c2_sum/1e12:.1f}조원 / {total/1e12:.1f}조원 = {c1c2_sum/total*100:.1f}%')
print()

CLUSTER_NAME = {0: 'C0 인건비형', 1: 'C1 자산취득형', 2: 'C2 출연금형', 3: 'C3 정상사업'}
for c in [0, 1, 2, 3]:
    sub = df[df['cluster'] == c].nlargest(5, 'total_budget')
    print(f'=== {CLUSTER_NAME[c]} 대표 사업 top 5 (집행액 기준) ===')
    for _, r in sub.iterrows():
        nm = str(r['ACTV_NM'])[:30]
        off = str(r['OFFC_NM'])[:12]
        fld = str(r['FLD_NM'])[:10]
        print(f'  {nm:<30} | {off:<12} | {fld:<10} | dec_pct={r["dec_pct"]:+.2f} | {r["total_budget"]/1e12:.2f}조원')
    print()
