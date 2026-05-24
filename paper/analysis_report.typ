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
  v(16pt, weak: true)
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

// 캡션 — V2 (좌측 레일 ID + 우측 컬럼 [강조 한 줄 + 본문])
//  · id    : "FIG-2.5" / "TBL-2.1" 등 — 좌측 mono 액센트 라벨
//  · title : 한 줄 결론 (sans semibold, ink) — 스캔용
//  · body  : 상세 설명 (sans regular, mid) — 디테일
#let caption(id, title, body) = block(
  width: 100%,
  above: 12pt,
  below: 8pt,
)[
  #line(length: 100%, stroke: 0.4pt + line-c)
  #v(10pt)
  #grid(
    columns: (64pt, 1fr),
    column-gutter: 14pt,
    align: (left + top, left + top),
    text(
      font: mono, size: 9pt, fill: accent,
      weight: "semibold", tracking: 0.5pt,
    )[#upper(id)],
    [
      #text(
        font: sans, size: 10.5pt, fill: ink,
        weight: "semibold", tracking: -0.1pt,
        title,
      )
      #v(10pt, weak: true)
      #text(font: sans, size: 9.5pt, fill: mid, body)
    ],
  )
]

// 헤딩 부제 — 인라인 호출(`= 서론 #h1sub[...]`)이라 사실상 헤딩 본문 일부가 된다.
//  · 헤딩 show rule이 본문을 큰 text() 안에 그릴 때, block은 줄을 깨고
//    `inset: top: -22pt` 만큼 위로 당겨져 타이틀 바로 아래 붙어 보인다.
//  · 다만 목차(outline)는 `it.element.body`를 통째로 그리므로 서브타이틀이 같은
//    셀에 겹쳐 나온다 → outline.entry에서 `strip-blocks`로 block을 걸러 그린다.
#let h1sub(body) = block(
  inset: (top: -22pt, bottom: 10pt),
  text(font: sans, size: 18pt, weight: "regular", fill: mid, tracking: -0.3pt, body),
)
#let h2sub(body) = block(
  inset: (top: -8pt, bottom: 0pt),
  text(font: sans, size: 13pt, weight: "regular", fill: mid, tracking: -0.2pt, body),
)

// 헤딩 본문에서 첫 block(=서브타이틀) 이전까지의 인라인 텍스트만 추출 — 목차용.
#let strip-blocks(body) = {
  if type(body) == str { return body }
  if body.has("children") {
    let out = []
    for c in body.children {
      if c.func() == block { break }
      out += c
    }
    out
  } else { body }
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
  font: mono, size: 11pt, weight: "semibold", tracking: 0.4pt, fill: mid,
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
        회계연도 경계 일별 단절은 § 3 정량 분석 (회귀불연속 설계, RDD).
      ]
    ],

    text(font: mono, size: 13pt, fill: accent, weight: "semibold")[02],
    [
      #text(size: 16pt, weight: "semibold", tracking: -0.3pt)[
        출연금형 사업은 *주기적으로 일제히 정산*된다.
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
      (size: 15pt, weight: "semibold", fill: ink)
    } else if lvl == 2 {
      (size: 11.5pt, weight: "regular", fill: mid)
    } else {
      (size: 10pt, weight: "regular", fill: soft)
    }
    // L1 = 큰 간격, L2+ = 좁은 간격으로 시각적 군집
    let top-gap = if lvl == 1 { 12pt } else { 3pt }
    // L2 이하는 왼쪽으로 들여쓰기 (번호 컬럼 폭만큼은 아니고 살짝)
    let indent = (lvl - 1) * 14pt

    block(
      inset: (top: top-gap, bottom: 0pt, left: indent),
      link(
        it.element.location(),
        grid(
          // 고정폭 번호 컬럼 + 본문 + 고정폭 페이지 컬럼 → 모든 level 본문 시작 x 일치
          columns: (30pt, 1fr, 24pt),
          column-gutter: 12pt,
          align: (left + horizon, left + horizon, right + horizon),
          // 번호 (L1만)
          if lvl == 1 {
            text(
              font: mono, size: 10pt, fill: accent, weight: "medium", tracking: 0.4pt,
              pad2(counter(heading).at(it.element.location()).first()),
            )
          } else { [] },
          // 본문 — 헤딩 안의 block(서브타이틀)은 strip-blocks가 걸러냄
          text(..body-style, strip-blocks(it.element.body)),
          // 페이지 번호
          text(font: mono, size: 10pt, fill: soft, it.page()),
        ),
      ),
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
    [
      *한국재정정보원 「재정지출 효율화를 위한 불용유형 분석 및 집행관리방안」 (김명규·김민경·지은초, 2022.12)* \
      #text(size: 9.5pt, fill: mid, style: "italic")[주요 불용사업 2,389개의 63%가 하반기 집행형. 월 집행률 변동성–불용률 상관 −0.31 — 같은 dBrain 데이터의 선행 정량 분석] \
      #text(size: 9pt, fill: soft)[— 한국재정정보원 분석 22-03 · #link("https://www.fis.kr/ko/notification/data/report?articleSeq=3464")[fis.kr]]
    ],
  )
]

#v(10pt)

본 보고서가 주목하는 질문은 *동일 풍경이 수십 년간 반복되는 구조적 원인*이다.
지속적 지적에도 해소되지 않는다는 사실은 이 패턴들이 행정 운영상의 일회적 오류가 아닌
*구조적 행동의 산물*임을 시사한다.

== 통합 정량 진단의 위치 #h2sub[본 보고서의 문제 설정]

정량 분석이 전무한 영역은 아니다. 같은 dBrain 패널을 활용한 한국재정정보원의 선행
분석(김명규 외, 2022)이 *주요 불용사업 2,389개*에서 *월 집행률 변동성–불용률 상관*을
드러낸 바 있다. 그러나 다음 질문에 대한 답은 여전히 *비어 있다*.

- 12월 집행 점프는 *전 사업에서 균질한가*, 아니면 사업 유형에 따라 차이가 있는가?
- 출연금 정산의 주기성은 *시간이 갈수록 강화되는가*, 완화되는가?
- 집행률과 사회 결과 지표의 격차는 *부처별로 어떤 분포를 보이는가*?

선행 분석은 *주요 불용사업 표본·단년도 산포도·상관 추정*에 머물러 있다. 본 보고서는
한국 중앙정부 월별 집행 자료 11년치 21만 셀 *전체 패널*에 외부 사회·경제 지표를 결합해,
*인과 추정(RDD) · 사후 군집 발견(TDA) · 시간 동학(웨이블릿) · 결과 매개(Sobel)* 네 도구를
한 분석 틀로 묶어 이 빈자리에 답한다.

#v(8pt)

#callout(label: "본 보고서의 분석 질문", color: ink, bg: chip-bg)[
  반복적으로 지적되어 온 세 패턴이 공개 재정·사회 데이터에 *어디서·얼마나·어떤 형태로* 나타나는지
  정량적으로 식별할 수 있는가? 그리고 관찰된 패턴은 *행정학·경제학에서 축적된 이론 frame*과
  어떻게 들어맞는가?
]

== 학술 이론 frame과의 맞물림

본 보고서의 작업이 임의적 관찰이 아닌 이유는, 위 세 패턴이 *행정학·경제학의 축적된 이론 frame*과
정확히 들어맞기 때문이다. 평가 지표·인센티브·예산 제약을 다루는 세 갈래 이론이 각각의 패턴을
설명해 왔으며, *한국 중앙정부 재정에 세 frame을 동시에 적용해 정량 진단한 선행 사례는 부재*하다는
점이 본 분석의 위치다.

학술 frame의 정식 매칭은 § 6에서 다룬다. 본 보고서는 § 2에서 원자료 탐색으로 풍경을 재확인하고,
§ 3·4·5에서 *선행 지적이 데이터에 실제로 나타나는지 정량 검증*하며, § 6에서 *축적된 이론 frame과
맞물림을 점검*한다.

#block(breakable: false)[
  == 본 보고서의 구성과 활용

  본 보고서는 *발견의 시각화 → 정량 검증 → 학술 frame 매칭 → 정책 시사점 도출*의
  4단계로 구성된다. 독자는 관심사에 따라 부분 발췌 독해가 가능하도록 챕터별 자기완결성을 유지하였다.

  #v(8pt)

  #set text(size: 10.5pt)
  #grid(
    columns: (auto, 1fr),
    column-gutter: 18pt,
    row-gutter: 10pt,

    [*Executive Summary*],     [5분 안에 파악하는 핵심 결론과 정책 활용 영역],
    [*§ 1 서론*],              [선행 진단의 누적·정량 진단의 부재·학술 frame 맞물림],
    [*§ 2 EDA*],               [원자료 시각화로 본 세 가지 관찰 — 12월 점프·출연금 사이클·집행률 압축],
    [*§ 3·4·5 정량 분석*],     [사업 유형별·부처별·시점별 정량 검증과 통계 검정],
    [*§ 6 학술 frame*],        [축적된 행정학·경제학 이론과의 맞물림 점검],
    [*§ 7 교차 검증*],         [관점·도구 간 결과 차이 정리와 견고성 확인],
    [*§ 8 산출물*],            [부처×결과 4분면 점검 우선순위 + 점검 우선 활동 Top-50],
    [*§ 9 정책 시사점*],       [회계 제도·평가 체계·감사 자원 배분 개선 방향],
    [*§ 10 한계*],             [통제군 부재·결과 지표 잡음·자료 시간 단위 한계 등 명시],
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

