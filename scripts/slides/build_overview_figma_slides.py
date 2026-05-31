"""발표 오프닝 5장(deck 02–06페이지) Figma-ready SVG 생성.

확정 내러티브 (사고흐름형 + 두괄식):
  02 관찰 → 03 의문(측정 비대칭) → 04 ★주장(다크 hero)
  → 05 방법(메타 1장) → 06 읽는 법

디자인: tokens.svg(v1) 색 시스템 참조 — 웜 오프화이트 캔버스 + 슬레이트 텍스트.
무게/밀도: 큰 블록이 y240–780을 채우고 y858에 결정적 한 줄(기존 deck 채움 방식).
이전 버전(rhythm/execution/pa/scope/flow/interpretation 6장)을 교체.
"""
from pathlib import Path
from html import escape

OUT_DIR = Path("figma_exports/intro_sequence")
OUT_DIR.mkdir(exist_ok=True, parents=True)
OVERVIEW_DIR = Path("figma_exports/overview_slides")

# ── tokens.svg 색 시스템 ───────────────────────────────────────────────
CANVAS = "#FAFAF7"        # canvas — 웜 오프화이트
PANEL = "#F4F1EA"         # panel — 웜 카드
PANEL_COOL = "#F1F5F9"    # panel·cool — 쿨 카드
SIGNAL = "#C0392B"        # signal/600
SIGNAL_SOFT = "#FBEEEC"   # signal/100
CAUTION = "#B45309"       # caution/600
CAUTION_SOFT = "#FEF6E4"  # caution/100
NIGHT = "#0A0E27"         # night/900
NIGHT_PANEL = "#1A2148"   # night/700
NIGHT_LINE = "#2d3a5a"
INK = "#0F172A"           # ink/900 — 제목
INK_700 = "#334155"       # ink/700 — 본문
MUTED = "#64748B"         # ink/500 — 메타·라벨
LINE = "#CBD5E1"          # ink/300 — 테두리
BAR_GRAY = "#CBD5E1"      # 차트 비강조 막대
ORANGE = "#E67E22"        # 다크 hero 앵커 강조
WHITE = "#FFFFFF"
DARK_TEXT = "#FFFFFF"
DARK_SUB = "#b8c0d8"

TOTAL = 40
M = 80  # 좌우 마진


def svg_doc(body, dark=False):
    bg = NIGHT if dark else CANVAS
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1920 1080" '
        'font-family="Pretendard, -apple-system, BlinkMacSystemFont, sans-serif">\n'
        f'<rect width="1920" height="1080" fill="{bg}"/>\n'
        f"{body}\n</svg>\n"
    )


def text(x, y, s, size=18, fill=INK, weight=None, anchor=None, family=None,
         italic=False, spacing=None):
    a = [f'x="{x}"', f'y="{y}"', f'font-size="{size}"', f'fill="{fill}"']
    if weight:
        a.append(f'font-weight="{weight}"')
    if anchor:
        a.append(f'text-anchor="{anchor}"')
    if family:
        a.append(f'font-family="{family}"')
    if italic:
        a.append('font-style="italic"')
    if spacing is not None:
        a.append(f'letter-spacing="{spacing}"')
    return f"<text {' '.join(a)}>{escape(s)}</text>"


def multiline(x, y, lines, size=18, fill=INK_700, leading=30, weight=None,
              anchor=None):
    return "\n".join(
        text(x, y + i * leading, ln, size=size, fill=fill, weight=weight,
             anchor=anchor)
        for i, ln in enumerate(lines)
    )


# ── 공통 요소 ──────────────────────────────────────────────────────────
def header(title, subtitle="", dark=False):
    fill = DARK_TEXT if dark else INK
    sub = DARK_SUB if dark else MUTED
    out = [text(M, 110, title, size=44, fill=fill, weight="700")]
    if subtitle:
        out.append(text(M, 154, subtitle, size=22, fill=sub))
    return "\n".join(out)


def page_num(n, dark=False):
    fill = DARK_SUB if dark else MUTED
    return text(M, 1050, f"{n:02d} / {TOTAL}", size=14, fill=fill,
                family="monospace")


