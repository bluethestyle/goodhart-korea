"""H6 v3: 디커플링 신호 견고성 검증 — outcome 4개 교체.

교체 내용 (사용자 비판 반영):
  과학기술:    rd_total        → patent_apps_total      (특허 출원)
  문화관광:    tourists_sample → foreign_tourists_total  (방한 외래관광객)
  일반·지방행정: local_tax_per_capita → fiscal_indep_natl  (재정자립도 전국평균)
  통신:        ict_value_added → broadband_per_100      (100명당 초고속인터넷)

유지 (★★★ 적합도):
  사회복지 wealth_gini / 보건 life_expectancy / 산업·중기 industry_production_index
  교육 private_edu_hours / 국토 housing_supply / 농림 farm_income
  교통 traffic_deaths / 환경 ghg_total / 통일외교 oda_total / 공공질서 crime_occurrence
  국방 defense_op_margin

출력:
  data/figs/h6_v3/H6_robustness_panel_v3.png
  data/figs/h6_v3/H6_permutation_null_v3.png
  data/figs/h6_v3/H6_lag_lead_v3.png
  data/results/H6_fe_regression_v3.csv
  data/results/H6_permutation_pvals_v3.csv
  data/results/H6_lag_lead_corr_v3.csv
  data/results/H6_natural_vs_gaming_v3.csv
  data/results/H6_ministry_outcome_corr_v3.csv
  data/results/H6_before_after_comparison_v3.csv
"""
import os, sys, io, warnings
import numpy as np
import pandas as pd
import duckdb
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns
from scipy.stats import pearsonr

warnings.filterwarnings('ignore')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB   = os.path.join(ROOT, 'data', 'warehouse.duckdb')
H3_CSV = os.path.join(ROOT, 'data', 'results', 'H3_activity_embedding.csv')
OUT_DIR = os.path.join(ROOT, 'data', 'figs', 'h6_v3')
RES_DIR = os.path.join(ROOT, 'data', 'results')
os.makedirs(OUT_DIR, exist_ok=True)

# ── 한국어 폰트 ──
KFONT = None
for f in ['Malgun Gothic', 'Noto Sans CJK KR', 'AppleGothic']:
    if any(f in fn.name for fn in mpl.font_manager.fontManager.ttflist):
        mpl.rcParams['font.family'] = f
        KFONT = f
        break
mpl.rcParams['axes.unicode_minus'] = False
RNG = np.random.default_rng(42)
MAX_PX = 1800
DPI = 130

con = duckdb.connect(DB, read_only=True)
emb = pd.read_csv(H3_CSV)
print(f'활동 N = {len(emb)}')

# ── OUTCOME_MAP v3 (4개 교체) ──
OUTCOME_MAP = {
    '사회복지':               'wealth_gini',
    '보건':                   'life_expectancy',
    '과학기술':               'patent_apps_total',        # ← 교체: rd_total → patent_apps_total
    '산업·중소기업및에너지':   'industry_production_index',
    '문화및관광':             'foreign_tourists_total',   # ← 교체: tourists_sample → foreign_tourists_total
    '교육':                   'private_edu_hours',
    '국토및지역개발':         'housing_supply',
    '일반·지방행정':          'fiscal_indep_natl',        # ← 교체: local_tax_per_capita → fiscal_indep_natl
    '농림수산':               'farm_income',
    '교통및물류':             'traffic_deaths',
    '환경':                   'ghg_total',
    '통신':                   'broadband_per_100',        # ← 교체: ict_value_added → broadband_per_100
    '통일·외교':              'oda_total',
    '공공질서및안전':          'crime_occurrence',
    '국방':                   'defense_op_margin',
}

# 기존 v1 OUTCOME_MAP (비교용)
OUTCOME_MAP_V1 = {
    '사회복지':               'wealth_gini',
    '보건':                   'life_expectancy',
    '과학기술':               'rd_total',
    '산업·중소기업및에너지':   'industry_production_index',
    '문화및관광':             'tourists_sample',
    '교육':                   'private_edu_hours',
    '국토및지역개발':         'housing_supply',
    '일반·지방행정':          'local_tax_per_capita',
    '농림수산':               'farm_income',
    '교통및물류':             'traffic_deaths',
    '환경':                   'ghg_total',
    '통신':                   'ict_value_added',
    '통일·외교':              'oda_total',
    '공공질서및안전':          'crime_occurrence',
    '국방':                   'defense_op_margin',
}

