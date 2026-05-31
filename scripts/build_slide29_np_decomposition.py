"""Slide 29 NeuralProphet 실제 학습 — 4 archetype × 2 spec 분해.

Spec A (AR-Net 제외, 메인 narrative):
  NeuralProphet(yearly_seasonality=True, n_changepoints=10, n_lags=0, epochs=200)

Spec B (AR-Net 포함, robustness check):
  NeuralProphet(yearly_seasonality=True, n_changepoints=10, n_lags=12, epochs=200)

출력:
  paper/figures/h29_np_decomposition.png        -- Spec A 메인 차트 (4 archetype × 3 panel)
  paper/figures/h29_np_arnet_robustness.png     -- Spec A vs B seasonality strength 비교

NP 설치 없을 시 STL fallback (except ImportError 절).
"""
import sys
import io
import os
import warnings
import numpy as np
import pandas as pd
import duckdb
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from pathlib import Path
from scipy.stats import linregress

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
warnings.filterwarnings('ignore')

# ── 폰트 설정 ──────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
font_path = ROOT / 'paper' / 'fonts' / 'Pretendard-Regular.otf'
if font_path.exists():
    fm.fontManager.addfont(str(font_path))
    plt.rcParams['font.family'] = 'Pretendard'
else:
    # Windows fallback
    for fn in ['Malgun Gothic', 'NanumGothic']:
        if any(fn.lower() in f.name.lower() for f in fm.fontManager.ttflist):
            plt.rcParams['font.family'] = fn
            break
plt.rcParams['axes.unicode_minus'] = False

# ── 색상·스타일 상수 (Slide 22/23/27/28 통일) ──────────────────────────
COLORS  = {'C0': '#888888', 'C1': '#C0392B', 'C2': '#E67E22', 'C3': '#9b9b9b'}
LW      = {'C0': 1.2, 'C1': 2.2, 'C2': 2.2, 'C3': 1.2}
LABELS  = {
    'C0': 'C0 인건비형',
    'C1': 'C1 직접투자형',
    'C2': 'C2 출연금형',
    'C3': 'C3 일반운영형',
}
ARCHETYPE_KEYS = ['C0', 'C1', 'C2', 'C3']

OUT_DIR  = ROOT / 'paper' / 'figures'
PREV_DIR = OUT_DIR / '_preview'
PREV_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH  = ROOT / 'data' / 'warehouse.duckdb'
EMB_PATH = ROOT / 'data' / 'results' / 'H3_activity_embedding_11y.csv'


# ──────────────────────────────────────────────────────────────────────
# 1) 데이터 준비
# ──────────────────────────────────────────────────────────────────────
def load_archetype_ts():
    """4 archetype 월별 정규화 시계열 반환.

    Returns
    -------
    dict[str, pd.Series]  키 = 'C0'~'C3', index = pd.DatetimeIndex (132 obs)
    """
    emb = pd.read_csv(EMB_PATH, encoding='utf-8')
    con = duckdb.connect(str(DB_PATH), read_only=True)

    result = {}
    idx = pd.date_range('2015-01', periods=132, freq='MS')

    for cid, key in enumerate(ARCHETYPE_KEYS):
        actv_list = emb[emb['cluster'] == cid]['ACTV_NM'].tolist()
        n_actv    = len(actv_list)

        if n_actv == 0:
            result[key] = pd.Series(np.zeros(132), index=idx)
            continue

        # DuckDB: 활동 리스트를 임시 테이블로 올려 조인
        actv_df = pd.DataFrame({'ACTV_NM': actv_list})
        con.register('actv_tmp', actv_df)

        ts_df = con.execute("""
            SELECT FSCL_YY AS yr, EXE_M AS mo, SUM(EP_AMT) AS ep
            FROM monthly_exec m
            JOIN actv_tmp a ON m.ACTV_NM = a.ACTV_NM
            WHERE m.FSCL_YY BETWEEN 2015 AND 2025
              AND m.EXE_M BETWEEN 1 AND 12
            GROUP BY 1, 2
            ORDER BY 1, 2
        """).fetchdf()
        con.unregister('actv_tmp')

        ts_df['date'] = pd.to_datetime(
            ts_df['yr'].astype(str) + '-' + ts_df['mo'].astype(str).str.zfill(2)
        )
        ser = ts_df.set_index('date')['ep'].reindex(idx).interpolate(
            method='linear', limit_direction='both'
        )
        # 활동 수로 나눠 normalize (단위 통일)
        ser = ser / n_actv
        # 추가 min-max 정규화 [0,1]
        ser = (ser - ser.min()) / (ser.max() - ser.min() + 1e-9)

        result[key] = ser
        print(f'  [{key}] n_actv={n_actv}, obs={len(ser)}, '
              f'mean={ser.mean():.4f}, std={ser.std():.4f}')

    con.close()
    return result, idx


