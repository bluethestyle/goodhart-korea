// ══════════════════════════════════════════════════════════════════════════
//  재정데이터 분석 발표자료 — Pied Piper
//  지표가 채운 95%, 데이터가 찾은 격차
//
//  대상: 한국재정정보원(KPFIS) 담당자·실무 공무원
//  분량: 30장 (PART 1~7 + 마무리)
//  컴파일: typst compile paper/slides.typ paper/slides.pdf
// ══════════════════════════════════════════════════════════════════════════

// ── 폰트 ────────────────────────────────────────────────────────────────
#let sans = ("Pretendard", "Inter", "Helvetica Neue", "Noto Sans KR")
#let mono = ("JetBrains Mono", "IBM Plex Mono", "Consolas", "Menlo")

// ── 컬러 팔레트 (analysis_report.typ과 통일) ─────────────────────────────
#let ink       = rgb("#0a0a0a")
#let paper-c   = rgb("#ffffff")
#let line-c    = rgb("#e5e5e5")
#let line-d    = rgb("#d4d4d4")
#let mid       = rgb("#525252")
#let soft      = rgb("#a3a3a3")
#let ghost     = rgb("#fafafa")
#let chip-bg   = rgb("#f5f5f5")
#let accent    = rgb("#2563eb")
#let accent-bg = rgb("#eff5ff")
#let pos       = rgb("#15803d")
#let neg       = rgb("#b91c1c")
#let warn      = rgb("#a16207")

// ── 메타 ───────────────────────────────────────────────────────────────
#let meta = (
  code: "FA-MIN-PROJ/2026",
  date: "2026.05.18",
  org: "Pied Piper",
  team: "재정데이터 분석팀",
  authors: ("정선규", "심은철", "김영찬", "김재호"),
)

// ── 페이지: 16:9 슬라이드 ───────────────────────────────────────────────
#set page(
  width: 338.7mm, height: 190.5mm,   // 표준 PowerPoint 16:9 (13.33" × 7.5")
  margin: (x: 18mm, y: 13mm),
  fill: paper-c,
)
#set text(font: sans, size: 13pt, lang: "ko", fill: ink, weight: "regular")
#set par(justify: false, leading: 0.62em, spacing: 0.85em)

#show strong: it => text(weight: "semibold", fill: ink, it)
#show emph: it => text(style: "italic", fill: mid, it)

// ══════════════════════════════════════════════════════════════════════════
//  공통 컴포넌트
// ══════════════════════════════════════════════════════════════════════════

// 슬라이드 헤더 — PART 라벨 + 슬라이드 번호
#let slide-header(part, no, total) = block(
  width: 100%, above: 0pt, below: 18pt,
)[
  #grid(
    columns: (1fr, auto),
    text(font: mono, size: 10pt, fill: accent, weight: "medium", tracking: 0.5pt)[
      #upper(part)
    ],
    text(font: mono, size: 10pt, fill: soft, weight: "regular")[
      #no #h(4pt) / #h(4pt) #total
    ],
  )
  #v(4pt)
  #line(length: 100%, stroke: 0.4pt + line-c)
]

#let slide-footer() = place(
  bottom + center,
  dx: 0pt, dy: 8mm,
  text(font: mono, size: 9pt, fill: soft, tracking: 0.4pt)[
    #upper[#meta.org #h(8pt) · #h(8pt) #meta.code #h(8pt) · #h(8pt) #meta.date]
  ],
)

// 슬라이드 제목
#let title(body, sub: none) = block(
  width: 100%, above: 2pt, below: 10pt,
)[
  #text(size: 24pt, weight: "semibold", tracking: -0.5pt, fill: ink, body)
  #if sub != none {
    v(4pt, weak: true)
    text(size: 13pt, weight: "regular", fill: mid, tracking: -0.2pt, sub)
  }
]

// 작은 캡션 (FIG-X.Y 형식)
#let fig-id(id, note: none) = block(
  inset: (top: 6pt),
  text(font: mono, size: 9pt, fill: accent, weight: "medium", tracking: 0.4pt)[
    #upper(id)
  ]
  + if note != none [
    #text(font: sans, size: 10pt, fill: mid)[ #h(8pt) · #h(8pt) #note]
  ]
)

// chip / 라벨
#let chip(label, fg: ink, bg: chip-bg) = box(
  inset: (x: 8pt, y: 3pt), outset: (y: 2pt),
  fill: bg, radius: 4pt,
  text(font: mono, size: 9.5pt, weight: "medium", fill: fg, tracking: 0.3pt)[
    #upper(label)
  ],
)

// KPI 카드 (보고서와 동일, 슬라이드용으로 슬림)
#let kpi(label, value, sub: none, unit: "") = block(
  width: 100%, inset: 11pt, fill: ghost,
  stroke: (left: 2pt + accent, rest: 0.5pt + line-c),
  radius: (right: 4pt), spacing: 4pt,
)[
  #text(font: mono, size: 9pt, fill: mid, tracking: 0.4pt, weight: "medium")[#upper(label)]
  #v(-4pt)
  #text(size: 26pt, weight: "semibold", tracking: -0.7pt, fill: ink)[
    #value
    #if unit != "" {
      text(size: 12pt, weight: "regular", fill: mid)[ #unit]
    }
  ]
  #if sub != none {
    v(-4pt)
    text(size: 10pt, fill: mid, sub)
  }
]

// callout
#let callout(label: none, body, color: accent, bg: accent-bg) = block(
  width: 100%, fill: bg, inset: 12pt, radius: 5pt,
)[
  #if label != none {
    text(font: mono, size: 9.5pt, fill: color, weight: "semibold", tracking: 0.4pt)[
      #upper(label)
    ]
    v(6pt)
  }
  #text(size: 11.5pt, fill: ink, body)
]

// 표 스타일
#show table.cell.where(y: 0): set text(
  font: mono, size: 9.5pt, weight: "semibold", tracking: 0.3pt, fill: mid,
)
#show table.cell.where(y: 0): it => upper(it)
#set table(
  stroke: (x, y) => (
    bottom: if y == 0 { 1pt + ink } else { 0.4pt + line-c },
  ),
  inset: (x: 0pt, y: 7pt),
  align: (col, row) => if col == 0 { left } else { right },
)

// ══════════════════════════════════════════════════════════════════════════
//  슬라이드 wrapper — 한 페이지 = 한 슬라이드
// ══════════════════════════════════════════════════════════════════════════
#let TOTAL = "30"

#let slide(part, no, body) = page()[
  #slide-header(part, no, TOTAL)
  #body
  #slide-footer()
]

