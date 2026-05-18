"""FIG-2.5: 집행률 분포 (좌) vs 결과지표 변화율 분포 (우).

§ 2.4 핵심 — 같은 부처들의 두 변수 분포가 체계적으로 다르다.
좌: 사업별 집행률 (95-100% 천장 압축).
우: 분야별 결과지표 YoY 변화율 (광범위한 분산).
"""
import os, sys, io, duckdb
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

for f in ['Pretendard-Regular.otf', 'Pretendard-SemiBold.otf', 'Pretendard-Bold.otf']:
    p = os.path.join(ROOT, 'paper', 'fonts', f)
    if os.path.exists(p):
        font_manager.fontManager.addfont(p)
plt.rcParams['font.family'] = 'Pretendard'
plt.rcParams['axes.unicode_minus'] = False

OUT_DIR = os.path.join(ROOT, 'paper', 'figures', 'eda')
os.makedirs(OUT_DIR, exist_ok=True)

con = duckdb.connect(os.path.join(ROOT, 'data', 'warehouse.duckdb'), read_only=True)

# 집행률 분포
exec_rate = con.execute("""
WITH actv AS (
  SELECT FSCL_YY, ACTV_CD,
         max(ANEXP_BDG_CAMT) AS budget,
         sum(EP_AMT) AS exec_total
  FROM monthly_exec
  WHERE FSCL_YY BETWEEN 2015 AND 2025 AND ANEXP_BDG_CAMT > 100000000
  GROUP BY FSCL_YY, ACTV_CD
)
SELECT exec_total*100.0/budget AS exec_rate
FROM actv
WHERE exec_total > 0 AND exec_total <= budget * 1.5
""").fetchdf()

# 결과지표 YoY 변화율
outcome_yoy = con.execute("""
WITH ranked AS (
  SELECT fld_nm, year, metric_code, value,
         lag(value) OVER (PARTITION BY fld_nm, metric_code ORDER BY year) AS prev
  FROM indicator_panel
  WHERE value IS NOT NULL
)
SELECT (value-prev)*100.0/prev AS yoy
FROM ranked
WHERE prev > 0 AND abs((value-prev)/prev) < 2
""").fetchdf()

ink = '#0a0a0a'; mid = '#525252'; soft = '#a3a3a3'
accent = '#2563eb'; neg = '#b91c1c'

# A4 폭 7.4 x height 3.4
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.4, 3.4), dpi=170)

# === 좌측: 집행률 히스토그램 ===
bins1 = np.linspace(50, 110, 30)
ax1.hist(exec_rate['exec_rate'], bins=bins1, color=accent, alpha=0.7, edgecolor='white', linewidth=0.5)
# 95-100% 구간 강조 (회색 음영)
ax1.axvspan(95, 100, alpha=0.18, color=neg, label='95–100% 구간')
median_e = exec_rate['exec_rate'].median()
ax1.axvline(median_e, color=ink, linestyle='-', linewidth=1.2)
ax1.text(median_e+0.5, ax1.get_ylim()[1]*0.9, f'중앙값 {median_e:.1f}%',
         fontsize=9, color=ink, weight='medium')

ax1.set_xlabel('집행률 = 집행액 / 예산 (%)', fontsize=10.5)
ax1.set_ylabel('사업-연도 수', fontsize=10.5)
ax1.set_title('사업별 집행률 분포', fontsize=11, color=ink, loc='left', pad=10, weight='semibold')
ax1.set_xlim(50, 110)
ax1.tick_params(labelsize=9.5)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.spines['left'].set_color(mid)
ax1.spines['bottom'].set_color(mid)
ax1.tick_params(colors=mid, length=3)
ax1.grid(axis='y', alpha=0.18, linewidth=0.4)
ax1.set_axisbelow(True)
ax1.legend(frameon=False, fontsize=9, loc='upper left')

# === 우측: 결과지표 YoY 히스토그램 ===
bins2 = np.linspace(-80, 80, 30)
ax2.hist(outcome_yoy['yoy'], bins=bins2, color=neg, alpha=0.7, edgecolor='white', linewidth=0.5)
ax2.axvline(0, color=ink, linestyle='-', linewidth=1.2, alpha=0.5)
median_o = outcome_yoy['yoy'].median()
ax2.axvline(median_o, color=ink, linestyle='-', linewidth=1.2)
ax2.text(median_o+2, ax2.get_ylim()[1]*0.9, f'중앙값 {median_o:.1f}%',
         fontsize=9, color=ink, weight='medium')

ax2.set_xlabel('결과지표 연간 변화율 (%)', fontsize=10.5)
ax2.set_ylabel('분야-지표-연도 수', fontsize=10.5)
ax2.set_title('결과지표 변화율 분포', fontsize=11, color=ink, loc='left', pad=10, weight='semibold')
ax2.set_xlim(-80, 80)
ax2.tick_params(labelsize=9.5)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.spines['left'].set_color(mid)
ax2.spines['bottom'].set_color(mid)
ax2.tick_params(colors=mid, length=3)
ax2.grid(axis='y', alpha=0.18, linewidth=0.4)
ax2.set_axisbelow(True)

plt.tight_layout()
out_path = os.path.join(OUT_DIR, 'fig_2_5_exec_vs_outcome.png')
plt.savefig(out_path, dpi=170, bbox_inches='tight', facecolor='white')
plt.close()

from PIL import Image
im = Image.open(out_path)
print(f'Saved: {out_path}')
print(f'Size: {im.size}')

# 핵심 통계
print(f'집행률 std: {exec_rate["exec_rate"].std():.1f}%p')
print(f'결과지표 std: {outcome_yoy["yoy"].std():.1f}%p')
print(f'결과지표/집행률 std 비: {outcome_yoy["yoy"].std()/exec_rate["exec_rate"].std():.1f}배')

con.close()
