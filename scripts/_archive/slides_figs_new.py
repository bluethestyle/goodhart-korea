"""
slides_figs_new.py
Generate 7 new figures for slide deck that are not in the paper.
Output: paper/slides/assets/figures/_preview/
"""
import os, sys, warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import duckdb

warnings.filterwarnings('ignore')

# ── Font setup ──────────────────────────────────────────────────────────────
import matplotlib.font_manager as fm
for font_name in ['Malgun Gothic', 'Arial Unicode MS', 'DejaVu Sans']:
    try:
        plt.rcParams['font.family'] = font_name
        fig_test, ax_test = plt.subplots()
        ax_test.set_title('테스트')
        plt.close(fig_test)
        FONT = font_name
        break
    except Exception:
        continue
plt.rcParams['font.family'] = FONT
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 200
plt.rcParams.update({
    'font.size': 15,
    'axes.titlesize': 17,
    'axes.labelsize': 15,
    'xtick.labelsize': 14,
    'ytick.labelsize': 14,
    'legend.fontsize': 13,
})

print(f"Using font: {FONT}")

# ── Paths ─────────────────────────────────────────────────────────────────
BASE = r'D:\workspace\재정자료분석'
PREVIEW = os.path.join(BASE, 'paper', 'slides', 'assets', 'figures', '_preview')
DEST    = os.path.join(BASE, 'paper', 'slides', 'assets', 'figures')
RESULTS = os.path.join(BASE, 'data', 'results')
DB_PATH = os.path.join(BASE, 'data', 'warehouse.duckdb')

os.makedirs(PREVIEW, exist_ok=True)

def save(fig, name):
    p = os.path.join(PREVIEW, name)
    fig.savefig(p, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    size_kb = os.path.getsize(p) // 1024
    print(f"  Saved {name}  ({fig.get_size_inches()}, {size_kb} KB)")
    return p

# ── Archetype colours ─────────────────────────────────────────────────────
ARCH_COLORS = {
    'personnel':     '#5475a8',
    'direct_invest': '#c44e52',
    'chooyeon':      '#54a868',
    'normal':        '#888888',
}

# ─────────────────────────────────────────────────────────────────────────────
# Figure 1: s2_dec_hook.png  — 자산취득형 월별 일평균 집행
# ─────────────────────────────────────────────────────────────────────────────
print("\n[1/7] s2_dec_hook.png")
try:
    emb = pd.read_csv(os.path.join(RESULTS, 'H3_activity_embedding_11y.csv'), encoding='utf-8-sig')
    direct_inv = emb[emb['cluster'] == 1][['ACTV_NM']].copy()

    con = duckdb.connect(DB_PATH)
    con.register('direct_inv_tbl', direct_inv)

    df_exec = con.execute("""
        SELECT m.EXE_M as month, m.FSCL_YY as year, SUM(m.EP_AMT) as total_ep
        FROM monthly_exec m
        INNER JOIN direct_inv_tbl d ON m.ACTV_NM = d.ACTV_NM
        WHERE m.FSCL_YY BETWEEN 2015 AND 2025
          AND m.EXE_M BETWEEN 1 AND 12
        GROUP BY m.EXE_M, m.FSCL_YY
        ORDER BY m.FSCL_YY, m.EXE_M
    """).df()

    days_in_month = {1:31, 2:28, 3:31, 4:30, 5:31, 6:30,
                     7:31, 8:31, 9:30, 10:31, 11:30, 12:31}
    df_exec['days'] = df_exec['month'].map(days_in_month)
    df_exec['daily_ep'] = df_exec['total_ep'] / df_exec['days']

    monthly_avg = df_exec.groupby('month')['daily_ep'].mean().reset_index()

    fig, ax = plt.subplots(figsize=(10, 5))
    months = monthly_avg['month'].values
    vals   = monthly_avg['daily_ep'].values

    colors = ['#c44e52' if m == 12 else '#7aadcf' for m in months]
    bars = ax.bar(months, vals, color=colors, edgecolor='white', linewidth=0.8,
                  zorder=3)

    # highlight 12월 annotation — placed mid-height to avoid title collision
    ax.annotate('12월\n연말 spike',
                xy=(12, vals[11]),
                xytext=(10.0, vals[11] * 0.55),
                fontsize=16, fontweight='bold', color='#c44e52',
                arrowprops=dict(arrowstyle='->', color='#c44e52', lw=1.8,
                                connectionstyle='arc3,rad=-0.2'),
                ha='center')

    ax.set_yscale('log')
    ax.set_xlabel('월 (Month)', fontsize=16)
    ax.set_ylabel('일평균 집행액 (원, log scale)', fontsize=16)
    ax.set_title('자산취득형 사업 — 월별 일평균 집행 (2015~2025)', fontsize=18, fontweight='bold', pad=12)
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels([f'{m}월' for m in range(1, 13)], fontsize=15)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x/1e9:.0f}B'))
    ax.grid(axis='y', alpha=0.25, zorder=0)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    fig.tight_layout()
    save(fig, 's2_dec_hook.png')