// ══════════════════════════════════════════════════════════════════════════
//                              SLIDE 1 — 타이틀
// ══════════════════════════════════════════════════════════════════════════
#page(margin: (x: 22mm, y: 16mm))[
  #set text(fill: ink)
  // 상단 메타
  #grid(
    columns: (1fr, 1fr),
    text(font: mono, size: 11pt, fill: ink, meta.code),
    align(right, text(font: mono, size: 11pt, fill: ink)[
      #meta.date
    ]),
  )

  #v(28pt)

  #text(font: mono, size: 12pt, fill: accent, tracking: 1pt)[
    #upper[Fiscal Data Analysis · Mini Project 2026]
  ]

  #v(16pt)

  #text(size: 52pt, weight: "semibold", tracking: -2pt, fill: ink)[
    지표가 채운 95%,\
    데이터가 찾은 격차
  ]

  #v(14pt)

  #text(size: 22pt, weight: "regular", fill: mid, tracking: -0.5pt)[
    한국 중앙정부 재정 11년 21만 셀 패널로 본 만성 재정 3종 문제
  ]

  #v(1fr)

  #line(length: 100%, stroke: 1pt + ink)
  #v(14pt)
  #grid(
    columns: (1.2fr, 1fr, 1.4fr),
    column-gutter: 18pt,
    [
      #text(font: mono, size: 10pt, fill: mid, tracking: 0.4pt)[#upper[Authors]]
      #v(6pt)
      #text(size: 13pt, weight: "medium")[
        #meta.authors.join(" · ")
      ]
    ],
    [
      #text(font: mono, size: 10pt, fill: mid, tracking: 0.4pt)[#upper[Period · Sample]]
      #v(6pt)
      #text(font: mono, size: 12pt)[2015.01 — 2025.12 · 210K cells]
    ],
    [
      #text(font: mono, size: 10pt, fill: mid, tracking: 0.4pt)[#upper[Published by]]
      #v(6pt)
      #text(size: 13pt, weight: "semibold")[#meta.org]
      #text(size: 13pt, fill: mid)[ · #(meta.team)]
    ],
  )
]

// ══════════════════════════════════════════════════════════════════════════
//                          SLIDE 2 — Executive Summary
// ══════════════════════════════════════════════════════════════════════════
#slide("Part 1 · 문제 제기", "02")[
  #title("3분 안에 보는 핵심 발견", sub: [본 분석이 데이터에서 잡아낸 세 가지 흔적과 정책 활용 영역])

  #grid(
    columns: (28pt, 1fr),
    row-gutter: 14pt, column-gutter: 12pt,

    text(font: mono, size: 14pt, fill: accent, weight: "semibold")[01],
    [
      #text(size: 18pt, weight: "semibold", tracking: -0.3pt)[
        회계연도 마감 직전, 집행이 *11월 대비 약 2.1배 점프*한다.
      ]
      #v(2pt)
      #text(size: 12pt, fill: mid)[
        사업별 정규화 비중 기준 11월 17.7% → 12월 37.2% (균등 가정 8.3%의 4.5배).
        *작은 사업일수록 점프 강도가 크다.*
      ]
    ],

    text(font: mono, size: 14pt, fill: accent, weight: "semibold")[02],
    [
      #text(size: 18pt, weight: "semibold", tracking: -0.3pt)[
        출연금형 사업은 *분기·반기 단위로 한꺼번에 정산*되며, 시간이 갈수록 강해진다.
      ]
      #v(2pt)
      #text(size: 12pt, fill: mid)[
        활동 동시 피크 정도(coherence) 0.54로 다른 사업 유형의 4–7배.
        *2015–17 → 2023–25 사이 진폭 5.5배 강화.*
      ]
    ],

    text(font: mono, size: 14pt, fill: accent, weight: "semibold")[03],
    [
      #text(size: 18pt, weight: "semibold", tracking: -0.3pt)[
        *집행률은 100%에 천장 압축*, 결과 지표는 *광범위하게 분산*.
      ]
      #v(2pt)
      #text(size: 12pt, fill: mid)[
        사업별 집행률 중앙값 100%, *약 67%가 95–100% 구간*에 압축.
        같은 분야의 결과 지표 변화율은 *-50%~+50% 광범위 분산* (σ ≈ 30%p).
      ]
    ],
  )

  #v(14pt)

  #callout(label: "정책 활용 영역", color: ink, bg: chip-bg)[
    본 분석은 *감사 자원 배분*·*경영평가 지표 개선*·*예산편성 협의*의 객관적 근거로 활용 가능하다.
    부처×결과 *4분면 점검 우선순위* + *자동 flagging 알고리즘*은 본 발표 후반에 제시.
  ]
]

// ══════════════════════════════════════════════════════════════════════════
//                          SLIDE 3 — 현장 딜레마 + 제도 배경
// ══════════════════════════════════════════════════════════════════════════
#slide("Part 1 · 문제 제기", "03")[
  #title("현장에서 매년 반복되는 풍경", sub: [세 가지 풍경 — 그러나 *같은 데이터 위에서 동시에* 본 적은 없다])

  #grid(
    columns: (1fr, 1fr),
    column-gutter: 24pt,

    [
      #chip("관찰 1", fg: neg, bg: rgb("#fee2e2"))
      #v(8pt)
      #text(size: 18pt, weight: "semibold")[
        "12월 되면 도로를 또 깐다"
      ]
      #v(6pt)
      #text(size: 11.5pt, fill: mid)[
        회계연도 마감 직전 *불용액 최소화 압력*과
        *차년도 이월 차단*이 결합해 12월에 집행이 몰린다.
        매년 언론 보도·감사원 지적이 반복.
      ]

      #v(20pt)

      #chip("관찰 2", fg: warn, bg: rgb("#fef3c7"))
      #v(8pt)
      #text(size: 18pt, weight: "semibold")[
        "출연기관은 어차피 모기관이 메워준다"
      ]
      #v(6pt)
      #text(size: 11.5pt, fill: mid)[
        출연금 비중이 큰 사업은 *분기·반기 정산 사이클*에 묶여 있어
        자율적 집행 규율이 약하다는 풍경.
        국회예산정책처 공식 지적 (2022).
      ]

      #v(20pt)

      #chip("관찰 3", fg: accent, bg: accent-bg)
      #v(8pt)
      #text(size: 18pt, weight: "semibold")[
        "집행률만 잘 맞추면 평가는 통과한다"
      ]
      #v(6pt)
      #text(size: 11.5pt, fill: mid)[
        공공기관 경영평가에서 *집행률은 측정 쉬운 지표*,
        결과 지표는 *측정 어려운 지표*.
        측정 격차가 행동에 흔적을 남긴다.
      ]
    ],

    align(left + top)[
      #v(6pt)
      #callout(label: "제도적 배경", color: ink, bg: chip-bg)[
        - *단년도 회계주의* — 미사용 예산은 차년도 이월 불가
        - *12.31 기준 집행률* — 평가의 가장 강력한 단일 지표
        - *디브레인 시스템* — 일별 집행 데이터 완벽 측정
        - *결과 지표 측정 비대칭* — outcome은 외부 요인 다수
      ]
      #v(16pt)
      #callout(label: "본 분석의 출발 질문", color: accent, bg: accent-bg)[
        이 세 풍경이 *공개된 재정·사회 데이터*에 *어디서·얼마나·어떤 형태로* 나타나는가?
        그리고 *서로 정합되는 단일 구조*인가, 아니면 독립적 현상의 우연인가?
      ]
    ],
  )
]

