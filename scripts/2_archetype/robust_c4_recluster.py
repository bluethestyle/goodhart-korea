"""견고성 검증 C4 — 군집 피처 부분 순환성.

질문: 게임화 유도 피처(amp_12m_norm·amp_6m_norm·hhi_period·q4_pct·dec_pct·cv_monthly)를
      빼고 편성목 구성비 4 + 규모 + 추세(6피처)만으로 재군집해도 같은 4 원형이 나오는가?

판정: ARI(재군집 vs 원본 4원형) ≳ 0.6 이면 "원형은 편성목 구조로 갈리며 게임화 피처
      없이도 재현됨 = 순환 아님". 낮으면 순환성 인정.

자기 정직성: 결과가 어느 쪽이든 수치를 먼저 보고 서술은 그 뒤에.

입력: data/results/H3_activity_embedding_11y.csv (12피처 + cluster 라벨, 1557행)
"""
import os, sys, io
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import (adjusted_rand_score, adjusted_mutual_info_score,
                             normalized_mutual_info_score, silhouette_score)
import umap
import hdbscan
import warnings

warnings.filterwarnings('ignore')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RES = os.path.join(ROOT, 'data', 'results')
df = pd.read_csv(os.path.join(RES, 'H3_activity_embedding_11y.csv'))

GAMING = ['amp_12m_norm', 'amp_6m_norm', 'hhi_period', 'q4_pct', 'dec_pct', 'cv_monthly']
BUDGET = ['chooyeon_pct', 'operating_pct', 'direct_invest_pct', 'personnel_pct']
SCALE_TREND = ['log_annual', 'growth_cagr']
NONGAMING = BUDGET + SCALE_TREND           # 6 피처 (게임화 유도 제외)
ALL12 = GAMING + BUDGET + SCALE_TREND

ARCH_KR = {0: 'C0 인건비형', 1: 'C1 자산취득형', 2: 'C2 출연금형', 3: 'C3 정상사업'}

y = df['cluster'].values   # 원본 4 원형 라벨 (0~3, 노이즈 없음)
print('=' * 72)
print('견고성 C4 — 편성목-only 재군집 vs 원본 4원형')
print('=' * 72)
print(f'활동 N = {len(df)},  원본 군집 분포: {dict(pd.Series(y).value_counts().sort_index())}')
print(f'  게임화 유도 피처(제외) {len(GAMING)}: {GAMING}')
print(f'  편성목 구성비 {len(BUDGET)}: {BUDGET}')
print(f'  규모·추세 {len(SCALE_TREND)}: {SCALE_TREND}')


def km4(feats, seed=42):
    X = StandardScaler().fit_transform(df[feats].values)
    return KMeans(n_clusters=4, n_init=25, random_state=seed).fit_predict(X), X


def cross(labels, title):
    ct = pd.crosstab(pd.Series(y, name='원본원형'), pd.Series(labels, name='재군집'))
    print(f'\n  [{title}] 교차표 (행=원본 원형, 열=재군집 라벨):')
    ct.index = [ARCH_KR.get(i, i) for i in ct.index]
    print(ct.to_string())


# ── (A) K-means k=4, 편성목+규모+추세 6피처 ──────────────────────
print('\n' + '-' * 72)
print('(A) K-means k=4 — 편성목 구성비 4 + 규모 + 추세 (6피처, 게임화 제외)')
print('-' * 72)
lab_A, X_A = km4(NONGAMING)
ari_A = adjusted_rand_score(y, lab_A)
ami_A = adjusted_mutual_info_score(y, lab_A)
nmi_A = normalized_mutual_info_score(y, lab_A)
print(f'  ARI = {ari_A:.3f}   AMI = {ami_A:.3f}   NMI = {nmi_A:.3f}')
cross(lab_A, 'A: 6피처 비게임화 K-means')

# ── (B) K-means k=4, 편성목 구성비 4피처만 ───────────────────────
print('\n' + '-' * 72)
print('(B) K-means k=4 — 편성목 구성비 4피처만 (규모·추세도 제외)')
print('-' * 72)
lab_B, _ = km4(BUDGET)
ari_B = adjusted_rand_score(y, lab_B)
print(f'  ARI = {ari_B:.3f}')
cross(lab_B, 'B: 4피처 편성목만 K-means')

# ── (C) K-means k=4, 게임화 유도 6피처만 (대조군 — 낮아야 정직) ──
print('\n' + '-' * 72)
print('(C) [대조군] K-means k=4 — 게임화 유도 6피처만')
print('   (낮으면: 원형은 게임화 피처가 아니라 편성목으로 갈린다는 직접 증거)')
print('-' * 72)
lab_C, _ = km4(GAMING)
ari_C = adjusted_rand_score(y, lab_C)
print(f'  ARI = {ari_C:.3f}')
cross(lab_C, 'C: 6피처 게임화만 K-means')

