"""Slide 32 우측 — 분야 평균 집행률 × outcome r 산점도.

메시지: "집행률은 모두 천장에 가까운데, outcome 응답은 분야마다 31배 분산"

데이터:
  - 분야 평균 집행률: data/warehouse.duckdb monthly_exec (활동×연도 단위 집행률 평균)
  - 분야 outcome r: data/results/H10_v3_alt_correlations.csv (pearson_r 절댓값 평균)

출력: paper/figures/eda/fig_slide32_quadrant.png (1280×800)
"""
import sys
import io
import duckdb
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from pathlib import Path
from adjustText import adjust_text

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(__file__).resolve().parent.parent.parent
font_path = ROOT / 'paper' / 'fonts' / 'Pretendard-Regular.otf'
if font_path.exists():
    fm.fontManager.addfont(str(font_path))
    plt.rcParams['font.family'] = 'Pretendard'
plt.rcParams['axes.unicode_minus'] = False

DB_PATH   = ROOT / 'data' / 'warehouse.duckdb'
H10_PATH  = ROOT / 'data' / 'results' / 'H10_v3_alt_correlations.csv'
OUT_PATH  = ROOT / 'paper' / 'figures' / 'eda' / 'fig_slide32_quadrant.png'

# ── 1. outcome r 평균 (분야별) ─────────────────────────────────────────
h10 = pd.read_csv(H10_PATH)
r_by_field = (h10.groupby('field')['pearson_r']
              .apply(lambda x: x.abs().mean())
              .reset_index()
              .rename(columns={'field': 'FLD_NM', 'pearson_r': 'r_abs'}))

# ── 2. 분야 평균 집행률 (활동×연도 단위 평균) ─────────────────────────
con = duckdb.connect(str(DB_PATH), read_only=True)
exec_df = con.execute("""
WITH ay AS (
  SELECT FSCL_YY, ACTV_CD, FLD_NM,
         SUM(EP_AMT) AS exec_amt,
         MAX(ANEXP_BDG_CAMT) AS bdg_amt
  FROM monthly_exec
  WHERE FSCL_YY BETWEEN 2015 AND 2025 AND FLD_NM IS NOT NULL
  GROUP BY 1,2,3
  HAVING MAX(ANEXP_BDG_CAMT) > 0
)
SELECT FLD_NM,
       AVG(LEAST(exec_amt*1.0/bdg_amt, 1.5)) * 100 AS exec_rate,
       COUNT(*) AS n_av
FROM ay
GROUP BY FLD_NM
""").fetchdf()
con.close()

# 매칭
df = r_by_field.merge(exec_df, on='FLD_NM', how='inner')
df = df.sort_values('r_abs', ascending=False).reset_index(drop=True)
print('=== 분야별 평균 집행률 × outcome r ===')
print(df.to_string())

# ── 3. 산점도 ─────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(12.8, 8.0), dpi=100,
                       gridspec_kw={'left': 0.085, 'right': 0.97,
                                    'top': 0.84, 'bottom': 0.13})

# 색: 좌측 차트와 동일 스키마 (회색 더 진하게)
def color_for(r):
    if r >= 0.5: return '#C0392B'
    if r >= 0.3: return '#E67E22'
    return '#555'

colors = [color_for(v) for v in df['r_abs']]

# 가로 영역 강조 (천장 도달 영역)
ax.axvspan(95, 100, alpha=0.10, color='#888', zorder=0)
ax.text(97.5, 0.80, '집행률 95~99%\n(모든 분야 천장 근처)',
        ha='center', va='top', fontsize=13, color='#555',
        style='italic', fontweight='medium', zorder=1)

# 가로 ref line — outcome 임계
ax.axhline(0.5, color='#C0392B', linewidth=0.8, linestyle=':', alpha=0.45, zorder=1)
ax.axhline(0.3, color='#E67E22', linewidth=0.8, linestyle=':', alpha=0.45, zorder=1)

# 점 (크기 ↑, edge ↑)
ax.scatter(df['exec_rate'], df['r_abs'], s=380, c=colors,
           edgecolor='#1a1a1a', linewidth=1.2, alpha=0.92, zorder=3)

# 분야명 라벨 줄임 매핑
SHORT = {
    '산업·중소기업및에너지': '산업·중소·에너지',
    '국토및지역개발': '국토·지역개발',
    '공공질서및안전': '공공질서·안전',
    '교통및물류': '교통·물류',
    '문화및관광': '문화·관광',
}

