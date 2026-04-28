"""H24: STL 분해 기반 게임화 재측정 — trend 제거 후 seasonal/remainder 분리.

이론:
  시계열 = trend + seasonal + remainder
  기존 amp_12m_norm = FFT 기반 연 주기 진폭 → trend 영향 混入 가능
  진짜 게임화 metric = seasonal_strength (trend-detrended 대비 계절 성분 비율)
  → H6 재실행으로 사회복지 신호 변화 추적

방법:
  1. 분야×월 집행 집계 (2015-01 ~ 2025-12, 132개월)
  2. STL decomposition (period=12, robust=True)
  3. seasonal_strength = Var(seasonal) / Var(seasonal + remainder)
  4. amp_seasonal  = seasonal component range (max-min, 연별)
  5. amp_remainder = remainder std (연별)
  6. trend_strength = Var(trend) / Var(trend + remainder)
  7. H6 재실행: seasonal_strength 사용 + permutation test
  8. FFT amp_12m_norm vs seasonal_strength 산점도 비교

출력:
  data/figs/h24/H24_stl_examples.png
  data/figs/h24/H24_seasonal_vs_amp12m.png
  data/results/H24_stl_metrics.csv
  data/results/H24_h6_replication.csv
"""
import os, sys, io, warnings
import numpy as np
import pandas as pd
import duckdb
import matplotlib.pyplot as plt
import matplotlib as mpl
import scienceplots
import seaborn as sns
from scipy.stats import pearsonr
from statsmodels.tsa.seasonal import STL
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

# ── 경로 설정 ──
ROOT   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB     = os.path.join(ROOT, 'data', 'warehouse.duckdb')
H3_CSV = os.path.join(ROOT, 'data', 'results', 'H3_activity_embedding.csv')
RES    = os.path.join(ROOT, 'data', 'results')
FIG    = os.path.join(ROOT, 'data', 'figs', 'h24')
os.makedirs(FIG, exist_ok=True)

RNG     = np.random.default_rng(42)
MAX_PX  = 1800
DPI     = 200
N_PERM  = 1000

# ── H6 outcome 매핑 (v3 기준) ──
OUTCOME_MAP = {
    '사회복지':               'wealth_gini',
    '보건':                   'life_expectancy',
    '과학기술':               'patent_apps_total',
    '산업·중소기업및에너지':   'industry_production_index',
    '문화및관광':             'foreign_tourists_total',
    '교육':                   'private_edu_hours',
    '국토및지역개발':         'housing_supply',
    '일반·지방행정':          'fiscal_indep_natl',
    '농림수산':               'farm_income',
    '교통및물류':             'traffic_deaths',
    '환경':                   'ghg_total',
    '통신':                   'broadband_per_100',
    '통일·외교':              'oda_total',
    '공공질서및안전':          'crime_occurrence',
    '국방':                   'defense_op_margin',
}

# ============================================================
# Step 1: monthly_exec → 분야×월 집계
# ============================================================
print('=' * 70)
print('Step 1: monthly_exec → 분야×월 집행 집계')
print('=' * 70)

con = duckdb.connect(DB, read_only=True)

monthly = con.execute("""
    SELECT
        FSCL_YY     AS year,
        EXE_M       AS month,
        FLD_NM      AS fld_nm,
        SUM(EP_AMT) AS exec_amt
    FROM monthly_exec
    WHERE FSCL_YY BETWEEN 2015 AND 2025
      AND EXE_M BETWEEN 1 AND 12
      AND FLD_NM NOT IN ('예비비', '외교·통일')
    GROUP BY FSCL_YY, EXE_M, FLD_NM
    ORDER BY FLD_NM, FSCL_YY, EXE_M
""").fetchdf()

# outcome 패널 로드 (H6 비교용)
oc_metrics = list(OUTCOME_MAP.values()) + ['amp_12m_norm', 'grdp_national']
metric_list = "', '".join(sorted(set(oc_metrics)))
panel_wide = con.execute(f"""
    SELECT fld_nm, year, metric_code, value
    FROM indicator_panel
    WHERE metric_code IN ('{metric_list}')
""").fetchdf().pivot_table(
    index=['fld_nm', 'year'], columns='metric_code', values='value'
).reset_index()

