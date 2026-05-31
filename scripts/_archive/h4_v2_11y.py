"""H4 v2: Mapper(TDA) 위상 분석 + 활동 단위 outcome decoupling (11y 기준).

목적
  1. UMAP+HDBSCAN의 평면 클러스터 위에 Mapper로 위상 구조 추출
     → 클러스터 간 "다리(bridge)"·"분기(branch)"·"고리(loop)" 식별
  2. KOSIS outcome (12개 분야)을 활동에 broadcast → 클러스터별 outcome 시계열
  3. 클러스터별 game↔outcome 차분 상관관계 (4 cluster × 12 outcome matrix)

입력
  data/results/H3_activity_embedding_11y.csv  (1,557 활동, 4 cluster)
  data/warehouse.duckdb (indicator_panel - outcome metrics)

출력
  data/figs/h4_11y/H4_mapper_graph_11y.png
  data/figs/h4_11y/H4_cluster_outcome_panel_11y.png
  data/figs/h4_11y/H4_mapper_chooyeon_11y.png
  data/results/H4_mapper_nodes_11y.csv
  data/results/H4_cluster_outcome_corr_11y.csv

클러스터 레이블 (11y v2)
  0 = 인건비형   1 = 자산취득형   2 = 출연금형   3 = 정상형
"""
import os, sys, io, warnings
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
from PIL import Image

warnings.filterwarnings('ignore')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB      = os.path.join(ROOT, 'data', 'warehouse.duckdb')
H3_CSV  = os.path.join(ROOT, 'data', 'results', 'H3_activity_embedding_11y.csv')
OUT_DIR = os.path.join(ROOT, 'data', 'figs', 'h4_11y')
RES_DIR = os.path.join(ROOT, 'data', 'results')
os.makedirs(OUT_DIR, exist_ok=True)

# 한글 폰트
KFONT = None
for f in ['Malgun Gothic', 'Noto Sans CJK KR', 'AppleGothic']:
    if any(f in fn.name for fn in mpl.font_manager.fontManager.ttflist):
        mpl.rcParams['font.family'] = f
        KFONT = f
        break
mpl.rcParams['axes.unicode_minus'] = False

MAX_PX = 1800  # 최대 픽셀

def save_and_resize(fig, path, dpi=130):
    """저장 후 1800px 초과 시 PIL로 리사이즈."""
    fig.savefig(path, dpi=dpi, bbox_inches='tight')
    plt.close(fig)
    img = Image.open(path)
    w, h = img.size
    if max(w, h) > MAX_PX:
        scale = MAX_PX / max(w, h)
        img = img.resize((int(w*scale), int(h*scale)), Image.LANCZOS)
        img.save(path)
        print(f'  [resize] {os.path.basename(path)}: {w}×{h} → {img.size[0]}×{img.size[1]}')
    else:
        print(f'  [ok] {os.path.basename(path)}: {w}×{h}')

# ============================================================
# 12개 분야 × outcome metric 매핑
# ============================================================
OUTCOME_METRICS = [
    'wealth_gini',
    'life_expectancy',
    'rd_total',
    'industry_production_index',
    'tourists_sample',
    'private_edu_hours',
    'housing_supply',
    'local_tax_per_capita',
    'farm_income',
    'traffic_deaths',
    'ghg_total',
    'ict_value_added',
]
OUTCOME_LABEL = {
    'wealth_gini':              '사회복지(지니)',
    'life_expectancy':          '보건(기대수명)',
    'rd_total':                 '과학기술(R&D)',
    'industry_production_index':'산업(생산지수)',
    'tourists_sample':          '문화관광(관광객)',
    'private_edu_hours':        '교육(사교육시간)',
    'housing_supply':           '국토(주택공급)',
    'local_tax_per_capita':     '일반행정(지방세)',
    'farm_income':              '농림수산(농가소득)',
    'traffic_deaths':           '교통(사망자)',
    'ghg_total':                '환경(온실가스)',
    'ict_value_added':          '통신(ICT부가)',
}

# 클러스터 레이블 (11y v2)
CLU_LABEL = {0:'인건비형', 1:'자산취득형', 2:'출연금형', 3:'정상형'}

