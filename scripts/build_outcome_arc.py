"""Act 5(결과) + Epilogue 도입 재구성 슬라이드 — 사용자 스타일 보정본 기준.

내러티브 thesis (2026-05-30 확정):
  집행률은 결과(outcome)를 설명하지 못한다 → 대안 지표가 필요하다.
  Goodhart 대응책은 이미 있다 — 본 분석은 그것을 *어디에* 적용할지 데이터로 타겟팅.

흐름 (각 trigger가 다음 slide 제목을 세팅 — 점프 없음):
  31a 전반부 종합        → "집행률로 결과를 설명할 수 있는가"
  32  집행률 ≠ 대리지표   → "결과와 연결되는 한 틈"
  33  농림수산 한 사례     → "나머지는 들여다볼 수조차 없었다"
  34  검증할 수 없는 지표   → "대안 지표를 어디에"
  35  타겟 지도 (Epilogue) → "다섯 가지 실무 제언"

스타일: figma_exports/slide-31a.svg(사용자 보정본) 토큰 정확 일치.
출력: figma_exports/slide-32.svg … slide-35.svg
"""
from pathlib import Path
from html import escape

OUT = Path("figma_exports")

# ── 팔레트 (사용자 보정본에서 추출) ──────────────────────────────────────
CANVAS = "#FAFAF7"
SIGNAL = "#C0392B"
SIGNAL_SOFT = "#FBEEEC"
CAUTION = "#B45309"
CAUTION_SOFT = "#FEF6E4"
INK = "#0F172A"
INK_700 = "#334155"
SLATE = "#475569"
MUTED = "#64748B"
MUTED2 = "#94A3B8"
LINE = "#CBD5E1"
COOL = "#F1F5F9"
WARM = "#F4F1EA"
WHITE = "#FFFFFF"
MONO = "JetBrains Mono, monospace"


def T(x, y, s, size=18, fill=INK, weight=None, anchor=None, mono=False,
      italic=False, ls=None):
    a = [f'x="{x}"', f'y="{y}"', f'font-size="{size}"', f'fill="{fill}"']
    if weight:
        a.append(f'font-weight="{weight}"')
    if anchor:
        a.append(f'text-anchor="{anchor}"')
    if mono:
        a.append(f'font-family="{MONO}"')
    if italic:
        a.append('font-style="italic"')
    if ls is not None:
        a.append(f'letter-spacing="{ls}"')
    return f'<text {" ".join(a)}>{escape(s)}</text>'


def rect(x, y, w, h, fill, stroke=LINE, sw=1, rx=10):
    s = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"{s} rx="{rx}"></rect>'


def panel(x, y, w, h, fill=COOL, bar=SIGNAL):
    out = rect(x, y, w, h, fill)
    if bar:
        out += f'\n<rect x="{x}" y="{y}" width="4" height="{h}" fill="{bar}" rx="2"></rect>'
    return out


def line(x1, x2, y, stroke=LINE, sw=1):
    return f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{stroke}" stroke-width="{sw}"></line>'


def slabel(x, y, s):  # section micro label
    return T(x, y, s, size=14, fill=MUTED, weight="700", mono=True, ls="0.6")


def head(kicker, insert, title, subtitle):
    return "\n".join([
        T(80, 58, kicker, size=24, fill=MUTED, weight="500", mono=True, ls="0.65"),
        T(1840, 58, insert, size=14, fill=MUTED2, anchor="end", mono=True, ls="0.4"),
        T(80, 106, title, size=44, fill=INK, weight="700", ls="-0.44"),
        T(80, 142, subtitle, size=22, fill=MUTED),
        line(80, 1840, 168),
    ])


def emph(pre, em, post, y=880, rule=838, size=24):
    parts = f'{escape(pre)}<tspan fill="{SIGNAL}">{escape(em)}</tspan>{escape(post)}'
    return (line(780, 1140, rule) + "\n"
            + f'<text x="960" y="{y}" font-size="{size}" fill="{INK}" '
              f'font-weight="700" text-anchor="middle">{parts}</text>')


def footer(left, trig):
    return "\n".join([
        T(80, 1035, left, size=20, fill=MUTED, mono=True, ls="0.55"),
        T(1840, 1035, trig + "  ↘", size=18, fill=MUTED, anchor="end", italic=True),
    ])


def doc(body):
    return ('<?xml version="1.0"?>\n'
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1920 1080" '
            'font-family="Pretendard, -apple-system, sans-serif">\n'
            f'<rect width="1920" height="1080" fill="{CANVAS}"></rect>\n'
            + body + "\n</svg>\n")


