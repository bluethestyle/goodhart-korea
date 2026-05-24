// ══════════════════════════════════════════════════════════════════════════
//  재정데이터 분석 보고서 · Swiss Minimal v3 (print-scaled)
//  Pied Piper · 재정데이터 분석팀
//
//  레퍼런스: Linear, Vercel, Stripe Docs
//  구성: 표지 · Colophon · Executive Summary · 목차 · 본문 5섹션
//        · Appendix A/B · Glossary · References
//
//  컴파일: typst compile templates/02_swiss_minimal_v2.typ
// ══════════════════════════════════════════════════════════════════════════

// ── 폰트 ────────────────────────────────────────────────────────────────
#let sans = ("Pretendard", "Inter", "Helvetica Neue")
#let mono = ("JetBrains Mono", "IBM Plex Mono", "Menlo")

// ── 컬러 팔레트 ─────────────────────────────────────────────────────────
#let ink       = rgb("#0a0a0a")
#let paper     = rgb("#ffffff")
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

// ── 보고서 메타 ─────────────────────────────────────────────────────────
#let meta = (
  code: "FA-REPORT/2026-Q1",
  version: "v1.0",
  date: "2026.05.18",
  org: "Pied Piper",
  team: "재정데이터 분석팀",
  authors: ("김도현", "이서영", "박지훈"),
  period: "2024.Q1 — 2026.Q1",
  sample: "21,438",
  sources: ("KOSIS", "BOK", "KOSTAT"),
)

// ══════════════════════════════════════════════════════════════════════════
//  전역 텍스트 / 단락 설정 (인쇄 기준 스케일)
// ══════════════════════════════════════════════════════════════════════════
#set text(font: sans, size: 10.5pt, lang: "ko", fill: ink, weight: "regular")
#set par(justify: false, leading: 0.78em, spacing: 1.1em)

// 인라인 코드 — 모노스페이스 칩
#show raw.where(block: false): it => box(
  inset: (x: 5pt, y: 1.5pt),
  outset: (y: 2pt),
  fill: chip-bg,
  radius: 3pt,
  text(font: mono, size: 9.5pt, fill: ink, it.text),
)

// 강조어
#show strong: it => text(weight: "semibold", fill: ink, it)
#show emph: it => text(style: "italic", fill: mid, it)

// ── 페이지 헤더/푸터 (공통 본문용) ──────────────────────────────────────
#let body-header() = context {
  let p = counter(page).get().first()
  if p > 1 {
    grid(
      columns: (1fr, 1fr, 1fr),
      text(font: mono, size: 9.5pt, fill: soft, meta.code),
      align(center, text(font: sans, size: 9.5pt, fill: mid, weight: "medium")[
        재정데이터 분석 보고서
      ]),
      align(right, text(font: mono, size: 9.5pt, fill: soft)[
        #counter(page).display() / #context counter(page).final().first()
      ]),
    )
    v(4pt)
    line(length: 100%, stroke: 0.4pt + line-c)
  }
}

#let body-footer() = context {
  line(length: 100%, stroke: 0.4pt + line-c)
  v(6pt)
  grid(
    columns: (1fr, 1fr),
    text(font: sans, size: 9pt, fill: soft, weight: "medium")[
      #meta.org #h(6pt) · #h(6pt) #meta.team
    ],
    align(right, text(font: mono, size: 9pt, fill: soft)[
      #meta.code #h(6pt) · #h(6pt) #meta.version
    ]),
  )
}

#set page(
  paper: "a4",
  margin: (x: 26mm, top: 28mm, bottom: 28mm),
  fill: paper,
  header: body-header(),
  footer: body-footer(),
)

// ══════════════════════════════════════════════════════════════════════════
//  헤딩 시스템
// ══════════════════════════════════════════════════════════════════════════
#show heading.where(level: 1): it => {
  pagebreak(weak: true)
  v(28pt)
  block[
    #text(font: mono, size: 10pt, fill: accent, weight: "medium", tracking: 0.6pt)[
      ※ SECTION #counter(heading).display("01")
    ]
    #v(18pt)
    #text(font: sans, size: 38pt, weight: "semibold", tracking: -1pt, fill: ink)[
      #it.body
    ]
  ]
  v(10pt)
  line(length: 100%, stroke: 0.6pt + ink)
  v(30pt)
}

#show heading.where(level: 2): it => {
  v(32pt, weak: true)
  block[
    #text(font: mono, size: 9.5pt, fill: soft, tracking: 0.4pt)[
      #counter(heading).display("01.01")
    ]
    #v(6pt)
    #text(font: sans, size: 22pt, weight: "semibold", tracking: -0.5pt, fill: ink)[
      #it.body
    ]
  ]
  v(14pt, weak: true)
}

#show heading.where(level: 3): it => {
  v(20pt, weak: true)
  text(font: sans, size: 13pt, weight: "semibold", fill: ink)[#it.body]
  v(6pt, weak: true)
}

#show heading.where(level: 4): it => {
  v(12pt, weak: true)
  text(font: mono, size: 10pt, fill: accent, weight: "medium", tracking: 0.4pt)[
    #upper(it.body)
  ]
  v(4pt, weak: true)
}

// ══════════════════════════════════════════════════════════════════════════
//  컴포넌트
// ══════════════════════════════════════════════════════════════════════════

// ── 칩 (인라인 태그) ────────────────────────────────────────────────────
#let chip(label, fg: ink, bg: chip-bg) = box(
  inset: (x: 8pt, y: 3pt),
  outset: (y: 2pt),
  fill: bg,
  radius: 4pt,
  text(font: mono, size: 9pt, weight: "medium", fill: fg, tracking: 0.2pt)[
    #upper(label)
  ],
)

// ── KPI 카드 (상단 라인 강조) ───────────────────────────────────────────
#let kpi(label, value, delta: none, unit: "", sub: none) = block(
  width: 100%,
  inset: (top: 20pt, bottom: 20pt, x: 0pt),
  stroke: (top: 1.2pt + ink),
)[
  #text(font: mono, size: 9.5pt, fill: mid, tracking: 0.4pt)[#upper(label)]
  #v(16pt)
  #text(font: sans, size: 38pt, weight: "semibold", tracking: -1.2pt, fill: ink)[
    #value
    #if unit != "" {
      text(size: 17pt, weight: "regular", fill: mid)[ #unit]
    }
  ]
  #if delta != none {
    v(14pt)
    let is-pos = delta.starts-with("+")
    text(font: mono, size: 10.5pt, fill: if is-pos { pos } else { neg }, weight: "medium")[
      #if is-pos [↑] else [↓] #h(3pt) #delta
    ]
    if sub != none {
      text(font: mono, size: 9.5pt, fill: soft)[ #sub]
    }
  }
]

// ── 차트 자리 placeholder ───────────────────────────────────────────────
//  나중에 #image("path.png") 로 교체하세요
#let chart-slot(
  id: "FIG-XX",
  title: "",
  note: "",
  height: 90mm,
) = block(
  width: 100%,
  height: height,
  fill: ghost,
  stroke: (paint: line-d, thickness: 0.6pt, dash: "dashed"),
  inset: 20pt,
)[
  #place(top + left)[
    #text(font: mono, size: 10pt, fill: accent, tracking: 0.4pt, weight: "medium")[
      #upper(id)
    ]
  ]
  #set align(center + horizon)
  #stack(
    dir: ttb,
    spacing: 10pt,
    text(font: mono, size: 11pt, fill: mid, weight: "medium")[[ #title ]],
    if note != "" {
      text(font: sans, size: 10pt, fill: soft, note)
    },
  )
]

// ── 캡션 ────────────────────────────────────────────────────────────────
#let caption(id, body) = block(
  inset: (top: 10pt),
  text(font: mono, size: 9pt, fill: soft, tracking: 0.3pt)[
    #upper(id) #h(10pt) · #h(10pt)
    #text(font: sans, size: 9.5pt, fill: mid, weight: "regular", body)
  ],
)

// ── 콜아웃 박스 ─────────────────────────────────────────────────────────
#let callout(label: "NOTE", body, color: accent, bg: accent-bg) = block(
  width: 100%,
  fill: bg,
  inset: 20pt,
  radius: 5pt,
)[
  #text(font: mono, size: 9.5pt, fill: color, weight: "semibold", tracking: 0.4pt)[
    #upper(label)
  ]
  #v(10pt)
  #text(size: 10.5pt, fill: ink, body)
]

