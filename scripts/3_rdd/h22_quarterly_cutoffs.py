"""H22 quarterly cutoff RDD — 3·6·9·12월 cutoff 각각 동일 spec으로 추정.

기존 h22_rdd_yearend.py의 12월 cutoff spec을 3개 분기말 cutoff에 동일 적용:
  log(daily) ~ T + C(year), bw=1 (cutoff 직전월 + cutoff월), cluster SE by ACTV_CD.

목적: Slide 22 "분기말 cutoff별 RDD 점프 — 12월이 최대" 차트의 4 막대 수치를
재현 가능한 결과로 정착. 결과 → data/results/H22_quarterly_cutoffs.csv.
"""
import sys, os, warnings
sys.stdout.reconfigure(encoding='utf-8')
import duckdb
import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
warnings.filterwarnings('ignore')

DB   = 'data/warehouse.duckdb'
RDIR = 'data/results'
DAYS = {1:31, 2:28, 3:31, 4:30, 5:31, 6:30,
        7:31, 8:31, 9:30, 10:31, 11:30, 12:31}

# 4 cutoff 정의: (cutoff_month, pre_month, label)
CUTOFFS = [
    (3,  2,  '3월/2월'),
    (6,  5,  '6월/5월'),
    (9,  8,  '9월/8월'),
    (12, 11, '12월/11월'),
]

con = duckdb.connect(DB)

# 4 cutoff에 필요한 모든 월 (2·3·5·6·8·9·11·12) 한 번에 fetch
needed_months = sorted({m for c, p, _ in CUTOFFS for m in (c, p)})
months_sql = ','.join(str(m) for m in needed_months)

df = con.execute(f"""
    SELECT
        FSCL_YY  AS year,
        EXE_M    AS month,
        ACTV_CD,
        ACTV_NM,
        FLD_NM,
        OFFC_NM,
        SUM(EP_AMT) AS ep_amt
    FROM monthly_exec
    WHERE FSCL_YY BETWEEN 2015 AND 2025
      AND EXE_M   IN ({months_sql})
      AND EP_AMT  > 0
    GROUP BY FSCL_YY, EXE_M, ACTV_CD, ACTV_NM, FLD_NM, OFFC_NM
""").df()

df['days']      = df['month'].map(DAYS)
df['daily_ep']  = df['ep_amt'] / df['days']
df['log_daily'] = np.log(df['daily_ep'])
print(f'raw rows: {len(df):,}  |  활동수: {df["ACTV_CD"].nunique():,}')

# H3 cluster merge (활동명 기준)
h3 = pd.read_csv('data/results/H3_activity_embedding_11y.csv',
                 usecols=['ACTV_NM', 'cluster']).drop_duplicates('ACTV_NM')
df = df.merge(h3, on='ACTV_NM', how='left')
CLUSTER_LABEL = {0: 'C0 인건비형', 1: 'C1 자산취득형',
                 2: 'C2 출연금형', 3: 'C3 정상사업'}
print(f'H3 cluster 매칭률: {df["cluster"].notna().mean()*100:.1f}% '
      f'({df["cluster"].notna().sum():,} / {len(df):,})')


def run_cutoff_rdd(data, cutoff_month, pre_month, label):
    """동일 spec으로 cutoff RDD 추정.

    formula: log_daily ~ T + C(year)
    sub = month in {pre_month, cutoff_month}
    T = (month == cutoff_month).astype(int)
    cluster SE by ACTV_CD
    """
    sub = data[data['month'].isin([pre_month, cutoff_month])].copy()
    sub['T'] = (sub['month'] == cutoff_month).astype(int)
    sub = sub.dropna(subset=['log_daily'])
    if len(sub) < 30 or sub['ACTV_CD'].nunique() < 3:
        return None
    mod = smf.ols('log_daily ~ T + C(year)', data=sub).fit(
        cov_type='cluster',
        cov_kwds={'groups': sub['ACTV_CD']}
    )
    return dict(
        cutoff=label,
        cutoff_month=cutoff_month,
        pre_month=pre_month,
        beta=mod.params['T'],
        se=mod.bse['T'],
        pval=mod.pvalues['T'],
        r2=mod.rsquared,
        n_obs=int(mod.nobs),
        n_clusters=sub['ACTV_CD'].nunique(),
        mult=float(np.exp(mod.params['T'])),
    )


results = []
print(f'\n=== Quarterly cutoff RDD (bw=1, log_daily ~ T + C(year), cluster SE by ACTV_CD) ===')
print(f'{"group":>15} {"cutoff":>10} | {"β":>7} {"SE":>6} {"p":>10} {"×배":>6} | {"n_obs":>7} {"n_act":>6}  sig')
print('-' * 90)

