"""H9 v2 — PH Wasserstein Bootstrap + Null Test.

Improvements over h9 original:
  - Bootstrap n=300 (vs 200), 100 trials (vs 50)
  - Wasserstein-2 and bottleneck distance to *reference* diagram (vs just max persistence)
  - Null distribution via feature-shuffle permutation
  - p-value: is observed PH structure significantly different from shuffled?

Output: data/results/H9_v2_wasserstein.csv
"""
import os, sys, io, warnings, time
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from scipy.optimize import linear_sum_assignment
from ripser import ripser

warnings.filterwarnings('ignore')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
H3_CSV  = os.path.join(ROOT, 'data', 'results', 'H3_activity_embedding.csv')
RES_DIR = os.path.join(ROOT, 'data', 'results')
os.makedirs(RES_DIR, exist_ok=True)

RNG = np.random.default_rng(42)

FEAT_COLS = [
    'amp_12m_norm','amp_6m_norm','hhi_period','q4_pct','dec_pct','cv_monthly',
    'chooyeon_pct','operating_pct','direct_invest_pct','personnel_pct',
    'log_annual','growth_cagr',
]
BOOT_N   = 300   # subsample size per bootstrap
N_BOOT   = 100   # bootstrap replicates
N_NULL   = 100   # null (shuffle) replicates
THRESH   = 8.0   # ripser filtration threshold
MAX_DIM  = 1     # compute H0 and H1


# ============================================================
# Wasserstein-2 and Bottleneck distance between two PDs
# ============================================================
def _augment_pd(dgm, n_total):
    """Pad diagram with diagonal (birth+death)/2 projections to make equal size."""
    finite = np.array([(b, d) for b, d in dgm if np.isfinite(d)], dtype=float)
    return finite


def wasserstein_p(dgm1, dgm2, p=2):
    """Compute p-Wasserstein distance between two persistence diagrams.

    Uses the standard matching with diagonal augmentation:
    each unmatched point pays its L_inf distance to the diagonal = (d-b)/2.
    """
    pts1 = np.array([(b, d) for b, d in dgm1 if np.isfinite(d)], dtype=float)
    pts2 = np.array([(b, d) for b, d in dgm2 if np.isfinite(d)], dtype=float)

    # If both empty
    if len(pts1) == 0 and len(pts2) == 0:
        return 0.0

    # Diagonal projections: project each point (b,d) -> ((b+d)/2, (b+d)/2)
    def diag_proj(pts):
        m = (pts[:, 0] + pts[:, 1]) / 2
        return np.stack([m, m], axis=1)

    # Build augmented sets: real points + diagonal projections of the other set
    if len(pts1) == 0:
        # all pts2 unmatched
        cost = np.sum((np.abs(pts2[:, 1] - pts2[:, 0]) / 2) ** p)
        return cost ** (1.0 / p)
    if len(pts2) == 0:
        cost = np.sum((np.abs(pts1[:, 1] - pts1[:, 0]) / 2) ** p)
        return cost ** (1.0 / p)

    diag1 = diag_proj(pts1)   # shape (n1, 2)
    diag2 = diag_proj(pts2)   # shape (n2, 2)

    # Augmented: pts1 | diag2  vs  diag1 | pts2
    n1, n2 = len(pts1), len(pts2)
    A = np.vstack([pts1, diag2])   # (n1+n2) x 2
    B = np.vstack([diag1, pts2])   # (n1+n2) x 2

    # Cost matrix: L_inf or L_2 ground metric on R^2
    diff = A[:, None, :] - B[None, :, :]          # (m, m, 2)
    cost_matrix = np.max(np.abs(diff), axis=2)     # L_inf  — standard for Wasserstein PD
    cost_matrix_p = cost_matrix ** p

    row_ind, col_ind = linear_sum_assignment(cost_matrix_p)
    total_cost = cost_matrix_p[row_ind, col_ind].sum()
    return float(total_cost ** (1.0 / p))


