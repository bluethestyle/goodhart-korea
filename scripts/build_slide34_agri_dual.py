"""Slide 34 — 농가소득의 역설 dual 시계열.

12월 집중 비중 (위) + 농가소득 (아래) 11년 시계열.
2023 12월 비중 peak (11.8%) → 2024 농가소득 −3.0% 감소 annotation.

데이터:
  - 12월 비중: monthly_exec (농림수산 분야 12월/연간 합)
  - 농가소득: indicator_panel (metric_code='farm_income', KOSIS DT_1EA1501)

출력: paper/figures/eda/fig_slide34_agri_dual.png  (1280×620)
"""
import sys
import io
import numpy as np
import pandas as pd
import duckdb
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(__file__).resolve().parent.parent
font_path = ROOT / 'paper' / 'fonts' / 'Pretendard-Regular.otf'
if font_path.exists():
    fm.fontManager.addfont(str(font_path))
    plt.rcParams['font.family'] = 'Pretendard'
plt.rcParams['axes.unicode_minus'] = False

DB_PATH  = ROOT / 'data' / 'warehouse.duckdb'
OUT_PATH = ROOT / 'paper' / 'figures' / 'eda' / 'fig_slide34_agri_dual.png'

C2_COLOR    = '#E67E22'  # 출연금형 주황 (참고용, 농림수산 매개)
PRIMARY     = '#C0392B'  # 12월 비중 빨강
SECONDARY   = '#2c3e50'  # 농가소득 검정/네이비

# ── 1) 12월 비중 (농림수산 분야) ─────────────────────────────────────
con = duckdb.connect(str(DB_PATH), read_only=True)

dec_df = con.execute("""
    SELECT FSCL_YY AS year,
           SUM(CASE WHEN EXE_M = 12 THEN EP_AMT ELSE 0 END) AS dec_sum,
           SUM(EP_AMT) AS annual_sum
    FROM monthly_exec
    WHERE FLD_NM = '농림수산'
      AND FSCL_YY BETWEEN 2015 AND 2025
    GROUP BY FSCL_YY
    ORDER BY FSCL_YY
""").fetchdf()
dec_df['dec_pct'] = dec_df['dec_sum'] / dec_df['annual_sum'] * 100

# ── 2) 농가소득 (indicator_panel, farm_income) ───────────────────────
farm_df = con.execute("""
    SELECT year, value AS farm_income
    FROM indicator_panel
    WHERE metric_code = 'farm_income'
      AND year BETWEEN 2015 AND 2025
    ORDER BY year
""").fetchdf()
# 천원 → 만원 (단위 1만원으로 변환)
farm_df['farm_income_10k'] = farm_df['farm_income'] / 10
farm_df['yoy_pct'] = farm_df['farm_income'].pct_change() * 100

con.close()

print('12월 비중:')
print(dec_df[['year', 'dec_pct']].to_string(index=False))
print('\n농가소득:')
print(farm_df[['year', 'farm_income_10k', 'yoy_pct']].to_string(index=False))

# ── 3) 차트 ──────────────────────────────────────────────────────────
fig, axes = plt.subplots(2, 1, figsize=(12.8, 6.8), dpi=100, sharex=True,
                         gridspec_kw={'hspace': 0.40, 'left': 0.08,
                                      'right': 0.94, 'top': 0.88, 'bottom': 0.14,
                                      'height_ratios': [1, 1]})

# ─── 상단: 12월 비중 ──────────────────────────────────────────────
ax1 = axes[0]
ax1.plot(dec_df['year'], dec_df['dec_pct'], color=PRIMARY, lw=2.4,
         marker='o', markersize=8, markeredgecolor='white',
         markeredgewidth=1.5, zorder=3, label='농림수산 12월 비중')

# 균등 가정 8.3% — 우측에 라벨 (좌측 데이터 라벨과 겹침 회피)
ax1.axhline(8.3, color='#888', lw=1.0, linestyle='--', alpha=0.7, zorder=1)
ax1.text(2025.4, 8.3, '균등 가정\n8.3%', fontsize=10, color='#666',
         va='center', ha='left')

