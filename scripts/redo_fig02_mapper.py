"""그림 2 (h4_mapper) — 두 패널 분리 (amp / cluster), 노드 라벨 가독성 확보.

source: scripts/h4_v3_replaced.py 의 Figure A를 paper-style로 분리

출력 (preview):
  paper/figures/_preview/h4_mapper_amp.png
  paper/figures/_preview/h4_mapper_cluster.png
"""
import os, sys, io, warnings
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
import kmapper as km
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.patches import Patch
from PIL import Image

warnings.filterwarnings('ignore')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# A4 본문 폭(약 6.3 인치)에 1:1 매핑되도록 figsize·폰트 통일.
# Typst image width:100% 사용 시 PNG가 PDF에서 6.3 인치로 표시됨 → 폰트 스케일 1:1
plt.rcParams.update({
    'font.size': 11, 'axes.titlesize': 12, 'axes.labelsize': 11,
    'xtick.labelsize': 10, 'ytick.labelsize': 10,
    'legend.fontsize': 11,
    'mathtext.default': 'regular',
    'axes.unicode_minus': False,
})
for fname in ['Malgun Gothic', 'Arial Unicode MS', 'NanumGothic']:
    if any(fname.lower() in fn.name.lower()
           for fn in mpl.font_manager.fontManager.ttflist):
        mpl.rcParams['font.family'] = [fname, 'Times New Roman', 'DejaVu Sans']
        break
KFONT = mpl.rcParams.get('font.family', 'Malgun Gothic')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
H3_CSV = os.path.join(ROOT, 'data', 'results', 'H3_activity_embedding_11y.csv')
PREVIEW = os.path.join(ROOT, 'paper', 'figures', '_preview')
os.makedirs(PREVIEW, exist_ok=True)

CLU_LABEL = {0: '인건비형 (n=129)', 1: '자산취득형 (n=99)',
             2: '출연금형 (n=154)', 3: '정상사업 (n=1,175)'}

df = pd.read_csv(H3_CSV)
feat_cols = ['amp_12m_norm', 'amp_6m_norm', 'hhi_period', 'q4_pct', 'dec_pct',
             'cv_monthly', 'chooyeon_pct', 'operating_pct',
             'direct_invest_pct', 'personnel_pct', 'log_annual', 'growth_cagr']
X = StandardScaler().fit_transform(df[feat_cols].values)

print('Mapper graph 재계산 ...')
mapper = km.KeplerMapper(verbose=0)
graph = mapper.map(
    lens=df[['u1', 'u2']].values, X=X,
    cover=km.Cover(n_cubes=18, perc_overlap=0.5),
    clusterer=DBSCAN(eps=0.45, min_samples=4),
)

G = nx.Graph()
node_meta = {}
for nid, members in graph['nodes'].items():
    sub = df.iloc[members]
    G.add_node(nid, size=len(members))
    node_meta[nid] = {
        'size': len(members),
        'mean_amp_12m': float(sub['amp_12m_norm'].mean()),
        'cluster_dom': int(sub['cluster'].mode().iloc[0]),
        'top_field': sub['FLD_NM'].mode().iloc[0] if len(sub) > 0 else '',
    }
for nid, neighbors in graph['links'].items():
    for nb in neighbors:
        G.add_edge(nid, nb)
n_comp = nx.number_connected_components(G)
LCC = G.subgraph(max(nx.connected_components(G), key=len)).copy()
n_loops = LCC.number_of_edges() - LCC.number_of_nodes() + 1
deg = dict(LCC.degree())
branches = [n for n, d in deg.items() if d >= 3]
endpoints = [n for n, d in deg.items() if d == 1]
print(f'  {G.number_of_nodes()} nodes / {G.number_of_edges()} edges, '
      f'comp={n_comp}, loops={n_loops}, branches={len(branches)}')

pos = nx.spring_layout(G, seed=42, k=0.32, iterations=300)
sizes_arr = np.array([G.nodes[n]['size'] for n in G.nodes()])