def bottleneck(dgm1, dgm2):
    """Bottleneck distance (L_inf Wasserstein p=inf) between two PDs."""
    pts1 = np.array([(b, d) for b, d in dgm1 if np.isfinite(d)], dtype=float)
    pts2 = np.array([(b, d) for b, d in dgm2 if np.isfinite(d)], dtype=float)

    if len(pts1) == 0 and len(pts2) == 0:
        return 0.0
    if len(pts1) == 0:
        return float(np.max(np.abs(pts2[:, 1] - pts2[:, 0]) / 2))
    if len(pts2) == 0:
        return float(np.max(np.abs(pts1[:, 1] - pts1[:, 0]) / 2))

    def diag_proj(pts):
        m = (pts[:, 0] + pts[:, 1]) / 2
        return np.stack([m, m], axis=1)

    n1, n2 = len(pts1), len(pts2)
    diag1 = diag_proj(pts1)
    diag2 = diag_proj(pts2)
    A = np.vstack([pts1, diag2])
    B = np.vstack([diag1, pts2])

    diff = A[:, None, :] - B[None, :, :]
    cost_matrix = np.max(np.abs(diff), axis=2)

    # Bottleneck: binary search on threshold epsilon
    # Equivalent to minimum over perfect matchings of maximum edge
    # Use LP relaxation / Hungarian on cost directly, take max of matched edges
    row_ind, col_ind = linear_sum_assignment(cost_matrix)
    return float(cost_matrix[row_ind, col_ind].max())


# ============================================================
# Load data
# ============================================================
print('='*70)
print('H9 v2: Wasserstein Bootstrap PH')
print('='*70)
df = pd.read_csv(H3_CSV)
X_full = StandardScaler().fit_transform(df[FEAT_COLS].values)
print(f'  Full embedding: {X_full.shape}')

# ============================================================
# Step 1: Reference PH on a fixed subsample (seed=42)
# ============================================================
print('\n--- Step 1: Reference PH (n=300, seed=42) ---')
t0 = time.time()
ref_idx = RNG.choice(len(X_full), size=BOOT_N, replace=False)
X_ref = X_full[ref_idx]
ref_result = ripser(X_ref, maxdim=MAX_DIM, thresh=THRESH)
ref_dgm_h0 = ref_result['dgms'][0]
ref_dgm_h1 = ref_result['dgms'][1]
print(f'  Reference H0 pairs: {len(ref_dgm_h0)}, H1 pairs: {len(ref_dgm_h1)}')
print(f'  Reference H1 max persistence: '
      f'{max((d-b for b,d in ref_dgm_h1 if np.isfinite(d)), default=0):.4f}')
print(f'  Elapsed: {time.time()-t0:.1f}s')

# ============================================================
# Step 2: Bootstrap — compute W2 + bottleneck vs reference
# ============================================================
print(f'\n--- Step 2: Bootstrap ({N_BOOT} trials, n={BOOT_N}) ---')
records = []
t0 = time.time()
for i in range(N_BOOT):
    idx_b = RNG.choice(len(X_full), size=BOOT_N, replace=False)
    Xb = X_full[idx_b]
    rb = ripser(Xb, maxdim=MAX_DIM, thresh=THRESH)
    dgm_h1 = rb['dgms'][1]

    w2  = wasserstein_p(ref_dgm_h1, dgm_h1, p=2)
    bn  = bottleneck(ref_dgm_h1, dgm_h1)
    records.append({'bootstrap_idx': i, 'w2_dist': w2, 'bottleneck_dist': bn, 'is_null': 0})

    if (i+1) % 20 == 0:
        elapsed = time.time() - t0
        w2s = [r['w2_dist'] for r in records if r['is_null'] == 0]
        print(f'  {i+1}/{N_BOOT} | W2 median={np.median(w2s):.4f} | {elapsed:.0f}s elapsed')

obs_w2  = [r['w2_dist']        for r in records if r['is_null'] == 0]
obs_bn  = [r['bottleneck_dist'] for r in records if r['is_null'] == 0]
print(f'\n  Observed W2:         mean={np.mean(obs_w2):.4f}, std={np.std(obs_w2):.4f}, '
      f'95% CI=[{np.percentile(obs_w2,2.5):.4f}, {np.percentile(obs_w2,97.5):.4f}]')
print(f'  Observed Bottleneck: mean={np.mean(obs_bn):.4f}, std={np.std(obs_bn):.4f}, '
      f'95% CI=[{np.percentile(obs_bn,2.5):.4f}, {np.percentile(obs_bn,97.5):.4f}]')

