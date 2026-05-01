"""generate_v3_charts.py
Generate 4 new v3 chart images for the paper — Korean + English versions.

Charts:
  1. h10_v3_robustness.png   — H5 robustness: 3 measures + LOO
  2. h9_v3_time_evo.png      — topology / wavelet dual (copy + resize)
  3. v3_calibration.png      — implied w_t/w_q ratios from official handbooks
  4. v3_alio_grades.png      — ALIO public institution grade distribution 2022-2024

Output:
  paper/figures/   (Korean labels)
  paper/figures_en/ (English labels)
"""

import os, sys, shutil, warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.patches as mpatches
from PIL import Image

warnings.filterwarnings('ignore')

try:
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
except AttributeError:
    pass

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(ROOT, 'data', 'results')
FIGS_SRC= os.path.join(ROOT, 'data', 'figs')
EXT     = os.path.join(ROOT, 'data', 'external')
FIG_KR  = os.path.join(ROOT, 'paper', 'figures')
FIG_EN  = os.path.join(ROOT, 'paper', 'figures_en')
os.makedirs(FIG_KR, exist_ok=True)
os.makedirs(FIG_EN, exist_ok=True)

# ── Font setup ─────────────────────────────────────────────────────────────────
FONT_KR = 'DejaVu Sans'
for fname in ['Malgun Gothic', 'Arial Unicode MS', 'NanumGothic']:
    if any(fname.lower() in fn.name.lower()
           for fn in mpl.font_manager.fontManager.ttflist):
        FONT_KR = fname
        break

plt.rcParams.update({
    'font.size': 15,
    'axes.titlesize': 17,
    'axes.labelsize': 15,
    'xtick.labelsize': 13,
    'ytick.labelsize': 13,
    'legend.fontsize': 12,
    'mathtext.default': 'regular',
    'axes.unicode_minus': False,
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
})

DPI      = 200
MAX_W    = 1600   # max width in pixels after resize (raised for A4 PDF readability)

# ── Colours ────────────────────────────────────────────────────────────────────
COL_PERSONNEL   = '#5475a8'
COL_DIRECT_INV  = '#c44e52'
COL_CHOOYEON    = '#54a868'
COL_NORMAL      = '#888888'
COL_ACCENT      = '#b73a2c'    # brick red emphasis
COL_HIGHLIGHT   = '#e8a838'    # amber highlight for 사회복지

# ── Helpers ────────────────────────────────────────────────────────────────────

def set_font(lang: str):
    if lang == 'kr':
        mpl.rcParams['font.family'] = [FONT_KR, 'DejaVu Sans']
    else:
        mpl.rcParams['font.family'] = ['DejaVu Sans', FONT_KR, 'Arial', 'Times New Roman']


