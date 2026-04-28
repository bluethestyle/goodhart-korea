"""H8 v2 (11y): 비판적 자기평가 — H3 v2 11년 임베딩 기반 재실행.

비판 A: "분야별 이질성은 trivial"
비판 B: "출연금→게임화 동인도 trivial — 회계 cycle"

H3 v2 11y 클러스터 (4개):
  C0 = 인건비 (personnel)
  C1 = 자산취득 신규 분리 (direct_invest)
  C2 = 출연금 (chooyeon) → sub0/sub1 존재
  C3 = 정상 (normal), sub-cluster 없음

방법:
  Q1: 활동 단위 → 분야 broadcast outcome → 분야 FE only vs +원형 비중×Δamp R² 분해
  Q2: 분야×원형그룹×11년 monthly_exec amp_12m → outcome 차분 상관

출력:
  data/figs/h8_11y/H8_within_field_panel_11y.png
  data/results/H8_archetype_outcome_11y.csv
  data/results/H8_field_archetype_decomp_11y.csv
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
H3_CSV  = os.path.join(ROOT, 'data', 'results', 'H3_activity_embedding_11y.csv')
SUB_CSV = os.path.join(ROOT, 'data', 'results', 'H3_cluster2_subembedding_11y.csv')
OUT_DIR = os.path.join(ROOT, 'data', 'figs', 'h8_11y')
RES_DIR = os.path.join(ROOT, 'data', 'results')
os.makedirs(OUT_DIR, exist_ok=True)

# Korean font
KFONT = None
for f in ['Malgun Gothic', 'Noto Sans CJK KR', 'AppleGothic']:
    if any(f in fn.name for fn in mpl.font_manager.fontManager.ttflist):
        mpl.rcParams['font.family'] = f
        KFONT = f
        break
mpl.rcParams['axes.unicode_minus'] = False

# ============================================================
# Step 1: 데이터 로드
# ============================================================
emb = pd.read_csv(H3_CSV)
sub = pd.read_csv(SUB_CSV)

key_cols = ['FLD_NM', 'OFFC_NM', 'PGM_NM', 'ACTV_NM']
df = emb.merge(sub[key_cols + ['subcluster']], on=key_cols, how='left')

# H3 v2 11y archetype label
# C0=인건비, C1=자산취득(신규), C2=출연금(sub0/sub1/-1), C3=정상
def archetype_label(row):
    c = row['cluster']
    if c == 0:
        return 'A0_personnel'
    if c == 1:
        return 'A1_direct_invest'   # 신규 분리 자산취득형
    if c == 2:
        sc = row.get('subcluster', np.nan)
        if pd.isna(sc) or sc == -1:
            return 'A2_noise'
        return f'A2_sub{int(sc):02d}'   # A2_sub00 / A2_sub01
    # c == 3
    return 'A3_normal'

df['archetype'] = df.apply(archetype_label, axis=1)
print(f'활동 N = {len(df):,}, 원형 수 = {df["archetype"].nunique()}')
print(df['archetype'].value_counts().sort_index())

# ============================================================
# OUTCOME_MAP (12분야)
# ============================================================
OUTCOME_MAP = {
    '사회복지':            'wealth_gini',
    '보건':                'life_expectancy',
    '과학기술':            'rd_total',
    '산업·중소기업및에너지': 'industry_production_index',
    '문화및관광':          'tourists_sample',
    '교육':                'private_edu_hours',
    '국토및지역개발':      'housing_supply',
    '일반·지방행정':       'local_tax_per_capita',
    '농림수산':            'farm_income',
    '교통및물류':          'traffic_deaths',
    '환경':                'ghg_total',
    '통신':                'ict_value_added',
}

con = duckdb.connect(DB, read_only=True)
metrics_needed = list(OUTCOME_MAP.values()) + ['amp_12m_norm']
panel = con.execute(f"""
    SELECT fld_nm, year, metric_code, value
    FROM indicator_panel
    WHERE metric_code IN ({",".join(["'"+m+"'" for m in metrics_needed])})
