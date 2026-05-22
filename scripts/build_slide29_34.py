"""Slide 29 NP 분해 도식 + Slide 34 농림수산 12월 시계열.

Slide 29: NP trend + yearly seasonality 분해 *개념도* (합성 데이터).
실제 plotly interactive viz는 main_v2 link.

Slide 34: 농림수산 분야 12월 집행 비중 11년 시계열 (실데이터).
"""
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import duckdb
from pathlib import Path
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
# Slide 29 — NP 분해 개념도 (trend + yearly seasonality)
# ──────────────────────────────────────────────────────────────────────
np.random.seed(42)
t = np.arange(132)  # 11년 × 12개월
trend = 100 + t * 0.5  # 자연 증가
seasonal = 30 * np.sin(2 * np.pi * t / 12 - np.pi / 2)  # 연 사이클 (12월 정점)
noise = np.random.normal(0, 5, 132)
y_raw = trend + seasonal + noise

fig, axes = plt.subplots(3, 1, figsize=(10, 7), dpi=140, sharex=True)

axes[0].plot(t, y_raw, color='#444', linewidth=1.2)
axes[0].set_title('원시 시계열 (자연 증가 추세 + 연 사이클 + 노이즈)',
                  fontsize=11, loc='left')
axes[0].set_ylabel('집행액', fontsize=10)
axes[0].grid(True, alpha=0.25, linestyle=':')

axes[1].plot(t, trend, color='#3498db', linewidth=2.2)
axes[1].set_title('Trend component — 자연 증가 추세 (제거 대상)',
                  fontsize=11, color='#3498db', loc='left')
axes[1].set_ylabel('Trend', fontsize=10)
axes[1].grid(True, alpha=0.25, linestyle=':')

axes[2].plot(t, seasonal, color='#C0392B', linewidth=2.2)
axes[2].axhline(0, color='#666', linewidth=0.5, linestyle='--')
axes[2].set_title('Yearly Seasonality — 추세 제거 후 잔존 (본 분석 관심)',
                  fontsize=11, color='#C0392B', loc='left')
axes[2].set_ylabel('Seasonality', fontsize=10)
axes[2].set_xlabel('월 (2015 → 2025, 11년 × 12 = 132)', fontsize=10)
axes[2].grid(True, alpha=0.25, linestyle=':')

for ax in axes:
    for s in ['top', 'right']:
        ax.spines[s].set_visible(False)

fig.suptitle('NeuralProphet 분해 개념도 — y(t) = T(t) + S(t) + ε',
             fontsize=12.5, y=1.005)

# 합성 데이터 footnote
fig.text(0.99, -0.02,
         '※ 개념 설명용 합성 데이터. 실제 4 archetype의 NP component 분해는 '
         'main_v2 interactive viz #5 (plotly) 참조.',
         ha='right', fontsize=8, color='#888', style='italic')

plt.tight_layout()
out29 = out_dir / 'fig_slide29_np_decomposition.png'
plt.savefig(out29, dpi=140, bbox_inches='tight', facecolor='white')
plt.close()
print(f'[Slide 29] {out29}')

# ──────────────────────────────────────────────────────────────────────
# Slide 34 — 농림수산 12월 비중 11년 시계열
# ──────────────────────────────────────────────────────────────────────
con = duckdb.connect('data/warehouse.duckdb', read_only=True)
q = """
SELECT FSCL_YY,
       SUM(EP_AMT) AS annual,
       SUM(CASE WHEN EXE_M=12 THEN EP_AMT ELSE 0 END) AS dec_exec,
       SUM(CASE WHEN EXE_M IN (3,6,9,12) THEN EP_AMT ELSE 0 END) AS qtr_exec
FROM monthly_exec
WHERE FLD_NM = '농림수산' AND FSCL_YY BETWEEN 2015 AND 2025
GROUP BY 1 ORDER BY 1
"""
df = con.execute(q).fetchdf()
df['dec_pct'] = df['dec_exec'] / df['annual'] * 100
df['qtr_pct'] = df['qtr_exec'] / df['annual'] * 100

fig, ax = plt.subplots(figsize=(10, 5.5), dpi=140)

# 12월 비중 line (메인)
ax.plot(df['FSCL_YY'], df['dec_pct'], marker='o', markersize=11,
        linewidth=2.6, color='#C0392B', label='12월 비중 (메인)', zorder=3)
# 분기말 비중 line (보조)
ax.plot(df['FSCL_YY'], df['qtr_pct'], marker='s', markersize=8,
        linewidth=1.8, color='#888', label='분기말 (3·6·9·12월) 합', alpha=0.7,
        zorder=2)

ax.axhline(8.3, color='#666', linestyle='--', linewidth=1, zorder=1)
ax.text(2015.2, 8.6, '균등 가정 8.3%', fontsize=9, color='#666')

# 12월 값 라벨
for x, y in zip(df['FSCL_YY'], df['dec_pct']):
    ax.annotate(f'{y:.1f}%', (x, y),
                textcoords='offset points', xytext=(0, 12),
                ha='center', fontsize=9.5, color='#C0392B', weight='bold')

ax.set_xlabel('연도', fontsize=11)
ax.set_ylabel('농림수산 분야 집행 비중 (%)', fontsize=11)
ax.set_title('농림수산 분야 12월 집중 시계열 — 농가소득 매개 anchor (Sobel z=−2.897)\n'
             '농어업재해보험재보험금(12월 31.3%·App-A 5위) 등 사업이 매개 경로의 핵심',
             fontsize=11.5, pad=10)
ax.legend(loc='upper right', fontsize=10, framealpha=0.9)
ax.grid(True, alpha=0.25, linestyle=':')
for s in ['top', 'right']:
    ax.spines[s].set_visible(False)

# narrative footnote
fig.text(0.5, -0.02,
         '※ 매개 경로: 12월 집중 → 시점 압력(archetype) → 농가소득. '
         'Slide 33 결정 카드와 직접 연결.',
         ha='center', fontsize=9, color='#666', style='italic')

plt.tight_layout()
out34 = out_dir / 'fig_slide34_agri_dec_timeline.png'
plt.savefig(out34, dpi=140, bbox_inches='tight', facecolor='white')
plt.close()
print(f'[Slide 34] {out34}')
print(df.to_string(index=False))
