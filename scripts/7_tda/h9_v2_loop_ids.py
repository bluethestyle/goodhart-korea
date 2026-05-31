"""H9 v2 — Loop ID Extraction + Interpretation.

Extracts the top-5 most persistent H1 loops from the activity embedding,
identifies which activities lie on each loop via ripser cocycles (coboundary
representatives), and tests whether loop activities cluster near archetype
boundaries (low-silhouette / mixed membership).

Outputs:
  data/results/H9_v2_loops.csv       — loop_id, activity_id, persistence, archetype, on_boundary
  data/results/H9_v2_loop_interpretation.txt  — text interpretation
"""
import os, sys, io, warnings
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_samples
from ripser import ripser
import networkx as nx

warnings.filterwarnings('ignore')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT    = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
H3_CSV  = os.path.join(ROOT, 'data', 'results', 'H3_activity_embedding.csv')
RES_DIR = os.path.join(ROOT, 'data', 'results')
os.makedirs(RES_DIR, exist_ok=True)

FEAT_COLS = [
    'amp_12m_norm','amp_6m_norm','hhi_period','q4_pct','dec_pct','cv_monthly',
    'chooyeon_pct','operating_pct','direct_invest_pct','personnel_pct',
    'log_annual','growth_cagr',
]
SUB_N   = 300
SEED    = 42
THRESH  = 8.0
TOP_K   = 5     # top-k most persistent loops


# ============================================================
# Load + subsample (same seed as h9 main)
# ============================================================
print('='*70)
print('H9 v2: Loop ID Extraction + Interpretation')
print('='*70)
df = pd.read_csv(H3_CSV)
X_full  = StandardScaler().fit_transform(df[FEAT_COLS].values)
print(f'  Full embedding: {X_full.shape}')

rng = np.random.default_rng(SEED)
sub_idx = rng.choice(len(X_full), size=SUB_N, replace=False)
X_sub   = X_full[sub_idx]
df_sub  = df.iloc[sub_idx].reset_index(drop=True)
print(f'  Subsample N = {SUB_N} (seed={SEED})')


# ============================================================
# Step 1: PH with cocycles
# ============================================================
print('\n--- Step 1: Vietoris-Rips PH with cocycles ---')
result  = ripser(X_sub, maxdim=1, thresh=THRESH, do_cocycles=True)
dgm_h1  = result['dgms'][1]          # shape (n_h1, 2)
cocycles_h1 = result['cocycles'][1]  # list of arrays, each shape (k, 3)
idx_perm    = result['idx_perm']     # permutation used by ripser (greedy landmark)
dperm2all   = result['dperm2all']    # distances from perm points to all points

print(f'  H1 pairs: {len(dgm_h1)}')
finite_mask = np.isfinite(dgm_h1[:, 1])
pers_h1     = np.where(finite_mask,
                        dgm_h1[:, 1] - dgm_h1[:, 0],
                        np.inf)
n_finite = finite_mask.sum()
print(f'  Finite H1 pairs: {n_finite}')
if n_finite > 0:
    top_pers = sorted(pers_h1[finite_mask], reverse=True)[:10]
    print(f'  Top-10 persistence: {[f"{p:.4f}" for p in top_pers]}')


# ============================================================
# Step 2: Sort H1 pairs by persistence, pick top-K
# ============================================================
# ripser orders dgms by birth; sort by persistence descending
sort_order = np.argsort(-pers_h1)
top_k_idx  = [i for i in sort_order if np.isfinite(pers_h1[i])][:TOP_K]
print(f'\n--- Step 2: Top-{TOP_K} loops ---')
for rank, i in enumerate(top_k_idx):
    b, d = dgm_h1[i]
    print(f'  Loop {rank+1}: birth={b:.4f}, death={d:.4f}, persistence={d-b:.4f}')


# ============================================================
# Step 3: Extract representative edges for each cocycle
#         Cocycle entries are (i, j, coeff) → edges of the representative cocycle
#         The loop's "carrier" = set of vertices appearing in cocycle edges
# ============================================================
print('\n--- Step 3: Cocycle → vertex extraction ---')