def trigger(s, dark=False, y=1035):
    c = DARK_SUB if dark else MUTED
    return text(1840, y, s + "  ↘", size=18, fill=c, anchor="end", italic=True)


def micro(x, y, s, dark=False):
    c = DARK_SUB if dark else MUTED
    return text(x, y, s, size=14, fill=c, weight="600", family="monospace",
                spacing="0.6")


def key_line(s, dark=False, y=860, size=26):
    c = DARK_TEXT if dark else INK
    return text(960, y, s, size=size, fill=c, weight="700", anchor="middle")


def panel(x, y, w, h, fill=PANEL, accent=False, bar=SIGNAL):
    out = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" '
           f'stroke="{LINE}" stroke-width="1" rx="10"/>')
    if accent:
        out += f'\n<rect x="{x}" y="{y}" width="4" height="{h}" fill="{bar}"/>'
    return out


def divider(x1, x2, y, color=LINE):
    return f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{color}" stroke-width="1"/>'


# ── 02 관찰 ───────────────────────────────────────────────────────────
def monthly_chart(x, y, w, h, values, hi, annot):
    vmax = max(values)
    n = len(values)
    slot = w / n
    bw = slot * 0.58
    base = y + h
    out = [divider(x, x + w, base)]
    for i, v in enumerate(values):
        bh = (v / vmax) * (h - 40)
        bx = x + i * slot + (slot - bw) / 2
        by = base - bh
        color = SIGNAL if i == hi else BAR_GRAY
        out.append(f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bw:.1f}" '
                   f'height="{bh:.1f}" fill="{color}" rx="3"/>')
        out.append(text(bx + bw / 2, base + 28, f"{i + 1}월", size=14,
                        fill=MUTED, anchor="middle"))
        if i in annot:
            ac = SIGNAL if i == hi else INK
            out.append(text(bx + bw / 2, by - 14, annot[i], size=20, fill=ac,
                            weight="800", anchor="middle"))
    return "\n".join(out)


def slide_observation():
    vals = [4, 4, 5, 4, 4, 6, 4, 4, 5, 6, 17.7, 37.2]
    reasons = ["미달 시 다음 해 예산 감축",
               "공공기관 경영평가의 지표명 그 자체",
               "경영실적 부진 시 기관장 해임 건의"]
    rrows = "\n".join(
        text(1252, 432 + i * 48, "·  " + r, size=21, fill=INK_700)
        for i, r in enumerate(reasons)
    )
    annot = {10: "17.7%", 11: "37.2%"}
    chart = monthly_chart(140, 330, 1000, 360, vals, hi=11, annot=annot)
    body = f"""
{header("집행률 100%, 이 숫자는 무엇을 보장하는가?",
        "회계 마감·평가 일정이 집행을 특정 월에 모은다.")}
{panel(M, 240, 1100, 540, fill=PANEL_COOL)}
{micro(116, 288, "사업당 100% 정규화 후 월별 집행 분포")}
{chart}
{text(116, 760, "11월 → 12월, 집행이 회계연도 끝에서 급등한다.", size=18, fill=INK_700)}
{panel(1220, 240, 620, 540, fill=PANEL, accent=True)}
{text(1252, 312, "집행률 100%", size=38, fill=INK, weight="800")}
{text(1252, 348, "한국 재정에서 가장 무거운 지표", size=18, fill=MUTED)}
{divider(1252, 1808, 376)}
{rrows}
{divider(1252, 1808, 560)}
{micro(1252, 600, "반복 제기되어 온 문제")}
{text(1252, 644, "“멀쩡한 길, 또 뜯는다? — 보도블록 공사”", size=21, fill=INK, weight="700", italic=True)}
{text(1252, 680, "전국뉴스", size=15, fill=MUTED)}
{key_line("회계와 평가가 만든 12월 정점 — 집행률 100%가 모든 판단의 기준이 된다.")}
{trigger("그렇다면, 이 숫자는 무엇을 못 보는가?")}
{page_num(2)}
"""
    return svg_doc(body)


