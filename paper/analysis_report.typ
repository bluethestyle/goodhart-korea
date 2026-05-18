// ══════════════════════════════════════════════════════════════════════════
//  재정데이터 분석 보고서 — Pied Piper
//  만성 재정 3종 문제(12월 몰아쓰기·출연기관 정산·평가 게임화) 정량 진단
//
//  스타일: 02_swiss_minimal_v3.typ 차용 (Swiss minimal, Linear/Vercel/Stripe Docs)
//  컴파일: typst compile paper/analysis_report.typ paper/analysis_report.pdf
// ══════════════════════════════════════════════════════════════════════════

// ── 폰트 ────────────────────────────────────────────────────────────────
#let sans = ("Pretendard", "Inter", "Helvetica Neue", "Noto Sans KR")
#let mono = ("JetBrains Mono", "IBM Plex Mono", "Consolas", "Menlo")

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
  code: "FA-MIN-PROJ/2026",
  version: "draft v1",
  date: "2026.05.18",
  org: "Pied Piper",
  team: "재정데이터 분석팀",
  authors: ("정선규", "심은철", "김영찬", "김재호"),
  period: "2015.01 — 2025.12",
  sample: "210K cells",
  sources: ("열린재정", "KODAS", "KOSIS", "ECOS", "공공데이터", "GIR"),
)

// ══════════════════════════════════════════════════════════════════════════
//  전역 텍스트 / 단락
// ══════════════════════════════════════════════════════════════════════════
#set text(font: sans, size: 10.5pt, lang: "ko", fill: ink, weight: "regular")
#set par(justify: false, leading: 0.78em, spacing: 1.1em)

// 헤딩 카운터 자동 increment 트리거 (본문엔 안 보임 — show rule이 it.body만 사용)
#set heading(numbering: "1.")

// 2자리 padding helper — numbering("01", n)이 n≥10에서 "010" 같이 깨지는 문제 우회
#let pad2 = (n) => {
  let s = str(n)
  if s.len() == 1 { "0" + s } else { s }
}

#show raw.where(block: false): it => box(
  inset: (x: 5pt, y: 1.5pt),
  outset: (y: 2pt),
  fill: chip-bg,
  radius: 3pt,
  text(font: mono, size: 9.5pt, fill: ink, it.text),
)

#show strong: it => text(weight: "semibold", fill: ink, it)
#show emph: it => text(style: "italic", fill: mid, it)

// ── 헤더 / 푸터 ─────────────────────────────────────────────────────────
#let body-header() = context {
  let p = counter(page).get().first()
  if p > 1 {
    grid(
      columns: (1fr, 1fr, 1fr),
      text(font: mono, size: 9.5pt, fill: soft, meta.code),
      align(center, text(font: sans, size: 9.5pt, fill: mid, weight: "medium")[
        만성 재정 3종 문제의 데이터 진단
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
      #meta.org #h(6pt) · #h(6pt) #(meta.team)
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
//  헤딩
// ══════════════════════════════════════════════════════════════════════════
#show heading.where(level: 1): it => {
  pagebreak(weak: true)
  v(28pt)
  block[
    #text(font: mono, size: 10pt, fill: accent, weight: "medium", tracking: 0.6pt)[
      ※ SECTION #counter(heading).display((..ns) => pad2(ns.pos().first()))
    ]
    #v(18pt)
    #text(font: sans, size: 34pt, weight: "semibold", tracking: -1pt, fill: ink)[
      #it.body
    ]
  ]
  v(10pt)
  line(length: 100%, stroke: 0.6pt + ink)
  v(30pt)
}

#show heading.where(level: 2): it => {
  v(26pt, weak: true)
  block[
    #text(font: sans, size: 20pt, weight: "semibold", tracking: -0.5pt, fill: ink)[
      #text(font: mono, size: 16pt, fill: accent, weight: "medium", tracking: 0.2pt)[
        #counter(heading).display("1.1")
      ]#h(14pt)#it.body
    ]
  ]
  v(10pt, weak: true)
}

#show heading.where(level: 3): it => {
  v(18pt, weak: true)
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
#let chip(label, fg: ink, bg: chip-bg) = box(
  inset: (x: 8pt, y: 3pt),
  outset: (y: 2pt),
  fill: bg,
  radius: 4pt,
  text(font: mono, size: 9pt, weight: "medium", fill: fg, tracking: 0.2pt)[
    #upper(label)
  ],
)

// KPI — fill+left accent+압축 v 간격으로 카드 묶음감 강화, 위/아래 텍스트 키움
#let kpi(label, value, sub: none, unit: "") = block(
  width: 100%,
  inset: 14pt,
  fill: ghost,
  stroke: (left: 2pt + accent, rest: 0.5pt + line-c),
  radius: (right: 4pt),
  spacing: 8pt,
)[
  #text(font: mono, size: 10.5pt, fill: mid, tracking: 0.4pt, weight: "medium")[#upper(label)]
  #v(-10pt)
  #text(font: sans, size: 26pt, weight: "semibold", tracking: -0.8pt, fill: ink)[
    #value
    #if unit != "" {
      text(size: 13pt, weight: "regular", fill: mid)[ #unit]
    }
  ]
  #if sub != none {
    v(-10pt)
    text(font: sans, size: 10pt, fill: mid, sub)
  }
]