# ============================================================
# Step 1: 데이터 로드
# ============================================================
print('='*70)
print('Step 1: H3 11y 임베딩 + outcome 데이터 로드')
print('='*70)
df = pd.read_csv(H3_CSV)
print(f'  활동 N = {len(df)}')
print(f'  cluster 분포:')
for cl, n in df['cluster'].value_counts().sort_index().items():
    print(f'    cluster {cl} ({CLU_LABEL.get(cl,"?")}) : {n}')

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
print('Step 2: Mapper graph (UMAP 2D filter, DBSCAN cover/cluster)')
print('='*70)

lens = df[['u1', 'u2']].values

mapper = km.KeplerMapper(verbose=0)

# 커버: 18×18, 50% overlap
cover = km.Cover(n_cubes=18, perc_overlap=0.5)

# 각 큐브 내부 클러스터링: DBSCAN (eps=0.45, min_samples=4)
clusterer = DBSCAN(eps=0.45, min_samples=4)

graph = mapper.map(
    lens=lens,
    X=X,
    cover=cover,
    clusterer=clusterer,
)

n_nodes = len(graph['nodes'])
n_edges = sum(len(v) for v in graph['links'].values())
print(f'  Mapper nodes = {n_nodes}, edges = {n_edges}')

# Mapper graph -> networkx
G = nx.Graph()
node_meta = {}
for nid, members in graph['nodes'].items():
    sub = df.iloc[members]
    G.add_node(nid, size=len(members))
    node_meta[nid] = {
        'size':               len(members),
        'mean_amp_12m':       float(sub['amp_12m_norm'].mean()),
        'mean_chooyeon':      float(sub['chooyeon_pct'].mean()),
        'mean_dec':           float(sub['dec_pct'].mean()),
        'mean_personnel':     float(sub['personnel_pct'].mean()),
        'mean_direct_invest': float(sub['direct_invest_pct'].mean()),
        'cluster_dom':        int(sub['cluster'].mode().iloc[0]),
        'top_field':          sub['FLD_NM'].mode().iloc[0] if len(sub) > 0 else '',
        'fld_diversity':      sub['FLD_NM'].nunique(),
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

# 최대 component → 1차 베티수
LCC = G.subgraph(max(comps, key=len)).copy()
n_loops = LCC.number_of_edges() - LCC.number_of_nodes() + 1
print(f'  최대 컴포넌트: {LCC.number_of_nodes()} nodes, {LCC.number_of_edges()} edges')
print(f'  → 1차 베티수 (독립 루프 수) = {n_loops}')
print(f'  → 0차 베티수 (컴포넌트 수) = {len(comps)}')

deg = dict(LCC.degree())
branches  = [n for n, d in deg.items() if d >= 3]
endpoints = [n for n, d in deg.items() if d == 1]
print(f'  분기점 (deg≥3) = {len(branches)}')
print(f'  말단 (deg=1) = {len(endpoints)}')

# ============================================================
# Step 4: outcome 데이터 로드 (12 metrics)
# ============================================================
print('\n' + '='*70)
print('Step 4: KOSIS outcome (12 분야) → 활동 broadcast')
print('='*70)

metrics_sql = "','".join(OUTCOME_METRICS)
panel = con.execute(f"""
    SELECT fld_nm, year, metric_code, value
    FROM indicator_panel
    WHERE metric_code IN ('amp_12m_norm','{metrics_sql}')
""").fetchdf()

wide = panel.pivot_table(index=['fld_nm','year'], columns='metric_code',
                         values='value').reset_index()
print(f'  wide table: {wide.shape}')
print(f'  연도 범위: {wide["year"].min()} ~ {wide["year"].max()}')
print(f'  분야 수: {wide["fld_nm"].nunique()}')

# ============================================================
# Step 5: 클러스터별 outcome 차분 상관 (4 cluster × 12 outcome)
# ============================================================
print('\n' + '='*70)
print('Step 5: 클러스터별 outcome 진동 (분야 가중평균) — 4×12 matrix')
print('='*70)

# 각 클러스터의 분야별 활동 비중
clu_fld = pd.crosstab(df['cluster'], df['FLD_NM'], normalize='index')
print('  cluster × field weight (상위 분야):')
print(clu_fld.round(3).to_string())

years    = sorted(wide['year'].unique())
clusters = sorted(df['cluster'].unique())

cluster_amp_ts = {}

for cl in clusters:
    weights = clu_fld.loc[cl]
    amp_w   = []
    for y in years:
        sub = wide[wide['year']==y].set_index('fld_nm')
        if 'amp_12m_norm' not in sub.columns:
            amp_w.append(np.nan); continue
        v = sub['amp_12m_norm'].reindex(weights.index).fillna(np.nan)
        valid = ~v.isna()
        if valid.sum() == 0:
            amp_w.append(np.nan); continue
        w = weights[valid]; w = w / w.sum()
        amp_w.append(float((v[valid] * w).sum()))
    cluster_amp_ts[cl] = pd.Series(amp_w, index=years)

oc_results = []
for cl in clusters:
    weights = clu_fld.loc[cl]
    for m in OUTCOME_METRICS:
        if m not in wide.columns:
            continue
        ts, ys = [], []
        for y in years:
            sub = wide[wide['year']==y].set_index('fld_nm')
            if m not in sub.columns:
                continue
            v = sub[m].reindex(weights.index).fillna(np.nan)
            valid = ~v.isna()
            if valid.sum() == 0:
                continue
            w = weights[valid]; w = w / w.sum()
            ts.append(float((v[valid] * w).sum()))
            ys.append(y)
        if len(ts) < 4:
            continue
        s   = pd.Series(ts, index=ys).sort_index()
        amp = cluster_amp_ts[cl].reindex(s.index).dropna()
        s   = s.loc[amp.index]
        if len(s) < 4:
            continue
        d_amp = amp.diff().dropna()
        d_oc  = s.diff().dropna()
        common = d_amp.index.intersection(d_oc.index)
        if len(common) < 3:
            continue
        oc_results.append({
            'cluster':     cl,
            'clu_label':   CLU_LABEL.get(cl, str(cl)),
            'metric':      m,
            'metric_label':OUTCOME_LABEL.get(m, m),
            'n_year':      len(s),
            'corr_levels': float(amp.corr(s)),
            'corr_diff':   float(d_amp[common].corr(d_oc[common])),
            'amp_mean':    float(amp.mean()),
            'oc_mean':     float(s.mean()),
        })

oc_corr = pd.DataFrame(oc_results)
print('\n  클러스터 × outcome 차분 상관 (4×12 matrix):')
if len(oc_corr) > 0:
    pv = oc_corr.pivot(index='metric', columns='cluster', values='corr_diff')
    pv.columns = [f'{c}({CLU_LABEL.get(c,"?")})' for c in pv.columns]
    print(pv.round(3).to_string())

# ============================================================
# Step 6: CSV 저장
# ============================================================
print('\n' + '='*70)
print('Step 6: CSV 저장')
print('='*70)

node_df = pd.DataFrame.from_dict(node_meta, orient='index')
node_df.index.name = 'node_id'
node_df.reset_index().to_csv(
    os.path.join(RES_DIR, 'H4_mapper_nodes_11y.csv'),
    index=False, encoding='utf-8-sig')
print(f'  Mapper nodes csv: H4_mapper_nodes_11y.csv ({len(node_df)} nodes)')

oc_corr.to_csv(
    os.path.join(RES_DIR, 'H4_cluster_outcome_corr_11y.csv'),
    index=False, encoding='utf-8-sig')
print(f'  cluster outcome corr csv: H4_cluster_outcome_corr_11y.csv ({len(oc_corr)} rows)')

# ============================================================
# Figure A: Mapper graph (amp_12m 색상 + 클러스터 색상)
# ============================================================
pos = nx.spring_layout(G, seed=42, k=0.4, iterations=200)
sizes_arr = np.array([G.nodes[n]['size'] for n in G.nodes()])

fig, axes = plt.subplots(1, 2, figsize=(15, 7))

# 왼쪽: amp_12m_norm 색상
ax = axes[0]
colors = np.array([node_meta[n]['mean_amp_12m'] for n in G.nodes()])
nx.draw_networkx_edges(G, pos, alpha=0.3, width=0.6, ax=ax)
sc = nx.draw_networkx_nodes(G, pos, node_size=20+5*sizes_arr,
                             node_color=colors, cmap='RdBu_r',
                             vmin=0, vmax=df['amp_12m_norm'].quantile(0.9),
                             alpha=0.85, ax=ax)
ax.set_title(
    f'Mapper graph (11y) — color=평균 amp_12m_norm\n'
    f'{G.number_of_nodes()} nodes, {G.number_of_edges()} edges, '
    f'components={len(comps)}, loops={n_loops}',
    fontsize=10
)
ax.axis('off')
fig.colorbar(sc, ax=ax, label='amp_12m_norm', shrink=0.7)

# 오른쪽: 4 클러스터 색상
ax = axes[1]
palette = plt.get_cmap('tab10')
clu_colors = [palette(node_meta[n]['cluster_dom'] % 10) for n in G.nodes()]
nx.draw_networkx_edges(G, pos, alpha=0.3, width=0.6, ax=ax)
nx.draw_networkx_nodes(G, pos, node_size=20+5*sizes_arr,
                       node_color=clu_colors, alpha=0.85, ax=ax)
# 분기점 상위 6개 라벨
top_branch = sorted(branches, key=lambda n: -G.nodes[n]['size'])[:6]
nx.draw_networkx_labels(G, pos,
                        labels={n: node_meta[n]['top_field'] for n in top_branch},
                        font_size=7, font_family=KFONT or 'sans-serif', ax=ax)
# 범례
from matplotlib.patches import Patch
legend_elems = [Patch(facecolor=palette(cl), label=f'{cl}:{CLU_LABEL.get(cl,"?")}')
                for cl in sorted(CLU_LABEL.keys())]
ax.legend(handles=legend_elems, loc='lower right', fontsize=8)
ax.set_title(
    f'Mapper graph (11y) — color=H3 클러스터\n'
    f'0:인건비/1:자산취득/2:출연금/3:정상  |  분기점={len(branches)}, 말단={len(endpoints)}',
    fontsize=10
)
ax.axis('off')
plt.tight_layout()
save_and_resize(fig, os.path.join(OUT_DIR, 'H4_mapper_graph_11y.png'))

# ============================================================
# Figure B: 클러스터별 outcome 차분 상관 패널
# ============================================================
fig, axes = plt.subplots(2, 2, figsize=(15, 9))

# (상단 좌) 클러스터별 amp_12m 가중 시계열
ax = axes[0, 0]
for cl in clusters:
    s = cluster_amp_ts[cl].dropna()
    ax.plot(s.index, s.values, marker='o', label=f'{cl}:{CLU_LABEL.get(cl,"?")}')
ax.set_title('클러스터별 amp_12m 가중평균 시계열 (11y, 분야 가중)', fontsize=10)
ax.set_xlabel('year'); ax.set_ylabel('amp_12m_norm')
ax.legend(fontsize=8); ax.grid(alpha=0.3)

# (상단 우) 4×12 outcome 차분 상관 히트맵
ax = axes[0, 1]
if len(oc_corr) > 0:
    pv = oc_corr.pivot(index='metric_label', columns='cluster', values='corr_diff')
    pv.columns = [f'{c}:{CLU_LABEL.get(c,"?")}' for c in pv.columns]
    sns.heatmap(pv, annot=True, fmt='.2f', cmap='RdBu_r', center=0, ax=ax,
                cbar_kws={'label': 'corr(1차 차분)'}, annot_kws={'size': 8})
    ax.set_title('클러스터 × outcome 차분 상관 (12 outcome × 4 cluster)', fontsize=10)
    ax.set_xlabel('cluster'); ax.set_ylabel('outcome metric')
    ax.tick_params(axis='x', labelsize=8)
    ax.tick_params(axis='y', labelsize=8)

# (하단 좌) component 크기 분포
ax = axes[1, 0]
sizes_dist = sorted([len(c) for c in comps], reverse=True)
ax.bar(range(len(sizes_dist)), sizes_dist, color='#5475a8')
ax.set_yscale('log')
ax.set_title(f'Mapper 연결 성분 크기 분포 ({len(comps)}개, 11y)', fontsize=10)
ax.set_xlabel('component rank'); ax.set_ylabel('node 수 (log)')
ax.grid(alpha=0.3)

# (하단 우) 노드 도수 분포
ax = axes[1, 1]
deg_full = dict(G.degree())
deg_dist = pd.Series(list(deg_full.values())).value_counts().sort_index()
ax.bar(deg_dist.index, deg_dist.values, color='#c87f5a')
n_branch_full = len([d for d in deg_full.values() if d >= 3])
ax.set_title(f'Mapper 노드 도수 분포 (deg≥3={n_branch_full}, 11y)', fontsize=10)
ax.set_xlabel('degree'); ax.set_ylabel('node 수')
ax.grid(alpha=0.3)

plt.tight_layout()
save_and_resize(fig, os.path.join(OUT_DIR, 'H4_cluster_outcome_panel_11y.png'))

# ============================================================
# Figure C: 출연금 비중 Mapper + 분기점 분야 라벨
# ============================================================
fig, ax = plt.subplots(figsize=(13, 8))
nx.draw_networkx_edges(G, pos, alpha=0.25, width=0.5, ax=ax)
size_arr    = np.array([G.nodes[n]['size'] for n in G.nodes()])
chooyeon_arr = np.array([node_meta[n]['mean_chooyeon'] for n in G.nodes()])
sc = nx.draw_networkx_nodes(G, pos, node_size=15+4*size_arr,
                             node_color=chooyeon_arr, cmap='Reds',
                             vmin=0, vmax=0.6, alpha=0.85, ax=ax)
fig.colorbar(sc, ax=ax, label='평균 chooyeon_pct', shrink=0.7)
top_branches = sorted(branches, key=lambda n: -G.nodes[n]['size'])[:10]
nx.draw_networkx_labels(G, pos,
                        labels={n: node_meta[n]['top_field'] for n in top_branches},
                        font_size=8, font_family=KFONT or 'sans-serif', ax=ax)
ax.set_title(
    f'Mapper (11y) — 출연금 비중 + 분기점 분야 라벨\n'
    f'components={len(comps)}, loops={n_loops}, branches={len(branches)}',
    fontsize=11
)
ax.axis('off')
plt.tight_layout()
save_and_resize(fig, os.path.join(OUT_DIR, 'H4_mapper_chooyeon_11y.png'))

# ============================================================
# 최종 요약 출력
# ============================================================
print('\n' + '='*70)
print('=== H4 11y Mapper 분석 요약 ===')
print('='*70)
print(f'  활동 N      = {len(df)} (11y 데이터)')
print(f'  Mapper nodes= {n_nodes}, edges = {n_edges}')
print(f'  Components  = {len(comps)} (0차 베티수)')
print(f'  Loops       = {n_loops} (1차 베티수, LCC 기준)')
print(f'  Branch pts  = {len(branches)}, Endpoints = {len(endpoints)}')
print()
print('  [5y vs 11y 비교]')
print('  5y: components=8, loops=7')
print(f'  11y: components={len(comps)}, loops={n_loops}')
print()
if len(oc_corr) > 0:
    pv_show = oc_corr.pivot(index='metric_label', columns='cluster', values='corr_diff')
    pv_show.columns = [f'{c}:{CLU_LABEL.get(c,"?")}' for c in pv_show.columns]
    print('  [4 클러스터 × 12 outcome 차분 상관 matrix]')
    print(pv_show.round(3).to_string())

print('\n  생성 파일:')
for f in sorted(os.listdir(OUT_DIR)):
    fpath = os.path.join(OUT_DIR, f)
    sz    = os.path.getsize(fpath) // 1024
    print(f'    {f} ({sz} KB)')

con.close()
print('\n완료.')
