"""H26: NeuralProphet 기반 게임화 강도 측정 — FFT amp_12m_norm & STL seasonal_strength 3-way 교차검증.

방법:
  1. monthly_exec 2015~2025 로드 → 활동×연도 월별 패널 구성
  2. 각 (활동, 연도) 쌍에 대해 NeuralProphet fit (yearly_seasonality=True, n_lags=0)
  3. 연 계절성 강도: range(yearly_component) / std(observed) → np_seasonal_strength
  4. FFT amp_12m_norm, STL seasonal_strength와 3-way 상관행렬 산출
  5. 14개 분야 × 3개 측도 게임화-결과 상관 비교

출력:
  data/results/H26_neuralprophet_summary.csv  — 3-way 상관행렬
  data/results/H26_field_outcome_corr_np.csv  — 14 분야 × 3 측도 결과 상관
  data/figs/h26_neuralprophet.png             — 3-panel figure
"""
import os, sys, io, warnings, logging
import numpy as np
import pandas as pd
import duckdb
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib as mpl
from scipy.stats import pearsonr
from scipy import fft as scfft

warnings.filterwarnings('ignore')
# NeuralProphet 로깅 억제
logging.getLogger("NP").setLevel(logging.ERROR)
logging.getLogger("neuralprophet").setLevel(logging.ERROR)
logging.getLogger("pytorch_lightning").setLevel(logging.ERROR)
logging.getLogger("lightning").setLevel(logging.ERROR)
# torch/lightning verbose 억제
os.environ.setdefault("PYTHONWARNINGS", "ignore")

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB     = os.path.join(ROOT, 'data', 'warehouse.duckdb')
RES    = os.path.join(ROOT, 'data', 'results')
FIG_DIR = os.path.join(ROOT, 'data', 'figs')
os.makedirs(RES, exist_ok=True)
os.makedirs(FIG_DIR, exist_ok=True)

# ── 한국어 폰트 설정 ──
KFONT = None
for cand in ['KoPubWorld Dotum', 'Noto Sans KR', 'Malgun Gothic', 'Noto Sans CJK KR', 'AppleGothic']:
    if any(cand in fn.name for fn in mpl.font_manager.fontManager.ttflist):
        mpl.rcParams['font.family'] = cand
        KFONT = cand
        break
mpl.rcParams['axes.unicode_minus'] = False
BASE_FONT = 13

RNG = np.random.default_rng(42)

# ── 결과 제외 활동 키워드 (회계거래) ──
PURE_ACCT = """(
    ACTV_NM ILIKE '%전출금%' OR ACTV_NM ILIKE '%타계정%' OR ACTV_NM ILIKE '%여유자금%'
 OR ACTV_NM ILIKE '%국고예탁%' OR ACTV_NM ILIKE '%기금예탁%' OR ACTV_NM ILIKE '%국고예치%'
 OR ACTV_NM ILIKE '%회계간거래%' OR ACTV_NM ILIKE '%회계간전출%'
 OR ACTV_NM ILIKE '%회계기금간%' OR ACTV_NM ILIKE '%여유자금운용%'
)"""

# ── H6 OUTCOME MAP (H24 기준) ──
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

MAX_ACTIVITIES = None   # None = 전체 사용; int이면 샘플링 (속도 절충)
SAMPLE_N       = 200    # 전체가 너무 느리면 이 숫자로 샘플링
EPOCHS         = 50
LR             = 0.1
MIN_OBS        = 12     # 연도당 최소 월 수

print('=' * 70)
print('H26: NeuralProphet 게임화 강도 측정')
print('=' * 70)

# ============================================================
# Step 1: DB에서 월별 집행 데이터 로드
# ============================================================
print('\nStep 1: 월별 집행 데이터 로드 (2015~2025)')
con = duckdb.connect(DB, read_only=True)

raw = con.execute(f"""
    SELECT FLD_NM, OFFC_NM, PGM_NM, ACTV_NM,
           FSCL_YY AS year, EXE_M AS month,
           SUM(EP_AMT) AS amt
    FROM monthly_exec
    WHERE EXE_M BETWEEN 1 AND 12
      AND FSCL_YY BETWEEN 2015 AND 2025
      AND NOT {PURE_ACCT}
    GROUP BY 1,2,3,4,5,6
""").fetchdf()
print(f'  월별 집행 rows: {len(raw):,}')

