"""Figure 5 (h10_cpi_control) — English label version.

Copied from scripts/redo_fig05_cpi.py; changes:
  - Output path -> paper/figures_en/_preview/
  - All Korean labels -> English
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
    'font.size': 13, 'axes.titlesize': 15, 'axes.labelsize': 13,
    'xtick.labelsize': 12, 'ytick.labelsize': 12,
    'legend.fontsize': 12,
    'mathtext.default': 'regular',
    'axes.unicode_minus': False,
})
for fname in ['Malgun Gothic', 'Arial Unicode MS', 'NanumGothic']:
    if any(fname.lower() in fn.name.lower()
           for fn in mpl.font_manager.fontManager.ttflist):
        mpl.rcParams['font.family'] = [fname, 'Times New Roman', 'DejaVu Sans']
        break

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, 'data', 'results')
PREVIEW = os.path.join(ROOT, 'paper', 'figures_en', '_preview')
os.makedirs(PREVIEW, exist_ok=True)

df = pd.read_csv(os.path.join(RES, 'H10_macro_control_corr_v3.csv'))
df = df.dropna(subset=['corr_raw', 'corr_resid_CPI'])
print(f'rows = {len(df)}')

# English short labels for scatter plot (label overlap mitigation)
SHORT_EN = {
    '산업·중소기업및에너지': 'Industry',
    '국토및지역개발': 'Land',
    '공공질서및안전': 'Pub. Order',
    '문화및관광': 'Culture',
    '일반·지방행정': 'Gen.Adm.',
    '교통및물류': 'Transport',
    '통일·외교': 'Unif./Dipl.',
    '사회복지': 'Welfare',
    '보건': 'Health',
    '과학기술': 'S&T',
    '교육': 'Education',
    '농림수산식품': 'Agriculture',
    '환경': 'Environment',
    '통신': 'ICT',
    '국방': 'Defense',
    '예비비': 'Reserve',
}

# Full English field names for bar chart y-ticks
FULL_EN = {
    '산업·중소기업및에너지': 'Industry/SMEs',
    '국토및지역개발': 'Land Dev.',
    '공공질서및안전': 'Public Order',
    '문화및관광': 'Culture & Tourism',
    '일반·지방행정': 'Gen. Admin.',
    '교통및물류': 'Transport',
    '통일·외교': 'Unification/Diplomacy',
    '사회복지': 'Welfare',
    '보건': 'Health',
    '과학기술': 'S&T',
    '교육': 'Education',
    '농림수산식품': 'Agriculture',
    '환경': 'Environment',
    '통신': 'ICT',
    '국방': 'Defense',
    '예비비': 'Reserve',
}

df = df.copy()
df['fld_short'] = df['fld'].map(lambda x: SHORT_EN.get(x, x))
df['fld_en'] = df['fld'].map(lambda x: FULL_EN.get(x, x))

fig, axes = plt.subplots(2, 1, figsize=(8.5, 8.5),
                         gridspec_kw={'height_ratios': [1.4, 1]})

# ── (a) Scatter: raw vs CPI-residual + field labels (adjustText)
ax1 = axes[0]
ax1.plot([-1, 1], [-1, 1], '--', color='#888', alpha=0.6,
         label='identity (no change)')
ax1.scatter(df['corr_raw'], df['corr_resid_CPI'], s=80, alpha=0.78,
            edgecolor='white', linewidth=1.2, color='#5475a8')
texts = []
for _, row in df.iterrows():
    t = ax1.text(row['corr_raw'], row['corr_resid_CPI'],
                 str(row['fld_short']),
                 fontsize=13, alpha=0.95, weight='medium')
    texts.append(t)
try:
    from adjustText import adjust_text
    adjust_text(
        texts, ax=ax1,
        arrowprops=dict(arrowstyle='-', color='#666', lw=0.7),
        expand_points=(3.0, 3.0),
        expand_text=(2.5, 2.5),
        force_text=(1.5, 1.8),
        force_points=(1.2, 1.4),
        only_move={'points': 'y', 'text': 'xy'},
        lim=200,
    )
except ImportError:
    pass
ax1.axhline(0, color='gray', lw=0.6, ls=':')
ax1.axvline(0, color='gray', lw=0.6, ls=':')
n_sign = (df['sign_change'] == True).sum()
ax1.set_xlabel('Raw correlation (pre-CPI control)')
ax1.set_ylabel('CPI-residual correlation')
ax1.set_xlim(-1.05, 1.05); ax1.set_ylim(-1.05, 1.05)
ax1.legend(loc='lower right')
ax1.grid(alpha=0.3)
ax1.set_title(f'(a) Pre/Post CPI Control — Sign Reversal {n_sign}/{len(df)}')

# ── (b) Horizontal bar: raw vs CPI-residual by field
ax2 = axes[1]
df_sorted = df.sort_values('corr_raw').reset_index(drop=True)
y = np.arange(len(df_sorted))
ax2.barh(y - 0.2, df_sorted['corr_raw'], height=0.4,
         label='Raw corr.', color='#5475a8', alpha=0.85)
ax2.barh(y + 0.2, df_sorted['corr_resid_CPI'], height=0.4,
         label='CPI-residual corr.', color='#a85454', alpha=0.85)
ax2.set_yticks(y)
ax2.set_yticklabels(df_sorted['fld_en'], fontsize=12)
ax2.axvline(0, color='gray', lw=0.6)
ax2.set_xlabel('Correlation coefficient')
ax2.legend(loc='lower right')
ax2.grid(axis='x', alpha=0.3)
ax2.set_title('(b) Raw vs CPI-residual by Field')

plt.tight_layout()

DPI = 200
MAX = 1900
out = os.path.join(PREVIEW, 'h10_cpi_control.png')
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