// ══════════════════════════════════════════════════════════════════════════
//                          SLIDE 4 — 분석 데이터 파이프라인
// ══════════════════════════════════════════════════════════════════════════
#slide("Part 2 · EDA", "04")[
  #title("분석 데이터 — 21만 셀 패널", sub: [공공 API · 공개 다운로드 기반, 비영리·연구 활용 허용 범위 내])

  #grid(
    columns: (1.4fr, 1fr),
    column-gutter: 22pt,

    [
      #set text(size: 11.5pt)
      #table(
        columns: (1.5fr, 1fr, 1fr, 1.2fr),
        table.header[데이터][기간][단위][출처],
        [월별 집행 (재정)],       [2015 — 2025], [활동 × 월], [열린재정 / KODAS],
        [편성목 구성 (재정)],     [2015 — 2025], [활동 × 년], [열린재정 / KODAS],
        [14분야 결과 지표],       [2015 — 2025], [분야 × 년], [KOSIS · ECOS · 공공],
        [소비자물가 (외생통제)],  [2015 — 2025], [전국 × 월], [한국은행 ECOS],
        [온실가스 인벤토리],      [2015 — 2023], [전국 × 년], [GIR],
        [도로교통 통계],          [2015 — 2025], [전국 × 년], [도로교통공단],
      )
    ],

    [
      #v(10pt)
      #kpi("활동 수", "1,557", sub: "세부 활동 단위")
      #v(8pt)
      #kpi("기간 (개월)", "132", sub: "2015.01 — 2025.12 (11년)")
      #v(8pt)
      #kpi("총 셀 수", "≈ 21 만", sub: "활동 × 개월 결합 패널")
    ],
  )

  #v(8pt)

  #text(size: 11pt, fill: mid, style: "italic")[
    디브레인이 산출하는 일별 집행 데이터가 월별로 공개 — 본 분석은 *이 공개 데이터만으로* 11년 흐름을
    따라가며, 외부 결과 지표를 시점 기준으로 결합해 정제했다.
  ]
]

// ══════════════════════════════════════════════════════════════════════════
//                          SLIDE 5 — EDA① 12월 점프
// ══════════════════════════════════════════════════════════════════════════
#slide("Part 2 · EDA", "05")[
  #title("EDA ① 12월 집행 점프", sub: [사업당 100% 정규화 후 본 월별 분포 — 11월 17.7% → 12월 37.2%])

  #grid(
    columns: (1.5fr, 1fr),
    column-gutter: 18pt,

    [
      #image("figures/eda/fig_2_2_monthly_exec_total.png", width: 100%)
      #fig-id("FIG-2.2", note: [사업 규모 4분위별 월 평균 집행 비중 — *작은 사업*(Q1)이 12월에 *15.4%*, *큰 사업*(Q4)은 *10.9%*])
    ],

    [
      #v(20pt)
      #kpi("12월 비중 (전체)", "37.2 %", sub: "균등 가정 8.3% 의 *4.5배*")
      #v(8pt)
      #kpi("11→12월 점프", "× 2.1", sub: "전체 평균 점프 배수")
      #v(8pt)
      #kpi("작은 사업 (Q1)", "× 2.6", sub: "11월 6.0% → 12월 15.4%")
    ],
  )
]

// ══════════════════════════════════════════════════════════════════════════
//                          SLIDE 6 — EDA② 출연금 일률 정산
// ══════════════════════════════════════════════════════════════════════════
#slide("Part 2 · EDA", "06")[
  #title("EDA ② 출연금형 사업의 일률 정산", sub: [대표 활동의 월별 시계열 — 매월 균등 vs 특정 시점 한꺼번에 정산])

  #grid(
    columns: (1.5fr, 1fr),
    column-gutter: 18pt,

    [
      #image("figures/eda/fig_2_4_activity_patterns.png", width: 100%)
      #fig-id("FIG-2.4", note: [위 두 사례는 *매월 균등* (국민연금급여·재외공관 인건비), 아래 두 사례는 *특정 시점에 큰 정산* — 직불기금·지역경제지원])
    ],

    [
      #v(18pt)
      #text(size: 14pt, weight: "semibold")[
        분야 간 출연금 비중 격차 *80배*
      ]
      #v(6pt)
      #text(size: 11.5pt, fill: mid)[
        국방 0.2% — 과학기술 36.2%. \
        같은 회계 압력이지만 *분야별로 다른 모양*으로 발현되는 첫 단서.
      ]
      #v(14pt)
      #set text(size: 11pt)
      #table(
        columns: (1fr, auto),
        table.header[분야][출연금 비중],
        [과학기술],     text(fill: warn, weight: "semibold")[36.2%],
        [통신],         text(fill: warn, weight: "semibold")[33.4%],
        [사회복지],     text(fill: soft)[0.4%],
        [국방],         text(fill: soft)[0.2%],
      )
    ],
  )
]

// ══════════════════════════════════════════════════════════════════════════
//                          SLIDE 7 — EDA③ 천장 압축 vs 결과 분산
// ══════════════════════════════════════════════════════════════════════════
#slide("Part 2 · EDA", "07")[
  #title("EDA ③ 집행률 천장 vs 결과 지표 분산", sub: [두 분포의 *모양*이 체계적으로 다르다 — 두 변수가 별개로 움직인다는 뜻])

  #grid(
    columns: (1.6fr, 1fr),
    column-gutter: 18pt,

    [
      #image("figures/eda/fig_2_5_exec_vs_outcome.png", width: 100%)
      #fig-id("FIG-2.5", note: [좌: 사업별 집행률 (n=29,892, 95–100%에 *2/3 압축*) · 우: 분야별 결과 변화율 (n=3,046, ±50%, σ ≈ 30%p)])
    ],

    [
      #v(10pt)
      #kpi("집행률 중앙값", "100 %", sub: "사업별 연간 n=29,892")
      #v(6pt)
      #kpi("95–100% 압축", "≈ 67 %", sub: "천장 구간 비율")
      #v(6pt)
      #kpi("결과 지표 σ", "30 %p", sub: "광범위 분산")
    ],
  )
]

// ══════════════════════════════════════════════════════════════════════════
//                          SLIDE 8 — EDA가 던지는 3 분석 질문
// ══════════════════════════════════════════════════════════════════════════
#slide("Part 2 · EDA", "08")[
  #title("EDA가 던지는 세 가지 분석 질문", sub: [세 관찰은 독립 우연인가, 서로 맞물리는 단일 구조인가?])

  #v(10pt)

  #grid(
    columns: (32pt, 1fr),
    row-gutter: 18pt, column-gutter: 12pt,

    text(font: mono, size: 16pt, fill: accent, weight: "semibold")[Q1],
    [
      #text(size: 17pt, weight: "semibold")[
        12월 점프의 *사업 유형별 이질성*은 어떻게 분포하는가?
      ]
      #v(3pt)
      #text(size: 11.5pt, fill: mid)[
        모든 사업에 균질한 압력인가, 사업 *지출 구조*에 따라 다른가? → *PART 4 발견 ②*
      ]
    ],

    text(font: mono, size: 16pt, fill: accent, weight: "semibold")[Q2],
    [
      #text(size: 17pt, weight: "semibold")[
        집행률과 결과 지표 *격차의 결정 요인*은 무엇인가?
      ]
      #v(3pt)
      #text(size: 11.5pt, fill: mid)[
        14분야 행정 분류 vs 데이터가 말하는 사업 형태 — 어느 단위가 행동을 설명하는가? → *PART 4 발견 ①·④*
      ]
    ],

    text(font: mono, size: 16pt, fill: accent, weight: "semibold")[Q3],
    [
      #text(size: 17pt, weight: "semibold")[
        일률 정산 패턴은 *시간 경과에 따라 강화되는가*?
      ]
      #v(3pt)
      #text(size: 11.5pt, fill: mid)[
        출연금형 사이클이 11년간 안정적인가, 진행형 패턴인가? → *PART 4 발견 ③*
      ]
    ],
  )

  #v(10pt)

  #callout(label: "다음 파트의 약속", color: ink, bg: chip-bg)[
    PART 3에서 *세 가지 새로운 렌즈*(군집·RDD·웨이블릿)로 같은 데이터를 다시 본다 —
    어떤 도구가 무엇을 찾아내는지 *수식 없이 직관*으로 설명한 뒤, PART 4에서 발견을 제시한다.
  ]
]