# ── 분야×연도 wide 패널 ──
all_metrics = list(set(list(OUTCOME_MAP.values()) + list(OUTCOME_MAP_V1.values())))
all_metrics += ['amp_12m_norm', 'grdp_national']
metric_list = "', '".join(sorted(set(all_metrics)))

panel = con.execute(f"""
    SELECT fld_nm, year, metric_code, value
    FROM indicator_panel
    WHERE metric_code IN ('{metric_list}')
""").fetchdf()
wide = panel.pivot_table(index=['fld_nm','year'], columns='metric_code',
                         values='value').reset_index()
print(f'wide shape: {wide.shape}, 분야 수: {wide["fld_nm"].nunique()}')

years = sorted(wide['year'].dropna().unique().astype(int))
fld_amp = wide.pivot_table(index='year', columns='fld_nm', values='amp_12m_norm')

# ============================================================
# Step 6.1: 부처 단위 outcome 매핑
# ============================================================
print('\n' + '='*70)
print('Step 6.1: 부처 단위 outcome 매핑 (분야 가중) — v3 outcome')
print('='*70)
ofc_fld = pd.crosstab(emb['OFFC_NM'], emb['FLD_NM'], normalize='index')
ofc_size = emb.groupby('OFFC_NM').size()
ofc_fld  = ofc_fld[ofc_size >= 5]
ofc_size = ofc_size[ofc_size >= 5]

ofc_results = []
for ofc, w in ofc_fld.iterrows():
    if (w > 0).sum() < 2: continue
    amp_ts = (fld_amp.reindex(columns=w.index) * w).sum(axis=1, min_count=1)
    amp_ts = amp_ts.dropna()
    for fld, oc_metric in OUTCOME_MAP.items():
        if oc_metric not in wide.columns: continue
        if w.get(fld, 0) < 0.05: continue
        oc_ts  = wide[wide['fld_nm']==fld].set_index('year')[oc_metric].dropna()
        common = amp_ts.index.intersection(oc_ts.index)
        if len(common) < 4: continue
        d_amp = amp_ts.loc[common].diff().dropna()
        d_oc  = oc_ts.loc[common].diff().dropna()
        ci = d_amp.index.intersection(d_oc.index)
        if len(ci) < 3: continue
        r_lvl = float(amp_ts.loc[common].corr(oc_ts.loc[common]))
        r_dif = float(d_amp[ci].corr(d_oc[ci]))
        ofc_results.append({
            'OFFC_NM': ofc, 'fld_outcome': fld, 'metric': oc_metric,
            'fld_weight': float(w[fld]), 'n_year': len(common),
            'corr_levels': r_lvl, 'corr_diff': r_dif,
        })
ofc_corr = pd.DataFrame(ofc_results)
print(f'  부처×outcome pair: {len(ofc_corr)}')
if len(ofc_corr) > 0:
    print('  상위/하위 5 (corr_diff):')
    print(ofc_corr.sort_values('corr_diff').head(5).round(3).to_string(index=False))
    print('  ...')
    print(ofc_corr.sort_values('corr_diff').tail(5).round(3).to_string(index=False))
ofc_corr.to_csv(os.path.join(RES_DIR, 'H6_ministry_outcome_corr_v3.csv'),
                index=False, encoding='utf-8-sig')

expo_path = os.path.join(RES_DIR, 'H5_ministry_exposure.csv')
ofc_corr_w_expo = ofc_corr.copy()
if os.path.exists(expo_path):
    expo = pd.read_csv(expo_path).set_index(pd.read_csv(expo_path).columns[0])
    ofc_corr_w_expo = ofc_corr.merge(expo[['exposure_score']],
                                     left_on='OFFC_NM', right_index=True, how='left')

