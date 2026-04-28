"""H27: 푸리에 변환 심층 분석 — Power Spectral Density(PSD) + Phase + Coherence.

지금까지 amp_12m_norm 한 점만 봤다. 본 분석은 FFT를 *완전히* 활용해
- 전체 PSD: k=1(12m), k=2(6m), k=3(4m), k=4(3m·분기) 고조파 식별
- Phase: 어느 월에 정확히 피크하는지 (12월 vs 11월)
- Cross-coherence: 활동·부처·outcome 간 *주파수별 동조*
- 사업원형별 PSD 평균 비교

산출물:
  data/results/H27_psd_archetype_avg.csv     - 4 원형 평균 PSD
  data/results/H27_phase_distribution.csv    - 활동별 12월/11월/1월 phase
  data/results/H27_coherence_intra_archetype.csv  - 원형 내 활동 간 평균 coherence
  data/figs/h27_psd_archetype.png            - PSD 비교 차트
  data/figs/h27_phase_polar.png              - 12월 phase 극좌표
  data/figs/h27_coherence_heatmap.png        - 원형 간 coherence
"""
import os, sys, warnings
warnings.filterwarnings('ignore')

try:
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
except AttributeError:
    pass

import numpy as np
import pandas as pd
import duckdb
import matplotlib.pyplot as plt
import matplotlib as mpl
import scienceplots
import seaborn as sns
plt.style.use(['science', 'no-latex', 'grid'])
plt.rcParams.update({
    'font.size': 20, 'axes.titlesize': 22, 'axes.labelsize': 20,
    'xtick.labelsize': 17, 'ytick.labelsize': 17,
    'legend.fontsize': 17, 'legend.title_fontsize': 17,
    'figure.titlesize': 23, 'lines.linewidth': 2.5, 'lines.markersize': 10,
    'axes.linewidth': 1.2, 'grid.alpha': 0.3,
    'mathtext.fontset': 'stix', 'mathtext.default': 'regular',
    'axes.unicode_minus': False,
})
for fname in ['Arial Unicode MS', 'Malgun Gothic', 'NanumGothic']:
    if any(fname.lower() in fn.name.lower() for fn in mpl.font_manager.fontManager.ttflist):
        mpl.rcParams['font.family'] = [fname, 'Arial Unicode MS', 'Times New Roman', 'DejaVu Sans']
        break
mpl.rcParams['axes.unicode_minus'] = False
sns.set_palette('Set2')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB   = os.path.join(ROOT, 'data', 'warehouse.duckdb')
RES  = os.path.join(ROOT, 'data', 'results')
FIG  = os.path.join(ROOT, 'data', 'figs')
os.makedirs(RES, exist_ok=True)
os.makedirs(FIG, exist_ok=True)
H3_CSV = os.path.join(RES, 'H3_activity_embedding_11y.csv')

print('=' * 70)
print('H27: 푸리에 변환 심층 분석 — PSD + Phase + Coherence')
print('=' * 70)

# ============================================================
# Step 1: 활동×연도 월별 시계열 + 사업원형 라벨
# ============================================================
print('\nStep 1: 데이터 로드')
emb = pd.read_csv(H3_CSV)
print(f'  H3 임베딩: {len(emb)} 활동')

# 회계거래 제외
PURE_ACCT = """(
    ACTV_NM ILIKE '%전출금%' OR ACTV_NM ILIKE '%타계정%' OR ACTV_NM ILIKE '%여유자금%'
 OR ACTV_NM ILIKE '%국고예탁%' OR ACTV_NM ILIKE '%기금예탁%' OR ACTV_NM ILIKE '%국고예치%'
 OR ACTV_NM ILIKE '%회계간거래%' OR ACTV_NM ILIKE '%회계간전출%')"""

con = duckdb.connect(DB, read_only=True)
raw = con.execute(f"""
    SELECT FLD_NM, OFFC_NM, PGM_NM, ACTV_NM,
           FSCL_YY AS year, EXE_M AS month, SUM(EP_AMT) AS amt
    FROM monthly_exec
    WHERE EXE_M BETWEEN 1 AND 12 AND FSCL_YY BETWEEN 2015 AND 2025
      AND NOT {PURE_ACCT}
    GROUP BY 1,2,3,4,5,6
""").fetchdf()
con.close()
print(f'  월별 집행 rows: {len(raw):,}')

