"""H26c: NeuralProphet 확장 full-component 인터랙티브 plotly 시각화.

h26b의 단순 NP (trend + yearly only)를 base로,
분기·월 seasonality + 회계연도 마감 이벤트(fy_close)를 추가한
full-component 분해를 HTML로 export.

산출물:
  docs/interactive/np_full_C0_personnel.html     - 인건비형 대표 (확장)
  docs/interactive/np_full_C1_direct_invest.html - 자산취득형 대표 (확장)
  docs/interactive/np_full_C2_chooyeon.html      - 출연금형 대표 (확장)
  docs/interactive/np_full_C3_normal.html        - 정상사업 대표 (확장)

NP 구성:
  n_changepoints=4, yearly(order=6) + quarterly(91.25d, order=6)
  + monthly(30.4d, order=4) + events=[fy_close] (매년 12월 1일)
  epochs=50
"""
import os, sys, warnings, logging
warnings.filterwarnings('ignore')

# torch 2.6+ weights_only 호환 (NP 0.9.0 checkpoint 로드)
import torch as _torch
_orig_torch_load = _torch.load
def _patched_torch_load(*args, **kwargs):
    kwargs['weights_only'] = False
    return _orig_torch_load(*args, **kwargs)
_torch.load = _patched_torch_load

logging.getLogger("NP").setLevel(logging.ERROR)
logging.getLogger("neuralprophet").setLevel(logging.ERROR)
logging.getLogger("pytorch_lightning").setLevel(logging.ERROR)
logging.getLogger("lightning").setLevel(logging.ERROR)

try:
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
except AttributeError:
    pass

import numpy as np
import pandas as pd
import duckdb
from neuralprophet import NeuralProphet, set_log_level
set_log_level("ERROR")
import plotly.graph_objects as go
from plotly.subplots import make_subplots

ROOT   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB     = os.path.join(ROOT, 'data', 'warehouse.duckdb')
OUT    = os.path.join(ROOT, 'docs', 'interactive')
H3_CSV = os.path.join(ROOT, 'data', 'results', 'H3_activity_embedding_11y.csv')
os.makedirs(OUT, exist_ok=True)
TMP    = os.path.join(ROOT, 'tmp', 'np_plotly_full')
os.makedirs(TMP, exist_ok=True)

print('=' * 70)
print('H26c: NeuralProphet 확장 full-component 인터랙티브 plotly 시각화')
print('=' * 70)

# ============================================================
# Step 1: 사업원형 라벨 로드 + 대표 활동 선택 (h26b와 동일 로직)
# ============================================================
print('\nStep 1: H3 사업원형 라벨 로드')

emb = pd.read_csv(H3_CSV)
print(f'  활동 임베딩 rows: {len(emb)}')
print(f'  cluster 분포: {emb["cluster"].value_counts().to_dict()}')

ARCHETYPE_LABELS = {
    'C0_personnel':     '인건비형 (C0)',
    'C1_direct_invest': '자산취득형 (C1)',
    'C2_chooyeon':      '출연금형 (C2)',
    'C3_normal':        '정상사업 (C3)',
}

archetype_keys = {
    0: ('C0_personnel',     '인건비형'),
    1: ('C1_direct_invest', '자산취득형'),
    2: ('C2_chooyeon',      '출연금형'),
    3: ('C3_normal',        '정상사업'),
}

# 각 클러스터 중심에 가장 가까운 활동 1개씩 선택 (UMAP 좌표 기준)
representatives = {}
for cluster_id, (key, name) in archetype_keys.items():
    sub = emb[emb['cluster'] == cluster_id].copy()
    if len(sub) == 0:
        print(f'  WARNING: cluster {cluster_id} ({name}) 비어있음')
        continue
    if 'u1' in sub.columns:
        cx, cy = sub['u1'].mean(), sub['u2'].mean()
        sub['_dist'] = ((sub['u1'] - cx) ** 2 + (sub['u2'] - cy) ** 2) ** 0.5
        chosen = sub.nsmallest(1, '_dist').iloc[0]
    else:
        chosen = sub.sample(1, random_state=42).iloc[0]
    representatives[key] = {
        'name':    name,
        'fld_nm':  chosen.get('FLD_NM',  chosen.get('fld_nm',  '')),
        'offc_nm': chosen.get('OFFC_NM', chosen.get('offc_nm', '')),
        'pgm_nm':  chosen.get('PGM_NM',  chosen.get('pgm_nm',  '')),
        'actv_nm': chosen.get('ACTV_NM', chosen.get('actv_nm', '')),
    }
    print(f'  {name}: {representatives[key]["actv_nm"][:40]}')