# ============================================================
# Step 6.2: 분야 패널 FE 회귀 (v3)
# ============================================================
print('\n' + '='*70)
print('Step 6.2: 분야 패널 FE 회귀 — v3 outcome')
print('='*70)

fe_rows = []
for fld, oc_m in OUTCOME_MAP.items():
    sub = wide[wide['fld_nm']==fld].sort_values('year').copy()
    if oc_m not in sub.columns:
        print(f'  [SKIP] {fld}: {oc_m} 없음')
        continue
    sub = sub[['year','amp_12m_norm', oc_m]].dropna()
    if len(sub) < 5:
        print(f'  [SKIP] {fld}: n={len(sub)} < 5')
        continue
    sub['d_amp'] = sub['amp_12m_norm'].diff()
    sub['d_oc']  = sub[oc_m].diff()
    sub = sub.dropna()
    sub['fld_nm'] = fld
    fe_rows.append(sub)

fe_df = pd.concat(fe_rows, ignore_index=True) if fe_rows else pd.DataFrame()
print(f'  pooled N = {len(fe_df)}')

def ols_with_dummies(df, y_col, x_col, fld_fe=True, year_fe=True):
    df = df.copy()
    X = df[[x_col]].copy()
    if fld_fe:
        for f in df['fld_nm'].unique()[1:]:
            X[f'fld_{f}'] = (df['fld_nm']==f).astype(float)
    if year_fe:
        for y in sorted(df['year'].unique())[1:]:
            X[f'yr_{y}'] = (df['year']==y).astype(float)
    X['const'] = 1.0
    y = df[y_col].values
    Xv = X.values
    beta, *_ = np.linalg.lstsq(Xv, y, rcond=None)
    yhat  = Xv @ beta
    resid = y - yhat
    df_resid = max(len(y) - Xv.shape[1], 1)
    sigma2 = (resid @ resid) / df_resid
    cov = sigma2 * np.linalg.pinv(Xv.T @ Xv)
    se   = np.sqrt(np.diag(cov))
    from scipy.stats import t as tdist
    tvals = beta / np.where(se > 0, se, np.nan)
    pvals = 2 * (1 - tdist.cdf(np.abs(tvals), df=df_resid))
    return pd.DataFrame({'var': X.columns, 'beta': beta, 'se': se,
                         't': tvals, 'p': pvals, 'n': len(y)})

fe_z = fe_df.copy()
for fld in fe_z['fld_nm'].unique():
    msk = fe_z['fld_nm'] == fld
    fe_z.loc[msk, 'd_amp_z'] = (
        (fe_z.loc[msk,'d_amp'] - fe_z.loc[msk,'d_amp'].mean()) /
        (fe_z.loc[msk,'d_amp'].std() + 1e-9))
    fe_z.loc[msk, 'd_oc_z'] = (
        (fe_z.loc[msk,'d_oc'] - fe_z.loc[msk,'d_oc'].mean()) /
        (fe_z.loc[msk,'d_oc'].std() + 1e-9))

fe_summary = pd.DataFrame()
if len(fe_z) >= 6:
    m1 = ols_with_dummies(fe_z, 'd_oc_z', 'd_amp_z', fld_fe=False, year_fe=False)
    m2 = ols_with_dummies(fe_z, 'd_oc_z', 'd_amp_z', fld_fe=True,  year_fe=False)
    m3 = ols_with_dummies(fe_z, 'd_oc_z', 'd_amp_z', fld_fe=True,  year_fe=True)
    print('\n  [Model 1] pooled OLS:')
    print('   ' + m1.head(2).round(4).to_string(index=False).replace('\n','\n   '))
    print('\n  [Model 2] +분야 FE:')
    print('   ' + m2[m2['var']=='d_amp_z'].round(4).to_string(index=False).replace('\n','\n   '))
    print('\n  [Model 3] +분야+연도 FE:')
    print('   ' + m3[m3['var']=='d_amp_z'].round(4).to_string(index=False).replace('\n','\n   '))
    fe_summary = pd.DataFrame([
        {'model': 'pooled',       **m1[m1['var']=='d_amp_z'].iloc[0].to_dict()},
        {'model': '+fld_FE',      **m2[m2['var']=='d_amp_z'].iloc[0].to_dict()},
        {'model': '+fld+year_FE', **m3[m3['var']=='d_amp_z'].iloc[0].to_dict()},
    ])
