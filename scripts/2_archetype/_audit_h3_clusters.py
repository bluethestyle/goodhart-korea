"""H3 클러스터링 품질 점검 — _audit_h3_clusters.py

조사 항목:
  A. 임베딩 input 확인
  B. 클러스터별 월별 시점 패턴 (DuckDB 재집계)
  C. L2 거리 분포 + outlier Top 5
  D. silhouette / ANOVA R²
  E. narrative 정합도
  F. 결론
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import numpy as np
import pandas as pd
import duckdb
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
from scipy.stats import f_oneway

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB   = os.path.join(ROOT, 'data', 'warehouse.duckdb')
CSV  = os.path.join(ROOT, 'data', 'results', 'H3_activity_embedding_11y.csv')

CLUSTER_KR = {0: 'C0 인건비형', 1: 'C1 자산취득형', 2: 'C2 출연금형', 3: 'C3 정상사업'}

# ─────────────────────────────────────────────
# §A. 임베딩 input 확인
# ─────────────────────────────────────────────
print("=" * 70)
print("§A. 임베딩 input 정체")
print("=" * 70)

emb = pd.read_csv(CSV, encoding='utf-8-sig')
print(f"  CSV rows: {len(emb)}, columns: {list(emb.columns)}")
print()
print("  [확인] h3_v2_11y.py 소스 기준 피처 목록 (12차원):")
feat_cols = [
    'amp_12m_norm', 'amp_6m_norm', 'hhi_period', 'q4_pct', 'dec_pct', 'cv_monthly',
    'chooyeon_pct', 'operating_pct', 'direct_invest_pct', 'personnel_pct',
    'log_annual', 'growth_cagr',
]
print(f"  → {feat_cols}")
print()
print("  이 피처 중 '월별 비중 시퀀스(12-dim)' 는 없음.")
print("  amp_12m_norm, amp_6m_norm: 연간 FFT 진폭 (scalar), hhi_period, q4_pct,")
print("  dec_pct, cv_monthly: 시점 통계 (scalar 6개)")
print("  chooyeon_pct ~ personnel_pct: 편성목 구성비 (scalar 4개)")
print("  log_annual, growth_cagr: 규모/성장 (scalar 2개)")
print()
print("  → INPUT은 12개 scalar feature (시점 시퀀스가 아닌 요약 통계)")
print("    월별 12차원 비중 벡터로 클러스터링한 것이 아님.")
print("    UMAP: n_neighbors=30, min_dist=0.05")
print("    HDBSCAN: min_cluster_size=60, min_samples=10, method=eom")

# ─────────────────────────────────────────────
# §B. 클러스터별 시점 패턴 (DuckDB 재집계)
# ─────────────────────────────────────────────
print()
print("=" * 70)
print("§B. 클러스터별 월별 집행 비중 (DuckDB 재집계)")
print("=" * 70)

con = duckdb.connect(DB, read_only=True)

# 활동 키 + 클러스터 매핑
key_cols = ['FLD_NM', 'OFFC_NM', 'PGM_NM', 'ACTV_NM']
emb_small = emb[key_cols + ['cluster']].copy()

# DuckDB에서 활동별 2015-2025 월별 집행 총합
raw = con.execute("""
    SELECT FLD_NM, OFFC_NM, PGM_NM, ACTV_NM,
           EXE_M AS month, SUM(EP_AMT) AS amt
    FROM monthly_exec
    WHERE EXE_M BETWEEN 1 AND 12
      AND FSCL_YY BETWEEN 2015 AND 2025
    GROUP BY 1,2,3,4,5