# 기존 FFT amp_12m_norm (indicator_panel에 저장됨)
panel_fft = None
try:
    panel_fft = con.execute("""
        SELECT fld_nm, year, metric_code, value
        FROM indicator_panel
        WHERE metric_code = 'amp_12m_norm'
    """).fetchdf().pivot_table(
        index=['fld_nm', 'year'], columns='metric_code', values='value'
    ).reset_index().rename(columns={'fld_nm': 'FLD_NM'})
    print(f'  FFT panel rows: {len(panel_fft):,}')
except Exception as e:
    print(f'  FFT panel 로드 실패: {e}')

# 결과 지표 패널
oc_metrics = list(OUTCOME_MAP.values()) + ['amp_12m_norm', 'grdp_national']
metric_list = "', '".join(sorted(set(oc_metrics)))
try:
    panel_wide = con.execute(f"""
        SELECT fld_nm, year, metric_code, value
        FROM indicator_panel
        WHERE metric_code IN ('{metric_list}')
    """).fetchdf().pivot_table(
        index=['fld_nm', 'year'], columns='metric_code', values='value'
    ).reset_index()
    print(f'  outcome panel: {len(panel_wide):,} rows × {len(panel_wide.columns)} cols')
except Exception as e:
    panel_wide = pd.DataFrame()
    print(f'  outcome panel 로드 실패: {e}')

con.close()

# ============================================================
# Step 2: 활동×연도 패널 구성
# ============================================================
print('\nStep 2: 활동×연도 패널 구성')

KEY = ['FLD_NM', 'OFFC_NM', 'PGM_NM', 'ACTV_NM']
raw['key'] = list(zip(raw['FLD_NM'], raw['OFFC_NM'], raw['PGM_NM'], raw['ACTV_NM']))

# 활동별 연도별 데이터 정리
activity_years = {}  # key → {year → 12-vector}

for keys_tuple, g in raw.groupby(KEY):
    for yr, gy in g.groupby('year'):
        arr = np.zeros(12)
        for _, row in gy.iterrows():
            m = int(row['month']) - 1
            if 0 <= m < 12:
                arr[m] = float(row['amt'])
        if arr.sum() <= 0 or (arr > 0).sum() < 6:
            continue
        k = keys_tuple
        if k not in activity_years:
            activity_years[k] = {}
        activity_years[k][int(yr)] = arr

# 연도가 충분한 활동만
valid_keys = [k for k, yd in activity_years.items() if len(yd) >= 1]
print(f'  총 유효 활동-연도 조합: {sum(len(yd) for yd in activity_years.values()):,}')
print(f'  유효 활동(≥1년): {len(valid_keys):,}')

# 샘플링 (너무 많으면)
total_fits = sum(len(activity_years[k]) for k in valid_keys)
print(f'  예상 NP fit 횟수: {total_fits:,}')

if total_fits > 20000:
    print(f'  >> {SAMPLE_N}개 활동으로 샘플링 (random_state=42)')
    rng_sample = np.random.default_rng(42)
    sampled_idx = rng_sample.choice(len(valid_keys), size=min(SAMPLE_N, len(valid_keys)), replace=False)
    valid_keys = [valid_keys[i] for i in sorted(sampled_idx)]
    total_fits = sum(len(activity_years[k]) for k in valid_keys)
    print(f'  샘플링 후 NP fit 횟수: {total_fits:,}')

# ============================================================
# Step 3: NeuralProphet fit → np_seasonal_strength 추출
# ============================================================
print(f'\nStep 3: NeuralProphet fit (epochs={EPOCHS}, lr={LR})')
print('  (각 (활동, 연도) 쌍에 대해 24개월 학습용 데이터 + 해당 연도 분석)')

try:
    from neuralprophet import NeuralProphet, set_log_level
    set_log_level("ERROR")
