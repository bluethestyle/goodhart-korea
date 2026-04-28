"""H6: 디커플링 신호의 견고성 검증.

H4의 "출연금형 부호 반전(wealth_gini +0.26)" 신호가 진짜 굿하트인지 vs
산업·사업의 자연 주기와 outcome이 우연히 동조한 결과인지를 검증.

검증 방법:
  6.1 부처 단위 outcome 매핑 (분야→부처 가중) — H4 분야 가중 결과의 robustness
  6.2 분야 패널 fixed-effect 회귀 (year FE + 분야 FE + GDP control)
  6.3 Permutation test (분야 라벨 1000회 셔플 → null 분포)
  6.4 Lag/lead 분석 (amp_t vs outcome_{t+k}, k=-2..+2)
  6.5 자연 주기성 vs 게임화 분리 (amp_12m 연도 cv)

입력
  data/warehouse.duckdb (indicator_panel)
  data/results/H3_activity_embedding.csv (활동 18원형 라벨)

출력
  data/figs/h6/H6_robustness_panel.png
  data/figs/h6/H6_permutation_null.png
  data/figs/h6/H6_lag_lead.png
  data/results/H6_fe_regression.csv
  data/results/H6_permutation_pvals.csv
  data/results/H6_lag_lead_corr.csv
  data/results/H6_natural_vs_gaming.csv
  data/results/H6_ministry_outcome_corr.csv
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
DB = os.path.join(ROOT, 'data', 'warehouse.duckdb')
H3_CSV = os.path.join(ROOT, 'data', 'results', 'H3_activity_embedding.csv')
OUT_DIR = os.path.join(ROOT, 'data', 'figs', 'h6')
RES_DIR = os.path.join(ROOT, 'data', 'results')
os.makedirs(OUT_DIR, exist_ok=True)

KFONT = None
for f in ['Malgun Gothic','Noto Sans CJK KR','AppleGothic']:
    if any(f in fn.name for fn in mpl.font_manager.fontManager.ttflist):
        mpl.rcParams['font.family'] = f
        KFONT = f
        break
mpl.rcParams['axes.unicode_minus'] = False
RNG = np.random.default_rng(42)

con = duckdb.connect(DB, read_only=True)
emb = pd.read_csv(H3_CSV)
print(f'활동 N = {len(emb)}')

# 분야×연도 wide 패널
panel = con.execute("""
    SELECT fld_nm, year, metric_code, value
    FROM indicator_panel
    WHERE metric_code IN ('amp_12m_norm','wealth_gini','life_expectancy',
                          'rd_total','industry_production_index','tourists_sample',
                          'grdp_national',
                          'housing_supply','local_tax_per_capita','private_edu_hours',
                          'farm_income','fishery_income',
                          'traffic_deaths','traffic_accidents',
                          'ghg_total','ghg_net','ghg_energy',
                          'ict_value_added')