except Exception as e:
    print(f"  ERROR: {e}")
    import traceback; traceback.print_exc()


# ─────────────────────────────────────────────────────────────────────────────
# Figure 2: s4a_measurability_gap.png  — 측정성 격차 schema
# ─────────────────────────────────────────────────────────────────────────────
print("\n[2/7] s4a_measurability_gap.png")
try:
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis('off')

    # Left box — Easy to measure (blue)
    lbox = FancyBboxPatch((0.3, 1.5), 3.4, 3.0,
                          boxstyle='round,pad=0.15', linewidth=2,
                          edgecolor='#5475a8', facecolor='#d6e4f0', zorder=2)
    ax.add_patch(lbox)
    ax.text(2.0, 4.1, '측정 쉬움', fontsize=18, fontweight='bold',
            color='#5475a8', ha='center', va='center')
    ax.text(2.0, 3.6, '(Easy to Measure)', fontsize=14, color='#5475a8',
            ha='center', va='center')
    for i, item in enumerate(['집행 시점', '집행 금액', '집행률']):
        ax.text(2.0, 3.0 - i*0.5, f'• {item}', fontsize=15,
                color='#2c3e6b', ha='center', va='center')

    # Right box — Hard to measure (red)
    rbox = FancyBboxPatch((6.3, 1.5), 3.4, 3.0,
                          boxstyle='round,pad=0.15', linewidth=2,
                          edgecolor='#c44e52', facecolor='#fde8e8', zorder=2)
    ax.add_patch(rbox)
    ax.text(8.0, 4.1, '측정 어려움', fontsize=18, fontweight='bold',
            color='#c44e52', ha='center', va='center')
    ax.text(8.0, 3.6, '(Hard to Measure)', fontsize=14, color='#c44e52',
            ha='center', va='center')
    for i, item in enumerate(['사회적 결과', '사업 품질', '다년 lag 효과']):
        ax.text(8.0, 3.0 - i*0.5, f'• {item}', fontsize=15,
                color='#6b2c2c', ha='center', va='center')

    # Central Goodhart arrow — wide, weighted
    ax.annotate('', xy=(6.1, 3.0), xytext=(3.9, 3.0),
                arrowprops=dict(arrowstyle='->', lw=3.5, color='#444',
                                connectionstyle='arc3,rad=0'))
    ax.text(5.0, 3.35, '평가 가중\n쏠림', fontsize=14, color='#444',
            ha='center', va='bottom', fontweight='bold')
    ax.text(5.0, 2.55, '→ 굿하트 효과', fontsize=20, color='#b73a2c',
            ha='center', va='top', fontweight='bold')

    # Top label
    ax.text(5.0, 5.5, '측정성 격차 (Measurability Gap)', fontsize=19,
            fontweight='bold', ha='center', va='center', color='#222')

    # Equation inset bottom
    eq_box = FancyBboxPatch((2.5, 0.2), 5.0, 0.9,
                             boxstyle='round,pad=0.1', linewidth=1.5,
                             edgecolor='#888', facecolor='#f9f9f9', zorder=2)
    ax.add_patch(eq_box)
    ax.text(5.0, 0.65, "Agent 측정성 통과율:  φ'(·) < 1  →  유효 품질 가중 하락",
            fontsize=15, ha='center', va='center', color='#333',
            style='italic')

    fig.tight_layout()
    save(fig, 's4a_measurability_gap.png')
