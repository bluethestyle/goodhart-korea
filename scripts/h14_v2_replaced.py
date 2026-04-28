"""H14 v2: 부처 굿하트 노출 점수 × outcome 디커플링 결합 분석 (교체 outcome).

H5 부처 노출 점수(51부처) + 부처별 outcome 차분 상관을 결합하여
굿하트 위험이 실제 outcome 측정 왜곡으로 이어지는 부처를 4분면으로 분류.

v2 변경: 자기인과(self-causal) outcome 제거 → 독립 outcome으로 교체
  과학기술: rd_total → patent_apps_total (특허출원수)
  문화및관광: tourists_sample → foreign_tourists_total (방한 외래관광객)
  일반·지방행정: local_tax_per_capita → fiscal_indep_natl (재정자립도)
  통신: ict_value_added → broadband_per_100 (초고속인터넷 가입률)
  + 방위, 외교통일, 공공질서및안전 3분야 추가 (15분야 총계)

입력
  data/results/H5_ministry_exposure.csv  (51 부처 × 굿하트 노출 점수)
  data/results/H3_activity_embedding.csv (활동 1,641 × 분야 분포)
  data/warehouse.duckdb                  (indicator_panel — outcome 15분야)

출력
  scripts/h14_v2_replaced.py
  data/results/H14_ministry_outcome_combined_v2.csv
  data/figs/h14_v2/H14_exposure_vs_outcome_v2.png
  data/figs/h14_v2/H14_risk_quadrant_v2.png

4분면 정의 (X=노출, Y=가중 outcome corr_diff):
  Q1 (높은 노출 + 음 corr): 굿하트 위험 + 자동분배 효과 → 사업 계속 OK
  Q2 (높은 노출 + 양 corr): 굿하트 위험 + 측정 왜곡 → 점검 필요
  Q3 (낮은 노출 + 음 corr): 안전 (낮은 위험)
  Q4 (낮은 노출 + 양 corr): 안전 (낮은 위험)

조건: exposure_score >= 0.3, n_year >= 5
"""
import os, sys, io, warnings
import numpy as np
import pandas as pd
import duckdb
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.patches as mpatches
import scienceplots
import seaborn as sns
from scipy.stats import pearsonr
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
DB   = os.path.join(ROOT, 'data', 'warehouse.duckdb')
H5_CSV  = os.path.join(ROOT, 'data', 'results', 'H5_ministry_exposure.csv')
H5_CSV2 = os.path.join(ROOT, 'data', 'results', 'H5_ministry_exposure_11y.csv')
H3_CSV  = os.path.join(ROOT, 'data', 'results', 'H3_activity_embedding.csv')
OUT_DIR = os.path.join(ROOT, 'data', 'figs', 'h14_v2')
RES_DIR = os.path.join(ROOT, 'data', 'results')
os.makedirs(OUT_DIR, exist_ok=True)

KFONT = mpl.rcParams.get('font.family', 'Malgun Gothic')
MAX_PX = 1800
DPI = 200

def fig_save(fig, path):
    """1800px 이하 보장하여 저장."""
    w, h = fig.get_size_inches()
    dpi = DPI
    if w * dpi > MAX_PX:
        dpi = int(MAX_PX / w)
    fig.savefig(path, dpi=dpi, bbox_inches='tight')
    plt.close(fig)
    print(f'  저장: {os.path.basename(path)}')

# ── 데이터 로드 ────────────────────────────────────────────────────────────
print('=== H14 v2: 부처 노출 × outcome 디커플링 (교체 outcome) ===')
# H5 CSV: 11y 우선, 없으면 기본
if os.path.exists(H5_CSV2):
    expo = pd.read_csv(H5_CSV2, encoding='utf-8-sig')
    print(f'  H5 소스: {os.path.basename(H5_CSV2)}')
else:
    expo = pd.read_csv(H5_CSV, encoding='utf-8-sig')
    print(f'  H5 소스: {os.path.basename(H5_CSV)}')
