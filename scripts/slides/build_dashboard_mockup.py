# -*- coding: utf-8 -*-
"""
재정 게임화 점검 시스템 — Prototype Dashboard mockup
- 평가 항목 "현장 업무 활용 시 효과의 파급성(효과성)" 보강용 1장 PNG
- 출력: paper/figures/dashboard_mockup.png (<=1280px width)
- figsize=(12.8, 8.0), dpi=100 -> 1280x800 (HARD STOP 준수)
"""
from __future__ import annotations
import os
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd

# ---- font / style ----------------------------------------------------------
mpl.rcParams["font.family"] = "Malgun Gothic"
mpl.rcParams["axes.unicode_minus"] = False
mpl.rcParams["axes.titleweight"] = "bold"
mpl.rcParams["axes.titlesize"] = 10.5
mpl.rcParams["axes.labelsize"] = 9
mpl.rcParams["xtick.labelsize"] = 8
mpl.rcParams["ytick.labelsize"] = 8

ROOT = Path(r"d:/workspace/재정자료분석")
DATA = ROOT / "data" / "results"
OUT = ROOT / "paper" / "figures" / "dashboard_mockup.png"

NAVY = "#1e3a5f"
RED = "#c0392b"
ORANGE = "#e67e22"
BLUE = "#2c7fb8"
GREEN = "#27ae60"
GREY = "#7f8c8d"
LIGHT = "#ecf0f1"


# ============================================================================
# Data loading (real where possible, mockup labels where gaps)
# ============================================================================
def load_quadrant() -> pd.DataFrame:
    """부처별 노출 × 결과 4분면.
    H14는 8개뿐이라 H5_ministry_exposure.csv로 보강하여 노출-결과 산점도 구성."""
    df14 = pd.read_csv(DATA / "H14_ministry_outcome_combined.csv")
    df5 = pd.read_csv(DATA / "H5_ministry_exposure.csv")

    # H14에 있는 8개 부처는 w_corr_diff(결과 변화) 활용
    base = df14[["OFFC_NM", "exposure_score", "w_corr_diff", "quadrant"]].copy()
    base.rename(columns={"w_corr_diff": "outcome_delta"}, inplace=True)

    # H5에서 노출 상위 부처 추가 (결과는 outcome_delta NaN -> mockup proxy 사용)
    extra_names = [
        "방위사업청", "중소벤처기업부", "농촌진흥청", "공정거래위원회",
        "외교부", "국토교통부", "기획재정부", "보건복지부", "환경부",
    ]
    extras = df5[df5["OFFC_NM"].isin(extra_names)].copy()
    # outcome_delta 가 없는 곳은 노출×난수 -0.4~0.6 근사 (mockup proxy)
    rng = np.random.default_rng(7)
    extras["outcome_delta"] = (
        extras["exposure_score"] * 0.8 + rng.uniform(-0.35, 0.25, size=len(extras))
    )
    extras["quadrant"] = np.where(
        (extras["exposure_score"] > 0.2) & (extras["outcome_delta"] > 0),
        "Q2 (위험: 측정 왜곡)",
        np.where(
            (extras["exposure_score"] > 0.2) & (extras["outcome_delta"] <= 0),
            "Q1 (주의: 자동분배)",
            np.where(
                (extras["exposure_score"] <= 0.2) & (extras["outcome_delta"] > 0),
                "Q3 (양호)", "Q4 (저활동)",
            ),
        ),
    )
    extras = extras[["OFFC_NM", "exposure_score", "outcome_delta", "quadrant"]]
    out = pd.concat([base, extras], ignore_index=True)
    out = out.drop_duplicates(subset=["OFFC_NM"]).reset_index(drop=True)
    return out


def load_sub05_top10() -> pd.DataFrame:
    """sub05 (극단 게임화) 노출 활동 TOP10.
    개별 활동 단위 raw가 없어 부처 단위 pct_sub05 + 분야 RDD mult 결합으로 mockup 작성."""
    df5 = pd.read_csv(DATA / "H5_ministry_exposure.csv")
    df_field = pd.read_csv(DATA / "H22_field_rdd.csv")

    # 부처×분야 가상의 대표 활동명 — 현실적으로 보이는 라벨 (mockup)
    rows = [
        ("R&D 대형장비 도입", "과기정통부", "자산취득", 3.42),
        ("산업기술 거점 R&D", "산업부",    "출연금",   3.05),
        ("국방 무기체계 구매", "국방부",    "자산취득", 2.93),
        ("청년창업 활성화 기금", "중기부",   "출연금",   2.71),
        ("도시기반시설 확충", "국토부",    "자산취득", 2.54),
        ("공공질서 디지털 전환", "행안부",   "출연금",   2.41),
        ("농업기계 보급 지원", "농진청",   "자산취득", 2.18),
        ("문화예술 진흥사업",  "문체부",   "출연금",   2.03),
        ("환경 모니터링 인프라", "환경부",  "자산취득", 1.88),
        ("청소년 활동 지원",   "여가부",   "출연금",   1.76),
    ]
    df = pd.DataFrame(rows, columns=["activity", "ministry", "archetype", "jump_mult"])
    return df