# 2023 peak 강조
peak_year = 2023
peak_val = dec_df.loc[dec_df['year'] == peak_year, 'dec_pct'].iloc[0]
ax1.scatter([peak_year], [peak_val], s=180, color=PRIMARY,
            edgecolor='white', linewidth=2.5, zorder=5)
ax1.annotate(f'2023 peak\n{peak_val:.1f}%', xy=(peak_year, peak_val),
             xytext=(2024.3, peak_val + 0.5),
             fontsize=11, color=PRIMARY, fontweight='bold',
             arrowprops=dict(arrowstyle='->', color=PRIMARY, lw=1.5))

# 값 라벨 (위 panel)
for _, row in dec_df.iterrows():
    ax1.text(row['year'], row['dec_pct'] + 0.3, f'{row["dec_pct"]:.1f}%',
             ha='center', fontsize=9.5, color='#444')

ax1.set_ylabel('12월 비중 (%)', fontsize=12)
ax1.set_ylim(6.5, 14.5)
ax1.set_xlim(2014.5, 2025.5)
ax1.grid(True, alpha=0.25, linestyle=':')
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.set_title('① 농림수산 12월 집행 비중 — 2023 peak (11.8%)',
              loc='left', fontsize=13, fontweight='bold', color=PRIMARY, pad=14)

# ─── 하단: 농가소득 ──────────────────────────────────────────────
ax2 = axes[1]
ax2.plot(farm_df['year'], farm_df['farm_income_10k'], color=SECONDARY, lw=2.4,
         marker='o', markersize=8, markeredgecolor='white',
         markeredgewidth=1.5, zorder=3, label='농가소득 (만원)')

# 2024 감소 강조
y_2023 = farm_df.loc[farm_df['year'] == 2023, 'farm_income_10k'].iloc[0]
y_2024 = farm_df.loc[farm_df['year'] == 2024, 'farm_income_10k'].iloc[0]
pct_2024 = farm_df.loc[farm_df['year'] == 2024, 'yoy_pct'].iloc[0]

ax2.scatter([2023, 2024], [y_2023, y_2024], s=180, color='#C0392B',
            edgecolor='white', linewidth=2.5, zorder=5)
ax2.annotate(f'2024 농가소득\n{pct_2024:+.1f}% 감소',
             xy=(2024, y_2024),
             xytext=(2024.3, y_2024 - 350),
             fontsize=11, color='#C0392B', fontweight='bold',
             arrowprops=dict(arrowstyle='->', color='#C0392B', lw=1.5))

# 값 라벨 (만원 단위)
for _, row in farm_df.iterrows():
    if not np.isnan(row['farm_income_10k']):
        ax2.text(row['year'], row['farm_income_10k'] + 80,
                 f'{row["farm_income_10k"]:,.0f}',
                 ha='center', fontsize=9.5, color='#444')

ax2.set_ylabel('농가소득 (만원)', fontsize=12)
ax2.set_ylim(3800, 6000)
ax2.set_xlim(2014.5, 2025.5)
ax2.set_xticks(range(2015, 2026))
ax2.grid(True, alpha=0.25, linestyle=':')
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.set_title('② 농가소득 (KOSIS DT_1EA1501) — 2024 −3.0% 감소',
              loc='left', fontsize=13, fontweight='bold', color=SECONDARY, pad=8)

# 2023 → 2024 연결 화살표 (panel 간)
fig.suptitle('농가소득의 역설 — 12월 집중 peak(2023) 다음 해 농가소득 감소(2024)',
             fontsize=15, fontweight='bold', y=0.965)

# footer narrative — bottom margin 충분히 확보
fig.text(0.5, 0.035,
         "raw 시계열 같은 해 양 상관 · 시점 압력 archetype 통제 후 매개 효과 음 (Slide 33 Sobel z = −2.897)",
         ha='center', fontsize=10.5, color='#555', style='italic')

OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(OUT_PATH, dpi=100, facecolor='white')
plt.close()

from PIL import Image
print(f'\nSaved: {OUT_PATH}')
print(f'Size:  {Image.open(OUT_PATH).size}')