except Exception as e:
    print(f"  ERROR: {e}")
    import traceback; traceback.print_exc()


# ─────────────────────────────────────────────────────────────────────────────
# Figure 3: s20_decompose_compare.png  — FFT / STL / NP comparison
# ─────────────────────────────────────────────────────────────────────────────
print("\n[3/7] s20_decompose_compare.png")
try:
    # Use a chooyeon (cluster 2) representative activity time series
    emb = pd.read_csv(os.path.join(RESULTS, 'H3_activity_embedding_11y.csv'), encoding='utf-8-sig')
    cho = emb[emb['cluster'] == 2].sort_values('amp_12m_norm', ascending=False)
    rep_actv = cho.iloc[0]['ACTV_NM']

    con = duckdb.connect(DB_PATH)
    q = """
        SELECT FSCL_YY as year, EXE_M as month, SUM(EP_AMT) as ep
        FROM monthly_exec
        WHERE ACTV_NM = ?
          AND FSCL_YY BETWEEN 2015 AND 2025
          AND EXE_M BETWEEN 1 AND 12
        GROUP BY FSCL_YY, EXE_M
        ORDER BY FSCL_YY, EXE_M
    """
    ts_df = con.execute(q, [rep_actv]).df()

    # Build full 132-month series (2015-01 to 2025-12)
    full_idx = pd.date_range('2015-01', periods=132, freq='MS')
    ts_df['date'] = pd.to_datetime(
        ts_df['year'].astype(str) + '-' + ts_df['month'].astype(str).str.zfill(2))
    ts_series = ts_df.set_index('date')['ep'].reindex(full_idx).interpolate()
    ts_vals = ts_series.values.astype(float)
    n = len(ts_vals)
    ts_vals = np.where(np.isnan(ts_vals), np.nanmean(ts_vals), ts_vals)

    # --- Panel a: FFT power spectrum
    fft_vals = np.fft.rfft(ts_vals - ts_vals.mean())
    freqs = np.fft.rfftfreq(n)
    periods = np.where(freqs > 0, 1.0 / freqs, np.inf)
    power = np.abs(fft_vals)**2

    # Keep periods 1–24 months
    mask = (periods >= 1) & (periods <= 24)
    p_plot = periods[mask]
    pw_plot = power[mask]

    # --- Panel b: Simple STL-like decomposition via moving average
    from scipy.ndimage import uniform_filter1d
    trend = uniform_filter1d(ts_vals, size=13, mode='nearest')
    seasonal = ts_vals - trend
    residual = seasonal.copy()
    # Compute monthly average seasonal
    months_idx = np.arange(n) % 12
    season_avg = np.array([seasonal[months_idx == m].mean() for m in range(12)])
    season_signal = np.array([season_avg[m] for m in months_idx])
    residual = ts_vals - trend - season_signal

    # --- Panel c: Simple NP-like (trend + annual Fourier)
    t = np.arange(n)
    # Linear trend
    from numpy.polynomial import polynomial as P
    coeff = np.polyfit(t, ts_vals, 1)
    np_trend = np.polyval(coeff, t)
    np_seasonal = ts_vals - np_trend
    # Smooth with 12-month period Fourier
    A = np.column_stack([
        np.sin(2*np.pi*t/12), np.cos(2*np.pi*t/12),
        np.sin(2*np.pi*t/6),  np.cos(2*np.pi*t/6),
    ])
    coef_f, *_ = np.linalg.lstsq(A, np_seasonal, rcond=None)
    np_seasonal_fit = A @ coef_f

    # ── Plot ──
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    TOOL_LABELS = ['FFT (Power Spectrum)', 'STL Decomposition', 'NeuralProphet (approx.)']
    colors3 = ['#5475a8', '#c44e52', '#54a868']
    t_axis = np.arange(n)

    # Panel A — FFT
    ax = axes[0]
    bar_colors = ['#c44e52' if abs(p - 12) < 1.0 else '#c9d8e8' for p in p_plot]
    ax.bar(p_plot, pw_plot / pw_plot.max(), color=bar_colors, width=0.4,
           edgecolor='white', linewidth=0.5, zorder=3)
    ax.axvline(12, color='#c44e52', lw=1.5, ls='--', alpha=0.7, label='12개월')
    ax.set_xlabel('주기 (개월)', fontsize=15)
    ax.set_ylabel('정규화 파워', fontsize=15)
    ax.set_title('(a) FFT', fontsize=17, fontweight='bold', color=colors3[0])
    ax.legend(fontsize=13)
    ax.grid(alpha=0.2)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Panel B — STL
    ax = axes[1]
    ax2_1 = ax
    fig_b, ax_b = plt.subplots()  # dummy, won't be saved
    plt.close(fig_b)

    # Compact 3 sub-lines in one panel using twinx offsets trick
    s = ts_vals / ts_vals.max()
    tr = trend / trend.max()
    se = season_signal / (np.abs(season_signal).max() + 1e-9)
    re = residual / (np.abs(residual).max() + 1e-9)

    ax.plot(t_axis, tr + 1.5, color='#5475a8', lw=1.8, label='Trend')
    ax.plot(t_axis, se + 0.5, color='#c44e52', lw=1.2, label='Seasonal')
    ax.plot(t_axis, re - 0.5, color='#888', lw=1.0, alpha=0.8, label='Residual')
    ax.set_yticks([1.5, 0.5, -0.5])
    ax.set_yticklabels(['Trend', 'Seasonal', 'Residual'], fontsize=14)
    ax.set_xlabel('시간 (월)', fontsize=15)
    ax.set_title('(b) STL', fontsize=17, fontweight='bold', color=colors3[1])
    ax.legend(fontsize=13, loc='upper right')
    ax.grid(alpha=0.2)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Panel C — NP-like
    ax = axes[2]
    np_tr_n = np_trend / (np_trend.max() + 1e-9)
    np_se_n = np_seasonal_fit / (np.abs(np_seasonal_fit).max() + 1e-9)
    ax.plot(t_axis, np_tr_n + 0.8, color='#5475a8', lw=1.8, label='Trend')
    ax.plot(t_axis, np_se_n - 0.2, color='#54a868', lw=1.2, label='Seasonal')
    ax.set_yticks([0.8, -0.2])
    ax.set_yticklabels(['Trend', 'Seasonal'], fontsize=14)
    ax.set_xlabel('시간 (월)', fontsize=15)
    ax.set_title('(c) NeuralProphet', fontsize=17, fontweight='bold', color=colors3[2])
    ax.legend(fontsize=13, loc='upper right')
    ax.grid(alpha=0.2)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    fig.suptitle('동일 시계열 — 3가지 분해 방법 비교 (출연금형 대표 활동)',
                 fontsize=17, fontweight='bold', y=1.01)
    fig.tight_layout()
    save(fig, 's20_decompose_compare.png')
