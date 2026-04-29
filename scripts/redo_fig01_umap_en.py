"""Figure 1 (h3_umap) standalone regeneration — paper-style minimal patch.

Changes from original (structure/information preserved):
  - legend markerscale=3.5 (dots too small)
  - font.size large values (20+) → paper readability 12~14
  - figsize × dpi adjusted → max(W,H) ≤ 1900px
  - All Korean labels replaced with English

Output: paper/figures_en/_preview/h3_umap.png
"""
import os, sys, io, warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from PIL import Image

warnings.filterwarnings('ignore')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# A4 body width (160mm ≈ 6.3 inch) 1:1 mapping guideline
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
PREVIEW = os.path.join(ROOT, 'paper', 'figures_en', '_preview')
os.makedirs(PREVIEW, exist_ok=True)

CLUSTER_EN = {-1: 'Noise', 0: 'Personnel', 1: 'Capital-Acq.',
              2: 'Grant-Transfer', 3: 'Normal'}

# English field name mapping
FIELD_EN = {
    '사회복지': 'Social Welfare',
    '보건': 'Health',
    '과학기술': 'S&T',
    '산업·중소기업및에너지': 'Industry/SMEs',
    '산업·중기': 'Industry/SMEs',
    '산업': 'Industry',
    '문화관광': 'Culture & Tourism',
    '문화': 'Culture',
    '교육': 'Education',
    '국토·지역개발': 'Land Development',
    '국토': 'Land',
    '국토및지역개발': 'Land Dev.',
    '일반·지방행정': 'Gen. Admin.',
    '일반행정': 'Gen. Admin.',
    '농림수산': 'Agriculture',
    '교통': 'Transport',
    '교통및물류': 'Transport',
    '환경': 'Environment',
    '통신': 'ICT',
    '통일·외교': 'Unification/Diplomacy',
    '통일외교': 'Unification/Diplomacy',
    '공공질서': 'Public Order',
    '공공질서및안전': 'Public Order',
    '국방': 'Defense',
    '예비비': 'Reserve',
}

df = pd.read_csv(H3_CSV)
print(f'Activity N = {len(df):,}')

fig, axes = plt.subplots(2, 1, figsize=(9.5, 7.5))

# Panel 1: HDBSCAN Project Archetype
ax = axes[0]
palette = plt.get_cmap('tab10')
for cl in sorted(df['cluster'].unique()):
    sub_ = df[df['cluster'] == cl]
    color = '#bbbbbb' if cl == -1 else palette(cl % 10)
    ax.scatter(sub_['u1'], sub_['u2'], s=8, c=[color], alpha=0.6,
               label=f"{CLUSTER_EN.get(cl, cl)} (n={len(sub_):,})")
ax.set_title(f'UMAP — HDBSCAN Project Archetype (total {len(df):,} activities)')
ax.set_xlabel('UMAP 1'); ax.set_ylabel('UMAP 2')
ax.legend(loc='best', markerscale=3.5, scatterpoints=1,
          frameon=True, framealpha=0.92)
ax.grid(alpha=0.3)

# Panel 2: Top 8 fields
ax = axes[1]
top_flds = df['FLD_NM'].value_counts().head(8).index.tolist()
palette2 = plt.get_cmap('tab20')
for i, f in enumerate(top_flds):
    sub_ = df[df['FLD_NM'] == f]
    label_en = FIELD_EN.get(f, f)
    ax.scatter(sub_['u1'], sub_['u2'], s=6, c=[palette2(i)], alpha=0.55,
               label=f'{label_en} (n={len(sub_):,})')
others = df[~df['FLD_NM'].isin(top_flds)]
ax.scatter(others['u1'], others['u2'], s=4, c='#dddddd', alpha=0.4,
           label='Others')
ax.set_title('UMAP — By Field (top 8)')
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