fe_summary.to_csv(os.path.join(RES_DIR, 'H6_fe_regression_v3.csv'),
                  index=False, encoding='utf-8-sig')

# ============================================================
# Step 6.3: Permutation test (v3)
# ============================================================
print('\n' + '='*70)
print('Step 6.3: Permutation test — v3 outcome (1000회)')
print('='*70)
N_PERM = 1000
perm_results = []
for fld, oc_m in OUTCOME_MAP.items():
    if oc_m not in wide.columns:
        print(f'  [SKIP] {fld}: {oc_m} 없음')
        continue
    amp_ts = wide[wide['fld_nm']==fld].set_index('year')['amp_12m_norm'].dropna()
    oc_ts  = wide[wide['fld_nm']==fld].set_index('year')[oc_m].dropna()
    common = amp_ts.index.intersection(oc_ts.index)
    if len(common) < 4:
        print(f'  [SKIP] {fld}: 공통연도 {len(common)} < 4')
        continue
    d_amp = amp_ts.loc[common].diff().dropna().values
    d_oc  = oc_ts.loc[common].diff().dropna().values
    if len(d_amp) != len(d_oc):
        continue
    obs = pearsonr(d_amp, d_oc)[0] if len(d_amp) > 1 else np.nan
    null = np.array([pearsonr(d_amp, RNG.permutation(d_oc))[0]
                     for _ in range(N_PERM)])
    p_two = float(((np.abs(null) >= np.abs(obs)).sum() + 1) / (N_PERM + 1))
    perm_results.append({
        'fld': fld, 'outcome': oc_m, 'n_diff': len(d_amp),
        'obs_corr_diff': obs,
        'null_mean': float(null.mean()),
        'null_std':  float(null.std()),
        'pval_2sided': p_two,
    })
perm_df = pd.DataFrame(perm_results).sort_values('pval_2sided')
print(perm_df.round(4).to_string(index=False))
perm_df.to_csv(os.path.join(RES_DIR, 'H6_permutation_pvals_v3.csv'),
               index=False, encoding='utf-8-sig')

# ============================================================
# Step 6.4: Lag / lead (v3)
# ============================================================
print('\n' + '='*70)
print('Step 6.4: Lag/lead 차분 상관 k=-2..+2 — v3')
print('='*70)
LAGS = [-2, -1, 0, 1, 2]
lag_results = []
for fld, oc_m in OUTCOME_MAP.items():
    if oc_m not in wide.columns: continue
    amp_ts = wide[wide['fld_nm']==fld].set_index('year')['amp_12m_norm'].dropna()
    oc_ts  = wide[wide['fld_nm']==fld].set_index('year')[oc_m].dropna()
    common = amp_ts.index.intersection(oc_ts.index)
    if len(common) < 5: continue
    a = amp_ts.loc[common].diff()
    o = oc_ts.loc[common].diff()
    for k in LAGS:
        a_s = a.shift(-k)
        df_lag = pd.concat([a_s.rename('amp'), o.rename('oc')], axis=1).dropna()
        if len(df_lag) < 3: continue
        c = pearsonr(df_lag['amp'], df_lag['oc'])[0]
        lag_results.append({'fld': fld, 'outcome': oc_m, 'lag': k,
                            'n': len(df_lag), 'corr_diff': c})
lag_df = pd.DataFrame(lag_results)
if len(lag_df) > 0:
    print(lag_df.pivot_table(index=['fld','outcome'], columns='lag',
                              values='corr_diff').round(3).to_string())
lag_df.to_csv(os.path.join(RES_DIR, 'H6_lag_lead_corr_v3.csv'),
              index=False, encoding='utf-8-sig')