#v(6pt)

본 챕터는 *선행 분석의 관찰에서 출발*한다. 한국재정정보원(김명규 외, 2022)이 같은
dBrain 패널의 *주요 불용사업 2,389개* (재량지출 + 10억원 이상 + 불용률 10% 이상)에서
*63%가 하반기 집행형*임을 보였다. 본 챕터는 그 출발점을 받아 안되, *불용사업으로 한정하지
않고 전체 활동 1,557개*를 동등하게 보고, 사업 형태에 따른 시점 분포의 *이질성*에
초점을 옮긴다.

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

#block(breakable: false)[
  #table(
    columns: (0.6fr, 0.6fr, 0.5fr, 1fr),
    table.header[데이터][기간][단위][출처],
    [월별 집행 (재정)],       [2015 — 2025], [활동 × 월], [열린재정 / KODAS],
    [편성목 구성 (재정)],     [2015 — 2025], [활동 × 년], [열린재정 / KODAS],
    [14분야 결과지표],        [2015 — 2025], [분야 × 년], [KOSIS · ECOS · 공공데이터],
    [소비자물가 (외부 요인 통제)],  [2015 — 2025], [전국 × 월], [한국은행 ECOS],
    [온실가스 인벤토리],      [2015 — 2023], [전국 × 년], [GIR],
    [도로교통 통계],          [2015 — 2025], [전국 × 년], [도로교통공단],
  )
  #caption(
    "TBL-2.1",
    [분석 패널의 원천 데이터.],
  )[
    모든 자료는 공공 API·공개 다운로드 기반, 비영리·연구 활용 허용 범위 내.
    결합 후 분석용 패널은 *활동 1,557개 × 132개월 ≈ 21만 셀*.
  ]
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
#caption(
  "FIG-2.2",
  [Q1 작은 사업이 12월에 가장 강하게 쏠리고, Q4 큰 사업은 완만하다.],
)[
  사업 규모 4분위별 *사업당 월 평균 집행 비중* (2015–2025, 11년 평균). 각 사업을 연간 총집행 = 100%로
  정규화 후 분위 평균. 균등 가정 8.3% (점선). Q1 12월 비중 15.4% vs Q4 10.9%.
]

#v(12pt)

FIG-2.2에서 세 가지가 드러난다.

#block(breakable: false)[
  #grid(
    columns: (1fr, 1fr, 1fr),
    column-gutter: 12pt,
    kpi("11월 → 12월", "× 2.1", sub: "전체 평균 점프 \n (17.7% → 37.2%)"),
    kpi("Q1 작은 사업", "× 2.6", sub: "11월 → 12월 \n (6.0% → 15.4%)"),
    kpi("Q4 큰 사업", "× 1.9", sub: "11월 → 12월 \n (5.9% → 10.9%)"),
  )

  #v(14pt)

  #text(size: 11pt, fill: mid)[
    - *분기말 패턴은 모든 규모에 공통* — 3월(13%대), 6월(10%대) 솟음은 Q1–Q4 거의 동일.
    - *12월 점프 강도가 사업 규모에 한 방향으로 꾸준히 감소* — 작은 사업일수록 회계연도 마감 시점에
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
#caption(
  "FIG-2.3",
  [사업 규모가 작은 분야일수록 12월에 더 쏠린다 — 같은 한 방향 관계가 분야 단위에서도 확인된다.],
)[
  분야별 *12월 집행 비중 중앙값* (사업×연도 단위 dec\_share median, 정렬).
  막대 색: 분야 평균 사업 규모 (진한 빨강 → 작은 사업, 회색 → 큰 사업).
  *작은 사업 위주 분야*(통일·외교 88억 = 100.0%, 일반·지방행정 140억 = 46.0%)가 12월에 강하게
  쏠리는 반면, *큰 사업 분야*(사회복지 297억 = 13.4%, 산업·중소·에너지 263억 = 13.5%)는 13%대에
  그친다 — *약 7.5배 격차*. 통일·외교 100%는 분야 내 사업 절반 이상이 일부 해에 12월에만
  집행되는 극단 패턴이고, 사회복지 13.4%는 기초연금 등 매월 균등 집행이 분야 중앙값을 끌어내린
  결과다. *보건 분야*는 작은 사업(76억)이지만 12월 쏠림 21.7%로 예외적이다.
]

#v(14pt)

#callout(label: "§ 3 정량 분석 과제", color: ink, bg: chip-bg)[
  - 회계연도 경계(12.31)에서 *집행이 단절적으로 점프하는 정도*를 일별 단위로 정밀 측정
  - 사업 유형(인건비·자산취득·출연금) 별 12월 점프 강도 차이 — 사업 유형 자체를 *데이터에서 자동 도출*
  - 작은 사업이 시점 압력에 더 취약한 메커니즘 — 예산 규모 vs 행정 부담의 변동 원인 분리
  - 보건 분야의 예외성 진단 — 작은 사업인데 분산적인 이유
]

#pagebreak()

== 관찰 2 #h2sub[출연금형 사업의 주기적 일률 정산]

이번에는 합계 대신 *개별 활동의 월별 시계열*을 하나씩 들여다본다. 두 가지 분명히 다른
모양이 보인다. 한 종류는 매월 비슷한 규모로 집행되는 안정적인 패턴(인건비·일반 운영형)이고,
다른 한 종류는 *평소에는 거의 0에 가깝다가 특정 시점에 한꺼번에 큰 규모로 정산되는
패턴*이다 (정산 주기는 § 5에서 정량 식별).

#v(10pt)

#image("figures/eda/fig_2_4_activity_patterns.png", width: 100%)
#caption(
  "FIG-2.4",
  [활동의 월별 시계열은 두 종류 — 매월 균등 vs 특정 시점 일률 정산.],
)[
  대표 활동 4건의 *11년 평균 월별 비중*. 위 두 사례는 *매월 균등*에 가까운 비중(국민연금급여지급 8.1–8.6%,
  재외공관 인건비 7.5–9.2%). 아래 두 사례는 *특정 시점에 큰 정산*이 몰리는 패턴 — 농가소득보전(직불기금)은
  11월에 67% 일률 정산, 지역경제지원은 2·9월 분기 정산.
]

#v(12pt)

그렇다면 두 번째 유형은 *어떤 분야에서 집중적으로 나타나는가*? 분야별 본예산 중 출연금
비중을 단순 집계로 비교해보면 분야 간 격차가 매우 크게 벌어진다.


#pagebreak()

#v(-15pt)
#block(breakable: false)[
  #table(
    columns: (1fr, 1fr, 1fr, 1fr),
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
  #caption(
    "TBL-2.2",
    [분야별 출연금 비중 — 국방 0.2% ↔ 과학기술 36.2%, *약 80배 격차*.],
  )[
    2026년 본예산 기준 분야별 출연금 비중 (14개 분야 중 일부 비교 표시).
    과학기술·통신 분야는 본예산의 1/3 이상이 출연금 항목으로 배정되어 있으며,
    일률 정산 패턴이 원자료 시계열에 직접 관찰된다.
  ]
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

#callout(label: "§ 5 정량 분석 과제", color: ink, bg: chip-bg)[
  - 일률 정산 패턴의 *시간 경과에 따른 강도 변화 추이*
  - 분기·반기·연 주기 중 우세한 주기 식별
  - 출연금 비중과 관찰 1(12월 점프) 간의 정량적 연관 분석
]

== 관찰 3 #h2sub[집행률 분포 압축과 결과 지표 분산의 비대칭]

세 번째로 부처별 집행률을 11년치 모아 분포로 그려본다. 거의 모든 부처가 95–100% 좁은 구간에
몰려 있다. 같은 부처가 책임지는 사회 결과 지표 — 농가소득·교통사고·온실가스 등 — 의 분포를
같은 폭으로 옆에 둔다. 분산이 *훨씬 넓다*. 한쪽은 천장에 압축, 한쪽은 흩어짐.

#v(0pt)

