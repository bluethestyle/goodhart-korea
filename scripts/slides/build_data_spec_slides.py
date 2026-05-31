"""데이터 명세 2장 Figma-ready SVG 와이어프레임 생성.

스토리보드 전·후반 구조에 맞춘 두 개의 '데이터 명세 표' 슬라이드:
  ① 재정 집행 데이터 명세  — Slide 4 → 5 사이 삽입.
     (전반부: 재정데이터 자체만으로 분석하는 구간의 토대)
  ② 외부 Outcome 데이터 명세 — Slide 31 → 32 사이 삽입.
     (후반부: 외부 결과지표와 엮어 분석하는 구간의 토대)

수치는 data/warehouse.duckdb monthly_exec 실측 기준:
  416,517행 · 17컬럼 · 2015–2026(분석 2015–2025/132개월) · 활동 1,720(공통 1,557)
  · 부처 72 · 분야 16.
디자인 토큰은 build_overview_figma_slides.py(tokens.svg v1)와 동일.
"""
from pathlib import Path
from html import escape

OUT_DIR = Path("figma_exports/data_spec")
OUT_DIR.mkdir(exist_ok=True, parents=True)

# ── tokens.svg 색 시스템 (build_overview_figma_slides.py와 동일) ──────────
CANVAS = "#FAFAF7"
PANEL = "#F4F1EA"
PANEL_COOL = "#F1F5F9"
SIGNAL = "#C0392B"
SIGNAL_SOFT = "#FBEEEC"
CAUTION = "#B45309"
CAUTION_SOFT = "#FEF6E4"
NIGHT = "#0A0E27"
NIGHT_PANEL = "#1A2148"
NIGHT_LINE = "#2d3a5a"
INK = "#0F172A"
INK_700 = "#334155"
MUTED = "#64748B"
LINE = "#CBD5E1"
BAR_GRAY = "#CBD5E1"
ORANGE = "#E67E22"
WHITE = "#FFFFFF"
DARK_SUB = "#b8c0d8"

TOTAL = 40
M = 80
MONO = "ui-monospace, SFMono-Regular, Menlo, monospace"


def svg_doc(body):
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1920 1080" '
        'font-family="Pretendard, -apple-system, BlinkMacSystemFont, sans-serif">\n'
        f'<rect width="1920" height="1080" fill="{CANVAS}"/>\n'
        f"{body}\n</svg>\n"
    )


def text(x, y, s, size=18, fill=INK, weight=None, anchor=None, family=None,
         italic=False, spacing=None, strike=False):
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
    if strike:
        a.append(f'text-decoration="line-through" '
                 f'text-decoration-color="{MUTED}"')
    return f"<text {' '.join(a)}>{escape(s)}</text>"


def multiline(x, y, lines, size=18, fill=INK_700, leading=30, weight=None,
              anchor=None, family=None):
    return "\n".join(
        text(x, y + i * leading, ln, size=size, fill=fill, weight=weight,
             anchor=anchor, family=family)
        for i, ln in enumerate(lines)
    )


def header(title, subtitle="", insert_note=""):
    out = [text(M, 104, title, size=44, fill=INK, weight="700")]
    if subtitle:
        out.append(text(M, 148, subtitle, size=22, fill=MUTED))
    if insert_note:
        out.append(text(1840, 104, insert_note, size=15, fill=SIGNAL,
                        weight="700", anchor="end", family=MONO,
                        spacing="0.5"))
    return "\n".join(out)


def page_num(label):
    return text(M, 1050, label, size=14, fill=MUTED, family=MONO)


def trigger(s, y=1035):
    return text(1840, y, s, size=17, fill=MUTED, anchor="end")


def key_line(s, y=988, size=24):
    return text(960, y, s, size=size, fill=INK, weight="700", anchor="middle")


def panel(x, y, w, h, fill=PANEL, accent=False, bar=SIGNAL, rx=10):
    out = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" '
           f'stroke="{LINE}" stroke-width="1" rx="{rx}"/>')
    if accent:
        out += f'\n<rect x="{x}" y="{y}" width="4" height="{h}" fill="{bar}" rx="2"/>'
    return out


def divider(x1, x2, y, color=LINE, w=1):
    return (f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{color}" '
            f'stroke-width="{w}"/>')


def micro(x, y, s, fill=MUTED):
    return text(x, y, s, size=14, fill=fill, weight="700", family=MONO,
                spacing="0.6")


# ── KPI 칩 스트립 ─────────────────────────────────────────────────────────
def kpi_strip(x, y, w, chips):
    """chips: [(value, label, accent_bool), ...]"""
    n = len(chips)
    gap = 18
    cw = (w - gap * (n - 1)) / n
    h = 92
    out = []
    for i, (val, lab, acc) in enumerate(chips):
        cx = x + i * (cw + gap)
        fill = SIGNAL_SOFT if acc else PANEL
        vcol = SIGNAL if acc else INK
        out.append(panel(cx, y, cw, h, fill=fill, accent=acc, rx=8))
        out.append(text(cx + cw / 2, y + 50, val, size=34, fill=vcol,
                        weight="800", anchor="middle"))
        out.append(text(cx + cw / 2, y + 78, lab, size=15, fill=MUTED,
                        anchor="middle"))
    return "\n".join(out)


