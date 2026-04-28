"""그림 5 (h10_cpi_control) — 원본 디자인 (산포도 + 수평막대) 유지 + 라벨 겹침 해소.

원본 source: scripts/h10_replot.py
핵심 수정:
  - 산포도 분야 라벨 adjustText로 자동 배치 (겹침 해소)
  - PNG 내부 큰 suptitle 제거 (Typst caption이 별도)
  - A4 본문 폭 6.3 inch 1:1 매핑
  - figsize=(6.3, 7), dpi=200
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
    'font.size': 11, 'axes.titlesize': 12, 'axes.labelsize': 11,
    'xtick.labelsize': 10, 'ytick.labelsize': 10,
    'legend.fontsize': 10,
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
PREVIEW = os.path.join(ROOT, 'paper', 'figures', '_preview')
os.makedirs(PREVIEW, exist_ok=True)

df = pd.read_csv(os.path.join(RES, 'H10_macro_control_corr_v3.csv'))
df = df.dropna(subset=['corr_raw', 'corr_resid_CPI'])
print(f'rows = {len(df)}')

# 산포도용 분야명 단축 (라벨 겹침 완화) — 막대는 원본 분야명 유지
SHORT = {
    '산업·중소기업및에너지': '산업·중기',
    '국토및지역개발': '국토',
    '공공질서및안전': '공공질서',
    '문화및관광': '문화관광',
    '일반·지방행정': '일반행정',
    '교통및물류': '교통',
    '통일·외교': '통일외교',
}
df = df.copy()
df['fld_short'] = df['fld'].map(lambda x: SHORT.get(x, x))

fig, axes = plt.subplots(2, 1, figsize=(6.3, 8.5),
                         gridspec_kw={'height_ratios': [1.4, 1]})

# ── (a) 산포도 raw vs CPI-residual + 분야 라벨 (adjustText)
ax1 = axes[0]
ax1.plot([-1, 1], [-1, 1], '--', color='#888', alpha=0.6,
         label='identity (변화 없음)')
ax1.scatter(df['corr_raw'], df['corr_resid_CPI'], s=80, alpha=0.78,
            edgecolor='white', linewidth=1.2, color='#5475a8')
texts = []
for _, row in df.iterrows():
    t = ax1.text(row['corr_raw'], row['corr_resid_CPI'],
                 str(row['fld_short']),
                 fontsize=9, alpha=0.9)
    texts.append(t)
try:
    from adjustText import adjust_text
    adjust_text(
        texts, ax=ax1,
        arrowprops=dict(arrowstyle='-', color='#777', lw=0.6),
        expand_points=(2.0, 2.0),
        expand_text=(1.6, 1.6),
        force_text=(0.8, 1.0),
        force_points=(0.6, 0.8),
        only_move={'points': 'y', 'text': 'xy'},
    )
except ImportError:
    pass
ax1.axhline(0, color='gray', lw=0.6, ls=':')
ax1.axvline(0, color='gray', lw=0.6, ls=':')
n_sign = (df['sign_change'] == True).sum()
ax1.set_xlabel('raw 상관 (CPI 통제 전)')
ax1.set_ylabel('CPI-residual 상관')
ax1.set_xlim(-1.05, 1.05); ax1.set_ylim(-1.05, 1.05)
ax1.legend(loc='lower right')
ax1.grid(alpha=0.3)
ax1.set_title(f'(a) CPI 통제 전후 비교 — 부호 반전 {n_sign}/{len(df)}')

# ── (b) 분야별 raw vs CPI-residual 수평 막대
ax2 = axes[1]
df_sorted = df.sort_values('corr_raw').reset_index(drop=True)
y = np.arange(len(df_sorted))
ax2.barh(y - 0.2, df_sorted['corr_raw'], height=0.4,
         label='raw 상관', color='#5475a8', alpha=0.85)
ax2.barh(y + 0.2, df_sorted['corr_resid_CPI'], height=0.4,
         label='CPI-residual 상관', color='#a85454', alpha=0.85)
ax2.set_yticks(y)
ax2.set_yticklabels(df_sorted['fld'], fontsize=9)
ax2.axvline(0, color='gray', lw=0.6)
ax2.set_xlabel('상관계수')
ax2.legend(loc='lower right')
ax2.grid(axis='x', alpha=0.3)
ax2.set_title('(b) 분야별 raw vs CPI-residual')

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