except ImportError as e:
    print(f'  NeuralProphet import 실패: {e}')
    sys.exit(1)

np_records = []
fail_count = 0
done = 0

for ki, key in enumerate(valid_keys):
    fld_nm, offc_nm, pgm_nm, actv_nm = key
    yd = activity_years[key]
    years_sorted = sorted(yd.keys())

    for yr in years_sorted:
        arr_yr = yd[yr]

        # 학습 데이터: 해당 연도 + 전년도(있으면) = 최대 24개월
        # NeuralProphet은 최소 2 주기(24개월) 필요
        prev_yr = yr - 1
        if prev_yr in yd:
            arr_full = np.concatenate([yd[prev_yr], arr_yr])
            start_month = f'{prev_yr}-01-01'
        else:
            # 해당 연도만: 다음 연도가 있으면 추가
            next_yr = yr + 1
            if next_yr in yd:
                arr_full = np.concatenate([arr_yr, yd[next_yr]])
                start_month = f'{yr}-01-01'
            else:
                # 1년치만 - 2 주기 미만이지만 시도
                arr_full = arr_yr
                start_month = f'{yr}-01-01'

        n_months = len(arr_full)
        if n_months < MIN_OBS:
            continue

        # DataFrame 구성 (NP 형식: ds, y)
        ds_range = pd.date_range(start=start_month, periods=n_months, freq='MS')
        df_np = pd.DataFrame({'ds': ds_range, 'y': arr_full.astype(float)})

        # 0/음수 처리 (log scale 안 쓰고 그대로 - 규모가 크므로)
        # y=0 인 달은 작은 양수로 보간 (NP는 y=0 허용하나 불안정할 수 있음)
        df_np['y'] = df_np['y'].replace(0, df_np['y'][df_np['y'] > 0].min() * 0.01
                                         if (df_np['y'] > 0).any() else 1.0)

        try:
            m = NeuralProphet(
                yearly_seasonality=True,
                weekly_seasonality=False,
                daily_seasonality=False,
                n_lags=0,
                epochs=EPOCHS,
                learning_rate=LR,
                batch_size=None,
                trainer_config={'enable_progress_bar': False,
                                'enable_model_summary': False,
                                'logger': False,
                                'enable_checkpointing': False,
                                'default_root_dir': os.path.join(ROOT, 'tmp', 'np_lightning')},
            )
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                # 로그 완전 억제
                import logging as _log
                for lg_name in ['NP', 'neuralprophet', 'pytorch_lightning',
                                 'lightning.pytorch', 'lightning']:
                    _log.getLogger(lg_name).setLevel(_log.ERROR)
                m.fit(df_np, freq='MS', progress=False)

            # 연 계절성 성분 추출 — training df에 직접 predict (in-sample)
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                forecast = m.predict(df_np)

            # yearly seasonality 컬럼 찾기
            seas_cols = [c for c in forecast.columns if 'yearly' in c.lower()]
            if not seas_cols:
                seas_cols = [c for c in forecast.columns
                             if 'season' in c.lower() and c != 'ds' and c != 'y']

            if seas_cols:
                # 해당 연도 행만 추출
                mask_yr = forecast['ds'].dt.year == yr
                seas_yr = forecast.loc[mask_yr, seas_cols[0]].values
                obs_yr  = df_np.loc[df_np['ds'].dt.year == yr, 'y'].values

                if len(seas_yr) >= 6 and len(obs_yr) >= 6:
                    seas_range = float(np.ptp(seas_yr))
                    obs_std    = float(np.std(obs_yr))
                    np_strength = seas_range / (obs_std + 1e-9)
                else:
                    np_strength = np.nan
            else:
                np_strength = np.nan

            # FFT amp_12m_norm (자체 계산, 해당 연도)
            total = arr_yr.sum()
            if total > 0:
                yf = scfft.fft(arr_yr - arr_yr.mean())
                amp_12 = abs(yf[1]) * 2 / 12 / (total / 12)
            else:
                amp_12 = np.nan

            np_records.append({
                'FLD_NM':  fld_nm,
                'OFFC_NM': offc_nm,
                'PGM_NM':  pgm_nm,
                'ACTV_NM': actv_nm,
                'year':    yr,
                'amp_12m_norm_calc': amp_12,
                'np_seasonal_strength': np_strength,
            })

        except Exception as e:
            fail_count += 1
            if fail_count <= 5:
                print(f'  [FAIL] {actv_nm[:20]} {yr}: {e}')

        done += 1
        if done % 500 == 0:
            print(f'  진행: {done}/{total_fits} fits, 성공 {len(np_records)}, 실패 {fail_count}')