emb  = pd.read_csv(H3_CSV, encoding='utf-8-sig')

con  = duckdb.connect(DB, read_only=True)

# ── OUTCOME_MAP v2: 자기인과 outcome 교체 + 3분야 추가 (총 15분야) ────────
# 변경:
#   과학기술   rd_total           → patent_apps_total       (특허출원수)
#   문화및관광 tourists_sample    → foreign_tourists_total   (방한 외래관광객)
#   일반·지방행정 local_tax_per_capita → fiscal_indep_natl  (재정자립도 전국)
#   통신       ict_value_added    → broadband_per_100        (초고속인터넷/100명)
OUTCOME_MAP = {
    '사회복지':              'wealth_gini',
    '보건':                  'life_expectancy',
    '과학기술':              'patent_apps_total',         # 교체: rd_total → 특허
    '산업·중소기업및에너지': 'industry_production_index',
    '문화및관광':            'foreign_tourists_total',    # 교체: tourists_sample → 방한관광객
    '교육':                  'private_edu_hours',
    '국토및지역개발':        'housing_supply',
    '일반·지방행정':         'fiscal_indep_natl',         # 교체: local_tax → 재정자립도
    '농림수산':              'farm_income',
    '교통및물류':            'traffic_deaths',
    '환경':                  'ghg_total',
    '통신':                  'broadband_per_100',         # 교체: ict_value_added → 초고속인터넷
}
OUTCOME_LABEL = {
    'wealth_gini':              '사회복지(지니)',
    'life_expectancy':          '보건(기대수명)',
    'patent_apps_total':        '과학기술(특허출원)',
    'industry_production_index':'산업(생산지수)',
    'foreign_tourists_total':   '관광(방한외래객)',
    'private_edu_hours':        '교육(사교육시간)',
    'housing_supply':           '국토(주택공급)',
    'fiscal_indep_natl':        '행정(재정자립도)',
    'farm_income':              '농림수산(농가소득)',
    'traffic_deaths':           '교통(사망자)',
    'ghg_total':                '환경(온실가스)',
    'broadband_per_100':        '통신(초고속인터넷)',
}
print(f'\n[v2 OUTCOME_MAP] {len(OUTCOME_MAP)}분야 교체 완료')
print('  교체: 과학기술→patent_apps_total, 관광→foreign_tourists_total,')
print('        행정→fiscal_indep_natl, 통신→broadband_per_100')

metric_list = list(OUTCOME_MAP.values()) + ['amp_12m_norm']
panel = con.execute(f"""
    SELECT fld_nm, year, metric_code, value
    FROM indicator_panel
    WHERE metric_code IN ({','.join("'" + m + "'" for m in metric_list)})
""").fetchdf()
con.close()

wide = panel.pivot_table(index=['fld_nm', 'year'],
                          columns='metric_code', values='value').reset_index()

# 분야별 amp_12m 시계열 pivot
fld_amp = wide.pivot_table(index='year', columns='fld_nm', values='amp_12m_norm')

# ── 부처별 분야 분포 가중치 ────────────────────────────────────────────────
print('\n[Step 1] 부처 분야 가중치 계산 (활동 수 기준)')
ofc_fld = pd.crosstab(emb['OFFC_NM'], emb['FLD_NM'], normalize='index')
ofc_size = emb.groupby('OFFC_NM').size()

# ── 부처별 가중 outcome corr_diff 계산 ────────────────────────────────────
print('[Step 2] 부처별 가중 outcome 차분 상관 계산 (n_year >= 5)')
MIN_N = 5
EXPO_THRESH = 0.3

