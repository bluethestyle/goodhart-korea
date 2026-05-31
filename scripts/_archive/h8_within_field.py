"""H8: 사용자 비판 두 가지에 정면 답.

비판 A: "분야별 이질성은 trivial — 분야가 다르니 outcome도 다르다"
비판 B: "출연금→게임화 동인도 trivial — 출연기관 실적평가 주기 반응"

이를 검증하려면:
  Q1. 분야 FE 통제 후에도 사업 원형(A0/A1/A2_subN) 비중이 outcome 차이를
      추가 설명하는가? (trivial 비판 답)
  Q2. 같은 분야 안에서 출연금형 vs 직접투자형 사업의 amp_12m이
      outcome과 다른 결합 패턴을 보이는가? (회계 cycle 비판 답)

방법:
  Q1: 활동 단위 → 분야 broadcast outcome → 분야 FE only 회귀 vs 분야 FE + 원형 비중 회귀
      R² 차이가 0이 아니면 사업 형태가 진짜 추가 정보
  Q2: 분야 안에서 출연금형 활동만의 amp_12m 시계열 vs 직접투자형 활동만의 시계열을
      각각 outcome과 차분 상관. 부호 다르면 회계 cycle 가설 기각.

출력:
  data/figs/h8/H8_within_field_panel.png
  data/results/H8_archetype_outcome.csv      각 archetype × outcome corr_diff
  data/results/H8_field_archetype_decomp.csv 분야 FE vs +원형 R²
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
SUB_CSV = os.path.join(ROOT, 'data', 'results', 'H3_cluster2_subembedding.csv')
OUT_DIR = os.path.join(ROOT, 'data', 'figs', 'h8')
RES_DIR = os.path.join(ROOT, 'data', 'results')
os.makedirs(OUT_DIR, exist_ok=True)

KFONT = None
for f in ['Malgun Gothic','Noto Sans CJK KR','AppleGothic']:
    if any(f in fn.name for fn in mpl.font_manager.fontManager.ttflist):
        mpl.rcParams['font.family'] = f
        KFONT = f
        break
mpl.rcParams['axes.unicode_minus'] = False

# ============================================================
# Step 1: 데이터 로드 — 활동 임베딩 + 분야 outcome 시계열
# ============================================================
emb = pd.read_csv(H3_CSV)
sub = pd.read_csv(SUB_CSV)
key_cols = ['FLD_NM','OFFC_NM','PGM_NM','ACTV_NM']
df = emb.merge(sub[key_cols+['subcluster']], on=key_cols, how='left')

def archetype_label(row):
    if row['cluster']==0: return 'A0_personnel'
    if row['cluster']==1: return 'A1_chooyeon'
    sc = row['subcluster']
    if pd.isna(sc) or sc==-1: return 'A2_noise'
    return f'A2_sub{int(sc):02d}'
df['archetype'] = df.apply(archetype_label, axis=1)
print(f'활동 N = {len(df)}, 원형 = {df["archetype"].nunique()}')

OUTCOME_MAP = {
    '사회복지': 'wealth_gini',
    '보건':   'life_expectancy',
    '과학기술': 'rd_total',
    '산업·중소기업및에너지': 'industry_production_index',
    '문화및관광': 'tourists_sample',
    '교육':           'private_edu_hours',
    '국토및지역개발': 'housing_supply',
    '일반·지방행정':   'local_tax_per_capita',
}
con = duckdb.connect(DB, read_only=True)
panel = con.execute(f"""
    SELECT fld_nm, year, metric_code, value
    FROM indicator_panel
    WHERE metric_code IN ('amp_12m_norm','{ "','".join(OUTCOME_MAP.values())}')
