"""그림 10 (h14_quadrant) — 부처×outcome 4분면 (전체 51개 부처 + 필터 필드 라벨).

source: scripts/h14_v2_replaced.py 의 Figure 2 (4분면 위험 분류도)
A4 본문 폭 6.3 inch 1:1, figsize=(6.3, 5.0), dpi=200
"""
import os, sys, io, warnings
import numpy as np
import pandas as pd
import duckdb
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.patches as mpatches
from scipy.stats import pearsonr
from PIL import Image

warnings.filterwarnings('ignore')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

plt.rcParams.update({
    'font.size': 10, 'axes.titlesize': 11, 'axes.labelsize': 10,
    'xtick.labelsize': 9, 'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'mathtext.default': 'regular',
    'axes.unicode_minus': False,
})
for fname in ['Malgun Gothic', 'Arial Unicode MS', 'NanumGothic']:
    if any(fname.lower() in fn.name.lower()
           for fn in mpl.font_manager.fontManager.ttflist):
        mpl.rcParams['font.family'] = [fname, 'Times New Roman', 'DejaVu Sans']
        break

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, 'data', 'warehouse.duckdb')
RES = os.path.join(ROOT, 'data', 'results')
PREVIEW = os.path.join(ROOT, 'paper', 'figures', '_preview')
os.makedirs(PREVIEW, exist_ok=True)

H5_CSV2 = os.path.join(RES, 'H5_ministry_exposure_11y.csv')
H5_CSV = os.path.join(RES, 'H5_ministry_exposure.csv')
H3_CSV = os.path.join(RES, 'H3_activity_embedding_11y.csv')

if os.path.exists(H5_CSV2):
    expo = pd.read_csv(H5_CSV2, encoding='utf-8-sig')
else:
    expo = pd.read_csv(H5_CSV, encoding='utf-8-sig')
emb = pd.read_csv(H3_CSV, encoding='utf-8-sig')
print(f'expo: {len(expo)}, emb: {len(emb)}')

OUTCOME_MAP = {
    '사회복지': 'wealth_gini', '보건': 'life_expectancy',
    '과학기술': 'patent_apps_total',
    '산업·중소기업및에너지': 'industry_production_index',
    '문화및관광': 'foreign_tourists_total',
    '교육': 'private_edu_hours', '국토및지역개발': 'housing_supply',
    '일반·지방행정': 'fiscal_indep_natl', '농림수산': 'farm_income',
    '교통및물류': 'traffic_deaths', '환경': 'ghg_total',
    '통신': 'broadband_per_100',
}

con = duckdb.connect(DB, read_only=True)
metric_list = list(OUTCOME_MAP.values()) + ['amp_12m_norm']
panel = con.execute(f"""
    SELECT fld_nm, year, metric_code, value
    FROM indicator_panel
    WHERE metric_code IN ({','.join("'" + m + "'" for m in metric_list)})
""").fetchdf()
con.close()

wide = panel.pivot_table(index=['fld_nm', 'year'],
                         columns='metric_code', values='value').reset_index()
fld_amp = wide.pivot_table(index='year', columns='fld_nm', values='amp_12m_norm')

ofc_fld = pd.crosstab(emb['OFFC_NM'], emb['FLD_NM'], normalize='index')
ofc_size = emb.groupby('OFFC_NM').size()

MIN_N = 5
EXPO_THRESH = 0.3
ofc_results = []
for ofc, w in ofc_fld.iterrows():
    if ofc_size.get(ofc, 0) < 3:
        continue
    amp_ts = (fld_amp.reindex(columns=w.index) * w).sum(axis=1, min_count=1).dropna()
    for fld, oc_metric in OUTCOME_MAP.items():
        if oc_metric not in wide.columns:
            continue
        fld_w = float(w.get(fld, 0.0))
        if fld_w < 0.05:
            continue
        oc_ts = (wide[wide['fld_nm'] == fld]
                 .set_index('year')[oc_metric].dropna())
        common = amp_ts.index.intersection(oc_ts.index)
        if len(common) < MIN_N:
            continue
        d_amp = amp_ts.loc[common].diff().dropna()
        d_oc = oc_ts.loc[common].diff().dropna()
        ci = d_amp.index.intersection(d_oc.index)
        if len(ci) < MIN_N - 1:
            continue
        r_dif, _ = pearsonr(d_amp.loc[ci], d_oc.loc[ci])
        ofc_results.append({
            'OFFC_NM': ofc, 'fld_outcome': fld,
            'fld_weight': fld_w, 'n_year': len(common),
            'corr_diff': float(r_dif),
        })