# 라벨: 큰 글자 + 흰 배경 박스
texts = []
for _, row in df.iterrows():
    label = SHORT.get(row['FLD_NM'], row['FLD_NM'])
    # 점 색에 맞춰 라벨도 약간 짙게
    if row['r_abs'] >= 0.5:
        lc, lw = '#1a1a1a', 'bold'
    elif row['r_abs'] >= 0.3:
        lc, lw = '#1a1a1a', 'semibold'
    else:
        lc, lw = '#1a1a1a', 'normal'
    t = ax.text(row['exec_rate'], row['r_abs'], label,
                fontsize=14, color=lc, fontweight=lw,
                ha='left', va='center', zorder=5,
                bbox=dict(boxstyle='round,pad=0.25',
                          fc='white', ec='none', alpha=0.85))
    texts.append(t)

# adjustText로 라벨 자동 회피 — 점·다른 라벨 모두 회피, leader line 추가
adjust_text(
    texts,
    x=df['exec_rate'].values, y=df['r_abs'].values,
    ax=ax,
    expand=(1.8, 2.2),
    force_text=(0.9, 1.3),
    force_static=(0.6, 0.9),
    arrowprops=dict(arrowstyle='-', color='#555', lw=1.0, alpha=0.7),
    only_move={'text': 'xy', 'static': 'xy'},
)

# 세로축 영역 강조 (31배 분산) — 굵게·진하게
r_min, r_max = df['r_abs'].min(), df['r_abs'].max()
ratio = r_max / r_min if r_min > 0 else float('inf')
ax.annotate('',
            xy=(85.0, r_max), xytext=(85.0, r_min),
            arrowprops=dict(arrowstyle='<->', color='#C0392B', lw=2.6,
                            shrinkA=0, shrinkB=0))
ax.text(84.0, (r_min + r_max)/2, f'outcome 응답\n×{ratio:.0f}배\n분산',
        ha='right', va='center', fontsize=15, color='#C0392B',
        fontweight='bold', linespacing=1.4)

# 축 설정 — 통신(101.05%) 라벨 공간 확보 위해 102.5까지
ax.set_xlim(80, 102.5)
ax.set_ylim(-0.05, 0.85)
ax.set_xlabel('분야 평균 집행률 (%)   —   모두 90% 이상의 좁은 구간',
              fontsize=14, color='#222')
ax.set_ylabel('|outcome 상관|  (분야별 평균, Pearson r 절댓값)',
              fontsize=14, color='#222')
ax.tick_params(axis='both', labelsize=12)

title_main = '집행률은 비슷한데, outcome 응답은 31배 분산'
title_sub  = '14분야 평균 집행률 × outcome 상관 — 가로축이 좁고 세로축이 넓다'
ax.set_title(title_main, fontsize=18, pad=22, loc='left', fontweight='bold')
ax.text(0.0, 1.015, title_sub, transform=ax.transAxes,
        fontsize=13, color='#555', style='italic', va='bottom')

for s in ['top', 'right']:
    ax.spines[s].set_visible(False)
ax.grid(True, alpha=0.22, linestyle=':')

# 범례 — 좌상단 빈 공간 (점·라벨 회피)
from matplotlib.lines import Line2D
legend_elem = [
    Line2D([0], [0], marker='o', color='w', markerfacecolor='#C0392B',
           markersize=13, label='|r| ≥ 0.5 (강함)', markeredgecolor='#1a1a1a'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='#E67E22',
           markersize=13, label='|r| ≥ 0.3 (중간)', markeredgecolor='#1a1a1a'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='#555',
           markersize=13, label='|r| < 0.3 (약함)', markeredgecolor='#1a1a1a'),
]
ax.legend(handles=legend_elem, loc='upper left',
          bbox_to_anchor=(0.01, 0.99),
          fontsize=12.5,
          frameon=True, framealpha=0.92, edgecolor='#bbb',
          title=None, ncol=1)

OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(OUT_PATH, dpi=100, facecolor='white')
plt.close()

from PIL import Image
print(f'\nSaved: {OUT_PATH}')
print(f'Size:  {Image.open(OUT_PATH).size}')
print(f'분야 수: {len(df)} / outcome r 범위: {r_min:.2f} ~ {r_max:.2f} (×{ratio:.0f}배)')
print(f'집행률 범위: {df["exec_rate"].min():.1f}% ~ {df["exec_rate"].max():.1f}%')