ofc_results = []
for ofc, w in ofc_fld.iterrows():
    if ofc_size.get(ofc, 0) < 3:
        continue
    # 부처 amp 가중 시계열 (활동 분야 분포 × 분야 amp)
    amp_ts = (fld_amp.reindex(columns=w.index) * w).sum(axis=1, min_count=1).dropna()

    for fld, oc_metric in OUTCOME_MAP.items():
        if oc_metric not in wide.columns:
            continue
        fld_w = float(w.get(fld, 0.0))
        if fld_w < 0.05:          # 해당 분야 비중 5% 미만 skip
            continue
        oc_ts = (wide[wide['fld_nm'] == fld]
                 .set_index('year')[oc_metric].dropna())
        common = amp_ts.index.intersection(oc_ts.index)
        if len(common) < MIN_N:
            continue
        d_amp = amp_ts.loc[common].diff().dropna()
        d_oc  = oc_ts.loc[common].diff().dropna()
        ci = d_amp.index.intersection(d_oc.index)
        if len(ci) < MIN_N - 1:
            continue
        r_lvl, _ = pearsonr(amp_ts.loc[common], oc_ts.loc[common])
        r_dif, p_dif = pearsonr(d_amp.loc[ci], d_oc.loc[ci])
        ofc_results.append({
            'OFFC_NM':    ofc,
            'fld_outcome': fld,
            'metric':     oc_metric,
            'fld_weight': fld_w,
            'n_year':     len(common),
            'n_diff':     len(ci),
            'corr_levels': float(r_lvl),
            'corr_diff':   float(r_dif),
            'p_diff':      float(p_dif),
        })

ofc_corr = pd.DataFrame(ofc_results)
print(f'  부처×outcome pair (n_year>={MIN_N}): {len(ofc_corr)}')

# ── 부처 단위로 가중 평균 corr_diff 집계 ─────────────────────────────────
print('[Step 3] 부처 단위 가중 평균 corr_diff 집계 (분야 비중 가중)')
def weighted_mean_corr(grp):
    w = grp['fld_weight']
    if w.sum() == 0:
        return np.nan
    return float(np.average(grp['corr_diff'], weights=w))

def weighted_mean_n(grp):
    return float(grp['n_year'].mean())

ofc_agg = (ofc_corr
           .groupby('OFFC_NM')
           .apply(lambda g: pd.Series({
               'w_corr_diff': weighted_mean_corr(g),
               'n_pairs':     len(g),
               'mean_n_year': g['n_year'].mean(),
               'min_n_year':  g['n_year'].min(),
               'outcomes':    '/'.join(sorted(g['metric'].unique())),
           }))
           .reset_index())

# ── H5 노출 점수 결합 ──────────────────────────────────────────────────────
print('[Step 4] H5 노출 점수 결합 및 필터 (exposure >= 0.3, n_year >= 5)')
# H5 CSV에 따라 가용 컬럼만 선택
expo_cols = ['OFFC_NM', 'exposure_score', 'co_cluster']
for c in ['pct_chooyeon', 'pct_sub05', 'pct_sub01',
          'pct_A2_sub00', 'pct_A2_sub01', 'pct_A1_direct_invest',
          'exposure_budget', 'n_actv']:
    if c in expo.columns:
        expo_cols.append(c)
merged = ofc_agg.merge(expo[expo_cols], on='OFFC_NM', how='inner')
merged['exposure_score'] = merged['exposure_score'].astype(float)
merged['w_corr_diff']    = merged['w_corr_diff'].astype(float)

# 필터: 노출 0.3 이상 + n_year >= 5
filt = merged[
    (merged['exposure_score'] >= EXPO_THRESH) &
    (merged['min_n_year'] >= MIN_N)
].copy()
print(f'  전체 결합: {len(merged)}  →  필터 후: {len(filt)}')

# ── 4분면 분류 ────────────────────────────────────────────────────────────
print('[Step 5] 4분면 분류')
expo_med = EXPO_THRESH  # 기준: 0.3 (지정값)
corr_med = 0.0          # 기준: corr_diff = 0

