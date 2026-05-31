"""H4: Mapper(TDA) 위상 분석 + 활동 단위 outcome decoupling.

목적
  1. UMAP+HDBSCAN의 평면 클러스터 위에 Mapper로 위상 구조 추출
     → 클러스터 간 "다리(bridge)"·"분기(branch)"·"고리(loop)" 식별
  2. KOSIS outcome (5개 분야)을 활동에 broadcast → 클러스터별 outcome 시계열
  3. 클러스터별 game↔outcome 차분 상관관계 (H2의 활동 단위 확장)

입력
  data/results/H3_activity_embedding.csv
  data/warehouse.duckdb (indicator_panel - outcome metrics)

출력
  data/figs/h4/H4_mapper_graph.png
  data/figs/h4/H4_cluster_outcome_panel.png
  data/results/H4_mapper_nodes.csv
  data/results/H4_cluster_outcome_corr.csv
"""
import os, sys, io, warnings, json
import numpy as np
import pandas as pd
import duckdb
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
import kmapper as km
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns

warnings.filterwarnings('ignore')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, 'data', 'warehouse.duckdb')
H3_CSV = os.path.join(ROOT, 'data', 'results', 'H3_activity_embedding.csv')
OUT_DIR = os.path.join(ROOT, 'data', 'figs', 'h4')
RES_DIR = os.path.join(ROOT, 'data', 'results')
os.makedirs(OUT_DIR, exist_ok=True)

KFONT = None
for f in ['Malgun Gothic', 'Noto Sans CJK KR', 'AppleGothic']:
    if any(f in fn.name for fn in mpl.font_manager.fontManager.ttflist):
        mpl.rcParams['font.family'] = f
        KFONT = f
        break
mpl.rcParams['axes.unicode_minus'] = False

# ============================================================
# Step 1: 데이터 로드
# ============================================================
print('='*70)
print('Step 1: H3 임베딩 + outcome 데이터 로드')
print('='*70)
df = pd.read_csv(H3_CSV)
print(f'  활동 N = {len(df)}')

feat_cols = [
    'amp_12m_norm','amp_6m_norm','hhi_period','q4_pct','dec_pct','cv_monthly',
    'chooyeon_pct','operating_pct','direct_invest_pct','personnel_pct',
    'log_annual','growth_cagr',
]
X = StandardScaler().fit_transform(df[feat_cols].values)

con = duckdb.connect(DB, read_only=True)

# ============================================================
# Step 2: Mapper graph
# ============================================================
print('\n' + '='*70)
print('Step 2: Mapper graph (UMAP 2D filter, HDBSCAN-like cover/cluster)')
print('='*70)

# 이미 H3에서 만든 UMAP 좌표 사용 (재현성)
lens = df[['u1', 'u2']].values

mapper = km.KeplerMapper(verbose=0)

# 커버: 2D UMAP을 18x18 = 324 hypercube로 50% overlap
cover = km.Cover(n_cubes=18, perc_overlap=0.5)

# 각 큐브 내부 클러스터링: DBSCAN
clusterer = DBSCAN(eps=0.45, min_samples=4)

graph = mapper.map(
    lens=lens,
    X=X,
    cover=cover,
    clusterer=clusterer,
)

n_nodes = len(graph['nodes'])
n_edges = sum(len(v) for v in graph['links'].values()) // 1
print(f'  Mapper nodes = {n_nodes}, edges = {n_edges}')

# Mapper graph -> networkx
G = nx.Graph()
node_meta = {}
for nid, members in graph['nodes'].items():
    sub = df.iloc[members]
    G.add_node(nid, size=len(members))
    node_meta[nid] = {
        'size': len(members),
        'mean_amp_12m': float(sub['amp_12m_norm'].mean()),
        'mean_chooyeon': float(sub['chooyeon_pct'].mean()),
        'mean_dec': float(sub['dec_pct'].mean()),
        'mean_personnel': float(sub['personnel_pct'].mean()),
        'mean_direct_invest': float(sub['direct_invest_pct'].mean()),
        'cluster_dom': int(sub['cluster'].mode().iloc[0]),
        'top_field': sub['FLD_NM'].mode().iloc[0] if len(sub) > 0 else '',
        'fld_diversity': sub['FLD_NM'].nunique(),
    }
for nid, neighbors in graph['links'].items():
    for nb in neighbors:
        G.add_edge(nid, nb)

print(f'  네트워크: {G.number_of_nodes()} nodes / {G.number_of_edges()} edges')

