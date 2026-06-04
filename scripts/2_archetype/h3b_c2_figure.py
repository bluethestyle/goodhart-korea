"""H3b figure + 교차검증: C2 sub-structure가 discrete 2분인가 gradient인가.
  - 교차검증 1: 피처기반(q1/h2/dec/amp) KMeans k=2 vs 프로파일기반 sub → ARI
  - 교차검증 2: q1_share 분포 bimodality coefficient (BC>0.555 → bimodal 경향)
  - 그림: (A) sub별 평균 월별 프로파일  (B) q1_share 분포
"""
import os, sys, io, warnings
import numpy as np, pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score
from scipy.stats import skew, kurtosis
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib import font_manager
warnings.filterwarnings('ignore')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RES = os.path.join(ROOT, 'data', 'results')
FIGDIR = os.path.join(ROOT, 'paper', 'figures')
for fp in ['Pretendard-Regular.otf', 'Pretendard-Bold.otf']:
    font_manager.fontManager.addfont(os.path.join(ROOT, 'paper', 'fonts', fp))
mpl.rcParams['font.family'] = 'Pretendard'
mpl.rcParams['axes.unicode_minus'] = False

c2 = pd.read_csv(os.path.join(RES, 'H3b_c2_subcluster.csv'))
mcols = [f'm{i+1}' for i in range(12)]
print('C2 n =', len(c2), '| sub 분포:', dict(c2['sub'].value_counts().sort_index()))

# ---- 교차검증 1: 피처기반 클러스터가 프로파일기반과 일치하나
feats = ['q1_share', 'h2_share', 'dec_share', 'amp12', 'amp6']
Xf = StandardScaler().fit_transform(c2[feats].values)
fk = KMeans(n_clusters=2, n_init=20, random_state=7).fit_predict(Xf)
ari = adjusted_rand_score(c2['sub'].values, fk)
print(f'교차검증1 — 피처기반 KMeans(k=2) vs 프로파일기반 sub: ARI = {ari:.3f}')

# ---- 교차검증 2: q1_share bimodality coefficient
x = c2['q1_share'].values
n = len(x)
g = skew(x); k = kurtosis(x, fisher=True)
BC = (g**2 + 1) / (k + 3 * (n - 1)**2 / ((n - 2) * (n - 3)))
print(f'교차검증2 — q1_share: skew={g:.2f}, kurtosis={k:.2f}, '
      f'bimodality coeff BC={BC:.3f} (>0.555 → bimodal 경향, 균등=0.555)')
# sub간 q1_share 평균차 / 합쳐진 표준편차 (분리도)
m0 = c2[c2['sub'] == 0]['q1_share']; m1 = c2[c2['sub'] == 1]['q1_share']
cohens_d = abs(m0.mean() - m1.mean()) / np.sqrt((m0.var() + m1.var()) / 2)
print(f'  sub0 q1={m0.mean():.3f} vs sub1 q1={m1.mean():.3f}, Cohen d={cohens_d:.2f}')

# sub 라벨을 해석적 이름으로 (q1 높은 쪽 = 연초집중형)
hi = c2.groupby('sub')['q1_share'].mean().idxmax()
name = {hi: '연초 집중형', (1 - hi): '분산형'}
col = {hi: '#c0392b', (1 - hi): '#2c6fbb'}

# ---- 그림 (width≈1260px) ----
fig, axes = plt.subplots(1, 2, figsize=(9.0, 3.8))
months = np.arange(1, 13)

ax = axes[0]
ax.plot(months, c2[mcols].mean().values * 100, '--', color='#888', lw=1.8, label='C2 전체 평균')
for s in sorted(c2['sub'].unique()):
    sub = c2[c2['sub'] == s]
    ax.plot(months, sub[mcols].mean().values * 100, '-o', color=col[s], lw=2.2, ms=4,
            label=f'{name[s]} (n={len(sub)})')
ax.set_xticks(months)
ax.set_xlabel('월'); ax.set_ylabel('정규화 집행 비중 (%)')
ax.set_title('(A) C2 출연금형 내부 sub-원형 월별 프로파일')
ax.legend(fontsize=8, loc='upper right'); ax.grid(alpha=0.3)

ax = axes[1]
for s in sorted(c2['sub'].unique()):
    sub = c2[c2['sub'] == s]
    ax.hist(sub['q1_share'] * 100, bins=np.arange(0, 90, 7), alpha=0.6,
            color=col[s], label=f'{name[s]}')
ax.axvline(c2['q1_share'].mean() * 100, color='#444', ls=':', lw=1.5)
ax.set_xlabel('1분기(1–3월) 집행 비중 (%)'); ax.set_ylabel('활동 수')
ax.set_title(f'(B) 연초집중도 분포 (BC={BC:.2f})')
ax.legend(fontsize=8); ax.grid(alpha=0.3)

plt.tight_layout()
outpng = os.path.join(FIGDIR, 'h3b_c2_subarchetype.png')
fig.savefig(outpng, dpi=140, bbox_inches='tight')
plt.close()

from PIL import Image
w, h = Image.open(outpng).size
print(f'\n저장: {outpng}  size={w}x{h}px')
print('완료.')