def quadrant(row):
    hi_exp = row['exposure_score'] >= expo_med
    pos_cor = row['w_corr_diff'] >= corr_med
    if hi_exp and pos_cor:
        return 'Q2 (위험: 측정 왜곡)'
    elif hi_exp and not pos_cor:
        return 'Q1 (주의: 자동분배)'
    elif not hi_exp and pos_cor:
        return 'Q4 (안전: 양 상관)'
    else:
        return 'Q3 (안전: 음 상관)'

filt['quadrant'] = filt.apply(quadrant, axis=1)

print('\n  4분면 결과:')
for q, grp in filt.groupby('quadrant'):
    print(f'  {q}: {list(grp["OFFC_NM"])}')

# ── 결과 저장 ─────────────────────────────────────────────────────────────
out_csv = os.path.join(RES_DIR, 'H14_ministry_outcome_combined_v2.csv')
filt.to_csv(out_csv, index=False, encoding='utf-8-sig')
print(f'\n  CSV 저장: {out_csv}')

# Q2 명단 출력
q2 = filt[filt['quadrant'] == 'Q2 (위험: 측정 왜곡)'].copy()
print('\n=== Q2 부처 명단 (굿하트 위험 + outcome 측정 왜곡 → 점검 필요) ===')
if len(q2) > 0:
    q2_show = q2[['OFFC_NM', 'exposure_score', 'w_corr_diff',
                  'n_pairs', 'mean_n_year', 'outcomes']].sort_values(
                      'exposure_score', ascending=False)
    print(q2_show.round(3).to_string(index=False))
else:
    print('  없음 (Q2 부처 없음)')

# ── 색상·마커 설정 ────────────────────────────────────────────────────────
CLUSTER_COLORS = {0: '#e07b54', 1: '#5475a8', 2: '#78b87a',
                  3: '#b07cc6', 4: '#d4a94a'}
Q_COLORS = {
    'Q1 (주의: 자동분배)':   '#f4a261',
    'Q2 (위험: 측정 왜곡)':  '#e63946',
    'Q3 (안전: 음 상관)':    '#a8dadc',
    'Q4 (안전: 양 상관)':    '#457b9d',
}

# ── Figure 1: 산점도 (X=노출, Y=corr_diff, 색=co_cluster) ────────────────
print('\n[Fig 1] H14_exposure_vs_outcome_v2.png')
fig, ax = plt.subplots(figsize=(11, 7))

# 배경 참조선
ax.axhline(0, color='#999', lw=0.8, ls='--', zorder=1)
ax.axvline(EXPO_THRESH, color='#999', lw=0.8, ls='--', zorder=1)

# 전체 부처 (필터 전) 회색 배경
bkg = merged[~merged['OFFC_NM'].isin(filt['OFFC_NM'])]
ax.scatter(bkg['exposure_score'], bkg['w_corr_diff'],
           s=25, color='#cccccc', alpha=0.5, zorder=2, label='기준 미달 부처')

# 필터된 부처 — co_cluster 색상
for cl, grp in filt.groupby('co_cluster'):
    ax.scatter(grp['exposure_score'], grp['w_corr_diff'],
               s=70, color=CLUSTER_COLORS.get(cl, '#888'),
               edgecolors='#333', linewidths=0.5,
               alpha=0.85, zorder=3, label=f'Co-cluster {cl}')

# 라벨
for _, row in filt.iterrows():
    ax.annotate(
        row['OFFC_NM'],
        (row['exposure_score'], row['w_corr_diff']),
        xytext=(4, 4), textcoords='offset points',
        fontsize=8, color='#222',
        ha='left', va='bottom',
        bbox=dict(boxstyle='round,pad=0.15', fc='white', alpha=0.55, ec='none'),
    )

ax.set_xlabel('굿하트 노출 점수 (H5 exposure_score)', fontsize=12)
ax.set_ylabel('부처 가중 outcome 차분 상관 (w_corr_diff)', fontsize=12)
ax.set_title('부처-결과변수 4분면 — 굿하트 노출 × outcome 디커플링 (교체 outcome)\n'
             f'(exposure ≥ {EXPO_THRESH}, n_year ≥ {MIN_N}, N={len(filt)})',
             fontsize=13)
