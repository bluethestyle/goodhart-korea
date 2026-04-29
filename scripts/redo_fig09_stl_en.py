"""Figure 9 (h24_stl) — EN version.
caption: 'STL vs FFT Comparison — Self-criticism on trend contamination in Welfare signal'

(a) STL vs FFT first-difference correlation grouped barh by field
(b) STL vs FFT scatter by field (sign reversal highlighted)

A4 body width 6.3 inch 1:1
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
    'xtick.labelsize': 9, 'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'mathtext.default': 'regular',
    'axes.unicode_minus': False,
    'font.family': 'DejaVu Sans',
})

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, 'data', 'results')
PREVIEW = os.path.join(ROOT, 'paper', 'figures_en', '_preview')
os.makedirs(PREVIEW, exist_ok=True)

# Field name short labels (English)
SHORT = {
    '산업·중소기업및에너지': 'Industry/SMEs',
    '국토및지역개발': 'Land Dev.',
    '공공질서및안전': 'Public Order',
    '문화및관광': 'Culture & Tourism',
    '일반·지방행정': 'Gen. Admin.',
    '교통및물류': 'Transport',
    '통일·외교': 'Unification/Diplomacy',
    '외교·통일': 'Unification/Diplomacy',
    '사회복지': 'Welfare',
    '보건': 'Health',
    '과학기술': 'S&T',
    '교육': 'Education',
    '농림수산': 'Agriculture',
    '환경': 'Environment',
    '통신': 'ICT',
    '국방': 'Defense',
}

df = pd.read_csv(os.path.join(RES, 'H24_h6_replication.csv'))
df = df.dropna(subset=['corr_stl', 'corr_fft'])
df['fld_short'] = df['fld'].map(lambda x: SHORT.get(x, x))
df = df.sort_values('corr_fft', ascending=True).reset_index(drop=True)
print(df[['fld', 'corr_stl', 'corr_fft', 'sign_change']].to_string())

DPI = 200
MAX = 1900
def save_resize(fig, fname):
    out = os.path.join(PREVIEW, fname)
    fig.savefig(out, dpi=DPI, bbox_inches='tight')
    plt.close(fig)
    img = Image.open(out)
    w, h = img.size
    if max(w, h) > MAX:
        s = MAX / max(w, h)
        ns = (int(w * s), int(h * s))
        img = img.resize(ns, Image.LANCZOS)
        img.save(out, optimize=True)
        print(f'  {fname:28s} {w}x{h} -> {ns[0]}x{ns[1]}')
    else:
        print(f'  {fname:28s} {w}x{h}')

# ── (a) STL vs FFT grouped barh by field — sign-reversal rows highlighted
fig, ax = plt.subplots(figsize=(9.84, 5.0))
y = np.arange(len(df))

# Highlight sign-reversal field rows
for i, r in df.iterrows():
    if r['sign_change']:
        ax.axhspan(i - 0.5, i + 0.5, color='#ffe0e0', alpha=0.55, zorder=0)

ax.barh(y - 0.2, df['corr_fft'], height=0.4,
        label='FFT amp_12m_norm', color='#5475a8', alpha=0.88, zorder=2)
ax.barh(y + 0.2, df['corr_stl'], height=0.4,
        label='STL seasonal_strength', color='#a85454', alpha=0.88, zorder=2)

# Sign-reversal fields — label in red bold
ax.set_yticks(y); ax.set_yticklabels(df['fld_short'])
for i, r in df.iterrows():
    if r['sign_change']:
        tick_label = ax.get_yticklabels()[i]
        tick_label.set_color('#a85454')
        tick_label.set_fontweight('bold')
ax.axvline(0, color='black', lw=1.0, zorder=3)
ax.set_xlabel('First-difference correlation (gaming ↔ outcome)')
ax.legend(loc='lower right', fontsize=10)
ax.grid(alpha=0.3, axis='x')
ax.text(0.02, 0.97,
        f'Pink rows + red field name = Sign reversal\n'
        f'(FFT and STL have opposite signs)  '
        f'{int(df["sign_change"].sum())}/{len(df)} fields',
        transform=ax.transAxes, va='top', fontsize=9,
        bbox=dict(boxstyle='round,pad=0.4', fc='white',
                  ec='#bbb', alpha=0.92))
plt.tight_layout()
save_resize(fig, 'h24_stl_bars.png')

# ── (b) STL vs FFT scatter — quadrant 2 & 4 (sign-reversal region) highlighted
fig, ax = plt.subplots(figsize=(9.84, 5.0))
# Quadrant 2 (FFT < 0, STL > 0)
ax.fill_between([-1.05, 0], 0, 1.05, color='#ffe0e0', alpha=0.55, zorder=0)
# Quadrant 4 (FFT > 0, STL < 0)
ax.fill_between([0, 1.05], -1.05, 0, color='#ffe0e0', alpha=0.55, zorder=0)
# Quadrant labels
ax.text(-0.97, 0.45, 'Sign reversal\nFFT−, STL+', fontsize=8.5,
        color='#a85454', va='center', ha='left', alpha=0.9,
        bbox=dict(boxstyle='round,pad=0.25', fc='white',
                  ec='#a85454', alpha=0.7))
ax.text(0.97, -0.45, 'Sign reversal\nFFT+, STL−', fontsize=8.5,
        color='#a85454', va='center', ha='right', alpha=0.9,
        bbox=dict(boxstyle='round,pad=0.25', fc='white',
                  ec='#a85454', alpha=0.7))

ax.scatter(df['corr_fft'], df['corr_stl'],
           c=['#a85454' if s else '#5475a8' for s in df['sign_change']],
           s=80, alpha=0.85, edgecolor='black', linewidth=0.6, zorder=3)
ax.plot([-1, 1], [-1, 1], '--', color='#888', alpha=0.5, label='y=x',
        zorder=2)
ax.axhline(0, color='#666', lw=0.8, zorder=2)
ax.axvline(0, color='#666', lw=0.8, zorder=2)

texts = []
try:
    from adjustText import adjust_text
    for _, row in df.iterrows():
        t = ax.text(row['corr_fft'], row['corr_stl'], row['fld_short'],
                    fontsize=9, alpha=0.9)
        texts.append(t)
    adjust_text(texts, ax=ax,
                arrowprops=dict(arrowstyle='-', color='#888', lw=0.5),
                expand_points=(1.5, 1.5),
                expand_text=(1.3, 1.3))
except ImportError:
    for _, row in df.iterrows():
        ax.annotate(row['fld_short'], (row['corr_fft'], row['corr_stl']),
                    xytext=(4, 4), textcoords='offset points',
                    fontsize=9, alpha=0.9)

# Welfare — larger dot for emphasis
sw = df[df['fld'].astype(str).str.contains('사회복지', na=False)]
for _, row in sw.iterrows():
    ax.scatter([row['corr_fft']], [row['corr_stl']], s=160,
               color='#a85454', edgecolor='black', linewidth=1.4, zorder=5)

ax.set_xlabel('FFT correlation (amp_12m_norm)')
ax.set_ylabel('STL correlation (seasonal_strength)')
ax.legend(loc='lower left')
ax.grid(alpha=0.3)
ax.set_xlim(-1.05, 1.05); ax.set_ylim(-1.05, 1.05)
ax.text(0.02, 0.97,
        f'Pink region = Sign reversal\n'
        f'Reversal fields: {int(df["sign_change"].sum())}/{len(df)}\n'
        f'Welfare: FFT −0.76 → STL 0.00 (Signal vanishes)',
        transform=ax.transAxes, va='top', fontsize=8.5,
        bbox=dict(boxstyle='round,pad=0.4', fc='#fff8e1',
                  ec='#daa520', alpha=0.92))
plt.tight_layout()
save_resize(fig, 'h24_stl_scatter.png')

print('Done.')
