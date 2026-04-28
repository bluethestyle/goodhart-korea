"""H4 v3: Mapper(TDA) 위상 분석 + 활동 단위 outcome decoupling (11y 기준, 교체 4개 반영).

목적
  1. UMAP+HDBSCAN의 평면 클러스터 위에 Mapper로 위상 구조 추출
     → 클러스터 간 "다리(bridge)"·"분기(branch)"·"고리(loop)" 식별
  2. KOSIS outcome (15개 분야, 교체 4개 반영)을 활동에 broadcast → 클러스터별 outcome 시계열
  3. 클러스터별 game↔outcome 차분 상관관계 (4 cluster × 15 outcome matrix)
  4. 5y / 11y / v3 비교: 자기 인과 제거 후 신호 변화 확인

교체 내역 (v2 → v3)
  과학기술: rd_total → patent_apps_total
  문화및관광: tourists_sample → foreign_tourists_total
  일반·지방행정: local_tax_per_capita → fiscal_indep_natl
  통신: ict_value_added → broadband_per_100

입력
  data/results/H3_activity_embedding_11y.csv  (1,557 활동, 4 cluster)
  data/warehouse.duckdb (indicator_panel - outcome metrics)

출력
  data/figs/h4_11y_v3/H4_mapper_graph_11y_v3.png
  data/figs/h4_11y_v3/H4_cluster_outcome_panel_11y_v3.png
  data/figs/h4_11y_v3/H4_mapper_chooyeon_11y_v3.png
  data/results/H4_cluster_outcome_corr_11y_v3.csv

클러스터 레이블 (11y v2)
  0 = 인건비형   1 = 자산취득형   2 = 출연금형   3 = 정상형
"""
import os, sys, io, warnings
import numpy as np
import pandas as pd
import duckdb
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
import kmapper as km
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib as mpl
import scienceplots
import seaborn as sns
from PIL import Image
plt.style.use(['science', 'no-latex', 'grid'])
plt.rcParams.update({
    'font.size': 16,
    'axes.titlesize': 18,
    'axes.labelsize': 16,
    'xtick.labelsize': 14,
    'ytick.labelsize': 14,
    'legend.fontsize': 14,
    'legend.title_fontsize': 14,
    'figure.titlesize': 19,
    'lines.linewidth': 2.0,
    'lines.markersize': 8,
    'axes.linewidth': 1.0,
    'grid.alpha': 0.3,
    'mathtext.fontset': 'stix',
    'mathtext.default': 'regular',
})
for fname in ['Malgun Gothic', 'NanumGothic', 'HYGothic']:
    if any(fname.lower() in fn.name.lower() for fn in mpl.font_manager.fontManager.ttflist):
        mpl.rcParams['font.family'] = [fname, 'Times New Roman', 'DejaVu Sans']
        break
mpl.rcParams['axes.unicode_minus'] = False
sns.set_palette('Set2')

warnings.filterwarnings('ignore')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB      = os.path.join(ROOT, 'data', 'warehouse.duckdb')
H3_CSV  = os.path.join(ROOT, 'data', 'results', 'H3_activity_embedding_11y.csv')
OUT_DIR = os.path.join(ROOT, 'data', 'figs', 'h4_11y_v3')
RES_DIR = os.path.join(ROOT, 'data', 'results')
os.makedirs(OUT_DIR, exist_ok=True)

KFONT = mpl.rcParams.get('font.family', 'Malgun Gothic')
print(f'  [font] 사용 폰트: {KFONT}')

MAX_PX = 1800  # 최대 픽셀

def save_and_resize(fig, path, dpi=200):
    """저장 후 1800px 초과 시 PIL로 리사이즈."""
    fig.savefig(path, dpi=dpi, bbox_inches='tight')
    plt.close(fig)
    img = Image.open(path)
    w, h = img.size
    if max(w, h) > MAX_PX:
        scale = MAX_PX / max(w, h)
        img = img.resize((int(w*scale), int(h*scale)), Image.LANCZOS)
        img.save(path)
        print(f'  [resize] {os.path.basename(path)}: {w}×{h} → {img.size[0]}×{img.size[1]}')
    else:
        print(f'  [ok] {os.path.basename(path)}: {w}×{h}')