# ── 03 의문 · 측정 비대칭 ─────────────────────────────────────────────
def compare_panel(x, label, items, note, accent=False):
    fill = SIGNAL_SOFT if accent else PANEL_COOL
    note_c = SIGNAL if accent else MUTED
    rows = "\n".join(
        text(x + 36, y, "·  " + it, size=24, fill=INK_700)
        for it, y in zip(items, (392, 456, 520))
    )
    return f"""
{panel(x, 240, 850, 540, fill=fill, accent=accent)}
{text(x + 36, 312, label, size=30, fill=INK, weight="700")}
{divider(x + 36, x + 814, 344)}
{rows}
{text(x + 36, 742, note, size=21, fill=note_c, weight="700")}
"""


def slide_blindspot():
    body = f"""
{header("측정 기준의 비대칭", "집행률 기준이 놓치는 정보 구조")}
{compare_panel(M, "기록되는 것", ["결재 시점", "집행 금액", "집행률 %"],
    "→  평가에 직접 반영된다")}
{compare_panel(990, "기록되지 않는 것",
    ["사업의 품질", "정책 목표 달성도", "사회적 결과(outcome)"],
    "→  평가에 남지 않는다", accent=True)}
{key_line("관측되는 것만 평가에 남고, 결과는 측정 밖에 머문다.")}
{trigger("그렇다면, 무엇을 보면 가려진 것이 드러나는가?")}
{page_num(3)}
"""
    return svg_doc(body)


# ── 04 ★주장 (다크 hero) ──────────────────────────────────────────────
def slide_thesis():
    line1 = (f'<text x="960" y="436" font-size="54" font-weight="800" '
             f'fill="{DARK_TEXT}" text-anchor="middle">'
             f'집행 패턴은 분야가 아니라 사업의 '
             f'<tspan fill="{ORANGE}">형태</tspan>에서 갈린다.</text>')
    body = f"""
{micro(960, 252, "본 분석의 주장", dark=True)}
<line x1="908" y1="278" x2="1012" y2="278" stroke="{SIGNAL}" stroke-width="3"/>
{line1}
{text(960, 512, "형태가 다르면, 측정과 관리도 형태별로 달라야 한다.", size=54, fill=DARK_TEXT, weight="800", anchor="middle")}
<rect x="660" y="568" width="600" height="74" fill="{NIGHT_PANEL}" stroke="{NIGHT_LINE}" rx="10"/>
{text(960, 616, "같은 12월, 점프 크기는 형태별로 1.1배 – 3.4배.", size=30, fill=ORANGE, weight="800", anchor="middle")}
{multiline(960, 712, [
    "P-A 모형이 이 구조를 설명하지만, 공개 재정 패널 위 유형별 실증은 드물었다 — 본 분석이 그 간격을 데이터로 메운다.",
    "그 결과는 유형별로 다른 접근의 이론적 토대이자 실증이 된다.",
], size=19, fill=DARK_SUB, leading=38, anchor="middle")}
{trigger("그럼, 어떻게 보았는가?", dark=True)}
{page_num(4, dark=True)}
"""
    return svg_doc(body, dark=True)


# ── 05 방법 (메타 1장) ────────────────────────────────────────────────
def stat_card(x, label, value, valsub, title, desc):
    return f"""
{panel(x, 240, 500, 440, fill=PANEL, accent=True)}
{micro(x + 32, 292, label)}
{text(x + 32, 376, value, size=56, fill=INK, weight="800")}
{text(x + 32, 416, valsub, size=18, fill=MUTED)}
{divider(x + 32, x + 468, 446)}
{text(x + 32, 492, title, size=24, fill=INK, weight="700")}
{multiline(x + 32, 532, desc, size=18, fill=INK_700, leading=30)}
"""


def flow_strip(x, y, w, steps):
    n = len(steps)
    gap = 70
    pw = (w - gap * (n - 1)) / n
    out = []
    for i, s in enumerate(steps):
        px = x + i * (pw + gap)
        out.append(f'<rect x="{px:.0f}" y="{y}" width="{pw:.0f}" height="64" '
                   f'fill="{PANEL_COOL}" stroke="{LINE}" rx="10"/>')
        out.append(text(px + pw / 2, y + 40, s, size=21, fill=INK,
                        weight="700", anchor="middle"))
        if i < n - 1:
            ex = px + pw
            out.append(f'<path d="M{ex + 16:.0f} {y + 32} L{ex + gap - 16:.0f} '
                       f'{y + 32}" stroke="{MUTED}" stroke-width="2.5"/>')
            out.append(f'<path d="M{ex + gap - 16:.0f} {y + 32} l-12 -7 l0 14 z" '
                       f'fill="{MUTED}"/>')
    return "\n".join(out)


