"""FIG-2.3: 분야별 12월 쏠림 + 사업 규모 (2015 — 2025).

§ 2.2 발견 "작은 사업일수록 쏠림 강함"이 분야 단위로도 보이는지 확인.
가로 막대: 분야별 12월 비중 중앙값 (정렬).
막대 색: 분야 평균 사업 규모 (작은 사업 → 진한 빨강, 큰 사업 → 회색).
"""
import os, sys, io, duckdb
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
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

df = con.execute("""
WITH activity_yearly AS (
  SELECT FSCL_YY, ACTV_CD, FLD_NM, sum(EP_AMT) AS yearly_total
  FROM monthly_exec
  WHERE FSCL_YY BETWEEN 2015 AND 2025 AND FLD_NM IS NOT NULL
  GROUP BY FSCL_YY, ACTV_CD, FLD_NM
  HAVING sum(EP_AMT) > 100000000
),
monthly_dec AS (
  SELECT m.FSCL_YY, m.ACTV_CD, a.FLD_NM, a.yearly_total,
         LEAST(sum(m.EP_AMT) * 1.0 / max(a.yearly_total), 1.0) AS dec_share
  FROM monthly_exec m
  JOIN activity_yearly a USING (FSCL_YY, ACTV_CD)
  WHERE m.EXE_M = 12
  GROUP BY m.FSCL_YY, m.ACTV_CD, a.FLD_NM, a.yearly_total
)
SELECT FLD_NM,
       median(dec_share)*100 AS pct_median,
       median(yearly_total)/1e8 AS median_size_eok,
       count(*) AS n
FROM monthly_dec
GROUP BY FLD_NM
HAVING count(*) >= 100
ORDER BY pct_median ASC
""").fetchdf()

# 색: 사업 규모 → 빨강 (작음) → 회색 (큼) 그라데이션
ink = '#0a0a0a'; mid = '#525252'; soft = '#a3a3a3'
neg = '#b91c1c'
log_sizes = np.log10(df['median_size_eok'])
sz_norm = (log_sizes - log_sizes.min()) / (log_sizes.max() - log_sizes.min())
cmap = mcolors.LinearSegmentedColormap.from_list('size_grad', [neg, '#dc7676', '#9ca3af', mid])
colors = [cmap(s) for s in sz_norm]

fig, ax = plt.subplots(figsize=(7.4, 4.4), dpi=170)

y = np.arange(len(df))
bars = ax.barh(y, df['pct_median'], color=colors, height=0.72, edgecolor='none')

# 막대 끝 값 + 사업 규모
for i, row in df.iterrows():
    yi = list(df.index).index(i)
    pct = row['pct_median']
    size_eok = row['median_size_eok']
    size_label = f'{size_eok:.0f}억' if size_eok < 100 else f'{size_eok/100:.1f}백억' if size_eok < 1000 else f'{size_eok/1000:.1f}천억'
    ax.text(pct + 1.5, yi, f' {pct:.1f}%   ·   사업 규모 {size_label}',
            va='center', ha='left', fontsize=9, color=mid)

# y축 라벨
ax.set_yticks(y)
ax.set_yticklabels(df['FLD_NM'], fontsize=10)

# 균등 가정
ax.axvline(100/12, color=mid, linestyle='--', linewidth=0.7, alpha=0.5)
ax.text(100/12, len(df)-0.3, '균등 가정 8.3%', fontsize=8.5, color=mid, ha='center')

ax.set_xlim(0, 130)
ax.set_xlabel('분야 12월 집행 비중 중앙값 (%)', fontsize=11)
ax.tick_params(axis='x', labelsize=10)

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['bottom'].set_color(mid)
ax.tick_params(colors=mid, length=3, left=False)
ax.grid(axis='x', alpha=0.2, linewidth=0.5)
ax.set_axisbelow(True)

# 컬러바 설명 (수동 패치)
from matplotlib.patches import Patch
legend = [
    Patch(facecolor=neg,       label='작은 사업 분야'),
    Patch(facecolor='#9ca3af', label='중간'),
    Patch(facecolor=mid,       label='큰 사업 분야'),
]
ax.legend(handles=legend, loc='lower right', fontsize=9, frameon=False,
          title='막대 색 (분야 평균 사업 규모)', title_fontsize=9)

plt.tight_layout()
out_path = os.path.join(OUT_DIR, 'fig_2_3_field_size_vs_dec.png')
plt.savefig(out_path, dpi=170, bbox_inches='tight', facecolor='white')
plt.close()

from PIL import Image
im = Image.open(out_path)
print(f'Saved: {out_path}')
print(f'Size: {im.size}')

con.close()
