"""h3_umap 가로(landscape) 버전 — 2-row를 1-row × 2-col로 재배치.

원본 paper/figures/h3_umap.png (1850×1449, 세로 stack) 보존.
슬라이드 16:9 친화 비율로 paper/figures/h3_umap_h.png 신규 생성.
"""
import os, sys, io, warnings
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from PIL import Image

warnings.filterwarnings('ignore')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

plt.rcParams.update({
    'font.size': 13,
    'axes.titlesize': 15,
    'axes.labelsize': 13,
    'xtick.labelsize': 11,
    'ytick.labelsize': 11,
    'legend.fontsize': 11,
    'figure.titlesize': 13,
    'lines.linewidth': 1.4,
    'lines.markersize': 6,
    'mathtext.default': 'regular',
    'axes.unicode_minus': False,
})
for fname in ['Malgun Gothic', 'Arial Unicode MS', 'NanumGothic']:
    if any(fname.lower() in fn.name.lower()
           for fn in mpl.font_manager.fontManager.ttflist):
        mpl.rcParams['font.family'] = [fname, 'Times New Roman', 'DejaVu Sans']
        break

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
H3_CSV = os.path.join(ROOT, 'data', 'results', 'H3_activity_embedding_11y.csv')
FIG_DIR = os.path.join(ROOT, 'paper', 'figures')
PREVIEW = os.path.join(FIG_DIR, '_preview')
os.makedirs(PREVIEW, exist_ok=True)

CLUSTER_KR = {-1: '노이즈', 0: '인건비형', 1: '자산취득형',
              2: '출연금형', 3: '정상사업'}

df = pd.read_csv(H3_CSV)
print(f'활동 N = {len(df):,}')

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# 패널 1: HDBSCAN 사업원형
ax = axes[0]
palette = plt.get_cmap('tab10')
for cl in sorted(df['cluster'].unique()):
    sub_ = df[df['cluster'] == cl]
    color = '#bbbbbb' if cl == -1 else palette(cl % 10)
    ax.scatter(sub_['u1'], sub_['u2'], s=8, c=[color], alpha=0.6,
               label=f"{CLUSTER_KR.get(cl, cl)} (n={len(sub_):,})")
ax.set_title(f'UMAP — HDBSCAN 사업원형 (전체 {len(df):,} 활동)')
ax.set_xlabel('UMAP 1'); ax.set_ylabel('UMAP 2')
ax.legend(loc='best', markerscale=3.5, scatterpoints=1,
          frameon=True, framealpha=0.92)
ax.grid(alpha=0.3)

# 패널 2: 분야별 상위 8개
ax = axes[1]
top_flds = df['FLD_NM'].value_counts().head(8).index.tolist()
palette2 = plt.get_cmap('tab20')
for i, f in enumerate(top_flds):
    sub_ = df[df['FLD_NM'] == f]
    ax.scatter(sub_['u1'], sub_['u2'], s=6, c=[palette2(i)], alpha=0.55,
               label=f'{f} (n={len(sub_):,})')
others = df[~df['FLD_NM'].isin(top_flds)]
ax.scatter(others['u1'], others['u2'], s=4, c='#dddddd', alpha=0.4,
           label='기타')
ax.set_title('UMAP — 분야별 (상위 8개)')
ax.set_xlabel('UMAP 1'); ax.set_ylabel('UMAP 2')
ax.legend(loc='best', ncol=2, markerscale=3.5, scatterpoints=1,
          frameon=True, framealpha=0.92)
ax.grid(alpha=0.3)

plt.tight_layout()

DPI = 140
MAX = 1900
out_full = os.path.join(FIG_DIR, 'h3_umap_h.png')
fig.savefig(out_full, dpi=DPI, bbox_inches='tight')
plt.close()

img = Image.open(out_full)
w, h = img.size
if max(w, h) > MAX:
    s = MAX / max(w, h)
    ns = (int(w * s), int(h * s))
    img.resize(ns, Image.LANCZOS).save(out_full, optimize=True)
    print(f'saved (resized): {w}x{h} -> {ns[0]}x{ns[1]} ({out_full})')
else:
    print(f'saved: {w}x{h} ({out_full})')

# Read 검증용 소형 preview (≤1280px)
img2 = Image.open(out_full)
w2, h2 = img2.size
if w2 > 1200:
    ratio = 1200 / w2
    sm = (1200, int(h2 * ratio))
    out_small = os.path.join(PREVIEW, 'h3_umap_h_small.png')
    img2.resize(sm, Image.LANCZOS).save(out_small, optimize=True)
    print(f'small preview: {sm[0]}x{sm[1]} ({out_small})')