# ============================================================
# Step 2: 각 대표 활동의 월별 시계열 로드
# ============================================================
print('\nStep 2: 대표 활동의 월별 집행 시계열 로드')

con = duckdb.connect(DB, read_only=True)
ts_data = {}

for key, rep in representatives.items():
    if not rep['actv_nm']:
        continue
    df = con.execute(f"""
        SELECT FSCL_YY AS year, EXE_M AS month, SUM(EP_AMT) AS amt
        FROM monthly_exec
        WHERE FLD_NM = '{rep['fld_nm']}'
          AND OFFC_NM = '{rep['offc_nm']}'
          AND PGM_NM = '{rep['pgm_nm']}'
          AND ACTV_NM = '{rep['actv_nm']}'
          AND FSCL_YY BETWEEN 2015 AND 2025
          AND EXE_M BETWEEN 1 AND 12
        GROUP BY 1, 2
        ORDER BY 1, 2
    """).fetchdf()

    if len(df) < 24:
        print(f'  {rep["name"]}: 데이터 부족 ({len(df)} obs), 스킵')
        continue

    df['ds'] = pd.to_datetime(
        df['year'].astype(str) + '-' +
        df['month'].astype(str).str.zfill(2) + '-01'
    )
    df['y'] = df['amt'].astype(float)
    ts_data[key] = df[['ds', 'y']].copy()
    print(f'  {rep["name"]}: {len(df)} months, {df["year"].min()}-{df["year"].max()}')

con.close()

# ============================================================
# Step 3: 회계연도 마감 이벤트 DataFrame 준비 (2015~2025, 매년 12월 1일)
# ============================================================
events_base = pd.DataFrame({
    'ds':    pd.to_datetime([f'{y}-12-01' for y in range(2015, 2026)]),
    'event': 'fy_close',
})
print(f'\nStep 3: fy_close 이벤트 {len(events_base)}건 준비 (2015-12-01 ~ 2025-12-01)')

# ============================================================
# Step 4: 각 활동에 확장 NP 적합 + plotly full-component HTML 생성
# ============================================================
print('\nStep 4: 확장 NP 적합 + full-component plot 생성')
print('  (yearly + quarterly + monthly seasonality + fy_close events)')

forecasts = {}