# ============================================================
# 15개 분야 × outcome metric 매핑 (v3: 교체 4개 반영)
# ★ 교체: 과학기술/문화및관광/일반·지방행정/통신
# ============================================================
OUTCOME_MAP = {
    '사회복지':              'wealth_gini',
    '보건':                  'life_expectancy',
    '과학기술':              'patent_apps_total',          # ★ 교체 (rd_total → patent_apps_total)
    '산업·중소기업및에너지': 'industry_production_index',
    '문화및관광':            'foreign_tourists_total',     # ★ 교체 (tourists_sample → foreign_tourists_total)
    '교육':                  'private_edu_hours',
    '국토및지역개발':        'housing_supply',
    '일반·지방행정':         'fiscal_indep_natl',          # ★ 교체 (local_tax_per_capita → fiscal_indep_natl)
    '농림수산':              'farm_income',
    '교통및물류':            'traffic_deaths',
    '환경':                  'ghg_total',
    '통신':                  'broadband_per_100',          # ★ 교체 (ict_value_added → broadband_per_100)
    '통일·외교':             'oda_total',
    '공공질서및안전':        'crime_occurrence',
    '국방':                  'defense_op_margin',
}

OUTCOME_METRICS = list(OUTCOME_MAP.values())

# metric → 한글 레이블
OUTCOME_LABEL = {
    'wealth_gini':              '사회복지(지니)',
    'life_expectancy':          '보건(기대수명)',
    'patent_apps_total':        '과학기술(특허출원)',       # ★ 교체
    'industry_production_index':'산업(생산지수)',
    'foreign_tourists_total':   '문화관광(외국인관광)',     # ★ 교체
    'private_edu_hours':        '교육(사교육시간)',
    'housing_supply':           '국토(주택공급)',
    'fiscal_indep_natl':        '일반행정(재정자립)',       # ★ 교체
    'farm_income':              '농림수산(농가소득)',
    'traffic_deaths':           '교통(사망자)',
    'ghg_total':                '환경(온실가스)',
    'broadband_per_100':        '통신(광대역가입)',          # ★ 교체
    'oda_total':                '통일외교(ODA)',
    'crime_occurrence':         '공공질서(범죄발생)',
    'defense_op_margin':        '국방(영업이익률)',
}

# v2 → v3 교체 쌍 (비교 출력용)
REPLACED = {
    'patent_apps_total':    ('rd_total',              '과학기술'),
    'foreign_tourists_total':('tourists_sample',      '문화및관광'),
    'fiscal_indep_natl':    ('local_tax_per_capita',  '일반·지방행정'),
    'broadband_per_100':    ('ict_value_added',        '통신'),
}

# 클러스터 레이블 (11y v2)
CLU_LABEL = {0:'인건비형', 1:'자산취득형', 2:'출연금형', 3:'정상형'}

# ============================================================
# Step 1: 데이터 로드
# ============================================================
print('='*70)
print('Step 1: H3 11y 임베딩 + outcome 데이터 로드')
print('='*70)
df = pd.read_csv(H3_CSV)
print(f'  활동 N = {len(df)}')
print(f'  cluster 분포:')
for cl, n in df['cluster'].value_counts().sort_index().items():
    print(f'    cluster {cl} ({CLU_LABEL.get(cl,"?")}) : {n}')

feat_cols = [
    'amp_12m_norm','amp_6m_norm','hhi_period','q4_pct','dec_pct','cv_monthly',
    'chooyeon_pct','operating_pct','direct_invest_pct','personnel_pct',
    'log_annual','growth_cagr',
]
X = StandardScaler().fit_transform(df[feat_cols].values)