#block(breakable: false)[
  #image("figures/eda/fig_2_5_exec_vs_outcome.png", width: 100%)
  #caption(
    "FIG-2.5",
    [집행률은 95–100%에 2/3가 압축, 결과지표는 ±50%로 분산 — 두 분포의 모양이 체계적으로 다르다.],
  )[
    좌: *사업별 집행률 분포* (n=29,892 사업–연도, 2015–2025). 중앙값 100%, 95–100% 구간(빨강 음영)에 *2/3가 압축*.
    우: *분야별 결과지표 연간 변화율 분포* (n=3,046 분야–지표–연도). 평균 ≈ 0% 중심으로
    -50% ~ +50% 광범위 분산, std 약 30%p.
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
  - 결과 지표 변동의 변동 원인 분리 — 집행률 기여분과 사업 유형 기여분의 정량 분리
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
        관찰 1 → *§ 3*: 분야·사업 유형별 점프 크기 비교 및 회계연도 경계의 수치로 잡히는 끊김 측정.
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

== 출발 질문 #h2sub[같은 12월 점프, 사업마다 다를까]

§ 2 EDA의 마지막 관찰은 *세 풍경이 서로 독립적 우연으로 보기 어렵다*는 것이었다. 본 챕터는
그 출발점인 *12월 점프*를 정량으로 좁힌다 — 11월 17.7% → 12월 37.2%의 *2.1배 점프*, 그리고
작은 사업일수록 더 강한 쏠림이 있었다(관찰 1). 다음 질문은 두 가지다.

- 12월 점프는 모든 사업에 *균질한 압력*인가, 사업 *유형에 따라* 체계적으로 다른가?
- 그 차이가 보인다면, 회계연도 경계(12월 31일)라는 *행정적 시점*에 진짜 응답하는 것인가?

*왜 이 질문이 중요한가* — 점프가 모든 사업에 균질하다면 정책 처방은 *단일*하지만, 사업 유형별로
다르다면 *처방도 차별화*돼야 한다. 감사 자원·평가 가중·예산 협의의 방향이 달라진다.

EDA에서는 사업 *규모*로 나눠 보았다(Q1 작음 → Q4 큼). 본 챕터는 한 단계 더 좁혀 *지출 구성*
(인건비·자산취득·출연금·일반)으로 갈라 본다. 이 *사업 유형 라벨*은 본 챕터에서는 잠시 가져다
쓰되, *근거 자체*는 § 4에서 데이터로 자동 발견된다(forward-pointer).

== 측정 절차 #h2sub[같은 사업을 11월 말과 12월 초로 잘라 보기]

직관은 단순하다 — 사업 본질에서 오는 변동(공정률·계약 일정·계절 수요)은 *11월과 12월 며칠
사이*에 급변하지 않는다. 반면 회계연도 마감이라는 *행정적 시점*은 12월 1일을 기점으로 압력을
만든다. 그래서 *같은 활동의 11월 마지막 주 vs 12월 첫 주 일평균 집행*을 비교하면, 사업 본질을
거의 통제한 *행정 시점 효과의 수치로 나타낸 값*에 가까워진다.

*왜 일·월 단위가 아닌 며칠 단위인가* — 12월 합계 vs 다른 달 합계로 비교하면 사업 본질의 계절
변동이 섞인다. 11월 vs 12월 같은 *월 단위 차분*도 분기 마감 효과가 끼어든다. 며칠 단위로 좁혀야
*회계연도 경계 그 자체*의 효과를 분리할 수 있다. 비교 결과의 분포가 우연인지 아닌지는 활동
단위 *1,000회 무작위 섞기*로 확인한다.

#callout(label: "본 챕터의 핵심 측정", color: ink, bg: chip-bg)[
  핵심 측정값: *11월 마지막 주 → 12월 첫 주 일평균 집행 배수* (활동 단위).
  배수 1.0이면 회계 시점 효과 없음, 2.0이면 일평균이 두 배로 점프.
  *경계 직전·직후를 잘라 비교하는 절차*는 통계학에서 *회귀불연속 설계*(Regression Discontinuity
  Design, RDD)라 부르며, 본 보고서는 본문에서 줄여 "12월 RDD"로 표기한다. 정식 수식·절차는
  부록 C에서, 학술 frame은 § 6.1에서 다룬다.
]

== 결과 1 #h2sub[전체 1.91배, 그러나 사업 유형별로 극단 격차]

활동 단위 일평균 집행의 12월 점프는 전체 평균 *1.91배* ($p < 10^{-124}$). 그러나 같은 정의로
사업 유형별 분해를 하면 *세 배 이상의 격차*가 드러난다.

#v(10pt)

#image("figures/report/h22_rdd_monthly.png", width: 100%)
#caption(
  "FIG-3.1",
  [활동 단위 일집행액이 매년 11→12월에 뚜렷한 점프, 3·6·9월에도 부수 점프가 관찰된다.],
)[
  활동 단위 월 평균 일집행액 (2015–2025). 색상은 연도(보라 2015 → 노랑 2025), 굵은 검정선은 11년 평균.
  *11→12월 영역(빨강)*에서 12월 점프가 매년 가시화되며, *3·6·9월*에도 분기말 부수 점프가 나타난다.
  점프는 매년 반복되는 패턴이지 특정 연도의 우연이 아니다.
]

#v(10pt)

#image("figures/report/h22_rdd_field.png", width: 100%)
#caption(
  "FIG-3.2",
  [자산취득형 3.42배 vs 인건비·출연금형 1.1배대 — 사업 유형에 따라 점프 응답이 체계적으로 다르다.],
)[
  사업 유형별 12월 점프 배수 (11월 마지막 주 → 12월 첫 주 일평균 비율). *자산취득형 사업군(C1, n=99 활동 풀링)이 3.42배로 가장 강함*,
  정상사업 2.24배, 인건비형·출연금형은 1.1배대. 사업 본질에서 오는 변동이 아니라, 회계 시점 압력에
  대한 응답이 사업 유형에 따라 다른 모양으로 발현된다.
]

#v(14pt)

#block(breakable: false)[
  #grid(
    columns: (1fr, 1fr),
    column-gutter: 10pt,
    kpi("자산취득형", "× 3.42", sub: "C1 군집 풀링 (n=99 활동) — 공정률 마감 + 회계 마감"),
    kpi("정상사업", "× 2.24", sub: "베이스라인 (n=1,175)"),
    kpi("인건비형", "× 1.12", sub: "구조상 평탄 — 점프 거의 없음"),
    kpi("출연금형", "× 1.10", sub: "RDD엔 약함, § 5에서 다른 모양"),
  )
]

#v(14pt)

#block(breakable: false)[
  #image("figures/report/h22_rdd_appendix.png", width: 90%)
  #caption(
    "FIG-3.3",
    [자산취득형 3.42배가 신뢰구간 분리·압도 우세, 출연금형 1.10배는 점프 자체로는 통계 미달.],
  )[
    사업 형태별 12월 점프 *효과 분포 그림* (forest plot) — 점은 추정 배수, 가로 막대는 95% 신뢰구간.
    자산취득형 *3.42배*가 가장 강하고, 출연금형 1.10배는 점프 자체로는 통계 미달(회색).
    출연금형은 *12월 1일 직후의 한 시점에서 갑작스러운 점프*가 아닌 *연 단위 사이클*에서 강함 — § 5에서 재확인.
  ]
]

#v(14pt)

#block(breakable: false)[
  #table(
    columns: (0.4fr, 0.3fr, 0.5fr, 0.8fr, 1.3fr),
    table.header[사업 유형][n][12월 점프][점프 위치][시점 조정 메커니즘],
    [자산취득형], [99],    text(fill: warn, weight: "semibold")[× 3.42], [12월 1일 직후 이산], [공정률 마감 + 회계 마감 결합],
    [정상사업],   [1,175], [× 2.24],                                    [12월 전반],         [일반 행정 마감 + 다종 결합],
    [인건비형],   [129],   text(fill: soft)[× 1.12],                    [평탄],              [매월 균등 지급 — 조정 불가],
    [출연금형],   [154],   text(fill: soft)[× 1.10],                    [연 단위 누적],      [위탁기관 정산 일정, § 5에서 확인],
  )
  #caption(
    "TBL-3.1",
    [12월 점프는 사업 지출 구조에 따라 1.1배 — 3.4배의 *3배 격차*를 보인다.],
  )[
    사업 유형별 12월 점프 강도 종합. 자산취득형과 인건비형의 *3.1배 격차*는 같은 회계 압력이
    *시점 조정이 가능한 사업*에서만 발현됨을 보여준다. 출연금형의 약한 RDD 점프는 사이클 강도
    부재가 아니라 *모양 차이*(12월 1일 직후 *특정 시점 직후 단발성 급등* vs 연중 연속적 누적)다.
  ]
]

#v(14pt)

같은 회계 마감 압력에 *왜 사업 유형마다 다르게 반응하는가*? 자산취득형은 시설 공사·물품
구매처럼 *공정률 마감과 회계연도 마감이 겹치는* 구조에서 일하기 때문에, 12월 직전 며칠의
한계비용이 평소보다 낮다. 반대로 인건비형은 매월 균등 지급 외에 시점 조정 자체가 사실상
불가능하다. 출연금형은 *연 단위 사이클*에서는 강하지만 12월 1일 직후의 한 시점에서 갑작스러운 점프는 약하다 —
이 모양 차이는 § 5에서 다른 도구로 본다.

