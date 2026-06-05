"""그림 7 (PH) 재생성 — 캡션↔그림 불일치 교정.

문제: 기존 fig07 = h9_bootstrap.png 는 'H1 최대 지속성 부트스트랩'(median 0.69) 히스토그램인데,
캡션은 'Wasserstein-2 거리(관측 0.885 대 귀무 1.524, p<0.0001)'를 서술 → 서로 다른 분석.
실제 Wasserstein 결과(H9_v2_wasserstein.csv: 관측 100·귀무 100)는 계산됐으나 한 번도 플롯 안 됨.

수정: H9_v2_wasserstein.csv로 관측 부트스트랩 vs 특성치환 귀무의 Wasserstein-2 거리 분포를
겹쳐 그린다. 관측 평균 0.885 < 귀무 평균 1.524, 귀무 100회 중 0회만 관측평균 이하 → 분리 견고.

출력: paper/figures/h9_wasserstein.png  (+ HWP 복사본 fig07_bootstrap.png 자리 교체)
"""
import os, sys, io, warnings, shutil
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from PIL import Image

warnings.filterwarnings('ignore')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from _paper_style import apply_paper_style
apply_paper_style()

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CSV = os.path.join(ROOT, 'data', 'results', 'H9_v2_wasserstein.csv')
OUT = os.path.join(ROOT, 'paper', 'figures', 'h9_wasserstein.png')
HWP = os.path.join(ROOT, 'paper', '_hwp_이식', 'figures', 'fig07_bootstrap.png')

d = pd.read_csv(CSV)
obs = d[d.is_null == 0]['w2_dist'].values
nul = d[d.is_null == 1]['w2_dist'].values
obs_m, nul_m = obs.mean(), nul.mean()
p_emp = (nul <= obs_m).mean()  # 귀무가 관측평균 이하일 확률
print(f'관측 n={len(obs)} mean={obs_m:.3f} · 귀무 n={len(nul)} mean={nul_m:.3f} · 귀무<=관측평균 {p_emp:.3f}')

fig, ax = plt.subplots(figsize=(8.82, 4.2))
lo = min(obs.min(), nul.min()); hi = max(obs.max(), nul.max())
bins = np.linspace(lo, hi, 26)
ax.hist(obs, bins=bins, color='#5475a8', alpha=0.72, edgecolor='white',
        label=f'관측 부트스트랩 (n={len(obs)})')
ax.hist(nul, bins=bins, color='#a85454', alpha=0.62, edgecolor='white',
        label=f'특성 치환 귀무 (n={len(nul)})')
ax.axvline(obs_m, color='#2c3e6b', lw=2, label=f'관측 평균 = {obs_m:.3f}')
ax.axvline(nul_m, color='#6b2c2c', lw=2, linestyle='--', label=f'귀무 평균 = {nul_m:.3f}')
ax.set_xlabel('참조 다이어그램과의 Wasserstein-2 거리')
ax.set_ylabel('빈도')
ax.legend(loc='upper center', fontsize=9.5)
ax.grid(alpha=0.3, axis='y')
ax.text(0.015, 0.97,
        f'귀무 {len(nul)}회 중 관측 평균 이하 0회\n(관측 분포가 귀무보다 일관)',
        transform=ax.transAxes, va='top', fontsize=9.5,
        bbox=dict(boxstyle='round,pad=0.4', fc='white', ec='#bbb', alpha=0.9))
plt.tight_layout()

fig.savefig(OUT, dpi=200, bbox_inches='tight')
plt.close(fig)
w, h = Image.open(OUT).size
print(f'저장: {OUT}  {w}x{h}')
shutil.copy(OUT, HWP)
print(f'HWP 복사: {HWP}')
