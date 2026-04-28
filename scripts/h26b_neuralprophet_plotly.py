"""H26b: NeuralProphet 인터랙티브 plotly 시각화.

각 사업원형(인건비형/자산취득형/출연금형/정상)의 대표 활동을 선택해 NP 적합 후
plotly backend으로 component 분해를 HTML로 export.

산출물:
  docs/interactive/np_components_personnel.html     - 인건비형 대표
  docs/interactive/np_components_asset.html         - 자산취득형 대표
  docs/interactive/np_components_chooyeon.html      - 출연금형 대표
  docs/interactive/np_components_normal.html        - 정상사업 대표
  docs/interactive/np_archetype_comparison.html     - 4 원형 yearly seasonality 비교
  docs/interactive/neuralprophet_components.html    - 카드형 landing page
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

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB   = os.path.join(ROOT, 'data', 'warehouse.duckdb')
OUT  = os.path.join(ROOT, 'docs', 'interactive')
H3_CSV = os.path.join(ROOT, 'data', 'results', 'H3_activity_embedding_11y.csv')
os.makedirs(OUT, exist_ok=True)
TMP  = os.path.join(ROOT, 'tmp', 'np_plotly')
os.makedirs(TMP, exist_ok=True)

print('=' * 70)
print('H26b: NeuralProphet 인터랙티브 plotly 시각화')
print('=' * 70)

# ============================================================
# Step 1: 사업원형 라벨 로드 + 대표 활동 선택
# ============================================================
print('\nStep 1: H3 사업원형 라벨 로드')

emb = pd.read_csv(H3_CSV)
print(f'  활동 임베딩 rows: {len(emb)}')
print(f'  cluster 분포: {emb["cluster"].value_counts().to_dict()}')

# 사업원형 매핑 (H3 결과에서)
ARCHETYPE_LABELS = {
    'C0_personnel':   '인건비형 (C0)',
    'C1_direct_invest': '자산취득형 (C1)',
    'C2_chooyeon':    '출연금형 (C2)',
    'C3_normal':      '정상사업 (C3)',
}

# cluster_main 컬럼으로 4 archetype 식별 (-1=노이즈 제외)
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
        sub['_dist'] = ((sub['u1']-cx)**2 + (sub['u2']-cy)**2)**0.5
        chosen = sub.nsmallest(1, '_dist').iloc[0]
    else:
        chosen = sub.sample(1, random_state=42).iloc[0]
    representatives[key] = {
        'name': name,
        'fld_nm': chosen.get('FLD_NM', chosen.get('fld_nm', '')),
        'offc_nm': chosen.get('OFFC_NM', chosen.get('offc_nm', '')),
        'pgm_nm': chosen.get('PGM_NM', chosen.get('pgm_nm', '')),
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

    df['ds'] = pd.to_datetime(df['year'].astype(str) + '-' +
                               df['month'].astype(str).str.zfill(2) + '-01')
    df['y']  = df['amt'].astype(float)
    ts_data[key] = df[['ds', 'y']].copy()
    print(f'  {rep["name"]}: {len(df)} months, {df["year"].min()}-{df["year"].max()}')

con.close()

# ============================================================
# Step 3: 각 활동에 NP 적합 + plotly component HTML 생성
# ============================================================
print('\nStep 3: NP 적합 + component plot 생성')

models = {}
forecasts = {}

for key, df in ts_data.items():
    name = representatives[key]['name']
    actv = representatives[key]['actv_nm'][:30]
    print(f'  fitting NP — {name}', flush=True)

    m = NeuralProphet(
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False,
        n_lags=0,
        n_changepoints=2,
        epochs=50,
        learning_rate=0.1,
        batch_size=None,
        trainer_config={
            'enable_progress_bar': False,
            'enable_model_summary': False,
            'logger': False,
            'enable_checkpointing': False,
            'default_root_dir': TMP,
        },
    )
    try:
        m.fit(df, freq='MS', progress=None)
    except Exception as e:
        print(f'    FAIL: {e}')
        continue

    fc = m.predict(df)
    models[key] = m
    forecasts[key] = fc

    # plotly backend 활성화
    try:
        m.set_plotting_backend('plotly')
    except Exception as e:
        print(f'    plotly backend 설정 실패: {e}')

    # Components 분해 figure (trend + yearly seasonality)
    try:
        fig = m.plot_components(fc, components=['trend', 'seasonality_yearly'])
        fig.update_layout(
            title=f'NeuralProphet 분해 — {name}<br><sub>{actv}</sub>',
            height=500, width=1100,
            font=dict(size=13, family='Malgun Gothic, sans-serif'),
        )
        out_html = os.path.join(OUT, f'np_components_{key}.html')
        fig.write_html(out_html, include_plotlyjs='cdn')
        print(f'    → {out_html}')
    except Exception as e:
        print(f'    components plot 실패: {e}')
        # fallback: yearly + trend을 직접 그림
        if 'season_yearly' in fc.columns:
            fig = make_subplots(rows=2, cols=1,
                                subplot_titles=('Trend (piecewise-linear)', 'Yearly Seasonality'),
                                vertical_spacing=0.15)
            fig.add_trace(go.Scatter(x=fc['ds'], y=fc.get('trend', fc.get('yhat1', None)),
                                      mode='lines', line=dict(color='#5475a8', width=2),
                                      name='trend'), row=1, col=1)
            fig.add_trace(go.Scatter(x=fc['ds'], y=fc['season_yearly'],
                                      mode='lines', line=dict(color='#a85454', width=2),
                                      name='yearly seasonality'), row=2, col=1)
            fig.update_layout(
                title=f'NeuralProphet 분해 — {name}<br><sub>{actv}</sub>',
                height=520, width=1100, showlegend=False,
                font=dict(size=13, family='Malgun Gothic, sans-serif'),
                plot_bgcolor='#fafafa',
            )
            fig.update_xaxes(title_text='', showgrid=True, gridcolor='#eee')
            fig.update_yaxes(showgrid=True, gridcolor='#eee')
            out_html = os.path.join(OUT, f'np_components_{key}.html')
            fig.write_html(out_html, include_plotlyjs='cdn')
            print(f'    → {out_html} (fallback)')

# ============================================================
# Step 4: 4 원형 yearly seasonality 비교 plotly HTML
# ============================================================
print('\nStep 4: 4 원형 yearly seasonality 비교 figure')

if forecasts:
    fig = go.Figure()
    palette = {'C0_personnel':   '#4C72B0',
               'C1_direct_invest':'#DD8452',
               'C2_chooyeon':    '#55A868',
               'C3_normal':      '#C44E52'}

    for key, fc in forecasts.items():
        if 'season_yearly' not in fc.columns:
            continue
        # 1년치만 추출 (가장 마지막 연도)
        fc['month'] = pd.to_datetime(fc['ds']).dt.month
        # 월별 평균 seasonality
        seasonal_by_month = fc.groupby('month')['season_yearly'].mean()
        name = ARCHETYPE_LABELS.get(key, key)
        fig.add_trace(go.Scatter(
            x=seasonal_by_month.index,
            y=seasonal_by_month.values,
            mode='lines+markers',
            name=name,
            line=dict(color=palette.get(key, '#888'), width=3),
            marker=dict(size=10),
        ))

    fig.update_layout(
        title='NeuralProphet — 사업원형별 Yearly Seasonality 비교<br><sub>월별 평균 NP 계절 성분 — 출연금형이 12월에 가장 강한 점프</sub>',
        xaxis_title='월',
        yaxis_title='NP yearly seasonality 성분',
        height=560, width=1100,
        legend=dict(yanchor='top', y=0.99, xanchor='right', x=0.99,
                     bgcolor='rgba(255,255,255,0.85)'),
        font=dict(size=14, family='Malgun Gothic, sans-serif'),
        plot_bgcolor='#fafafa',
    )
    fig.update_xaxes(tickmode='array', tickvals=list(range(1, 13)),
                     showgrid=True, gridcolor='#eee')
    fig.update_yaxes(showgrid=True, gridcolor='#eee', zeroline=True, zerolinecolor='#888')

    out_html = os.path.join(OUT, 'np_archetype_comparison.html')
    fig.write_html(out_html, include_plotlyjs='cdn')
    print(f'  → {out_html}')

# ============================================================
# Step 5: 카드형 landing page
# ============================================================
print('\nStep 5: landing page neuralprophet_components.html 생성')

card_template = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>NeuralProphet 분해 — 사업원형별 인터랙티브 시각화</title>
<style>
  body {{ font-family: 'Malgun Gothic', 'Noto Sans KR', sans-serif;
         max-width: 1200px; margin: 2rem auto; padding: 0 1.5rem; line-height: 1.6; color: #222; }}
  h1 {{ font-size: 1.8rem; border-bottom: 2px solid #5a67d8; padding-bottom: 0.5rem; }}
  h2 {{ font-size: 1.2rem; margin-top: 2.5rem; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
          gap: 1.5rem; margin: 2rem 0; }}
  .card {{ border: 1px solid #ddd; border-radius: 8px; padding: 1.2rem;
          transition: all 0.15s; background: #fff; }}
  .card:hover {{ transform: translateY(-2px); box-shadow: 0 4px 16px rgba(0,0,0,0.08); }}
  .card h3 {{ margin: 0 0 0.5rem 0; }}
  .card p {{ font-size: 0.95rem; color: #555; margin: 0.4rem 0; }}
  .badge {{ display: inline-block; padding: 0.15rem 0.55rem; font-size: 0.78rem;
           border-radius: 4px; margin-right: 0.4rem; font-weight: 500; }}
  .b-personnel  {{ background: #e6f0fa; color: #2c5282; }}
  .b-asset      {{ background: #faead8; color: #9c4221; }}
  .b-chooyeon   {{ background: #e6f0e6; color: #285e2a; }}
  .b-normal     {{ background: #fae6e6; color: #9b2c2c; }}
  .b-compare    {{ background: #f0e6fa; color: #553c9a; }}
  .btn {{ display: inline-block; margin-top: 0.6rem; padding: 0.4rem 1rem;
          background: #5a67d8; color: #fff !important; text-decoration: none;
          border-radius: 5px; font-weight: 500; font-size: 0.9rem; }}
  .btn:hover {{ background: #4c51bf; }}
  .nav {{ margin-bottom: 1rem; }}
  .nav a {{ font-size: 0.9rem; color: #5a67d8; text-decoration: none; }}
  .ctx {{ background: #f7fafc; padding: 1rem 1.4rem; border-left: 3px solid #5a67d8;
          border-radius: 4px; margin: 1rem 0; }}
</style>
</head>
<body>
  <div class="nav">
    <a href="index.md">← 인터랙티브 시각화 인덱스로</a>
  </div>

  <h1>NeuralProphet 분해 — 사업원형별 시계열 분해 시각화</h1>

  <div class="ctx">
  <p><strong>맥락:</strong> 본 연구는 게임화 측정에 FFT amp_12m_norm·STL seasonal_strength·NeuralProphet 세 도구를 cross-check으로 사용한다. NP는 시계열을 <em>piecewise-linear 추세 + Fourier 계열 계절성</em>으로 가법 분해해 추세와 계절을 명시적으로 분리한다. 본 페이지는 4개 사업원형의 대표 활동에 대해 NP 분해 결과를 인터랙티브로 보여준다.</p>
  </div>

  <h2>사업원형별 분해 (대표 활동 1개씩)</h2>
  <div class="grid">
    {cards}
  </div>

  <h2>4 원형 비교 — Yearly Seasonality 패턴</h2>
  <div class="grid">
    <div class="card" style="grid-column: 1/-1;">
      <h3>월별 NP yearly seasonality 비교</h3>
      <span class="badge b-compare">4 원형 overlay</span>
      <p>4 사업원형의 월별 평균 NP 계절 성분을 한 그래프에 겹쳐서, 어느 원형이 12월에 가장 강한 점프를 보이는지 비교한다. 출연금형(C2)이 가장 강한 12월 양의 진폭을 보일 것으로 예상.</p>
      <a class="btn" href="np_archetype_comparison.html">열기 →</a>
    </div>
  </div>

  <h2>분석 도구 정보</h2>
  <p style="font-size: 0.9rem; color: #666;">
    NeuralProphet 0.9 / PyTorch Lightning, n_lags=0 (자기회귀 차단), n_changepoints=2, yearly_seasonality=True (Fourier order=6), epochs=50.
    상세 모형식과 본 연구에서 AR을 끈 이유는 <a href="https://github.com/bluethestyle/goodhart-korea">논문 부록 C.3</a> 참조.
  </p>

</body>
</html>
"""