// ── 미니 막대 (인라인) ──────────────────────────────────────────────────
#let bar(value, max: 100, color: ink, width: 50mm) = box(
  width: width, height: 8pt, fill: chip-bg,
)[
  #place(left + horizon, box(
    width: calc.min(value / max, 1.0) * width,
    height: 8pt,
    fill: color,
  ))
]

// ── 표 기본 스타일 ──────────────────────────────────────────────────────
#show table.cell.where(y: 0): set text(
  font: mono, size: 9pt, weight: "semibold", tracking: 0.4pt, fill: mid,
)
#show table.cell.where(y: 0): it => upper(it)
#set table(
  stroke: (x, y) => (
    bottom: if y == 0 { 1pt + ink } else { 0.4pt + line-c },
  ),
  inset: (x: 0pt, y: 12pt),
  align: (col, row) => if col == 0 { left } else { right },
)

// ── 각주 ────────────────────────────────────────────────────────────────
#show footnote.entry: it => {
  set text(font: sans, size: 9.5pt, fill: mid)
  block(inset: (left: 0pt), it)
}
#set footnote.entry(
  separator: line(length: 30%, stroke: 0.5pt + line-c),
  gap: 0.7em,
)
#show footnote: it => text(font: mono, fill: accent, weight: "medium", size: 0.85em, it)

// ── 용어집 엔트리 ───────────────────────────────────────────────────────
#let term(name, en: none, body) = block(
  width: 100%,
  inset: (top: 14pt, bottom: 14pt),
  stroke: (top: 0.4pt + line-c),
)[
  #grid(
    columns: (130pt, 1fr),
    column-gutter: 20pt,
    [
      #text(font: sans, size: 13pt, weight: "semibold", fill: ink, name)
      #if en != none {
        v(4pt)
        text(font: mono, size: 9pt, fill: soft, tracking: 0.2pt, en)
      }
    ],
    text(size: 10.5pt, fill: mid, body),
  )
]

// ══════════════════════════════════════════════════════════════════════════
//                                  표지
// ══════════════════════════════════════════════════════════════════════════
#page(
  margin: (x: 26mm, y: 26mm),
  header: none,
  footer: none,
)[
  #set text(font: sans, fill: ink)

  // 상단 메타 바
  #grid(
    columns: (1fr, 1fr),
    text(font: mono, size: 10pt, fill: ink, meta.code),
    align(right, text(font: mono, size: 10pt, fill: ink)[
      #meta.version  ·  #meta.date
    ]),
  )

  #v(120pt)

  // 시리즈 라벨 (영문 메타)
  #text(font: mono, size: 11pt, fill: accent, tracking: 1pt)[
    #upper[Quarterly Financial Analysis]
  ]
  #v(24pt)

  // 한글 메인 타이틀
  #text(font: sans, size: 64pt, weight: "semibold", tracking: -2pt, fill: ink)[
    가계 재정\
    분기 분석\
    보고서
  ]
  #v(24pt)
  #text(font: sans, size: 22pt, weight: "regular", fill: mid, tracking: -0.4pt)[
    2026년 1분기 · 한국 가계의 부채 · 자산 · 소비 데이터 분석
  ]

  #v(1fr)

  // 하단 메타 — 4컬럼 그리드
  #line(length: 100%, stroke: 1pt + ink)
  #v(20pt)
  #grid(
    columns: (1fr, 1fr, 1fr, 1fr),
    column-gutter: 20pt,
    [
      #text(font: mono, size: 9.5pt, fill: mid, tracking: 0.4pt)[#upper[Authors]]
      #v(12pt)
      #for a in meta.authors [
        #text(size: 11.5pt, weight: "medium")[#a] \
      ]
    ],
    [
      #text(font: mono, size: 9.5pt, fill: mid, tracking: 0.4pt)[#upper[Period]]
      #v(12pt)
      #text(font: mono, size: 11.5pt, meta.period)
    ],
    [
      #text(font: mono, size: 9.5pt, fill: mid, tracking: 0.4pt)[#upper[Sources]]
      #v(12pt)
      #text(font: mono, size: 10.5pt, meta.sources.join(" · "))
    ],
    [
      #text(font: mono, size: 9.5pt, fill: mid, tracking: 0.4pt)[#upper[Sample]]
      #v(12pt)
      #text(font: mono, size: 11.5pt)[n = #meta.sample]
    ],
  )

  #v(20pt)

  // 발행 주체
  #grid(
    columns: (1fr, 1fr),
    [
      #text(font: mono, size: 9.5pt, fill: mid, tracking: 0.4pt)[#upper[Published by]]
      #v(8pt)
      #text(size: 13pt, weight: "semibold")[#meta.org]
      #text(size: 13pt, fill: mid)[  ·  #meta.team]
    ],
    align(right + bottom, [
      #box(width: 14pt, height: 14pt, fill: accent)
      #h(8pt)
      #text(size: 13pt, weight: "semibold", meta.org)
    ]),
  )
]