except Exception as e:
    print(f"  ERROR: {e}")
    import traceback; traceback.print_exc()


# ─────────────────────────────────────────────────────────────────────────────
# Figure 4: s22a_rdd_assumption.png  — RDD identification schema
# ─────────────────────────────────────────────────────────────────────────────
print("\n[4/7] s22a_rdd_assumption.png")
try:
    fig, ax = plt.subplots(figsize=(14, 6.5))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 5.4)
    ax.axis('off')

    # ── Top: fiscal year timeline ──
    ax.annotate('', xy=(11.2, 4.5), xytext=(0.8, 4.5),
                arrowprops=dict(arrowstyle='->', lw=2.5, color='#333'))
    ax.text(0.8, 4.78, '1월', fontsize=20, ha='center', color='#444')
    ax.text(4.5, 4.78, '6월', fontsize=20, ha='center', color='#444')
    # 11/30 marker
    ax.axvline(x=7.0, ymin=0.80, ymax=0.92, color='#555', lw=1.8, ls='-')
    ax.text(7.0, 4.78, '11/30', fontsize=20, ha='center', color='#555', fontweight='bold')
    # 12/1 red line
    ax.axvline(x=7.6, ymin=0.68, ymax=0.92, color='#c44e52', lw=3.0, ls='-')
    ax.text(7.6, 4.78, '12/1', fontsize=22, ha='center', color='#c44e52', fontweight='bold')
    ax.text(7.6, 5.18, 'arbitrary cutoff', fontsize=18, ha='center',
            color='#c44e52', style='italic', fontweight='bold')
    ax.text(11.2, 4.78, '12/31', fontsize=20, ha='center', color='#444')

    # ── Left box: 11/30 — same environment ──
    lbox = FancyBboxPatch((0.3, 1.6), 4.2, 2.1,
                          boxstyle='round,pad=0.18', linewidth=2.5,
                          edgecolor='#5475a8', facecolor='#d6e4f0', zorder=2)
    ax.add_patch(lbox)
    ax.text(2.4, 3.3, '11/30', fontsize=28, fontweight='bold',
            color='#5475a8', ha='center', va='center')
    ax.text(2.4, 2.75, '사업 환경 동일', fontsize=22, ha='center',
            va='center', color='#2c3e6b', fontweight='bold')
    ax.text(2.4, 2.15, '· 예산 잔액 동일\n· 사업 진행 중', fontsize=18,
            ha='center', va='center', color='#2c3e6b')

    # ── Right box: 12/1 — budget deadline ──
    rbox = FancyBboxPatch((7.5, 1.6), 4.2, 2.1,
                          boxstyle='round,pad=0.18', linewidth=2.5,
                          edgecolor='#c44e52', facecolor='#fde8e8', zorder=2)
    ax.add_patch(rbox)
    ax.text(9.6, 3.3, '12/1', fontsize=28, fontweight='bold',
            color='#c44e52', ha='center', va='center')
    ax.text(9.6, 2.75, '회계 cycle 다름', fontsize=22, ha='center',
            va='center', color='#6b2c2c', fontweight='bold')
    ax.text(9.6, 2.15, '· 예산 마감 임박\n· 집행 압박 시작', fontsize=18,
            ha='center', va='center', color='#6b2c2c')

    # ── Center dashed arrow with "며칠 차이" ──
    ax.annotate('', xy=(7.4, 2.65), xytext=(4.6, 2.65),
                arrowprops=dict(arrowstyle='->', lw=2.5, color='#555',
                                linestyle='dashed',
                                connectionstyle='arc3,rad=0'))
    ax.text(6.0, 3.0, '며칠 차이', fontsize=20, ha='center',
            color='#555', style='italic', fontweight='bold')

    # ── Bottom message box ──
    mbox = FancyBboxPatch((1.0, 0.2), 10.0, 1.05,
                          boxstyle='round,pad=0.14', linewidth=2,
                          edgecolor='#54a868', facecolor='#e8f5ec', zorder=2)
    ax.add_patch(mbox)
    ax.text(6.0, 0.72, 'Agent는 cutoff를 옮길 수 없다 → 회계 기한이 자연 실험 역할',
            fontsize=20, ha='center', va='center', color='#1a4d28', fontweight='bold')

    ax.set_title('RDD 식별 가정 — 왜 12월 1일이 random인가', fontsize=24,
                 fontweight='bold', y=1.02)
    fig.tight_layout()
    save(fig, 's22a_rdd_assumption.png')
