"""Slide 33 — 14분야 × Sobel z 매개 분석 비교.

Slide 32 (outcome 상관 강도) 패턴 재사용 — 14분야 막대로 *"농림수산만 유의"* 시각 즉답.
기존 h14_quadrant (부처 단위)는 Slide 40 부처 layer로 이동.

데이터: data/results/H23_mediation_estimates.csv (14분야 Sobel z)
출력:   paper/figures/eda/fig_slide33_sobel_bars.png  (1280×800)
"""
import sys
import io
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(__file__).resolve().parent.parent
font_path = ROOT / 'paper' / 'fonts' / 'Pretendard-Regular.otf'
if font_path.exists():
    fm.fontManager.addfont(str(font_path))
    plt.rcParams['font.family'] = 'Pretendard'
plt.rcParams['axes.unicode_minus'] = False

DATA_PATH = ROOT / 'data' / 'results' / 'H23_mediation_estimates.csv'
OUT_PATH  = ROOT / 'paper' / 'figures' / 'eda' / 'fig_slide33_sobel_bars.png'

# ── 데이터 ───────────────────────────────────────────────────────────
df = pd.read_csv(DATA_PATH)

# 14분야만 (POOLED 제외, NA 제외)
df = df[df['fld_nm'] != 'POOLED (FE)'].copy()
df = df.dropna(subset=['sobel_z']).copy()

# |z| 큰 순 정렬
df['abs_z'] = df['sobel_z'].abs()
df = df.sort_values('abs_z', ascending=False).reset_index(drop=True)

print(f'14분야 Sobel z:')
for _, row in df.iterrows():
    sig = '★ 유의' if row['sobel_p'] < 0.01 else ('· p<0.05' if row['sobel_p'] < 0.05 else '')
    print(f"  {row['fld_nm']:<20} z={row['sobel_z']:+7.3f}  p={row['sobel_p']:.3f}  {sig}")

# ── 차트 ─────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(12.8, 8.0), dpi=100,
                       gridspec_kw={'left': 0.20, 'right': 0.96,
                                    'top': 0.86, 'bottom': 0.10})

# 색: 유의(p<0.01) 빨강, p<0.05 주황, 그 외 회색
def get_color(p):
    if p < 0.01: return '#C0392B'
    if p < 0.05: return '#E67E22'
    return '#999999'

colors = [get_color(p) for p in df['sobel_p']]

y = list(range(len(df)))
ax.barh(y, df['sobel_z'].values, color=colors, edgecolor='#444', linewidth=0.6)

# 값 라벨 (Sobel z + 유의 여부)
for i, row in df.iterrows():
    z = row['sobel_z']
    p = row['sobel_p']
    sig_mark = ' ★' if p < 0.01 else (' ·' if p < 0.05 else '')
    label = f'{z:+.2f}{sig_mark}'
    # 라벨 위치: 막대 끝 외부 (여유 더)
    x_pos = z + (0.18 if z >= 0 else -0.18)
    ha = 'left' if z >= 0 else 'right'
    color = '#C0392B' if p < 0.01 else '#333'
    weight = 'bold' if p < 0.01 else 'normal'
    fsize = 14 if p < 0.01 else 13
    ax.text(x_pos, i, label, va='center', ha=ha, fontsize=fsize,
            color=color, fontweight=weight)

ax.set_yticks(y)
ax.set_yticklabels(df['fld_nm'].values, fontsize=14)
ax.invert_yaxis()
ax.set_xlabel('Sobel z = ab / SE(ab)   (유의: |z| > 1.96, p < 0.05)', fontsize=13)

# 유의 임계선 ±1.96 점선
ax.axvline(0, color='#333', lw=0.8, zorder=2)
ax.axvline(-1.96, color='#888', lw=0.8, linestyle='--', alpha=0.6, zorder=1)
ax.axvline(1.96, color='#888', lw=0.8, linestyle='--', alpha=0.6, zorder=1)
ax.text(-1.96, -0.7, '−1.96', ha='center', fontsize=10, color='#666')
ax.text(1.96, -0.7, '+1.96', ha='center', fontsize=10, color='#666')

title_main = '14분야 매개 분석 — 농림수산만 유일하게 유의'
title_sub  = '빨강 p<0.01 (★ 매개 유의)  ·  주황 p<0.05  ·  회색 p≥0.05 (유의 미달)'
ax.set_title(title_main + '\n' + title_sub, fontsize=14, pad=14)

for s in ['top', 'right']:
    ax.spines[s].set_visible(False)
ax.grid(True, axis='x', alpha=0.25, linestyle=':')

# x 축 range — 라벨 외부 여유 충분히
zmin = min(df['sobel_z'].min(), -2.2)
zmax = max(df['sobel_z'].max(), 2.2)
ax.set_xlim(zmin - 0.9, zmax + 0.7)

OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(OUT_PATH, dpi=100, facecolor='white')
plt.close()

from PIL import Image
print(f'\nSaved: {OUT_PATH}')
print(f'Size:  {Image.open(OUT_PATH).size}')
