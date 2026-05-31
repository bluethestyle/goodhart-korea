"""§ 3·§ 4·§ 5 본문 차트 9장 재생성 — 보고서 톤 (EDA 스크립트 사양 통일).

학술 논문용 차트(폰트 17-20pt, 좁은 figure 영역)는 보고서 본문(Pretendard 10.5pt)에 부적합.
본 스크립트는 동일 분석 결과를 figsize 7.4×3.6 / dpi 170 / font 10-11pt로 재생성한다.

출력: paper/figures/report/
입력: data/results/H22_*·H8_*·H3_*·H27_*·H28_*.csv + warehouse.duckdb (월별 raw)
"""
import os, sys, io
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager, colors as mcolors
from matplotlib.patches import Rectangle
import duckdb

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ── 폰트 등록 ─────────────────────────────────────────────────────
for f in ['Pretendard-Regular.otf', 'Pretendard-SemiBold.otf', 'Pretendard-Bold.otf']:
    p = os.path.join(ROOT, 'paper', 'fonts', f)
    if os.path.exists(p):
        font_manager.fontManager.addfont(p)

# ── 보고서 톤 표준 ────────────────────────────────────────────────
plt.rcParams.update({
    'font.family': 'Pretendard',
    'axes.unicode_minus': False,
    'font.size': 10.5,
    'axes.titlesize': 11,
    'axes.labelsize': 10.5,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 9.5,
    'axes.linewidth': 0.6,
    'axes.edgecolor': '#525252',
    'axes.spines.top': False,
    'axes.spines.right': False,
    'xtick.color': '#525252',
    'ytick.color': '#525252',
    'xtick.major.size': 3,
    'ytick.major.size': 3,
    'grid.color': '#e5e5e5',
    'grid.linewidth': 0.5,
    'grid.alpha': 0.7,
})

# 색상 (analysis_report.typ과 동일)
INK     = '#0a0a0a'
MID     = '#525252'
SOFT    = '#a3a3a3'
ACCENT  = '#2563eb'
POS     = '#15803d'
NEG     = '#b91c1c'
WARN    = '#a16207'
LINE_C  = '#e5e5e5'

# 4개 사업 형태 색상 (EDA fig_2_4와 통일)
ARCH_COLOR = {
    'C0_personnel':     '#525252',  # 인건비형 - 진한 회색
    'C1_direct_invest': '#b91c1c',  # 자산취득형 - 진한 빨강
    'C2_chooyeon':      '#a16207',  # 출연금형 - 황토
    'C3_normal':        '#9ca3af',  # 정상사업 - 회색
}
ARCH_LABEL = {
    'C0_personnel':     '인건비형 (n=129)',
    'C1_direct_invest': '자산취득형 (n=99)',
    'C2_chooyeon':      '출연금형 (n=154)',
    'C3_normal':        '정상사업 (n=1,175)',
}
# CSV의 archetype 라벨 변형 호환
ARCH_ALIAS = {
    'C0_personnel': 'C0_personnel',
    'C1_direct_invest': 'C1_direct_invest',
    'C2_chooyeon': 'C2_chooyeon',
    'C3_normal': 'C3_normal',
}

OUT = os.path.join(ROOT, 'paper', 'figures', 'report')
RES = os.path.join(ROOT, 'data', 'results')
os.makedirs(OUT, exist_ok=True)


def style_ax(ax):
    """공통 축 스타일."""
    ax.spines['left'].set_color(MID)
    ax.spines['bottom'].set_color(MID)
    ax.grid(axis='y', alpha=0.4, linewidth=0.5)
    ax.set_axisbelow(True)


def save(name, w=7.4, h=3.6):
    """tight_layout + savefig + size 보고."""
    out = os.path.join(OUT, name)
    plt.savefig(out, dpi=170, bbox_inches='tight', facecolor='white', pad_inches=0.2)
    plt.close()
    from PIL import Image
    im = Image.open(out)
    print(f'  → {name}  {im.size}')


