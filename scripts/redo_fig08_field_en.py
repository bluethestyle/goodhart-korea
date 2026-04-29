"""Figure 8 (h22_rdd_field) — English label version.

Copied from scripts/redo_fig08_field.py; changes:
  - Output path -> paper/figures_en/_preview/
  - All Korean labels -> English (field names, axis labels, legend)
"""
import os, sys, io, warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.patches as mpatches
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
RES = os.path.join(ROOT, 'data', 'results')
PREVIEW = os.path.join(ROOT, 'paper', 'figures_en', '_preview')
os.makedirs(PREVIEW, exist_ok=True)

LM_MULT = 5.0

# English short field names for y-axis ticks
SHORT_EN = {
    '산업·중소기업및에너지': 'Industry/SMEs',
    '국토및지역개발': 'Land Dev.',
    '공공질서및안전': 'Public Order',
    '문화및관광': 'Culture & Tourism',
    '일반·지방행정': 'Gen. Admin.',
    '교통및물류': 'Transport',
    '통일·외교': 'Unif./Diplomacy',
    '과학기술': 'S&T',
    '사회복지': 'Welfare',
    '보건': 'Health',
    '교육': 'Education',
    '농림수산식품': 'Agriculture',
    '환경': 'Environment',
    '통신': 'ICT',
    '국방': 'Defense',
    '예비비': 'Reserve',
}

df = pd.read_csv(os.path.join(RES, 'H22_field_rdd.csv'))
# bw=1 only, fields only (exclude cluster archetypes)
df = df[df['bw'] == 1].copy()
cluster_kw = ['인건비형', '자산취득형', '출연금형', '정상사업']
df = df[~df['label'].isin(cluster_kw)].reset_index(drop=True)
# Remove duplicate '외교·통일' (small sample; keep '통일·외교')
df = df[df['label'] != '외교·통일'].reset_index(drop=True)
df['label_short'] = df['label'].map(lambda x: SHORT_EN.get(x, x))
df = df.sort_values('beta', ascending=True).reset_index(drop=True)
print(df[['label', 'beta', 'pval', 'mult']].to_string())

# Overall RDD beta
estimates = pd.read_csv(os.path.join(RES, 'H22_rdd_estimates.csv'))
beta_total = float(estimates[estimates['bw'] == 1]['beta'].values[0])
mult_total = float(estimates[estimates['bw'] == 1]['mult'].values[0])

fig, ax = plt.subplots(figsize=(9.84, 5.0))

ys = np.arange(len(df))
colors = ['#a85454' if p < 0.05 else '#aaaaaa' for p in df['pval']]
ax.barh(ys, df['beta'], xerr=1.96 * df['se'],
        color=colors, alpha=0.82, height=0.6,
        error_kw={'elinewidth': 1.2, 'capsize': 3, 'ecolor': '#444'})

ax.set_yticks(ys)
ax.set_yticklabels(df['label_short'])

ax.axvline(0, color='black', lw=0.8)
ax.axvline(beta_total, color='darkorange', lw=1.6, ls='--',
           label=f'Overall β={beta_total:.2f} ({mult_total:.2f}x)')
ax.axvline(np.log(LM_MULT), color='purple', lw=1.4, ls=':',
           label=f'L-M 5x (β≈{np.log(LM_MULT):.2f})')

# Multiplier labels at bar ends
xmax = max(float((df['beta'] + 1.96 * df['se']).max()), np.log(LM_MULT))
xpad = (xmax - df['beta'].min()) * 0.04
for i, row in df.iterrows():
    end = row['beta'] + 1.96 * row['se']
    ax.text(end + xpad * 0.5, i, f"{row['mult']:.2f}x",
            va='center', ha='left', fontsize=8.5,
            color='#333' if row['pval'] < 0.05 else '#888')

ax.set_xlabel('December jump multiplier (β, log daily spending, 95% CI)')

# Legend — p-value colours + reference lines
sig_patch = mpatches.Patch(color='#a85454', label='p<0.05', alpha=0.82)
ns_patch  = mpatches.Patch(color='#aaaaaa', label='p≥0.05', alpha=0.82)
ax.legend(handles=[sig_patch, ns_patch,
                   plt.Line2D([0], [0], color='darkorange', lw=1.6, ls='--',
                              label=f'Overall β={beta_total:.2f}'),
                   plt.Line2D([0], [0], color='purple', lw=1.4, ls=':',
                              label='L-M 5x')],
          loc='lower right', fontsize=9, ncol=1)

ax.grid(alpha=0.3, axis='x')
ax.set_xlim(min(df['beta'].min() - 0.1, -0.05), xmax + xpad * 6)

plt.tight_layout()

DPI = 200
MAX = 1900
out = os.path.join(PREVIEW, 'h22_rdd_field.png')
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
