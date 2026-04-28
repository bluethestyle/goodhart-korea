"""H10: 한은 거시 통제 후 H6 디커플링 신호 견고성 재검증.

가정: 사회복지 wealth_gini의 -0.77 음 상관이 자연 경제 사이클(CPI) 동조일 수 있다.
방법: outcome 차분에서 CPI 변화율 잔차를 빼고 amp_12m 차분과 상관 → 거시 통제 잔차 상관

비교:
  - raw corr_diff (H6) vs CPI-residual corr_diff (H10)
  - 부호 유지·약화·반전?

산출:
  data/results/H10_macro_control_corr.csv
  data/figs/h10/H10_macro_control_compare.png
"""
import os, sys, io, json, warnings
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
RAW = os.path.join(ROOT, 'data', 'external', 'bok_data')
OUT = os.path.join(ROOT, 'data', 'figs', 'h10')
RES = os.path.join(ROOT, 'data', 'results')
os.makedirs(OUT, exist_ok=True)

KFONT = None
for f in ['Malgun Gothic','Noto Sans CJK KR','AppleGothic']:
    if any(f in fn.name for fn in mpl.font_manager.fontManager.ttflist):
        mpl.rcParams['font.family'] = f
        KFONT = f
        break
mpl.rcParams['axes.unicode_minus'] = False

# ============================================================
# Step 1: CPI 시계열 로드
# ============================================================
print('='*70)
print('Step 1: CPI (901Y009 / 연)')
print('='*70)
d = json.load(open(f'{RAW}/cpi_annual.json', encoding='utf-8'))
rows = d['StatisticSearch']['row']
cpi = pd.DataFrame(rows)
cpi['year'] = pd.to_numeric(cpi['TIME'], errors='coerce').astype('Int64')
cpi['cpi'] = pd.to_numeric(cpi['DATA_VALUE'], errors='coerce')
cpi = cpi[['year','cpi']].dropna().sort_values('year').reset_index(drop=True)
cpi['cpi_pct'] = cpi['cpi'].pct_change() * 100
print(f'  CPI {len(cpi)} years: {cpi["year"].min()} ~ {cpi["year"].max()}')
print(f'  최근 5년 CPI: {cpi.tail(5).to_dict("records")}')

# ============================================================
# Step 2: 분야 outcome + amp_12m + CPI 결합
# ============================================================
con = duckdb.connect(DB, read_only=True)
panel = con.execute("""
    SELECT fld_nm, year, metric_code, value FROM indicator_panel
    WHERE metric_code IN ('amp_12m_norm','wealth_gini','life_expectancy',
                          'rd_total','industry_production_index','tourists_sample',
                          'housing_supply','local_tax_per_capita','private_edu_hours',
                          'farm_income','fishery_income')
""").fetchdf()
con.close()
wide = panel.pivot_table(index=['fld_nm','year'], columns='metric_code',
                         values='value').reset_index()
wide = wide.merge(cpi[['year','cpi','cpi_pct']], on='year', how='left')

OUTCOME_MAP = {
    '사회복지': 'wealth_gini',
    '보건':   'life_expectancy',
    '과학기술': 'rd_total',
    '산업·중소기업및에너지': 'industry_production_index',
    '문화및관광': 'tourists_sample',
    '교육':           'private_edu_hours',
    '국토및지역개발': 'housing_supply',
    '일반·지방행정':   'local_tax_per_capita',
    '농림수산':       'farm_income',
}

