"""그림 3 (h9_persistence) — 1x3 압축 → 세 figure 분리.

세 figure (각 A4 본문 폭 6.3in 1:1 매핑):
  paper/figures/_preview/h9_pd.png        (Persistence Diagram)
  paper/figures/_preview/h9_barcode.png   (H1 Barcode top 30)
  paper/figures/_preview/h9_bootstrap.png (Bootstrap H1 max histogram)

source: scripts/h9_v2_11y.py 의 plot 코드 분리 + A4 가이드 적용
"""
import os, sys, io, warnings
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from ripser import ripser
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
H3_CSV = os.path.join(ROOT, 'data', 'results', 'H3_activity_embedding_11y.csv')
H9_CSV = os.path.join(ROOT, 'data', 'results', 'H9_persistence_pairs_11y.csv')
PREVIEW = os.path.join(ROOT, 'paper', 'figures', '_preview')
os.makedirs(PREVIEW, exist_ok=True)

DPI = 200
MAX = 1900

def save_resize(fig, fname):
    out = os.path.join(PREVIEW, fname)
    fig.savefig(out, dpi=DPI, bbox_inches='tight')
    plt.close(fig)
    img = Image.open(out)
    w, h = img.size
    if max(w, h) > MAX:
        s = MAX / max(w, h)
        ns = (int(w * s), int(h * s))
        img = img.resize(ns, Image.LANCZOS)
        img.save(out, optimize=True)
        print(f'  {fname:25s} {w}x{h} -> {ns[0]}x{ns[1]}')
    else:
        print(f'  {fname:25s} {w}x{h}')

# ── 데이터 로드
df = pd.read_csv(H3_CSV)
ph = pd.read_csv(H9_CSV)
print(f'활동 N = {len(df):,}, PH pairs = {len(ph)}')

feat_cols = ['amp_12m_norm', 'amp_6m_norm', 'hhi_period', 'q4_pct', 'dec_pct',
             'cv_monthly', 'chooyeon_pct', 'operating_pct',
             'direct_invest_pct', 'personnel_pct', 'log_annual', 'growth_cagr']
X = StandardScaler().fit_transform(df[feat_cols].values)

# ── Bootstrap (H9 v2와 동일: n=200, RNG=42, 50회)
SUB_N = 200
RNG = np.random.default_rng(42)
print('bootstrap 50회 ...')
boot = []
for i in range(50):
    idx_b = RNG.choice(len(X), size=SUB_N, replace=False)
    rb = ripser(X[idx_b], maxdim=1, thresh=8.0)
    p1b = np.array([d - b for b, d in rb['dgms'][1] if d != np.inf])
    boot.append(p1b.max() if len(p1b) > 0 else 0.0)
boot = np.array(boot)
h1m = float(np.median(boot))
h1lo = float(np.percentile(boot, 2.5))
h1hi = float(np.percentile(boot, 97.5))
print(f'H1 max bootstrap median={h1m:.3f}, CI=[{h1lo:.3f}, {h1hi:.3f}]')

is_finite = lambda x: not (isinstance(x, float)
                           and (np.isinf(x) or np.isnan(x)))
h0 = ph[(ph['dim'] == 0) & ph['death'].apply(is_finite)]
h1 = ph[(ph['dim'] == 1) & ph['death'].apply(is_finite)]

# ── 3A: Persistence Diagram
fig, ax = plt.subplots(figsize=(9.84, 5))
ax.scatter(h0['birth'], h0['death'], s=18, c='#5475a8',
           label=f'H0 (n={len(h0)})', alpha=0.7)
ax.scatter(h1['birth'], h1['death'], s=22, c='#a85454',
           label=f'H1 (n={len(h1)})', alpha=0.75)
m = max(h0['death'].max() if len(h0) else 0,
        h1['death'].max() if len(h1) else 0, 8.0)
ax.plot([0, m], [0, m], '--', color='#888', alpha=0.5)
ax.set_xlabel('Birth')
ax.set_ylabel('Death')
ax.legend(loc='lower right')
ax.grid(alpha=0.3)
ax.text(0.02, 0.98, 'Vietoris-Rips\nN=300, max thresh=8.0',
        transform=ax.transAxes, va='top', fontsize=10,
        bbox=dict(boxstyle='round,pad=0.4', fc='white',
                  ec='#bbb', alpha=0.9))
plt.tight_layout()
save_resize(fig, 'h9_pd.png')

# ── 3B: H1 Barcode top 30
fig, ax = plt.subplots(figsize=(8.82, 4.2))
h1_sorted = h1.sort_values('persistence', ascending=False).reset_index(drop=True)
n_top = min(30, len(h1_sorted))
for i in range(n_top):
    ax.plot([float(h1_sorted.iloc[i]['birth']),
             float(h1_sorted.iloc[i]['death'])],
            [i, i], lw=2.3, color='#a85454', alpha=0.85)
ax.set_yticks([0, n_top // 2, n_top - 1])
ax.set_xlabel('filtration scale')
ax.set_ylabel('loop rank')
ax.text(0.02, 0.96,
        f'top {n_top} loops · '
        f'max persist = {float(h1_sorted.iloc[0]["persistence"]):.3f}',
        transform=ax.transAxes, va='top', fontsize=10,
        bbox=dict(boxstyle='round,pad=0.4', fc='white',
                  ec='#bbb', alpha=0.9))
ax.grid(alpha=0.3, axis='x')
plt.tight_layout()
save_resize(fig, 'h9_barcode.png')

# ── 3C: Bootstrap H1 max histogram
fig, ax = plt.subplots(figsize=(8.82, 4.2))
ax.hist(boot, bins=15, color='#a85454', alpha=0.78, edgecolor='black')
ax.axvline(h1m, color='black', lw=2, label=f'median = {h1m:.2f}')
ax.axvspan(h1lo, h1hi, alpha=0.15, color='black',
           label=f'95% CI = [{h1lo:.2f}, {h1hi:.2f}]')
ax.axvline(0.65, color='steelblue', lw=1.4, linestyle='--',
           label='5y 참조 (median 0.65)')
ax.set_xlabel('H1 max persistence (bootstrap, n=200, 50회)')
ax.set_ylabel('빈도')
ax.legend(loc='upper right')
ax.grid(alpha=0.3, axis='y')
plt.tight_layout()
save_resize(fig, 'h9_bootstrap.png')

print('완료.')