""").fetchdf()
wide = panel.pivot_table(
    index=['fld_nm', 'year'], columns='metric_code', values='value'
).reset_index()
con.close()
print(f'\nindicator_panel wide: {wide.shape}, 분야 = {wide["fld_nm"].nunique()}')
available_outcomes = [c for c in metrics_needed if c in wide.columns and c != 'amp_12m_norm']
print(f'유효 outcome 컬럼: {available_outcomes}')

# ============================================================
# Step 2: Q1 — 분야 FE vs +원형 비중×Δamp R² 분해
# ============================================================
print('\n' + '=' * 70)
print('Q1: 분야 FE vs +원형 비중×Δamp 상호작용 R² 분해')
print('=' * 70)

# 원형 비중 (분야별)
fld_archetype_share = pd.crosstab(df['FLD_NM'], df['archetype'], normalize='index')
noise_cols = [c for c in fld_archetype_share.columns if 'noise' in c.lower()]
fld_archetype_share = fld_archetype_share.drop(columns=noise_cols, errors='ignore')

# Δoutcome 시계열 (분야×연도 차분) — 12분야 pooled
delta_records = []
for fld, oc_m in OUTCOME_MAP.items():
    sub_w = wide[wide['fld_nm'] == fld].sort_values('year')
    if oc_m not in sub_w.columns:
        continue
    sub_w = sub_w[['year', 'amp_12m_norm', oc_m]].dropna()
    if len(sub_w) < 4:
        continue
    sub_w = sub_w.copy()
    sub_w['d_amp'] = sub_w['amp_12m_norm'].diff()
    sub_w['d_oc']  = sub_w[oc_m].diff()
    sub_w = sub_w.dropna()
    if sub_w['d_amp'].std() > 0:
        sub_w['d_amp_z'] = (sub_w['d_amp'] - sub_w['d_amp'].mean()) / sub_w['d_amp'].std()
    else:
        sub_w['d_amp_z'] = 0.0
    if sub_w['d_oc'].std() > 0:
        sub_w['d_oc_z'] = (sub_w['d_oc'] - sub_w['d_oc'].mean()) / sub_w['d_oc'].std()
    else:
        sub_w['d_oc_z'] = 0.0
    sub_w['fld_nm'] = fld
    delta_records.append(sub_w)

if not delta_records:
    print('  [WARNING] delta_records 없음 — indicator_panel 분야명 불일치 가능')
    fe_df = pd.DataFrame()
else:
    fe_df = pd.concat(delta_records, ignore_index=True)
    print(f'  pooled N = {len(fe_df)}')

shares = fld_archetype_share.reset_index()
fe_df = fe_df.merge(shares, left_on='fld_nm', right_on='FLD_NM', how='left')

def ols(df_in, y_col, x_cols):
    df_in = df_in.dropna(subset=[y_col] + x_cols).copy()
    if len(df_in) < 5:
        return None
    X = df_in[x_cols].copy()
    for c in X.columns:
        X[c] = pd.to_numeric(X[c], errors='coerce')
    X['const'] = 1.0
    y = df_in[y_col].values
    Xv = X.values.astype(float)
    msk = ~np.isnan(Xv).any(axis=1)
    Xv = Xv[msk]; y = y[msk]
    if len(y) < 5:
        return None
    beta, *_ = np.linalg.lstsq(Xv, y, rcond=None)
    yhat = Xv @ beta
    ss_res = ((y - yhat) ** 2).sum()
    ss_tot = ((y - y.mean()) ** 2).sum()
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0
    return {'beta': beta, 'cols': X.columns.tolist(), 'r2': r2, 'n': int(len(y))}

# Model A: Δoc_z ~ Δamp_z (no FE)
m_base = ols(fe_df, 'd_oc_z', ['d_amp_z'])
if m_base:
    print(f'\n[A] Δoc ~ Δamp (no FE): R²={m_base["r2"]:.3f}, '
          f'β_amp={m_base["beta"][0]:.3f}, N={m_base["n"]}')
else:
    print('[A] 모델 추정 실패 (데이터 부족)')
    m_base = {'r2': 0.0, 'n': 0, 'beta': [0]}

# Model B: + 분야 FE
fe_df_b = fe_df.copy()
flds_unique = sorted(fe_df_b['fld_nm'].dropna().unique())
for f in flds_unique[1:]:
    fe_df_b[f'fld_{f}'] = (fe_df_b['fld_nm'] == f).astype(float)
fld_dummies = [c for c in fe_df_b.columns if c.startswith('fld_') and c != 'fld_nm']
m_fld = ols(fe_df_b, 'd_oc_z', ['d_amp_z'] + fld_dummies)
if m_fld:
    print(f'[B] +분야 FE: R²={m_fld["r2"]:.3f}, '
          f'β_amp={m_fld["beta"][0]:.3f}, N={m_fld["n"]}')
else:
    print('[B] 모델 추정 실패')
    m_fld = {'r2': 0.0, 'n': 0, 'beta': [0]}

# Model C: + 원형 비중×Δamp 상호작용
# v2 11y: C0=인건비(A0_personnel), C1=자산취득(A1_direct_invest),
#         C2=출연금sub(A2_sub00/A2_sub01), C3=정상(A3_normal)
risk_archs = ['A0_personnel', 'A1_direct_invest', 'A2_sub00', 'A2_sub01', 'A3_normal']
fe_df_c = fe_df_b.copy()
for a in risk_archs:
    if a in fe_df_c.columns:
        fe_df_c[f'{a}_x_amp'] = fe_df_c[a] * fe_df_c['d_amp_z']
ix_cols = [f'{a}_x_amp' for a in risk_archs if f'{a}_x_amp' in fe_df_c.columns]
m_c = ols(fe_df_c, 'd_oc_z', ['d_amp_z'] + fld_dummies + ix_cols)
if m_c:
    print(f'[C] +분야 FE +원형×Δamp: R²={m_c["r2"]:.3f}, '
          f'β_amp={m_c["beta"][0]:.3f}, N={m_c["n"]}')
    for i, col in enumerate(m_c['cols']):
        if 'x_amp' in col:
            print(f'    {col}: β={m_c["beta"][i]:.3f}')
else:
    print('[C] 모델 추정 실패')
    m_c = {'r2': 0.0, 'n': 0, 'beta': [0], 'cols': []}

dr2_arch = m_c['r2'] - m_fld['r2']
dr2_fe   = m_fld['r2'] - m_base['r2']
print(f'\n  → 분야 FE만 ΔR² (vs base)  = {dr2_fe:+.4f}')
print(f'  → +원형 ΔR² (B→C)          = {dr2_arch:+.4f}')
print(f'  (참고: 5y 버전 ΔR² = +0.094)')

decomp = pd.DataFrame([
    {'model': 'A_base',                    'r2': m_base['r2'], 'n': m_base['n']},
    {'model': 'B_field_FE',               'r2': m_fld['r2'],  'n': m_fld['n']},
    {'model': 'C_field_FE+archetype_xamp', 'r2': m_c['r2'],   'n': m_c['n']},
])
decomp['delta_r2'] = decomp['r2'].diff().fillna(decomp['r2'])
print('\n=== R² 분해 ===')
print(decomp.round(4).to_string(index=False))
decomp.to_csv(
    os.path.join(RES_DIR, 'H8_field_archetype_decomp_11y.csv'),
    index=False, encoding='utf-8-sig'
)

# ============================================================
# Step 3: Q2 — 분야×원형그룹×11년 monthly_exec amp 시계열 vs outcome
# ============================================================
print('\n' + '=' * 70)
print('Q2: 분야×원형그룹 monthly amp_12m × outcome 차분 상관')
print('=' * 70)

con = duckdb.connect(DB, read_only=True)
PURE_ACCT = """(
    ACTV_NM ILIKE '%전출금%' OR ACTV_NM ILIKE '%타계정%' OR ACTV_NM ILIKE '%여유자금%'
 OR ACTV_NM ILIKE '%국고예탁%' OR ACTV_NM ILIKE '%기금예탁%' OR ACTV_NM ILIKE '%국고예치%'
 OR ACTV_NM ILIKE '%회계간거래%' OR ACTV_NM ILIKE '%회계간전출%'
 OR ACTV_NM ILIKE '%회계기금간%' OR ACTV_NM ILIKE '%여유자금운용%'
)"""
me = con.execute(f"""
    SELECT FLD_NM, OFFC_NM, PGM_NM, ACTV_NM, FSCL_YY AS year, EXE_M AS month,
           SUM(EP_AMT) AS amt
    FROM monthly_exec
    WHERE EXE_M BETWEEN 1 AND 12
      AND FSCL_YY BETWEEN 2013 AND 2024
      AND NOT {PURE_ACCT}
    GROUP BY 1,2,3,4,5,6