# ============================================================
# Step 2: 활동×연도 월별 12-vector 패널
# ============================================================
print('\nStep 2: 활동×연도 12-vector 패널 구성')
KEY = ['FLD_NM', 'OFFC_NM', 'PGM_NM', 'ACTV_NM']
raw['key'] = list(zip(*[raw[c] for c in KEY]))

ay_panel = {}  # (key, year) -> 12-vec
for keys_tuple, g in raw.groupby(KEY):
    for yr, gy in g.groupby('year'):
        arr = np.zeros(12)
        for _, row in gy.iterrows():
            m = int(row['month']) - 1
            if 0 <= m < 12:
                arr[m] = float(row['amt'])
        if arr.sum() > 0 and (arr > 0).sum() >= 6:
            ay_panel[(keys_tuple, int(yr))] = arr

print(f'  유효 활동-연도: {len(ay_panel):,}')

# 원형 라벨 매핑 (H3 활동 단위)
emb['key'] = list(zip(emb['FLD_NM'], emb['OFFC_NM'], emb['PGM_NM'], emb['ACTV_NM']))
ARCHETYPE = {0: 'C0_personnel', 1: 'C1_direct_invest', 2: 'C2_chooyeon', 3: 'C3_normal'}
key_to_arch = dict(zip(emb['key'], emb['cluster'].map(ARCHETYPE)))

# ============================================================
# Step 3: 활동×연도 PSD 계산 (rfft → |X(k)|^2)
# ============================================================
print('\nStep 3: PSD 계산 (rfft)')
records = []
for (key, yr), arr in ay_panel.items():
    arr_centered = arr - arr.mean()
    X = np.fft.rfft(arr_centered)
    psd = np.abs(X)**2  # 7개 주파수 빈 (k=0..6)
    psd_norm = psd / psd[1:].sum() if psd[1:].sum() > 0 else psd
    arch = key_to_arch.get(key, 'noise')
    rec = {'archetype': arch, 'year': yr}
    for k in range(7):
        rec[f'psd_k{k}'] = psd[k]
        rec[f'psdnorm_k{k}'] = psd_norm[k]
    # phase 12월 진폭 = phase k=1
    rec['phase_k1'] = np.angle(X[1]) if len(X) > 1 else 0
    rec['amp_k1'] = np.abs(X[1]) if len(X) > 1 else 0
    records.append(rec)

psd_df = pd.DataFrame(records)
print(f'  PSD 패널: {len(psd_df)} 활동-연도')
print(f'  archetype 분포: {psd_df["archetype"].value_counts().to_dict()}')

# 원형별 PSD 평균
psd_avg = psd_df[psd_df['archetype'] != 'noise'].groupby('archetype')[
    [f'psdnorm_k{k}' for k in range(7)]].mean().reset_index()
psd_avg.to_csv(os.path.join(RES, 'H27_psd_archetype_avg.csv'), index=False)
print(f'  → H27_psd_archetype_avg.csv')

# ============================================================
# Step 4: Phase distribution (어느 월에 피크)
# ============================================================
print('\nStep 4: Phase 분석')
# k=1 (12-month period) phase: 0 = January 1, then 2π = December 31
# convert to peak month
psd_df['peak_month_k1'] = ((psd_df['phase_k1'] / (2*np.pi) * 12 + 0.5) % 12).round().astype(int)
psd_df.loc[psd_df['peak_month_k1'] == 0, 'peak_month_k1'] = 12

peak_dist = psd_df[psd_df['archetype'] != 'noise'].groupby(
    ['archetype', 'peak_month_k1']).size().reset_index(name='n')
peak_dist.to_csv(os.path.join(RES, 'H27_phase_distribution.csv'), index=False)

