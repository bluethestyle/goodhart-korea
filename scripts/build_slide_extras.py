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
# Slide 22 — cutoff 4 막대
# ──────────────────────────────────────────────────────────────────────
cutoffs = ['3월/2월', '6월/5월', '9월/8월', '12월/11월']
betas = [0.17, 0.36, 0.22, 0.65]
ratios = [1.18, 1.44, 1.24, 1.97]
colors_22 = ['#888888', '#888888', '#888888', '#C0392B']

fig, ax = plt.subplots(figsize=(7.5, 4.8), dpi=140)
bars = ax.bar(cutoffs, ratios, color=colors_22, edgecolor='#444', linewidth=0.5)
ax.axhline(1.0, color='#666', linewidth=0.8, linestyle=':')
ax.text(3.4, 1.03, '× 1.0 (점프 없음)', fontsize=8.5, color='#666', ha='right')
for bar, r, b in zip(bars, ratios, betas):
    is_max = r > 1.5
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.04,
            f'× {r:.2f}\nβ={b:.2f}',
            ha='center', fontsize=11,
            weight='bold' if is_max else 'normal',
            color='#C0392B' if is_max else '#333')
ax.set_ylim(0, max(ratios) * 1.22)
ax.set_ylabel('일평균 집행 점프 배율 (e^β)', fontsize=11)
ax.set_xlabel('cutoff (전월 대비)', fontsize=11)
ax.set_title('분기말 cutoff별 RDD 점프 — 12월이 최대 (n=18,348 활동×연도)',
             fontsize=12, pad=10)
for s in ['top', 'right']:
    ax.spines[s].set_visible(False)
ax.grid(True, axis='y', alpha=0.25, linestyle=':')
plt.tight_layout()
out22 = out_dir / 'fig_slide22_cutoff_bars.png'
plt.savefig(out22, dpi=140, bbox_inches='tight', facecolor='white')
plt.close()
print(f'[Slide 22] {out22}')

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