def cocycle_vertices(cocycle_edges):
    """Return unique vertex indices from cocycle edge list."""
    if len(cocycle_edges) == 0:
        return np.array([], dtype=int)
    edges = cocycle_edges[:, :2].astype(int)
    return np.unique(edges.ravel())


def cocycle_cycle_vertices(cocycle_edges, X, birth, death, alpha=0.3):
    """Refine: keep only edges whose filtration value is in [birth, death+alpha].

    Ripser cocycle edges use the vertex indices into idx_perm (the greedy landmark).
    These are LOCAL indices into the subsampled X_sub.
    """
    if len(cocycle_edges) == 0:
        return np.array([], dtype=int)
    edges = cocycle_edges[:, :2].astype(int)
    # Filter: edge weight (Euclidean dist between those points) should be ≤ death
    mask = []
    for e in edges:
        u, v = e
        if u < len(X) and v < len(X):
            dist_uv = np.linalg.norm(X[u] - X[v])
            mask.append(dist_uv <= death * (1 + alpha))
        else:
            mask.append(False)
    filtered = edges[mask]
    if len(filtered) == 0:
        return np.unique(edges.ravel())
    return np.unique(filtered.ravel())


loop_records = []
loop_vertex_sets = []   # list of vertex index arrays (into X_sub)

for rank, loop_h1_idx in enumerate(top_k_idx):
    b, d = dgm_h1[loop_h1_idx]
    pers  = d - b
    cocyc = cocycles_h1[loop_h1_idx]

    # vertex indices in X_sub
    verts_local = cocycle_cycle_vertices(cocyc, X_sub, b, d)
    loop_vertex_sets.append(verts_local)

    print(f'\n  Loop {rank+1} (persistence={pers:.4f}, birth={b:.4f}, death={d:.4f}):')
    print(f'    Cocycle edges: {len(cocyc)}, Carrier vertices: {len(verts_local)}')

    # Map back to original df rows
    orig_rows = df_sub.iloc[verts_local] if len(verts_local) > 0 else pd.DataFrame()
    if len(orig_rows) > 0:
        # Archetype (cluster) distribution
        arch_dist = orig_rows['cluster'].value_counts()
        print(f'    Archetype distribution: {arch_dist.to_dict()}')
        # Ministry distribution (top 3)
        if 'OFFC_NM' in orig_rows.columns:
            min_dist = orig_rows['OFFC_NM'].value_counts().head(3)
            print(f'    Top-3 ministries: {min_dist.to_dict()}')
        # Field distribution
        if 'FLD_NM' in orig_rows.columns:
            fld_dist = orig_rows['FLD_NM'].value_counts().head(3)
            print(f'    Top-3 fields: {fld_dist.to_dict()}')
        # Feature stats
        feat_means = orig_rows[FEAT_COLS].mean()
        print(f'    Feature means:')
        for col in ['amp_12m_norm','q4_pct','cv_monthly','log_annual']:
            print(f'      {col}: {feat_means[col]:.4f}')
    else:
        print('    (no vertices extracted)')


# ============================================================
# Step 4: Silhouette / boundary analysis
#         Low silhouette score = near archetype boundary
# ============================================================
print('\n--- Step 4: Silhouette / Boundary Analysis ---')
cluster_labels = df_sub['cluster'].values
n_clusters = len(np.unique(cluster_labels))

if n_clusters >= 2:
    sil_scores = silhouette_samples(X_sub, cluster_labels)
    df_sub = df_sub.copy()
    df_sub['silhouette'] = sil_scores

    # Threshold: "on boundary" = silhouette in bottom 25%
    sil_thresh = np.percentile(sil_scores, 25)
    df_sub['on_boundary'] = (sil_scores <= sil_thresh).astype(int)

    print(f'  Silhouette threshold (25th pct): {sil_thresh:.4f}')
    print(f'  Overall boundary fraction: {df_sub["on_boundary"].mean():.3f}')

    for rank, verts_local in enumerate(loop_vertex_sets):
        if len(verts_local) == 0:
            print(f'  Loop {rank+1}: no vertices')
            continue
        loop_sil  = sil_scores[verts_local]
        loop_on_b = (loop_sil <= sil_thresh).mean()
        print(f'  Loop {rank+1}: mean_silhouette={np.mean(loop_sil):.4f}, '
              f'boundary_fraction={loop_on_b:.3f} '
              f'(vs background {df_sub["on_boundary"].mean():.3f})')