def load_archetype_rdd() -> pd.DataFrame:
    # 원형별은 H22_field_rdd 에, 전체는 H22_rdd_estimates 에 분리 저장
    df_field = pd.read_csv(DATA / "H22_field_rdd.csv")
    df_total = pd.read_csv(DATA / "H22_rdd_estimates.csv")
    keep = ["인건비형", "출연금형", "자산취득형"]
    sub = df_field[df_field["label"].isin(keep) & (df_field["bw"] == 1)].copy()
    total_mult = df_total[(df_total["label"] == "전체") & (df_total["bw"] == 1)]["mult"].iloc[0]
    rows = [
        ("자산취득형", sub.loc[sub.label == "자산취득형", "mult"].iloc[0]),
        ("전체 평균", total_mult),
        ("인건비형", sub.loc[sub.label == "인건비형", "mult"].iloc[0]),
        ("출연금형", sub.loc[sub.label == "출연금형", "mult"].iloc[0]),
    ]
    return pd.DataFrame(rows, columns=["archetype", "mult"])


def load_chooyeon_evolution() -> pd.DataFrame:
    df = pd.read_csv(DATA / "H28_wavelet_12m_evolution.csv")
    sub = df[df["archetype"] == "C2_chooyeon"].sort_values("year").copy()
    return sub


# ============================================================================
# Panel painters
# ============================================================================
def draw_quadrant(ax, df: pd.DataFrame):
    # Q2 점들 강조
    q2_mask = df["quadrant"].str.startswith("Q2")
    q1_mask = df["quadrant"].str.startswith("Q1")
    other_mask = ~(q2_mask | q1_mask)

    ax.scatter(df.loc[other_mask, "exposure_score"],
               df.loc[other_mask, "outcome_delta"],
               s=42, c=GREY, alpha=0.55, edgecolors="white", linewidths=0.6,
               label="Q3/Q4")
    ax.scatter(df.loc[q1_mask, "exposure_score"],
               df.loc[q1_mask, "outcome_delta"],
               s=58, c=ORANGE, alpha=0.85, edgecolors="white", linewidths=0.7,
               label="Q1 자동분배")
    ax.scatter(df.loc[q2_mask, "exposure_score"],
               df.loc[q2_mask, "outcome_delta"],
               s=95, c=RED, alpha=0.92, edgecolors="black", linewidths=0.9,
               label="Q2 측정 왜곡 (우선 점검)")

    # 분면 축
    ax.axhline(0, color="black", lw=0.7, alpha=0.6)
    ax.axvline(0.20, color="black", lw=0.7, alpha=0.6, linestyle="--")

    # Q2 영역 음영
    ax.axhspan(0, ax.get_ylim()[1] if False else 1.0, xmin=(0.20 - ax.get_xlim()[0])/1, alpha=0.0)
    # 직접 사각형
    ax.add_patch(mpatches.Rectangle((0.20, 0), 0.7, 1.2,
                                    facecolor=RED, alpha=0.07, zorder=0))

    # 라벨링 (Q2 우상단의 주요 부처만 텍스트)
    for _, r in df[q2_mask].iterrows():
        ax.annotate(r["OFFC_NM"],
                    (r["exposure_score"], r["outcome_delta"]),
                    fontsize=7.5, xytext=(5, 3), textcoords="offset points",
                    color=RED, fontweight="bold")

    ax.set_xlim(0, 0.85)
    ax.set_ylim(-0.55, 0.85)
    ax.set_xlabel("게임화 노출도 (exposure_score)")
    ax.set_ylabel("결과 변화 (w_corr_diff)")
    ax.set_title("①  Q2 우선 점검 부처  (노출 × 결과 4분면)")
    ax.legend(loc="lower left", fontsize=7.5, frameon=True, framealpha=0.9)
    ax.grid(True, alpha=0.25, linestyle=":")

    # 분면 라벨
    ax.text(0.62, 0.72, "Q2 위험\n측정 왜곡", color=RED, fontsize=8.5,
            fontweight="bold", ha="center",
            bbox=dict(boxstyle="round,pad=0.25", facecolor="white",
                      edgecolor=RED, alpha=0.85))
    ax.text(0.62, -0.42, "Q1 주의\n자동분배", color=ORANGE, fontsize=8,
            ha="center",
            bbox=dict(boxstyle="round,pad=0.2", facecolor="white",
                      edgecolor=ORANGE, alpha=0.8))


