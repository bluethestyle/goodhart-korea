"""신규 차트 4종 생성 (Slide 22 · 26 · 32 · 33).

- Slide 22: cutoff 4막대 (3·6·9·12월 점프 배율)
- Slide 26: 3 렌즈 도구 카드 (FFT·Wavelet·NeuralProphet)
- Slide 32: 14분야 outcome 상관 강도 (분산 노출)
- Slide 33: 매개 분석 다이어그램 (X → M → Y + Sobel z)
"""
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from pathlib import Path
import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

font_path = Path('paper/fonts/Pretendard-Regular.otf')
if font_path.exists():
    fm.fontManager.addfont(str(font_path))
    plt.rcParams['font.family'] = 'Pretendard'
plt.rcParams['axes.unicode_minus'] = False

out_dir = Path('paper/figures/eda')
out_dir.mkdir(exist_ok=True, parents=True)

# ──────────────────────────────────────────────────────────────────────
# Slide 22 — archetype × cutoff 2x2 grid
# (data/results/H22_quarterly_cutoffs.csv 동적 로드)
# 추정 spec: log_daily ~ T + C(year), bw=1, cluster SE by ACTV_CD
# ──────────────────────────────────────────────────────────────────────
q_csv = Path('data/results/H22_quarterly_cutoffs.csv')
if not q_csv.exists():
    raise FileNotFoundError(
        f'{q_csv} 부재 — 먼저 `python scripts/h22_quarterly_cutoffs.py` 실행 필요')
q_df = pd.read_csv(q_csv)

# 4 archetype 패널 정의 (좌상→우상→좌하→우하 = C0→C1→C2→C3)
ARCHETYPE_PANELS = [
    ('C0 인건비형',  '#888888', '비교군'),
    ('C1 자산취득형', '#C0392B', '분석 대상'),
    ('C2 출연금형',  '#E67E22', '분석 대상'),
    ('C3 정상사업',  '#9b9b9b', '비교군'),
]

# 공통 y축 범위 (최대 ×배 + 여유)
all_archetype_df = q_df[q_df['group'] != '전체']
y_max = all_archetype_df['mult'].max() * 1.28

fig, axes = plt.subplots(2, 2, figsize=(11, 7), dpi=140, sharey=True)
axes_flat = axes.flatten()

for i, (group_label, color, role) in enumerate(ARCHETYPE_PANELS):
    ax = axes_flat[i]
    sub = q_df[q_df['group'] == group_label].sort_values('cutoff_month').reset_index(drop=True)
    cutoffs = sub['cutoff'].tolist()
    betas   = sub['beta'].tolist()
    ratios  = sub['mult'].tolist()
    pvals   = sub['pval'].tolist()
    n_acts  = sub['n_clusters'].tolist()

    # 12월(cutoff_month=12)만 cluster color accent, 나머지는 연회색
    colors = [color if cm == 12 else '#cccccc'
              for cm in sub['cutoff_month']]
    bars = ax.bar(cutoffs, ratios, color=colors,
                  edgecolor='#444', linewidth=0.5)
    ax.axhline(1.0, color='#666', linewidth=0.8, linestyle=':')

    # 막대 위 라벨 (×배 + 유의성)
    for bar, r, b, p in zip(bars, ratios, betas, pvals):
        sig = ('***' if p<0.001 else '**' if p<0.01
               else '*' if p<0.05 else 'ns')
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.06,
                f'×{r:.2f}\n{sig}',
                ha='center', fontsize=9.5,
                weight='bold' if r > 1.5 else 'normal',
                color=color if r > 1.5 else '#666')

    # panel title: archetype + role + 12월 ×배
    dec_row = sub[sub['cutoff_month']==12].iloc[0]
    is_target = (role == '분석 대상')
    ax.set_title(
        f'{group_label}  ▸  {role}',
        fontsize=12, color=color if is_target else '#444',
        weight='bold' if is_target else 'normal', pad=8)

    ax.set_ylim(0, y_max)
    ax.tick_params(axis='x', labelsize=9.5)
    if i % 2 == 0:
        ax.set_ylabel('점프 배율 (e^β)', fontsize=10)
    if i >= 2:
        ax.set_xlabel('cutoff (전월 대비)', fontsize=10)
    for s in ['top', 'right']:
        ax.spines[s].set_visible(False)
    ax.grid(True, axis='y', alpha=0.25, linestyle=':')