def bar_color(v):
    return SIGNAL if v >= 0.5 else (CAUTION if v >= 0.3 else MUTED)


# ══════════════════════════════════════════════════════════════════════════
# 32 — 집행률은 결과를 설명하지 못한다
# ══════════════════════════════════════════════════════════════════════════
def slide_32():
    fields = [("사회복지", 0.73), ("산업·중기", 0.61), ("환경", 0.58),
              ("보건", 0.58), ("농림수산", 0.49), ("국토·지역", 0.37),
              ("공공질서", 0.29), ("통신", 0.28), ("교통·물류", 0.22),
              ("교육", 0.20), ("문화·관광", 0.19), ("일반·지방행정", 0.10),
              ("국방", 0.10), ("과학기술", 0.04), ("통일·외교", 0.02)]
    bx0, bmax, lblx = 320, 600, 300
    rows = [slabel(110, 212, "분야별 outcome 상관 강도 |r| (분야 평균) — 0.02 ~ 0.73, 약 31배 차이")]
    y = 248
    for name, v in fields:
        w = v / 0.80 * bmax
        c = bar_color(v)
        rows.append(T(lblx, y + 5, name, size=17, fill=INK_700, anchor="end"))
        rows.append(rect(bx0, y - 14, max(w, 2), 22, c, stroke=None, rx=4))
        rows.append(T(bx0 + w + 12, y + 5, f"{v:.2f}", size=16, fill=c,
                      weight="700"))
        y += 36.5
    chart = "\n".join(rows)

    rxp = 1180
    right = "\n".join([
        panel(rxp, 206, 660, 156, fill=COOL, bar=MUTED),
        slabel(rxp + 28, 246, "집행률이 보는 것 (OUTPUT)"),
        T(rxp + 28, 288, "· 결재 시점   · 집행 금액   · 집행률", size=21, fill=INK_700),
        T(rxp + 28, 330, "→ 평가지표에 직접 반영 (분야 간 거의 동일, 90%+)",
          size=17, fill=MUTED),
        panel(rxp, 378, 660, 188, fill=SIGNAL_SOFT, bar=SIGNAL),
        slabel(rxp + 28, 418, "보지 못하는 것 (OUTCOME)"),
        T(rxp + 28, 460, "· 사업 품질   · 목표 달성도", size=21, fill=INK_700),
        T(rxp + 28, 494, "· 사회적 결과 (지니·기대수명·범죄율 등)", size=21,
          fill=INK_700),
        T(rxp + 28, 536, "→ 평가지표에 미포함 · 분야 단위로만 측정", size=17,
          fill=SIGNAL),
        panel(rxp, 582, 660, 150, fill=CAUTION_SOFT, bar=CAUTION),
        slabel(rxp + 28, 622, "측정 단위의 한계"),
        T(rxp + 28, 660, "결과는 분야 단위로만 측정 — 사업 단위 미시결과", size=19,
          fill=INK_700),
        T(rxp + 28, 690, "(품질·단가)는 데이터 자체가 없다.", size=19, fill=INK_700),
        T(rxp + 28, 720, "검정 범위 상세 → 부록 App-MED", size=15, fill=MUTED,
          mono=True),
    ])

    body = "\n".join([
        head("ACT 05 · 진단 — Output vs Outcome",
             "ACT 5 재구성 · 32",
             "집행률은 결과(outcome)를 설명하지 못한다",
             "집행률은 분야 간 거의 같은데(90%+), 결과와의 상관은 0.02–0.73 — 약 31배 차이."),
        chart, right,
        emph("집행률은 ‘썼는가’만 보는 output 지표 — ", "결과의 대리지표가 될 수 없다",
             ".", y=880, rule=838),
        footer("ACT 05 · 진단", "다음 — 결과와 연결되는 한 틈을 본다"),
    ])
    return doc(body)


# ══════════════════════════════════════════════════════════════════════════
# 33 — 결과까지 연결된 단 한 곳: 농림수산
# ══════════════════════════════════════════════════════════════════════════
def node(x, y, w, h, title, sub, fill, bar, tcol):
    return "\n".join([
        panel(x, y, w, h, fill=fill, bar=bar),
        T(x + w / 2, y + h / 2 - 6, title, size=26, fill=tcol, weight="800",
          anchor="middle"),
        T(x + w / 2, y + h / 2 + 24, sub, size=16, fill=MUTED, anchor="middle",
          mono=True),
    ])


