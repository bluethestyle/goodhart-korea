"""Slide 29 NeuralProphet forecasting — 4 archetype 11년 학습 + 12개월 미래 예측.

AR-Net(n_lags=12) 포함 spec으로 각 archetype 학습 후 다음 1년(2026) forecast.
Slide 28 scaleogram과 동일 layout (2×2 grid, 출연금형 좌하 강조).

n_forecasts=12 — NP multi-step의 가장 안정적인 horizon.

출력:
  paper/figures/h29_np_forecast.png  — 4 archetype 2×2 grid, 1280×550
"""
import sys
import io
import pickle
import warnings
import numpy as np
import pandas as pd
import duckdb
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
warnings.filterwarnings('ignore')

# ── 폰트 ─────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
font_path = ROOT / 'paper' / 'fonts' / 'Pretendard-Regular.otf'
if font_path.exists():
    fm.fontManager.addfont(str(font_path))
    plt.rcParams['font.family'] = 'Pretendard'
plt.rcParams['axes.unicode_minus'] = False

# ── 상수 ─────────────────────────────────────────────────────────────
DB_PATH  = ROOT / 'data' / 'warehouse.duckdb'
EMB_PATH = ROOT / 'data' / 'results' / 'H3_activity_embedding_11y.csv'
OUT_PATH   = ROOT / 'paper' / 'figures' / 'h29_np_forecast.png'
CACHE_PATH = ROOT / 'data' / 'results' / 'h29_np_forecasts_cache.pkl'

N_FORECAST = 12

# Slide 28 scaleogram 동일 layout: C0 좌상 / C1 우상 / C2 좌하 / C3 우하
LAYOUT = {
    'C0': {'pos': (0, 0), 'color': '#888888', 'label': '인건비형',   'lw_fc': 1.8, 'emphasis': False},
    'C1': {'pos': (0, 1), 'color': '#C0392B', 'label': '자산취득형', 'lw_fc': 2.2, 'emphasis': False},
    'C2': {'pos': (1, 0), 'color': '#E67E22', 'label': '출연금형',   'lw_fc': 2.8, 'emphasis': True},
    'C3': {'pos': (1, 1), 'color': '#9B9B9B', 'label': '정상사업',   'lw_fc': 2.2, 'emphasis': False},
}
ARCHETYPE_KEYS = ['C0', 'C1', 'C2', 'C3']


# ──────────────────────────────────────────────────────────────────────
def load_archetype_ts():
    """4 archetype 월별 정규화 시계열."""
    emb = pd.read_csv(EMB_PATH, encoding='utf-8')
    con = duckdb.connect(str(DB_PATH), read_only=True)

    result = {}
    idx = pd.date_range('2015-01', periods=132, freq='MS')

    for cid, key in enumerate(ARCHETYPE_KEYS):
        actv_list = emb[emb['cluster'] == cid]['ACTV_NM'].tolist()
        n_actv = len(actv_list)

        actv_df = pd.DataFrame({'ACTV_NM': actv_list})
        con.register('actv_tmp', actv_df)
        ts_df = con.execute("""
            SELECT FSCL_YY AS yr, EXE_M AS mo, SUM(EP_AMT) AS ep
            FROM monthly_exec m JOIN actv_tmp a ON m.ACTV_NM = a.ACTV_NM
            WHERE m.FSCL_YY BETWEEN 2015 AND 2025
              AND m.EXE_M BETWEEN 1 AND 12
            GROUP BY 1, 2 ORDER BY 1, 2
        """).fetchdf()
        con.unregister('actv_tmp')

        ts_df['date'] = pd.to_datetime(
            ts_df['yr'].astype(str) + '-' + ts_df['mo'].astype(str).str.zfill(2)
        )
        ser = ts_df.set_index('date')['ep'].reindex(idx).interpolate(
            'linear', limit_direction='both'
        )
        ser = ser / n_actv
        ser = (ser - ser.min()) / (ser.max() - ser.min() + 1e-9)
        result[key] = ser
        print(f'  [{key}] {LAYOUT[key]["label"]}: n_actv={n_actv}, '
              f'mean={ser.mean():.4f}')

    con.close()
    return result


