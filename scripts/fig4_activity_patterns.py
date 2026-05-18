"""FIG-2.4: 두 종류의 사업 — 월별 패턴 비교 (대표 4건, 2023년).

§ 2.3 핵심 시각화 — 일반 운영형 vs 일률 정산형이 raw 월별 시계열에서 분명히 다른 모양.
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

# 11년치 평균 패턴이 더 안정적 — 같은 활동명에 대해 11년 월별 평균
activities = [
    ('일반 운영형',   '국민연금급여지급',  '#525252'),
    ('일반 운영형',   '재외공관 인건비',   '#9ca3af'),
    ('일률 정산형',   '농가소득보전(직불기금)', '#b91c1c'),
    ('일률 정산형',   '지역경제지원',      '#dc7676'),
]

# 데이터 가져오기 (11년 평균 월별 패턴, 각 활동 100% 정규화)
fig, axes = plt.subplots(2, 2, figsize=(7.4, 4.8), dpi=170, sharex=True)
axes = axes.flatten()

ink = '#0a0a0a'; mid = '#525252'

for i, (kind, name, color) in enumerate(activities):
    df = con.execute(f"""
    WITH yearly AS (
      SELECT FSCL_YY, sum(EP_AMT) AS yearly_total
      FROM monthly_exec
      WHERE ACTV_NM = '{name}' AND FSCL_YY BETWEEN 2015 AND 2025
      GROUP BY FSCL_YY
      HAVING sum(EP_AMT) > 0
    ),
    monthly AS (
      SELECT m.FSCL_YY, m.EXE_M,
             sum(m.EP_AMT) * 1.0 / max(y.yearly_total) AS share
      FROM monthly_exec m
      JOIN yearly y USING (FSCL_YY)
      WHERE m.ACTV_NM = '{name}'
      GROUP BY m.FSCL_YY, m.EXE_M
    )
    SELECT EXE_M, avg(share)*100 AS pct_mean
    FROM monthly
    GROUP BY EXE_M
    ORDER BY EXE_M
    """).fetchdf()

    ax = axes[i]
    # 12월 위치 점색 강조
    bar_colors = [color if m != 12 else '#7f1d1d' if 'HIGH' in kind or '일률' in kind else color
                  for m in df['EXE_M']]
    ax.bar(df['EXE_M'], df['pct_mean'], color=color, width=0.78, edgecolor='none')

    # 균등 가이드
    ax.axhline(100/12, color=mid, linestyle='--', linewidth=0.5, alpha=0.45)

    # 제목 — 유형 + 활동명
    ax.set_title(f'{kind} · {name}', fontsize=10.5, color=ink, loc='left',
                 weight='medium', pad=8)

    # X축
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels([str(m) for m in range(1, 13)], fontsize=8.5)
    ax.set_xlim(0.4, 12.6)

    # Y축
    ax.tick_params(axis='y', labelsize=8.5)
    ax.set_ylim(0, max(df['pct_mean']) * 1.18 + 5)
    if i % 2 == 0:
        ax.set_ylabel('월별 비중 (%)', fontsize=9.5)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(mid)
    ax.spines['bottom'].set_color(mid)
    ax.tick_params(colors=mid, length=2)
    ax.grid(axis='y', alpha=0.18, linewidth=0.4)
    ax.set_axisbelow(True)

plt.tight_layout()
out_path = os.path.join(OUT_DIR, 'fig_2_4_activity_patterns.png')
plt.savefig(out_path, dpi=170, bbox_inches='tight', facecolor='white')
plt.close()

from PIL import Image
im = Image.open(out_path)
print(f'Saved: {out_path}')
print(f'Size: {im.size}')

con.close()
