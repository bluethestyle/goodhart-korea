"""H3b: C2 출연금형(grant) 내부 세분 — 시점(월별 집행 프로파일) 기반 sub-clustering.

배경
  - 1차 원형(H3)은 편성목 구성비로 갈림 → C2 출연금형 내부는 편성목이 균질.
  - PH 루프 분석(H9)이 C2 내부 세부 이질성을 시사. main_v2 §6.1은 C2가
    "연초 일괄 출연형 vs 분기말 사이클형" bimodal 구조라고 가설.
  - 본 스크립트: C2 154개 활동의 *월별 집행 모양*으로 sub-cluster를 데이터로 확인.
    → 의미있게 갈리면 TDA "시사"가 "확인"으로 승급.

방법
  - 활동 키 = (FLD_NM, OFFC_NM, PGM_NM, ACTV_NM)  [h3_v2_11y.py와 동일]
  - 각 C2 활동: 연도별 12-월 정규화 프로파일 → 연 평균 → mean 12-profile
  - KMeans(k=2..5)+Ward, silhouette로 최적 k. 위상(FFT k=1 각도)·dec/nov 일평균비 특성화.
  - 부트스트랩 ARI로 안정성 점검.
"""
import os, sys, io, warnings
import numpy as np
import pandas as pd
import duckdb
from scipy import fft as scfft
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.metrics import silhouette_score, adjusted_rand_score
warnings.filterwarnings('ignore')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB = os.path.join(ROOT, 'data', 'warehouse.duckdb')
RES = os.path.join(ROOT, 'data', 'results')

PURE_ACCT = """(
    ACTV_NM ILIKE '%전출금%' OR ACTV_NM ILIKE '%타계정%' OR ACTV_NM ILIKE '%여유자금%'
 OR ACTV_NM ILIKE '%국고예탁%' OR ACTV_NM ILIKE '%기금예탁%' OR ACTV_NM ILIKE '%국고예치%'
 OR ACTV_NM ILIKE '%회계간거래%' OR ACTV_NM ILIKE '%회계간전출%'
 OR ACTV_NM ILIKE '%회계기금간%' OR ACTV_NM ILIKE '%여유자금운용%'
)"""

KEY = ['FLD_NM', 'OFFC_NM', 'PGM_NM', 'ACTV_NM']

# ============================================================
# Step 0: 1차 원형 라벨 검증 → C2 출연금형 식별
# ============================================================
print('=' * 70); print('Step 0: 클러스터 라벨 검증'); print('=' * 70)
emb = pd.read_csv(os.path.join(RES, 'H3_activity_embedding_11y.csv'))
print('  embedding shape:', emb.shape)
vc = emb['cluster'].value_counts().sort_index()
print('  cluster 분포:\n', vc.to_string())
prof = emb.groupby('cluster')[['chooyeon_pct', 'personnel_pct', 'direct_invest_pct',
                               'operating_pct', 'amp_12m_norm', 'dec_pct']].mean().round(3)
print('\n  cluster별 편성목·게임화 평균:\n', prof.to_string())
# 출연금형 = chooyeon_pct 최대 & n in [120,200]
cand = prof['chooyeon_pct'].idxmax()
n_cand = int(vc.get(cand, 0))
print(f'\n  → 출연금형 후보 = cluster {cand} (chooyeon_pct 최대, n={n_cand})')
C2 = cand
c2keys = emb[emb['cluster'] == C2][KEY].drop_duplicates()
print(f'  C2 활동 수 = {len(c2keys)}')

# ============================================================
# Step 1: C2 활동의 월별 집행 프로파일 (warehouse)
# ============================================================
print('\n' + '=' * 70); print('Step 1: C2 월별 프로파일 추출'); print('=' * 70)
con = duckdb.connect(DB, read_only=True)
raw = con.execute(f"""
    SELECT FLD_NM, OFFC_NM, PGM_NM, ACTV_NM, FSCL_YY AS year, EXE_M AS month,
           SUM(EP_AMT) AS amt
    FROM monthly_exec
    WHERE EXE_M BETWEEN 1 AND 12 AND FSCL_YY BETWEEN 2015 AND 2025
      AND NOT {PURE_ACCT}
    GROUP BY 1,2,3,4,5,6
""").fetchdf()
con.close()

c2set = set(map(tuple, c2keys.values))
DAYS = np.array([31,28,31,30,31,30,31,31,30,31,30,31], float)

recs = []
for keys, g in raw.groupby(KEY):
    if tuple(keys) not in c2set:
        continue
    profs, dnr = [], []
    for y, gy in g.groupby('year'):
        arr = np.zeros(12)
        for _, r in gy.iterrows():
            arr[int(r['month']) - 1] = r['amt']
        if arr.sum() <= 0 or (arr > 0).sum() < 6:
            continue
        profs.append(arr / arr.sum())
        # Dec/Nov 일평균비 (RDD-style)
        if arr[10] > 0:
            dnr.append((arr[11] / DAYS[11]) / (arr[10] / DAYS[10]))
    if len(profs) < 6:
        continue
    p = np.mean(profs, axis=0)
    yf = scfft.fft(p - p.mean())
    phase12 = np.angle(yf[1])              # 1년 주기 위상
    amp12 = abs(yf[1]) * 2 / 12
    amp6 = abs(yf[2]) * 2 / 12
    peak_m = int(np.argmax(p)) + 1
    recs.append({
        **{k: keys[i] for i, k in enumerate(KEY)},
        **{f'm{i+1}': p[i] for i in range(12)},
        'q1_share': p[0:3].sum(), 'h2_share': p[6:12].sum(),
        'dec_share': p[11], 'peak_month': peak_m,
        'amp12': amp12, 'amp6': amp6, 'phase12': phase12,
        'dec_nov_ratio': np.median(dnr) if dnr else np.nan,
        'n_year': len(profs),
    })