# ============================================================
# Step 6.5: 자연 주기성 vs 게임화 (v3)
# ============================================================
print('\n' + '='*70)
print('Step 6.5: 자연 주기성 vs 게임화 (amp_cv)')
print('='*70)
nat_results = []
for fld in fld_amp.columns:
    s = fld_amp[fld].dropna()
    if len(s) < 4: continue
    cv = float(s.std() / (s.mean() + 1e-9))
    nat_results.append({
        'fld': fld, 'n_year': len(s),
        'amp_mean': float(s.mean()),
        'amp_std':  float(s.std()),
        'amp_cv':   cv,
        'amp_trend_slope': float(np.polyfit(range(len(s)), s.values, 1)[0]),
    })
nat_df = pd.DataFrame(nat_results).sort_values('amp_cv', ascending=False)
print(nat_df.round(3).to_string(index=False))
nat_df.to_csv(os.path.join(RES_DIR, 'H6_natural_vs_gaming_v3.csv'),
              index=False, encoding='utf-8-sig')

# ============================================================
# Step 6.6: 교체 전후 비교 (v1 → v3)
# ============================================================
print('\n' + '='*70)
print('Step 6.6: 교체 전후 permutation p값·상관 비교')
print('='*70)
# v1 perm 재계산 (교체된 4개 분야만)
REPLACED = {
    '과학기술':     ('rd_total',           'patent_apps_total'),
    '문화및관광':   ('tourists_sample',     'foreign_tourists_total'),
    '일반·지방행정': ('local_tax_per_capita', 'fiscal_indep_natl'),
    '통신':         ('ict_value_added',     'broadband_per_100'),
}

compare_rows = []
for fld, (old_m, new_m) in REPLACED.items():
    for label, metric in [('v1_old', old_m), ('v3_new', new_m)]:
        if metric not in wide.columns:
            compare_rows.append({'fld': fld, 'version': label, 'outcome': metric,
                                 'obs_corr': np.nan, 'pval': np.nan, 'n': 0})
            continue
        amp_ts = wide[wide['fld_nm']==fld].set_index('year')['amp_12m_norm'].dropna()
        oc_ts  = wide[wide['fld_nm']==fld].set_index('year')[metric].dropna()
        common = amp_ts.index.intersection(oc_ts.index)
        if len(common) < 4:
            compare_rows.append({'fld': fld, 'version': label, 'outcome': metric,
                                 'obs_corr': np.nan, 'pval': np.nan, 'n': len(common)})
            continue
        d_amp = amp_ts.loc[common].diff().dropna().values
        d_oc  = oc_ts.loc[common].diff().dropna().values
        if len(d_amp) < 2 or len(d_amp) != len(d_oc):
            compare_rows.append({'fld': fld, 'version': label, 'outcome': metric,
                                 'obs_corr': np.nan, 'pval': np.nan, 'n': len(d_amp)})
            continue
        obs  = pearsonr(d_amp, d_oc)[0]
        null = np.array([pearsonr(d_amp, RNG.permutation(d_oc))[0]
                         for _ in range(N_PERM)])
        p_two = float(((np.abs(null) >= np.abs(obs)).sum() + 1) / (N_PERM + 1))
        compare_rows.append({'fld': fld, 'version': label, 'outcome': metric,
                              'obs_corr': round(obs, 4), 'pval': round(p_two, 4),
                              'n': len(d_amp)})

compare_df = pd.DataFrame(compare_rows)
print(compare_df.to_string(index=False))
compare_df.to_csv(os.path.join(RES_DIR, 'H6_before_after_comparison_v3.csv'),
                  index=False, encoding='utf-8-sig')

# ============================================================
# Figure A: 견고성 패널 (2×2)
# ============================================================
fig_w = min(MAX_PX / DPI, 15)
fig_h = min(MAX_PX / DPI * 0.7, 11)
fig, axes = plt.subplots(2, 2, figsize=(fig_w, fig_h))

