"""H9 v2: Persistent Homology — H3 v2 (11y) 활동 임베딩으로 재실행.

입력: data/results/H3_activity_embedding_11y.csv (1,557 × 12 피처)
출력:
  data/figs/h9_11y/H9_persistence_diagram_11y.png
  data/results/H9_persistence_pairs_11y.csv

파라미터: subsample N=300, Vietoris-Rips, max thresh=8.0
Bootstrap: 50회 (n=200) — H1 max persistence CI
"""
import os, sys, io, warnings
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from ripser import ripser
import matplotlib.pyplot as plt
import matplotlib as mpl
import scienceplots
import seaborn as sns
plt.style.use(['science', 'no-latex', 'grid'])
plt.rcParams.update({
    'font.size': 20,
    'axes.titlesize': 22,
    'axes.labelsize': 20,
    'xtick.labelsize': 17,
    'ytick.labelsize': 17,
    'legend.fontsize': 17,
    'legend.title_fontsize': 17,
    'figure.titlesize': 23,
    'lines.linewidth': 2.5,
    'lines.markersize': 10,
    'axes.linewidth': 1.2,
    'grid.alpha': 0.3,
    'mathtext.fontset': 'stix',
    'mathtext.default': 'regular',
    'axes.unicode_minus': False,
})
for fname in ['Arial Unicode MS', 'Malgun Gothic', 'NanumGothic']:
    if any(fname.lower() in fn.name.lower() for fn in mpl.font_manager.fontManager.ttflist):
        mpl.rcParams['font.family'] = [fname, 'Arial Unicode MS', 'Times New Roman', 'DejaVu Sans']
        break
mpl.rcParams['axes.unicode_minus'] = False
sns.set_palette('Set2')

warnings.filterwarnings('ignore')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
H3_CSV = os.path.join(ROOT, 'data', 'results', 'H3_activity_embedding_11y.csv')
OUT_DIR = os.path.join(ROOT, 'data', 'figs', 'h9_11y')
RES_DIR = os.path.join(ROOT, 'data', 'results')
os.makedirs(OUT_DIR, exist_ok=True)

KFONT = mpl.rcParams.get('font.family', 'Malgun Gothic')
RNG = np.random.default_rng(42)

# ============================================================
# Step 1: 데이터 로드 + 표준화
# ============================================================
print('=' * 70)
print('Step 1: H3 v2 활동 임베딩 11y (1,557 × 12 피처)')
print('=' * 70)
df = pd.read_csv(H3_CSV)
feat_cols = [
    'amp_12m_norm', 'amp_6m_norm', 'hhi_period', 'q4_pct', 'dec_pct', 'cv_monthly',
    'chooyeon_pct', 'operating_pct', 'direct_invest_pct', 'personnel_pct',
    'log_annual', 'growth_cagr',
]
X_full = StandardScaler().fit_transform(df[feat_cols].values)
print(f'  X shape = {X_full.shape}')

SUB_N = 300
idx = RNG.choice(len(X_full), size=SUB_N, replace=False)
X = X_full[idx]
print(f'  subsample N = {SUB_N}')

# ============================================================
# Step 2: Vietoris-Rips PH (H0, H1)
# ============================================================
print('\n' + '=' * 70)
print('Step 2: Vietoris-Rips PH (max thresh=8.0)')
print('=' * 70)
result = ripser(X, maxdim=1, thresh=8.0)
diagrams = result['dgms']
print(f'  H0 birth-death pairs: {len(diagrams[0])}')
print(f'  H1 birth-death pairs: {len(diagrams[1])}')


def persistence(dgm):
    return np.array([d - b for b, d in dgm if d != np.inf])


p0 = persistence(diagrams[0])
p1 = persistence(diagrams[1])

print(f'\n  H0 (component) persistence stats:')
print(f'    n_finite = {len(p0)}, max = {p0.max():.3f}, median = {np.median(p0):.3f}')
print(f'    top 5: {sorted(p0, reverse=True)[:5]}')