# ── 스키마/소스 테이블 ─────────────────────────────────────────────────────
def table(x, y, w, cols, groups, row_h=44, head_h=40, band_adv=36):
    """범용 테이블.
    cols: [(label, rel_width, anchor), ...]  (rel_width 합 = 1)
    groups: [(group_title, [ (cell0, cell1, ..., star_bool), ... ]), ...]
    """
    out = []
    # 컬럼 x 위치
    xs, acc = [], 0.0
    for _, rw, _a in cols:
        xs.append(x + acc * w)
        acc += rw
    pad = 16
    # 헤더
    out.append(divider(x, x + w, y - 6, color=INK_700, w=1.5))
    for (lab, _rw, an), cxp in zip(cols, xs):
        tx = cxp + pad if an != "end" else cxp + (cols[xs.index(cxp)][1]) * 0  # noqa
    # 헤더 라벨
    for (lab, rw, an), cxp in zip(cols, xs):
        if an == "end":
            tx = cxp + rw * w - pad
        else:
            tx = cxp + pad
        out.append(text(tx, y + 18, lab, size=14, fill=MUTED, weight="700",
                        anchor=an if an else None, family=MONO, spacing="0.4"))
    out.append(divider(x, x + w, y + head_h - 4, color=LINE, w=1))

    cy = y + head_h
    for gi, (gtitle, rows) in enumerate(groups):
        # 그룹 라벨 밴드
        out.append(f'<rect x="{x}" y="{cy}" width="{w}" height="30" '
                   f'fill="{PANEL}" rx="4"/>')
        out.append(text(x + pad, cy + 21, gtitle, size=14, fill=INK_700,
                        weight="800", spacing="0.4"))
        cy += band_adv
        for row in rows:
            *cells, star = row
            dim = star == "dim"
            if star is True:
                out.append(f'<rect x="{x}" y="{cy - 2}" width="{w}" '
                           f'height="{row_h}" fill="{SIGNAL_SOFT}" rx="4"/>')
                out.append(f'<rect x="{x}" y="{cy - 2}" width="4" '
                           f'height="{row_h}" fill="{SIGNAL}" rx="2"/>')
            for ci, (cell, (lab, rw, an)) in enumerate(zip(cells, cols)):
                cxp = xs[ci]
                if an == "end":
                    tx = cxp + rw * w - pad
                else:
                    tx = cxp + pad
                fam = MONO if ci == 0 else None
                col = INK if ci == 0 else INK_700
                wt = "700" if ci == 0 else None
                sz = 17 if ci == 0 else 18
                if star is True and ci == 0:
                    col = SIGNAL
                if dim:
                    col = "#AEB4BD"
                out.append(text(tx, cy + 28, cell, size=sz, fill=col,
                                weight=wt, anchor=an if an else None,
                                family=fam,
                                strike=(dim and ci == 0)))
            out.append(divider(x, x + w, cy + row_h - 2, color="#E6E2D8"))
            cy += row_h
        cy += 10
    return "\n".join(out), cy


# ── 깔때기(분류 위계) ──────────────────────────────────────────────────────
def funnel(x, y, w, steps):
    """steps: [(label, value), ...] 위→아래 좁아지는 분류 위계."""
    out = []
    n = len(steps)
    rh = 52
    gap = 14
    for i, (lab, val) in enumerate(steps):
        shrink = i * (w * 0.10)
        bx = x + shrink / 2
        bw = w - shrink
        by = y + i * (rh + gap)
        last = i == n - 1
        fill = SIGNAL_SOFT if last else PANEL_COOL
        bar = SIGNAL if last else MUTED
        out.append(panel(bx, by, bw, rh, fill=fill, accent=True, bar=bar, rx=8))
        out.append(text(bx + 20, by + 32, lab, size=18,
                        fill=SIGNAL if last else INK, weight="700"))
        out.append(text(bx + bw - 18, by + 32, val, size=20,
                        fill=SIGNAL if last else INK_700, weight="800",
                        anchor="end", family=MONO))
        if not last:
            ax = x + w / 2
            ay = by + rh + 1
            out.append(f'<path d="M{ax} {ay} l-7 0 l7 11 l7 -11 z" '
                       f'fill="{MUTED}"/>')
    return "\n".join(out)