#let chart-slot(
  id: "FIG-XX",
  title: "",
  note: "",
  height: 80mm,
) = block(
  width: 100%,
  height: height,
  fill: ghost,
  stroke: (paint: line-d, thickness: 0.6pt, dash: "dashed"),
  inset: 18pt,
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

#let caption(id, body) = block(
  inset: (top: 10pt),
  text(font: mono, size: 9pt, fill: soft, tracking: 0.3pt)[
    #upper(id) #h(10pt) · #h(10pt)
    #text(font: sans, size: 9.5pt, fill: mid, weight: "regular", body)
  ],
)

// 헤딩 부제 — 메인 헤딩 바로 아래 작은 활자로 (대시 패턴 대체, inline 형태)
#let h1sub(body) = {
  linebreak()
  text(font: sans, size: 18pt, weight: "regular", fill: mid, tracking: -0.3pt, body)
}
#let h2sub(body) = {
  linebreak()
  text(font: sans, size: 13pt, weight: "regular", fill: mid, tracking: -0.2pt, body)
}

#let callout(label: "NOTE", body, color: accent, bg: accent-bg) = block(
  width: 100%,
  fill: bg,
  inset: 18pt,
  radius: 5pt,
)[
  #text(font: mono, size: 9.5pt, fill: color, weight: "semibold", tracking: 0.4pt)[
    #upper(label)
  ]
  #v(10pt)
  #text(size: 10.5pt, fill: ink, body)
]

// ── 표 ─────────────────────────────────────────────────────────────────
#show table.cell.where(y: 0): set text(
  font: mono, size: 9pt, weight: "semibold", tracking: 0.4pt, fill: mid,
)
#show table.cell.where(y: 0): it => upper(it)
#set table(
  stroke: (x, y) => (
    bottom: if y == 0 { 1pt + ink } else { 0.4pt + line-c },
  ),
  inset: (x: 0pt, y: 11pt),
  align: (col, row) => if col == 0 { left } else { right },
)

