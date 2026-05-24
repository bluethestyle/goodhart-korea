"""Slide 23 메인 차트 — 분야별 RDD β forest plot 단독 PNG.

Slide 22의 2x2 archetype grid와 narrative 중복 회피.
Slide 23은 분야 단위(13개+) deep dive로 역할 분담.

데이터: data/results/H22_field_rdd.csv (h22_rdd_yearend.py 산출).
모형: log_daily ~ T + C(year), bw=1, cluster SE by ACTV_CD (12월 cutoff).
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.patches as mpatches
from pathlib import Path

# 한글 폰트
font_path = Path('paper/fonts/Pretendard-Regular.otf')
if font_path.exists():
    fm.fontManager.addfont(str(font_path))
    plt.rcParams['font.family'] = 'Pretendard'
plt.rcParams['axes.unicode_minus'] = False

# 데이터 로드 & 분야 분리
df = pd.read_csv('data/results/H22_field_rdd.csv')
ARCHETYPES = {'인건비형', '자산취득형', '출연금형', '정상사업'}
fld = df[~df['label'].isin(ARCHETYPES)].copy()
fld = fld.sort_values('beta', ascending=True).reset_index(drop=True)
print(f'분야 수: {len(fld)} (archetype 4개 제외)')

# 한국 전체 + L-M 5x 참조값
LM_BETA = np.log(5.0)
try:
    ref = pd.read_csv('data/results/H22_rdd_estimates.csv')
    korea_beta = ref[(ref['label']=='전체') & (ref['bw']==1)].iloc[0]['beta']
except Exception:
    korea_beta = 0.6477

# Forest plot
fig, ax = plt.subplots(figsize=(11, 7), dpi=140)
ys = np.arange(len(fld))
colors = ['#C0392B' if p < 0.05 else '#aaaaaa' for p in fld['pval']]
ax.barh(ys, fld['beta'], xerr=1.96 * fld['se'],
        color=colors, alpha=0.78, height=0.6,
        error_kw={'elinewidth': 1.4, 'capsize': 4, 'ecolor': '#444'})

ax.set_yticks(ys)
ax.set_yticklabels(fld['label'], fontsize=11)
ax.axvline(0, color='black', lw=1.0, zorder=1)
ax.axvline(korea_beta, color='#E67E22', lw=1.8, ls='--', zorder=2,
           label=f'한국 전체 β={korea_beta:.2f} (×{np.exp(korea_beta):.2f})')
ax.axvline(LM_BETA, color='#6a4caf', lw=1.8, ls=':', zorder=2,
           label=f'L-M 2017 미국 5× (β≈{LM_BETA:.2f})')

# 각 막대 옆 ×배 라벨
for i, row in fld.iterrows():
    sig = '***' if row['pval'] < 0.001 else '**' if row['pval'] < 0.01 \
          else '*' if row['pval'] < 0.05 else 'ns'
    color = '#222' if row['pval'] < 0.05 else '#888'
    weight = 'bold' if row['beta'] > korea_beta and row['pval'] < 0.05 else 'normal'
    ax.text(row['beta'] + 1.96 * row['se'] + 0.04, i,
            f'×{row["mult"]:.2f} {sig}',
            va='center', ha='left', fontsize=10,
            color=color, weight=weight)

# 범례
sig_patch = mpatches.Patch(color='#C0392B', alpha=0.78, label='p<0.05')
ns_patch  = mpatches.Patch(color='#aaaaaa', alpha=0.78, label='p≥0.05')
ax.legend(handles=[sig_patch, ns_patch,
                   plt.Line2D([0], [0], color='#E67E22', ls='--', lw=1.8,
                              label=f'한국 전체 β={korea_beta:.2f}'),
                   plt.Line2D([0], [0], color='#6a4caf', ls=':', lw=1.8,
                              label=f'L-M 미국 β≈{LM_BETA:.2f}')],
          loc='lower right', fontsize=9.5, framealpha=0.9)

ax.set_xlabel('β (log 일평균 집행액 점프, 12월 cutoff · 95% CI)', fontsize=11)
# 동적 통계: 상회 분야 + ns 분야
n_sig = (fld['pval'] < 0.05).sum()
n_total = len(fld)
ns_fields = fld[fld['pval'] >= 0.05]['label'].tolist()
above_korea = fld[(fld['beta'] > korea_beta) & (fld['pval'] < 0.05)]['label'].tolist()
above_str = ('국방·국토 등 ' + str(len(above_korea)) + '개 분야' if len(above_korea) > 3
             else ' · '.join(above_korea))
ns_str = ('전체 ***' if not ns_fields
          else f'{", ".join(ns_fields)}만 ns')

ax.set_title(
    'Slide 23. 12월 cutoff RDD — 분야별 점프 강도\n'
    f'{n_total}분야 중 {n_sig}개 *** 유의 ({ns_str}) · {above_str}이 한국 전체 평균 상회',
    fontsize=12.5, pad=12, weight='bold', linespacing=1.4)
ax.title.set_multialignment('center')

# 우측 여유 (라벨이 막대 옆에 표시되므로 x 범위 확장)
x_max = max((fld['beta'] + 1.96 * fld['se']).max() + 0.3,
            LM_BETA + 0.1)
ax.set_xlim(-0.1, x_max)
for s in ['top', 'right']:
    ax.spines[s].set_visible(False)
ax.grid(True, axis='x', alpha=0.25, linestyle=':')

# 하단 footnote
fig.text(0.5, -0.01,
         '※ log_daily ~ T + C(year), bw=1 (11·12월), cluster SE by ACTV_CD · '
         '출처: data/results/H22_field_rdd.csv',
         ha='center', fontsize=8.5, color='#666', style='italic')

plt.tight_layout(rect=[0, 0.02, 1, 0.95])
out = Path('paper/figures/h22_rdd_field_forest.png')
plt.savefig(out, dpi=140, bbox_inches='tight', facecolor='white')
plt.close()

from PIL import Image
w, h = Image.open(out).size
print(f'저장: {out} | {w}x{h}px')