// ══════════════════════════════════════════════════════════════════════════
//                              Colophon (표지 뒷면)
// ══════════════════════════════════════════════════════════════════════════
#page(header: none, footer: none)[
  #set text(font: sans, fill: ink)
  #set par(leading: 0.65em)

  #v(40pt)
  #text(font: mono, size: 11pt, fill: accent, tracking: 0.6pt)[
    #upper[Colophon · 발행 정보]
  ]
  #v(20pt)
  #line(length: 100%, stroke: 0.6pt + ink)
  #v(20pt)

  #grid(
    columns: (130pt, 1fr),
    row-gutter: 18pt,
    column-gutter: 22pt,

    text(font: mono, size: 10pt, fill: mid, tracking: 0.4pt)[#upper[Document]],
    [
      재정데이터 분석 보고서 · 2026년 1분기 \
      #text(font: mono, size: 10pt, fill: mid)[#meta.code  ·  #meta.version]
    ],

    text(font: mono, size: 10pt, fill: mid, tracking: 0.4pt)[#upper[Issued]],
    text(font: mono, size: 11pt)[#meta.date],

    text(font: mono, size: 10pt, fill: mid, tracking: 0.4pt)[#upper[Publisher]],
    [
      #meta.org \
      #text(fill: mid)[#meta.team]
    ],

    text(font: mono, size: 10pt, fill: mid, tracking: 0.4pt)[#upper[Authors]],
    [
      #for (i, a) in meta.authors.enumerate() [
        #text(weight: "medium")[#a]#if i < meta.authors.len() - 1 [, ]
      ]
    ],

    text(font: mono, size: 10pt, fill: mid, tracking: 0.4pt)[#upper[Reviewers]],
    [한지수 (수석연구원), 최민호 (정책분석실장)],

    text(font: mono, size: 10pt, fill: mid, tracking: 0.4pt)[#upper[Period]],
    text(font: mono, size: 11pt, meta.period),

    text(font: mono, size: 10pt, fill: mid, tracking: 0.4pt)[#upper[Sample]],
    text(font: mono, size: 11pt)[n = #meta.sample  ·  가구 단위  ·  가중치 적용],

    text(font: mono, size: 10pt, fill: mid, tracking: 0.4pt)[#upper[Sources]],
    [
      KOSIS 가계금융복지조사 (2025) \
      한국은행 ECOS 분기 통계 \
      통계청 가계동향조사 (2024–2026)
    ],

    text(font: mono, size: 10pt, fill: mid, tracking: 0.4pt)[#upper[Tooling]],
    text(font: mono, size: 10.5pt)[
      pandas 2.2.0  ·  statsmodels 0.14  ·  Typst 0.13
    ],

    text(font: mono, size: 10pt, fill: mid, tracking: 0.4pt)[#upper[Typography]],
    text(font: mono, size: 10.5pt)[Pretendard  ·  JetBrains Mono],

    text(font: mono, size: 10pt, fill: mid, tracking: 0.4pt)[#upper[License]],
    [내부 자료 · 대외비 (Confidential, Internal Use Only)],
  )

  #v(40pt)
  #line(length: 100%, stroke: 0.6pt + ink)
  #v(20pt)

  #callout(label: "버전 이력", color: ink, bg: chip-bg)[
    #set text(font: mono, size: 10pt)
    #table(
      columns: (auto, auto, 1fr, 1fr),
      stroke: none,
      inset: (x: 0pt, y: 4pt),
      [v1.0], [2026.05.18], [최초 발행],     [김도현],
      [v0.9], [2026.05.10], [내부 검토 반영], [이서영],
      [v0.5], [2026.04.28], [초안],          [박지훈],
    )
  ]

  #v(1fr)

  // 페이지 하단 — 작은 풋
  #line(length: 100%, stroke: 0.4pt + line-c)
  #v(8pt)
  #grid(
    columns: (1fr, 1fr),
    text(font: mono, size: 9pt, fill: soft)[© 2026 #meta.org],
    align(right, text(font: mono, size: 9pt, fill: soft)[
      이 문서는 #meta.org 사내 분석 표준 v3을 따릅니다.
    ]),
  )
]

// ══════════════════════════════════════════════════════════════════════════
//                            Executive Summary
// ══════════════════════════════════════════════════════════════════════════
#page[
  #v(20pt)
  #text(font: mono, size: 11pt, fill: accent, tracking: 0.6pt, weight: "medium")[
    #upper[Executive Summary]
  ]
  #v(12pt)
  #text(font: sans, size: 34pt, weight: "semibold", tracking: -0.8pt, fill: ink)[
    한 페이지로 보는 결론
  ]
  #v(6pt)
  #line(length: 100%, stroke: 0.6pt + ink)
  #v(24pt)

  // 핵심 명제 3개 — 큰 활자
  #grid(
    columns: (30pt, 1fr),
    row-gutter: 26pt,
    column-gutter: 10pt,

    text(font: mono, size: 14pt, fill: accent, weight: "semibold")[01],
    [
      #text(size: 18pt, weight: "semibold", tracking: -0.3pt)[
        가계부채는 *양 극단에서 동시에* 증가했다.
      ]
      #v(6pt)
      #text(size: 11pt, fill: mid)[
        하위 20% (Q1)는 +20.4%, 상위 20% (Q5)는 +16.7% — 중간 분위 (Q2–Q4)는 평균 +5.2%에 그쳤다.
        성격은 다르다. Q1은 생계형 신용대출, Q5는 자산형성형 주택담보대출이 주도한다.
      ]
    ],

    text(font: mono, size: 14pt, fill: accent, weight: "semibold")[02],
    [
      #text(size: 18pt, weight: "semibold", tracking: -0.3pt)[
        소비 회복은 *Q5에서만* 코로나 이전 수준에 도달했다.
      ]
      #v(6pt)
      #text(size: 11pt, fill: mid)[
        선택재 지출 기준 Q5는 2019 평균 대비 +3.8%, Q1–Q3는 평균 -12.1%로 여전히 회복 미달.
        필수재 지출은 전 분위에서 인구추세선과 일치.
      ]
    ],

    text(font: mono, size: 14pt, fill: accent, weight: "semibold")[03],
    [
      #text(size: 18pt, weight: "semibold", tracking: -0.3pt)[
        자산 지니계수는 *2년 만에 0.024 상승*했다.
      ]
      #v(6pt)
      #text(size: 11pt, fill: mid)[
        2024.Q1 → 2026.Q1 동안 자산 지니계수는 0.588 → 0.612로 상승.
        주택자산 보유율 격차가 주된 동인이며, 금융자산은 상대적으로 안정적.
      ]
    ],
  )

  #v(32pt)
  #line(length: 100%, stroke: 0.6pt + ink)
  #v(20pt)

  // KPI 4-카드
  #grid(
    columns: (1fr, 1fr, 1fr, 1fr),
    column-gutter: 14pt,
    kpi("Avg. Debt", "248", delta: "+8.2%", unit: "M₩"),
    kpi("Savings Rate", "11.4", delta: "-1.8%", unit: "%"),
    kpi("Asset Gini", "0.612", delta: "+0.024"),
    kpi("Sample", "21.4", delta: "+3.1%", unit: "K"),
  )

  #v(24pt)
  #callout(label: "policy hook")[
    가계 재정 정책은 *평균이 아닌 분포의 형태*를 표적으로 삼아야 한다.
    Q1과 Q5에서 동시에 관찰되는 부채 증가는 동일 정책 도구로 다룰 수 없는 이질적 현상이다.
    세부 권고안은 § 05 에서 다룬다.
  ]
]

// ══════════════════════════════════════════════════════════════════════════
//                                  목차
// ══════════════════════════════════════════════════════════════════════════
#page[
  #v(20pt)
  #text(font: mono, size: 11pt, fill: accent, tracking: 0.6pt, weight: "medium")[
    #upper[Contents · 목차]
  ]
  #v(12pt)
  #text(font: sans, size: 34pt, weight: "semibold", tracking: -0.8pt, fill: ink)[
    이 보고서의 구성
  ]
  #v(6pt)
  #line(length: 100%, stroke: 0.6pt + ink)
  #v(24pt)

  // 커스텀 outline 스타일
  #show outline.entry: it => {
    let lvl = it.level
    let body-style = if lvl == 1 {
      (size: 15pt, weight: "semibold", fill: ink)
    } else if lvl == 2 {
      (size: 11.5pt, weight: "regular", fill: mid)
    } else {
      (size: 9pt, weight: "regular", fill: soft)
    }
    let pad-left = (lvl - 1) * 16pt
    block(
      inset: (top: if lvl == 1 { 12pt } else { 3pt }, bottom: 0pt, left: pad-left),
      link(it.element.location(), grid(
        columns: (auto, 1fr, auto),
        column-gutter: 10pt,
        align: (left, left, right),
        if lvl == 1 {
          text(
            font: mono, size: 9.5pt, fill: accent, weight: "medium", tracking: 0.4pt,
            numbering("01", ..counter(heading).at(it.element.location())),
          )
        } else { [] },
        text(..body-style, it.element.body),
        text(font: mono, size: 10pt, fill: soft, it.page()),
      )),
    )
  }

  #outline(title: none, depth: 2, indent: 0pt)
]

// ══════════════════════════════════════════════════════════════════════════
//  본문 — 페이지 번호 시작
// ══════════════════════════════════════════════════════════════════════════
#set page(numbering: "1")
#counter(page).update(1)

// ══════════════════════════════════════════════════════════════════════════
= 개요

본 보고서는 *2024년 1분기부터 2026년 1분기까지* 한국 가계의 재정 상태 변화를 추적한다.
분석 단위는 가구이며, 모든 지표는 가구 가중치를 적용한 가중평균 또는 분위별 중앙값이다.
신뢰구간은 별도 명시가 없는 한 95% BCa 부트스트랩으로 산정하였다#footnote[
  Efron, B. (1987). Better Bootstrap Confidence Intervals. JASA, 82(397), 171–185.
].

#v(18pt)

// KPI 그리드
#grid(
  columns: (1fr, 1fr, 1fr, 1fr),
  column-gutter: 14pt,
  kpi("Avg. Debt", "248", delta: "+8.2%", unit: "M₩"),
  kpi("Savings Rate", "11.4", delta: "-1.8%", unit: "%"),
  kpi("Asset Gini", "0.612", delta: "+0.024"),
  kpi("Sample", "21.4", delta: "+3.1%", unit: "K"),
)

#v(24pt)

== 보고서의 위치

#chip("Series", fg: accent, bg: accent-bg) #h(4pt) #chip("Quarterly")
#h(4pt) #chip("Internal")

본 문서는 #meta.org #(meta.team)이 분기 단위로 발행하는 *재정데이터 분석 시리즈*의
네 번째 리포트이다. 동일 시리즈의 이전 보고서들과의 핵심 차이는 두 가지이다.

- *표본 확장*. 2026.Q1부터 통계청 가계금융복지조사 미시 데이터를 직접 사용한다 (이전: 집계표).
- *가중치 재산정*. 2025년 인구주택총조사 결과를 반영해 전 기간 가중치를 재산정하였다.

== 분석 범위

분석 대상은 #strong[가구 단위 재정 상태]이며, 다음 세 축에서 추적한다.