con = duckdb.connect(DB, read_only=True)

# ============================================================
# Step 2: Mapper graph
# ============================================================
print('\n' + '='*70)
print('Step 2: Mapper graph (UMAP 2D filter, DBSCAN cover/cluster)')
print('='*70)

lens = df[['u1', 'u2']].values

mapper = km.KeplerMapper(verbose=0)

# 커버: 18×18, 50% overlap
cover = km.Cover(n_cubes=18, perc_overlap=0.5)

# 각 큐브 내부 클러스터링: DBSCAN (eps=0.45, min_samples=4)
clusterer = DBSCAN(eps=0.45, min_samples=4)

graph = mapper.map(
    lens=lens,
    X=X,
    cover=cover,
    clusterer=clusterer,
)

n_nodes = len(graph['nodes'])
n_edges = sum(len(v) for v in graph['links'].values())
print(f'  Mapper nodes = {n_nodes}, edges = {n_edges}')

# Mapper graph -> networkx
G = nx.Graph()
node_meta = {}
for nid, members in graph['nodes'].items():
    sub = df.iloc[members]
    G.add_node(nid, size=len(members))
    node_meta[nid] = {
        'size':               len(members),
        'mean_amp_12m':       float(sub['amp_12m_norm'].mean()),
        'mean_chooyeon':      float(sub['chooyeon_pct'].mean()),
        'mean_dec':           float(sub['dec_pct'].mean()),
        'mean_personnel':     float(sub['personnel_pct'].mean()),
        'mean_direct_invest': float(sub['direct_invest_pct'].mean()),
        'cluster_dom':        int(sub['cluster'].mode().iloc[0]),
        'top_field':          sub['FLD_NM'].mode().iloc[0] if len(sub) > 0 else '',
        'fld_diversity':      sub['FLD_NM'].nunique(),
    }
for nid, neighbors in graph['links'].items():
    for nb in neighbors:
        G.add_edge(nid, nb)

print(f'  네트워크: {G.number_of_nodes()} nodes / {G.number_of_edges()} edges')

# ============================================================
# Step 3: 위상 통계 (component, cycle basis, branch points)
# ============================================================
print('\n' + '='*70)
print('Step 3: Mapper 위상 통계')
print('='*70)
comps = list(nx.connected_components(G))
sizes = sorted([len(c) for c in comps], reverse=True)
print(f'  연결 성분 = {len(comps)}, 상위 5: {sizes[:5]}')

# 최대 component → 1차 베티수
LCC = G.subgraph(max(comps, key=len)).copy()
n_loops = LCC.number_of_edges() - LCC.number_of_nodes() + 1
print(f'  최대 컴포넌트: {LCC.number_of_nodes()} nodes, {LCC.number_of_edges()} edges')
print(f'  → 1차 베티수 (독립 루프 수) = {n_loops}')
print(f'  → 0차 베티수 (컴포넌트 수) = {len(comps)}')

deg = dict(LCC.degree())
branches  = [n for n, d in deg.items() if d >= 3]
endpoints = [n for n, d in deg.items() if d == 1]
print(f'  분기점 (deg≥3) = {len(branches)}')
print(f'  말단 (deg=1) = {len(endpoints)}')

# ============================================================
# Step 4: outcome 데이터 로드 (15 metrics, v3)
# ============================================================
print('\n' + '='*70)
print('Step 4: KOSIS outcome (15 분야, v3 교체) → 활동 broadcast')
print('='*70)
print('  교체 항목:')
for new_m, (old_m, field) in REPLACED.items():
    print(f'    [{field}] {old_m} → {new_m}')

metrics_sql = "','".join(OUTCOME_METRICS)
panel = con.execute(f"""
    SELECT fld_nm, year, metric_code, value
    FROM indicator_panel
    WHERE metric_code IN ('amp_12m_norm','{metrics_sql}')
""").fetchdf()

wide = panel.pivot_table(index=['fld_nm','year'], columns='metric_code',
                         values='value').reset_index()