def save_resize(fig, path: str):
    """Save figure, then resize if wider than MAX_W pixels."""
    fig.savefig(path, dpi=DPI, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    img = Image.open(path)
    w, h = img.size
    if w > MAX_W:
        scale = MAX_W / w
        new_size = (MAX_W, int(h * scale))
        img = img.resize(new_size, Image.LANCZOS)
        img.save(path, optimize=True)
        print(f'    resized {w}x{h} -> {new_size[0]}x{new_size[1]}')
    else:
        print(f'    kept    {w}x{h}')


def copy_resize(src: str, dst: str):
    """Copy PNG and resize to max MAX_W wide."""
    shutil.copy2(src, dst)
    img = Image.open(dst)
    w, h = img.size
    if w > MAX_W:
        scale = MAX_W / w
        new_size = (MAX_W, int(h * scale))
        img = img.resize(new_size, Image.LANCZOS)
        img.save(dst, optimize=True)
        print(f'    copy+resize {w}x{h} -> {new_size[0]}x{new_size[1]}')
    else:
        print(f'    copy kept   {w}x{h}')


# ══════════════════════════════════════════════════════════════════════════════
# Chart 1 — h10_v3_robustness.png
# ══════════════════════════════════════════════════════════════════════════════
print('\n[1/4] h10_v3_robustness.png')

corr_path = os.path.join(RESULTS, 'H10_v3_alt_correlations.csv')
loo_path  = os.path.join(RESULTS, 'H10_v3_socialwelfare_loo.csv')

if not os.path.exists(corr_path):
    print('  SKIP: H10_v3_alt_correlations.csv not found')
else:
    df_corr = pd.read_csv(corr_path)
    print(f'  Loaded alt_correlations: {len(df_corr)} rows')

    # ── LOO data (사회복지 leave-one-out r values, 8 LOO_ rows only)
    loo_r = []
    if os.path.exists(loo_path):
        df_loo = pd.read_csv(loo_path)
        loo_r = df_loo[df_loo['removed_year_or_window'].str.startswith('LOO_')]['r'].dropna().tolist()
        print(f'  Loaded LOO r-values: {loo_r}')
    else:
        print('  WARNING: H10_v3_socialwelfare_loo.csv not found — LOO panel will be empty')

    # ── Helper: build a single version of the figure ──────────────────────────
    def make_h10_chart(lang: str) -> plt.Figure:
        set_font(lang)

        # Labels
        if lang == 'kr':
            panel_a_title  = '(A) 분야별 Pearson / Spearman / Kendall'
            panel_b_title  = '(B) 사회복지 LOO 분포'
            xlabel_a       = '상관계수'
            xlabel_b       = '상관계수 (LOO)'
            ylabel_a       = '분야'
            ylabel_b       = '빈도'
            legend_labels  = ['Pearson', 'Spearman', 'Kendall']
            orig_label     = f'원본 Pearson r = −0.86'
            suptitle       = 'H5 강건성 — 3 측도 부호 일관 + LOO 안정성'
            field_sw       = '사회복지'
            leg_title      = '측도'
        else:
            panel_a_title  = '(A) Pearson / Spearman / Kendall by Policy Field'
            panel_b_title  = '(B) LOO Distribution (사회복지 / Social Welfare)'
            xlabel_a       = 'Correlation coefficient'
            xlabel_b       = 'Correlation coefficient (LOO)'
            ylabel_a       = 'Policy field'
            ylabel_b       = 'Count'
            legend_labels  = ['Pearson', 'Spearman', 'Kendall']
            orig_label     = 'Original Pearson r = −0.86'
            suptitle       = 'H5 Robustness — Sign Consistency Across 3 Measures + LOO Stability'
            field_sw       = '사회복지'
            leg_title      = 'Measure'

        # English field-name mapping
        FIELD_EN = {
            '사회복지':         'Social Welfare',
            '보건':             'Health',
            '과학기술':         'Science & Tech',
            '산업·중소기업및에너지': 'Industry/SME/Energy',
            '문화및관광':       'Culture & Tourism',
            '교육':             'Education',
            '국토및지역개발':   'Regional Development',
            '일반·지방행정':    'Local Admin',
            '농림수산':         'Agriculture/Fishery',
            '교통및물류':       'Transport & Logistics',
            '환경':             'Environment',
            '통신':             'Telecom',
            '통일·외교':        'Unification/Diplomacy',
            '공공질서및안전':   'Public Safety',
            '국방':             'Defense',
        }

        fields = df_corr['field'].tolist()
        if lang == 'en':
            field_labels = [FIELD_EN.get(f, f) for f in fields]
        else:
            field_labels = fields

        n_fields = len(fields)
        y = np.arange(n_fields)
        bar_h = 0.22

        measures = [
            ('pearson_r',   legend_labels[0], '#5475a8'),
            ('spearman_rho', legend_labels[1], '#54a868'),
            ('kendall_tau', legend_labels[2], '#c44e52'),
        ]

        fig, (ax_a, ax_b) = plt.subplots(
            1, 2,
            figsize=(15, 7.5),
            gridspec_kw={'width_ratios': [2.5, 1]},
            facecolor='white'
        )

        # ── Panel A: grouped horizontal bar chart ──────────────────────────
        for idx, (col, lbl, col_c) in enumerate(measures):
            offsets = (idx - 1) * bar_h
            vals = df_corr[col].values
            # Highlight 사회복지 bar edges
            edge_colors = [COL_ACCENT if f == field_sw else 'none' for f in fields]
            edge_widths = [1.8    if f == field_sw else 0.0  for f in fields]
            ax_a.barh(
                y + offsets, vals, bar_h * 0.92,
                color=col_c, alpha=0.82,
                label=lbl,
                edgecolor=edge_colors, linewidth=edge_widths
            )

        ax_a.axvline(0, color='black', lw=0.8, zorder=5)
        ax_a.set_yticks(y)
        ax_a.set_yticklabels(field_labels, fontsize=13)
        ax_a.set_xlabel(xlabel_a)
        ax_a.set_title(panel_a_title, fontsize=15, fontweight='bold')
        ax_a.legend(title=leg_title, loc='lower right', fontsize=12, title_fontsize=12)
        ax_a.grid(axis='x', alpha=0.3)
        ax_a.set_xlim(-1.05, 1.05)

        # Shade 사회복지 row
        sw_idx = fields.index(field_sw) if field_sw in fields else None
        if sw_idx is not None:
            ax_a.axhspan(sw_idx - 0.45, sw_idx + 0.45,
                         color=COL_HIGHLIGHT, alpha=0.12, zorder=0)

        # ── Panel B: LOO histogram ─────────────────────────────────────────
        if loo_r:
            ax_b.hist(loo_r, bins=6, color=COL_PERSONNEL, alpha=0.82,
                      edgecolor='white', linewidth=0.8)
            orig_r = -0.8619  # original full-sample Pearson
            ax_b.axvline(orig_r, color=COL_ACCENT, lw=2.2, ls='--',
                         label=orig_label)
            ax_b.set_xlabel(xlabel_b)
            ax_b.set_ylabel(ylabel_b)
            ax_b.set_title(panel_b_title, fontsize=15, fontweight='bold')
            ax_b.legend(fontsize=12, loc='upper left')
            ax_b.grid(alpha=0.3)
        else:
            ax_b.text(0.5, 0.5, 'LOO data\nnot available',
                      ha='center', va='center', transform=ax_b.transAxes)
            ax_b.set_title(panel_b_title, fontsize=15, fontweight='bold')

        fig.suptitle(suptitle, fontsize=17, fontweight='bold', y=1.01)
        fig.tight_layout()
        return fig

    # Save Korean
    fig_kr = make_h10_chart('kr')
    out_kr = os.path.join(FIG_KR, 'h10_v3_robustness.png')
    save_resize(fig_kr, out_kr)
    print(f'  -> {out_kr}')

    # Save English
    fig_en = make_h10_chart('en')
    out_en = os.path.join(FIG_EN, 'h10_v3_robustness.png')
    save_resize(fig_en, out_en)
    print(f'  -> {out_en}')


# ══════════════════════════════════════════════════════════════════════════════
# Chart 2 — h9_v3_time_evo.png  (KR: copy existing PNG, EN: re-render with English labels)
# ══════════════════════════════════════════════════════════════════════════════
print('\n[2/4] h9_v3_time_evo.png')

src_png = os.path.join(FIGS_SRC, 'h9_v3_time_evo', 'H9_v3_topology_wavelet_dual.png')
align_csv = os.path.join(RESULTS, 'H9_v3_topology_wavelet_alignment.csv')

if not os.path.exists(src_png):
    print(f'  SKIP: source PNG not found at {src_png}')
else:
    # Korean copy (source PNG already has Korean labels)
    out_kr = os.path.join(FIG_KR, 'h9_v3_time_evo.png')
    copy_resize(src_png, out_kr)
    print(f'  -> {out_kr}')

    # English re-render from cached alignment CSV
    if not os.path.exists(align_csv):
        print(f'  WARN: alignment CSV not found ({align_csv}); copying KR version as fallback')
        out_en = os.path.join(FIG_EN, 'h9_v3_time_evo.png')
        copy_resize(src_png, out_en)
    else:
        from scipy.stats import pearsonr
        set_font('en')

        df_align = pd.read_csv(align_csv, encoding='utf-8-sig')
        valid = df_align.dropna(subset=['w2_vs_2015_h1', 'chooyeon_wavelet_power'])
        r_corr, p_corr = pearsonr(valid['w2_vs_2015_h1'], valid['chooyeon_wavelet_power'])

        fig, ax1 = plt.subplots(figsize=(12, 6))
        ax2 = ax1.twinx()

        c_tda, c_wav = '#a85454', '#5475a8'
        valid_tda = df_align.dropna(subset=['w2_vs_2015_h1'])
        ax1.plot(valid_tda['year'], valid_tda['w2_vs_2015_h1'],
                 'o-', color=c_tda, lw=2.5, markersize=7,
                 label=r'$W_2$(year, 2015) — H1 topological distance')
        ax1.set_xlabel('Year')
        ax1.set_ylabel('Wasserstein-2 Distance from 2015', color=c_tda)
        ax1.tick_params(axis='y', labelcolor=c_tda)

        ax2.plot(df_align['year'], df_align['chooyeon_wavelet_power'],
                 's--', color=c_wav, lw=2.5, markersize=7, alpha=0.85,
                 label='Grant-Transfer 12m Wavelet Power')
        ax2.set_ylabel('12m Wavelet Power (Grant-Transfer)', color=c_wav)
        ax2.tick_params(axis='y', labelcolor=c_wav)

        ax1.axvspan(2020, 2021.5, alpha=0.12, color='green', label='COVID Period')

        l1, lb1 = ax1.get_legend_handles_labels()
        l2, lb2 = ax2.get_legend_handles_labels()
        ax1.legend(l1 + l2, lb1 + lb2, loc='upper left', fontsize=12)

        ax1.set_title(
            f'Time-Topology Evolution: TDA H1 Distance vs Grant-Transfer Wavelet Power\n'
            f'(Pearson r = {r_corr:.3f}, p = {p_corr:.3f})'
        )
        ax1.set_xticks(list(range(2015, 2026)))
        ax1.grid(alpha=0.3)
        plt.tight_layout()

        out_en = os.path.join(FIG_EN, 'h9_v3_time_evo.png')
        save_resize(fig, out_en)

    print(f'  -> {out_en}')


# ══════════════════════════════════════════════════════════════════════════════
# Chart 3 — v3_calibration.png
# ══════════════════════════════════════════════════════════════════════════════
print('\n[3/4] v3_calibration.png')

calib_path = os.path.join(RESULTS, 'v3_calibration_wt_wq_ratios.csv')
if not os.path.exists(calib_path):
    print(f'  SKIP: {calib_path} not found')
else:
    df_cal = pd.read_csv(calib_path)
    print(f'  Loaded calibration: {len(df_cal)} rows')

    # Select representative rows (one per source×year, prefer high confidence)
    # Keep the key rows only — avoid duplicates for same source
    keep_rows = [
        # (source label, year, ratio, confidence_label)
        ('재정사업자율평가\n(narrow, 2016)',  0.75,  '< 1'),
        ('재정사업자율평가\n(broad, 2016)',   0.60,  '< 1'),
        ('경영평가편람 준정부\n위탁(2019)',    0.642, '< 1'),
        ('경영평가편람 준정부\n위탁(2023)',    1.292, '> 1'),
        ('NST 출연기관\n연구사업 (2024)',     0.429, '< 1'),
        ('NST 출연기관\n기관운영 (2024)',     0.417, '< 1'),
    ]

    keep_rows_en = [
        ('Fiscal Program\nSelf-Eval (narrow)',  0.75,  '< 1'),
        ('Fiscal Program\nSelf-Eval (broad)',   0.60,  '< 1'),
        ('Quasi-Gov Agency\nHandbook (2019)',   0.642, '< 1'),
        ('Quasi-Gov Agency\nHandbook (2023)',   1.292, '> 1'),
        ('NST Research\nInstitutions (2024)',   0.429, '< 1'),
        ('NST Institutional\nOps (2024)',       0.417, '< 1'),
    ]

    def make_calibration_chart(rows, lang: str) -> plt.Figure:
        set_font(lang)

        labels = [r[0] for r in rows]
        ratios = [r[1] for r in rows]
        directions = [r[2] for r in rows]

        bar_colors = [COL_ACCENT if d == '> 1' else COL_PERSONNEL for d in directions]

        if lang == 'kr':
            title   = '공식 평가편람 implied $w_t/w_q$ 비율\n— archetype별 큰 격차'
            ylabel  = '$w_t / w_q$ 비율'
            bal_lbl = 'balanced ($w_t = w_q$)'
            leg_gaming  = '$w_t/w_q > 1$ (집행 우위 / 게임화 위험)'
            leg_quality = '$w_t/w_q < 1$ (성과 우위 / 품질 지향)'
        else:
            title   = 'Implied $w_t/w_q$ Ratios from Official Evaluation Handbooks\n— Large Gap Across Archetypes'
            ylabel  = '$w_t / w_q$ ratio'
            bal_lbl = 'balanced ($w_t = w_q$)'
            leg_gaming  = '$w_t/w_q > 1$ (timing-heavy / gaming-prone)'
            leg_quality = '$w_t/w_q < 1$ (quality-heavy / outcome-oriented)'

        fig, ax = plt.subplots(figsize=(11, 6.5), facecolor='white')
        x = np.arange(len(labels))
        bars = ax.bar(x, ratios, color=bar_colors, alpha=0.85,
                      edgecolor='white', linewidth=0.8, width=0.65)

        # Value labels on bars
        for bar, ratio in zip(bars, ratios):
            y_pos = ratio + 0.02
            ax.text(bar.get_x() + bar.get_width() / 2, y_pos,
                    f'{ratio:.3f}', ha='center', va='bottom',
                    fontsize=13, fontweight='bold')

        # Horizontal balanced line
        ax.axhline(1.0, color='#444', lw=1.8, ls='--', alpha=0.85,
                   label=bal_lbl, zorder=5)

        # Shade > 1 region lightly
        ax.axhspan(1.0, 2.5, color=COL_ACCENT, alpha=0.05, zorder=0)

        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=13)
        ax.set_ylabel(ylabel)
        ax.set_title(title, fontsize=15, fontweight='bold')
        ax.set_ylim(0, 1.55)
        ax.grid(axis='y', alpha=0.35)

        # Legend patches
        p_gaming  = mpatches.Patch(color=COL_ACCENT,    alpha=0.85, label=leg_gaming)
        p_quality = mpatches.Patch(color=COL_PERSONNEL, alpha=0.85, label=leg_quality)
        ax.legend(handles=[p_gaming, p_quality,
                            plt.Line2D([0], [0], color='#444', lw=1.8,
                                       ls='--', label=bal_lbl)],
                  fontsize=11, loc='upper right', framealpha=0.92)

        fig.tight_layout()
        return fig

    # Korean
    fig_kr = make_calibration_chart(keep_rows, 'kr')
    out_kr = os.path.join(FIG_KR, 'v3_calibration.png')
    save_resize(fig_kr, out_kr)
    print(f'  -> {out_kr}')

    # English
    fig_en = make_calibration_chart(keep_rows_en, 'en')
    out_en = os.path.join(FIG_EN, 'v3_calibration.png')
    save_resize(fig_en, out_en)
    print(f'  -> {out_en}')