print(f'\n  H1 (loop) persistence stats:')
if len(p1) > 0:
    print(f'    n = {len(p1)}, max = {p1.max():.3f}, median = {np.median(p1):.3f}')
    print(f'    top 10: {sorted(p1, reverse=True)[:10]}')
else:
    print(f'    no H1 features (no loops)')

if len(p0) > 0:
    thresh0 = np.percentile(p0, 90)
    sig0 = (p0 > thresh0).sum()
    print(f'\n  H0 신호 (top 10%) = {sig0}개 / 90pct threshold = {thresh0:.3f}')
if len(p1) > 0:
    thresh1 = np.percentile(p1, 90)
    sig1 = (p1 > thresh1).sum()
    print(f'  H1 신호 (top 10%) = {sig1}개 / 90pct threshold = {thresh1:.3f}')

# 저장
ph_pairs = []
for dim, dgm in enumerate(diagrams):
    for b, d in dgm:
        ph_pairs.append({
            'dim': dim,
            'birth': float(b),
            'death': float(d) if d != np.inf else np.inf,
            'persistence': float(d - b) if d != np.inf else np.inf,
        })
pd.DataFrame(ph_pairs).to_csv(
    os.path.join(RES_DIR, 'H9_persistence_pairs_11y.csv'),
    index=False, encoding='utf-8-sig'
)
print(f'\n  saved: H9_persistence_pairs_11y.csv')

# ============================================================
# Step 3: Bootstrap PH — 50회 n=200
# ============================================================
print('\n' + '=' * 70)
print('Step 3: Bootstrap PH (50회 subsample n=200)')
print('=' * 70)
bootstrap_h1_max = []
bootstrap_h0_count_top = []
for i in range(50):
    idx_b = RNG.choice(len(X_full), size=200, replace=False)
    Xb = X_full[idx_b]
    rb = ripser(Xb, maxdim=1, thresh=8.0)
    p0b = persistence(rb['dgms'][0])
    p1b = persistence(rb['dgms'][1])
    bootstrap_h1_max.append(p1b.max() if len(p1b) > 0 else 0.0)
    bootstrap_h0_count_top.append((p0b > 1.0).sum())
    if i % 10 == 0:
        print(f'  {i + 1}/50 ... H1 max so far median={np.median(bootstrap_h1_max):.3f}')

h1_med = np.median(bootstrap_h1_max)
h1_lo, h1_hi = np.percentile(bootstrap_h1_max, [2.5, 97.5])
h0_med = np.median(bootstrap_h0_count_top)
h0_lo, h0_hi = np.percentile(bootstrap_h0_count_top, [2.5, 97.5])

print(f'\n  H1 max persistence: median={h1_med:.3f}, '
      f'95% CI=[{h1_lo:.3f}, {h1_hi:.3f}]')
print(f'  H0 (persistence>1) count: median={h0_med:.0f}, '
      f'95% CI=[{h0_lo:.0f}, {h0_hi:.0f}]')

# ============================================================
# Step 4: 5y vs 11y 비교 (참조값)
# ============================================================
print('\n' + '=' * 70)
print('Step 4: 5y vs 11y 비교')
print('=' * 70)
print('  5y: 30 강건 components + 15 강건 loops, H1 max 0.65, CI [0.46, 0.98]')
h1_max_val = p1.max() if len(p1) > 0 else 0.0
print(f'  11y: H0 sig={sig0 if len(p0)>0 else 0}, H1 sig={sig1 if len(p1)>0 else 0}, '
      f'H1 max={h1_max_val:.3f}, CI=[{h1_lo:.2f}, {h1_hi:.2f}]')

# ============================================================
# Step 5: Figure (3-panel, max 1800px)
# ============================================================
DPI = 200
fig, axes = plt.subplots(1, 3, figsize=(18, 5.8))

# A. Persistence diagram
ax = axes[0]
if len(diagrams[0]) > 0:
    finite_h0 = np.array([(b, d) for b, d in diagrams[0] if d != np.inf])
    if len(finite_h0) > 0:
        ax.scatter(finite_h0[:, 0], finite_h0[:, 1], s=15,
                   c='#5475a8', label=f'H0 (n={len(finite_h0)})', alpha=0.7)