def varrow(x, y0, y1, lab):
    return ("\n".join([
        f'<path d="M{x} {y0} L{x} {y1 - 12}" stroke="{INK_700}" stroke-width="2"></path>',
        f'<path d="M{x} {y1} L{x - 7} {y1 - 12} L{x + 7} {y1 - 12} Z" fill="{INK_700}"></path>',
        T(x + 30, (y0 + y1) / 2, lab, size=20, fill=MUTED, italic=True, mono=True),
    ]))


def slide_33():
    dx, dw = 110, 440
    cx = dx + dw / 2
    diagram = "\n".join([
        slabel(dx, 212, "매개 모형 — Sobel 간접효과 a·b"),
        node(dx, 234, dw, 96, "12월 집중도", "원인 · X", SIGNAL_SOFT, SIGNAL, SIGNAL),
        varrow(cx, 330, 374, "a"),
        node(dx, 374, dw, 96, "시점 압력", "매개 · M", WARM, CAUTION, INK),
        varrow(cx, 470, 514, "b"),
        node(dx, 514, dw, 96, "농가소득", "결과 · Y", COOL, MUTED, INK),
    ])

    rxp = 620
    right = "\n".join([
        panel(rxp, 234, 1220, 232, fill=SIGNAL_SOFT, bar=SIGNAL),
        slabel(rxp + 32, 276, "검정 결과 — Sobel만 유의, 부트스트랩 미확증"),
        line(rxp + 32, rxp + 1188, 292),
        T(rxp + 32, 338, "Sobel z = −2.897  (p = 0.004)   ·   표본 n = 5 (연 단위)",
          size=24, fill=INK_700, mono=True),
        T(rxp + 32, 384, "부트스트랩 95% CI가 0을 포함 → 권장 검정 기준으로는 유의하지 않다.",
          size=22, fill=INK_700),
        T(rxp + 32, 430, "소표본에서 Sobel은 신뢰 낮음 — 통계 확증이 아닌 사례적 예시.",
          size=22, fill=INK_700),
        panel(rxp, 482, 1220, 128, fill=WARM, bar=CAUTION),
        slabel(rxp + 32, 522, "그래도 보는 이유 — 메커니즘·raw 패턴 정합"),
        T(rxp + 32, 560, "수확기·재해보험처럼 결과가 ‘집행 시점’에 민감한 구조.",
          size=21, fill=INK_700),
        T(rxp + 32, 592, "2023년 12월 집중 peak(11.8%) → 2024년 농가소득 −3.0% (raw 정합).",
          size=21, fill=INK_700),
    ])

    body = "\n".join([
        head("ACT 05 · 한 사례 — 농림수산",
             "ACT 5 재구성 · 33",
             "들여다본 한 틈 — 농림수산",
             "결과가 측정되는 분야에서만 매개 검정이 가능하다. 농림수산만 Sobel 유의하나, 부트스트랩으로는 확증되지 않는다."),
        diagram, right,
        emph("들여다볼 수 있었던 한 사례마저 통계로 확증되지 않는다 — ",
             "결과를 검증할 데이터가 그만큼 얇다",
             ".", y=880, rule=838),
        footer("ACT 05 · 한 사례", "다음 — 그렇다면 결과 검증 자체가 가능한가"),
    ])
    return doc(body)


