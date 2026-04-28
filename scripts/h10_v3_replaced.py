"""H10 v3: CPI 외생 통제 — outcome 4개 교체 후 재검증.

교체 내역 (H6 v3와 동일):
  과학기술:      rd_total          → patent_apps_total
  문화및관광:    tourists_sample   → foreign_tourists_total
  일반·지방행정: local_tax_per_capita → fiscal_indep_natl
  통신:          ict_value_added   → broadband_per_100

비교:
  - 교체 전 H10: 부호+70% 유지 13/15 (87%)
  - 교체 후 H10 v3: ?/15
  - 자기 인과 가능성 있던 rd_total, ict_value_added 제거 → 신호 명확도

산출:
  data/results/H10_macro_control_corr_v3.csv
  data/figs/h10_v3/H10_macro_control_compare_v3.png
"""
import os, sys, io, json, warnings
import numpy as np
import pandas as pd
import duckdb
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns
from scipy.stats import pearsonr

warnings.filterwarnings('ignore')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB   = os.path.join(ROOT, 'data', 'warehouse.duckdb')
RAW  = os.path.join(ROOT, 'data', 'external', 'bok_data')
OUT  = os.path.join(ROOT, 'data', 'figs', 'h10_v3')
RES  = os.path.join(ROOT, 'data', 'results')
os.makedirs(OUT, exist_ok=True)

KFONT = None
for f in ['Malgun Gothic', 'Noto Sans CJK KR', 'AppleGothic']:
    if any(f in fn.name for fn in mpl.font_manager.fontManager.ttflist):
        mpl.rcParams['font.family'] = f
        KFONT = f
        break
mpl.rcParams['axes.unicode_minus'] = False

# ============================================================
# Step 1: CPI 시계열 로드
# ============================================================
print('='*70)
print('Step 1: CPI (901Y009 / 연)')
print('='*70)
d = json.load(open(f'{RAW}/cpi_annual.json', encoding='utf-8'))
rows = d['StatisticSearch']['row']
cpi = pd.DataFrame(rows)
cpi['year']    = pd.to_numeric(cpi['TIME'],       errors='coerce').astype('Int64')
cpi['cpi']     = pd.to_numeric(cpi['DATA_VALUE'], errors='coerce')
cpi = cpi[['year','cpi']].dropna().sort_values('year').reset_index(drop=True)
cpi['cpi_pct'] = cpi['cpi'].pct_change() * 100
print(f'  CPI {len(cpi)} years: {cpi["year"].min()} ~ {cpi["year"].max()}')
print(f'  최근 5년 CPI: {cpi.tail(5).to_dict("records")}')

# ============================================================
# Step 2: 분야 outcome + amp_12m + CPI 결합
#         — 교체 4개 metric 포함
# ============================================================
con = duckdb.connect(DB, read_only=True)
panel = con.execute("""
    SELECT fld_nm, year, metric_code, value FROM indicator_panel
    WHERE metric_code IN (
        'amp_12m_norm',
        'wealth_gini',
        'life_expectancy',
        'patent_apps_total',
        'industry_production_index',
        'foreign_tourists_total',
        'housing_supply',
        'fiscal_indep_natl',
        'private_edu_hours',
        'farm_income',
        'fishery_income',
        'traffic_deaths',
        'traffic_accidents',
        'ghg_total', 'ghg_net', 'ghg_energy',
        'broadband_per_100',
        'oda_total',
        'crime_occurrence',
        'defense_op_margin'
    )
""").fetchdf()
con.close()

wide = panel.pivot_table(index=['fld_nm','year'], columns='metric_code',
                         values='value').reset_index()
wide = wide.merge(cpi[['year','cpi','cpi_pct']], on='year', how='left')

# v3 OUTCOME_MAP — 4개 교체
OUTCOME_MAP_V3 = {
    '사회복지':             'wealth_gini',
    '보건':                 'life_expectancy',
    '과학기술':             'patent_apps_total',       # rd_total → 교체
    '산업·중소기업및에너지': 'industry_production_index',
    '문화및관광':           'foreign_tourists_total',  # tourists_sample → 교체
    '교육':                 'private_edu_hours',
    '국토및지역개발':       'housing_supply',
    '일반·지방행정':        'fiscal_indep_natl',       # local_tax_per_capita → 교체
    '농림수산':             'farm_income',
    '교통및물류':           'traffic_deaths',
    '환경':                 'ghg_total',
    '통신':                 'broadband_per_100',       # ict_value_added → 교체
    '통일·외교':            'oda_total',
    '공공질서및안전':       'crime_occurrence',
    '국방':                 'defense_op_margin',
}