# ============================================================
# Step 3: raw vs CPI-residual 차분 상관 비교
# ============================================================
print('\n' + '='*70)
print('Step 3: raw corr_diff vs CPI-residual corr_diff')
print('='*70)
results = []
for fld, oc in OUTCOME_MAP.items():
    sub = wide[wide['fld_nm']==fld].sort_values('year').copy()
    if oc not in sub.columns: continue
    sub = sub[['year','amp_12m_norm', oc, 'cpi','cpi_pct']].dropna(subset=['amp_12m_norm', oc])
    if len(sub) < 5: continue
    sub['d_amp'] = sub['amp_12m_norm'].diff()
    sub['d_oc']  = sub[oc].diff()
    sub['d_cpi'] = sub['cpi_pct'].diff()  # CPI 변화의 변화 (가속도)
    sub = sub.dropna()

    if len(sub) < 4: continue
    # raw corr
    r_raw, p_raw = pearsonr(sub['d_amp'], sub['d_oc'])

    # outcome 차분에서 CPI 변화율 효과 제거 (잔차 회귀)
    # d_oc = α + β·cpi_pct + ε
    if sub['cpi_pct'].std() > 0:
        slope = np.polyfit(sub['cpi_pct'], sub['d_oc'], 1)
        d_oc_resid = sub['d_oc'].values - (slope[0] * sub['cpi_pct'].values + slope[1])
    else:
        d_oc_resid = sub['d_oc'].values

    # amp 차분에서도 cpi 효과 제거
    if sub['cpi_pct'].std() > 0:
        slope2 = np.polyfit(sub['cpi_pct'], sub['d_amp'], 1)
        d_amp_resid = sub['d_amp'].values - (slope2[0] * sub['cpi_pct'].values + slope2[1])
    else:
        d_amp_resid = sub['d_amp'].values

    if len(d_oc_resid) >= 3 and np.std(d_oc_resid) > 0 and np.std(d_amp_resid) > 0:
        r_resid, p_resid = pearsonr(d_amp_resid, d_oc_resid)
    else:
        r_resid, p_resid = np.nan, np.nan

    results.append({
        'fld': fld, 'outcome': oc, 'n': len(sub),
        'corr_raw': r_raw, 'corr_resid_CPI': r_resid,
        'delta': r_resid - r_raw,
        'p_raw': p_raw, 'p_resid': p_resid,
    })

df = pd.DataFrame(results).sort_values('corr_raw')
print(df.round(3).to_string(index=False))

# 부호 유지 / 약화 / 반전 분류
df['sign_change'] = np.sign(df['corr_raw']) != np.sign(df['corr_resid_CPI'])
df['abs_weaken'] = df['corr_resid_CPI'].abs() < df['corr_raw'].abs() * 0.7
print()
print(f'부호 반전: {df["sign_change"].sum()} / {len(df)}')
print(f'30%+ 약화: {df["abs_weaken"].sum()} / {len(df)}')
print(f'  → CPI 통제 후에도 부호 유지 + 강도 70% 이상 유지: {((~df["sign_change"]) & (~df["abs_weaken"])).sum()}개')

df.to_csv(f'{RES}/H10_macro_control_corr.csv', index=False, encoding='utf-8-sig')

# ============================================================
# Figure
# ============================================================
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# A: raw vs resid scatter
ax = axes[0]
ax.scatter(df['corr_raw'], df['corr_resid_CPI'], s=60, c='#5475a8', alpha=0.85)
for _, r in df.iterrows():
    ax.annotate(f'{r["fld"][:8]}', (r['corr_raw'], r['corr_resid_CPI']),
                xytext=(4,4), textcoords='offset points', fontsize=8)
ax.plot([-1,1],[-1,1],'--', color='#888', alpha=0.5, label='identity')
ax.axhline(0, color='#888', lw=0.5); ax.axvline(0, color='#888', lw=0.5)
ax.set_xlabel('raw corr_diff (H6)')
ax.set_ylabel('CPI-residual corr_diff (H10)')
ax.set_title(f'CPI 통제 전후 비교\n부호 반전 {df["sign_change"].sum()}/{len(df)}, '
             f'30%+ 약화 {df["abs_weaken"].sum()}/{len(df)}')
ax.legend()
ax.grid(alpha=0.3)
ax.set_xlim(-1, 1); ax.set_ylim(-1, 1)

# B: 각 분야 raw vs resid bar
ax = axes[1]
df_sorted = df.sort_values('corr_raw')
y = np.arange(len(df_sorted))
ax.barh(y - 0.2, df_sorted['corr_raw'], height=0.4, color='#5475a8', alpha=0.85, label='raw')
ax.barh(y + 0.2, df_sorted['corr_resid_CPI'], height=0.4, color='#a85454', alpha=0.85, label='CPI-residual')
ax.set_yticks(y); ax.set_yticklabels(df_sorted['fld'])
ax.axvline(0, color='#888', lw=0.5)
ax.set_xlabel('corr_diff')
ax.set_title('분야별 corr_diff: raw vs CPI 통제 후')
ax.legend()
ax.grid(alpha=0.3, axis='x')

plt.tight_layout()
fig.savefig(f'{OUT}/H10_macro_control_compare.png', dpi=130, bbox_inches='tight')
plt.close()

print('\n=== 그림 ===')
print(f'  {OUT}/H10_macro_control_compare.png')
print('\n완료.')
