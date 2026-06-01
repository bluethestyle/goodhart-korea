"""논문 차트 공통 스타일 — 모든 paper figure 생성기(redo_fig*.py 등)가 import.

목적: 차트 간 폰트·크기·범례 스타일을 통일해 PDF 삽입 시 시각적 일관성 확보.
- 폰트: Pretendard (paper/fonts/, CLAUDE.md 프로젝트 표준). 없으면 Malgun Gothic fallback.
- 폰트 크기: A4 본문 폭(약 6.3 inch) 기준 통일값. 스크립트별 제각각 크기 제거.
- 범례: 반투명(framealpha 0.85)으로 선/점 가림 완화.

사용:
    from _paper_style import apply_paper_style
    apply_paper_style()
"""
import os
import matplotlib as mpl
import matplotlib.pyplot as plt  # noqa: F401  (import 보장용)
from matplotlib import font_manager

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_FONTS = os.path.join(_ROOT, "paper", "fonts")

_PRETENDARD = [
    "Pretendard-Regular.otf", "Pretendard-Medium.otf",
    "Pretendard-SemiBold.otf", "Pretendard-Bold.otf",
]


def _register_pretendard():
    ok = False
    for fn in _PRETENDARD:
        p = os.path.join(_FONTS, fn)
        if os.path.exists(p):
            try:
                font_manager.fontManager.addfont(p)
                ok = True
            except Exception:
                pass
    return ok


def apply_paper_style(base=11):
    """공통 논문 스타일 적용. 반환: Pretendard 등록 성공 여부."""
    has_pre = _register_pretendard()
    family = (["Pretendard"] if has_pre
              else ["Malgun Gothic", "AppleGothic", "NanumGothic"]) + ["DejaVu Sans"]
    mpl.rcParams.update({
        "font.family": family,
        "font.size": base,
        "axes.titlesize": base + 1.5,
        "axes.titleweight": "semibold",
        "axes.labelsize": base,
        "xtick.labelsize": base - 1.5,
        "ytick.labelsize": base - 1.5,
        "legend.fontsize": base - 1.5,
        "figure.titlesize": base + 2,
        "lines.linewidth": 1.6,
        "lines.markersize": 6,
        "axes.linewidth": 0.8,
        "axes.edgecolor": "#444444",
        "legend.frameon": True,
        "legend.framealpha": 0.85,
        "legend.edgecolor": "#cccccc",
        "legend.fancybox": True,
        "legend.borderpad": 0.4,
        "mathtext.default": "regular",
        "axes.unicode_minus": False,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
    })
    return has_pre