# 전체 figure title
fig.suptitle(
    '분기말 cutoff별 RDD 점프 — archetype마다 다른 패턴\n'
    'C1 자산취득형은 12월 ×3.42 폭발 · C2 출연금형은 모든 cutoff ns (점프 아닌 cycle)',
    fontsize=12.5, y=1.00, weight='bold',
    linespacing=1.4)

# 하단 footnote
n_obs_total = int(q_df[q_df['group']=='전체']['n_obs'].sum())
fig.text(0.5, -0.01,
         f'※ log_daily ~ T + C(year), bw=1 (cutoff 양쪽 두 달), '
         f'cluster SE by ACTV_CD · '
         f'H3 cluster 매칭 활동만 (전체 1,605 활동 중 약 935)',
         ha='center', fontsize=10.5, color='#666', style='italic')

plt.tight_layout(rect=[0, 0.02, 1, 0.94])
out22 = out_dir / 'fig_slide22_cutoff_bars.png'
plt.savefig(out22, dpi=140, bbox_inches='tight', facecolor='white')
plt.close()
print(f'[Slide 22] {out22} | 2x2 archetype grid')

# ──────────────────────────────────────────────────────────────────────
# Slide 33 — 매개 분석 다이어그램 (X → M → Y)
# ──────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 4.5), dpi=140)
ax.set_xlim(0, 10)
ax.set_ylim(0, 4)
ax.axis('off')

for x, label, sub in [(1.5, 'X', '12월 집중도\n(dec_pct)'),
                       (5.0, 'M', '시점 압력\narchetype'),
                       (8.5, 'Y', '농가소득\noutcome')]:
    rect = FancyBboxPatch((x - 0.85, 1.4), 1.7, 1.2,
                          boxstyle='round,pad=0.08', linewidth=2,
                          edgecolor='#C0392B', facecolor='#FFF5F5')
    ax.add_patch(rect)
    ax.text(x, 2.25, label, ha='center', fontsize=22, weight='bold',
            color='#C0392B')
    ax.text(x, 1.65, sub, ha='center', fontsize=10, color='#444')

for x_start, x_end, label in [(2.4, 4.2, 'a path'), (5.8, 7.7, 'b path')]:
    arrow = FancyArrowPatch((x_start, 2.0), (x_end, 2.0),
                             arrowstyle='-|>', mutation_scale=22,
                             linewidth=1.8, color='#555')
    ax.add_patch(arrow)
    ax.text((x_start + x_end) / 2, 2.25, label,
            ha='center', fontsize=10.5, color='#555', weight='bold')

# c' direct curve (아래로 우회)
arrow_c = FancyArrowPatch((2.4, 1.4), (7.7, 1.4),
                          arrowstyle='-|>',
                          connectionstyle='arc3,rad=-0.35',
                          mutation_scale=18, linewidth=1.2, color='#999',
                          linestyle='--')
ax.add_patch(arrow_c)
ax.text(5.0, 0.45, "c' (직접 효과, 매개 통제 후)",
        ha='center', fontsize=10, color='#888', style='italic')

# Sobel z (상단)
ax.text(5.0, 3.55, 'Sobel z = ab / SE(ab) = −2.897   (p = 0.004)',
        ha='center', fontsize=14, color='#C0392B', weight='bold')
ax.text(5.0, 3.15, '14분야 중 농림수산 H4만 통계적으로 유의',
        ha='center', fontsize=10.5, color='#555', style='italic')

ax.set_title('매개 분석 (Baron-Kenny + Sobel + Bootstrap) — 농림수산 H4',
             fontsize=13, pad=10)
plt.tight_layout()
out33 = out_dir / 'fig_slide33_mediation_diagram.png'
plt.savefig(out33, dpi=140, bbox_inches='tight', facecolor='white')
plt.close()
print(f'[Slide 33] {out33}')

# ──────────────────────────────────────────────────────────────────────
# Slide 26 — 3 렌즈 도구 카드 (FFT · Wavelet · NeuralProphet)
# ──────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(11, 4.5), dpi=140)
ax.set_xlim(0, 12)
ax.set_ylim(0, 4.5)
ax.axis('off')