== 결과 2 #h2sub[12월에만 있는가, 다른 시점에도 있는가]

자연스럽게 따라오는 질문 — 회계 시점 압력이 *12월 단독*에 작동하는가, 다른 행정 마감에도
같은 모양으로 나타나는가? FIG-3.1의 11년 평균선을 다시 보면, 12월뿐 아니라 *3·6·9월*에도
부수 점프가 보인다.
이는 기획재정부 *분기별 집행관리제도*(분기마다 집행률을 점검·환수 조정)의 흔적이다.
12월 점프가 압도적으로 큰 이유는 *분기 마감 + 회계연도 마감 + 차년도 이월 차단*의 세 압력이
12월에 중첩되기 때문이다.

같은 RDD 추정을 *4개 분기말 cutoff × 4개 사업원형*으로 분해해보면, 사업원형별로 *어느
경계에서 점프가 작동하는가*가 갈라진다.

#v(8pt)

#image("figures/eda/fig_slide22_cutoff_bars.png", width: 95%)
#caption(
  "FIG-3.5",
  [archetype × 분기말 cutoff RDD — C1은 모든 cutoff에서 강한 점프, C2는 모든 cutoff에서 점프 부재.],
)[
  활동 단위 일평균 집행에 대한 RDD 점프 배율 ($e^beta$, log\_daily ~ T + C(year), bw=1, cluster
  SE by ACTV\_CD). *C1 자산취득형*은 모든 분기말에서 유의한 점프(6월 ×2.50, 9월 ×1.80, 12월
  ×3.42 — 3중 deadline 효과 누적). *C2 출연금형*은 4개 cutoff 모두 ns (점프 자체로는
  통계 미달) — RDD가 잡지 못하는 *연 단위 사이클*이 § 5에서 다른 도구로 드러난다.
  *C3 정상사업*은 12월 ×2.24 + 6월 ×1.44로 약한 점프 동반.
]

#v(10pt)

#callout(label: "관찰 — 행정 시점 압력은 단일 절단점이 아니다")[
  점프는 12월 단독이 아니라 *4개 분기말 cutoff에서 archetype별로 다른 강도*로 작동한다. 자산취득형은
  공정률 마감이 분기마다 누적되는 구조이기 때문에 6·9·12월 모두 강하고, 출연금형은 RDD가
  포착할 *이산적 점프* 자체를 만들지 않는다 — 모양이 다르다. 12월 RDD를 1차 검증 도구로
  보고하되, 본 표가 보여주는 *원형별 cutoff 응답성 차이*가 § 5의 사이클 분석으로 자연스럽게
  이어진다.
]

== 결과 3 #h2sub[연도별 점프 강도와 국제 비교 — 1.91배의 위치]

#image("figures/report/h22_rdd_yearly.png", width: 90%)
#caption(
  "FIG-3.4",
  [한국 1.91배는 11년 내내 안정 반복, 미국 5배에는 미달 — 제도 구조 차이의 흔적.],
)[
  연도별 12월 점프 (활동 중앙값 *log 일집행액*의 12월 − 11월 차분). 전체 추정계수 0.65 =
  *1.91배 점프*(주황 점선). 미국 연방조달 약 5배 (Liebman & Mahoney 2017, 보라 점선) 대비 위치 표시.
  국제 비교 견고성 검증(가상 주별 시나리오)은 *부록 C.10*에서.
]

#v(12pt)

미국 절대값(약 5배)에 못 미치는 이유는 단순한 *측정 단위 차이*가 아니다. 가상 시나리오로
12월 첫 주에 신호의 50%를 몰아주는 극단 가정을 두어도 한국 추정은 4.1배에 그쳐 미국 수치에
도달하지 않는다. 양국 차이는 *제도 구조 차이*(조달 유형, 회계 분권화 정도)에서 오는 본질적
요인으로 해석하는 것이 정직하다.

== 우연 가능성 점검 #h2sub[1,000회 무작위 섞기]

활동 단위로 11월·12월 라벨을 무작위 섞어 점프를 재추정한 *1,000회 순열 검정*에서, 실측 1.91배는
순열 분포 상한($p < 10^{-124}$)을 압도적으로 초과한다. 사업 유형별 분해의 순서(자산취득 3.42 >
정상 2.24 > 인건비 1.12 ≈ 출연금 1.10)도 우연 분포에서 동시에 나타날 확률이 무시할 수준이다.

== 한계 #h2sub[해석에 주의해야 할 점]

#block(breakable: false)[
  - *통제군 부재*: 한국 단일 정부 데이터로는 다년도 회계 도입 전후 비교가 어렵다. 점프 자체의
    *발현*은 분명하나, 제도 변경의 *효과 크기 추정*은 본 데이터의 범위 밖이다.
  - *12월 점프 ≠ 무조건 비정상*: 계약·정산 사이클의 정상 운영분도 12월에 일부 포함된다.
    본 분석은 11월 말 vs 12월 초 며칠 단위로 비교해 정상 사이클을 가능한 한 통제했으나,
    잔여 모호성은 남는다.
  - *자료 시간 단위의 한계*: 한국은 월 단위 공개라 *12월 첫째 주의 신호*가 12월 전체로 분산되어
    추정의 정확도가 낮아진다. 주별·일별 공개가 확대되면 점프 정밀도는 더 높아질 것 (§ 9 정책 시사점).
]

== 본 챕터 결론 #h2sub[같은 압력, 다른 응답]

#callout(label: "§ 3 정리", color: ink, bg: chip-bg)[
  12월 점프는 *전체 평균 1.91배*로 매년 안정적으로 반복되며, *사업 유형별로 1.1배 — 3.4배의
  극단 격차*가 있다. 같은 회계 압력이 사업 *지출 구조*에 따라 다르게 발현된다는 의미다.
  분기말(3·6·9월) 부수 점프는 회계 시점 압력이 *다중 경계*에서 작동하는 시스템임을 시사한다.

  *현장 풍경과의 일치*: § 1에서 인용한 "12월 되면 도로를 다시 깐다"는 풍경은, 데이터에서
  *자산취득형 사업군(C1, n=99 활동 풀링)의 3.42배 점프*로 흔적이 남는다. 시설 공사·자산 취득은 공정률 마감과 회계
  마감이 겹쳐 12월 직전 몰리는 구조이기 때문이다. 풍경과 데이터가 같은 쪽을 가리킨다.

  *다음 챕터로의 질문 사슬*: 본 챕터의 "사업 유형 라벨"은 사후 분류를 빌려 썼다. § 4는
  이 분류 자체가 *데이터에서 자동으로 출현*하는지 — 즉 행정 분류(14개 분야)와 데이터가 말하는
  단위(사업 유형) 중 어느 쪽이 진짜 분석 단위인지를 본다. § 2 관찰 3의 *집행률 천장 vs 결과
  지표 분산*은 이 분류 차이와 어떻게 맞물리는지가 § 4의 핵심 질문이다.

  본 패턴에 *학계가 붙인 이름*은 § 6.1에서 일괄 매칭한다.
]

= 측정 격차 #h1sub[집행률 천장 vs 결과 분산]

== 출발 질문 #h2sub[분야가 진짜 분석 단위인가]

§ 2 관찰 3에서 본 두 가지 — 집행률이 *95–100% 좁은 구간에 67% 압축*, 그러면서도 같은 부처의
결과 지표는 *-50% ~ +50% 광범위 분산* — 사이의 간극은 *분야별로 균질한가*?
한국 행정학·재정학 연구는 통상 *14개 분야*(사회복지·교육·국방·과학기술 …) 단위로 분석하며
분야 간 이질성을 결과 차이의 1차 설명으로 가정해 왔다. 본 분석이 § 3에서 발견한 사업 유형별
12월 점프 격차(자산취득형 C1 사업군 3.42 vs 인건비형 1.12)는 이 통상적 가정과 충돌한다.

본 챕터는 두 단계로 묻는다 — (1) *분야 라벨*이 사업 행동의 분산을 얼마나 설명하는가,
(2) 데이터가 *스스로 말하는* 사업 단위는 무엇이며 분야보다 강한가.

== 측정 절차 #h2sub[행정 분류 vs 데이터가 말하는 분류]

활동 1,557개를 *지출 구성*(인건비·자산취득·출연금·일반 비중 등 12개 피처)으로 표현한 뒤,
*분야 라벨로 묶었을 때*와 *데이터 기반 자동 묶음*의 행동 설명력을 비교한다. 자동 묶음은
12차원을 2차원으로 압축한 좌표 공간에서 *밀도가 높은 영역끼리* 묶는다.

#callout(label: "도구 명칭과 견고성 검증", color: ink, bg: chip-bg)[
  차원 축소 · 밀도 군집 · 고정효과 회귀의 정식 명칭과 절차는 부록 C.4–C.8에서. 자동 군집이
  알고리즘 우연이 아닌지에 대한 *위상 안정성 검증*(Mapper 32 노드 / 38 엣지, Persistent
  Homology Wasserstein-2 $p < 0.0001$)도 부록 C.6–C.7에 분리해 보고한다.
]