# ══════════════════════════════════════════════════════════════════════════════
# Chart 4 — v3_alio_grades.png
# ══════════════════════════════════════════════════════════════════════════════
print('\n[4/4] v3_alio_grades.png')

alio_path = os.path.join(EXT, 'v3_micro_eval_alio.csv')
if not os.path.exists(alio_path):
    print(f'  SKIP: {alio_path} not found')
else:
    df_alio = pd.read_csv(alio_path, encoding='utf-8-sig')
    print(f'  Loaded ALIO: {len(df_alio)} rows, years={sorted(df_alio["year"].unique())}')

    GRADE_ORDER = ['S', 'A', 'B', 'C', 'D', 'E']

    # Grade Korean name map
    GRADE_KOR = {'S': 'S 탁월',  'A': 'A 우수',  'B': 'B 양호',
                 'C': 'C 보통', 'D': 'D 미흡',  'E': 'E 아주미흡'}
    GRADE_EN  = {'S': 'S Excellent', 'A': 'A Good', 'B': 'B Satisfactory',
                 'C': 'C Average',   'D': 'D Poor',  'E': 'E Very Poor'}

    # Grade colors (traffic-light palette)
    GRADE_COLORS = {
        'S': '#2a7d4f',
        'A': '#4caf50',
        'B': '#8bc34a',
        'C': '#ffc107',
        'D': '#ff7043',
        'E': '#c62828',
    }

    def make_alio_chart(lang: str) -> plt.Figure:
        set_font(lang)

        years = sorted(df_alio['year'].unique())

        if lang == 'kr':
            title_a     = '(A) 2024년 등급 분포'
            title_b     = '(B) 연도별 등급 분포 (2022–2024)'
            xlabel_a    = '등급'
            ylabel_a    = '기관 수'
            ylabel_b    = '기관 수'
            suptitle    = 'ALIO 공공기관 경영평가 결과 분포 (2022–2024)'
            grade_labels= GRADE_KOR
            year_lbl    = lambda y: f'{y}년'
        else:
            title_a     = '(A) Grade Distribution 2024'
            title_b     = '(B) Year-by-Year Grade Distribution (2022–2024)'
            xlabel_a    = 'Grade'
            ylabel_a    = 'Number of institutions'
            ylabel_b    = 'Number of institutions'
            suptitle    = 'ALIO Public Institution Management Evaluation Results (2022–2024)'
            grade_labels= GRADE_EN
            year_lbl    = lambda y: str(y)

        fig, (ax_a, ax_b) = plt.subplots(
            1, 2, figsize=(12, 4.5), facecolor='white',
            gridspec_kw={'width_ratios': [1, 1.4]}
        )

        # ── Panel A: 2024 bar chart ────────────────────────────────────────
        df_2024 = df_alio[df_alio['year'] == 2024]
        counts_2024 = {g: 0 for g in GRADE_ORDER}
        for _, row in df_2024.iterrows():
            g = row['grade']
            if g in counts_2024:
                counts_2024[g] += 1

        present_grades = [g for g in GRADE_ORDER if counts_2024[g] > 0]
        ax_a.bar(
            [grade_labels[g] for g in present_grades],
            [counts_2024[g] for g in present_grades],
            color=[GRADE_COLORS[g] for g in present_grades],
            alpha=0.88, edgecolor='white', linewidth=0.8
        )
        for i, g in enumerate(present_grades):
            cnt = counts_2024[g]
            if cnt > 0:
                ax_a.text(i, cnt + 0.15, str(cnt),
                          ha='center', va='bottom', fontsize=13, fontweight='bold')

        ax_a.set_xlabel(xlabel_a)
        ax_a.set_ylabel(ylabel_a)
        ax_a.set_title(title_a, fontsize=15, fontweight='bold')
        ax_a.grid(axis='y', alpha=0.35)
        ax_a.set_ylim(0, max(counts_2024.values()) * 1.2 + 1)
        plt.setp(ax_a.get_xticklabels(), rotation=15, ha='right', fontsize=12)

        # ── Panel B: grouped bar chart by year ─────────────────────────────
        year_grade_counts = {}
        for yr in years:
            sub = df_alio[df_alio['year'] == yr]
            gc = {g: 0 for g in GRADE_ORDER}
            for _, row in sub.iterrows():
                g = row['grade']
                if g in gc:
                    gc[g] += 1
            year_grade_counts[yr] = gc

        # Only grades that appear in any year
        active_grades = [g for g in GRADE_ORDER
                         if any(year_grade_counts[yr].get(g, 0) > 0 for yr in years)]

        n_grades = len(active_grades)
        n_years  = len(years)
        x = np.arange(n_grades)
        bar_w = 0.72 / n_years

        for i, yr in enumerate(years):
            offsets = (i - (n_years - 1) / 2) * bar_w
            vals = [year_grade_counts[yr].get(g, 0) for g in active_grades]
            ax_b.bar(
                x + offsets, vals, bar_w * 0.92,
                label=year_lbl(yr),
                color=plt.cm.Blues(0.4 + 0.3 * i),
                alpha=0.88, edgecolor='white', linewidth=0.6
            )

        ax_b.set_xticks(x)
        ax_b.set_xticklabels(
            [grade_labels[g] for g in active_grades],
            fontsize=12, rotation=15, ha='right'
        )
        ax_b.set_ylabel(ylabel_b)
        ax_b.set_title(title_b, fontsize=15, fontweight='bold')
        ax_b.legend(fontsize=12, loc='upper right')
        ax_b.grid(axis='y', alpha=0.35)
        ax_b.set_ylim(0, max(
            year_grade_counts[yr].get(g, 0)
            for yr in years for g in active_grades
        ) * 1.25 + 1)

        fig.suptitle(suptitle, fontsize=16, fontweight='bold', y=1.02)
        fig.tight_layout()
        return fig

    # Korean
    fig_kr = make_alio_chart('kr')
    out_kr = os.path.join(FIG_KR, 'v3_alio_grades.png')
    save_resize(fig_kr, out_kr)
    print(f'  -> {out_kr}')

    # English
    fig_en = make_alio_chart('en')
    out_en = os.path.join(FIG_EN, 'v3_alio_grades.png')
    save_resize(fig_en, out_en)
    print(f'  -> {out_en}')


# ── Final summary ──────────────────────────────────────────────────────────────
print('\n' + '=' * 60)
print('generate_v3_charts.py DONE')
print('=' * 60)
saved = []
for name in ['h10_v3_robustness.png', 'h9_v3_time_evo.png',
             'v3_calibration.png', 'v3_alio_grades.png']:
    for folder in [FIG_KR, FIG_EN]:
        p = os.path.join(folder, name)
        if os.path.exists(p):
            kb = os.path.getsize(p) // 1024
            saved.append(f'  {p}  ({kb} KB)')
        else:
            saved.append(f'  MISSING: {p}')
for s in saved:
    print(s)
