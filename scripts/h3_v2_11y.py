"""H3 v2 (11y): 활동 임베딩 11년 재추출 (monthly_exec 2015~2025).

차이점:
  - WHERE 2015~2025 (5y → 11y)
  - 최소 6년 보유 활동만 (4년 → 6년)
  - 출력 dir/csv suffix _11y
  - expenditure_*는 2020+만이라 예산 구성 피처는 그대로

원본 H3:

목적
  - 분야 단위 분석(N=15)의 한계를 넘어 사업/활동 단위(N≈2,600)에서
    게임화 패턴을 임베딩하고 군집 구조를 본다.
  - "분야별 게임화 패턴이 어떻게 다른가?"를
    클러스터×분야 cross-tab으로 정량화.

피처 (활동 1개당 1행)
  게임화 시그니처 (월별 시계열 → 연도 평균):
    amp_12m_norm   1cycle/year FFT 진폭 (정규화)
    amp_6m_norm    2cycle/year FFT 진폭
    hhi_period     월별 비중 HHI
    q4_pct         Q4 집중도
    dec_pct        12월 집중도
    cv_monthly     월별 변동계수
  예산 구성 (편성목 기반):
    chooyeon_pct   출연금 비중
    operating_pct  운영비 비중
    direct_invest_pct  자산취득·건설비 비중
    personnel_pct  인건비 비중
  스케일/추이:
    log_annual     연 평균 집행 log10
    growth_cagr    예산 CAGR (확정예산 기반)

방법
  Z-score → UMAP(2D) → HDBSCAN
  → 클러스터별 평균 프로파일 + 분야×클러스터 분포
"""
import os, sys, io, warnings
import numpy as np
import pandas as pd
import duckdb
from scipy import fft as scfft
from sklearn.preprocessing import StandardScaler
import umap
import hdbscan
import matplotlib.pyplot as plt
import matplotlib as mpl
import scienceplots
import seaborn as sns
plt.style.use(['science', 'no-latex', 'grid'])
plt.rcParams.update({
    'font.size': 20,
    'axes.titlesize': 22,
    'axes.labelsize': 20,
    'xtick.labelsize': 17,
    'ytick.labelsize': 17,
    'legend.fontsize': 17,
    'legend.title_fontsize': 17,
    'figure.titlesize': 23,
    'lines.linewidth': 2.5,
    'lines.markersize': 10,
    'axes.linewidth': 1.2,
    'grid.alpha': 0.3,
    'mathtext.fontset': 'stix',
    'mathtext.default': 'regular',
    'axes.unicode_minus': False,
})
for fname in ['Arial Unicode MS', 'Malgun Gothic', 'NanumGothic']:
    if any(fname.lower() in fn.name.lower() for fn in mpl.font_manager.fontManager.ttflist):
        mpl.rcParams['font.family'] = [fname, 'Arial Unicode MS', 'Times New Roman', 'DejaVu Sans']
        break
mpl.rcParams['axes.unicode_minus'] = False
sns.set_palette('Set2')

warnings.filterwarnings('ignore')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, 'data', 'warehouse.duckdb')
OUT_DIR = os.path.join(ROOT, 'data', 'figs', 'h3_embed_11y')
RES_DIR = os.path.join(ROOT, 'data', 'results')
SUFFIX = '_11y'
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(RES_DIR, exist_ok=True)

KFONT = mpl.rcParams.get('font.family', 'Malgun Gothic')

PURE_ACCT = """(
    ACTV_NM ILIKE '%전출금%' OR ACTV_NM ILIKE '%타계정%' OR ACTV_NM ILIKE '%여유자금%'
 OR ACTV_NM ILIKE '%국고예탁%' OR ACTV_NM ILIKE '%기금예탁%' OR ACTV_NM ILIKE '%국고예치%'
 OR ACTV_NM ILIKE '%회계간거래%' OR ACTV_NM ILIKE '%회계간전출%'
 OR ACTV_NM ILIKE '%회계기금간%' OR ACTV_NM ILIKE '%여유자금운용%'
)"""

con = duckdb.connect(DB, read_only=True)

# ============================================================
# Step 1: 활동×연도 월별 집행 → 게임화 시그니처
# ============================================================
print('='*70)
print('Step 1: 활동×연도 월별 시계열 게임화 시그니처')
print('='*70)