""").fetchdf()
con.close()
me = me.merge(df[key_cols + ['archetype']], on=key_cols, how='inner')
print(f'  joined monthly rows = {len(me):,}')

# arch_group 함수: v2 11y 4 cluster 기반
def arch_group(a):
    if a == 'A2_sub00':        return 'chooyeon_sub0'
    if a == 'A2_sub01':        return 'chooyeon_sub1'
    if a == 'A1_direct_invest': return 'direct_invest'
    if a == 'A0_personnel':     return 'personnel'
    if a == 'A3_normal':        return 'normal'
    return 'noise'

me['arch_grp'] = me['archetype'].map(arch_group)

# 분야×원형그룹×연도별 amp_12m
from scipy import fft as scfft
records = []
for (fld, grp, yr), g in me.groupby(['FLD_NM', 'arch_grp', 'year']):
    if grp == 'noise':
        continue
    arr = np.zeros(12)
    for _, r in g.iterrows():
        m_idx = int(r['month']) - 1
        if 0 <= m_idx < 12:
            arr[m_idx] += r['amt']
    if arr.sum() <= 0:
        continue
    yf = scfft.fft(arr - arr.mean())
    amp_12 = abs(yf[1]) * 2 / 12 / (arr.sum() / 12 + 1e-9)
    records.append({'fld_nm': fld, 'arch_grp': grp, 'year': int(yr), 'amp_12m': amp_12})

amp_df = pd.DataFrame(records)
print(f'  분야×원형×연도 amp_12m 셀 수: {len(amp_df)}')

# 분야×원형그룹별 amp 시계열 vs outcome 차분 상관
results = []
for (fld, grp), g in amp_df.groupby(['fld_nm', 'arch_grp']):
    if fld not in OUTCOME_MAP:
        continue
    oc_m = OUTCOME_MAP[fld]
    amp_ts = g.set_index('year')['amp_12m'].sort_index()
    if len(amp_ts) < 4:
        continue
    oc_ts = wide[wide['fld_nm'] == fld].set_index('year')[oc_m].dropna() \
            if oc_m in wide.columns else pd.Series(dtype=float)
    common = amp_ts.index.intersection(oc_ts.index)
    if len(common) < 4:
        continue
    d_amp = amp_ts.loc[common].diff().dropna()
    d_oc  = oc_ts.loc[common].diff().dropna()
    ci = d_amp.index.intersection(d_oc.index)
    if len(ci) < 3:
        continue
    r_lvl = float(amp_ts.loc[common].corr(oc_ts.loc[common]))
    r_dif = float(d_amp[ci].corr(d_oc[ci]))
    results.append({
        'fld': fld, 'arch_grp': grp, 'outcome': oc_m,
        'n_year': len(common),
        'amp_mean': float(amp_ts.mean()),
        'corr_levels': r_lvl,
        'corr_diff': r_dif,
    })

arch_corr = pd.DataFrame(results)
arch_corr['fld_arch'] = arch_corr['fld'] + ' / ' + arch_corr['arch_grp']
print('\n  분야×원형그룹 outcome 차분 상관:')
print(arch_corr.sort_values(['fld', 'arch_grp']).round(3).to_string(index=False))
arch_corr.to_csv(
    os.path.join(RES_DIR, 'H8_archetype_outcome_11y.csv'),
    index=False, encoding='utf-8-sig'
)

# 같은 분야 안 원형별 부호 폭 (5y 대비 확인)
print('\n  === 같은 분야 안 원형별 부호 폭 ===')
sign_width_rows = []
for fld in arch_corr['fld'].unique():
    sub_a = arch_corr[arch_corr['fld'] == fld]
    if len(sub_a) < 2:
        continue
    diff = sub_a['corr_diff'].max() - sub_a['corr_diff'].min()
    sign_width_rows.append({'fld': fld, 'sign_width': diff})
    if diff > 0.3:
        print(f'  [{fld}] 부호 폭 = {diff:.3f}')
        for _, r in sub_a.iterrows():
            print(f'    {r["arch_grp"]:22s}  N={r["n_year"]:>2d}  corr_diff={r["corr_diff"]:+.3f}')

sign_width_df = pd.DataFrame(sign_width_rows).sort_values('sign_width', ascending=False)
print(f'\n  최대 부호 폭: {sign_width_df["sign_width"].max():.3f} ({sign_width_df.iloc[0]["fld"]})')

# ============================================================
# Step 4: 5y vs 11y 비교 요약
# ============================================================
print('\n' + '=' * 70)
print('5y vs 11y 비교')
print('=' * 70)
print('  5y ΔR² (B→C) = +0.094')
print(f'  11y ΔR² (B→C) = {dr2_arch:+.4f}')
print(f'  차이 = {dr2_arch - 0.094:+.4f}')
print()
print('  5y 자산취득형: C1=자산취득 (H3 5y에서 chooyeon과 혼재)')
print('  11y 자산취득형: C1=direct_invest 완전 분리 → 신호 강화 예상')

# ============================================================
# Step 5: 시각화 (max 1800px)
# ============================================================
DPI = 130
MAX_PX = 1800
FIGW = min(MAX_PX / DPI, 14)
FIGH = 7.5

fig, axes = plt.subplots(1, 2, figsize=(FIGW, FIGH))
fig.suptitle('H8 v2 (11년): 분야 FE vs 원형 비중×Δamp — 비판적 자기평가',
             fontsize=13, fontweight='bold', y=1.01)

# --- 왼쪽: Q1 R² 분해 바 차트 ---
ax = axes[0]
r2_vals = [decomp.loc[decomp['model'] == m, 'r2'].values[0]
           for m in ['A_base', 'B_field_FE', 'C_field_FE+archetype_xamp']]
labels = ['A: 기본\n(Δamp만)', 'B: +분야 FE', 'C: +원형×Δamp']
colors = ['#bbbbbb', '#5475a8', '#a85454']
xx = np.arange(len(labels))
bars = ax.bar(xx, r2_vals, color=colors, alpha=0.85, width=0.6)
ax.set_xticks(xx)
ax.set_xticklabels(labels, fontsize=10)
ax.set_ylabel('R²', fontsize=11)
ax.set_title(
    f'Q1: R² 분해\n'
    f'ΔR² (B→C, 원형 추가) = {dr2_arch:+.3f}\n'
    f'[5y: +0.094]',
    fontsize=11
)
ax.grid(alpha=0.3, axis='y')
for i, (v, b) in enumerate(zip(r2_vals, bars)):
    ax.annotate(f'{v:.3f}', (xx[i], v), xytext=(0, 5),
                textcoords='offset points', ha='center', fontsize=10)
# 원형 interaction β 주석
beta_labels = []
for i, col in enumerate(m_c.get('cols', [])):
    if 'x_amp' in col:
        beta_labels.append(f'{col.replace("_x_amp","")}: β={m_c["beta"][i]:.2f}')
if beta_labels:
    ax.text(0.02, 0.97, '\n'.join(beta_labels),
            transform=ax.transAxes, va='top', fontsize=7.5,
            bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', alpha=0.8))

# --- 오른쪽: Q2 분야×원형그룹 corr_diff 히트맵 ---
ax = axes[1]
if not arch_corr.empty:
    piv = arch_corr.pivot_table(index='fld', columns='arch_grp', values='corr_diff')
    grp_order = [g for g in ['personnel', 'direct_invest', 'chooyeon_sub0', 'chooyeon_sub1', 'normal']
                 if g in piv.columns]
    piv = piv[grp_order] if grp_order else piv
    vabs = max(abs(piv.values[~np.isnan(piv.values)]).max() if piv.values.size > 0 else 0.5, 0.3)
    sns.heatmap(
        piv, annot=True, fmt='.2f', cmap='RdBu_r',
        center=0, vmin=-vabs, vmax=vabs, ax=ax,
        cbar_kws={'label': 'corr(Δamp ~ Δoutcome)'},
        linewidths=0.4, linecolor='#cccccc'
    )
    ax.set_title(
        'Q2: 분야×원형그룹 outcome 결합\n'
        '(부호 차이 = 회계 cycle 가설 기각)\n'
        f'최대 부호 폭: {sign_width_df["sign_width"].max():.2f}'
        f' ({sign_width_df.iloc[0]["fld"]})',
        fontsize=11
    )
    ax.set_xlabel('원형 그룹', fontsize=10)
    ax.set_ylabel('분야', fontsize=10)
    ax.tick_params(axis='x', rotation=25)
    ax.tick_params(axis='y', rotation=0)
else:
    ax.text(0.5, 0.5, 'arch_corr 데이터 없음', ha='center', va='center',
            transform=ax.transAxes)

plt.tight_layout()
out_png = os.path.join(OUT_DIR, 'H8_within_field_panel_11y.png')
fig.savefig(out_png, dpi=DPI, bbox_inches='tight')
plt.close()
print(f'\n그림 저장: {out_png}')
print('\n완료.')