con.close()

print(f'  monthly rows: {len(monthly)}, 분야: {monthly["fld_nm"].nunique()}')
print(f'  연도: {monthly["year"].min()} ~ {monthly["year"].max()}')
print(f'  분야: {sorted(monthly["fld_nm"].unique())}')

# ============================================================
# Step 2: STL 분해 — 분야별
# ============================================================
print('\n' + '=' * 70)
print('Step 2: STL decomposition (period=12, robust=True)')
print('=' * 70)

# 분야별로 STL 수행 → 연별 strength 메트릭 집계
stl_metrics_rows = []   # 분야×연 단위 결과
stl_store        = {}   # 분야별 전체 시계열 저장 (그래프용)

FIELDS = sorted(monthly['fld_nm'].unique())

for fld in FIELDS:
    sub = monthly[monthly['fld_nm'] == fld].sort_values(['year', 'month'])

    # 2015-01 ~ 2025-12 완전한 132개 인덱스 보장
    idx = pd.MultiIndex.from_product(
        [range(2015, 2026), range(1, 13)], names=['year', 'month']
    )
    ts = sub.set_index(['year', 'month'])['exec_amt']
    ts = ts.reindex(idx, fill_value=0).values.astype(float)

    # 0 값이 너무 많으면 skip
    n_nonzero = np.count_nonzero(ts)
    if n_nonzero < 24:
        print(f'  [SKIP] {fld}: 비영 값 {n_nonzero} < 24')
        continue

    # 0 값을 NaN → 선형 보간 (극단적 0-집중 방지)
    ts_series = pd.Series(ts)
    ts_series[ts_series == 0] = np.nan
    ts_series = ts_series.interpolate(method='linear', limit_direction='both')
    ts_series = ts_series.fillna(ts_series.mean())

    try:
        stl_res = STL(ts_series, period=12, robust=True).fit()
    except Exception as e:
        print(f'  [STL ERROR] {fld}: {e}')
        continue

    trend     = stl_res.trend
    seasonal  = stl_res.seasonal
    remainder = stl_res.resid         # statsmodels DecomposeResult → .resid
    detrended = seasonal + remainder   # = ts - trend

    # 전체 strength
    var_seas   = np.var(seasonal)
    var_det    = np.var(detrended)
    var_rem    = np.var(remainder)
    var_trend  = np.var(trend)
    var_tr_rem = np.var(trend + remainder)

    seas_strength_all  = max(0.0, 1.0 - var_rem / var_det) if var_det > 0 else np.nan
    trend_strength_all = max(0.0, 1.0 - var_rem / var_tr_rem) if var_tr_rem > 0 else np.nan

    # 연별 메트릭 집계
    for y_idx, year in enumerate(range(2015, 2026)):
        sl = slice(y_idx * 12, (y_idx + 1) * 12)
        s_y  = seasonal[sl]
        r_y  = remainder[sl]
        t_y  = trend[sl]
        d_y  = detrended[sl]

        var_s = np.var(s_y)
        var_r = np.var(r_y)
        var_d = np.var(d_y)
        var_tr_r = np.var(t_y + r_y)

        ss = max(0.0, 1.0 - var_r / var_d) if var_d > 0 else np.nan
        ts_s = max(0.0, 1.0 - var_r / var_tr_r) if var_tr_r > 0 else np.nan

        stl_metrics_rows.append({
            'fld_nm':          fld,
            'year':            year,
            'seasonal_strength': ss,
            'trend_strength':    ts_s,
            'amp_seasonal':    float(np.ptp(s_y)),   # peak-to-peak
            'amp_remainder':   float(np.std(r_y)),
            'seas_strength_all':  seas_strength_all,
            'trend_strength_all': trend_strength_all,
        })

    stl_store[fld] = {
        'ts':        ts_series.values,
        'trend':     trend,
        'seasonal':  seasonal,
        'remainder': remainder,    # = resid
    }
    print(f'  {fld:20s}: seas_str={seas_strength_all:.3f}  trend_str={trend_strength_all:.3f}')

