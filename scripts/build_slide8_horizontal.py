"""Slide 8 가로(landscape) — 51개 부처 ranking, 12월 비중 임계값 색.

EDA 단계 — 부처 단위 12월 비중 분포 시각화.
community detection 등 본격 군집 분석은 제외 (Slide 14 archetype에서 본 분석).
"""
import duckdb
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
from pathlib import Path
import sys
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')

font_path = Path('paper/fonts/Pretendard-Regular.otf')
if font_path.exists():
    fm.fontManager.addfont(str(font_path))
    plt.rcParams['font.family'] = 'Pretendard'
plt.rcParams['axes.unicode_minus'] = False

# ── 부처 dec_pct ─────────────────────────────────────────────────
con = duckdb.connect('data/warehouse.duckdb', read_only=True)
q = """
WITH ay AS (
  SELECT FSCL_YY, OFFC_NM, SUM(EP_AMT) AS annual,
         SUM(CASE WHEN EXE_M=12 THEN EP_AMT ELSE 0 END) AS dec_exec
  FROM monthly_exec WHERE FSCL_YY BETWEEN 2015 AND 2025 AND EP_AMT > 0
  GROUP BY 1, 2
)
SELECT OFFC_NM, AVG(CASE WHEN annual>0 THEN dec_exec*1.0/annual END)*100 AS dec_pct
FROM ay GROUP BY OFFC_NM ORDER BY dec_pct DESC
"""
df_off = con.execute(q).fetchdf()
df_off = df_off[df_off['dec_pct'].notna()].reset_index(drop=True)
df_off = df_off.iloc[:51].reset_index(drop=True)
con.close()
n_total = len(df_off)
print(f'부처 수: {n_total}')

# ── 임계값 색 ─────────────────────────────────────────────────────
def color_for(v):
    if v > 15: return '#C0392B'  # 빨강 — 15% 초과
    if v > 10: return '#E67E22'  # 주황 — 10~15%
    return '#888'                 # 회색 — 10% 이하

n_cols = 3
chunks = np.array_split(df_off, n_cols)
x_max = float(df_off['dec_pct'].max()) * 1.08

fig, axes = plt.subplots(1, n_cols, figsize=(12.8, 6.0), dpi=100, sharex=True)

for i, (ax, chunk) in enumerate(zip(axes, chunks)):
    chunk = chunk.reset_index(drop=True)
    y = list(range(len(chunk)))
    colors = [color_for(v) for v in chunk['dec_pct'].values]
    ax.barh(y, chunk['dec_pct'].values, color=colors,
            edgecolor='#444', linewidth=0.3)
    ax.axvline(8.33, color='#444', linestyle='--', linewidth=0.8, alpha=0.7)
    ax.set_yticks(y)
    ax.set_yticklabels(chunk['OFFC_NM'].tolist(), fontsize=8)
    ax.invert_yaxis()
    ax.set_xlim(0, x_max)
    ax.set_xlabel('연 평균 12월 집행 비중 (%)', fontsize=9.5)
    for s in ['top', 'right']:
        ax.spines[s].set_visible(False)
    ax.grid(True, axis='x', alpha=0.25, linestyle=':')
    if i == 0:
        ax.text(8.5, -0.6, '균등 가정 8.3%', fontsize=8.5, color='#444')

n_above_8 = (df_off['dec_pct'] > 8.33).sum()
n_above_15 = (df_off['dec_pct'] > 15).sum()
n_above_10 = ((df_off['dec_pct'] > 10) & (df_off['dec_pct'] <= 15)).sum()
n_below_10 = (df_off['dec_pct'] <= 10).sum()

fig.suptitle(
    f'Slide 8. 부처 {n_total}개 — 모든 부처에서 12월 봉우리\n'
    f'빨강 > 15% ({n_above_15}개) · 주황 10~15% ({n_above_10}개) · 회색 ≤ 10% ({n_below_10}개)',
    fontsize=12, y=0.97)

fig.text(0.99, 0.01,
         f'※ {n_above_8}/{n_total} 부처가 균등 가정(8.3%) 초과 = '
         f'{n_above_8/n_total*100:.0f}%  —  부처 단위 EDA',
         ha='right', fontsize=9, color='#555', style='italic')

plt.tight_layout(rect=[0, 0.04, 1, 0.91])
out_h = Path('paper/figures/eda/fig_slide8_ministry_dec_ranking_h.png')
plt.savefig(out_h, dpi=100, bbox_inches='tight', facecolor='white')
plt.close()

w, h = Image.open(out_h).size
print(f'[Slide 8] {out_h} | {w}x{h}px | {n_above_8}/{n_total} 균등 초과')
print(f'  >15%: {n_above_15} / 10~15%: {n_above_10} / ≤10%: {n_below_10}')