== 결과 1 #h2sub[분야 라벨로는 거의 설명되지 않는다]

전체 활동을 한 번에 회귀해서 *분야 라벨이 사업 행동 분산을 얼마나 설명하는가*를 본다 — 회귀
모형에 *분야 더미 변수*(고정효과)만 넣었을 때의 설명력 R²과, 거기에 *사업 유형 × 지출 진동*을
추가했을 때의 설명력을 비교한다. 분야 단독 R²은 거의 0, 사업 유형 추가 시 2.7배로 뛴다.

#v(10pt)

#image("figures/report/h8_panel.png", width: 100%)
#caption(
  "FIG-4.1",
  [분야 단독은 설명력 거의 0, 사업 유형을 추가하면 R²가 2.7배로 — 분야 라벨은 행동을 거의 설명하지 못한다.],
)[
  *분야 라벨이 진짜 분석 단위인지* 검정. 좌: 분야 더미 변수만 넣은 모형의 R²(0.014). 우: 사업 유형 ×
  지출 진동을 추가한 모형의 R²(0.038, 증분 +0.025). 어느 분야인지는 사업 행동을 거의 결정하지
  못하고, *어떤 형태의 사업인가*(인건비 집중·자산취득·출연금 위탁·일반)가 진짜 단위다.
]

#v(14pt)

#block(breakable: false)[
  #grid(
    columns: (1fr, 1fr, 1fr),
    column-gutter: 12pt,
    kpi("분야만 사용", "R² ≈ 0", sub: "행정 분류는 거의 설명력 없음"),
    kpi("사업 유형 추가", "+0.025", sub: "전체 설명력 2.7배 증가"),
    kpi("자동 도출 유형 수", "4 개", sub: "1,557 활동에서 안정 발견"),
  )
]

#pagebreak()

== 결과 2 #h2sub[데이터가 말하는 4개의 사업 형태]

12차원을 2차원 좌표로 압축한 뒤 밀도 군집을 적용하면 *4개의 안정 군집*이 나타난다. 각 군집의 z-score 프로파일이
*행정 실무에서 직관적으로 인지 가능한 사업 형태*와 정확히 일치한다.

#v(0pt)

#image("figures/report/h3_umap.png", width: 90%)
#caption(
  "FIG-4.2",
  [같은 분야 안에서도 사업 형태가 공간상 분리되고, 다른 분야의 같은 형태가 가까이 모인다.],
)[
  활동들을 2차원 좌표로 표현 (1,557 활동 × 12 피처를 2차원 압축). 색상은 자동 군집 4개 — *C0 인건비형*(파랑),
  *C1 자산취득형*(빨강), *C2 출연금형*(주황), *C3 정상사업*(회색). 분야가 아닌 사업 형태가
  진짜 단위라는 시각적 증거.
]

#v(14pt)

#block(breakable: false)[
  #table(
    columns: (1fr, 0.5fr, 1.7fr, 1.1fr),
    table.header[사업 형태][n][지출 프로파일 특징][§ 3 12월 점프],
    [C0 인건비형], [129],   [인건비 비중 +3.07σ],                            text(fill: soft)[× 1.12 (평탄)],
    [C1 자산취득형], [99],  [자산취득 비중 +3.28σ],                          text(fill: warn, weight: "semibold")[× 3.42 (최강)],
    [C2 출연금형], [154],   [출연금 비중 +2.89σ, 12월 진동 +0.88σ],          text(fill: soft)[× 1.10 (RDD 약함)],
    [C3 정상사업], [1,175], [평균 부근 (베이스라인)],                        [× 2.24 (기준값)],
  )
  #caption(
    "TBL-4.1",
    [4개 사업 형태는 분야와 무관하게 각자 다른 12월 점프 강도를 갖는다.],
  )[
    4개 자동 군집의 프로파일과 § 3 12월 점프 강도. *분야와 무관하게* 같은 사업 형태는 비슷한 점프
    행동을 보인다. 출연금형은 RDD 점프는 약하지만 § 5에서 *연 단위 사이클*에 가장 강한 결속을 보인다.
  ]
]

#v(10pt)

선행 분석과의 비교가 가능하다. 김명규 외(2022)는 같은 dBrain 패널에서 *상반기 집행형 ·
하반기 집행형 · 연중 균등집행형 · 일회성 집행형*이라는 *4개의 집행 패턴*을 사전 정의로
분류한 바 있다. 본 분석의 4군집은 *동일한 수의 군집*을 데이터로부터 사후 발견했으나,
*분류 축이 다르다*. FIS 2022는 *언제* 집행하는가(월별 분포)를 기준으로 묶었고, 본 분석은
*무엇*에 집행하는가(인건비·자산취득·출연금·기타 지출 구성)를 기준으로 묶었다. 두 축은
보완적이다 — 같은 *하반기 집행형* 안에 인프라성 자산취득형(12월 절벽 점프)과 출연금형(연 사이클,
분기말 cycle 서브셋 포함)이 함께 포함되어 있고, RDD 점프 강도가 둘에서 극단으로 갈린다(× 3.42 vs × 1.10).
지출 구성을 분류 축으로 삼을 때 시점 분포의 이질성이 사라지지 않고 더 선명해진다는 것이
본 챕터의 발견이다.

== 결과 3 #h2sub[집행률과 결과 지표 사이의 연결 통로]

§ 2 관찰 3의 간극(집행률 천장 vs 결과 분산)이 *어떤 사업 형태에서 가장 크게 발현되는지*를
14분야에서 따로 본다. 가설은 단순하다 — 출연금 비중이 높은 분야일수록 시점 조정 압력이 강하고,
그 압력이 결과 지표에 흔적을 남긴다면, *분야별로 신호 강도*가 달라야 한다.

#v(10pt)

#block(breakable: false)[
  #table(
    columns: (0.5fr, 0.2fr, 0.8fr, 1.8fr),
    table.header[분야][n][신호 강도][해석],
    [농림수산], [충분], text(fill: pos, weight: "semibold")[안정적인 음 신호], [출연금 비중 → 12월 진동 → 농가소득\ — *14분야 중 유일하게* 통계적으로 안정],
    [사회복지], [6],   [방향성 있으나 약함], [연결 통로 강도은 분야 중 양호하나 표본 6개로 통계 미달],
    [환경],    [4],   text(fill: soft)[추정 불가], [표본 4개로 신호/잡음 분리 자체가 불가능],
    [그 외 11분야], [—], text(fill: soft)[신호 없음], [추정값 0 근처, 일관된 패턴 없음],
  )
  #caption(
    "TBL-4.2",
    [*14분야 중 농림수산만 안정적인 음 신호* — 다른 분야는 표본 부족 또는 신호 없음.],
  )[
    14분야 평균만 보면 신호가 통계적으로 흔들림(평균 효과 ≈ 0)지만, 분야별로 풀면 농림수산 단독으로 강한 음
    신호. 정식 검정 통계값(Sobel z·부트스트랩 신뢰구간)과 통계 도구는 *부록 C.11* 참조.
    사회복지·환경의 추정 불가는 *분야별 시계열 길이 한계*에서 온다.
  ]
]

#v(14pt)

이 결과의 의미는 두 가지다. 첫째, *분야 평균은 신호를 가린다* — 1개 분야에서 강한 효과가
13개 분야의 약한 신호에 희석된다. 둘째, *측정 격차의 분포가 사업 형태와 결합한다* —
출연금형 사업이 많은 분야에서 시점 조정이 결과 지표에 더 큰 흔적을 남긴다. § 5에서 이
출연금형 사이클을 시간 축에서 직접 본다.

== 한계 #h2sub[해석에 주의해야 할 점]

#block(breakable: false)[
  - *분야별 표본 크기 제약*: 사회복지(n=6)·환경(n=4) 등은 결과 지표 연 단위 시계열 길이가
    매개 검정에 부족하다. 향후 10년 이상 분야 시계열 확장이 검정력 확보의 핵심 과제다.
  - *결과 지표 자체의 잡음*: 사회 결과 지표는 재정 외 요인(경기·인구·국제 가격)에 크게
    좌우된다. 거시 경기(소비자물가지수, CPI)를 통계적으로 제거한 뒤에도 핵심 신호가 유지되는지에
    대한 보강은 § 5와 부록 C.12에서 다룬다.
  - *상관 기반 매개*: 본 추정은 상관 구조에 의존한다. 인과까지는 단일 정부 데이터로 도달하지
    못한다. 도구 변수·정책 자연 실험 결합은 후속 연구 과제다 (§ 10).
  - *측정 격차의 역방향 사례 — 우연히 결과가 좋아지는 분야*: 사회복지에서는 12월 집중 집행
    강도가 *클수록* 빈곤 격차가 *완화*되는 방향(상관 -0.86, 거시 경기 통제 후 강화)으로
    관찰된다. 측정 격차가 항상 결과의 *희생*으로 발현되지는 않는다는 사례 — 12월 집중 분배가
    빈곤층에 자원이 자동 도달하는 메커니즘과 결합되었을 가능성. 자세한 분해는 § 7 측도 의존성
    검증 + 부록 C.11에서.
]