stl_df = pd.DataFrame(stl_metrics_rows)
stl_df.to_csv(os.path.join(RES, 'H24_stl_metrics.csv'),
              index=False, encoding='utf-8-sig')
print(f'\n  STL metrics → {RES}/H24_stl_metrics.csv  ({len(stl_df)} rows)')

# ============================================================
# Step 3: Figure A — 4 분야 STL 분해 예시
# ============================================================
print('\n' + '=' * 70)
print('Step 3: 그림 A — 4분야 STL 분해 예시')
print('=' * 70)

# 사회복지, 보건, 교육, 국방 (다양한 패턴)
EXAMPLE_FLDS = ['사회복지', '보건', '교육', '국방']
EXAMPLE_FLDS = [f for f in EXAMPLE_FLDS if f in stl_store]

months_idx = pd.date_range('2015-01', periods=132, freq='MS')

n_ex = len(EXAMPLE_FLDS)
fig, axes = plt.subplots(n_ex, 4, figsize=(min(MAX_PX / DPI, 16), n_ex * 3.2))
if n_ex == 1:
    axes = axes[np.newaxis, :]

col_titles = ['원시계열 (집행액)', 'Trend', 'Seasonal', 'Remainder']
colors_comp = ['#3a6ea5', '#d35c37', '#5ba85a', '#8e4fb8']

for row, fld in enumerate(EXAMPLE_FLDS):
    d = stl_store[fld]
    comps = [d['ts'], d['trend'], d['seasonal'], d['remainder']]
    for col, (comp, ctitle, col_c) in enumerate(zip(comps, col_titles, colors_comp)):
        ax = axes[row, col]
        ax.plot(months_idx, comp, lw=1.2, color=col_c)
        ax.axhline(0, color='#aaa', lw=0.5, ls='--')
        ax.grid(alpha=0.3, lw=0.5)
        if row == 0:
            ax.set_title(ctitle, fontsize=10, fontweight='bold')
        if col == 0:
            ax.set_ylabel(fld, fontsize=10, fontweight='bold')
        ax.tick_params(labelsize=7)
        # x축 레이블: 첫 열만 연도 표시
        if row == n_ex - 1:
            ax.set_xlabel('연월', fontsize=8)
        # seas_strength 표기 (seasonal 패널)
        if col == 2:
            ss_val = stl_df[stl_df['fld_nm'] == fld]['seas_strength_all'].iloc[0] \
                     if len(stl_df[stl_df['fld_nm'] == fld]) > 0 else np.nan
            ax.set_title(f'{ctitle}\n(seas_str={ss_val:.3f})', fontsize=9)

plt.suptitle('STL 분해 예시 (4개 분야)\ntend + seasonal + remainder',
             fontsize=12, fontweight='bold', y=1.01)
plt.tight_layout()
out_a = os.path.join(FIG, 'H24_stl_examples.png')
fig.savefig(out_a, dpi=DPI, bbox_inches='tight')
plt.close()
print(f'  저장: {out_a}')

# ============================================================
# Step 4: Figure B — seasonal_strength vs amp_12m_norm 산점도
# ============================================================
print('\n' + '=' * 70)
print('Step 4: 그림 B — seasonal_strength vs amp_12m_norm 산점도')
print('=' * 70)

# amp_12m_norm (기존 FFT metric)
amp_wide = panel_wide[['fld_nm', 'year', 'amp_12m_norm']].dropna()

# 연별 seasonal_strength merge
compare_df = stl_df[['fld_nm', 'year', 'seasonal_strength', 'trend_strength',
                      'amp_seasonal', 'amp_remainder']].merge(
    amp_wide, on=['fld_nm', 'year'], how='inner'
)
compare_df = compare_df.dropna(subset=['seasonal_strength', 'amp_12m_norm'])
print(f'  비교 데이터: {len(compare_df)} 행')