# ══════════════════════════════════════════════════════════════════════════
# ① 재정 집행 데이터 명세  (Slide 4 → 5 사이)
# ══════════════════════════════════════════════════════════════════════════
def slide_fiscal_spec():
    chips = [
        ("416,517", "활동×월 행", False),
        ("9", "분석 사용 컬럼 (수집 17)", True),
        ("132", "개월 (2015–2025)", False),
        ("1,557", "세부사업 (분석 공통)", True),
        ("72", "부처·기관", False),
        ("16", "분야", False),
    ]
    cols = [
        ("COLUMN", 0.28, None),
        ("의미", 0.40, None),
        ("값 · 비고", 0.32, "end"),
    ]
    # star: True=핵심 강조 / "dim"=수집했으나 분석 미사용 / False=일반 사용
    groups = [
        ("시점 식별", [
            ("FSCL_YY", "회계연도", "2015 – 2026", False),
            ("EXE_M", "집행 월", "1 – 12", False),
        ]),
        ("조직·회계·분류 위계", [
            ("OFFC_CD · NM", "부처·기관", "72개", False),
            ("FSCL_CD · NM", "회계·기금 구분", "114개 회계·기금 · 분석 미사용", "dim"),
            ("FLD_CD · NM", "분야", "16개", False),
            ("SECT_CD · NM", "부문", "분석 미사용 (보조)", "dim"),
            ("PGM_CD · NM", "프로그램", "85개", False),
            ("ACTV_CD · NM", "세부사업 (분석 최소단위)", "1,707 → 공통 1,557", True),
        ]),
        ("금액 (원)", [
            ("ANEXP_BDG_CAMT", "예산현액", "집행률 분모", False),
            ("EP_AMT", "월별 집행액", "★ 분석 핵심 변수", True),
            ("THISM_AGGR_EP_AMT", "당월 누계 집행", "집행률 산출", False),
        ]),
    ]
    tbl, _ = table(M, 350, 1080, cols, groups, row_h=38, band_adv=34)

    rx = 1230
    rw = 610
    right = f"""
{panel(rx, 290, rw, 250, fill=PANEL_COOL, accent=True, bar=ORANGE)}
{micro(rx + 28, 330, "데이터 개요")}
{text(rx + 28, 364, "dBrain+ / 열린재정", size=24, fill=INK, weight="800")}
{divider(rx + 28, rx + rw - 28, 384)}
{multiline(rx + 28, 420, [
    "출처 · 열린재정 API (VWFOEM) · dBrain+ / KODAS",
    "기간 · 2015–2025 · 월별 132개월 (원자료 ~2026)",
    "대상 · 세부사업 1,557개 (11년 공통, 신설·폐지 제외)",
    "위계 · 분야16 → 부문86 → 프로그램85 → 세부사업",
    "갱신 · 매월 결산 후",
], size=16, fill=INK_700, leading=26)}
{panel(rx, 556, rw, 384, fill=WHITE)}
{micro(rx + 28, 596, "분류 항목 (실제 값)")}
{text(rx + 28, 638, "분야 16", size=16, fill=INK, weight="800")}
{multiline(rx + 28, 666, [
    "사회복지·일반지방행정·산업중기·농림수산·교통물류·",
    "보건·공공질서·문화관광·국방·과학기술·교육·환경·",
    "통일외교·통신·국토지역개발 (+예비비)",
], size=14, fill=INK_700, leading=24)}
{text(rx + 28, 758, "회계·기금 114", size=16, fill=INK, weight="800")}
{multiline(rx + 28, 786, [
    "일반회계 · 국민연금기금 · 주택도시기금 ·",
    "교통시설특별회계 · 고용보험기금 … 외 다수",
], size=14, fill=INK_700, leading=24)}
{text(rx + 28, 856, "부처·기관 72", size=16, fill=INK, weight="800")}
{multiline(rx + 28, 884, [
    "보건복지부 · 기획재정부 · 국토교통부 ·",
    "교육부 · 행정안전부 · 국방부 … 외",
], size=14, fill=INK_700, leading=24)}
"""
    body = f"""
{header("재정 집행 데이터 (monthly_exec)",
        "열린재정/dBrain+ 월별 집행 패널, 2015–2025. 전반부 분석의 단일 원천 데이터.",
        insert_note="삽입 위치 · Slide 4 → 5")}
{kpi_strip(M, 196, 1760, chips)}
{panel(M, 300, 1080, 640, fill=WHITE)}
{text(M + 24, 334, "테이블 스키마 — monthly_exec", size=20, fill=INK, weight="700")}
{text(M + 1056, 334, "수집 17컬럼 · 분석 9컬럼 (회계구분·부문 제외)", size=15, fill=MUTED, anchor="end", family=MONO)}
{tbl}
{right}
{divider(M, 1840, 956)}
{key_line("외부 지표 없이 이 패널만으로 집행 시점 분포·집행률·분류 단위 분석을 수행한다.", size=22)}
{trigger("다음 — 월별 집행 분포 (Slide 5)")}
{page_num("재정 집행 데이터 · 04–05")}
"""
    return svg_doc(body)