#v(14pt)

#callout(label: "H3 클러스터링 한계 — 정직하게 짚어두면", color: warn, bg: ghost)[
  클러스터링이 학습한 입력은 *편성목 구성비 + FFT 요약 + HHI + 규모* 12개 스칼라 피처다.
  12개월 시점 시퀀스를 그대로 임베딩한 것이 아니다 — 즉 군집은 *편성목 유형*을 분리할 뿐,
  *월별 집행 패턴* 자체를 정의하지는 않는다.

  들여다보면 두 공간의 실루엣 점수가 이 차이를 숫자로 보여준다. 편성목 피처 공간에서는
  silhouette = 0.240으로 적절한 분리가 확인되지만, 같은 라벨을 12개월 시점 벡터 공간에
  투영하면 silhouette = −0.179로 음수다 — 클러스터 라벨이 월별 비중 분산을 설명하면
  ANOVA R²는 평균 0.065(6.5%)에 그친다.

  따라서 C0–C3 명칭은 *편성목 그룹*으로 읽는 것이 맞다. 월별 패턴은 그룹 평균을 사후에
  서술한 것이지 군집이 처음부터 최적화한 목표가 아니다.

  다른 각도로 보면, C2 출연금형은 내부가 bimodal하다 — 연초 집중형(한국산업인력공단출연 등)과
  분기말 cycle형(원자력연구개발사업 등)이 한 그룹에 묶여 있으며, C2 평균 cycle_ratio = 0.42는
  연 주기가 우세한 서브셋을 반영한다. Slide 19에서 cycle 대표 사례로 든 원자력연구개발사업은
  그 cycle 서브셋을 대변하며 C2 전체를 대표하지는 않는다.

  C3 정상사업(n = 1,175, 전체 75.5%)은 그룹 크기가 가장 큰 잔류 그룹으로 내부 분산이 가장 크다.
  "정상사업"이라는 명칭은 *시점 압력이 약한 비교군*이라는 의미로 사용할 뿐, 행동이 균질하다는
  뜻이 아니다.

  마지막으로, RDD × 3.42(자산취득형) 같은 추정치는 *편성목 그룹 단위 풀링*이다.
  본 분석의 정량 결과는 모두 이 한계 안에서 해석한다.
]

== 본 챕터 결론 #h2sub[분야는 분류 라벨, 사업 형태가 단위]

#callout(label: "§ 4 정리", color: ink, bg: chip-bg)[
  *분야 라벨은 사업 행동의 분산을 거의 설명하지 못한다* (분야 FE 단독 ΔR² ≈ 0). 데이터가 스스로
  말하는 *4개 사업 형태* — 인건비·자산취득·출연금·정상 — 가 § 3 12월 점프 격차와 맞물리며,
  연결 통로는 *농림수산에서 유일하게 안정적으로* 식별된다.

  관찰 3의 측정 격차(집행률 압축 vs 결과 분산)는 *분야 평균*이 아닌 *사업 형태 분포*의 함수다.
  다음 챕터(§ 5)는 출연금형 사업을 *시간 축*에서 들여다보며 § 2 관찰 2(일률 정산 패턴)에 답한다.

  본 패턴에 *학계가 붙인 이름*은 § 6.2에서 일괄 매칭한다.
]

= 출연기관 정산 압력 #h1sub[주기적 패턴의 정체]

== 출발 질문 #h2sub[이 사이클은 시간이 갈수록 강해지는가]

§ 2 관찰 2에서 본 것 — 일부 사업은 *평소엔 0에 가깝다 특정 시점에 일제히 정산*되고, 출연금 비중은
분야별 *80배 격차*(국방 0.2% — 과학기술 36.2%) — 의 다음 질문은 셋이다.

- 일률 정산 패턴은 *어떤 주기*가 우세한가 (분기·반기·연)?
- 활동들이 *서로 동시에* 같은 시점에 피크하는가, 각자 다른 시점인가?
- 이 패턴은 *시간이 갈수록 강해지는가*, 안정적인가?

§ 3에서 본 출연금형의 약한 12월 점프(1.10배)는 사이클 *부재*가 아니라 *모양 차이*다.
12월 직후 *특정 시점 직후 단발성 급등*이 아닌 *연 단위 누적*이라면, 시간을 다르게 자르는 도구로 봤을 때 모양이 달라야 한다.

*왜 이 질문이 중요한가* — 사이클이 *시간이 갈수록 강해진다*면, 단순 평균값(11년 평균)은
*최신 강도를 희석*시킨다. 정책 시점 가중치가 *최근 자료에 더 실려야* 한다는 함의가 다르다.
또한 *진행형 패턴*인지 *안정 상태 패턴*인지에 따라 개입의 시급성이 달라진다.

== 측정 절차 #h2sub[같은 시계열을 다른 렌즈로 본다]

본 챕터는 세 가지 *서로 다른 렌즈*를 사용한다. 같은 활동의 월 시계열을 각자 다른 방식으로
잘라 본 모양을 비교한다.

- *주기 진폭* (PSD k=1): 활동 시계열 안에 *어떤 주기(12개월·6개월·…)가 얼마나 강한지*를
  분리해 측정. k=1은 12개월 주기 진폭이다.
- *동시 피크 정도* (phase coherence): 같은 사업 유형의 활동들이 *같은 달*에 피크하는가, 각자
  다른 달인가를 0–1 값으로 정량화. 1에 가까울수록 일제히 동기화.
- *시간 동학* (wavelet): *주기 진폭이 11년간 어떻게 변화*했는지를 시간 축에서 추적.
  2015–2017 평균 vs 2023–2025 평균의 변화율을 본다.

세 렌즈가 같은 사업 유형을 가리키면 그 발견이 *견고*하고, 갈라지면 그 지점이 *자기 비판의
출발점*이다(§ 7에서 도구 간 일관성 점검).

#callout(label: "본 챕터에서 사용하는 도구 명칭", color: ink, bg: chip-bg)[
  - *주기 진폭* (영문 약어 PSD, Power Spectral Density): 시계열을 주파수 영역으로 분해해
    각 주기(12·6·4개월…)가 *얼마나 강한지*를 수치화. k=1은 12개월 주기에 해당.
  - *동시 피크 정도* (phase coherence): 활동들이 *같은 달*에 일제히 피크할수록 1에 가깝고,
    각자 흩어져 피크할수록 0에 가까운 0–1 지표.
  - *시간 동학* (wavelet, 정식 명칭 Continuous Wavelet Transform): 주기 진폭을 *시간 축*에서
    추적하는 도구. 진폭이 어느 시기에 강해졌는지 확인 가능.
  - 정식 수식과 절차는 부록 C.1·D.1–D.4.
]

== 결과 1 #h2sub[연 사이클 진폭과 동시성에서 압도적 우세]

세 측도(PSD·phase coherence·wavelet) 모두 *출연금형이 다른 사업 유형의 2배–7배*로 강하다.

#v(10pt)

#image("figures/report/h27_psd.png", width: 95%)
#caption(
  "FIG-5.1",
  [출연금형 PSD k=1 진폭 0.332 — 다른 사업 유형 0.097–0.172의 *2–3.4배*.],
)[
  사업 유형별 PSD (Power Spectral Density). 12개월 주기 위치에서 출연금형(주황)의 봉우리가 압도적으로
  높다. 36개월(3년) 위치에는 다른 사업 유형도 부수 봉우리가 있으나, 12개월 위치에서는 출연금형 단독 우세다.
]

#v(10pt)

#image("figures/report/h27_coherence.png", width: 90%)
#caption(
  "FIG-5.2",
  [출연금형 phase coherence 0.54 — 활동들이 같은 달에 일제히 피크 (다른 유형의 *4–7배*).],
)[
  사업 유형별 phase coherence heatmap. 활동들이 *서로 다른 시점에* 흩어져 피크하는 게 아니라
  *같은 달에 일제히* 정산된다는 직접 증거 — § 2 관찰 2의 "평소엔 0, 특정 시점에 일제히 정산"
  모양이 데이터에서 정량 확인된다.
]

#v(14pt)

#block(breakable: false)[
  #grid(
    columns: (1fr, 1fr, 1fr),
    column-gutter: 12pt,
    kpi("PSD k=1 진폭", "0.332", sub: "다른 유형 0.097–0.172의 2–3.4배"),
    kpi("Phase coherence", "0.54", sub: "다른 유형 0.08–0.13의 4–7배"),
    kpi("§ 3 12월 RDD", "× 1.10", sub: "점프 약함 — 모양 차이"),
  )
]

#v(14pt)