ofc_corr = pd.DataFrame(ofc_results)

def w_mean(g):
    w = g['fld_weight']
    return float(np.average(g['corr_diff'], weights=w)) if w.sum() > 0 else np.nan
ofc_agg = (ofc_corr.groupby('OFFC_NM')
           .apply(lambda g: pd.Series({
               'w_corr_diff': w_mean(g),
               'n_pairs': len(g),
               'min_n_year': g['n_year'].min(),
           }))
           .reset_index())

expo_cols = ['OFFC_NM', 'exposure_score']
if 'co_cluster' in expo.columns:
    expo_cols.append('co_cluster')
if 'n_actv' in expo.columns:
    expo_cols.append('n_actv')
merged = ofc_agg.merge(expo[expo_cols], on='OFFC_NM', how='inner')
merged['exposure_score'] = merged['exposure_score'].astype(float)
merged['w_corr_diff'] = merged['w_corr_diff'].astype(float)
filt = merged[
    (merged['exposure_score'] >= EXPO_THRESH) &
    (merged['min_n_year'] >= MIN_N)
].copy()
print(f'전체: {len(merged)}, 필터: {len(filt)}')

# 4분면 분류
def quadrant(row):
    hi_exp = row['exposure_score'] >= EXPO_THRESH
    pos_cor = row['w_corr_diff'] >= 0
    if hi_exp and pos_cor: return 'Q2'
    if hi_exp and not pos_cor: return 'Q1'
    if not hi_exp and pos_cor: return 'Q4'
    return 'Q3'
filt['quadrant'] = filt.apply(quadrant, axis=1)

# ── Figure
fig, ax = plt.subplots(figsize=(9.84, 5.2))

# 4분면 배경
x1 = max(merged['exposure_score'].max() + 0.05, 0.85)
y0_lim = min(merged['w_corr_diff'].min() - 0.1, -0.6)
y1_lim = max(merged['w_corr_diff'].max() + 0.1, 0.6)

ax.fill_between([EXPO_THRESH, x1], 0, y1_lim,
                color='#ffe0e0', alpha=0.45, zorder=0)   # Q2 빨강
ax.fill_between([EXPO_THRESH, x1], y0_lim, 0,
                color='#fff3e0', alpha=0.45, zorder=0)   # Q1 주황
ax.fill_between([0, EXPO_THRESH], 0, y1_lim,
                color='#e8f4f8', alpha=0.30, zorder=0)   # Q4 파랑
ax.fill_between([0, EXPO_THRESH], y0_lim, 0,
                color='#e8f8ee', alpha=0.30, zorder=0)   # Q3 녹색

ax.axhline(0, color='#666', lw=0.9, zorder=1)
ax.axvline(EXPO_THRESH, color='#666', lw=0.9, zorder=1)

# 배경 부처 (필터 외, 회색)
bkg = merged[~merged['OFFC_NM'].isin(filt['OFFC_NM'])]
ax.scatter(bkg['exposure_score'], bkg['w_corr_diff'],
           s=22, color='#bbbbbb', alpha=0.55, zorder=2,
           label=f'기준 미달 ({len(bkg)})')

# 필터 부처 (4분면 색상)
Q_COLOR = {'Q1': '#e07b54', 'Q2': '#e63946',
           'Q3': '#2c7873', 'Q4': '#457b9d'}