else:
    sil_thresh = 0.0
    df_sub['silhouette'] = 0.0
    df_sub['on_boundary'] = 0
    print('  Only 1 cluster — skipping silhouette')


# ============================================================
# Step 5: Hypothesis test — chi-square boundary enrichment
# ============================================================
print('\n--- Step 5: Boundary Enrichment Test ---')
from scipy.stats import chi2_contingency, fisher_exact, mannwhitneyu

background_boundary = df_sub['on_boundary'].values
background_on = background_boundary.sum()
background_off = len(background_boundary) - background_on

enrichment_results = []
for rank, verts_local in enumerate(loop_vertex_sets):
    if len(verts_local) < 2:
        enrichment_results.append({'loop': rank+1, 'p_boundary': np.nan, 'effect': np.nan})
        continue
    loop_on  = (df_sub.iloc[verts_local]['on_boundary'] == 1).sum()
    loop_off = len(verts_local) - loop_on
    loop_sil = sil_scores[verts_local] if n_clusters >= 2 else np.array([0.0])
    rest_sil = np.delete(sil_scores, verts_local) if n_clusters >= 2 else np.array([0.0])

    # Mann-Whitney U: are loop silhouettes lower than the rest?
    if len(loop_sil) >= 2 and len(rest_sil) >= 2:
        stat, p_mw = mannwhitneyu(loop_sil, rest_sil, alternative='less')
    else:
        p_mw = np.nan

    # Fisher exact on boundary flag
    ct = np.array([[loop_on, loop_off],
                   [background_on - loop_on, background_off - loop_off]])
    try:
        _, p_fish = fisher_exact(ct, alternative='greater')
    except Exception:
        p_fish = np.nan

    effect = (loop_on / len(verts_local)) / (background_on / len(background_boundary)) if background_on > 0 else np.nan
    enrichment_results.append({
        'loop': rank+1,
        'p_mannwhitney': p_mw,
        'p_fisher': p_fish,
        'boundary_enrichment_ratio': effect,
    })
    print(f'  Loop {rank+1}: boundary_ratio={effect:.2f}x, '
          f'p_MW={p_mw:.4f}, p_Fisher={p_fish:.4f}')


# ============================================================
# Step 6: Build output dataframe
# ============================================================
print('\n--- Step 6: Building output ---')
rows = []
for rank, (loop_h1_idx, verts_local) in enumerate(zip(top_k_idx, loop_vertex_sets)):
    b, d = dgm_h1[loop_h1_idx]
    pers  = d - b
    for v in verts_local:
        row_info = df_sub.iloc[v]
        rows.append({
            'loop_id':        rank + 1,
            'loop_birth':     round(float(b), 5),
            'loop_death':     round(float(d), 5),
            'persistence':    round(float(pers), 5),
            'sub_vertex_idx': int(v),
            'activity_id':    int(df_sub.index[v]) if hasattr(df_sub.index[v], '__int__') else v,
            'FLD_NM':         row_info.get('FLD_NM', ''),
            'OFFC_NM':        row_info.get('OFFC_NM', ''),
            'PGM_NM':         row_info.get('PGM_NM', ''),
            'ACTV_NM':        row_info.get('ACTV_NM', ''),
            'archetype':      int(row_info.get('cluster', -1)),
            'silhouette':     round(float(row_info.get('silhouette', 0)), 5),
            'on_boundary':    int(row_info.get('on_boundary', 0)),
            'amp_12m_norm':   round(float(row_info.get('amp_12m_norm', 0)), 5),
            'q4_pct':         round(float(row_info.get('q4_pct', 0)), 5),
            'cv_monthly':     round(float(row_info.get('cv_monthly', 0)), 5),
            'log_annual':     round(float(row_info.get('log_annual', 0)), 5),
        })