""").fetchdf()
wide = panel.pivot_table(index=['fld_nm','year'], columns='metric_code',
                         values='value').reset_index()
con.close()

# ============================================================
# Step 2: Q1 — 분야 FE 통제 후 사업 원형이 추가 설명?
# ============================================================
print('\n' + '='*70)
print('Q1: 분야 FE vs +원형 비중 — outcome 차분 상관 설명력')
print('='*70)
# 활동 단위 amp_12m(연도 평균) 이미 있음. 이를 분야×연도로 집계가 아니라
# *분야×원형×연도* 단위로 활동의 amp_12m 가중평균을 시계열로
# 그러나 활동 amp_12m은 H3에서 연도 평균이라 시계열 X.
# 대안: 분야×원형 비중을 정적 변수로 사용 + 분야×연도 outcome 변화로 회귀

# 원형 비중 (분야별)
fld_archetype_share = pd.crosstab(df['FLD_NM'], df['archetype'], normalize='index')
fld_archetype_share = fld_archetype_share[[c for c in fld_archetype_share.columns if c!='A2_noise']]

# Δoutcome 시계열 (분야×연도 차분)
delta_records = []
for fld, oc_m in OUTCOME_MAP.items():
    sub_w = wide[wide['fld_nm']==fld].sort_values('year')
    if oc_m not in sub_w.columns: continue
    sub_w = sub_w[['year','amp_12m_norm', oc_m]].dropna()
    if len(sub_w) < 4: continue
    sub_w['d_amp'] = sub_w['amp_12m_norm'].diff()
    sub_w['d_oc']  = sub_w[oc_m].diff()
    sub_w = sub_w.dropna()
    sub_w['fld_nm'] = fld
    # 표준화
    if sub_w['d_amp'].std() > 0:
        sub_w['d_amp_z'] = (sub_w['d_amp'] - sub_w['d_amp'].mean()) / sub_w['d_amp'].std()
    if sub_w['d_oc'].std() > 0:
        sub_w['d_oc_z'] = (sub_w['d_oc'] - sub_w['d_oc'].mean()) / sub_w['d_oc'].std()
    delta_records.append(sub_w)
fe_df = pd.concat(delta_records, ignore_index=True)
print(f'  pooled N = {len(fe_df)}')

# 원형 비중을 분야로 broadcast
shares = fld_archetype_share.reset_index()
fe_df = fe_df.merge(shares, left_on='fld_nm', right_on='FLD_NM', how='left')

# OLS 함수
def ols(df, y_col, x_cols):
    df = df.dropna(subset=[y_col]+x_cols).copy()
    if len(df) < 5: return None
    X = df[x_cols].copy()
    # 비숫자 컬럼 제거 — 누락된 dummy 컬럼이 행렬로 들어가지 않게
    for c in X.columns:
        X[c] = pd.to_numeric(X[c], errors='coerce')
    X['const'] = 1.0
    y = df[y_col].values
    Xv = X.values.astype(float)
    # 결측 행 제외
    msk = ~np.isnan(Xv).any(axis=1)
    Xv = Xv[msk]; y = y[msk]
    beta, *_ = np.linalg.lstsq(Xv, y, rcond=None)
    yhat = Xv @ beta
    r2 = 1 - ((y-yhat)**2).sum() / ((y-y.mean())**2).sum()
    return {'beta': beta, 'cols': X.columns.tolist(), 'r2': r2, 'n': len(y)}

# Model A: Δoc_z ~ Δamp_z  (no FE)
m_base = ols(fe_df, 'd_oc_z', ['d_amp_z'])
print(f'\n[A] Δoc ~ Δamp (no FE): R²={m_base["r2"]:.3f}, β_amp={m_base["beta"][0]:.3f}, N={m_base["n"]}')

# Model B: + 분야 FE
fe_df_b = fe_df.copy()
flds_unique = sorted(fe_df_b['fld_nm'].unique())
for f in flds_unique[1:]:
    fe_df_b[f'fld_{f}'] = (fe_df_b['fld_nm']==f).astype(float)
fld_dummies = [c for c in fe_df_b.columns if c.startswith('fld_') and c != 'fld_nm']
m_fld = ols(fe_df_b, 'd_oc_z', ['d_amp_z'] + fld_dummies)
print(f'[B] +분야 FE: R²={m_fld["r2"]:.3f}, β_amp={m_fld["beta"][0]:.3f}, N={m_fld["n"]}')

# Model C: + 원형 비중 (몇 개만 — A1_chooyeon, A2_sub01, A2_sub05, A0_personnel, direct_invest로 묶기)
risk_archs = ['A1_chooyeon', 'A2_sub01', 'A2_sub05', 'A0_personnel']
fe_df_c = fe_df_b.copy()
# 원형 비중 × Δamp 상호작용
for a in risk_archs:
    if a in fe_df_c.columns:
        fe_df_c[f'{a}_x_amp'] = fe_df_c[a] * fe_df_c['d_amp_z']
ix_cols = [f'{a}_x_amp' for a in risk_archs if f'{a}_x_amp' in fe_df_c.columns]
m_c = ols(fe_df_c, 'd_oc_z', ['d_amp_z'] + fld_dummies + ix_cols)
print(f'[C] +분야 FE + 원형×Δamp 상호작용: R²={m_c["r2"]:.3f}, β_amp={m_c["beta"][0]:.3f}, N={m_c["n"]}')
for i, col in enumerate(m_c['cols']):
    if 'x_amp' in col:
        print(f'    {col}: β={m_c["beta"][i]:.3f}')

# R² 변화량
print(f'\n  → 분야 FE → +원형 ΔR² = {m_c["r2"]-m_fld["r2"]:.4f}')
print(f'  → 분야 FE만 ΔR² (vs base) = {m_fld["r2"]-m_base["r2"]:.4f}')

decomp = pd.DataFrame([
    {'model': 'A_base', 'r2': m_base['r2'], 'n': m_base['n']},
    {'model': 'B_field_FE', 'r2': m_fld['r2'], 'n': m_fld['n']},
    {'model': 'C_field_FE+archetype_x_amp', 'r2': m_c['r2'], 'n': m_c['n']},
])
decomp['delta_r2'] = decomp['r2'].diff().fillna(decomp['r2'])
print('\n=== R² 분해 ===')
print(decomp.round(4).to_string(index=False))
decomp.to_csv(os.path.join(RES_DIR, 'H8_field_archetype_decomp.csv'),
              index=False, encoding='utf-8-sig')

# ============================================================
# Step 3: Q2 — 같은 분야 안 원형별 outcome 결합 비교
# ============================================================
print('\n' + '='*70)
print('Q2: 같은 분야 안에서 원형별 outcome 결합 패턴')
print('='*70)
# 분야별로 활동을 원형 그룹으로 나누고, 각 그룹의 활동들 amp_12m 평균(상수) vs outcome 시계열은 의미 없음
# 대안: 분야×원형 단위의 *시계열*이 필요하지만 활동 단위 amp_12m은 1점 (연도 평균)
# 따라서 monthly_exec를 다시 분야×원형×연도로 집계해서 amp_12m 시계열 만들어야 함

con = duckdb.connect(DB, read_only=True)
print('  분야×원형 monthly_exec 시계열 산출 중...')
PURE_ACCT = """(
    ACTV_NM ILIKE '%전출금%' OR ACTV_NM ILIKE '%타계정%' OR ACTV_NM ILIKE '%여유자금%'
 OR ACTV_NM ILIKE '%국고예탁%' OR ACTV_NM ILIKE '%기금예탁%' OR ACTV_NM ILIKE '%국고예치%'
 OR ACTV_NM ILIKE '%회계간거래%' OR ACTV_NM ILIKE '%회계간전출%'
 OR ACTV_NM ILIKE '%회계기금간%' OR ACTV_NM ILIKE '%여유자금운용%'
)"""

# 분야×활동 단위 monthly_exec ↔ 활동 archetype 매핑
me = con.execute(f"""
    SELECT FLD_NM, OFFC_NM, PGM_NM, ACTV_NM, FSCL_YY AS year, EXE_M AS month,
           SUM(EP_AMT) AS amt
    FROM monthly_exec
    WHERE EXE_M BETWEEN 1 AND 12
      AND FSCL_YY BETWEEN 2015 AND 2025
      AND NOT {PURE_ACCT}
    GROUP BY 1,2,3,4,5,6