// ══════════════════════════════════════════════════════════════════════════
//                                  표지
// ══════════════════════════════════════════════════════════════════════════
#page(
  margin: (x: 26mm, y: 26mm),
  header: none,
  footer: none,
)[
  #set text(font: sans, fill: ink)

  // 상단 메타
  #grid(
    columns: (1fr, 1fr),
    text(font: mono, size: 10pt, fill: ink, meta.code),
    align(right, text(font: mono, size: 10pt, fill: ink)[
      #meta.version  ·  #meta.date
    ]),
  )

  #v(48pt)

  #text(font: mono, size: 11pt, fill: accent, tracking: 1pt)[
    #upper[Fiscal Data Analysis · Mini Project 2026]
  ]
  #v(16pt)

  #text(font: sans, size: 44pt, weight: "semibold", tracking: -1.8pt, fill: ink)[
    지표가 채운 95%,\
    데이터가 찾은 격차
  ]
  #v(16pt)
  #text(font: sans, size: 18pt, weight: "regular", fill: mid, tracking: -0.4pt)[
    : 한국 중앙정부 재정 11년 21만 셀 패널 \
    — 집행률 · 결과지표 시계열 결합 분석
  ]
  #v(18pt)
  #text(font: sans, size: 13pt, weight: "regular", fill: soft, tracking: -0.2pt)[
    12월 집행 집중 · 출연금 정산 사이클 · \
    외부 사회·경제 결과 지표 결합
  ]

  #v(1fr)

  #line(length: 100%, stroke: 1pt + ink)
  #v(18pt)
  #grid(
    columns: (1.2fr, 1fr, 1.4fr, 1fr),
    column-gutter: 18pt,
    [
      #text(font: mono, size: 9.5pt, fill: mid, tracking: 0.4pt)[#upper[Authors]]
      #v(10pt)
      #for a in meta.authors [
        #text(size: 11pt, weight: "medium")[#a] \
      ]
    ],
    [
      #text(font: mono, size: 9.5pt, fill: mid, tracking: 0.4pt)[#upper[Period]]
      #v(10pt)
      #text(font: mono, size: 11pt, meta.period)
    ],
    [
      #text(font: mono, size: 9.5pt, fill: mid, tracking: 0.4pt)[#upper[Sources]]
      #v(10pt)
      #text(font: mono, size: 10pt, meta.sources.join(" · "))
    ],
    [
      #text(font: mono, size: 9.5pt, fill: mid, tracking: 0.4pt)[#upper[Sample]]
      #v(10pt)
      #text(font: mono, size: 11pt)[#meta.sample]
    ],
  )

  #v(18pt)

  #grid(
    columns: (1fr, 1fr),
    [
      #text(font: mono, size: 9.5pt, fill: mid, tracking: 0.4pt)[#upper[Published by]]
      #v(8pt)
      #text(size: 13pt, weight: "semibold")[#meta.org]
      #text(size: 13pt, fill: mid)[  ·  #(meta.team)]
    ],
    align(right + bottom, [
      #box(width: 14pt, height: 14pt, fill: accent)
      #h(8pt)
      #text(size: 13pt, weight: "semibold", meta.org)
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
  #v(10pt)
  #text(font: sans, size: 32pt, weight: "semibold", tracking: -0.8pt, fill: ink)[
    분석 결과 요약
  ]
  #v(6pt)
  #line(length: 100%, stroke: 0.6pt + ink)
  #v(22pt)

  #grid(
    columns: (28pt, 1fr),
    row-gutter: 18pt,
    column-gutter: 10pt,

    text(font: mono, size: 13pt, fill: accent, weight: "semibold")[01],
    [
      #text(size: 16pt, weight: "semibold", tracking: -0.3pt)[
        회계연도 마감 직전 집행이 *11월 대비 약 2.1배 점프*한다.
      ]
      #v(5pt)
      #text(size: 10.5pt, fill: mid)[
        사업별 정규화 비중 기준 11월 17.7% → 12월 37.2% (균등 가정 8.3%의 4.5배).
        *작은 사업일수록 점프 강도가 크다* — Q1(연 예산 하위 25%) 2.6배, Q4(상위 25%) 1.9배.
        회계연도 경계 일별 단절은 § 3 RDD 정량 분석.
      ]
    ],

    text(font: mono, size: 13pt, fill: accent, weight: "semibold")[02],
    [
      #text(size: 16pt, weight: "semibold", tracking: -0.3pt)[
        출연금형 사업은 *분기·반기 단위로 일률 정산*된다.
      ]
      #v(5pt)
      #text(size: 10.5pt, fill: mid)[
        활동별 시계열을 들여다보면 두 종류의 사업이 분명히 다른 모양을 그린다 — 평소엔
        0에 가깝다 특정 시점에 일제히 정산되는 패턴이 *시간이 갈수록 강해진다*.
        출연금 비중은 분야별 *80배 격차* (국방 0.2% — 과학기술 36.2%) — § 5 정량 분석.
      ]
    ],

    text(font: mono, size: 13pt, fill: accent, weight: "semibold")[03],
    [
      #text(size: 16pt, weight: "semibold", tracking: -0.3pt)[
        *집행률은 100%에 천장 압축*, 결과 지표는 *광범위하게 분산*된다.
      ]
      #v(5pt)
      #text(size: 10.5pt, fill: mid)[
        사업별 집행률 중앙값 100%, *약 67%가 95–100% 구간*에 압축.
        반면 같은 분야의 결과 지표 연간 변화율은 *-50% ~ +50% 광범위 분산* (σ ≈ 30%p).
        둘은 별개로 움직인다 — § 4 정량 분석.
      ]
    ],
  )

  #v(20pt)
  #line(length: 100%, stroke: 0.6pt + ink)
  #v(16pt)

  #callout(label: "정책 활용 영역")[
    본 분석은 *감사 자원 배분*·*경영평가 지표 개선*·*예산편성 협의*의 객관적
    근거로 활용 가능하다. 부처×결과 지표 *4분면 점검 우선순위*와 *점검 우선 활동 Top-50*은 § 8에서 산출물로 제시한다.
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
  #v(10pt)
  #text(font: sans, size: 32pt, weight: "semibold", tracking: -0.8pt, fill: ink)[
    이 보고서의 구성
  ]
  #v(6pt)
  #line(length: 100%, stroke: 0.6pt + ink)
  #v(22pt)

  #show outline.entry: it => {
    let lvl = it.level
    let body-style = if lvl == 1 {
      (size: 14pt, weight: "semibold", fill: ink)
    } else if lvl == 2 {
      (size: 11pt, weight: "regular", fill: mid)
    } else {
      (size: 9pt, weight: "regular", fill: soft)
    }
    let pad-left = (lvl - 1) * 16pt
    block(
      inset: (top: if lvl == 1 { 10pt } else { 3pt }, bottom: 0pt, left: pad-left),
      link(it.element.location(), grid(
        columns: (auto, 1fr, auto),
        column-gutter: 10pt,
        align: (left, left, right),
        if lvl == 1 {
          text(
            font: mono, size: 9.5pt, fill: accent, weight: "medium", tracking: 0.4pt,
            pad2(counter(heading).at(it.element.location()).first()),
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
= 서론 #h1sub[분석 배경과 문제 설정]

== 선행 진단의 누적 #h2sub[본 분석의 위치]

다음 세 가지 풍경은 한국 중앙정부 재정 운영의 현장에서 반복적으로 관찰되어 왔다.

- "12월 되면 도로를 다시 깐다"
- "출연기관은 어차피 모기관이 메워준다"
- "평가는 집행률만 잘 맞추면 통과한다"

*기획재정부 · 감사원 · 국회예산정책처*가 매년 지적해 왔으며 언론 보도도 반복되어 왔다.
회계연도 마감 집행, 출연기관 정산, 경영평가 지표 운영에 대한 공식 진단 · 국정감사 지적 · 언론
기획 보도가 누적되어 있다 (대표 사례는 아래 박스 및 부록 E 참조).

#v(10pt)

#block(
  width: 100%,
  fill: ghost,
  stroke: (left: 2pt + accent, rest: 0.5pt + line-c),
  inset: 16pt,
  radius: (right: 4pt),
)[
  #text(font: mono, size: 9pt, fill: accent, weight: "semibold", tracking: 0.4pt)[
    #upper[관련 언론·공식 진단 (대표 사례)]
  ]
  #v(10pt)

  #set text(size: 10pt, fill: ink)
  #grid(
    columns: (1fr,),
    row-gutter: 12pt,

    [
      *"멀쩡한 길, 또 뜯는다? — 해마다 반복되는 보도블록 공사, 세금만 줄줄 샌다"* \
      #text(size: 9.5pt, fill: mid, style: "italic")["'쓸 곳이 없으면 보도블록이라도 갈자'는 분위기가 암묵적으로 조성된다"] \
      #text(size: 9pt, fill: soft)[— 전국뉴스 · 2025.06.19 · #link("https://www.jeonguknews.co.kr/news/articleView.html?idxno=74694")[jeonguknews.co.kr]]
    ],
    [
      *"사실상 성역 된 출연금… '제재 규정 마련 시급'"* \
      #text(size: 9.5pt, fill: mid, style: "italic")["국가재정법에 출연금의 사후 정산·제재·처벌 규정이 전무하다"] \
      #text(size: 9pt, fill: soft)[— 서울경제 · 2025.03.10 · #link("https://m.sedaily.com/article/14037550")[sedaily.com]]
    ],
    [
      *"'생사 달렸다' 순위 경쟁에 매몰된 공공기관… 뭘 위한 평가인가"* \
      #text(size: 9.5pt, fill: mid, style: "italic")["기관의 운명이 평가 결과로 결정 — 순위 경쟁이 공공기관의 모든 에너지를 소모"] \
      #text(size: 9pt, fill: soft)[— 머니투데이 · 2025.08.11 · #link("https://www.mt.co.kr/economy/2025/08/11/2025081021183534668")[mt.co.kr]]
    ],
    [
      *국회예산정책처 「출연금 현황과 개선과제」 (장희란, 2022.5)* \
      #text(size: 9.5pt, fill: mid, style: "italic")[공공기관별·개별 출연사업별 정산체계 상이, 통일된 정산체계 부재 — 공식 진단] \
      #text(size: 9pt, fill: soft)[— 국회예산정책처 공공기관분석 · #link("https://www.nabo.go.kr")[nabo.go.kr]]
    ],
  )
]

#v(10pt)

본 보고서가 주목하는 질문은 *동일 풍경이 수십 년간 반복되는 구조적 원인*이다.
지속적 지적에도 해소되지 않는다는 사실은 이 패턴들이 행정 운영상의 일회적 오류가 아닌
*구조적 행동의 산물*임을 시사한다.

== 정량 진단의 부재 #h2sub[본 보고서의 문제 설정]

정성적 지적은 이미 풍부하지만, *세 풍경을 같은 데이터 패널 위에서 동시에 정량으로 본
사례는 없다*. 개별 사안에 대한 단편적 보고가 누적되어 있을 뿐, 다음 질문에 대한 답은
비어 있는 상태다.

- 12월 집행 점프는 *전 사업에서 균질한가*, 아니면 사업 유형에 따라 차이가 있는가?
- 출연금 정산의 주기성은 *시간이 갈수록 강화되는가*, 완화되는가?
- 집행률과 사회 결과 지표의 격차는 *부처별로 어떤 분포를 보이는가*?

본 보고서는 한국 중앙정부 월별 집행 자료 11년치 21만 셀 패널에 외부 사회·경제 지표를
결합해 이 빈자리에 정량으로 답한다.

#v(8pt)

#callout(label: "본 보고서의 분석 질문", color: ink, bg: chip-bg)[
  반복적으로 지적되어 온 세 패턴이 공개 재정·사회 데이터에 *어디서·얼마나·어떤 형태로* 나타나는지
  정량적으로 식별할 수 있는가? 그리고 관찰된 패턴은 *행정학·경제학에서 축적된 이론 frame*과
  어떻게 정합되는가?
]

== 학술 이론 frame과의 정합성

본 보고서의 작업이 임의적 관찰이 아닌 이유는, 위 세 패턴이 *행정학·경제학의 축적된 이론 frame*과
정확히 정합되기 때문이다. 평가 지표·인센티브·예산 제약을 다루는 세 갈래 이론이 각각의 패턴을
설명해 왔으며, *한국 중앙정부 재정에 세 frame을 동시에 적용해 정량 진단한 선행 사례는 부재*하다는
점이 본 분석의 위치다.

학술 frame의 정식 매칭은 § 6에서 다룬다. 본 보고서는 § 2에서 원자료 탐색으로 풍경을 재확인하고,
§ 3·4·5에서 *선행 지적이 데이터에 실제로 나타나는지 정량 검증*하며, § 6에서 *축적된 이론 frame과
정합성을 점검*한다.

#block(breakable: false)[
  == 본 보고서의 구성과 활용

  본 보고서는 *발견의 시각화 → 정량 검증 → 학술 frame 매칭 → 정책 시사점 도출*의
  4단계로 구성된다. 독자는 관심사에 따라 부분 발췌 독해가 가능하도록 챕터별 자기완결성을 유지하였다.

  #v(8pt)

  #set text(size: 10.5pt)
  #table(
    columns: (auto, 1fr),
    stroke: none,
    inset: (x: 0pt, y: 7pt),
    align: (left, left),

    [*Executive Summary*],     [5분 안에 파악하는 핵심 결론과 정책 활용 영역],
    [*§ 1 서론*],              [선행 진단의 누적·정량 진단의 부재·학술 frame 정합성],
    [*§ 2 EDA*],               [원자료 시각화로 본 세 가지 관찰 — 12월 점프·출연금 사이클·집행률 압축],
    [*§ 3·4·5 정량 분석*],     [사업 유형별·부처별·시점별 정량 검증과 통계 검정],
    [*§ 6 학술 frame*],        [축적된 행정학·경제학 이론과의 정합성 점검],
    [*§ 7 교차 검증*],         [관점·도구 간 결과 차이 정리와 견고성 확인],
    [*§ 8 산출물*],            [부처×결과 4분면 점검 우선순위 + 점검 우선 활동 Top-50],
    [*§ 9 정책 시사점*],       [회계 제도·평가 체계·감사 자원 배분 개선 방향],
    [*§ 10 한계*],             [통제군 부재·outcome 노이즈·시간 granularity 등 명시],
    [*부록 A–E*],              [용어집·데이터 출처·방법론 디테일·재현 코드·참고자료],
  )

  #v(10pt)

  #callout(label: "학술 용어 표기 원칙")[
    § 5까지의 본문은 *일상 어휘만으로 서술*하며, 학술 용어와 이론 frame은 § 6에서 일괄
    매칭한다. 본문 중 불분명한 용어는 부록 A 용어집을 참조하기 바란다.
    그림과 표 번호는 *FIG-2.3*, *TBL-2.2* 형식으로 챕터-순번을 표기한다.
  ]
]