# ══════════════════════════════════════════════════════════════════
#  FIG-3.1  월별 활동 평균 일집행액 (연도별 색)
# ══════════════════════════════════════════════════════════════════
def fig_h22_monthly():
    print('FIG-3.1 h22_rdd_monthly')
    con = duckdb.connect(os.path.join(ROOT, 'data', 'warehouse.duckdb'), read_only=True)
    df = con.execute("""
    WITH days AS (
      SELECT FSCL_YY, EXE_M,
             CASE
               WHEN EXE_M IN (1,3,5,7,8,10,12) THEN 31
               WHEN EXE_M IN (4,6,9,11) THEN 30
               WHEN EXE_M = 2 AND (FSCL_YY % 4 = 0 AND (FSCL_YY % 100 != 0 OR FSCL_YY % 400 = 0)) THEN 29
               WHEN EXE_M = 2 THEN 28
             END AS dpm
      FROM monthly_exec WHERE FSCL_YY BETWEEN 2015 AND 2025
      GROUP BY FSCL_YY, EXE_M
    ),
    daily AS (
      SELECT m.FSCL_YY, m.EXE_M, m.ACTV_CD,
             sum(m.EP_AMT) * 1.0 / max(d.dpm) AS daily_amt
      FROM monthly_exec m JOIN days d USING (FSCL_YY, EXE_M)
      WHERE m.FSCL_YY BETWEEN 2015 AND 2025 AND m.EP_AMT > 0
      GROUP BY m.FSCL_YY, m.EXE_M, m.ACTV_CD
    )
    SELECT FSCL_YY, EXE_M, AVG(daily_amt) / 1e6 AS avg_daily_mil
    FROM daily GROUP BY FSCL_YY, EXE_M ORDER BY FSCL_YY, EXE_M
    """).fetchdf()
    con.close()

    fig, ax = plt.subplots(figsize=(7.4, 3.6), dpi=170)
    years = sorted(df['FSCL_YY'].unique())
    cmap = plt.get_cmap('viridis')
    for i, y in enumerate(years):
        sub = df[df['FSCL_YY'] == y].sort_values('EXE_M')
        c = cmap(i / max(len(years) - 1, 1))
        ax.plot(sub['EXE_M'], sub['avg_daily_mil'], color=c, alpha=0.5, lw=1.0, marker='o', ms=2.5)
    # 11년 평균
    mean = df.groupby('EXE_M')['avg_daily_mil'].mean()
    ax.plot(mean.index, mean.values, color=INK, lw=2.2, marker='o', ms=5, label='11년 평균')
    # 11-12월 강조
    ax.axvspan(10.5, 12.5, alpha=0.08, color=NEG, zorder=0)
    ax.axvline(11.5, color=NEG, lw=0.8, ls='--', alpha=0.5)
    ax.text(11.5, ax.get_ylim()[1]*0.95, '12월 cutoff', color=NEG, fontsize=9, ha='left', va='top')

    # 색바: 연도
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=years[0], vmax=years[-1]))
    cbar = plt.colorbar(sm, ax=ax, pad=0.02, fraction=0.04)
    cbar.set_label('연도', fontsize=9.5, color=MID)
    cbar.ax.tick_params(labelsize=9, colors=MID)
    cbar.outline.set_visible(False)

    ax.set_xticks(range(1, 13))
    ax.set_xticklabels([f'{m}월' for m in range(1, 13)])
    ax.set_ylabel('활동 평균 일집행액 (백만원)')
    ax.set_xlim(0.5, 12.5)
    ax.legend(loc='upper left', frameon=False)
    style_ax(ax)
    plt.tight_layout()
    save('h22_rdd_monthly.png')