raw = con.execute(f"""
    SELECT FLD_NM, OFFC_NM, PGM_NM, ACTV_NM, FSCL_YY AS year, EXE_M AS month,
           SUM(EP_AMT) AS amt
    FROM monthly_exec
    WHERE EXE_M BETWEEN 1 AND 12
      AND FSCL_YY BETWEEN 2015 AND 2025
      AND NOT {PURE_ACCT}
    GROUP BY 1,2,3,4,5,6
""").fetchdf()
print(f'  raw monthly rows: {len(raw):,}')

key_cols = ['FLD_NM', 'OFFC_NM', 'PGM_NM', 'ACTV_NM']
records = []
for keys, g in raw.groupby(key_cols):
    by_year = {}
    for y, gy in g.groupby('year'):
        arr = np.zeros(12)
        for _, r in gy.iterrows():
            arr[int(r['month']) - 1] = r['amt']
        if arr.sum() <= 0 or (arr > 0).sum() < 6:
            continue
        by_year[int(y)] = arr

    if len(by_year) < 6:  # 11년 중 최소 6년
        continue

    sigs = []
    for y, arr in by_year.items():
        total = arr.sum()
        pct = arr / total
        yf = scfft.fft(arr - arr.mean())
        amp_12 = abs(yf[1]) * 2 / 12 / (total / 12)
        amp_6  = abs(yf[2]) * 2 / 12 / (total / 12)
        hhi = (pct ** 2).sum()
        q4 = pct[9:12].sum()
        dec = pct[11]
        cv = arr.std() / (arr.mean() + 1e-9)
        sigs.append([amp_12, amp_6, hhi, q4, dec, cv, total])
    sigs = np.array(sigs)

    feats = {
        'FLD_NM':  keys[0],
        'OFFC_NM': keys[1],
        'PGM_NM':  keys[2],
        'ACTV_NM': keys[3],
        'year_n':  len(by_year),
        'amp_12m_norm': sigs[:, 0].mean(),
        'amp_6m_norm':  sigs[:, 1].mean(),
        'hhi_period':   sigs[:, 2].mean(),
        'q4_pct':       sigs[:, 3].mean(),
        'dec_pct':      sigs[:, 4].mean(),
        'cv_monthly':   sigs[:, 5].mean(),
        'mean_annual':  sigs[:, 6].mean(),
    }
    records.append(feats)

gaming_df = pd.DataFrame(records)
print(f'  활동(≥4년) feature rows: {len(gaming_df):,}')

# ============================================================
# Step 2: 활동 단위 예산 구성 (출연금/운영비/...)
# ============================================================
print('\n' + '='*70)
print('Step 2: 활동 단위 예산 구성 (편성목 비중)')
print('='*70)
comp_df = con.execute("""
    WITH t AS (
      SELECT FLD_NM, OFFC_NM, PGM_NM, ACTV_NM,
             SUM(Y_YY_DFN_KCUR_AMT) AS total,
             SUM(CASE WHEN CITM_NM IN ('일반출연금','연구개발출연금','출연금')
                      THEN Y_YY_DFN_KCUR_AMT ELSE 0 END) AS chooyeon,
             SUM(CASE WHEN CITM_NM = '자치단체이전'
                      THEN Y_YY_DFN_KCUR_AMT ELSE 0 END) AS local_transfer,
             SUM(CASE WHEN CITM_NM IN ('인건비')
                      THEN Y_YY_DFN_KCUR_AMT ELSE 0 END) AS personnel,
             SUM(CASE WHEN CITM_NM IN ('운영비','업무추진비','여비','직무수행경비')
                      THEN Y_YY_DFN_KCUR_AMT ELSE 0 END) AS operating,
             SUM(CASE WHEN CITM_NM IN ('자산취득비','유형자산','무형자산','건설비')
                      THEN Y_YY_DFN_KCUR_AMT ELSE 0 END) AS direct_invest
      FROM expenditure_item
      WHERE SBUDG_DGR=0 AND FSCL_YY BETWEEN 2020 AND 2025
      GROUP BY 1,2,3,4
    )
    SELECT FLD_NM, OFFC_NM, PGM_NM, ACTV_NM,
           total*1.0/nullif(total,0) AS _ck,
           chooyeon*1.0/nullif(total,0)        AS chooyeon_pct,
           local_transfer*1.0/nullif(total,0)  AS local_transfer_pct,
           personnel*1.0/nullif(total,0)       AS personnel_pct,
           operating*1.0/nullif(total,0)       AS operating_pct,
           direct_invest*1.0/nullif(total,0)   AS direct_invest_pct,
           total                               AS total_budget
    FROM t WHERE total > 0
""").fetchdf()
print(f'  활동 budget composition rows: {len(comp_df):,}')

