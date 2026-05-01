"""
S33 슬라이드용 Sobel z forest plot.

원본 s33_baron_kenny.png은 ab(절대값) 단위로 그려서 1e8 스케일로 폭주하고,
사회복지가 빨간색으로 잘못 강조돼 있었다. 이 스크립트는
data/results/H23_mediation_estimates.csv 에서 Sobel z 값을 읽어
14분야를 한 axis 위에 깔끔하게 비교하고 농림수산만 accent로 강조한다.
"""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib as mpl

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "data" / "results" / "H23_mediation_estimates.csv"
OUT = ROOT / "paper" / "slides" / "assets" / "s33_forest_sobel_z.png"

# Deck palette
INK = "#1a1814"
INK_2 = "#3a352e"
INK_3 = "#6b6358"
LINE = "#c9bfa5"
PAPER = "#f5f1e8"
ACCENT = "#b73a2c"
GOLD = "#a87f24"

mpl.rcParams.update({
    "font.family": ["Pretendard Variable", "Pretendard", "Malgun Gothic",
                    "AppleGothic", "Noto Sans KR", "DejaVu Sans"],
    "axes.edgecolor": INK_3,
    "axes.labelcolor": INK_2,
    "xtick.color": INK_2,
    "ytick.color": INK_2,
    "axes.linewidth": 0.8,
})


def load() -> list[dict]:
    rows: list[dict] = []
    with CSV.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            short = (r.get("fld_short") or "").strip()
            z_raw = (r.get("sobel_z") or "").strip()
            if not short or not z_raw or short == "POOLED":
                continue
            try:
                z = float(z_raw)
            except ValueError:
                continue
            rows.append({"name": short, "z": z, "p": float(r["sobel_p"])})
    return rows


def main() -> None:
    rows = load()
    rows.sort(key=lambda r: r["z"])

    names = [r["name"] for r in rows]
    zs = [r["z"] for r in rows]
    is_target = [r["name"] == "농림수산" for r in rows]

    fig, ax = plt.subplots(figsize=(7.0, 4.4), dpi=180)
    fig.patch.set_facecolor(PAPER)
    ax.set_facecolor(PAPER)

    y = list(range(len(names)))

    # Significance threshold ribbon (n.s. region |z| < 1.96)
    ax.axvspan(-1.96, 1.96, color=LINE, alpha=0.30, lw=0)
    ax.axvline(0, color=INK_3, lw=0.9, ls="-", alpha=0.6)
    ax.axvline(-1.96, color=INK_3, lw=0.7, ls=":", alpha=0.8)
    ax.axvline(1.96, color=INK_3, lw=0.7, ls=":", alpha=0.8)

    # Lollipop sticks
    for i, (z, tgt) in enumerate(zip(zs, is_target)):
        c = ACCENT if tgt else INK_3
        a = 1.0 if tgt else 0.55
        ax.plot([0, z], [i, i], color=c, lw=2.4 if tgt else 1.2, alpha=a,
                solid_capstyle="round")
        ax.scatter([z], [i], s=72 if tgt else 28, color=c, alpha=a, zorder=3,
                   edgecolor=PAPER, linewidth=1.2)

    # Cosmetic
    ax.set_yticks(y)
    ax.set_yticklabels(names, fontsize=10.5)
    for i, tick in enumerate(ax.get_yticklabels()):
        if is_target[i]:
            tick.set_color(ACCENT)
            tick.set_fontweight("bold")
    ax.set_xlabel("Sobel z  (간접효과의 표준화 통계량)",
                  fontsize=10.5, color=INK_2, labelpad=8)
    ax.set_xlim(-3.6, 1.6)
    ax.set_ylim(-0.8, len(names) - 0.4)

    # Threshold tick labels above x-axis line
    for x_th, lbl in [(-1.96, "−1.96"), (1.96, "+1.96")]:
        ax.text(x_th, len(names) - 0.55, lbl, fontsize=8.5, color=INK_3,
                ha="center", va="bottom")
    ax.text(0, len(names) - 0.55, "n.s. band  (|z| < 1.96)",
            fontsize=8.5, color=INK_3, ha="center", va="bottom",
            fontstyle="italic")

    ax.set_title("14분야 매개효과 Sobel z — 농림수산만 유의 (z = −2.897, p = 0.004)",
                 fontsize=12.5, color=INK, pad=14, loc="left",
                 fontweight="bold")
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.tick_params(axis="x", labelsize=9.5)

    fig.tight_layout()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=180, facecolor=PAPER, bbox_inches="tight")
    print(f"saved: {OUT}  ({OUT.stat().st_size / 1024:.1f} KB)")
    from PIL import Image  # noqa: WPS433
    print("size:", Image.open(OUT).size)


if __name__ == "__main__":
    main()
