"""Slide 32 — 14분야 outcome 상관 강도 (Output vs Outcome narrative).

기존 build_slide_extras.py에서 분리. 변경 사항:
- title 라벨: "결과는 약 8배 분산" → "분야 간 약 36배 차이 (0.02 ~ 0.73)"
  (실측 max 0.73 / min 0.02 → 약 36배, 메모리의 약 8배는 정확치 않음)
- 사이즈: 1280 이하 가드 (figsize=12.8×8 dpi=100 = 1280×800)
- bbox_inches=None — 사이즈 정확히 유지

데이터: data/results/H10_v3_alt_correlations.csv (분야별 pearson_r)
출력:   paper/figures/eda/fig_slide32_outcome_sd.png  (1280×800)
"""
import sys
import io
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(__file__).resolve().parent.parent.parent
font_path = ROOT / 'paper' / 'fonts' / 'Pretendard-Regular.otf'
if font_path.exists():
    fm.fontManager.addfont(str(font_path))
    plt.rcParams['font.family'] = 'Pretendard'
plt.rcParams['axes.unicode_minus'] = False

DATA_PATH = ROOT / 'data' / 'results' / 'H10_v3_alt_correlations.csv'
OUT_PATH  = ROOT / 'paper' / 'figures' / 'eda' / 'fig_slide32_outcome_sd.png'

# ── 데이터 ───────────────────────────────────────────────────────────
h10 = pd.read_csv(DATA_PATH)
abs_by_field = (h10.groupby('field')['pearson_r']
                .apply(lambda x: x.abs().mean())
                .sort_values(ascending=False))

vmax = abs_by_field.max()
vmin = abs_by_field.min()
ratio = vmax / vmin if vmin > 0 else float('inf')
print(f'분야별 |outcome 상관| 평균:')
print(abs_by_field)
print(f'\nmax {vmax:.3f} ({abs_by_field.idxmax()}) / min {vmin:.3f} ({abs_by_field.idxmin()})')
print(f'분야 간 비율: ×{ratio:.1f}')

# ── 차트 ─────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(12.8, 8.0), dpi=100,
                       gridspec_kw={'left': 0.20, 'right': 0.96,
                                    'top': 0.86, 'bottom': 0.10})

y = list(range(len(abs_by_field)))
colors = ['#C0392B' if v >= 0.5 else ('#E67E22' if v >= 0.3 else '#888')
          for v in abs_by_field.values]
ax.barh(y, abs_by_field.values, color=colors, edgecolor='#444', linewidth=0.6)

# 값 라벨
for i, (field, val) in enumerate(abs_by_field.items()):
    ax.text(val + 0.012, i, f'{val:.2f}', va='center', fontsize=13,
            color='#222')

ax.set_yticks(y)
ax.set_yticklabels(abs_by_field.index, fontsize=14)
ax.invert_yaxis()
ax.set_xlabel('|outcome 상관| (분야별 평균, Pearson r 절댓값)', fontsize=13)

title_main = f'14분야 outcome 상관 강도 — 분야 간 약 {ratio:.0f}배 차이 ({vmin:.2f} ~ {vmax:.2f})'
title_sub  = '빨강 ≥ 0.5 강함 · 주황 ≥ 0.3 중간 · 회색 < 0.3 약함'
ax.set_title(title_main + '\n' + title_sub, fontsize=14, pad=14)

for s in ['top', 'right']:
    ax.spines[s].set_visible(False)
ax.grid(True, axis='x', alpha=0.25, linestyle=':')
ax.set_xlim(0, vmax * 1.12)

OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(OUT_PATH, dpi=100, facecolor='white')
plt.close()

from PIL import Image
print(f'\nSaved: {OUT_PATH}')
print(f'Size:  {Image.open(OUT_PATH).size}')