print(f'  wide table: {wide.shape}')
print(f'  연도 범위: {wide["year"].min()} ~ {wide["year"].max()}')
print(f'  분야 수: {wide["fld_nm"].nunique()}')
print(f'  컬럼: {sorted(wide.columns.tolist())}')

# 실제 로드된 v3 메트릭 확인
loaded_metrics = [m for m in OUTCOME_METRICS if m in wide.columns]
missing_metrics = [m for m in OUTCOME_METRICS if m not in wide.columns]
print(f'\n  로드된 metric ({len(loaded_metrics)}): {loaded_metrics}')
if missing_metrics:
    print(f'  누락된 metric ({len(missing_metrics)}): {missing_metrics}')

# ============================================================
# Step 5: 클러스터별 outcome 차분 상관 (4 cluster × 15 outcome)
# ============================================================
print('\n' + '='*70)
print('Step 5: 클러스터별 outcome 진동 (분야 가중평균) — 4×15 matrix')
print('='*70)

# 각 클러스터의 분야별 활동 비중
clu_fld = pd.crosstab(df['cluster'], df['FLD_NM'], normalize='index')
print('  cluster × field weight (상위 분야):')
print(clu_fld.round(3).to_string())

years    = sorted(wide['year'].unique())
clusters = sorted(df['cluster'].unique())

cluster_amp_ts = {}

for cl in clusters:
    weights = clu_fld.loc[cl]
    amp_w   = []
    for y in years:
        sub = wide[wide['year']==y].set_index('fld_nm')
        if 'amp_12m_norm' not in sub.columns:
            amp_w.append(np.nan); continue
        v = sub['amp_12m_norm'].reindex(weights.index).fillna(np.nan)
        valid = ~v.isna()
        if valid.sum() == 0:
            amp_w.append(np.nan); continue
        w = weights[valid]; w = w / w.sum()
        amp_w.append(float((v[valid] * w).sum()))
    cluster_amp_ts[cl] = pd.Series(amp_w, index=years)

oc_results = []
for cl in clusters:
    weights = clu_fld.loc[cl]
    for m in OUTCOME_METRICS:
        if m not in wide.columns:
            continue
        ts, ys = [], []
        for y in years:
            sub = wide[wide['year']==y].set_index('fld_nm')
            if m not in sub.columns:
                continue
            v = sub[m].reindex(weights.index).fillna(np.nan)
            valid = ~v.isna()
            if valid.sum() == 0:
                continue
            w = weights[valid]; w = w / w.sum()
            ts.append(float((v[valid] * w).sum()))
            ys.append(y)
        if len(ts) < 4:
            continue
        s   = pd.Series(ts, index=ys).sort_index()
        amp = cluster_amp_ts[cl].reindex(s.index).dropna()
        s   = s.loc[amp.index]
        if len(s) < 4:
            continue
        d_amp = amp.diff().dropna()
        d_oc  = s.diff().dropna()
        common = d_amp.index.intersection(d_oc.index)
        if len(common) < 3:
            continue
        corr_diff_val = float(d_amp[common].corr(d_oc[common]))
        oc_results.append({
            'cluster':      cl,
            'clu_label':    CLU_LABEL.get(cl, str(cl)),
            'metric':       m,
            'metric_label': OUTCOME_LABEL.get(m, m),
            'n_year':       len(s),
            'corr_levels':  float(amp.corr(s)),
            'corr_diff':    corr_diff_val,
            'amp_mean':     float(amp.mean()),
            'oc_mean':      float(s.mean()),
            'is_replaced':  m in REPLACED,
        })

oc_corr = pd.DataFrame(oc_results)
print('\n  클러스터 × outcome 차분 상관 (4×15 matrix):')
if len(oc_corr) > 0:
    pv = oc_corr.pivot(index='metric', columns='cluster', values='corr_diff')
    pv.columns = [f'{c}({CLU_LABEL.get(c,"?")})' for c in pv.columns]
    print(pv.round(3).to_string())

