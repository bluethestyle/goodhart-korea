"""슬라이드용 h27_psd — 4 archetype × 6 freq bin 평균 PSD.

paper와 다른 슬라이드 사양:
- figsize=(9, 4.5) landscape
- legend 차트 외부 하단 4-칼럼 (꺾은선 가림 방지)
- annotation 박스 좌상단 (paper와 동일하지만 폰트 약간 작게)
- output: paper/slides/assets/ 만

paper용은 redo_fig11_psd.py 참조.
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

psd_avg = pd.read_csv(os.path.join(RES, 'H27_psd_archetype_avg.csv'))

ARCH_NAME = {'C0_personnel': '인건비형 (n=129)',
             'C1_direct_invest': '자산취득형 (n=99)',
             'C2_chooyeon': '출연금형 (n=154)',
             'C3_normal': '정상사업 (n=1,175)'}
ARCH_COLOR = {'C0_personnel': '#4C72B0',
              'C1_direct_invest': '#DD8452',
              'C2_chooyeon': '#55A868',
              'C3_normal': '#C44E52'}

fig, ax = plt.subplots(figsize=(9, 4.5))
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
ax.grid(alpha=0.3)

# legend 외부 하단
ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.18),
          ncol=4, frameon=False, columnspacing=1.4, handletextpad=0.5,
          fontsize=12)

# 출연금형 12m 강조 — 좌상단
chooyeon_12m = float(psd_avg[psd_avg['archetype'] == 'C2_chooyeon']['psdnorm_k1'].values[0])
ax.text(0.02, 0.96,
        f'출연금형 12m: {chooyeon_12m:.3f}\n(다른 원형 대비 ~2배)',
        transform=ax.transAxes, ha='left', va='top', fontsize=12,
        bbox=dict(boxstyle='round,pad=0.4', fc='#fff8e1',
                  ec='#daa520', alpha=0.92))

plt.tight_layout()

DPI = 180
MAX = 1900
out = os.path.join(SLIDES, 'h27_psd.png')
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