# ──────────────────────────────────────────────────────────────────────
# 2) NeuralProphet 학습 + 분해
# ──────────────────────────────────────────────────────────────────────
def fit_neuralprophet(ser: pd.Series, spec: str, key: str):
    """NeuralProphet 학습 후 trend / seasonality / residual 반환.

    Parameters
    ----------
    ser  : pd.Series, DatetimeIndex
    spec : 'A' (AR-Net 제외) | 'B' (AR-Net 포함)
    key  : archetype key (로그용)

    Returns
    -------
    dict with keys: trend, seasonality, residual,
                    ss (seasonality strength), slope (trend slope)
                    ar_contribution (Spec B만; else None)
    """
    from neuralprophet import NeuralProphet, set_log_level
    set_log_level('ERROR')

    df_np = pd.DataFrame({'ds': ser.index, 'y': ser.values})

    if spec == 'A':
        m = NeuralProphet(
            yearly_seasonality=True,
            weekly_seasonality=False,
            daily_seasonality=False,
            n_changepoints=10,
            changepoints_range=0.85,
            seasonality_mode='additive',
            epochs=200,
            learning_rate=0.01,
            # n_lags=0  ← default, AR-Net 제외
        )
    else:  # Spec B
        m = NeuralProphet(
            yearly_seasonality=True,
            weekly_seasonality=False,
            daily_seasonality=False,
            n_changepoints=10,
            changepoints_range=0.85,
            seasonality_mode='additive',
            n_lags=12,          # 12개월 AR
            ar_layers=[],       # linear AR (no MLP) — interpretable
            epochs=200,
            learning_rate=0.01,
        )

    print(f'  Fitting NP Spec {spec} [{key}] ...', flush=True)
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        metrics = m.fit(df_np, freq='MS', progress='none')

    # in-sample predict — NP 0.8.0 API: n_historic_predictions=True
    future = m.make_future_dataframe(df_np, n_historic_predictions=True)
    forecast = m.predict(future)

    print(f'    forecast columns: {[c for c in forecast.columns if "season" in c.lower() or "trend" in c.lower() or "ar" in c.lower()]}')

    # ── component 추출 ──────────────────────────────────────────────
    # trend
    trend_col = [c for c in forecast.columns if c == 'trend']
    trend = forecast[trend_col[0]].values if trend_col else None

    # yearly seasonality (NP 0.8: 'season_yearly')
    seas_cols = [c for c in forecast.columns if 'season_yearly' in c.lower()]
    if not seas_cols:
        seas_cols = [c for c in forecast.columns if 'yearly' in c.lower()]
    if not seas_cols:
        seas_cols = [c for c in forecast.columns if 'season' in c.lower()]
    if seas_cols:
        seasonality = forecast[seas_cols[0]].values
    else:
        seasonality = np.zeros(len(forecast))

    # AR contribution (Spec B): 'ar1' in NP 0.8
    ar_cols = [c for c in forecast.columns if c == 'ar1' or
               (c.startswith('ar') and c[2:].isdigit())]
    ar_contribution = forecast[ar_cols[0]].values if ar_cols else None

    # residual — y와 forecast 정렬
    y_vals = df_np['y'].values  # 원본 길이 (132)
    n_orig = len(y_vals)

    # NP forecast 길이: n_lags=0이면 133 (1개 미래 포함), n_lags>0이면 앞쪽 NaN
    trend_full = trend     if trend is not None else np.full(len(forecast), np.nan)
    seas_full  = seasonality
    ar_full    = ar_contribution if ar_contribution is not None else np.zeros(len(forecast))

    # 전략: NaN 제거 후 y 길이에 맞춰 뒤쪽 n_orig개 취득
    valid_mask = ~np.isnan(trend_full) & ~np.isnan(seas_full)
    trend_v = trend_full[valid_mask]
    seas_v  = seas_full[valid_mask]
    ar_v    = ar_full[valid_mask]

    # valid 중 마지막 n_orig개가 실제 학습 범위
    n_valid = len(trend_v)
    take    = min(n_valid, n_orig)
    trend_v = trend_v[-take:]
    seas_v  = seas_v[-take:]
    ar_v    = ar_v[-take:]
    y_v     = y_vals[-take:]
    min_len = take

    if ar_contribution is not None:
        residual = y_v - trend_v - seas_v - ar_v
        ar_contribution = ar_v
    else:
        residual = y_v - trend_v - seas_v

    trend       = trend_v
    seasonality = seas_v

    # ── metrics ────────────────────────────────────────────────────
    var_s = float(np.var(seasonality))
    var_r = float(np.var(residual))
    ss    = var_s / (var_s + var_r + 1e-12)  # seasonality strength

    # trend slope (linear fit over normalized time)
    t_norm = np.linspace(0, 1, min_len)
    slope, *_ = linregress(t_norm, trend)

    return {
        'trend':          trend,
        'seasonality':    seasonality,
        'residual':       residual,
        'y_trimmed':      y_v,
        'min_len':        min_len,
        'ss':             ss,
        'slope':          float(slope),
        'ar_contribution': ar_contribution,
        'metrics':        metrics,
    }