# ══════════════════════════════════════════════════════════════════════════
# 34 — 결과를 검증할 수 없는 지표 (진단 + 규율)
# ══════════════════════════════════════════════════════════════════════════
def slide_34():
    cells = ["농림수산", "사회복지", "산업·중기", "보건", "통신", "문화·관광",
             "일반·지방행정", "과학기술", "통일·외교", "국방", "교육",
             "교통·물류", "공공질서", "국토·지역"]
    cw, ch, gap = 237, 104, 16
    gx, gy = 80, 222
    grid = [slabel(gx, 212, "분야별 매개 검정 (n=14)")]
    for i, nm in enumerate(cells):
        c, r = i % 7, i // 7
        x = gx + c * (cw + gap)
        y = gy + r * (ch + 18)
        if i == 0:
            grid.append(rect(x, y, cw, ch, SIGNAL, stroke=None, rx=12))
            grid.append(T(x + cw / 2, y + 44, "★", size=24, fill=WHITE,
                          anchor="middle"))
            grid.append(T(x + cw / 2, y + 82, nm, size=27, fill=WHITE,
                          weight="800", anchor="middle"))
        else:
            grid.append(rect(x, y, cw, ch, WHITE, stroke=LINE, sw=1.5, rx=12))
            grid.append(T(x + cw / 2, y + 62, nm, size=26, fill=SLATE,
                          weight="600", anchor="middle"))
    grid = "\n".join(grid)
    leg_y = gy + 2 * ch + 18 + 24
    legend = "\n".join([
        rect(gx, leg_y, 28, 28, SIGNAL, stroke=None, rx=6),
        T(gx + 40, leg_y + 22, "Sobel 유의 1", size=22, fill=INK_700),
        rect(gx + 200, leg_y, 28, 28, WHITE, stroke=LINE, sw=1.5, rx=6),
        T(gx + 240, leg_y + 22, "비유의 13", size=22, fill=INK_700),
        T(gx + 430, leg_y + 22, "· 농림수산도 부트스트랩 미확증 → 확증 0건 · 환경 제외",
          size=18, fill=MUTED2, mono=True),
    ])

    py = gy + 2 * ch + 18 + 78
    panels = "\n".join([
        panel(80, py, 860, 196, fill=COOL, bar=MUTED),
        slabel(112, py + 40, "비유의 13분야 — 두 갈래"),
        line(112, 908, py + 56),
        T(112, py + 100, "(i) 효과 부재 — 결과가 집행 시점에 둔감한 분야", size=23,
          fill=INK_700),
        T(112, py + 138, "(ii) 측정 한계 — 분야 집계 지표가 사업 단위 효과를 희석,",
          size=23, fill=INK_700),
        T(112, py + 170, "      미시 결과(품질·단가)는 데이터 자체가 없음", size=23,
          fill=INK_700),
        panel(980, py, 860, 196, fill=SIGNAL_SOFT, bar=SIGNAL),
        slabel(1012, py + 40, "규율 — 가장 강한 상관도 메커니즘 없으면 기각"),
        line(1012, 1808, py + 56),
        T(1012, py + 100, "사회복지 r = −0.86 (최강) — 그러나 기각.", size=23,
          fill=INK_700),
        T(1012, py + 138, "기초연금 등 자동 소득이전이라 타이밍과 무관.", size=23,
          fill=INK_700),
        T(1012, py + 170, "상관 강도 ≠ 의미 — 메커니즘으로 거른다.", size=23,
          fill=SIGNAL, weight="700"),
    ])

    body = "\n".join([
        head("ACT 05 · 소결 — 검증 공백",
             "ACT 5 재구성 · 34",
             "결과를 검증할 수 없는 지표",
             "측정되는 1곳마저 부트스트랩 미확증, 가장 강한 상관(사회복지)은 메커니즘 없어 기각 — 통계로 확증된 연관은 0건."),
        grid, legend, panels,
        emph("결과와의 연관을 통계로 확증할 수 없다 — 집행률엔 결과 피드백이 없다. 그래서 ",
             "대안·측정 보강이 필요하다",
             ".", y=1000, rule=py + 196 + 22),
        footer("ACT 05 · 소결", "그래서 — 대안 지표를 어디에 둘 것인가"),
    ])
    return doc(body)


# ══════════════════════════════════════════════════════════════════════════
# 35 — 대안 지표를 어디에: 본 분석의 타겟 지도 (Epilogue 도입)
# ══════════════════════════════════════════════════════════════════════════
def slide_35():
    tools = [
        ("결과중심 예산 · 다지표 평가", "OECD 성과주의 예산"),
        ("다년도 회계 — 단년 마감압력 제거", "英 Capital DEL · 美 USACE"),
        ("정산 시점 분산", "獨 분기정산 · 日 IPA·NEDO"),
        ("측정가능 업무에만 인센티브 금지", "Holmström–Milgrom 1991"),
        ("연말지출 상시 모니터링", "美 GAO · 英 NAO"),
        ("이론 토대 — ‘지표가 목표가 되면’", "Goodhart 1975 · Campbell 1979"),
    ]
    targets = [
        ("C1 자산취득형", "×3.42 · 12월 절벽", "다년도 회계", SIGNAL),
        ("C2 출연금형", "+554% 사이클", "정산 분산", CAUTION),
        ("C0 · C3", "효과 없음 (null)", "현행 유지", MUTED),
        ("고노출 부처 (Q2)", "Exposure 高", "우선 점검", SIGNAL),
        ("측정 불가 분야", "결과 미측정", "측정 보강", CAUTION),
    ]
    L = [panel(80, 216, 860, 456, fill=COOL, bar=MUTED),
         slabel(112, 256, "① 이미 제시된 대응책 — 레퍼런스")]
    yy = 308
    for name, ref in tools:
        L.append(T(112, yy, name, size=21, fill=INK, weight="800"))
        L.append(T(112, yy + 26, ref, size=15, fill=MUTED, mono=True))
        yy += 60
    R = [panel(980, 216, 860, 456, fill=SIGNAL_SOFT, bar=SIGNAL),
         slabel(1012, 256, "② 본 분석의 기여 — 적용 타겟 (데이터)")]
    yy = 304
    for found, ev, target, c in targets:
        R.append(T(1012, yy + 6, found, size=19, fill=c, weight="800"))
        R.append(T(1012, yy + 30, ev, size=14, fill=MUTED, mono=True))
        R.append(f'<path d="M1330 {yy + 18} L1374 {yy + 18}" stroke="{c}" stroke-width="2.5"></path>')
        R.append(f'<path d="M1374 {yy + 18} l-11 -6 l0 12 z" fill="{c}"></path>')
        R.append(T(1394, yy + 24, target, size=20, fill=INK_700, weight="700"))
        yy += 70
    body = "\n".join([
        head("EPILOGUE · 진입 — 처방의 지도", "Slide 35 · Epilogue 진입",
             "처방은 이미 있다 — 본 분석은 ‘어디에’를 댄다",
             "Goodhart 대응책은 학계·해외에서 제시돼 왔다. 빠진 건 ‘어느 사업·체질에 적용하나’ — 그 타겟을 데이터로 채운다."),
        "\n".join(L), "\n".join(R),
        emph("도구를 발명하지 않는다 — ", "검증된 처방을, 데이터가 가리키는 곳에 댄다",
             ".", y=752, rule=710),
        footer("EPILOGUE · 진입", "이제 하나씩 적용한다 — ① 평가"),
    ])
    return doc(body)