# CAGR (예산 기반)
print('\n  예산 CAGR 계산...')
cagr_df = con.execute("""
    WITH yr AS (
      SELECT FLD_NM, OFFC_NM, PGM_NM, ACTV_NM, FSCL_YY,
             SUM(Y_YY_DFN_KCUR_AMT) AS bdg
      FROM expenditure_budget
      WHERE SBUDG_DGR=0 AND FSCL_YY BETWEEN 2020 AND 2025
      GROUP BY 1,2,3,4,5
      HAVING bdg > 0
    ),
    ranked AS (
      SELECT *,
        FIRST_VALUE(bdg) OVER (PARTITION BY FLD_NM,OFFC_NM,PGM_NM,ACTV_NM ORDER BY FSCL_YY) AS bdg0,
        LAST_VALUE(bdg)  OVER (PARTITION BY FLD_NM,OFFC_NM,PGM_NM,ACTV_NM ORDER BY FSCL_YY
                               ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS bdg1,
        FIRST_VALUE(FSCL_YY) OVER (PARTITION BY FLD_NM,OFFC_NM,PGM_NM,ACTV_NM ORDER BY FSCL_YY) AS y0,
        LAST_VALUE(FSCL_YY)  OVER (PARTITION BY FLD_NM,OFFC_NM,PGM_NM,ACTV_NM ORDER BY FSCL_YY
                                  ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS y1,
        COUNT(*) OVER (PARTITION BY FLD_NM,OFFC_NM,PGM_NM,ACTV_NM) AS n
      FROM yr
    )
    SELECT DISTINCT FLD_NM, OFFC_NM, PGM_NM, ACTV_NM,
           CASE WHEN y1>y0 AND bdg0>0
                THEN POWER(bdg1/bdg0, 1.0/(y1-y0)) - 1 ELSE NULL END AS growth_cagr
    FROM ranked WHERE n >= 3
""").fetchdf()
print(f'  CAGR rows: {len(cagr_df):,}')

# ============================================================
# Step 3: 조인 + 결측 정리
# ============================================================
print('\n' + '='*70)
print('Step 3: 피처 행렬 조인')
print('='*70)
df = (gaming_df
      .merge(comp_df, on=key_cols, how='inner')
      .merge(cagr_df, on=key_cols, how='left'))
df['log_annual'] = np.log10(df['mean_annual'] + 1)

# CAGR clip (outlier 보호)
df['growth_cagr'] = df['growth_cagr'].clip(-0.9, 5.0)
df['growth_cagr'] = df['growth_cagr'].fillna(df['growth_cagr'].median())

feat_cols = [
    'amp_12m_norm','amp_6m_norm','hhi_period','q4_pct','dec_pct','cv_monthly',
    'chooyeon_pct','operating_pct','direct_invest_pct','personnel_pct',
    'log_annual','growth_cagr',
]
df = df.dropna(subset=feat_cols)
print(f'  최종 활동 N = {len(df):,}, 피처 {len(feat_cols)}개')
print('  피처 요약:')
print(df[feat_cols].describe().round(3).to_string())

# ============================================================
# Step 4: UMAP + HDBSCAN
# ============================================================
print('\n' + '='*70)
print('Step 4: UMAP(2D) + HDBSCAN')
print('='*70)
X = StandardScaler().fit_transform(df[feat_cols].values)

reducer = umap.UMAP(n_neighbors=30, min_dist=0.05, metric='euclidean',
                    n_components=2, random_state=42)
emb = reducer.fit_transform(X)
df['u1'] = emb[:, 0]
df['u2'] = emb[:, 1]

clusterer = hdbscan.HDBSCAN(min_cluster_size=60, min_samples=10,
                            cluster_selection_method='eom')
labels = clusterer.fit_predict(emb)
df['cluster'] = labels

n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
n_noise = (labels == -1).sum()
print(f'  클러스터 = {n_clusters}, 노이즈 = {n_noise} ({n_noise/len(df)*100:.1f}%)')