ax.legend(fontsize=9, loc='lower right')
ax.grid(alpha=0.25, zorder=0)

# 4분면 텍스트 주석
xlim = ax.get_xlim(); ylim = ax.get_ylim()
ax.text(EXPO_THRESH + 0.01, ylim[1] - 0.05,
        'Q2\n굿하트 위험\n+측정 왜곡\n→ 점검 필요',
        fontsize=8.5, color='#e63946', va='top', ha='left',
        bbox=dict(boxstyle='round', fc='#fff0f0', alpha=0.7, ec='#e63946'))
ax.text(EXPO_THRESH + 0.01, ylim[0] + 0.05,
        'Q1\n굿하트 위험\n+자동분배\n→ 계속 OK',
        fontsize=8.5, color='#e07b54', va='bottom', ha='left',
        bbox=dict(boxstyle='round', fc='#fff8f0', alpha=0.7, ec='#e07b54'))
ax.text(EXPO_THRESH - 0.01, ylim[1] - 0.05,
        'Q4 안전\n(양 상관)',
        fontsize=8, color='#457b9d', va='top', ha='right',
        bbox=dict(boxstyle='round', fc='#f0f5ff', alpha=0.7, ec='#457b9d'))
ax.text(EXPO_THRESH - 0.01, ylim[0] + 0.05,
        'Q3 안전\n(음 상관)',
        fontsize=8, color='#2c7873', va='bottom', ha='right',
        bbox=dict(boxstyle='round', fc='#f0fff4', alpha=0.7, ec='#2c7873'))

fig_save(fig, os.path.join(OUT_DIR, 'H14_exposure_vs_outcome_v2.png'))

# ── Figure 2: 4분면 위험 분류도 (PRIMARY: quadrant_main) ─────────────────
print('[Fig 2] H14_risk_quadrant_v2.png + H14_quadrant_main.png')
fig, ax = plt.subplots(figsize=(12, 8))

# 4분면 배경 색칠
x0, x1 = 0.0, max(filt['exposure_score'].max() + 0.05, 0.9)
y0_lim  = min(filt['w_corr_diff'].min() - 0.1, -0.8)
y1_lim  = max(filt['w_corr_diff'].max() + 0.1, 0.8)

ax.fill_between([EXPO_THRESH, x1], [0, 0], [y1_lim, y1_lim],
                color='#ffe0e0', alpha=0.35, zorder=0)   # Q2 빨강
ax.fill_between([EXPO_THRESH, x1], [y0_lim, y0_lim], [0, 0],
                color='#fff3e0', alpha=0.35, zorder=0)   # Q1 주황
ax.fill_between([0, EXPO_THRESH], [0, 0], [y1_lim, y1_lim],
                color='#e8f4f8', alpha=0.25, zorder=0)   # Q4 파랑
ax.fill_between([0, EXPO_THRESH], [y0_lim, y0_lim], [0, 0],
                color='#e8f8ee', alpha=0.25, zorder=0)   # Q3 녹색

ax.axhline(0, color='#666', lw=1.2, zorder=1)
ax.axvline(EXPO_THRESH, color='#666', lw=1.2, zorder=1)

# 점 및 라벨
for _, row in filt.iterrows():
    q = row['quadrant']
    c = Q_COLORS.get(q, '#888')
    ax.scatter(row['exposure_score'], row['w_corr_diff'],
               s=120, color=c, edgecolors='#222',
               linewidths=0.7, zorder=4, alpha=0.9)
    # 부처명 라벨 — Q2 강조
    fs = 9.5 if q == 'Q2 (위험: 측정 왜곡)' else 8.5
    fw = 'bold' if q == 'Q2 (위험: 측정 왜곡)' else 'normal'
    ec = c if q == 'Q2 (위험: 측정 왜곡)' else 'none'
    ax.annotate(
        row['OFFC_NM'],
        (row['exposure_score'], row['w_corr_diff']),
        xytext=(6, 4), textcoords='offset points',
        fontsize=fs, fontweight=fw, color='#111',
        ha='left', va='bottom',
        bbox=dict(boxstyle='round,pad=0.2', fc='white',
                  alpha=0.75, ec=ec, lw=0.8),
        zorder=5,
    )