세 측도의 의미는 다르다. PSD는 *얼마나 강한 연 주기*가 있는지, coherence는 *활동들이 같은 달에
모이는지*, RDD는 *12월 1일 직후의 한 시점에서 갑작스러운 점프*가 있는지를 본다. 출연금형은 *PSD·coherence는 압도
우세, RDD는 약함* — 즉 12월 1일 직후의 *한 차례 급등*이 아니라 *연중 위탁기관 정산 일정에 따른
다회 분산 + 12월 누적* 모양이다.

#pagebreak()

== 결과 2 #h2sub[시간 동학 — 연 사이클 진폭의 5.5배 강화]

같은 시계열의 *시간이 흐르며 변화*하는 모양은 어떤가? 2015–2017 평균과 2023–2025 평균의
12개월 cycle 진폭을 사업 유형별로 비교하면 *극단적 비대칭*이 드러난다.

#v(10pt)

#image("figures/report/h28_evolution.png", width: 90%)
#caption(
  "FIG-5.3",
  [출연금형 +554% 강화 vs 인건비형 −0.8%(통제) — 극단 비대칭의 시간 진화.],
)[
  사업 유형별 12개월 cycle 진폭의 *시간 진화* (2015–2025). 출연금형(주황)이 *+554% 강화*,
  정상사업 +317%, 자산취득형 +175%. *인건비형은 −0.8%로 변화 없음* — 매월 균등 지급이라
  시점 조정 자체가 불가능한 통제 사례. 2020년경 출연금형 곡선의 *급격 점프*는 코로나 확장재정 시기.
]

#v(14pt)

#block(breakable: false)[
  #table(
    columns: (1fr, 1fr, 1fr, 1fr),
    table.header[사업 유형][2015–17 평균][2023–25 평균][변화율],
    [인건비형 (통제)], [0.007], [0.007], text(fill: soft)[−0.8% (변화 없음)],
    [자산취득형], [0.055], [0.150], [+174.7%],
    [정상사업],   [0.057], [0.237], [+316.7%],
    [출연금형],   [0.201], [1.315], text(fill: warn, weight: "semibold")[+553.6%],
  )
  #caption(
    "TBL-5.1",
    [출연금형 사이클 진폭 11년간 *5.5배 강화* — 인건비형 0% 통제와의 비대칭.],
  )[
    사업 유형별 12개월 cycle 진폭의 11년 변화. *인건비형 0% 통제*는 도구가 noise를 잡아내지 않는다는
    도구 자체의 신뢰성 — 진폭이 진짜 증가한 유형에서만 신호가 발현된다. 출연금형의 5.5배 강화는 본 분석의
    핵심 발견 중 하나다.
  ]
]

== 한계 #h2sub[해석에 주의해야 할 점]

#block(breakable: false)[
  - *주기적 정산 ≠ 모두 비정상*: 분기 정산 규정 등 계약상 정상 운영분도 포함된다. 본 분석은
    *유형 간 격차*(출연금 0.332 vs 다른 0.097–0.172)와 *시간 변화*(+554%)를 핵심 신호로 본다.
  - *측정 도구 의존성*: 사회복지 분야의 음 상관은 한 측도에서 강하나 다른 측도에서 소멸한다.
    본 분석은 *여러 도구의 부분적 일치*에 의존하며 단일 측도에 결론을 귀속하지 않는다 (§ 7 측도
    의존성 검증).
  - *모기관-출연기관 인과 식별 불가*: 일률 정산 패턴의 *원인*은 모기관 정산 사이클·위탁 계약
    구조 등 거버넌스 데이터 결합이 필요하며, 본 데이터 범위 밖이다 (§ 10).
  - *+554% 수치의 시기 합성 — 해석 단서*: 대표 수치는 *추세적 강화 + 코로나 충격 상승의 합성*이다.
    출연금형 시계열을 세 구간으로 나누면 *코로나 이전(2015–18) 평균 0.265 → 코로나 시기
    (2019–21) 평균 1.049 (+295.8% 전환) → 코로나 이후(2022–25) 평균 1.375 (정체 구간)*. 즉
    +554%의 상당 부분은 코로나 확장재정 시기의 *운영 흐름의 전환*에서 기인하나, 코로나 이후에도
    *사전 수준으로 회귀하지 않았다*는 점이 "진행형" 해석의 근거다. 시기 분할 표는 부록 D.4.
]

== 본 챕터 결론 #h2sub[연 사이클은 출연금형 단독, 시간이 갈수록 강해진다]

#callout(label: "§ 5 정리", color: ink, bg: chip-bg)[
  출연금형 사업은 *연 사이클 진폭(PSD 0.332)·동시 피크(coherence 0.54) 모두 다른 유형의 2–7배*로
  압도적 우세이며, *2015–17 → 2023–25 11년간 5.5배 강화*되었다. § 3의 12월 점프가 약했던 것은
  사이클 부재가 아니라 *모양 차이* — 12월 직후 단발성 급등이 아닌 연중 분산 + 누적이었다.

  *현장 풍경과의 일치*: § 1에서 인용한 "출연기관은 어차피 모기관이 메워준다"는 풍경은,
  데이터에서 *연 사이클 안에서 활동들이 동시에 피크하는 모양*(coherence 0.54)으로 흔적이 남는다.
  자율적으로 집행 계획을 짜는 환경에서는 활동들이 *서로 다른 시점*에 흩어져야 자연스럽다 —
  같은 달에 일제히 모이는 것은 *외부 정산 일정*이 기관 내부 의사결정보다 우위에 있다는 단서다.

  *인건비형 통제*: −0.8%(시점 조정 자체가 불가능한 사업)와의 극단 비대칭은 도구가 진짜 동적
  신호만 잡아낸다는 도구 자체의 신뢰성이다. 도구가 noise를 잡으면 인건비형도 양의 변화율을 보여야 한다.

  *세 발견의 맞물림*: § 3 (12월 점프) · § 4 (사업 형태 분류) · § 5 (출연금형 사이클)은 *서로
  독립적 우연으로 보기 어렵다*. 자산취득형의 12월 RDD 우세 + 출연금형의 연 사이클 우세 +
  인건비형의 양쪽 모두 평탄 — 사업의 *지출 구조*가 점프와 사이클을 모두 결정한다는 패턴이다.
  *학계가 이 세 패턴에 붙여 온 이름*은 § 6에서, *세 발견이 측정 도구를 바꿔도 같이 가리키는지*는
  § 7에서 일괄 점검한다.
]

= 학계는 30년째 이름을 붙여왔다

#chip("placeholder", fg: warn, bg: rgb("#fef3c7"))

§3·§4·§5 발견과 학술 이론(*굿하트-캠벨 법칙* · *다업무 계약 이론* · *연성 예산 제약*)의 통합 매칭 — *후속 작업*.
한눈에 매칭표 + 각 이론 frame이 발견과 어떻게 맞물리는지 풀이.

= 교차 검증 #h1sub[도구 간 결과 차이가 의미하는 것]

== 출발 질문 #h2sub[한 도구의 결론을 다른 도구도 같이 가리키는가]

본 분석의 § 3 (12월 RDD) · § 4 (사업 형태 분류) · § 5 (출연금형 사이클)은 *서로 다른 측정 도구*에
기반한다. § 3은 11월 vs 12월 일평균 *특정 시점 전후 비교*, § 5는 *주파수 분해 + 시간-주파수 분해*다.
같은 시계열을 *다른 렌즈*로 보았을 때 결론이 일관되는가, 어디서 갈라지는가가 본 챕터의 질문이다.

본 분석은 § 5의 핵심 측정인 *연 사이클 진폭*을 세 가지 독립 도구로 *교차 검증*한다.

- *주파수 영역 분해* (영문 약어 FFT, 정식 명칭 Fast Fourier Transform): 시계열에서 12개월 주기
  진폭의 *상대 비중*을 뽑아낸다. § 5의 PSD가 같은 계열의 측도다.
- *시간 영역 분해* (STL, Seasonal-Trend decomposition using Loess): 시계열을 *추세 + 계절성 +
  잔차*로 더해서 푸는 분해한 뒤 *계절성 강도*를 측정.
- *신경망 분해* (NeuralProphet, 줄여서 NP): 추세의 *전환점*(changepoint)을 자동으로 보정한 뒤
  연 주기 진폭을 적합한다. 추세적 증가가 큰 시계열에서 STL이 신호를 흡수하는 한계를 우회.

셋이 같은 결론을 가리키면 견고하고, 갈라지면 그 지점이 *자기 비판의 출발점*이다.

#pagebreak()

== 결과 1 #h2sub[세 도구는 같은 신호의 다른 차원]

활동-연도 패널(n=1,051)에 세 측도를 산출한 뒤 상호 상관을 계산하면 *셋 모두 0에 가깝다*.
즉 세 도구는 *서로 다른 신호*를 보는 것이 아니라, *같은 신호의 다른 면*을 본다.

#v(10pt)

