"""
Build formula PNGs for app-MED appendix slides.
Output: paper/figures/appendix_formulas/
  - med_baron_kenny.png
  - med_sobel.png
  - med_bootstrap.png
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os

# Pretendard font (for fallback labels), but formulas use mathtext
font_path = r"d:\workspace\재정자료분석\paper\fonts\Pretendard-Regular.otf"
if os.path.exists(font_path):
    fm.fontManager.addfont(font_path)

plt.rcParams['mathtext.fontset'] = 'cm'
plt.rcParams['font.family'] = 'serif'

OUT_DIR = r"d:\workspace\재정자료분석\paper\figures\appendix_formulas"
os.makedirs(OUT_DIR, exist_ok=True)

# ── 1. Baron-Kenny 4 conditions ──────────────────────────────────────
fig, ax = plt.subplots(figsize=(6.8, 1.5), dpi=150)
ax.set_axis_off()
fig.patch.set_facecolor('white')

lines = [
    (0.04, 0.82, r"$\mathbf{Step\ 1:}\quad Y = c \cdot X + \varepsilon_1$"
     r"$\qquad\text{(total effect)}$", 18),
    (0.04, 0.58, r"$\mathbf{Step\ 2:}\quad M = a \cdot X + \varepsilon_2$"
     r"$\qquad\text{(}a\text{ path)}$", 18),
    (0.04, 0.34, r"$\mathbf{Step\ 3:}\quad Y = b \cdot M + c' \cdot X + \varepsilon_3$"
     r"$\qquad\text{(}b\text{ path + direct)}$", 18),
    (0.04, 0.10, r"$\mathbf{Step\ 4:}\quad |c'| < |c|$"
     r"$\qquad\text{(}\exists\text{ mediation)}$", 18),
]

for x, y, s, fs in lines:
    ax.text(x, y, s, transform=ax.transAxes,
            fontsize=fs, va='bottom', ha='left', color='#1a1a1a')

plt.tight_layout(pad=0.3)
out = os.path.join(OUT_DIR, "med_baron_kenny.png")
plt.savefig(out, dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
from PIL import Image
sz = Image.open(out).size
print(f"med_baron_kenny.png  {sz}")

# ── 2. Sobel z full formula ───────────────────────────────────────────
fig, ax = plt.subplots(figsize=(6.0, 1.2), dpi=150)
ax.set_axis_off()
fig.patch.set_facecolor('white')

formula = (r"$z = \dfrac{a \cdot b}"
           r"{\sqrt{b^2 \cdot SE(a)^2 + a^2 \cdot SE(b)^2}}$")
ax.text(0.5, 0.5, formula, transform=ax.transAxes,
        fontsize=22, va='center', ha='center', color='#1a1a1a')

plt.tight_layout(pad=0.4)
out = os.path.join(OUT_DIR, "med_sobel.png")
plt.savefig(out, dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
sz = Image.open(out).size
print(f"med_sobel.png        {sz}")

# ── 3. Bootstrap CI formula ───────────────────────────────────────────
fig, ax = plt.subplots(figsize=(7.0, 1.2), dpi=150)
ax.set_axis_off()
fig.patch.set_facecolor('white')

formula = (r"$(a \cdot b)^* = \frac{1}{B}\sum_{i=1}^{B} a_i^* \cdot b_i^*,"
           r"\quad CI_{95\%} = [Q_{2.5\%},\; Q_{97.5\%}]$")
ax.text(0.5, 0.5, formula, transform=ax.transAxes,
        fontsize=20, va='center', ha='center', color='#1a1a1a')

plt.tight_layout(pad=0.4)
out = os.path.join(OUT_DIR, "med_bootstrap.png")
plt.savefig(out, dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
sz = Image.open(out).size
print(f"med_bootstrap.png    {sz}")

print("All formula PNGs built.")