# ══════════════════════════════════════════════════════════════════════════
# ② 외부 Outcome 데이터 명세  (Slide 31 → 32 사이)
# ══════════════════════════════════════════════════════════════════════════
def slide_outcome_spec():
    chips = [
        ("15", "분야 결과지표 확보", True),
        ("14", "매개 검정 분야", False),
        ("5", "데이터 출처", False),
        ("1990–2025", "지표 시계열 범위", False),
    ]
    cols = [
        ("분야", 0.20, None),
        ("결과지표 (변수 · 한글 설명)", 0.50, None),
        ("통계표 · 지표 ID", 0.30, "end"),
    ]
    groups = [
        ("KOSIS · 통계청", [
            ("사회복지", "wealth_gini · 순자산 지니계수", "DT_1HDAAD04", False),
            ("보건", "life_expectancy · 0세 기대여명", "DT_1B41", False),
            ("산업·중기", "industry_production_index · 전산업생산지수", "DT_1JH20201", False),
            ("문화·관광", "foreign_tourists_total · 외래 관광객 수", "DT_113_…", False),
            ("교육", "private_edu_hours · 주당 사교육 시간", "DT_1PE103", False),
            ("국토·지역", "housing_supply · 주택보급률", "DT_MLTM_2100", False),
            ("농림수산", "farm_income · 농가소득", "DT_1EA1501 ★", True),
        ]),
        ("공공데이터포털 · 부처 · OECD", [
            ("교통·물류", "traffic_deaths · 교통사고 사망자", "도로교통공단", False),
            ("일반·지방행정", "fiscal_indep_natl · 재정자립도", "행정안전부", False),
            ("과학기술", "patent_apps_total · 특허출원 건수", "특허청", False),
            ("통신", "broadband_per_100 · 100명당 초고속망", "과기정통부", False),
        ]),
        ("GIR · e-나라지표", [
            ("환경", "ghg_total · 온실가스 총배출량", "GIR 국가인벤토리", False),
            ("통일·외교", "oda_total · ODA 원조규모", "e-나라 idx 1687", False),
            ("공공질서", "crime_occurrence · 총범죄 발생 건수", "e-나라 idx 1606", False),
            ("국방", "defense_op_margin · 방산업체 경영실태", "e-나라 idx 1703", False),
        ]),
    ]
    tbl, _ = table(M, 322, 1760, cols, groups, row_h=29, band_adv=31, head_h=34)

    body = f"""
{header("분야별 결과지표(Outcome) 매핑",
        "각 정책 분야에 어떤 결과지표를, 어디서 확보했는가 — 분야별 1개 대표 지표.",
        insert_note="삽입 위치 · Slide 31 → 32 (전환 3/3)")}
{kpi_strip(M, 196, 1760, chips)}
{panel(M, 290, 1760, 588, fill=WHITE)}
{text(M + 24, 314, "분야 → 결과지표 → 출처 (실측 매핑)", size=18, fill=INK, weight="700")}
{text(M + 1736, 314, "★ = 매개효과 유의 (농림수산) · 거시 통제: CPI(ECOS 901Y009)", size=14, fill=MUTED, anchor="end", family=MONO)}
{tbl}
{divider(M, 1840, 904)}
{key_line("15개 분야에 1개 대표 결과지표를 매핑해 확보, 그중 14개 분야에서 매개효과를 검정했다.", y=946, size=21)}
{text(960, 980, "분야별 보조지표·정확한 시계열·다운로드 링크는 부록 App-DATA / data/external/SOURCES.md.", size=15, fill=MUTED, anchor="middle")}
{trigger("다음 — 집행률과 결과의 분산 (Slide 32)", y=1012)}
{page_num("분야별 결과지표 · 전환 3/3")}
"""
    return svg_doc(body)


# ── 연결 화살표 (mediation 다이어그램용) ──────────────────────────────────
def connect(x1, y1, x2, y2, color=MUTED, w=2.5):
    import math
    ang = math.atan2(y2 - y1, x2 - x1)
    hx, hy = x2 - 11 * math.cos(ang), y2 - 11 * math.sin(ang)
    p1 = (hx - 7 * math.cos(ang - 0.5), hy - 7 * math.sin(ang - 0.5))
    p2 = (hx - 7 * math.cos(ang + 0.5), hy - 7 * math.sin(ang + 0.5))
    return (f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" '
            f'stroke="{color}" stroke-width="{w}"/>'
            f'<path d="M{x2:.0f} {y2:.0f} L{p1[0]:.0f} {p1[1]:.0f} '
            f'L{p2[0]:.0f} {p2[1]:.0f} z" fill="{color}"/>')


