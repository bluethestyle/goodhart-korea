"""H28: 웨이블릿 분석 — FFT 정상성 가정 보완.

FFT는 시계열 전체에서 12개월 진폭의 *고정* 값을 측정. 그러나 한국 정부 예산은
2007 국가재정법, 2014 국가회계제도 개편, 2020 코로나 확장재정 등 *시간에 따라*
게임화 강도가 변화했을 가능성. 웨이블릿(Continuous Wavelet Transform, CWT)으로
*시간 × 주기 평면*에서 진폭 변화를 추적한다.

방법:
  - Morlet 웨이블릿 (`scipy.signal.cwt` 또는 `pywt.cwt`)
  - 각 사업원형의 *전 활동 평균 시계열*에 CWT 적용 (2015~2025, 132개월)
  - scaleogram: x=시간, y=주기, color=power
  - 12개월 cycle 강도의 *연도별 진폭* 추출 → 시간 진화 plot

산출물:
  data/results/H28_wavelet_12m_evolution.csv  - 원형별 12m 진폭 시계열
  data/figs/h28_scaleogram.png                - 4 원형 scaleogram
  data/figs/h28_12m_evolution.png             - 12m 진폭 시간 진화
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
import pywt
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

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB   = os.path.join(ROOT, 'data', 'warehouse.duckdb')
RES  = os.path.join(ROOT, 'data', 'results')
FIG  = os.path.join(ROOT, 'data', 'figs')
H3_CSV = os.path.join(RES, 'H3_activity_embedding_11y.csv')

print('=' * 70)
print('H28: 웨이블릿 분석 — 시간-주파수 결합')
print('=' * 70)

# ============================================================
# Step 1: 사업원형별 평균 시계열 구성 (2015~2025, 132 months)
# ============================================================
print('\nStep 1: 원형별 평균 시계열 (132 months)')
emb = pd.read_csv(H3_CSV)
ARCHETYPE = {0: 'C0_personnel', 1: 'C1_direct_invest', 2: 'C2_chooyeon', 3: 'C3_normal'}
emb['archetype'] = emb['cluster'].map(ARCHETYPE)

PURE_ACCT = """(
    ACTV_NM ILIKE '%전출금%' OR ACTV_NM ILIKE '%타계정%' OR ACTV_NM ILIKE '%여유자금%'
 OR ACTV_NM ILIKE '%국고예탁%' OR ACTV_NM ILIKE '%기금예탁%' OR ACTV_NM ILIKE '%국고예치%'
 OR ACTV_NM ILIKE '%회계간거래%' OR ACTV_NM ILIKE '%회계간전출%')"""

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

# Merge archetype labels
raw_keyed = raw.merge(emb[['FLD_NM', 'OFFC_NM', 'PGM_NM', 'ACTV_NM', 'archetype']],
                      on=['FLD_NM', 'OFFC_NM', 'PGM_NM', 'ACTV_NM'])
print(f'  매칭된 활동×월: {len(raw_keyed):,}')

# Activity-normalized monthly amount: divide each activity by its annual mean to remove scale bias
raw_keyed['date'] = pd.to_datetime(raw_keyed['year'].astype(str) + '-' +
                                    raw_keyed['month'].astype(str).str.zfill(2) + '-01')
# Per-activity annual normalization
raw_keyed['act_year_key'] = list(zip(raw_keyed['FLD_NM'], raw_keyed['OFFC_NM'],
                                       raw_keyed['PGM_NM'], raw_keyed['ACTV_NM'],
                                       raw_keyed['year']))
ann_mean = raw_keyed.groupby('act_year_key')['amt'].transform('mean')
raw_keyed['amt_norm'] = raw_keyed['amt'] / ann_mean.replace(0, np.nan)

# Aggregate to archetype × date (mean normalized amount)
panel = raw_keyed.dropna(subset=['amt_norm']).groupby(['archetype', 'date'])['amt_norm'].mean().reset_index()
panel = panel.pivot(index='date', columns='archetype', values='amt_norm').fillna(0)
panel = panel.sort_index()
print(f'  panel: {panel.shape} (date × archetype)')

# ============================================================
# Step 2: CWT (Continuous Wavelet Transform) per archetype
# ============================================================
print('\nStep 2: Morlet CWT per archetype')

# scales: 2 ~ 40 months (covers k=2 ~ k=66 ish)
scales = np.arange(2, 40)
# wavelet: Complex Morlet
wavelet = 'cmor1.5-1.0'

# sampling frequency: 1 sample per month
sampling_period = 1  # 1 month

# Convert scales to periods
freqs = pywt.scale2frequency(wavelet, scales) / sampling_period  # cycles per month
periods = 1 / freqs  # months per cycle

cwt_results = {}
for arch in ['C0_personnel', 'C1_direct_invest', 'C2_chooyeon', 'C3_normal']:
    if arch not in panel.columns:
        continue
    sig = panel[arch].values
    sig_centered = sig - sig.mean()
    coeffs, _ = pywt.cwt(sig_centered, scales, wavelet, sampling_period=sampling_period)
    power = np.abs(coeffs)**2
    cwt_results[arch] = {'power': power, 'periods': periods, 'time': panel.index}
    print(f'  {arch}: power shape {power.shape}, period range {periods.min():.1f}~{periods.max():.1f} months')

# ============================================================
# Step 3: 12개월 진폭의 시간 진화 — 연도별 평균
# ============================================================
print('\nStep 3: 12-month 진폭 시간 진화 (연도별)')

# Find scale closest to 12 months
target_period = 12
idx_12m = np.argmin(np.abs(periods - target_period))
print(f'  12m에 가장 가까운 scale: idx={idx_12m}, period={periods[idx_12m]:.2f}')

evol_records = []
for arch, d in cwt_results.items():
    power_12m = d['power'][idx_12m, :]  # over time
    df_evol = pd.DataFrame({'date': d['time'], 'power_12m': power_12m})
    df_evol['year'] = pd.to_datetime(df_evol['date']).dt.year
    by_year = df_evol.groupby('year')['power_12m'].mean().reset_index()
    by_year['archetype'] = arch
    evol_records.append(by_year)

evol_df = pd.concat(evol_records, ignore_index=True)
evol_df.to_csv(os.path.join(RES, 'H28_wavelet_12m_evolution.csv'), index=False)
print(f'  → H28_wavelet_12m_evolution.csv')

# ============================================================
# Step 4: Scaleogram 시각화 (4 원형)
# ============================================================
print('\nStep 4: Scaleogram figure 생성')
arch_names = {'C0_personnel': '인건비형 (n=129)', 'C1_direct_invest': '자산취득형 (n=99)',
              'C2_chooyeon': '출연금형 (n=154)', 'C3_normal': '정상사업 (n=1,175)'}

fig, axes = plt.subplots(4, 1, figsize=(11, 22), sharex=False, sharey=False,
                         constrained_layout=True)
arch_list = ['C0_personnel', 'C1_direct_invest', 'C2_chooyeon', 'C3_normal']
for ax, arch in zip(axes.flatten(), arch_list):
    if arch not in cwt_results:
        continue
    d = cwt_results[arch]
    times = pd.to_datetime(d['time'])
    # log-scale colormap
    Z = np.log1p(d['power'])
    im = ax.pcolormesh(times, d['periods'], Z, shading='auto',
                       cmap='viridis', vmin=0, vmax=Z.max())
    ax.set_yscale('log')
    ax.set_yticks([3, 6, 12, 24])
    ax.set_yticklabels(['3m', '6m', '12m', '24m'])
    ax.set_ylim(2, 36)
    ax.invert_yaxis()
    ax.axhline(12, color='red', linestyle='--', alpha=0.6, linewidth=2)
    ax.set_title(arch_names.get(arch, arch), fontweight='bold')
    ax.set_ylabel('주기 (개월)')
    ax.set_xlabel('연도')

# colorbar: figure 오른쪽 세로로 한 번에
cbar = fig.colorbar(im, ax=axes.tolist(), orientation='vertical',
                     label='log(1 + power)', pad=0.02, shrink=0.8)
cbar.set_label('log(1 + power)')

fig.suptitle('웨이블릿 Scaleogram — 사업원형별 시간×주기 power 분포\n'
             '(붉은 점선: 12m, 색이 밝을수록 강한 진폭)', fontweight='bold')
plt.savefig(os.path.join(FIG, 'h28_scaleogram.png'), dpi=200, bbox_inches='tight')
plt.close()
print(f'  → h28_scaleogram.png')

# ============================================================
# Step 5: 12m 진폭 시간 진화
# ============================================================
print('\nStep 5: 12m 진폭 시간 진화 figure')
fig, ax = plt.subplots(figsize=(11, 6))
arch_colors = {'C0_personnel': '#4C72B0', 'C1_direct_invest': '#DD8452',
               'C2_chooyeon': '#55A868', 'C3_normal': '#C44E52'}
for arch in ['C0_personnel', 'C1_direct_invest', 'C2_chooyeon', 'C3_normal']:
    sub = evol_df[evol_df['archetype'] == arch]
    if len(sub) == 0:
        continue
    ax.plot(sub['year'], sub['power_12m'], 'o-',
            label=arch_names.get(arch, arch),
            color=arch_colors.get(arch, '#888'),
            linewidth=2.5, markersize=10)

# 정책 변화점 annotation
for yr, lbl in [(2017, '국가재정법 시행 후 10년'),
                 (2020, 'COVID 확장재정')]:
    ax.axvline(yr, color='gray', linestyle=':', alpha=0.5)
    ax.text(yr, ax.get_ylim()[1] * 0.95, f' {lbl}', fontsize=plt.rcParams['font.size'] * 0.85, color='gray', va='top')

ax.set_xlabel('연도')
ax.set_ylabel('웨이블릿 12m 평균 power')
ax.set_title('12개월 cycle 진폭의 시간 진화 — 게임화 강도가 시간에 따라 변하는가',
             fontweight='bold')
ax.legend(loc='best', frameon=True, fancybox=True)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(FIG, 'h28_12m_evolution.png'), dpi=200, bbox_inches='tight')
plt.close()
print(f'  → h28_12m_evolution.png')

# ============================================================
# Summary
# ============================================================
print('\n[원형별 12m 진폭 시간 진화]')
for arch in ['C0_personnel', 'C1_direct_invest', 'C2_chooyeon', 'C3_normal']:
    sub = evol_df[evol_df['archetype'] == arch].sort_values('year')
    if len(sub) == 0:
        continue
    early = sub.head(3)['power_12m'].mean()
    late = sub.tail(3)['power_12m'].mean()
    print(f'  {arch_names.get(arch, arch)}: early(2015~2017)={early:.4f}, late(2023~2025)={late:.4f}, '
          f'change={(late/early - 1)*100:+.1f}%')

print('\n완료 (H28 웨이블릿).')
print('출력:')
print('  data/results/H28_wavelet_12m_evolution.csv')
print('  data/figs/h28_scaleogram.png')
print('  data/figs/h28_12m_evolution.png')