# 상관
r_all, p_all = pearsonr(compare_df['seasonal_strength'], compare_df['amp_12m_norm']) \
    if len(compare_df) >= 3 else (np.nan, np.nan)

fig, axes = plt.subplots(1, 3, figsize=(min(MAX_PX / DPI, 16), 5.5))

# B1: seasonal_strength vs amp_12m_norm (전체)
ax = axes[0]
cmap = plt.cm.tab20
fld_list = sorted(compare_df['fld_nm'].unique())
for i, fld in enumerate(fld_list):
    sub = compare_df[compare_df['fld_nm'] == fld]
    ax.scatter(sub['amp_12m_norm'], sub['seasonal_strength'],
               color=cmap(i / max(len(fld_list) - 1, 1)),
               s=35, alpha=0.7, label=fld[:6])
ax.set_xlabel('amp_12m_norm (FFT 기반)', fontsize=10)
ax.set_ylabel('seasonal_strength (STL 기반)', fontsize=10)
ax.set_title(f'FFT vs STL seasonal_strength\n(N={len(compare_df)}, r={r_all:.3f}, p={p_all:.3f})',
             fontsize=10)
ax.legend(fontsize=6, ncol=2, loc='upper left')
ax.grid(alpha=0.3)

# B2: 분야별 평균 비교 (막대 2종 비교)
ax = axes[1]
fld_mean = compare_df.groupby('fld_nm')[['seasonal_strength', 'amp_12m_norm']].mean().reset_index()
fld_mean_sort = fld_mean.sort_values('seasonal_strength', ascending=True)
yy = np.arange(len(fld_mean_sort))
bw = 0.38
# amp_12m_norm을 0~1 범위로 스케일 맞춤 (단위 다름)
amp_scaled = (fld_mean_sort['amp_12m_norm'] - fld_mean_sort['amp_12m_norm'].min()) / \
             (fld_mean_sort['amp_12m_norm'].max() - fld_mean_sort['amp_12m_norm'].min() + 1e-9)
ax.barh(yy - bw/2, fld_mean_sort['seasonal_strength'], height=bw,
        color='#5475a8', alpha=0.85, label='seasonal_strength (STL)')
ax.barh(yy + bw/2, amp_scaled, height=bw,
        color='#c87f5a', alpha=0.8, label='amp_12m_norm (FFT, 정규화)')
ax.set_yticks(yy)
ax.set_yticklabels(fld_mean_sort['fld_nm'], fontsize=9)
ax.set_xlabel('값', fontsize=9)
ax.set_title('분야별 평균: STL vs FFT\n(FFT는 0~1 정규화)', fontsize=10)
ax.legend(fontsize=8)
ax.grid(alpha=0.3, axis='x')

# B3: trend_strength vs seasonal_strength
ax = axes[2]
for i, fld in enumerate(fld_list):
    sub = compare_df[compare_df['fld_nm'] == fld]
    ax.scatter(sub['seasonal_strength'], sub['trend_strength'],
               color=cmap(i / max(len(fld_list) - 1, 1)),
               s=35, alpha=0.7, label=fld[:6])
r_ts, p_ts = pearsonr(compare_df['seasonal_strength'].dropna(),
                       compare_df['trend_strength'].dropna()) \
    if len(compare_df.dropna(subset=['trend_strength'])) >= 3 else (np.nan, np.nan)
ax.set_xlabel('seasonal_strength', fontsize=10)
ax.set_ylabel('trend_strength', fontsize=10)
ax.set_title(f'seasonal_strength vs trend_strength\n(r={r_ts:.3f}, p={p_ts:.3f})', fontsize=10)
ax.legend(fontsize=6, ncol=2, loc='upper left')
ax.grid(alpha=0.3)

