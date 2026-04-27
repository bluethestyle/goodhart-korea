"""굿하트 가설 — 주기성 분석 (Step 2~4 통합).

Tier 1: FLD (16개) — STL + FFT
Tier 2: SECT (74개) — Coherence + Hierarchical Clustering
Tier 3: ACTV (~1,000개) — 게임화 지수 분포

이론적 토대:
  - Cooley-Tukey FFT (1965): 주파수 분해
  - Cleveland et al. (1990) STL: Seasonal-Trend decomposition by LOESS
  - Welch's method: Power Spectral Density 추정
  - Coherence: 두 시계열의 주파수 영역 상관성

산출:
  data/figs/freq/ - 시각화
  data/results/   - CSV
"""
import os, sys, io, duckdb
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import signal, fft as scfft
from scipy.cluster import hierarchy
from scipy.spatial.distance import squareform
from statsmodels.tsa.seasonal import STL

for f in ['Malgun Gothic','NanumGothic','AppleGothic','Noto Sans CJK KR']:
    try: plt.rcParams['font.family']=f; break
    except: pass
plt.rcParams['axes.unicode_minus']=False
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG = os.path.join(ROOT,'data','figs','freq'); os.makedirs(FIG, exist_ok=True)
RES = os.path.join(ROOT,'data','results'); os.makedirs(RES, exist_ok=True)

con = duckdb.connect(os.path.join(ROOT,'data','warehouse.duckdb'), read_only=True)

# 회계거래 키워드 (좁힌 필터)
PURE_ACCT = """(
    ACTV_NM ILIKE '%전출금%' OR ACTV_NM ILIKE '%타계정%' OR ACTV_NM ILIKE '%여유자금%'
 OR ACTV_NM ILIKE '%국고예탁%' OR ACTV_NM ILIKE '%기금예탁%' OR ACTV_NM ILIKE '%국고예치%'
 OR ACTV_NM ILIKE '%회계간거래%' OR ACTV_NM ILIKE '%회계간전출%'
 OR ACTV_NM ILIKE '%회계기금간%' OR ACTV_NM ILIKE '%여유자금운용%'
)"""

def yyyymm(yr, m): return yr*100 + m

# ============================================================
# Tier 1 — 분야별 시계열 + STL + FFT
# ============================================================
print('='*70); print('Tier 1: FLD (16개)'); print('='*70)

df_fld = con.execute(f"""
SELECT FSCL_YY, EXE_M, FLD_NM, sum(EP_AMT) AS amt
FROM monthly_exec
WHERE EXE_M BETWEEN 1 AND 12 AND NOT {PURE_ACCT}
  AND FSCL_YY BETWEEN 2020 AND 2025
GROUP BY FSCL_YY, EXE_M, FLD_NM
""").fetchdf()
df_fld['ym'] = df_fld['FSCL_YY']*100 + df_fld['EXE_M']
pivot_fld = df_fld.pivot(index='ym', columns='FLD_NM', values='amt').fillna(0).sort_index()
print(f'분야×월 시계열: {pivot_fld.shape} (월 × 분야)')

# STL: 분야별 seasonal/trend/resid
stl_results = {}
for fld in pivot_fld.columns:
    series = pivot_fld[fld]
    if (series > 0).sum() < 24: continue
    try:
        stl = STL(series.values, period=12, robust=True).fit()
        stl_results[fld] = {
            'trend': stl.trend, 'seasonal': stl.seasonal, 'resid': stl.resid,
            'season_strength': max(0, 1 - np.var(stl.resid) / np.var(stl.seasonal + stl.resid)),
            'trend_strength': max(0, 1 - np.var(stl.resid) / np.var(stl.trend + stl.resid)),
        }
    except Exception as e:
        print(f'  STL FAIL {fld}: {e}')