# 교체 전 원본 매핑 (비교용)
OUTCOME_MAP_ORIG = {
    '사회복지':             'wealth_gini',
    '보건':                 'life_expectancy',
    '과학기술':             'rd_total',
    '산업·중소기업및에너지': 'industry_production_index',
    '문화및관광':           'tourists_sample',
    '교육':                 'private_edu_hours',
    '국토및지역개발':       'housing_supply',
    '일반·지방행정':        'local_tax_per_capita',
    '농림수산':             'farm_income',
    '교통및물류':           'traffic_deaths',
    '환경':                 'ghg_total',
    '통신':                 'ict_value_added',
    '통일·외교':            'oda_total',
    '공공질서및안전':       'crime_occurrence',
    '국방':                 'defense_op_margin',
}

REPLACED = {fld for fld, oc in OUTCOME_MAP_V3.items()
            if OUTCOME_MAP_ORIG.get(fld) != oc}

print(f'\n교체 분야: {sorted(REPLACED)}')

# ============================================================
# Step 3: CPI 잔차 상관 계산 함수
# ============================================================
def compute_corr(wide_df, outcome_map, cpi_df):
    results = []
    for fld, oc in outcome_map.items():
        sub = wide_df[wide_df['fld_nm'] == fld].sort_values('year').copy()
        if oc not in sub.columns:
            print(f'  [MISSING] {fld}: {oc} 없음')
            continue
        sub = sub[['year','amp_12m_norm', oc, 'cpi','cpi_pct']].dropna(
            subset=['amp_12m_norm', oc])
        if len(sub) < 5:
            print(f'  [SKIP] {fld}: n={len(sub)} < 5')
            continue
        sub['d_amp'] = sub['amp_12m_norm'].diff()
        sub['d_oc']  = sub[oc].diff()
        sub = sub.dropna()
        if len(sub) < 4:
            continue

        # raw 상관
        r_raw, p_raw = pearsonr(sub['d_amp'], sub['d_oc'])

        # outcome 차분에서 CPI 효과 제거
        if sub['cpi_pct'].std() > 0:
            sl = np.polyfit(sub['cpi_pct'], sub['d_oc'], 1)
            d_oc_resid = sub['d_oc'].values - (sl[0] * sub['cpi_pct'].values + sl[1])
        else:
            d_oc_resid = sub['d_oc'].values

        # amp 차분에서도 CPI 효과 제거
        if sub['cpi_pct'].std() > 0:
            sl2 = np.polyfit(sub['cpi_pct'], sub['d_amp'], 1)
            d_amp_resid = sub['d_amp'].values - (sl2[0] * sub['cpi_pct'].values + sl2[1])
        else:
            d_amp_resid = sub['d_amp'].values

        if len(d_oc_resid) >= 3 and np.std(d_oc_resid) > 0 and np.std(d_amp_resid) > 0:
            r_resid, p_resid = pearsonr(d_amp_resid, d_oc_resid)
        else:
            r_resid, p_resid = np.nan, np.nan

        results.append({
            'fld': fld, 'outcome': oc, 'n': len(sub),
            'corr_raw':       r_raw,
            'corr_resid_CPI': r_resid,
            'delta':          r_resid - r_raw,
            'p_raw':          p_raw,
            'p_resid':        p_resid,
        })
    return pd.DataFrame(results)

# ============================================================
# Step 4: 원본 H10 결과 재현 (CSV가 있으면 로드, 없으면 재계산)
# ============================================================
print('\n' + '='*70)
print('Step 4: 원본 H10 결과 (교체 전)')
print('='*70)

orig_csv = os.path.join(RES, 'H10_macro_control_corr.csv')
if os.path.exists(orig_csv):
    df_orig = pd.read_csv(orig_csv, encoding='utf-8-sig')
    print(f'  원본 CSV 로드: {orig_csv}  (N={len(df_orig)})')
else:
    # 원본 메트릭도 wide에 없을 수 있으므로 조건부 계산
    con2 = duckdb.connect(DB, read_only=True)
    panel_orig = con2.execute("""
        SELECT fld_nm, year, metric_code, value FROM indicator_panel
        WHERE metric_code IN (
            'amp_12m_norm','wealth_gini','life_expectancy',
            'rd_total','industry_production_index','tourists_sample',
            'housing_supply','local_tax_per_capita','private_edu_hours',
            'farm_income','traffic_deaths','ghg_total',
            'ict_value_added','oda_total','crime_occurrence','defense_op_margin'
        )
    """).fetchdf()
    con2.close()
    wide_orig = panel_orig.pivot_table(index=['fld_nm','year'], columns='metric_code',
                                       values='value').reset_index()
    wide_orig = wide_orig.merge(cpi[['year','cpi','cpi_pct']], on='year', how='left')
    df_orig = compute_corr(wide_orig, OUTCOME_MAP_ORIG, cpi)
    print('  원본 재계산 완료')

