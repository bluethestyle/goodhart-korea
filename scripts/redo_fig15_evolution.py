"""그림 15 (h28_evolution) — 12개월 cycle 진폭의 연도별 진화 (4 archetype line).

source: scripts/h28_wavelet.py
A4 본문 폭 6.3 inch 1:1, figsize=(6.3, 3.8), dpi=200

레전드는 차트 밖(하단)에 배치하고, 변화율 박스는 제거 — 슬라이드/논문에서
숫자 카드를 별도 컬럼으로 표시하므로 차트 안에 중복 텍스트를 남기지 않는다.
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
    'font.size': 15, 'axes.titlesize': 17, 'axes.labelsize': 15,
    'xtick.labelsize': 13, 'ytick.labelsize': 13,
    'legend.fontsize': 13,
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

fig, ax = plt.subplots(figsize=(6.3, 4.0))

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

# 데이터 정점에 약간의 헤드룸만 — 빈 공간 박스가 사라졌으므로 1.40 → 1.10
ymax_data = ev['power_12m'].max()
ax.set_ylim(-0.05, ymax_data * 1.10)

# 레전드는 차트 외부 하단에 4-칼럼 가로 배치 → 데이터 영역 가리지 않음
ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.18),
          ncol=4, frameon=False, columnspacing=1.4, handletextpad=0.5)

plt.tight_layout()

DPI = 200
MAX = 1900
out_preview = os.path.join(PREVIEW, 'h28_evolution.png')
fig.savefig(out_preview, dpi=DPI, bbox_inches='tight')
plt.close()
img = Image.open(out_preview)
w, h = img.size
if max(w, h) > MAX:
    s = MAX / max(w, h)
    ns = (int(w * s), int(h * s))
    img = img.resize(ns, Image.LANCZOS)
    img.save(out_preview, optimize=True)
    print(f'preview: {w}x{h} -> {ns[0]}x{ns[1]}')
else:
    print(f'preview: {w}x{h}')

# 슬라이드/논문 production 경로에도 복사 (figures/ + paper/slides/assets/)
import shutil
for dst in [os.path.join(ROOT, 'paper', 'figures', 'h28_evolution.png'),
            os.path.join(ROOT, 'paper', 'slides', 'assets', 'h28_evolution.png')]:
    shutil.copy2(out_preview, dst)
    print(f'  -> {dst}')
