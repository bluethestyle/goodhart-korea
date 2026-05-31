"""Slide 40 좌 — 세부사업(1,557) 산점도. 측정가능 축(output only).

x = 12월 집행 비중(%), y = 연주기 진폭(정규화), 색 = 체질(C0~C3).
※ outcome 축을 쓰지 않는 이유: 사업 단위 outcome이 없어(측정 공백) 분야값 대리는
   가짜 정밀도를 만든다. 측정 가능한 output 축으로 "체질이 영역을 가른다"만 보인다.
가독성: 절반-슬라이드(≈700px) 배치 — 큰 폰트·여백·범례 충돌 회피.
출처: data/results/H3_activity_embedding_11y.csv
"""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent.parent
for f in ["Pretendard-Regular.otf", "Pretendard-Bold.otf", "Pretendard-SemiBold.otf"]:
    p = ROOT / "paper" / "fonts" / f
    if p.exists():
        font_manager.fontManager.addfont(str(p))
plt.rcParams["font.family"] = "Pretendard"
plt.rcParams["axes.unicode_minus"] = False

df = pd.read_csv(ROOT / "data/results/H3_activity_embedding_11y.csv")
df["x"] = df["dec_pct"] * 100
df["y"] = df["amp_12m_norm"]

# cluster: 0 인건비 / 1 자산취득 / 2 출연금 / 3 정상  (color, alpha, size, draw-order)
ARCH = {
    3: ("정상사업 (C3, n=1,175)", "#C2CCD9", 0.30, 12, 0),
    0: ("인건비형 (C0, n=129)", "#8C5A8F", 0.60, 20, 1),
    2: ("출연금형 (C2, n=154)", "#E67E22", 0.72, 24, 2),
    1: ("자산취득형 (C1, n=99)", "#C0392B", 0.78, 26, 3),
}

fig, ax = plt.subplots(figsize=(7.0, 5.7), dpi=158)
for cl, (lab, col, al, sz, _) in sorted(ARCH.items(), key=lambda k: k[1][4]):
    s = df[df["cluster"] == cl]
    ax.scatter(s["x"], s["y"], s=sz, c=col, alpha=al, edgecolors="none", label=lab)

ax.set_xlabel("12월 집행 비중 (%)", fontsize=15, color="#334155")
ax.set_ylabel("연주기 진폭 (정규화)", fontsize=15, color="#334155")
ax.set_title("사업 단위로 보면 — 4 체질이 다른 영역에 분포",
             fontsize=16, fontweight="bold", color="#0F172A", pad=12)
ax.axvline(8.3, color="#94A3B8", ls="--", lw=1, alpha=0.8)
ylo, yhi = ax.get_ylim()
ax.text(9.0, yhi * 0.95, "균등 8.3%", fontsize=11, color="#94A3B8")
ax.tick_params(labelsize=12, colors="#475569")
ax.grid(True, color="#E6E2D8", lw=0.6, alpha=0.7)
for sp in ["top", "right"]:
    ax.spines[sp].set_visible(False)
leg = ax.legend(fontsize=12, loc="upper right", frameon=True, framealpha=0.96,
                edgecolor="#CBD5E1", borderpad=0.7, labelspacing=0.55,
                handletextpad=0.4)
leg.get_frame().set_linewidth(0.8)
fig.tight_layout()
out = ROOT / "paper/figures/eda/fig_slide40_actv_quadrant.png"
fig.savefig(out, facecolor="white", bbox_inches="tight")
from PIL import Image
print("saved", out, Image.open(out).size)