# ══════════════════════════════════════════════════════════════════════════
# 36 — 제언 ① 평가: 체질별 차등
# ══════════════════════════════════════════════════════════════════════════
def slide_36():
    # 사용자 Figma 레이아웃 유지: 3 LAYER MAP(3 큰 카드) + 시사점① 본문 + 닫는 줄
    # 보충: 카드③ 비전→실제도구 / 본문에 체질별 처방+회계연동 / 본문 C-코드 + 연결 부제
    cards = [
        ("① 평가  ·  지금", "평가는 체질을 따른다.",
         ["4 archetype이 시점 압력", "메커니즘이 모두 다르다."], "현재 슬라이드", SIGNAL, True),
        ("② 모니터링", "5종 지표 대시보드",
         ["FIS 권고 자동화", "+ 11월 사전 신호"], "Slide 37", MUTED, False),
        ("③ 정책 도구", "사업·부처 사분면 진단",
         ["Q2 위험 부처 사전 점검", "(시점 집중 高)"], "Slide 38", MUTED, False),
    ]
    cw, gap, cy, chh = 573, 20, 222, 208
    smap = [slabel(80, 200, "3 LAYER MAP")]
    for i, (hdr, stmt, subs, tag, c, now) in enumerate(cards):
        x = 80 + i * (cw + gap)
        smap.append(panel(x, cy, cw, chh, fill=SIGNAL_SOFT if now else WHITE, bar=c))
        smap.append(T(x + 28, cy + 46, hdr, size=20, fill=c if now else INK_700,
                      weight="800"))
        smap.append(T(x + 28, cy + 92, stmt, size=22, fill=INK, weight="800"))
        for j, s in enumerate(subs):
            smap.append(T(x + 28, cy + 126 + j * 30, s, size=17, fill=INK_700))
        smap.append(T(x + 28, cy + chh - 22, tag, size=15,
                      fill=c if now else MUTED, weight="700", mono=True))
    smap = "\n".join(smap)

    presc = [
        ("C1 자산취득형 (×3.42)", "다년도 평균 집행률  (= 다년도 회계)", SIGNAL),
        ("C2 출연금형 (사이클)", "분기 진행률  (= 정산 분산)", CAUTION),
        ("C0·C3 (효과 없음)", "현행 유지", MUTED),
    ]
    bb = [slabel(80, 478, "시사점 ① · 본문"),
          T(80, 518, "분석이 식별한 4 체질은 시점 압력에 대한 응답이 모두 다르다 — 그래서 평가 기준도 체질별로:",
            size=20, fill=INK_700)]
    yy = 564
    for name, std, c in presc:
        bb.append(rect(80, yy - 14, 9, 9, c, stroke=None, rx=2))
        bb.append(T(104, yy, name, size=19, fill=c, weight="800"))
        bb.append(T(470, yy, "→  " + std, size=19, fill=INK_700, weight="700"))
        yy += 38
    bb.append(T(80, yy + 22, "일괄 평가는 동일 효과를 만들지 못한다 — 조정 불가형(C0·C3)엔 무관, 조정 대상형(C1·C2)엔 압박.",
               size=19, fill=INK_700))
    body_block = "\n".join(bb)

    body = "\n".join([
        head("EPILOGUE · 실무적 시사점 ①", "Slide 36 · Epilogue",
             "평가는 사업 유형에 따라 다르다",
             "데이터가 가리킨 곳에 집중하는 첫 갈래 — 적용은 평가·모니터링·정책도구 3 layer로."),
        smap, body_block,
        emph("같은 평가표가 ", "같은 결과를 만들지 않는다", ".", y=820, rule=778),
        footer("EPILOGUE · 시사점 ①", "다음 — ② 모니터링: 5종 지표 대시보드"),
    ])
    return doc(body)


