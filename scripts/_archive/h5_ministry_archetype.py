"""H5: 부처 × 사업원형 이분그래프로 본 굿하트 노출 부처.

동기
  H3에서 부처를 12피처 평균으로 본 시그니처 그래프(5 커뮤니티)는 부처 평균만
  보았다. 이 평균은 부처 안에서 어떤 사업원형이 섞여있는지를 가린다.
  본 분석은 부처를 활동(1,641건)의 분포로 보고, H3 1차 클러스터(3개) +
  C2 sub-cluster(15개) = 18개 사업원형 위에서 부처 mix를 분석한다.

  H4에서 발견된 두 신호와 결합:
    - 출연금형(cluster 1): wealth_gini 부호 반전(+0.26)
    - sub5(극단 게임화 hhi z=+2.91), sub1(12월 잔금 z=+1.85)
  → 이 위험 원형들의 활동 비중을 부처별로 합산 = 굿하트 노출 점수

방법
  1. 부처 × 18원형 활동수 매트릭스
  2. SpectralCoclustering(n=5)로 부처/원형 동시 군집
  3. 위험 원형 가중치로 부처 노출 점수 계산
  4. 노출 점수 vs 부처 사업 규모 산점 / 상위 노출 부처 ranking

출력
  data/figs/h5/H5_bipartite_heatmap.png        부처×원형 매트릭스 (co-clustering 정렬)
  data/figs/h5/H5_exposure_ranking.png         부처별 노출 점수 막대
  data/figs/h5/H5_exposure_scatter.png         규모 vs 노출 산점
  data/results/H5_ministry_exposure.csv        부처별 노출 점수
  data/results/H5_cocluster_assignment.csv     부처/원형 co-cluster 라벨
"""
import os, sys, io, warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns
from sklearn.cluster import SpectralCoclustering

warnings.filterwarnings('ignore')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EMBED = os.path.join(ROOT, 'data', 'results', 'H3_activity_embedding.csv')
SUBE  = os.path.join(ROOT, 'data', 'results', 'H3_cluster2_subembedding.csv')
OUT_DIR = os.path.join(ROOT, 'data', 'figs', 'h5')
RES_DIR = os.path.join(ROOT, 'data', 'results')
os.makedirs(OUT_DIR, exist_ok=True)

KFONT = None
for f in ['Malgun Gothic','Noto Sans CJK KR','AppleGothic']:
    if any(f in fn.name for fn in mpl.font_manager.fontManager.ttflist):
        mpl.rcParams['font.family'] = f
        KFONT = f
        break
mpl.rcParams['axes.unicode_minus'] = False

# ============================================================
# Step 1: 데이터 로드 + 18원형 라벨 부여
# ============================================================
print('='*70)
print('Step 1: 활동 1,641건에 18 사업원형 라벨 부여')
print('='*70)

emb = pd.read_csv(EMBED)
sub = pd.read_csv(SUBE)
key_cols = ['FLD_NM','OFFC_NM','PGM_NM','ACTV_NM']
df = emb.merge(sub[key_cols + ['subcluster']], on=key_cols, how='left')
print(f'  활동 N = {len(df)}')
print(f'  cluster 0 (인건비) = {(df["cluster"]==0).sum()}')
print(f'  cluster 1 (출연금) = {(df["cluster"]==1).sum()}')
print(f'  cluster 2 (정상)   = {(df["cluster"]==2).sum()}, sub={df["subcluster"].notna().sum()}')

def archetype_label(row):
    if row['cluster'] == 0: return 'A0_personnel'
    if row['cluster'] == 1: return 'A1_chooyeon'
    sc = row['subcluster']
    if pd.isna(sc) or sc == -1: return 'A2_noise'
    return f'A2_sub{int(sc):02d}'

df['archetype'] = df.apply(archetype_label, axis=1)
print(f'\n  18 원형 + noise:')
print(df['archetype'].value_counts().sort_index().to_string())

# ============================================================
# Step 2: 부처 × 원형 매트릭스
# ============================================================
print('\n' + '='*70)
print('Step 2: 부처 × 원형 이분 행렬 (활동수)')
print('='*70)

M = pd.crosstab(df['OFFC_NM'], df['archetype'])
# 부처 활동수 ≥ 5
ofc_n = M.sum(axis=1)
M = M[ofc_n >= 5]
ofc_n = ofc_n[ofc_n >= 5]
# 원형 noise 제외 (분석 대상은 의미 있는 원형만)
keep_arch = [c for c in M.columns if c != 'A2_noise']
M = M[keep_arch]
print(f'  부처 N = {len(M)}, 원형 N = {len(M.columns)}')
print(f'  매트릭스 합계 = {int(M.values.sum()):,} 활동')