def node(x, y, w, h, title, sub, fill, bar, tcol=INK):
    box = panel(x, y, w, h, fill=fill, accent=True, bar=bar)
    t = text(x + w / 2, y + h / 2 - 4, title, size=22, fill=tcol,
             weight="800", anchor="middle")
    s = text(x + w / 2, y + h / 2 + 24, sub, size=15, fill=MUTED,
             anchor="middle")
    return f"{box}\n{t}\n{s}"


# ══════════════════════════════════════════════════════════════════════════
# 전환 1/3 — 전반부 종합 (세 렌즈) → 후반부 질문  (Slide 31 → 32)
# ══════════════════════════════════════════════════════════════════════════
def slide_synthesis():
    cy, ch = 250, 366
    cw, gap = 560, 40
    xs = [M, M + cw + gap, M + 2 * (cw + gap)]

    def lens_card(x, kicker, name, tool, value, vlabel, subs, bar):
        out = [panel(x, cy, cw, ch, fill=PANEL_COOL, accent=True, bar=bar)]
        out.append(micro(x + 28, cy + 46, kicker, fill=bar))
        out.append(text(x + 28, cy + 92, name, size=25, fill=INK, weight="800"))
        out.append(text(x + 28, cy + 122, tool, size=14, fill=MUTED,
                        family=MONO))
        out.append(divider(x + 28, x + cw - 28, cy + 142))
        out.append(text(x + 28, cy + 222, value, size=50, fill=bar,
                        weight="800"))
        out.append(text(x + 28, cy + 258, vlabel, size=18, fill=INK_700,
                        weight="700"))
        for i, s in enumerate(subs):
            out.append(text(x + 28, cy + 300 + i * 28, s, size=15, fill=MUTED))
        return "\n".join(out)

    cards = "\n".join([
        lens_card(xs[0], "관점 1 · 형태", "형태 (Shape)",
                  "TDA · UMAP · HDBSCAN", "4", "사업 체질 (archetype)",
                  ["1,557 세부사업을 월별 패턴으로", "자동 군집 — 행정 분류와 무관"],
                  INK_700),
        lens_card(xs[1], "관점 2 · 단절", "단절 (Discontinuity)",
                  "RDD (회귀불연속)", "×1.9", "12월 1일 집행 점프",
                  ["회계연도 말 결재 집중", "자산취득형(C1)은 ×3.4"], SIGNAL),
        lens_card(xs[2], "관점 3 · 주기", "주기 (Cycle)",
                  "FFT · Wavelet · NeuralProphet", "+554%", "연주기 진폭 11년 강화",
                  ["출연금형(C2) 분기·연말 주기", "시간이 갈수록 진폭 확대"], ORANGE),
    ])

    body = f"""
{header("전반부 종합 — 세 분석 관점이 한 방향을 가리킨다",
        "행정 분류 대신 사업 형태로 본 집행 시점. 세 분석 관점의 발견을 한 화면에 모은다.",
        insert_note="삽입 위치 · Slide 31 → 32 (전환 1/3)")}
{cards}
{text(960, 666, "세 관점 모두 — 집행 시점이 회계연도 말에 집중됨을 가리킨다 (output 차원의 일관된 신호).", size=21, fill=INK, weight="700", anchor="middle")}
{panel(M, 692, 1760, 92, fill=SIGNAL_SOFT, accent=True, bar=SIGNAL)}
{micro(M + 28, 730, "전환 질문", fill=SIGNAL)}
{text(M + 200, 736, "이 집행 시점 집중이 정책 결과(outcome)와 연관되는가? — 후반부에서 검정한다.", size=21, fill=INK, weight="700")}
{divider(M, 1840, 842)}
{key_line("전반부는 집행 시점 집중을 세 방식으로 확인했다. 후반부는 그 집중과 결과의 통계적 연관을 검정한다.", y=896, size=22)}
{trigger("다음 — 매개모형과 검정 범위")}
{page_num("전반부 종합 · 전환 1/3")}
"""
    return svg_doc(body)