#v(6pt)
#grid(
  columns: (1fr, 1fr, 1fr),
  column-gutter: 14pt,
  [
    #chip("01", fg: accent, bg: accent-bg)
    #v(6pt)
    #text(size: 13pt, weight: "semibold")[부채]
    #v(2pt)
    #text(size: 10pt, fill: mid)[
      신용대출 · 주택담보대출 · 기타 부채를 분위·연령·지역별로 추적한다.
    ]
  ],
  [
    #chip("02", fg: accent, bg: accent-bg)
    #v(6pt)
    #text(size: 13pt, weight: "semibold")[자산]
    #v(2pt)
    #text(size: 10pt, fill: mid)[
      금융자산과 실물(주택)자산을 분리해 측정하고, 분위 간 격차를 정량화한다.
    ]
  ],
  [
    #chip("03", fg: accent, bg: accent-bg)
    #v(6pt)
    #text(size: 13pt, weight: "semibold")[소비]
    #v(2pt)
    #text(size: 10pt, fill: mid)[
      필수재 · 선택재 · 서비스로 구분해 카테고리별 회복 양상을 본다.
    ]
  ],
)

== 핵심 용어

이 보고서에서 자주 등장하는 용어의 정의는 §부록 C의 용어집에 정리되어 있다.
본문에서 처음 등장할 때마다 #chip("term") 표시로 표시한다.

= 데이터를 그냥 보면 보이는 것

#chip("EDA", fg: accent, bg: accent-bg) #h(4pt) #chip("관찰") #h(4pt) #chip("raw plot only")

이 챕터에는 이론도 모형도 없다. 가공 없이 그대로 그렸을 때 데이터가 무엇을 말하는지 본다.
*"어 진짜 그렇네?"* 하는 직관을 먼저 만든 다음, 다음 세 챕터에서 그 직관을 정량으로 좁힌다.

#v(14pt)

#callout(label: "이 챕터의 약속")[
  - 모든 그림은 *원자료를 그대로 그린 것*이며, 모형 추정·평활·필터링이 없다.
  - 학술 용어와 분석 도구 이름은 한 개도 등장하지 않는다 — §6에서 일괄 매칭한다.
  - 챕터 끝에서 §3·§4·§5로 이어지는 *세 가지 의문*만 남긴다. 답은 아직 하지 않는다.
]

== 우리가 본 데이터

분석 대상은 한국 중앙정부의 *11년치 월별 집행 자료*다. 2015년 1월부터 2025년 12월까지
132개월, 1,557개 세부 활동, 14개 분야가 한 테이블 위에 패널 형태로 정리되어 있다.
외부 결과 지표 — 농가소득·교통사고·온실가스·고용 — 는 KOSIS·한국은행·공공데이터포털·온실가스종합정보센터에서
같은 기간 시점으로 결합했다.

#v(14pt)

#table(
  columns: (1.5fr, 1fr, 1fr, 1fr),
  table.header[데이터][기간][단위][출처],
  [월별 집행 (재정)],       [2015 — 2025], [활동 × 월], [열린재정 / KODAS],
  [편성목 구성 (재정)],     [2015 — 2025], [활동 × 년], [열린재정 / KODAS],
  [14분야 결과지표],        [2015 — 2025], [분야 × 년], [KOSIS · ECOS · 공공데이터],
  [소비자물가 (외생통제)],  [2015 — 2025], [전국 × 월], [한국은행 ECOS],
  [온실가스 인벤토리],      [2015 — 2023], [전국 × 년], [GIR],
  [도로교통 통계],          [2015 — 2025], [전국 × 년], [도로교통공단],
)
#caption("TBL-2.1")[
  분석 패널의 원천 데이터 한눈에. 모든 자료는 공공 API·공개 다운로드 기반, 비영리·연구 활용 허용 범위 내.
  결합 후 분석용 패널은 *활동 1,557개 × 132개월 ≈ 21만 셀*.
]

#v(14pt)

본 챕터에서 다룰 모든 그림은 이 패널에서 *집계만* 거친 것이다.
회귀 추정·시계열 분해·군집 분류는 §3 이후에 등장한다.

== 발견 ① — 12월의 그 막대

이 패널에서 가장 먼저 눈에 들어오는 것은 *매년 12월에 반복되는 막대*다.
전체 활동의 월별 집행 합계를 11년 시계열로 그리면, 매년 12월 자리에서
다른 11개월과 분명히 다른 높이의 막대가 나타난다.

#v(12pt)

#chart-slot(
  id: "FIG-2.2",
  title: "전체 월별 집행 합계 (2015 — 2025, 1,557 활동)",
  note: "원자료 단순 합산, 평활/조정 없음",
  height: 80mm,
)
#caption("FIG-2.2")[
  세로축: 월별 집행 합계 (조원). 가로축: 2015.01 — 2025.12. 매년 12월 위치에서 다른 11개월과
  구별되는 높이의 막대가 *예외 없이* 반복된다.
]

#v(14pt)

같은 자료를 다른 각도로 본다. 12개월을 가로축에 두고 11년치를 *세로로 겹쳐* 그리면
12월 칸의 분포가 명확히 위로 떠 있다.

#v(12pt)

#chart-slot(
  id: "FIG-2.3",
  title: "월별 일평균 집행 분포 (12개월 × 11년)",
  note: "11월과 12월의 차이가 가장 두드러진다",
  height: 75mm,
)
#caption("FIG-2.3")[
  세로축: 일평균 집행 (월합계 ÷ 일수). 가로축: 1월~12월. 박스: 11년치의 25~75 분위.
  중앙값 기준으로 12월은 11월의 약 *1.9배*.
]

#v(14pt)

#grid(
  columns: (1fr, 1.4fr),
  column-gutter: 22pt,
  [
    #text(font: mono, size: 10pt, fill: mid, tracking: 0.4pt)[#upper[11월 → 12월]]
    #v(8pt)
    #text(font: sans, size: 42pt, weight: "semibold", tracking: -1.2pt)[× 1.9]
    #v(6pt)
    #text(font: mono, size: 9.5pt, fill: soft)[전체 활동 일평균, 11년 평균]
    #v(20pt)
    #text(font: mono, size: 10pt, fill: mid, tracking: 0.4pt)[#upper[연 평균월 → 12월]]
    #v(8pt)
    #text(font: sans, size: 42pt, weight: "semibold", tracking: -1.2pt)[× 1.6]
    #v(6pt)
    #text(font: mono, size: 9.5pt, fill: soft)[연 평균 대비 12월 단월 비]
  ],
  [
    #text(size: 11.5pt, fill: mid)[
      11월 마지막 주와 12월 첫 주는 캘린더상 인접한 *7일*이다.
      그런데 이 7일을 경계로 일평균 집행이 약 2배 점프한다.
      이 점프가 우연이 아니라는 것은 연도를 바꿔 봐도 *예외 없이 반복*된다는 데서 알 수 있다.

      이 점프는 *얼마나 큰가, 모든 분야·모든 사업에서 같은가, 어떤 사업에서 더 뾰족한가* —
      이 세 질문은 EDA만으로는 답할 수 없다.
    ]
    #v(10pt)
    #text(font: mono, size: 10pt, fill: accent, tracking: 0.4pt, weight: "medium")[#upper[§3에서 본격 정량화]]
    - 분야별·사업 종류별 점프 크기 비교
    - 회계연도 경계(12.31)에서의 단절 측정
    - 정상 운영분과 경계 압력 점프의 분리
  ],
)

== 발견 ② — 평소엔 잠잠하다, 한 번에 큰 돈

같은 패널에서 *활동별 시계열*을 하나씩 들여다보면 두 종류의 사업이 분명히 다른 모양을 그린다.
한 종류는 매월 비슷한 규모로 일정하게 집행된다 (인건비·일반 운영).
다른 한 종류는 *평소에는 거의 0에 가깝다가 분기말 정산 시점에 한 번 크게 집행*된다.

#v(12pt)

