"""견고성 검증 3분석 그림 생성 (C4·C7·C6). width ≤ 1280px, Pretendard 폰트."""
import os, sys, io
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib import font_manager
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score
import warnings

warnings.filterwarnings('ignore')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RES = os.path.join(ROOT, 'data', 'results')
FIG = os.path.join(ROOT, 'paper', 'figures')
FONTS = os.path.join(ROOT, 'paper', 'fonts')
for f in ['Pretendard-Regular.otf', 'Pretendard-Bold.otf', 'Pretendard-SemiBold.otf']:
    font_manager.fontManager.addfont(os.path.join(FONTS, f))
mpl.rcParams['font.family'] = 'Pretendard'
mpl.rcParams['axes.unicode_minus'] = False
mpl.rcParams['font.size'] = 10

ACC = '#4a6fa5'      # accent blue
RED = '#c0392b'
GRN = '#27ae60'
AMB = '#e67e22'
GRAY = '#b8c0cc'
ARCH_COL = {'C0인건비': '#7fb3d5', 'C1자산취득': '#e67e22',
            'C2출연금': '#9b59b6', 'C3정상': '#d5dbe3'}


def savep(fig, name):
    p = os.path.join(FIG, name)
    fig.savefig(p, dpi=128, bbox_inches='tight')
    plt.close(fig)
    from PIL import Image
    w, h = Image.open(p).size
    flag = 'OK' if w <= 1280 else '⚠️ TOO WIDE'
    print(f'  {name}: {w}×{h}px  {flag}')


# ════════════════════════════════════════════════════════════════
# FIG C4 — 재군집 ARI + 게임화 순위 보존
# ════════════════════════════════════════════════════════════════
df = pd.read_csv(os.path.join(RES, 'H3_activity_embedding_11y.csv'))
ARCH_KR = {0: 'C0 인건비', 1: 'C1 자산취득', 2: 'C2 출연금', 3: 'C3 정상'}
y = df['cluster'].values
ari_tbl = pd.read_csv(os.path.join(RES, 'robust_c4_recluster_ari.csv'))

# spec B 재계산(편성목 4피처만) → 매칭 → amp_12m 원본 vs 재군집
BUDGET = ['chooyeon_pct', 'operating_pct', 'direct_invest_pct', 'personnel_pct']
labB = KMeans(4, n_init=25, random_state=42).fit_predict(
    StandardScaler().fit_transform(df[BUDGET].values))
matchB = {b: pd.Series(y[labB == b]).value_counts().idxmax() for b in sorted(set(labB))}
df['_B'] = pd.Series(labB).map(matchB).values
orig = df.groupby('cluster')['amp_12m_norm'].mean()
recl = df.groupby('_B')['amp_12m_norm'].mean()
ariB = adjusted_rand_score(y, labB)

fig, axes = plt.subplots(1, 2, figsize=(9.0, 3.9))
# 좌: ARI 막대
ax = axes[0]
labels = ['편성목4\n(KMeans)', '편성목4+규모+추세\n(KMeans)',
          '비게임화6\nUMAP+HDBSCAN', '게임화6만\n(대조군)']
keys = ['(B) 편성목 4피처만 (KMeans)', '(A) 편성목4+규모+추세 (6, KMeans)',
        '(D) 편성목 6피처 UMAP+HDBSCAN', '(C) 게임화 6피처만 [대조군] (KMeans)']
vals = [ari_tbl.set_index('재군집 입력').loc[k, 'ARI'] for k in keys]
cols = [GRN, AMB, AMB, RED]
bars = ax.bar(range(4), vals, color=cols, width=0.62, edgecolor='white')
ax.axhline(0.6, ls='--', lw=1, color='#555')
ax.text(3.45, 0.62, '판정 기준 0.6', ha='right', fontsize=8, color='#555')
for i, v in enumerate(vals):
    ax.text(i, v + 0.02, f'{v:.3f}', ha='center', fontsize=9, fontweight='bold')
ax.set_xticks(range(4))
ax.set_xticklabels(labels, fontsize=7.5)
ax.set_ylim(0, 1.0)
ax.set_ylabel('ARI (원본 4원형 대비)')
ax.set_title('재군집 일치도 — 게임화 피처 없이도 원형 재현', fontsize=10.5, fontweight='bold')
ax.spines[['top', 'right']].set_visible(False)

# 우: amp_12m 원본 vs 편성목-only 재군집
ax = axes[1]
order = [0, 1, 2, 3]
x = np.arange(4)
ax.bar(x - 0.2, [orig[i] for i in order], 0.38, label='원본 4원형', color=ACC, edgecolor='white')
ax.bar(x + 0.2, [recl[i] for i in order], 0.38, label=f'편성목-only 재군집 (ARI={ariB:.2f})',
       color='#a9c1de', edgecolor='white')
ax.set_xticks(x)
ax.set_xticklabels([ARCH_KR[i] for i in order], fontsize=8.5)
ax.set_ylabel('12개월 진폭 amp_12m_norm (평균)')
ax.set_title('게임화 순위 보존 — 편성목만으로도 동일 순서', fontsize=10.5, fontweight='bold')
ax.legend(fontsize=8, loc='upper left')
ax.spines[['top', 'right']].set_visible(False)
fig.tight_layout()
savep(fig, 'robust_c4_recluster.png')