# ============================================================
# Step 5: 클러스터 프로파일
# ============================================================
print('\n' + '='*70)
print('Step 5: 클러스터 프로파일 (z-score 평균)')
print('='*70)
prof = (df[df['cluster']>=0]
        .groupby('cluster')[feat_cols]
        .mean()
        .round(3))
prof['n'] = df[df['cluster']>=0].groupby('cluster').size()
print(prof.to_string())

# 표준화 z-score 프로파일 (해석용)
mu = df[feat_cols].mean()
sd = df[feat_cols].std()
zprof = ((prof[feat_cols] - mu) / sd).round(2)
zprof['n'] = prof['n']
print('\n  z-score 프로파일 (전체 평균 대비):')
print(zprof.to_string())

# ============================================================
# Step 6: 분야 × 클러스터 cross-tab
# ============================================================
print('\n' + '='*70)
print('Step 6: 분야 × 클러스터 분포 (행 비율)')
print('='*70)
ct = pd.crosstab(df['FLD_NM'], df['cluster'], normalize='index').round(3)
ct['n'] = df.groupby('FLD_NM').size()
ct = ct.sort_values('n', ascending=False)
print(ct.to_string())

# 분야별 우세 클러스터
dom = ct.drop(columns=['n']).idxmax(axis=1)
print('\n  분야별 우세 클러스터:')
for fld, cl in dom.items():
    pct = ct.loc[fld, cl] * 100
    print(f'    {fld:20s} → cluster {cl}  ({pct:.0f}%)')

# ============================================================
# Step 7: 부처 × KPI(클러스터) 이분그래프 + 커뮤니티
# ============================================================
print('\n' + '='*70)
print('Step 7: 부처 × 클러스터 이분그래프 / 커뮤니티 디텍션')
print('='*70)
import networkx as nx
from networkx.algorithms import community as nxcom

# 부처 단위로 활동을 클러스터 분포로 요약 → 부처 노드
sub = df[df['cluster']>=0].copy()
ofc_x_cl = pd.crosstab(sub['OFFC_NM'], sub['cluster'])
# 활동 N <5 인 부처는 제외 (노이즈)
mask = ofc_x_cl.sum(axis=1) >= 5
ofc_x_cl = ofc_x_cl[mask]
print(f'  부처 N(>=5 actv) = {len(ofc_x_cl)}, 클러스터 N = {ofc_x_cl.shape[1]}')

# 부처 간 cosine 유사도 → 부처 그래프
from sklearn.metrics.pairwise import cosine_similarity
P = ofc_x_cl.div(ofc_x_cl.sum(axis=1), axis=0).values
sim = cosine_similarity(P)
np.fill_diagonal(sim, 0)

G = nx.Graph()
ofc_names = list(ofc_x_cl.index)
for o in ofc_names:
    G.add_node(o)
THRESH = 0.6
for i in range(len(ofc_names)):
    for j in range(i+1, len(ofc_names)):
        if sim[i,j] > THRESH:
            G.add_edge(ofc_names[i], ofc_names[j], weight=sim[i,j])
print(f'  edges (sim>{THRESH}) = {G.number_of_edges()}')

comms = list(nxcom.greedy_modularity_communities(G, weight='weight'))
print(f'  Louvain-like 커뮤니티 N = {len(comms)}')
for ci, c in enumerate(sorted(comms, key=len, reverse=True)[:5]):
    print(f'    [C{ci}] N={len(c)}: {sorted(list(c))[:6]}{"..." if len(c)>6 else ""}')

ofc_comm = {}
for ci, c in enumerate(comms):
    for o in c:
        ofc_comm[o] = ci

# ============================================================
# Step 8: 저장 (CSV + 그림)
# ============================================================
print('\n' + '='*70)
print('Step 8: 저장')
print('='*70)
df_out = df[key_cols + feat_cols + ['cluster','u1','u2','year_n','total_budget']]
csv_path = os.path.join(RES_DIR, f'H3_activity_embedding{SUFFIX}.csv')
df_out.to_csv(csv_path, index=False, encoding='utf-8-sig')
print(f'  활동 임베딩: {csv_path} ({len(df_out)} rows)')

prof_path = os.path.join(RES_DIR, f'H3_cluster_profile{SUFFIX}.csv')
zprof.to_csv(prof_path, encoding='utf-8-sig')
print(f'  클러스터 프로파일: {prof_path}')