# ══════════════════════════════════════════════════════════════════
#  FIG-3.2  분야별 12월 점프 배수 (수평 막대)
# ══════════════════════════════════════════════════════════════════
def fig_h22_field():
    print('FIG-3.2 h22_rdd_field')
    df = pd.read_csv(os.path.join(RES, 'H22_field_rdd.csv'), encoding='utf-8-sig')
    df = df[df['bw'] == 1].copy()  # bandwidth 1년만
    df = df.sort_values('mult', ascending=True)

    fig, ax = plt.subplots(figsize=(7.4, 4.6), dpi=170)
    colors = [NEG if v > 2.0 else (WARN if v > 1.5 else SOFT) for v in df['mult']]
    bars = ax.barh(df['label'], df['mult'], color=colors, edgecolor='white', lw=0.6, height=0.7)
    # 1.0 기준선
    ax.axvline(1.0, color=MID, ls='--', lw=0.7, alpha=0.6)
    # 막대 끝 라벨
    for b, v in zip(bars, df['mult']):
        ax.text(v + 0.05, b.get_y() + b.get_height()/2,
                f'{v:.2f}×', va='center', fontsize=9.5, color=INK, weight='semibold')
    ax.set_xlabel('12월 점프 배수 (12월 첫 주 / 11월 마지막 주, log scale)')
    ax.set_xlim(0, df['mult'].max() * 1.15)
    style_ax(ax)
    ax.grid(axis='x', alpha=0.4, linewidth=0.5)
    ax.grid(axis='y', alpha=0)
    plt.tight_layout()
    save('h22_rdd_field.png', h=4.6)


# ══════════════════════════════════════════════════════════════════
#  FIG-3.3  사업원형별 12월 점프 forest plot
# ══════════════════════════════════════════════════════════════════
def fig_h22_appendix():
    print('FIG-3.3 h22_rdd_appendix (forest plot)')
    # 본문 인용 수치 (main_v2.typ §6.3 / report_outline.md)
    archetypes = [
        ('자산취득형', 3.42, 3.05, 3.79, NEG,  True,  99),
        ('정상사업',   2.24, 2.13, 2.35, NEG,  True,  1175),
        ('인건비형',   1.12, 1.02, 1.22, MID,  True,  129),
        ('출연금형',   1.10, 0.95, 1.25, SOFT, False, 154),  # 통계 미달 → 회색
    ]
    fig, ax = plt.subplots(figsize=(7.4, 3.2), dpi=170)
    y = np.arange(len(archetypes))
    for i, (name, m, lo, hi, c, sig, n) in enumerate(archetypes):
        ax.plot([lo, hi], [i, i], color=c, lw=2.2, solid_capstyle='round')
        ax.plot(m, i, 'o', color=c, ms=10, mec='white', mew=1.2)
        # 라벨
        ax.text(hi + 0.12, i, f'{m:.2f}×', va='center', fontsize=10.5,
                color=c, weight='semibold')
        ax.text(0.05, i - 0.34, f'n={n:,}', fontsize=9, color=SOFT, va='top')
    ax.axvline(1.0, color=MID, ls='--', lw=0.7, alpha=0.6)
    ax.axvline(1.91, color=ACCENT, ls=':', lw=1.0, alpha=0.7)
    ax.text(1.91 + 0.05, len(archetypes) - 0.55, '전체 평균 1.91×',
            fontsize=9, color=ACCENT)
    ax.set_yticks(y)
    ax.set_yticklabels([a[0] for a in archetypes])
    ax.set_xlabel('12월 점프 배수 (95% CI)')
    ax.set_xlim(0.7, 4.2)
    ax.set_ylim(-0.7, len(archetypes) - 0.2)
    ax.invert_yaxis()  # 자산취득 위쪽
    style_ax(ax)
    ax.grid(axis='x', alpha=0.4, linewidth=0.5)
    ax.grid(axis='y', alpha=0)
    plt.tight_layout()
    save('h22_rdd_appendix.png', h=3.2)