# ============================================================
# Step 5b: 5y / 11y / v3 비교 (교체 4개 metric)
# ============================================================
print('\n' + '='*70)
print('Step 5b: 5y / 11y(v2) / 11y(v3) 신호 비교')
print('='*70)

# 11y v2 결과 로드 (비교용)
v2_path = os.path.join(RES_DIR, 'H4_cluster_outcome_corr_11y.csv')
v3_path = os.path.join(RES_DIR, 'H4_cluster_outcome_corr_11y_v3.csv')  # 이 스크립트가 생성
v1_path = os.path.join(RES_DIR, 'H4_cluster_outcome_corr.csv')

print('  [교체 전후 신호 방향 요약]')
if os.path.exists(v2_path) and len(oc_corr) > 0:
    v2 = pd.read_csv(v2_path)
    # 교체된 4개 metric에 대응하는 구-metric 코드
    replaced_old = {v[0]: (k, v[1]) for k, v in REPLACED.items()}
    # 예: 'rd_total' → ('patent_apps_total', '과학기술')

    print(f'  {"분야":<12} {"구 metric":<25} {"신 metric":<25} {"cluster":<8} {"구 corr":>8} {"신 corr":>8} {"변화":>6}')
    print('  ' + '-'*100)
    for old_m, (new_m, field) in replaced_old.items():
        for cl in clusters:
            old_row = v2[(v2['metric']==old_m) & (v2['cluster']==cl)]
            new_row = oc_corr[(oc_corr['metric']==new_m) & (oc_corr['cluster']==cl)]
            old_c = float(old_row['corr_diff'].values[0]) if len(old_row) > 0 else float('nan')
            new_c = float(new_row['corr_diff'].values[0]) if len(new_row) > 0 else float('nan')
            sign_change = ''
            if not (np.isnan(old_c) or np.isnan(new_c)):
                if np.sign(old_c) != np.sign(new_c):
                    sign_change = '★ 부호반전'
                elif abs(new_c - old_c) > 0.2:
                    sign_change = '△ 큰변화'
            clu_nm = CLU_LABEL.get(cl, str(cl))
            print(f'  {field:<12} {old_m:<25} {new_m:<25} {clu_nm:<8} {old_c:>8.3f} {new_c:>8.3f} {sign_change:>10}')
else:
    print('  [경고] v2 CSV 없음 — 비교 생략')

# ============================================================
# Step 6: CSV 저장
# ============================================================
print('\n' + '='*70)
print('Step 6: CSV 저장')
print('='*70)

oc_corr.to_csv(
    os.path.join(RES_DIR, 'H4_cluster_outcome_corr_11y_v3.csv'),
    index=False, encoding='utf-8-sig')
print(f'  cluster outcome corr csv: H4_cluster_outcome_corr_11y_v3.csv ({len(oc_corr)} rows)')

# ============================================================
# Figure A: Mapper graph (amp_12m 색상 + 클러스터 색상)
# ============================================================
print('\n' + '='*70)
print('Figure A: Mapper graph')
print('='*70)
pos = nx.spring_layout(G, seed=42, k=0.4, iterations=200)
sizes_arr = np.array([G.nodes[n]['size'] for n in G.nodes()])

fig, axes = plt.subplots(1, 2, figsize=(15, 7))

# 왼쪽: amp_12m_norm 색상
ax = axes[0]
colors = np.array([node_meta[n]['mean_amp_12m'] for n in G.nodes()])
nx.draw_networkx_edges(G, pos, alpha=0.3, width=0.6, ax=ax)
sc = nx.draw_networkx_nodes(G, pos, node_size=20+5*sizes_arr,
                             node_color=colors, cmap='RdBu_r',
                             vmin=0, vmax=df['amp_12m_norm'].quantile(0.9),
                             alpha=0.85, ax=ax)