for key, df in ts_data.items():
    name = representatives[key]['name']
    actv = representatives[key]['actv_nm'][:30]
    print(f'  fitting NP — {name}', flush=True)

    # ---- NP 모델 풍부화 ----
    m = NeuralProphet(
        n_lags=0,
        n_changepoints=4,          # h26b의 2 → 4로 증가
        yearly_seasonality=True,   # Fourier order=6 (기본값)
        weekly_seasonality=False,
        daily_seasonality=False,
        epochs=50,
        learning_rate=0.1,
        batch_size=None,
        trainer_config={
            'enable_progress_bar':   False,
            'enable_model_summary':  False,
            'logger':                False,
            'enable_checkpointing':  False,
            'default_root_dir':      TMP,
        },
    )

    # 분기 주기 (3개월 ≈ 91.25일) 추가
    m = m.add_seasonality(name='quarterly', period=91.25, fourier_order=6)
    # 월별 주기 (1개월 ≈ 30.4일) 추가
    m = m.add_seasonality(name='monthly',   period=30.4,  fourier_order=4)
    # 회계연도 마감 이벤트 등록
    m = m.add_events(['fy_close'])

    # 시계열 범위에 맞게 이벤트 DataFrame 필터링
    ds_min = df['ds'].min()
    ds_max = df['ds'].max()
    events_df = events_base[
        (events_base['ds'] >= ds_min) & (events_base['ds'] <= ds_max)
    ].copy()

    # 이벤트 포함 history DataFrame 생성
    try:
        history_df = m.create_df_with_events(df, events_df)
    except Exception as e:
        print(f'    create_df_with_events 실패: {e}')
        history_df = df.copy()

    # 적합
    try:
        m.fit(history_df, freq='MS', progress=None)
    except Exception as e:
        print(f'    FAIL (fit): {e}')
        continue

    fc = m.predict(history_df)
    forecasts[key] = fc

    # plotly backend 활성화
    try:
        m.set_plotting_backend('plotly')
    except Exception as e:
        print(f'    plotly backend 설정 실패: {e}')

    # Full-component 분해 figure (components 인자 없이 — 모든 component 자동 표시)
    out_html = os.path.join(OUT, f'np_full_{key}.html')
    try:
        fig = m.plot_components(fc)          # trend + yearly + quarterly + monthly + events
        fig.update_layout(
            title=(
                f'NeuralProphet 확장 분해 — {name}'
                f'<br><sub>{actv} | yearly + quarterly + monthly + fy_close</sub>'
            ),
            height=900, width=1100,
            font=dict(size=13, family='Malgun Gothic, sans-serif'),
        )
        fig.write_html(out_html, include_plotlyjs='cdn', full_html=True)
        print(f'    → {out_html}')
    except Exception as e:
        print(f'    plot_components 실패 ({e}), fallback 사용')

        # fallback: trend + 주요 seasonality 컬럼을 직접 서브플롯으로 그림
        season_cols = [c for c in fc.columns if c.startswith('season_')]
        event_cols  = [c for c in fc.columns if 'event' in c.lower() or 'fy_close' in c.lower()]
        all_cols    = season_cols + event_cols
        n_rows      = 1 + len(all_cols)
        subplot_titles = ['Trend (piecewise-linear)'] + [c.replace('season_', '') for c in season_cols] + event_cols

        fig = make_subplots(
            rows=n_rows, cols=1,
            subplot_titles=subplot_titles,
            vertical_spacing=0.08,
        )
        trend_col = 'trend' if 'trend' in fc.columns else 'yhat1'
        fig.add_trace(
            go.Scatter(x=fc['ds'], y=fc[trend_col],
                       mode='lines', line=dict(color='#5475a8', width=2), name='trend'),
            row=1, col=1,
        )
        palette_fallback = ['#a85454', '#54a87e', '#a8a054', '#9054a8', '#54a8a8']
        for i, col in enumerate(all_cols, start=2):
            if col not in fc.columns:
                continue
            fig.add_trace(
                go.Scatter(x=fc['ds'], y=fc[col],
                           mode='lines',
                           line=dict(color=palette_fallback[(i - 2) % len(palette_fallback)], width=2),
                           name=col),
                row=i, col=1,
            )
        fig.update_layout(
            title=(
                f'NeuralProphet 확장 분해 — {name}'
                f'<br><sub>{actv} | yearly + quarterly + monthly + fy_close (fallback)</sub>'
            ),
            height=max(700, 220 * n_rows),
            width=1100,
            showlegend=False,
            font=dict(size=13, family='Malgun Gothic, sans-serif'),
            plot_bgcolor='#fafafa',
        )
        fig.update_xaxes(showgrid=True, gridcolor='#eee')
        fig.update_yaxes(showgrid=True, gridcolor='#eee')
        fig.write_html(out_html, include_plotlyjs='cdn', full_html=True)
        print(f'    → {out_html} (fallback)')

# ============================================================
# Step 5: 완료 요약
# ============================================================
print('\n완료. 확장 NP 인터랙티브 시각화 HTML 생성:')
for key in archetype_keys.values():
    fname = f'np_full_{key[0]}.html'
    fpath = os.path.join(OUT, fname)
    status = '생성됨' if os.path.exists(fpath) else '미생성'
    print(f'  [{status}] docs/interactive/{fname}')
