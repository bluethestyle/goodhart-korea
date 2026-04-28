"""그림 1 (h3_umap) 단독 재생성 — paper-style minimal patch.

수정 항목 (원본 차트 구조·정보 유지):
  - legend markerscale=3.5 (사용자 지적: 도트 너무 작음)
  - font.size 큰 값(20+) → paper 가독성용 12~14
  - figsize × dpi 조정 → max(W,H) ≤ 1900px

미리보기는 paper/figures/_preview/h3_umap.png 에 저장.
사용자 OK 후 paper/figures/h3_umap.png 로 복사.
"""
import os, sys, io, warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from PIL import Image

warnings.filterwarnings('ignore')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# A4 본문 폭(160mm ≈ 6.3 inch) 1:1 매핑 가이드라인
plt.rcParams.update({
    'font.size': 11,
    'axes.titlesize': 12,
    'axes.labelsize': 11,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
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
PREVIEW = os.path.join(ROOT, 'paper', 'figures', '_preview')
os.makedirs(PREVIEW, exist_ok=True)

CLUSTER_KR = {-1: '노이즈', 0: '인건비형', 1: '자산취득형',
              2: '출연금형', 3: '정상사업'}

df = pd.read_csv(H3_CSV)
print(f'활동 N = {len(df):,}')

fig, axes = plt.subplots(2, 1, figsize=(6.3, 7.5))

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

DPI = 200
MAX = 1900
out = os.path.join(PREVIEW, 'h3_umap.png')
fig.savefig(out, dpi=DPI, bbox_inches='tight')
plt.close()

img = Image.open(out)
w, h = img.size
if max(w, h) > MAX:
    s = MAX / max(w, h)
    ns = (int(w * s), int(h * s))
    img = img.resize(ns, Image.LANCZOS)
    img.save(out, optimize=True)
    print(f'preview saved: {w}x{h} -> {ns[0]}x{ns[1]} ({out})')
else:
    print(f'preview saved: {w}x{h} ({out})')