# ============================================================
# Step 3: 위상 통계 (component, cycle basis, branch points)
# ============================================================
print('\n' + '='*70)
print('Step 3: Mapper 위상 통계')
print('='*70)
comps = list(nx.connected_components(G))
sizes = sorted([len(c) for c in comps], reverse=True)
print(f'  연결 성분 = {len(comps)}, 상위 5: {sizes[:5]}')

# 가장 큰 component 위에서 cycle basis = 1차 베티수 (loop 수)
LCC = G.subgraph(max(comps, key=len)).copy()
n_loops = LCC.number_of_edges() - LCC.number_of_nodes() + 1
print(f'  최대 컴포넌트: {LCC.number_of_nodes()} nodes, {LCC.number_of_edges()} edges')
print(f'  → 1차 베티수 (독립 루프 수) = {n_loops}')
print(f'  → 0차 베티수 (컴포넌트 수) = {len(comps)}')

# branch points: 도수 ≥ 3
deg = dict(LCC.degree())
branches = [n for n, d in deg.items() if d >= 3]
endpoints = [n for n, d in deg.items() if d == 1]
print(f'  분기점 (deg≥3) = {len(branches)}')
print(f'  말단 (deg=1) = {len(endpoints)}')

# ============================================================
# Step 4: outcome 적재 + 활동 broadcast
# ============================================================
print('\n' + '='*70)
print('Step 4: KOSIS outcome → 활동 broadcast')
print('='*70)

OUTCOME_FLD = {
    'wealth_gini':              ['사회복지'],
    'life_expectancy':          ['보건'],
    'rd_total':                 ['과학기술'],
    'industry_production_index':['산업·중소기업및에너지'],
    'tourists_sample':          ['문화및관광'],
}

oc = con.execute("""
    SELECT fld_nm, year, metric_code, value
    FROM indicator_panel
    WHERE metric_code IN ('wealth_gini','life_expectancy','rd_total',
                          'industry_production_index','tourists_sample')
""").fetchdf()

# H3는 활동 기준이고 outcome은 분야×연도. 우선 outcome을 분야 평균 시계열로 변환
# 그리고 활동→해당 분야 outcome 평균 (스칼라 한 개) 부여
oc_field = oc.groupby('fld_nm').agg(
    outcome_metric=('metric_code','first'),
    outcome_mean=('value','mean'),
    outcome_n=('value','count'),
).reset_index()
print(f'  outcome 분야 매핑:')
print(oc_field.to_string(index=False))

# 분야별 game↔outcome 시계열 차분 상관 (H2에서 만든 것을 다시 클러스터별로)
# 활동의 mean_annual 기반 시계열은 H3 데이터에 없음. 분야 단위로 game 시계열 추출
print('\n  분야 단위 amp_12m 시계열 + outcome 시계열:')
panel = con.execute("""
    SELECT fld_nm, year, metric_code, value
    FROM indicator_panel
    WHERE metric_code IN ('amp_12m_norm','wealth_gini','life_expectancy',
                          'rd_total','industry_production_index','tourists_sample')
""").fetchdf()
wide = panel.pivot_table(index=['fld_nm','year'], columns='metric_code',
                         values='value').reset_index()

# ============================================================
# Step 5: 클러스터별 outcome 평균 + 차분 상관
# ============================================================
print('\n' + '='*70)
print('Step 5: 클러스터별 outcome 진동 (분야 가중평균)')
print('='*70)

# 각 1차 클러스터의 분야별 활동 비중
clu_fld = pd.crosstab(df['cluster'], df['FLD_NM'], normalize='index')
print(f'  cluster × field weight:')
print(clu_fld.round(2).to_string())

# 분야별 amp_12m 시계열 ↔ 클러스터 가중 평균 시계열
years = sorted(wide['year'].unique())
clusters = sorted(df['cluster'].unique())

cluster_amp_ts = {}    # cluster -> {year: amp_12m_weighted}
cluster_oc_ts  = {}    # cluster -> {(metric, year): value_weighted}

for cl in clusters:
    weights = clu_fld.loc[cl]
    amp_w = []
    for y in years:
        sub = wide[wide['year']==y].set_index('fld_nm')
        if 'amp_12m_norm' not in sub.columns: continue
        v = sub['amp_12m_norm'].reindex(weights.index).fillna(np.nan)
        # 결측 제외 가중평균
        valid = ~v.isna()
        if valid.sum() == 0:
            amp_w.append(np.nan); continue
        w = weights[valid]; w = w/w.sum()
        amp_w.append(float((v[valid] * w).sum()))
    cluster_amp_ts[cl] = pd.Series(amp_w, index=years)