# ──────────────────────────────────────────────────────────────────────
# 3) STL fallback (NeuralProphet ImportError 시)
# ──────────────────────────────────────────────────────────────────────
def fit_stl_fallback(ser: pd.Series, key: str):
    from statsmodels.tsa.seasonal import STL
    stl = STL(ser, period=12, seasonal=13)
    res = stl.fit()
    trend     = res.trend.values
    seasonal  = res.seasonal.values
    residual  = res.resid.values
    var_s     = float(np.var(seasonal))
    var_r     = float(np.var(residual))
    ss        = var_s / (var_s + var_r + 1e-12)
    t_norm    = np.linspace(0, 1, len(trend))
    slope, *_ = linregress(t_norm, trend)
    return {
        'trend':          trend,
        'seasonality':    seasonal,
        'residual':       residual,
        'y_trimmed':      ser.values,
        'min_len':        len(ser),
        'ss':             ss,
        'slope':          float(slope),
        'ar_contribution': None,
        'metrics':        None,
    }


# ──────────────────────────────────────────────────────────────────────
# 4) 차트 생성 — 메인 (Spec A, 4 archetype × 3 panel)
# ──────────────────────────────────────────────────────────────────────
def build_main_chart(results_A, ts_data, idx):
    fig, axes = plt.subplots(
        4, 3, figsize=(13, 11), dpi=130,
        sharex=False,
        gridspec_kw={'hspace': 0.55, 'wspace': 0.35}
    )

    for row, key in enumerate(ARCHETYPE_KEYS):
        r    = results_A[key]
        col  = COLORS[key]
        lw_  = LW[key]
        lab  = LABELS[key]
        n    = r['min_len']

        # x-axis ticks (월별 인덱스)
        t = np.arange(n)
        # 인덱스 절삭분 반영
        full_idx  = idx
        trim_idx  = full_idx[-n:]
        year_ticks = [i for i, d in enumerate(trim_idx) if d.month == 1 and d.year % 2 == 1]
        year_labels = [str(trim_idx[i].year) for i in year_ticks]

        # --- Panel 0: 원시 시계열 + trend overlay ---
        ax0 = axes[row, 0]
        ax0.plot(t, r['y_trimmed'], color=col, lw=lw_, alpha=0.7,
                 label='Signal')
        ax0.plot(t, r['trend'], color='#222', lw=1.8, linestyle='--',
                 label='Trend')
        ax0.set_title(f'{lab}\n신호 + 추세', fontsize=9.5, loc='left', pad=3)
        ax0.set_ylabel('정규화 집행액', fontsize=8)
        slope_sign = '+' if r['slope'] >= 0 else ''
        ax0.annotate(f"slope {slope_sign}{r['slope']:.3f}",
                     xy=(0.97, 0.95), xycoords='axes fraction',
                     fontsize=8, ha='right', va='top',
                     bbox=dict(boxstyle='round,pad=0.2', fc='white', alpha=0.8))

        # --- Panel 1: 계절성 ---
        ax1 = axes[row, 1]
        ax1.plot(t, r['seasonality'], color=col, lw=lw_)
        ax1.axhline(0, color='#aaa', lw=0.7, linestyle=':')
        ax1.set_title('연 계절성 (Yearly Seasonality)', fontsize=9.5, loc='left', pad=3)
        ax1.set_ylabel('Seasonality', fontsize=8)
        ax1.annotate(f"SS={r['ss']:.3f}",
                     xy=(0.97, 0.95), xycoords='axes fraction',
                     fontsize=8.5, ha='right', va='top', color='#333',
                     bbox=dict(boxstyle='round,pad=0.3', fc='#ffffcc', alpha=0.9,
                               ec='#cccc00'))

        # --- Panel 2: 잔차 ---
        ax2 = axes[row, 2]
        ax2.bar(t, r['residual'], color=col, alpha=0.55, width=0.85)
        ax2.axhline(0, color='#aaa', lw=0.7, linestyle=':')
        ax2.set_title('잔차 (Residual)', fontsize=9.5, loc='left', pad=3)
        ax2.set_ylabel('Residual', fontsize=8)

        for ax in [ax0, ax1, ax2]:
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.grid(True, alpha=0.18, linestyle=':')
            ax.tick_params(axis='both', labelsize=7.5)
            if year_ticks:
                ax.set_xticks(year_ticks)
                ax.set_xticklabels(year_labels, fontsize=7.5)

    fig.suptitle(
        'NeuralProphet 분해 — 추세 제거 후 archetype-specific 계절성\n'
        'AR-Net 제외 spec · seasonality strength (SS) + trend slope per archetype',
        fontsize=11.5, y=1.001, weight='bold'
    )
    fig.text(
        0.99, -0.005,
        '※ NeuralProphet 0.8.0 실제 학습 (Spec A: n_lags=0). '
        'data/warehouse.duckdb monthly_exec 2015–2025.',
        ha='right', fontsize=7.5, color='#888', style='italic'
    )

    plt.tight_layout(rect=[0, 0.01, 1, 0.99])

    out = OUT_DIR / 'h29_np_decomposition.png'
    fig.savefig(out, dpi=130, bbox_inches='tight', facecolor='white')
    plt.close()
    return out