""").fetchdf()
wide = panel.pivot_table(index=['fld_nm','year'], columns='metric_code',
                         values='value').reset_index()

# outcome 매핑 (분야 → outcome metric)
OUTCOME_MAP = {
    '사회복지': 'wealth_gini',
    '보건':   'life_expectancy',
    '과학기술': 'rd_total',
    '산업·중소기업및에너지': 'industry_production_index',
    '문화및관광': 'tourists_sample',
    # H7 추가 (2026-04-28)
    '교육':           'private_edu_hours',
    '국토및지역개발': 'housing_supply',
    '일반·지방행정':   'local_tax_per_capita',
    # 농림 (2026-04-28 추가)
    '농림수산':       'farm_income',
    # H11 추가 (도로교통공단)
    '교통및물류':     'traffic_deaths',
    # H12 추가
    '환경':           'ghg_total',
    # H13 추가
    '통신':           'ict_value_added',
}

# ============================================================
# Step 6.1: 부처 단위 outcome 매핑
# ============================================================
print('\n' + '='*70)
print('Step 6.1: 부처 단위 outcome 매핑 (분야 가중)')
print('='*70)
# 각 부처의 활동 분야 분포 → outcome metric별 가중
# 각 부처의 활동 분야 포트폴리오 비중
ofc_fld = pd.crosstab(emb['OFFC_NM'], emb['FLD_NM'], normalize='index')
ofc_size = emb.groupby('OFFC_NM').size()
ofc_fld = ofc_fld[ofc_size >= 5]
ofc_size = ofc_size[ofc_size >= 5]

# 각 부처에 대해 (활동 가중 amp_12m 시계열) ↔ (분야 가중 outcome 시계열)
# 분야 amp_12m 시계열 사용
years = sorted(wide['year'].dropna().unique().astype(int))
fld_amp = wide.pivot_table(index='year', columns='fld_nm', values='amp_12m_norm')

ofc_results = []
for ofc, w in ofc_fld.iterrows():
    if (w > 0).sum() < 2: continue
    # amp 가중 시계열
    amp_ts = (fld_amp.reindex(columns=w.index) * w).sum(axis=1, min_count=1)
    amp_ts = amp_ts.dropna()
    for fld, oc_metric in OUTCOME_MAP.items():
        if oc_metric not in wide.columns: continue
        if w.get(fld, 0) < 0.05: continue   # 해당 분야 비중 5% 미만이면 skip
        oc_ts = wide[wide['fld_nm']==fld].set_index('year')[oc_metric].dropna()
        common = amp_ts.index.intersection(oc_ts.index)
        if len(common) < 4: continue
        d_amp = amp_ts.loc[common].diff().dropna()
        d_oc  = oc_ts.loc[common].diff().dropna()
        ci = d_amp.index.intersection(d_oc.index)
        if len(ci) < 3: continue
        r_lvl = float(amp_ts.loc[common].corr(oc_ts.loc[common]))
        r_dif = float(d_amp[ci].corr(d_oc[ci]))
        ofc_results.append({
            'OFFC_NM': ofc,
            'fld_outcome': fld,
            'metric': oc_metric,
            'fld_weight': float(w[fld]),
            'n_year': len(common),
            'corr_levels': r_lvl,
            'corr_diff': r_dif,
        })
ofc_corr = pd.DataFrame(ofc_results)
print(f'  부처×outcome pair: {len(ofc_corr)}')
print('  상위/하위 5 (corr_diff):')
print(ofc_corr.sort_values('corr_diff').head(5).round(3).to_string(index=False))
print('  ...')
print(ofc_corr.sort_values('corr_diff').tail(5).round(3).to_string(index=False))
ofc_corr.to_csv(os.path.join(RES_DIR, 'H6_ministry_outcome_corr.csv'),
                index=False, encoding='utf-8-sig')

# 부처 H5 노출 점수 결합
expo = pd.read_csv(os.path.join(RES_DIR, 'H5_ministry_exposure.csv'))
expo = expo.set_index(expo.columns[0])
ofc_corr_w_expo = ofc_corr.merge(expo[['exposure_score']],
                                  left_on='OFFC_NM', right_index=True, how='left')

# ============================================================
# Step 6.2: 분야 패널 fixed-effect 회귀
# ============================================================
print('\n' + '='*70)
print('Step 6.2: 분야 패널 FE 회귀 — Δoutcome ~ Δamp + 분야 FE + 연도 FE')
print('='*70)
fe_rows = []
fe_table = []
for fld, oc_m in OUTCOME_MAP.items():
    sub = wide[wide['fld_nm']==fld].sort_values('year').copy()
    sub = sub[['year','amp_12m_norm', oc_m]].dropna()
    if len(sub) < 5: continue
    # 1차 차분
    sub['d_amp'] = sub['amp_12m_norm'].diff()
    sub['d_oc']  = sub[oc_m].diff()
    sub = sub.dropna()
    sub['fld_nm'] = fld
    fe_rows.append(sub)

fe_df = pd.concat(fe_rows, ignore_index=True) if fe_rows else pd.DataFrame()
print(f'  pooled N = {len(fe_df)} (분야 5 × 차분연도)')

# OLS with dummies (statsmodels 없이 numpy로)
def ols_with_dummies(df, y_col, x_col, fld_fe=True, year_fe=True):
    df = df.copy()
    X = df[[x_col]].copy()
    if fld_fe:
        for f in df['fld_nm'].unique()[1:]:  # baseline drop
            X[f'fld_{f}'] = (df['fld_nm']==f).astype(float)
    if year_fe:
        for y in sorted(df['year'].unique())[1:]:
            X[f'yr_{y}'] = (df['year']==y).astype(float)
    X['const'] = 1.0
    y = df[y_col].values
    Xv = X.values
    beta, *_ = np.linalg.lstsq(Xv, y, rcond=None)
    yhat = Xv @ beta
    resid = y - yhat
    df_resid = max(len(y) - Xv.shape[1], 1)
    sigma2 = (resid @ resid) / df_resid
    cov = sigma2 * np.linalg.pinv(Xv.T @ Xv)
    se = np.sqrt(np.diag(cov))
    from scipy.stats import t as tdist
    tvals = beta / np.where(se>0, se, np.nan)
    pvals = 2 * (1 - tdist.cdf(np.abs(tvals), df=df_resid))
    return pd.DataFrame({'var': X.columns, 'beta': beta, 'se': se,
                         't': tvals, 'p': pvals, 'n': len(y)})

# 정규화 된 standardize: outcome scale 차이 큼. Z 처리.
fe_z = fe_df.copy()
for fld in fe_z['fld_nm'].unique():
    msk = fe_z['fld_nm']==fld
    fe_z.loc[msk, 'd_amp_z'] = (fe_z.loc[msk,'d_amp'] - fe_z.loc[msk,'d_amp'].mean()) / (fe_z.loc[msk,'d_amp'].std() + 1e-9)
    fe_z.loc[msk, 'd_oc_z']  = (fe_z.loc[msk,'d_oc']  - fe_z.loc[msk,'d_oc'].mean())  / (fe_z.loc[msk,'d_oc'].std() + 1e-9)

print('\n  [Model 1] pooled OLS (no FE):')
m1 = ols_with_dummies(fe_z, 'd_oc_z', 'd_amp_z', fld_fe=False, year_fe=False)
print('   ' + m1.head(2).round(4).to_string(index=False).replace('\n','\n   '))

print('\n  [Model 2] +분야 FE:')
m2 = ols_with_dummies(fe_z, 'd_oc_z', 'd_amp_z', fld_fe=True, year_fe=False)
print('   ' + m2[m2['var']=='d_amp_z'].round(4).to_string(index=False).replace('\n','\n   '))

print('\n  [Model 3] +분야 FE + 연도 FE:')
m3 = ols_with_dummies(fe_z, 'd_oc_z', 'd_amp_z', fld_fe=True, year_fe=True)
print('   ' + m3[m3['var']=='d_amp_z'].round(4).to_string(index=False).replace('\n','\n   '))

fe_summary = pd.DataFrame([
    {'model': 'pooled', **m1[m1['var']=='d_amp_z'].iloc[0].to_dict()},
    {'model': '+fld_FE', **m2[m2['var']=='d_amp_z'].iloc[0].to_dict()},
    {'model': '+fld+year_FE', **m3[m3['var']=='d_amp_z'].iloc[0].to_dict()},
])
fe_summary.to_csv(os.path.join(RES_DIR, 'H6_fe_regression.csv'),
                  index=False, encoding='utf-8-sig')
print('\n  → β의 분야 FE 추가 후 변화로 "분야 자연 주기성" vs "게임화 효과" 분리도 가능')

# ============================================================
# Step 6.3: Permutation test
# ============================================================
print('\n' + '='*70)
print('Step 6.3: Permutation test (분야 라벨 셔플 1000회)')
print('='*70)
# 각 분야×outcome의 corr_diff(차분 상관)에 대해 분야 라벨을 1000번 무작위 셔플 → null
# 관찰값과 null 비교
N_PERM = 1000
perm_results = []
for fld, oc_m in OUTCOME_MAP.items():
    amp_ts = wide[wide['fld_nm']==fld].set_index('year')['amp_12m_norm'].dropna()
    oc_ts  = wide[wide['fld_nm']==fld].set_index('year')[oc_m].dropna()
    common = amp_ts.index.intersection(oc_ts.index)
    if len(common) < 4: continue
    d_amp = amp_ts.loc[common].diff().dropna().values
    d_oc  = oc_ts.loc[common].diff().dropna().values
    if len(d_amp) != len(d_oc): continue
    obs = pearsonr(d_amp, d_oc)[0] if len(d_amp) > 1 else np.nan

    null = []
    for _ in range(N_PERM):
        shuf = RNG.permutation(d_oc)
        null.append(pearsonr(d_amp, shuf)[0])
    null = np.array(null)
    p_two = float(((np.abs(null) >= np.abs(obs)).sum() + 1) / (N_PERM + 1))
    perm_results.append({
        'fld': fld, 'outcome': oc_m, 'n_diff': len(d_amp),
        'obs_corr_diff': obs,
        'null_mean': float(null.mean()),
        'null_std': float(null.std()),
        'pval_2sided': p_two,
    })
perm_df = pd.DataFrame(perm_results).sort_values('pval_2sided')
print(perm_df.round(4).to_string(index=False))
perm_df.to_csv(os.path.join(RES_DIR, 'H6_permutation_pvals.csv'),
               index=False, encoding='utf-8-sig')

# ============================================================
# Step 6.4: Lag / lead 분석
# ============================================================
print('\n' + '='*70)
print('Step 6.4: Lag/lead 차분 상관 (k=-2..+2)')
print('='*70)
LAGS = [-2, -1, 0, 1, 2]
lag_results = []
for fld, oc_m in OUTCOME_MAP.items():
    amp_ts = wide[wide['fld_nm']==fld].set_index('year')['amp_12m_norm'].dropna()
    oc_ts  = wide[wide['fld_nm']==fld].set_index('year')[oc_m].dropna()
    common = amp_ts.index.intersection(oc_ts.index)
    if len(common) < 5: continue
    a = amp_ts.loc[common].diff()
    o = oc_ts.loc[common].diff()
    for k in LAGS:
        a_s = a.shift(-k)  # k>0: amp 미래값 ↔ oc 현재 → "outcome → amp" 인과
        df_lag = pd.concat([a_s.rename('amp'), o.rename('oc')], axis=1).dropna()
        if len(df_lag) < 3: continue
        c = pearsonr(df_lag['amp'], df_lag['oc'])[0]
        lag_results.append({'fld': fld, 'outcome': oc_m, 'lag': k,
                            'n': len(df_lag), 'corr_diff': c})
lag_df = pd.DataFrame(lag_results)
print(lag_df.pivot_table(index=['fld','outcome'], columns='lag',
                          values='corr_diff').round(3).to_string())
lag_df.to_csv(os.path.join(RES_DIR, 'H6_lag_lead_corr.csv'),
              index=False, encoding='utf-8-sig')

# ============================================================
# Step 6.5: 자연 주기성 vs 게임화 분리 (amp_12m의 연도 cv)
# ============================================================
print('\n' + '='*70)
print('Step 6.5: 자연 주기성 vs 게임화 (amp_12m 연도 cv)')
print('='*70)
# 분야별 amp_12m_norm의 시간적 안정성
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
nat_df.to_csv(os.path.join(RES_DIR, 'H6_natural_vs_gaming.csv'),
              index=False, encoding='utf-8-sig')
print('\n  해석: amp_cv 큼 = 게임화 변동성 큼 (KPI 압력 동적)')
print('        amp_cv 작음 = 자연 주기성 (사업 특성 고정)')

# 활동 단위로도 해보기
emb_actv_cv = emb.groupby('FLD_NM')['amp_12m_norm'].agg(['mean','std','count']).reset_index()
emb_actv_cv['cv_actv'] = emb_actv_cv['std'] / emb_actv_cv['mean']
print('\n  활동 분포 cv (분야 내 활동 amp 분산):')
print(emb_actv_cv.round(3).to_string(index=False))

# ============================================================
# Figure A: 견고성 패널 (4 subplots)
# ============================================================
fig, axes = plt.subplots(2, 2, figsize=(15, 10))

# A1: FE 회귀 결과
ax = axes[0,0]
xx = np.arange(len(fe_summary))
ax.bar(xx, fe_summary['beta'], yerr=fe_summary['se']*1.96, color='#5475a8', alpha=0.85)
ax.axhline(0, color='#888', lw=0.8)
ax.set_xticks(xx); ax.set_xticklabels(fe_summary['model'], rotation=10)
ax.set_ylabel('β (Δoutcome ~ Δamp)')
ax.set_title(f'FE 회귀 — Δoutcome_z ~ Δamp_z + FE\n(N={int(fe_summary.iloc[0]["n"])}, ±95% CI)')
ax.grid(alpha=0.3)
for i, p in enumerate(fe_summary['p']):
    ax.annotate(f'p={p:.3f}', (xx[i], fe_summary['beta'].iloc[i]),
                xytext=(0,8), textcoords='offset points',
                ha='center', fontsize=9)

# A2: 자연 vs 게임화 cv (분야)
ax = axes[0,1]
nat_sorted = nat_df.sort_values('amp_cv', ascending=True)
ax.barh(range(len(nat_sorted)), nat_sorted['amp_cv'], color='#c87f5a')
ax.set_yticks(range(len(nat_sorted)))
ax.set_yticklabels(nat_sorted['fld'])
ax.set_xlabel('amp_12m 시간적 cv (높을수록 게임화 변동, 낮으면 자연 주기)')
ax.set_title('분야별 amp_12m 시간 변동성')
ax.grid(alpha=0.3, axis='x')

# A3: 부처 노출 vs 부처 outcome 차분 상관
ax = axes[1,0]
if len(ofc_corr_w_expo) > 0:
    sub = ofc_corr_w_expo.dropna()
    ax.scatter(sub['exposure_score'], sub['corr_diff'],
               s=40, c=sub['fld_weight']*250, alpha=0.6, cmap='Reds')
    # outcome 별 색
    for oc in sub['metric'].unique():
        ss = sub[sub['metric']==oc]
        ax.scatter(ss['exposure_score'], ss['corr_diff'], label=oc, alpha=0.8, s=30)
    ax.axhline(0, color='#888', lw=0.6)
    ax.set_xlabel('굿하트 노출 점수 (H5)')
    ax.set_ylabel('amp ~ outcome 차분 상관 (부처 단위)')
    ax.set_title(f'부처 노출 × outcome 디커플링 (N={len(sub)})')
    ax.legend(fontsize=7, loc='best')
    ax.grid(alpha=0.3)

# A4: Permutation null vs obs
ax = axes[1,1]
if len(perm_df) > 0:
    yy = np.arange(len(perm_df))
    ax.barh(yy, perm_df['obs_corr_diff'], color='#a85454', alpha=0.85, label='관측 corr_diff')
    ax.errorbar(perm_df['null_mean'], yy, xerr=perm_df['null_std']*2,
                fmt='o', color='#444', label='null ±2σ')
    ax.set_yticks(yy); ax.set_yticklabels([f'{r["fld"]}/{r["outcome"]}' for _,r in perm_df.iterrows()])
    ax.axvline(0, color='#888', lw=0.6)
    for i, p in enumerate(perm_df['pval_2sided'].values):
        ax.annotate(f'p={p:.3f}', (perm_df['obs_corr_diff'].iloc[i], yy[i]),
                    xytext=(5,0), textcoords='offset points', va='center', fontsize=8)
    ax.set_xlabel('Δamp ~ Δoutcome 상관')
    ax.set_title(f'Permutation test ({N_PERM}회) — null 대비 관측치')
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3, axis='x')

plt.tight_layout()
fig.savefig(os.path.join(OUT_DIR, 'H6_robustness_panel.png'), dpi=130, bbox_inches='tight')
plt.close()

# ============================================================
# Figure B: Permutation null distribution detail
# ============================================================
if len(perm_df) > 0:
    fig, axes = plt.subplots(1, len(perm_df), figsize=(4*len(perm_df), 4), sharey=True)
    if len(perm_df) == 1: axes = [axes]
    for ax, (_, row) in zip(axes, perm_df.iterrows()):
        # 다시 simulate (간단히 다시)
        amp_ts = wide[wide['fld_nm']==row['fld']].set_index('year')['amp_12m_norm'].dropna()
        oc_ts  = wide[wide['fld_nm']==row['fld']].set_index('year')[row['outcome']].dropna()
        common = amp_ts.index.intersection(oc_ts.index)
        d_amp = amp_ts.loc[common].diff().dropna().values
        d_oc  = oc_ts.loc[common].diff().dropna().values
        null = np.array([pearsonr(d_amp, RNG.permutation(d_oc))[0] for _ in range(N_PERM)])
        ax.hist(null, bins=30, color='#cccccc', edgecolor='#888888')
        ax.axvline(row['obs_corr_diff'], color='#a31010', lw=2,
                   label=f'관측: {row["obs_corr_diff"]:.2f}')
        ax.set_title(f'{row["fld"]} × {row["outcome"]}\np={row["pval_2sided"]:.3f}, N={int(row["n_diff"])}')
        ax.set_xlabel('null corr_diff')
        ax.legend(fontsize=8)
        ax.grid(alpha=0.3)
    axes[0].set_ylabel('빈도')
    plt.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, 'H6_permutation_null.png'), dpi=130, bbox_inches='tight')
    plt.close()

# ============================================================
# Figure C: lag/lead heatmap
# ============================================================
if len(lag_df) > 0:
    pv = lag_df.pivot_table(index=['fld','outcome'], columns='lag', values='corr_diff')
    fig, ax = plt.subplots(figsize=(9, 4 + 0.3*len(pv)))
    sns.heatmap(pv, annot=True, fmt='.2f', cmap='RdBu_r', center=0, ax=ax,
                cbar_kws={'label':'corr_diff'})
    ax.set_title('Lag/Lead 차분 상관 — k=-2..+2 (k>0: outcome → amp 가능성)')
    plt.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, 'H6_lag_lead.png'), dpi=130, bbox_inches='tight')
    plt.close()

print('\n=== 그림 ===')
for f in sorted(os.listdir(OUT_DIR)):
    print(f'  {f}')

con.close()
print('\n완료.')