print(f'\n  완료: {done} fits, 성공 {len(np_records)}, 실패 {fail_count}')

np_df = pd.DataFrame(np_records)
print(f'  NP 결과: {len(np_df)} 활동-연도 행')
if len(np_df) == 0:
    print('ERROR: NP 결과가 없습니다. 스크립트를 종료합니다.')
    sys.exit(1)

# ============================================================
# Step 4: STL seasonal_strength 로드 및 병합
# ============================================================
print('\nStep 4: STL seasonal_strength 로드')

stl_path = os.path.join(RES, 'H24_stl_metrics.csv')
if os.path.exists(stl_path):
    stl_df = pd.read_csv(stl_path)
    print(f'  STL metrics: {len(stl_df)} 행')
    # STL은 분야×연 단위
    stl_fld = stl_df[['fld_nm', 'year', 'seasonal_strength']].rename(
        columns={'fld_nm': 'FLD_NM', 'seasonal_strength': 'stl_seasonal_strength'}
    )
else:
    print('  H24_stl_metrics.csv 없음 — STL 직접 계산 스킵')
    stl_fld = pd.DataFrame(columns=['FLD_NM', 'year', 'stl_seasonal_strength'])

# np_df에 STL 병합 (분야-연도 기준)
np_merged = np_df.merge(stl_fld, on=['FLD_NM', 'year'], how='left')

# FFT amp_12m_norm (활동 단위 자체 계산값 사용)
# indicator_panel의 amp_12m_norm은 분야 단위이므로 자체 계산값 우선
np_merged['fft_amp'] = np_merged['amp_12m_norm_calc']

print(f'  병합 후: {len(np_merged)} 행')
print(f'  NP strength 비결측: {np_merged["np_seasonal_strength"].notna().sum()}')
print(f'  FFT amp 비결측: {np_merged["fft_amp"].notna().sum()}')
print(f'  STL strength 비결측: {np_merged["stl_seasonal_strength"].notna().sum()}')

# ============================================================
# Step 5: 3-way 상관행렬
# ============================================================
print('\nStep 5: 3-way 상관행렬 계산')

corr_sub = np_merged[['fft_amp', 'stl_seasonal_strength', 'np_seasonal_strength']].dropna()
N_corr = len(corr_sub)
print(f'  3개 측도 모두 유효: {N_corr}개 활동-연도')

if N_corr >= 3:
    r_fft_np,  p_fft_np  = pearsonr(corr_sub['fft_amp'], corr_sub['np_seasonal_strength'])
    r_stl_np,  p_stl_np  = pearsonr(corr_sub['stl_seasonal_strength'], corr_sub['np_seasonal_strength'])
    r_fft_stl, p_fft_stl = pearsonr(corr_sub['fft_amp'], corr_sub['stl_seasonal_strength'])
else:
    # STL이 분야 단위라 직접 매칭 어려울 수 있음 - 분야 평균으로 시도
    print('  STL 직접 매칭 부족 → 분야×연 평균으로 재시도')
    np_fld_yr = np_merged.groupby(['FLD_NM', 'year'])[
        ['fft_amp', 'np_seasonal_strength']
    ].mean().reset_index()
    np_fld_yr = np_fld_yr.merge(stl_fld, on=['FLD_NM', 'year'], how='inner')
    corr_sub = np_fld_yr[['fft_amp', 'stl_seasonal_strength', 'np_seasonal_strength']].dropna()
    N_corr = len(corr_sub)
    print(f'  분야×연 평균 3-way 유효: {N_corr}')
    if N_corr >= 3:
        r_fft_np,  p_fft_np  = pearsonr(corr_sub['fft_amp'], corr_sub['np_seasonal_strength'])
        r_stl_np,  p_stl_np  = pearsonr(corr_sub['stl_seasonal_strength'], corr_sub['np_seasonal_strength'])
        r_fft_stl, p_fft_stl = pearsonr(corr_sub['fft_amp'], corr_sub['stl_seasonal_strength'])
    else:
        r_fft_np = r_stl_np = r_fft_stl = np.nan
        p_fft_np = p_stl_np = p_fft_stl = np.nan

