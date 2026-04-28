"""그림 15 (h28_evolution) — 12개월 cycle 진폭의 연도별 진화 (4 archetype line).

source: scripts/h28_wavelet.py
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

ARCH_NAME = {'C0_personnel': '인건비형 (n=129)',
             'C1_direct_invest': '자산취득형 (n=99)',
             'C2_chooyeon': '출연금형 (n=154)',
             'C3_normal': '정상사업 (n=1,175)'}
ARCH_COLOR = {'C0_personnel': '#4C72B0',
              'C1_direct_invest': '#DD8452',
              'C2_chooyeon': '#55A868',
              'C3_normal': '#C44E52'}

ev = pd.read_csv(os.path.join(RES, 'H28_wavelet_12m_evolution.csv'))
print(ev.head())

fig, ax = plt.subplots(figsize=(6.3, 3.8))

for arch in ['C0_personnel', 'C1_direct_invest', 'C2_chooyeon', 'C3_normal']:
    sub = ev[ev['archetype'] == arch].sort_values('year')
    if len(sub) == 0:
        continue
    color = ARCH_COLOR.get(arch, '#888')
    label = ARCH_NAME.get(arch, arch)
    ax.plot(sub['year'], sub['power_12m'], 'o-', lw=2.0, markersize=6,
            color=color, label=label, alpha=0.92)

ax.set_xlabel('연도')
ax.set_ylabel('12m cycle wavelet power')
ax.grid(alpha=0.3)

# 정점(출연금형 1.55) 위쪽 여유 확보 → legend/박스가 데이터 안 가림
ymax_data = ev['power_12m'].max()
ax.set_ylim(-0.05, ymax_data * 1.40)

ax.legend(loc='upper left', frameon=True, framealpha=0.95)

# 변화율 박스 우상단 (정점 위 빈공간)
ax.text(0.98, 0.97,
        '2015~2017 → 2023~2025\n'
        '출연금형  +554%\n'
        '정상사업  +317%\n'
        '자산취득형 +175%\n'
        '인건비형  −0.8% (통제)',
        transform=ax.transAxes, ha='right', va='top', fontsize=9,
        bbox=dict(boxstyle='round,pad=0.45', fc='#fff8e1',
                  ec='#daa520', alpha=0.95))

plt.tight_layout()

DPI = 200
MAX = 1900
out = os.path.join(PREVIEW, 'h28_evolution.png')
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