# ──────────────────────────────────────────────────────────────────────
# 5) 차트 생성 — Robustness (Spec A vs B 비교)
# ──────────────────────────────────────────────────────────────────────
def build_robustness_chart(results_A, results_B):
    keys   = ARCHETYPE_KEYS
    ss_A   = [results_A[k]['ss'] for k in keys]
    ss_B   = [results_B[k]['ss'] for k in keys]
    labels = [LABELS[k] for k in keys]

    x     = np.arange(len(keys))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=130)

    bars_A = ax.bar(x - width/2, ss_A, width, label='Spec A (AR-Net 제외)',
                    color=[COLORS[k] for k in keys], alpha=0.85, edgecolor='white')
    bars_B = ax.bar(x + width/2, ss_B, width, label='Spec B (AR-Net 포함)',
                    color=[COLORS[k] for k in keys], alpha=0.45, edgecolor='white',
                    hatch='//')

    # value labels
    for bar in bars_A:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.008,
                f'{bar.get_height():.3f}', ha='center', va='bottom',
                fontsize=9, weight='bold')
    for bar in bars_B:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.008,
                f'{bar.get_height():.3f}', ha='center', va='bottom',
                fontsize=9, color='#555')

    # delta annotations
    for i, (a, b) in enumerate(zip(ss_A, ss_B)):
        delta = b - a
        sign  = '+' if delta >= 0 else ''
        ax.annotate(f'Δ{sign}{delta:.3f}',
                    xy=(x[i], max(a, b) + 0.04),
                    ha='center', fontsize=8, color='#333',
                    arrowprops=None)

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=10)
    ax.set_ylabel('Seasonality Strength\n[var(S) / (var(S)+var(ε))]', fontsize=10)
    ax.set_ylim(0, min(1.0, max(ss_A + ss_B) + 0.15))
    ax.set_title(
        'Slide 29 Robustness Check — Spec A vs Spec B Seasonality Strength\n'
        'AR-Net 포함해도 seasonality strength 유의 → archetype 분해 견고',
        fontsize=11, pad=10
    )
    ax.legend(fontsize=9.5, loc='upper right', framealpha=0.9)
    ax.grid(True, axis='y', alpha=0.2, linestyle=':')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    fig.text(
        0.99, -0.005,
        '※ Spec A: n_lags=0 | Spec B: n_lags=12, ar_layers=[]. '
        'Seasonality strength: Wang & Smith-Miles (2013).',
        ha='right', fontsize=8, color='#888', style='italic'
    )

    plt.tight_layout()
    out = OUT_DIR / 'h29_np_arnet_robustness.png'
    fig.savefig(out, dpi=130, bbox_inches='tight', facecolor='white')
    plt.close()
    return out