// ══════════════════════════════════════════════════════════════════════════
= 데이터 탐색 #h1sub[원자료에서 보이는 세 가지 패턴]

#chip("EDA", fg: accent, bg: accent-bg) #h(4pt) #chip("raw observation")

여기서는 *모형이나 통계 검정 없이, 원자료 시각화만으로* § 1에서 본 세 풍경이 데이터에
실제로 나타나는지 차례로 살펴본다. 그림 한 장씩, 단순한 질문 — *그게 진짜 보이는가, 그럼 그
다음은?* — 을 따라 흘러간다. 정량 추정과 통계 검정은 § 3 이후에서 다룬다.

#v(14pt)

#callout(label: "본 챕터의 분석 원칙")[
  - 모든 그림은 *원자료에서 집계만 거친 결과*이며, 모형 추정·평활·필터링을 적용하지 않는다.
  - 학술 용어와 분석 도구 명칭은 본 챕터에서 사용하지 않으며, § 6에서 일괄 매칭한다.
  - 본 챕터의 결론은 § 3·4·5로 이어지는 *세 가지 분석 질문의 도출*에 한정하며, 정량 판단은 유보한다.
]

== 분석 데이터의 구성

분석 대상은 한국 중앙정부의 *2015년 1월 — 2025년 12월 월별 집행 자료 11년치*다.
132개월 × 1,557개 세부 활동 × 14개 분야가 단일 패널 형태로 정리되어 있으며,
외부 결과 지표 — 농가소득·교통사고·온실가스·고용 — 는 KOSIS · 한국은행 ECOS · 공공데이터포털 ·
온실가스종합정보센터(GIR) 에서 동일 기간 시점으로 결합하였다.

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