# ──────────────────────────────────────────────────────────────────────
def fit_forecast(ser, key):
    """AR-Net 포함 NP 학습 + 12개월 forecast."""
    from neuralprophet import NeuralProphet, set_log_level
    set_log_level('ERROR')

    df_np = pd.DataFrame({'ds': ser.index, 'y': ser.values})

    m = NeuralProphet(
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False,
        n_changepoints=10,
        changepoints_range=0.85,
        seasonality_mode='additive',
        n_lags=12,
        n_forecasts=N_FORECAST,
        ar_layers=[],
        epochs=300,
        learning_rate=0.01,
        quantiles=[0.05, 0.95],
    )

    print(f'  [{key}] Fitting NP forecast ...', flush=True)
    metrics = m.fit(df_np, freq='MS', progress='none')

    future = m.make_future_dataframe(df_np, periods=N_FORECAST,
                                     n_historic_predictions=True)
    forecast = m.predict(future)

    # extract forecast: future row i → ds = origin + i+1, yhat_{i+1}
    fut = forecast[forecast['y'].isna()].copy().reset_index(drop=True)
    fut_ds = fut['ds'].values
    fut_mean = np.full(len(fut), np.nan)
    fut_lo = np.full(len(fut), np.nan)
    fut_hi = np.full(len(fut), np.nan)
    for i in range(len(fut)):
        step = i + 1
        if f'yhat{step}' in fut.columns:
            fut_mean[i] = fut.iloc[i][f'yhat{step}']
        if f'yhat{step} 5.0%' in fut.columns:
            fut_lo[i] = fut.iloc[i][f'yhat{step} 5.0%']
        if f'yhat{step} 95.0%' in fut.columns:
            fut_hi[i] = fut.iloc[i][f'yhat{step} 95.0%']

    mae = float(metrics['MAE'].iloc[-1])
    rmse = float(metrics['RMSE'].iloc[-1])
    print(f'    MAE {mae:.4f} · RMSE {rmse:.4f}')

    return {
        'fut_ds': fut_ds, 'fut_mean': fut_mean,
        'fut_lo': fut_lo, 'fut_hi': fut_hi,
        'mae': mae, 'rmse': rmse,
    }


# ──────────────────────────────────────────────────────────────────────
def plot_panel(ax, ser, fc, layout, key, ylim=(0.0, 1.05)):
    color = layout['color']
    label = layout['label']
    lw_fc = layout['lw_fc']
    emphasis = layout['emphasis']

    # 학습/예측 경계 우측 영역 음영 (forecast 가시성 강화 — 진한 음영)
    boundary = pd.Timestamp('2025-12-15')
    fut_end = pd.Timestamp('2026-12-31')
    ax.axvspan(boundary, fut_end, color=color, alpha=0.14, zorder=0)

    # 실측 (검정 얇게)
    ax.plot(ser.index, ser.values, color='#222', lw=1.0, zorder=3,
            label='실측' if key == 'C0' else None)

    # CI band (forecast line 아래)
    valid_ci = ~np.isnan(fc['fut_lo']) & ~np.isnan(fc['fut_hi'])
    if valid_ci.any():
        ax.fill_between(
            np.array(fc['fut_ds'])[valid_ci],
            fc['fut_lo'][valid_ci], fc['fut_hi'][valid_ci],
            color=color, alpha=0.32, zorder=2,
            label='90% CI' if key == 'C0' else None,
        )

    # forecast central — 굵게, 가시성 강화
    ax.plot(fc['fut_ds'], fc['fut_mean'], color=color, lw=lw_fc + 0.8, zorder=5,
            label='예측 (2026)' if key == 'C0' else None)

    # 학습/예측 경계 점선
    ax.axvline(boundary, color='#444', lw=1.0, linestyle=':', zorder=4)

    # forecast 12월 dot
    fut_ds_pd = pd.to_datetime(fc['fut_ds'])
    dec_mask = fut_ds_pd.month == 12
    fut_dec_vals = fc['fut_mean'][dec_mask]
    fut_dec_vals = fut_dec_vals[~np.isnan(fut_dec_vals)]
    next_dec_pred = fut_dec_vals[0] if len(fut_dec_vals) > 0 else np.nan
    if not np.isnan(next_dec_pred):
        dec_ds = fut_ds_pd[dec_mask][0]
        ax.scatter([dec_ds], [next_dec_pred], s=110, color=color,
                  edgecolor='white', linewidth=2.0, zorder=7)

    # 축 설정
    ax.set_xlim(pd.Timestamp('2015-01'), pd.Timestamp('2027-01'))
    ax.set_ylim(*ylim)
    ax.set_xticks([pd.Timestamp(f'{y}-01-01') for y in [2016, 2020, 2024]])
    ax.set_xticklabels(['2016', '2020', '2024'], fontsize=11)
    ax.set_yticks([0, 0.5, 1.0])
    ax.set_yticklabels(['0', '0.5', '1.0'], fontsize=11)
    ax.grid(True, alpha=0.25, linestyle=':', zorder=1)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # 강조 panel: 굵은 border + title 색 강조
    if emphasis:
        for spine in ['left', 'bottom']:
            ax.spines[spine].set_linewidth(3.0)
            ax.spines[spine].set_color(color)
        title_color = color
        title_wt = 'bold'
        star = '  ★'
    else:
        title_color = '#222'
        title_wt = 'bold'
        star = ''

    # panel title + KPI — 외부 (그래프 위, transform=ax.transAxes)
    last_dec = ser[ser.index.month == 12].iloc[-1] if (ser.index.month == 12).any() else np.nan
    ratio = next_dec_pred / last_dec if (not np.isnan(next_dec_pred) and last_dec > 0) else np.nan
    title_txt = f'{key}  {label}{star}'
    kpi_txt = (f'2025 실측 {last_dec:.2f}   →   2026 예측 {next_dec_pred:.2f}'
               f'   ({"×%.2f" % ratio})' if not np.isnan(ratio)
               else f'2026 예측 {next_dec_pred:.2f}')
    ax.text(0.0, 1.20, title_txt, transform=ax.transAxes, fontsize=14,
            fontweight=title_wt, color=title_color, va='bottom')
    ax.text(0.0, 1.04, kpi_txt, transform=ax.transAxes, fontsize=11,
            color='#444', va='bottom')