# ══════════════════════════════════════════════════════════════════════════
# 37 — 제언 ② 회계: 체질 맞춤 유연화
# ══════════════════════════════════════════════════════════════════════════
def slide_37():
    def box(x, kicker, title, lines, bench, c, soft):
        out = [panel(x, 224, 860, 480, fill=soft, bar=c)]
        out.append(slabel(x + 32, 266, kicker))
        out.append(T(x + 32, 312, title, size=28, fill=INK, weight="800"))
        out.append(line(x + 32, x + 828, 332))
        yy = 380
        for ln in lines:
            out.append(T(x + 32, yy, ln, size=20, fill=INK_700))
            yy += 40
        out.append(T(x + 32, 668, bench, size=16, fill=MUTED, mono=True))
        return "\n".join(out)
    body = "\n".join([
        head("EPILOGUE · 적용 ② — 회계", "Epilogue · 37",
             "회계: 체질 맞춤 유연화",
             "마감 압력의 근원인 단년 회계 원칙을, 시점 압력이 강한 체질에 한해 푼다."),
        box(80, "C1 자산취득형 (n=99) — 다년도 회계 격상",
            "다년도 회계 전환",
            ["① 「국가재정법」 §46 — 자산취득성 사업 자동 이월 허용",
             "② 「국가재정법」 §7 — MTEF 5년을 실 회계로 격상",
             "③ Capital DEL 분리 회계 도입 검토",
             "예상: 12월 절벽 ×3.42 → 기준선 ×1.9 이하"],
            "벤치마크 · 영국 Capital DEL 다년도 / 미국 USACE multi-year", SIGNAL, SIGNAL_SOFT),
        box(980, "C2 출연금형 (n=154) — 정산 시점 분산",
            "분기·반기 정산",
            ["① 「공운법 시행령」 §27 — 분기 보고 + 반기 정산 의무화",
             "② 출연금 교부 1회 일괄 → 분기 분할",
             "③ 출연기관 단기 현금관리 인프라 보강",
             "예상: Wavelet +554% 사이클 진폭 약화"],
            "벤치마크 · 독일 분기정산 / 일본 IPA·NEDO 반기보고", CAUTION, CAUTION_SOFT),
        emph("변경 대상은 ", "「국가재정법」 §46·§7 + 「공운법 시행령」 §27", ".",
             y=792, rule=750),
        footer("EPILOGUE · 적용 ②", "다음 — 무엇을 상시 감시하나"),
    ])
    return doc(body)


# ══════════════════════════════════════════════════════════════════════════
# 38 — 제언 ③ 모니터링: 5종 지표 대시보드
# ══════════════════════════════════════════════════════════════════════════
def slide_38():
    inds = [
        ("①", "Goodhart Exposure Score", "12월 비중·사이클·강화 가중 · 임계 ≥0.3 알람"),
        ("②", "Archetype 분류", "1,557 사업 C0~C3 · 신규 사업 자동 분류"),
        ("③", "11월→12월 burst 예측", "11월까지 패널 → 12월 집중 사전 신호"),
        ("④", "Outcome 측정·추적 (보강 대상)", "분야 결과지표 연계 · 측정 공백 우선 보강"),
        ("⑤", "Wavelet 사이클 추적", "연도별 진폭 강화 모니터 · 통제군 기준선"),
    ]
    y = 224
    block = [slabel(80, 212, "본 분석이 제공하는 상시 지표 5종 (FIS 22-03 권고 → 대시보드)")]
    for num, name, desc, in [(a, b, c) for a, b, c in inds]:
        block.append(panel(80, y, 1760, 84, fill=WHITE, bar=SIGNAL if num in ("①", "④") else MUTED))
        block.append(T(112, y + 52, num, size=30, fill=SIGNAL if num in ("①", "④") else INK_700, weight="800"))
        block.append(T(168, y + 40, name, size=24, fill=INK, weight="800"))
        block.append(T(168, y + 68, desc, size=17, fill=MUTED))
        y += 98
    block.append(T(80, y + 30, "적용 layer · 세부사업(1,557) → 부처(72) → 분야(14) → 시간(Wavelet)  ·  매년 결산 후 자동 갱신",
                   size=18, fill=INK_700))
    body = "\n".join([
        head("EPILOGUE · 적용 ③ — 모니터링", "Epilogue · 38",
             "5종 지표 대시보드",
             "FIS 22-03의 ‘불용사업 집중관리’ 권고를, 상시 모니터링 지표 5종으로 확장한다."),
        "\n".join(block),
        emph("FIS 권고를, ", "5종 지표 대시보드로", " — 11월 사전 신호 + 사업 단위 조정.",
             y=900, rule=858),
        footer("EPILOGUE · 적용 ③", "다음 — 어디로 가는가"),
    ])
    return doc(body)