cards = [
    (2.0, '① FFT', '주파수 (도메인 1)',
     '한 곡을\n음높이별로 쪼개\n어느 음이 강한지', '#3498db'),
    (6.0, '② Wavelet', '시간 × 주파수 (도메인 2)',
     '한 곡을 시간대별로 잘라\n시점마다 어느 음이\n강했는지', '#e67e22'),
    (10.0, '③ NeuralProphet', '추세 + 계절성 (도메인 3)',
     '지구온난화 추세를 빼고\n4계절 패턴만\n(AR Net 제외)', '#27ae60'),
]
for x, title, axis_label, desc, color in cards:
    rect = FancyBboxPatch((x - 1.6, 0.8), 3.2, 3.0,
                          boxstyle='round,pad=0.1', linewidth=2,
                          edgecolor=color, facecolor=color + '15')
    ax.add_patch(rect)
    ax.text(x, 3.4, title, ha='center', fontsize=15, weight='bold', color=color)
    ax.text(x, 3.0, axis_label, ha='center', fontsize=10, color='#555',
            style='italic')
    ax.text(x, 2.0, desc, ha='center', fontsize=10, color='#333')

# 트라이앵귤레이션 화살표
for x1, x2 in [(3.6, 4.4), (7.6, 8.4)]:
    arrow = FancyArrowPatch((x1, 2.3), (x2, 2.3),
                             arrowstyle='<->', mutation_scale=14,
                             linewidth=1, color='#999')
    ax.add_patch(arrow)

ax.text(6.0, 0.35,
        '트라이앵귤레이션 — 합의가 아니라 상호 보완. 세 도구가 같은 미궁을 다른 각도로.',
        ha='center', fontsize=11.5, color='#555', style='italic')

ax.set_title('렌즈 3 — 세 렌즈의 정렬', fontsize=13, pad=10)
plt.tight_layout()
out26 = out_dir / 'fig_slide26_3lens_cards.png'
plt.savefig(out26, dpi=140, bbox_inches='tight', facecolor='white')
plt.close()
print(f'[Slide 26] {out26}')

# ──────────────────────────────────────────────────────────────────────
# Slide 32 — 14분야 outcome 상관 강도 (분산 노출)
# ──────────────────────────────────────────────────────────────────────
h10 = pd.read_csv('data/results/H10_v3_alt_correlations.csv')

# 분야별 |pearson_r| 평균 (outcome 영향 강도)
abs_by_field = (h10.groupby('field')['pearson_r']
                .apply(lambda x: x.abs().mean())
                .sort_values(ascending=False))

fig, ax = plt.subplots(figsize=(9.5, 6), dpi=140)
y = list(range(len(abs_by_field)))
colors_32 = ['#C0392B' if v >= 0.5 else ('#E67E22' if v >= 0.3 else '#888')
             for v in abs_by_field.values]
ax.barh(y, abs_by_field.values, color=colors_32, edgecolor='#444', linewidth=0.4)
# 값 라벨
for i, (field, val) in enumerate(abs_by_field.items()):
    ax.text(val + 0.01, i, f'{val:.2f}', va='center', fontsize=9.5,
            color='#333')
ax.set_yticks(y)
ax.set_yticklabels(abs_by_field.index, fontsize=10)
ax.invert_yaxis()
ax.set_xlabel('|outcome 상관| (분야별 평균, Pearson r 절댓값)', fontsize=11)
ax.set_title('14분야 outcome 상관 강도 — 결과는 약 8배 분산\n'
             '(빨강 ≥ 0.5 강함 · 주황 ≥ 0.3 중간 · 회색 < 0.3 약함)',
             fontsize=11.5, pad=10)
for s in ['top', 'right']:
    ax.spines[s].set_visible(False)
ax.grid(True, axis='x', alpha=0.25, linestyle=':')
plt.tight_layout()
out32 = out_dir / 'fig_slide32_outcome_sd.png'
plt.savefig(out32, dpi=140, bbox_inches='tight', facecolor='white')
plt.close()
print(f'[Slide 32] {out32}')

print('\n=== ALL 4 EXTRAS GENERATED ===')