#chart-slot(
  id: "FIG-2.4",
  title: "두 종류의 사업 — 월별 패턴 비교 (대표 4건)",
  note: "위: 일반 운영형 2건  ·  아래: 일률 정산형 2건",
  height: 92mm,
)
#caption("FIG-2.4")[
  같은 11년 기간을 같은 가로축에 두고 4개 활동의 월별 집행을 겹쳐 그렸다.
  위 두 곡선은 매월 비슷한 진폭을 유지하고, 아래 두 곡선은 *평소엔 0, 특정 시점에 급격한 막대* 패턴을 보인다.
]

#v(14pt)

후자의 패턴은 *어떤 분야에 많은가*? 분야별 본예산 중 출연금 비중을 단순 집계하면
분야 간 격차가 매우 크다.

#v(8pt)

#table(
  columns: (1.8fr, 1fr, 1fr, 1fr),
  table.header[분야][본예산 (조원)][출연금 (조원)][출연금 비중],
  [과학기술],              [10.4],  [3.8], text(fill: warn, weight: "semibold")[36.2%],
  [통신],                  [2.1],   [0.7], text(fill: warn, weight: "semibold")[33.4%],
  [산업·중소기업·에너지],  [11.2],  [1.6], [14.5%],
  [환경],                  [13.8],  [1.2], [8.4%],
  [농림수산],              [25.6],  [1.4], [5.6%],
  [교통및물류],            [27.4],  [0.5], [1.8%],
  [사회복지],              [109.3], [0.4], text(fill: soft)[0.4%],
  [국방],                  [59.2],  [0.1], text(fill: soft)[0.2%],
)
#caption("TBL-2.2")[
  2026년 본예산 기준, 분야별 출연금 비중 (전체 14분야 중 일부 비교 표시).
  과학기술·통신은 전체의 1/3 이상이 출연금 항목으로 배정되어, 일률 정산 패턴이 raw 시계열에 직접 드러난다.
]

#v(14pt)

#callout(label: "raw에서 보이는 단서")[
  분야별 출연금 비중 격차는 단순 집계만으로도 *80배 이상*이다 (국방 0.2% vs 과학기술 36.2%).
  발견 ②의 일률 정산 패턴은 이 격차와 *raw 단계에서부터* 연결된다 —
  같은 12월 점프(발견 ①)도 분야에 따라 모양이 다른 이유가 여기서 시작된다.
]

#v(14pt)

#text(font: mono, size: 10pt, fill: accent, tracking: 0.4pt, weight: "medium")[#upper[§5에서 본격 정량화]]

- 일률 정산 패턴이 *시간에 따라 강화되고 있는가, 안정적인가*
- 분기/반기/연 단위 중 어느 주기가 더 강한가
- 출연금 비중 자체와 12월 점프(발견 ①)는 어떻게 연결되는가

== 발견 ③ — 집행률은 늘 100% 가까이, 그런데 결과지표는?

세 번째로 눈에 띄는 모양은 *집행률 분포의 압축*과 *결과지표 분포의 확산*의 대비다.
부처별 집행률을 11년치 모아 분포로 그리면 거의 모든 부처가 좁은 구간(95~100%)에 묶여 있다.
같은 부처들이 책임지는 사회 결과 지표 — 농가소득, 교통사고 감소, 온실가스 등 — 는
같은 기간 동안 *훨씬 넓게* 흩어진다.

#v(12pt)

#chart-slot(
  id: "FIG-2.5",
  title: "부처별 집행률 분포 (좌) vs 결과지표 변화율 분포 (우)",
  note: "같은 부처들의 두 변수 — 한쪽은 천장에 압축, 한쪽은 분산",
  height: 78mm,
)
#caption("FIG-2.5")[
  좌: 14분야 ↔ 51개 부처의 집행률 분포 (2015 — 2025). 우: 같은 부처들의 분야별 결과지표 11년 변화율 분포.
  스케일은 동일 폭으로 표시.
]

#v(14pt)

#grid(
  columns: (1fr, 1.4fr),
  column-gutter: 22pt,
  [
    #text(font: mono, size: 10pt, fill: mid, tracking: 0.4pt)[#upper[집행률 중앙값]]
    #v(8pt)
    #text(font: sans, size: 36pt, weight: "semibold", tracking: -1pt)[97.8 %]
    #v(4pt)
    #text(font: mono, size: 9pt, fill: soft)[부처별 · σ ≈ 2.1%p]
    #v(18pt)
    #text(font: mono, size: 10pt, fill: mid, tracking: 0.4pt)[#upper[95~100% 압축]]
    #v(8pt)
    #text(font: sans, size: 36pt, weight: "semibold", tracking: -1pt)[≈ 90 %]
    #v(4pt)
    #text(font: mono, size: 9pt, fill: soft)[전체 부처 중 천장 구간 비율]
    #v(18pt)
    #text(font: mono, size: 10pt, fill: mid, tracking: 0.4pt)[#upper[결과지표 분산]]
    #v(8pt)
    #text(font: sans, size: 36pt, weight: "semibold", tracking: -1pt)[× 8]
    #v(4pt)
    #text(font: mono, size: 9pt, fill: soft)[집행률 분포 대비 σ 폭]
  ],
  [
    #text(size: 11.5pt, fill: mid)[
      같은 11년, 같은 부처를 두고 *예산이 얼마나 쓰였는가*와
      *그 돈이 책임지는 사회 지표가 어떻게 움직였는가*를 나란히 놓으면,
      두 분포의 모양이 *체계적으로 다르다*. 한쪽은 천장에 압축, 한쪽은 분산.

      이는 두 가지 가능성을 시사한다.
    ]
    #v(8pt)
    - 집행률이 사회 지표를 결정하는 변수가 아닐 가능성
    - 측정하기 쉬운 일(예산 집행)과 측정하기 어려운 일(사회 결과)의 *행정 압력 차이*가 결과에 흔적을 남길 가능성
    #v(10pt)
    #text(font: mono, size: 10pt, fill: accent, tracking: 0.4pt, weight: "medium")[#upper[§4에서 본격 정량화]]
    - 예산을 다 쓴 것 ≠ 사회 지표 개선이라면, 둘 사이의 격차는 무엇이 결정하는가
    - *부처 따라*인가 *사업 종류 따라*인가
    - 결과지표 변화 중 얼마만큼이 집행률로, 얼마만큼이 사업 종류 차이로 설명되는가
  ],
)

== EDA가 남긴 세 가지 의문 — §3 · §4 · §5의 입구

세 발견은 따로 보면 별개의 관찰이지만, *남은 질문을 같은 자리에 놓고 보면 하나의 구조*가
드러나기 시작한다. 각 발견은 그 자체가 답이 아니라 *다음 챕터로 가는 입구*다.

#v(14pt)

#grid(
  columns: (30pt, 1fr),
  row-gutter: 22pt,
  column-gutter: 12pt,

  text(font: mono, size: 14pt, fill: accent, weight: "semibold")[Q1],
  [
    #text(size: 15pt, weight: "semibold")[12월 점프는 모든 사업에서 같은가, 어떤 사업에서 더 큰가?]
    #v(4pt)
    #text(size: 11pt, fill: mid)[
      발견 ① → *§3*: 분야·사업 종류별 점프 크기 비교, 회계연도 경계의 단절 측정.
    ]
  ],

  text(font: mono, size: 14pt, fill: accent, weight: "semibold")[Q2],
  [
    #text(size: 15pt, weight: "semibold")[예산을 다 쓴 것 ≠ 사회를 좋게 만든 것이라면, 격차는 무엇이 결정하는가?]
    #v(4pt)
    #text(size: 11pt, fill: mid)[
      발견 ③ → *§4*: 14분야 라벨 vs 데이터가 스스로 말하는 사업 종류 — 어느 쪽이 행동을 더 잘 설명하는가.
    ]
  ],

  text(font: mono, size: 14pt, fill: accent, weight: "semibold")[Q3],
  [
    #text(size: 15pt, weight: "semibold")[일률 정산 패턴이 시간이 갈수록 강해지고 있는가?]
    #v(4pt)
    #text(size: 11pt, fill: mid)[
      발견 ② → *§5*: 출연금 비중과 정산 사이클의 시간 동학, 분기·반기·연 주기 강도 추적.
    ]
  ],
)

#v(18pt)