plt.suptitle('STL vs FFT 비교 — seasonal_strength vs amp_12m_norm', fontsize=12, fontweight='bold', y=1.01)
plt.tight_layout()
out_b = os.path.join(FIG, 'H24_seasonal_vs_amp12m.png')
fig.savefig(out_b, dpi=DPI, bbox_inches='tight')
plt.close()
print(f'  저장: {out_b}')
print(f'  상관(seasonal_strength ~ amp_12m_norm): r={r_all:.3f}, p={p_all:.3f}')

# ============================================================
# Step 5: H6 재실행 — seasonal_strength 사용
# ============================================================
print('\n' + '=' * 70)
print('Step 5: H6 재실행 — seasonal_strength 사용 + permutation test')
print('=' * 70)

# seasonal_strength 연별 테이블 (분야×연)
seas_annual = stl_df[['fld_nm', 'year', 'seasonal_strength']].copy()

h6_results = []

for fld, oc_metric in OUTCOME_MAP.items():
    if oc_metric not in panel_wide.columns:
        print(f'  [SKIP] {fld}: {oc_metric} 없음')
        continue

    # STL seasonal_strength 시계열
    amp_ts = seas_annual[seas_annual['fld_nm'] == fld].set_index('year')['seasonal_strength'].dropna()

    # outcome 시계열
    oc_ts = panel_wide[panel_wide['fld_nm'] == fld].set_index('year')[oc_metric].dropna()

    common = amp_ts.index.intersection(oc_ts.index)
    if len(common) < 4:
        print(f'  [SKIP] {fld}: 공통연도 {len(common)} < 4')
        continue

    d_amp = amp_ts.loc[common].diff().dropna()
    d_oc  = oc_ts.loc[common].diff().dropna()
    ci    = d_amp.index.intersection(d_oc.index)
    if len(ci) < 3:
        print(f'  [SKIP] {fld}: 차분 공통 {len(ci)} < 3')
        continue

    # 원시 상관
    obs_corr, p_raw = pearsonr(d_amp.loc[ci], d_oc.loc[ci])

    # Permutation test
    null = np.array([
        pearsonr(d_amp.loc[ci].values, RNG.permutation(d_oc.loc[ci].values))[0]
        for _ in range(N_PERM)
    ])
    p_perm = float(((np.abs(null) >= np.abs(obs_corr)).sum() + 1) / (N_PERM + 1))

    # 기존 amp_12m_norm으로도 상관 계산 (비교)
    amp12_ts = panel_wide[panel_wide['fld_nm'] == fld].set_index('year')['amp_12m_norm'].dropna() \
        if 'amp_12m_norm' in panel_wide.columns else pd.Series(dtype=float)
    common2 = amp12_ts.index.intersection(oc_ts.index)
    if len(common2) >= 4:
        d_amp12 = amp12_ts.loc[common2].diff().dropna()
        d_oc2   = oc_ts.loc[common2].diff().dropna()
        ci2     = d_amp12.index.intersection(d_oc2.index)
        obs_corr12 = pearsonr(d_amp12.loc[ci2], d_oc2.loc[ci2])[0] if len(ci2) >= 3 else np.nan
        null12 = np.array([
            pearsonr(d_amp12.loc[ci2].values, RNG.permutation(d_oc2.loc[ci2].values))[0]
            for _ in range(N_PERM)
        ]) if len(ci2) >= 3 else np.array([np.nan])
        p_perm12 = float(((np.abs(null12) >= np.abs(obs_corr12)).sum() + 1) / (N_PERM + 1)) \
            if not np.isnan(obs_corr12) else np.nan
    else:
        obs_corr12, p_perm12 = np.nan, np.nan

    h6_results.append({
        'fld':           fld,
        'outcome':       oc_metric,
        'n_diff':        len(ci),
        # STL seasonal_strength
        'corr_stl':      round(float(obs_corr), 4),
        'pval_stl':      round(p_perm, 4),
        # 기존 FFT amp_12m_norm
        'corr_fft':      round(float(obs_corr12), 4) if not np.isnan(obs_corr12) else np.nan,
        'pval_fft':      round(p_perm12, 4) if not np.isnan(p_perm12) else np.nan,
        # 부호 변화
        'sign_change':   (np.sign(obs_corr) != np.sign(obs_corr12)) if not np.isnan(obs_corr12) else False,
    })

    sig_stl = '★' if p_perm   < 0.05 else ' '
    sig_fft = '★' if (not np.isnan(p_perm12) and p_perm12 < 0.05) else ' '
    print(f'  {fld:20s}: STL r={obs_corr:+.3f} p={p_perm:.3f}{sig_stl} | '
          f'FFT r={obs_corr12:+.3f} p={p_perm12:.3f}{sig_fft}')