// ══════════════════════════════════════════════════════════════════════════
//                          SLIDE 9 — 새 렌즈 개요
// ══════════════════════════════════════════════════════════════════════════
#slide("Part 3 · 방법론 직관", "09")[
  #title("EDA를 넘는 세 가지 새 렌즈", sub: [같은 데이터에 *서로 다른 도구*를 대보면 다른 면이 보인다])

  #v(10pt)

  #grid(
    columns: (1fr, 1fr, 1fr),
    column-gutter: 14pt,

    block(width: 100%, inset: 16pt, fill: ghost,
      stroke: (left: 3pt + neg, rest: 0.5pt + line-c), radius: (right: 5pt))[
      #chip("Lens 1", fg: neg, bg: rgb("#fee2e2"))
      #v(8pt)
      #text(size: 18pt, weight: "semibold")[
        경계 현미경 (RDD)
      ]
      #v(4pt)
      #text(size: 12pt, fill: mid, weight: "medium")[
        *행정적 절단점 검증*
      ]
      #v(8pt)
      #text(size: 11pt, fill: mid)[
        12월 1일이라는 *인위적 달력 경계선* 직전·직후 며칠을 비교한다. 본질적 변동이 아닌
        *행정 시점 효과*만 분리.
      ]
    ],

    block(width: 100%, inset: 16pt, fill: ghost,
      stroke: (left: 3pt + accent, rest: 0.5pt + line-c), radius: (right: 5pt))[
      #chip("Lens 2", fg: accent, bg: accent-bg)
      #v(8pt)
      #text(size: 18pt, weight: "semibold")[
        군집 분석
      ]
      #v(4pt)
      #text(size: 12pt, fill: mid, weight: "medium")[
        *사업 체질 검사*
      ]
      #v(8pt)
      #text(size: 11pt, fill: mid)[
        1,557개 사업을 *돈 쓰는 패턴* 으로 묶는다. 사람이 분류하기 전에 *기계가 스스로* 4개의
        사업 유형을 찾는다.
      ]
    ],

    block(width: 100%, inset: 16pt, fill: ghost,
      stroke: (left: 3pt + warn, rest: 0.5pt + line-c), radius: (right: 5pt))[
      #chip("Lens 3", fg: warn, bg: rgb("#fef3c7"))
      #v(8pt)
      #text(size: 18pt, weight: "semibold")[
        시간 지진계 (Wavelet)
      ]
      #v(4pt)
      #text(size: 12pt, fill: mid, weight: "medium")[
        *주기의 시간 진화*
      ]
      #v(8pt)
      #text(size: 11pt, fill: mid)[
        같은 사이클이 *시간이 갈수록 강해지는지* 추적한다. 지진계가 진폭 변화를 잡듯, 패턴 강도
        변화를 시각화.
      ]
    ],
  )

  #v(14pt)

  #callout(label: "본 발표의 방법론 사용 원칙", color: ink, bg: chip-bg)[
    수식은 부록·보고서 §C로 분리. 각 도구를 *무엇을 찾는 렌즈인지*만 직관으로 설명한다.
    *세 렌즈가 같은 방향을 가리키는지*가 본 발표 *PART 5 교차 검증*의 핵심 점검 대상이다.
  ]
]

// ══════════════════════════════════════════════════════════════════════════
//                          SLIDE 10 — RDD = 경계 현미경
// ══════════════════════════════════════════════════════════════════════════
#slide("Part 3 · 방법론 직관", "10")[
  #title("Lens 1 — RDD: 12월 1일 직전·직후 며칠 비교", sub: [회귀불연속 설계 (Regression Discontinuity Design)])

  #grid(
    columns: (1fr, 1fr),
    column-gutter: 20pt,

    [
      #v(6pt)
      #text(size: 14pt, weight: "semibold")[
        왜 며칠 단위로 비교하는가?
      ]
      #v(8pt)
      #text(size: 12pt, fill: mid)[
        - 사업 본질 변동(공정률·계약 일정·계절 수요)은 *11월과 12월 며칠 사이*에 급변하지 않는다.
        - 회계연도 마감이라는 *행정적 시점*은 12월 1일을 기점으로 압력을 만든다.
        - 두 시점의 *일평균 집행*을 비교하면 사업 본질을 거의 통제한 *행정 시점 효과*에 가까워진다.
      ]

      #v(12pt)

      #callout(label: "본 분석의 핵심 측정", color: ink, bg: chip-bg)[
        *11월 마지막 주 → 12월 첫 주 일평균 집행 배수* (활동 단위). \
        배수 1.0 = 시점 효과 없음, 2.0 = 일평균 두 배 점프.
      ]
    ],

    [
      #v(8pt)
      #image("figures/report/h22_rdd_yearly.png", width: 100%)
      #fig-id("FIG-3.4", note: [연도별 12월 점프 — 한국 전체 *1.91배*(주황), 11년 내내 안정적 반복])
    ],
  )
]

// ══════════════════════════════════════════════════════════════════════════
//                          SLIDE 11 — 군집 = 사업 체질 검사
// ══════════════════════════════════════════════════════════════════════════
#slide("Part 3 · 방법론 직관", "11")[
  #title("Lens 2 — 군집: 사업 체질 검사", sub: [지출 구성 12개 특징으로 1,557개 활동을 *데이터가 스스로* 묶는다])

  #grid(
    columns: (1fr, 1fr),
    column-gutter: 20pt,

    [
      #v(6pt)
      #text(size: 14pt, weight: "semibold")[
        분야 vs 사업 형태 — 어느 단위가 진짜인가
      ]
      #v(8pt)
      #text(size: 12pt, fill: mid)[
        - *기존 행정 분류*: 14개 분야 (사회복지·교육·국방 …)
        - *데이터 기반 분류*: 지출 구성(인건비·자산취득·출연금·일반 비중)으로 사업을 묶음
        - 12차원을 2차원 좌표로 압축한 뒤 *밀도가 높은 영역*을 자동으로 발견
        - *분야 라벨로는 R² ≈ 0.014*, 사업 유형 추가 시 *R² 2.7배 증가* (PART 4에서)
      ]

      #v(12pt)

      #callout(label: "직관", color: ink, bg: chip-bg)[
        분야는 *행정 분류*, 사업 형태는 *지출 체질*. 진짜 행동을 결정하는 단위가 무엇인지를
        데이터에 직접 묻는다.
      ]
    ],

    [
      #image("figures/report/h3_umap.png", width: 75%)
      #fig-id("FIG-4.2", note: [활동 2차원 좌표 — 같은 분야가 공간상 분리, 다른 분야의 같은 형태가 가까이 모인다])
    ],
  )
]

