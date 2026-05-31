"""H4-v2: Mapper parameter sensitivity sweep.

Reviewer concern: "Mapper says 10 components vs HDBSCAN says 4 archetypes —
is this artifact of cover overlap or real?"

Sweep:
  cover overlap  ∈ {0.3, 0.5, 0.7}
  n_intervals    ∈ {6, 10, 15}
  min_cluster_size (HDBSCAN) ∈ {15, 30, 50}
  → 27 configurations total

Output:
  data/results/H4_mapper_sensitivity.csv
  columns: overlap, n_intervals, min_cluster_size,
           n_nodes, n_edges, n_components, n_loops
"""
import os, sys, io, warnings, itertools, time
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
import kmapper as km
import networkx as nx

# ── suppress noisy hdbscan / numba / sklearn warnings ──────────────────────
warnings.filterwarnings('ignore')
os.environ.setdefault('NUMBA_DISABLE_JIT', '0')

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT    = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
H3_CSV  = os.path.join(ROOT, 'data', 'results', 'H3_activity_embedding_11y.csv')
# NOTE: uses the _11y variant (N=1557) — same source as redo_fig02_mapper.py
# which reproduces the reported 32 nodes / 38 edges / 10 components / 7 loops.
RES_DIR = os.path.join(ROOT, 'data', 'results')
OUT_CSV = os.path.join(RES_DIR, 'H4_mapper_sensitivity.csv')
os.makedirs(RES_DIR, exist_ok=True)

# ── load & standardise ──────────────────────────────────────────────────────
df = pd.read_csv(H3_CSV)
feat_cols = [
    'amp_12m_norm', 'amp_6m_norm', 'hhi_period', 'q4_pct', 'dec_pct',
    'cv_monthly', 'chooyeon_pct', 'operating_pct',
    'direct_invest_pct', 'personnel_pct', 'log_annual', 'growth_cagr',
]
X    = StandardScaler().fit_transform(df[feat_cols].values)
lens = df[['u1', 'u2']].values   # same 2-D UMAP projection as baseline

print(f'H3 embedding loaded: {X.shape}')
print(f'Lens (UMAP): {lens.shape}')
print()

# ── sweep parameters ────────────────────────────────────────────────────────
OVERLAPS    = [0.3, 0.5, 0.7]
N_INTERVALS = [6, 10, 15]
MIN_CLUSTER = [15, 30, 50]

# Try to import HDBSCAN; fall back gracefully if unavailable
try:
    import hdbscan as _hdbscan_mod
    def make_clusterer(min_cluster_size):
        return _hdbscan_mod.HDBSCAN(
            min_cluster_size=min_cluster_size,
            min_samples=5,
            metric='euclidean',
            cluster_selection_method='eom',
        )
    print('Clusterer backend: hdbscan (native)')
except ImportError:
    from sklearn.cluster import HDBSCAN as _sklearn_hdb
    def make_clusterer(min_cluster_size):
        return _sklearn_hdb(
            min_cluster_size=min_cluster_size,
            min_samples=5,
            metric='euclidean',
            cluster_selection_method='eom',
        )
    print('Clusterer backend: sklearn.cluster.HDBSCAN')

print()

# ── run sweep ───────────────────────────────────────────────────────────────
mapper = km.KeplerMapper(verbose=0)
results = []
total  = len(OVERLAPS) * len(N_INTERVALS) * len(MIN_CLUSTER)
done   = 0
t0     = time.time()

header = f"{'#':>3} {'overlap':>8} {'n_int':>6} {'mcs':>5} | " \
         f"{'nodes':>6} {'edges':>6} {'comp':>5} {'loops':>6}"
print(header)
print('-' * len(header))