ax.set_title(
    f'Mapper graph (11y v3) — color=평균 amp_12m_norm\n'
    f'{G.number_of_nodes()} nodes, {G.number_of_edges()} edges, '
    f'components={len(comps)}, loops={n_loops}',
    fontsize=10
)
ax.axis('off')
fig.colorbar(sc, ax=ax, label='amp_12m_norm', shrink=0.7)

# 오른쪽: 4 클러스터 색상
ax = axes[1]
palette = plt.get_cmap('tab10')
clu_colors = [palette(node_meta[n]['cluster_dom'] % 10) for n in G.nodes()]
nx.draw_networkx_edges(G, pos, alpha=0.3, width=0.6, ax=ax)
nx.draw_networkx_nodes(G, pos, node_size=20+5*sizes_arr,
                       node_color=clu_colors, alpha=0.85, ax=ax)
# 분기점 상위 6개 라벨
top_branch = sorted(branches, key=lambda n: -G.nodes[n]['size'])[:6]
nx.draw_networkx_labels(G, pos,
                        labels={n: node_meta[n]['top_field'] for n in top_branch},
                        font_size=7, font_family=KFONT or 'sans-serif', ax=ax)
# 범례
from matplotlib.patches import Patch
legend_elems = [Patch(facecolor=palette(cl), label=f'{cl}:{CLU_LABEL.get(cl,"?")}')
                for cl in sorted(CLU_LABEL.keys())]
ax.legend(handles=legend_elems, loc='lower right', fontsize=8)
ax.set_title(
    f'Mapper graph (11y v3) — color=H3 클러스터\n'
    f'0:인건비/1:자산취득/2:출연금/3:정상  |  분기점={len(branches)}, 말단={len(endpoints)}',
    fontsize=10
)
ax.axis('off')
plt.tight_layout()
save_and_resize(fig, os.path.join(OUT_DIR, 'H4_mapper_graph_11y_v3.png'))

# ============================================================
# Figure B: 클러스터별 outcome 차분 상관 패널 (4×15 + 비교)
# ============================================================
print('\n' + '='*70)
print('Figure B: 클러스터별 outcome 차분 상관 패널')
print('='*70)
fig, axes = plt.subplots(2, 2, figsize=(17, 11))

# (상단 좌) 클러스터별 amp_12m 가중 시계열
ax = axes[0, 0]
for cl in clusters:
    s = cluster_amp_ts[cl].dropna()
    ax.plot(s.index, s.values, marker='o', label=f'{cl}:{CLU_LABEL.get(cl,"?")}')
ax.set_title('클러스터별 amp_12m 가중평균 시계열 (11y v3, 분야 가중)', fontsize=10)
ax.set_xlabel('year'); ax.set_ylabel('amp_12m_norm')
ax.legend(fontsize=8); ax.grid(alpha=0.3)

# (상단 우) 4×15 outcome 차분 상관 히트맵
ax = axes[0, 1]
if len(oc_corr) > 0:
    pv = oc_corr.pivot(index='metric_label', columns='cluster', values='corr_diff')
    pv.columns = [f'{c}:{CLU_LABEL.get(c,"?")}' for c in pv.columns]
    # 교체 항목 표시용 마스크
    replaced_labels = [OUTCOME_LABEL.get(m, m) for m in REPLACED.keys()]
    sns.heatmap(pv, annot=True, fmt='.2f', cmap='RdBu_r', center=0, ax=ax,
                cbar_kws={'label': 'corr(1차 차분)'}, annot_kws={'size': 7})
    ax.set_title('클러스터 × outcome 차분 상관 (15 outcome × 4 cluster, v3)\n★=교체 항목', fontsize=10)
    ax.set_xlabel('cluster'); ax.set_ylabel('outcome metric')
    ax.tick_params(axis='x', labelsize=8)
    ax.tick_params(axis='y', labelsize=8)
    # 교체 항목 행 강조 (y축 레이블에 ★ 표시)
    ylabels = ax.get_yticklabels()
    for lbl in ylabels:
        if lbl.get_text() in replaced_labels:
            lbl.set_fontweight('bold')
            lbl.set_text('★ ' + lbl.get_text())
    ax.set_yticklabels(ylabels)