# ── (D) 원래 파이프라인 복제: StandardScaler→UMAP→HDBSCAN, 6피처 ─
print('\n' + '-' * 72)
print('(D) 원본 파이프라인 복제 — UMAP+HDBSCAN, 비게임화 6피처')
print('    (UMAP n_neighbors=30 min_dist=0.05 seed=42, HDBSCAN mcs=60 ms=10 eom)')
print('-' * 72)
Xd = StandardScaler().fit_transform(df[NONGAMING].values)
emb = umap.UMAP(n_neighbors=30, min_dist=0.05, metric='euclidean',
                n_components=2, random_state=42).fit_transform(Xd)
lab_D = hdbscan.HDBSCAN(min_cluster_size=60, min_samples=10,
                        cluster_selection_method='eom').fit_predict(emb)
n_cl = len(set(lab_D)) - (1 if -1 in lab_D else 0)
n_noise = int((lab_D == -1).sum())
print(f'  발견 군집 = {n_cl}, 노이즈 = {n_noise} ({n_noise/len(df)*100:.1f}%)')
mask = lab_D >= 0
ari_D = adjusted_rand_score(y[mask], lab_D[mask])
print(f'  ARI (노이즈 제외) = {ari_D:.3f}')
cross(lab_D, 'D: 6피처 비게임화 UMAP+HDBSCAN')

# ── (E) 사니티: K-means k=4 전체 12피처 vs 원본 ──────────────────
print('\n' + '-' * 72)
print('(E) [사니티] K-means k=4 — 전체 12피처 vs 원본 HDBSCAN 라벨')
print('-' * 72)
lab_E, _ = km4(ALL12)
ari_E = adjusted_rand_score(y, lab_E)
print(f'  ARI = {ari_E:.3f}  (K-means가 HDBSCAN 4원형을 얼마나 재현하나)')

# ── (F) 게임화 순위 보존: 비게임화 재군집(A) 각 군집의 게임화 측도 ─
print('\n' + '-' * 72)
print('(F) 게임화 순위 보존 — 비게임화 재군집(A) 군집별 게임화 측도 평균')
print('    원본 원형 순위(amp_12m: C2>C1>C3>C0 / dec_pct: C1 최고)가 보존되나?')
print('-' * 72)
df['_reA'] = lab_A
# A 군집을 원본과 매칭: 각 A군집의 다수 원본 라벨로 명명
match = {}
for a in sorted(set(lab_A)):
    dom = pd.Series(y[lab_A == a]).value_counts().idxmax()
    match[a] = dom
print(f'  A군집→원본 다수매칭: { {a: ARCH_KR[match[a]] for a in match} }')
df['_reA_arch'] = df['_reA'].map(match)
g = df.groupby('_reA_arch')[['amp_12m_norm', 'dec_pct', 'hhi_period']].mean().round(3)
g.index = [ARCH_KR.get(i, i) for i in g.index]
g['n'] = df.groupby('_reA_arch').size().values
print('\n  비게임화 재군집(매칭 후) 군집별 게임화 측도:')
print(g.to_string())
print('\n  [참조] 원본 4원형의 게임화 측도:')
g0 = df.groupby('cluster')[['amp_12m_norm', 'dec_pct', 'hhi_period']].mean().round(3)
g0.index = [ARCH_KR.get(i, i) for i in g0.index]
g0['n'] = df.groupby('cluster').size().values
print(g0.to_string())

# ── 요약 ────────────────────────────────────────────────────────
print('\n' + '=' * 72)
print('요약')
print('=' * 72)
summary = pd.DataFrame({
    '재군집 입력': ['(A) 편성목4+규모+추세 (6, KMeans)',
                   '(B) 편성목 4피처만 (KMeans)',
                   '(C) 게임화 6피처만 [대조군] (KMeans)',
                   '(D) 편성목 6피처 UMAP+HDBSCAN',
                   '(E) 전체 12피처 [사니티] (KMeans)'],
    'ARI': [round(ari_A, 3), round(ari_B, 3), round(ari_C, 3),
            round(ari_D, 3), round(ari_E, 3)],
})
print(summary.to_string(index=False))
print(f'\n  판정 기준: ARI ≳ 0.6 → 순환 아님 (편성목 구조로 재현)')
verdict = '통과 (순환 아님)' if ari_A >= 0.6 else ('경계' if ari_A >= 0.4 else '미통과 (순환성 인정)')
print(f'  (A) 비게임화 6피처 ARI = {ari_A:.3f} → 판정: {verdict}')
print(f'  대조군(C) 게임화-only ARI = {ari_C:.3f} '
      f'({"낮음 → 원형은 게임화가 아닌 편성목으로 갈림 (방어)" if ari_C < ari_A else "높음 → 주의"})')

# CSV 저장
out = os.path.join(RES, 'robust_c4_recluster_ari.csv')
summary.to_csv(out, index=False, encoding='utf-8-sig')
g.to_csv(os.path.join(RES, 'robust_c4_recluster_gaming_by_cluster.csv'), encoding='utf-8-sig')
print(f'\n  저장: {out}')