# FFT: 분야별 주파수 amplitude
fft_results = {}
for fld in pivot_fld.columns:
    s = pivot_fld[fld].values
    if (s > 0).sum() < 24: continue
    s_dt = s - s.mean()  # detrend (mean removal)
    n = len(s_dt)
    yf = scfft.fft(s_dt)
    freqs = scfft.fftfreq(n, d=1)[:n//2]   # cycles per month
    amp = np.abs(yf[:n//2]) * 2 / n
    # period: 1/freq (months)
    fft_results[fld] = {
        'freqs': freqs, 'amp': amp,
        # 주요 주기 amplitude
        'amp_12m': amp[np.argmin(abs(freqs - 1/12))],
        'amp_6m':  amp[np.argmin(abs(freqs - 1/6))],
        'amp_3m':  amp[np.argmin(abs(freqs - 1/3))],
        'mean': s.mean(),
    }

# 결과 정리
fld_summary = pd.DataFrame({
    'FLD_NM': list(fft_results.keys()),
    'mean_eok': [v['mean']/1e6 for v in fft_results.values()],
    'amp_12m_norm': [v['amp_12m']/v['mean'] for v in fft_results.values()],
    'amp_6m_norm':  [v['amp_6m']/v['mean']  for v in fft_results.values()],
    'amp_3m_norm':  [v['amp_3m']/v['mean']  for v in fft_results.values()],
    'season_strength': [stl_results[k]['season_strength'] if k in stl_results else None for k in fft_results.keys()],
    'trend_strength':  [stl_results[k]['trend_strength']  if k in stl_results else None for k in fft_results.keys()],
}).sort_values('amp_12m_norm', ascending=False)
print('\nTier 1 — 분야별 주기성 강도 (정규화 amplitude)')
print(fld_summary.to_string(index=False))
fld_summary.to_csv(f'{RES}/T1_fld_freq.csv', index=False, encoding='utf-8-sig')

# 시각화 1: 분야별 12월 주기 amplitude
fig, ax = plt.subplots(figsize=(11, 6))
sd = fld_summary.dropna(subset=['amp_12m_norm']).sort_values('amp_12m_norm')
ax.barh(sd['FLD_NM'], sd['amp_12m_norm']*100, color='#d62728')
ax.set_xlabel('연 주기(12개월) amplitude / 평균 (%)')
ax.set_title('분야별 연주기 게임화 강도 (FFT amplitude / mean)')
ax.grid(axis='x', alpha=0.3)
plt.tight_layout(); plt.savefig(f'{FIG}/T1_fld_amp12m.png', dpi=140); plt.close()
print(f'saved {FIG}/T1_fld_amp12m.png')

# 시각화 2: 상위 6 분야 STL decomposition
top6 = fld_summary.head(6)['FLD_NM'].tolist()
fig, axes = plt.subplots(len(top6), 3, figsize=(15, 2.2*len(top6)))
for i, fld in enumerate(top6):
    if fld not in stl_results: continue
    r = stl_results[fld]
    n = len(r['trend'])
    x = np.arange(n)
    axes[i,0].plot(x, r['trend'], color='#1f77b4'); axes[i,0].set_title(f'{fld[:8]} - Trend' if i==0 else fld[:8])
    axes[i,1].plot(x, r['seasonal'], color='#d62728'); axes[i,1].set_title('Seasonal' if i==0 else '')
    axes[i,2].plot(x, r['resid'], color='#7f7f7f'); axes[i,2].set_title('Residual' if i==0 else '')
    for a in axes[i]: a.grid(alpha=0.3)
plt.tight_layout(); plt.savefig(f'{FIG}/T1_top6_stl.png', dpi=140); plt.close()
print(f'saved {FIG}/T1_top6_stl.png')

# ============================================================
# Tier 2 — 부문(SECT) 74개 + Coherence + Clustering
# ============================================================
print('\n'+'='*70); print('Tier 2: SECT (74개) — Coherence Matrix + Clustering'); print('='*70)

df_sect = con.execute(f"""
SELECT FSCL_YY, EXE_M, SECT_NM, sum(EP_AMT) AS amt
FROM monthly_exec
WHERE EXE_M BETWEEN 1 AND 12 AND NOT {PURE_ACCT}
  AND FSCL_YY BETWEEN 2020 AND 2025
  AND SECT_NM IS NOT NULL
GROUP BY FSCL_YY, EXE_M, SECT_NM
""").fetchdf()
df_sect['ym'] = df_sect['FSCL_YY']*100 + df_sect['EXE_M']
piv_sect = df_sect.pivot(index='ym', columns='SECT_NM', values='amt').fillna(0).sort_index()
# 충분한 데이터가 있는 부문만 (최소 24월 + 평균 1억 이상)
keep = [c for c in piv_sect.columns if (piv_sect[c] > 0).sum() >= 24 and piv_sect[c].mean() > 1e6]
piv_sect = piv_sect[keep]
print(f'부문×월 시계열: {piv_sect.shape}')

# 정규화 (각 부문별 평균을 1로) — 스케일 차이 제거
piv_sect_norm = piv_sect.div(piv_sect.mean(axis=0), axis=1)

# Coherence 매트릭스 (12월 주기 = freq=1/12)
sects = piv_sect_norm.columns.tolist()
n = len(sects)
coh = np.eye(n)
for i in range(n):
    for j in range(i+1, n):
        f, Cxy = signal.coherence(piv_sect_norm.iloc[:,i].values,
                                   piv_sect_norm.iloc[:,j].values,
                                   fs=12, nperseg=min(36, len(piv_sect_norm)//2))
        # 1/12 cycle/month 근처의 coherence
        idx = np.argmin(abs(f - 1.0))  # f가 cycles/year 단위 (fs=12), 1.0 = 연1회 주기
        coh[i,j] = coh[j,i] = Cxy[idx]
print(f'Coherence matrix shape: {coh.shape}')

# Hierarchical clustering on (1 - coherence)
dist = 1 - coh
np.fill_diagonal(dist, 0)
condensed = squareform(dist, checks=False)
Z = hierarchy.linkage(condensed, method='average')
clusters = hierarchy.fcluster(Z, t=8, criterion='maxclust')

# 클러스터별 부문 정렬
cluster_df = pd.DataFrame({'SECT_NM': sects, 'cluster': clusters})
cluster_df = cluster_df.sort_values(['cluster','SECT_NM'])
cluster_df.to_csv(f'{RES}/T2_sect_clusters.csv', index=False, encoding='utf-8-sig')
print('\nT2 부문 클러스터 (12월 주기 coherence 기반):')
for c in sorted(set(clusters)):
    members = cluster_df[cluster_df.cluster==c]['SECT_NM'].tolist()
    print(f'  C{c} ({len(members)}개): {", ".join(members[:8])}{"..." if len(members)>8 else ""}')

# 시각화 — coherence dendrogram
fig, ax = plt.subplots(figsize=(14, max(8, n*0.18)))
hierarchy.dendrogram(Z, labels=sects, orientation='left', leaf_font_size=7,
                     color_threshold=0.7, ax=ax)
ax.set_title('부문(SECT) 연주기 Coherence 기반 Hierarchical Clustering')
ax.set_xlabel('1 - Coherence')
plt.tight_layout(); plt.savefig(f'{FIG}/T2_sect_dendrogram.png', dpi=140); plt.close()
print(f'saved {FIG}/T2_sect_dendrogram.png')

# 시각화 — coherence heatmap (cluster 정렬)
order = np.argsort(clusters)
coh_ord = coh[order][:, order]
fig, ax = plt.subplots(figsize=(13, 11))
im = ax.imshow(coh_ord, cmap='RdYlBu_r', vmin=0, vmax=1, aspect='auto')
plt.colorbar(im, ax=ax, label='Coherence at 12-mo period')
labels_ord = [sects[i] for i in order]
ax.set_xticks(range(n)); ax.set_xticklabels(labels_ord, rotation=90, fontsize=5)
ax.set_yticks(range(n)); ax.set_yticklabels(labels_ord, fontsize=5)
ax.set_title('부문 간 Coherence 매트릭스 (클러스터 정렬)')
plt.tight_layout(); plt.savefig(f'{FIG}/T2_sect_heatmap.png', dpi=140); plt.close()
print(f'saved {FIG}/T2_sect_heatmap.png')

# ============================================================
# Tier 3 — 단위사업(ACTV) 게임화 지수 분포
# ============================================================
print('\n'+'='*70); print('Tier 3: ACTV (100억+) — Gaming Index Distribution'); print('='*70)

df_actv = con.execute(f"""
WITH base AS (
  SELECT m.FSCL_YY, m.EXE_M, m.OFFC_NM, m.ACTV_NM, m.FLD_NM, m.EP_AMT,
         max(m.THISM_AGGR_EP_AMT) OVER (PARTITION BY m.OFFC_NM, m.ACTV_NM, m.FSCL_YY) AS yr_total
  FROM monthly_exec m
  WHERE m.EXE_M BETWEEN 1 AND 12 AND NOT {PURE_ACCT}
    AND m.FSCL_YY BETWEEN 2020 AND 2025
)
SELECT FSCL_YY, EXE_M, OFFC_NM, ACTV_NM, FLD_NM, sum(EP_AMT) AS amt, max(yr_total) AS yr_total
FROM base GROUP BY FSCL_YY, EXE_M, OFFC_NM, ACTV_NM, FLD_NM
""").fetchdf()
print(f'단위사업×월 행수: {len(df_actv):,}')

# 100억+ 사업만 (연도별)
big = df_actv[df_actv['yr_total'] > 1e10].copy()
print(f'100억+ 사업×년: {len(big):,}')

# 사업별 게임화 지수 — 1년 단위
def gaming_metrics(group):
    arr = np.zeros(12)
    for _, r in group.iterrows():
        arr[int(r['EXE_M'])-1] = r['amt']
    total = arr.sum()
    if total <= 0: return pd.Series({'total':0,'dec_pct':0,'q1_pct':0,'q4_pct':0,'hhi':0,'gini':0,'amp_12m_norm':0})
    pct = arr/total
    hhi = (pct**2).sum()
    # Gini
    s = np.sort(arr)
    n_m = 12
    gini = (2*np.sum((np.arange(1,n_m+1)) * s) / (n_m*s.sum()) - (n_m+1)/n_m) if s.sum()>0 else 0
    # 12-mo amplitude (단일 연도 내 — 가짜 주기지만 강도 비례)
    yf = scfft.fft(arr - arr.mean())
    amp_12m = np.abs(yf[1])*2/12  # k=1: 1cycle/12mo
    return pd.Series({
        'total': total,
        'dec_pct': pct[11]*100,
        'q1_pct': pct[:3].sum()*100,
        'q4_pct': pct[9:12].sum()*100,
        'hhi': hhi,
        'gini': gini,
        'amp_12m_norm': amp_12m / (total/12) if total > 0 else 0,
    })

gm = big.groupby(['FSCL_YY','OFFC_NM','ACTV_NM','FLD_NM']).apply(gaming_metrics).reset_index()
gm.to_csv(f'{RES}/T3_actv_gaming.csv', index=False, encoding='utf-8-sig')
print(f'사업×연 게임화 지수: {len(gm):,}')

# 분야별 분포
print('\n분야별 게임화 지수 평균/중앙값 (2024)')
g24 = gm[gm.FSCL_YY==2024]
fld_dist = g24.groupby('FLD_NM').agg(
    n=('ACTV_NM','count'),
    dec_mean=('dec_pct','mean'), dec_med=('dec_pct','median'),
    hhi_mean=('hhi','mean'), hhi_med=('hhi','median'),
    gini_mean=('gini','mean'), gini_med=('gini','median'),
    amp12_mean=('amp_12m_norm','mean'), amp12_med=('amp_12m_norm','median'),
).round(3).sort_values('amp12_med', ascending=False)
print(fld_dist.to_string())
fld_dist.to_csv(f'{RES}/T3_fld_distribution.csv', encoding='utf-8-sig')

# AI vs 기타 분포 비교 (Mann-Whitney U test)
from scipy.stats import mannwhitneyu
ai_mask = g24['FLD_NM'].isin(['과학기술','통신'])
ai_vals = g24[ai_mask]['amp_12m_norm'].dropna()
oth_vals = g24[~ai_mask]['amp_12m_norm'].dropna()
u_stat, p_val = mannwhitneyu(ai_vals, oth_vals, alternative='two-sided')
print(f'\n[Mann-Whitney U] AI/통신 vs 기타 — amp_12m_norm')
print(f'  AI/통신:  n={len(ai_vals)}, median={ai_vals.median():.3f}')
print(f'  기타:     n={len(oth_vals)}, median={oth_vals.median():.3f}')
print(f'  U={u_stat:.0f}, p={p_val:.4g}')

# 시각화 — 분야별 게임화 지수 boxplot
fig, ax = plt.subplots(figsize=(12, 6))
fld_order = fld_dist.index.tolist()[::-1]
data = [g24[g24.FLD_NM==f]['amp_12m_norm'].dropna().values for f in fld_order]
bp = ax.boxplot(data, vert=False, labels=fld_order, showfliers=False, patch_artist=True)
for patch, med in zip(bp['boxes'], [d.mean() if len(d)>0 else 0 for d in data]):
    patch.set_facecolor(plt.cm.RdYlBu_r(min(med/3, 1.0)))
ax.set_xlabel('정규화 12개월 amplitude (게임화 지수)')
ax.set_title('분야별 게임화 지수 분포 (단위사업 100억+, 2024)')
ax.grid(axis='x', alpha=0.3)
ax.axvline(0.5, color='gray', ls='--', lw=0.5, label='기준선')
plt.tight_layout(); plt.savefig(f'{FIG}/T3_fld_box.png', dpi=140); plt.close()
print(f'saved {FIG}/T3_fld_box.png')

print('\n=== 분석 완료 ===')
print(f'결과: {RES}/')
print(f'그림: {FIG}/')
con.close()