# 노드 좌표 분포에 맞춰 axis 잘라내기 (빈 공간 줄임)
xs = np.array([pos[n][0] for n in G.nodes()])
ys = np.array([pos[n][1] for n in G.nodes()])
xpad = 0.08 * (xs.max() - xs.min())
ypad = 0.08 * (ys.max() - ys.min())
XLIM = (xs.min() - xpad, xs.max() + xpad)
YLIM = (ys.min() - ypad, ys.max() + ypad)

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
        print(f'  preview: {fname} {w}x{h} -> {ns[0]}x{ns[1]}')
    else:
        print(f'  preview: {fname} {w}x{h}')

# ── 그림 2A: amp_12m 색상
fig, ax = plt.subplots(figsize=(8.76, 4.7))
colors = np.array([node_meta[n]['mean_amp_12m'] for n in G.nodes()])
nx.draw_networkx_edges(G, pos, alpha=0.3, width=0.6, ax=ax)
sc = nx.draw_networkx_nodes(
    G, pos, node_size=50 + 10 * sizes_arr,
    node_color=colors, cmap='RdBu_r',
    vmin=0, vmax=df['amp_12m_norm'].quantile(0.9),
    alpha=0.88, ax=ax,
)
ax.set_xlim(XLIM); ax.set_ylim(YLIM)
ax.axis('off')
fig.colorbar(sc, ax=ax, label='amp_12m_norm', shrink=0.75)
ax.text(
    0.02, 0.98,
    f'{G.number_of_nodes()} nodes · {G.number_of_edges()} edges\n'
    f'components = {n_comp} · loops = {n_loops}',
    transform=ax.transAxes, va='top', fontsize=11,
    bbox=dict(boxstyle='round,pad=0.4', fc='white',
              ec='#bbb', alpha=0.9),
)
plt.tight_layout()
save_resize(fig, 'h4_mapper_amp.png')

# ── 그림 2B: H3 클러스터 색상 + 분기점 분야 라벨
fig, ax = plt.subplots(figsize=(8.76, 4.7))
palette = plt.get_cmap('tab10')
clu_colors = [palette(node_meta[n]['cluster_dom'] % 10) for n in G.nodes()]
nx.draw_networkx_edges(G, pos, alpha=0.3, width=0.6, ax=ax)
nx.draw_networkx_nodes(
    G, pos, node_size=50 + 10 * sizes_arr,
    node_color=clu_colors, alpha=0.88, ax=ax,
)
# 분기점 상위 노드의 *unique* 분야만 라벨 (중복 분야 1번만)
top_branch = sorted(branches, key=lambda n: -G.nodes[n]['size'])
seen_fields = set()
labels_dict = {}
for n in top_branch:
    f = node_meta[n].get('top_field', '')
    if f and f not in seen_fields:
        labels_dict[n] = f
        seen_fields.add(f)
    if len(labels_dict) >= 6:
        break
nx.draw_networkx_labels(
    G, pos, labels=labels_dict,
    font_size=10, font_family=KFONT or 'sans-serif', ax=ax,

    bbox=dict(boxstyle='round,pad=0.25', fc='white',
              ec='#888', alpha=0.85),
)
legend_elems = [Patch(facecolor=palette(cl), label=CLU_LABEL.get(cl, f'cluster {cl}'))
                for cl in [0, 1, 2, 3]]
ax.legend(handles=legend_elems, loc='lower right',
          frameon=True, framealpha=0.92)
ax.set_xlim(XLIM); ax.set_ylim(YLIM)
ax.axis('off')
ax.text(
    0.02, 0.98,
    f'분기점 = {len(branches)} · 말단 = {len(endpoints)}\n'
    f'위상적으로 분리된 사업원형 검증',
    transform=ax.transAxes, va='top', fontsize=11,
    bbox=dict(boxstyle='round,pad=0.4', fc='white',
              ec='#bbb', alpha=0.9),
)
plt.tight_layout()
save_resize(fig, 'h4_mapper_cluster.png')

print('완료.')
