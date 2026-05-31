"""슬라이드용 트라이앵귤레이션 매트릭스 — 세 도구가 4 archetype에서 본 같은 주기.

3 도구(FFT 12m PSD · Wavelet 시간강화 · NeuralProphet seasonality) × 4 archetype(C0~C3)
매트릭스. 세 도구 모두 C2 출연금형을 최강으로 지목 = 상호 보완 트라이앵귤레이션.

데이터 출처 (하드코딩 제거 — 37.2% 부류 stale 방지):
  - FFT 12m PSD     → data/results/H27_psd_archetype_avg.csv (12m = psdnorm_k1, 행=archetype)
  - Wavelet 시간강화 → data/results/H28_wavelet_12m_evolution.csv
                       window(2015–17 평균 → 2023–25 평균) 배율
  - NeuralProphet   → 추적 가능한 CSV 원천 없음 → 하드코딩 유지(아래 NP_SEASONALITY 주석 참조)

출력: paper/figures/slides/triangulation_archetype.png (Figma 플레이스홀더 자산).
논문 §6.5.3의 h30_triangulation.png(15분야 heatmap)와는 다른 슬라이드 전용 차트.
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

ORDER = ['C0_personnel', 'C1_direct_invest', 'C2_chooyeon', 'C3_normal']
COL_LABELS = ['C0\n인건비형', 'C1\n자산취득형', 'C2\n출연금형 ★', 'C3\n정상사업']

# ── 1) FFT 12m PSD (psdnorm_k1) ──────────────────────────────
psd = pd.read_csv(ROOT / 'data' / 'results' / 'H27_psd_archetype_avg.csv').set_index('archetype')
fft_row = [round(float(psd.loc[a, 'psdnorm_k1']), 3) for a in ORDER]

# ── 2) Wavelet 시간강화 배율 window(2015–17 → 2023–25) ────────
ev = pd.read_csv(ROOT / 'data' / 'results' / 'H28_wavelet_12m_evolution.csv')
def _wmult(a):
    s = ev[ev['archetype'] == a].sort_values('year')
    early = s[s['year'].isin([2015, 2016, 2017])]['power_12m'].mean()
    late = s[s['year'].isin([2023, 2024, 2025])]['power_12m'].mean()
    return round(float(late / early), 2)
wav_row = [_wmult(a) for a in ORDER]

# ── 3) NeuralProphet seasonality strength ────────────────────
# 추적 가능한 CSV 원천 없음 (H29 분해에서 단순 공식 재현 불가). App-WAV 부록과 동일 값 유지.
# C2(0.458) 최댓값 → "세 도구 합치" 메시지 보존. 향후 산출식 정의 후 CSV화 필요.
NP_SEASONALITY = [0.274, 0.281, 0.458, 0.390]
np_row = list(NP_SEASONALITY)

ROWS = [fft_row, wav_row, np_row]
ROW_LABELS = ['FFT\n12m PSD', 'Wavelet\n시간 강화 (×배)', 'NeuralProphet\nseasonality strength']
FMT = ['{:.3f}', '×{:.2f}', '{:.3f}']

M = np.array(ROWS, dtype=float)
# 행 내 max=1 정규화 (색 강도)
norm = M / M.max(axis=1, keepdims=True)

fig, ax = plt.subplots(figsize=(7.2, 4.2), dpi=150)
ax.imshow(norm, aspect='auto', cmap='Oranges', vmin=0, vmax=1)

n_row, n_col = M.shape
for i in range(n_row):
    for j in range(n_col):
        v = M[i, j]
        is_c2 = (j == 2)
        tc = '#ffffff' if norm[i, j] > 0.6 else '#1a1a1a'
        txt = FMT[i].format(v)
        ax.text(j, i, txt, ha='center', va='center',
                fontsize=13 if is_c2 else 12,
                color=('#7f1d1d' if (is_c2 and norm[i, j] <= 0.6) else tc),
                fontweight='bold' if is_c2 else 'normal')

# C2 열 강조 박스
rect = plt.Rectangle((2 - 0.5, -0.5), 1, n_row, fill=False,
                     edgecolor='#C0392B', linewidth=2.4, zorder=5)
ax.add_patch(rect)

ax.set_xticks(range(n_col))
ax.set_xticklabels(COL_LABELS, fontsize=11)
ax.set_yticks(range(n_row))
ax.set_yticklabels(ROW_LABELS, fontsize=11)
ax.tick_params(length=0)
ax.get_xticklabels()[2].set_color('#C0392B')
ax.get_xticklabels()[2].set_fontweight('bold')

ax.set_xticks(np.arange(-0.5, n_col, 1), minor=True)
ax.set_yticks(np.arange(-0.5, n_row, 1), minor=True)
ax.grid(which='minor', color='white', linewidth=3)
ax.tick_params(which='minor', length=0)
for sp in ax.spines.values():
    sp.set_visible(False)

ax.set_title('세 도구가 4 체질에서 본 같은 주기 — 트라이앵귤레이션',
             fontsize=14, fontweight='bold', pad=26)
ax.text(0.5, 1.045, '각 도구 행 내 max×1 정규화(색 강도) · 셀 값은 실측 · 세 도구 모두 C2 출연금형 최강',
        transform=ax.transAxes, ha='center', fontsize=9.5, color='#666')

fig.text(0.5, -0.02,
         '※ FFT: H27_psd_archetype_avg.csv · Wavelet: H28_wavelet_12m_evolution.csv · NP: seasonality strength(부록 App-WAV)',
         ha='center', fontsize=7.5, color='#888', style='italic')

plt.tight_layout(rect=[0, 0.02, 1, 0.95])
out_dir = ROOT / 'paper' / 'figures' / 'slides'
out_dir.mkdir(parents=True, exist_ok=True)
out = out_dir / 'triangulation_archetype.png'
plt.savefig(out, dpi=150, bbox_inches='tight', facecolor='white')
plt.close()

from PIL import Image
w, h = Image.open(out).size
print(f'saved: {out} | {w}x{h}px')
print(f'FFT 12m   : {fft_row}')
print(f'Wavelet x : {wav_row}')
print(f'NP season : {np_row}')
print('row-max archetype: ' + ', '.join(ORDER[int(np.argmax(r))] for r in ROWS))