# ──────────────────────────────────────────────────────────────────────
def main():
    # 캐시 로드 또는 학습
    if CACHE_PATH.exists():
        print(f'  Loading cache: {CACHE_PATH}')
        with open(CACHE_PATH, 'rb') as f:
            cache = pickle.load(f)
        series   = cache['series']
        forecasts = cache['forecasts']
    else:
        series = load_archetype_ts()
        forecasts = {}
        for key in ARCHETYPE_KEYS:
            forecasts[key] = fit_forecast(series[key], key)
        CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(CACHE_PATH, 'wb') as f:
            pickle.dump({'series': series, 'forecasts': forecasts}, f)
        print(f'  Cache saved: {CACHE_PATH}')

    # 시각화 — 1280×620 보장
    fig, axes = plt.subplots(2, 2, figsize=(12.8, 6.2), dpi=100,
                             gridspec_kw={'hspace': 0.95, 'wspace': 0.16,
                                          'left': 0.05, 'right': 0.98,
                                          'top': 0.85, 'bottom': 0.10})

    for key in ARCHETYPE_KEYS:
        r, c = LAYOUT[key]['pos']
        plot_panel(axes[r, c], series[key], forecasts[key], LAYOUT[key], key)

    # 전체 figure title (충분한 위 공간)
    fig.suptitle(
        '4 체질의 NeuralProphet forecasting — 각 체질이 자기 박자를 다음 해에도 유지',
        fontsize=15, fontweight='bold', y=0.965,
    )

    # legend 대신 footer 한 줄 — gridspec 밖에서 안 겹침
    fig.text(0.5, 0.025,
             '검정 실측 (2015–2025)   ·   색깔 line 예측 (2026, AR-Net 포함)   ·   음영 90% CI',
             ha='center', va='bottom', fontsize=10, color='#555')

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(OUT_PATH, dpi=100, facecolor='white')
    plt.close()

    # 결과 보고
    im_h = OUT_PATH
    from PIL import Image
    print(f'\n  Saved: {OUT_PATH}')
    print(f'  Size:  {Image.open(OUT_PATH).size}')

    print(f'\n=== KPI ===')
    for key in ARCHETYPE_KEYS:
        ser = series[key]
        fc = forecasts[key]
        last_dec = ser[ser.index.month == 12].iloc[-1]
        fut_ds_pd = pd.to_datetime(fc['fut_ds'])
        dec_mask = fut_ds_pd.month == 12
        next_dec = fc['fut_mean'][dec_mask][~np.isnan(fc['fut_mean'][dec_mask])]
        next_dec_v = next_dec[0] if len(next_dec) > 0 else np.nan
        ratio = next_dec_v / last_dec if last_dec > 0 else np.nan
        print(f'  [{key}] {LAYOUT[key]["label"]:8s}  '
              f'2025 실측 {last_dec:.4f}  →  2026 예측 {next_dec_v:.4f}  '
              f'(×{ratio:.2f})  MAE {fc["mae"]:.3f}')


if __name__ == '__main__':
    main()
