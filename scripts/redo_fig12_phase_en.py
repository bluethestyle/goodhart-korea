"""Figure 12 (h27_phase) — EN version. 4 archetype 12-month phase polar histogram.

source: scripts/h27_power_spectrum_coherence.py (B) Phase polar
A4 body width 6.3 inch 1:1, figsize=(6.3, 6.3), dpi=200  [square ratio 0.94 maintained]
H27_phase_distribution.csv (archetype x peak_month_k1 x n)
"""
import os, sys, io, warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from PIL import Image

warnings.filterwarnings('ignore')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

plt.rcParams.update({
    'font.size': 10, 'axes.titlesize': 11, 'axes.labelsize': 10,
    'xtick.labelsize': 8, 'ytick.labelsize': 8,
    'mathtext.default': 'regular',
    'axes.unicode_minus': False,
    'font.family': 'DejaVu Sans',
})

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, 'data', 'results')
PREVIEW = os.path.join(ROOT, 'paper', 'figures_en', '_preview')
os.makedirs(PREVIEW, exist_ok=True)

ph = pd.read_csv(os.path.join(RES, 'H27_phase_distribution.csv'))
print(ph.head())

ARCH_NAME = {'C0_personnel': 'Personnel (n=129)',
             'C1_direct_invest': 'Capital-Acq. (n=99)',
             'C2_chooyeon': 'Grant-Transfer (n=154)',
             'C3_normal': 'Normal (n=1,175)'}
ARCH_COLOR = {'C0_personnel': '#4C72B0',
              'C1_direct_invest': '#DD8452',
              'C2_chooyeon': '#55A868',
              'C3_normal': '#C44E52'}

# Month labels in English
MONTH_LABELS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

fig, axes = plt.subplots(2, 2, figsize=(6.3, 6.3),
                         subplot_kw={'projection': 'polar'})

for ax, arch in zip(axes.flat,
                    ['C0_personnel', 'C1_direct_invest',
                     'C2_chooyeon', 'C3_normal']):
    sub = ph[ph['archetype'] == arch].sort_values('peak_month_k1')
    if len(sub) == 0:
        ax.set_visible(False)
        continue
    months = sub['peak_month_k1'].values
    counts = sub['n'].values
    angles = (months - 1) * (2 * np.pi / 12)
    color = ARCH_COLOR.get(arch, '#888')
    ax.bar(angles, counts, width=2 * np.pi / 12 * 0.85,
           color=color, alpha=0.82,
           edgecolor='white', linewidth=1.2)
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    ax.set_xticks(np.linspace(0, 2 * np.pi, 12, endpoint=False))
    ax.set_xticklabels(MONTH_LABELS, fontsize=8)
    # 3 concentric circles (33%, 66%, 100% of max count)
    max_c = float(counts.max())
    ax.set_yticks([max_c * 0.33, max_c * 0.66, max_c])
    ax.set_yticklabels([])
    ax.yaxis.grid(True, alpha=0.3, linestyle=':')
    ax.spines['polar'].set_visible(False)
    mode_month = int(months[counts.argmax()])
    mode_label = MONTH_LABELS[mode_month - 1]
    ax.set_title(f'{ARCH_NAME[arch]}\nmode: {mode_label}',
                 fontsize=10, pad=12, fontweight='bold')

plt.tight_layout()

DPI = 200
MAX = 1900
out = os.path.join(PREVIEW, 'h27_phase.png')
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

print('Done.')
