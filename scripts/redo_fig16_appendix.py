"""그림 16 (h22_rdd_appendix) — 사업원형(archetype)별 12월 점프 forest plot.

원본 source: scripts/h22_rdd_yearend.py 의 panel D
(분야별 forest는 그림 8 [h22_rdd_field]에 단독으로 별도 작업됨 — 중복 회피)

A4 본문 폭 6.3 inch 1:1, figsize=(6.3, 3.4), dpi=200
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
RES = os.path.join(ROOT, 'data', 'results')
PREVIEW = os.path.join(ROOT, 'paper', 'figures', '_preview')
os.makedirs(PREVIEW, exist_ok=True)

LM_MULT = 5.0

df = pd.read_csv(os.path.join(RES, 'H22_field_rdd.csv'))
# 클러스터(archetype) 행만
arch_kw = ['인건비형', '자산취득형', '출연금형', '정상사업']
df = df[(df['bw'] == 1) & (df['label'].isin(arch_kw))].copy()
df = df.sort_values('beta', ascending=True).reset_index(drop=True)
print(df[['label', 'beta', 'pval', 'mult']].to_string())

estimates = pd.read_csv(os.path.join(RES, 'H22_rdd_estimates.csv'))
beta_total = float(estimates[estimates['bw'] == 1]['beta'].values[0])
mult_total = float(estimates[estimates['bw'] == 1]['mult'].values[0])

fig, ax = plt.subplots(figsize=(6.3, 3.4))

ys = np.arange(len(df))
colors = ['#a85454' if p < 0.05 else '#aaaaaa' for p in df['pval']]
ax.barh(ys, df['beta'], xerr=1.96 * df['se'],
        color=colors, alpha=0.85, height=0.55,
        error_kw={'elinewidth': 1.4, 'capsize': 4, 'ecolor': '#444'})

ax.set_yticks(ys)
ax.set_yticklabels(df['label'])

ax.axvline(0, color='black', lw=0.8)
ax.axvline(beta_total, color='darkorange', lw=1.6, ls='--',
           label=f'한국 전체 β={beta_total:.2f} ({mult_total:.2f}x)')
ax.axvline(np.log(LM_MULT), color='purple', lw=1.4, ls=':',
           label=f'L-M 5x (β≈{np.log(LM_MULT):.2f})')

# mult 라벨 (막대 끝)
xmax = max(float((df['beta'] + 1.96 * df['se']).max()), np.log(LM_MULT))
xpad = (xmax - df['beta'].min()) * 0.04
for i, row in df.iterrows():
    end = row['beta'] + 1.96 * row['se']
    ax.text(end + xpad * 0.5, i, f"{row['mult']:.2f}x",
            va='center', ha='left', fontsize=10,
            color='#222' if row['pval'] < 0.05 else '#888',
            fontweight='bold' if row['pval'] < 0.05 else 'normal')

ax.set_xlabel('β (log 일집행액 12월 점프, 95% CI)')

sig_patch = mpatches.Patch(color='#a85454', label='p<0.05', alpha=0.85)
ns_patch = mpatches.Patch(color='#aaaaaa', label='p≥0.05', alpha=0.85)
ax.legend(handles=[sig_patch, ns_patch,
                   plt.Line2D([0], [0], color='darkorange', lw=1.6, ls='--',
                              label=f'전체 β={beta_total:.2f}'),
                   plt.Line2D([0], [0], color='purple', lw=1.4, ls=':',
                              label=f'L-M 5x')],
          loc='lower right', fontsize=9, ncol=1)

ax.grid(alpha=0.3, axis='x')
ax.set_xlim(min(df['beta'].min() - 0.1, -0.05), xmax + xpad * 6)

plt.tight_layout()

DPI = 200
MAX = 1900
out = os.path.join(PREVIEW, 'h22_rdd_appendix.png')
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
