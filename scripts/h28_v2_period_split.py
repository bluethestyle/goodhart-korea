"""H28 v2: Period-split analysis to test H6 (+554%) monotonicity vs. pandemic shock.

Splits 2015-2025 into:
  Pre-COVID:   2015-2018 (4 years)
  COVID:       2019-2021 (3 years)
  Post-COVID:  2022-2025 (4 years)

Outputs:
  data/results/H28_v2_period_split.csv
  data/results/H28_v2_transitions.csv
"""

import os
import sys
try:
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
except AttributeError:
    pass
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Absolute fallback: if __file__ resolves badly (e.g., run via python -c), use hard path
if not os.path.isdir(os.path.join(ROOT, 'data')):
    ROOT = 'D:/workspace/재정자료분석'
RES  = os.path.join(ROOT, 'data', 'results')

print('=' * 70)
print('H28 v2: Period-split — Monotonic vs. COVID-shock test')
print('=' * 70)

# ----------------------------------------------------------------
# Load existing 12m evolution CSV
# ----------------------------------------------------------------
src = os.path.join(RES, 'H28_wavelet_12m_evolution.csv')
df = pd.read_csv(src)
print(f'Loaded: {src}  ({len(df)} rows)')
print(df.head())

# Period definition
PERIODS = {
    'pre_covid':  (2015, 2018),
    'covid':      (2019, 2021),
    'post_covid': (2022, 2025),
}

def assign_period(year):
    for name, (lo, hi) in PERIODS.items():
        if lo <= year <= hi:
            return name
    return None

df['period'] = df['year'].apply(assign_period)
df = df.dropna(subset=['period'])

# ----------------------------------------------------------------
# Per archetype × period: mean power + linear slope
# ----------------------------------------------------------------
archetypes = df['archetype'].unique()
split_records = []

for arch in sorted(archetypes):
    sub = df[df['archetype'] == arch].copy()
    for period_name, (lo, hi) in PERIODS.items():
        seg = sub[(sub['year'] >= lo) & (sub['year'] <= hi)].sort_values('year')
        if len(seg) < 2:
            slope = np.nan
        else:
            slope, _ = np.polyfit(seg['year'], seg['power_12m'], 1)
        split_records.append({
            'archetype':     arch,
            'period':        period_name,
            'year_range':    f'{lo}-{hi}',
            'mean_power':    seg['power_12m'].mean(),
            'slope_per_year': slope,
            'n_years':       len(seg),
        })

split_df = pd.DataFrame(split_records)
split_out = os.path.join(RES, 'H28_v2_period_split.csv')
split_df.to_csv(split_out, index=False, float_format='%.6f')
print(f'\nSaved: {split_out}')

# ----------------------------------------------------------------
# Period transitions
# ----------------------------------------------------------------
trans_records = []

for arch in sorted(archetypes):
    sub = split_df[split_df['archetype'] == arch].copy()
    sub = sub.set_index('period')

    def safe_pct(a, b):
        return (b / a - 1) * 100 if a and not np.isnan(a) and a != 0 else np.nan

    # Pre → COVID
    pre_mean   = sub.loc['pre_covid',  'mean_power']
    cov_mean   = sub.loc['covid',      'mean_power']
    post_mean  = sub.loc['post_covid', 'mean_power']
    pre_slope  = sub.loc['pre_covid',  'slope_per_year']
    cov_slope  = sub.loc['covid',      'slope_per_year']
    post_slope = sub.loc['post_covid', 'slope_per_year']

    trans_records.append({
        'archetype':    arch,
        'transition':   'pre_to_covid',
        'from_mean':    pre_mean,
        'to_mean':      cov_mean,
        'pct_change':   safe_pct(pre_mean, cov_mean),
        'slope_change': cov_slope - pre_slope,
    })
    trans_records.append({
        'archetype':    arch,
        'transition':   'covid_to_post',
        'from_mean':    cov_mean,
        'to_mean':      post_mean,
        'pct_change':   safe_pct(cov_mean, post_mean),
        'slope_change': post_slope - cov_slope,
    })

trans_df = pd.DataFrame(trans_records)
trans_out = os.path.join(RES, 'H28_v2_transitions.csv')
trans_df.to_csv(trans_out, index=False, float_format='%.6f')
print(f'Saved: {trans_out}')

# ----------------------------------------------------------------
# Console summary
# ----------------------------------------------------------------
print('\n' + '=' * 70)
print('PERIOD-SPLIT RESULTS')
print('=' * 70)

ARCH_LABEL = {
    'C0_personnel':    '인건비형',
    'C1_direct_invest':'자산취득형',
    'C2_chooyeon':     '출연금형',
    'C3_normal':       '정상사업',
}

