"""Slide 26 (자산취득형 11년 안정성) — C1만 필터링.

기존 build_slide24_yearly.py 는 전체 활동의 12→11월 점프 중앙값을 보였다.
본 슬라이드는 분석 focus(C1 자산취득형)에 맞춰 cluster==1 만 필터링.
다음 슬라이드(REFRAME ×3.42)와 직결되는 셋업 차트.

데이터 spec: monthly_exec ⊳ H3_activity_embedding_11y(cluster==1, n=99)
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import duckdb
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from pathlib import Path
from PIL import Image

font_path = Path('paper/fonts/Pretendard-Regular.otf')
if font_path.exists():
    fm.fontManager.addfont(str(font_path))
    plt.rcParams['font.family'] = 'Pretendard'
plt.rcParams['axes.unicode_minus'] = False

DAYS = {11: 30, 12: 31}

# 1. C1(자산취득형) 활동 NM 목록
emb = pd.read_csv('data/results/H3_activity_embedding_11y.csv')
c1 = emb[emb['cluster'] == 1][['FLD_NM','OFFC_NM','PGM_NM','ACTV_NM']].copy()
print(f'C1 자산취득형 활동 수: {len(c1):,}')

# 2. monthly_exec에서 11·12월 ep_amt — C1 활동만 inner join
con = duckdb.connect('data/warehouse.duckdb', read_only=True)
con.register('c1_keys', c1)
df = con.execute("""
    SELECT m.FSCL_YY AS year, m.EXE_M AS month, m.ACTV_CD,
           SUM(m.EP_AMT) AS ep_amt
    FROM monthly_exec m
    INNER JOIN c1_keys k
       ON m.FLD_NM  = k.FLD_NM
      AND m.OFFC_NM = k.OFFC_NM
      AND m.PGM_NM  = k.PGM_NM
      AND m.ACTV_NM = k.ACTV_NM
    WHERE m.FSCL_YY BETWEEN 2015 AND 2025
      AND m.EXE_M IN (11, 12)
      AND m.EP_AMT > 0
    GROUP BY 1, 2, 3
""").df()
df['days']      = df['month'].map(DAYS)
df['log_daily'] = np.log(df['ep_amt'] / df['days'])

piv = df.pivot_table(index=['year','ACTV_CD'], columns='month',
                     values='log_daily').dropna()
piv.columns = ['nov', 'dec']
piv['jump'] = piv['dec'] - piv['nov']
yr_jump = piv.groupby('year')['jump'].median().reset_index()
print(yr_jump.to_string(index=False))

# 3. C1 평균·범위 + 미국 비교
yr_jumps  = yr_jump['jump'].values
mean_jump = yr_jumps.mean()
sd_jump   = yr_jumps.std()
min_mult  = np.exp(yr_jumps.min())
max_mult  = np.exp(yr_jumps.max())
mean_mult = np.exp(mean_jump)
print(f'C1 11년 범위 ×{min_mult:.2f}–×{max_mult:.2f}, '
      f'평균 ×{mean_mult:.2f}, sd ±{sd_jump:.3f}')

LM_MULT = 5.0
LM_BETA = np.log(LM_MULT)

# 4. 차트 (figsize × dpi ≤ 1280 가드 — 9×5 @140 = 1260×700)
fig, ax = plt.subplots(figsize=(9, 5), dpi=140)

# 평균 ±1sd 음영
ax.axhspan(mean_jump - sd_jump, mean_jump + sd_jump,
           color='#fde4d8', alpha=0.6, zorder=0,
           label=f'C1 11년 평균 ±1sd 범위')

# C1 막대 (자산취득형 강조: 더 진한 brick-red)
bars = ax.bar(yr_jump['year'], yr_jump['jump'],
              color='#c0392b', alpha=0.88, width=0.65,
              edgecolor='#3a1f1c', linewidth=0.5, zorder=3)
for bar, j in zip(bars, yr_jump['jump']):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.03,
            f'×{np.exp(j):.2f}',
            ha='center', va='bottom', fontsize=9.5, color='#2a1a17',
            weight='bold', zorder=4)

# 11년 평균 점선
ax.axhline(mean_jump, color='#1a1814', lw=1.6, ls='--', zorder=2,
           label=f'C1 11년 평균 β={mean_jump:.2f} (×{mean_mult:.2f})')
# L-M 미국 점선
ax.axhline(LM_BETA, color='#6a4caf', lw=1.4, ls=':', zorder=2,
           label=f'L-M 2017 미국 ×{LM_MULT:.1f} (β≈{LM_BETA:.2f})')

ax.set_xticks(yr_jump['year'])
ax.set_xticklabels([str(int(y)) for y in yr_jump['year']], fontsize=10)
ax.set_xlabel('회계연도', fontsize=11)
ax.set_ylabel('log 점프 (12월 − 11월, C1 활동 중앙값)', fontsize=11)

ax.set_title(
    'C1 자산취득형 — 매년 ×3 안팎 점프, 11년 연속 제도 패턴\n'
    f'11년 범위 ×{min_mult:.2f}–×{max_mult:.2f} '
    f'(평균 ×{mean_mult:.2f}, sd ±{sd_jump:.3f}) · '
    f'현장 공정률이 매년 12월에 함께 ×3+ 뛸 가능성은 0',
    fontsize=11.5, pad=12, weight='bold', linespacing=1.4)
ax.title.set_multialignment('center')

# 우측 secondary ×배율 축
def log_to_mult(x): return np.exp(x)
def mult_to_log(x): return np.log(x)
secax = ax.secondary_yaxis('right', functions=(log_to_mult, mult_to_log))
secax.set_ylabel('점프 배율 (×배)', fontsize=10.5, color='#666')
secax.set_yticks([1.5, 2.0, 3.0, 5.0])
secax.tick_params(axis='y', labelcolor='#666', labelsize=9.5)

# y축 한계 — L-M ×5 점선이 보이도록
y_top = max(yr_jumps.max(), LM_BETA) + 0.15
ax.set_ylim(0, y_top)

ax.legend(loc='upper left', fontsize=9.5, framealpha=0.94)
for s in ['top']:
    ax.spines[s].set_visible(False)
ax.grid(True, axis='y', alpha=0.22, linestyle=':', zorder=1)

fig.text(0.5, -0.01,
         '※ 각 연도 = C1 자산취득형 99개 사업의 log(12월/11월 일평균 집행액) 점프 중앙값 · '
         '출처: data/warehouse.duckdb monthly_exec · H3_activity_embedding_11y(cluster==1)',
         ha='center', fontsize=8.0, color='#666', style='italic')

plt.tight_layout(rect=[0, 0.02, 1, 0.94])
out = Path('paper/figures/h22_rdd_yearly_c1.png')
plt.savefig(out, dpi=140, bbox_inches='tight', facecolor='white')
plt.close()

w, h = Image.open(out).size
print(f'저장: {out} | {w}x{h}px')

# 1280 가드
if w > 1280:
    im = Image.open(out)
    new_h = im.height * 1280 // im.width
    im.resize((1280, new_h), Image.LANCZOS).save(out)
    w2, h2 = Image.open(out).size
    print(f'리사이즈: {w2}x{h2}px')