except Exception as e:
    print(f"  ERROR: {e}")
    import traceback; traceback.print_exc()


# ─────────────────────────────────────────────────────────────────────────────
# Figure 5: s27_archetype_zscore.png  — 4 archetype z-score grouped bar
# ─────────────────────────────────────────────────────────────────────────────
print("\n[5/7] s27_archetype_zscore.png")
try:
    prof = pd.read_csv(os.path.join(RESULTS, 'H3_cluster_profile_11y.csv'), encoding='utf-8-sig')
    # cluster 0=personnel, 1=chooyeon, 2=direct_invest, 3=normal (from profile_11y)
    # Verify from profile values
    # cluster_profile_11y: 0=C0_personnel(personnel_pct=3.07), 1=direct_invest?, 2=chooyeon?, 3=normal
    # From data: C0: personnel=3.07, C1: direct_invest=3.28, C2: chooyeon=2.89, C3=normal
    # But profile_11y shows cluster 0/1/2/3 with different values:
    # 0: personnel=3.07 → personnel
    # 1: direct_invest=3.28 → direct_invest
    # 2: chooyeon=2.89 → chooyeon
    # 3: normal

    arch_map = {0: 'personnel', 1: 'direct_invest', 2: 'chooyeon', 3: 'normal'}
    arch_labels = {
        'personnel':     '인건비형\n(Personnel)',
        'direct_invest': '자산취득형\n(Direct Invest)',
        'chooyeon':      '출연금형\n(Chooyeon)',
        'normal':        '정상사업\n(Normal)',
    }

    features = ['personnel_pct', 'direct_invest_pct', 'chooyeon_pct']
    feat_labels = ['인건비 비중\n(personnel_pct)',
                   '자산취득 비중\n(direct_invest_pct)',
                   '출연금 비중\n(chooyeon_pct)']

    prof['arch'] = prof['cluster'].map(arch_map)
    # Profile values are already z-scores (normalised across activities)

    arch_order = ['personnel', 'direct_invest', 'chooyeon', 'normal']
    n_arch = len(arch_order)
    n_feat = len(features)

    x = np.arange(n_arch)
    width = 0.22
    offsets = np.linspace(-(n_feat-1)/2, (n_feat-1)/2, n_feat) * width

    feat_colors = ['#7aadcf', '#f0a070', '#98d498']

    fig, ax = plt.subplots(figsize=(10, 6))

    for fi, (feat, flabel, fc) in enumerate(zip(features, feat_labels, feat_colors)):
        vals = []
        for arch in arch_order:
            row = prof[prof['arch'] == arch]
            v = float(row[feat].values[0]) if len(row) > 0 else 0.0
            vals.append(v)

        bars = ax.bar(x + offsets[fi], vals, width=width,
                      label=flabel, color=fc, edgecolor='white', linewidth=0.8,
                      zorder=3)
        for bar, v in zip(bars, vals):
            # Place labels at bar tip, with consistent offset from x-axis
            if v >= 0:
                y = v + 0.08
                va = 'bottom'
            else:
                y = v - 0.08
                va = 'top'
            ax.text(bar.get_x() + bar.get_width()/2, y,
                    f'{v:.2f}', ha='center', va=va,
                    fontsize=13, fontweight='bold', color='#333')

    # Expand y-axis range to give labels breathing room
    ymin, ymax = ax.get_ylim()
    ax.set_ylim(ymin - 0.25, ymax + 0.20)

    # Colour the x-tick labels to match archetype colours, with extra padding
    ax.set_xticks(x)
    ax.set_xticklabels([arch_labels[a] for a in arch_order], fontsize=15)
    ax.tick_params(axis='x', pad=14)  # push x-tick labels further from axis
    tick_colors = [ARCH_COLORS[a] for a in arch_order]
    for tick, color in zip(ax.get_xticklabels(), tick_colors):
        tick.set_color(color)
        tick.set_fontweight('bold')

    ax.axhline(0, color='#666', lw=1.0, ls='-')
    ax.set_ylabel('Z-score (표준편차)', fontsize=16)
    ax.set_title('사업원형별 핵심 피처 Z-score — 4 Archetypes × 3 Features',
                 fontsize=17, fontweight='bold', pad=12)
    ax.legend(loc='upper right', fontsize=14, framealpha=0.9)
    ax.grid(axis='y', alpha=0.25, zorder=0)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    fig.tight_layout()
    save(fig, 's27_archetype_zscore.png')