# ══════════════════════════════════════════════════════════════════
#  FIG-3.4  연도별 12월 점프 (h22_rdd_yearly)
# ══════════════════════════════════════════════════════════════════
def fig_h22_yearly():
    print('FIG-3.4 h22_rdd_yearly')
    con = duckdb.connect(os.path.join(ROOT, 'data', 'warehouse.duckdb'), read_only=True)
    df = con.execute("""
    WITH days AS (
      SELECT FSCL_YY, EXE_M,
             CASE WHEN EXE_M = 11 THEN 30 WHEN EXE_M = 12 THEN 31 END AS dpm
      FROM monthly_exec WHERE FSCL_YY BETWEEN 2015 AND 2025 AND EXE_M IN (11, 12)
      GROUP BY FSCL_YY, EXE_M
    ),
    nov_dec AS (
      SELECT m.FSCL_YY, m.EXE_M, m.ACTV_CD,
             LN(sum(m.EP_AMT) * 1.0 / max(d.dpm) + 1) AS log_daily
      FROM monthly_exec m JOIN days d USING (FSCL_YY, EXE_M)
      WHERE m.EP_AMT > 0
      GROUP BY m.FSCL_YY, m.EXE_M, m.ACTV_CD
    ),
    diff AS (
      SELECT FSCL_YY,
             median(CASE WHEN EXE_M = 12 THEN log_daily END)
              - median(CASE WHEN EXE_M = 11 THEN log_daily END) AS log_jump
      FROM nov_dec GROUP BY FSCL_YY
    )
    SELECT FSCL_YY, log_jump FROM diff ORDER BY FSCL_YY
    """).fetchdf()
    con.close()

    fig, ax = plt.subplots(figsize=(7.4, 3.4), dpi=170)
    ax.bar(df['FSCL_YY'], df['log_jump'], color=NEG, alpha=0.85,
           edgecolor='white', lw=0.8, width=0.7)
    # 전체 평균 (β = 0.65)
    ax.axhline(0.65, color=WARN, ls='--', lw=1.4, alpha=0.9, label='전체 β=0.65 (1.91×)')
    # 미국 5x 참조 (log 5 = 1.609)
    ax.axhline(np.log(5), color='#7c3aed', ls=':', lw=1.4, alpha=0.9,
               label='미국 Liebman-Mahoney 5× (log 5≈1.61)')
    ax.set_xlabel('회계연도')
    ax.set_ylabel('12월 점프 β (log 일집행액 12월 − 11월)')
    ax.set_xticks(df['FSCL_YY'])
    ax.set_xticklabels(df['FSCL_YY'].astype(int), rotation=0)
    ax.legend(loc='upper right', frameon=False)
    ax.set_ylim(0, max(df['log_jump'].max(), 1.7) * 1.05)
    style_ax(ax)
    plt.tight_layout()
    save('h22_rdd_yearly.png', h=3.4)


# ══════════════════════════════════════════════════════════════════
#  FIG-4.1  분야 trivial 검정 패널 (h8_panel)
# ══════════════════════════════════════════════════════════════════
def fig_h8_panel():
    print('FIG-4.1 h8_panel')
    df = pd.read_csv(os.path.join(RES, 'H8_field_archetype_decomp_v3.csv'), encoding='utf-8-sig')
    # model 라벨 한국어 매핑
    name_map = {
        'A_base':                  '베이스라인',
        'B_field_FE':              '+분야 FE',
        'C_archetype_amp_int':     '+사업 유형 × 진동',
        'B_archetype_FE':          '+사업 유형 FE',
        'C_field_archetype_int':   '+분야 × 사업 유형',
    }
    df['label'] = df['model'].map(name_map).fillna(df['model'])

    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.4), dpi=170,
                              gridspec_kw={'width_ratios': [1.0, 1.2]})
    # 좌: 누적 R²
    ax = axes[0]
    bar_colors = [SOFT, MID, NEG, MID, ACCENT][:len(df)]
    ax.bar(df['label'], df['r2'], color=bar_colors, edgecolor='white', lw=0.6, width=0.7)
    for i, v in enumerate(df['r2']):
        ax.text(i, v + 0.001, f'{v:.3f}', ha='center', fontsize=9, color=INK, weight='semibold')
    ax.set_ylabel('모형 R²')
    ax.set_title('누적 설명력', fontsize=10.5, color=MID, pad=8)
    ax.set_xticklabels(df['label'], rotation=15, ha='right')
    style_ax(ax)

    # 우: ΔR²
    ax = axes[1]
    delta_colors = [SOFT if v < 0.005 else NEG for v in df['delta_r2']]
    ax.bar(df['label'], df['delta_r2'], color=delta_colors, edgecolor='white', lw=0.6, width=0.7)
    for i, v in enumerate(df['delta_r2']):
        ax.text(i, v + 0.0005, f'+{v:.3f}' if v > 0 else f'{v:.3f}',
                ha='center', fontsize=9, color=INK, weight='semibold')
    ax.set_ylabel('ΔR² (이전 모형 대비)')
    ax.set_title('단계별 증분', fontsize=10.5, color=MID, pad=8)
    ax.set_xticklabels(df['label'], rotation=15, ha='right')
    style_ax(ax)

    plt.tight_layout()
    save('h8_panel.png', h=3.4)


