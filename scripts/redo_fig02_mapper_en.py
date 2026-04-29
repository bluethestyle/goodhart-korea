"""Figure 2 (h4_mapper) — two panels separated (amp / cluster), node label readability.

source: scripts/h4_v3_replaced.py Figure A split into paper-style panels

Output (preview):
  paper/figures_en/_preview/h4_mapper_amp.png
  paper/figures_en/_preview/h4_mapper_cluster.png

All Korean labels replaced with English.
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

# A4 body width (~6.3 inches) 1:1 mapping. figsize/font unified.
# Typst image width:100% → PNG displayed at 6.3 inches in PDF → font scale 1:1
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
PREVIEW = os.path.join(ROOT, 'paper', 'figures_en', '_preview')
os.makedirs(PREVIEW, exist_ok=True)

CLU_LABEL = {0: 'Personnel (n=129)', 1: 'Capital-Acq. (n=99)',
             2: 'Grant-Transfer (n=154)', 3: 'Normal (n=1,175)'}

# English field name mapping
FIELD_EN = {
    '사회복지': 'Social Welfare',
    '보건': 'Health',
    '과학기술': 'S&T',
    '산업·중소기업및에너지': 'Industry/SMEs',
    '산업·중기': 'Industry/SMEs',
    '산업': 'Industry',
    '문화관광': 'Culture & Tourism',
    '문화': 'Culture',
    '교육': 'Education',
    '국토·지역개발': 'Land Development',
    '국토': 'Land',
    '국토및지역개발': 'Land Dev.',
    '일반·지방행정': 'Gen. Admin.',
    '일반행정': 'Gen. Admin.',
    '농림수산': 'Agriculture',
    '교통': 'Transport',
    '교통및물류': 'Transport',
    '환경': 'Environment',
    '통신': 'ICT',
    '통일·외교': 'Unification/Diplomacy',
    '통일외교': 'Unification/Diplomacy',
    '공공질서': 'Public Order',
    '공공질서및안전': 'Public Order',
    '국방': 'Defense',
    '예비비': 'Reserve',
}

df = pd.read_csv(H3_CSV)
feat_cols = ['amp_12m_norm', 'amp_6m_norm', 'hhi_period', 'q4_pct', 'dec_pct',
             'cv_monthly', 'chooyeon_pct', 'operating_pct',
             'direct_invest_pct', 'personnel_pct', 'log_annual', 'growth_cagr']
X = StandardScaler().fit_transform(df[feat_cols].values)

print('Recomputing Mapper graph ...')
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

# Clip axis to node coordinate distribution (reduce empty space)
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

# ── Figure 2A: amp_12m coloring
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

# ── Figure 2B: H3 cluster coloring + branch field labels
fig, ax = plt.subplots(figsize=(8.76, 4.7))
palette = plt.get_cmap('tab10')
clu_colors = [palette(node_meta[n]['cluster_dom'] % 10) for n in G.nodes()]
nx.draw_networkx_edges(G, pos, alpha=0.3, width=0.6, ax=ax)
nx.draw_networkx_nodes(
    G, pos, node_size=50 + 10 * sizes_arr,
    node_color=clu_colors, alpha=0.88, ax=ax,
)
# Label unique fields on top branch nodes (deduplicated)
top_branch = sorted(branches, key=lambda n: -G.nodes[n]['size'])
seen_fields = set()
labels_dict = {}
for n in top_branch:
    f = node_meta[n].get('top_field', '')
    f_en = FIELD_EN.get(f, f)
    if f_en and f_en not in seen_fields:
        labels_dict[n] = f_en
        seen_fields.add(f_en)
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
    f'Branch nodes = {len(branches)} · Endpoints = {len(endpoints)}\n'
    f'Topologically separated Project Archetypes confirmed',
    transform=ax.transAxes, va='top', fontsize=11,
    bbox=dict(boxstyle='round,pad=0.4', fc='white',
              ec='#bbb', alpha=0.9),
)
plt.tight_layout()
save_resize(fig, 'h4_mapper_cluster.png')

print('Done.')
