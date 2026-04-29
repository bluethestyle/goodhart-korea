"""그림 6 (h8_panel) — 원본 디자인 (3 모델 R² 막대 + ΔR² + β 박스) 유지 + A4 1:1.

source: scripts/h8_v3_replaced.py 의 Figure 1
"""
import os, sys, io, warnings
import numpy as np
import pandas as pd
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
RES = os.path.join(ROOT, 'data', 'results')
PREVIEW = os.path.join(ROOT, 'paper', 'figures', '_preview')
os.makedirs(PREVIEW, exist_ok=True)

decomp = pd.read_csv(os.path.join(RES, 'H8_field_archetype_decomp_v3.csv'))
print(decomp.to_string())
dr2_arch = float(
    decomp.loc[decomp['model'] == 'C_field_FE+archetype_xamp', 'delta_r2'].values[0])

# 원형별 β (source script 실행 결과 — paper/figures/h8_panel.png 박스에 있던 값)
beta_labels = [
    'A0_personnel: β=3.72',
    'A1_direct_invest: β=−3.74',
    'A2_sub0: β=0.94',
    'A2_sub1: β=−7.29',
    'A3_normal: β=2.99',
]

fig, ax = plt.subplots(figsize=(7.3, 4.4))

r2_vals = [decomp.loc[decomp['model'] == m, 'r2'].values[0]
           for m in ['A_base', 'B_field_FE', 'C_field_FE+archetype_xamp']]
labels = ['A: 기본\n(Δamp만)', 'B: +분야 FE', 'C: +원형×Δamp']
import seaborn as sns
pal = sns.color_palette('Set2', 3)
xx = np.arange(len(labels))
bars = ax.bar(xx, r2_vals, color=pal, alpha=0.85, width=0.55)
ax.set_xticks(xx); ax.set_xticklabels(labels, fontsize=10)
ax.set_ylabel('R²')
ax.set_title(
    f'ΔR² (B→C, 원형 추가) = {dr2_arch:+.3f}   '
    f'[5y: +0.094  /  11y v2: +0.085]'
)
ymax = max(r2_vals)
ax.set_ylim(0, ymax * 1.30)
for i, v in enumerate(r2_vals):
    ax.annotate(f'{v:.3f}', (xx[i], v), xytext=(0, 6),
                textcoords='offset points', ha='center', fontsize=10)

# 좌상단: 원형별 β
ax.text(0.02, 0.97, '\n'.join(beta_labels),
        transform=ax.transAxes, va='top', fontsize=9,
        bbox=dict(boxstyle='round,pad=0.4', facecolor='#fff8e1',
                  ec='#daa520', alpha=0.92))

# 우하단: 교체 정보
ax.text(0.98, 0.03,
        '교체: 과기→patent / 관광→외국인\n'
        '행정→재정자립도 / 통신→광대역',
        transform=ax.transAxes, va='bottom', ha='right', fontsize=9,
        bbox=dict(boxstyle='round,pad=0.4', facecolor='#e8f4f8',
                  ec='#5475a8', alpha=0.85))

ax.grid(alpha=0.3, axis='y')

plt.tight_layout()

DPI = 200
MAX = 1900
out = os.path.join(PREVIEW, 'h8_panel.png')
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