# ══════════════════════════════════════════════════════════════════
#  FIG-4.2  UMAP 임베딩 (h3_umap) — 두 패널 비교
#   상단: HDBSCAN 4 사업원형 색상
#   하단: 상위 8개 분야 색상
#   메시지: "같은 분야 안에서도 사업 형태가 공간상 분리,
#           다른 분야의 같은 형태가 가까이 모인다."
# ══════════════════════════════════════════════════════════════════
def fig_h3_umap():
    print('FIG-4.2 h3_umap (두 패널)')
    df = pd.read_csv(os.path.join(RES, 'H3_activity_embedding_11y.csv'), encoding='utf-8-sig')

    fig, axes = plt.subplots(2, 1, figsize=(7.4, 8.4), dpi=170,
                              gridspec_kw={'hspace': 0.28})

    # ─── 상단: HDBSCAN 4 사업원형 ───────────────────────────────
    ax = axes[0]
    cluster_color = {0: MID, 1: NEG, 2: WARN, 3: SOFT}
    cluster_label = {
        0: '인건비형 (n=129)',
        1: '자산취득형 (n=99)',
        2: '출연금형 (n=154)',
        3: '정상사업 (n=1,175)',
    }
    # 정상사업을 먼저(뒤로)
    for cl in [3, 0, 1, 2]:
        sub = df[df['cluster'] == cl]
        ax.scatter(sub['u1'], sub['u2'], c=cluster_color[cl], s=10,
                   alpha=0.55 if cl == 3 else 0.85, edgecolors='white',
                   linewidths=0.3, label=cluster_label[cl])
    ax.set_title('① HDBSCAN 사업원형 색상 (1,557 활동)',
                  fontsize=11, color=INK, weight='semibold', loc='left', pad=8)
    ax.set_xlabel('UMAP 1')
    ax.set_ylabel('UMAP 2')
    ax.legend(loc='best', frameon=False, scatterpoints=1, markerscale=1.6,
              fontsize=9, ncol=2, columnspacing=1.0)
    style_ax(ax)
    ax.grid(alpha=0.25, linewidth=0.5)

    # ─── 하단: 상위 8개 분야 ─────────────────────────────────────
    ax = axes[1]
    top_fields = df['FLD_NM'].value_counts().head(8).index.tolist()
    field_palette = ['#2563eb', '#b91c1c', '#15803d', '#a16207',
                      '#7c3aed', '#0891b2', '#db2777', '#525252']
    field_color = dict(zip(top_fields, field_palette))

    # 그 외 분야는 회색 배경으로
    other = df[~df['FLD_NM'].isin(top_fields)]
    ax.scatter(other['u1'], other['u2'], c='#e5e5e5', s=6, alpha=0.45,
               edgecolors='none', label='그 외 분야')

    for fld in top_fields:
        sub = df[df['FLD_NM'] == fld]
        ax.scatter(sub['u1'], sub['u2'], c=field_color[fld], s=12,
                   alpha=0.85, edgecolors='white', linewidths=0.3,
                   label=f'{fld} (n={len(sub)})')
    ax.set_title('② 상위 8개 분야 색상 — 같은 분야가 공간상 분리, 다른 분야가 가까이 모인다',
                  fontsize=11, color=INK, weight='semibold', loc='left', pad=8)
    ax.set_xlabel('UMAP 1')
    ax.set_ylabel('UMAP 2')
    ax.legend(loc='best', frameon=False, scatterpoints=1, markerscale=1.4,
              fontsize=8.5, ncol=2, columnspacing=0.8)
    style_ax(ax)
    ax.grid(alpha=0.25, linewidth=0.5)

    plt.tight_layout()
    save('h3_umap.png', h=8.4)