for overlap, n_int, mcs in itertools.product(OVERLAPS, N_INTERVALS, MIN_CLUSTER):
    done += 1

    cover      = km.Cover(n_cubes=n_int, perc_overlap=overlap)
    clusterer  = make_clusterer(mcs)

    try:
        graph = mapper.map(
            lens=lens,
            X=X,
            cover=cover,
            clusterer=clusterer,
        )
    except Exception as e:
        print(f'  WARN config ({overlap}, {n_int}, {mcs}): {e}')
        graph = {'nodes': {}, 'links': {}}

    # ── topology stats ──────────────────────────────────────────────────
    n_nodes = len(graph['nodes'])
    n_edges = sum(len(v) for v in graph['links'].values())

    if n_nodes == 0:
        n_comp  = 0
        n_loops = 0
    else:
        G = nx.Graph()
        for nid in graph['nodes']:
            G.add_node(nid)
        for nid, neighbors in graph['links'].items():
            for nb in neighbors:
                G.add_edge(nid, nb)

        n_comp = nx.number_connected_components(G)

        # Betti-1: loops in largest connected component
        if G.number_of_nodes() > 0:
            LCC     = G.subgraph(max(nx.connected_components(G), key=len)).copy()
            n_loops = max(0, LCC.number_of_edges() - LCC.number_of_nodes() + 1)
        else:
            n_loops = 0

    results.append({
        'overlap':          overlap,
        'n_intervals':      n_int,
        'min_cluster_size': mcs,
        'n_nodes':          n_nodes,
        'n_edges':          n_edges,
        'n_components':     n_comp,
        'n_loops':          n_loops,
    })

    elapsed = time.time() - t0
    print(f"{done:>3} {overlap:>8.1f} {n_int:>6} {mcs:>5} | "
          f"{n_nodes:>6} {n_edges:>6} {n_comp:>5} {n_loops:>6}"
          f"  [{elapsed:5.1f}s]")

# ── save CSV ─────────────────────────────────────────────────────────────────
sens_df = pd.DataFrame(results)
sens_df.to_csv(OUT_CSV, index=False, encoding='utf-8-sig')
print(f'\nSaved: {OUT_CSV}')
print(f'Total elapsed: {time.time()-t0:.1f}s for {total} configurations\n')

# ── summary statistics ────────────────────────────────────────────────────
comp_series = sens_df['n_components']
median_comp = float(comp_series.median())
q25         = float(comp_series.quantile(0.25))
q75         = float(comp_series.quantile(0.75))
comp_min    = int(comp_series.min())
comp_max    = int(comp_series.max())
baseline_10_in_iqr = (q25 <= 10 <= q75)

print('=' * 60)
print('SENSITIVITY SUMMARY — n_components across 27 configs')
print('=' * 60)
print(f'  Median n_components : {median_comp:.1f}')
print(f'  IQR [Q25, Q75]      : [{q25:.1f}, {q75:.1f}]')
print(f'  Range [min, max]    : [{comp_min}, {comp_max}]')
print(f'  Baseline (n=10) in IQR? : {"YES — robust" if baseline_10_in_iqr else "NO — check configs"}')
print()

# breakdown by overlap
print('  Breakdown by cover overlap:')
print(sens_df.groupby('overlap')['n_components']
      .agg(['median','min','max']).rename(
          columns={'median':'med_comp','min':'min_comp','max':'max_comp'})
      .to_string())
print()

# breakdown by n_intervals
print('  Breakdown by n_intervals:')
print(sens_df.groupby('n_intervals')['n_components']
      .agg(['median','min','max']).rename(
          columns={'median':'med_comp','min':'min_comp','max':'max_comp'})
      .to_string())
print()

# breakdown by min_cluster_size
print('  Breakdown by min_cluster_size:')
print(sens_df.groupby('min_cluster_size')['n_components']
      .agg(['median','min','max']).rename(
          columns={'median':'med_comp','min':'min_comp','max':'max_comp'})
      .to_string())
print()

# configs that reproduce ≈10 components (9-11)
near10 = sens_df[(sens_df['n_components'] >= 9) & (sens_df['n_components'] <= 11)]
print(f'  Configs with n_components in [9,11]: {len(near10)}/27')
if len(near10) > 0:
    print(near10[['overlap','n_intervals','min_cluster_size','n_components']].to_string(index=False))

print()
print('Full table:')
print(sens_df.to_string(index=False))
print('\nDone.')