df_orig['sign_change'] = np.sign(df_orig['corr_raw']) != np.sign(df_orig['corr_resid_CPI'])
df_orig['abs_weaken']  = df_orig['corr_resid_CPI'].abs() < df_orig['corr_raw'].abs() * 0.7
kept_orig = ((~df_orig['sign_change']) & (~df_orig['abs_weaken'])).sum()
print(f'  원본 부호+70% 유지: {kept_orig}/{len(df_orig)} ({100*kept_orig/len(df_orig):.0f}%)')
print(df_orig.round(3).to_string(index=False))

# ============================================================
# Step 5: v3 (교체 후) 계산
# ============================================================
print('\n' + '='*70)
print('Step 5: v3 (교체 후) — raw vs CPI-residual corr_diff')
print('='*70)
df_v3 = compute_corr(wide, OUTCOME_MAP_V3, cpi)
df_v3['sign_change'] = np.sign(df_v3['corr_raw']) != np.sign(df_v3['corr_resid_CPI'])
df_v3['abs_weaken']  = df_v3['corr_resid_CPI'].abs() < df_v3['corr_raw'].abs() * 0.7
df_v3['replaced']    = df_v3['fld'].isin(REPLACED)

kept_v3 = ((~df_v3['sign_change']) & (~df_v3['abs_weaken'])).sum()
print(df_v3.round(3).to_string(index=False))
print()
print(f'  v3 부호 반전: {df_v3["sign_change"].sum()}/{len(df_v3)}')
print(f'  v3 30%+ 약화: {df_v3["abs_weaken"].sum()}/{len(df_v3)}')
print(f'  v3 부호+70% 유지: {kept_v3}/{len(df_v3)} ({100*kept_v3/len(df_v3):.0f}%)')

# 교체 4개 분야 상세
print('\n--- 교체 4개 분야 원본 vs v3 ---')
for fld in sorted(REPLACED):
    oc_orig = OUTCOME_MAP_ORIG[fld]
    oc_v3   = OUTCOME_MAP_V3[fld]
    row_o = df_orig[df_orig['fld'] == fld]
    row_v = df_v3[df_v3['fld'] == fld]
    if len(row_o) and len(row_v):
        ro = row_o.iloc[0]
        rv = row_v.iloc[0]
        print(f'  [{fld}]')
        print(f'    원본 ({oc_orig}): raw={ro["corr_raw"]:.3f}  CPI잔차={ro["corr_resid_CPI"]:.3f}  Δ={ro["delta"]:.3f}')
        print(f'    v3   ({oc_v3}): raw={rv["corr_raw"]:.3f}  CPI잔차={rv["corr_resid_CPI"]:.3f}  Δ={rv["delta"]:.3f}')
    elif len(row_v):
        rv = row_v.iloc[0]
        print(f'  [{fld}] 원본 없음 → v3 ({oc_v3}): raw={rv["corr_raw"]:.3f}  CPI잔차={rv["corr_resid_CPI"]:.3f}')
    else:
        print(f'  [{fld}] v3 데이터 없음 (metric={oc_v3})')

# CSV 저장
df_v3.to_csv(f'{RES}/H10_macro_control_corr_v3.csv', index=False, encoding='utf-8-sig')
print(f'\n  CSV → {RES}/H10_macro_control_corr_v3.csv')

# ============================================================
# Figure: 교체 전후 비교 (3-panel)
# ============================================================
# 공통 분야만 merge
merged = df_orig[['fld','outcome','corr_raw','corr_resid_CPI']].rename(
    columns={'outcome':'outcome_orig',
             'corr_raw':'raw_orig','corr_resid_CPI':'resid_orig'}).merge(
    df_v3[['fld','outcome','corr_raw','corr_resid_CPI','replaced']].rename(
        columns={'outcome':'outcome_v3',
                 'corr_raw':'raw_v3','corr_resid_CPI':'resid_v3'}),
    on='fld', how='outer')

fig, axes = plt.subplots(1, 3, figsize=(18, 6))
fig.suptitle('H10 v3: CPI 통제 후 corr_diff — 교체 전후 비교', fontsize=13)

# ── Panel A: raw corr 산점도 (원본 vs v3)
ax = axes[0]
colors = ['#a85454' if r else '#5475a8' for r in merged['replaced'].fillna(False)]
ax.scatter(merged['raw_orig'], merged['raw_v3'], s=65, c=colors, alpha=0.85, zorder=3)
ax.plot([-1, 1], [-1, 1], '--', color='#888', alpha=0.5, label='identity')
ax.axhline(0, color='#888', lw=0.5); ax.axvline(0, color='#888', lw=0.5)
for _, r in merged.iterrows():
    ax.annotate(f'{str(r["fld"])[:6]}', (r['raw_orig'], r['raw_v3']),
                xytext=(4, 3), textcoords='offset points', fontsize=7)