ct_path = os.path.join(RES_DIR, f'H3_field_x_cluster{SUFFIX}.csv')
ct.to_csv(ct_path, encoding='utf-8-sig')
print(f'  분야×클러스터: {ct_path}')

ofc_comm_df = pd.DataFrame([(o, ofc_comm[o]) for o in ofc_comm], columns=['OFFC_NM','community'])
ofc_comm_df.to_csv(os.path.join(RES_DIR, f'H3_ministry_community{SUFFIX}.csv'),
                   index=False, encoding='utf-8-sig')

# ── Figure A: UMAP scatter (클러스터별) ─────────────
fig, axes = plt.subplots(1, 2, figsize=(15, 6.5))
ax = axes[0]
palette = plt.get_cmap('tab10')
for cl in sorted(df['cluster'].unique()):
    sub_ = df[df['cluster']==cl]
    color = '#bbbbbb' if cl == -1 else palette(cl % 10)
    ax.scatter(sub_['u1'], sub_['u2'], s=10, c=[color], alpha=0.6,
               label=f'cluster {cl} (n={len(sub_)})')
ax.set_title('UMAP 임베딩 — HDBSCAN 클러스터')
ax.set_xlabel('UMAP 1'); ax.set_ylabel('UMAP 2')
ax.legend(loc='best', fontsize=8)
ax.grid(alpha=0.3)

# 분야별 색
ax = axes[1]
top_flds = df['FLD_NM'].value_counts().head(8).index.tolist()
palette2 = plt.get_cmap('tab20')
for i, f in enumerate(top_flds):
    sub_ = df[df['FLD_NM']==f]
    ax.scatter(sub_['u1'], sub_['u2'], s=8, c=[palette2(i)], alpha=0.6, label=f'{f} (n={len(sub_)})')
others = df[~df['FLD_NM'].isin(top_flds)]
ax.scatter(others['u1'], others['u2'], s=4, c='#dddddd', alpha=0.4, label='기타')
ax.set_title('UMAP 임베딩 — 분야별 (상위 8개)')
ax.set_xlabel('UMAP 1'); ax.set_ylabel('UMAP 2')
ax.legend(loc='best', fontsize=8, ncol=2)
ax.grid(alpha=0.3)
plt.tight_layout()
fig.savefig(os.path.join(OUT_DIR, 'H3_umap_scatter.png'), dpi=200, bbox_inches='tight')
plt.close()

# ── Figure B: 클러스터 프로파일 heatmap ────────────
fig, ax = plt.subplots(figsize=(12, 6))
import seaborn as sns
sns.heatmap(zprof.drop(columns='n').T, annot=True, fmt='.2f', cmap='RdBu_r',
            center=0, ax=ax, cbar_kws={'label':'z-score'})
ax.set_title('클러스터별 피처 z-score 프로파일')
ax.set_xlabel(f'cluster (총 N: {zprof["n"].sum()})')
plt.tight_layout()
fig.savefig(os.path.join(OUT_DIR, 'H3_cluster_profile.png'), dpi=200, bbox_inches='tight')
plt.close()

# ── Figure C: 분야 × 클러스터 heatmap ──────────────
fig, ax = plt.subplots(figsize=(12, 7))
sns.heatmap(ct.drop(columns='n'), annot=True, fmt='.2f', cmap='YlOrRd',
            ax=ax, cbar_kws={'label':'활동 비율'})
ax.set_title('분야별 클러스터 분포 (행=분야, 행 합=1)')
plt.tight_layout()
fig.savefig(os.path.join(OUT_DIR, 'H3_field_cluster_heatmap.png'), dpi=200, bbox_inches='tight')
plt.close()

# ============================================================
# Step 9: cluster 2 (지배 클러스터) 내부 sub-clustering
# ============================================================
print('\n' + '='*70)
print('Step 9: cluster 2 (정상 사업) 내부 sub-clustering')
print('='*70)
mask_c2 = df['cluster'] == 2
df_c2 = df[mask_c2].copy()
X2 = StandardScaler().fit_transform(df_c2[feat_cols].values)
red2 = umap.UMAP(n_neighbors=20, min_dist=0.0, n_components=2, random_state=42)
emb2 = red2.fit_transform(X2)
df_c2['v1'] = emb2[:,0]; df_c2['v2'] = emb2[:,1]
sub_clus = hdbscan.HDBSCAN(min_cluster_size=40, min_samples=5,
                            cluster_selection_method='leaf').fit_predict(emb2)