corr_matrix = pd.DataFrame({
    'measure': ['FFT amp_12m_norm', 'STL seasonal_strength', 'NP seasonal_strength'],
    'r_vs_FFT':  [1.0, round(r_fft_stl, 4), round(r_fft_np, 4)],
    'r_vs_STL':  [round(r_fft_stl, 4), 1.0, round(r_stl_np, 4)],
    'r_vs_NP':   [round(r_fft_np, 4), round(r_stl_np, 4), 1.0],
    'p_vs_FFT':  [0.0, round(p_fft_stl, 4), round(p_fft_np, 4)],
    'p_vs_STL':  [round(p_fft_stl, 4), 0.0, round(p_stl_np, 4)],
    'p_vs_NP':   [round(p_fft_np, 4), round(p_stl_np, 4), 0.0],
})
corr_matrix.to_csv(os.path.join(RES, 'H26_neuralprophet_summary.csv'),
                   index=False, encoding='utf-8-sig')
print(f'  3-way 상관행렬 저장')

# ============================================================
# Step 6: 분야별 게임화-결과 상관 (3개 측도 비교)
# ============================================================
print('\nStep 6: 분야별 게임화-결과 상관 (FFT / STL / NP)')

# 분야×연 NP 평균
np_fld_yr_avg = np_merged.groupby(['FLD_NM', 'year'])['np_seasonal_strength'].mean().reset_index()

# STL 분야×연
stl_lookup = stl_fld.set_index(['FLD_NM', 'year'])['stl_seasonal_strength'].to_dict() \
    if len(stl_fld) > 0 else {}

# FFT 분야×연 (자체 계산 평균)
fft_fld_yr_avg = np_merged.groupby(['FLD_NM', 'year'])['fft_amp'].mean().reset_index()

h6_rows = []
N_PERM = 500

