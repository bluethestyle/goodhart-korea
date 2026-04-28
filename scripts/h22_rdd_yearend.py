"""
H22: 한국판 Liebman & Mahoney (2017, AER) Year-End Spending RDD
================================================================
Liebman & Mahoney: 미국 연방조달 11월 마지막 주 vs 12월 첫 주 RDD
- 결과: 12월 첫 주 지출 5배 ↑ (use-it-or-lose-it)

한국판 설계:
- cutoff: 12월 1일 (회계연도 1/1~12/31의 마지막 달 시작)
- bw=1: 11·12월  →  Y = α + β·T + γ_year + ε  (T=1:12월, 활동+연도 FE)
- bw=2: 10·11·12월 → Y = α + β·T + γ·month_rel + δ·T·month_rel + γ_year + ε
- Y: log(일평균 집행액)
- β = 12월 점프 (배수 = exp(β))
- 클러스터 SE by ACTV_CD
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import os, duckdb, warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.font_manager as fm
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import statsmodels.formula.api as smf
import scienceplots
import seaborn as sns
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

# ── 상수 ──────────────────────────────────────────────────────────────────────
DB    = 'data/warehouse.duckdb'
FDIR  = 'data/figs/h22'
RDIR  = 'data/results'
DAYS  = {1:31,2:28,3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31}
DPI   = 200
MAXPX = 1800
W_IN  = MAXPX / DPI   # 12 inch
LM_MULT = 5.0         # Liebman-Mahoney 기준

os.makedirs(FDIR, exist_ok=True)
os.makedirs(RDIR, exist_ok=True)

# ── 1. 데이터 로드 ─────────────────────────────────────────────────────────────
print("=== H22 Year-End Spending RDD ===")
con = duckdb.connect(DB)

df_raw = con.execute("""
    SELECT
        FSCL_YY  AS year,
        EXE_M    AS month,
        ACTV_CD,
        ACTV_NM,
        FLD_NM,
        OFFC_NM,
        SUM(EP_AMT) AS ep_amt
    FROM monthly_exec
    WHERE FSCL_YY BETWEEN 2015 AND 2025
      AND EXE_M   IN (10,11,12)
      AND EP_AMT  > 0
    GROUP BY FSCL_YY, EXE_M, ACTV_CD, ACTV_NM, FLD_NM, OFFC_NM