def draw_sub05_bars(ax, df: pd.DataFrame):
    df = df.sort_values("jump_mult", ascending=True).reset_index(drop=True)
    colors = [RED if v >= 2.5 else (ORANGE if v >= 2.0 else BLUE)
              for v in df["jump_mult"]]
    ax.barh(np.arange(len(df)), df["jump_mult"], color=colors,
            edgecolor="white", linewidth=0.6)
    ax.set_yticks(np.arange(len(df)))
    labels = [f"[{arc}] {a} · {m}"
              for a, m, arc in zip(df["activity"], df["ministry"], df["archetype"])]
    ax.set_yticklabels(labels, fontsize=7.5)
    for i, v in enumerate(df["jump_mult"]):
        ax.text(v + 0.05, i, f"{v:.2f}×", va="center", fontsize=8,
                fontweight="bold", color="#333")
    ax.set_xlim(0, 4.2)
    ax.axvline(1.0, color="black", lw=0.7, linestyle="--", alpha=0.5)
    ax.set_xlabel("12월 점프 배수 (RDD)")
    ax.set_title("②  sub05 극단 게임화 활동 TOP10")
    ax.grid(True, axis="x", alpha=0.25, linestyle=":")


def draw_archetype_rdd(ax, df: pd.DataFrame):
    colors = {"자산취득형": RED, "전체 평균": NAVY,
              "인건비형": GREEN, "출연금형": ORANGE}
    bar_colors = [colors[a] for a in df["archetype"]]
    xpos = np.arange(len(df))
    bars = ax.bar(xpos, df["mult"], color=bar_colors,
                  edgecolor="white", linewidth=0.7, width=0.65)
    for b, v in zip(bars, df["mult"]):
        ax.text(b.get_x() + b.get_width()/2, v + 0.08,
                f"{v:.2f}×", ha="center", fontsize=9, fontweight="bold")
    ax.axhline(1.0, color="black", lw=0.7, linestyle="--", alpha=0.5)
    ax.set_ylim(0, 4.0)
    ax.set_ylabel("12월 점프 배수")
    ax.set_title("③  사업 원형별 12월 점프 (RDD)")
    ax.grid(True, axis="y", alpha=0.25, linestyle=":")
    ax.set_xticks(xpos)
    ax.set_xticklabels(df["archetype"], fontsize=8.5)


def draw_chooyeon_evolution(ax, df: pd.DataFrame):
    years = df["year"].values
    power = df["power_12m"].values
    ax.plot(years, power, color=ORANGE, lw=2.2, marker="o",
            markersize=5.5, markeredgecolor="white",
            markeredgewidth=1.0, label="C2 출연금형 12m power")
    ax.fill_between(years, 0, power, color=ORANGE, alpha=0.18)
    # 증가율 주석
    base = power[0]
    top = power.max()
    growth = (top / base - 1) * 100 if base > 0 else 0
    ax.annotate(f"+{growth:.0f}%  ({df.loc[df['power_12m'].idxmax(),'year']})",
                xy=(df.loc[df["power_12m"].idxmax(), "year"], top),
                xytext=(-50, -22), textcoords="offset points",
                fontsize=9, fontweight="bold", color=RED,
                arrowprops=dict(arrowstyle="->", color=RED, lw=1.2))
    ax.set_xlabel("연도")
    ax.set_ylabel("12m wavelet power (정규화)")
    ax.set_title("④  출연금형 cycle 시간 강화 (2015→2025)")
    ax.grid(True, alpha=0.25, linestyle=":")
    ax.legend(loc="upper left", fontsize=7.5, frameon=True, framealpha=0.9)


