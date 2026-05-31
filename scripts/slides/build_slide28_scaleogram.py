"""Slide 28 우측 차트 — 4 archetype wavelet scaleogram (슬라이드 강화).

기존 redo_fig14_scaleogram.py 대비 개선:
  (a) 사이즈 슬라이드 친화 — 약 1500×800 (1280 한계 근처, 1900에서 줄임)
  (b) panel title 색·border 색 = archetype 정체성 (Slide 22/23/27 매칭)
  (c) panel 배치 — C2가 좌상(가장 강한 spike) → narrative flow
  (d) panel별 vmax 유지 (내부 패턴 보존) + max power title 강조
  (e) 분석 대상/비교군 라벨 추가
"""
import os, sys, io, warnings
import numpy as np
import pandas as pd
import duckdb
import pywt
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

ROOT = Path(__file__).resolve().parent.parent.parent
DB = ROOT / 'data' / 'warehouse.duckdb'
RES = ROOT / 'data' / 'results'

ARCH = {
    'C0_personnel':     dict(name='C0 인건비형', role='비교군',   color='#888888'),
    'C1_direct_invest': dict(name='C1 자산취득형', role='분석 대상', color='#C0392B'),
    'C2_chooyeon':      dict(name='C2 출연금형',  role='분석 대상', color='#E67E22'),
    'C3_normal':        dict(name='C3 정상사업',  role='비교군',   color='#9b9b9b'),
}
ARCHETYPE_MAP = {0: 'C0_personnel', 1: 'C1_direct_invest',
                 2: 'C2_chooyeon', 3: 'C3_normal'}

emb = pd.read_csv(RES / 'H3_activity_embedding_11y.csv')
emb['archetype'] = emb['cluster'].map(ARCHETYPE_MAP)

PURE_ACCT = (
    "(ACTV_NM ILIKE '%전출금%' OR ACTV_NM ILIKE '%타계정%' "
    "OR ACTV_NM ILIKE '%여유자금%' OR ACTV_NM ILIKE '%국고예탁%' "
    "OR ACTV_NM ILIKE '%기금예탁%' OR ACTV_NM ILIKE '%국고예치%' "
    "OR ACTV_NM ILIKE '%회계간거래%' OR ACTV_NM ILIKE '%회계간전출%')"
)
con = duckdb.connect(str(DB), read_only=True)
raw = con.execute(f"""
    SELECT FLD_NM, OFFC_NM, PGM_NM, ACTV_NM, FSCL_YY AS year, EXE_M AS month,
           SUM(EP_AMT) AS amt
    FROM monthly_exec
    WHERE EXE_M BETWEEN 1 AND 12 AND FSCL_YY BETWEEN 2015 AND 2025
      AND NOT {PURE_ACCT}
    GROUP BY 1,2,3,4,5,6
""").fetchdf()
con.close()

raw_keyed = raw.merge(
    emb[['FLD_NM', 'OFFC_NM', 'PGM_NM', 'ACTV_NM', 'archetype']],
    on=['FLD_NM', 'OFFC_NM', 'PGM_NM', 'ACTV_NM'])
raw_keyed['date'] = pd.to_datetime(
    raw_keyed['year'].astype(str) + '-' +
    raw_keyed['month'].astype(str).str.zfill(2) + '-01')
raw_keyed['act_year_key'] = list(zip(
    raw_keyed['FLD_NM'], raw_keyed['OFFC_NM'],
    raw_keyed['PGM_NM'], raw_keyed['ACTV_NM'], raw_keyed['year']))
ann_mean = raw_keyed.groupby('act_year_key')['amt'].transform('mean')
raw_keyed['amt_norm'] = raw_keyed['amt'] / ann_mean.replace(0, np.nan)

panel = (raw_keyed.dropna(subset=['amt_norm', 'archetype'])
         .groupby(['archetype', 'date'])['amt_norm'].mean()
         .reset_index()
         .pivot(index='date', columns='archetype', values='amt_norm')
         .fillna(0).sort_index())

scales = np.arange(2, 40)
wavelet = 'cmor1.5-1.0'
freqs = pywt.scale2frequency(wavelet, scales)
periods = 1 / freqs

# Panel 배치: C2(가장 강) 좌상 / C1 우상 / C0 좌하 / C3 우하 — narrative flow
panel_order = ['C2_chooyeon', 'C1_direct_invest', 'C0_personnel', 'C3_normal']

fig, axes = plt.subplots(2, 2, figsize=(12, 7), dpi=130,
                         sharex=True, sharey=True)
axes_flat = axes.flatten()

year_labels = pd.to_datetime(panel.index).year
year_ticks, year_tick_labels = [], []
for y in range(2015, 2026, 2):
    matches = np.where(year_labels == y)[0]
    if len(matches) > 0:
        year_ticks.append(matches[0])
        year_tick_labels.append(str(y))

powers, maxes = {}, {}
for arch in panel_order:
    if arch in panel.columns:
        signal = panel[arch].values - panel[arch].values.mean()
        coef, _ = pywt.cwt(signal, scales, wavelet, sampling_period=1)
        power = np.abs(coef) ** 2
        powers[arch] = power
        maxes[arch] = float(np.max(power))

for ax, arch in zip(axes_flat, panel_order):
    if arch not in powers:
        ax.set_visible(False)
        continue
    cfg = ARCH[arch]
    power = powers[arch]
    panel_vmax = float(np.percentile(power, 95))
    ax.imshow(power, aspect='auto',
              extent=[0, len(panel), periods[-1], periods[0]],
              cmap='inferno', interpolation='bilinear',
              vmin=0, vmax=panel_vmax)
    ax.set_yscale('log')
    ax.axhline(12, color='cyan', lw=1.0, ls='--', alpha=0.85)
    ax.set_xticks(year_ticks)
    ax.set_xticklabels(year_tick_labels, fontsize=10)

    # (b) panel title 색·weight = archetype 정체성
    is_target = cfg['role'] == '분석 대상'
    ax.set_title(
        f'{cfg["name"]} · {cfg["role"]}  (max power = {maxes[arch]:.2f})',
        fontsize=11.5, color=cfg['color'],
        fontweight='bold' if is_target else 'normal',
        pad=8)

    # (b) border 색 = archetype color (분석 대상은 굵게)
    for spine in ax.spines.values():
        spine.set_edgecolor(cfg['color'])
        spine.set_linewidth(2.5 if is_target else 1.2)

for ax in axes[:, 0]:
    ax.set_ylabel('주기 (개월)', fontsize=10.5)
for ax in axes[-1, :]:
    ax.set_xlabel('연도', fontsize=10.5)

fig.suptitle(
    'Wavelet scaleogram — 시간×주파수 동학\n'
    'C2 출연금형은 12m 라인(cyan)이 시간 따라 강화, C0 인건비형은 거의 무신호 (null)',
    fontsize=12, weight='bold', y=0.995, linespacing=1.4)

fig.subplots_adjust(hspace=0.38, wspace=0.12, top=0.86, bottom=0.08,
                    left=0.07, right=0.97)

fig.text(0.5, 0.005,
         '※ Continuous Wavelet Transform (cmor1.5-1.0) · panel별 vmax는 95-percentile (내부 동학 보존)',
         ha='center', fontsize=8.5, color='#666', style='italic')

out = ROOT / 'paper' / 'figures' / 'h28_scaleogram.png'
plt.savefig(out, dpi=130, bbox_inches='tight', facecolor='white')
plt.close()

w, h = Image.open(out).size
print(f'저장: {out} | {w}x{h}px')