print(f'  → H27_phase_distribution.csv')
print('  원형별 peak month 모드 (가장 흔한 피크 월):')
for arch in ['C0_personnel', 'C1_direct_invest', 'C2_chooyeon', 'C3_normal']:
    sub = psd_df[(psd_df['archetype'] == arch)]
    if len(sub) > 0:
        mode = sub['peak_month_k1'].mode()
        print(f'    {arch}: mode = {mode.values[0] if len(mode) else "—"} 월 (N={len(sub)})')

# ============================================================
# Step 5: Cross-coherence (원형 내 활동 간 평균 coherence)
# ============================================================
print('\nStep 5: 원형 내 cross-coherence (k=1 시그널 동조)')
# coherence between two 12-month vectors u, v at frequency k:
# γ²(k) = |U(k) V(k)*|² / (|U(k)|² × |V(k)|²)
# For length-12 series: 7 frequency bins. We focus on k=1 (12-month period)
coh_records = []
for arch in ['C0_personnel', 'C1_direct_invest', 'C2_chooyeon', 'C3_normal']:
    sub = psd_df[psd_df['archetype'] == arch]
    if len(sub) < 5:
        continue
    # we don't have the original array here (lost in groupby) — use separately
    pass

# Re-iterate ay_panel with archetype filter
arch_arrays = {a: [] for a in ['C0_personnel', 'C1_direct_invest', 'C2_chooyeon', 'C3_normal']}
for (key, yr), arr in ay_panel.items():
    arch = key_to_arch.get(key)
    if arch in arch_arrays:
        arch_arrays[arch].append(arr - arr.mean())