본 챕터의 모든 그림은 위 패널에서 *단순 집계만 거친 결과*이다.
회귀 추정·시계열 분해·군집 분류는 § 3 이후에서 다룬다.

== 관찰 1 #h2sub[12월 집행 분포의 이상 패턴]

가장 단순한 질문부터 시작한다 — *재정 집행이 시간상 어떻게 분포하는가*? 원자료의 월별
합계 시계열을 그려보면 분기말(3·6·9·12월)마다 집행이 솟는 일반적 패턴은 보이지만, 12월의
*특별성*은 단순 합계만으로는 분명히 드러나지 않는다.

문제는 *단순 합계가 큰 사업이 작은 사업을 가린다*는 점이다. 연 예산이 수조 원인 대형 사업
한 개의 월별 변동이, 수백억 원 규모의 수많은 소규모 사업이 보이는 패턴을 압도한다.
정직한 비교를 위해서는 *모든 사업을 동등하게* 보아야 한다.

그래서 시각을 바꾼다 — 각 사업을 *연간 총집행 = 100%*로 정규화한 뒤, *사업 규모 분위*(Q1 작음
~ Q4 큼)별로 월 평균 비중을 그린다. 균등하게 집행되면 매월 약 8.3% (= 100/12)가 기대값이다.

#v(10pt)

