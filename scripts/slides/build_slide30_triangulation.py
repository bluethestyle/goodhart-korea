"""§6.5.3 트라이앵귤레이션 heatmap — 15분야 × 3도구 outcome 상관.

각 정책 분야의 outcome과 게임화 측도(FFT·STL·NeuralProphet) 셋의 *부호 있는* 상관을
15분야 × 3도구 매트릭스로 정리한다. 도구 간 *부호 일관* 분야와 *측도 의존* 분야가
시각적으로 분리되어, '합의'가 아닌 '상보적' 트라이앵귤레이션을 보인다.

값은 `data/results/H26_field_outcome_corr_np.csv`에서 직접 읽는다 (하드코딩 없음).
출력: paper/figures/h30_triangulation.png  (~1260 × ~1125)
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

ROOT = Path(__file__).resolve().parent.parent.parent
font_path = ROOT / 'paper' / 'fonts' / 'Pretendard-Regular.otf'
if font_path.exists():
    fm.fontManager.addfont(str(font_path))
    plt.rcParams['font.family'] = 'Pretendard'
plt.rcParams['axes.unicode_minus'] = False

SRC = ROOT / 'data' / 'results' / 'H26_field_outcome_corr_np.csv'
OUT_PATH = ROOT / 'paper' / 'figures' / 'h30_triangulation.png'

# 분야명 축약 (표시용)
SHORT = {
    '산업·중소기업및에너지': '산업·중기',
    '국토및지역개발': '국토·지역',
    '문화및관광': '문화·관광',
    '공공질서및안전': '공공질서',
    '교통및물류': '교통·물류',
    '일반·지방행정': '일반·지방',
    '통일·외교': '통일·외교',
}

TOOLS = ['FFT\n(amp 12m)', 'STL\n(계절강도)', 'NeuralProphet\n(seasonality)']
COLS = ['corr_fft', 'corr_stl', 'corr_np']


def main():
    df = pd.read_csv(SRC)
    # FFT 상관 오름차순 정렬 (가장 강한 음 신호 = 측정 적응 위)
    df = df.sort_values('corr_fft').reset_index(drop=True)

    fields = [SHORT.get(f, f) for f in df['fld']]
    M = df[COLS].to_numpy(dtype=float)  # (15, 3)

    n_row = len(fields)
    fig, ax = plt.subplots(figsize=(8.4, 7.5), dpi=150,
                           gridspec_kw={'left': 0.14, 'right': 0.97,
                                        'top': 0.88, 'bottom': 0.10})

    # 발산 색지도: 음(파랑) ↔ 0(흰) ↔ 양(빨강), 0 중심
    vlim = 0.8
    im = ax.imshow(M, aspect='auto', cmap='RdBu_r', vmin=-vlim, vmax=vlim)

    # 셀 값 annotation
    for i in range(n_row):
        for j in range(3):
            v = M[i, j]
            tc = '#ffffff' if abs(v) > 0.5 else '#1a1a1a'
            ax.text(j, i, f'{v:+.2f}', ha='center', va='center',
                    fontsize=11.5, color=tc)

    # 축
    ax.set_xticks(range(3))
    ax.set_xticklabels(TOOLS, fontsize=11.5)
    ax.set_yticks(range(n_row))
    ax.set_yticklabels(fields, fontsize=11)
    ax.tick_params(axis='x', length=0, pad=8)
    ax.tick_params(axis='y', length=0, pad=6)

    # 흰 격자
    ax.set_xticks(np.arange(-0.5, 3, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, n_row, 1), minor=True)
    ax.grid(which='minor', color='white', linewidth=2)
    ax.tick_params(which='minor', bottom=False, left=False)
    for spine in ax.spines.values():
        spine.set_visible(False)

    # 컬러바
    cbar = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.03)
    cbar.set_label('시점집중 ↔ outcome 상관 계수', fontsize=10)
    cbar.ax.tick_params(labelsize=9)

    fig.suptitle('세 도구가 본 분야별 outcome 상관 — 부호 일관 vs 측도 의존',
                 fontsize=15, fontweight='bold', y=0.965)
    ax.text(0.5, 1.025,
            '음(파랑)=시점집중↔outcome 악화 · 도구 간 부호 갈림 = 측도 의존(상보적 트라이앵귤레이션)',
            transform=ax.transAxes, ha='center', fontsize=9.5, color='#666')

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(OUT_PATH, dpi=150, facecolor='white')
    plt.close()

    from PIL import Image
    sz = Image.open(OUT_PATH).size
    print(f'Saved: {OUT_PATH}')
    print(f'Size:  {sz}')
    print(f'분야 수: {n_row} (H26 CSV)')
    # 검증 출력
    for f in ['보건', '통신', '사회복지']:
        r = df[df['fld'] == f]
        if len(r):
            print(f'  {f}: FFT {r.corr_fft.values[0]:+.2f} / STL {r.corr_stl.values[0]:+.2f} / NP {r.corr_np.values[0]:+.2f}')


if __name__ == '__main__':
    main()