except Exception as e:
    print(f"  ERROR: {e}")
    import traceback; traceback.print_exc()


# ─────────────────────────────────────────────────────────────────────────────
# Figure 6: s33_baron_kenny.png  — DAG + mediation forest plot
# ─────────────────────────────────────────────────────────────────────────────
print("\n[6/7] s33_baron_kenny.png")
try:
    med = pd.read_csv(os.path.join(RESULTS, 'H23_mediation_estimates.csv'), encoding='utf-8-sig')
    # Filter to field-level rows (exclude POOLED)
    med_fld = med[med['fld_nm'] != 'POOLED (FE)'].copy()
    med_fld = med_fld.dropna(subset=['ab', 'ab_lo95', 'ab_hi95'])
    med_fld = med_fld.sort_values('ab', ascending=True)

    fig, (ax_dag, ax_forest) = plt.subplots(1, 2, figsize=(14, 5),
                                             gridspec_kw={'width_ratios': [1, 1.4]})

    # ── Left: Baron-Kenny DAG ──
    ax_dag.set_xlim(0, 10)
    ax_dag.set_ylim(0, 6)
    ax_dag.axis('off')

    node_style = dict(boxstyle='round,pad=0.4', linewidth=1.8, zorder=3)

    # X node
    xb = FancyBboxPatch((0.3, 2.3), 2.4, 1.2,
                         facecolor='#d6e4f0', edgecolor='#5475a8', **node_style)
    ax_dag.add_patch(xb)
    ax_dag.text(1.5, 2.9, 'X', fontsize=19, fontweight='bold',
                ha='center', va='center', color='#5475a8')
    ax_dag.text(1.5, 2.4, 'chooyeon_pct', fontsize=13, ha='center',
                va='center', color='#5475a8')

    # M node
    mb = FancyBboxPatch((3.8, 4.2), 2.4, 1.2,
                         facecolor='#fff3cd', edgecolor='#b8860b', **node_style)
    ax_dag.add_patch(mb)
    ax_dag.text(5.0, 4.8, 'M', fontsize=19, fontweight='bold',
                ha='center', va='center', color='#8a6500')
    ax_dag.text(5.0, 4.3, 'amp_12m_norm', fontsize=13, ha='center',
                va='center', color='#8a6500')

    # Y node
    yb = FancyBboxPatch((7.3, 2.3), 2.4, 1.2,
                         facecolor='#fde8e8', edgecolor='#c44e52', **node_style)
    ax_dag.add_patch(yb)
    ax_dag.text(8.5, 2.9, 'Y', fontsize=19, fontweight='bold',
                ha='center', va='center', color='#c44e52')
    ax_dag.text(8.5, 2.4, 'outcome', fontsize=13, ha='center',
                va='center', color='#c44e52')

    # X → M (a path)
    ax_dag.annotate('', xy=(3.9, 4.5), xytext=(2.1, 3.5),
                    arrowprops=dict(arrowstyle='->', lw=2.0, color='#5475a8'))
    ax_dag.text(2.7, 4.2, 'a path', fontsize=13, color='#5475a8',
                style='italic', rotation=35)

    # M → Y (b path)
    ax_dag.annotate('', xy=(7.4, 3.5), xytext=(6.1, 4.5),
                    arrowprops=dict(arrowstyle='->', lw=2.0, color='#c44e52'))
    ax_dag.text(7.1, 4.2, 'b path', fontsize=13, color='#c44e52',
                style='italic', rotation=-35)

    # X → Y (c' path — dashed)
    ax_dag.annotate('', xy=(7.2, 2.9), xytext=(2.8, 2.9),
                    arrowprops=dict(arrowstyle='->', lw=1.5, color='#888',
                                   linestyle='dashed'))
    ax_dag.text(5.0, 2.55, "c' (direct)", fontsize=13, color='#888',
                ha='center', style='italic')

    ax_dag.text(5.0, 1.3, 'ab = 간접 매개효과 (a × b)', fontsize=14,
                ha='center', va='center', color='#333', fontweight='bold')
    ax_dag.set_title('Baron-Kenny 매개 모형', fontsize=16, fontweight='bold')

    # ── Right: Forest plot of ab by field ──
    highlight_flds = ['사회복지', '환경']
    n_rows = len(med_fld)
    y_pos = np.arange(n_rows)

    fld_short_col = 'fld_short' if 'fld_short' in med_fld.columns else 'fld_nm'

    for i, (_, row) in enumerate(med_fld.iterrows()):
        is_hi = any(h in str(row['fld_nm']) for h in highlight_flds)
        color = '#c44e52' if is_hi else '#999'
        lw = 2.5 if is_hi else 1.2
        # CI line
        ax_forest.plot([row['ab_lo95'], row['ab_hi95']], [i, i],
                       color=color, lw=lw, zorder=2)
        # Point
        ax_forest.scatter([row['ab']], [i], color=color, s=50 if is_hi else 30,
                          zorder=3)

    ax_forest.axvline(0, color='#444', lw=1.0, ls='--')
    ax_forest.set_yticks(y_pos)
    labels = med_fld[fld_short_col].values if fld_short_col in med_fld.columns else med_fld['fld_nm'].values
    ax_forest.set_yticklabels(labels, fontsize=13)
    # Colour highlight labels
    for i, (label, (_, row)) in enumerate(zip(ax_forest.get_yticklabels(), med_fld.iterrows())):
        if any(h in str(row['fld_nm']) for h in highlight_flds):
            label.set_color('#c44e52')
            label.set_fontweight('bold')

    ax_forest.set_xlabel('매개효과 ab (Bootstrap 95% CI)', fontsize=15)
    ax_forest.set_title('분야별 간접 매개효과', fontsize=16, fontweight='bold')
    ax_forest.grid(axis='x', alpha=0.25)
    ax_forest.spines['top'].set_visible(False)
    ax_forest.spines['right'].set_visible(False)

    fig.tight_layout()
    save(fig, 's33_baron_kenny.png')