for arch in sorted(archetypes):
    label = ARCH_LABEL.get(arch, arch)
    sub   = split_df[split_df['archetype'] == arch].set_index('period')
    print(f'\n  [{arch}] {label}')
    for p in ['pre_covid', 'covid', 'post_covid']:
        row = sub.loc[p]
        print(f'    {p:15s}  mean={row.mean_power:.4f}  slope={row.slope_per_year:+.5f}/yr  n={int(row.n_years)}')

print('\n' + '=' * 70)
print('TRANSITION SUMMARY')
print('=' * 70)

chooyeon_trans = trans_df[trans_df['archetype'] == 'C2_chooyeon']
print('\n  C2_chooyeon (출연금형) — KEY archetype for H6:')
for _, row in chooyeon_trans.iterrows():
    print(f'    {row.transition:20s}  pct_change={row.pct_change:+.1f}%  slope_change={row.slope_change:+.5f}')

# ----------------------------------------------------------------
# Scenario verdict for C2_chooyeon
# ----------------------------------------------------------------
print('\n' + '=' * 70)
print('SCENARIO VERDICT: C2_chooyeon (출연금형)')
print('=' * 70)

c2 = split_df[split_df['archetype'] == 'C2_chooyeon'].set_index('period')
pre_m  = c2.loc['pre_covid',  'mean_power']
cov_m  = c2.loc['covid',      'mean_power']
post_m = c2.loc['post_covid', 'mean_power']
pre_s  = c2.loc['pre_covid',  'slope_per_year']
cov_s  = c2.loc['covid',      'slope_per_year']
post_s = c2.loc['post_covid', 'slope_per_year']

print(f'\n  Pre-COVID mean  : {pre_m:.4f}  (slope {pre_s:+.5f}/yr)')
print(f'  COVID mean      : {cov_m:.4f}  (slope {cov_s:+.5f}/yr)')
print(f'  Post-COVID mean : {post_m:.4f}  (slope {post_s:+.5f}/yr)')

pct_pre_cov  = (cov_m  / pre_m  - 1) * 100
pct_cov_post = (post_m / cov_m  - 1) * 100
pct_overall  = (post_m / pre_m  - 1) * 100

print(f'\n  Pre→COVID:       {pct_pre_cov:+.1f}%')
print(f'  COVID→Post:      {pct_cov_post:+.1f}%')
print(f'  Pre→Post (total):{pct_overall:+.1f}%')

# Decision logic
all_slopes_positive = pre_s > 0 and cov_s > 0 and post_s > 0
post_exceeds_covid  = post_m > cov_m
pre_to_cov_large    = pct_pre_cov > 50
cov_to_post_large   = abs(pct_cov_post) > 30

print('\n  Diagnostic flags:')
print(f'    All periods have positive slope : {all_slopes_positive}')
print(f'    Post-COVID mean > COVID mean    : {post_exceeds_covid}')
print(f'    Pre→COVID jump > 50%            : {pre_to_cov_large}')
print(f'    COVID→Post |change| > 30%       : {cov_to_post_large}')

print('\n  VERDICT:')
if all_slopes_positive and post_exceeds_covid:
    verdict = '(a) MONOTONIC — all three periods show positive slope AND post-COVID > COVID'
    interp  = ('출연금형의 12m 사이클 진폭은 코로나 이전·중·이후 모두에서 양의 기울기를 보이며, '
               '팬데믹 이후에도 오히려 더 강해졌다. 이는 일시적 충격이 아닌 '
               'Performative Prediction 하의 지속적 학습 적응(learned adaptation)을 지지한다.')
elif pre_to_cov_large and not post_exceeds_covid:
    verdict = '(b) COVID SHOCK then plateau — large jump in COVID, no further rise post-COVID'
    interp  = ('코로나 시기에 급증 후 정체 패턴으로, 팬데믹 재정충격이 주된 원인일 가능성이 높다. '
               'Performative Prediction 해석에 주의가 필요하다.')
elif not pre_to_cov_large and post_exceeds_covid:
    verdict = '(c) POST-COVID SURGE — recent regulatory/political driver'
    interp  = ('코로나 시기보다 이후에 급증하여 최근 제도·정치적 요인이 주 원인일 수 있다.')
else:
    verdict = 'MIXED — no single scenario dominates; inspect plot.'
    interp  = '패턴이 복합적이므로 시각적 검토가 필요하다.'

print(f'\n  {verdict}')
print(f'\n  Interpretation:\n    {interp}')

print('\n완료 (H28 v2 period-split).')
print('출력:')
print(f'  {split_out}')
print(f'  {trans_out}')