for q, grp in filt.groupby('quadrant'):
    ax.scatter(grp['exposure_score'], grp['w_corr_diff'],
               s=85, color=Q_COLOR.get(q, '#888'),
               edgecolor='black', linewidth=0.6,
               alpha=0.92, zorder=4, label=f'{q} (n={len(grp)})')

# 부처명 라벨 — filt 강조 + bkg 중 exposure 상위 5개 (분포 가시화)
texts = []
bkg_top = bkg.nlargest(5, 'exposure_score')
try:
    from adjustText import adjust_text
    # filt: 색상 굵게
    for _, row in filt.iterrows():
        nm = str(row['OFFC_NM'])
        if len(nm) > 16:
            nm = nm[:15] + '…'
        weight = 'bold' if row['quadrant'] == 'Q2' else 'normal'
        t = ax.text(row['exposure_score'], row['w_corr_diff'], nm,
                    fontsize=8.5, alpha=0.95, fontweight=weight,
                    color='#222')
        texts.append(t)
    # bkg 상위: 옅은 회색 작게
    for _, row in bkg_top.iterrows():
        nm = str(row['OFFC_NM'])
        if len(nm) > 14:
            nm = nm[:13] + '…'
        t = ax.text(row['exposure_score'], row['w_corr_diff'], nm,
                    fontsize=7.5, alpha=0.7, color='#666')
        texts.append(t)
    adjust_text(texts, ax=ax,
                arrowprops=dict(arrowstyle='-', color='#aaa', lw=0.35),
                expand_points=(1.4, 1.4),
                expand_text=(1.3, 1.3))
except ImportError:
    for _, row in filt.iterrows():
        nm = str(row['OFFC_NM'])
        if len(nm) > 14:
            nm = nm[:13] + '…'
        ax.annotate(nm, (row['exposure_score'], row['w_corr_diff']),
                    xytext=(4, 4), textcoords='offset points',
                    fontsize=8.5, alpha=0.95)
    for _, row in bkg_top.iterrows():
        nm = str(row['OFFC_NM'])
        if len(nm) > 14:
            nm = nm[:13] + '…'
        ax.annotate(nm, (row['exposure_score'], row['w_corr_diff']),
                    xytext=(3, 3), textcoords='offset points',
                    fontsize=7.5, alpha=0.7, color='#666')

# 4분면 텍스트 라벨
qkw = dict(fontsize=9, alpha=0.6, ha='center', va='center')
ax.text((EXPO_THRESH + x1) / 2, y1_lim * 0.85,
        'Q2 위험\n(점검 필요)', color='#c0392b', **qkw)
ax.text((EXPO_THRESH + x1) / 2, y0_lim * 0.85,
        'Q1 자동분배', color='#c05000', **qkw)
ax.text(EXPO_THRESH * 0.5, y1_lim * 0.85,
        'Q4 안전 (양 상관)', color='#1a6fa0', **qkw)
ax.text(EXPO_THRESH * 0.5, y0_lim * 0.85,
        'Q3 안전 (음 상관)', color='#1a7a4a', **qkw)

ax.set_xlim(0, x1)
ax.set_ylim(y0_lim, y1_lim)
ax.set_xlabel('굿하트 노출 점수 (H5 exposure_score)')
ax.set_ylabel('부처 가중 outcome 차분 상관 (w_corr_diff)')
ax.legend(loc='lower right', fontsize=8.5, ncol=1)
ax.grid(alpha=0.2)

plt.tight_layout()

DPI = 200
MAX = 1900
out = os.path.join(PREVIEW, 'h14_quadrant.png')
fig.savefig(out, dpi=DPI, bbox_inches='tight')
plt.close()
img = Image.open(out)
w, h = img.size
if max(w, h) > MAX:
    s = MAX / max(w, h)
    ns = (int(w * s), int(h * s))
    img = img.resize(ns, Image.LANCZOS)
    img.save(out, optimize=True)
    print(f'preview: {w}x{h} -> {ns[0]}x{ns[1]}')
else:
    print(f'preview: {w}x{h}')