# coherence: between pairs of fits, sample if too many
np.random.seed(42)
SAMPLE_PAIRS = 500
for arch, arrs in arch_arrays.items():
    if len(arrs) < 5:
        continue
    A = np.array(arrs)
    n = len(A)
    print(f'  {arch}: {n} arrays')
    # FFT all
    X = np.fft.rfft(A, axis=1)  # n × 7
    # average pairwise coherence at each k: |⟨X_i X_j*⟩|² / (⟨|X_i|²⟩ ⟨|X_j|²⟩)
    # Use spectral form: ratio of cross-power to sqrt(auto-power)
    for k in range(1, 7):
        # sample pairs
        idx_i = np.random.choice(n, size=min(SAMPLE_PAIRS, n*(n-1)//2), replace=True)
        idx_j = np.random.choice(n, size=min(SAMPLE_PAIRS, n*(n-1)//2), replace=True)
        mask = idx_i != idx_j
        idx_i = idx_i[mask]; idx_j = idx_j[mask]
        Xi = X[idx_i, k]; Xj = X[idx_j, k]
        # phase coherence (alignment of phases): magnitude of mean(exp(i Δφ))
        if len(Xi) > 0:
            dphi = np.angle(Xi) - np.angle(Xj)
            phase_coh = np.abs(np.mean(np.exp(1j * dphi)))
            # amplitude correlation
            amp_corr = np.corrcoef(np.abs(Xi), np.abs(Xj))[0, 1]
            coh_records.append({
                'archetype': arch, 'k': k, 'period_months': 12/k,
                'phase_coherence': phase_coh, 'amplitude_correlation': amp_corr,
                'n_pairs': len(Xi),
            })

coh_df = pd.DataFrame(coh_records)
coh_df.to_csv(os.path.join(RES, 'H27_coherence_intra_archetype.csv'), index=False)
print(f'  → H27_coherence_intra_archetype.csv')
print('\n  k=1 (12-month) phase coherence (1.0=완전 동조, 0=무관):')
print(coh_df[coh_df['k'] == 1].pivot_table(
    index='archetype', columns='k', values='phase_coherence'))

# ============================================================
# Step 6: 시각화
# ============================================================
print('\nStep 6: 시각화 figure 생성')

# (A) PSD 비교 — 4 원형의 normalized PSD
fig, ax = plt.subplots(figsize=(11, 6))
freqs = list(range(7))
labels = ['DC (k=0)', '12m (k=1)', '6m (k=2)', '4m (k=3)', '3m·분기 (k=4)', '2.4m (k=5)', '2m (k=6)']
arch_names = {'C0_personnel': '인건비형', 'C1_direct_invest': '자산취득형',
              'C2_chooyeon': '출연금형', 'C3_normal': '정상사업'}
arch_colors = {'C0_personnel': '#4C72B0', 'C1_direct_invest': '#DD8452',
               'C2_chooyeon': '#55A868', 'C3_normal': '#C44E52'}

for _, row in psd_avg.iterrows():
    vals = [row[f'psdnorm_k{k}'] for k in range(7)]
    ax.plot(freqs[1:], vals[1:], 'o-', label=arch_names.get(row['archetype'], row['archetype']),
            color=arch_colors.get(row['archetype'], '#888'), linewidth=2.5, markersize=10)

ax.set_xticks(freqs[1:])
ax.set_xticklabels(labels[1:], rotation=15, ha='right')
ax.set_ylabel('정규화 power spectral density')
ax.set_xlabel('주파수 빈 (period)')
ax.set_title('사업원형별 평균 PSD — 12개월 vs 분기·기타 고조파',
             fontweight='bold')
ax.legend(loc='best', frameon=True, fancybox=True)
plt.tight_layout()
plt.savefig(os.path.join(FIG, 'h27_psd_archetype.png'), dpi=200, bbox_inches='tight')
plt.close()
print(f'  → h27_psd_archetype.png')

# (B) Phase polar plot — 12월/1월 피크 분포
from matplotlib.patches import Wedge
fig, axes = plt.subplots(2, 2, figsize=(11, 11), subplot_kw=dict(projection='polar'))
for ax, arch in zip(axes.flatten(), ['C0_personnel', 'C1_direct_invest', 'C2_chooyeon', 'C3_normal']):
    sub = psd_df[psd_df['archetype'] == arch]
    if len(sub) == 0:
        ax.set_title(arch_names.get(arch, arch))
        continue
    # k=1 phase to angle (peak month)
    angles = sub['phase_k1'].values
    # histogram on polar
    ax.hist(angles, bins=12, color=arch_colors.get(arch, '#888'), alpha=0.7,
            edgecolor='white', linewidth=1.5)
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    ax.set_xticks(np.linspace(0, 2*np.pi, 12, endpoint=False))
    ax.set_xticklabels(['1','2','3','4','5','6','7','8','9','10','11','12'])
    ax.set_title(f'{arch_names.get(arch, arch)}\n(N={len(sub)})', fontweight='bold', pad=20)
    ax.set_yticklabels([])
fig.suptitle('사업원형별 12개월 주기 Phase 분포 — 어느 월에 피크하는가',
             fontweight='bold', y=1.00)
plt.tight_layout()
plt.savefig(os.path.join(FIG, 'h27_phase_polar.png'), dpi=200, bbox_inches='tight')
plt.close()
print(f'  → h27_phase_polar.png')

# (C) Phase coherence heatmap — 원형별 × 주파수별 동조
fig, ax = plt.subplots(figsize=(10, 5))
piv = coh_df.pivot_table(index='archetype', columns='k', values='phase_coherence')
piv.index = piv.index.map(arch_names)
piv.columns = [f'k={k}\n({12/k:.1f}m)' for k in piv.columns]
sns.heatmap(piv, annot=True, fmt='.2f', cmap='RdYlGn', vmin=0, vmax=1,
            cbar_kws={'label': 'Phase coherence (1.0 = 완전 동조)'}, ax=ax,
            linewidths=0.5)
ax.set_title('원형 내 활동 간 Phase Coherence — 같은 원형 활동들이 같은 월에 피크하는가',
             fontweight='bold')
ax.set_xlabel('주파수 빈')
ax.set_ylabel('')
plt.tight_layout()
plt.savefig(os.path.join(FIG, 'h27_coherence_heatmap.png'), dpi=200, bbox_inches='tight')
plt.close()
print(f'  → h27_coherence_heatmap.png')

print('\n완료 (H27 PSD + Phase + Coherence).')
print('출력:')
print('  data/results/H27_psd_archetype_avg.csv')
print('  data/results/H27_phase_distribution.csv')
print('  data/results/H27_coherence_intra_archetype.csv')
print('  data/figs/h27_psd_archetype.png')
print('  data/figs/h27_phase_polar.png')
print('  data/figs/h27_coherence_heatmap.png')
