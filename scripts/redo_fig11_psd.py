"""그림 11 (h27_psd) — 4 archetype × 6 freq bin 평균 PSD.

source: scripts/h27_power_spectrum_coherence.py 의 (A) PSD plot
A4 본문 폭 6.3 inch 1:1, figsize=(6.3, 3.8), dpi=200
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

psd_avg = pd.read_csv(os.path.join(RES, 'H27_psd_archetype_avg.csv'))
print(psd_avg.to_string())

ARCH_NAME = {'C0_personnel': '인건비형 (n=129)',
             'C1_direct_invest': '자산취득형 (n=99)',
             'C2_chooyeon': '출연금형 (n=154)',
             'C3_normal': '정상사업 (n=1,175)'}
ARCH_COLOR = {'C0_personnel': '#4C72B0',
              'C1_direct_invest': '#DD8452',
              'C2_chooyeon': '#55A868',
              'C3_normal': '#C44E52'}

fig, ax = plt.subplots(figsize=(6.3, 3.8))
freqs = list(range(7))
labels_freq = ['DC (k=0)', '12m', '6m', '4m', '3m·분기', '2.4m', '2m']

for _, row in psd_avg.iterrows():
    vals = [row[f'psdnorm_k{k}'] for k in range(7)]
    arch = row['archetype']
    ax.plot(freqs[1:], vals[1:], 'o-',
            label=ARCH_NAME.get(arch, arch),
            color=ARCH_COLOR.get(arch, '#888'),
            linewidth=2.0, markersize=8)

ax.set_xticks(freqs[1:])
ax.set_xticklabels(labels_freq[1:])
ax.set_ylabel('정규화 PSD')
ax.set_xlabel('주파수 빈 (주기)')
ax.legend(loc='upper right', frameon=True)
ax.grid(alpha=0.3)

# 출연금형 12m 강조 — 좌상단
chooyeon_12m = float(psd_avg[psd_avg['archetype'] == 'C2_chooyeon']['psdnorm_k1'].values[0])
ax.text(0.02, 0.96,
        f'출연금형 12m: {chooyeon_12m:.3f}\n(다른 원형 대비 ~2배)',
        transform=ax.transAxes, ha='left', va='top', fontsize=9,
        bbox=dict(boxstyle='round,pad=0.4', fc='#fff8e1',
                  ec='#daa520', alpha=0.92))

plt.tight_layout()

DPI = 200
MAX = 1900
out = os.path.join(PREVIEW, 'h27_psd.png')
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