# ============================================================
# Step 3: Spectral Co-clustering
# ============================================================
print('\n' + '='*70)
print('Step 3: Spectral Co-clustering (부처-원형 동시 군집)')
print('='*70)

# 행/열 정규화 후 적용 (Bistochastic)
n_co = 5
sc_model = SpectralCoclustering(n_clusters=n_co, random_state=42)
sc_model.fit(M.values + 0.01)  # 안정성용 작은 상수

ofc_co = pd.Series(sc_model.row_labels_, index=M.index, name='ofc_co')
arc_co = pd.Series(sc_model.column_labels_, index=M.columns, name='arc_co')

print(f'  부처 co-cluster 분포:')
print(ofc_co.value_counts().sort_index().to_string())
print(f'  원형 co-cluster 분포:')
print(arc_co.value_counts().sort_index().to_string())

# 정렬용 인덱스 (co-cluster 순)
ofc_order = ofc_co.sort_values().index.tolist()
arc_order = arc_co.sort_values().index.tolist()
M_sorted = M.loc[ofc_order, arc_order]

# 각 co-cluster 요약
print('\n  Co-cluster 요약:')
for k in range(n_co):
    members_ofc = ofc_co[ofc_co==k].index.tolist()
    members_arc = arc_co[arc_co==k].index.tolist()
    if not members_ofc and not members_arc:
        continue
    sub_M = M.loc[members_ofc, members_arc] if members_ofc and members_arc else None
    n_act = int(sub_M.values.sum()) if sub_M is not None else 0
    print(f'  [CC{k}] 부처 {len(members_ofc)} / 원형 {len(members_arc)} / 활동 {n_act}')
    print(f'        부처: {members_ofc[:6]}{"..." if len(members_ofc)>6 else ""}')
    print(f'        원형: {members_arc}')

# ============================================================
# Step 4: 굿하트 노출 점수
# ============================================================
print('\n' + '='*70)
print('Step 4: 굿하트 노출 점수 (위험 원형 비중)')
print('='*70)
# 위험 원형 정의:
#   primary: A1_chooyeon (H4에서 wealth_gini 부호 반전)
#   secondary: A2_sub05 (극단 게임화 hhi z=+2.91)
#              A2_sub01 (12월 잔금 z=+1.85)
#              A2_sub04 (Q4/12월 z=+2.08/+2.19)
RISK = {
    'A1_chooyeon': 1.0,
    'A2_sub05':    0.9,
    'A2_sub01':    0.7,
    'A2_sub04':    0.6,
}
print(f'  위험 원형 가중치: {RISK}')

# 활동수 기반 노출 점수 (가중 합계 / 부처 총 활동수)
weights = pd.Series(0.0, index=M.columns)
for k, w in RISK.items():
    if k in weights.index:
        weights[k] = w
exposure_act = (M * weights).sum(axis=1) / ofc_n
exposure_act.name = 'exposure_score'

# 예산 가중 노출도 — H3 임베딩의 total_budget 사용
b_w = df.groupby(['OFFC_NM','archetype'])['total_budget'].sum().unstack(fill_value=0)
b_w = b_w.reindex(index=M.index, columns=M.columns).fillna(0)
b_total = b_w.sum(axis=1)
exposure_bdg = (b_w * weights).sum(axis=1) / b_total
exposure_bdg.name = 'exposure_budget'

result = pd.DataFrame({
    'n_actv': ofc_n,
    'exposure_score': exposure_act,
    'exposure_budget': exposure_bdg,
    'co_cluster': ofc_co,
    'pct_chooyeon': M['A1_chooyeon']/ofc_n if 'A1_chooyeon' in M.columns else 0,
    'pct_sub05':    M['A2_sub05']/ofc_n if 'A2_sub05' in M.columns else 0,
    'pct_sub01':    M['A2_sub01']/ofc_n if 'A2_sub01' in M.columns else 0,
}).sort_values('exposure_score', ascending=False)
print(f'\n  상위 12 노출 부처:')
print(result.head(12).round(3).to_string())
print(f'\n  하위 8 노출 부처:')
print(result.tail(8).round(3).to_string())

result.to_csv(os.path.join(RES_DIR, 'H5_ministry_exposure.csv'), encoding='utf-8-sig')

# Co-cluster 결과 저장
co_df = pd.concat([
    ofc_co.rename('label').to_frame().assign(node_type='ministry'),
    arc_co.rename('label').to_frame().assign(node_type='archetype'),
])
co_df.to_csv(os.path.join(RES_DIR, 'H5_cocluster_assignment.csv'), encoding='utf-8-sig')

# ============================================================
# Figure A: 부처×원형 heatmap (co-cluster 정렬)
# ============================================================
fig, ax = plt.subplots(figsize=(13, 13))
M_plot = np.log1p(M_sorted)
sns.heatmap(M_plot, cmap='YlOrRd', cbar_kws={'label':'log1p(활동수)'},
            ax=ax, linewidths=0.2, linecolor='#eeeeee')