df_c2['subcluster'] = sub_clus
n_sub = len(set(sub_clus)) - (1 if -1 in sub_clus else 0)
print(f'  sub-cluster 수 = {n_sub}, 노이즈 = {(sub_clus==-1).sum()} ({(sub_clus==-1).mean()*100:.1f}%)')
sub_prof = df_c2[df_c2['subcluster']>=0].groupby('subcluster')[feat_cols].mean().round(3)
sub_prof['n'] = df_c2[df_c2['subcluster']>=0].groupby('subcluster').size()
zsub = ((sub_prof[feat_cols] - mu) / sd).round(2); zsub['n'] = sub_prof['n']
print('\n  sub-cluster z-score 프로파일:')
print(zsub.to_string())

ct_sub = pd.crosstab(df_c2['FLD_NM'], df_c2['subcluster'], normalize='index').round(3)
ct_sub['n'] = df_c2.groupby('FLD_NM').size()
ct_sub = ct_sub.sort_values('n', ascending=False)
print('\n  분야 × sub-cluster (cluster 2 내부, 행 비율):')
print(ct_sub.to_string())

df_c2[key_cols + ['subcluster','v1','v2']].to_csv(
    os.path.join(RES_DIR, f'H3_cluster2_subembedding{SUFFIX}.csv'),
    index=False, encoding='utf-8-sig')

# ============================================================
# Step 10: 부처 시그니처 유사도 그래프 (원본 피처 평균 기반)
# ============================================================
print('\n' + '='*70)
print('Step 10: 부처 그래프 (12차원 피처 평균 cosine)')
print('='*70)
sub2 = df.copy()
ofc_feat = sub2.groupby('OFFC_NM')[feat_cols].mean()
ofc_n = sub2.groupby('OFFC_NM').size()
ofc_feat = ofc_feat[ofc_n >= 5]
ofc_n = ofc_n[ofc_n >= 5]
print(f'  부처 N = {len(ofc_feat)}')

# z-score 후 cosine
ofc_z = (ofc_feat - ofc_feat.mean()) / ofc_feat.std()
sim2 = cosine_similarity(ofc_z.values)
np.fill_diagonal(sim2, 0)

G2 = nx.Graph()
ofc_names2 = list(ofc_feat.index)
for o in ofc_names2:
    G2.add_node(o, weight=int(ofc_n[o]))
THRESH2 = 0.55
for i in range(len(ofc_names2)):
    for j in range(i+1, len(ofc_names2)):
        if sim2[i,j] > THRESH2:
            G2.add_edge(ofc_names2[i], ofc_names2[j], weight=sim2[i,j])
print(f'  edges (cos>{THRESH2}) = {G2.number_of_edges()}')

comms2 = list(nxcom.greedy_modularity_communities(G2, weight='weight'))
print(f'  커뮤니티 N = {len(comms2)}')
ofc_comm2 = {}
for ci, c in enumerate(comms2):
    for o in c:
        ofc_comm2[o] = ci
for ci, c in enumerate(sorted(comms2, key=len, reverse=True)):
    members = sorted(list(c))
    # 커뮤니티 평균 시그니처
    avg = ofc_z.loc[list(c)].mean()
    top_pos = avg.sort_values(ascending=False).head(3).index.tolist()
    top_neg = avg.sort_values().head(3).index.tolist()
    print(f'  [C{ci}] N={len(c)}  +주도: {top_pos}  -약함: {top_neg}')
    print(f'        멤버: {members[:8]}{"..." if len(members)>8 else ""}')

pd.DataFrame([(o, ofc_comm2[o]) for o in ofc_comm2],
             columns=['OFFC_NM','community']).to_csv(
    os.path.join(RES_DIR, f'H3_ministry_community_v2{SUFFIX}.csv'),
    index=False, encoding='utf-8-sig')

# ============================================================
# Step 11: 분야 시그니처 유사도 그래프 + KS-test
# ============================================================
print('\n' + '='*70)
print('Step 11: 분야 시그니처 비교 + amp_12m 분포 KS-test')
print('='*70)
fld_feat = df.groupby('FLD_NM')[feat_cols].mean()
fld_z = (fld_feat - fld_feat.mean()) / fld_feat.std()
print('\n  분야별 z-score 시그니처 (12개 피처):')
print(fld_z.round(2).to_string())