# (하단 좌) component 크기 분포
ax = axes[1, 0]
sizes_dist = sorted([len(c) for c in comps], reverse=True)
ax.bar(range(len(sizes_dist)), sizes_dist, color='#5475a8')
ax.set_yscale('log')
ax.set_title(f'Mapper 연결 성분 크기 분포 ({len(comps)}개, 11y v3)', fontsize=10)
ax.set_xlabel('component rank'); ax.set_ylabel('node 수 (log)')
ax.grid(alpha=0.3)

# (하단 우) v2 vs v3 교체 4개 metric 차분 상관 비교 막대그래프
ax = axes[1, 1]
if os.path.exists(v2_path) and len(oc_corr) > 0:
    v2_df = pd.read_csv(v2_path)
    compare_rows = []
    replaced_old = {v[0]: (k, v[1]) for k, v in REPLACED.items()}
    for old_m, (new_m, field) in replaced_old.items():
        for cl in clusters:
            old_row = v2_df[(v2_df['metric']==old_m) & (v2_df['cluster']==cl)]
            new_row = oc_corr[(oc_corr['metric']==new_m) & (oc_corr['cluster']==cl)]
            old_c = float(old_row['corr_diff'].values[0]) if len(old_row) > 0 else np.nan
            new_c = float(new_row['corr_diff'].values[0]) if len(new_row) > 0 else np.nan
            compare_rows.append({
                'field': field,
                'cluster': CLU_LABEL.get(cl, str(cl)),
                'v2_corr': old_c,
                'v3_corr': new_c,
                'label': f'{field}\n{CLU_LABEL.get(cl,"?")}',
            })
    cmp_df = pd.DataFrame(compare_rows).dropna(subset=['v2_corr','v3_corr'])
    if len(cmp_df) > 0:
        x = np.arange(len(cmp_df))
        w = 0.35
        ax.bar(x - w/2, cmp_df['v2_corr'], w, label='v2(구)', color='#5475a8', alpha=0.8)
        ax.bar(x + w/2, cmp_df['v3_corr'], w, label='v3(교체)', color='#c87f5a', alpha=0.8)
        ax.axhline(0, color='k', linewidth=0.8)
        ax.set_xticks(x)
        ax.set_xticklabels(cmp_df['label'], fontsize=6, rotation=45, ha='right')
        ax.set_ylabel('차분 상관계수')
        ax.set_title('v2 vs v3: 교체 4개 metric 차분 상관 비교', fontsize=10)
        ax.legend(fontsize=8); ax.grid(alpha=0.3, axis='y')
else:
    ax.text(0.5, 0.5, 'v2 비교 데이터 없음', ha='center', va='center',
            transform=ax.transAxes, fontsize=12)
    ax.set_title('v2 vs v3 비교 (데이터 없음)', fontsize=10)

plt.tight_layout()
save_and_resize(fig, os.path.join(OUT_DIR, 'H4_cluster_outcome_panel_11y_v3.png'))

# ============================================================
# Figure C: 출연금 비중 Mapper + 분기점 분야 라벨
# ============================================================
print('\n' + '='*70)
print('Figure C: 출연금 비중 Mapper')
print('='*70)
fig, ax = plt.subplots(figsize=(13, 8))
nx.draw_networkx_edges(G, pos, alpha=0.25, width=0.5, ax=ax)
size_arr     = np.array([G.nodes[n]['size'] for n in G.nodes()])
chooyeon_arr = np.array([node_meta[n]['mean_chooyeon'] for n in G.nodes()])
sc = nx.draw_networkx_nodes(G, pos, node_size=15+4*size_arr,
                             node_color=chooyeon_arr, cmap='Reds',
                             vmin=0, vmax=0.6, alpha=0.85, ax=ax)