# ════════════════════════════════════════════════════════════════
# FIG C7 — 분야×원형 (활동수 가중 vs EP 가중)
# ════════════════════════════════════════════════════════════════
ct = pd.read_csv(os.path.join(RES, 'robust_c7_field_archetype_pct.csv'), index_col=0)
ctep = pd.read_csv(os.path.join(RES, 'robust_c7_field_archetype_ep_pct.csv'), index_col=0)
stats = pd.read_csv(os.path.join(RES, 'robust_c7_association_stats.csv')).set_index('metric')['value']
order_f = [f for f in ct.index if f != '예비비']           # drop n=1
cols4 = ['C0인건비', 'C1자산취득', 'C2출연금', 'C3정상']

fig, axes = plt.subplots(1, 2, figsize=(9.4, 4.6), sharey=True)
for ax, tab, ttl in [(axes[0], ct, '활동 수 가중'), (axes[1], ctep, 'EP(집행액) 가중')]:
    t = tab.loc[order_f, cols4]
    left = np.zeros(len(order_f))
    yy = np.arange(len(order_f))
    for c in cols4:
        ax.barh(yy, t[c].values, left=left, color=ARCH_COL[c], label=c,
                edgecolor='white', height=0.74)
        left += t[c].values
    ax.set_yticks(yy)
    tls = ax.set_yticklabels(order_f, fontsize=8)
    ax.set_xlim(0, 100)
    ax.set_xlabel('원형 구성비 (%)')
    ax.set_title(ttl, fontsize=10, fontweight='bold')
    ax.invert_yaxis()
    ax.spines[['top', 'right']].set_visible(False)
    # 사회복지 강조 (sharey라 좌축 라벨만 존재)
    if '사회복지' in order_f and len(tls) > order_f.index('사회복지'):
        idx = order_f.index('사회복지')
        tls[idx].set_color(RED)
        tls[idx].set_fontweight('bold')
axes[0].legend(ncol=4, fontsize=7.5, loc='upper center', bbox_to_anchor=(1.05, 1.12),
               frameon=False)
fig.suptitle(f"분야 × 사업원형 — 약한 연관 (Cramér's V={stats['cramers_v_corrected']:.2f}, "
             f"NMI={stats['nmi']:.3f}) · 16/16 분야 C3(정상) 다수 · 사회복지(빨강) 게임화원형 과소노출",
             fontsize=9.5, y=1.0)
fig.tight_layout(rect=[0, 0, 1, 0.96])
savep(fig, 'robust_c7_field_archetype.png')


# ════════════════════════════════════════════════════════════════
# FIG C6 — 사회복지 12월 집중도 + 월별 프로파일
# ════════════════════════════════════════════════════════════════
dec = pd.read_csv(os.path.join(RES, 'robust_c6_field_dec_share.csv'))
prof = pd.read_csv(os.path.join(RES, 'robust_c6_monthly_profile.csv'), index_col=0)
prof.columns = [int(c) for c in prof.columns]

fig, axes = plt.subplots(1, 2, figsize=(9.6, 4.0))
# 좌: 분야별 12월 중앙 비중
ax = axes[0]
d = dec.sort_values('dec_median_pct')
colors = [RED if f == '사회복지' else GRAY for f in d.FLD_NM]
ax.barh(range(len(d)), d.dec_median_pct, color=colors, height=0.74, edgecolor='white')
ax.axvline(100 / 12, ls='--', lw=1, color=ACC)
ax.text(100 / 12 + 0.3, 0.2, '균등 8.3%', fontsize=8, color=ACC)
ax.set_yticks(range(len(d)))
ax.set_yticklabels(d.FLD_NM, fontsize=7.5)
for i, (f, v) in enumerate(zip(d.FLD_NM, d.dec_median_pct)):
    if f == '사회복지':
        ax.text(v + 0.3, i, f'{v:.1f}%', va='center', fontsize=8.5, color=RED, fontweight='bold')
ax.set_xlabel('12월 집행 비중 중앙값 (%)')
ax.set_title('사회복지 12월 비중 = 균등(8.3%) 이하', fontsize=10.5, fontweight='bold')
ax.spines[['top', 'right']].set_visible(False)

# 우: 월별 프로파일 — 사회복지 vs 국방
ax = axes[1]
months = list(range(1, 13))
ax.plot(months, prof.loc['사회복지', months].values, '-o', color=RED, lw=2,
        markersize=4, label='사회복지 (평탄)')
if '국방' in prof.index:
    ax.plot(months, prof.loc['국방', months].values, '-s', color='#34495e', lw=1.6,
            markersize=4, label='국방 (12월 급증)')
ax.axhline(100 / 12, ls='--', lw=1, color=ACC)
ax.text(1, 100 / 12 + 0.4, '균등 8.3%', fontsize=8, color=ACC)
ax.set_xticks(months)
ax.set_xlabel('집행 월')
ax.set_ylabel('월별 집행 비중 (%)')
ax.set_title('사회복지 월별 평탄 (12월 11.3%, 점프 미미)', fontsize=10.5, fontweight='bold')
ax.legend(fontsize=8.5, loc='upper center')
ax.spines[['top', 'right']].set_visible(False)
fig.tight_layout()
savep(fig, 'robust_c6_socialwelfare.png')

print('완료.')