# 분야 간 cosine 유사도 매트릭스
sim_fld = cosine_similarity(fld_z.values)
sim_fld_df = pd.DataFrame(sim_fld, index=fld_z.index, columns=fld_z.index).round(2)
print('\n  분야 간 cosine 유사도 (시그니처):')
print(sim_fld_df.to_string())

# pair-wise KS-test on amp_12m_norm
from scipy.stats import ks_2samp
flds = sorted(df['FLD_NM'].unique())
ks_results = []
for i, f1 in enumerate(flds):
    for f2 in flds[i+1:]:
        x1 = df.loc[df['FLD_NM']==f1, 'amp_12m_norm'].values
        x2 = df.loc[df['FLD_NM']==f2, 'amp_12m_norm'].values
        if len(x1) < 5 or len(x2) < 5: continue
        stat, p = ks_2samp(x1, x2)
        ks_results.append({'fld_a':f1,'fld_b':f2,'ks_stat':stat,'p':p,
                           'n_a':len(x1),'n_b':len(x2)})
ks_df = pd.DataFrame(ks_results).sort_values('ks_stat', ascending=False)
sig = (ks_df['p'] < 0.001).sum()
print(f'\n  KS-test (amp_12m_norm 분야 간): N pair={len(ks_df)}, p<0.001 pair={sig}')
print('  최대 차이 top 8:')
print(ks_df.head(8).round(4).to_string(index=False))
ks_df.to_csv(os.path.join(RES_DIR, f'H3_field_ks_amp12m{SUFFIX}.csv'),
             index=False, encoding='utf-8-sig')

# ============================================================
# 그림: A,B,C 기존 + D(부처 그래프 v2) + E(sub-cluster) + F(분야 유사도)
# ============================================================
# ── Figure A: UMAP scatter (클러스터별) ─────────────
fig, axes = plt.subplots(1, 2, figsize=(15, 6.5))
ax = axes[0]
palette = plt.get_cmap('tab10')
for cl in sorted(df['cluster'].unique()):
    sub_ = df[df['cluster']==cl]
    color = '#bbbbbb' if cl == -1 else palette(cl % 10)
    ax.scatter(sub_['u1'], sub_['u2'], s=10, c=[color], alpha=0.6,
               label=f'cluster {cl} (n={len(sub_)})')
ax.set_title('UMAP — HDBSCAN 클러스터 (전체 1,641 활동)')
ax.set_xlabel('UMAP 1'); ax.set_ylabel('UMAP 2')
ax.legend(loc='best', fontsize=8)
ax.grid(alpha=0.3)

ax = axes[1]
top_flds = df['FLD_NM'].value_counts().head(8).index.tolist()
palette2 = plt.get_cmap('tab20')
for i, f in enumerate(top_flds):
    sub_ = df[df['FLD_NM']==f]
    ax.scatter(sub_['u1'], sub_['u2'], s=8, c=[palette2(i)], alpha=0.6, label=f'{f} (n={len(sub_)})')
others = df[~df['FLD_NM'].isin(top_flds)]
ax.scatter(others['u1'], others['u2'], s=4, c='#dddddd', alpha=0.4, label='기타')
ax.set_title('UMAP — 분야별 (상위 8개)')
ax.set_xlabel('UMAP 1'); ax.set_ylabel('UMAP 2')
ax.legend(loc='best', fontsize=8, ncol=2)
ax.grid(alpha=0.3)
plt.tight_layout()
fig.savefig(os.path.join(OUT_DIR, 'H3_umap_scatter.png'), dpi=200, bbox_inches='tight')
plt.close()

# ── Figure B: 클러스터 프로파일 heatmap ────────────
fig, ax = plt.subplots(figsize=(11, 6))
sns.heatmap(zprof.drop(columns='n').T, annot=True, fmt='.2f', cmap='RdBu_r',
            center=0, ax=ax, cbar_kws={'label':'z-score'})
ax.set_title(f'1차 클러스터 z-score 프로파일 (N: {zprof["n"].astype(int).tolist()})')
ax.set_xlabel('cluster')
plt.tight_layout()
fig.savefig(os.path.join(OUT_DIR, 'H3_cluster_profile.png'), dpi=200, bbox_inches='tight')
plt.close()