# outcome metric별 시계열도 동일
oc_metrics = ['wealth_gini','life_expectancy','rd_total','industry_production_index','tourists_sample']
oc_results = []
for cl in clusters:
    weights = clu_fld.loc[cl]
    for m in oc_metrics:
        if m not in wide.columns: continue
        ts = []
        ys = []
        for y in years:
            sub = wide[wide['year']==y].set_index('fld_nm')
            if m not in sub.columns: continue
            v = sub[m].reindex(weights.index).fillna(np.nan)
            valid = ~v.isna()
            if valid.sum() == 0: continue
            w = weights[valid]; w = w/w.sum()
            ts.append(float((v[valid] * w).sum()))
            ys.append(y)
        if len(ts) < 4: continue
        # 시간 정렬
        s = pd.Series(ts, index=ys).sort_index()
        # amp_12m 시계열도 같은 연도로
        amp = cluster_amp_ts[cl].reindex(s.index).dropna()
        s = s.loc[amp.index]
        if len(s) < 4: continue
        # 1차 차분 상관
        d_amp = amp.diff().dropna()
        d_oc  = s.diff().dropna()
        common = d_amp.index.intersection(d_oc.index)
        if len(common) < 3: continue
        corr_lvl = float(amp.corr(s))
        corr_diff = float(d_amp[common].corr(d_oc[common]))
        oc_results.append({
            'cluster': cl,
            'metric': m,
            'n_year': len(s),
            'corr_levels': corr_lvl,
            'corr_diff': corr_diff,
            'amp_mean': float(amp.mean()),
            'oc_mean':  float(s.mean()),
        })

oc_corr = pd.DataFrame(oc_results)
print('\n  클러스터별 outcome 차분 상관 (분야 가중):')
print(oc_corr.round(3).to_string(index=False))

# ============================================================
# Step 6: 저장
# ============================================================
print('\n' + '='*70)
print('Step 6: 저장')
print('='*70)
node_df = pd.DataFrame.from_dict(node_meta, orient='index')
node_df.index.name = 'node_id'
node_df.reset_index().to_csv(os.path.join(RES_DIR, 'H4_mapper_nodes.csv'),
                              index=False, encoding='utf-8-sig')
print(f'  Mapper nodes csv: H4_mapper_nodes.csv ({len(node_df)})')
oc_corr.to_csv(os.path.join(RES_DIR, 'H4_cluster_outcome_corr.csv'),
               index=False, encoding='utf-8-sig')
print(f'  cluster outcome corr csv: H4_cluster_outcome_corr.csv')

# ============================================================
# Figure A: Mapper graph (size=members, color=mean_amp_12m or cluster_dom)
# ============================================================
fig, axes = plt.subplots(1, 2, figsize=(16, 7.5))
pos = nx.spring_layout(G, seed=42, k=0.4, iterations=200)

ax = axes[0]
sizes_arr = np.array([G.nodes[n]['size'] for n in G.nodes()])
colors = np.array([node_meta[n]['mean_amp_12m'] for n in G.nodes()])
nx.draw_networkx_edges(G, pos, alpha=0.3, width=0.6, ax=ax)
sc = nx.draw_networkx_nodes(G, pos, node_size=20+5*sizes_arr,
                             node_color=colors, cmap='RdBu_r',
                             vmin=0, vmax=df['amp_12m_norm'].quantile(0.9),
                             alpha=0.85, ax=ax)
ax.set_title(f'Mapper graph — color=평균 amp_12m_norm\n'
             f'{G.number_of_nodes()} nodes, {G.number_of_edges()} edges, '
             f'components={len(comps)}, loops={n_loops}')
ax.axis('off')
fig.colorbar(sc, ax=ax, label='amp_12m_norm', shrink=0.7)

ax = axes[1]
palette = plt.get_cmap('tab10')
clu_colors = [palette(node_meta[n]['cluster_dom'] % 10) for n in G.nodes()]
nx.draw_networkx_edges(G, pos, alpha=0.3, width=0.6, ax=ax)
nx.draw_networkx_nodes(G, pos, node_size=20+5*sizes_arr,
                       node_color=clu_colors, alpha=0.85, ax=ax)