# ══════════════════════════════════════════════════════════════════════════
# 브릿지 2/2 — 결과로 가는 통로 (인과 가설)  (Slide 31 → 32)
# ══════════════════════════════════════════════════════════════════════════
def slide_pathways():
    # 매개 다이어그램: X → M(시점 압력) → Y  (Slide 33과 동일 구조)
    nh = 116
    ny = 234
    xn = (M, ny, 300, nh)
    mn = (810, ny, 300, nh)
    yn = (1460, ny, 300, nh)
    diagram = f"""
{node(*xn, "12월 집중도", "원인 · X", SIGNAL_SOFT, SIGNAL, SIGNAL)}
{node(*mn, "시점 압력", "매개 · M", PANEL, ORANGE)}
{node(*yn, "정책 결과", "outcome · Y", PANEL_COOL, MUTED)}
{connect(M + 300, ny + nh / 2, 810, ny + nh / 2, color=INK_700, w=2.5)}
{connect(1110, ny + nh / 2, 1460, ny + nh / 2, color=INK_700, w=2.5)}
{text(605, ny + nh / 2 - 14, "a", size=18, fill=MUTED, anchor="middle", family=MONO, italic=True)}
{text(1285, ny + nh / 2 - 14, "b", size=18, fill=MUTED, anchor="middle", family=MONO, italic=True)}
{text(960, ny - 22, "Sobel 검정 — 간접효과 a·b (Slide 33)", size=14, fill=MUTED, anchor="middle", family=MONO)}
"""
    # M이 결과를 갉는 세 통로 + 증거 위계
    rows = [
        ("①", "졸속 집행", "마감 직전 집중 집행 → 품질·정산 점검 약화 (결재가 공정에 선행)",
         "정성 근거 · Act 3 RDD (S24–25)", CAUTION, CAUTION_SOFT),
        ("②", "시점 불일치", "집행 시점이 계절·수요 시점과 어긋남 → 결과 지연 (농림수산)",
         "직접 검정 · Act 5 매개 (S33–34)", SIGNAL, SIGNAL_SOFT),
        ("③", "단가 상승", "연말 입찰 집중 → 계약 단가 상승 가능 (계약 단가 데이터 없음)",
         "검정 불가 · 데이터 부재 (L-M 2017 참조)", MUTED, PANEL),
    ]
    rx0, rw0, rh0 = M, 1760, 78
    rys = [430, 518, 606]
    rbox = [micro(rx0, 408, "이론상 가능한 메커니즘 (L-M 2017) — 본 데이터의 검정 가능 여부")]
    for (num, name, desc, tag, c, soft), ry in zip(rows, rys):
        tested = c == SIGNAL
        rbox.append(panel(rx0, ry, rw0, rh0, fill=soft if tested else WHITE,
                          accent=True, bar=c))
        rbox.append(text(rx0 + 28, ry + 48, num, size=26, fill=c, weight="800"))
        rbox.append(text(rx0 + 72, ry + 34, name, size=21, fill=INK,
                        weight="800"))
        rbox.append(text(rx0 + 72, ry + 60, desc, size=17, fill=INK_700))
        # 증거 태그 pill (우측)
        pw = 360
        px = rx0 + rw0 - pw - 20
        rbox.append(f'<rect x="{px}" y="{ry + 22}" width="{pw}" height="34" '
                    f'rx="17" fill="{c if tested else WHITE}" '
                    f'stroke="{c}" stroke-width="1.4"/>')
        rbox.append(text(px + pw / 2, ry + 44, tag, size=15,
                        fill=WHITE if tested else c, weight="700",
                        anchor="middle"))
    rbox = "\n".join(rbox)

    body = f"""
{header("결과 영향의 검정 범위 — 3개 메커니즘 중 1개만 측정 가능",
        "후반부는 결과 영향을 ‘입증’하지 않는다. 측정되는 한 메커니즘만 검정하고, 나머지는 측정 한계로 둔다.",
        insert_note="삽입 위치 · Slide 31 → 32 (전환 2/3)")}
{diagram}
{rbox}
{panel(M, 704, 1760, 96, fill=CAUTION_SOFT, accent=True, bar=CAUTION)}
{micro(M + 28, 738, "측정 공백 — 약점이 아니라 논지", fill=CAUTION)}
{multiline(M + 28, 766, [
    "셋 중 데이터로 검정되는 것은 ②뿐. ①은 정성 근거(Act 3 RDD), ③은 계약 단가 데이터가 없어 검정 불가. 분야 outcome도 집계 지표라 사업 단위 효과를 일부만 포착한다.",
    "이렇게 ‘대부분 측정되지 않는다’는 사실 자체가 — 평가가 결과를 보지 못한다는 전반부 논지를 뒷받침한다.",
], size=16, fill=INK_700, leading=28)}
{divider(M, 1840, 840)}
{key_line("결과까지의 영향은 대부분 측정되지 않는다 — 검정은 측정되는 ② 하나로 한정하고, 그 측정 공백을 논지의 일부로 받아들인다.", y=892, size=20)}
{trigger("다음 — 결과지표 데이터 출처")}
{page_num("결과 영향의 검정 범위 · 전환 2/3")}
"""
    return svg_doc(body)