""").df()
print(f"Raw rows: {len(df_raw):,}  |  활동수: {df_raw['ACTV_CD'].nunique():,}")

# H3 클러스터 (11y 기준)
h3 = pd.read_csv('data/results/H3_activity_embedding_11y.csv',
                 usecols=['ACTV_NM','cluster','dec_pct',
                          'chooyeon_pct','direct_invest_pct',
                          'personnel_pct','operating_pct']
                ).drop_duplicates('ACTV_NM')
CLUSTER_LABEL = {0:'인건비형', 1:'출연금형', 2:'직접투자형', 3:'일반사업형'}

df_raw = df_raw.merge(h3, on='ACTV_NM', how='left')
df_raw['days']      = df_raw['month'].map(DAYS)
df_raw['daily_ep']  = df_raw['ep_amt'] / df_raw['days']
df_raw['log_daily'] = np.log(df_raw['daily_ep'])
df_raw['T']         = (df_raw['month'] == 12).astype(int)
df_raw['month_rel'] = df_raw['month'] - 12   # 10→-2, 11→-1, 12→0

# ── 2. RDD 회귀 함수 ───────────────────────────────────────────────────────────
def run_rdd(data, bw=1, label='전체', outcome='log_daily'):
    """
    bw=1 (11·12월): Y = α + β·T + C(year)  [T⊥month_rel, 연도 FE]
    bw=2 (10~12월): Y = α + β·T + γ·month_rel + δ·T·month_rel + C(year)
    """
    if bw == 1:
        sub = data[data['month'].isin([11, 12])].copy()
        formula = f"{outcome} ~ T + C(year)"
    else:
        sub = data[data['month'].isin([10, 11, 12])].copy()
        formula = f"{outcome} ~ T + month_rel + T:month_rel + C(year)"

    sub = sub.dropna(subset=[outcome])
    if len(sub) < 30 or sub['ACTV_CD'].nunique() < 3:
        return None
    try:
        mod = smf.ols(formula, data=sub).fit(
            cov_type='cluster',
            cov_kwds={'groups': sub['ACTV_CD']}
        )
        beta = mod.params['T']
        se   = mod.bse['T']
        pval = mod.pvalues['T']
        mult = np.exp(beta) if outcome == 'log_daily' else beta
        return dict(label=label, bw=bw, outcome=outcome,
                    beta=beta, se=se, pval=pval,
                    r2=mod.rsquared, n=int(mod.nobs), mult=mult)
    except Exception as e:
        print(f"  [SKIP] {label} bw={bw}: {e}")
        return None

# ── 3. 전체 RDD ────────────────────────────────────────────────────────────────
results = []
for bw in [1, 2]:
    r = run_rdd(df_raw, bw=bw, label='전체')
    if r:
        results.append(r)
        sig = ('***' if r['pval']<0.001 else '**' if r['pval']<0.01
               else '*' if r['pval']<0.05 else 'ns')
        print(f"[전체 bw={bw}] β={r['beta']:.4f} (SE={r['se']:.4f},"
              f" p={r['pval']:.2e}) → {r['mult']:.2f}x {sig}")

# ── 4. 분야별 RDD ──────────────────────────────────────────────────────────────
print("\n=== 분야별 RDD (bw=1, 연도 FE) ===")
field_results = []
for fld, grp in df_raw.groupby('FLD_NM'):
    if grp['ACTV_CD'].nunique() < 5:
        continue
    r = run_rdd(grp, bw=1, label=fld)
    if r:
        field_results.append(r)
        sig = ('***' if r['pval']<0.001 else '**' if r['pval']<0.01
               else '*' if r['pval']<0.05 else 'ns')
        print(f"  {fld}: β={r['beta']:.3f}({sig})  → {r['mult']:.2f}x  [N={r['n']}]")

field_df = pd.DataFrame(field_results).sort_values('beta', ascending=True).reset_index(drop=True)

# ── 5. H3 클러스터별 RDD ───────────────────────────────────────────────────────
print("\n=== H3 클러스터별 RDD (bw=1) ===")
clust_results = []
for cl, grp in df_raw[df_raw['cluster'].notna()].groupby('cluster'):
    lbl = CLUSTER_LABEL.get(int(cl), f'클러스터{int(cl)}')
    r = run_rdd(grp, bw=1, label=lbl)
    if r:
        clust_results.append(r)
        sig = ('***' if r['pval']<0.001 else '**' if r['pval']<0.01
               else '*' if r['pval']<0.05 else 'ns')
        print(f"  {lbl}: β={r['beta']:.3f}({sig}) → {r['mult']:.2f}x [N={r['n']}]")

# ── 6. CSV 저장 ────────────────────────────────────────────────────────────────
main_csv = pd.DataFrame(results)
main_csv.to_csv(f'{RDIR}/H22_rdd_estimates.csv', index=False, encoding='utf-8-sig')

field_csv = pd.DataFrame(field_results + clust_results)
field_csv.to_csv(f'{RDIR}/H22_field_rdd.csv', index=False, encoding='utf-8-sig')
print(f"\n저장: {RDIR}/H22_rdd_estimates.csv")
print(f"저장: {RDIR}/H22_field_rdd.csv")

# ── 7. 월별 집계 (시각화용) ────────────────────────────────────────────────────
agg_all = (df_raw.groupby(['year','month'])
           .agg(mean_daily=('daily_ep','mean'),
                median_daily=('daily_ep','median'),
                n=('ACTV_CD','nunique'))
           .reset_index())

agg_fld = (df_raw.groupby(['year','month','FLD_NM'])
           .agg(mean_daily=('daily_ep','mean'))
           .reset_index())

# ── 8. 그림 1: 주 RDD 시각화 ──────────────────────────────────────────────────
fig = plt.figure(figsize=(W_IN, W_IN * 0.95), dpi=DPI)
gs  = GridSpec(2, 3, figure=fig, hspace=0.55, wspace=0.42)

# --- A. 월별 연도별 일집행액 ---
ax_a = fig.add_subplot(gs[0, :2])
yr_list   = sorted(agg_all['year'].unique())
cmap_vals = plt.cm.Blues(np.linspace(0.35, 0.9, len(yr_list)))
for i, yr in enumerate(yr_list):
    g = agg_all[agg_all['year']==yr].sort_values('month')
    ax_a.plot(g['month'], g['mean_daily']/1e9,
              alpha=0.55, color=cmap_vals[i], lw=1.1, label=str(yr))

avg_m = agg_all.groupby('month')['mean_daily'].mean()
ax_a.plot(avg_m.index, avg_m.values/1e9, 'k-', lw=2.5, zorder=5, label='평균')
ax_a.axvline(11.5, color='crimson', lw=2, ls='--', alpha=0.85, label='12월 진입 cutoff')

# 11·12월 차이 강조 영역
ax_a.axvspan(11, 12.5, alpha=0.08, color='crimson')

ax_a.set_xlabel('월')
ax_a.set_ylabel('활동 평균 일집행액 (십억원)')
ax_a.set_title('A. 월별 활동 평균 일집행액 (2015~2025)', fontweight='bold')
ax_a.set_xticks([10, 11, 12])
ax_a.set_xticklabels(['10월', '11월', '12월'])
ax_a.legend(ncol=6, loc='upper left', framealpha=0.7)
ax_a.grid(alpha=0.3)

# --- B. RDD 점프 시각화 (연도별 11→12월 변화율) ---
ax_b = fig.add_subplot(gs[0, 2])
# 각 연도×활동의 11월→12월 변화
pivot = df_raw[df_raw['month'].isin([11,12])].pivot_table(
    index=['year','ACTV_CD'], columns='month', values='log_daily'
).dropna()
pivot.columns = ['nov','dec']
pivot['jump'] = pivot['dec'] - pivot['nov']

# 연도별 중앙값 jump
yr_jump = pivot.groupby('year')['jump'].median().reset_index()

bars = ax_b.bar(yr_jump['year'], yr_jump['jump'],
                color=['crimson' if v>0 else 'steelblue'
                       for v in yr_jump['jump']],
                alpha=0.78, width=0.6)
ax_b.axhline(0, color='black', lw=1)

# 전체 β 표시선
r_bw1 = next((r for r in results if r['bw']==1), None)
if r_bw1:
    ax_b.axhline(r_bw1['beta'], color='darkorange', lw=2, ls='--',
                 label=f"β={r_bw1['beta']:.3f}")
ax_b.axhline(np.log(LM_MULT), color='purple', lw=1.8, ls=':',
             label=f'L-M 5x (β≈{np.log(LM_MULT):.2f})')

ax_b.set_xlabel('연도')
ax_b.set_ylabel('log 일집행액 jump\n(12월-11월 중앙값)')
ax_b.set_title('B. 연도별 12월 점프\n(활동 중앙값)', fontweight='bold')
ax_b.set_xticks(yr_list)
ax_b.set_xticklabels([str(y)[2:] for y in yr_list])
ax_b.legend()
ax_b.grid(alpha=0.3)

# --- C. 분야별 β Forest plot ---
ax_c = fig.add_subplot(gs[1, :2])
if not field_df.empty:
    colors_c = ['crimson' if p < 0.05 else '#aaaaaa'
                for p in field_df['pval']]
    ys = np.arange(len(field_df))
    ax_c.barh(ys, field_df['beta'], xerr=1.96 * field_df['se'],
              color=colors_c, alpha=0.78, height=0.55,
              error_kw={'elinewidth':1.2, 'capsize':3})
    ax_c.set_yticks(ys)
    ax_c.set_yticklabels(field_df['label'])
    ax_c.axvline(0, color='black', lw=1)
    ax_c.axvline(np.log(LM_MULT), color='purple', lw=1.5, ls=':',
                 label=f'L-M 5x (β≈{np.log(LM_MULT):.2f})')
    if r_bw1:
        ax_c.axvline(r_bw1['beta'], color='darkorange', lw=1.5, ls='--',
                     label=f"한국 전체 β={r_bw1['beta']:.2f}")
    # 배수 주석
    for i, row in field_df.iterrows():
        ax_c.text(row['beta'] + 0.015, i,
                  f"{row['mult']:.1f}x",
                  va='center', ha='left', fontsize=plt.rcParams['font.size'] * 0.85,
                  color='black' if row['pval'] < 0.05 else '#888888')
    sig_patch  = mpatches.Patch(color='crimson', label='p<0.05', alpha=0.78)
    ns_patch   = mpatches.Patch(color='#aaaaaa', label='p≥0.05', alpha=0.78)
    handles = [sig_patch, ns_patch]
    ax_c.legend(handles=handles, loc='lower right')
    ax_c.set_xlabel('β (log 일집행액 점프, 95% CI)')
    ax_c.set_title('C. 분야별 12월 집행 점프 (RDD β, bw=±1월)', fontweight='bold')
    ax_c.grid(alpha=0.3, axis='x')

# --- D. H3 클러스터별 β ---
ax_d = fig.add_subplot(gs[1, 2])
if clust_results:
    cl_df = pd.DataFrame(clust_results).sort_values('beta').reset_index(drop=True)
    colors_d = ['crimson' if p < 0.05 else '#aaaaaa' for p in cl_df['pval']]
    ys = np.arange(len(cl_df))
    ax_d.barh(ys, cl_df['beta'], xerr=1.96 * cl_df['se'],
              color=colors_d, alpha=0.78, height=0.45,
              error_kw={'elinewidth':1.5, 'capsize':4})
    ax_d.set_yticks(ys)
    ax_d.set_yticklabels(cl_df['label'])
    ax_d.axvline(0, color='black', lw=1)
    ax_d.axvline(np.log(LM_MULT), color='purple', lw=1.5, ls=':')
    for i, row in cl_df.iterrows():
        ax_d.text(row['beta'] + 0.02, i,
                  f"{row['mult']:.2f}x",
                  va='center', ha='left', fontsize=plt.rcParams['font.size'] * 0.85,
                  color='black' if row['pval'] < 0.05 else '#888888')
    ax_d.set_xlabel('β (log 일집행액)')
    ax_d.set_title('D. 활동 클러스터별\n12월 점프', fontweight='bold')
    ax_d.grid(alpha=0.3, axis='x')

# 하단 결과 요약 텍스트
if r_bw1:
    r2 = next((r for r in results if r['bw']==2), None)
    lines = [
        f"한국 전체: β={r_bw1['beta']:.3f} (SE={r_bw1['se']:.3f}, p={r_bw1['pval']:.2e})"
        f"  →  12월 배수 = {r_bw1['mult']:.2f}x",
    ]
    if r2:
        lines.append(
            f"bw=2(±2월 시): β={r2['beta']:.3f} → {r2['mult']:.2f}x"
        )
    lines.append(f"참고: Liebman-Mahoney (2017, AER) 미국 = 5.0x")
    fig.text(0.5, -0.02, '\n'.join(lines), ha='center',
             bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.92))

fig.suptitle('한국판 Year-End Spending RDD\n(Liebman & Mahoney 2017, AER 복제)',
             fontweight='bold', y=1.02)

plt.savefig(f'{FDIR}/H22_rdd_main.png', dpi=DPI,
            bbox_inches='tight', facecolor='white')
print(f"저장: {FDIR}/H22_rdd_main.png")
plt.close()

# ── 9. 그림 2: 분야별 상세 시계열 ─────────────────────────────────────────────
# 점프 크기 상위·하위 각 3개 선택
if len(field_df) >= 6:
    top3  = field_df.tail(3)['label'].tolist()
    bot3  = field_df.head(3)['label'].tolist()
    plot_list = bot3 + top3
else:
    plot_list = field_df['label'].tolist()

n_panels = len(plot_list)
ncols = 3
nrows = (n_panels + ncols - 1) // ncols

fig2, axes2 = plt.subplots(nrows=nrows, ncols=ncols,
                            figsize=(W_IN, W_IN * 0.62),
                            dpi=DPI, sharey=False)
axes2_flat = np.array(axes2).flatten()

for idx, fld in enumerate(plot_list):
    ax = axes2_flat[idx]
    sub = agg_fld[agg_fld['FLD_NM'] == fld]

    # 연도별 흐린 선
    for yr, g in sub.groupby('year'):
        g_s = g.sort_values('month')
        ax.plot(g_s['month'], g_s['mean_daily']/1e9,
                alpha=0.25, color='steelblue', lw=0.9)

    # 전체 평균
    avg = sub.groupby('month')['mean_daily'].mean()
    ax.plot(avg.index, avg.values/1e9, 'k-', lw=2, label='평균')
    ax.axvline(11.5, color='crimson', lw=1.6, ls='--', alpha=0.85)
    ax.axvspan(11, 12.5, alpha=0.07, color='crimson')

    # β 정보
    r_row = field_df[field_df['label'] == fld]
    if not r_row.empty:
        b = r_row.iloc[0]['beta']
        p = r_row.iloc[0]['pval']
        m = r_row.iloc[0]['mult']
        sig = '***' if p<0.001 else '**' if p<0.01 else '*' if p<0.05 else ''
        ax.set_title(f'{fld}\nβ={b:.2f}{sig}  ({m:.1f}x)', fontweight='bold')
    else:
        ax.set_title(fld, fontweight='bold')

    ax.set_xticks([10, 11, 12])
    ax.set_xticklabels(['10월','11월','12월'])
    ax.set_ylabel('평균 일집행액\n(십억원)')
    ax.grid(alpha=0.3)

# 빈 패널 숨기기
for idx in range(n_panels, len(axes2_flat)):
    axes2_flat[idx].set_visible(False)

fig2.suptitle('분야별 12월 Year-End 집행 점프\n(상위·하위 각 3개 분야)',
              fontweight='bold')
plt.tight_layout()
plt.savefig(f'{FDIR}/H22_rdd_by_field.png', dpi=DPI,
            bbox_inches='tight', facecolor='white')
print(f"저장: {FDIR}/H22_rdd_by_field.png")
plt.close()

# ── 10. 최종 출력 ─────────────────────────────────────────────────────────────
print("\n" + "="*65)
print("[ H22 최종 결과 ]")
print("="*65)
for r in results:
    sig = ('***' if r['pval']<0.001 else '**' if r['pval']<0.01
           else '*' if r['pval']<0.05 else 'ns')
    print(f"  bw={r['bw']}월: β={r['beta']:.4f}({sig})"
          f"  → 12월 배수={r['mult']:.2f}x"
          f"  [N={r['n']:,}, R²={r['r2']:.3f}]")
print(f"  ※ Liebman-Mahoney (2017) 미국 기준: 5.0x")
print()
print("분야별 (큰→작 순):")
for _, row in field_df[::-1].iterrows():
    sig = ('***' if row['pval']<0.001 else '**' if row['pval']<0.01
           else '*' if row['pval']<0.05 else 'ns')
    print(f"  {row['label']}: {row['mult']:.2f}x ({sig})")
print()
print("H3 클러스터:")
for r in sorted(clust_results, key=lambda x: -x['mult']):
    sig = ('***' if r['pval']<0.001 else '**' if r['pval']<0.01
           else '*' if r['pval']<0.05 else 'ns')
    print(f"  {r['label']}: {r['mult']:.2f}x ({sig})")
print("\n완료.")