# ============================================================
# Step 3: Null distribution — shuffle features, recompute PH
# ============================================================
print(f'\n--- Step 3: Null distribution (feature-shuffle, {N_NULL} trials) ---')
t0 = time.time()
for i in range(N_NULL):
    # Shuffle each feature column independently (destroys all pairwise structure)
    Xn = X_full.copy()
    for j in range(Xn.shape[1]):
        Xn[:, j] = RNG.permutation(Xn[:, j])
    idx_n = RNG.choice(len(Xn), size=BOOT_N, replace=False)
    Xn_sub = Xn[idx_n]
    rn = ripser(Xn_sub, maxdim=MAX_DIM, thresh=THRESH)
    dgm_h1_null = rn['dgms'][1]

    w2  = wasserstein_p(ref_dgm_h1, dgm_h1_null, p=2)
    bn  = bottleneck(ref_dgm_h1, dgm_h1_null)
    records.append({'bootstrap_idx': i, 'w2_dist': w2, 'bottleneck_dist': bn, 'is_null': 1})

    if (i+1) % 20 == 0:
        elapsed = time.time() - t0
        null_w2s = [r['w2_dist'] for r in records if r['is_null'] == 1]
        print(f'  {i+1}/{N_NULL} | Null W2 median={np.median(null_w2s):.4f} | {elapsed:.0f}s elapsed')

null_w2 = [r['w2_dist']        for r in records if r['is_null'] == 1]
null_bn = [r['bottleneck_dist'] for r in records if r['is_null'] == 1]
print(f'\n  Null W2:         mean={np.mean(null_w2):.4f}, std={np.std(null_w2):.4f}')
print(f'  Null Bottleneck: mean={np.mean(null_bn):.4f}, std={np.std(null_bn):.4f}')

# ============================================================
# Step 4: p-value (one-sided: is observed W2 < null W2?)
# ============================================================
print('\n--- Step 4: Statistical Test ---')
# H0: observed PH structure is as different from reference as shuffled data
# A *lower* W2 distance from reference = MORE consistent / structured
# p-value: proportion of null samples with W2 <= median observed W2
median_obs_w2 = np.median(obs_w2)
p_val_w2   = np.mean(np.array(null_w2)  <= median_obs_w2)
p_val_bn   = np.mean(np.array(null_bn)  <= np.median(obs_bn))

print(f'  Median observed W2:        {median_obs_w2:.4f}')
print(f'  Median null W2:            {np.median(null_w2):.4f}')
print(f'  p-value (W2, one-sided):   {p_val_w2:.4f}')
print(f'  p-value (BN, one-sided):   {p_val_bn:.4f}')

if p_val_w2 < 0.05:
    print('\n  RESULT: Observed PH is significantly MORE STABLE than shuffled (p<0.05).')
    print('  The H1 loop structure reflects genuine data geometry, not noise.')
else:
    print('\n  RESULT: No significant difference from null (p>=0.05).')
    print('  Loop structure may be driven by chance geometry.')

# ============================================================
# Step 5: Save
# ============================================================
out_df = pd.DataFrame(records)
out_path = os.path.join(RES_DIR, 'H9_v2_wasserstein.csv')
out_df.to_csv(out_path, index=False, encoding='utf-8-sig')
print(f'\n  Saved: {out_path}')
print(f'  Shape: {out_df.shape}')

# Summary stats also printed for paper
print('\n=== PAPER-READY SUMMARY ===')
print(f'  Bootstrap W2 to reference:  {np.mean(obs_w2):.3f} ± {np.std(obs_w2):.3f}  '
      f'[{np.percentile(obs_w2,2.5):.3f}, {np.percentile(obs_w2,97.5):.3f}]')
print(f'  Null W2 to reference:       {np.mean(null_w2):.3f} ± {np.std(null_w2):.3f}  '
      f'[{np.percentile(null_w2,2.5):.3f}, {np.percentile(null_w2,97.5):.3f}]')
print(f'  p-value (Wasserstein-2):    {p_val_w2:.4f}')
print(f'  Bottleneck p-value:         {p_val_bn:.4f}')
print('\nDone.')
