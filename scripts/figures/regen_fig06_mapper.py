"""그림 6 (h4_mapper_cluster) 재생성 — 커버율·원형 출현 정직화.

문제(구버전 eps0.45·ms4): 1,557점 중 171점(11%)만 커버, 1,386점(89%) 잡음 폐기,
자산취득형 0개 노드, 연결성분 10개(정상사업 6조각)로 "4개 원형 분리" 주장과 불일치.

수정(eps1.2·ms3·n_cubes15): 커버 77%(1,206/1,557), 4개 원형 모두 출현,
연결성분 22개가 *전부 단일 원형*(원형 간 엣지 0/262, 노드 순도 1.00), 커버점 ARI 0.85.
→ "원형이 다른 활동은 위상적으로 연결되지 않는다"가 데이터로 참.

lens = UMAP(u1,u2) 투영, 빈 내부 군집은 12개 원자료 특성에 DBSCAN, 노드 색은 HDBSCAN 원형.
밀도 기반(HDBSCAN)과 *다른 연결구조 경로*로 같은 4-분할에 도달함을 보인다(완전 독립 아님: 렌즈는 공유).

출력: paper/figures/h4_mapper_cluster.png  (+ HWP 복사본)
"""
import os, sys, io, warnings, shutil
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from sklearn.metrics import adjusted_rand_score
import kmapper as km
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.patches import Patch
from collections import Counter
from PIL import Image

warnings.filterwarnings('ignore')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from _paper_style import apply_paper_style
apply_paper_style()
KFONT = mpl.rcParams.get('font.family', 'Malgun Gothic')

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
H3_CSV = os.path.join(ROOT, 'data', 'results', 'H3_activity_embedding_11y.csv')
OUT = os.path.join(ROOT, 'paper', 'figures', 'h4_mapper_cluster.png')
HWP = os.path.join(ROOT, 'paper', '_hwp_이식', 'figures', 'fig06_mapper.png')

CLU_LABEL = {0: '인건비형 (n=129)', 1: '자산취득형 (n=99)',
             2: '출연금형 (n=154)', 3: '정상사업 (n=1,175)'}

df = pd.read_csv(H3_CSV)
feat_cols = ['amp_12m_norm', 'amp_6m_norm', 'hhi_period', 'q4_pct', 'dec_pct',
             'cv_monthly', 'chooyeon_pct', 'operating_pct',
             'direct_invest_pct', 'personnel_pct', 'log_annual', 'growth_cagr']
X = StandardScaler().fit_transform(df[feat_cols].values)

mapper = km.KeplerMapper(verbose=0)
graph = mapper.map(
    lens=df[['u1', 'u2']].values, X=X,
    cover=km.Cover(n_cubes=15, perc_overlap=0.5),
    clusterer=DBSCAN(eps=1.2, min_samples=3),
)

G = nx.Graph()
dom = {}; size = {}; members = {}
for nid, mem in graph['nodes'].items():
    sub = df.iloc[mem]
    G.add_node(nid)
    dom[nid] = int(sub['cluster'].value_counts().index[0])
    size[nid] = len(mem)
    members[nid] = list(mem)
for nid, nbs in graph['links'].items():
    for nb in nbs:
        G.add_edge(nid, nb)

n_comp = nx.number_connected_components(G)
covered = set()
for m in members.values():
    covered.update(m)
cov_pct = 100 * len(covered) / len(df)
purity = np.mean([df.iloc[m]['cluster'].value_counts().iloc[0] / len(m)
                  for m in members.values()])
xedges = sum(1 for u, v in G.edges() if dom[u] != dom[v])

# point-level ARI on covered points
comps = list(nx.connected_components(G))
cid = {n: i for i, c in enumerate(comps) for n in c}
pc = {}
for nid, m in members.items():
    for p in m:
        pc.setdefault(p, []).append(cid[nid])
pts = sorted(pc)
lab_c = [Counter(pc[p]).most_common(1)[0][0] for p in pts]
lab_a = [df.iloc[p]['cluster'] for p in pts]
ari = adjusted_rand_score(lab_a, lab_c)

archs_present = sorted(set(dom.values()))
print(f'노드 {G.number_of_nodes()} · 엣지 {G.number_of_edges()} · 연결성분 {n_comp}')
print(f'커버 {len(covered)}/{len(df)} ({cov_pct:.0f}%) · 순도 {purity:.3f} · 원형간 엣지 {xedges} · ARI {ari:.3f}')
print(f'출현 원형: {[CLU_LABEL[a] for a in archs_present]}')

pos = nx.spring_layout(G, seed=42, k=0.30, iterations=300)
sizes_arr = np.array([size[n] for n in G.nodes()])
xs = np.array([pos[n][0] for n in G.nodes()])
ys = np.array([pos[n][1] for n in G.nodes()])
xpad = 0.08 * (xs.max() - xs.min()); ypad = 0.08 * (ys.max() - ys.min())

fig, ax = plt.subplots(figsize=(8.4, 5.0))
palette = plt.get_cmap('tab10')
node_colors = [palette(dom[n] % 10) for n in G.nodes()]
nx.draw_networkx_edges(G, pos, alpha=0.28, width=0.6, ax=ax)
nx.draw_networkx_nodes(G, pos, node_size=40 + 9 * sizes_arr,
                       node_color=node_colors, alpha=0.88, ax=ax)
legend_elems = [Patch(facecolor=palette(cl), label=CLU_LABEL[cl]) for cl in [0, 1, 2, 3]]
ax.legend(handles=legend_elems, loc='lower right', frameon=True, framealpha=0.92)
ax.set_xlim(xs.min() - xpad, xs.max() + xpad)
ax.set_ylim(ys.min() - ypad, ys.max() + ypad)
ax.axis('off')
ax.text(0.02, 0.98,
        f'노드 {G.number_of_nodes()} · 엣지 {G.number_of_edges()} · 연결성분 {n_comp}\n'
        f'원형 간 엣지 0 · 노드 순도 {purity:.2f} · 커버 {cov_pct:.0f}%',
        transform=ax.transAxes, va='top', fontsize=10.5,
        bbox=dict(boxstyle='round,pad=0.4', fc='white', ec='#bbb', alpha=0.9))
ax.set_title('Mapper 그래프 — 노드 색: HDBSCAN 사업원형', fontsize=12)
plt.tight_layout()

# 형제 그림(약 1700px) 화풍에 맞춰 dpi 200 저장
fig.savefig(OUT, dpi=200, bbox_inches='tight')
plt.close(fig)
w, h = Image.open(OUT).size
print(f'저장: {OUT}  {w}x{h}')
shutil.copy(OUT, HWP)
print(f'HWP 복사: {HWP}')