for fld, oc_metric in OUTCOME_MAP.items():
    if len(panel_wide) == 0:
        break
    if oc_metric not in panel_wide.columns:
        continue

    oc_ts = panel_wide[panel_wide['fld_nm'] == fld].set_index('year')[oc_metric].dropna()

    row = {'fld': fld, 'outcome': oc_metric}

    # --- NP ---
    np_ts_df = np_fld_yr_avg[np_fld_yr_avg['FLD_NM'] == fld].set_index('year')['np_seasonal_strength'].dropna()
    ci_np = np_ts_df.index.intersection(oc_ts.index)
    if len(ci_np) >= 4:
        d_np = np_ts_df.loc[ci_np].diff().dropna()
        d_oc = oc_ts.loc[ci_np].diff().dropna()
        ci2  = d_np.index.intersection(d_oc.index)
        if len(ci2) >= 3:
            r_np, _ = pearsonr(d_np.loc[ci2], d_oc.loc[ci2])
            null = np.array([
                pearsonr(d_np.loc[ci2].values, RNG.permutation(d_oc.loc[ci2].values))[0]
                for _ in range(N_PERM)
            ])
            p_np = float(((np.abs(null) >= np.abs(r_np)).sum() + 1) / (N_PERM + 1))
            row['corr_np'] = round(float(r_np), 4)
            row['pval_np'] = round(p_np, 4)
            row['n_np'] = len(ci2)
        else:
            row['corr_np'] = row['pval_np'] = row['n_np'] = np.nan
    else:
        row['corr_np'] = row['pval_np'] = row['n_np'] = np.nan

    # --- FFT (자체 계산 분야 평균) ---
    fft_ts_df = fft_fld_yr_avg[fft_fld_yr_avg['FLD_NM'] == fld].set_index('year')['fft_amp'].dropna()
    ci_fft = fft_ts_df.index.intersection(oc_ts.index)
    if len(ci_fft) >= 4:
        d_fft = fft_ts_df.loc[ci_fft].diff().dropna()
        d_oc2 = oc_ts.loc[ci_fft].diff().dropna()
        ci3   = d_fft.index.intersection(d_oc2.index)
        if len(ci3) >= 3:
            r_fft, _ = pearsonr(d_fft.loc[ci3], d_oc2.loc[ci3])
            null2 = np.array([
                pearsonr(d_fft.loc[ci3].values, RNG.permutation(d_oc2.loc[ci3].values))[0]
                for _ in range(N_PERM)
            ])
            p_fft = float(((np.abs(null2) >= np.abs(r_fft)).sum() + 1) / (N_PERM + 1))
            row['corr_fft'] = round(float(r_fft), 4)
            row['pval_fft'] = round(p_fft, 4)
        else:
            row['corr_fft'] = row['pval_fft'] = np.nan
    else:
        row['corr_fft'] = row['pval_fft'] = np.nan

    # --- STL (H24 기존) ---
    stl_ts = {yr: v for (f, yr), v in stl_lookup.items() if f == fld}
    if stl_ts:
        stl_series = pd.Series(stl_ts).dropna()
        ci_stl = stl_series.index.intersection(oc_ts.index)
        if len(ci_stl) >= 4:
            d_stl = stl_series.loc[ci_stl].diff().dropna()
            d_oc3 = oc_ts.loc[ci_stl].diff().dropna()
            ci4   = d_stl.index.intersection(d_oc3.index)
            if len(ci4) >= 3:
                r_stl, _ = pearsonr(d_stl.loc[ci4], d_oc3.loc[ci4])
                null3 = np.array([
                    pearsonr(d_stl.loc[ci4].values, RNG.permutation(d_oc3.loc[ci4].values))[0]
                    for _ in range(N_PERM)
                ])
                p_stl = float(((np.abs(null3) >= np.abs(r_stl)).sum() + 1) / (N_PERM + 1))
                row['corr_stl'] = round(float(r_stl), 4)
                row['pval_stl'] = round(p_stl, 4)
            else:
                row['corr_stl'] = row['pval_stl'] = np.nan
        else:
            row['corr_stl'] = row['pval_stl'] = np.nan
    else:
        row['corr_stl'] = row['pval_stl'] = np.nan

    h6_rows.append(row)
    print(f'  {fld:20s}: NP r={row.get("corr_np", np.nan):+.3f} '
          f'FFT r={row.get("corr_fft", np.nan):+.3f} '
          f'STL r={row.get("corr_stl", np.nan):+.3f}')

h6_df = pd.DataFrame(h6_rows)
h6_df.to_csv(os.path.join(RES, 'H26_field_outcome_corr_np.csv'),
             index=False, encoding='utf-8-sig')
print(f'\n  H26 분야-결과 상관 저장: {len(h6_df)} 분야')

# ============================================================
# Step 7: 그림 — 3-panel
# ============================================================
print('\nStep 7: 3-panel 그림 생성')

fig_w = 1800 / 130
fig_h = 600  / 130
fig, axes = plt.subplots(1, 3, figsize=(fig_w, fig_h))
plt.rcParams.update({'font.size': BASE_FONT})

# Panel 1: FFT vs NP scatter
ax = axes[0]
if N_corr >= 3:
    scatter_data = corr_sub.copy()
    # 분야별 색상 (상위 n개)
    fld_labels = np_merged.loc[
        np_merged.index.isin(corr_sub.index) if hasattr(corr_sub, 'index') else slice(None),
        'FLD_NM'
    ] if 'FLD_NM' in np_merged.columns else pd.Series(['?']*N_corr)

    ax.scatter(scatter_data['fft_amp'], scatter_data['np_seasonal_strength'],
               s=18, alpha=0.4, color='#4a7fc1', edgecolors='none')
    # 추세선
    try:
        z = np.polyfit(scatter_data['fft_amp'].dropna(),
                       scatter_data['np_seasonal_strength'].dropna(), 1)
        p_line = np.poly1d(z)
        x_range = np.linspace(scatter_data['fft_amp'].min(), scatter_data['fft_amp'].max(), 100)
        ax.plot(x_range, p_line(x_range), 'r-', lw=1.5, alpha=0.8)
    except Exception:
        pass