fig.colorbar(sc, ax=ax, label='평균 chooyeon_pct', shrink=0.7)
top_branches = sorted(branches, key=lambda n: -G.nodes[n]['size'])[:10]
nx.draw_networkx_labels(G, pos,
                        labels={n: node_meta[n]['top_field'] for n in top_branches},
                        font_size=8, font_family=KFONT or 'sans-serif', ax=ax)
ax.set_title(
    f'Mapper (11y v3) — 출연금 비중 + 분기점 분야 라벨\n'
    f'components={len(comps)}, loops={n_loops}, branches={len(branches)}\n'
    f'outcome: 15분야 v3 (교체 4개 반영)',
    fontsize=11
)
ax.axis('off')
plt.tight_layout()
save_and_resize(fig, os.path.join(OUT_DIR, 'H4_mapper_chooyeon_11y_v3.png'))

# ============================================================
# 최종 요약 출력
# ============================================================
print('\n' + '='*70)
print('=== H4 v3 Mapper 분석 요약 (11y + 교체 4개 outcome) ===')
print('='*70)
print(f'  활동 N       = {len(df)} (11y 데이터)')
print(f'  Mapper nodes = {n_nodes}, edges = {n_edges}')
print(f'  Components   = {len(comps)} (0차 베티수)')
print(f'  Loops        = {n_loops} (1차 베티수, LCC 기준)')
print(f'  Branch pts   = {len(branches)}, Endpoints = {len(endpoints)}')
print()
print('  [5y vs 11y vs 11y_v3 비교]')
print('  5y:     components=8,  loops=7')
print(f'  11y(v2): components={len(comps)}, loops={n_loops}')
print(f'  11y(v3): 위상 동일 (Mapper 입력 불변), outcome metric만 교체')
print()
if len(oc_corr) > 0:
    pv_show = oc_corr.pivot(index='metric_label', columns='cluster', values='corr_diff')
    pv_show.columns = [f'{c}:{CLU_LABEL.get(c,"?")}' for c in pv_show.columns]
    print('  [4 클러스터 × 15 outcome 차분 상관 matrix (v3)]')
    print(pv_show.round(3).to_string())
    print()
    # 직관 반대 신호 (부호 확인)
    print('  [직관 반대 신호 탐색]')
    print('  (예: 지출↑ → 재정자립↓, 지출↑ → 범죄↑ 등)')
    for _, row in oc_corr.iterrows():
        flag = ''
        # 교통사망자: 지출↑ → 사망↑ (예상: -)
        if row['metric'] == 'traffic_deaths' and row['corr_diff'] > 0.2:
            flag = '★ 직관반대(사망↑)'
        # 재정자립: 지출↑ → 재정자립↓ (예상: -)
        if row['metric'] == 'fiscal_indep_natl' and row['corr_diff'] > 0.15:
            flag = '★ 직관반대(자립↓예상)'
        # 범죄: 지출↑ → 범죄↑ (예상: -)
        if row['metric'] == 'crime_occurrence' and row['corr_diff'] > 0.2:
            flag = '★ 직관반대(범죄↑)'
        # 온실가스: 지출↑ → 감소 (예상: -)
        if row['metric'] == 'ghg_total' and row['corr_diff'] > 0.2:
            flag = '★ 직관반대(온실↑)'
        # 지니: 복지지출↑ → 불평등↑ (예상: -)
        if row['metric'] == 'wealth_gini' and row['corr_diff'] > 0.2:
            flag = '★ 직관반대(불평등↑)'
        if flag:
            print(f'    {row["clu_label"]} × {row["metric_label"]}: corr={row["corr_diff"]:.3f} {flag}')

print('\n  생성 파일:')
for f in sorted(os.listdir(OUT_DIR)):
    fpath = os.path.join(OUT_DIR, f)
    sz    = os.path.getsize(fpath) // 1024
    print(f'    {f} ({sz} KB)')

con.close()
print('\n완료.')