# ══════════════════════════════════════════════════════════════════
#  FIG-5.1  PSD by archetype (h27_psd)
# ══════════════════════════════════════════════════════════════════
def fig_h27_psd():
    print('FIG-5.1 h27_psd')
    df = pd.read_csv(os.path.join(RES, 'H27_psd_archetype_avg.csv'), encoding='utf-8-sig')
    # k 컬럼: psdnorm_k1 ~ psdnorm_k6
    ks = list(range(1, 7))
    periods = [12 / k for k in ks]  # k=1 → 12개월, k=2 → 6개월 ...

    fig, ax = plt.subplots(figsize=(7.4, 3.6), dpi=170)
    for _, row in df.iterrows():
        arch = row['archetype']
        if arch not in ARCH_COLOR:
            continue
        vals = [row[f'psdnorm_k{k}'] for k in ks]
        lw = 2.4 if arch == 'C2_chooyeon' else 1.4
        alpha = 1.0 if arch == 'C2_chooyeon' else 0.75
        ax.plot(ks, vals, marker='o', ms=6, color=ARCH_COLOR[arch],
                lw=lw, alpha=alpha, label=ARCH_LABEL[arch])
    # k=1 강조
    ax.axvline(1, color=NEG, ls=':', lw=0.8, alpha=0.4)
    ax.text(1.05, ax.get_ylim()[1]*0.92, '12개월 주기 (k=1)', fontsize=9, color=NEG)

    ax.set_xticks(ks)
    ax.set_xticklabels([f'k={k}\n({p:.1f}개월)' if k <= 3 else f'k={k}' for k, p in zip(ks, periods)])
    ax.set_xlabel('주기 (k)')
    ax.set_ylabel('정규화 PSD')
    ax.legend(loc='upper right', frameon=False)
    style_ax(ax)
    plt.tight_layout()
    save('h27_psd.png')


# ══════════════════════════════════════════════════════════════════
#  FIG-5.2  Phase coherence heatmap (h27_coherence)
# ══════════════════════════════════════════════════════════════════
def fig_h27_coherence():
    print('FIG-5.2 h27_coherence')
    df = pd.read_csv(os.path.join(RES, 'H27_coherence_intra_archetype.csv'), encoding='utf-8-sig')
    # archetype × k pivot
    arch_order = ['C2_chooyeon', 'C1_direct_invest', 'C3_normal', 'C0_personnel']
    pv = df.pivot(index='archetype', columns='k', values='phase_coherence')
    pv = pv.reindex(arch_order)

    fig, ax = plt.subplots(figsize=(7.4, 2.8), dpi=170)
    cmap = plt.get_cmap('Oranges')
    im = ax.imshow(pv.values, cmap=cmap, vmin=0, vmax=0.6, aspect='auto')
    # 셀 값 텍스트
    for i in range(pv.shape[0]):
        for j in range(pv.shape[1]):
            v = pv.values[i, j]
            color = 'white' if v > 0.35 else INK
            ax.text(j, i, f'{v:.2f}', ha='center', va='center',
                    fontsize=10, color=color, weight='semibold')

    ax.set_yticks(range(len(arch_order)))
    ax.set_yticklabels([ARCH_LABEL[a].split(' (')[0] for a in arch_order])
    ks = list(pv.columns)
    ax.set_xticks(range(len(ks)))
    ax.set_xticklabels([f'k={k}\n({12/k:.1f}개월)' for k in ks])
    ax.set_xlabel('주기 (k)')
    cbar = plt.colorbar(im, ax=ax, fraction=0.04, pad=0.02)
    cbar.set_label('Phase coherence', fontsize=9.5, color=MID)
    cbar.ax.tick_params(labelsize=9, colors=MID)
    cbar.outline.set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    plt.tight_layout()
    save('h27_coherence.png', h=2.8)