def slide_method():
    body = f"""
{header("어떻게 보았는가 — 데이터·검증·산출물")}
{stat_card(M, "INPUT · 분석 자료", "21만", "activity-month cells",
    "열린재정 월별 집행", ["2015–2025, 활동·부처·분야·", "사업원형을 한 표로 묶는다."])}
{stat_card(710, "METHOD · 검증 축", "3", "RDD · 군집 · Wavelet/PSD",
    "세 기준으로 교차", ["회계연도 경계·사업 형태·", "시간 주기를 분리해 본다."])}
{stat_card(1340, "OUTPUT · 산출물", "3종", "4분면 · Top-50 · 모니터링",
    "유형별 차등 접근으로", ["확인 후보를 좁히고 다른", "접근의 근거로 잇는다."])}
{flow_strip(M, 712, 1760, ["원자료 패턴", "유형별 검증", "활용 산출물"])}
{key_line("원자료에서 활용 산출물까지, 같은 패널 위에서 본다.", y=850)}
{text(960, 902, "본 분석은 부정·비위를 단정하지 않는다 — 반복 패턴과 결과 격차로 점검 후보를 좁힌다.", size=17, fill=MUTED, anchor="middle")}
{trigger("읽기 전에, 세 가지만.")}
{page_num(5)}
"""
    return svg_doc(body)


# ── 06 읽는 법 ────────────────────────────────────────────────────────
def reading_card(x, label, title, body_lines):
    return f"""
{panel(x, 240, 500, 500, fill=PANEL, accent=True)}
{micro(x + 32, 300, label)}
{text(x + 32, 364, title, size=27, fill=INK, weight="700")}
{divider(x + 32, x + 468, 396)}
{multiline(x + 32, 452, body_lines, size=20, fill=INK_700, leading=34)}
"""


def slide_reading():
    body = f"""
{header("이 분석을 읽는 세 가지 기준")}
{reading_card(M, "01 · 단위", "분야가 아니라 사업 형태",
    ["같은 분야 안에서도 시점", "행동이 갈린다. 형태를", "분석의 단위로 삼는다."])}
{reading_card(710, "02 · 자세", "판정이 아니라 점검 순서",
    ["결론은 부정·비위 단정이", "아니라 먼저 확인할", "우선 점검 순서다."])}
{reading_card(1340, "03 · 도구", "차이는 오류가 아닌 보완",
    ["도구 간 결과 차이는 한", "현상을 여러 각도로 비춘", "상호 보완으로 읽는다."])}
{key_line("형태를 단위로, 판정이 아닌 점검 순서로 읽는다.")}
{trigger("그럼, 형태부터 본다.")}
{page_num(6)}
"""
    return svg_doc(body)


# ── 생성 ──────────────────────────────────────────────────────────────
OUTPUTS = {
    "slide-02-observation.svg": slide_observation,
    "slide-03-blindspot.svg": slide_blindspot,
    "slide-04-thesis.svg": slide_thesis,
    "slide-05-method.svg": slide_method,
    "slide-06-reading.svg": slide_reading,
}

SUPERSEDED = [
    OVERVIEW_DIR / "slide-05-project-scope.svg",
    OVERVIEW_DIR / "slide-06-analysis-flow.svg",
    OVERVIEW_DIR / "slide-07-interpretation-criteria.svg",
]


def main():
    for name, render in OUTPUTS.items():
        (OUT_DIR / name).write_text(render(), encoding="utf-8")
    removed = sum(1 for p in SUPERSEDED if p.exists() and (p.unlink() or True))
    print(f"generated {len(OUTPUTS)} slides in {OUT_DIR}")
    if removed:
        print(f"removed {removed} superseded files")


if __name__ == "__main__":
    main()