#callout(label: "이 챕터를 떠나며", color: ink, bg: chip-bg)[
  EDA가 보여주는 세 모양 — *12월 점프*, *일률 정산*, *집행률 압축 + 결과 분산* —
  은 서로 독립적인 우연으로 보기 어렵다. 다음 세 챕터에서 이 모양들을
  하나씩 정량화하고, §6에서 *이 세 모양에 학계가 30년째 붙여온 이름*과 매칭한다.
]

= 주요 발견

== 부채 구조의 이중화

#chart-slot(
  id: "FIG-3.1",
  title: "분위별 가계부채 변화 (2024.Q1 → 2026.Q1)",
  note: "U-형 패턴: Q1, Q5에서 동시 증가",
  height: 78mm,
)
#caption("FIG-3.1")[
  중앙값 기준, 단위 백만원. 가중치 적용 후 분위별 부채 중앙값의 시계열 비교.
]

#v(12pt)

#table(
  columns: (1.4fr, 1fr, 1fr, 1fr, 1fr, 1.5fr),
  table.header[Quintile][2024.Q1][2025.Q1][2026.Q1][Δ 2yr][Distribution],
  [Q1 (하위 20%)],  [142],  [156],  [171],  text(fill: neg, weight: "semibold")[+20.4%],   bar(20.4, max: 25, color: neg),
  [Q2],             [188],  [195],  [201],  text(fill: mid)[+6.9%],                          bar(6.9,  max: 25, color: mid),
  [Q3],             [221],  [224],  [228],  text(fill: mid)[+3.2%],                          bar(3.2,  max: 25, color: mid),
  [Q4],             [274],  [281],  [289],  text(fill: mid)[+5.5%],                          bar(5.5,  max: 25, color: mid),
  [Q5 (상위 20%)],  [318],  [342],  [371],  text(fill: neg, weight: "semibold")[+16.7%],   bar(16.7, max: 25, color: neg),
)
#caption("TBL-3.1")[소득 분위별 가계부채 (중앙값, 백만원). 분포 막대는 2024.Q1 대비 누적 증가율.]

#v(14pt)

부채의 절대 규모가 아니라 #strong[증가의 성격]이 분위 간에 다르다. Q1의 부채 증가는
주로 신용대출과 카드론에 의해 견인되었으며, 평균 대출 만기는 19개월에서 14개월로 단축되었다.
반면 Q5의 증가는 만기 20년 이상의 주택담보대출이 76%를 차지한다.

== 자산 분포의 분산 확대

#chart-slot(
  id: "FIG-3.2",
  title: "자산 지니계수 시계열 (2020–2026)",
  height: 70mm,
)
#caption("FIG-3.2")[총자산 기준 지니계수의 분기별 추이. 음영은 95% 부트스트랩 신뢰구간.]

#v(12pt)

#grid(
  columns: (1fr, 1.4fr),
  column-gutter: 18pt,
  [
    #text(font: mono, size: 10pt, fill: mid, tracking: 0.4pt)[#upper[총자산 지니]]
    #v(8pt)
    #text(font: sans, size: 36pt, weight: "semibold", tracking: -1pt)[0.612]
    #v(4pt)
    #text(font: mono, size: 9pt, fill: neg)[↑ +0.024 (2024 대비)]
    #v(20pt)
    #text(font: mono, size: 10pt, fill: mid, tracking: 0.4pt)[#upper[금융자산 지니]]
    #v(8pt)
    #text(font: sans, size: 36pt, weight: "semibold", tracking: -1pt)[0.541]
    #v(4pt)
    #text(font: mono, size: 9pt, fill: mid)[↑ +0.008]
  ],
  [
    #text(size: 11.5pt, fill: mid)[
      자산 격차 확대의 주된 동인은 #strong[주택자산]이다. 같은 기간 금융자산의 지니계수는
      유의한 변화를 보이지 않은 반면 (Δ +0.008, p = 0.21), 실물자산 (주로 주택) 의
      지니계수는 0.024 상승했다 (p < 0.001).
      \
      \
      이는 두 가지 요인의 합성으로 해석된다.
    ]
    #v(8pt)
    - 신규 주택 구매가 Q4–Q5에 집중
    - Q1–Q2의 주택 보유 비율이 24개월간 4.1%p 하락
  ],
)

== 소비 회복의 비대칭성

#chart-slot(
  id: "FIG-3.3",
  title: "분위별 소비지출 회복률 (2019 평균 = 100)",
  height: 72mm,
)
#caption("FIG-3.3")[
  카테고리별 (필수재 · 선택재 · 서비스) 분위별 회복률. Q5만 선택재에서 100을 초과.
]

#v(12pt)

#table(
  columns: (1.4fr, 1fr, 1fr, 1fr),
  table.header[Quintile][필수재][선택재][서비스],
  [Q1], [101.4], text(fill: neg)[ 84.7], text(fill: neg)[ 89.2],
  [Q2], [102.1], text(fill: neg)[ 87.3], text(fill: neg)[ 91.5],
  [Q3], [101.9], text(fill: neg)[ 91.0], text(fill: mid)[ 96.4],
  [Q4], [102.6], text(fill: mid)[ 96.8], text(fill: mid)[ 99.1],
  [Q5], [103.0], text(fill: pos)[103.8], text(fill: pos)[105.2],
)
#caption("TBL-3.3")[
  2019년 평균 = 100 기준 회복률. *빨강 = 미회복, 회색 = 회복권, 초록 = 초과회복.*
]

#v(14pt)

선택재 지출에서 #strong[Q5만 코로나 이전 수준을 초과]했다. Q1과 Q2는 여전히 13–15%p
낮은 수준이며, 이 격차는 2025년 이후 거의 좁혀지지 않고 있다.

== 부채 상환 부담의 분포

#chart-slot(
  id: "FIG-3.4",
  title: "소득 대비 원리금 상환 비율 (DSR) 분포",
  height: 70mm,
)
#caption("FIG-3.4")[
  소득 대비 원리금 상환 비율 (DSR) 의 분위별 분포. 박스플롯, n = 21,287.
]

#v(12pt)

#callout(label: "key observation")[
  Q1 가구의 #strong[18.2%]가 DSR 40% 이상에 해당하며, 이는 위험가구 기준을 초과한다.
  Q5에서는 동일 비율이 6.4%이나, 절대 부채 규모가 크므로 시스템 리스크 측면에서
  여전히 주의가 필요하다.
]

= 분위별 심층 분석

== Q1 — 하위 20% 가구

#chip("debt-driven", fg: neg, bg: rgb("#fde8e8"))
#h(4pt)
#chip("liquidity-risk", fg: warn, bg: rgb("#fef3c7"))

#chart-slot(
  id: "FIG-4.1",
  title: "Q1 가구의 부채 종류별 구성 변화",
  height: 60mm,
)
#caption("FIG-4.1")[Q1 가구 평균 부채 구성 (n = 4,289). 단위: 백만원.]

#v(12pt)

Q1 가구의 부채는 *생계 유지 목적*이 지배적이다. 평균 부채 잔액은 2년간 +20.4% 증가했으나,
같은 기간 평균 소득은 +3.2% 증가에 그쳤다. 따라서 소득 대비 부채 비율 (DTI) 은
4.7배에서 5.6배로 악화되었다.

#v(10pt)

#table(
  columns: (1.6fr, 1fr, 1fr, 1fr),
  table.header[지표][2024.Q1][2026.Q1][Δ],
  [평균 부채 (M₩)],     [142],   [171],   text(fill: neg)[+20.4%],
  [평균 소득 (M₩/년)],  [30.2],  [31.2],  text(fill: mid)[+3.2%],
  [DTI 배수],            [4.7],   [5.6],   text(fill: neg)[+0.9x],
  [DSR 40% 초과 비율],   [14.1%], [18.2%], text(fill: neg)[+4.1%p],
  [주택 보유율],         [33.2%], [29.1%], text(fill: neg)[-4.1%p],
)
#caption("TBL-4.1")[Q1 가구 핵심 지표.]

== Q2–Q3 — 중간 분위

#chip("stable", fg: pos, bg: rgb("#dcfce7"))

중간 분위 가구는 표면적으로 가장 안정적이다. 부채 증가율은 평균 +5.0%로 명목임금
상승률과 비슷하며, DSR 분포의 중앙값도 24.1% → 25.8%로 소폭 상승에 그쳤다.

