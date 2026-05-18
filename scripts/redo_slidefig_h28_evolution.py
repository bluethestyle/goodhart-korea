"""슬라이드용 h28_evolution — 12개월 cycle 진폭 진화 (4 archetype line).

paper와 다른 슬라이드 사양:
- figsize=(11, 4.0) landscape (슬라이드 가로폭 활용)
- legend 차트 외부 하단 4-칼럼 (충분한 horizontal room 활용)
- 변화율 annotation 박스 제거 (슬라이드는 별도 카드로 수치 표시)
- ymax 헤드룸 1.10 (annotation 자리 불필요)
- output: paper/slides/assets/ 만

paper용은 redo_fig15_evolution.py 참조.
"""
import os, sys, io, warnings
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
SLIDES = os.path.join(ROOT, 'paper', 'slides', 'assets')

ARCH_NAME = {'C0_personnel': '인건비형 (n=129)',
             'C1_direct_invest': '자산취득형 (n=99)',
             'C2_chooyeon': '출연금형 (n=154)',
             'C3_normal': '정상사업 (n=1,175)'}
ARCH_COLOR = {'C0_personnel': '#4C72B0',
              'C1_direct_invest': '#DD8452',
              'C2_chooyeon': '#55A868',
              'C3_normal': '#C44E52'}

ev = pd.read_csv(os.path.join(RES, 'H28_wavelet_12m_evolution.csv'))

fig, ax = plt.subplots(figsize=(11, 4.0))

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

ymax_data = ev['power_12m'].max()
ax.set_ylim(-0.05, ymax_data * 1.10)

# 외부 하단 legend
ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.18),
          ncol=4, frameon=False, columnspacing=1.4, handletextpad=0.5)

plt.tight_layout()

DPI = 180
MAX = 1900
out = os.path.join(SLIDES, 'h28_evolution.png')
fig.savefig(out, dpi=DPI, bbox_inches='tight')
plt.close()

img = Image.open(out)
w, h = img.size
if max(w, h) > MAX:
    s = MAX / max(w, h)
    ns = (int(w * s), int(h * s))
    img = img.resize(ns, Image.LANCZOS)
    img.save(out, optimize=True)
    print(f'slide: {w}x{h} -> {ns[0]}x{ns[1]}')
else:
    print(f'slide: {w}x{h}')
print(f'  -> {out}')