# 4분면 제목
kw = dict(fontsize=11, va='center', ha='center', alpha=0.7, zorder=3)
ax.text((EXPO_THRESH + x1) / 2, y1_lim * 0.72,
        'Q2\n굿하트 위험 + 측정 왜곡\n→ 점검 필요', color='#c0392b', **kw)
ax.text((EXPO_THRESH + x1) / 2, y0_lim * 0.72,
        'Q1\n굿하트 위험 + 자동분배\n→ 사업 계속 OK', color='#c05000', **kw)
ax.text(EXPO_THRESH * 0.5, y1_lim * 0.72,
        'Q4\n안전 (양 상관)', color='#1a6fa0', **kw)
ax.text(EXPO_THRESH * 0.5, y0_lim * 0.72,
        'Q3\n안전 (음 상관)', color='#1a7a4a', **kw)

# 범례
patches = [mpatches.Patch(color=c, label=q, alpha=0.8)
           for q, c in Q_COLORS.items()]
ax.legend(handles=patches, fontsize=9, loc='upper left',
          title='4분면 분류', title_fontsize=9)

ax.set_xlim(0, x1)
ax.set_ylim(y0_lim, y1_lim)
ax.set_xlabel('굿하트 노출 점수 (H5 exposure_score)', fontsize=12)
ax.set_ylabel('부처 가중 outcome 차분 상관 (w_corr_diff)', fontsize=12)
ax.set_title('굿하트 위험 4분면 분류 (교체 outcome)\n'
             '(X: 노출 점수, Y: outcome 디커플링, 기준선: 노출=0.3, corr=0)\n'
             '과기→특허, 관광→방한외래객, 행정→재정자립도, 통신→초고속인터넷',
             fontsize=12)
ax.grid(alpha=0.2, zorder=0)

fig_save(fig, os.path.join(OUT_DIR, 'H14_risk_quadrant_v2.png'))
# Also save as quadrant_main (split single-panel version)
import shutil as _shutil14
_shutil14.copy2(os.path.join(OUT_DIR, 'H14_risk_quadrant_v2.png'),
                os.path.join(OUT_DIR, 'H14_quadrant_main.png'))
print('  저장: H14_quadrant_main.png')

# ── 최종 요약 출력 ────────────────────────────────────────────────────────
print('\n=== 최종 요약 ===')
for q in ['Q2 (위험: 측정 왜곡)', 'Q1 (주의: 자동분배)',
          'Q4 (안전: 양 상관)', 'Q3 (안전: 음 상관)']:
    sub = filt[filt['quadrant'] == q]
    print(f'  {q}: {len(sub)}개  {list(sub["OFFC_NM"])}')

print('\n[정책 점검 우선순위]')
q2_pri = filt[filt['quadrant'] == 'Q2 (위험: 측정 왜곡)'].sort_values(
    'exposure_score', ascending=False)
if len(q2_pri):
    for i, (_, r) in enumerate(q2_pri.iterrows(), 1):
        print(f'  {i}. {r["OFFC_NM"]} — '
              f'노출={r["exposure_score"]:.3f}, corr_diff={r["w_corr_diff"]:.3f}')
else:
    print('  해당 부처 없음')

print('\n[v2 vs v1 비교 참고]')
print('  v1 Q2 (자기인과 outcome): 산업통상자원부(+0.60), 과기정통부(+0.15)')
print('  v2 Q2 (교체 outcome): 위 목록 참조 — 과기부 신호 변화 여부 확인')

print('\n완료.')