#chart-slot(
  id: "FIG-4.2",
  title: "Q2–Q3 가구의 자산-부채 균형 시계열",
  height: 60mm,
)
#caption("FIG-4.2")[자산-부채의 동시 증가 — 순자산 수준은 거의 유지.]

#v(12pt)

다만 #strong[연령 효과]에 주목해야 한다. 중간 분위 내 30대 가구의 자산형성 속도는
40–50대 동일 분위 대비 절반에 그쳐, *세대 내 격차*가 누적되고 있다.

== Q4 — 상위 21–40%

#chip("expansion", fg: accent, bg: accent-bg)

Q4는 본 분기 가장 활발한 신규 주택 구매 분위였다. 분기 중 주택 구매 건수는
1,247건으로 Q5 (1,891건) 에 이어 두 번째이며, 평균 LTV는 67.2%로 가장 높다.

#table(
  columns: (1.6fr, 1fr, 1fr),
  table.header[지표][2025.Q1][2026.Q1],
  [신규 주택 구매 건수],   [891],    [1,247],
  [평균 LTV],              [62.1%],  [67.2%],
  [평균 주담대 잔액 (M₩)], [187],    [219],
  [고정금리 비율],          [41%],    [52%],
)
#caption("TBL-4.2")[Q4 가구 주택금융 지표.]

== Q5 — 상위 20%

#chip("asset-driven", fg: accent, bg: accent-bg)
#h(4pt)
#chip("watch", fg: warn, bg: rgb("#fef3c7"))

Q5의 부채 +16.7% 증가는 #strong[부정적 신호가 아니다]. 동기간 자산은 +24.1% 증가했고,
순자산은 +28.5% 늘었다. 다만 부채 규모의 절대값이 크므로 거시 안정성 모니터링 대상이다.

#chart-slot(
  id: "FIG-4.3",
  title: "Q5 가구의 자산 구성 (실물 vs 금융)",
  height: 60mm,
)
#caption("FIG-4.3")[Q5 자산은 실물 (주로 주택) 비중이 71% — 2024 대비 +3%p.]

#v(12pt)

#callout(label: "risk note", color: warn, bg: rgb("#fef3c7"))[
  Q5 부채의 86%가 변동금리 또는 혼합형이다. 금리 +100bp 충격 시 가계 가처분소득이
  평균 4.2% 감소하는 것으로 추정된다 (시뮬레이션 결과, §부록 A.4).
]

= 정책적 함의

== 분포 기반 정책 설계

본 분석의 핵심 함의는 가계 재정 정책이 #strong[평균이 아닌 분포의 형태]를 표적으로
삼아야 한다는 것이다. Q1과 Q5에서 동시에 관찰되는 부채 증가는 동일한 정책 도구로
다룰 수 없는 #emph[이질적 현상]이다.

== 권고안 (Recommendations)

#grid(
  columns: (30pt, 1fr),
  row-gutter: 22pt,
  column-gutter: 10pt,

  text(font: mono, size: 14pt, fill: accent, weight: "semibold")[R1],
  [
    #text(size: 15pt, weight: "semibold")[Q1 대상: 생계형 부채 재구조화 우선]
    #v(4pt)
    #text(size: 11pt, fill: mid)[
      단기 신용대출의 만기 연장 + 금리 부담 완화. 현금 흐름 안정화를 통해 DSR 위험가구 진입 차단.
    ]
  ],

  text(font: mono, size: 14pt, fill: accent, weight: "semibold")[R2],
  [
    #text(size: 15pt, weight: "semibold")[Q5 대상: 거시 건전성 모니터링 강화]
    #v(4pt)
    #text(size: 11pt, fill: mid)[
      변동금리 비중이 높은 Q5 주담대 포지션은 금리 충격 시 시스템 리스크의 잠재 경로.
      분기별 스트레스 테스트 수행.
    ]
  ],

  text(font: mono, size: 14pt, fill: accent, weight: "semibold")[R3],
  [
    #text(size: 15pt, weight: "semibold")[중간 분위 내 세대 격차 추적]
    #v(4pt)
    #text(size: 11pt, fill: mid)[
      Q2–Q3는 평균으로 보면 안정적이나, 30대 코호트의 자산형성 정체가 진행 중.
      별도 마이크로 분석 패널 운영 권고.
    ]
  ],
)

== 향후 과제

차기 분기 보고서에서 다룰 주제는 다음과 같다.

- *지역별 분해.* 본 보고서의 수도권 vs 비수도권 분해를 광역단위까지 확장.
- *전세 대출.* 본 분석에서 부분 포함된 전세 대출을 별도 카테고리로 분리.
- *자영업 가구.* 임금근로자와 자영업자의 부채 동학을 분리 추적.

// ══════════════════════════════════════════════════════════════════════════
//                              부록 A — 방법론 상세
// ══════════════════════════════════════════════════════════════════════════
= 부록 A · 방법론 상세

== A.1  표본 가중치 재산정

가중치 #math.equation($w_i$) 는 다음과 같이 정의된다.

$ w_i = (N_(c(i))) / (n_(c(i))) dot lambda_i $

여기서 #math.equation($c(i)$) 는 가구 #math.equation($i$) 가 속한 인구학적 셀,
#math.equation($N_c$) 는 모집단 셀 크기, #math.equation($n_c$) 는 표본 셀 크기,
그리고 #math.equation($lambda_i$) 는 무응답 조정 계수이다.

== A.2  적응형 분산 추정량

분위 #math.equation($q$) 내 분산은 다음과 같이 산정한다.

$ V_q = 1/(n_q - 1) sum_(i in q) (x_i - macron(x)_q)^2 dot tau(x_i) $

여기서 #math.equation($tau(x_i)$) 는 분포 꼬리에서의 영향을 완화하는 가중치이다
(자세한 정의는 Sato & Park, 2024 참조).

== A.3  부트스트랩 신뢰구간

BCa (Bias-Corrected and Accelerated) 부트스트랩을 적용한다. B = 10,000회 리샘플링,
편향 보정 계수 #math.equation($hat(z)_0$) 와 가속도 #math.equation($hat(a)$) 는
표준 정의를 따른다 (Efron, 1987).

== A.4  금리 충격 시뮬레이션

Q5 가구를 대상으로 한 시뮬레이션은 다음 가정 하에 수행되었다.

#table(
  columns: (1.8fr, 1fr),
  table.header[가정][값],
  [충격 크기],                [+100 bp],
  [충격 시점],                [2026.Q2 (가정)],
  [변동금리 재산정 주기],     [3 개월],
  [반영률],                   [85% (이력 평균)],
  [관찰 기간],                [충격 후 12 개월],
)
#caption("TBL-A.1")[금리 충격 시뮬레이션의 핵심 가정.]

== A.5  결측 처리

결측치는 #strong[다중대입 (multiple imputation, m = 5)]으로 처리하였다. 결측 패턴은
무작위가 아니므로 (MAR 가정 위배 가능성), 민감도 분석을 위해 단일 결측 처리 결과
(complete-case) 와 비교하였다. 주요 결론은 두 방법에서 일관되었다.

// ══════════════════════════════════════════════════════════════════════════
//                          부록 B — 데이터 표 (대형)
// ══════════════════════════════════════════════════════════════════════════
= 부록 B · 분기별 전체 데이터

이 부록은 본문에서 인용된 모든 지표의 #strong[분기별 원시 수치]를 수록한다.
출처는 §부록 D 참고문헌의 [S1]–[S3]을 결합 가공한 결과이다.

== B.1  분위별 부채 — 분기 단위 (백만원, 중앙값)

#table(
  columns: (1.2fr, 1fr, 1fr, 1fr, 1fr, 1fr, 1fr, 1fr, 1fr),
  table.header[분위][24Q1][24Q2][24Q3][24Q4][25Q1][25Q2][25Q3][25Q4],
  [Q1],  [142], [146], [149], [153], [156], [160], [164], [167],
  [Q2],  [188], [190], [192], [194], [195], [197], [198], [200],
  [Q3],  [221], [222], [223], [223], [224], [225], [226], [227],
  [Q4],  [274], [276], [278], [280], [281], [283], [285], [287],
  [Q5],  [318], [325], [331], [337], [342], [350], [358], [365],
)
#caption("TBL-B.1")[2024.Q1 – 2025.Q4 분위별 가계부채 중앙값.]