ax.set_xlabel('FFT amp_12m_norm', fontsize=BASE_FONT)
ax.set_ylabel('NP seasonal_strength', fontsize=BASE_FONT)
ax.set_title(f'FFT vs NP\n(r={r_fft_np:.3f}, N={N_corr})', fontsize=BASE_FONT)
ax.grid(alpha=0.3)
ax.tick_params(labelsize=BASE_FONT - 1)

# Panel 2: STL vs NP scatter
ax = axes[1]
if N_corr >= 3:
    ax.scatter(scatter_data['stl_seasonal_strength'], scatter_data['np_seasonal_strength'],
               s=18, alpha=0.4, color='#5ba85a', edgecolors='none')
    try:
        z2 = np.polyfit(scatter_data['stl_seasonal_strength'].dropna(),
                        scatter_data['np_seasonal_strength'].dropna(), 1)
        p2 = np.poly1d(z2)
        x2 = np.linspace(scatter_data['stl_seasonal_strength'].min(),
                          scatter_data['stl_seasonal_strength'].max(), 100)
        ax.plot(x2, p2(x2), 'r-', lw=1.5, alpha=0.8)
    except Exception:
        pass
ax.set_xlabel('STL seasonal_strength', fontsize=BASE_FONT)
ax.set_ylabel('NP seasonal_strength', fontsize=BASE_FONT)
ax.set_title(f'STL vs NP\n(r={r_stl_np:.3f}, N={N_corr})', fontsize=BASE_FONT)
ax.grid(alpha=0.3)
ax.tick_params(labelsize=BASE_FONT - 1)

# Panel 3: 14 분야 × 3 측도 상관 막대
ax = axes[2]
if len(h6_df) > 0:
    valid_h6 = h6_df.dropna(subset=['corr_np']).copy()
    if len(valid_h6) == 0:
        valid_h6 = h6_df.copy()
    valid_h6 = valid_h6.sort_values('corr_np', ascending=True)
    yy = np.arange(len(valid_h6))
    bw = 0.25

    bars_fft = ax.barh(yy - bw, valid_h6['corr_fft'].fillna(0), height=bw,
                       color='#4a7fc1', alpha=0.85, label='FFT amp_12m_norm')
    bars_stl = ax.barh(yy,       valid_h6['corr_stl'].fillna(0), height=bw,
                       color='#5ba85a', alpha=0.8, label='STL seasonal_str')
    bars_np  = ax.barh(yy + bw,  valid_h6['corr_np'].fillna(0),  height=bw,
                       color='#d35c37', alpha=0.85, label='NP seasonal_str')

    ax.set_yticks(yy)
    ax.set_yticklabels(valid_h6['fld'], fontsize=BASE_FONT - 2)
    ax.axvline(0, color='#666', lw=0.8, ls='-')
    ax.set_xlabel('Δ게임화 강도 ~ Δ결과 상관 (r)', fontsize=BASE_FONT - 1)
    ax.set_title('14 분야 × 3 측도\n게임화-결과 상관', fontsize=BASE_FONT)
    ax.legend(fontsize=BASE_FONT - 3, loc='lower right')
    ax.grid(alpha=0.3, axis='x')
    ax.tick_params(labelsize=BASE_FONT - 2)
    ax.set_xlim(-1.1, 1.1)

plt.suptitle('H26: NeuralProphet 게임화 강도 3-way 교차검증\n(FFT amp_12m_norm / STL seasonal_strength / NP seasonal_strength)',
             fontsize=BASE_FONT + 1, fontweight='bold', y=1.02)
plt.tight_layout()

fig_path = os.path.join(FIG_DIR, 'h26_neuralprophet.png')
fig.savefig(fig_path, dpi=130, bbox_inches='tight')
plt.close()
print(f'  그림 저장: {fig_path}')