#image("figures/eda/fig_2_2_monthly_exec_total.png", width: 100%)
#caption("FIG-2.2")[
  사업 규모 4분위별 *사업당 월 평균 집행 비중* (2015–2025, 11년 평균). 각 사업을 연간 총집행 = 100%로
  정규화 후 분위 평균. 균등 가정 8.3% (점선). *Q1(작은 사업)이 12월에 15.4%로 가장 강하게 쏠리며,
  Q4(큰 사업)는 10.9%에 그친다.*
]

#v(12pt)

FIG-2.2에서 세 가지가 드러난다.

#block(breakable: false)[
  #grid(
    columns: (1fr, 1fr, 1fr),
    column-gutter: 12pt,
    kpi("11월 → 12월", "× 2.1", sub: "전체 평균 점프 (17.7% → 37.2%)"),
    kpi("Q1 작은 사업", "× 2.6", sub: "11월 → 12월 (6.0% → 15.4%)"),
    kpi("Q4 큰 사업", "× 1.9", sub: "11월 → 12월 (5.9% → 10.9%)"),
  )

  #v(14pt)

  #text(size: 11pt, fill: mid)[
    - *분기말 패턴은 모든 규모에 공통* — 3월(13%대), 6월(10%대) 솟음은 Q1–Q4 거의 동일.
    - *12월 점프 강도가 사업 규모에 단조 감소* — 작은 사업일수록 회계연도 마감 시점에
      더 강하게 쏠린다. Q1의 12월 비중(15.4%)은 균등 가정(8.3%)의 *약 1.9배*이고
      11월 대비 *2.6배 점프*.
    - *11월의 골에서 12월 솟음으로의 비대칭이 가장 두드러진다* — 분기말 중 11월 직전
      골이 가장 깊고, 그 다음 점프 강도가 가장 크다.
  ]
]

#v(14pt)

이 패턴이 *분야 단위에서도 같은가*? 같은 정규화를 14개 분야에 적용해 분야별 12월 비중을 본다.
각 분야의 평균 사업 규모도 막대 색에 함께 표시한다.

#v(8pt)

#image("figures/eda/fig_2_3_field_size_vs_dec.png", width: 100%)
#caption("FIG-2.3")[
  분야별 *12월 집행 비중 중앙값* (정렬). 막대 색: 분야 평균 사업 규모 (진한 빨강 → 작은 사업, 회색 → 큰 사업).
  *작은 사업 위주 분야*(통일·외교 88억·과학기술 100억대)가 12월에 50%+ 강하게 쏠리는 반면,
  *큰 사업 분야*(사회복지·산업·중소기업) 는 13%대에 그쳐 같은 사업 규모–쏠림 단조 관계가 분야 단위에서도 확인된다.
  *보건 분야*는 작은 사업이지만 12월 쏠림 21.7%로 예외적이다.
]

#v(14pt)

#callout(label: "§ 3 정량 분석 과제", color: ink, bg: chip-bg)[
  - 회계연도 경계(12.31) 일별 단절의 정밀 측정 — RDD bandwidth 1년·log scale
  - 사업 유형별(인건비·자산취득·출연금) 12월 점프 강도 차이 — UMAP+HDBSCAN 임베딩으로 사업 유형 자동 추출
  - 작은 사업이 시점 압력에 더 취약한 메커니즘 — 예산 규모 vs 행정 부담의 분산 분해
  - 보건 분야의 예외성 진단 — 작은 사업인데 분산적인 이유
]

== 관찰 2 #h2sub[출연금형 사업의 주기적 일률 정산]

이번에는 합계 대신 *개별 활동의 월별 시계열*을 하나씩 들여다본다. 두 가지 분명히 다른
모양이 보인다. 한 종류는 매월 비슷한 규모로 집행되는 안정적인 패턴(인건비·일반 운영형)이고,
다른 한 종류는 *평소에는 거의 0에 가깝다가 특정 분기·반기에 한꺼번에 큰 규모로 정산되는
패턴*이다.

#v(10pt)

#image("figures/eda/fig_2_4_activity_patterns.png", width: 100%)
#caption("FIG-2.4")[
  대표 활동 4건의 *11년 평균 월별 비중*. 위 두 사례는 *매월 균등에 가까운* 비중(국민연금급여지급 8.1–8.6%,
  재외공관 인건비 7.5–9.2%). 아래 두 사례는 *특정 시점에 큰 정산*이 몰리는 패턴 — 농가소득보전(직불기금)은
  11월에 67% 일률 정산, 지역경제지원은 2·9월 분기 정산.
]

#v(12pt)

그렇다면 두 번째 유형은 *어떤 분야에서 집중적으로 나타나는가*? 분야별 본예산 중 출연금
비중을 단순 집계로 비교해보면 분야 간 격차가 매우 크게 벌어진다.

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
  2026년 본예산 기준 분야별 출연금 비중 (14개 분야 중 일부 비교 표시).
  과학기술·통신 분야는 본예산의 1/3 이상이 출연금 항목으로 배정되어 있으며,
  일률 정산 패턴이 원자료 시계열에 직접 관찰된다.
]