# ══════════════════════════════════════════════════════════════════════════
# 39 — 제언 ④ 진화 (statement)
# ══════════════════════════════════════════════════════════════════════════
def slide_39():
    body = "\n".join([
        T(80, 58, "EPILOGUE · 적용 ④ — 진화", size=24, fill=MUTED,
          weight="500", mono=True, ls="0.65"),
        T(1840, 58, "Epilogue · 39", size=14, fill=MUTED2, anchor="end", mono=True),
        T(80, 250, "방향", size=20, fill=MUTED, mono=True, ls="0.6"),
        f'<text x="80" y="470" font-size="56" fill="{INK}" font-weight="800">'
        f'숫자를 맞추는 재정에서,</text>',
        f'<text x="80" y="556" font-size="56" fill="{SIGNAL}" font-weight="800">'
        f'가치를 증명하는 재정으로.</text>',
        T(80, 660, "output(집행률) 측정에 outcome 측정을 더해 — 측정 공백을 좁히는 것이 장기 과제다.",
          size=24, fill=INK_700),
        line(80, 1840, 860),
        f'<text x="960" y="912" font-size="24" fill="{INK}" font-weight="700" text-anchor="middle">'
        f'측정되는 것에 개입하고, <tspan fill="{SIGNAL}">측정되지 않는 것은 측정하기 시작한다</tspan>.</text>',
        footer("EPILOGUE · 적용 ④", "다음 — 누가, 어디에 적용하나"),
    ])
    return doc(body)


# ══════════════════════════════════════════════════════════════════════════
# 40 — 제언 ⑤ 정책 도구 · 적용 단위
# ══════════════════════════════════════════════════════════════════════════
def img(href, x, y, w, h):
    return f'<image href="{href}" x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid meet"></image>'


def slide_40():
    # 두 차트를 좌·우 절반에 임베드 (ratio≈1.21 · 높이 우선 fit, 좌우 여백 균등)
    iw, ih = 700, 560          # 이미지 박스 (ratio 1.25)
    iy = 226
    lx = 80 + (880 - iw) / 2   # 좌 절반 중앙
    rx = 960 + (880 - iw) / 2  # 우 절반 중앙
    L = "../paper/figures/eda/fig_slide40_actv_quadrant.png"
    R = "../paper/figures/h14_quadrant.png"
    body = "\n".join([
        head("EPILOGUE · 적용 ⑤ — 정책 도구", "Epilogue · 40",
             "발견은 사업 단위에서, 적용은 책임자 단위에서",
             "1,557 세부사업에서 발견한 패턴을, 72개 부처 단위로 집계해 진단 도구로 제공한다."),
        slabel(80, 212, "분석 layer · 세부사업 1,557 — 출력 축 (12월 비중 × 연주기 진폭)"),
        slabel(960, 212, "도구 layer · 부처 72 — Exposure × 분야 outcome 상관"),
        rect(lx - 16, iy - 12, iw + 32, ih + 36, "#FCFCFB", stroke=LINE, sw=1, rx=12),
        rect(rx - 16, iy - 12, iw + 32, ih + 36, "#FCFCFB", stroke=LINE, sw=1, rx=12),
        img(L, lx, iy, iw, ih),
        img(R, rx, iy, iw, ih),
        T(lx + iw / 2, iy + ih + 18, "한 점 = 사업 하나 · 체질(C0~C3) 색", size=15,
          fill=MUTED, anchor="middle"),
        T(rx + iw / 2, iy + ih + 18, "한 점 = 책임자 단위 · Q2 위험 부처", size=15,
          fill=MUTED, anchor="middle"),
        T(960, 856, "위험(Q2) 부처 · 국무조정실(Exposure 0.67) · 과학기술정보통신부(0.40) — 시점 집중 高",
          size=19, fill=INK_700, anchor="middle"),
        emph("발견은 사업 단위에서, ", "적용은 책임자 단위에서", ".", y=908, rule=884),
        footer("EPILOGUE · 적용 ⑤", "질문 받습니다  ·  부록 App-A~WAV"),
    ])
    return doc(body)


