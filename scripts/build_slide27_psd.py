"""Slide 27 메인 차트 — 4 archetype × 6 freq bin 평균 PSD (슬라이드 강화 버전).

기존 redo_fig11_psd.py 대비 3가지 narrative 정합 개선:
  (a) y축 범위 0.35까지 확장 — 출연금형 12m spike(0.332) 완전 표시
  (b) archetype 색 통일 — Slide 22/23 패턴 (C0·C3 회색 / C1 빨강 / C2 주황)
  (c) 핵심 spike(3m·12m) annotation arrow + 분석 대상 line 굵게

paper 본문용은 redo_fig11_psd.py 유지 (논문 호환).
"""
import os, sys, io, warnings
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from pathlib import Path
from PIL import Image

warnings.filterwarnings('ignore')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

font_path = Path('paper/fonts/Pretendard-Regular.otf')
if font_path.exists():
    fm.fontManager.addfont(str(font_path))
    plt.rcParams['font.family'] = 'Pretendard'
plt.rcParams['axes.unicode_minus'] = False

ROOT = Path(__file__).resolve().parent.parent
psd_avg = pd.read_csv(ROOT / 'data' / 'results' / 'H27_psd_archetype_avg.csv')

# Slide 22/23 색 코드와 통일
ARCH = {
    'C0_personnel':     dict(name='C0 인건비형 · 비교군',   color='#888888', role='비교군',   lw=1.8),
    'C1_direct_invest': dict(name='C1 자산취득형 · 분석 대상', color='#C0392B', role='분석',     lw=3.0),
    'C2_chooyeon':      dict(name='C2 출연금형 · 분석 대상',  color='#E67E22', role='분석',     lw=3.0),
    'C3_normal':        dict(name='C3 정상사업 · 비교군',    color='#9b9b9b', role='비교군',   lw=1.8),
}

fig, ax = plt.subplots(figsize=(11, 5.5), dpi=140)
freqs = list(range(7))
labels_freq = ['DC (k=0)', '12m', '6m', '4m', '3m·분기', '2.4m', '2m']

# DC(k=0) 제외, k=1~6만 plot
plot_order = ['C0_personnel', 'C3_normal', 'C1_direct_invest', 'C2_chooyeon']  # 비교군 먼저 그려 분석 대상이 위
for arch_key in plot_order:
    row = psd_avg[psd_avg['archetype'] == arch_key].iloc[0]
    vals = [row[f'psdnorm_k{k}'] for k in range(7)]
    cfg = ARCH[arch_key]
    ax.plot(freqs[1:], vals[1:], 'o-',
            label=cfg['name'], color=cfg['color'],
            linewidth=cfg['lw'], markersize=9,
            alpha=0.95 if cfg['role'] == '분석' else 0.7,
            zorder=5 if cfg['role'] == '분석' else 3)

# (a) y축 범위 확장 — 출연금형 12m=0.332 spike 완전 표시
ax.set_ylim(0.05, 0.36)
ax.set_xticks(freqs[1:])
ax.set_xticklabels(labels_freq[1:], fontsize=11.5)
ax.set_ylabel('정규화 PSD', fontsize=12)
ax.set_xlabel('주파수 빈 (주기)', fontsize=12)
ax.tick_params(axis='y', labelsize=11)

# (c) 핵심 spike annotation
# 출연금형 12m
chooyeon_12m = float(psd_avg[psd_avg['archetype']=='C2_chooyeon']['psdnorm_k1'].values[0])
ax.annotate(f'출연금형 12m = {chooyeon_12m:.3f}\n(연 주기 — 다른 원형 ×2)',
            xy=(1, chooyeon_12m), xytext=(1.4, 0.34),
            fontsize=11, color='#E67E22', weight='bold',
            ha='left',
            arrowprops=dict(arrowstyle='->', color='#E67E22', lw=1.6),
            bbox=dict(boxstyle='round,pad=0.4', fc='#fff5eb',
                      ec='#E67E22', linewidth=1.0))

# 분기 spike — 3 archetype 공통
qrt_vals = {a: psd_avg[psd_avg['archetype']==a]['psdnorm_k4'].values[0]
            for a in plot_order}
qrt_max = max(qrt_vals.values())
ax.annotate(f'분기(3m) ≈ {qrt_max:.2f}\n— 4 archetype 공통 spike',
            xy=(4, qrt_max), xytext=(4.3, 0.30),
            fontsize=11, color='#444', weight='bold',
            ha='left',
            arrowprops=dict(arrowstyle='->', color='#444', lw=1.5),
            bbox=dict(boxstyle='round,pad=0.4', fc='#f5f1e8',
                      ec='#888', linewidth=1.0))

# 차트 제목·부제
ax.set_title(
    'Slide 27. FFT — archetype마다 다른 맥박\n'
    '분기(3m) spike는 4 archetype 공통 · 연주기(12m) spike는 C2 출연금형에만',
    fontsize=12.5, pad=12, weight='bold', linespacing=1.4)
ax.title.set_multialignment('center')

# legend 외부 하단 4-칼럼
ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.14),
          ncol=4, frameon=False, fontsize=10.5,
          columnspacing=1.2, handletextpad=0.5)

for s in ['top', 'right']:
    ax.spines[s].set_visible(False)
ax.grid(True, axis='y', alpha=0.22, linestyle=':')

# footnote
fig.text(0.5, -0.02,
         '※ Welch PSD (k=1..6, 정규화) · 출처: data/results/H27_psd_archetype_avg.csv',
         ha='center', fontsize=8.5, color='#666', style='italic')

plt.tight_layout(rect=[0, 0.03, 1, 0.94])
out = ROOT / 'paper' / 'figures' / 'h27_psd.png'
plt.savefig(out, dpi=140, bbox_inches='tight', facecolor='white')
plt.close()

w, h = Image.open(out).size
print(f'저장: {out} | {w}x{h}px')