ax.set_xlabel('raw corr_diff — 원본 H10')
ax.set_ylabel('raw corr_diff — v3 (교체)')
ax.set_title('raw corr: 원본 vs v3\n(빨강=교체 분야)')
ax.legend(fontsize=8)
ax.grid(alpha=0.3)
ax.set_xlim(-1, 1); ax.set_ylim(-1, 1)

# ── Panel B: CPI잔차 corr 산점도 (원본 vs v3)
ax = axes[1]
ax.scatter(merged['resid_orig'], merged['resid_v3'], s=65, c=colors, alpha=0.85, zorder=3)
ax.plot([-1, 1], [-1, 1], '--', color='#888', alpha=0.5, label='identity')
ax.axhline(0, color='#888', lw=0.5); ax.axvline(0, color='#888', lw=0.5)
for _, r in merged.iterrows():
    ax.annotate(f'{str(r["fld"])[:6]}', (r['resid_orig'], r['resid_v3']),
                xytext=(4, 3), textcoords='offset points', fontsize=7)
ax.set_xlabel('CPI잔차 corr — 원본 H10')
ax.set_ylabel('CPI잔차 corr — v3 (교체)')
ax.set_title(f'CPI잔차 corr: 원본 vs v3\n원본 {kept_orig}/{len(df_orig)} → v3 {kept_v3}/{len(df_v3)} (부호+70%유지)')
ax.legend(fontsize=8)
ax.grid(alpha=0.3)
ax.set_xlim(-1, 1); ax.set_ylim(-1, 1)

# ── Panel C: 분야별 raw vs CPI잔차 bar (v3)
ax = axes[2]
df_sorted = df_v3.sort_values('corr_raw')
y = np.arange(len(df_sorted))
bar_colors_raw   = ['#a85454' if r else '#5475a8' for r in df_sorted['replaced']]
bar_colors_resid = ['#e89090' if r else '#80a0cc' for r in df_sorted['replaced']]
ax.barh(y - 0.2, df_sorted['corr_raw'],       height=0.4,
        color=bar_colors_raw,   alpha=0.9, label='raw (v3)')
ax.barh(y + 0.2, df_sorted['corr_resid_CPI'], height=0.4,
        color=bar_colors_resid, alpha=0.9, label='CPI잔차 (v3)')
ax.set_yticks(y)
ax.set_yticklabels(df_sorted['fld'], fontsize=8)
ax.axvline(0, color='#888', lw=0.5)
ax.set_xlabel('corr_diff')
ax.set_title(f'v3 분야별 corr_diff\n(진한색=교체, 연한색=비교체)\n부호+70%유지: {kept_v3}/{len(df_v3)}')
ax.legend(fontsize=8)
ax.grid(alpha=0.3, axis='x')

plt.tight_layout()

# max 1800px 제한
fig.canvas.draw()
w_in, h_in = fig.get_size_inches()
dpi = min(130, int(1800 / max(w_in * 130, 1)))
dpi = max(dpi, 80)
fig.savefig(f'{OUT}/H10_macro_control_compare_v3.png',
            dpi=dpi, bbox_inches='tight')
plt.close()

# ============================================================
# 최종 요약 출력
# ============================================================
print('\n' + '='*70)
print('최종 비교 요약')
print('='*70)
print(f'  교체 전 H10  — 부호+70% 유지: {kept_orig}/{len(df_orig)} ({100*kept_orig/len(df_orig):.0f}%)')
print(f'  교체 후 H10 v3 — 부호+70% 유지: {kept_v3}/{len(df_v3)} ({100*kept_v3/len(df_v3):.0f}%)')
print()
print('  교체 분야별 CPI잔차 corr 비교:')
for fld in sorted(REPLACED):
    row_v = df_v3[df_v3['fld'] == fld]
    if len(row_v):
        rv = row_v.iloc[0]
        sc = '반전' if rv['sign_change'] else ('약화' if rv['abs_weaken'] else '유지')
        print(f'    {fld:12s}: {OUTCOME_MAP_ORIG[fld]:25s} → {OUTCOME_MAP_V3[fld]:25s}  [{sc}]  raw={rv["corr_raw"]:.3f} → CPI잔차={rv["corr_resid_CPI"]:.3f}')

print(f'\n=== 출력 ===')
print(f'  CSV : {RES}/H10_macro_control_corr_v3.csv')
print(f'  PNG : {OUT}/H10_macro_control_compare_v3.png')
print('\n완료.')