# co-cluster 경계선
prev = -1
for i, ofc in enumerate(ofc_order):
    cur = ofc_co[ofc]
    if cur != prev and i > 0:
        ax.axhline(i, color='#0066cc', lw=1.0)
    prev = cur
prev = -1
for j, arc in enumerate(arc_order):
    cur = arc_co[arc]
    if cur != prev and j > 0:
        ax.axvline(j, color='#0066cc', lw=1.0)
    prev = cur
ax.set_title(f'부처 × 사업원형 (Spectral Co-clustering, {len(M)} ministry × {len(M.columns)} archetype)\n'
             f'파란선=co-cluster 경계 / 색=log(활동수)')
ax.set_xlabel('archetype')
ax.set_ylabel('ministry')
plt.tight_layout()
fig.savefig(os.path.join(OUT_DIR, 'H5_bipartite_heatmap.png'), dpi=130, bbox_inches='tight')
plt.close()

# ============================================================
# Figure B: 부처별 노출 점수 ranking (top 25)
# ============================================================
fig, ax = plt.subplots(figsize=(11, 9))
top = result.head(25).iloc[::-1]
y = np.arange(len(top))
ax.barh(y - 0.2, top['exposure_score'], height=0.4,
        color='#c84b3a', label='활동수 가중')
ax.barh(y + 0.2, top['exposure_budget'], height=0.4,
        color='#3a7fc8', label='예산 가중')
ax.set_yticks(y)
ax.set_yticklabels(top.index)
ax.set_xlabel('굿하트 노출 점수 (위험 원형 비중)')
ax.set_title('부처별 굿하트 노출 점수 — 상위 25\n'
             '위험 원형: A1 출연금형(+1.0), sub05 극단게임화(+0.9), sub01 12월잔금(+0.7), sub04 Q4집중(+0.6)')
ax.axvline(result['exposure_score'].median(), color='#888', ls='--', alpha=0.6,
           label=f'중앙값(활동) {result["exposure_score"].median():.3f}')
ax.legend()
ax.grid(alpha=0.3, axis='x')
plt.tight_layout()
fig.savefig(os.path.join(OUT_DIR, 'H5_exposure_ranking.png'), dpi=130, bbox_inches='tight')
plt.close()

# ============================================================
# Figure C: 부처 활동 규모 vs 노출 점수 산점
# ============================================================
fig, ax = plt.subplots(figsize=(11, 7.5))
palette = plt.get_cmap('tab10')
colors = [palette(int(ofc_co[m]) % 10) for m in result.index]
ax.scatter(result['n_actv'], result['exposure_score'],
           s=80 + 200*result['exposure_budget'],
           c=colors, alpha=0.75, edgecolors='black', linewidth=0.5)
# 라벨: 노출 상위 + 활동수 상위
to_label = set(result.head(15).index) | set(result.sort_values('n_actv', ascending=False).head(10).index)
for m in to_label:
    x = result.loc[m,'n_actv']; y = result.loc[m,'exposure_score']
    ax.annotate(m, (x, y), fontsize=8, alpha=0.85,
                xytext=(3,3), textcoords='offset points')
ax.set_xscale('log')
ax.set_xlabel('부처 활동수 (log)')
ax.set_ylabel('굿하트 노출 점수 (활동수 가중)')
ax.set_title('부처 규모 × 굿하트 노출 — 색=co-cluster, 크기=예산 가중 노출')
ax.grid(alpha=0.3)
plt.tight_layout()
fig.savefig(os.path.join(OUT_DIR, 'H5_exposure_scatter.png'), dpi=130, bbox_inches='tight')
plt.close()

# ============================================================
# Figure D: 위험 원형 4개 분포 boxplot (부처 co-cluster별)
# ============================================================
fig, axes = plt.subplots(1, 4, figsize=(15, 4.8), sharey=False)
for ax, k in zip(axes, ['A1_chooyeon','A2_sub05','A2_sub01','A2_sub04']):
    if k not in M.columns: continue
    pcts = (M[k] / ofc_n).rename('pct')
    pcts = pd.concat([pcts, ofc_co.rename('cc')], axis=1)
    sns.boxplot(data=pcts, x='cc', y='pct', ax=ax, palette='tab10')
    ax.set_title(f'{k} 비중 by 부처 co-cluster')
    ax.set_xlabel('co-cluster')
    ax.set_ylabel('비중')
    ax.grid(alpha=0.3, axis='y')
plt.tight_layout()
fig.savefig(os.path.join(OUT_DIR, 'H5_risk_archetype_box.png'), dpi=130, bbox_inches='tight')
plt.close()

print('\n=== 그림 ===')
for f in sorted(os.listdir(OUT_DIR)):
    print(f'  {f}')

print('\n완료.')
