"""H9: Persistent Homology(PH) — 활동 임베딩 + 시계열 데이터의 위상적 안정성.

Mapper(H4)는 시각화 도구. PH는 위상적 특징의 *수명(persistence)*을 측정해
신호의 강건성을 정량화한다.

분석 1: H3 활동 임베딩 12피처에 PH (Vietoris-Rips)
  - H0 (component): 클러스터의 위상적 분리도
  - H1 (loop): 데이터 매니폴드의 닫힌 경로 = 사업 원형 변형 cycle
  - persistence diagram: birth-death 점들로 구조 안정성 시각화

분석 2: 분야×원형×연도 amp_12m 시계열을 *시간 간 거리 행렬*로 PH
  - 자연 주기성 vs 외생 충격을 위상으로 구분
  - cycle persistence = 안정 패턴

분석 3: bootstrap PH (subsample n=300, 50회) → confidence band
  - 신호 안정성 검증

산출:
  data/figs/h9/H9_persistence_diagram.png
  data/figs/h9/H9_barcode.png
  data/figs/h9/H9_bootstrap_confidence.png
  data/results/H9_persistence_pairs.csv
"""
import os, sys, io, warnings
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from ripser import ripser
import matplotlib.pyplot as plt
import matplotlib as mpl

warnings.filterwarnings('ignore')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
H3_CSV = os.path.join(ROOT, 'data', 'results', 'H3_activity_embedding.csv')
OUT_DIR = os.path.join(ROOT, 'data', 'figs', 'h9')
RES_DIR = os.path.join(ROOT, 'data', 'results')
os.makedirs(OUT_DIR, exist_ok=True)

KFONT = None
for f in ['Malgun Gothic','Noto Sans CJK KR','AppleGothic']:
    if any(f in fn.name for fn in mpl.font_manager.fontManager.ttflist):
        mpl.rcParams['font.family'] = f
        KFONT = f
        break
mpl.rcParams['axes.unicode_minus'] = False
RNG = np.random.default_rng(42)

# ============================================================
# Step 1: 데이터 로드 + 표준화
# ============================================================
print('='*70)
print('Step 1: H3 활동 임베딩 (1,641 × 12 피처)')
print('='*70)
df = pd.read_csv(H3_CSV)
feat_cols = [
    'amp_12m_norm','amp_6m_norm','hhi_period','q4_pct','dec_pct','cv_monthly',
    'chooyeon_pct','operating_pct','direct_invest_pct','personnel_pct',
    'log_annual','growth_cagr',
]
X_full = StandardScaler().fit_transform(df[feat_cols].values)
print(f'  X shape = {X_full.shape}')

# Ripser는 N=1641로 너무 많음. subsample 300으로 PH.
SUB_N = 300
idx = RNG.choice(len(X_full), size=SUB_N, replace=False)
X = X_full[idx]
print(f'  subsample N = {SUB_N}')

# ============================================================
# Step 2: Vietoris-Rips PH (H0, H1)
# ============================================================
print('\n' + '='*70)
print('Step 2: Vietoris-Rips PH (max H1)')
print('='*70)
result = ripser(X, maxdim=1, thresh=8.0)
diagrams = result['dgms']
print(f'  H0 birth-death pairs: {len(diagrams[0])}')
print(f'  H1 birth-death pairs: {len(diagrams[1])}')

# Persistence = death - birth (높을수록 강건한 위상 특징)
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

# noise threshold (90 percentile)
if len(p0) > 0:
    thresh0 = np.percentile(p0, 90)
    sig0 = (p0 > thresh0).sum()
    print(f'\n  H0 신호 (top 10%) = {sig0}개 / 90 percentile threshold = {thresh0:.3f}')
if len(p1) > 0:
    thresh1 = np.percentile(p1, 90)
    sig1 = (p1 > thresh1).sum()
    print(f'  H1 신호 (top 10%) = {sig1}개 / 90 percentile threshold = {thresh1:.3f}')

# 저장
ph_pairs = []
for dim, dgm in enumerate(diagrams):
    for b, d in dgm:
        ph_pairs.append({'dim': dim, 'birth': float(b),
                          'death': float(d) if d != np.inf else np.inf,
                          'persistence': float(d - b) if d != np.inf else np.inf})
pd.DataFrame(ph_pairs).to_csv(os.path.join(RES_DIR, 'H9_persistence_pairs.csv'),
                                index=False, encoding='utf-8-sig')

