"""H5 v2 (11y): 부처 × 사업원형 이분그래프로 본 굿하트 노출 부처 — 11년 4-클러스터 기준.

H3 v2 (11y) 변경 사항:
  - 4 cluster: C0=인건비, C1=자산취득(direct_invest), C2=출연금, C3=정상
  - C1(자산취득)이 5y 기준 C2_sub에서 신규 분리된 독립 클러스터
  - C2(출연금) → A2_chooyeon, sub0/sub1 두 하위 원형
  - C3(정상) → A3_normal (sub 없음)
  - 굿하트 위험: A2_chooyeon=1.0, A2_sub01=0.9(있다면), A1_direct_invest=0.7

출력
  data/figs/h5_11y/H5_bipartite_heatmap_11y.png
  data/figs/h5_11y/H5_exposure_ranking_11y.png
  data/figs/h5_11y/H5_exposure_scatter_11y.png
  data/figs/h5_11y/H5_risk_archetype_box_11y.png
  data/results/H5_ministry_exposure_11y.csv
  data/results/H5_cocluster_assignment_11y.csv
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

ROOT    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EMBED   = os.path.join(ROOT, 'data', 'results', 'H3_activity_embedding_11y.csv')
SUBE    = os.path.join(ROOT, 'data', 'results', 'H3_cluster2_subembedding_11y.csv')
OUT_DIR = os.path.join(ROOT, 'data', 'figs', 'h5_11y')
RES_DIR = os.path.join(ROOT, 'data', 'results')
os.makedirs(OUT_DIR, exist_ok=True)

# ── 한글 폰트 ────────────────────────────────────────────────
KFONT = None
for f in ['Malgun Gothic', 'Noto Sans CJK KR', 'AppleGothic']:
    if any(f in fn.name for fn in mpl.font_manager.fontManager.ttflist):
        mpl.rcParams['font.family'] = f
        KFONT = f
        break
mpl.rcParams['axes.unicode_minus'] = False
MAX_PX = 1800
DPI = 130

print('한글 폰트:', KFONT)

# ============================================================
# Step 1: 데이터 로드 + 사업원형 라벨 부여 (4-cluster 기준)
# ============================================================
print('='*70)
print('Step 1: 활동 1,557건에 사업원형 라벨 부여 (11y 4-cluster)')
print('='*70)

emb = pd.read_csv(EMBED)
sub = pd.read_csv(SUBE)
key_cols = ['FLD_NM', 'OFFC_NM', 'PGM_NM', 'ACTV_NM']
df = emb.merge(sub[key_cols + ['subcluster']], on=key_cols, how='left')

print(f'  활동 N = {len(df)}')
for c, name in [(0,'인건비'), (1,'자산취득'), (2,'출연금'), (3,'정상')]:
    print(f'  cluster {c} ({name}) = {(df["cluster"]==c).sum()}')

# ── 원형 라벨 ─────────────────────────────────────────────────
# C0 → A0_personnel
# C1 → A1_direct_invest  (5y에서 신규 분리된 자산취득형)
# C2 → A2_chooyeon + sub0/sub1 세분화
# C3 → A3_normal  (sub-cluster 없음)
def archetype_label(row):
    c = row['cluster']
    if c == 0:
        return 'A0_personnel'
    if c == 1:
        return 'A1_direct_invest'
    if c == 2:
        sc = row['subcluster']
        if pd.isna(sc) or sc == -1:
            return 'A2_chooyeon_noise'
        return f'A2_sub{int(sc):02d}'
    # c == 3
    return 'A3_normal'

df['archetype'] = df.apply(archetype_label, axis=1)
print(f'\n  원형 분포:')
print(df['archetype'].value_counts().sort_index().to_string())

# ============================================================
# Step 2: 부처 × 원형 매트릭스
# ============================================================
print('\n' + '='*70)
print('Step 2: 부처 × 원형 이분 행렬 (활동수)')
print('='*70)

M = pd.crosstab(df['OFFC_NM'], df['archetype'])

# 활동수 ≥ 5 부처만
ofc_n = M.sum(axis=1)
M = M[ofc_n >= 5]
ofc_n = ofc_n[ofc_n >= 5]

# noise 원형 제외
keep_arch = [c for c in M.columns if 'noise' not in c]
M = M[keep_arch]

print(f'  부처 N = {len(M)}, 원형 N = {len(M.columns)}')
print(f'  원형 목록: {M.columns.tolist()}')
print(f'  매트릭스 합계 = {int(M.values.sum()):,} 활동')

# ============================================================
# Step 3: Spectral Co-clustering (n=5)
# ============================================================
print('\n' + '='*70)
print('Step 3: Spectral Co-clustering (n=5)')
print('='*70)

n_co = 5
sc_model = SpectralCoclustering(n_clusters=n_co, random_state=42)
sc_model.fit(M.values + 0.01)

ofc_co = pd.Series(sc_model.row_labels_, index=M.index, name='ofc_co')
arc_co = pd.Series(sc_model.column_labels_, index=M.columns, name='arc_co')

print(f'  부처 co-cluster 분포:')
print(ofc_co.value_counts().sort_index().to_string())
print(f'  원형 co-cluster 분포:')
print(arc_co.value_counts().sort_index().to_string())

ofc_order = ofc_co.sort_values().index.tolist()
arc_order = arc_co.sort_values().index.tolist()
M_sorted = M.loc[ofc_order, arc_order]

print('\n  Co-cluster 요약:')
for k in range(n_co):
    members_ofc = ofc_co[ofc_co == k].index.tolist()
    members_arc = arc_co[arc_co == k].index.tolist()
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
print('Step 4: 굿하트 노출 점수')
print('='*70)

# 위험 원형 가중치 (11y 기준)
# A2_chooyeon = A2_sub00 + A2_sub01 합산 → 각 1.0/0.9
# A2_chooyeon_noise는 제외됨 (keep_arch에서 제거)
RISK = {}
if 'A2_sub01' in M.columns:
    RISK['A2_sub01'] = 0.9    # 출연금 sub01: 높은 위험
if 'A2_sub00' in M.columns:
    RISK['A2_sub00'] = 1.0    # 출연금 sub00: 최고 위험 (A2_chooyeon 대표)
if 'A1_direct_invest' in M.columns:
    RISK['A1_direct_invest'] = 0.7   # 자산취득형 신규
print(f'  위험 원형 가중치: {RISK}')

weights = pd.Series(0.0, index=M.columns)
for k, w in RISK.items():
    if k in weights.index:
        weights[k] = w

exposure_act = (M * weights).sum(axis=1) / ofc_n
exposure_act.name = 'exposure_score'

# 예산 가중 노출도
b_w = df.groupby(['OFFC_NM', 'archetype'])['total_budget'].sum().unstack(fill_value=0)
b_w = b_w.reindex(index=M.index, columns=M.columns).fillna(0)
b_total = b_w.sum(axis=1).replace(0, np.nan)
exposure_bdg = (b_w * weights).sum(axis=1) / b_total
exposure_bdg.name = 'exposure_budget'

pct_cols = {}
for arch in ['A2_sub00', 'A2_sub01', 'A1_direct_invest']:
    if arch in M.columns:
        pct_cols[f'pct_{arch}'] = M[arch] / ofc_n

result = pd.DataFrame({
    'n_actv': ofc_n,
    'exposure_score': exposure_act,
    'exposure_budget': exposure_bdg,
    'co_cluster': ofc_co,
    **pct_cols,
}).sort_values('exposure_score', ascending=False)

print(f'\n  상위 12 노출 부처:')
print(result.head(12).round(3).to_string())
print(f'\n  하위 8 노출 부처:')
print(result.tail(8).round(3).to_string())

result.to_csv(os.path.join(RES_DIR, 'H5_ministry_exposure_11y.csv'), encoding='utf-8-sig')

co_df = pd.concat([
    ofc_co.rename('label').to_frame().assign(node_type='ministry'),
    arc_co.rename('label').to_frame().assign(node_type='archetype'),
])
co_df.to_csv(os.path.join(RES_DIR, 'H5_cocluster_assignment_11y.csv'), encoding='utf-8-sig')

# ============================================================
# Figure A: 부처×원형 heatmap (co-cluster 정렬)  ≤ 1800px
# ============================================================
n_ofc = len(M_sorted)
n_arc = len(M_sorted.columns)
fig_h = min(1800 / DPI, max(8, n_ofc * 0.22))
fig_w = min(1800 / DPI, 14)

fig, ax = plt.subplots(figsize=(fig_w, fig_h))
M_plot = np.log1p(M_sorted)
sns.heatmap(M_plot, cmap='YlOrRd',
            cbar_kws={'label': 'log1p(활동수)'},
            ax=ax, linewidths=0.15, linecolor='#eeeeee',
            xticklabels=True, yticklabels=True)

# co-cluster 경계선
prev = -1
for i, ofc in enumerate(ofc_order):
    cur = ofc_co[ofc]
    if cur != prev and i > 0:
        ax.axhline(i, color='#0066cc', lw=1.2)
    prev = cur
prev = -1
for j, arc in enumerate(arc_order):
    cur = arc_co[arc]
    if cur != prev and j > 0:
        ax.axvline(j, color='#0066cc', lw=1.2)
    prev = cur

ax.set_title(
    f'부처 × 사업원형 이분그래프 (11y · 4-cluster)\n'
    f'Spectral Co-clustering n={n_co}  |  {n_ofc} 부처 × {n_arc} 원형  |  파란선=경계',
    fontsize=11
)
ax.set_xlabel('archetype', fontsize=10)
ax.set_ylabel('ministry', fontsize=10)
ax.tick_params(labelsize=7)
plt.tight_layout()
out_path = os.path.join(OUT_DIR, 'H5_bipartite_heatmap_11y.png')
fig.savefig(out_path, dpi=DPI, bbox_inches='tight')
plt.close()
print(f'  저장: {out_path}')

# ============================================================
# Figure B: 부처별 노출 점수 ranking (top 25)
# ============================================================
fig_w2 = min(1800/DPI, 12)
fig, ax = plt.subplots(figsize=(fig_w2, 9))
top = result.head(25).iloc[::-1]
y = np.arange(len(top))
ax.barh(y - 0.2, top['exposure_score'], height=0.38,
        color='#c84b3a', label='활동수 가중 노출')
ax.barh(y + 0.2, top['exposure_budget'], height=0.38,
        color='#3a7fc8', label='예산 가중 노출')
ax.set_yticks(y)
ax.set_yticklabels(top.index, fontsize=9)
ax.set_xlabel('굿하트 노출 점수 (위험 원형 비중)')
ax.set_title(
    '부처별 굿하트 노출 점수 — 상위 25 (11y)\n'
    '위험 원형: A2_sub00 출연금0(1.0), A2_sub01 출연금1(0.9), A1_direct_invest 자산취득(0.7)'
)
median_s = result['exposure_score'].median()
ax.axvline(median_s, color='#888', ls='--', alpha=0.7,
           label=f'중앙값 {median_s:.3f}')
ax.legend(fontsize=9)
ax.grid(alpha=0.3, axis='x')
plt.tight_layout()
out_path = os.path.join(OUT_DIR, 'H5_exposure_ranking_11y.png')
fig.savefig(out_path, dpi=DPI, bbox_inches='tight')
plt.close()
print(f'  저장: {out_path}')

# ============================================================
# Figure C: 부처 규모 vs 노출 산점
# ============================================================
fig, ax = plt.subplots(figsize=(min(1800/DPI, 12), 8))
palette = plt.get_cmap('tab10')
colors = [palette(int(ofc_co[m]) % 10) for m in result.index]
sizes  = 80 + 200 * result['exposure_budget'].fillna(0).clip(0, 1)
ax.scatter(result['n_actv'], result['exposure_score'],
           s=sizes, c=colors, alpha=0.75,
           edgecolors='black', linewidth=0.4)

to_label = (
    set(result.head(15).index) |
    set(result.sort_values('n_actv', ascending=False).head(10).index)
)
for m in to_label:
    xv = result.loc[m, 'n_actv']
    yv = result.loc[m, 'exposure_score']
    ax.annotate(m, (xv, yv), fontsize=8, alpha=0.85,
                xytext=(3, 3), textcoords='offset points')

ax.set_xscale('log')
ax.set_xlabel('부처 활동수 (log)')
ax.set_ylabel('굿하트 노출 점수 (활동수 가중)')
ax.set_title('부처 규모 × 굿하트 노출 — 색=co-cluster, 크기=예산 가중 노출 (11y)')
ax.grid(alpha=0.3)

# co-cluster 범례
for k in sorted(ofc_co.unique()):
    ax.scatter([], [], c=[palette(k % 10)], label=f'CC{k}', s=60)
ax.legend(title='co-cluster', fontsize=9)
plt.tight_layout()
out_path = os.path.join(OUT_DIR, 'H5_exposure_scatter_11y.png')
fig.savefig(out_path, dpi=DPI, bbox_inches='tight')
plt.close()
print(f'  저장: {out_path}')

# ============================================================
# Figure D: 위험 원형 분포 boxplot (부처 co-cluster별)
# ============================================================
risk_archs = [a for a in ['A2_sub00', 'A2_sub01', 'A1_direct_invest', 'A0_personnel']
              if a in M.columns]
n_box = len(risk_archs)
fig, axes = plt.subplots(1, n_box, figsize=(min(1800/DPI, 4.2*n_box), 5), sharey=False)
if n_box == 1:
    axes = [axes]

for ax, arch in zip(axes, risk_archs):
    pcts = (M[arch] / ofc_n).rename('pct')
    pdata = pd.concat([pcts, ofc_co.rename('cc')], axis=1)
    sns.boxplot(data=pdata, x='cc', y='pct', ax=ax,
                palette='tab10', order=sorted(ofc_co.unique()))
    ax.set_title(f'{arch}\n비중 by 부처 co-cluster', fontsize=9)
    ax.set_xlabel('co-cluster', fontsize=8)
    ax.set_ylabel('비중', fontsize=8)
    ax.grid(alpha=0.3, axis='y')

plt.suptitle('위험 원형별 부처 co-cluster 분포 (11y)', y=1.01, fontsize=11)
plt.tight_layout()
out_path = os.path.join(OUT_DIR, 'H5_risk_archetype_box_11y.png')
fig.savefig(out_path, dpi=DPI, bbox_inches='tight')
plt.close()
print(f'  저장: {out_path}')

# ============================================================
# 5y vs 11y 비교 요약 출력
# ============================================================
print('\n' + '='*70)
print('5y vs 11y 비교')
print('='*70)
print('  5y: 3 cluster (인건비/출연금/정상), 18 원형, 상위 노출=국무조정실 0.78')
print(f'  11y: 4 cluster (인건비/자산취득/출연금/정상), {len(M.columns)} 원형')
print(f'       신규: A1_direct_invest 자산취득형 독립 분리')
print(f'\n  11y 상위 10 노출 부처:')
print(result[['exposure_score','exposure_budget','n_actv','co_cluster']].head(10).round(3).to_string())

print('\n=== 저장된 그림 ===')
for f in sorted(os.listdir(OUT_DIR)):
    fpath = os.path.join(OUT_DIR, f)
    sz_kb = os.path.getsize(fpath) // 1024
    print(f'  {f}  ({sz_kb} KB)')

print('\n완료.')