archetype_meta = {
    'C0_personnel': {
        'badge': 'b-personnel',
        'desc': '인건비 비중이 매우 높고 매월 일정 지급. 게임화 진폭이 가장 낮은 평탄한 시계열.',
    },
    'C1_direct_invest': {
        'badge': 'b-asset',
        'desc': '자산 취득·시설 공사 사업. 공정률에 따른 자연스러운 변동, 12월 점프 약함.',
    },
    'C2_chooyeon': {
        'badge': 'b-chooyeon',
        'desc': '공공·출연기관 위탁 사업. 12월 정산 압력으로 가장 강한 yearly seasonality (3.42x RDD 점프).',
    },
    'C3_normal': {
        'badge': 'b-normal',
        'desc': '일반 사업 (n=1,175). 평균적인 12월 1.91x 집중 패턴.',
    },
}

cards_html = []
for key, rep in representatives.items():
    if key not in forecasts:
        continue
    meta = archetype_meta.get(key, {'badge': 'b-normal', 'desc': ''})
    cards_html.append(f'''
    <div class="card">
      <h3>{rep['name']}</h3>
      <span class="badge {meta['badge']}">대표 활동</span>
      <p style="font-size:0.85rem; color:#888;">{rep['offc_nm']} — {rep['actv_nm'][:50]}</p>
      <p>{meta['desc']}</p>
      <a class="btn" href="np_components_{key}.html">분해 보기 →</a>
    </div>''')

landing_html = card_template.format(cards='\n'.join(cards_html))
out = os.path.join(OUT, 'neuralprophet_components.html')
with open(out, 'w', encoding='utf-8') as f:
    f.write(landing_html)
print(f'  → {out}')

print('\n완료. NP 인터랙티브 시각화 5개 HTML 생성:')
for f in sorted(os.listdir(OUT)):
    if 'np_' in f or 'neuralprophet' in f:
        print(f'  - docs/interactive/{f}')
