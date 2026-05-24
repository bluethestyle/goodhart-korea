"""Slide 30 트라이앵귤레이션 heatmap — 4 archetype × 3 도구.

Slide 27/28/29의 KPI를 한 표에 정렬:
  FFT 12m PSD · Wavelet ×배 강화 · NeuralProphet seasonality strength

각 도구 행 내에서 max=1 정규화 (색 강도). 셀 텍스트는 raw 측정값.
출연금형 column이 일관 진한 색 → 트라이앵귤레이션 시각 증거.

출력: paper/figures/h30_triangulation.png  (1280 × ~ 550)
"""
import sys
import io
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.colors import LinearSegmentedColormap
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(__file__).resolve().parent.parent
font_path = ROOT / 'paper' / 'fonts' / 'Pretendard-Regular.otf'
if font_path.exists():
    fm.fontManager.addfont(str(font_path))
    plt.rcParams['font.family'] = 'Pretendard'
plt.rcParams['axes.unicode_minus'] = False

OUT_PATH = ROOT / 'paper' / 'figures' / 'h30_triangulation.png'

# ── 데이터 (Slide 27/28/29 KPI 통합) ────────────────────────────────
ARCHETYPES = ['C0\n인건비형', 'C1\n자산취득형', 'C2\n출연금형 ★', 'C3\n정상사업']
TOOLS = [
    'FFT\n12m PSD',
    'Wavelet\n시간 강화 (×배)',
    'NeuralProphet\nseasonality strength',
]
RAW = np.array([
    [0.097,  0.172,  0.332,  0.115],   # FFT
    [1.00,   2.75,   6.54,   4.17],    # Wavelet
    [0.274,  0.281,  0.458,  0.390],   # NP
])

# 셀 텍스트 형식
FMT = [
    '{:.3f}',     # FFT (소수 3)
    '×{:.2f}',    # Wavelet (×배)
    '{:.3f}',     # NP (소수 3)
]

# 각 행 max=1 정규화 → 색 강도
NORM = RAW / RAW.max(axis=1, keepdims=True)


# ── 색 scale: 출연금형 주황 강조 ────────────────────────────────────
cmap = LinearSegmentedColormap.from_list(
    'tri_orange',
    ['#FFFFFF', '#FCE9D2', '#F5BC78', '#E67E22', '#C0640F'],
    N=256,
)


# ──────────────────────────────────────────────────────────────────────
def main():
    fig, ax = plt.subplots(figsize=(12.8, 5.5), dpi=100,
                           gridspec_kw={'left': 0.18, 'right': 0.96,
                                        'top': 0.84, 'bottom': 0.12})

    # heatmap
    im = ax.imshow(NORM, aspect='auto', cmap=cmap, vmin=0, vmax=1)

    # 셀 텍스트
    for i in range(RAW.shape[0]):
        for j in range(RAW.shape[1]):
            v_raw = RAW[i, j]
            v_norm = NORM[i, j]
            text_color = '#FFFFFF' if v_norm > 0.55 else '#222222'
            weight = 'bold' if j == 2 else 'normal'  # 출연금형 column 굵게
            ax.text(j, i, FMT[i].format(v_raw),
                    ha='center', va='center', fontsize=18,
                    color=text_color, fontweight=weight)

    # 출연금형 column 강조 border
    from matplotlib.patches import Rectangle
    rect = Rectangle((1.5, -0.5), 1, 3, fill=False,
                     edgecolor='#C0392B', linewidth=3.0, zorder=10)
    ax.add_patch(rect)

    # 축 라벨
    ax.set_xticks(range(len(ARCHETYPES)))
    ax.set_xticklabels(ARCHETYPES, fontsize=13)
    ax.set_yticks(range(len(TOOLS)))
    ax.set_yticklabels(TOOLS, fontsize=12)

    # tick 스타일
    ax.tick_params(axis='x', length=0, pad=10)
    ax.tick_params(axis='y', length=0, pad=10)

    # 출연금형 x-tick label 색 강조
    xtick_labels = ax.get_xticklabels()
    xtick_labels[2].set_color('#C0392B')
    xtick_labels[2].set_fontweight('bold')

    # 격자
    ax.set_xticks(np.arange(-0.5, len(ARCHETYPES), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(TOOLS), 1), minor=True)
    ax.grid(which='minor', color='white', linewidth=3)
    ax.tick_params(which='minor', bottom=False, left=False)

    # spines off
    for spine in ax.spines.values():
        spine.set_visible(False)

    # title
    fig.suptitle(
        '세 도구가 4 체질에서 본 같은 박자 — 트라이앵귤레이션',
        fontsize=16, fontweight='bold', y=0.95,
    )
    ax.text(0.5, 1.04, '각 도구 행 내 max=1 정규화 (색 강도) · 셀 값은 실측',
            transform=ax.transAxes, ha='center', fontsize=10.5, color='#666')

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(OUT_PATH, dpi=100, facecolor='white')
    plt.close()

    from PIL import Image
    print(f'Saved: {OUT_PATH}')
    print(f'Size:  {Image.open(OUT_PATH).size}')

    # KPI 요약 출력
    print(f'\n=== KPI ===')
    print(f'  FFT 12m PSD       — 출연금형 0.332 (최강, C0 인건비형 0.097의 ×3.4)')
    print(f'  Wavelet 강화      — 출연금형 ×6.54 (최강, C0 ×1.00의 ×6.5)')
    print(f'  NP seasonality    — 출연금형 0.458 (최강, C0 0.274의 ×1.67)')


if __name__ == '__main__':
    main()