# A1: FE 회귀 결과
ax = axes[0, 0]
if len(fe_summary) > 0:
    xx = np.arange(len(fe_summary))
    ax.bar(xx, fe_summary['beta'], yerr=fe_summary['se']*1.96,
           color='#5475a8', alpha=0.85, capsize=4)
    ax.axhline(0, color='#888', lw=0.8)
    ax.set_xticks(xx); ax.set_xticklabels(fe_summary['model'], rotation=10)
    ax.set_ylabel('β (Δoutcome_z ~ Δamp_z)')
    ax.set_title(f'FE 회귀 v3 — Δoutcome_z ~ Δamp_z\n(N={int(fe_summary.iloc[0]["n"])}, ±95% CI)')
    ax.grid(alpha=0.3)
    for i, p in enumerate(fe_summary['p']):
        ax.annotate(f'p={p:.3f}', (xx[i], fe_summary['beta'].iloc[i]),
                    xytext=(0, 8), textcoords='offset points',
                    ha='center', fontsize=9)
else:
    ax.text(0.5, 0.5, 'FE 데이터 부족', ha='center', va='center', transform=ax.transAxes)
    ax.set_title('FE 회귀 v3')

# A2: 자연 vs 게임화 cv
ax = axes[0, 1]
nat_sorted = nat_df.sort_values('amp_cv', ascending=True)
colors = ['#c87f5a' if cv > nat_df['amp_cv'].median() else '#5a8ac8'
          for cv in nat_sorted['amp_cv']]
ax.barh(range(len(nat_sorted)), nat_sorted['amp_cv'], color=colors)
ax.set_yticks(range(len(nat_sorted)))
ax.set_yticklabels(nat_sorted['fld'], fontsize=9)
ax.set_xlabel('amp_12m 시간적 cv')
ax.set_title('분야별 amp_12m 변동성\n(주황=중위초과, 파랑=중위이하)')
ax.grid(alpha=0.3, axis='x')

# A3: 부처 노출 vs outcome 차분 상관
ax = axes[1, 0]
if len(ofc_corr_w_expo) > 0 and 'exposure_score' in ofc_corr_w_expo.columns:
    sub = ofc_corr_w_expo.dropna(subset=['exposure_score'])
    if len(sub) > 0:
        sc = ax.scatter(sub['exposure_score'], sub['corr_diff'],
                        s=40, c=sub['fld_weight']*250, alpha=0.6, cmap='Reds')
        ax.axhline(0, color='#888', lw=0.6)
        ax.set_xlabel('굿하트 노출 점수 (H5)')
        ax.set_ylabel('amp ~ outcome 차분 상관 (부처)')
        ax.set_title(f'부처 노출 × outcome 디커플링 v3\n(N={len(sub)})')
        ax.grid(alpha=0.3)
    else:
        ax.text(0.5, 0.5, '매칭 데이터 없음', ha='center', va='center', transform=ax.transAxes)
        ax.set_title('부처 노출 × outcome v3')
else:
    ax.text(0.5, 0.5, 'H5 노출점수 없음', ha='center', va='center', transform=ax.transAxes)
    ax.set_title('부처 노출 × outcome v3')

# A4: Permutation null vs obs (정렬된 막대)
ax = axes[1, 1]
if len(perm_df) > 0:
    perm_sorted = perm_df.sort_values('obs_corr_diff')
    yy = np.arange(len(perm_sorted))
    colors_p = ['#a85454' if v < 0 else '#5475a8' for v in perm_sorted['obs_corr_diff']]
    ax.barh(yy, perm_sorted['obs_corr_diff'], color=colors_p, alpha=0.85, label='관측 corr_diff')
    ax.errorbar(perm_sorted['null_mean'], yy, xerr=perm_sorted['null_std']*2,
                fmt='o', color='#333', ms=3, lw=1, label='null ±2σ')
    labels = [f'{r["fld"]}\n({r["outcome"]})' for _, r in perm_sorted.iterrows()]
    ax.set_yticks(yy); ax.set_yticklabels(labels, fontsize=7)
    ax.axvline(0, color='#888', lw=0.6)
    for i, (_, row) in enumerate(perm_sorted.iterrows()):
        sig = '★' if row['pval_2sided'] < 0.05 else ''
        ax.annotate(f'p={row["pval_2sided"]:.3f}{sig}',
                    (row['obs_corr_diff'], yy[i]),
                    xytext=(5, 0), textcoords='offset points',
                    va='center', fontsize=7)
    ax.set_xlabel('Δamp ~ Δoutcome 상관')
    ax.set_title(f'Permutation test v3 ({N_PERM}회)\n★=p<0.05')
    ax.legend(fontsize=7)
    ax.grid(alpha=0.3, axis='x')

