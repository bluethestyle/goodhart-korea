"""H10 figure 재생성 — 캐시된 CSV 사용 (CPI raw data 불요).

paper/figures/h10_cpi_control.png을 vertical stack(2행 1열)으로 다시 그림.
"""
import os, sys
try: sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
except AttributeError: pass

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import scienceplots
import seaborn as sns

plt.style.use(['science', 'no-latex', 'grid'])
plt.rcParams.update({
    'font.size': 20, 'axes.titlesize': 22, 'axes.labelsize': 20,
    'xtick.labelsize': 17, 'ytick.labelsize': 17,
    'legend.fontsize': 17, 'legend.title_fontsize': 17,
    'figure.titlesize': 23, 'lines.linewidth': 2.5, 'lines.markersize': 12,
    'axes.linewidth': 1.2, 'grid.alpha': 0.3,
    'mathtext.fontset': 'stix', 'mathtext.default': 'regular',
    'axes.unicode_minus': False,
})
for fname in ['Arial Unicode MS', 'Malgun Gothic', 'NanumGothic']:
    if any(fname.lower() in fn.name.lower() for fn in mpl.font_manager.fontManager.ttflist):
        mpl.rcParams['font.family'] = [fname, 'Arial Unicode MS', 'Times New Roman', 'DejaVu Sans']
        break
sns.set_palette('Set2')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
df = pd.read_csv(os.path.join(ROOT, 'data', 'results', 'H10_macro_control_corr_v3.csv'))
df = df.dropna(subset=['corr_raw', 'corr_resid_CPI'])

# 2행 1열 vertical stack
fig, axes = plt.subplots(2, 1, figsize=(11, 13))

# 위 panel: scatter raw vs CPI-residual
ax1 = axes[0]
ax1.plot([-1, 1], [-1, 1], '--', color='gray', alpha=0.6, label='identity (변화 없음)')
sc = ax1.scatter(df['corr_raw'], df['corr_resid_CPI'], s=140, alpha=0.75,
                  edgecolor='white', linewidth=1.5, color='#5475a8')
for _, row in df.iterrows():
    label = row['fld']
    ax1.annotate(label, (row['corr_raw'], row['corr_resid_CPI']),
                  xytext=(7, 7), textcoords='offset points', alpha=0.85)
ax1.axhline(0, color='gray', linewidth=0.7, linestyle=':')
ax1.axvline(0, color='gray', linewidth=0.7, linestyle=':')
n_sign = (df['sign_change'] == True).sum()
ax1.set_xlabel('raw 상관 (H6, CPI 통제 전)')
ax1.set_ylabel('CPI-residual 상관 (H10)')
ax1.set_title(f'CPI 통제 전후 상관 비교 — 부호 반전 {n_sign}/{len(df)}', fontweight='bold')
ax1.legend(loc='best', frameon=True)
ax1.set_xlim(-1.05, 1.05); ax1.set_ylim(-1.05, 1.05)

# 아래 panel: 분야별 raw vs CPI-residual bar chart
ax2 = axes[1]
df_sorted = df.sort_values('corr_raw').reset_index(drop=True)
y = np.arange(len(df_sorted))
ax2.barh(y - 0.2, df_sorted['corr_raw'], height=0.4,
         label='raw 상관', color='#5475a8', alpha=0.85)
ax2.barh(y + 0.2, df_sorted['corr_resid_CPI'], height=0.4,
         label='CPI-residual 상관', color='#a85454', alpha=0.85)
ax2.set_yticks(y)
ax2.set_yticklabels(df_sorted['fld'])
ax2.axvline(0, color='gray', linewidth=0.7)
ax2.set_xlabel('상관계수')
ax2.set_title('분야별 raw vs CPI-residual 상관', fontweight='bold')
ax2.legend(loc='best', frameon=True)
ax2.grid(axis='x', alpha=0.3)

fig.suptitle('CPI 외생 통제 — 14/14 분야 부호 유지, 게임화 신호의 자연 cycle 가설 기각',
             fontweight='bold', y=1.00)
plt.tight_layout()
out = os.path.join(ROOT, 'paper', 'figures', 'h10_cpi_control.png')
plt.savefig(out, dpi=200, bbox_inches='tight')
plt.close()

from PIL import Image
im = Image.open(out)
print(f'  → {out}: {im.size[0]}x{im.size[1]} px')
print(f'  effective pt at A4 (1260px width): {20 * 1260 / im.size[0]:.1f}pt')