# ══════════════════════════════════════════════════════════════════════════
# 22 — cutoff × 체질 매트릭스 (in-SVG · H22_quarterly_cutoffs)
# ══════════════════════════════════════════════════════════════════════════
def slide_22():
    cols_m = ["3월", "6월", "9월", "12월"]
    cx = [400, 760, 1120, 1480]
    cw = 345
    # (이름, accent, [(배율, 유의?, star?), ...])  — H22_quarterly_cutoffs.csv mult
    rows = [
        ("전체", INK_700, [("1.18", 1, 0), ("1.39", 1, 0), ("1.24", 1, 0), ("1.91", 1, 0)]),
        ("C1 자산취득형", SIGNAL, [("1.53", 1, 0), ("2.50", 1, 0), ("1.80", 1, 0), ("3.42", 1, 1)]),
        ("C3 정상사업", MUTED, [("1.27", 1, 0), ("1.44", 1, 0), ("1.22", 1, 0), ("2.24", 1, 0)]),
        ("C0 인건비형", MUTED, [("1.12", 1, 0), ("1.08", 1, 0), ("1.28", 1, 0), ("1.12", 1, 0)]),
        ("C2 출연금형", CAUTION, [("0.90", 0, 0), ("1.06", 0, 0), ("1.07", 0, 0), ("1.10", 0, 0)]),
    ]
    ry0, rh, gap = 264, 84, 14
    out = [slabel(80, 232, "회계 절단점 × 체질 — 직전월 대비 일집행 점프 배율 (eᵝ, bw=1)")]
    for i, m in enumerate(cols_m):
        is12 = i == 3
        out.append(T(cx[i] + cw / 2, 254, m, size=22,
                     fill=SIGNAL if is12 else MUTED, weight="800", anchor="middle"))
    for ri, (name, acc, vals) in enumerate(rows):
        y = ry0 + ri * (rh + gap)
        out.append(rect(80, y, 300, rh, "#F8FAFC" if name == "전체" else WHITE,
                        stroke=LINE, sw=1, rx=8))
        out.append(rect(80, y, 4, rh, acc, stroke=None, rx=2))
        out.append(T(104, y + rh / 2 + 9, name, size=22, fill=INK, weight="800"))
        for ci, (val, sig, star) in enumerate(vals):
            x = cx[ci]
            is12 = ci == 3
            fill = SIGNAL if star else (SIGNAL_SOFT if is12 else WHITE)
            tcol = WHITE if star else (MUTED if not sig else INK)
            out.append(rect(x, y, cw, rh, fill, stroke=LINE, sw=1, rx=8))
            lab = ("×" + val) + (" ★" if star else "") + ("  ns" if not sig else "")
            out.append(T(x + cw / 2, y + rh / 2 + 9, lab,
                         size=30 if star else 29, fill=tcol, weight="800",
                         anchor="middle"))
    out.append(T(80, ry0 + 5 * (rh + gap) + 20,
                 "출연금형 ns = 점프가 아니라 사이클 → Act 4 Wavelet에서 분해 · 출처 H22_quarterly_cutoffs.csv",
                 size=15, fill=MUTED2, mono=True))
    body = "\n".join([
        head("ACT 03 · 단절 — cutoff 매트릭스", "Slide 22 · RDD",
             "분기말마다 점프, 12월이 압도 — 체질별로 갈린다",
             "4개 절단점(3·6·9·12월) × 4 체질의 일집행 점프 배율. 12월·자산취득형이 최대, 출연금형은 점프 없음."),
        "\n".join(out),
        emph("회계연도 마감은 분기 마감과 다른 무게 — ", "자산취득형 12월 ×3.42",
             ", 출연금형은 어느 cutoff도 ns.", y=872, rule=830),
        footer("ACT 03 · 단절", "다음 — 12월 점프, 체질별 비교"),
    ])
    return doc(body)


OUTPUTS = {
    # 36~40은 사용자 Figma 정본 사용 — 미생성 (함수는 재활용 위해 코드 보존)
    "slide-32.svg": slide_32,
    "slide-33.svg": slide_33,
    "slide-34.svg": slide_34,
    "slide-35.svg": slide_35,
    "slide-36.svg": slide_36,  # 수정본 목업 (Figma 반영용 참고)
}


def main():
    for name, fn in OUTPUTS.items():
        (OUT / name).write_text(fn(), encoding="utf-8")
    print(f"generated {len(OUTPUTS)} slides in {OUT}")


if __name__ == "__main__":
    main()