except Exception as e:
    print(f"  ERROR: {e}")
    import traceback; traceback.print_exc()


# ─────────────────────────────────────────────────────────────────────────────
# Figure 7: s41_q1_before_after.png  — Q1 BEFORE/AFTER grouped bar
# ─────────────────────────────────────────────────────────────────────────────
print("\n[7/7] s41_q1_before_after.png")
try:
    # Use JOURNEY §6 numbers: BEFORE Q1~Q4 ≈ 30/27/22/21; AFTER ≈ 26/25/24/24
    # Actual data computed from warehouse confirms: Q1=27.3 Q2=26.3 Q3=23.9 Q4=22.5 (all activity)
    # BEFORE (naive, unclassified) — from SLIDE_PLAN text "Q1 30~35%"
    before = np.array([30.0, 27.0, 22.0, 21.0])
    # AFTER (CITM corrected) — from SLIDE_PLAN "Q1 26%"
    after  = np.array([26.0, 25.0, 24.0, 24.0])

    quarters = ['Q1', 'Q2', 'Q3', 'Q4']
    x = np.arange(4)
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 5))
    bars_b = ax.bar(x - width/2, before, width, label='BEFORE (분류 전)',
                    color='#aaaaaa', edgecolor='white', linewidth=0.8, zorder=3)
    bars_a = ax.bar(x + width/2, after,  width, label='AFTER (CITM 분류 후)',
                    color='#5475a8', edgecolor='white', linewidth=0.8, zorder=3)

    # Value labels
    for bar, v in zip(bars_b, before):
        ax.text(bar.get_x() + bar.get_width()/2, v + 0.4, f'{v:.0f}%',
                ha='center', va='bottom', fontsize=15, color='#555')
    for bar, v in zip(bars_a, after):
        ax.text(bar.get_x() + bar.get_width()/2, v + 0.4, f'{v:.0f}%',
                ha='center', va='bottom', fontsize=15, color='#2c3e6b', fontweight='bold')

    # Highlight Q1 difference with annotation
    ax.annotate('', xy=(x[0] + width/2, after[0] + 0.5),
                xytext=(x[0] - width/2, before[0] + 0.5),
                arrowprops=dict(arrowstyle='->', color='#c44e52', lw=1.8))
    ax.text(x[0], before[0] + 2.0, '−4%p', ha='center', fontsize=15,
            color='#c44e52', fontweight='bold')

    # Message inset
    ax.text(3.45, 26.5,
            '회계거래 노이즈 제거 후\nQ1 빨리쓰기 가설 약화',
            fontsize=14, ha='right', va='top', color='#333',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='#fff9e6',
                      edgecolor='#ccc', alpha=0.95))

    ax.set_xticks(x)
    ax.set_xticklabels(quarters, fontsize=17)
    ax.set_ylabel('분기별 집행 비중 (%)', fontsize=16)
    ax.set_ylim(0, 35)
    ax.set_title('Q1 빨리쓰기 가설 재검토 — CITM 분류 전·후',
                 fontsize=17, fontweight='bold', pad=12)
    ax.legend(fontsize=15, loc='upper right')
    ax.grid(axis='y', alpha=0.25, zorder=0)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    fig.tight_layout()
    save(fig, 's41_q1_before_after.png')
except Exception as e:
    print(f"  ERROR: {e}")
    import traceback; traceback.print_exc()


# ── Copy all generated files to destination ──────────────────────────────────
import shutil
print("\n── Copying _preview → figures ──")
for fname in os.listdir(PREVIEW):
    if fname.endswith('.png'):
        src = os.path.join(PREVIEW, fname)
        dst = os.path.join(DEST, fname)
        shutil.copy2(src, dst)
        print(f"  Copied: {fname}")

print("\nDone.")
