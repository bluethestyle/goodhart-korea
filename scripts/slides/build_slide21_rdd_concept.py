"""Slide 21 메인 차트 — RDD 개념 도입 다이어그램.

S21은 'RDD가 뭔가'를 보여주는 교과서 패턴: cutoff 양쪽 fit + 점프 + counterfactual.
S22/S23(실제 데이터 정량)과 narrative 명확 분리.

월별 데이터(day-level X) 부재이므로 schematic mock으로 표현.
β·×배 값은 한국 전체 RDD 실제 추정치(β=0.65, ×1.91)에 정렬.
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from pathlib import Path

font_path = Path('paper/fonts/Pretendard-Regular.otf')
if font_path.exists():
    fm.fontManager.addfont(str(font_path))
    plt.rcParams['font.family'] = 'Pretendard'
plt.rcParams['axes.unicode_minus'] = False

np.random.seed(42)

# 한국 실제 RDD 추정치
beta_actual = 0.6477   # 점프 크기 (log)
mult_actual = np.exp(beta_actual)  # ×1.91

# x = 시간 (day 단위, cutoff = 12월 1일 = 0). 좌(11월) / 우(12월)
n_pts = 28
x_nov = np.linspace(-30, -1, n_pts)   # 11월
x_dec = np.linspace(0, 30, n_pts)     # 12월

# y = log(일평균 집행액) schematic
intercept_nov = 1.00
intercept_dec = intercept_nov + beta_actual  # 점프 = β
slope_within = 0.003   # 내부 slope 작음 (회계 마감 효과는 cutoff 이산점)
noise_sd = 0.13

y_nov = intercept_nov + slope_within * x_nov + np.random.normal(0, noise_sd, n_pts)
y_dec = intercept_dec + slope_within * x_dec + np.random.normal(0, noise_sd, n_pts)

# fit
fit_nov = np.polyfit(x_nov, y_nov, 1)
fit_dec = np.polyfit(x_dec, y_dec, 1)
xx_nov = np.linspace(-30, 0, 60)
xx_dec = np.linspace(0, 30, 60)
yy_nov = np.polyval(fit_nov, xx_nov)
yy_dec = np.polyval(fit_dec, xx_dec)
# counterfactual: 11월 fit을 12월로 extrapolate
yy_cfact = np.polyval(fit_nov, xx_dec)

# 점프 크기 (fit 기준, x=0에서 측정)
y_at_cutoff_left  = np.polyval(fit_nov, 0)
y_at_cutoff_right = np.polyval(fit_dec, 0)
beta_observed = y_at_cutoff_right - y_at_cutoff_left

fig, ax = plt.subplots(figsize=(11, 6), dpi=140)

# 산점도
ax.scatter(x_nov, y_nov, c='#888888', s=38, alpha=0.7,
           edgecolor='#444', linewidth=0.4, label='11월 관측 (T=0, 처치 전)', zorder=3)
ax.scatter(x_dec, y_dec, c='#C0392B', s=38, alpha=0.75,
           edgecolor='#444', linewidth=0.4, label='12월 관측 (T=1, 처치 후)', zorder=3)

# fit lines
ax.plot(xx_nov, yy_nov, color='#444', lw=2.5, zorder=4)
ax.plot(xx_dec, yy_dec, color='#C0392B', lw=2.5, zorder=4)

# counterfactual
ax.plot(xx_dec, yy_cfact, color='#444', lw=1.8, ls='--', alpha=0.55,
        label='counterfactual (cutoff 없었다면)', zorder=2)

# cutoff 수직선
ax.axvline(0, color='black', lw=1.3, ls=':', zorder=1)

# 점프 화살표 + β 라벨 (한국 실제 추정치 사용)
ax.annotate('', xy=(2.5, y_at_cutoff_right), xytext=(2.5, y_at_cutoff_left),
            arrowprops=dict(arrowstyle='<->', color='#C0392B', lw=2.8,
                            mutation_scale=18), zorder=5)
mid_y = (y_at_cutoff_left + y_at_cutoff_right) / 2
ax.text(4, mid_y,
        f'β = {beta_actual:.2f}\n×{mult_actual:.2f}\n(한국 전체 추정)',
        fontsize=12, color='#C0392B', weight='bold',
        verticalalignment='center', linespacing=1.3,
        bbox=dict(boxstyle='round,pad=0.4', facecolor='white',
                  edgecolor='#C0392B', linewidth=1.2))

# cutoff 라벨
ax.text(-0.3, ax.get_ylim()[1] if False else 1.95,
        '12월 1일\ncutoff', fontsize=10.5, color='#222',
        ha='right', va='top',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='#f5f1e8',
                  edgecolor='#aaa', linewidth=0.8))

# 축·제목
ax.set_xlabel('시간 (cutoff 기준 일 · 회계연도 마감 = 12월 31일)', fontsize=11)
ax.set_ylabel('log (일평균 집행액)', fontsize=11)
ax.set_title(
    'RDD 개념 — 외형은 연속, 절단은 제도가 만든다\n'
    '11→12월 cutoff에서 같은 사업의 일평균 집행이 e^β = ×배로 점프 (한국 전체 β≈0.65)',
    fontsize=12.5, pad=12, weight='bold', linespacing=1.4)
ax.title.set_multialignment('center')

ax.legend(loc='lower right', fontsize=10, framealpha=0.92)
for s in ['top', 'right']:
    ax.spines[s].set_visible(False)
ax.grid(alpha=0.2, linestyle=':')

# footnote
fig.text(0.5, -0.01,
         '※ schematic 다이어그램 (월별 데이터의 RDD 개념 도식화). 실제 추정은 monthly daily-avg with year FE + cluster SE. 정량 결과는 Slide 22-23.',
         ha='center', fontsize=8.5, color='#666', style='italic')

plt.tight_layout(rect=[0, 0.02, 1, 0.94])
out = Path('paper/figures/rdd_concept.png')
plt.savefig(out, dpi=140, bbox_inches='tight', facecolor='white')
plt.close()

from PIL import Image
w, h = Image.open(out).size
print(f'저장: {out} | {w}x{h}px')