#v(14pt)

#callout(label: "원자료에서 보이는 단서")[
  분야 간 출연금 비중 격차가 단순 집계만으로 *80배 이상* (국방 0.2% — 과학기술 36.2%)에 달한다.
  관찰 2의 일률 정산 패턴이 이 격차와 *원자료 단계에서 직접 맞물려 있다*는 점, 그리고
  같은 패턴이 관찰 1의 12월 점프와 *분야별로 다른 모양*을 만들어내는 단서로 보인다는 점이
  여기서 함께 떠오른다.
]

#v(14pt)

다음 질문이 이어진다 — 이 일률 정산 패턴은 *시간이 갈수록 강해지는가 안정적인가*?
분기·반기·연 중 어느 주기가 가장 우세한가? 출연금 비중과 12월 점프(관찰 1)는 *정량적으로 어떻게
연결되는가*? 원자료로는 단서까지만 보이고, 답은 다음 챕터에서 좁힌다.

#v(10pt)

#text(font: mono, size: 10pt, fill: accent, tracking: 0.4pt, weight: "medium")[#upper[§ 5 정량 분석 과제]]

- 일률 정산 패턴의 *시간 경과에 따른 강도 변화 추이*
- 분기·반기·연 주기 중 우세한 주기 식별
- 출연금 비중과 관찰 1(12월 점프) 간의 정량적 연관 분석

== 관찰 3 #h2sub[집행률 분포 압축과 결과 지표 분산의 비대칭]

세 번째로 부처별 집행률을 11년치 모아 분포로 그려본다. 거의 모든 부처가 95–100% 좁은 구간에
몰려 있다. 같은 부처가 책임지는 사회 결과 지표 — 농가소득·교통사고·온실가스 등 — 의 분포를
같은 폭으로 옆에 둔다. 분산이 *훨씬 넓다*. 한쪽은 천장에 압축, 한쪽은 흩어짐.

#v(10pt)

#block(breakable: false)[
  #image("figures/eda/fig_2_5_exec_vs_outcome.png", width: 100%)
  #caption("FIG-2.5")[
    좌: *사업별 집행률 분포* (n=29,892 사업–연도, 2015–2025). 95–100% 구간(빨강 음영)에 *2/3가 압축*,
    중앙값 100%. 우: *분야별 결과지표 연간 변화율 분포* (n=3,046 분야–지표–연도). 평균 ≈ 0% 중심으로
    -50% ~ +50% 광범위 분산, std 약 30%p. *두 분포의 모양이 체계적으로 다르다.*
  ]

  #v(14pt)

  #grid(
    columns: (1fr, 1fr, 1fr),
    column-gutter: 12pt,
    kpi("집행률 중앙값", "100 %", sub: "사업별 연간 · n=29,892"),
    kpi("95–100% 압축", "≈ 67 %", sub: "전체 사업 중 천장 구간 비율"),
    kpi("결과 지표 σ", "30 %p", sub: "YoY 변화율 — 광범위 분산"),
  )

  #v(14pt)

  #text(size: 11pt, fill: mid)[
    같은 11년·같은 부처를 두고 *예산이 얼마나 쓰였는가*(집행률)와 *그 돈이 책임지는
    사회 지표가 어떻게 움직였는가*(결과 지표)를 나란히 놓으면, 두 분포의 모양이
    *체계적으로 다르다*. 두 변수가 별개로 움직인다는 뜻이다.

    왜 이런 격차가 보이는가? 두 가지 가능성이 떠오른다.
  ]
  #v(8pt)
  - 집행률이 사회 결과 지표를 결정하는 변수가 *아닐* 가능성
  - 측정이 쉬운 지표(예산 집행)와 어려운 지표(사회 결과) 사이의 *행정 압력 차이*가 결과에 흔적을 남길 가능성
]

#v(14pt)

#callout(label: "§ 4 정량 분석 과제", color: ink, bg: chip-bg)[
  - 집행률 ≠ 사회 지표 개선이라면, 양자의 격차를 결정하는 요인 식별
  - 격차의 분산이 *부처 단위* 또는 *사업 유형 단위* 중 어느 차원에서 더 크게 설명되는지
  - 결과 지표 변동의 분산 분해 — 집행률 기여분과 사업 유형 기여분의 정량 분리
]

== EDA 결론 #h2sub[정량 분석으로 이어지는 세 가지 분석 질문]

세 관찰을 따로 보면 단편적 시각화 결과지만, 각 관찰이 남긴 *분석 질문을 같은 자리에 놓고
보면 하나의 구조적 패턴*이 드러나기 시작한다. 여기서의 결론은 정량 판단이 아니라
*다음 챕터에서 본격적으로 검증할 분석 과제의 도출*이다.

#v(12pt)