// ══════════════════════════════════════════════════════════════════════════
//                          SLIDE 12 — Wavelet = 시간 지진계
// ══════════════════════════════════════════════════════════════════════════
#slide("Part 3 · 방법론 직관", "12")[
  #title("Lens 3 — Wavelet: 시간 지진계", sub: [같은 사이클이 *시간이 갈수록 강해지는지* 추적])

  #grid(
    columns: (1fr, 1fr),
    column-gutter: 20pt,

    [
      #v(6pt)
      #text(size: 14pt, weight: "semibold")[
        FFT로는 보이지 않는 것
      ]
      #v(8pt)
      #text(size: 12pt, fill: mid)[
        - *FFT*: 11년 *평균 진폭*만 측정 — 정상성 가정 필요.
        - 한국 재정 환경은 *정책 변화점 다수* (2007 국가재정법, 2014 회계제도 개편, 2020 코로나 확장재정 등).
        - *Wavelet*은 *시간 축에서 진폭이 어떻게 변했는지* 추적 가능.
        - 2015–2017 vs 2023–2025 변화율로 *진행형 패턴* 식별.
      ]

      #v(12pt)

      #callout(label: "비유", color: ink, bg: chip-bg)[
        지진계가 진폭의 *시간 변화*를 잡듯, Wavelet은 12개월 주기 진폭의 *11년 진화*를 잡는다.
        FFT가 *평균 강도*라면 Wavelet은 *시간별 강도 곡선*.
      ]
    ],

    [
      #v(8pt)
      #image("figures/report/h28_evolution.png", width: 100%)
      #fig-id("FIG-5.3", note: [사업 유형별 12개월 cycle 진폭의 시간 진화 — 출연금형 *+554%*, 인건비형 −0.8%(통제)])
    ],
  )
]

// ══════════════════════════════════════════════════════════════════════════
//                          SLIDE 13 — 발견 ① 사업 4유형
// ══════════════════════════════════════════════════════════════════════════
#slide("Part 4 · 발견", "13")[
  #title("발견 ① 데이터가 말하는 4개 사업 형태", sub: [기계가 스스로 묶었더니 *행정 실무 직관과 정확히 일치*])

  #grid(
    columns: (1.2fr, 1fr),
    column-gutter: 18pt,

    [
      #image("figures/report/h8_panel.png", width: 100%)
      #fig-id("FIG-4.1", note: [분야 단독 ΔR² ≈ 0, 사업 유형 추가 시 R² 2.7배 증가])
    ],

    [
      #set text(size: 11.5pt)
      #table(
        columns: (1fr, auto, 1.3fr),
        table.header[사업 형태][n][지출 프로파일],
        [C0 인건비형],    [129],   [인건비 +3.07σ],
        [C1 자산취득형],  [99],    [자산취득 +3.28σ],
        [C2 출연금형],    [154],   [출연금 +2.89σ],
        [C3 정상사업],    [1,175], [평균 부근],
      )
      #v(14pt)
      #grid(
        columns: (1fr, 1fr),
        column-gutter: 8pt,
        kpi("분야만 사용", "R² ≈ 0", sub: "행정 분류 설명력 부재"),
        kpi("사업 유형 추가", "+0.025", sub: "전체 설명력 2.7배 증가"),
      )
    ],
  )

  #v(8pt)

  #callout(label: "결론", color: ink, bg: chip-bg)[
    *분야 라벨은 사업 행동을 거의 설명하지 못한다.* 진짜 단위는 *지출 구조* — 인건비·자산취득·
    출연금·정상 4가지 형태가 행동의 1차 결정 변수다. 이 분류를 이후 모든 발견에서 사용한다.
  ]
]

// ══════════════════════════════════════════════════════════════════════════
//                          SLIDE 14 — 발견 ② 12월 점프 격차
// ══════════════════════════════════════════════════════════════════════════
#slide("Part 4 · 발견", "14")[
  #title("발견 ② 12월 점프는 사업 유형별로 3배 격차", sub: [전체 1.91배 — 자산취득형 3.42배, 인건비·출연금형 1.1배대])

  #grid(
    columns: (1fr, 1fr),
    column-gutter: 18pt,

    [
      #image("figures/report/h22_rdd_appendix.png", width: 100%)
      #fig-id("FIG-3.3", note: [사업 형태별 12월 점프 효과 분포 — 자산취득형 압도 우세, 출연금형은 점프 자체로는 통계 미달])
    ],

    [
      #v(8pt)
      #grid(
        columns: (1fr, 1fr),
        column-gutter: 8pt, row-gutter: 8pt,
        kpi("자산취득형", "× 3.42", sub: "공정률 + 회계 마감 결합"),
        kpi("정상사업", "× 2.24", sub: "베이스라인 (n=1,175)"),
        kpi("인건비형", "× 1.12", sub: "구조상 평탄"),
        kpi("출연금형", "× 1.10", sub: "RDD 약함, § 5에서 다른 모양"),
      )
    ],
  )

  #v(8pt)

  #callout(label: "현장 풍경과의 일치", color: ink, bg: chip-bg)[
    "12월 되면 도로를 또 깐다"는 현장 풍경이 *자산취득형 3.42배 점프*로 데이터에 흔적이 남는다 —
    공정률 마감과 회계 마감이 겹쳐 12월 직전 한계비용이 낮아지기 때문. 현장과 데이터가 같은 쪽을 가리킨다.
  ]
]

// ══════════════════════════════════════════════════════════════════════════
//                          SLIDE 15 — 발견 ③ 출연금형 사이클
// ══════════════════════════════════════════════════════════════════════════
#slide("Part 4 · 발견", "15")[
  #title("발견 ③ 출연금형 — 연 사이클·동시 피크에서 압도 우세", sub: [12월 RDD는 약하지만 *모양 차이* — 단발 급등 아닌 연중 누적])

  #grid(
    columns: (1fr, 1fr),
    column-gutter: 18pt,

    [
      #image("figures/report/h27_psd.png", width: 100%)
      #fig-id("FIG-5.1", note: [PSD k=1 진폭 — 출연금형(주황) 0.332로 다른 유형의 2–3.4배])
    ],

    [
      #image("figures/report/h27_coherence.png", width: 100%)
      #fig-id("FIG-5.2", note: [Phase coherence — 출연금형 0.54로 다른 유형의 4–7배. 활동들이 같은 달에 일제히 피크])
    ],
  )

  #v(6pt)

  #grid(
    columns: (1fr, 1fr, 1fr),
    column-gutter: 12pt,
    kpi("PSD 12개월 진폭", "0.332", sub: "다른 유형 0.097–0.172의 2–3.4배"),
    kpi("Phase coherence", "0.54", sub: "다른 유형 0.08–0.13의 4–7배"),
    kpi("§ 3 12월 RDD", "× 1.10", sub: "점프 약함 — 모양 차이"),
  )
]

// ══════════════════════════════════════════════════════════════════════════
//                          SLIDE 16 — 발견 ④ 5.5배 시간 강화
// ══════════════════════════════════════════════════════════════════════════
#slide("Part 4 · 발견", "16")[
  #title("발견 ④ 출연금형 사이클 — 11년간 5.5배 강화", sub: [+554% — 인건비형 통제(−0.8%)와 극단 비대칭])

  #grid(
    columns: (1.2fr, 1fr),
    column-gutter: 18pt,

    [
      #image("figures/report/h28_evolution.png", width: 100%)
      #fig-id("FIG-5.3", note: [12개월 cycle 진폭의 시간 진화 — 2020년 코로나 시기 급격 상승, 코로나 이후 정체 구간])
    ],

    [
      #set text(size: 11.5pt)
      #table(
        columns: (1fr, auto, auto, auto),
        table.header[유형][2015-17][2023-25][변화율],
        [인건비형 (통제)], [0.007], [0.007], text(fill: soft)[−0.8%],
        [자산취득형],     [0.055], [0.150], [+174.7%],
        [정상사업],       [0.057], [0.237], [+316.7%],
        [출연금형],       [0.201], [1.315], text(fill: warn, weight: "semibold")[+553.6%],
      )
      #v(10pt)
      #callout(label: "현장 풍경과의 일치", color: ink, bg: chip-bg)[
        "출연기관은 모기관이 메워준다"는 풍경이 *동시 피크 coherence 0.54*로 데이터에 흔적이 남는다.
        *진행형 패턴*임이 시간 축에서 확인.
      ]
    ],
  )
]