# ── Figure C: 분야 × 클러스터 heatmap ──────────────
fig, ax = plt.subplots(figsize=(10, 6.5))
sns.heatmap(ct.drop(columns='n'), annot=True, fmt='.2f', cmap='YlOrRd',
            ax=ax, cbar_kws={'label':'활동 비율'})
ax.set_title('분야별 1차 클러스터 분포 (행=분야, 행 합=1)')
plt.tight_layout()
fig.savefig(os.path.join(OUT_DIR, 'H3_field_cluster_heatmap.png'), dpi=200, bbox_inches='tight')
plt.close()

# ── Figure D: 부처 그래프 (피처 평균 cosine) ────────
fig, ax = plt.subplots(figsize=(13, 9))
pos = nx.spring_layout(G2, seed=42, k=0.7, iterations=120)
node_colors = [palette2(ofc_comm2.get(n,0) % 20) for n in G2.nodes()]
node_sizes = [40 + 4*ofc_n[n] for n in G2.nodes()]
nx.draw_networkx_edges(G2, pos, alpha=0.18, width=0.5, ax=ax)
nx.draw_networkx_nodes(G2, pos, node_color=node_colors, node_size=node_sizes, alpha=0.85, ax=ax)
nx.draw_networkx_labels(G2, pos, font_size=7, ax=ax,
                        font_family=KFONT or 'sans-serif')
ax.set_title(f'부처 시그니처 유사 그래프 (cos>{THRESH2}, 커뮤니티={len(comms2)})\n색=커뮤니티  크기=활동 수')
ax.axis('off')
plt.tight_layout()
fig.savefig(os.path.join(OUT_DIR, 'H3_ministry_graph.png'), dpi=200, bbox_inches='tight')
plt.close()

# ── Figure E: cluster 2 sub-clustering ────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
ax = axes[0]
palette3 = plt.get_cmap('tab10')
for sc in sorted(df_c2['subcluster'].unique()):
    sub_ = df_c2[df_c2['subcluster']==sc]
    color = '#dddddd' if sc==-1 else palette3(sc % 10)
    ax.scatter(sub_['v1'], sub_['v2'], s=8, c=[color], alpha=0.6,
               label=f'sub {sc} (n={len(sub_)})')
ax.set_title('cluster 2 (정상 사업, N=1,327) 내부 UMAP+HDBSCAN')
ax.set_xlabel('UMAP-A'); ax.set_ylabel('UMAP-B')
ax.legend(loc='best', fontsize=7)
ax.grid(alpha=0.3)

ax = axes[1]
sns.heatmap(zsub.drop(columns='n').T, annot=True, fmt='.2f',
            cmap='RdBu_r', center=0, ax=ax, cbar_kws={'label':'z-score'})
ax.set_title(f'sub-cluster z-score 프로파일 (N: {zsub["n"].astype(int).tolist()})')
ax.set_xlabel('subcluster')
plt.tight_layout()
fig.savefig(os.path.join(OUT_DIR, 'H3_subcluster.png'), dpi=200, bbox_inches='tight')
plt.close()

# ── Figure F: 분야 유사도 + KS heat ────────────────
fig, axes = plt.subplots(1, 2, figsize=(16, 6.5))
sns.heatmap(sim_fld_df, annot=True, fmt='.2f', cmap='RdBu_r', center=0,
            ax=axes[0], cbar_kws={'label':'cosine'})
axes[0].set_title('분야 시그니처 cosine 유사도 (12피처 평균)')

# KS heatmap (대칭화)
ks_mat = pd.DataFrame(0.0, index=flds, columns=flds)
for r in ks_results:
    ks_mat.loc[r['fld_a'], r['fld_b']] = r['ks_stat']
    ks_mat.loc[r['fld_b'], r['fld_a']] = r['ks_stat']
sns.heatmap(ks_mat, annot=True, fmt='.2f', cmap='YlOrRd', ax=axes[1],
            cbar_kws={'label':'KS statistic'})
axes[1].set_title('분야 amp_12m 분포 차이 (KS statistic)')
plt.tight_layout()
fig.savefig(os.path.join(OUT_DIR, 'H3_field_similarity.png'), dpi=200, bbox_inches='tight')
plt.close()

print('\n=== 그림 ===')
for f in sorted(os.listdir(OUT_DIR)):
    print(f'  {f}')

con.close()
print('\n완료.')
