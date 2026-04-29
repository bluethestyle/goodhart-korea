"""Figure 14 (h28_scaleogram) — 4 archetype wavelet scaleogram (time x period) [English].

source: scripts/redo_fig14_scaleogram.py
A4 body width 6.3 inch, figsize=(11.48, 6.0), dpi=200
4 archetypes in 2x2 grid (time on x-axis)
"""
import os, sys, io, warnings
import numpy as np
import pandas as pd
import duckdb
import pywt
import matplotlib.pyplot as plt
import matplotlib as mpl
from PIL import Image

warnings.filterwarnings('ignore')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

plt.rcParams.update({
    'font.size': 10, 'axes.titlesize': 10, 'axes.labelsize': 9,
    'xtick.labelsize': 8, 'ytick.labelsize': 8,
    'mathtext.default': 'regular',
    'axes.unicode_minus': False,
})
mpl.rcParams['font.family'] = ['DejaVu Sans', 'Times New Roman']

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, 'data', 'warehouse.duckdb')
RES = os.path.join(ROOT, 'data', 'results')
PREVIEW = os.path.join(ROOT, 'paper', 'figures_en', '_preview')
os.makedirs(PREVIEW, exist_ok=True)

ARCH_NAME = {'C0_personnel': 'Personnel (n=129)',
             'C1_direct_invest': 'Capital-Acq. (n=99)',
             'C2_chooyeon': 'Grant-Transfer (n=154)',
             'C3_normal': 'Normal (n=1,175)'}
ARCHETYPE_MAP = {0: 'C0_personnel', 1: 'C1_direct_invest',
                 2: 'C2_chooyeon', 3: 'C3_normal'}

# -- load data
emb = pd.read_csv(os.path.join(RES, 'H3_activity_embedding_11y.csv'))
emb['archetype'] = emb['cluster'].map(ARCHETYPE_MAP)

PURE_ACCT = (
    "(ACTV_NM ILIKE '%전출금%' OR ACTV_NM ILIKE '%타계정%' "
    "OR ACTV_NM ILIKE '%여유자금%' OR ACTV_NM ILIKE '%국고예탁%' "
    "OR ACTV_NM ILIKE '%기금예탁%' OR ACTV_NM ILIKE '%국고예치%' "
    "OR ACTV_NM ILIKE '%회계간거래%' OR ACTV_NM ILIKE '%회계간전출%')"
)

con = duckdb.connect(DB, read_only=True)
raw = con.execute(f"""
    SELECT FLD_NM, OFFC_NM, PGM_NM, ACTV_NM, FSCL_YY AS year, EXE_M AS month,
           SUM(EP_AMT) AS amt
    FROM monthly_exec
    WHERE EXE_M BETWEEN 1 AND 12 AND FSCL_YY BETWEEN 2015 AND 2025
      AND NOT {PURE_ACCT}
    GROUP BY 1,2,3,4,5,6
""").fetchdf()
con.close()
print(f'raw: {len(raw):,}')

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
print(f'panel shape: {panel.shape}')

# -- CWT
scales = np.arange(2, 40)
wavelet = 'cmor1.5-1.0'
freqs = pywt.scale2frequency(wavelet, scales)
periods = 1 / freqs

# -- Figure
fig, axes = plt.subplots(2, 2, figsize=(11.48, 6.0), sharex=True, sharey=True)
arch_order = ['C0_personnel', 'C1_direct_invest',
              'C2_chooyeon', 'C3_normal']

times = np.arange(len(panel))
year_labels = pd.to_datetime(panel.index).year
year_ticks = []
year_tick_labels = []
for y in range(2015, 2026, 2):
    matches = np.where(year_labels == y)[0]
    if len(matches) > 0:
        year_ticks.append(matches[0])
        year_tick_labels.append(str(y))

powers = {}
maxes = {}
for arch in arch_order:
    if arch in panel.columns:
        signal = panel[arch].values - panel[arch].values.mean()
        coef, _ = pywt.cwt(signal, scales, wavelet, sampling_period=1)
        power = np.abs(coef) ** 2
        powers[arch] = power
        maxes[arch] = float(np.max(power))

# per-panel separate vmax (95th percentile) for better contrast
for ax, arch in zip(axes.flat, arch_order):
    if arch not in powers:
        ax.set_visible(False)
        continue
    power = powers[arch]
    panel_vmax = float(np.percentile(power, 95))
    ax.imshow(power, aspect='auto',
              extent=[0, len(panel), periods[-1], periods[0]],
              cmap='inferno', interpolation='bilinear',
              vmin=0, vmax=panel_vmax)
    ax.set_yscale('log')
    ax.axhline(12, color='cyan', lw=1.0, ls='--', alpha=0.85)
    ax.set_xticks(year_ticks)
    ax.set_xticklabels(year_tick_labels, fontsize=8)
    ax.set_title(f'{ARCH_NAME[arch]}  (max power={maxes[arch]:.2f})',
                 fontsize=9.5, fontweight='bold')

for ax in axes[:, 0]:
    ax.set_ylabel('Period (months)', fontsize=9)
for ax in axes[-1, :]:
    ax.set_xlabel('Time (year)', fontsize=9)

fig.subplots_adjust(hspace=0.35, wspace=0.15)
# absolute comparison via max power in title; colorbar omitted (per-panel normalization)

DPI = 200
MAX = 1900
out = os.path.join(PREVIEW, 'h28_scaleogram.png')
fig.savefig(out, dpi=DPI, bbox_inches='tight')
plt.close()
img = Image.open(out)
w, h = img.size
if max(w, h) > MAX:
    s = MAX / max(w, h)
    ns = (int(w * s), int(h * s))
    img = img.resize(ns, Image.LANCZOS)
    img.save(out, optimize=True)
    print(f'preview: {w}x{h} -> {ns[0]}x{ns[1]}')
else:
    print(f'preview: {w}x{h}')