// ══════════════════════════════════════════════════════════════════════════
//                          SLIDE 17 — 세 발견의 정합성
// ══════════════════════════════════════════════════════════════════════════
#slide("Part 4 · 발견", "17")[
  #title("세 발견은 독립 우연이 아니다", sub: [*사업 지출 구조*가 점프와 사이클을 모두 결정])

  #v(10pt)

  #set text(size: 12pt)
  #table(
    columns: (1.2fr, 1fr, 1fr, 1fr, 1.4fr),
    table.header[사업 형태][n][§ 3 12월 점프][§ 5 연 사이클][한 줄 해석],
    [자산취득형], [99],    text(fill: neg, weight: "semibold")[× 3.42 (최강)], [중],          [공정률 + 회계 마감 결합 — 12월 직후 이산 급등],
    [출연금형],   [154],   [× 1.10 (약함)],                                   text(fill: warn, weight: "semibold")[0.332 (최강)], [위탁기관 정산 — 연중 분산 누적, 시간 강화],
    [인건비형],   [129],   text(fill: soft)[× 1.12],                          text(fill: soft)[0.097],                            [매월 균등 — *양쪽 모두* 평탄],
    [정상사업],   [1,175], [× 2.24],                                          [0.115],                                            [베이스라인 — 일반 행정 마감 결합],
  )

  #v(14pt)

  #callout(label: "통합 해석 — 단일 구조의 흔적", color: ink, bg: chip-bg)[
    *시점 조정이 가능한 사업*만 회계 압력에 응답한다 — 자산취득형은 12월 직후 단발 급등으로,
    출연금형은 연중 분산 + 누적 + 시간 강화로. *인건비형의 평탄함*은 도구의 신뢰성을 입증한다
    (조정 불가 사업에서 신호가 없어야 한다). 세 발견은 *지출 구조라는 단일 변수*가 형태를 다르게
    발현시킨 결과다.
  ]
]

// ══════════════════════════════════════════════════════════════════════════
//                          SLIDE 18 — 교차 검증
// ══════════════════════════════════════════════════════════════════════════
#slide("Part 5 · 교차 검증", "18")[
  #title("도구 간 결과 차이가 의미하는 것", sub: [세 측정 도구(FFT·STL·NeuralProphet) 교차 검증])

  #grid(
    columns: (1fr, 1.3fr),
    column-gutter: 18pt,

    [
      #image("figures/report/np_correlation.png", width: 100%)
      #fig-id("FIG-7.1", note: [세 도구 상호 상관 ≈ 0 — 같은 신호의 서로 독립된 시각])
    ],

    [
      #v(6pt)
      #text(size: 14pt, weight: "semibold")[
        세 도구는 *같은 신호의 다른 면*을 본다
      ]
      #v(8pt)
      #text(size: 11.5pt, fill: mid)[
        - FFT: 주파수 영역의 *진폭 비중*
        - STL: 시간 영역의 *추세와 나머지로 가르기*
        - NeuralProphet: 전환점 보정 후 *더해서 푸는 분해*
      ]
      #v(10pt)
      #image("figures/report/np_3way_outcome.png", width: 100%)
      #fig-id("FIG-7.2", note: [보건·통신은 세 도구 모두 음 신호로 일관, 사회복지는 도구에 따라 부호가 갈림])
    ],
  )

  #v(6pt)

  #callout(label: "트라이앵귤레이션 원칙", color: ink, bg: chip-bg)[
    *"셋이 같은 답"이 아니라 "셋이 어디서 합의하고 어디서 갈리는지"*가 분석의 일부.
    합의 분야(보건·통신)는 견고한 발견, 갈림 분야(사회복지)는 *자기 비판의 출발점*.
  ]
]

// ══════════════════════════════════════════════════════════════════════════
//                          SLIDE 19 — 측정 격차 매개 경로
// ══════════════════════════════════════════════════════════════════════════
#slide("Part 5 · 교차 검증", "19")[
  #title("측정 격차 — 집행률은 만점, 결과는 제각각", sub: [*출연금 비중 → 시점 조정 → 결과 지표* 연결 통로의 분야별 분해])

  #grid(
    columns: (1.3fr, 1fr),
    column-gutter: 18pt,

    [
      #set text(size: 12pt)
      #table(
        columns: (1fr, auto, auto, 1.5fr),
        table.header[분야][n][신호 강도][해석],
        [농림수산], [충분], text(fill: pos, weight: "semibold")[안정된 연결 통로], [*14분야 중 유일* — 통계적으로 안정],
        [사회복지], [6],    [방향성 있으나 약함],                                  [표본 6개로 통계 미달],
        [환경],     [4],    text(fill: soft)[추정 불가],                          [표본 4개로 신호/잡음 분리 불가],
        [그 외 11분야], [—], text(fill: soft)[신호 없음],                          [추정값 0 근처],
      )
    ],

    [
      #v(10pt)
      #callout(label: "두 가지 의미", color: ink, bg: chip-bg)[
        *(1) 분야 평균은 신호를 가린다.* \
        1개 분야 강한 효과가 13개 약한 신호에 희석.

        *(2) 측정 격차의 분포는 사업 형태에 결합한다.* \
        출연금형이 많은 분야에서 시점 조정이 결과 지표에 흔적을 남긴다.
      ]
      #v(10pt)
      #callout(label: "예외 — 사회복지", color: warn, bg: rgb("#fef3c7"))[
        12월 집중이 클수록 *빈곤 격차 완화* 방향 (r=−0.86, 거시 경기 통제 후 강화).
        측정 격차가 항상 결과의 희생으로 발현되지는 않는다.
      ]
    ],
  )
]

// ══════════════════════════════════════════════════════════════════════════
//                          SLIDE 20 — 부처×결과 4분면
// ══════════════════════════════════════════════════════════════════════════
#slide("Part 5 · 교차 검증", "20")[
  #title("부처×결과 4분면 — 점검 우선순위", sub: [집행률 압력 × 결과 정체로 *우상단 = 즉시 점검 후보*])

  #grid(
    columns: (1.2fr, 1fr),
    column-gutter: 18pt,

    [
      #image("figures/h14_quadrant.png", width: 100%)
      #fig-id("FIG-8.1", note: [부처별 굿하트 노출 × 결과 변수 4분면 — Q2(우상단)가 점검 우선 부처])
    ],

    [
      #v(8pt)
      #text(size: 14pt, weight: "semibold")[4분면 해석]
      #v(6pt)
      #text(size: 11.5pt, fill: mid)[
        - *Q1 우하단*: 집행률 압력 강함 + 결과 개선 → *우연히 정렬* (사회복지형)
        - *Q2 우상단*: 집행률 압력 강함 + 결과 정체 → *최우선 점검 후보*
        - *Q3 좌상단*: 압력 약함 + 결과 정체 → 측정 격차 외 요인
        - *Q4 좌하단*: 압력 약함 + 결과 개선 → 모범 사례
      ]
      #v(12pt)
      #callout(label: "§ 7 교차 검증과의 연결", color: ink, bg: chip-bg)[
        *세 도구 일관 신호 분야*는 우선순위 상위로, *측도 갈림 분야*는 *재검토 큐*로 분리.
        자기 비판이 산출물의 *신뢰도 등급*에 직접 반영.
      ]
    ],
  )
]