#image("figures/report/np_correlation.png", width: 100%)
#caption(
  "FIG-7.1",
  [세 측도(FFT·STL·NP)의 상호 상관 ≈ 0 — 같은 신호의 *서로 독립된 시각*임을 직접 입증.],
)[
  활동-연도 패널 n=1,051. FFT-STL 상관 −0.130, FFT-NP 상관 −0.039, STL-NP 상관 −0.018.
  중복 측정이 아니라 같은 신호의 *서로 다른 차원*을 본다 — FFT는 주파수 영역의 *진폭 비중*,
  STL은 시간 영역의 *추세와 나머지로 가르기*, NP는 전환점 보정 후 *더해서 푸는 분해*.
]

#v(14pt)

세 도구가 서로 독립한다는 사실은 *약점이 아니라 강점*이다. 한 도구만 사용하면 그 도구가 잡지 못하는
신호 차원이 사각지대가 된다. 세 도구의 *공통 신호*만 핵심 결론으로 채택하면, 단일 도구의 측정
편향에서 자유로워진다.

#pagebreak()

== 결과 2 #h2sub[14분야 결과 지표 상관 — 세 도구 비교]

§ 4의 연결 통로(*출연금 비중 → 시점 조정 → 결과 지표*)를 14분야에서 세 도구로 따로 추정한다.
어떤 분야가 *세 도구 모두에서 일관 신호*를 보이는지, 어떤 분야에서 *측도에 따라 부호가 갈리는지*를
한 화면에서 본다.

#v(10pt)

#image("figures/report/np_3way_outcome.png", width: 100%)
#caption(
  "FIG-7.2",
  [보건·통신은 세 도구 모두 음 신호로 일관, *사회복지는 도구에 따라 부호가 갈린다*.],
)[
  14분야 결과지표 1차 차분 상관을 세 측도로 재산출. *세 도구 일관 음 신호*: 보건(기대수명 ·
  FFT −0.55 / STL +0.20 / NP −0.71)·통신(광대역 보급률 · FFT −0.15 / STL +0.05 / NP −0.75).
  *부호 반전 분야*: 사회복지(순자산 지니계수 · FFT +0.03 / STL +0.00 / NP −0.24).
  NP가 FFT가 놓친 통신 분야의 신호를 추가로 식별한다.
]

#v(14pt)

#block(breakable: false)[
  #grid(
    columns: (1fr, 1fr, 1fr),
    column-gutter: 12pt,
    kpi("일관 신호 분야", "2 개", sub: "보건·통신 \n (세 도구 모두 음)"),
    kpi("부호 반전 분야", "1 개", sub: "사회복지 \n — 측도 의존성 명시 필요"),
    kpi("NP 추가 식별", "통신", sub: "FFT 0에 가까운 분야의 음 신호 회복"),
  )
]

== 결과 3 #h2sub[사회복지 부호 반전 — 어느 도구가 진실인가]

§ 5의 *fortuitous alignment* 단서(12월 집중 집행이 클수록 빈곤 격차 완화 방향)는 측도에 따라
다르게 나타난다. 본 분석은 *단일 측도에 결론을 귀속하지 않고* 세 도구의 부분 합의를 명시한다.

#v(10pt)

#block(breakable: false)[
  #table(
    columns: (1.1fr, 0.5fr, 0.5fr, 0.3fr, 1.6fr),
    table.header[측도][상관 r][p][n][해석],
    [FFT 12개월 진폭],      [+0.03], [0.92], [10], [신호 없음\ — 단순 진폭으로는 보이지 않음],
    [STL 계절성 강도],      [+0.00], [0.99], [10], [추세 흡수 가능성\ — *추세적 증가*에 가려짐],
    [NP 연 주기 진폭],      text(fill: warn, weight: "semibold")[−0.24], [0.55], [8], [*음 신호 부분 회복* \ — 전환점 명시 모델링],
    [활동-단위 FFT (§ 5 부록)], [−0.76], [0.04], [—], [활동 단위로 분해 시 강한 음 신호],
    [물가 통제 후 (§ 5 부록)],  [−0.86], [0.01], [—], [거시 경기 통제 후 *신호 강화*],
  )
  #caption(
    "TBL-7.1",
    [사회복지 fortuitous alignment의 *측도 의존성* 정리.],
  )[
    분야-단위 집계 측도(FFT·STL)에서는 신호가 약하거나 부재하나, *활동-단위 NP·CPI 통제 측도*에서는
    음 신호가 회복·강화된다. 단일 측도 결론보다 *여러 도구의 부분적 일치*가 더 정직한 보고 방식이다.
  ]
]

#v(14pt)

이 패턴이 시사하는 두 가지 가능성:
- *(a) STL이 추세를 흡수했을 가능성*: 사회복지 예산의 *지속 증가 추세*가 STL의 추세 항에 흡수되어
  진짜 12월 집중 신호가 잔차로 남지 않음. NP는 *추세의 전환점*을 명시적으로 모델에 포함하므로
  이 흡수를 우회한다.
- *(b) FFT가 가짜 주기성을 만들었을 가능성*: 활동-단위로 풀면 강한 음 신호이지만 분야 단위로 모으면
  서로 다른 활동의 신호가 상쇄될 수 있음.

본 분석은 둘을 *완전 식별하지 못한다*는 점을 명시하며, FFT·NP의 부분 합의(음 신호) + 거시
경기 통제 후 *신호 강화*를 근거로 *우연히 결과가 좋아지는 분야* 가설을 지지하나 *확정하지는 않는다*고 보고한다.

== 한계 #h2sub[교차 검증의 본질적 제약]

#block(breakable: false)[
  - *세 도구는 같은 데이터에서 파생*: 같은 월 시계열을 세 가지 방식으로 분해한 것이므로,
    *측정 도구 다양성*은 확보되나 *데이터 다양성*은 확보되지 않는다. 동일 데이터의 한계
    (월 단위 자료 시간 단위, 11년 길이)는 세 도구 모두에 공통이다.
  - *세 도구 합의가 진리 보장은 아니다*: 셋 다 같은 방향을 가리켜도 *동일한 편향*을 공유할 수
    있다. 예: 11년의 *추세적 변동*은 세 도구가 모두 흡수할 수 있다 — 그래서 § 5의 +554%는
    추세적 강화와 COVID 충격의 합성으로 신중하게 해석한다.
  - *표본 크기 제약*: 14분야 중 표본 6개 이하인 분야(사회복지·환경 등)는 셋 어느 도구로도
    안정 추정이 어렵다. 분야 단위 결론은 *2개 일관 신호 분야*(보건·통신)에 한정한다.
  - *NeuralProphet 적합 비용*: 200개 활동 *무작위 표본* 기반으로 11년 전체 활동을 일반화한다.
    표본 확장은 후속 과제(§ 10).
]

== 본 챕터 결론 #h2sub[트라이앵귤레이션은 만장일치가 아닌 상호 보완]

#callout(label: "§ 7 정리", color: ink, bg: chip-bg)[
  세 측정 도구는 *같은 신호의 서로 독립된 시각*이며, 본 분석의 핵심 결론은 *여러 도구가 일관되게
  가리키는 분야·유형 패턴*에 의존한다. 보건·통신은 세 도구 모두에서 음 신호로 일관 — 견고한
  발견. 사회복지는 측도에 따라 부호가 갈림 — *자기 비판의 출발점*이며 단일 측도에 결론을
  귀속하지 않는다.

  본 분석의 *트라이앵귤레이션*(triangulation, 셋 이상의 독립 도구로 같은 신호를 가리키는지 확인하는
  검증 방식)은 "셋이 같은 답을 줘야 결론이 성립"이 아니라 "*셋이 어디서 합의하고 어디서 갈리는지가
  분석의 일부*"라는 *구성*이다.

  *§ 8 산출물에의 함의*: 부처×결과 4분면 점검 우선순위는 *세 도구 일관 신호 분야*를 우선
  순위 상위로, *측도 갈림 분야*는 추가 데이터 확보 후 재검토 큐로 분리한다. 즉 § 7의
  자기 비판은 § 8 산출물의 *신뢰도 등급 부여*에 직접 반영된다.
]

= 산출물 #h1sub[현장에서 쓸 수 있는 것]

#chip("placeholder", fg: warn, bg: rgb("#fef3c7"))

부처×결과변수 4분면 점검 우선순위 + 점검 우선 활동 Top-50 + 자동 점검 알고리즘.

= 정책 시사점

#chip("placeholder", fg: warn, bg: rgb("#fef3c7"))

다년도 회계 도입 확대 · 출연기관 정산 분산 · 경영평가 지표 개선 · 데이터 인프라 개선 · 자동 flagging.

= 한계와 향후 과제

#chip("placeholder", fg: warn, bg: rgb("#fef3c7"))

통제군 부재 · 결과 지표 잡음 · 자료 시간 단위 한계 · 출연기관 거버넌스 데이터 부재.

= 부록

#chip("placeholder", fg: warn, bg: rgb("#fef3c7"))

A 용어 사전 · B 데이터 출처와 라이선스 · C 방법론 디테일 · D 재현 코드 안내 · E 참고자료 *(학술 문헌 + 선행 공식 진단 + 언론 보도 인용)*.