plt.suptitle('H6 견고성 검증 v3 — outcome 4개 교체 후', fontsize=13, fontweight='bold', y=1.01)
plt.tight_layout()
out_a = os.path.join(OUT_DIR, 'H6_robustness_panel_v3.png')
fig.savefig(out_a, dpi=DPI, bbox_inches='tight')
plt.close()
print(f'\n저장: {out_a}')

# ============================================================
# Figure B: Permutation null 분포 상세 (분야별)
# ============================================================
if len(perm_df) > 0:
    n_fld = len(perm_df)
    cols_b = min(n_fld, 5)
    rows_b = (n_fld + cols_b - 1) // cols_b
    px_w = min(MAX_PX, cols_b * 300)
    px_h = min(MAX_PX, rows_b * 260)
    fig, axes_b = plt.subplots(rows_b, cols_b,
                                figsize=(px_w/DPI, px_h/DPI),
                                squeeze=False)
    flat_axes = axes_b.flatten()
    for i, (_, row) in enumerate(perm_df.iterrows()):
        ax = flat_axes[i]
        amp_ts = wide[wide['fld_nm']==row['fld']].set_index('year')['amp_12m_norm'].dropna()
        if row['outcome'] not in wide.columns:
            ax.set_visible(False); continue
        oc_ts  = wide[wide['fld_nm']==row['fld']].set_index('year')[row['outcome']].dropna()
        common = amp_ts.index.intersection(oc_ts.index)
        if len(common) < 4:
            ax.set_visible(False); continue
        d_amp = amp_ts.loc[common].diff().dropna().values
        d_oc  = oc_ts.loc[common].diff().dropna().values
        if len(d_amp) < 2 or len(d_amp) != len(d_oc):
            ax.set_visible(False); continue
        null = np.array([pearsonr(d_amp, RNG.permutation(d_oc))[0]
                         for _ in range(N_PERM)])
        ax.hist(null, bins=30, color='#cccccc', edgecolor='#888888')
        ax.axvline(row['obs_corr_diff'], color='#a31010', lw=2,
                   label=f'관측: {row["obs_corr_diff"]:.2f}')
        sig = '★' if row['pval_2sided'] < 0.05 else ''
        ax.set_title(f'{row["fld"]}\n{row["outcome"]}\np={row["pval_2sided"]:.3f}{sig}',
                     fontsize=8)
        ax.set_xlabel('null corr_diff', fontsize=7)
        ax.legend(fontsize=6)
        ax.grid(alpha=0.3)
    for j in range(i+1, len(flat_axes)):
        flat_axes[j].set_visible(False)
    flat_axes[0].set_ylabel('빈도')
    plt.suptitle(f'H6 v3 — Permutation null 분포 (각 분야)', fontsize=11, fontweight='bold')
    plt.tight_layout()
    out_b = os.path.join(OUT_DIR, 'H6_permutation_null_v3.png')
    fig.savefig(out_b, dpi=DPI, bbox_inches='tight')
    plt.close()
    print(f'저장: {out_b}')