""").fetchdf()
con.close()

print(f"  raw monthly rows: {len(raw):,}")

# 활동별 월별 비중 벡터 (11년 합산 기준)
pivoted = (raw.pivot_table(index=key_cols, columns='month', values='amt', aggfunc='sum')
             .reindex(columns=range(1, 13), fill_value=0)
             .reset_index())

totals = pivoted[list(range(1, 13))].sum(axis=1)
pct_df = pivoted[key_cols].copy()
for m in range(1, 13):
    pct_df[m] = pivoted[m] / totals.replace(0, np.nan)
pct_df = pct_df.dropna()

# 클러스터 조인
merged = pct_df.merge(emb_small, on=key_cols, how='inner')
print(f"  클러스터 조인 후 rows: {len(merged):,}")
print()

month_cols = list(range(1, 13))

for cl in sorted(CLUSTER_KR.keys()):
    sub = merged[merged['cluster'] == cl]
    if len(sub) == 0:
        continue
    means = sub[month_cols].mean().values * 100
    stds  = sub[month_cols].std().values * 100
    mean_sd = stds.mean()
    print(f"  {CLUSTER_KR[cl]} (n={len(sub)})")
    month_str = " ".join([f"M{m:02d}:{v:.1f}%" for m, v in zip(range(1, 13), means)])
    print(f"    Mean: {month_str}")
    sd_str = " ".join([f"{v:.1f}" for v in stds])
    print(f"    SD  : {sd_str} (월평균SD={mean_sd:.2f}%p)")
    print()

# ─────────────────────────────────────────────
# §C. L2 거리 분포 + outlier Top 5 per cluster
# ─────────────────────────────────────────────
print("=" * 70)
print("§C. 클러스터 mean까지 L2 거리 분포 + outlier Top 5")
print("=" * 70)

cluster_means = {}
for cl in sorted(CLUSTER_KR.keys()):
    sub = merged[merged['cluster'] == cl]
    cluster_means[cl] = sub[month_cols].mean().values

merged['l2_dist'] = np.nan
for idx, row in merged.iterrows():
    cl = int(row['cluster'])
    if cl not in cluster_means:
        continue
    vec = row[month_cols].values.astype(float)
    merged.at[idx, 'l2_dist'] = np.linalg.norm(vec - cluster_means[cl])

for cl in sorted(CLUSTER_KR.keys()):
    sub = merged[merged['cluster'] == cl].copy()
    if len(sub) == 0:
        continue
    dists = sub['l2_dist'].dropna()
    pcts = np.percentile(dists, [50, 90, 95, 99])
    print(f"  {CLUSTER_KR[cl]} (n={len(sub)})")
    print(f"    L2 median={pcts[0]:.4f}  p90={pcts[1]:.4f}  p95={pcts[2]:.4f}  p99={pcts[3]:.4f}")

    top5 = sub.nlargest(5, 'l2_dist')[['ACTV_NM', 'l2_dist'] + month_cols]
    print(f"    Top-5 outlier:")
    for _, r in top5.iterrows():
        max_m = int(np.argmax(r[month_cols].values)) + 1
        max_v = r[month_cols].values.max() * 100
        print(f"      [{r['l2_dist']:.4f}] {r['ACTV_NM'][:30]}  (M{max_m:02d}={max_v:.1f}%)")
    print()

# narrative-위반 outlier 수 (p95 초과)
print("  narrative 위반 기준 (자기 클러스터 p95 초과):")
total_outliers = 0
for cl in sorted(CLUSTER_KR.keys()):
    sub = merged[merged['cluster'] == cl].copy()
    dists = sub['l2_dist'].dropna()
    p95 = np.percentile(dists, 95)
    n_out = (dists > p95).sum()
    total_outliers += n_out
    print(f"    {CLUSTER_KR[cl]}: p95={p95:.4f}, >p95 count={n_out} ({n_out/len(sub)*100:.1f}%)")

# ─────────────────────────────────────────────
# §D. silhouette + ANOVA R²
# ─────────────────────────────────────────────
print()
print("=" * 70)
print("§D. silhouette (시점 벡터 기준) + ANOVA")
print("=" * 70)

X_month = merged[month_cols].values
y_cl    = merged['cluster'].values

# 12차원 월별 비중 벡터로 silhouette
sil = silhouette_score(X_month, y_cl, sample_size=min(2000, len(X_month)), random_state=42)
print(f"  silhouette score (12-month pct vectors): {sil:.4f}")
print(f"  (0에 가까우면 클러스터 구분이 시점 기준으로는 약함,")
print(f"   1에 가까울수록 잘 분리됨)")
print()

# ANOVA F / R² — 각 월 집행비중 ~ 클러스터
print("  ANOVA (각 월 비중 ~ cluster label):")
r2_list = []
for m in month_cols:
    groups = [merged.loc[merged['cluster'] == cl, m].values for cl in sorted(CLUSTER_KR.keys())]
    fstat, pval = f_oneway(*groups)
    # R² = SS_between / SS_total
    grand = merged[m].mean()
    ss_tot = ((merged[m] - grand) ** 2).sum()
    ss_bw  = sum(len(g) * (g.mean() - grand) ** 2 for g in groups)
    r2 = ss_bw / ss_tot if ss_tot > 0 else 0
    r2_list.append(r2)
    print(f"    M{m:02d}: F={fstat:.1f}  p={'<0.001' if pval<0.001 else f'{pval:.3f}'}  R²={r2:.3f}")

print(f"\n  평균 R² across 12 months: {np.mean(r2_list):.3f}")

# ─────────────────────────────────────────────
# §E. C0/C1/C2/C3 narrative 정합도
# ─────────────────────────────────────────────
print()
print("=" * 70)
print("§E. narrative 정합도 판정")
print("=" * 70)

narrative = {
    0: ("C0 인건비형 (매월 균등)", "12개월 균등 분포, 인건비 비중↑"),
    1: ("C1 자산취득형", "연말(Q4/12월) 집중, 자산취득비↑"),
    2: ("C2 출연금형", "분기·반기 사이클 (이전 narrative) or 연초 집중"),
    3: ("C3 정상사업", "큰 편향 없는 정규 집행"),
}

for cl in sorted(CLUSTER_KR.keys()):
    sub = merged[merged['cluster'] == cl]
    if len(sub) == 0:
        continue
    means = sub[month_cols].mean().values * 100
    # 주요 통계
    max_m   = int(np.argmax(means)) + 1
    max_v   = means.max()
    q4_v    = means[9:12].sum()
    dec_v   = means[11]
    cv_v    = np.std(means) / (np.mean(means) + 1e-9)
    q1_v    = means[0:3].sum()   # Jan-Mar

    label, desc = narrative[cl]
    print(f"  {label}")
    print(f"    서술: {desc}")
    print(f"    실제: 최고월=M{max_m:02d}({max_v:.1f}%), Q4={q4_v:.1f}%, Dec={dec_v:.1f}%,")
    print(f"          Q1(Jan-Mar)={q1_v:.1f}%, CV={cv_v:.3f}")

    # 정합 판정
    if cl == 0:
        # 균등형 → CV 낮아야, 최고월이 특정 달에 쏠리지 않아야
        if cv_v < 0.3 and max_v < 15:
            verdict = "OK — 상대적으로 균등"
        else:
            verdict = f"WARNING — 최고월 M{max_m:02d}={max_v:.1f}%, CV={cv_v:.2f} (균등 narrative 약화)"
    elif cl == 1:
        if q4_v > 40 or dec_v > 20:
            verdict = "OK — Q4/12월 집중 확인"
        else:
            verdict = f"WARNING — Q4={q4_v:.1f}% 낮음, 자산취득형 narrative 약화"
    elif cl == 2:
        # 이전 narrative "분기·반기" vs 실제 "연초 집중"
        if q1_v > 35:
            verdict = f"MISMATCH — 연초(Q1={q1_v:.1f}%) 집중, '분기·반기' narrative 불일치"
        elif cv_v > 0.3:
            verdict = f"PARTIAL — 높은 변동성(CV={cv_v:.2f}) but 특정 사이클 불명확"
        else:
            verdict = "OK"
    elif cl == 3:
        if cv_v < 0.3 and max_v < 15:
            verdict = "OK — 정규 집행 확인"
        else:
            verdict = f"WARNING — CV={cv_v:.2f}, 최고월 M{max_m:02d}={max_v:.1f}%"
    print(f"    판정: {verdict}")
    print()

# 노인일자리지원 특정 확인
print("  [특정 활동 확인] 노인일자리지원 계열 (ACTV_NM contains '노인일자리')")
senior = merged[merged['ACTV_NM'].str.contains('노인일자리', na=False)]
if len(senior) > 0:
    for _, r in senior.iterrows():
        m_vals = r[month_cols].values * 100
        cl_mean = cluster_means[int(r['cluster'])]
        l2 = np.linalg.norm(r[month_cols].values - cl_mean)
        print(f"    [{CLUSTER_KR.get(int(r['cluster']), '?')}] {r['ACTV_NM'][:40]}")
        m_str = " ".join([f"M{m}:{v:.1f}%" for m, v in zip(range(1, 13), m_vals)])
        print(f"      {m_str}")
        print(f"      L2={l2:.4f}")
else:
    print("  → '노인일자리' 포함 활동 없음 (키 조인에서 누락 가능)")
    # 느슨하게 검색
    possible = merged[merged['ACTV_NM'].str.contains('노인', na=False)]
    print(f"  → '노인' 포함: {len(possible)}개")
    for _, r in possible.head(5).iterrows():
        print(f"    cluster={r['cluster']} | {r['ACTV_NM'][:50]}")

# ─────────────────────────────────────────────
# §F. 결론
# ─────────────────────────────────────────────
print()
print("=" * 70)
print("§F. 결론 요약")
print("=" * 70)

# emb 기준 feature silhouette (원본 12-dim feature 기준)
X_feat = emb[feat_cols].values
scaler = StandardScaler()
X_feat_z = scaler.fit_transform(X_feat)
y_feat_cl = emb['cluster'].values
sil_feat = silhouette_score(X_feat_z, y_feat_cl, sample_size=min(2000, len(X_feat_z)), random_state=42)
print(f"  silhouette (원본 12피처 z-score): {sil_feat:.4f}")
print(f"  silhouette (12-month pct 시점벡터): {sil:.4f}")
print()

gap = sil_feat - sil
print(f"  gap (feature silhouette - month silhouette): {gap:.4f}")
if gap > 0.15:
    print("  → 피처 공간에서는 잘 분리되지만 시점 공간에서는 분리 약함")
    print("    임베딩이 시점 패턴이 아닌 다른 차원(편성목, 규모, FFT 요약)으로 분리된 가능성")
elif sil < 0.2:
    print("  → 시점 벡터 기준 silhouette < 0.2: 클러스터가 월별 패턴을 잘 반영하지 못함")
else:
    print("  → 시점 벡터 기준으로도 어느 정도 분리됨")

print()
print("  [핵심 진단]")
print("  1. INPUT: 12개 scalar feature (시점 요약 통계 6 + 편성목 구성비 4 + 규모 2)")
print("     → 월별 12-dim 비중 시퀀스가 아니라 요약 통계 기반 클러스터링")
print("  2. C0 인건비형 narrative: personnel_pct↑ + cv 낮음 으로 분리됨")
print("     → 하지만 실제 월별 패턴이 '매월 균등'인지는 보증 안 됨")
print("     → 노인일자리지원처럼 '1월·4월 집중'인데 personnel_pct↑면 C0에 배정 가능")
print("  3. outlier 처리: p95 초과 활동이 각 클러스터당 ~5%씩 존재")
print("     → narrative-위반 outlier를 '비정형 하위유형'으로 별도 표기 권장")
print()

n_total = len(merged)
for cl in sorted(CLUSTER_KR.keys()):
    sub = merged[merged['cluster'] == cl]
    dists = sub['l2_dist'].dropna()
    p95 = np.percentile(dists, 95)
    n_out = (dists > p95).sum()
    print(f"  {CLUSTER_KR[cl]}: n={len(sub)}, L2_p95 outlier={n_out}")

print()
print("완료.")