c2 = pd.DataFrame(recs)
print(f'  프로파일 확보 C2 활동 = {len(c2)} / {len(c2keys)}')
mcols = [f'm{i+1}' for i in range(12)]
print('  C2 전체 평균 월별 프로파일(%):')
print('   ', np.round(c2[mcols].mean().values * 100, 1))
print(f'  peak_month 분포:\n{c2["peak_month"].value_counts().sort_index().to_string()}')

# ============================================================
# Step 2: sub-clustering — 월별 프로파일 모양 기반
# ============================================================
print('\n' + '=' * 70); print('Step 2: C2 내부 sub-clustering (월별 프로파일)'); print('=' * 70)
Xp = StandardScaler().fit_transform(c2[mcols].values)   # 12-월 모양 표준화

print('  KMeans silhouette by k:')
best = {}
for k in range(2, 6):
    km = KMeans(n_clusters=k, n_init=20, random_state=42).fit(Xp)
    sil = silhouette_score(Xp, km.labels_)
    ward = AgglomerativeClustering(n_clusters=k, linkage='ward').fit(Xp)
    silw = silhouette_score(Xp, ward.labels_)
    print(f'    k={k}: KMeans sil={sil:.3f}  Ward sil={silw:.3f}')
    best[k] = (sil, km)

kbest = max(best, key=lambda k: best[k][0])
sil_b, km_b = best[kbest]
print(f'\n  → 최적 k = {kbest} (silhouette {sil_b:.3f})')
c2['sub'] = km_b.labels_

# 안정성: 부트스트랩 ARI (동일 k, 표본 재추출 후 라벨 일치도)
rng = np.random.RandomState(0)
aris = []
base = KMeans(n_clusters=kbest, n_init=10, random_state=1).fit_predict(Xp)
for b in range(30):
    idx = rng.choice(len(Xp), len(Xp), replace=True)
    lab_b = KMeans(n_clusters=kbest, n_init=10, random_state=b + 2).fit_predict(Xp[idx])
    aris.append(adjusted_rand_score(base[idx], lab_b))
print(f'  부트스트랩 ARI(30회) 평균 = {np.mean(aris):.3f} (±{np.std(aris):.3f})')

# ============================================================
# Step 3: sub-cluster 특성화
# ============================================================
print('\n' + '=' * 70); print('Step 3: sub-cluster 특성화'); print('=' * 70)
for s in sorted(c2['sub'].unique()):
    sub = c2[c2['sub'] == s]
    prof_m = sub[mcols].mean().values * 100
    print(f'\n  [sub {s}] n={len(sub)}')
    print(f'    월별프로파일%: {np.round(prof_m,1)}')
    print(f'    peak_month 최빈={sub["peak_month"].mode().values}, '
          f'q1_share={sub["q1_share"].mean():.3f}, h2_share={sub["h2_share"].mean():.3f}, '
          f'dec_share={sub["dec_share"].mean():.3f}')
    print(f'    amp12={sub["amp12"].mean():.3f}, amp6={sub["amp6"].mean():.3f}, '
          f'dec_nov_ratio(median)={sub["dec_nov_ratio"].median():.2f}')
    top_ofc = sub['OFFC_NM'].value_counts().head(5)
    print(f'    상위 부처: {dict(top_ofc)}')
    # 대표 활동(피크월 기준 극단)
    ex = sub.sort_values('dec_share', ascending=False)['ACTV_NM'].head(3).tolist()
    ex2 = sub.sort_values('q1_share', ascending=False)['ACTV_NM'].head(3).tolist()
    print(f'    dec 최대 예: {ex}')
    print(f'    q1 최대 예: {ex2}')

# 저장
out = c2[KEY + mcols + ['sub', 'peak_month', 'q1_share', 'h2_share', 'dec_share',
                        'amp12', 'amp6', 'phase12', 'dec_nov_ratio', 'n_year']]
out.to_csv(os.path.join(RES, 'H3b_c2_subcluster.csv'), index=False, encoding='utf-8-sig')
summ = c2.groupby('sub').agg(
    n=('ACTV_NM', 'size'),
    **{c: (c, 'mean') for c in mcols},
    q1=('q1_share', 'mean'), h2=('h2_share', 'mean'), dec=('dec_share', 'mean'),
    amp12=('amp12', 'mean'), amp6=('amp6', 'mean'),
    dec_nov=('dec_nov_ratio', 'median'),
).round(4)
summ.to_csv(os.path.join(RES, 'H3b_c2_subcluster_profile.csv'), encoding='utf-8-sig')
print('\n저장: H3b_c2_subcluster.csv / H3b_c2_subcluster_profile.csv')
print(f'\nSUMMARY: k={kbest}, silhouette={sil_b:.3f}, bootstrap_ARI={np.mean(aris):.3f}')
print('완료.')