# 전체 + 각 H3 cluster (0~3)
GROUPS = [('전체', df)]
for cl_id in sorted(df['cluster'].dropna().unique()):
    cl_id = int(cl_id)
    sub = df[df['cluster'] == cl_id]
    GROUPS.append((CLUSTER_LABEL[cl_id], sub))

for group_label, group_df in GROUPS:
    for cutoff_month, pre_month, c_label in CUTOFFS:
        r = run_cutoff_rdd(group_df, cutoff_month, pre_month, c_label)
        if r is None:
            print(f'{group_label:>15} {c_label:>10}: SKIP')
            continue
        r['group'] = group_label
        results.append(r)
        sig = ('***' if r['pval']<0.001 else '**' if r['pval']<0.01
               else '*' if r['pval']<0.05 else 'ns')
        print(f'{group_label:>15} {c_label:>10} | {r["beta"]:7.4f} {r["se"]:6.4f} '
              f'{r["pval"]:10.2e} {r["mult"]:6.3f} | {r["n_obs"]:7,} '
              f'{r["n_clusters"]:6,}  {sig}')

# CSV 저장 — group 컬럼 포함 (전체 + 4 archetype × 4 cutoff = 20행)
os.makedirs(RDIR, exist_ok=True)
out = pd.DataFrame(results)
# 컬럼 순서 정리
out = out[['group', 'cutoff', 'cutoff_month', 'pre_month',
           'beta', 'se', 'pval', 'r2', 'n_obs', 'n_clusters', 'mult']]
out_path = f'{RDIR}/H22_quarterly_cutoffs.csv'
out.to_csv(out_path, index=False, encoding='utf-8-sig')
print(f'\n저장: {out_path} (총 {len(out)}행)')

# Sanity check 1: 전체 12월 cutoff vs H22_rdd_estimates.csv
try:
    ref = pd.read_csv(f'{RDIR}/H22_rdd_estimates.csv')
    ref_bw1 = ref[(ref['label']=='전체') & (ref['bw']==1)].iloc[0]
    my_dec = next(r for r in results
                  if r['cutoff_month']==12 and r['group']=='전체')
    print(f'\n=== sanity check 1: 전체 12월 cutoff ===')
    print(f'  H22_rdd_estimates.csv (전체 bw=1): β={ref_bw1["beta"]:.4f}, '
          f'×{ref_bw1["mult"]:.3f}, n={ref_bw1["n"]:,}')
    print(f'  본 (전체 12월):                     β={my_dec["beta"]:.4f}, '
          f'×{my_dec["mult"]:.3f}, n={my_dec["n_obs"]:,}')
    diff = abs(my_dec['beta'] - ref_bw1['beta'])
    print(f'  β 차이: {diff:.6f} ({"정합 ✓" if diff < 1e-4 else "불일치 ⚠️"})')
except Exception as e:
    print(f'sanity check 1 skip: {e}')

# Sanity check 2: archetype별 12월 cutoff vs H22_field_rdd.csv
try:
    ref2 = pd.read_csv(f'{RDIR}/H22_field_rdd.csv')
    print(f'\n=== sanity check 2: archetype별 12월 cutoff ===')
    print(f'{"label":>15} | {"기존 β":>8} {"기존 ×":>6} | {"본 β":>8} {"본 ×":>6} | match')
    for cl_label_full in ['C0 인건비형', 'C1 자산취득형', 'C2 출연금형', 'C3 정상사업']:
        # ref2의 label은 '인건비형'/'자산취득형'/'출연금형'/'정상사업' 형태
        ref_label = cl_label_full.split(' ', 1)[1]
        ref_row = ref2[ref2['label']==ref_label]
        my_row = next((r for r in results
                       if r['cutoff_month']==12 and r['group']==cl_label_full), None)
        if ref_row.empty or my_row is None:
            print(f'{cl_label_full:>15} | (skip)')
            continue
        ref_b = ref_row.iloc[0]['beta']
        ref_m = ref_row.iloc[0]['mult']
        diff = abs(my_row['beta'] - ref_b)
        match = '✓' if diff < 1e-4 else f'⚠️ Δβ={diff:.4f}'
        print(f'{cl_label_full:>15} | {ref_b:8.4f} {ref_m:6.3f} | '
              f'{my_row["beta"]:8.4f} {my_row["mult"]:6.3f} | {match}')
except Exception as e:
    print(f'sanity check 2 skip: {e}')
