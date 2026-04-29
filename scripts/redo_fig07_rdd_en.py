"""Figure 7 (h22_rdd_monthly, h22_rdd_yearly) — English label version.

Copied from scripts/redo_fig07_rdd.py; changes:
  - Output path -> paper/figures_en/_preview/
  - All Korean labels -> English
"""
import os, sys, io, warnings
import numpy as np
import pandas as pd
import duckdb
import matplotlib.pyplot as plt
import matplotlib as mpl
from PIL import Image

warnings.filterwarnings('ignore')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

plt.rcParams.update({
    'font.size': 11, 'axes.titlesize': 12, 'axes.labelsize': 11,
    'xtick.labelsize': 10, 'ytick.labelsize': 10,
    'legend.fontsize': 10,
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
PREVIEW = os.path.join(ROOT, 'paper', 'figures_en', '_preview')
os.makedirs(PREVIEW, exist_ok=True)

DAYS = {1:31, 2:28, 3:31, 4:30, 5:31, 6:30,
        7:31, 8:31, 9:30, 10:31, 11:30, 12:31}
LM_MULT = 5.0

DPI = 200
MAX = 1900

def save_resize(fig, fname):
    out = os.path.join(PREVIEW, fname)
    fig.savefig(out, dpi=DPI, bbox_inches='tight')
    plt.close(fig)
    img = Image.open(out)
    w, h = img.size
    if max(w, h) > MAX:
        s = MAX / max(w, h)
        ns = (int(w * s), int(h * s))
        img = img.resize(ns, Image.LANCZOS)
        img.save(out, optimize=True)
        print(f'  {fname:30s} {w}x{h} -> {ns[0]}x{ns[1]}')
    else:
        print(f'  {fname:30s} {w}x{h}')

con = duckdb.connect(DB, read_only=True)
df_raw = con.execute("""
    SELECT FSCL_YY AS year, EXE_M AS month, ACTV_CD,
           SUM(EP_AMT) AS ep_amt
    FROM monthly_exec
    WHERE FSCL_YY BETWEEN 2015 AND 2025
      AND EXE_M BETWEEN 1 AND 12
      AND EP_AMT > 0
    GROUP BY FSCL_YY, EXE_M, ACTV_CD
""").df()
con.close()
print(f'raw rows: {len(df_raw):,}  activities: {df_raw["ACTV_CD"].nunique():,}')

df_raw['days'] = df_raw['month'].map(DAYS)
df_raw['daily_ep'] = df_raw['ep_amt'] / df_raw['days']
df_raw['log_daily'] = np.log(df_raw['daily_ep'])

agg_all = (df_raw.groupby(['year', 'month'])
           .agg(mean_daily=('daily_ep', 'mean'))
           .reset_index())

pivot = (df_raw[df_raw['month'].isin([11, 12])]
         .pivot_table(index=['year', 'ACTV_CD'], columns='month',
                      values='log_daily').dropna())
pivot.columns = ['nov', 'dec']
pivot['jump'] = pivot['dec'] - pivot['nov']
yr_jump = pivot.groupby('year')['jump'].median().reset_index()

estimates = pd.read_csv(os.path.join(RES, 'H22_rdd_estimates.csv'))
beta_total = float(estimates[estimates['bw'] == 1]['beta'].values[0])
mult_total = float(estimates[estimates['bw'] == 1]['mult'].values[0])

# ── (A) Monthly average daily spending — viridis cmap + colorbar for year
fig, ax = plt.subplots(figsize=(6.3, 3.7))
yr_list = sorted(agg_all['year'].unique())
norm = mpl.colors.Normalize(vmin=min(yr_list), vmax=max(yr_list))
cmap = plt.cm.viridis
for yr in yr_list:
    g = agg_all[agg_all['year'] == yr].sort_values('month')
    ax.plot(g['month'], g['mean_daily'] / 1e9,
            color=cmap(norm(yr)), lw=1.1, alpha=0.75)
avg_m = agg_all.groupby('month')['mean_daily'].mean()
ax.plot(avg_m.index, avg_m.values / 1e9,
        'k-', lw=2.6, zorder=5, label='11-year average')
ax.axvline(11.5, color='crimson', lw=1.8, ls='--', alpha=0.85,
           label='December cutoff')
ax.axvspan(11, 12.5, alpha=0.08, color='crimson')
ax.set_xlabel('Month')
ax.set_ylabel('Activity avg. daily spending (billion KRW)')
ax.set_xticks(list(range(1, 13)))
# English month abbreviations
MONTH_LABELS = ['Jan','Feb','Mar','Apr','May','Jun',
                'Jul','Aug','Sep','Oct','Nov','Dec']
ax.set_xticklabels(MONTH_LABELS)
ax.legend(loc='upper left', framealpha=0.9)
ax.grid(alpha=0.3)
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax, pad=0.015, shrink=0.85,
                    ticks=[2015, 2018, 2021, 2025])
cbar.set_label('Fiscal Year', fontsize=10)
cbar.ax.tick_params(labelsize=9)
plt.tight_layout()
save_resize(fig, 'h22_rdd_monthly.png')

# ── (B) Yearly November→December jump
fig, ax = plt.subplots(figsize=(6.3, 3.4))
ax.bar(yr_jump['year'], yr_jump['jump'],
       color=['crimson' if v > 0 else 'steelblue'
              for v in yr_jump['jump']],
       alpha=0.78, width=0.65)
ax.axhline(0, color='black', lw=0.8)
ax.axhline(beta_total, color='darkorange', lw=1.8, ls='--',
           label=f'Overall β = {beta_total:.2f}  ({mult_total:.2f}x)')
ax.axhline(np.log(LM_MULT), color='purple', lw=1.5, ls=':',
           label=f'L-M 5x reference (β≈{np.log(LM_MULT):.2f})')
ax.set_xlabel('Fiscal Year')
ax.set_ylabel('Log jump\n(December − November, activity median)')
ax.set_xticks(yr_list)
ax.set_xticklabels([str(y)[2:] for y in yr_list])
ax.legend(loc='upper right')
ax.grid(alpha=0.3)
plt.tight_layout()
save_resize(fig, 'h22_rdd_yearly.png')

print('Done.')