#v(10pt)

#table(
  columns: (1.2fr, 1fr, 1fr),
  table.header[분위][26Q1][Δ 2yr],
  [Q1],  [171], text(fill: neg)[+20.4%],
  [Q2],  [201], [+6.9%],
  [Q3],  [228], [+3.2%],
  [Q4],  [289], [+5.5%],
  [Q5],  [371], text(fill: neg)[+16.7%],
)
#caption("TBL-B.1 (cont.)")[2026.Q1 및 누적 변화율.]

== B.2  분위별 자산 — 분기 단위 (백만원, 평균)

#table(
  columns: (1.2fr, 1fr, 1fr, 1fr, 1fr, 1fr, 1fr, 1fr, 1fr),
  table.header[분위][24Q1][24Q2][24Q3][24Q4][25Q1][25Q2][25Q3][25Q4],
  [Q1],  [89],   [91],   [92],   [93],   [94],   [94],   [95],   [95],
  [Q2],  [187],  [190],  [193],  [195],  [197],  [200],  [202],  [205],
  [Q3],  [342],  [350],  [357],  [365],  [371],  [380],  [388],  [395],
  [Q4],  [621],  [638],  [654],  [671],  [687],  [705],  [722],  [740],
  [Q5],  [1,847], [1,891], [1,938], [1,987], [2,034], [2,089], [2,147], [2,206],
)
#caption("TBL-B.2")[분위별 가계 평균 자산 (총자산).]

== B.3  소비지출 회복률 — 카테고리별

#table(
  columns: (1.2fr, 1.1fr, 1.1fr, 1.1fr, 1.1fr, 1.1fr),
  table.header[기간][Q1][Q2][Q3][Q4][Q5],
  [2024.Q1], [82.1], [84.7], [88.2], [93.1], [98.4],
  [2024.Q2], [82.9], [85.4], [89.0], [93.8], [99.1],
  [2024.Q3], [83.4], [85.9], [89.7], [94.3], [99.9],
  [2024.Q4], [83.9], [86.4], [90.1], [94.9], [100.7],
  [2025.Q1], [84.2], [86.8], [90.4], [95.5], [101.5],
  [2025.Q2], [84.4], [87.0], [90.6], [95.9], [102.1],
  [2025.Q3], [84.5], [87.1], [90.8], [96.3], [102.7],
  [2025.Q4], [84.6], [87.2], [90.9], [96.6], [103.3],
  [2026.Q1], text(fill: neg)[84.7], text(fill: neg)[87.3], text(fill: neg)[91.0], [96.8], text(fill: pos)[103.8],
)
#caption("TBL-B.3")[
  선택재 지출 회복률 (2019 평균 = 100). *빨강 = 미회복.*
]

== B.4  DSR 위험가구 비율

#table(
  columns: (1.2fr, 1.1fr, 1.1fr, 1.1fr, 1.1fr, 1.1fr),
  table.header[기간][Q1][Q2][Q3][Q4][Q5],
  [2024.Q1], [14.1%], [9.8%], [7.4%], [6.1%], [5.9%],
  [2025.Q1], [16.2%], [10.4%], [7.8%], [6.3%], [6.1%],
  [2026.Q1], text(fill: neg)[18.2%], [11.1%], [8.1%], [6.5%], [6.4%],
)
#caption("TBL-B.4")[DSR ≥ 40% 가구의 분위별 비율.]

// ══════════════════════════════════════════════════════════════════════════
//                              부록 C — 용어집
// ══════════════════════════════════════════════════════════════════════════
= 부록 C · 용어집

본 보고서에서 사용한 주요 용어와 그 정의를 모았다. 영문 표기는 국제 비교가
빈번한 분야의 관행을 따른다.

#v(12pt)

#term("가처분소득", en: "Disposable income")[
  세금과 사회보장기여금을 차감한 후 가구가 실제 사용할 수 있는 소득.
]

#term("지니계수", en: "Gini coefficient")[
  분포의 불평등도를 0(완전평등)–1(완전불평등) 사이의 값으로 측정. 본문 §3.2에서는
  자산 분포에, §3.1에서는 부채 분포에 적용.
]

#term("DSR", en: "Debt Service Ratio")[
  소득 대비 원리금 상환 비율. 본 보고서는 연소득 대비 연간 원리금 상환액으로 산정.
  DSR ≥ 40%인 가구를 #emph[위험가구]로 분류한다.
]

#term("DTI", en: "Debt-to-Income Ratio")[
  연소득 대비 총부채 잔액의 배수. 위험 임계값은 별도 명시하지 않으나, 본 보고서
  §4에서는 분위 비교 지표로 사용.
]

#term("LTV", en: "Loan-to-Value Ratio")[
  담보 가치 대비 대출 잔액 비율. 본 보고서에서는 주택담보대출에 한정해 사용.
]

#term("BCa 부트스트랩", en: "Bias-Corrected and Accelerated Bootstrap")[
  편향 보정과 가속도를 포함한 부트스트랩 신뢰구간 산정법. Efron (1987) 참조.
]

#term("다중대입", en: "Multiple Imputation")[
  결측치를 #math.equation($m$) 개의 가능한 값으로 다중 추정하는 방법. 본 보고서는
  #math.equation($m = 5$), Rubin's rule로 분산을 결합.
]

#term("적응형 분산", en: "Adaptive Variance")[
  분포 꼬리의 영향을 가중치로 완화한 분산 추정량. Sato & Park (2024) 의 정의를 따른다.
]

#term("Winsorize", en: "Winsorization")[
  분위 내 ±3 IQR 초과 관측치를 상·하한값으로 치환하는 처리. 이상치 영향 완화.
]

// ══════════════════════════════════════════════════════════════════════════
//                            부록 D — 참고문헌
// ══════════════════════════════════════════════════════════════════════════
= 부록 D · 참고문헌

#set par(leading: 0.7em)

== 데이터 출처

#set enum(numbering: it => text(font: mono, fill: accent, weight: "medium")[[S#it]])

+ #strong[KOSIS 가계금융복지조사] (2025). 통계청. \
  #text(font: mono, size: 10pt, fill: mid)[
    https://kosis.kr/statHtml/statHtml.do?orgId=101#&tblId=DT_1HDLF05
  ]

+ #strong[한국은행 경제통계시스템 (ECOS)]. 가계부채 분기 통계. \
  #text(font: mono, size: 9pt, fill: mid)[
    https://ecos.bok.or.kr/#/SearchStat
  ]

+ #strong[가계동향조사] (2024–2026 분기). 통계청. \
  #text(font: mono, size: 9pt, fill: mid)[
    https://kosis.kr/statHtml/statHtml.do?orgId=101#&tblId=DT_1L9H016
  ]

#v(16pt)

== 문헌

#set enum(numbering: it => text(font: mono, fill: accent, weight: "medium")[[R#it]])

+ Efron, B. (1987). *Better Bootstrap Confidence Intervals.*
  Journal of the American Statistical Association, 82(397), 171–185.

+ Rubin, D. B. (1987). *Multiple Imputation for Nonresponse in Surveys.*
  John Wiley & Sons.

+ Sato, K. & Park, J. (2024). *Adaptive variance estimation for skewed
  financial distributions.* Korean Journal of Statistics, 31(2), 88–112.

+ Piketty, T. (2014). *Capital in the Twenty-First Century.*
  Harvard University Press.

+ 한국은행 (2025). *분기 가계부채 보고서 — 2025년 4분기.*
  한국은행 금융안정국.

+ 통계청 (2025). *2025년 가계금융복지조사 방법론 보고서.* 통계청 사회통계국.

#v(20pt)

== 인용 방법

본 보고서의 인용은 다음 형식을 권장한다.

#callout(label: "suggested citation", color: ink, bg: chip-bg)[
  #set text(font: mono, size: 10.5pt)
  Pied Piper 재정데이터 분석팀 (2026). \
  *재정데이터 분석 보고서: 2026년 1분기 가계 재정 분석.* \
  #meta.code, #meta.version. Seoul: Pied Piper.
]