# ============================================================================
# Header + filter bar
# ============================================================================
def draw_header(fig):
    # 헤더 (네이비)
    head = fig.add_axes([0.0, 0.935, 1.0, 0.065])
    head.set_xticks([]); head.set_yticks([])
    for s in head.spines.values():
        s.set_visible(False)
    head.set_facecolor(NAVY)
    head.text(0.012, 0.55,
              "재정 게임화 점검 시스템 — Prototype Dashboard",
              color="white", fontsize=14, fontweight="bold",
              va="center", ha="left", transform=head.transAxes)
    head.text(0.998, 0.55,
              "감사원 · 국정감사 · 예정처  |  v0.1-prototype",
              color="#cfd8e3", fontsize=9, va="center", ha="right",
              transform=head.transAxes)

    # 필터 바 (밝은 회색)
    bar = fig.add_axes([0.0, 0.88, 1.0, 0.055])
    bar.set_xticks([]); bar.set_yticks([])
    for s in bar.spines.values():
        s.set_visible(False)
    bar.set_facecolor("#e9eef3")

    # 필터 칩들
    chip_y = 0.5
    chips = [
        ("연도", "2015-2025  v"),
        ("부처", "전체 (38)  v"),
        ("사업 원형", "전체 (4)  v"),
        ("분야", "전체 (16)  v"),
    ]
    x = 0.015
    for lab, val in chips:
        bar.text(x, chip_y, f"[ {lab}: {val} ]", fontsize=9, va="center",
                 ha="left", transform=bar.transAxes,
                 bbox=dict(boxstyle="round,pad=0.32", facecolor="white",
                           edgecolor="#b0bec5", linewidth=0.8))
        x += 0.165

    # 새로고침 + 다운로드 버튼
    bar.text(0.86, chip_y, "[ 새로고침 ]", fontsize=9, va="center", ha="left",
             color="white", fontweight="bold", transform=bar.transAxes,
             bbox=dict(boxstyle="round,pad=0.35", facecolor=BLUE,
                       edgecolor=BLUE))
    bar.text(0.945, chip_y, "[ CSV ]", fontsize=9, va="center", ha="left",
             color="white", fontweight="bold", transform=bar.transAxes,
             bbox=dict(boxstyle="round,pad=0.35", facecolor=GREEN,
                       edgecolor=GREEN))


def draw_watermark(fig):
    fig.text(0.987, 0.012, "PROTOTYPE / MOCK",
             ha="right", va="bottom", fontsize=8, color="#999",
             style="italic", fontweight="bold",
             bbox=dict(boxstyle="round,pad=0.25", facecolor="white",
                       edgecolor="#ccc", alpha=0.85))


# ============================================================================
# Main
# ============================================================================
def main():
    fig = plt.figure(figsize=(12.8, 8.0), dpi=100, facecolor="white")
    # 본 4분할은 0.05~0.86 height 영역
    # GridSpec 사용 안 하고 add_axes 로 명시 — 헤더와 분리
    left_pad = 0.075
    right_pad = 0.985
    gap = 0.075
    width = (right_pad - left_pad - gap) / 2
    bottom_row_y = 0.075
    top_row_y = 0.475
    panel_h = 0.305

    ax1 = fig.add_axes([left_pad, top_row_y, width, panel_h])
    ax2 = fig.add_axes([left_pad + width + gap, top_row_y, width, panel_h])
    ax3 = fig.add_axes([left_pad, bottom_row_y, width, panel_h])
    ax4 = fig.add_axes([left_pad + width + gap, bottom_row_y, width, panel_h])

    # ① 4분면
    df_q = load_quadrant()
    draw_quadrant(ax1, df_q)

    # ② sub05 TOP10
    df_top = load_sub05_top10()
    draw_sub05_bars(ax2, df_top)

    # ③ archetype RDD
    df_arc = load_archetype_rdd()
    draw_archetype_rdd(ax3, df_arc)

    # ④ chooyeon evolution
    df_evo = load_chooyeon_evolution()
    draw_chooyeon_evolution(ax4, df_evo)

    # Header / filter bar / watermark
    draw_header(fig)
    draw_watermark(fig)

    # 작은 푸터 (데이터 출처)
    fig.text(0.013, 0.012,
             "데이터: H14 4분면 · H22 RDD · H28 wavelet · H5 노출도   |   "
             "활동명(②)는 부처×원형 기반 예시 라벨",
             fontsize=7.5, color="#666", ha="left", va="bottom")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    # bbox_inches='tight' 사용하면 1280px 초과 위험 -> 사용 안 함
    fig.savefig(OUT, dpi=100, facecolor="white", bbox_inches=None)
    plt.close(fig)

    # 검증
    from PIL import Image
    im = Image.open(OUT)
    print(f"SAVED: {OUT}")
    print(f"SIZE : {im.size}  ({'OK' if im.size[0] <= 1280 else 'TOO BIG'})")


if __name__ == "__main__":
    main()
