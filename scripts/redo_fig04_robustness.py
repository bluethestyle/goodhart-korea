"""그림 4 분리 — (a)+(b) main / (c)+(d) lag·amp 별도 figure.

paper/figures/_preview/
  h6_robustness.png    — (a) FE 회귀  +  (b) Permutation null
  h6_lag_amp.png       — (c) Lag/Lead  +  (d) amp_cv vs amp_mean

A4 본문 폭 6.3 inch 1:1, 1x2 가로 패널 (figsize 약 6.3 × 3.3)
"""
import os, sys, io, warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns
from PIL import Image
from scipy.stats import norm

warnings.filterwarnings('ignore')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

plt.rcParams.update({
    'font.size': 10, 'axes.titlesize': 11, 'axes.labelsize': 10,
    'xtick.labelsize': 9, 'ytick.labelsize': 9,
    'legend.fontsize': 9,
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
        print(f'  {fname:25s} {w}x{h} -> {ns[0]}x{ns[1]}')
    else:
        print(f'  {fname:25s} {w}x{h}')

fe = pd.read_csv(os.path.join(RES, 'H6_fe_regression.csv'))
perm = pd.read_csv(os.path.join(RES, 'H6_permutation_pvals.csv'))
lag = pd.read_csv(os.path.join(RES, 'H6_lag_lead_corr.csv'))
nat = pd.read_csv(os.path.join(RES, 'H6_natural_vs_gaming.csv'))
print(f'fe={len(fe)}, perm={len(perm)}, lag={len(lag)}, nat={len(nat)}')

target_keys = ['사회복지', '복지', 'wealth']

# ============================================================
# Figure 1: h6_robustness.png — (a) FE 회귀 + (b) 14분야 Permutation forest
# ============================================================
fig, axes = plt.subplots(1, 2, figsize=(6.3, 4.2),
                         gridspec_kw={'width_ratios': [1, 1.4]})

# ── (a) FE 회귀 (제목 단축)
ax = axes[0]
labels_short = []
for m in fe['model'].astype(str):
    if 'pooled' in m:
        labels_short.append('A. pooled')
    elif '+분야 FE +연도 FE' in m:
        labels_short.append('C. 분야+연도')
    elif '+분야 FE' in m:
        labels_short.append('B. 분야 FE')
    else:
        labels_short.append(m[:12])
xs = np.arange(len(fe))
betas = fe['beta'].values
ses = fe['se'].values
colors = ['#9aa9c2', '#5475a8', '#c87f5a']
ax.bar(xs, betas, color=colors[:len(fe)], alpha=0.85,
       edgecolor='black', linewidth=0.5,
       yerr=1.96 * ses, capsize=4, ecolor='#444')

err_top = betas + 1.96 * ses
err_bot = betas - 1.96 * ses
ymax = max(err_top.max(), 0)
ymin = min(err_bot.min(), 0)
yrange = ymax - ymin
ax.set_ylim(ymin - yrange * 0.18, ymax + yrange * 0.30)
for i, p in enumerate(fe['p']):
    ax.text(i, err_top[i] + yrange * 0.04,
            f'p={p:.2f}', ha='center', va='bottom', fontsize=9,
            bbox=dict(boxstyle='round,pad=0.18', fc='white',
                      ec='#bbb', alpha=0.85))

ax.axhline(0, color='gray', lw=0.6)
ax.set_xticks(xs)
ax.set_xticklabels(labels_short, fontsize=9, rotation=12, ha='right')
ax.set_ylabel('β (Δoutcome ~ Δamp_z)')
ax.set_title('(a) FE 회귀 β  (N=128)')
ax.grid(alpha=0.3, axis='y')

# ── (b) 14분야 Permutation forest plot
ax = axes[1]
perm_sorted = perm.sort_values('obs_corr_diff', ascending=True).reset_index(drop=True)
y_pos = np.arange(len(perm_sorted))

# null 95% CI 띠 (회색)
for i, r in perm_sorted.iterrows():
    null_lo = float(r['null_mean']) - 1.96 * float(r['null_std'])
    null_hi = float(r['null_mean']) + 1.96 * float(r['null_std'])
    ax.plot([null_lo, null_hi], [i, i], color='#cccccc', lw=5,
            alpha=0.65, zorder=1, solid_capstyle='round')
    ax.plot([float(r['null_mean'])], [i], 'o', color='#888',
            markersize=3, zorder=2)

# obs 점 — p<0.05 빨강, 그 외 파랑
sig_mask = perm_sorted['pval_2sided'] < 0.05
obs_colors = ['#a85454' if s else '#5475a8' for s in sig_mask]
ax.scatter(perm_sorted['obs_corr_diff'], y_pos, s=42,
           c=obs_colors, edgecolor='black', linewidth=0.5, zorder=3)

ax.axvline(0, color='gray', lw=0.6, ls=':')
ax.set_yticks(y_pos)
ax.set_yticklabels(perm_sorted['fld'], fontsize=8)
ax.set_xlabel('차분 상관 (점=obs · 띠=null 95% CI)')
ax.set_title('(b) Permutation forest — 14분야 (p<.05 빨강)')
ax.grid(alpha=0.3, axis='x')

plt.tight_layout()
save_resize(fig, 'h6_robustness.png')

# ============================================================
# Figure 2: h6_lag_amp.png — (c) Lag/Lead heatmap + (d) amp_cv 수평막대
# (원본 source: scripts/h6_robustness.py Figure C, A2)
# ============================================================
fig, axes = plt.subplots(1, 2, figsize=(6.3, 4.2))

# ── (c) Lag/Lead heatmap (분야 × lag, color = corr_diff)
ax = axes[0]
pv = lag.pivot_table(index='fld', columns='lag', values='corr_diff')
sns.heatmap(pv, annot=True, fmt='.2f', cmap='RdBu_r', center=0, ax=ax,
            cbar_kws={'label': 'corr_diff'},
            annot_kws={'size': 7}, linewidths=0.3, linecolor='white')
ax.set_xlabel('lag (year)'); ax.set_ylabel('')
ax.set_title('(c) Lag/Lead 차분 상관 heatmap')
ax.tick_params(axis='y', labelsize=7.5)
ax.tick_params(axis='x', labelsize=8)

# ── (d) 분야별 amp_cv 수평 막대 (정렬, 사회복지 강조)
ax = axes[1]
nat_sorted = nat.sort_values('amp_cv', ascending=True).reset_index(drop=True)
target_mask = nat_sorted['fld'].astype(str).str.contains(
    '|'.join(target_keys), regex=True, na=False)
colors_bar = ['#a85454' if m else '#5475a8' for m in target_mask]
ax.barh(range(len(nat_sorted)), nat_sorted['amp_cv'],
        color=colors_bar, alpha=0.85, edgecolor='black', linewidth=0.4)
ax.set_yticks(range(len(nat_sorted)))
ax.set_yticklabels(nat_sorted['fld'], fontsize=8)
ax.set_xlabel('amp_12m 시간 CV')
ax.set_title('(d) 분야별 amp_cv (게임화 변동 vs 자연 주기)')
ax.grid(alpha=0.3, axis='x')

plt.tight_layout()
save_resize(fig, 'h6_lag_amp.png')

print('완료.')
