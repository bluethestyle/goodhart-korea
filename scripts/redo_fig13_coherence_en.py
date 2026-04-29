"""Figure 13 (h27_coherence) — archetype × k phase coherence heatmap [English].

source: scripts/redo_fig13_coherence.py
A4 body width 6.3 inch 1:1, figsize=(6.3, 3.2), dpi=200
"""
import os, sys, io, warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns
from PIL import Image

warnings.filterwarnings('ignore')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

plt.rcParams.update({
    'font.size': 10, 'axes.titlesize': 11, 'axes.labelsize': 10,
    'xtick.labelsize': 9, 'ytick.labelsize': 9,
    'mathtext.default': 'regular',
    'axes.unicode_minus': False,
})
mpl.rcParams['font.family'] = ['DejaVu Sans', 'Times New Roman']

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, 'data', 'results')
PREVIEW = os.path.join(ROOT, 'paper', 'figures_en', '_preview')
os.makedirs(PREVIEW, exist_ok=True)

ARCH_NAME = {'C0_personnel': 'Personnel',
             'C1_direct_invest': 'Capital-Acq.',
             'C2_chooyeon': 'Grant-Transfer',
             'C3_normal': 'Normal'}

coh = pd.read_csv(os.path.join(RES, 'H27_coherence_intra_archetype.csv'))
print(coh.head())

piv = coh.pivot_table(index='archetype', columns='k', values='phase_coherence')
piv = piv.reindex(['C0_personnel', 'C1_direct_invest',
                   'C2_chooyeon', 'C3_normal'])
piv.index = [ARCH_NAME[a] for a in piv.index]
# k → period label
piv.columns = [f'k={k}\n({12/k:.1f}m)' for k in piv.columns]

fig, ax = plt.subplots(figsize=(6.3, 3.2))
sns.heatmap(piv, annot=True, fmt='.2f', cmap='Blues',
            vmin=0, vmax=0.6, ax=ax,
            cbar_kws={'label': 'Phase coherence'},
            linewidths=0.5, linecolor='white',
            annot_kws={'size': 10})
ax.set_xlabel('Frequency bin')
ax.set_ylabel('')
ax.tick_params(axis='y', rotation=0)
ax.tick_params(axis='x', rotation=0)
ax.set_title('Within-Archetype 12-month Phase Coherence',
             fontsize=11, pad=8)

# highlight Grant-Transfer 12m cell (row 2, col 0) with black border
import matplotlib.patches as mpatches
ax.add_patch(mpatches.Rectangle(
    (0, 2), 1, 1, fill=False, edgecolor='black',
    lw=2.2, zorder=10,
))

# annotation text below
ax.text(0.5, -0.55,
        "Grant-Transfer 12m phase coherence = 0.54  (4-7x other archetypes: 0.08-0.13)",
        transform=ax.transAxes, ha='center', va='top', fontsize=9,
        color='#a85454', fontweight='bold',
        bbox=dict(boxstyle='round,pad=0.4', fc='#fff8e1',
                  ec='#daa520', alpha=0.92))

plt.tight_layout()

DPI = 200
MAX = 1900
out = os.path.join(PREVIEW, 'h27_coherence.png')
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