# ══════════════════════════════════════════════════════════════════
#  FIG-5.3  Wavelet 12m power 시간 진화 (h28_evolution)
# ══════════════════════════════════════════════════════════════════
def fig_h28_evolution():
    print('FIG-5.3 h28_evolution')
    df = pd.read_csv(os.path.join(RES, 'H28_wavelet_12m_evolution.csv'), encoding='utf-8-sig')

    fig, ax = plt.subplots(figsize=(7.4, 3.6), dpi=170)
    order = ['C0_personnel', 'C1_direct_invest', 'C3_normal', 'C2_chooyeon']
    for arch in order:
        sub = df[df['archetype'] == arch].sort_values('year')
        if sub.empty:
            continue
        lw = 2.6 if arch == 'C2_chooyeon' else 1.6
        ax.plot(sub['year'], sub['power_12m'], marker='o', ms=5,
                color=ARCH_COLOR[arch], lw=lw, label=ARCH_LABEL[arch])

    # COVID 영역 강조
    ax.axvspan(2019, 2021, alpha=0.07, color=ACCENT, zorder=0)
    ax.text(2020, ax.get_ylim()[1]*0.92, 'COVID', fontsize=9, color=ACCENT,
            ha='center', alpha=0.8)

    # 출연금형 +554% 라벨
    cho = df[df['archetype'] == 'C2_chooyeon'].sort_values('year')
    if len(cho) > 0:
        last = cho.iloc[-1]
        ax.annotate('+554%', xy=(last['year'], last['power_12m']),
                    xytext=(last['year']-0.5, last['power_12m']+0.05),
                    fontsize=10.5, color=WARN, weight='semibold')

    ax.set_xlabel('연도')
    ax.set_ylabel('12개월 cycle 진폭 (wavelet power)')
    ax.legend(loc='upper left', frameon=False)
    style_ax(ax)
    plt.tight_layout()
    save('h28_evolution.png')


# ══════════════════════════════════════════════════════════════════
#  FIG-7.1  3-way 측정 도구 상관 (FFT·STL·NP, 활동-연도 패널)
# ══════════════════════════════════════════════════════════════════
def fig_np_correlation():
    print('FIG-7.1 np_correlation')
    df = pd.read_csv(os.path.join(RES, 'H26_neuralprophet_summary.csv'), encoding='utf-8-sig')
    # 3x3 상관 매트릭스 구축
    labels = ['FFT', 'STL', 'NP']
    M = np.zeros((3, 3))
    for i, row_label in enumerate(['FFT amp_12m_norm', 'STL seasonal_strength', 'NP yearly_seasonality']):
        for j, col in enumerate(['r_vs_FFT', 'r_vs_STL', 'r_vs_NP']):
            sub = df[df['measure'] == row_label]
            if not sub.empty:
                M[i, j] = sub.iloc[0][col]
    # row label NP 확인 (CSV 라벨이 다를 수 있음)
    # H26_neuralprophet_summary.csv 형식 확인 — measure 컬럼이 'NP'로 끝나는 행 보충
    np_row = df[df['measure'].str.contains('NP|NeuralProphet', regex=True, na=False)]
    if not np_row.empty:
        for j, col in enumerate(['r_vs_FFT', 'r_vs_STL', 'r_vs_NP']):
            M[2, j] = np_row.iloc[0][col]

    fig, ax = plt.subplots(figsize=(5.4, 4.2), dpi=170)
    cmap = plt.get_cmap('RdBu_r')
    im = ax.imshow(M, cmap=cmap, vmin=-0.5, vmax=1.0, aspect='auto')
    for i in range(3):
        for j in range(3):
            v = M[i, j]
            color = 'white' if v > 0.6 else INK
            ax.text(j, i, f'{v:.3f}', ha='center', va='center',
                    fontsize=11, color=color, weight='semibold')
    ax.set_xticks(range(3)); ax.set_yticks(range(3))
    ax.set_xticklabels(labels); ax.set_yticklabels(labels)
    cbar = plt.colorbar(im, ax=ax, fraction=0.04, pad=0.02)
    cbar.set_label('상호 상관 (r)', fontsize=9.5, color=MID)
    cbar.ax.tick_params(labelsize=9, colors=MID)
    cbar.outline.set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    plt.tight_layout()
    save('np_correlation.png', w=5.4, h=4.2)