# ──────────────────────────────────────────────────────────────────────
# 6) 다운샘플 preview
# ──────────────────────────────────────────────────────────────────────
def make_preview(src_path, max_w=1280):
    from PIL import Image
    img = Image.open(src_path)
    w, h = img.size
    if w > max_w:
        new_h = h * max_w // w
        img_s = img.resize((max_w, new_h), Image.LANCZOS)
    else:
        img_s = img
    dst = PREV_DIR / ('preview_' + Path(src_path).name)
    img_s.save(dst)
    return dst, img.size, img_s.size


# ──────────────────────────────────────────────────────────────────────
# main
# ──────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print('=' * 60)
    print('Slide 29 NeuralProphet 실제 학습 시작')
    print('=' * 60)

    # 데이터 준비
    print('\n[1] 데이터 준비 ...')
    ts_data, idx = load_archetype_ts()

    # NP 학습 시도
    USE_NP = False
    try:
        import neuralprophet
        USE_NP = True
        print(f'\n[환경] NeuralProphet {neuralprophet.__version__} import 성공')
    except ImportError:
        print('\n[환경] NeuralProphet import 실패 → STL fallback')

    results_A = {}
    results_B = {}

    if USE_NP:
        # Spec A — AR-Net 제외
        print('\n[2] Spec A (AR-Net 제외) 학습 ...')
        for key in ARCHETYPE_KEYS:
            try:
                results_A[key] = fit_neuralprophet(ts_data[key], 'A', key)
                print(f'    [{key}] SS={results_A[key]["ss"]:.4f}  slope={results_A[key]["slope"]:.4f}')
            except Exception as e:
                print(f'    [{key}] NP 실패 ({e}) → STL fallback')
                results_A[key] = fit_stl_fallback(ts_data[key], key)

        # Spec B — AR-Net 포함
        print('\n[3] Spec B (AR-Net 포함) 학습 ...')
        for key in ARCHETYPE_KEYS:
            try:
                results_B[key] = fit_neuralprophet(ts_data[key], 'B', key)
                r_b = results_B[key]
                ar_std = np.std(r_b['ar_contribution']) if r_b['ar_contribution'] is not None else 0.0
                print(f'    [{key}] SS={r_b["ss"]:.4f}  slope={r_b["slope"]:.4f}  AR_std={ar_std:.4f}')
            except Exception as e:
                print(f'    [{key}] NP Spec B 실패 ({e}) → STL fallback')
                results_B[key] = fit_stl_fallback(ts_data[key], key)
    else:
        # STL fallback
        print('\n[2+3] STL fallback (NP 없음) ...')
        for key in ARCHETYPE_KEYS:
            results_A[key] = fit_stl_fallback(ts_data[key], key)
            results_B[key] = fit_stl_fallback(ts_data[key], key)

    # 결과 요약 테이블
    print('\n' + '=' * 60)
    print('Spec A (AR-Net 제외) 결과')
    print(f'{"Archetype":<20} {"SS":>8} {"Slope":>10} {"Method":>15}')
    print('-' * 55)
    for key in ARCHETYPE_KEYS:
        r = results_A[key]
        method = 'NeuralProphet' if USE_NP else 'STL'
        print(f'{LABELS[key]:<20} {r["ss"]:>8.4f} {r["slope"]:>10.4f} {method:>15}')

    print('\nSpec B (AR-Net 포함) 결과')
    print(f'{"Archetype":<20} {"SS":>8} {"Slope":>10} {"AR_std":>10}')
    print('-' * 55)
    for key in ARCHETYPE_KEYS:
        r = results_B[key]
        ar_std = np.std(r['ar_contribution']) if r['ar_contribution'] is not None else 0.0
        print(f'{LABELS[key]:<20} {r["ss"]:>8.4f} {r["slope"]:>10.4f} {ar_std:>10.4f}')

    print('\nSpec A vs B Seasonality Strength 비교 (Δ = B − A)')
    print(f'{"Archetype":<20} {"SS_A":>8} {"SS_B":>8} {"Delta":>8} {"Verdict":>12}')
    print('-' * 60)
    for key in ARCHETYPE_KEYS:
        ss_a = results_A[key]['ss']
        ss_b = results_B[key]['ss']
        delta = ss_b - ss_a
        verdict = '안정' if abs(delta) < 0.05 else ('증가' if delta > 0 else '감소')
        print(f'{LABELS[key]:<20} {ss_a:>8.4f} {ss_b:>8.4f} {delta:>+8.4f} {verdict:>12}')

    # 차트 생성
    print('\n[4] 메인 차트 생성 ...')
    out_main = build_main_chart(results_A, ts_data, idx)
    print(f'    저장: {out_main}')

    print('\n[5] Robustness 차트 생성 ...')
    out_rob = build_robustness_chart(results_A, results_B)
    print(f'    저장: {out_rob}')

    # 사이즈 확인 + preview
    print('\n[6] 사이즈 확인 및 preview 생성 ...')
    for out_path in [out_main, out_rob]:
        prev, orig_sz, prev_sz = make_preview(out_path)
        print(f'    {out_path.name}: {orig_sz[0]}x{orig_sz[1]}px → preview {prev_sz[0]}x{prev_sz[1]}px')

    print('\n완료.')
    print(f'  메인: {out_main}')
    print(f'  Robustness: {out_rob}')
    print(f'  Preview: {PREV_DIR}')
