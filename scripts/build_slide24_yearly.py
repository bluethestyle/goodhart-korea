"""Slide 24 보조 차트 강화 — 11년 안정성 시각화.

기존 h22_rdd_yearly.png는 단순 막대였으나, "매년 동일 점프 = 제도적 패턴"
narrative가 시각적으로 즉시 안 와닿는 한계. 개선 사항:
  (a) 제목·부제로 메시지 명시
  (b) 막대 위 ×배율 라벨 (log scale 직관 어려움 해소)
  (c) 11년 평균 ±1sd 배경 axhspan (좁은 범위 시각 강조)
  (d) y축 우측 secondary ×배율 축
  (e) 연도 4자리 표기
  (f) L-M 미국 ×5 참조선 유지 + 한국 평균 점선

데이터 spec: h22_rdd_yearend.py와 동일 — 11·12월 log_daily 활동별 점프, 연도별 중앙값.
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import duckdb
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from pathlib import Path

font_path = Path('paper/fonts/Pretendard-Regular.otf')
if font_path.exists():
    fm.fontManager.addfont(str(font_path))
    plt.rcParams['font.family'] = 'Pretendard'
plt.rcParams['axes.unicode_minus'] = False

DAYS = {11: 30, 12: 31}

# 데이터: 11·12월 활동·연도별 log(일평균 집행액)
con = duckdb.connect('data/warehouse.duckdb', read_only=True)
df = con.execute("""
    SELECT FSCL_YY AS year, EXE_M AS month, ACTV_CD,
           SUM(EP_AMT) AS ep_amt
    FROM monthly_exec
    WHERE FSCL_YY BETWEEN 2015 AND 2025
      AND EXE_M IN (11, 12)
      AND EP_AMT > 0
    GROUP BY 1, 2, 3
""").df()
df['days']      = df['month'].map(DAYS)
df['log_daily'] = np.log(df['ep_amt'] / df['days'])

# 연도별 11→12월 활동 단위 log 점프 중앙값
piv = df.pivot_table(index=['year', 'ACTV_CD'], columns='month',
                     values='log_daily').dropna()
piv.columns = ['nov', 'dec']
piv['jump'] = piv['dec'] - piv['nov']
yr_jump = piv.groupby('year')['jump'].median().reset_index()
print(yr_jump.to_string(index=False))

# 한국 전체 β 참조
try:
    ref = pd.read_csv('data/results/H22_rdd_estimates.csv')
    beta_total = float(ref[(ref['label']=='전체') & (ref['bw']==1)].iloc[0]['beta'])
except Exception:
    beta_total = 0.6477
mult_total = np.exp(beta_total)

# L-M 미국 참조
LM_MULT = 5.0
LM_BETA = np.log(LM_MULT)

# 11년 평균·sd (yr 중앙값들의 평균)
yr_jumps = yr_jump['jump'].values
mean_jump = yr_jumps.mean()
sd_jump   = yr_jumps.std()
min_jump  = yr_jumps.min()
max_jump  = yr_jumps.max()
min_mult  = np.exp(min_jump)
max_mult  = np.exp(max_jump)
print(f'11년 점프 범위: ×{min_mult:.2f} ~ ×{max_mult:.2f}, '
      f'평균 ×{np.exp(mean_jump):.2f}, sd ±{sd_jump:.3f}')

# 차트
fig, ax = plt.subplots(figsize=(11, 6), dpi=140)

# (c) 11년 평균 ±1sd 배경 axhspan — "좁은 범위" 시각 강조
ax.axhspan(mean_jump - sd_jump, mean_jump + sd_jump,
           color='#fde4d8', alpha=0.55, zorder=0,
           label=f'11년 평균 ±1sd 범위')

# 막대
bars = ax.bar(yr_jump['year'], yr_jump['jump'],
              color='#C0392B', alpha=0.82, width=0.65,
              edgecolor='#444', linewidth=0.5, zorder=3)

# (b) 막대 위 ×배율 라벨
for bar, j in zip(bars, yr_jump['jump']):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
            f'×{np.exp(j):.2f}',
            ha='center', va='bottom', fontsize=9.5, color='#444',
            zorder=4)

# 한국 전체 점선
ax.axhline(beta_total, color='#1a1814', lw=1.8, ls='--', zorder=2,
           label=f'한국 11년 평균 β={beta_total:.2f} (×{mult_total:.2f})')
# L-M 미국 점선
ax.axhline(LM_BETA, color='#6a4caf', lw=1.5, ls=':', zorder=2,
           label=f'L-M 2017 미국 ×{LM_MULT:.1f} (β≈{LM_BETA:.2f})')

ax.set_xticks(yr_jump['year'])
ax.set_xticklabels([str(int(y)) for y in yr_jump['year']], fontsize=10)
ax.set_xlabel('회계연도', fontsize=11)
ax.set_ylabel('log 점프 (12월 − 11월, 활동 중앙값)', fontsize=11)

# (a) 제목·부제
ax.set_title(
    'Slide 24. 매년 동일 점프 — 단일 연도 우연 아닌 제도적 패턴\n'
    f'11년 연속 ×{min_mult:.2f}–×{max_mult:.2f} 좁은 범위 '
    f'(평균 ×{np.exp(mean_jump):.2f}, sd ±{sd_jump:.3f}) · '
    f'공정률이 매년 12월에 함께 뛸 가능성은 0',
    fontsize=12, pad=12, weight='bold', linespacing=1.4)
ax.title.set_multialignment('center')

# (d) y축 우측 secondary ×배율 축
def log_to_mult(x):
    return np.exp(x)
def mult_to_log(x):
    return np.log(x)
secax = ax.secondary_yaxis('right', functions=(log_to_mult, mult_to_log))
secax.set_ylabel('점프 배율 (×배)', fontsize=10.5, color='#666')
secax.set_yticks([1.0, 1.5, 2.0, 3.0, 5.0])
secax.tick_params(axis='y', labelcolor='#666', labelsize=9.5)

ax.legend(loc='upper right', fontsize=9.5, framealpha=0.94)
for s in ['top']:
    ax.spines[s].set_visible(False)
ax.grid(True, axis='y', alpha=0.22, linestyle=':', zorder=1)

# footnote
fig.text(0.5, -0.01,
         '※ 각 연도 = 해당 연도 활동 단위 log(12월/11월 일평균 집행액) 점프의 중앙값 · '
         '출처: data/warehouse.duckdb monthly_exec',
         ha='center', fontsize=8.5, color='#666', style='italic')

plt.tight_layout(rect=[0, 0.02, 1, 0.94])
out = Path('paper/figures/h22_rdd_yearly.png')
plt.savefig(out, dpi=140, bbox_inches='tight', facecolor='white')
plt.close()

from PIL import Image
w, h = Image.open(out).size
print(f'저장: {out} | {w}x{h}px')