# ══════════════════════════════════════════════════════════════════
#  FIG-7.2  14분야 outcome 상관 3-way 비교 (FFT·STL·NP)
# ══════════════════════════════════════════════════════════════════
def fig_np_3way_outcome():
    print('FIG-7.2 np_3way_outcome')
    df = pd.read_csv(os.path.join(RES, 'H26_field_outcome_corr_np.csv'), encoding='utf-8-sig')
    # 부호 일관성 기준 정렬: corr_np 오름차순 (음 신호 강한 분야 위)
    df = df.sort_values('corr_np').reset_index(drop=True)

    fig, ax = plt.subplots(figsize=(7.4, 5.4), dpi=170)
    y = np.arange(len(df))
    w = 0.27
    # FFT 빨강, STL 회색, NP 파랑
    ax.barh(y - w, df['corr_fft'], height=w, color=NEG, alpha=0.85,
             edgecolor='white', lw=0.5, label='FFT amp_12m_norm')
    ax.barh(y,      df['corr_stl'], height=w, color=SOFT, alpha=0.85,
             edgecolor='white', lw=0.5, label='STL seasonal_strength')
    ax.barh(y + w, df['corr_np'],  height=w, color=ACCENT, alpha=0.85,
             edgecolor='white', lw=0.5, label='NP yearly_seasonality')
    # 0 기준선
    ax.axvline(0, color=MID, lw=0.6, alpha=0.7)
    ax.set_yticks(y)
    ax.set_yticklabels(df['fld'])
    ax.set_xlabel('outcome 상관 r (음 = 측정 적응 강함)')
    ax.set_xlim(-0.85, 0.85)
    # 사회복지 강조 — 부호 반전 분야
    sw_idx = df.index[df['fld'] == '사회복지']
    if len(sw_idx) > 0:
        idx = sw_idx[0]
        ax.axhspan(idx - 0.5, idx + 0.5, alpha=0.06, color=WARN, zorder=0)
        ax.text(0.82, idx, '부호 반전 분야', fontsize=8.5, color=WARN,
                ha='right', va='center', alpha=0.9)
    ax.legend(loc='lower right', frameon=False, fontsize=9)
    style_ax(ax)
    ax.grid(axis='x', alpha=0.4, linewidth=0.5)
    ax.grid(axis='y', alpha=0)
    plt.tight_layout()
    save('np_3way_outcome.png', h=5.4)


if __name__ == '__main__':
    print(f'Output: {OUT}\n')
    fig_h22_monthly()
    fig_h22_field()
    fig_h22_appendix()
    fig_h22_yearly()
    fig_h8_panel()
    fig_h3_umap()
    fig_h27_psd()
    fig_h27_coherence()
    fig_h28_evolution()
    fig_np_correlation()
    fig_np_3way_outcome()
    print('\nAll 11 figures done.')