h6_df = pd.DataFrame(h6_results).sort_values('pval_stl')
h6_df.to_csv(os.path.join(RES, 'H24_h6_replication.csv'),
             index=False, encoding='utf-8-sig')
print(f'\n  H6 replication → {RES}/H24_h6_replication.csv')

# ============================================================
# Step 6: Figure C — H6 재실행 결과 비교 (STL vs FFT)
# ============================================================
print('\n' + '=' * 70)
print('Step 6: 그림 C — H6 재실행 결과 시각화 (STL vs FFT)')
print('=' * 70)

if len(h6_df) > 0:
    fig, axes = plt.subplots(1, 3,
        figsize=(min(MAX_PX / DPI, 18), max(6, 0.55 * len(h6_df) + 2.5)),
        gridspec_kw={'width_ratios': [1.8, 1.8, 1.2]})

    h6_sort_stl = h6_df.sort_values('corr_stl')
    yy = np.arange(len(h6_sort_stl))
    bw = 0.38

    # C1: STL corr
    ax = axes[0]
    colors_stl = ['#a85454' if v < 0 else '#5475a8' for v in h6_sort_stl['corr_stl']]
    ax.barh(yy, h6_sort_stl['corr_stl'], color=colors_stl, alpha=0.85)
    ax.set_yticks(yy)
    ax.set_yticklabels(h6_sort_stl['fld'], fontsize=9)
    ax.axvline(0, color='#888', lw=0.7)
    for i, (_, row) in enumerate(h6_sort_stl.iterrows()):
        sig = '★' if row['pval_stl'] < 0.05 else ''
        ax.annotate(f'{sig}p={row["pval_stl"]:.3f}',
                    (row['corr_stl'], yy[i]),
                    xytext=(4, 0), textcoords='offset points',
                    va='center', fontsize=7)
    n_sig_stl = (h6_df['pval_stl'] < 0.05).sum()
    ax.set_xlabel('Δseasonal_strength ~ Δoutcome 상관', fontsize=9)
    ax.set_title(f'STL seasonal_strength — 견고성 검증\n★p<0.05: {n_sig_stl}/{len(h6_df)} 분야',
                 fontsize=10, fontweight='bold')
    ax.grid(alpha=0.3, axis='x')

    # C2: FFT corr
    ax = axes[1]
    h6_sort_fft = h6_df.sort_values('corr_fft')
    yy2 = np.arange(len(h6_sort_fft))
    colors_fft = ['#a85454' if (not np.isnan(v) and v < 0) else '#5475a8'
                  for v in h6_sort_fft['corr_fft']]
    ax.barh(yy2, h6_sort_fft['corr_fft'].fillna(0), color=colors_fft, alpha=0.75)
    ax.set_yticks(yy2)
    ax.set_yticklabels(h6_sort_fft['fld'], fontsize=9)
    ax.axvline(0, color='#888', lw=0.7)
    for i, (_, row) in enumerate(h6_sort_fft.iterrows()):
        if not np.isnan(row['pval_fft']):
            sig = '★' if row['pval_fft'] < 0.05 else ''
            ax.annotate(f'{sig}p={row["pval_fft"]:.3f}',
                        (row['corr_fft'] if not np.isnan(row['corr_fft']) else 0, yy2[i]),
                        xytext=(4, 0), textcoords='offset points',
                        va='center', fontsize=7)
    n_sig_fft = (h6_df['pval_fft'].fillna(1.0) < 0.05).sum()
    ax.set_xlabel('Δamp_12m_norm ~ Δoutcome 상관', fontsize=9)
    ax.set_title(f'FFT amp_12m_norm — 견고성 검증\n★p<0.05: {n_sig_fft}/{len(h6_df)} 분야',
                 fontsize=10, fontweight='bold')
    ax.grid(alpha=0.3, axis='x')

    # C3: STL vs FFT 산점도 (분야별)
    ax = axes[2]
    valid = h6_df.dropna(subset=['corr_stl', 'corr_fft'])
    sign_same = (np.sign(valid['corr_stl']) == np.sign(valid['corr_fft'])).sum()
    ax.scatter(valid['corr_fft'], valid['corr_stl'],
               c=['#a85454' if s else '#5475a8' for s in valid['sign_change']],
               s=65, alpha=0.85, zorder=3)
    ax.plot([-1, 1], [-1, 1], '--', color='#888', alpha=0.5, label='y=x')
    ax.axhline(0, color='#aaa', lw=0.5)
    ax.axvline(0, color='#aaa', lw=0.5)
    for _, row in valid.iterrows():
        ax.annotate(row['fld'][:5], (row['corr_fft'], row['corr_stl']),
                    xytext=(3, 3), textcoords='offset points', fontsize=7)
    r_ff_st, _ = pearsonr(valid['corr_fft'], valid['corr_stl']) if len(valid) >= 3 else (np.nan, np.nan)
    ax.set_xlabel('FFT 상관 (amp_12m_norm)', fontsize=9)
    ax.set_ylabel('STL 상관 (seasonal_strength)', fontsize=9)
    ax.set_title(f'FFT vs STL 상관\nr={r_ff_st:.3f}, 동부호: {sign_same}/{len(valid)}\n(빨강=부호반전)', fontsize=9)
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    ax.set_xlim(-1.05, 1.05)
    ax.set_ylim(-1.05, 1.05)

    plt.suptitle('견고성 재실행 — STL seasonal_strength vs FFT amp_12m_norm',
                 fontsize=12, fontweight='bold', y=1.01)
    plt.tight_layout()
    out_c = os.path.join(FIG, 'H24_h6_replication.png')
    fig.savefig(out_c, dpi=DPI, bbox_inches='tight')
    plt.close()
    print(f'  저장: {out_c}')

