"""Slide 23 메인 차트 — archetype 4개 RDD β forest plot + L-M 미국 참조선.

narrative arc 유지: Slide 10에서 분야를 떨궈내고 archetype 전환했으니,
Act 3 결정 카드도 archetype-centric으로.

데이터: data/results/H22_field_rdd.csv 마지막 4행 (archetype 4개)
모형: log_daily ~ T + C(year), bw=1 (11·12월), cluster SE by ACTV_CD.
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from pathlib import Path

font_path = Path('paper/fonts/Pretendard-Regular.otf')
if font_path.exists():
    fm.fontManager.addfont(str(font_path))
    plt.rcParams['font.family'] = 'Pretendard'
plt.rcParams['axes.unicode_minus'] = False

# 데이터: H22_field_rdd.csv의 archetype 4행 추출
df = pd.read_csv('data/results/H22_field_rdd.csv')
ARCH_LABELS = ['인건비형', '자산취득형', '출연금형', '정상사업']
arch = df[df['label'].isin(ARCH_LABELS)].copy()

# label → archetype full name + color + role
META = {
    '인건비형':    ('C0 인건비형 · 비교군',   '#888888', '비교군'),
    '자산취득형':  ('C1 자산취득형 · 분석 대상', '#C0392B', '분석 대상'),
    '출연금형':    ('C2 출연금형 · 분석 대상',  '#E67E22', '분석 대상'),
    '정상사업':    ('C3 정상사업 · 비교군',    '#9b9b9b', '비교군'),
}
arch['full_label'] = arch['label'].map(lambda x: META[x][0])
arch['color']      = arch['label'].map(lambda x: META[x][1])
arch['role']       = arch['label'].map(lambda x: META[x][2])

# β 큰→작 정렬 (위에서 아래로) — C1이 맨 위
arch = arch.sort_values('beta', ascending=True).reset_index(drop=True)
print(arch[['label', 'beta', 'se', 'pval', 'mult', 'n']].to_string())

# 참조값
LM_BETA = np.log(5.0)  # 1.6094
try:
    ref = pd.read_csv('data/results/H22_rdd_estimates.csv')
    korea_beta = ref[(ref['label']=='전체') & (ref['bw']==1)].iloc[0]['beta']
except Exception:
    korea_beta = 0.6477

# Forest plot
fig, ax = plt.subplots(figsize=(11, 5.5), dpi=140)
ys = np.arange(len(arch))
ax.barh(ys, arch['beta'], xerr=1.96 * arch['se'],
        color=arch['color'], alpha=0.85, height=0.55,
        edgecolor='#444', linewidth=0.5,
        error_kw={'elinewidth': 1.8, 'capsize': 6, 'ecolor': '#444'})

ax.set_yticks(ys)
# y label에 archetype label + 굵게 (분석 대상 강조)
y_labels = arch['full_label'].tolist()
ax.set_yticklabels(y_labels, fontsize=11.5)
for tick_label, role in zip(ax.get_yticklabels(), arch['role']):
    if role == '분석 대상':
        tick_label.set_weight('bold')

ax.axvline(0, color='black', lw=1.0, zorder=1)
ax.axvline(korea_beta, color='#666', lw=1.8, ls='--', zorder=2,
           label=f'한국 전체 β={korea_beta:.2f} (×{np.exp(korea_beta):.2f})')
ax.axvline(LM_BETA, color='#6a4caf', lw=1.8, ls=':', zorder=2,
           label=f'L-M 2017 미국 β≈{LM_BETA:.2f} (×5.0)')

# 각 막대 옆 ×배 + p값 라벨
for i, row in arch.iterrows():
    sig = ('***' if row['pval'] < 0.001 else '**' if row['pval'] < 0.01
           else '*' if row['pval'] < 0.05 else 'ns')
    is_sig = row['pval'] < 0.05
    color_text = row['color'] if is_sig else '#888'
    weight = 'bold' if is_sig and row['beta'] > korea_beta else 'normal'
    ax.text(row['beta'] + 1.96 * row['se'] + 0.06, i,
            f'×{row["mult"]:.2f}  {sig}',
            va='center', ha='left', fontsize=12,
            color=color_text, weight=weight)

ax.legend(loc='lower right', fontsize=10, framealpha=0.92)
ax.set_xlabel('β (log 일평균 집행액 점프, 12월 cutoff · 95% CI)', fontsize=11)
ax.set_title(
    'Slide 23. 12월 cutoff RDD — 4 archetype 비교\n'
    'C1 자산취득형 ×3.42 압도 · C2 출연금형 ns (점프 아닌 cycle) · '
    '한국 어느 archetype도 미국 5×에는 못 미친다',
    fontsize=12, pad=12, weight='bold', linespacing=1.4)
ax.title.set_multialignment('center')

x_max = max((arch['beta'] + 1.96 * arch['se']).max() + 0.4,
            LM_BETA + 0.1)
x_min = min(0, (arch['beta'] - 1.96 * arch['se']).min() - 0.1)
ax.set_xlim(x_min, x_max)
for s in ['top', 'right']:
    ax.spines[s].set_visible(False)
ax.grid(True, axis='x', alpha=0.25, linestyle=':')

# 하단 footnote
fig.text(0.5, -0.01,
         '※ log_daily ~ T + C(year), bw=1 (11·12월), cluster SE by ACTV_CD · '
         '출처: data/results/H22_field_rdd.csv (archetype 4행)',
         ha='center', fontsize=8.5, color='#666', style='italic')

plt.tight_layout(rect=[0, 0.02, 1, 0.94])
out = Path('paper/figures/h22_rdd_archetype_forest.png')
plt.savefig(out, dpi=140, bbox_inches='tight', facecolor='white')
plt.close()

from PIL import Image
w, h = Image.open(out).size
print(f'저장: {out} | {w}x{h}px')
