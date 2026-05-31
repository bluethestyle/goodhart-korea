"""FIG-2.2: 사업 규모 분위별 월 평균 집행 비중 (2015 — 2025).

raw 월합계 차트는 큰 사업이 작은 사업을 가린다 → 사업별 100% 정규화.
정규화 후 단순 평균만 보면 사업 규모 차이를 무시 → 규모 분위별로 본다.

발견:
- 12월 쏠림이 사업 규모에 따라 *체계적으로 다름*
  - Q1 (작은 사업): 11월 6.0% → 12월 15.4% (2.58배)
  - Q4 (큰 사업):   11월 5.9% → 12월 10.9% (1.86배)
- 작은 사업이 회계연도 마감 시점 압력에 더 취약
"""
import os, sys, io, duckdb
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
  SELECT FSCL_YY, ACTV_CD, sum(EP_AMT) AS yearly_total
  FROM monthly_exec
  WHERE FSCL_YY BETWEEN 2015 AND 2025
  GROUP BY FSCL_YY, ACTV_CD
  HAVING sum(EP_AMT) > 0
),
sized AS (
  SELECT FSCL_YY, ACTV_CD, yearly_total,
         ntile(4) OVER (PARTITION BY FSCL_YY ORDER BY yearly_total) AS size_q
  FROM activity_yearly
),
monthly AS (
  SELECT m.FSCL_YY, m.ACTV_CD, m.EXE_M, s.size_q,
         sum(m.EP_AMT) * 1.0 / max(s.yearly_total) AS share
  FROM monthly_exec m
  JOIN sized s USING (FSCL_YY, ACTV_CD)
  WHERE m.FSCL_YY BETWEEN 2015 AND 2025
  GROUP BY m.FSCL_YY, m.ACTV_CD, m.EXE_M, s.size_q
)
SELECT EXE_M, size_q, avg(share)*100 AS pct_mean
FROM monthly
GROUP BY EXE_M, size_q
ORDER BY size_q, EXE_M
""").fetchdf()

# pivot to (12, 4)
pv = df.pivot(index='EXE_M', columns='size_q', values='pct_mean')
months = pv.index.values

# 색: 작은 사업 → 진한 빨강, 큰 사업 → 회색 (쏠림 강도 그라데이션)
colors = {
    1: '#b91c1c',  # Q1 작음 - 진한 빨강 (강조)
    2: '#dc7676',  # Q2
    3: '#9ca3af',  # Q3
    4: '#525252',  # Q4 큼 - 진한 회색
}
labels = {
    1: 'Q1 (연 예산 하위 25%)',
    2: 'Q2',
    3: 'Q3',
    4: 'Q4 (연 예산 상위 25%)',
}

# A4 콘텐츠 폭 ≈ 158mm. figsize 7.4 × 3.6 dpi 170 ≈ 1258×612
fig, ax = plt.subplots(figsize=(7.4, 3.6), dpi=170)

mid = '#525252'

for q in [4, 3, 2, 1]:  # Q1을 가장 위 (z-order)
    lw = 2.4 if q in (1, 4) else 1.6
    alpha = 1.0 if q in (1, 4) else 0.85
    ax.plot(months, pv[q].values, marker='o', markersize=6,
            color=colors[q], linewidth=lw, alpha=alpha, label=labels[q])

# 균등 가이드라인 (텍스트 라벨은 line과 겹쳐서 차트 외부 y축 옆으로)
ax.axhline(100/12, color=mid, linestyle='--', linewidth=0.7, alpha=0.55)
ax.text(0.55, 100/12, '8.3%',
        fontsize=8.5, color=mid, ha='right', va='center',
        bbox=dict(facecolor='white', edgecolor='none', pad=2, boxstyle='square,pad=0.2'))

# 12월 강조 — value annotation
for q in [1, 4]:
    v = pv.loc[12, q]
    ax.annotate(f'{v:.1f}%', xy=(12, v), xytext=(11.4, v + 1.1),
                fontsize=10, color=colors[q], weight='semibold')

# X축
ax.set_xticks(range(1, 13))
ax.set_xticklabels([f'{m}월' for m in range(1, 13)], fontsize=10)
ax.set_xlim(0.5, 12.5)

# Y축
ax.set_ylabel('사업별 월 평균 집행 비중 (%)', fontsize=11)
ax.tick_params(axis='y', labelsize=10)
ax.set_ylim(0, 17.5)

# 스타일
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color(mid)
ax.spines['bottom'].set_color(mid)
ax.tick_params(colors=mid, length=3)
ax.grid(axis='y', alpha=0.2, linewidth=0.5)
ax.set_axisbelow(True)

# 범례
ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=4,
          frameon=False, fontsize=9.5, columnspacing=1.3)

plt.tight_layout()
out_path = os.path.join(OUT_DIR, 'fig_2_2_monthly_exec_total.png')
plt.savefig(out_path, dpi=170, bbox_inches='tight', facecolor='white')
plt.close()

from PIL import Image
im = Image.open(out_path)
print(f'Saved: {out_path}')
print(f'Size: {im.size}')

con.close()