# ============================================================
# Step 3: Bootstrap PH — confidence
# ============================================================
print('\n' + '='*70)
print('Step 3: Bootstrap PH (50회 subsample n=200)')
print('='*70)
bootstrap_h1_max = []
bootstrap_h0_count_top = []
for i in range(50):
    idx_b = RNG.choice(len(X_full), size=200, replace=False)
    Xb = X_full[idx_b]
    rb = ripser(Xb, maxdim=1, thresh=8.0)
    p0b = persistence(rb['dgms'][0])
    p1b = persistence(rb['dgms'][1])
    bootstrap_h1_max.append(p1b.max() if len(p1b) > 0 else 0.0)
    bootstrap_h0_count_top.append((p0b > 1.0).sum())  # persistence>1 인 H0 개수
    if i % 10 == 0:
        print(f'  {i+1}/50 ... H1 max so far median={np.median(bootstrap_h1_max):.3f}')

print(f'\n  H1 max persistence: median={np.median(bootstrap_h1_max):.3f}, '
       f'95% CI=[{np.percentile(bootstrap_h1_max, 2.5):.3f}, '
       f'{np.percentile(bootstrap_h1_max, 97.5):.3f}]')
print(f'  H0 (persistence>1) count: median={np.median(bootstrap_h0_count_top):.0f}, '
       f'95% CI=[{np.percentile(bootstrap_h0_count_top, 2.5):.0f}, '
       f'{np.percentile(bootstrap_h0_count_top, 97.5):.0f}]')

# ============================================================
# Step 4: Figures
# ============================================================
fig, axes = plt.subplots(1, 3, figsize=(18, 5.8))

# A. Persistence diagram
ax = axes[0]
if len(diagrams[0]) > 0:
    finite_h0 = np.array([(b, d) for b, d in diagrams[0] if d != np.inf])
    if len(finite_h0) > 0:
        ax.scatter(finite_h0[:,0], finite_h0[:,1], s=15, c='#5475a8', label=f'H0 (n={len(finite_h0)})', alpha=0.7)
if len(diagrams[1]) > 0:
    ax.scatter(diagrams[1][:,0], diagrams[1][:,1], s=20, c='#a85454', label=f'H1 (n={len(diagrams[1])})', alpha=0.7)
m = max(diagrams[0].max() if len(diagrams[0])>0 else 0,
        diagrams[1].max() if len(diagrams[1])>0 else 0)
m = max(m, 8) if not np.isfinite(m) else m
ax.plot([0, m], [0, m], '--', color='#888', alpha=0.5)
ax.set_xlabel('Birth'); ax.set_ylabel('Death')
ax.set_title(f'Persistence Diagram\n(N={SUB_N}, Vietoris-Rips, max thresh=8.0)')
ax.legend()
ax.grid(alpha=0.3)

# B. Barcode (H1)
ax = axes[1]
if len(diagrams[1]) > 0:
    sorted_h1 = sorted(diagrams[1], key=lambda x: -(x[1]-x[0]))
    n_top = min(30, len(sorted_h1))
    for i, (b, d) in enumerate(sorted_h1[:n_top]):
        ax.plot([b, d], [i, i], lw=2.5, color='#a85454', alpha=0.85)
    ax.set_yticks([0, n_top//2, n_top-1])
    ax.set_xlabel('filtration scale')
    ax.set_title(f'H1 Barcode — top {n_top} loops by persistence\n'
                 f'장수: {sorted_h1[0][1]-sorted_h1[0][0]:.2f}')
    ax.grid(alpha=0.3, axis='x')
else:
    ax.text(0.5, 0.5, 'no H1 features', ha='center', va='center', transform=ax.transAxes)

# C. Bootstrap H1 max persistence distribution
ax = axes[2]
ax.hist(bootstrap_h1_max, bins=15, color='#a85454', alpha=0.75, edgecolor='black')
ax.axvline(np.median(bootstrap_h1_max), color='black', lw=2, label=f'median={np.median(bootstrap_h1_max):.2f}')
lo, hi = np.percentile(bootstrap_h1_max, [2.5, 97.5])
ax.axvspan(lo, hi, alpha=0.15, color='black', label=f'95% CI=[{lo:.2f},{hi:.2f}]')
ax.set_xlabel('H1 max persistence (bootstrap n=200)')
ax.set_ylabel('빈도')
ax.set_title(f'Bootstrap PH — 50회 subsample\n루프 안정성 검증')
ax.legend(fontsize=8)
ax.grid(alpha=0.3, axis='y')

plt.tight_layout()
fig.savefig(os.path.join(OUT_DIR, 'H9_persistence_diagram.png'), dpi=130, bbox_inches='tight')
plt.close()

print('\n=== 그림 ===')
for f in sorted(os.listdir(OUT_DIR)): print(f'  {f}')
print('\n완료.')
