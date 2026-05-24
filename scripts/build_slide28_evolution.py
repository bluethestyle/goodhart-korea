"""Slide 28 좌측 차트 — 12m cycle 11년 진화 (슬라이드 강화).

기존 redo_fig15_evolution.py 대비 narrative 정합 개선:
  (a) archetype 색 통일 — Slide 22/23/27 패턴 (C0·C3 회색·C1 빨강·C2 주황)
  (b) 분석 대상(C1·C2) line 굵게 + 비교군 얇고 흐리게
  (c) KPI 박스 위치 조정 — 출연금형 spike와 시각 충돌 회피
  (d) legend 라벨에 분석 대상/비교군 명시
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
ev = pd.read_csv(ROOT / 'data' / 'results' / 'H28_wavelet_12m_evolution.csv')

ARCH = {
    'C0_personnel':     dict(name='C0 인건비형 · 비교군',   color='#888888', lw=1.8, alpha=0.6, zorder=3),
    'C1_direct_invest': dict(name='C1 자산취득형 · 분석 대상', color='#C0392B', lw=2.8, alpha=0.95, zorder=5),
    'C2_chooyeon':      dict(name='C2 출연금형 · 분석 대상',  color='#E67E22', lw=3.2, alpha=0.98, zorder=6),
    'C3_normal':        dict(name='C3 정상사업 · 비교군',    color='#9b9b9b', lw=1.8, alpha=0.7, zorder=4),
}

fig, ax = plt.subplots(figsize=(10, 5.5), dpi=140)
plot_order = ['C0_personnel', 'C3_normal', 'C1_direct_invest', 'C2_chooyeon']

for arch in plot_order:
    sub = ev[ev['archetype'] == arch].sort_values('year')
    if len(sub) == 0:
        continue
    cfg = ARCH[arch]
    ax.plot(sub['year'], sub['power_12m'], 'o-',
            lw=cfg['lw'], markersize=7,
            color=cfg['color'], label=cfg['name'],
            alpha=cfg['alpha'], zorder=cfg['zorder'])

ax.set_xlabel('연도', fontsize=12)
ax.set_ylabel('12m cycle wavelet power', fontsize=12)
ax.grid(alpha=0.25, linestyle=':')

ymax_data = ev['power_12m'].max()
ax.set_ylim(-0.05, ymax_data * 1.18)

# (c) KPI 박스를 좌상단으로 이동 — 출연금형 spike 끝(우상단)과 시각 충돌 회피
ax.text(0.02, 0.97,
        '12m cycle power 강화  (2015–2017  →  2023–2025)\n'
        '\n'
        'C2 출연금형     +554%   ★ Act 4 결정\n'
        'C3 정상사업     +317%\n'
        'C1 자산취득형   +175%\n'
        'C0 인건비형     −0.8%   (null 검증)',
        transform=ax.transAxes, ha='left', va='top', fontsize=10.5,
        bbox=dict(boxstyle='round,pad=0.55', fc='#fff8e1',
                  ec='#daa520', linewidth=1.2, alpha=0.95))

# 출연금형 spike에 직접 annotation
peak_row = ev[(ev['archetype']=='C2_chooyeon') &
              (ev['year']==2024)].iloc[0] if len(ev[(ev['archetype']=='C2_chooyeon') & (ev['year']==2024)])>0 \
    else ev[ev['archetype']=='C2_chooyeon'].sort_values('power_12m').iloc[-1]
ax.annotate(f'C2 출연금형\n11년 +554%',
            xy=(peak_row['year'], peak_row['power_12m']),
            xytext=(peak_row['year']-1.5, peak_row['power_12m']+0.15),
            fontsize=10.5, color='#E67E22', weight='bold',
            ha='center',
            arrowprops=dict(arrowstyle='->', color='#E67E22', lw=1.6))

ax.set_title(
    'Slide 28 (좌). Wavelet 12m cycle 11년 진화 — C2 출연금형만 폭발적 강화\n'
    'C0 인건비형(통제) null = 거시 trend 아닌 archetype-specific 효과',
    fontsize=11.5, pad=12, weight='bold', linespacing=1.4)
ax.title.set_multialignment('center')

ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.13),
          ncol=4, frameon=False, fontsize=10,
          columnspacing=1.2, handletextpad=0.5)

for s in ['top', 'right']:
    ax.spines[s].set_visible(False)

fig.text(0.5, -0.02,
         '※ 출처: data/results/H28_wavelet_12m_evolution.csv · pywt CWT (cmor1.5-1.0)',
         ha='center', fontsize=8.5, color='#666', style='italic')

plt.tight_layout(rect=[0, 0.03, 1, 0.93])
out = ROOT / 'paper' / 'figures' / 'h28_evolution.png'
plt.savefig(out, dpi=140, bbox_inches='tight', facecolor='white')
plt.close()

w, h = Image.open(out).size
print(f'저장: {out} | {w}x{h}px')