// ══════════════════════════════════════════════════════════════════════════
//                          SLIDE 21 — 학술 frame 한눈에
// ══════════════════════════════════════════════════════════════════════════
#slide("Part 6 · 학술 frame 매칭", "21")[
  #title("학계는 30년째 같은 이름을 붙여왔다", sub: [본 분석 세 발견 ↔ 행정학·경제학 이론의 한눈에 매칭])

  #v(10pt)

  #set text(size: 12pt)
  #table(
    columns: (1.6fr, 1.4fr, 2fr, 1.2fr),
    table.header[본 발견 (일상어)][학계가 붙인 이름][핵심 명제][대표 문헌],
    [12월 몰아쓰기 + 점프 격차],  [*굿하트-캠벨 법칙*],  [평가 지표가 도입되면 *해당 지표 자체의 신뢰성이 저하*],     [Bevan & Hood (2006)],
    [집행률↔결과 측정 격차],      [*다업무 계약 이론*],  [측정 쉬운 일에 보상 → 측정 어려운 일의 *체계적 희생*],     [Holmstrom & Milgrom (1991)],
    [출연기관 사이클 + 시간 강화], [*연성 예산 제약*],    [모기관 보전 기대 → *자율적 규율 약화*],                    [Kornai & Maskin (2003)],
  )

  #v(14pt)

  #callout(label: "본 분석의 위치", color: ink, bg: chip-bg)[
    세 이론은 *각각 단편적 인용*은 한국 재정학에 존재하나, *세 이론을 동시에* 한국 중앙정부 재정에
    *정량 진단*으로 묶은 사례는 부재. 본 분석은 이 빈자리를 채우는 시도.
  ]
]

// ══════════════════════════════════════════════════════════════════════════
//                          SLIDE 22 — frame이 설명하는 것
// ══════════════════════════════════════════════════════════════════════════
#slide("Part 6 · 학술 frame 매칭", "22")[
  #title("세 이론은 한 현상의 다른 면을 본다", sub: [상호 보완 framing — 발견을 *우연이 아닌 구조*로 묶는다])

  #v(10pt)

  #grid(
    columns: (1fr, 1fr, 1fr),
    column-gutter: 14pt,

    block(width: 100%, inset: 16pt, fill: ghost,
      stroke: (left: 3pt + accent, rest: 0.5pt + line-c), radius: (right: 5pt))[
      #chip("거대 frame", fg: accent, bg: accent-bg)
      #v(8pt)
      #text(size: 16pt, weight: "semibold")[
        굿하트-캠벨
      ]
      #v(6pt)
      #text(size: 11pt, fill: mid)[
        *"측정이 행동을 바꾼다"* — 어떤 지표가 평가 기준이 되면 사람들은 *그 지표 잘 받기* 행동.
        지표 신뢰성 저하.
      ]
    ],

    block(width: 100%, inset: 16pt, fill: ghost,
      stroke: (left: 3pt + neg, rest: 0.5pt + line-c), radius: (right: 5pt))[
      #chip("왜 특정 영역인가", fg: neg, bg: rgb("#fee2e2"))
      #v(8pt)
      #text(size: 16pt, weight: "semibold")[
        다업무 계약
      ]
      #v(6pt)
      #text(size: 11pt, fill: mid)[
        *"측정 난이도 격차가 결정"* — 집행률은 측정 쉽고, 결과 지표는 측정 어렵다. 어려운 쪽이
        체계적 희생.
      ]
    ],

    block(width: 100%, inset: 16pt, fill: ghost,
      stroke: (left: 3pt + warn, rest: 0.5pt + line-c), radius: (right: 5pt))[
      #chip("왜 자율 규율 약한가", fg: warn, bg: rgb("#fef3c7"))
      #v(8pt)
      #text(size: 16pt, weight: "semibold")[
        연성 예산 제약
      ]
      #v(6pt)
      #text(size: 11pt, fill: mid)[
        *"외부 보전 기대가 결정"* — 모기관·정부가 메워주리라는 기대 환경에서 자율 규율 약화.
        사회주의 기업 분석에서 출발.
      ]
    ],
  )

  #v(14pt)

  #callout(label: "트라이앵귤레이션 원칙 — 셋의 발산도 분석의 일부", color: ink, bg: chip-bg)[
    세 이론은 *만장일치가 아닌 상호 보완*이며, 발산 지점이 자기 비판의 출발점. 자세한 frame 매칭과
    정합성 점검은 *분석보고서 § 6* 참조.
  ]
]

// ══════════════════════════════════════════════════════════════════════════
//                          SLIDE 23 — 제언 ① 평가 지표 다각화
// ══════════════════════════════════════════════════════════════════════════
#slide("Part 7 · 정책 제언", "23")[
  #title("제언 ① 사업 형태별 평가 지표 다각화", sub: [모든 사업에 *일괄 100% 집행* 잣대 → *유형별 차등 유연성*])

  #v(10pt)

  #set text(size: 12pt)
  #table(
    columns: (1fr, 1fr, 1.6fr, 1.6fr),
    table.header[사업 형태][n][현 평가 압력][제언 — 평가 가중 조정],
    [인건비형],   [129],   [집행률 자체가 큰 의미 없음 (구조상 평탄)],   [*집행률 가중 축소*, 운영 효율 지표 신설],
    [자산취득형], [99],    [12월 마감 3.42배 점프 — 품질 저하 우려],     [*분기·반기 진행률* 가중, 12월 단독 평가 완화],
    [출연금형],   [154],   [연중 분산 정산 — 12월 점프 의미 약화],       [*위탁기관 정산 시점 분산* 인센티브 + 결과 지표 비중 강화],
    [정상사업],   [1,175], [현행 집행률 평가의 주 대상],                 [기존 체계 유지, 결과 지표 보완],
  )

  #v(14pt)

  #callout(label: "근거", color: ink, bg: chip-bg)[
    *§ 4 분야 라벨은 R² ≈ 0, 사업 형태가 진짜 단위* + *§ 3 사업 유형별 점프 1.1배–3.4배 격차*에서
    직접 도출. 한 잣대를 모든 사업에 적용하는 현행 평가는 *체질이 다른 사업을 같은 모양으로 강제*하는 셈.
  ]
]