""").fetchdf()
con.close()
me = me.merge(df[key_cols+['archetype']], on=key_cols, how='inner')
print(f'  joined monthly rows = {len(me):,}')

# archetype을 출연/직접/평탄으로 그룹핑
def arch_group(a):
    if a == 'A1_chooyeon': return 'chooyeon'
    if a == 'A0_personnel': return 'personnel'
    if a in ('A2_sub01','A2_sub04'): return 'direct_invest'  # sub01 12월잔금 + sub04 Q4
    if a == 'A2_sub05': return 'extreme_gaming'
    return 'normal'
me['arch_grp'] = me['archetype'].map(arch_group)

# 각 분야×원형그룹×연도 monthly amp_12m
from scipy import fft as scfft
records = []
for (fld, grp, yr), g in me.groupby(['FLD_NM','arch_grp','year']):
    arr = np.zeros(12)
    for _, r in g.iterrows():
        arr[int(r['month'])-1] += r['amt']
    if arr.sum() <= 0: continue
    yf = scfft.fft(arr - arr.mean())
    amp_12 = abs(yf[1]) * 2 / 12 / (arr.sum()/12 + 1e-9)
    records.append({'fld_nm':fld, 'arch_grp':grp, 'year':int(yr), 'amp_12m':amp_12})
amp_df = pd.DataFrame(records)
print(f'  분야×원형×연도 amp_12m: {len(amp_df)} cells')

# 분야×원형그룹별 amp 시계열 vs outcome 시계열 차분 상관
results = []
for (fld, grp), g in amp_df.groupby(['fld_nm','arch_grp']):
    if fld not in OUTCOME_MAP: continue
    oc_m = OUTCOME_MAP[fld]
    amp_ts = g.set_index('year')['amp_12m'].sort_index()
    if len(amp_ts) < 4: continue
    oc_ts = wide[wide['fld_nm']==fld].set_index('year')[oc_m].dropna()
    common = amp_ts.index.intersection(oc_ts.index)
    if len(common) < 4: continue
    d_amp = amp_ts.loc[common].diff().dropna()
    d_oc  = oc_ts.loc[common].diff().dropna()
    ci = d_amp.index.intersection(d_oc.index)
    if len(ci) < 3: continue
    r_lvl = float(amp_ts.loc[common].corr(oc_ts.loc[common]))
    r_dif = float(d_amp[ci].corr(d_oc[ci]))
    results.append({
        'fld': fld, 'arch_grp': grp, 'outcome': oc_m,
        'n_year': len(common),
        'amp_mean': float(amp_ts.mean()),
        'corr_levels': r_lvl, 'corr_diff': r_dif,
    })
arch_corr = pd.DataFrame(results)
arch_corr['fld_arch'] = arch_corr['fld'] + ' / ' + arch_corr['arch_grp']
print('\n  분야×원형그룹 outcome 차분 상관:')
print(arch_corr.sort_values(['fld','arch_grp']).round(3).to_string(index=False))
arch_corr.to_csv(os.path.join(RES_DIR, 'H8_archetype_outcome.csv'),
                 index=False, encoding='utf-8-sig')

# 같은 분야 안에서 부호 차이 발견
print('\n  === 같은 분야 안 원형별 부호 차이 (회계 cycle 가설 기각 후보) ===')
for fld in arch_corr['fld'].unique():
    sub_a = arch_corr[arch_corr['fld']==fld]
    if len(sub_a) < 2: continue
    diff = sub_a['corr_diff'].max() - sub_a['corr_diff'].min()
    if diff > 0.3:  # 의미있는 차이
        print(f'    [{fld}] amp_grp 부호 폭 = {diff:.2f}')
        for _, r in sub_a.iterrows():
            print(f'        {r["arch_grp"]:18s}  N={r["n_year"]:>2d}  corr_diff={r["corr_diff"]:+.3f}')

# ============================================================
# Step 4: Figures
# ============================================================
fig, axes = plt.subplots(1, 2, figsize=(16, 7))

# Q1: R² 분해
ax = axes[0]
xx = np.arange(len(decomp))
ax.bar(xx, decomp['r2'], color=['#bbbbbb','#5475a8','#a85454'], alpha=0.85)
ax.set_xticks(xx); ax.set_xticklabels(decomp['model'], rotation=12)
ax.set_ylabel('R²')
ax.set_title(f'Q1: 분야 FE → +원형 ΔR² = {m_c["r2"]-m_fld["r2"]:+.3f}\n'
             '(분야 라벨이 다 설명 vs 사업 원형이 추가 설명)')
ax.grid(alpha=0.3, axis='y')
for i, r in enumerate(decomp['r2']):
    ax.annotate(f'{r:.3f}', (xx[i], r), xytext=(0,5), textcoords='offset points', ha='center')

# Q2: 분야×원형그룹 corr_diff
ax = axes[1]
piv = arch_corr.pivot_table(index='fld', columns='arch_grp', values='corr_diff')
sns.heatmap(piv, annot=True, fmt='.2f', cmap='RdBu_r', center=0, ax=ax,
            cbar_kws={'label':'corr (Δamp ~ Δoutcome)'})
ax.set_title('Q2: 같은 분야 안 원형그룹별 outcome 결합 — 부호가 다르면 회계 cycle 가설 기각')
plt.tight_layout()
fig.savefig(os.path.join(OUT_DIR, 'H8_within_field_panel.png'), dpi=130, bbox_inches='tight')
plt.close()

print('\n=== 그림 ===')
for f in sorted(os.listdir(OUT_DIR)): print(f'  {f}')
print('\n완료.')