# ══════════════════════════════════════════════════════════════════════════
# Act 5 소결 — 분야별 매개효과 검정 결과  (Slide 35 → 36)
# ══════════════════════════════════════════════════════════════════════════
def slide_iceberg():
    # 14분야 매개 검정 결과 그리드 (1 유의 / 13 비유의)
    gx, gy = 120, 360
    cs, gap, cols = 84, 14, 7
    sig_idx = 8                      # 농림수산 강조 셀
    cells = []
    for i in range(14):
        c, r = i % cols, i // cols
        x = gx + c * (cs + gap)
        y = gy + r * (cs + 40)
        if i == sig_idx:
            cells.append(f'<rect x="{x}" y="{y}" width="{cs}" height="{cs}" '
                         f'rx="10" fill="{SIGNAL}"/>')
            cells.append(text(x + cs / 2, y + cs / 2 + 6, "유의", size=17,
                              fill=WHITE, weight="800", anchor="middle"))
            cells.append(text(x + cs / 2, y + cs + 26, "농림수산", size=15,
                              fill=SIGNAL, weight="700", anchor="middle"))
        else:
            cells.append(f'<rect x="{x}" y="{y}" width="{cs}" height="{cs}" '
                         f'rx="10" fill="{WHITE}" stroke="{LINE}" '
                         f'stroke-width="1.5"/>')
    grid = "\n".join(cells)
    leg_y = gy + 2 * (cs + 40) + 24
    legend = f"""
<rect x="{gx}" y="{leg_y}" width="22" height="22" rx="5" fill="{SIGNAL}"/>
{text(gx + 32, leg_y + 17, "유의 1 (Sobel p<0.01)", size=15, fill=INK_700)}
<rect x="{gx + 240}" y="{leg_y}" width="22" height="22" rx="5" fill="{WHITE}" stroke="{LINE}" stroke-width="1.5"/>
{text(gx + 272, leg_y + 17, "비유의 13", size=15, fill=INK_700)}
"""
    rx = 900
    rw = 940
    body = f"""
{header("결과 영향의 탐색 — 한 분야의 존재 증명과 측정 공백",
        "주 발견은 전반부 집행 패턴(광범위·견고). 결과 영향은 보조 탐색이며, 일반적 훼손을 주장하지 않는다.",
        insert_note="삽입 위치 · Slide 35 → 36 (Act 5 소결)")}
{micro(gx, 326, "분야별 매개 검정 (n=14)")}
{grid}
{legend}
{panel(rx, 300, rw, 230, fill=SIGNAL_SOFT, accent=True, bar=SIGNAL)}
{micro(rx + 32, 342, "유의 분야 — 농림수산 · 존재 증명 (시사적)", fill=SIGNAL)}
{multiline(rx + 32, 384, [
    "Sobel z=−2.897 (p=0.004) · CI[−0.41,−0.09] · CPI·LOO 견고.",
    "단 N≈9(연 단위)로 결정적이 아닌 시사적.",
    "‘회계 안에서만 도는 무해한 현상’이라는 반론을 깨는 한 사례.",
], size=17, fill=INK_700, leading=32)}
{panel(rx, 554, rw, 216, fill=PANEL)}
{micro(rx + 32, 594, "나머지 13분야 + 측정 공백")}
{multiline(rx + 32, 632, [
    "(i) 효과 부재 — 결과가 집행 시점에 둔감 (예: 사회복지 자동이전).",
    "(ii) 측정 한계 — 분야 집계 지표는 사업 단위 효과를 희석,",
    "     사업 단위 미시 결과(품질·단가)는 데이터 자체가 없음.",
], size=17, fill=INK_700, leading=32)}
{divider(M, 1840, 826)}
{key_line("한 분야의 시사적 존재 증명 + 광범위한 측정 공백 — 후자가 곧 ‘결과를 측정하지 않는다’는 논지의 증거다.", y=872, size=20)}
{text(960, 906, "일반적 결과 훼손은 본 분석의 주장이 아니다 — 데이터가 없어 검정할 수 없는 영역이다.", size=16, fill=MUTED, anchor="middle")}
{trigger("다음 — 정책 함의")}
{page_num("결과 영향의 탐색 · Act 5 소결")}
"""
    return svg_doc(body)