# ============================================================
# Figure C: lag/lead heatmap + 교체 전후 비교
# ============================================================
if len(lag_df) > 0:
    pv = lag_df.pivot_table(index=['fld','outcome'], columns='lag', values='corr_diff')
    fig_h_c = min(MAX_PX / DPI, max(5, 0.55 * len(pv) + 2))
    fig, axes_c = plt.subplots(1, 2, figsize=(min(MAX_PX/DPI, 16), fig_h_c),
                                gridspec_kw={'width_ratios': [2, 1]})

    # C1: lag/lead heatmap
    ax = axes_c[0]
    sns.heatmap(pv, annot=True, fmt='.2f', cmap='RdBu_r', center=0, ax=ax,
                cbar_kws={'label': 'corr_diff'}, linewidths=0.5)
    ax.set_title('Lag/Lead 차분 상관 v3\n(k=-2..+2, k>0: outcome→amp 가능성)', fontsize=10)
    ax.set_ylabel('')
    ax.tick_params(axis='y', labelsize=8)

    # C2: 교체 전후 비교 (교체된 4개 분야)
    ax = axes_c[1]
    if len(compare_df) > 0:
        comp_pivot = compare_df.pivot_table(index='fld', columns='version',
                                            values='obs_corr', aggfunc='first')
        if 'v1_old' in comp_pivot.columns and 'v3_new' in comp_pivot.columns:
            yy_c = np.arange(len(comp_pivot))
            bw   = 0.35
            ax.barh(yy_c - bw/2, comp_pivot['v1_old'].fillna(0),
                    height=bw, color='#888888', alpha=0.8, label='v1 (교체 전)')
            ax.barh(yy_c + bw/2, comp_pivot['v3_new'].fillna(0),
                    height=bw, color='#5475a8', alpha=0.9, label='v3 (교체 후)')
            ax.set_yticks(yy_c)
            ax.set_yticklabels(comp_pivot.index, fontsize=9)
            ax.axvline(0, color='#555', lw=0.7)
            ax.set_xlabel('Δamp ~ Δoutcome 상관')
            ax.set_title('교체 전후 상관 변화\n(교체 4개 분야)', fontsize=9)
            ax.legend(fontsize=8)
            ax.grid(alpha=0.3, axis='x')
            # p값 표기
            for _, row in compare_df.iterrows():
                if not np.isnan(row['pval']):
                    sig = '★' if row['pval'] < 0.05 else ''
                    idx_y = list(comp_pivot.index).index(row['fld'])
                    dy = bw/2 if row['version'] == 'v3_new' else -bw/2
                    ax.annotate(f'{sig}p={row["pval"]:.2f}',
                                (row['obs_corr'] if not np.isnan(row['obs_corr']) else 0,
                                 idx_y + dy),
                                xytext=(4, 0), textcoords='offset points',
                                va='center', fontsize=6)
        else:
            ax.text(0.5, 0.5, '비교 데이터 없음', ha='center', va='center',
                    transform=ax.transAxes)
    else:
        ax.text(0.5, 0.5, '비교 없음', ha='center', va='center', transform=ax.transAxes)
    ax.set_title('교체 전후 상관 변화\n(교체 4개 분야)', fontsize=9)

    plt.suptitle('H6 v3 — Lag/Lead & 교체 전후 비교', fontsize=11, fontweight='bold')
    plt.tight_layout()
    out_c = os.path.join(OUT_DIR, 'H6_lag_lead_v3.png')
    fig.savefig(out_c, dpi=DPI, bbox_inches='tight')
    plt.close()
    print(f'저장: {out_c}')

# ============================================================
# 최종 요약 출력
# ============================================================
print('\n' + '='*70)
print('최종 요약 (교체 전후 permutation p값 비교)')
print('='*70)
print('\n[교체된 4개 분야 before/after]')
print(compare_df.to_string(index=False))

print('\n[v3 전체 분야 permutation 결과]')
print(perm_df[['fld','outcome','obs_corr_diff','pval_2sided']].round(4).to_string(index=False))

sig_flds = perm_df[perm_df['pval_2sided'] < 0.05]
print(f'\n  유의(p<0.05) 분야 수: {len(sig_flds)} / {len(perm_df)}')
if len(sig_flds) > 0:
    print('  ' + ', '.join(sig_flds['fld'].tolist()))

if len(fe_summary) > 0:
    fe_m3 = fe_summary[fe_summary['model']=='+fld+year_FE']
    if len(fe_m3) > 0:
        print(f'\n  FE 회귀 (분야+연도 FE): β={fe_m3.iloc[0]["beta"]:.4f}, '
              f'p={fe_m3.iloc[0]["p"]:.4f}')

print('\n출력 파일:')
for f in sorted(os.listdir(OUT_DIR)):
    print(f'  data/figs/h6_v3/{f}')
for f in sorted(os.listdir(RES_DIR)):
    if 'v3' in f and f.startswith('H6'):
        print(f'  data/results/{f}')

con.close()
print('\n완료 (H6 v3).')