# 분기점 label
top_branch = sorted(branches, key=lambda n: -G.nodes[n]['size'])[:6]
nx.draw_networkx_labels(G, pos, labels={n: node_meta[n]['top_field'] for n in top_branch},
                        font_size=7, font_family=KFONT or 'sans-serif', ax=ax)
ax.set_title(f'Mapper graph — color=H3 1차 클러스터 (0:인건비/1:출연금/2:정상)\n'
             f'분기점(deg≥3)={len(branches)}, 말단={len(endpoints)}')
ax.axis('off')
plt.tight_layout()
fig.savefig(os.path.join(OUT_DIR, 'H4_mapper_graph.png'), dpi=130, bbox_inches='tight')
plt.close()

# ============================================================
# Figure B: 클러스터별 outcome 시계열 + 차분 상관 막대
# ============================================================
fig, axes = plt.subplots(2, 2, figsize=(15, 9))
# (top) cluster 별 amp_12m 가중 시계열
ax = axes[0,0]
for cl in clusters:
    s = cluster_amp_ts[cl].dropna()
    ax.plot(s.index, s.values, marker='o', label=f'cluster {cl}')
ax.set_title('클러스터별 amp_12m 가중평균 시계열 (분야 가중)')
ax.set_xlabel('year'); ax.set_ylabel('amp_12m_norm')
ax.legend(); ax.grid(alpha=0.3)

# (top right) outcome metric별 클러스터 corr_diff
ax = axes[0,1]
if len(oc_corr) > 0:
    pv = oc_corr.pivot(index='metric', columns='cluster', values='corr_diff')
    sns.heatmap(pv, annot=True, fmt='.2f', cmap='RdBu_r', center=0, ax=ax,
                cbar_kws={'label':'corr (1차 차분)'})
    ax.set_title('클러스터 × outcome 차분 상관')

# (bottom left) component size dist
ax = axes[1,0]
sizes_dist = sorted([len(c) for c in comps], reverse=True)
ax.bar(range(len(sizes_dist)), sizes_dist, color='#5475a8')
ax.set_yscale('log')
ax.set_title(f'Mapper 연결 성분 크기 분포 ({len(comps)}개)')
ax.set_xlabel('component rank'); ax.set_ylabel('node 수 (log)')
ax.grid(alpha=0.3)

# (bottom right) 분기점/말단 표시 - 도수 분포
ax = axes[1,1]
deg_full = dict(G.degree())
deg_dist = pd.Series(list(deg_full.values())).value_counts().sort_index()
ax.bar(deg_dist.index, deg_dist.values, color='#c87f5a')
ax.set_title(f'Mapper 노드 도수 분포 (분기점 deg≥3 = {len([d for d in deg_full.values() if d>=3])})')
ax.set_xlabel('degree'); ax.set_ylabel('node 수')
ax.grid(alpha=0.3)

plt.tight_layout()
fig.savefig(os.path.join(OUT_DIR, 'H4_cluster_outcome_panel.png'), dpi=130, bbox_inches='tight')
plt.close()

# ============================================================
# Figure C: H3 1차 클러스터별 dominant top field/대표 prog 라벨링된 Mapper
# ============================================================
fig, ax = plt.subplots(figsize=(13, 9))
nx.draw_networkx_edges(G, pos, alpha=0.25, width=0.5, ax=ax)
size_arr = np.array([G.nodes[n]['size'] for n in G.nodes()])
chooyeon_arr = np.array([node_meta[n]['mean_chooyeon'] for n in G.nodes()])
sc = nx.draw_networkx_nodes(G, pos, node_size=15+4*size_arr,
                             node_color=chooyeon_arr, cmap='Reds',
                             vmin=0, vmax=0.6, alpha=0.85, ax=ax)
fig.colorbar(sc, ax=ax, label='평균 chooyeon_pct', shrink=0.7)
# 분기점 라벨
top_branches = sorted(branches, key=lambda n: -G.nodes[n]['size'])[:10]
nx.draw_networkx_labels(G, pos, labels={n:node_meta[n]['top_field'] for n in top_branches},
                        font_size=8, font_family=KFONT or 'sans-serif', ax=ax)
ax.set_title('Mapper — 출연금 비중 + 분기점 분야 라벨')
ax.axis('off')
plt.tight_layout()
fig.savefig(os.path.join(OUT_DIR, 'H4_mapper_chooyeon.png'), dpi=130, bbox_inches='tight')
plt.close()

print('\n=== 그림 ===')
for f in sorted(os.listdir(OUT_DIR)):
    print(f'  {f}')

con.close()
print('\n완료.')