# ══════════════════════════════════════════════════════════════════════════
# Epilogue 전환 — 진단에서 처방으로 (빙산 → 두 갈래 → 시사점 5)  (Slide 35 → 36)
# ══════════════════════════════════════════════════════════════════════════
def slide_diagnosis_to_prescription():
    def chip(x, y, w, h, num, name, descs, color):
        out = [panel(x, y, w, h, fill=WHITE, accent=True, bar=color)]
        out.append(f'<circle cx="{x + 44}" cy="{y + 40}" r="19" fill="{color}"/>')
        out.append(text(x + 44, y + 47, num, size=20, fill=WHITE, weight="800",
                        anchor="middle"))
        out.append(text(x + 84, y + 38, name, size=21, fill=INK, weight="800"))
        for i, d in enumerate(descs):
            out.append(text(x + 84, y + 66 + i * 26, d, size=15, fill=INK_700))
        return "\n".join(out)

    lx, rx, cw = M, 990, 850
    cy, ch = 332, 476

    # 검정 결과 요약 band
    band = f"""
{panel(M, 196, 1760, 68, fill=PANEL, accent=True, bar=SIGNAL)}
{micro(M + 28, 238, "검정 결과 요약", fill=SIGNAL)}
{text(M + 230, 238, "분야 매개 검정에서 농림수산만 유의. 사업 단위 미시 결과는 측정되지 않아 검정 범위 밖.", size=19, fill=INK_700)}
"""
    fork = (connect(960, 268, lx + cw / 2, cy - 6, color=MUTED)
            + connect(960, 268, rx + cw / 2, cy - 6, color=MUTED))

    left = f"""
{panel(lx, cy, cw, ch, fill=PANEL_COOL, accent=True, bar=SIGNAL)}
{micro(lx + 32, cy + 44, "방향 A · 측정되는 집행 패턴에 개입", fill=SIGNAL)}
{text(lx + 32, cy + 92, "집행 시점·체질 기반 제도 조정", size=26, fill=INK, weight="800")}
{text(lx + 32, cy + 122, "체질·시점 집중은 데이터로 측정된다 (Act 2–4)", size=16, fill=MUTED)}
{divider(lx + 32, lx + cw - 32, cy + 140)}
{chip(lx + 32, cy + 158, cw - 64, 90, "①", "평가의 체질별 차등화",
      ["일괄 집행률 평가 대신 체질별 기준 적용"], SIGNAL)}
{chip(lx + 32, cy + 260, cw - 64, 90, "②", "회계: Archetype 맞춤 유연화",
      ["C1 다년도 회계 · C2 분기 정산 (국가재정법·시행령)"], SIGNAL)}
{chip(lx + 32, cy + 362, cw - 64, 90, "③", "모니터링: 5종 지표 대시보드",
      ["Goodhart Score · 12월 집중 예측 등 사전 지표"], SIGNAL)}
"""
    right = f"""
{panel(rx, cy, cw, ch, fill=CAUTION_SOFT, accent=True, bar=CAUTION)}
{micro(rx + 32, cy + 44, "방향 B · 결과 측정 범위 확장", fill=CAUTION)}
{text(rx + 32, cy + 92, "outcome 측정 체계 보강", size=26, fill=INK, weight="800")}
{text(rx + 32, cy + 122, "사업 단위 결과 지표를 도입해 검정 범위를 넓힌다", size=16, fill=MUTED)}
{divider(rx + 32, rx + cw - 32, cy + 140)}
{chip(rx + 32, cy + 158, cw - 64, 138, "④", "결과 중심 평가로의 전환",
      ["집행률(output) 지표에 결과(outcome) 지표를 결합",
       "사업 단위·미시 결과 지표 정의가 전제"], CAUTION)}
{chip(rx + 32, cy + 312, cw - 64, 138, "⑤", "정책 도구 · 사전 진단",
      ["사업·부처 사분면 (집중도 × 결과 지표)",
       "측정되는 집행 패턴으로 위험을 사전 진단"], CAUTION)}
"""
    body = f"""
{header("정책 함의의 구조 — 두 방향",
        "검정 결과에 따른 두 가지 대응: 측정되는 집행 패턴에 개입 / 결과 측정 범위 확장.",
        insert_note="삽입 위치 · Slide 35 → 36 (Epilogue 도입)")}
{band}
{fork}
{left}
{right}
{divider(M, 1840, 846)}
{key_line("측정되는 집행 패턴은 제도로 조정하고, 측정되지 않는 결과는 지표를 확장해 관측 범위를 넓힌다.", y=898, size=22)}
{trigger("다음 — 시사점 ①~⑤ (Slide 36~40)")}
{page_num("정책 함의의 구조 · Epilogue 도입")}
"""
    return svg_doc(body)


OUTPUTS = {
    "slide-04b-fiscal-data-spec.svg": slide_fiscal_spec,
    "slide-31a-synthesis.svg": slide_synthesis,
    "slide-31b-pathways.svg": slide_pathways,
    "slide-31c-outcome-data-spec.svg": slide_outcome_spec,
    "slide-35b-mediation-results.svg": slide_iceberg,
    "slide-35c-diagnosis-to-prescription.svg": slide_diagnosis_to_prescription,
}

# 이전 네이밍 정리 — 31a two-faces→synthesis / 31b→31c 재배치 / 35b 빙산→매개결과
SUPERSEDED = ["slide-31b-outcome-data-spec.svg", "slide-35b-iceberg.svg",
              "slide-31a-two-faces.svg"]


def main():
    for name, render in OUTPUTS.items():
        (OUT_DIR / name).write_text(render(), encoding="utf-8")
    removed = 0
    for name in SUPERSEDED:
        for p in (OUT_DIR / name, OUT_DIR / f"_v_{name[:-4]}.png"):
            if p.exists():
                p.unlink()
                removed += 1
    print(f"generated {len(OUTPUTS)} slides in {OUT_DIR}"
          + (f" · removed {removed} superseded" if removed else ""))


if __name__ == "__main__":
    main()