// ══════════════════════════════════════════════════════════════════════════
//                          SLIDE 24 — 제언 ② 자동 flagging
// ══════════════════════════════════════════════════════════════════════════
#slide("Part 7 · 정책 제언", "24")[
  #title("제언 ② 디브레인 기반 자동 flagging 체계", sub: [본 분석 모델을 *11월 말 기준 사전 경고*로 운영 가능])

  #grid(
    columns: (1fr, 1fr),
    column-gutter: 20pt,

    [
      #text(size: 14pt, weight: "semibold")[운영 시나리오]
      #v(8pt)
      #text(size: 12pt, fill: mid)[
        1. *디브레인 일일 집행* 데이터에 본 분석 모델을 적용
        2. *11월 말 기준* — 12월 예상 집행 패턴 사전 추정
        3. *3 시그마 초과* 활동 자동 추출 (점프 강도·동시 피크 기준)
        4. *부처×결과 4분면 + 사업 형태* 결합한 우선순위 큐 생성
        5. 감사원·기재부 점검팀에 *주간 단위* 통지
      ]
      #v(10pt)
      #callout(label: "운영 효과", color: ink, bg: chip-bg)[
        본 분석은 *11년 사후 분석*이지만, 모델은 *준 실시간*으로 운영 가능.
        디브레인이 이미 산출하는 데이터로 *추가 수집 없이* 구현.
      ]
    ],

    [
      #v(6pt)
      #image("figures/report/h22_rdd_field.png", width: 100%)
      #fig-id("FIG-3.2", note: [사업 유형별 12월 점프 — 자동 flagging의 우선순위 기준점])
    ],
  )
]

// ══════════════════════════════════════════════════════════════════════════
//                          SLIDE 25 — 제언 ③ 다년도 회계
// ══════════════════════════════════════════════════════════════════════════
#slide("Part 7 · 정책 제언", "25")[
  #title("제언 ③ 다년도 회계의 전략적 적용", sub: [공기가 긴 사업에 한해 *회계연도 독립 원칙 완화*])

  #v(10pt)

  #grid(
    columns: (1fr, 1fr),
    column-gutter: 20pt,

    [
      #text(size: 14pt, weight: "semibold")[현행 단년도 회계의 한계]
      #v(8pt)
      #text(size: 12pt, fill: mid)[
        - 자산취득형 사업은 *공정률 마감 + 회계 마감* 결합으로 *3.42배 점프* 발현
        - 12월 직전 *불필요 집행* 또는 *공정 단축* 압력 발생
        - 사업 *품질*은 측정 어려워 흔적이 결과 지표에만 늦게 남음
      ]
      #v(10pt)
      #text(size: 14pt, weight: "semibold")[다년도 회계의 효과 가설]
      #v(6pt)
      #text(size: 12pt, fill: mid)[
        *회계연도 경계*가 약해지면 12월 점프 압력 *분산*. 본 분석은 단일 정부 데이터로
        *전후 비교 불가*이나, OECD 일부 국가의 다년도 회계 도입 후 점프 약화 사례 존재 (선행 연구).
      ]
    ],

    [
      #v(8pt)
      #callout(label: "적용 우선순위 제안", color: ink, bg: chip-bg)[
        *자산취득형 우선* — 시설 공사·물품 구매 등 공기 6개월 이상 사업 \
        → *회계연도 횡단 이월* 허용 (전체 예산의 일부) \
        → 효과 측정 후 *정상사업 일부로 점진 확대*

        *인건비형·출연금형*은 다년도 회계 효과 제한적 (이미 평탄 또는 연중 분산).
      ]
      #v(12pt)
      #text(size: 11pt, fill: soft, style: "italic")[
        본 제언은 데이터에서 *직접 입증된 가설*이 아닌 *근거 기반 권고*. 시행 시 *시범 사업 평가*를
        통한 단계적 확대 권장.
      ]
    ],
  )
]

// ══════════════════════════════════════════════════════════════════════════
//                          SLIDE 26 — 한계와 향후 과제
// ══════════════════════════════════════════════════════════════════════════
#slide("Part 7 · 정책 제언", "26")[
  #title("한계와 향후 과제", sub: [본 분석이 *답하지 못한 것*과 *후속 데이터 확보 시* 가능한 과제])

  #v(10pt)

  #grid(
    columns: (1fr, 1fr),
    column-gutter: 18pt,

    [
      #chip("본 분석의 한계", fg: warn, bg: rgb("#fef3c7"))
      #v(10pt)
      #text(size: 11.5pt, fill: mid)[
        - *통제군 부재* — 한국 단일 정부, 다년도 회계 전후 비교 불가
        - *결과 지표 잡음* — 사회 지표는 재정 외 요인 다수
        - *자료 시간 단위* — 월 단위 공개로 12월 첫 주 신호 분산
        - *모기관-출연기관 거버넌스 데이터* 부재 — 일률 정산 원인 식별 불가
        - *상관 기반 매개* — 인과까지는 단일 데이터로 도달 못 함
      ]
    ],

    [
      #chip("향후 과제 — 데이터 확보 시", fg: accent, bg: accent-bg)
      #v(10pt)
      #text(size: 11.5pt, fill: mid)[
        - *주별·일별 집행 공개* 확대 → RDD 정밀도 향상
        - *공공기관 경영평가 등급* 기계 가독 공개 → 미시 outcome 확보
        - *위탁 계약·이사회 데이터 결합* → 연성 예산 제약 직접 검증
        - *분야별 결과 지표 시계열 확장* (>10년) → 매개 검정력 확보
        - *정책 자연 실험* 결합 → 인과 추정 가능
      ]
    ],
  )

  #v(14pt)

  #callout(label: "객관성 원칙", color: ink, bg: chip-bg)[
    본 분석은 *데이터가 가리키는 것*과 *데이터가 가리키지 못하는 것*을 분명히 구분한다.
    한계는 *분석의 약점*이 아니라 *후속 연구·정책 데이터 인프라*의 구체적 우선순위다.
  ]
]

// ══════════════════════════════════════════════════════════════════════════
//                          SLIDE 27 — 결론 · Q&A
// ══════════════════════════════════════════════════════════════════════════
#slide("Closing", "27")[
  #title("결론 — 측정을 위한 측정을 넘어", sub: [데이터 기반 *스마트 재정 운영*으로 가는 길])

  #v(14pt)

  #grid(
    columns: (28pt, 1fr),
    row-gutter: 14pt, column-gutter: 12pt,

    text(font: mono, size: 14pt, fill: accent, weight: "semibold")[1],
    [
      #text(size: 16pt, weight: "semibold")[
        *세 풍경은 데이터에 흔적이 남는다* — 우연이 아닌 *지출 구조에 의한 구조적 패턴*.
      ]
    ],

    text(font: mono, size: 14pt, fill: accent, weight: "semibold")[2],
    [
      #text(size: 16pt, weight: "semibold")[
        *사업 형태가 진짜 단위* — 일률 잣대 대신 *체질별 차등 평가*가 출발점.
      ]
    ],

    text(font: mono, size: 14pt, fill: accent, weight: "semibold")[3],
    [
      #text(size: 16pt, weight: "semibold")[
        *분석 결과는 운영 시스템에 직접 환원 가능* — 디브레인 자동 flagging·4분면 우선순위.
      ]
    ],
  )

  #v(20pt)

  #line(length: 100%, stroke: 0.6pt + ink)
  #v(14pt)

  #grid(
    columns: (1fr, 1fr),
    column-gutter: 20pt,
    [
      #text(font: mono, size: 11pt, fill: accent, weight: "medium", tracking: 0.4pt)[
        #upper[Q & A · 감사합니다]
      ]
      #v(8pt)
      #text(size: 14pt, fill: mid)[
        분석보고서·재현 코드·데이터 출처는 별도 자료 참조.
      ]
    ],
    align(right + top)[
      #text(font: mono, size: 11pt, fill: mid, tracking: 0.4pt)[
        #upper[#meta.org]
      ]
      #v(4pt)
      #text(size: 13pt, weight: "semibold")[
        #meta.authors.join(" · ")
      ]
    ],
  )
]