if len(diagrams[1]) > 0:
    ax.scatter(diagrams[1][:, 0], diagrams[1][:, 1], s=20,
               c='#a85454', label=f'H1 (n={len(diagrams[1])})', alpha=0.7)

all_vals = []
if len(diagrams[0]) > 0:
    finite_d0 = diagrams[0][np.isfinite(diagrams[0][:, 1])]
    if len(finite_d0) > 0:
        all_vals.extend(finite_d0.flatten().tolist())
if len(diagrams[1]) > 0:
    finite_d1 = diagrams[1][np.isfinite(diagrams[1][:, 1])]
    if len(finite_d1) > 0:
        all_vals.extend(finite_d1.flatten().tolist())
m = max(all_vals) if all_vals else 8.0
ax.plot([0, m], [0, m], '--', color='#888', alpha=0.5)
ax.set_xlabel('Birth')
ax.set_ylabel('Death')
ax.set_title(f'Persistence Diagram — 11y\n(N={SUB_N}, Vietoris-Rips, thresh=8.0)')
ax.legend()
ax.grid(alpha=0.3)

# B. H1 Barcode (top 30)
ax = axes[1]
if len(diagrams[1]) > 0:
    sorted_h1 = sorted(diagrams[1], key=lambda x: -(x[1] - x[0]))
    n_top = min(30, len(sorted_h1))
    for i, (b, d) in enumerate(sorted_h1[:n_top]):
        ax.plot([b, d], [i, i], lw=2.5, color='#a85454', alpha=0.85)
    ax.set_yticks([0, n_top // 2, n_top - 1])
    ax.set_xlabel('filtration scale')
    ax.set_title(f'H1 Barcode — top {n_top} loops (11y)\n'
                 f'max persist={sorted_h1[0][1] - sorted_h1[0][0]:.3f}')
    ax.grid(alpha=0.3, axis='x')
else:
    ax.text(0.5, 0.5, 'no H1 features', ha='center', va='center', transform=ax.transAxes)

# C. Bootstrap H1 max distribution
ax = axes[2]
ax.hist(bootstrap_h1_max, bins=15, color='#a85454', alpha=0.75, edgecolor='black')
ax.axvline(h1_med, color='black', lw=2, label=f'median={h1_med:.2f}')
ax.axvspan(h1_lo, h1_hi, alpha=0.15, color='black',
           label=f'95% CI=[{h1_lo:.2f},{h1_hi:.2f}]')
# 5y 참조선
ax.axvline(0.65, color='steelblue', lw=1.5, linestyle='--', label='5y median=0.65')
ax.set_xlabel('H1 max persistence (bootstrap n=200)')
ax.set_ylabel('빈도')
ax.set_title(f'Bootstrap PH — 50회 (11y)\n5y 비교: median 0.65, CI [0.46,0.98]')
ax.legend()
ax.grid(alpha=0.3, axis='y')

plt.suptitle('Persistent Homology — 11y (자산취득형 4-클러스터)', y=1.01)
plt.tight_layout()

out_png = os.path.join(OUT_DIR, 'H9_persistence_diagram_11y.png')
fig.savefig(out_png, dpi=DPI, bbox_inches='tight')
plt.close()

# 해상도 확인 (max 1800px)
try:
    from PIL import Image
    with Image.open(out_png) as im:
        w, h = im.size
        print(f'\n  PNG size: {w}x{h}px')
        if max(w, h) > 1800:
            factor = 1800 / max(w, h)
            new_w, new_h = int(w * factor), int(h * factor)
            im = im.resize((new_w, new_h), Image.LANCZOS)
            im.save(out_png)
            print(f'  resized to {new_w}x{new_h}px')
except ImportError:
    pass

print('\n=== 출력 파일 ===')
for fn in sorted(os.listdir(OUT_DIR)):
    print(f'  {OUT_DIR}/{fn}')
print(f'  {RES_DIR}/H9_persistence_pairs_11y.csv')
print('\n완료.')