out_df = pd.DataFrame(rows)
out_path = os.path.join(RES_DIR, 'H9_v2_loops.csv')
out_df.to_csv(out_path, index=False, encoding='utf-8-sig')
print(f'  Saved: {out_path}  ({len(out_df)} rows)')


# ============================================================
# Step 7: Interpretation
# ============================================================
print('\n--- Step 7: Interpretation ---')

# Classify each loop
loop_types = []
for rank, er in enumerate(enrichment_results):
    verts_local = loop_vertex_sets[rank]
    if len(verts_local) == 0:
        loop_types.append('insufficient_data')
        continue
    arch_dist = df_sub.iloc[verts_local]['cluster'].value_counts()
    dom_frac  = arch_dist.iloc[0] / len(verts_local) if len(arch_dist) > 0 else 1.0
    bnd_ratio = er.get('boundary_enrichment_ratio', np.nan)
    p_mw      = er.get('p_mannwhitney', np.nan)

    if not np.isnan(bnd_ratio) and bnd_ratio >= 1.5 and (np.isnan(p_mw) or p_mw < 0.10):
        loop_types.append('archetype_boundary')
    elif dom_frac >= 0.7:
        loop_types.append('sub_archetype')
    elif not np.isnan(bnd_ratio) and bnd_ratio < 0.8:
        loop_types.append('random_or_noise')
    else:
        loop_types.append('mixed/cycle_pattern')

# Tally
from collections import Counter
type_counts = Counter(loop_types)
dominant_type = type_counts.most_common(1)[0][0]

print(f'\n  Loop type distribution: {dict(type_counts)}')
print(f'  Dominant interpretation: {dominant_type}')

type_label_map = {
    'archetype_boundary': '(a) archetype boundaries — loops run along transition zones between clusters',
    'sub_archetype':      '(b) sub-archetypes — within-cluster heterogeneity / sub-groups',
    'random_or_noise':    '(c) random / noise — no meaningful concentration',
    'mixed/cycle_pattern':'(d) mixed or seasonal cycle pattern',
    'insufficient_data':  '(?) insufficient data to classify',
}

lines = [
    'H9 v2 — Loop Interpretation',
    '='*60,
    f'Subsample: N={SUB_N}, seed={SEED}',
    f'H1 pairs found: {len(dgm_h1)} total, {n_finite} finite',
    f'Top-{TOP_K} loops analyzed',
    '',
    'Per-loop classification:',
]
for rank, (lt, er) in enumerate(zip(loop_types, enrichment_results)):
    b, d = dgm_h1[top_k_idx[rank]]
    verts_local = loop_vertex_sets[rank]
    lines.append(
        f'  Loop {rank+1}: persistence={d-b:.4f}, n_vertices={len(verts_local)}, '
        f'type={lt}, boundary_ratio={er.get("boundary_enrichment_ratio", float("nan")):.2f}x, '
        f'p_MW={er.get("p_mannwhitney", float("nan")):.4f}'
    )

lines += [
    '',
    'Summary:',
    f'  Dominant loop type: {type_label_map.get(dominant_type, dominant_type)}',
    '',
    'Possible archetype distribution per loop:',
]
for rank, verts_local in enumerate(loop_vertex_sets):
    if len(verts_local) == 0:
        lines.append(f'  Loop {rank+1}: no vertices')
        continue
    arch_dist = df_sub.iloc[verts_local]['cluster'].value_counts().to_dict()
    lines.append(f'  Loop {rank+1}: {arch_dist}')

lines += [
    '',
    'Interpretation:',
    f'  Loops appear to be: {type_label_map.get(dominant_type, dominant_type)}',
    '',
    'Note: cocycle carrier vertices = vertices incident to representative cocycle edges.',
    'These are not guaranteed to be the minimal cycle; they identify the "zone"',
    'in feature space where the topological loop lives.',
]

interp_text = '\n'.join(lines)
print('\n' + interp_text)

interp_path = os.path.join(RES_DIR, 'H9_v2_loop_interpretation.txt')
with open(interp_path, 'w', encoding='utf-8') as f:
    f.write(interp_text)
print(f'\n  Saved interpretation: {interp_path}')
print('\nDone.')