# ============================================================
# Step 8: 최종 요약 출력
# ============================================================
print('\n' + '=' * 70)
print('H26 최종 요약')
print('=' * 70)

print(f'\n[샘플 크기]')
print(f'  NP fit 대상 활동-연도: {len(np_df):,}')
print(f'  3-way 상관 유효 N:    {N_corr:,}')

print(f'\n[3-way 상관행렬]')
hdr   = ""
col1  = "FFT amp_12m_norm"
col2  = "STL seasonal_strength"
col3  = "NP seasonal_strength"
print(f"  {hdr:30s}  FFT    STL    NP")
print(f"  {col1:30s}  1.000  {r_fft_stl:+.3f}  {r_fft_np:+.3f}")
print(f"  {col2:30s}  {r_fft_stl:+.3f}  1.000  {r_stl_np:+.3f}")
print(f"  {col3:30s}  {r_fft_np:+.3f}  {r_stl_np:+.3f}  1.000")
print(f'\n  FFT–NP:  r={r_fft_np:.3f}  (p={p_fft_np:.4f})')
print(f'  STL–NP:  r={r_stl_np:.3f}  (p={p_stl_np:.4f})')
print(f'  FFT–STL: r={r_fft_stl:.3f}  (p={p_fft_stl:.4f})')

print(f'\n[분야별 게임화-결과 상관 요약]')
if len(h6_df) > 0:
    print(h6_df[['fld', 'outcome', 'corr_fft', 'corr_stl', 'corr_np',
                  'pval_fft', 'pval_stl', 'pval_np']].to_string(index=False))

print(f'\n[사회복지 세부]')
sw = h6_df[h6_df['fld'] == '사회복지'] if len(h6_df) > 0 else pd.DataFrame()
if len(sw) > 0:
    r = sw.iloc[0]
    fft_v = r.get('corr_fft', np.nan)
    stl_v = r.get('corr_stl', np.nan)
    np_v  = r.get('corr_np', np.nan)
    fft_p = r.get('pval_fft', np.nan)
    stl_p = r.get('pval_stl', np.nan)
    np_p  = r.get('pval_np', np.nan)
    print(f'  FFT: r={fft_v:+.3f} (p={fft_p:.3f})')
    print(f'  STL: r={stl_v:+.3f} (p={stl_p:.3f})')
    print(f'  NP:  r={np_v:+.3f}  (p={np_p:.3f})')

    # 부호 일관성
    signs = [np.sign(v) for v in [fft_v, stl_v, np_v] if not np.isnan(v)]
    agree = len(set(signs)) == 1
    dominant = '일치' if agree else '불일치'
    print(f'  3개 측도 부호: {dominant} ({["FFT","STL","NP"]} = {[round(v,3) for v in [fft_v,stl_v,np_v]]})')

    print(f'''
[해석]
  사회복지 분야에서 FFT r={fft_v:+.3f}, STL r={stl_v:+.3f}, NP r={np_v:+.3f}로,
  세 측도의 부호가 {"모두 일치" if agree else "일치하지 않아"} {"NP가 FFT/STL과 동일한 방향을 지지한다" if agree else "측도 간 결과가 상이하다"}.
  3-way 상관에서 FFT-NP r={r_fft_np:.3f}, STL-NP r={r_stl_np:.3f}로,
  NP는 {"FFT에 더 가깝다" if abs(r_fft_np) > abs(r_stl_np) else "STL에 더 가깝다" if abs(r_stl_np) > abs(r_fft_np) else "FFT·STL과 유사한 수준의 일치도를 보인다"}.
  즉 NP 기반 측도는 기존 FFT·STL 측도의 게임화 신호를 {"재확인한다" if agree else "일부 다른 각도에서 포착한다"}.
''')
else:
    print('  사회복지 데이터 없음')

print('[출력 파일]')
print(f'  {os.path.join(RES, "H26_neuralprophet_summary.csv")}')
print(f'  {os.path.join(RES, "H26_field_outcome_corr_np.csv")}')
print(f'  {fig_path}')
print('\n완료 (H26 NeuralProphet 교차검증).')