# ============================================================
# 최종 요약
# ============================================================
print('\n' + '=' * 70)
print('최종 요약')
print('=' * 70)
print()
print('  [STL seasonal_strength H6 결과]')
print(h6_df[['fld', 'outcome', 'corr_stl', 'pval_stl',
             'corr_fft', 'pval_fft', 'sign_change']].to_string(index=False))

n_sig_stl = (h6_df['pval_stl'] < 0.05).sum()
n_sig_fft = (h6_df['pval_fft'].fillna(1.0) < 0.05).sum()
n_sign_change = h6_df['sign_change'].sum()
n_same_sign = len(h6_df.dropna(subset=['corr_fft'])) - int(n_sign_change)

print(f'\n  STL p<0.05: {n_sig_stl}/{len(h6_df)} 분야')
print(f'  FFT p<0.05: {n_sig_fft}/{len(h6_df)} 분야')
print(f'  부호 일관: {n_same_sign}/{len(h6_df.dropna(subset=["corr_fft"]))} 분야')

# 사회복지 중심 비교
sw = h6_df[h6_df['fld'] == '사회복지']
if len(sw) > 0:
    r = sw.iloc[0]
    print(f'\n  [사회복지] FFT: r={r["corr_fft"]:+.3f} p={r["pval_fft"]:.3f}'
          f' → STL: r={r["corr_stl"]:+.3f} p={r["pval_stl"]:.3f}'
          f'  (부호반전={r["sign_change"]})')

print('\n  출력 파일:')
for f in sorted(os.listdir(FIG)):
    print(f'    data/figs/h24/{f}')
for f in sorted(os.listdir(RES)):
    if f.startswith('H24_'):
        print(f'    data/results/{f}')

print('\n완료 (H24 STL 분해).')