#block(breakable: false)[
  #grid(
    columns: (28pt, 1fr),
    row-gutter: 16pt,
    column-gutter: 10pt,

    text(font: mono, size: 13pt, fill: accent, weight: "semibold")[Q1],
    [
      #text(size: 13pt, weight: "semibold")[12월 점프의 *사업 유형별 이질성*은 어떻게 분포하는가?]
      #v(3pt)
      #text(size: 10.5pt, fill: mid)[
        관찰 1 → *§ 3*: 분야·사업 유형별 점프 크기 비교 및 회계연도 경계의 정량 단절 측정.
      ]
    ],

    text(font: mono, size: 13pt, fill: accent, weight: "semibold")[Q2],
    [
      #text(size: 13pt, weight: "semibold")[집행률과 사회 결과 지표 *격차의 결정 요인*은 무엇인가?]
      #v(3pt)
      #text(size: 10.5pt, fill: mid)[
        관찰 3 → *§ 4*: 14분야 기준 분류와 데이터 기반 자동 군집의 설명력 비교 분석.
      ]
    ],

    text(font: mono, size: 13pt, fill: accent, weight: "semibold")[Q3],
    [
      #text(size: 13pt, weight: "semibold")[일률 정산 패턴은 *시간 경과에 따라 강화되는가*?]
      #v(3pt)
      #text(size: 10.5pt, fill: mid)[
        관찰 2 → *§ 5*: 출연금 비중과 정산 주기의 시간 동학 분석, 분기·반기·연 주기 강도 추적.
      ]
    ],
  )

  #v(14pt)

  #callout(label: "본 챕터 요약", color: ink, bg: chip-bg)[
    EDA에서 본 세 패턴 — *12월 집행 점프*, *출연금형 일률 정산*, *집행률 압축 — 결과 지표
    분산 비대칭* — 은 서로 독립적인 우연으로 보기 어려운 구조적 단서다. § 3·4·5에서 각
    패턴을 정량 검증하고, § 6에서 *축적된 행정학·경제학 이론 frame*과 어떻게 맞물리는지 확인한다.
  ]
]

// ══════════════════════════════════════════════════════════════════════════
//  § 3 이후는 후속 작업 placeholder
// ══════════════════════════════════════════════════════════════════════════

= 12월의 압력 #h1sub[회계연도 마감이 만든 점프]

#chip("placeholder", fg: warn, bg: rgb("#fef3c7"))

본 챕터는 § 2 관찰 1의 정량화 — *후속 작업*. 사업 종류별 12월 점프 크기 비교, 회계연도 경계 회귀 분석,
1,000회 순열 검정 결과 포함 예정.

= 측정 격차 #h1sub[집행률 천장 vs 결과 분산]

#chip("placeholder", fg: warn, bg: rgb("#fef3c7"))

본 챕터는 § 2 관찰 3의 정량화 — *후속 작업*. 활동 자동 군집, 14분야 vs 자동 군집의 행동 설명력 비교,
집행률 → 사업 종류 → outcome 매개 경로 검증 예정.

= 출연기관 정산 압력 #h1sub[주기적 패턴의 정체]

#chip("placeholder", fg: warn, bg: rgb("#fef3c7"))

본 챕터는 § 2 관찰 2의 정량화 — *후속 작업*. 출연금형 사업 시간-주파수 분석, 출연금 비중과 점프 강도 상관,
시간 동학 추적 예정.

= 학계는 30년째 이름을 붙여왔다

#chip("placeholder", fg: warn, bg: rgb("#fef3c7"))

§3·§4·§5 발견과 학술 이론(*굿하트-캠벨 법칙* · *다업무 계약 이론* · *연성 예산 제약*)의 통합 매칭 — *후속 작업*.
한눈에 매칭표 + 각 이론 frame이 발견과 어떻게 맞물리는지 풀이.

= 교차 검증

#chip("placeholder", fg: warn, bg: rgb("#fef3c7"))

도구 간·관점 간 결과 차이 정리. 발산 지점이 자기 비판의 출발점이라는 원칙의 실제 적용.

= 산출물 #h1sub[현장에서 쓸 수 있는 것]

#chip("placeholder", fg: warn, bg: rgb("#fef3c7"))

부처×결과변수 4분면 점검 우선순위 + 점검 우선 활동 Top-50 + 자동 점검 알고리즘.

= 정책 시사점

#chip("placeholder", fg: warn, bg: rgb("#fef3c7"))

다년도 회계 도입 확대 · 출연기관 정산 분산 · 경영평가 지표 개선 · 데이터 인프라 개선 · 자동 flagging.

= 한계와 향후 과제

#chip("placeholder", fg: warn, bg: rgb("#fef3c7"))

통제군 부재 · outcome 노이즈 · 데이터 시간 granularity · 출연기관 거버넌스 데이터 부재.

= 부록

#chip("placeholder", fg: warn, bg: rgb("#fef3c7"))

A 용어 사전 · B 데이터 출처와 라이선스 · C 방법론 디테일 · D 재현 코드 안내 · E 참고자료 *(학술 문헌 + 선행 공식 진단 + 언론 보도 인용)*.
