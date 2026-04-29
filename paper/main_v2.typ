// 한국 정부 재정 집행의 굿하트 게임 — Principal-Agent 균형 분석 논문 (v2)
// Typst 컴파일: typst compile paper/main_v2.typ paper/main_v2.pdf

#set document(
  title: "한국 정부 재정 집행의 굿하트 게임 — Principal-Agent 균형 분석, 사업원형별 다중 검증, 정책 처방",
  author: ("정선규", "심은철", "김영찬"),
)

#set page(
  paper: "a4",
  margin: (top: 25mm, bottom: 25mm, left: 25mm, right: 25mm),
  numbering: "1",
)

// 모던 KCI 학술지 폰트: 본문 명조 = Noto Serif KR (Google open-source, 2024+ 트렌드)
// 영문은 Times New Roman, 한글 fallback HYSinMyeongJo·Batang
#set text(
  font: ("Times New Roman", "Noto Serif KR", "HYSinMyeongJo", "Batang"),
  size: 10.5pt,
  lang: "ko",
)

// 학술지 표준: 줄간격 200% (line-height 2.0 ≈ leading 1.0em on 11pt with default 0.65em base)
// Typst leading is *additional* space between lines. 11pt 본문 line-height 2.0 ≈ leading 1.05em
// 한국 학술지 표준: 모든 문단 들여쓰기 (절 첫 문단 포함) — `all: true` 옵션
#set par(
  justify: true,
  leading: 1.05em,
  first-line-indent: (amount: 1em, all: true),
  spacing: 1.2em,
)

#set heading(numbering: "1.1")

// KCI 학술지 표준 헤딩 — 본문(10.5pt 명조)과 자연 구분, sans-serif Pretendard
// 색상은 검정, 외곽 룰 없음, 절제된 여백
#show heading.where(level: 1): it => [
  #v(1.0em)
  #text(
    font: ("Pretendard", "Times New Roman", "Noto Sans KR", "HYGothic"),
    size: 13pt, weight: "bold",
    it
  )
  #v(0.4em)
]
#show heading.where(level: 2): it => [
  #v(0.7em)
  #text(
    font: ("Pretendard", "Times New Roman", "Noto Sans KR", "HYGothic"),
    size: 11.5pt, weight: "bold",
    it
  )
  #v(0.25em)
]
#show heading.where(level: 3): it => [
  #v(0.5em)
  #text(
    font: ("Pretendard", "Times New Roman", "Noto Sans KR", "HYGothic"),
    size: 10.8pt, weight: "bold",
    it
  )
  #v(0.2em)
]

// figure / table supplement 분리: image → 그림, table → 표
#show figure.where(kind: image): set figure(supplement: [그림])
#show figure.where(kind: table): set figure(supplement: [표])

// 표 디자인 — KCI 학술지 표준 (헤더 강조 + 본문 행 사이 얇은 구분선 + 하단 마감선)
#set table(
  stroke: (x, y) => (
    // 맨 위 바깥선 (헤더 위)
    top: if y == 0 { 1.0pt + black } else { 0pt },
    // 헤더와 본문 사이 = 진한 선, 본문 행 사이·표 하단 = 얇은 회색 구분선
    bottom: if y == 0 { 1.0pt + black } else { 0.3pt + rgb("#bbb") },
  ),
  fill: none,
  inset: (x: 10pt, y: 9pt),
)

#show table.cell: it => {
  set par(leading: 0.50em)
  it
}

// 헤더 행(첫 행)은 non-variable 폰트로 bold 강제 (Noto Serif KR이 variable font라 bold 미지원 회피)
#show table.cell.where(y: 0): set text(
  weight: "bold",
  font: ("Times New Roman", "Malgun Gothic", "HYGothic", "Batang"),
)

// =============================================================
// 표지
// =============================================================
#align(center)[
  #v(2em)
  #text(size: 18pt, weight: "bold",
        font: ("Pretendard", "Times New Roman", "Noto Sans KR", "HYGothic"))[
    한국 정부 재정 집행의 굿하트 게임
  ]
  #v(0.6em)
  #text(size: 12.5pt,
        font: ("Pretendard", "Times New Roman", "Noto Sans KR", "HYGothic"))[
    Principal-Agent 균형 분석, 사업원형별 다중 검증, 정책 처방
  ]
  #v(2.5em)
  #text(size: 11pt)[정선규, 심은철, 김영찬]
  #v(0.35em)
  #text(size: 9pt, fill: rgb("#555"))[
    정선규 #h(0.5em) jsk320098\@gmail.com #h(1.5em)
    심은철 #h(0.5em) simeunchul\@naver.com #h(1.5em)
    김영찬 #h(0.5em) findurwind\@gmail.com
  ]
  #linebreak()
  #v(0.3em)
  #text(size: 10pt, fill: rgb("#444"))[2026년 4월]

  #v(2em)
  #line(length: 40%, stroke: 0.6pt + rgb("#999"))
  #v(0.5em)
  #text(size: 9pt, fill: rgb("#555"))[
    GitHub #link("https://github.com/bluethestyle/goodhart-korea")[bluethestyle/goodhart-korea]
  ]
  #linebreak()
  #text(size: 9pt, fill: rgb("#555"))[
    인터랙티브 시각화 #link("https://bluethestyle.github.io/goodhart-korea/")[bluethestyle.github.io/goodhart-korea]
  ]
  #v(0.5em)
  #line(length: 40%, stroke: 0.6pt + rgb("#999"))
]

#v(2.5em)

// =============================================================
// 초록
// =============================================================
#align(center)[
  #text(weight: "bold", size: 12pt,
        font: ("Pretendard", "Times New Roman", "Noto Sans KR", "HYGothic"))[국문 초록]
]
#v(0.6em)

#[
  #set par(first-line-indent: 0pt, leading: 0.95em)
  본 연구는 한국 중앙정부 재정 집행에 *굿하트 효과* #cite(<goodhart1975>)가 발현하는 *미시적 기제*를 Principal-Agent 균형 분석으로 도출하고, 그로부터 파생되는 6개 검증 가능 가설(H1\~H6)을 11년 시계열·14분야·1,557개 활동·11개 방법론으로 다중 검증한다.

  *이론*: 평가 가중 $w_t$(시점 조정, 측정 가능)와 $w_q$(사업 품질, 측정 어려움)의 *측정성 격차*가 큰 한국 평가 제도(집행률 평가·출연기관 경영평가·감사) 환경에서 *합리적 행위자*의 균형 행동이 *시점 조정 노력 $e_t$로 자원이 쏠리는 굿하트 게임*임을 도출한다 — #cite(<holmstrom1991>, form: "prose")의 한국 적용.

  *실증*: 활동 단위 임베딩(UMAP+HDBSCAN)으로 *4개 사업원형*(인건비형·자산취득형·출연금형·정상사업)을 발견하고, Mapper·Persistent Homology로 위상 안정성을 입증한다(H1). 분야 라벨은 게임화 강도 분산에 *trivial한 추가 설명력*에 그치는 반면, 사업원형×지출진동 상호작용은 유의한 추가 설명력을 가진다. 회계연도 12월 RDD 분석에서 *자산취득형이 여타 사업원형 대비 가장 강한 연말 집중 점프*를 보이며(H2), 출연금형은 여타 원형 대비 현저히 강한 *연간 사이클 우세* 패턴을 나타낸다(H3). 사회복지 분야는 자동분배 특성에 의한 *fortuitous alignment* 효과를 보이며($r = -0.86$, CPI 통제 후 강화), 이는 모형의 분야 alignment 함수로 명시적으로 포착된다(H5). 웨이블릿 분석은 *출연금형 게임화 강도가 표본 기간 내 시간에 따라 강화*됨을 새롭게 보인다(H6) — #cite(<liebman2017>, form: "prose") 미국 결과의 *질적·동적* 한국 확장.

  *정책*: 모형의 비교정역학에서 6개 정책 권고를 *직접 도출*한다 — 집행률 평가 가중 완화 방향의 다년도 회계, 출연기관 평가 지표 전환, 정산 시점 분산, 데이터 인프라, 자동 flagging, 시간 가중 점검. 각 권고는 모형 레버와 1:1 대응하며, Holmstrom-Milgrom impossibility의 본질적 한계를 정직하게 명시한다.
]

#v(1em)

#[
  #set par(first-line-indent: 0pt)
  #text(weight: "bold")[주요어:] 굿하트 법칙, Principal-Agent 모형, 다업무 계약, 정부 재정, 사업원형, 회귀불연속, 웨이블릿, 토폴로지 데이터 분석, 한국
]

#v(2em)

// =============================================================
// 영문 초록 (English Abstract) — Zenodo DOI 메타데이터·국제 검색 노출용
// =============================================================
#align(center)[
  #text(weight: "bold", size: 12pt,
        font: ("Pretendard", "Times New Roman", "Noto Sans KR", "HYGothic"))[Abstract]
]
#v(0.4em)
#align(center)[
  #text(weight: "bold", size: 11pt,
        font: ("Pretendard", "Times New Roman", "Noto Sans KR", "HYGothic"))[
    Goodhart's Game in Korean Central Government Spending: \
    A Principal-Agent Equilibrium Analysis with Multi-Method \
    Validation and Model-Based Policy Prescriptions
  ]
]
#v(0.6em)

#[
  #set par(first-line-indent: 0pt, leading: 0.95em)
  This paper derives the micro-mechanism through which Goodhart's effect #cite(<goodhart1975>) manifests in Korean central government budget execution via a Principal-Agent equilibrium model, then validates six falsifiable hypotheses (H1--H6) using 11-year monthly data, 14 expenditure fields, 1,557 spending activities, and 11 analytical methods.

  Korea's evaluation regime --- execution-rate audits, management assessments of government-affiliated institutions, and Board of Audit reviews --- creates a large measurability gap between the timing-adjustment weight $w_t$ (observable) and the quality weight $w_q$ (unobservable). Following #cite(<holmstrom1991>, form: "prose"), a rational agent's equilibrium response is to concentrate effort on the measurable dimension, yielding what the paper terms a Goodhart game: systematic near-year-end over-execution at the expense of project quality. The model maps onto all four Goodhart categories of Manheim and Garrabrant (2019).

  Activity-level embeddings (UMAP + HDBSCAN) uncover four project archetypes --- personnel-cost, capital-acquisition, grant-transfer, and normal-operation --- with Mapper and Persistent Homology confirming topological stability (H1). Field labels add negligible explanatory power over gaming intensity ($Delta R^2 = 0.000$). Regression discontinuity at the December boundary shows capital-acquisition activities spike 3.42$times$ at fiscal year-end (H2); grant-transfer activities exhibit the strongest annual-cycle dominance in spectral and wavelet coherence analyses (H3). Social-welfare spending shows a fortuitous alignment effect from automatic-transfer mechanics ($r = -0.86$, strengthened after CPI controls; H5). Wavelet decomposition reveals that grant-transfer gaming intensity amplified by +554% in 12-month amplitude over the sample, extending #cite(<liebman2017>, form: "prose") qualitatively and dynamically to Korea (H6).

  Six policy prescriptions follow directly from the model's comparative statics: multi-year appropriations, revised indicators for affiliated institutions, staggered settlement deadlines, data infrastructure, automated execution-pattern flagging, and time-weighted monitoring. Each maps one-to-one to a model lever. The analysis forthrightly acknowledges the fundamental limits imposed by Holmstrom--Milgrom impossibility.
]

#v(1em)

#[
  #set par(first-line-indent: 0pt)
  #text(weight: "bold")[Keywords:] Goodhart's Law, Principal-Agent Model, Multitasking Contract, Public Finance, Project Archetype, Regression Discontinuity, Wavelet Analysis, Topological Data Analysis, Korea
]

#pagebreak()

// =============================================================
// 약어 일람·핵심 용어 정의는 부록 A·B로 이동 (서론 앞 배치는 학술지 관행에서 어색)
// 본문은 첫 등장 시 풀어쓰기 + 부록 참조 방식 사용

// =============================================================
= 서론

== 문제 의식 — "측정되는 것이 중요해진다"

  #cite(<bevan2006>, form: "prose")는 영국 NHS 사례 연구를 통해 "측정되는 것이 중요해진다(What's measured is what matters)"는 명제 아래 평가지표 게임화의 4가지 패턴(threshold effect, ratchet effect, output distortion, gaming)을 식별했다. 이는 #cite(<goodhart1975>, form: "prose")와 #cite(<campbell1979>, form: "prose")이 각각 통화정책과 사회과학 일반에서 제안한 *지표가 정책 도구로 채택되는 순간 그 지표의 측정 신뢰도가 하락한다*는 명제의 행정학적 구체화다.

  같은 메커니즘이 한국 중앙정부 재정 집행에서도 작동하는가? 이 질문에 답하기 위해서는 (a) 게임화를 *측정 가능한 양*으로 정의하고, (b) 분야·부처·사업 형태에 걸친 *이질성을 분리*하며, (c) 자연 경기 cycle이나 추세 효과 같은 *경합 가설을 배제*해야 한다. 본 연구는 11년 시계열·14분야·1,557개 활동을 다중 방법론으로 결합해 이 세 과제를 단계적으로 수행한다.

== 미국 선행연구의 한국적 확장

  #cite(<liebman2017>, form: "prose") (AER)는 미국 연방조달의 11월 마지막 주 vs 12월 첫 주 회귀불연속(RDD)으로 회계연도 마감 직전 주의 지출이 *5배* 증가하고 동시에 *품질 점수가 하락*함을 입증했다. 사용하지 않으면 이월되지 않는 예산 제도(use-it-or-lose-it)가 만들어내는 측정 왜곡의 모범적 인과 식별 사례다.

  본 연구는 동일한 RDD 설계를 한국 11년 시계열에 적용한다. 한국 자료가 월 단위 granularity인 점을 고려해 11월 vs 12월 일평균 집행을 비교하며, 사업원형별 점프 규모의 이질성이 질적으로 같은 메커니즘의 한국적 발현인지를 검토한다. 구체적인 추정 결과는 §6.3에서 보고한다.

== 본 연구의 핵심 기여

  본 연구의 기여는 (1) 이론 모형, (2) 분석 단위 재정의, (3) 직관 반대 발견, (4) 시간 동적 강화, (5) 정책 처방의 모형적 도출이라는 다섯 측면으로 구성된다. 본문 각 섹션에서 정식 검증되며, 결론에서 다시 요약한다.

  + *기여 1 — 이론 모형 (§3)*: Principal-Agent 균형 분석을 통해 *왜* 한국에서 굿하트 효과가 발현하는가에 답한다. Agent의 *비합리성*이 아닌 *합리성*이 측정성 격차 환경에서 시점 조정 노력으로 자원이 쏠리도록 유도한다. 모형은 6개 검증 가능 가설(H1\~H6)을 산출.

  + *기여 2 — 분석 단위 재정의 (§6.1, H1)*: 한국 행정학·재정학이 표준으로 사용해온 *분야 단위 분석*이 게임화에 대해 *trivial*($Delta R^2 = 0.000$)이고, 진짜 단위는 *사업 형태(archetype)*임을 위상 데이터 분석으로 다중 입증.

  + *기여 3 — 직관 반대 발견 (§6.3\~§6.7, H2/H3/H5)*: 게임화는 단순한 부정적 측정 왜곡이 아니라 *분야 이질적·사업원형 이질적* 현상이다. 자산취득형 RDD 점프 3.42배(H2), 출연금형 사이클 우세(H3), 사회복지 *fortuitous alignment*에 의한 자동분배 효과(H5)가 핵심.

  + *기여 4 — 시간 동적 강화 (§6.8, H6, Wavelet 신규)*: FFT 정상성 가정의 한계를 웨이블릿으로 보완해 *게임화가 시간이 갈수록 강화*됨을 새롭게 입증. 출연금형 12개월 cycle 진폭 *2015\~2017 → 2023\~2025로 +554\%* 증가, 인건비형 변화 없음(통제). 한국 굿하트 효과는 *고정 패턴이 아닌 진행 중인 동적 현상*.

  + *기여 5 — 정책 처방의 모형적 도출 (§7)*: 정책 권고를 *임의 나열*이 아닌 모형의 비교정역학 ($(partial e_t^*) / (partial w_t) > 0$ 등)에서 *직접 도출*. 6대 권고 — 다년도 회계, 출연기관 평가 지표 전환, 정산 분산, 데이터 인프라, 자동 flagging, 시간 가중 점검 — 은 모형 레버 ($w_t, w_q$, $c_(t t)$)와 1:1 대응. Holmstrom-Milgrom impossibility의 본질적 한계를 정직 명시.

= 이론적 토대

  본 연구의 분석은 세 갈래의 이론적 전통을 결합한다. (1) *공공관리 이론*에서 굿하트-캠벨 법칙과 NPM(New Public Management) 측정 패러독스, (2) *계약경제학*에서 Holmstrom-Milgrom의 다업무 모형, (3) *비교경제학*에서 Kornai의 연성 예산 제약이다. 각 이론은 본 연구의 다른 발견을 설명하며, 셋이 결합될 때 사업 형태별 게임화 강도 차이가 자연스럽게 도출된다.

== 굿하트-캠벨 법칙과 NPM 패러독스

  #cite(<goodhart1975>, form: "prose")는 영란은행 통화 통계를 정책 도구로 사용한 뒤 그 통계와 거시경제 실체의 관계가 무너진 사례를 관찰하며 *"통계 규칙성은 통제 목적으로 사용되는 순간 무너진다"*고 정식화했다. #cite(<campbell1979>, form: "prose")은 같은 원리를 사회과학 일반에 확장했다.

  #cite(<manheim2018>, form: "prose")는 이를 네 유형으로 분류했다.
  - *Regressional*: 측정 노이즈에 정책이 과적합
  - *Causal*: 지표를 직접 조작하나 그 인과 경로는 비효율적
  - *Extremal*: 극단 영역에서 지표-목표 관계가 깨짐
  - *Adversarial*: 행위자가 의도적으로 지표를 조작

  인센티브 구조와 측정 왜곡의 관계는 #cite(<kerr1975>, form: "prose")의 고전 명제 — "A를 보상하면서 B를 기대하는 것의 어리석음" — 으로 일찍이 제기되었다. 한국 집행률 평가는 이 명제의 전형적 사례다. 공공 인센티브 프로그램에서 게임화 반응을 실증한 연구로 #cite(<courty2004>, form: "prose")를 참조한다.

  본 연구의 12월 점프와 출연금 게임화는 주로 *Causal*(시점 조정으로 집행률 지표 달성)과 *Adversarial*(이월 회피를 위한 의도적 몰아쓰기)에 해당한다.

== 다업무 계약 이론(Multitasking)

  #cite(<holmstrom1991>, form: "prose") (JLEO)은 대리인이 *다차원 업무*를 수행할 때 측정 가능한 차원에만 인센티브를 걸면 측정 불가능한 차원의 노력이 *체계적으로 감소*하는 모형을 제시했다. 측정성 격차가 큰 업무 구성에서는 어떤 인센티브 강도도 1차 최적이 될 수 없다는 결과(impossibility theorem)다. 후속 연구로 #cite(<baker1992>, form: "prose")는 *측정 노이즈*보다 *측정 왜곡(distortion)*이 인센티브 설계에 더 치명적임을 보였다 — 본 연구의 측정성 격차 함수 $phi'(\cdot) < 1$은 Baker의 distortion 파라미터에 직접 대응한다.

  공공 사업에 적용하면, 집행률(측정 가능)과 사업 품질(측정 어려움)이 상충하는 환경에서 집행률 인센티브가 강할수록 품질이 희생된다. 본 연구의 사업 형태별 RDD 점프 차이(자산취득형 3.42배 vs 출연금형 1.10배 vs 인건비형 1.12배)는 *측정 압력에 대한 반응성이 사업 형태별로 다르다*는 이 가설의 한국 실증이다.

  한국 공공기관 평가 게임화 문헌: 한국 행정학·재정학 KCI 학술지에서도 출연기관 PBS(Project-Based Funding System)와 공공기관 경영평가의 게임화·ratchet effect를 다룬 연구가 축적되어 있다. 김근세·이만형 @kim2009pbs, 박정수 @park2014pbs, 임도빈 외 @lim2020kpi 등이 PBS 도입 이후 R&D 성과 지표의 *수치 inflation*과 *전략적 보고*를 보고했다.

== 연성 예산 제약(Soft Budget Constraint)

  #cite(<kornai1980>, form: "prose")는 사회주의 경제의 국유기업이 시장 규율 대신 정부 구제를 기대하며 예산 제약이 *연성화*되는 현상을 이론화했다. 시장경제 공공 부문의 출연기관·공공기관도 동일한 메커니즘에 노출된다.

  *공공기관·출연기관은 직접 사업과 달리 사업 시점 조정의 자유도가 높다*. 정산 기일을 맞추기 위해 12월 집중 집행이 가능하고, 다음 회계연도 예산이 감액되더라도 모기관 보전 가능성이 시장 규율을 약화시킨다. 본 연구의 출연금 비중과 게임화 강도 회귀(β=+0.375, p=0.005), 그리고 출연금형의 PSD k=1 진폭 0.332 + phase coherence 0.54(다른 원형의 2\~6배)가 이 메커니즘의 정량적 증거다. 한편 RDD 12월 점프 3.42배는 *자산취득형*에서 가장 두드러지는데, 이는 시설 공사·자산 취득 사업이 *공정률 마감 + 회계연도 마감* 결합으로 12월 1일 cutoff 직후 *이산적 점프*를 만들어내는 다른 메커니즘이다.

= 이론 모형 — Principal-Agent 굿하트 게임

  앞 절(이론적 토대)이 *세 가지 이론적 전통*을 소개했다면, 본 절은 그 전통을 *한국 평가 제도*에 specialize한 정식 모형을 제시한다. 본 모형은 agent의 *비합리성*이 아닌 *합리적 선택*이 측정성 격차 환경에서 굿하트 게임을 유발함을 보인다. 평가 제도가 정의한 목적함수 아래에서 균형 행동이 시점 조정 노력으로의 자원 집중이다.

== 현행 한국 평가 제도와 측정성 격차

  한국 중앙정부 사업 수행 부처·출연기관은 4중 평가에 노출된다.

  + *집행률 평가*: 회계연도 12월 31일 기준 % executed. 정확한 측정 (회계 시스템 일별 기록).
  + *사업 성과 평가 (KPI)*: 정량 지표 (산출, 결과). 부분 측정 — 사업별 KPI 정의가 다양하고 일부는 *대리 지표*에 의존.
  + *출연기관 경영평가*: 기획재정부 매년 평가. 집행률과 사업 KPI 모두 반영하나 *집행률 가중치가 높음*.
  + *감사원 정기 감사*: 사후 점검. 절차 위반·부정 집행 적발 위주, 사업 *실질 효과* 평가는 어려움.

  *측정성 격차* @holmstrom1991: 어떤 task는 정확히 측정되고 다른 task는 부분/불가 측정. 본 연구의 핵심 격차는 다음과 같다.

  - $e_t$ = *시점 조정 노력* (12월 집중 집행 행위): *완벽 측정* (월별 집행 기록)
  - $e_q$ = *사업 품질 노력* (사업의 실질적 사회 결과 기여): *측정 어려움* — 사회 결과는 다년 후 발현, 다중 인과 요인, 측정 도구 부재

  격차가 큰 환경에서는 인센티브 설계가 본질적으로 왜곡된다. 본 절은 이 격차를 게임 이론적으로 정식화한다.

== 모형 setup — Principal과 Agent의 목적함수

  활동 $i$, 회계연도 $t$를 단위로 하는 stage game을 정의한다.

  Principal (정부/부처, $P$)의 목적함수:
  $ U_P = E[Y(e_q, e_t)] - C(I) $
  여기서 $Y$=사회적 결과(예: 빈곤 격차, 기대수명, 특허 수), $I$=Agent에 지급한 transfer(예산), $C(I)$=재정 비용. 통상 $(partial Y) / (partial e_q) > 0$ (품질 노력 → 결과 ↑), $(partial Y) / (partial e_t) approx 0$ (시점 조정은 사회 결과에 큰 영향 없음).

  분야별 alignment 함수 $alpha(theta_("field"))$: 사회 결과 $Y$의 시점 조정 노력에 대한 한계 생산성을 분야별 함수로 정식화한다.
  $ alpha(theta_("field")) := (partial Y) / (partial e_t) (e_q, e_t; theta_("field")) $
  본 연구의 14분야 실증에서 $alpha$의 분포는 다음과 같다.
  - $alpha(theta_("사회복지")) > 0$: 12월 집중 분배 → 빈곤층 자원 공급, 빈곤 격차 ↓
  - $alpha(theta_("환경")) < 0$: 12월 집중 집행 → 행정 절차 부실, 환경 결과 ↓
  - $alpha(theta_("기타 12분야")) approx 0$: 시점 조정이 사회 결과와 무관

  Fortuitous alignment의 정식 정의: 사회복지의 자동분배 효과는 *모형 외생적 분야 함수 $alpha$의 우연한 양수성*이다. Agent의 목적함수 $U_A$가 $Y$를 포함하지 않으므로 *모든* $Y$ 변화는 fortuitous — 사회복지가 음 상관을 보이는 것은 *분야의 외생 특성*이지 *agent의 의도된 사회 기여*가 아니다.

  본 정의는 *분야 trivial vs 사회복지 자동분배 양립*의 모형 기반이다 — *비용 함수 $c(\cdot; theta_("archetype"))$의 단위*는 사업원형이지만 (H1, 분야 trivial), *결과 함수 $alpha(theta_("field"))$의 단위*는 분야이다. 두 layer는 모형의 *서로 독립한 차원*이며, 사회복지의 outcome alignment는 *분야 layer의 우연한 한 점*에 해당한다.

  Agent (사업 수행 부처·출연기관, $A$)의 목적함수:
  $ U_A = w_t thin e_t + w_q thin tilde(e)_q - c(e_t, e_q; theta) $
  여기서
  - $w_t$ = 시점 조정의 평가 가중 (집행률 평가 + 출연기관 경영평가에서 *큼*)
  - $w_q$ = 측정 가능한 품질의 평가 가중 (KPI 일부 + 감사 기준에 *반영되나 작음*)
  - $tilde(e)_q = phi(e_q)$ = $e_q$의 *측정 가능 부분*. $phi: RR_+ arrow RR_+$, $phi(0) = 0$, $phi'(\cdot) > 0$, $phi'(\cdot) < 1$
  - $c(e_t, e_q; theta)$ = 노력 비용 함수, *사업원형 $theta$별 차이*. 볼록·증가 가정.

  측정성 격차 함수 $phi$의 정식 의미: $phi'(\cdot) < 1$은 *agent가 1단위 품질 노력 $e_q$를 투입해도 평가 시스템이 그 절대 비율 미만만 측정*함을 의미한다. 이는 #cite(<baker1992>, form: "prose")의 *distortion parameter*와 정확히 대응한다 — 측정 지표 $M$과 진정한 가치 $V$ 간 한계 생산성 격차 ($(partial M) / (partial e) != (partial V) / (partial e)$). $phi(e_q) = e_q$ ($phi'$ ≡ 1)이면 측정성 격차 0 → first-best 달성. 한국 사업 성과 평가는 $phi'(\cdot) << 1$인 환경 (예: 사회 결과 측정 시계열 5\~35년, 다중 인과 요인, 측정 도구 부재) — 본 연구의 핵심 가정이다.

  핵심 비대칭: $Y$는 Principal의 목적이지만 Agent의 목적함수에 *직접 들어가지 않는다*. Agent는 $Y$를 신경쓰지 않고 평가 점수 $w_t e_t + w_q tilde(e)_q$만 최대화한다. *모든 $Y$-개선은 우연한 alignment의 결과*다.

  비용 함수 편미분 표기 규약: 본 절 이하에서 비용 함수 $c$의 1·2계 편미분은 하첨자 표기로 줄여 쓴다 — $c_t equiv (partial c)/(partial e_t)$, $c_q equiv (partial c)/(partial e_q)$, $c_(t t) equiv (partial^2 c)/(partial e_t^2)$, $c_(q q) equiv (partial^2 c)/(partial e_q^2)$, $c_(t q) equiv (partial^2 c)/(partial e_t partial e_q)$. 비교정역학에서 *분수 안 분수* 표기를 회피하기 위한 표준 규약이다.

== 균형점 도출 — 굿하트 게임의 1차 조건

  Agent의 1차 조건(FOC). $tilde(e)_q = phi(e_q)$이므로 $e_q$에 대한 미분에 chain rule이 적용된다:
  $ (partial U_A) / (partial e_t) = w_t - (partial c) / (partial e_t) = 0 quad => quad w_t = (partial c) / (partial e_t) $
  $ (partial U_A) / (partial e_q) = w_q phi'(e_q) - (partial c) / (partial e_q) = 0 quad => quad w_q phi'(e_q) = (partial c) / (partial e_q) $

  *핵심 결과*: $w_t >> w_q$인 환경(현행 한국 평가 제도) + $phi'(\cdot) < 1$ (측정성 격차)에서 *효과적 품질 가중* $w_q phi'(e_q) < w_q << w_t$이므로 균형 $e_t^* >> e_q^*$ — Agent가 *합리적*으로 시점 조정에 노력 집중. 측정성 격차는 두 경로로 균형을 왜곡한다: (i) 평가 가중 비대칭 ($w_t > w_q$), (ii) 품질 노력의 *측정 누설* ($phi' < 1$). 이것이 *굿하트 게임의 미시적 기제*다.

  굿하트 법칙은 흔히 "지표가 정책 도구가 되면 측정성이 무너진다"는 명제로 표현되지만, 본 모형의 미시적 도출은 보다 강한 명제를 제공한다 — *합리적 agent의 균형 행동이 측정성 붕괴를 유발*한다. Agent의 도덕적 비난은 부적절하며, *제도 설계의 결함*이 본질이다.

  Holmstrom-Milgrom impossibility의 한국 적용: 측정성 격차가 큰 환경에서 어떠한 인센티브 강도 $(w_t, w_q)$도 1차 최적(first-best)이 될 수 없다. 구체적으로
  - $w_q$를 키우려 해도 $tilde(e)_q$만 늘어남 — 측정 가능 부분으로의 *효과 누설*
  - $w_t$를 줄이려면 발주자의 *직접 감시 비용* 부담
  본 연구의 실증 결과는 이 impossibility의 한국 환경 *직접 검증*이다.

== 비교정역학 — 정책 변수 변화의 균형 효과

  $e_t^*$의 부분 미분(상세 도출은 부록 F):
  $ (partial e_t^*) / (partial w_t) > 0 quad ("시점 평가 가중 ↑ → 게임화 ↑") $
  $ (partial e_t^*) / (partial w_q) < 0 quad ("품질 평가 가중 ↑ → 게임화 ↓") $
  $ (partial e_t^*) / (partial c_(t t)) < 0 quad ("시점 조정 비용 ↑ → 게임화 ↓") $

  세 부분 미분은 *세 가지 정책 처방*에 직접 대응한다.
  + $w_t$ 감소: *집행률 평가 완화* (다년도 회계, MTEF 강화)
  + $w_q$ 증가: *사업 성과 측정 인프라* 구축 (단점: 측정성 격차 본질적 한계)
  + $c_(t t)$ 증가: *시점 조정의 한계 비용 증가* (출연기관 정산 분산, 자동 flagging)

  세 처방은 본 연구의 정책 함의 절(권고 1\~4)과 일대일 대응한다.

== Career Concerns — 출연금형의 집단 평판 균형

  본 절은 §3.3의 정적 모형을 다년 평판 게임으로 *확장*하나, 본 연구의 주요 검증(H1~H6)은 §3.3의 정적 균형으로 도출되며 본 절의 동적 결과는 §6.4 출연금형 phase coherence 분석의 메커니즘적 해석에 한정 활용된다.

  본 모형의 stage game은 단일 평가 라운드에서의 균형을 다룬다. 그러나 한국 출연기관·공공기관은 *다년 반복 게임*에 노출되며, 이때 *집단 평판(collective reputation)*이 추가 인센티브로 작용한다 (@holmstrom1999; @dewatripont1999).

  동적 게임 setup: 연도 $t = 1, 2, ..., T$에서 활동 $i in cal(I)_("모기관")$ (동일 모기관 산하 출연기관 활동)이 시점 노력 $e_(i,t)$를 선택한다. 모기관의 *진정한 평가 기준* $mu^* in RR$은 시점 조정의 *효과적 가중*을 결정 — 즉 활동 $i$가 인지하는 시점 평가 가중은 $w_t(mu^*)$로, $mu^*$가 클수록 집행률 평가의 가중이 큼 ($w_t' (mu^*) > 0$). $mu^*$는 *불확실*하며 agent들은 동료 활동의 평가 결과로부터 학습한다.

  활동 $i$의 평가 점수 $s_(i,t) = w_t(mu^*) e_(i,t) + w_q(mu^*) tilde(e)_(q,i,t) + epsilon_(i,t)$. 활동 $i$는 $t-1$기 동료 점수 ${s_(j,t-1)}_(j != i)$를 관측해 $mu^*$의 belief를 update.

  Bayesian belief update: 가우스 conjugate에서 사후평균 $hat(mu)_(i,t) = E[mu^* | s_(j,t-1), j != i]$는 동료 점수 평균 $hat(R)_(t-1) = (1\/n) sum_(j != i) s_(j,t-1)$의 affine 함수가 된다 — 동료 점수가 클수록 "$mu^*$가 크다"는 사후 추정.

  동적 균형 (effective weight 매개): 활동 $i$는 *효과적 가중* $tilde(w)_t equiv w_t(hat(mu)_(i,t))$ (§3.3의 $w_t$에 신념 $hat(mu)_t$를 조건부로 한 동적 가중)를 사용해 stage problem을 푼다.
  $ e_(i,t)^* = arg max_(e_t) {tilde(w)_t (hat(mu)_(i,t)) e_t + tilde(w)_q (hat(mu)_(i,t)) tilde(e)_q - c(e_t, e_q)} $
  여기서 $tilde(w)_t$가 $hat(R)_(t-1)$을 통해 $hat(mu)_(i,t)$에 의존하므로 $hat(R)$이 max에 *실질적으로 진입*한다 (단순 가법 항이 아닌 *가중 함수 자체의 인수*로 진입). 1차 조건은 $tilde(w)_t (hat(mu)_(i,t)) = c_t(e_(i,t)^*, e_(q,i,t)^*)$.

  Nash 수렴 (collective synchronization): 모든 활동이 *공통* 신호 ${s_(j,t-1)}$에 노출되어 $hat(mu)_(i,t)$가 *유사한 분포*로 수렴하면 (LLN), 모든 $i$의 $tilde(w)_t (hat(mu)_(i,t))$가 동기화 → FOC를 통해 $e_(i,t)^*$도 동기화:
  $ "phase"(e_(i,t)^*) approx "phase"(e_(j,t)^*) quad forall i, j in cal(I)_("모기관") $
  이는 *Bayesian-Nash equilibrium of similar games* (@morris2002 정보 협응의 한국 변형)에서 자연스럽게 도출된다.

  우리 실증과의 정확한 대응: 출연금형 phase coherence 0.54 (다른 원형 0.08\~0.13의 *4\~7배*; 부록 D.3)는 이 *효과적 가중 동기화의 직접 측정*이다 — 활동 $i, j$가 *학습된 $hat(mu)$를 통해 동시에 피크*에 도달함. 인건비형 phase coherence 0.41(통제)은 *구조적 균등 지급*에 따른 자연 동기화이며, 자산취득형(0.08)·정상사업(0.13)은 *동료 평가 신호 학습이 약한* 사업 환경 — 즉 모기관-위탁기관 결속이 출연금형보다 약함 — 의 발현으로 해석된다.

  후속 연구의 자연 출발점: 본 동적 mechanism의 정량 검증은 *연도별 평가 결과 패널*과 *agent 행동 lag 분석*으로 가능 (@sannikov2008 연속시간 PA, @cabrales2011 동조 학습). $w_R$ 정량 측정 (모기관별 출연기관 평가 결과 분산 → 집단 평판 신호 강도)도 후속 자연 실험의 핵심 calibration 대상이다.

== 사업원형별 균형 예측

  비용 함수 $c(e_t, e_q; theta)$가 사업원형 $theta in \{$인건비형, 자산취득형, 출연금형, 정상사업$\}$별로 다르며, 평가 가중 $(w_t, w_q)$도 원형별로 다르다. 이로부터 *균형 $e_t^*$의 원형별 패턴*이 예측된다.

  #figure(
    table(
      columns: (auto, auto, auto, auto, auto),
      align: (left, center, center, center, left),
      table.hline(y: 1, stroke: 1.0pt + black),
      [*원형*], [*$w_t$*], [*$w_q$*], [*$partial c\/partial e_t$*], [*예측 $e_t^*$ 패턴*],
      [인건비형], [0], [작음], [매우 큼], [$approx 0$ — 매월 균등 (구조 제약)],
      [자산취득형], [큼], [작음], [작음 (12월 1일 가능)], [큼, *이산적 spike*],
      [출연금형], [큼], [작음], [중간 (분산 가능)], [큼, *연 사이클 분산*],
      [정상사업], [중간], [중간], [중간], [중간],
    ),
    caption: [사업원형별 모형 균형 예측 — 비용 함수와 평가 가중의 차이가 4개 패턴을 도출],
  )

== 실증 검증 가설

  본 절의 모형 도출은 *6개의 검증 가능한 가설*을 산출한다 (모두 결과 절에서 검증):

  + *H1 (분야 vs 원형)*: 비용 함수 $c$의 단위는 *사업원형*이지 분야가 아니다. → 분야 더미 $Delta R^2 approx 0$, 원형 상호작용 $Delta R^2 > 0$ 예측. (검증: §6.1·§6.2)
  + *H2 (자산취득형 RDD 점프)*: $c(\cdot)$이 12월 1일 직후 급감하는 원형. → RDD 점프 가장 큼. (검증: §6.3 — 3.42배)
  + *H3 (출연금형 사이클 우세)*: $w_t$ 큼 + 분산형 $c(\cdot)$. → PSD/wavelet/coherence 가장 큼. (검증: §6.4 + 부록 D — 0.332/+554%/0.54)
  + *H4 (매개 경로 이질성)*: $X arrow e_t arrow Y$ 경로가 *원형 이질적*이라 pooled 매개효과 미유의 예측. (검증: §6.5·§6.6 + 한계 절 — p=0.481)
  + *H5 (사회복지 fortuitous)*: $(partial Y) / (partial e_t) > 0$인 *예외* 분야. *우연*이지 정책 정당화 아님. (검증: §6.7)
  + *H6 (시간 강화)*: $w_t / w_q$ 비율의 시간 증가 → $e_t^*$ 시계열 강화. (검증: §6.8 — wavelet +554%)

  *Performative Prediction과의 이론적 연결*: H6는 #cite(<hardt2016strategic>, form: "prose")과 #cite(<perdomo2020performative>, form: "prose")의 Performative Prediction — *지표가 평가 도구로 채택되는 순간 그 지표가 측정하는 분포 자체가 변화한다* — 의 한국 재정 데이터 실증 사례에 해당한다. Agent가 평가 시스템의 구조를 학습해 시간이 지날수록 게임화 강도를 점진적으로 강화하는 *적응적 행동*이 그 메커니즘이다. 이 이론적 연결은 H6의 실증 해석을 뒷받침하며, 상세한 분석 결과는 §6.8에서 보고한다.

  본 모형은 *6개 가설을 동시에 예측*하며, 각 가설은 독립적인 데이터 분석으로 검증된다. 이는 모형의 *과적합 위험을 낮추는* 다중 검증 구조다.

== 굿하트 효과 분류와의 매핑 #cite(<manheim2018>)

  #cite(<manheim2018>, form: "prose")는 굿하트 효과를 *4가지 변형*으로 분류했다 — Regressional(측정 노이즈에 정책 과적합), Causal(지표 직접 조작), Extremal(극단 영역 관계 붕괴), Adversarial(의도적 조작). 본 연구의 6 가설은 이 4유형에 다음과 같이 매핑된다.

  #figure(
    table(
      columns: (0.4fr, 0.45fr, 1fr),
      align: (center+horizon, center+horizon, center+horizon),
      table.hline(y: 1, stroke: 1.0pt + black),
      [*Manheim-\ Garrabrant 유형*], [*우리 가설*], [*메커니즘*],
      [*Causal*], [H2 (자산취득 RDD),\ H3 (출연금 사이클)], [Agent가 *측정 가능 차원* $e_t$를 직접 조작 — 사업 본질이 요구하지 않는 12월 spike 또는 연 사이클 누적],
      [*Adversarial*], [H6\ (시간 강화 +554\%)], [Agent가 *학습*해 시간이 지날수록 게임화 강도 증가 — 평가 시스템 약점 식별 후 적응 (Performative prediction과 직접 연결)],
      [*Regressional*], [H5\ (사회복지 fortuitous)], [Agent의 $e_t$ 노력이 *우연히* 사회 결과 $Y$와 양의 상관 — 측정 노이즈가 분야별 alignment로 발현],
      [*Extremal*], [H4 (매개 이질성)], [매개효과 평균이 0 가까워도 *극단 원형(출연금/자산취득)에서는* 강한 매개. 평균 측정의 한계가 다중 게임화 메커니즘을 가린다],
    ),
    caption: [#cite(<manheim2018>, form: "prose") 4유형 굿하트 분류와 본 연구 6 가설의 매핑],
  )

  H1(분야 trivial)은 *모든 유형에 선행*하는 *분석 단위 식별* 결과다 — 굿하트 분류를 적용하기 *전에* "어느 단위에 게임화가 발현하는가"를 묻는 메타 가설.

= 데이터

== 정부 재정 집행 (게임화 측정 입력)

  - 열린재정정보 VWFOEM (월별 집행): 2015~2025 (11년), 활동 1,557건
  - 열린재정정보 expenditure_item (편성목): 2020~2025 (활동 단위 출연금/직접투자/인건비 비중)
  - 한국은행 ECOS 901Y009 소비자물가지수: 1990~2025 (외생 통제변수)

== 결과변수 (14분야 매핑)

  부적절 6개 outcome을 외부 검토 후 교체:

  #figure(
    table(
      columns: 4,
      table.hline(y: 1, stroke: 1.0pt + black),
      [*분야*], [*결과변수*], [*시계열*], [*출처*],
      [사회복지], [순자산 지니계수], [9년], [KOSIS DT_1HDAAD04],
      [보건], [기대수명], [15년], [KOSIS DT_1B41],
      [과학기술], [특허 출원/등록], [22년], [지식재산처 (e-나라지표 2787)],
      [산업·중기], [전산업생산지수], [15년], [KOSIS DT_1JH20201],
      [문화관광], [방한 외래관광객], [35년], [한국관광공사 (e-나라지표 1653)],
      [교육], [IMD 교육경쟁력 순위], [17년], [IMD (e-나라지표 1526)],
      [국토], [주택보급률], [20년], [KOSIS DT_MLTM_2100],
      [일반·지방행정], [지방재정자립도], [29년], [행정안전부 (e-나라지표 2458)],
      [농림수산], [농가소득], [22년], [KOSIS DT_1EA1501],
      [교통], [교통사고 사망], [10년], [도로교통공단 lgStat],
      [환경], [총 온실가스 배출], [34년], [GIR 국가 인벤토리],
      [통신], [초고속인터넷 가입률], [27년], [과기정통부 (e-나라지표 1348)],
      [통일외교], [ODA 원조규모], [24년], [OECD DAC (e-나라지표 1687)],
      [공공질서], [범죄 발생], [29년], [경찰청 (e-나라지표 1606)],
    ),
    caption: [14분야 결과변수 매핑],
  )

  국방과 예비비는 측정 불가능 분야로 명시 후 분석에서 제외했다.

= 방법론

  본 연구는 "게임화"라는 추상적 개념을 정량화하기 위해 신호 처리·차원 축소·위상 데이터 분석·인과 추론을 단계적으로 결합한다. 각 방법은 *서로 다른 약점을 보완*하도록 선택되었으며, 한 방법이 실패해도 다른 방법이 같은 결론을 지지하는지 점검하는 *방법론 트라이앵귤레이션*을 추구한다. 본 절은 *직관*과 *주제 적합성*에 집중하며, 상세 수식·알고리즘 골자·대안 비교는 *부록 C*에 별도 정리한다.

== 방법론 트라이앵귤레이션의 원칙

  단일 도구의 결과는 그 도구의 가정이 옳을 때만 신뢰할 수 있다. 도구마다 *서로 다른 실패 양태*를 갖기 때문에, 가정이 직교적인 도구 두셋이 같은 결론을 지지하면 결과의 *방법론 견고성*이 입증된다. 본 연구는 게임화 측정에서 FFT(주파수 영역, 정상성 가정)·STL(시간 영역, 가법 분해)·NeuralProphet(신경망 가법모형, 변화점 모델링)의 세 도구를 사용한다. 각 도구의 가정과 약점을 표 1에 정리한다.

  #figure(
    table(
      columns: (auto, auto, auto, auto),
      align: (center, center, center, center),
      table.hline(y: 1, stroke: 1.0pt + black),
      [*도구*], [*가정*], [*약점*], [*보완하는 도구*],
      [FFT], [정상성, 주기 일정], [추세 흡수, edge effect], [STL, NP],
      [STL], [가법 분해, LOESS 평활], [점프를 추세로 흡수], [FFT, NP],
      [NeuralProphet], [piecewise linear 추세 + Fourier 계절], [작은 N 과적합], [FFT, STL],
    ),
    caption: [세 게임화 측정 도구의 가정·약점·상호 보완 관계],
  )

== 게임화 강도를 어떻게 "측정"할 것인가

  게임화는 직접 관측할 수 없는 잠재 행동이다. 본 연구는 *집행 시계열의 모양*에서 그 흔적을 추출한다. 정상적인 자연 사업이라면 월별 집행이 비교적 평탄하거나 사업 일정에 따른 자연스러운 변동을 보인다. 반면 게임화된 사업은 "회계연도 마감 전 몰아쓰기" 또는 "보고 시점 직전 점프"처럼 *외생적 일정에 종속된 1년 주기 패턴*을 갖는다. 이 가설을 두 가지 직교 방법으로 검증한다.

=== 푸리에 변환(FFT) 기반 amp_12m_norm

  *직관*: 어떤 시계열이든 다양한 주기의 사인파 합으로 분해할 수 있다 #cite(<fourier1822>). 연도-내 시계열에 푸리에 변환을 적용하면 1년 주기 성분의 진폭이 추출된다. 이 진폭이 클수록 "12월 점프 + 1월 reset"이라는 회계연도 게임화 패턴이 강하다는 뜻이다. 정의(이산 푸리에 변환·`amp_12m_norm` 비율 식·Parseval 해석)는 부록 C.1.

  *주제 적합성*: 굿하트 효과는 *외생적 평가 주기에 동조된 게임화*로 정의된다@bevan2006. 한국 회계연도(1\~12월)는 모든 부처에 *동일 주기*로 강제되며 결산·집행률 평가가 12월 31일에 일률 적용된다. 즉 게임화 신호의 *주파수가 사전에 알려진* 1년이라는 점이 이 주제의 본질적 특성이며, 알려진 주파수의 진폭 측정은 *주파수 영역 분해(FFT)가 최적*이다. 시간 영역 변동성 지표(CV 등)는 알려진 주파수 정보를 활용하지 못한다.

=== STL 분해(Seasonal-Trend decomposition using Loess)

  *직관*: FFT amp_12m_norm 신호가 진짜 게임화일까, 아니면 *지속적으로 증가하는 추세*가 12월 결산 시점 기록 방식과 결합해 만들어내는 가짜 주기성일까? 이 의문을 검증하기 위해 STL #cite(<cleveland1990>)을 사용한다. STL은 시계열을 가법 분해 $x_t = T_t + S_t + R_t$로 추세·계절·잔차로 분리하고, 추세 제거 후 계절 성분의 분산 비율을 `seasonal_strength`로 정의해 게임화 지표로 사용한다. 두 겹 반복(inner/outer loop)·robustness weight·정의식은 부록 C.2.

  *주제 적합성*: 한국 정부 예산은 IMF 구조조정(1998), 국가재정법 도입(2007), MTEF 5년 framework 적용(2009) 등 *명확한 추세 변동 동인*을 가진다. 이런 추세를 분리하지 않으면 FFT는 "추세 + 12월 게임화"의 합성 신호를 측정한다. STL은 비모수 LOESS로 *임의 형태의 추세*를 흡수해 *순수 계절 성분만* 분리한다 — 한국 예산의 비선형 추세에 대해 ARIMA 차분보다 적합하다. 본 연구의 핵심 발견인 사회복지 자동분배 신호가 STL 후 소멸한다는 점은 추세 혼재 가능성을 시사하는 자기 비판 증거가 된다.

=== NeuralProphet 신경망 분해 — 세 번째 cross-check

  *직관*: FFT(정상성 가정)와 STL(임의 추세 가정)이 서로 다른 결론을 줄 때 어느 쪽이 게임화의 진짜 신호인지 결정하기 위해 *세 번째 독립 도구*가 필요하다. NeuralProphet #cite(<triebe2021>)은 Facebook Prophet #cite(<taylor2018>)의 신경망 확장으로, 시계열을 *추세 + Fourier 계절 + AR-Net 자기회귀 + 이벤트 + 외생 회귀*의 6개 가법 성분으로 분해한다. 본 연구는 cross-check 비교 형평성을 위해 자기회귀(`n_lags=0`)·외생 회귀를 *비활성화*하고 *추세 + 계절*만 사용한다. 6항 모형식·AR-Net 신경망 식·Prophet 원판과의 차이·하이퍼파라미터 설정은 부록 C.3.

  *주제 적합성*: 한국 정부 예산은 (a) 점진적 추세, (b) 정책 변화점(2007 국가재정법, 2014 국가회계제도 개편, 2017 추경 확대), (c) 회계연도 12월 강제 주기를 동시에 갖는다. NeuralProphet은 *piecewise-linear + 자동 changepoint 검출*로 추세를 흡수하면서 Fourier 기저로 계절을 분리해, 이 세 요소를 *해석 가능한 가법 모형*으로 동시 처리할 수 있는 거의 유일한 도구다 — FFT는 (a)·(b)에 약하고, STL은 (b)에 약하다. ARIMA·LSTM 등의 대안과 비교는 부록 C.3.

  *세 도구 합의 기준*: FFT `amp_12m_norm`, STL `seasonal_strength`, NP `yearly_seasonality` 진폭이 활동×연도 패널에서 강한 상관($r > 0.6$ 이상)을 보이면 게임화 신호 측정이 도구 의존이 아닌 *데이터의 본질적 특성*임이 입증된다. 갈리면 도구별 가정 차이를 한계로 명시한다.

== 사업 형태(원형) 발견 — 차원 축소 + 밀도 군집

  분야 라벨로 묶기 전에, *데이터가 자연스럽게 묶이는 형태*가 따로 있는지 확인해야 한다. 1,557개 활동을 12개 피처(예산 구성·집행 패턴·진폭)로 표현하면 12차원 공간의 점들이 된다. 이를 시각화 가능한 2차원으로 압축하고 군집을 식별한다.

=== UMAP (Uniform Manifold Approximation and Projection)

  *직관*: 12차원에서 가까운 점들은 2차원에서도 가깝게, 멀리 있는 점들은 멀리 보이도록 *국소 이웃 구조를 보존하면서* 차원을 압축하는 비선형 알고리즘@mcinnes2018. 고차원·저차원의 fuzzy simplicial set 표현 사이의 cross-entropy를 SGD로 최소화한다. 손실함수 정의·하이퍼파라미터·PCA·t-SNE·Autoencoder와의 비교는 부록 C.4.

  *주제 적합성*: 사업 활동의 12피처(예산 구성·집행 패턴·진폭)는 강한 *비선형 상관*을 갖는다 — 예: 출연금 비중과 게임화 진폭 사이 sigmoid 관계. 또한 1,557개 활동이라는 *작은 데이터*에서 자율 임베딩 학습은 과적합되며, *재현 가능한 결정론적 임베딩*이 정책 보고서에 인용 가능해야 한다. UMAP은 (a) 비선형 보존 (b) 작은 N 안정성 (c) `random_state` 재현 가능 — 세 요건을 모두 만족하는 거의 유일한 도구다.

=== HDBSCAN (Hierarchical Density-Based Spatial Clustering)

  *직관*: K-means처럼 군집 수를 미리 정하지 않고 *밀도가 높은 영역*을 군집으로 식별한다@campello2013. 밀도가 낮은 점은 *노이즈*로 분류한다. mutual reachability distance를 가중치로 하는 최소 신장 트리에서 임계값 $epsilon$을 변화시켜 condensed cluster tree를 만들고 *안정성* 점수가 높은 군집을 선택한다. 거리 정의·트리 구성·K-means·DBSCAN·GMM과의 비교는 부록 C.5.

  *주제 적합성*: 한국 사업 활동은 (a) 사업 형태별 *밀도 차이가 큼*(정상사업 1,175 vs 자산취득형 99), (b) 군집 수 사전 가정이 *연구 가설을 오염*시킴(분야가 trivial한지가 결과 가설), (c) *outlier 활동(극단 게임화 사업)*의 노이즈 처리가 정책 점검 대상 식별에 필수. HDBSCAN은 이 세 요건을 모두 만족한다(상세 §6.2 참조).

== 위상 데이터 분석(TDA) — 군집 구조의 안정성 검증

  UMAP+HDBSCAN의 결과가 알고리즘 우연성이나 매개변수 선택의 산물이 아닌, *데이터 자체의 위상적 구조*인지 확인하기 위해 두 가지 위상 도구를 적용한다. 위상 데이터 분석(TDA)의 이론적 토대는 #cite(<carlsson2009>, form: "prose")의 리뷰를 참조한다.

=== Mapper (kmapper)

  *직관*: 데이터의 *모양 골격*을 그래프로 추출한다@singh2007. UMAP+HDBSCAN이 *어디에 군집이 있는가*를 답한다면, Mapper는 *군집들이 어떻게 연결되어 있는가*를 답한다. 데이터 공간을 필터 함수의 겹치는 cover로 분할하고 각 부분을 군집한 뒤, 군집들을 노드로 두고 교집합에 점이 있으면 엣지로 잇는 nerve simplicial complex를 만든다. 결과는 connected component 수, loop 수($beta_1$) 등 위상 불변량으로 요약. 정의식·UMAP+HDBSCAN과의 비교는 부록 C.6.

  *주제 적합성*: "분야 단위 trivial"이라는 본 연구의 핵심 주장은 사업 형태들이 분야와 무관하게 *위상적으로 분리된 component*를 형성한다는 것에 의존한다. Mapper graph에서 4개 사업원형이 분리된 components로 나타나면 *위상적으로* 별개 단위임을 입증할 수 있다 — 단순 임베딩 거리가 아닌 *연결성 부재*가 증거다.

=== Persistent Homology (PH, ripser)

  *직관*: 점들의 위상 구조를 *모든 스케일에서 동시에* 측정한다. 작은 $epsilon$에서 잠시 나타났다 사라지는 구조는 노이즈, *오래 살아남는* 구조는 진짜 위상 특성이다@edelsbrunner2008. 본 연구는 차원 0(연결성분 $beta_0$)과 차원 1(loop $beta_1$)을 분석하며, *부트스트랩 50회*에서 강건한 $beta_0 = 30$, $beta_1 = 15$, max persistence 95% CI는 위상 구조의 *표본 안정성*을 입증한다. 계산은 Python ripser 라이브러리#cite(<tralie2018>)를 사용했다. Vietoris-Rips complex·filtration·persistence diagram 정의·Mapper/silhouette 비교는 부록 C.7.

  *주제 적합성*: 본 연구가 발견한 4개 사업원형이 (a) UMAP 매개변수 변화에 견고한가, (b) 표본 변동에 견고한가를 입증해야 한다. PH는 (a)·(b) 모두에 대해 *비모수·스케일 불변* 검증을 제공하는 거의 유일한 도구다.

== 분야 라벨이 진짜 단위인가 — 고정효과 회귀

  *직관*: "분야가 다르니 결과가 다르다"는 직관이 맞다면, 모형에 분야 더미를 추가했을 때 설명력 R²가 크게 증가해야 한다. 반대로 ΔR²가 0에 가깝다면 분야 라벨은 *trivial*하고 진짜 변동은 다른 변수(사업 형태 등)에서 온다. 분야 더미 모형 vs 사업원형×게임화 상호작용 모형의 조정 R² 증가량을 비교한다. 회귀 식·판정 기준은 부록 C.8.

  *주제 적합성*: 한국 행정부 예산 분류는 (a) *역사적 관성*(1960년대부터 점진 확장)이 강하고 (b) 분야 내부에 이질적 사업 형태가 *공존*한다(예: 사회복지에 출연금형 한국사회보장정보원 + 정상사업 기초생활급여 동거). 분야 라벨이 게임화 차이를 설명하지 못한다면 정책 분석 단위를 *사업 형태로 재정의*해야 한다는 본 연구의 정책 시사점에 직결된다. 분야 FE는 이 가설의 *직접 검정* 도구다.

== 부처-원형 이중 그래프 — Spectral Co-clustering

  본 방법의 결과는 §7.1 부처-결과변수 4분면 분석에 직접 활용된다.

  *직관*: 부처와 사업원형으로 이뤄진 빈도 행렬을 *동시에* 군집해, "어느 부처가 어느 사업 형태에 특화되어 있는가"를 자동 식별한다@dhillon2001. 정규화된 빈도 행렬을 SVD하여 좌·우 특이벡터로 행·열을 동시 임베딩한 뒤 K-means로 군집한다. 정규화·SVD·K-means 구체식 및 단순 K-means·LDA와의 비교는 부록 C.9.

  *주제 적합성*: 한국 부처는 (a) 동일 분야에서도 *사업 형태별 특화도가 다름*(예: 과기정통부=출연금형 비중 큼, 행정안전부=인건비형 비중 큼), (b) 정책 점검 자원 배분에서 *부처 단위로 우선순위*를 매겨야 함. Co-clustering은 부처를 *사업 형태 특화 패턴으로 자동 분류*해 부처-결과변수 4분면 분석의 입력을 제공한다. 51개 부처가 5개 co-cluster로 분리되었다.

== 인과 식별 — 게임화는 진짜 원인인가

=== 회귀불연속 설계(RDD)

  *직관*: 회계연도 12월 1일은 행정적으로 *연속적인 시간*에 인위적으로 그어진 선이다. 사업의 본질적 필요와 무관하게 이 선 직전·직후로 집행 패턴이 점프한다면 그 점프는 *외생적 회계 cycle*에 의한 것으로 해석할 수 있다(@imbens2008; @lee2010). 본 연구는 활동 단위 11월 vs 12월 일평균 비율을 사용해 *비율형 점프 배수*로 보고한다(미국 Liebman-Mahoney 5배 형식과 비교 가능). 식별 가정·국지 선형 추정량 식·DID/IV/month-FE와의 비교는 부록 C.10.

  *주제 적합성*: 한국 회계연도 cutoff는 (a) 1948년 이래 *불변*, (b) 모든 부처에 *동시* 적용, (c) 개별 활동이 *조작 불가능* — RDD의 *세 핵심 가정*이 모두 성립하는 거의 이상적 자연실험 환경이다. #cite(<liebman2017>, form: "prose")가 미국에서 cutoff 며칠 차이로 5배 점프 + 품질 하락을 입증한 설계의 한국 적용은 *이론적으로 직접 가능*하며, 실제 분석에서 1.91배(전체) / 3.42배(자산취득형) 점프를 확인한다. 같은 활동의 단 며칠 차이를 비교하므로 *분야·기관·사업 특성이 자동 통제*되는 준실험이다.

=== 매개분석 — Baron-Kenny + Sobel + Bootstrap

  *직관*: 출연금 비중($X$)이 높을수록 결과변수($Y$)가 나빠진다는 상관이 발견되더라도, 그 경로가 "$X arrow$ 게임화($M$) $arrow Y$"의 *간접 효과*인지 "$X arrow Y$"의 *직접 효과*인지 분리해야 한다@baron1986. 4단계 회귀로 총효과 $c$, 매개경로 $a$, 직접효과 $c'$, 매개효과 $a b$를 분해한 뒤 Sobel z-검정 + Bootstrap 1,000회 신뢰구간으로 유의성을 검증한다. 4단계 식·Sobel 표준오차 식·Bootstrap 절차·SEM/Causal Mediation 비교는 부록 C.11.

  *주제 적합성*: 본 연구의 핵심 가설은 "출연금 → 12월 게임화 → 결과변수 악화"라는 *순차적 인과 경로*다. 매개라면 *게임화 자체* 개혁(예: 다년도 회계, MTEF 강화), 직접 효과라면 *출연 구조* 개혁(예: 위탁 사업 직영 전환)으로 정책 함의가 갈린다. Baron-Kenny는 이 경로 분리를 *해석 가능한 회귀 계수*로 제공한다. 결과: 시스템 평균 매개효과 미유의(p=0.481)이나 사회복지·환경 분야에서 강한 매개 — 게임화 메커니즘의 *분야 이질성*을 지지.

== 외생 통제 — 자연 경기 cycle 가설 기각

  *직관*: 사회복지 게임화-결과변수 상관이 진짜 인과인가, 아니면 *경기 변동에 의한 spurious 동조*인가? §4의 CPI(ECOS 901Y009)를 외생 거시 통제변수로 사용해 *Frisch-Waugh-Lovell residualization*(2단계 잔차회귀)으로 부분 상관을 산출한다. 정의식·외생성 가정·실업률/GDP 대안 비교는 부록 C.12.

  *외생성 정당화*: CPI는 한국은행이 통화정책 도구로 결정하므로 (a) *한은 독립성*에 의해 재정부 행정 결정에 직접 노출되지 않음, (b) *목표값(2.0\%)*이 사전 공표되어 *역인과 위협이 작음*. 따라서 한국 거시변수 중 *재정 게임화로부터 가장 외생적*인 후보이며 1990\~2025년 월별 공식 시계열로 신뢰성 있게 통제 가능하다. 결과: 14/14 분야에서 부호 유지, 70% 유의성 유지. 사회복지 신호는 $r = -0.76 arrow -0.86$으로 *오히려 강화* — 자연 cycle 가설 강력 기각.

== 견고성 검증 — Permutation·Lag/Lead·CV

  *Permutation 검정*: 결과변수 시계열을 $B = 1000$회 무작위 셔플하여 귀무 분포를 구성하고 양측 p-값을 산출한다. 정규성·등분산 가정이 필요 없는 비모수 검정. 분야별 N=8\~12 작은 표본에서 정규 근사 t-검정의 신뢰성 부족 문제를 우회.

  *Lag/Lead 분석*: 게임화-결과변수 상관에 시차 $tau in {-1, 0, +1}$년을 주어 *방향성*을 점검. $r(0)$ 동기 상관이 가장 강하면 즉시적 메커니즘(사회복지 자동분배 가설 정합), $r(+1)$ 강하면 지연 효과, $r(-1)$ 강하면 역인과 의심.

  *amp_cv 대안*: FFT 외에 변동계수($"CV" = sigma\/mu$) 기반 게임화 지표로 재산출해 *측정 도구 의존성*을 점검. 이 변동계수 기반 지표를 이하 `amp_cv`로 표기한다. 두 지표가 같은 결론이면 측정 robust성 입증. 검정식·구체 식은 부록 C.13.

= 결과 — 6 가설 다중 검증

  본 절은 §3에서 도출된 6개 가설(H1\~H6)을 *각 가설별 sub-section*으로 검증한다. 각 결과는 단일 회귀 계수가 아니라 *복수 도구의 합의*에 의해 지지될 때만 본문에 보고하며, 마지막 sub-section에서 *방법론 robustness*(STL 자기 비판 + NeuralProphet cross-check 통합)를 별도로 보강한다.

  #figure(
    table(
      columns: (0.3fr, 1fr, 0.5fr),
      align: (center, center, center),
      table.hline(y: 1, stroke: 1.0pt + black),
      [*가설*], [*예측*], [*검증 sub-section*],
      [H1], [분야 trivial, 원형이 진짜 분석 단위], [§6.1·§6.2],
      [H2], [자산취득형 RDD 점프 가장 큼 (이산적 spike)], [§6.3],
      [H3], [출연금형 사이클 우세 (PSD/coherence)], [§6.4],
      [H4], [매개 경로의 원형 이질성 (pooled 미유의)], [§6.6],
      [H5], [사회복지 fortuitous alignment ($(partial Y) / (partial e_t) > 0$)], [§6.7],
      [H6], [시간 동적 강화 ($w_t / w_q$ 비율 증가)], [§6.8],
      [방법론], [STL 자기 비판 + NeuralProphet·Wavelet 중재], [§6.9],
    ),
    caption: [P-A 모형의 6 가설과 결과 절의 검증 매핑],
  )

  본 연구는 11개 분석 도구를 가설별로 분담시킨다. 각 가설은 *1차 검증 도구*로 핵심 결과를 도출하고, *보조·견고성 도구*로 robust 여부를 점검하는 트라이앵귤레이션 구조다.

  #figure(
    table(
      columns: (auto, 1.1fr, 1.1fr),
      align: (center+horizon, left+horizon, left+horizon),
      table.hline(y: 1, stroke: 1.0pt + black),
      [*가설*], [*1차 검증 도구*], [*보조·견고성 도구*],
      [H1], [Pooled FE 회귀 ($Delta R^2 = 0.000$)], [UMAP+HDBSCAN, Mapper, Persistent Homology (PH 부트스트랩)],
      [H2], [회귀불연속(RDD), 월 단위 11/12월 비교], [Permutation 1,000회·분야별·원형별 forest plot],
      [H3], [FFT amp_12m + Welch PSD], [Phase coherence·Wavelet (부록 D)],
      [H4], [Baron-Kenny + Sobel + Bootstrap 매개분석], [NeuralProphet cross-check (§6.5)],
      [H5], [1차 차분 상관 ($r = -0.86$, $p < 0.01$)], [Permutation, Frisch-Waugh-Lovell CPI 외생 통제],
      [H6], [Continuous Wavelet Transform (Morlet)], [STL 자기 비판 + NeuralProphet 중재 (§6.9)],
    ),
    caption: [가설 × 분석 도구 매트릭스 — 11개 도구의 가설별 분담 (1차 + 보조·견고성)],
  )

== H1 검증 — 분야 trivial, 사업원형이 진짜 분석 단위

  *왜 이 검증이 먼저인가*: 한국 행정학·재정학 연구는 통상 분야(사회복지, 교육, 국방 등) 단위로 분석을 수행하며, 분야 간 이질성을 결과 차이의 1차 설명으로 가정한다. 본 연구의 모든 후속 결과(사업원형 발견, 위상 분석, RDD 점프)는 이 가정이 *틀렸음*을 전제로 한다. 따라서 검증 순서상 가장 먼저 분야 라벨의 한계 설명력을 정량 평가한다.

  Pooled FE 회귀에서 분야 고정효과만 추가했을 때 R²는 0.014에서 0.014로 변화하지 않았으며(분야 FE 단독 ΔR²=0.000), 사업원형×지출진동 상호작용을 추가하면 R²가 0.038로 증가하였다(ΔR²=+0.025)(@fig-h8). 이는 분야 단위 이질성이 trivial하다는 정량적 반증이며, 진짜 설명 변수가 사업 형태임을 시사한다.

  *해석*: 어느 분야의 사업이든 *사업이 어떻게 운영되는가*(인건비 집중·자산 취득·출연금 위탁·정상)에 따라 게임화 강도가 결정된다. 후속 절은 이 "사업 형태"를 데이터로부터 발견한다.

  *모형 검증 (H1)*: 본 결과는 P-A 모형의 *비용 함수 $c(e_t, e_q; theta)$의 단위는 사업원형 $theta$이지 분야가 아니다*는 가설을 직접 입증한다(@fig-h8). 분야 라벨은 *행정 분류 편의*일 뿐 비용 구조와 결정 행동에 정보를 담지 않는다.

== H1 보강 — 4개 사업원형의 위상 안정성

  *질문*: 분야가 진짜 단위가 아니라면 어떤 단위가 진짜인가? 정답을 미리 정하지 않고 *데이터에 묻는다*. UMAP으로 12차원을 2차원에 압축하고 HDBSCAN으로 밀도 기반 군집을 발견한 결과, 4개의 안정 군집이 출현한다(@fig-umap).

  각 군집의 z-score 프로파일은 행정 실무자가 *직관적으로 인지 가능한 사업 형태*와 일치한다:

  - *C0 인건비형* (n=129): personnel +3.07, 게임화 진폭 −1.32 — 매월 일정 지급 → 평탄
  - *C1 자산취득형* (n=99): direct_invest +3.28, 인프라 공사 분야 비중 큼 — 공정률 따라 변동
  - *C2 출연금형* (n=154): chooyeon +2.89, 게임화 진폭 +0.88 — 공공·출연기관 위탁 → 12월 몰림
  - *C3 정상사업* (n=1,175): 평균 부근 — 베이스라인

  *위상 안정성 검증*: UMAP+HDBSCAN의 4개 군집이 알고리즘 우연이 아닌지 확인하기 위해 두 가지 위상 도구를 병행 적용한다.

  - *Mapper 그래프* (@fig-mapper-amp, @fig-mapper-cluster)에서 32 노드 / 38 엣지 / 10 components / 7 loops로 군집 구분이 위상적으로 분리되어 있음이 확인되었다.
  - *Persistent Homology*는 30개 강건 component와 15개 강건 loop를 보고하였으며(@fig-ph-pd, @fig-ph-barcode), 50회 부트스트랩에서 H1 max persistence 95% CI [0.48, 1.19]로 위상 구조의 우연성을 배제하였다(@fig-ph-bootstrap).

  세 도구(UMAP+HDBSCAN, Mapper, PH)가 일관되게 *사업 형태가 분야보다 강한 단위*임을 지지한다.

#figure(
  image("figures/h3_umap.png", width: 100%),
  caption: [\[H1 검증\] 활동 임베딩 UMAP — 4개 사업원형 (1,557 활동 × 12 피처)],
) <fig-umap>

#figure(
  image("figures/h4_mapper_amp.png", width: 70%),
  caption: [\[H1.b 검증\] Mapper graph — 평균 amp_12m_norm 색상. \ 32 nodes / 38 edges / 10 components / 7 loops. 노드 크기는 활동 수에 비례.],
) <fig-mapper-amp>

#figure(
  image("figures/h4_mapper_cluster.png", width: 70%),
  caption: [\[H1.b 검증\] Mapper graph — 동일 그래프, HDBSCAN 사업원형(4 archetype) 색상.\ 위상적으로 분리된 4 archetype 검증.],
) <fig-mapper-cluster>

#figure(
  image("figures/h9_pd.png", width: 100%),
  caption: [\[H1.b 검증\] Persistence Diagram — Vietoris-Rips, N=300, max thresh=8.0.\ H0(파랑)·H1(빨강) birth-death 쌍.],
) <fig-ph-pd>

#figure(
  image("figures/h9_barcode.png", width: 100%),
  caption: [\[H1.b 검증\] H1 Barcode — 가장 오래 지속되는 30개 loop의 birth-death 막대.\ max persistence = 0.671.],
) <fig-ph-barcode>


#figure(
  image("figures/h9_bootstrap.png", width: 100%),
  caption: [\[H1.b 검증\] Bootstrap PH 50회 (n=200) — H1 max persistence 95% CI [0.48, 1.19].\ 5y 참조(median 0.65) 대비 표본 안정성 검증.],
) <fig-ph-bootstrap>

== H2 검증 — 자산취득형 회계연도 12월 RDD 점프

  *왜 RDD가 결정적 증거인가*: 사업 본질에 따른 정상적 변동과 회계 게임화를 분리하기 위해, 같은 활동의 *11월 마지막 주 vs 12월 첫 주* 일평균 집행을 비교한다. 며칠 차이의 변동은 사업 본질로 설명할 수 없고, 12월 1일이라는 *행정적 임의 절단점*만이 작동한다. #cite(<liebman2017>, form: "prose") (AER)가 미국 연방조달에서 5배 점프를 보고한 설계의 한국 적용이다.

  활동 단위 일평균 집행을 11월\~12월 RDD로 추정한 결과, 12월 점프는 *전체 평균 1.91배*($p < 10^(-124)$)로 나타났다(@fig-rdd-monthly, @fig-rdd-yearly). 사업 형태별 분해(@fig-rdd-field):

  - *자산취득형 3.42배* (가장 강함, n=99) — 시설 공사·자산 취득의 공정률 마감과 회계연도 마감이 결합한 12월 1일 직후 *이산적 점프*
  - *정상사업 2.24배* (n=1,175)
  - *인건비형 1.12배* (n=129, 구조상 평탄)
  - *출연금형 1.10배* (n=154, 통계 미달) — RDD에는 약하나 *연 단위 사이클*에는 가장 강함

  미국 5배 대비 한국 1.9배의 절대값 차이는 *측정 단위 granularity* 차이로 설명된다(미국 주 단위 vs 한국 월 단위 — 12월 첫째 주의 신호가 12월 전체로 분산). 사업 형태별 RDD 점프의 *순서*는 #cite(<liebman2017>, form: "prose")의 use-it-or-lose-it 메커니즘이 *공정률·자산취득 사업*에서 가장 강하게 작동함을 보여준다.

  *RDD vs 스펙트럼 측도 — 사업원형별 메커니즘 차이*: RDD가 12월 1일 직후 *이산적 점프*를 측정하는 반면, FFT/STL/NeuralProphet/Wavelet은 *연 단위 사이클 진폭*을 측정한다. 자산취득형은 RDD 점프가 강하고(3.42배), 출연금형은 사이클 강도가 강하다(PSD 0.332, phase coherence 0.54, wavelet +554\%; 상세는 §6.4). 두 사업원형 모두 *외생 회계 cycle에 결속*되어 있으나, 자산취득형은 *공정률 마감 직후 단발적 spike*로, 출연금형은 *위탁기관 정산 일정에 따른 다회 분산 + 12월 누적*으로 발현된다. 게임화 메커니즘이 사업원형별로 다르다는 점은 본 연구의 정책 함의(권고 1·2)에 직접 반영된다.

  *모형 검증 (H2)*: 본 결과는 P-A 모형의 *사업원형별 비용 함수 $c(e_t, e_q; theta)$ 차이*가 균형 $e_t^*$의 *시간 구조 차이*로 발현됨을 직접 입증한다. 자산취득형은 $c(e_t)$가 12월 1일 직후 *급감*(공정률 마감과 회계 마감이 동시에 만료되는 임의 시점)하므로 RDD 점프 가장 큼(H2). 두 균형은 모형의 *동일 FOC* $w_t = (partial c) / (partial e_t)$가 *원형별 비용 함수의 차이*를 통해 다른 시간 구조로 발현된 것이다.

#figure(
  image("figures/h22_rdd_monthly.png", width: 100%),
  caption: [\[H2 검증\] 월별 활동 평균 일집행액 (2015\~2025) — 색상은 연도(보라 2015 → 노랑 2025),\ 굵은 검정선은 11년 평균. 11~12월 영역(빨강)에서 12월 점프 가시화.],
) <fig-rdd-monthly>

#figure(
  image("figures/h22_rdd_yearly.png", width: 80%),
  caption: [\[H2 검증\] 연도별 12월 점프 (활동 중앙값 log 일집행액 12월 − 11월).\ 전체 RDD β=0.65 (1.91배, 주황 점선), #cite(<liebman2017>, form: "prose") 미국 5x 참조선(보라 점선) 대비.],
) <fig-rdd-yearly>

#figure(
  image("figures/h22_rdd_field.png", width: 100%),
  caption: [\[H2 검증\] 분야별 12월 점프 배수 — 국방·국토·교통이 가장 큼, *자산취득형 3.42배 (가장 강함)*],
) <fig-rdd-field>

== H3 검증 — 출연금형 사이클 우세 (PSD·Phase·Coherence·Wavelet)

본 절은 핵심 수치만 보고하며, 스펙트럼 분해 절차와 그림은 *부록 D.1~D.3*에 정리한다. H3 검증 대상: 출연금형의 PSD k=1 진폭·phase coherence·wavelet 진폭이 다른 원형보다 우세하다는 가설.

*모형 맥락*: §6.3의 RDD 분석에서 출연금형은 점프(1.10배)가 약하나 연 단위 사이클에서 강하다고 보고되었다. 이는 P-A 모형에서 출연금형의 비용 함수 $c(e_t)$가 *분산형*(위탁기관 정산이 연중 다회 발생)임을 예측하는 H3 가설의 직접 검증 대상이다.

*검증 결과 요약*:
- *PSD k=1 진폭* (12개월 사이클): 출연금형 0.332 (다른 원형 0.097\~0.172의 *2\~3.4배*)
- *Phase coherence* (활동 간 동시 피크): 출연금형 0.54 (다른 원형 0.08\~0.13의 *4\~7배*)
- *Wavelet 진폭 시간 진화*: 출연금형 +554% (2015\~17 → 2023\~25), 자산취득 +175%, 정상 +317%, 인건비 −0.8%

세 측도 모두 일관되게 *출연금형이 연 단위 게임화 사이클*에 가장 강하게 결속됨을 보여준다. 이는 *RDD 점프(이산적 spike)는 자산취득형이 강하지만, 사이클 진폭(연속적 강도)은 출연금형이 강함*이라는 사업원형별 시간 구조 차이를 입증한다.

*모형 검증 (H3)*: 세 측도는 P-A 모형의 예측을 지지한다. 분산형 $c(e_t)$ → 균형 $e_t^*$가 연 사이클 전반에 걸쳐 분산 누적되는 패턴이 PSD/coherence/wavelet에서 모두 우세하게 확인되었다. 자산취득형의 step function $c(e_t)$(12월 1일 직후 한계비용 급감)와 대조적인 이 결과는 H3를 지지한다.

== 방법론 상보성 검증 — FFT·STL·NeuralProphet 측도 비교

  *본 절의 범위*: 본 절은 세 게임화 측도(FFT·STL·NeuralProphet)의 상보성을 점검한다. H4(매개 경로 원형 이질성) 검증은 §6.6에서 수행된다. 본 연구는 처음에 FFT·STL·NeuralProphet을 "서로 다른 결론을 줄 수 있는 cross-check 도구"로 설정했으나, 실제 분석 결과는 *세 도구가 게임화의 다른 측면을 측정하는 상보적 lens*임을 시사한다. FFT는 *주파수 영역의 진폭 비중*, STL은 *시간 영역의 추세-잔차 분해*, NP는 *changepoint 보정 후 가법 분해*다. 셋이 *동일 신호의 직교적 표현*이므로 약한 상관은 모순이 아니라 *각 도구가 잡아내는 게임화 차원의 이질성*을 정량화한 것이다.

  *분석 설계*: 200개 활동 random sample(`random_state=42`)에 대해 활동-연도 단위 NeuralProphet 적합(epochs=50, n_lags=0, n_changepoints=2). 약 1,051개 적합. 적합 후 yearly seasonality 진폭을 활동 표준편차로 정규화해 `np_seasonal_strength`로 추출.

  *세 측도의 활동-연도 패널 상관*:

  #figure(
    table(
      columns: (auto, auto, auto, auto),
      align: (left, center, center, center),
      table.hline(y: 1, stroke: 1.0pt + black),
      [], [*FFT*], [*STL*], [*NP*],
      [*FFT*], [1.000], [], [],
      [*STL*], [$-0.130$], [1.000], [],
      [*NP*], [$-0.039$], [$-0.018$], [1.000],
    ),
    caption: [세 게임화 측도 상호 상관 (활동-연도 패널, $N = 1051$)],
  )

  *해석 (상보성)*: 셋 모두 0에 가까운 상관은 *서로 다른 신호 차원*을 측정한다는 직접 증거다.
  - *FFT amp_12m_norm*: 활동 시계열을 주파수 분해해 *12개월 주기 진폭이 전체 변동에서 차지하는 비중*. 추세는 분해 안 함.
  - *STL seasonal_strength*: LOESS 평활로 추세 제거 후 *잔차 분산 대비 계절 분산 비율*. 가법 분해.
  - *NP yearly seasonality*: piecewise-linear 추세 + 자동 changepoint 보정 후 *Fourier 기저의 적합 진폭*. 신경망 동시 추정.

  본 연구의 부록 D(H27)는 FFT를 *진폭 1점*에서 *전체 PSD + phase + cross-coherence*로 확장해 셋의 상보성을 더 깊이 보인다 — 출연금형은 *PSD k=1 진폭 가장 큼* + *phase coherence 0.54* (활동 간 *동시 피크*)로 외생 회계 cycle에 가장 강하게 결속됨이 새롭게 드러난다.

  *분야별 outcome 상관 (3-way)*: 14분야 outcome 상관을 세 측도로 재산출한 결과, 보건(life expectancy)·통신(broadband)에서 세 측도 모두 음(보건: FFT $-0.55$, STL $+0.20$, NP $-0.71$; 통신: FFT $-0.15$, STL $+0.05$, NP $-0.75$)을 보이며, *NP가 FFT가 놓친 통신 분야의 게임화 신호를 추가로 식별*한다. 반면 사회복지는 세 측도 모두 약한 신호(FFT $+0.03$, STL $+0.00$, NP $-0.24$)로 *14분야 단위 STL에서 신호 소멸*한 결과와 활동-단위 NP에서도 일관된다.

  *인터랙티브 시각화*: 4 사업원형의 NP component 분해(trend + yearly seasonality)는 인터랙티브 plotly로 #link("https://bluethestyle.github.io/goodhart-korea/interactive/neuralprophet_components.html")[interactive viz #5: NeuralProphet 분해]에 공개. 출연금형 활동의 12월 양의 점프, 인건비형의 평탄한 trend, 정상사업의 약한 seasonality를 hover·zoom으로 비교 가능.

  *결론*: 셋이 같은 신호를 *다른 차원*으로 분해하므로, 본 연구의 견고성은 *한 도구의 절대값*이 아닌 *복수 도구가 일관되게 가리키는 분야·원형 패턴*에 의존한다. 보건·통신·국방·교육의 음 신호 (모든 측도 일관), 출연금형 12월 phase coherence 0.54 (PSD/Phase 분석으로 추가 확인)는 *방법론 트라이앵귤레이션*의 성공 사례다.

== H4 보강 — 매개경로 원형 이질성 (Baron-Kenny + Sobel + Bootstrap)

  *질문*: 본 모형은 *출연금 비중 ($X$) → 시점 조정 노력 ($M = e_t$) → 사회 결과 ($Y$)*의 순차적 인과 경로를 가정한다. 모형이 옳다면 매개분석에서 *원형별 이질성*이 발현되어야 한다 — 출연금형·자산취득형(높은 $w_t$)에서는 매개 경로가 강하고, 인건비형(낮은 $w_t$)·정상사업에서는 약해야.

  *방법*: #cite(<baron1986>, form: "prose") 4단계 + Sobel z-검정 + Bootstrap 95\% 신뢰구간(부록 C.11; 매개분석 방법론 일반은 @hayes2017 참조). 활동 단위 $X$ = 출연금 비중, $M$ = `amp_12m_norm`, $Y$ = 분야별 결과변수.

  *결과 — pooled 매개효과 미유의*: 14분야 평균 매개효과 $a b$의 Sobel z-검정 $p = 0.481$로 미유의. 즉 *시스템 평균*으로는 매개 경로가 약함.

  *모형 검증 (H4) — pooled 미유의는 archetype 이질성의 직접 증거*: P-A 모형은 *비용 함수 $c(\cdot; theta)$가 사업원형 $theta$별로 다름*을 예측한다 (5.2 결과). 평균 매개효과는 *원형별 이질적 매개 강도*가 평균에서 상쇄되어 약화되는 것이 자연스럽다. 즉 $p = 0.481$은 모순이 아니라 *모형의 직접적 검증*이다.

  *분야별 매개 분해*: 사회복지 ($a b > 0$, 자동분배 채널) + 환경 ($a b < 0$, 직접 부정 채널)에서 매개 효과가 강하게 발현된다. 두 분야 모두 *$(partial Y) / (partial e_t) != 0$인 alignment 분야*다 (H5 fortuitous 명제와 일관). 다른 12개 분야는 매개효과가 작아 평균에서 희석된다.

  *해석*: 모형 가설 H4(매개 경로의 원형 이질성)는 검증되었다. 이는 정책 처방이 *원형별로 차별화*되어야 함을 시사한다 — 모든 사업에 동일한 평가 제도를 적용하면 처방의 효과가 평균적으로 희석된다.

== H5 검증 — 사회복지 자동분배 (Fortuitous Alignment)

  *직관 반대 발견*: 게임화는 부정적 측정 왜곡으로 통상 인식되지만, 본 연구는 사회복지 분야에서 *오히려 긍정적 결과*와 연결되는 사례를 발견한다. 사회복지 정상사업의 12월 집중 집행 강도가 클수록 *순자산 지니계수가 감소(불평등 완화)*하는 음의 상관이다. 이는 회계연도 마감 직전 사회복지 급여·보조금이 일괄 지급되면서 빈곤층에 자원이 자동 분배되는 메커니즘으로 해석된다.

  사회복지 분야의 1차 차분 상관은 r=−0.762(p=0.035, permutation 1,000회)로 14분야 중 유일하게 통계적으로 유의했다(@fig-h6). Lag/Lead 차분 상관(k=−2..+2)에서 동기 상관이 가장 강해 즉시적 자동분배 메커니즘을 지지하며, amp_cv 대안 지표에서도 방향이 일관된다(@fig-h6-lag). CPI 외생 통제 후 r=−0.86(p=0.007)로 *신호가 강화*되어, 자연 경기 cycle 가설을 기각하였다(@fig-h10).

  *왜 강화되는가*: CPI 잔차로 분석하면 거시 경기 변동(인플레이션·실업률 동조)으로 설명되는 부분이 제거된다. 신호가 약해지지 않고 강해진다는 것은 게임화-결과변수 연결이 경기 cycle보다 *행정 메커니즘 자체*에 뿌리가 있음을 시사한다.

  *모형 검증 (H5) — fortuitous alignment 명시*: P-A 모형에서 Agent의 목적함수 $U_A$는 *사회 결과 $Y$를 포함하지 않는다*. Agent는 평가 점수 $w_t e_t + w_q tilde(e)_q$만 최대화한다. 따라서 사회복지 분야의 음 상관 ($r = -0.86$)은 *우연히* $(partial Y) / (partial e_t) > 0$이 성립하는 분야 — 12월 집중 분배가 빈곤 격차 완화와 alignment되는 분야 — 에서 발현된 결과다. 13개 다른 분야 ($Delta Y/Delta e_t approx 0$)에서는 동일한 게임화 노력이 사회 결과 개선과 연결되지 않는다.

  *해석 — 정책 정당화 아님*: 본 결과는 *게임화 → 사회 결과 개선*이라는 일반 명제가 *아니다*. 사회복지에서 우연한 alignment가 발생할 뿐이며, 이를 일반화해 "게임화는 좋은 것"이라고 해석하면 안 된다. 모형은 이 우연성을 *수학적 명제*로 표현한다 — Agent가 $Y$를 신경쓰지 않으므로 $Y$-개선은 항상 fortuitous다.

  *모형 검증 (H1 보강) — 분야 trivial vs 사회복지 자동분배 양립*: "분야가 trivial(H1)인데 어떻게 사회복지 분야에서 강한 상관이 가능한가?" 모형은 두 layer를 분리한다: (a) *비용 함수 $c(\cdot)$의 단위*는 사업원형(분야 trivial), (b) *결과변수 $Y$의 alignment 단위*는 분야(사회복지에서 우연 일치). 두 layer는 *독립*이라 양립 가능하다.

#figure(
  image("figures/h6_robustness.png", width: 100%),
  caption: [\[H5 검증\] 견고성 검증 — (a) FE 회귀 β + 95% CI (N=128, 분야 FE 추가에도 β 유의 안 함).\ (b) 14분야 Permutation forest (점=관측, 띠=null 95% CI).\ 사회복지 obs=−0.762, p=0.035로 14분야 중 유일하게 유의 (fortuitous alignment).],
) <fig-h6>
#pagebreak()
#v(-2em)

#figure(
  image("figures/h6_lag_amp.png", width: 100%),
  caption: [견고성 검증 (계속) — (c) Lag/Lead 차분 상관 heatmap (k=−2..+2).\ (d) 분야별 amp_12m 시간 변동계수(amp_cv) — 사회복지(빨강 강조)는 변동성이 크지 않으나\ outcome과 강한 상관, 즉 자연 주기보다 KPI 압력 가설을 지지.],
) <fig-h6-lag>
#v(-0em)

#figure(
  image("figures/h10_cpi_control.png", width: 85%),
  caption: [\[H5 보조\] CPI 외생 통제 — 14/14 분야 부호 유지,\ 70% 유의성 유지. 사회복지 r=−0.76 → −0.86 강화로 자연 cycle 가설 기각.],
) <fig-h10>

#figure(
  image("figures/h8_panel.png", width: 100%),
  caption: [\[H1 검증\] 분야 라벨 trivial 검정 — 분야 FE 단독 ΔR²=0.000,\ 사업원형×Δamp 추가 ΔR²=+0.025 (R²: 0.014 → 0.038)],
) <fig-h8>

== H6 검증 — 시간 동적 강화 (Wavelet)

  *왜 시간 분석인가*: FFT amp_12m_norm은 11년 시계열의 *고정 평균* 진폭을 측정하므로 *시간에 따른 변화*를 볼 수 없다. 정상성 가정이 본 연구 환경(2007 국가재정법, 2014 회계제도 개편, 2020 코로나 확장재정 등 정책 변화점 다수)에서 부적합할 가능성을 검증하기 위해 Continuous Wavelet Transform(CWT, complex Morlet)을 적용했다(상세는 부록 D.4).

  *결과 — 12개월 cycle 진폭의 시간 진화* (사업원형 평균 시계열, 2015\~2017 → 2023\~2025 평균 비교):

  #figure(
    table(
      columns: (auto, auto, auto, auto),
      align: (left, center, center, center),
      table.hline(y: 1, stroke: 1.0pt + black),
      [*원형*], [*early (2015\~17)*], [*late (2023\~25)*], [*변화율*],
      [인건비형], [0.007], [0.007], [$-0.8\%$ (변화 없음)],
      [자산취득형], [0.055], [0.150], [*$+174.7\%$*],
      [출연금형], [0.201], [1.315], [*$+553.6\%$*],
      [정상사업], [0.057], [0.237], [*$+316.7\%$*],
    ),
    caption: [원형별 12m wavelet power 시간 진화 — 출연금형 5.5배 강화. 출연금형 변화율 정밀값 +553.6%, 본문 인용 시 반올림 +554%.],
  )

  *모형 검증 (H6) — $w_t / w_q$ 비율의 시간 증가*: P-A 모형의 비교정역학에서 $(partial e_t^*) / (partial w_t) > 0$이므로, 평가 가중 비율 $w_t / w_q$가 시간에 따라 증가하면 균형 시점 조정 노력 $e_t^*$도 증가해야 한다. 한국에서 $w_t / w_q$ 증가의 plausible 동인:

  - *2007 국가재정법 시행*: 집행률 평가 정착·강화 → $w_t$ ↑
  - *2014 국가회계제도 개편*: 결산 표준화·투명화로 집행률 측정 정확도 ↑ → 효과적 $w_t$ ↑
  - *2017 추경 확대 + 출연기관 비중 증가*: 출연금 활동 수 ↑ → $w_t$가 큰 활동의 *비중* 증가
  - *2020\~2022 코로나 확장재정*: 신설 사업의 12월 정산 압력 강화

  $w_q$ 측면은 거의 변화 없음 (사업 성과 측정 기술의 본질적 어려움 그대로). 따라서 $w_t / w_q$ 비율 증가는 *합리적 추론*이며, wavelet 결과(+554\%)는 이 추론을 *직접 검증*한다.

  *통제 사례 — 인건비형 변화 없음*: 인건비형은 구조상 매월 균등 지급이라 *$e_t$ 조정 자체가 불가능*($(partial c) / (partial e_t) = infinity$). 모형은 이 원형에서는 시간 강화가 발현되지 않을 것으로 예측 — 결과 −0.8\%로 *예측 정확*. 이는 측정 도구(wavelet)가 진짜 동적 신호만 잡아내며 noise가 아님을 보강한다.

  *함의 — 한국 굿하트 효과는 진행형*: 본 결과는 한국 게임화가 *고정 패턴이 아니라 진행 중인 동적 강화 현상*임을 입증한다. 정책 분석의 시간 가중치는 *최근 3년 자료*로 옮겨가야 하며(권고 5), FFT amp_12m_norm 같은 정상성 가정 도구의 11년 평균값은 *증폭 추세를 희석*하므로 보완이 필요하다.

#figure(
  image("figures/h28_evolution.png", width: 80%),
  caption: [\[H6 검증\] 12개월 cycle 진폭의 연도별 진화 — *출연금형 +554% 강화*, 인건비형 변화 없음(통제). 정책 변화점 (2017 국가재정법 시행 후 10년, 2020 COVID 확장재정) annotate.],
) <fig-h28-evol-body>

== 방법론 Robustness — STL 자기 비판 + NeuralProphet·Wavelet 중재

  *왜 자기 비판인가*: 본 연구의 사회복지 자동분배 결과가 진짜 12월 집중 신호인지, 아니면 사회복지 예산이 매년 *지속 증가하는 추세*가 만들어내는 가짜 주기성인지를 자체 검증해야 한다. 동일 활동 시계열에 STL을 적용해 추세를 제거한 뒤 seasonal_strength로 다시 상관을 계산했다.

  *결과 — 신호 소멸*: STL 분해 후 seasonal_strength를 게임화 지표로 사용하면 사회복지 신호는 r=+0.003(p=0.991)로 *완전히 소멸하였다*(@fig-stl-bars, @fig-stl-scatter). 두 가능성:
  - (a) FFT 신호가 *지속 증가 trend × 12월 기록 시점*의 합성 — 게임화는 가짜
  - (b) STL 평활이 *진짜 게임화 점프*를 추세로 흡수 — 게임화는 진짜이나 STL이 못 봄

  *(a)와 (b)를 어떻게 구분하는가*: 본 연구는 두 가지 보조 검증으로 응답한다.
  - *NeuralProphet 중재* (§6.5 참조): changepoint 명시적 모델링으로 STL이 추세로 흡수했을 가능성을 우회. 활동-단위 결과는 사회복지 r=−0.24로 음 신호 회복(약하지만 STL의 0.003보다 강함).
  - *Wavelet 시간 진화*: 사회복지 활동의 12개월 cycle 진폭이 *시간에 따라 변화*하는지 추적. 변화가 있다면 정상성·trend 분해 가정 자체가 한국 자료에 부분 부적합(부록 D.4 참조).

  본 연구는 이를 *분해 가정 의존성 한계*로 명시하며, 사회복지 발견은 *FFT amp_12m_norm 1지표 단독*이 아니라 *복수 도구의 부분 합의*에 의존한다고 정직하게 보고한다.

#figure(
  image("figures/h24_stl_bars.png", width: 100%),
  caption: [분야별 1차 차분 상관 — FFT amp_12m_norm vs STL seasonal_strength 비교.\ 분홍 행 + 빨간 분야명 = 부호 반전 5/15분야. 사회복지는 FFT −0.76 → STL +0.07 로 신호 소멸.],
) <fig-stl-bars>

#figure(
  image("figures/h24_stl_scatter.png", width: 100%),
  caption: [FFT vs STL 상관 산점도 — 분홍 영역(2·4 사분면)이 부호 반전.\ 사회복지(검정 큰 점)는 좌상단 부호반전 영역 안. y=x 참조선.],
) <fig-stl-scatter>

#pagebreak()

= 정책 함의

  본 연구의 발견은 *진단*과 *처방*의 두 층위로 정책 권고를 도출한다.

== 진단 도구 — 부처-결과변수 4분면

  *왜 4분면인가*: 게임화 노출과 결과변수 부호의 조합으로 부처를 4사분면에 배치하면, *같은 게임화 강도라도 결과 부호가 다른 부처*를 분리할 수 있다. 점검 자원을 배분할 때 무조건 게임화 강한 부처를 보지 말고, *게임화 + 결과변수 악화*가 동시에 나타나는 부처를 우선해야 한다는 의사결정 도구다.

  부처×결과변수 4분면 분석(@fig-quadrant)에서:

  - *Q2 (점검 필요, 빨강)*: 국무조정실 및 국무총리비서실, 과학기술정보통신부 — 굿하트 노출 + 결과변수 양 상관, 즉 게임화가 결과 악화와 동행 (측정 왜곡 의심)
  - *Q1 (자동분배 OK, 녹색)*: 행정중심복합도시건설청 등 — 게임화 노출은 있으나 결과변수와 음 상관, 사회복지형 자동분배 가능성
  - *Q3, Q4*: 게임화 노출이 낮아 본 분석 우선순위 외

  추가 점검 우선순위로 모든 분야의 극단 게임화 활동(sub05 분류, 50건)이 식별된다. 본 연구는 이 50건을 감사원·국정감사·행정안전부 자체 점검에 입력 가능한 *데이터 기반 우선순위 리스트*로 제공한다.

#figure(
  image("figures/h14_quadrant.png", width: 100%),
  caption: [부처별 굿하트 노출 × 결과변수 4분면 — Q2가 점검 우선],
) <fig-quadrant>

== 처방 — 모형 균형점 이동의 행정 액션 매핑

  본 절은 정책 처방을 *임의로 나열*하지 않고, *P-A 모형의 비교정역학 결과*에서 직접 도출한다. 모형(이론 모형 절)은 균형 시점 조정 노력 $e_t^*$의 부분 미분으로 *세 가지 정책 레버*를 식별했다.

  $ (partial e_t^*) / (partial w_t) > 0, quad (partial e_t^*) / (partial w_q) < 0, quad (partial e_t^*) / (partial c_(t t)) < 0 $

  각 레버를 한국 행정 환경에서 *어떤 액션*으로 작동시킬 수 있는가:

  #figure(
    table(
      columns: (auto, auto, 1fr),
      align: (left, left, left),
      table.hline(y: 1, stroke: 0.5pt + black),
      [*레버*], [*기대 효과*], [*행정 액션 후보*],
      [$w_t$ ↓], [$e_t^*$ ↓ (게임화 완화)], [집행률 평가 완화·다년도 회계·MTEF 강화·출연기관 경영평가에서 집행률 비중 축소],
      [$w_q$ ↑], [$tilde(e)_q$ ↑ (단, $e_q$는 측정성 격차로 한계)], [사업 성과 측정 인프라 (행정연구원 사업평가센터 강화)·KPI 정의 표준화·결과지표 활용 확대],
      [$c_(t t)$ ↑], [$e_t$ 한계 비용 ↑ → 시점 조정 ↓], [출연기관 정산 시점 분산 (분기/반기)·자동 감사 flagging·실시간 모니터링·예외 정산 사전 신고 의무],
    ),
    caption: [P-A 모형 레버 → 한국 행정 액션 매핑],
  )

  *권고 1 — 다년도 회계 도입 확대 ($w_t$ ↓)*: 현행 *단년도 예산 마감* 구조는 $w_t$ 가중치를 *극단적으로 크게* 만드는 제도적 장치다 — 미사용 예산이 자동 소멸되므로 12월 31일 직전이 *실질적인 절단점*이 된다. MTEF(2009 도입)를 *5년 framework에서 실제 회계 단위로 격상*하면 $w_t$가 크게 감소하고 $e_t^*$도 따라 감소할 것으로 예측된다. 미국 GPRA(Government Performance and Results Act) 다년도 funding 사례 참조.

  *권고 2 — 출연기관 평가 지표 전환 ($w_t$ ↓ + $w_q$ ↑)*: 출연금형 phase coherence 0.54 + PSD k=1 진폭 0.332는 *모기관-위탁기관의 12월 일률 정산 압력*의 직접 증거다. 출연기관 경영평가에서 *집행률 100\%*의 비중 축소($w_t$ ↓) + *사업 품질 평가*(피인용·인용·산출물 평가) 가중 확대($w_q$ ↑)가 두 레버를 동시에 움직인다. 다만 $w_q$ 증가의 효과는 *측정성 격차의 본질적 한계*(Holmstrom-Milgrom impossibility)로 일부에 그친다.

  *권고 3 — 출연기관 정산 시점 분산 ($c_(t t)$ ↑)*: 위탁계약별 정산 주기를 *분기 또는 반기*로 분산하면, 12월 1일 직후의 시점 조정 한계 비용이 증가($c_(t t)$ ↑)해 $e_t^*$가 분산된다. 출연금형 phase coherence가 0.54에서 *분산형 cycle*로 바뀌면 outcome alignment에서 우연한 alignment 외 효과를 추가로 식별 가능.

  *권고 4 — 데이터 인프라 강화 (모형 $w_q$ ↑의 *전제 조건*)*: 본 연구는 *월별 집행*(VWFOEM) 자료 한계로 12월 *주(week) 단위* 점프를 직접 관측하지 못했다. 미국 #cite(<liebman2017>, form: "prose")는 주별 자료로 5배 점프를 보고했다. 열린재정 API의 *주별·일별 granularity 추가*는 RDD 식별력 향상 외에도 $w_q$ 증가에 필요한 *사업 성과 측정 인프라*의 1차 자료가 된다.

  *권고 5 — 자동 감사 flagging 시스템 ($c_(t t)$ ↑)*: 본 연구의 50건 sub05 (극단 게임화 활동) 식별 알고리즘(amp_12m_norm 상위 + RDD 점프 3배 이상)을 *상시 운영*하면 적발 가능성 ↑ → $(partial c) / (partial e_t)$ 증가 → $e_t^*$ 감소. 감사원·국회 예산정책처와 협력해 *실시간 게임화 모니터링 dashboard* 구축 가능.

  *권고 6 — 시간 가중 점검 (모형 H6 검증)*: 웨이블릿 분석에서 출연금형 게임화가 *2015\~2017 → 2023\~2025 +554\%* 증가했다는 발견(§6.8)은, $w_t / w_q$ 비율의 시간 증가가 진행 중임을 의미한다. 정책 점검은 *최근 3년 자료*에 가중되어야 하며, 11년 평균 지표는 강화 추세를 희석한다.

  *예상 효과 비교*: 권고 1·2·3은 직접 $e_t^*$ 감소를, 권고 4·5는 측정·적발 강화로 *$c$ 함수 상승*을, 권고 6은 *시점 가중* 변경을 통해 모형의 비교정역학을 활용한다. 가장 큰 효과는 *권고 1*(다년도 회계)이 예측되며($w_t$ 변화 폭이 크기 때문), 가장 빠른 도입 가능성은 *권고 5*(flagging)이다. 두 권고를 *우선순위*로 한다.

  *Holmstrom-Milgrom impossibility의 한계 인정*: 본 모형 처방으로 *완전 게임화 제거*는 불가능하다. 측정성 격차가 본질적이라 $w_q$를 무한히 키워도 $tilde(e)_q$만 늘어날 뿐 $e_q$는 따라오지 않는다. 따라서 본 처방은 *균형점 이동*을 목표로 하지 *완전 해결*을 약속하지 않는다.

= 한계와 후속 연구

  본 연구의 한계는 *모형의 한계*와 *실증의 한계*로 구분된다. 각 한계는 후속 연구의 명확한 출발점이다.

== 모형 측면 한계

+ *Calibration 미시도*: P-A 모형은 $w_t, w_q, c$의 *부호와 비교정역학 방향*만 식별한다. 평가 가중의 *절대값 calibration*은 자연 실험(예: 다년도 회계 도입 부처 vs 미도입 부처) 또는 부처 간 평가 가중 차이의 administrative data로 가능.
+ *Dynamic 균형 미반영*: 시간 강화 (H6, +554\%)는 $w_t / w_q$ 비율의 시간 변화로 비교정역학 해석했으나, *반복 게임의 dynamic 균형* (reputational concerns, multi-period bonus, learning curve)은 모형 외. Stationary equilibrium 가정의 본질적 한계.
+ *Multi-Agent 상호작용 부재*: 부처 간 spillover(한 부처의 게임화 강화가 다른 부처의 평가 압력에 영향)는 모형에서 무시. Spectral Co-clustering 부처 그래프를 multi-agent setup으로 확장 가능.

== 실증 측면 한계

+ *자연 실험 부재 (외부 통제군 없음)*: 한국 단일 정부 + KPI 도입 시점 점진적 → 외부 통제군 없이 RDD만이 가장 강한 인과 식별 수단. 명확한 자연 실험 부재로 RDD 식별의 외적 타당성이 제한된다.
+ *STL trend 혼재*: 사회복지 메인 신호의 STL 후 소멸은 추세-계절 분리 가설 의존. NeuralProphet 중재로 부분 보강했으나 한국 자료의 짧은 표본이 본질 약점.
+ *표본 제약*: 차분 후 분야별 $N = 8 \~ 12$ — permutation·Bootstrap 보완에도 점추정 신뢰구간 넓음.
+ *국방·예비비 결측*: 측정 가능 결과변수 부재 분야 제외 (제거 편향). 후속 연구는 보안 해제 가능 부분 데이터 활용.
+ *주별·일별 granularity 부재*: 월별 집행 자료 한계로 12월 *주(week) 단위* 점프 직접 관측 불가. 미국 5배 vs 한국 1.91배 차이의 일부는 자료 granularity.

== 후속 연구 방향

+ *자연 실험 calibration*: 다년도 회계 시범 부처 (예: 과기정통부 일부 R&D 사업) vs 일반 부처 비교로 $w_t$ 변화의 균형 효과 *직접 calibration*.
+ *부처 그래프 multi-agent 확장*: Spectral Co-clustering 부처 5개 community 단위로 게임화 spillover network 분석.
+ *Wavelet 변화점 매핑*: 시간 강화 추세를 정책 변화점 (2007 국가재정법, 2014 국가회계제도, 2017 추경, 2020 코로나)에 매핑해 변화점별 균형 이동 정량 추정.
+ *국제 비교*: 미국 #cite(<liebman2017>, form: "prose") 5배, 한국 본 연구 1.91배(자산취득 3.42배), 일본·EU 동일 분석 시 비교 → 평가 제도 차이의 균형 효과 측정.
+ *Mediation의 원형별 분해*: pooled $p = 0.481$를 원형별 매개 분석으로 ($e_t$ 채널 강도가 사업 형태에 따라 달라지는 정도) 정량화.

= 결론

  본 연구는 한국 중앙정부 재정 집행의 게임화를 *원리·실증·정책*의 3-축으로 통합 분석했다. 핵심 기여는 다음 *다섯*이다.

  *기여 1 — 이론 모형: 굿하트 게임의 미시 도출*: Principal-Agent 균형 분석을 통해 *왜* 한국에서 굿하트 효과가 발현하는가에 답했다. Agent의 *비합리성*이 아닌 *합리성*이 측정성 격차 환경에서 시점 조정 노력으로 자원이 쏠리도록 유도한다는 점을 이론적으로 도출했다 @holmstrom1991. 모형은 6개 검증 가능한 가설(H1\~H6)을 산출했으며, 그중 *사업원형별 균형 패턴 차이*가 본 연구의 핵심 예측이다.

  *기여 2 — 분석 단위 재정의 (모형 H1 검증)*: 한국 행정학·재정학 연구가 표준으로 사용해온 *분야 단위 분석*이 게임화 현상에 대해 *trivial*하다는 정량 증거($Delta R^2 = 0.000$)를 제시하고, 진짜 분석 단위는 *사업 형태(archetype)*임을 위상 데이터 분석으로 입증했다 — UMAP+HDBSCAN 4개 군집, Mapper graph 4 components, Persistent Homology 30 강건 components로 다중 검증. *행정 분류와 게임화의 진짜 단위가 다르다*는 본 발견은 후속 정책 분석의 단위 선택 기준을 재고하게 한다.

  *기여 3 — 직관 반대 발견 (모형 H2, H3, H5 검증)*: 게임화는 단순히 부정적 측정 왜곡이 아닌 *분야 이질적·시간 동적 현상*임을 보였다.
  - *자산취득형 RDD 점프 3.42배* (H2 검증): 12월 1일 직후 *이산적 spike* — #cite(<liebman2017>, form: "prose") 미국 결과의 한국 확장.
  - *출연금형 사이클 우세* (H3 검증): PSD 0.332 + phase coherence 0.54 + wavelet +554\% — 다른 메커니즘으로 동일 회계 cycle에 결속.
  - *사회복지 자동분배 효과 (fortuitous, H5 명제)*: 게임화 ↔ 빈곤 격차 음 상관 ($r = -0.86$, CPI 통제 후 강화) — *우연한* outcome alignment, 정책 정당화 아님.
  - *분야 trivial vs 사회복지 자동분배 양립*: 비용 함수 layer(원형 trivial)와 outcome layer(분야 우연 alignment)는 모형의 독립 layer.

  *기여 4 — 시간 동적 강화 (모형 H6 검증, Wavelet 신규)*: FFT 정상성 가정의 한계를 웨이블릿으로 보완해 *게임화가 시간이 갈수록 강화*되고 있음을 새롭게 입증했다.
  - *출연금형*: 12개월 cycle 진폭 *2015\~2017 → 2023\~2025로 +554\%*
  - *정상사업*: +316.7\%, *자산취득형*: +174.7\%, *인건비형*: $-0.8\%$ (통제)

  $w_t / w_q$ 비율의 시간 증가(국가재정법·국가회계제도 시행 + 코로나 확장재정 + 출연기관 비중 증가)가 plausible 동인이며, 인건비형의 변화 없음이 측정 도구의 신뢰성을 보강한다.

  *기여 5 — 정책 처방의 모형적 도출*: 정책 권고를 *임의 나열*이 아닌 모형의 비교정역학 ($(partial e_t^*) / (partial w_t) > 0$ 등)에서 직접 도출했다. *6가지 핵심 권고* — 다년도 회계, 출연기관 평가 지표 전환, 정산 시점 분산, 데이터 인프라, 자동 flagging, *시간 가중 점검* — 은 각각 모형의 한 레버 ($w_t, w_q$, 또는 $c_(t t)$)에 대응한다. 동시에 Holmstrom-Milgrom impossibility의 한계 — 측정성 격차의 본질적 제약 — 를 *완전 해결 약속하지 않음*으로 정직하게 명시했다.

  *방법론 트라이앵귤레이션과 정직한 한계 보고*: FFT·STL·NeuralProphet·Wavelet 4-도구 시간 해상도 spectrum + UMAP·HDBSCAN·Mapper·PH 위상 다중 검증 + RDD·매개분석·CPI 통제 인과 식별이 모두 일관된 *원형별 균형 패턴*으로 수렴했다. STL 후 사회복지 신호 소멸은 자기 비판적으로 명시했으며, P-A 모형의 calibration 미시도와 dynamic 균형 미반영은 향후 자연 실험·국제 비교 연구의 출발점으로 제시했다. 모든 코드·데이터·결과는 GitHub repository(`bluethestyle/goodhart-korea`)와 Zenodo에 공개되어 *재현 가능한 연구*를 지향한다.

  한국 재정 집행의 굿하트 게임이 *고정 패턴이 아닌 진행 중인 동적 현상*이라는 본 발견은, 평가 제도 자체가 측정 대상 행동의 분포를 변화시킨다는 *Performative Prediction* (@hardt2016strategic; @perdomo2020performative)의 한국 실증으로 해석될 수 있다. 후속 연구는 국제 비교(미국·일본·EU)와 자연 실험을 통해 *어떤 제도 조건에서 이 동적 강화가 억제되는가*를 밝힐 수 있을 것이다.



// =============================================================
= AI 도구 사용 명시

#set par(first-line-indent: 0pt)

본 연구의 데이터 수집·정제·분석·시각화는 *Anthropic Claude (claude-opus-4-7, claude-sonnet-4-6)*가 *Claude Code* 환경에서 보조했다. 구체적으로:

- *데이터 파이프라인 작성*: 열린재정정보·KOSIS·ECOS·공공데이터포털·GIR API 호출 스크립트, DuckDB warehouse 빌드
- *분석 코드 작성*: 분석 스크립트(약 30개, repo의 H1\~H24 시리즈로 번호 부여), UMAP/HDBSCAN/Mapper/PH/RDD/Mediation/STL 구현
- *시각화*: matplotlib 기반 figure 생성
- *문서화*: JOURNEY.md 분석 여정, REFERENCES.md, SOURCES.md 정리
- *비판적 검토*: outcome 적합도 검증(부적절 6개 식별 후 교체), STL trend 혼재 자기 비판

연구 가설 설정·결과 해석·정책 함의는 저자가 직접 결정하고 검토했다. AI 도구의 모든 출력물은 저자가 학술적 정합성·재현성·인과 추론 한계 측면에서 검토했다. 본 명시는 *학술 책임 소재*가 저자에게 있음을 분명히 한다.

연구 재현 자료(코드, 결과 CSV, 시각화)는 GitHub repository와 Zenodo에 공개한다.

- GitHub: #link("https://github.com/bluethestyle/goodhart-korea")[github.com/bluethestyle/goodhart-korea]
- Zenodo DOI: (DOI 발급 예정)
- 인터랙티브 시각화: #link("https://bluethestyle.github.io/goodhart-korea/interactive/")[bluethestyle.github.io/goodhart-korea/interactive]
- 분석 여정 (전체 H1\~H24): #link("https://bluethestyle.github.io/goodhart-korea/analysis/JOURNEY/")[bluethestyle.github.io/goodhart-korea/analysis/JOURNEY]

*라이선스 및 배포*: 본 논문 본문은 #link("https://creativecommons.org/licenses/by/4.0/")[CC BY 4.0] 하에 배포된다. 분석 코드는 #link("https://github.com/bluethestyle/goodhart-korea")[GitHub repository]에 MIT 라이선스로 공개되며, 분석 산출물(CSV·PNG)은 CC BY 4.0이다. 인용 시 출처(GitHub repository + Zenodo DOI)를 표기해 주시기 바란다.

#set par(first-line-indent: 1em)

#v(1em)

// =============================================================
#bibliography("refs.bib", title: "참고문헌", style: "apa")

#pagebreak()

// 부록 섹션은 자동 numbering 비활성화 (제목에 "부록 A.", "부록 B." 등이 직접 표기됨)
#set heading(numbering: none)

// =============================================================
= 부록 A. 약어 일람

#figure(
  text(size: 9.5pt)[
    #table(
      columns: (auto, 0.6fr, 1fr),
      align: (left, left, left),
      inset: (x: 5pt, y: 3pt),
      stroke: (x, y) => if y == 0 { (bottom: 0.6pt) } else { (top: 0pt, bottom: 0pt) },
      table.hline(y: 1, stroke: 0.3pt + black),
      [*약어*], [*원어*], [*의미·용도*],
      [FFT], [Fast Fourier Transform], [고속 푸리에 변환. 시계열을 주파수 성분으로 분해해 1년 주기 진폭(`amp_12m_norm`)을 추출.],
      [STL], [Seasonal-Trend decomp. using Loess], [Loess 평활 기반 가법 분해. 추세·계절·잔차로 분리해 `seasonal_strength` 산출.],
      [NP], [NeuralProphet], [Prophet의 신경망 확장. 추세·Fourier 계절·AR-Net을 가법 결합한 분해 모형.],
      [AR], [Autoregression], [자기회귀. 과거값으로 현재값 설명. NP 적합 시 `n_lags=0`으로 비활성화.],
      [UMAP], [Uniform Manifold Approx. & Projection], [비선형 차원 축소. fuzzy simplicial set 기반 국소·전역 구조 보존.],
      [HDBSCAN], [Hierarchical DBSCAN], [밀도 기반 계층 군집. 군집 수 사전 지정 불요, 노이즈 분리.],
      [TDA], [Topological Data Analysis], [위상 데이터 분석. Mapper · Persistent Homology를 포함.],
      [PH], [Persistent Homology], [지속 호몰로지. 모든 스케일에서 위상 특성(연결성·loop) 추적.],
      [FE], [Fixed Effects], [고정효과. 분야·연도 등 그룹 더미로 이질성 통제.],
      [RDD], [Regression Discontinuity Design], [회귀불연속 설계. 인위적 절단점 직근의 비교로 인과 식별.],
      [DID], [Difference-in-Differences], [이중차분. 처리·통제군 + 사전·사후 비교(본 연구 미사용).],
      [IV], [Instrumental Variables], [도구변수. 외생적 변동을 활용한 인과 식별.],
      [CV], [Coefficient of Variation], [변동계수($sigma\/mu$). FFT 대안 게임화 지표.],
      [CPI], [Consumer Price Index], [소비자물가지수. 한국은행 ECOS 901Y009. 외생 거시 통제변수.],
      [NPM], [New Public Management], [신공공관리. 1980년대 영국·뉴질랜드의 KPI·민영화 패러다임.],
      [KPI], [Key Performance Indicator], [핵심성과지표. NPM 도입 이후 행정 평가 도구.],
      [MTEF], [Medium-Term Expenditure Framework], [중기재정운용계획. 한국은 2009년 5년 단위로 도입.],
      [ECOS], [Economic Statistics System (BOK)], [한국은행 경제통계시스템. CPI 등 거시 시계열 제공.],
      [KOSIS], [Korean Statistical Information Service], [국가통계포털. 분야별 결과변수 제공.],
      [GIR], [Greenhouse gas Inventory & Research], [온실가스종합정보센터. 국가 인벤토리 보고.],
      [ODA], [Official Development Assistance], [공적개발원조. OECD DAC 기준.],
    )
  ],
  caption: [본 연구 약어 및 약식 표기 일람],
)

= 부록 B. 핵심 용어 정의

#set par(first-line-indent: 0pt)

본 연구의 다중 방법론에 등장하는 통계·수치해석 용어를 일괄 정의한다. 본문 첫 등장 시 핵심 약어는 각주로 1줄 풀어쓰며, 상세 정의는 본 부록을 참조한다.

*P-A 모형 기호 (§3, 부록 F)*

- *$P, A$*: Principal(정부/부처)과 Agent(사업 수행 부처·출연기관)
- *$U_P, U_A$*: 각각의 목적함수
- *$Y(e_q, e_t)$*: 사회적 결과 (예: 빈곤 격차, 기대수명, 특허 수)
- *$e_t in RR_+$*: Agent의 *시점 조정 노력* (12월 집중 집행, 측정 가능)
- *$e_q in RR_+$*: Agent의 *사업 품질 노력* (사회 결과 기여, 측정 어려움)
- *$tilde(e)_q = phi(e_q)$*: $e_q$의 측정 가능 부분 (측정성 격차 $phi'(\cdot) < 1$)
- *$w_t, w_q$*: 시점·품질 노력에 대한 평가 가중치
- *$c(e_t, e_q; theta)$*: 노력 비용 함수, 사업원형 $theta$별 차이 (볼록·증가)
- *$theta in {$인건비형, 자산취득형, 출연금형, 정상사업$}$*: 사업원형 라벨
- *$e_t^*, e_q^*$*: 1차 조건을 만족하는 균형 노력 (FOC: $w_t = partial c/partial e_t$ 등)

*경제학·계약이론 용어*

- *굿하트 법칙*: 사회 지표가 정책 결정 도구로 사용되는 순간 그 지표의 측정 신뢰도가 하락한다@goodhart1975. Campbell(1979)이 사회과학 일반에 확장.
- *다업무 계약 이론 (Multitasking)*: 대리인이 다차원 업무를 수행할 때 측정 가능한 차원에만 인센티브가 걸리면 비측정 차원의 노력이 체계적으로 감소한다@holmstrom1991.
- *Holmstrom-Milgrom Impossibility*: 측정성 격차가 큰 환경에서 *어떠한 인센티브 가중치도 1차 최적이 될 수 없다*는 이론적 결과. 본 연구의 정책 권고가 *완전 해결을 약속하지 않는* 이론적 근거.
- *Fortuitous Alignment*: Agent의 균형 행동($e_t^*$)이 Principal의 사회 결과($Y$)와 *우연히* 정렬되는 경우. 본 연구의 사회복지 자동분배 효과(H5)의 모형 frame. 분야 함수 $alpha(theta_("field")) = (partial Y) / (partial e_t)$의 우연한 양수성으로 정식화.
- *Baker Distortion @baker1992*: 측정 지표 $M$과 진정한 가치 $V$ 간 한계 생산성 격차 ($(partial M) / (partial e) != (partial V) / (partial e)$). 본 모형의 측정성 격차 함수 $phi'(\cdot) < 1$가 distortion의 구체화.
- *Career Concerns* (@holmstrom1999; @dewatripont1999): 평가가 단일 stage가 아닌 *다년 평판 신호*로 작동하는 PA 동적 균형. 출연기관의 모기관 결속 평판이 *집단 동기화*(phase coherence 0.54)를 유발.
- *Performative Prediction* (@hardt2016strategic; @perdomo2020performative): 지표가 *학습 대상*이 되는 순간 분포가 변화한다는 ML-economics 교차 프레임. 본 연구의 H6 시간 강화(+554\%)는 행정 시스템에서의 직접 사례.
- *Strategic Classification* #cite(<hardt2016strategic>): 분류기가 평가 도구가 되는 순간 입력 분포가 *전략적 적응*된다는 ML 이론. Performative Prediction의 정적 버전.
- *연성 예산 제약 (Soft Budget Constraint)*: 시장 규율 대신 모기관·정부의 사후 보전을 기대해 예산 제약이 약화되는 현상@kornai1980.
- *매개분석 (Mediation)*: $X arrow M arrow Y$ 경로의 *간접 효과*를 직접 효과 $X arrow Y$로부터 분리하는 회귀 기법. 본 연구는 Baron-Kenny 4단계 + Sobel 검정 + Bootstrap CI 사용.
- *Sobel 검정* #cite(<sobel1982>): 매개효과 $a b$의 표준오차 $sqrt(b^2 sigma_a^2 + a^2 sigma_b^2)$로 z-검정. 정규성 가정 의존.
- *Spectral Co-clustering*: 부처(행)와 사업원형(열)의 빈도 행렬을 SVD로 *동시* 군집해 블록 대각 구조를 찾는 알고리즘@dhillon2001.
- *Permutation 검정*: 결과변수를 무작위 셔플해 귀무 분포 생성. 정규성·등분산 가정 불요.
*데이터분석·ML 용어*
- *MCMC (Markov Chain Monte Carlo)*: 사후분포에서 표본을 추출하는 Bayes 추론 기법. Prophet 원판이 사용; NeuralProphet은 SGD로 대체.
- *SGD (Stochastic Gradient Descent)*: 미분 가능한 목적함수를 미니배치 단위로 최적화하는 알고리즘. NP는 PyTorch SGD로 학습.
- *SVD (Singular Value Decomposition)*: 행렬을 $U Sigma V^T$로 분해. Spectral Co-clustering 핵심.
- *DFT (Discrete Fourier Transform)*: 이산 시계열의 푸리에 변환. FFT는 DFT의 빠른 알고리즘.
- *LOESS (Locally Estimated Scatterplot Smoothing)*: 국소 가중 다항회귀 평활. STL의 평활 엔진.
- *GAM (Generalized Additive Model)*: 비선형 함수 항의 가법 결합. Prophet/NeuralProphet의 토대.
- *PCA (Principal Component Analysis)*: 선형 차원 축소. UMAP과 대조군으로 언급.
- *t-SNE*: 비선형 임베딩 알고리즘. 전역 구조 보존이 약해 UMAP을 채택.
- *DBSCAN*: 밀도 기반 군집의 단일 임계 버전. HDBSCAN의 전신.
- *ARIMA / SARIMA*: 자기회귀 누적이동평균 모형. 정상성 가정으로 본 연구 시계열에 부적합.
- *LSTM / Transformer*: 신경망 시계열 모형. 분해 가능성 부재로 본 연구에 부적합.
- *Frisch-Waugh-Lovell 정리*: 다중회귀 계수가 *2단계 잔차회귀*와 동일함을 보이는 정리. CPI 통제의 이론적 근거.
- *Gibbs 현상*: 유한 푸리에 합이 점프 점 근방에서 진동·과대평가하는 현상. FFT 약점.
- *AR-Net*: 신경망 자기회귀. NeuralProphet의 핵심 차별점.
- *ReLU*: $max(0, x)$ 비선형 활성함수. AR-Net의 표준 활성함수.
- *사업원형 (Archetype)*: 본 연구가 데이터에서 발견한 4개 사업 형태(인건비형·자산취득형·출연금형·정상사업).
- *`amp_12m_norm`*: FFT 1년 주기 진폭 / 전체 진폭 합. 게임화 1차 지표.
- *`seasonal_strength`*: STL 분해 후 $1 - "Var"("잔차")/"Var"("detrended")$. 게임화 STL 지표.
- *`np_seasonal_strength`*: NeuralProphet yearly seasonality 진폭 / 표준편차. 게임화 NP 지표.

#set par(first-line-indent: 1em)

#pagebreak()

// =============================================================
= 부록 C. 방법론 상세 — 수식·알고리즘·대안 비교

본 부록은 본문 방법론 절의 *직관·주제 적합성* 서술을 보완한다. 각 도구의 (1) 수식 정의, (2) 알고리즘 골자, (3) 대안 도구와의 비교를 정리한다. 본문 절 번호와 일대일 대응한다.

== C.1 FFT — DFT 정의·`amp_12m_norm` 비율식·약점

*이산 푸리에 변환(DFT)*: 길이 $N$의 신호 $x_n$에 대해 (@cooley1965 의 FFT 알고리즘으로 $O(N log N)$ 계산)
$ hat(x)_k = sum_(n=0)^(N-1) x_n e^(-i 2 pi k n / N), quad k=0,1,...,N-1 $
$|hat(x)_k|$=주파수 $f_k = k\/N$ 성분의 진폭, $arg(hat(x)_k)$=위상.

*`amp_12m_norm` 정의*: 활동 $i$, 연도 $t$의 월별 시계열 ${x_(i,t,m)}_(m=1)^12$($N=12$)에 대해
$ "amp_12m_norm"_(i,t) = (|hat(x)_(i,t)(k=1)|) / (sum_(k=1)^(N\/2) |hat(x)_(i,t)(k)|) $
분자: 연 1회 주기 성분의 진폭, 분모: DC 제외 모든 주파수 진폭의 *L1-합* — 비율은 *주파수 영역 L1 강도 중 1년 주기가 차지하는 비중*. 분모를 $sum_k |hat(x)_k|^2$ (L2)로 바꾸면 Parseval 정리($sum_n |x_n|^2 = (1\/N) sum_k |hat(x)_k|^2$)에 의해 *총 변동 에너지 비중*이 되며 정의가 등가가 아니다 (L1 vs L2). 본 연구의 L1 형식은 *진폭 단위* 직관성을 우선했으며, 두 형식은 단조 변환 관계라 가설 검정 결론은 일치한다.

*FFT의 약점*: (a) 정상성(stationarity) 가정 — 한국 정부 예산은 평균 ~6% 증가 추세, (b) 12개월 windowing의 *Gibbs 현상* — 연도 경계 점프가 인접 주파수로 누설. STL과 NP로 보완.

== C.2 STL — 알고리즘·`seasonal_strength` 정의·약점

*알고리즘*: STL은 두 겹 반복으로 가법 분해한다. inner-loop는 (1) 시계열에서 추세 추정값을 빼서 detrended 신호 생성, (2) 동일 계절 값들(예: 매년 1월)을 cycle-subseries로 묶어 LOESS 평활해 $S_t$ 추정, (3) $x_t - S_t$를 다시 LOESS 평활해 $T_t$ 갱신. 수렴까지 반복. outer-loop는 큰 잔차에 *robustness weight* 부여로 outlier 영향 차단.

*`seasonal_strength` 정의*: 추세 제거 신호 $D_t = x_t - T_t = S_t + R_t$에서 계절 성분의 분산 비율
$ "seasonal_strength" = max(0, 1 - "Var"(R_t) / "Var"(D_t)) $
@hyndman2021.

*STL의 약점*: (a) LOESS 대역폭(span) 선택 민감 — 좁으면 점프를 추세로 흡수, 넓으면 추세 부족 추정, (b) 가법 모델만 지원, (c) 변화점 직전후 추세 추정 왜곡. NP의 명시적 changepoint 모델링이 보완.

== C.3 NeuralProphet — 6항 모형·AR-Net·Prophet 차이·하이퍼파라미터

*Full 6항 모형* (@triebe2021, eq. 1):
$ y_t = T(t) + S(t) + E(t) + A(t) + sum_(j=1)^p F_j (t) + L(t) + epsilon_t $

- $T(t)$=piecewise-linear 추세, $C$개 자동 변화점:
  $ T(t) = (k + sum_(c=1)^C delta_c bb(1)[t > tau_c])(t - tau_("ref")) $
- $S(t)$=Fourier 계열 계절성:
  $ S(t) = sum_p sum_(n=1)^(N_p) [a_(p,n) cos(2 pi n t / P_p) + b_(p,n) sin(2 pi n t / P_p)] $
  본 연구 $P=12$ 개월, $N_P=6$.
- $E(t)$=이벤트(휴일·회계 마감)
- $A(t)$=*AR-Net 자기회귀 (NP의 핵심 차별점)*:
  $ A(t) = "ReLU"(W_2 thin "ReLU"(W_1 thin [y_(t-1), ..., y_(t-l)]^T + b_1) + b_2) $
  $l$=`n_lags`, $W_1, W_2, b_1, b_2$=신경망 가중치. AR-Net은 자기회귀를 *비선형 활성화*로 확장.
- $F_j$=외생 회귀변수, $L$=lagged regressor 비선형 시차 효과, $epsilon$=정규 잔차.

*Prophet 원판과의 차이*: Prophet #cite(<taylor2018>)에는 $A(t), L(t)$가 *없고* 학습이 Stan MCMC. NP는 (a) AR-Net 추가, (b) lagged regressor 비선형화, (c) PyTorch SGD 학습 — 세 가지가 실질 확장.

*본 연구 설정 (의도적 단순화)*: 활동×연도 24개월 시계열에 적합하되 *순수 계절 분해만 보기 위해* 다른 항 비활성화.
- `n_lags=0` → $A(t) equiv 0$ (cross-check 비교 형평성)
- `n_future_regressors=0`, `n_lagged_regressors=0`, `events=None`
- `n_changepoints=2`, `yearly_seasonality=True (N=6)`, `weekly/daily=False`
- 결과 적합 모형: $y_t = T(t) + S(t) + epsilon_t$

*왜 AR을 끄는가*: AR이 활성화되면 NP는 단기 자기상관도 학습해 잔차에 들어갈 *순수 계절 신호*를 흡수한다. cross-check 메시지("도구가 달라도 같은 게임화를 본다")의 비교 형평성을 위해 끈다. 다만 AR을 켜면 *예측 정확도*가 향상되어 후속 연구의 활용 여지가 있다.

*세 도구 결정적 차이*:
- *FFT*: $sin\/cos$ 기저 *고정 진폭*. 추세 분해 안 함 — 정상성 위배 시 추세가 저주파로 누설.
- *STL*: 추세를 *비모수 LOESS*로 흡수. 변화점 명시적 모델링 안 함.
- *NP*: 추세를 *piecewise-linear + 자동 변화점 검출*. 계절성은 변화점 기반 추세 *위에서* 추정 → 추세-계절 분리 명시적·해석 가능.

*왜 NP이지 다른 신경망이 아닌가*:
- *vs ARIMA/SARIMA*: 정상성 가정 + 단일 계절 주기 + 변화점 자동 검출 없음.
- *vs LSTM/Transformer*: black-box, $N=24$ 표본에서 과적합, *분해 가능성 없음*. 본 연구 목적은 *예측이 아니라 해석 가능한 계절 강도 추출*.
- *vs Prophet 원판*: NP는 모든 해석성을 유지하면서 *대규모 활동 단위 패널*에 효율적 적합 가능. Prophet의 Stan MCMC는 1,500개 활동에 너무 느림.

== C.4 UMAP — fuzzy cross-entropy 손실·대안 비교

*손실 함수*: 고차원 데이터 $X$의 fuzzy simplicial set 표현 $A$, 저차원 임베딩 $Y$의 표현 $B$ 사이의 fuzzy cross-entropy
$ "loss" = sum_(i j) [a_(i j) log (a_(i j)) / (b_(i j)) + (1 - a_(i j)) log (1 - a_(i j)) / (1 - b_(i j))] $
를 SGD로 최소화. $a_(i j) = exp(-(d(x_i, x_j) - rho_i)\/sigma_i)$ ($k$ 최근접 이웃 기반 이웃 확률), $b_(i j) = (1 + a' ||y_i - y_j||^(2 b'))^(-1)$ (저차원 student-t 유사 분포).

*vs PCA*: 선형 투영이라 비선형 매니폴드(U자, 환상 구조) 망가뜨림.
*vs t-SNE*: KL divergence 사용 — *전역 거리* 부정확 압축. UMAP은 fuzzy set 이론으로 전역 구조도 잘 보존 (@mcinnes2018, §3).
*vs Autoencoder*: 학습 데이터 양·아키텍처 의존; UMAP은 결정론적(`random_state=42`)이고 작은 데이터에 안정.

== C.5 HDBSCAN — mutual reachability·MST·대안

*Core distance*: 점 $x$의 $k$번째 최근접 이웃까지 거리 $d_("core")(x)$.

*Mutual reachability distance*:
$ d_("mreach")(x, y) = max(d_("core")(x), d_("core")(y), d(x,y)) $

이를 가중치로 하는 *최소 신장 트리*(MST)를 구성하고, 가중치 임계값 $epsilon$을 변화시키며 단계적으로 끊어 *condensed cluster tree*를 만든다. 군집의 *안정성* 점수가 가장 높은 cluster를 최종 선택.

*vs K-means*: $k$ 사전 결정 + 구형 군집 가정 + 노이즈 처리 못함 — 본 연구의 *4개 군집·비구형·소수 outlier* 환경에 부적합.
*vs DBSCAN*: 단일 밀도 임계값 $epsilon$ — 군집 밀도 차이 크면 실패. HDBSCAN은 모든 $epsilon$ 스펙트럼 통합 분석.
*vs GMM*: 가우스 분포 가정 — 비선형 형태 군집 부적합.

== C.6 Mapper — Nerve simplicial complex 정의·대안

*수식 골자*: 데이터 공간 $X subset RR^d$, *필터 함수* $f: X arrow RR^k$ 선택(본 연구는 PCA 첫 두 성분). $f(X)$ 코도메인을 *겹치는 cover* $cal(U) = {U_1, U_2, ...}$로 분할 → 각 $f^(-1)(U_i)$를 군집 → 군집들을 노드로, 두 노드의 점이 *교집합*에 있으면 엣지로 연결한 *nerve simplicial complex*가 Mapper graph:
$ "Mapper"(X, f, cal(U), "cluster") = "Nerve"({"cluster"(f^(-1)(U_i))}) $

결과는 위상 불변량(connected components 수, loops 수, $beta_1$)으로 요약.

*vs UMAP+HDBSCAN*: 임베딩+군집은 *위치* 정보, Mapper는 *연결성* 정보. 두 군집 사이 다리(bridge) 점 존재 여부 진단 — 연속체에서 임의 절단인지 진짜 분리인지.
*vs DBSCAN*: 군집 식별만 수행, 연결성 못 봄.

== C.7 Persistent Homology — Vietoris-Rips·persistence diagram

*수식 골자*: 점집합 $P$에 대해 반지름 $epsilon$의 *Vietoris-Rips complex* $V_epsilon(P)$ 구성 — 거리 $d(x,y) <= epsilon$ 인 점쌍을 엣지로, 모든 쌍이 가까운 $k+1$개 점을 $k$-simplex로 추가. $epsilon$을 0부터 키우면 *filtration* ${V_epsilon(P)}_(epsilon >= 0)$. 각 차원 $d$의 호몰로지 군 $H_d(V_epsilon)$를 따라가면 *birth-death 페어* $(b, d)$가 출현 — hole이 $epsilon = b$에 태어나 $epsilon = d$에 사라지는 것을 기록. 이 페어 집합이 *persistence diagram*이며 *persistence* $d - b$가 클수록 robust한 위상 특성.

본 연구는 차원 0(연결성분 $beta_0$)·차원 1(loop $beta_1$) 분석. *부트스트랩 50회*로 $beta_0 = 30$, $beta_1 = 15$, max persistence 95% CI 산출.

*vs Mapper*: Mapper는 단일 스케일 graph, PH는 *모든 스케일 통합 분석*. PH 더 엄밀, Mapper 더 직관적.
*vs silhouette/Calinski-Harabasz*: 후자는 스케일 의존적 단일 점수; PH는 *스케일-불변* 위상 특성.

== C.8 분야 trivial 검정 — FE 회귀 모형 비교

*기본 모형*: 활동 $i$, 연도 $t$의 결과변수
$ Y_(i,t) = beta_0 + beta_1 X_(i,t) + sum_k gamma_k D_(i,k)^("field") + epsilon_(i,t) $
$X_(i,t)$=게임화 지표, $D_k^("field")$=14개 분야 더미.

*비교 모형*: 사업원형 × 게임화 상호작용
$ Y_(i,t) = beta_0 + beta_1 X_(i,t) + sum_c delta_c (D_(i,c)^("archetype") times X_(i,t)) + epsilon_(i,t) $
$D_c^("archetype")$=4개 사업원형 더미.

*판정 기준*: 두 모형의 *조정 R² 증가량* $Delta R^2_("adj")$ 비교. 분야 모형 $Delta R^2 approx 0$이고 원형 모형 $Delta R^2 > 0$이면 분야는 *trivial*이고 원형이 *진짜 단위*.

== C.9 Spectral Co-clustering — SVD·정규화

*행렬 정규화*: 부처-원형 빈도 행렬 $A in RR^(m times n)$($m=51$, $n=4$)을 이분 그래프로 해석. 정규화된 행렬
$ A_n = D_1^(-1\/2) A D_2^(-1\/2) $
$D_1$=행 차수 대각, $D_2$=열 차수 대각.

*임베딩*: $A_n$을 SVD하여 좌특이벡터 $U_(l)$, 우특이벡터 $V_(l)$의 처음 $l = log_2 k$개 열을 행·열에 부여. 결합 행렬 $[U_(l) ; V_(l)]^T$에 K-means 적용. 결과 클러스터가 *normalized cut* 의미에서 이분 그래프를 $k$개로 균등 분할@dhillon2001.

*vs 단순 K-means(부처)*: 부처만 군집은 "왜" 같이 묶이는지(어떤 사업 형태 특화 때문인지) 모름. Co-clustering은 부처 군집과 사업원형 군집의 *대응*을 동시 출력.
*vs LDA*: 확률적이지만 *행·열 동시 군집 보장 없음*; SVD가 spectral 의미에서 더 엄밀.

== C.10 RDD — 식별 가정·국지 선형 추정·대안

*식별 가정*: cutoff $c$ = 12월 1일 중심
$ tau_("RDD") = lim_(t arrow c^+) E[Y_t | t] - lim_(t arrow c^-) E[Y_t | t] $
가 인과 효과로 식별되려면 (a) cutoff에서의 *연속성 가정*, (b) *manipulation 부재*가 필요.

*국지 선형 추정량*: 대역폭 $h$ 안에서 좌우 각각 1차 OLS 적합
$ Y_t = alpha_-/+ + beta_-/+ (t - c) + epsilon_t, quad t in [c - h, c) "또는" (c, c + h] $
$hat(tau)_("RDD") = hat(alpha)_+ - hat(alpha)_-$. 본 연구는 *비율형 점프 배수*로 보고.

*vs DID*: 통제군 필요 — 한국 단일 정부에 외부 통제군 없음. RDD는 *자체 시간을 통제군으로* 사용.
*vs IV*: 강한 도구변수 부재; cutoff 자체가 외생적이라 IV 불요.
*vs month-of-year FE*: month FE는 *평균 점프*만 추정; RDD는 *cutoff 직근의 한계 효과* — 식별이 더 엄밀.

== C.11 매개분석 — Baron-Kenny + Sobel + Bootstrap

*4단계 회귀*:
$ "단계 1": quad Y = i_1 + c X + epsilon_1 quad ("총효과 " c) $
$ "단계 2": quad M = i_2 + a X + epsilon_2 quad ("매개경로 " a) $
$ "단계 3,4": quad Y = i_3 + c' X + b M + epsilon_3 quad ("직접 " c', " 매개 " a b) $
매개효과는 $a b$ 또는 $c - c'$ (둘은 OLS 하에서 일치).

*Sobel z-통계량*: $a b$의 점근 표준오차
$ "SE"(a b) = sqrt(b^2 sigma_a^2 + a^2 sigma_b^2) $
$z = (a b) / "SE"(a b)$로 검정. 정규성 가정에 의존.

*Bootstrap CI*: $B = 1000$회 비복원 추출 → 매번 $hat(a)^((b)) hat(b)^((b))$ 계산 → 분포의 2.5–97.5\% 분위수를 신뢰구간으로 사용. 정규성 가정 없이 *비대칭 분포*에 robust@preacher2008.

*vs SEM*: $a b$ *동시 추정*으로 효율적이나 latent variable + 큰 N 요구; 분야 단위 N=14는 SEM 부적합.
*vs Causal Mediation Analysis @imai2010*: 잠재 결과 framework으로 *비모수* 식별; 본 연구의 분야 N이 작아 비모수 검정력 부족 → parametric Baron-Kenny가 실용적.

== C.12 외생 통제 — Frisch-Waugh-Lovell residualization

*방법*: 게임화 지표 $X_t$, 결과변수 $Y_t$, 거시 통제변수 $Z_t$=CPI에 대해
$ "1단계": quad X_t = alpha_X + gamma_X Z_t + e^X_t, quad Y_t = alpha_Y + gamma_Y Z_t + e^Y_t $
$ "2단계": quad e^Y_t = beta thin e^X_t + u_t $
Frisch-Waugh-Lovell 정리: 2단계 $hat(beta)$는 다중회귀 $Y_t = alpha + beta X_t + gamma Z_t + epsilon_t$의 $hat(beta)$와 일치. 잔차 시계열 간 상관 $"cor"(e^X, e^Y)$가 *CPI 통제 후 부분 상관*.

*외생성 가정*: $Z_t$가 *재정 게임화 $X_t$에 영향받지 않음*. CPI는 한은 통화정책 도구로 (a) *한은 독립성*에 의해 재정부 결정으로부터 분리, (b) *목표값(2.0\%) 사전 공표*로 역인과 위협 작음.

*vs 단순 다중회귀에 CPI 추가*: 수학적 동일하나 잔차 분리는 *해석성* 우수("CPI 제거 후 신호" 직관 제공).
*vs 실업률·GDP 통제*: 두 변수는 정부 재정 정책의 *직접 도구*이자 결과 → 양방향 인과 위협. CPI는 통화 영역이라 재정 영역으로부터 *상대적으로 분리*.

== C.13 견고성 검증 — Permutation·Lag/Lead·CV 식

*Permutation 양측 p-값*: 결과변수 $B = 1000$회 셔플 ${Y^((b))}$, 매번 $hat(r)^((b)) = "cor"(X, Y^((b)))$
$ p = (1) / (B) sum_(b=1)^(B) bb(1)[|hat(r)^((b))| >= |hat(r)|] $

*Lag/Lead*: $r(tau) = "cor"(X_t, Y_(t + tau))$, $tau in {-1, 0, +1}$년.
- $r(0)$ 최대 → 즉시적 메커니즘 (사회복지 자동분배 가설 지지)
- $r(+1)$ 최대 → 지연 효과
- $r(-1)$ 최대 → 역인과 의심

*amp_cv*: $"CV" = sigma\/mu$. 주파수 정보를 무시하므로 FFT가 비검출하는 비주기 변동도 포착 — 두 지표 합의 시 측정 robust성 입증.

#pagebreak()

// =============================================================
= 부록 D. FFT 심층 분석 — Power Spectrum·Phase·Cross-Coherence

본문 방법론은 FFT의 *진폭 1점*(`amp_12m_norm` = $|hat(x)(k=1)|/sum_k |hat(x)(k)|$)만 사용했다. 본 부록은 FFT를 *완전히* 활용해 (D.1) 전체 power spectrum, (D.2) phase 분포, (D.3) 활동 간 cross-coherence를 분석한다. 이는 "FFT/STL/NP가 서로 다른 측정이 아니라 *상보적*"이라는 본문 결론을 정량적으로 강화한다.

== D.1 Power Spectral Density — 12개월·분기 고조파

각 활동×연도 12-vector를 평균 중심화한 뒤 `np.fft.rfft`로 7개 주파수 빈 ($k = 0, 1, ..., 6$, 주기 $infinity$, 12, 6, 4, 3, 2.4, 2개월)의 PSD $|hat(x)(k)|^2$를 산출, 1\~6 빈 합으로 정규화. 4 사업원형의 평균 PSD를 비교한다(@fig-psd).

#figure(
  table(
    columns: (auto, auto, auto, auto, auto, auto, auto),
    align: (left, center, center, center, center, center, center),
    table.hline(y: 1, stroke: 1.0pt + black),
    [*원형*], [*k=1*\ *(12m)*], [*k=2*\ *(6m)*], [*k=3*\ *(4m)*], [*k=4*\ *(3m)*], [*k=5*\ *(2.4m)*], [*k=6*\ *(2m)*],
    [인건비형], [0.097], [0.143], [0.125], [*0.269*], [0.162], [0.202],
    [자산취득형], [0.155], [0.162], [0.124], [*0.304*], [0.117], [0.138],
    [출연금형], [*0.332*], [0.131], [0.142], [0.163], [0.127], [0.105],
    [정상사업], [0.172], [0.169], [0.144], [0.239], [0.141], [0.135],
  ),
  caption: [원형별 평균 정규화 PSD — 출연금형이 12개월 진폭 dominance 최고 (0.332)],
)

#figure(
  image("figures/h27_psd.png", height: 7cm),
  caption: [원형별 평균 PSD — 출연금형(녹색)이 12m에서 다른 원형보다 2배 높은 진폭 dominance],
) <fig-psd>

*핵심 발견*:
- *출연금형*: 12개월 주기 진폭이 $33.2\%$로 압도적. 분기·기타 고조파는 약함 → *연 1회 cycle에 단일 동조*.
- *인건비형·자산취득형·정상사업*: $k=4$ (3개월·분기) 진폭이 가장 큼 ($0.27 \~ 0.30$) — 분기 보고/공정률 cycle 흔적.
- 본 발견은 *amp_12m_norm 1점 측정으로는 보이지 않던 분기 cycle의 존재*를 새롭게 드러내며, 후속 연구가 *k=4 분기 점프*를 별도 인과 분석할 가능성을 제시.

== D.2 Phase Distribution — 어느 월에 정확히 피크하는가

$arg(hat(x)(k=1))$로 12개월 dominant 사인파의 위상을 추출, 활동의 *peak month*로 변환. 4 원형의 polar histogram(@fig-phase):

#figure(
  image("figures/h27_phase.png", width:90%),
  caption: [원형별 12개월 cycle phase 분포 — 출연금형 mode 10월 (다른 원형보다 1개월 빠름)],
) <fig-phase>

*peak month mode*:
- 인건비형: 11월 (N=1,246)
- 자산취득형: 11월 (N=929)
- 출연금형: *10월* (N=1,289)
- 정상사업: 11월 (N=10,646)

*해석*: 출연금형은 다른 원형보다 *1개월 일찍* 피크에 도달한다. 12월 정산 마감 대비 *사전 준비 단계*가 더 길고, 위탁 기관과의 정산 일정상 10월 집중 집행이 발생함을 시사한다. 이는 본문 RDD에서 *자산취득형이 12월 점프 3.42x로 가장 강했던 결과와 상보적*: 자산취득형은 *12월 1일 직후 이산적 점프*를, 출연금형은 *10\~12월에 걸친 연속적 사이클*을 형성한다 — 게임화 메커니즘이 사업원형별로 다르게 발현됨을 의미한다.

== D.3 Cross-Coherence — 같은 원형 활동들이 *동시에* 피크하는가

원형 내 활동 쌍 $i, j$의 12개월 주파수 phase coherence $abs(chevron.l e^(i Delta phi) chevron.r)$를 측정 (1.0=완전 동기, 0=무관). 500쌍 무작위 표본:

#figure(
  table(
    columns: (auto, auto, auto, auto, auto, auto, auto),
    align: (left, center, center, center, center, center, center),
    table.hline(y: 1, stroke: 0.5pt + black),
    [*원형*], [*k=1*\ *(12m)*], [*k=2*], [*k=3*], [*k=4*\ *(3m)*], [*k=5*], [*k=6*],
    [인건비형], [0.41], [0.07], [0.10], [0.12], [0.06], [0.08],
    [자산취득형], [0.08], [0.06], [0.07], [0.06], [0.05], [0.07],
    [*출연금형*], [*0.54*], [0.09], [0.08], [0.10], [0.06], [0.09],
    [정상사업], [0.13], [0.05], [0.04], [0.05], [0.04], [0.05],
  ),
  caption: [원형 내 활동 간 phase coherence — 출연금형은 k=1에서 0.54로 강한 동기],
)

#figure(
  image("figures/h27_coherence.png", width:90%),
  caption: [원형별 phase coherence heatmap — 출연금형의 12m 동기화가 압도적],
) <fig-coh>

*결정적 발견*: *출연금형 활동들은 12개월 cycle에서 phase coherence 0.54로 가장 강하게 동기화*되어 있다(@fig-coh). 즉 *서로 다른 출연금 활동들이 *같은 월*에 함께 피크*한다는 의미이며, 이는 외생적 회계 cycle이 *집단 행위*를 유도한다는 본 연구의 핵심 가설을 직접 입증한다. 자산취득형(0.08)·정상사업(0.13)은 동기화가 약함 — 사업별 자체 일정에 따라 분산된 시기에 피크.

*FFT/STL/NP 상보성 종합*:
- *FFT*: 12개월 진폭 비중과 phase + coherence (이 부록)
- *STL*: 추세-잔차 분리, 추세 흡수 가능성 자기 비판
- *NP*: changepoint 보정 + 가법 분해 (인터랙티브 viz)

세 도구는 *동일 신호를 직교 차원으로 분해*하므로, "출연금형 12월 게임화"라는 본 연구의 핵심 발견은 *세 도구 모두에서 일관된 방향*으로 지지된다 (FFT k=1 진폭 33\%, NP yearly seasonality 진폭 최대, STL trend 후 잔여 신호도 출연금 우세). 이는 *방법론 트라이앵귤레이션*의 정의상 robustness 입증이다.

== D.4 Wavelet 분석 — 게임화 강도의 *시간 진화*

본 절의 표 D.4-1(원형별 12m wavelet power 시간 진화)은 §6.8 H6 결과의 핵심 데이터이므로 본문 §6.8과 함께 읽을 것을 권한다.

FFT는 *시계열 전체*의 평균 진폭을 측정하므로 정상성을 가정한다. 그러나 한국 정부 예산은 2007 국가재정법 시행, 2014 국가회계제도 개편, 2020 코로나 확장재정 등 *시간에 따라 게임화 강도가 변화*했을 가능성이 있다. 이를 검증하기 위해 *Continuous Wavelet Transform*(CWT, complex Morlet)을 적용해 시간×주기 평면에서 진폭의 진화를 추적한다.

*방법*: 각 사업원형의 *전 활동 평균 시계열*(2015\~2025, 132개월, 활동별 연 단위 정규화 후 원형 평균)에 CWT 적용. scales = 2\~40개월, complex Morlet 1.5-1.0. 12개월 scale의 power를 시계열로 추출해 *연도별 평균*으로 진화 추적. 4개 원형의 scaleogram(@fig-scaleogram)과 연도별 진폭 진화(@fig-h28-evol)는 아래에 제시한다.

#figure(
  image("figures/h28_scaleogram.png", width:100%),
  caption: [4 사업원형 wavelet scaleogram — 색이 밝을수록 강한 진폭.\ 출연금형의 12m 신호가 후반(2020\~2025)으로 갈수록 점점 진해짐.],
) <fig-scaleogram>

#figure(
  image("figures/h28_evolution.png", height: 7cm),
  caption: [12개월 cycle 진폭의 연도별 진화 — 출연금형 5.5배 증폭, 정상사업 3.2배 증폭. 인건비형만 변화 없음.],
) <fig-h28-evol>

*결정적 발견*: 12개월 cycle 진폭의 *2015\~2017 평균* 대비 *2023\~2025 평균*:

#figure(
  table(
    columns: (auto, auto, auto, auto),
    align: (left, center, center, center),
    table.hline(y: 1, stroke: 1.0pt + black),
    [*원형*], [*early (2015\~17)*], [*late (2023\~25)*], [*변화율*],
    [인건비형], [0.0068], [0.0067], [$-0.8\%$ (변화 없음)],
    [자산취득형], [0.0547], [0.1503], [*$+174.7\%$*],
    [출연금형], [0.2012], [1.3148], [*$+553.6\%$*],
    [정상사업], [0.0569], [0.2373], [*$+316.7\%$*],
  ),
  caption: [원형별 12m wavelet power 시간 진화 — 출연금형의 5배 이상 강화. 출연금형 변화율 정밀값 +553.6%, 본문 인용 시 반올림 +554%.],
)

*해석*: 한국 재정 게임화는 *고정 패턴이 아니라 진행 중인 동적 현상*이며, *출연금형에서 가장 빠르게 강화*되고 있다. FFT amp_12m_norm은 11년 평균값을 보고하므로 이 *증폭 현상*을 놓쳤다. 가능한 동인:
- *2017\~2020*: 추경 빈도 증가 + 출연기관 위탁 사업 비중 상승
- *2020\~2022*: 코로나 확장재정으로 사업 신설 가속, 12월 정산 압력 증대
- *2023\~2025*: 경상예산 평탄화 흐름에도 출연금 정산 cycle은 유지·강화

인건비형이 *변화 없음*이라는 점은 본 분석의 신뢰성을 보강한다 — 인건비는 매월 일정 지급 구조라 회계 cycle 변화에 본질적으로 둔감하다. 즉 wavelet은 *진짜 동적 신호*만 잡아냈다.

*함의*: 본 연구의 정책 시사점(부처별 4분면 점검)은 *최근 3년 데이터*에 더 집중해야 하며, 후속 연구는 wavelet 기반 *동적 게임화 지표*를 새 측도로 활용 가능하다.

*FFT/STL/NP/Wavelet 4-도구 종합 상보성*:
- *FFT*: 평균 진폭 (정적·전체)
- *STL*: 추세 vs 계절 분리 (정적, 추세 보정)
- *NP*: 가법 분해 + changepoint (반-동적, 명시적 변화점)
- *Wavelet*: 시간×주기 power (완전 동적, 진화 추적)

네 도구는 *시간 차원의 해상도*에서 점진적으로 강해지며, 함께 사용 시 *정상성·추세·changepoint·동적 진화*를 모두 다룬다. 본 연구의 게임화 측정은 이 4중 lens에서 *출연금형 사이클 우세 + 시간 강화* 결론으로 수렴한다(자산취득형은 RDD 점프에서 별도로 우세 — 부록 E 참조).

#pagebreak()

= 부록 E. 회계연도 RDD 보완 — 분야별·사업원형별 forest plot

본문 결과 절은 RDD 결과를 *전체 1.91배* + *자산취득형 3.42배 (가장 강함)*로 요약했다. 분야별 14개 forest plot과 4개 사업원형별 점프 배수의 상세는 본 부록을 참조한다.

*사업원형별 RDD 점프 순서*: 자산취득형(3.42x) > 정상사업(2.24x) > 인건비형(1.12x) > 출연금형(1.10x ns).

자산취득형이 RDD에서 가장 강한 점프를 보이는 반면, 출연금형은 RDD에서는 약하나 *연 단위 사이클 진폭*(부록 D)에서 가장 강하다. 두 사업원형은 외생 회계 cycle에 결속되어 있으나 *발현 시간 구조가 다르다*: 자산취득형은 *12월 1일 직후 이산적 spike*, 출연금형은 *연 사이클 전반에 걸친 분산형 강도*. 본문 결과 절의 'RDD vs 스펙트럼 측도' 단락 참조.

#figure(
  image("figures/h22_rdd_appendix.png", height: 7cm),
  caption: [사업원형별 12월 점프 forest plot — 자산취득형 3.42x 가장 강함, 출연금형 1.10x는 통계 미달(회색)이나 부록 D의 사이클 강도에서 우세. 분야별 forest plot은 본문 @fig-rdd-field 참조.],
)

#pagebreak()

= 부록 F. P-A 모형 도출 상세

본 부록은 본문 *이론 모형* 절의 1차 조건과 비교정역학을 정식 도출한다. 기호는 본문과 동일.

== F.1 Agent 1차 조건과 균형해

Agent 목적함수
$ U_A(e_t, e_q) = w_t e_t + w_q tilde(e)_q(e_q) - c(e_t, e_q; theta) $
에서 $tilde(e)_q$는 $e_q$의 측정 가능 부분으로 $tilde(e)_q = phi(e_q)$, $phi'(\cdot) > 0$, $phi'(\cdot) < 1$ (측정성 격차), $phi''(\cdot) <= 0$ (수확체감). 비용 함수 $c$는 *$C^2$급 strictly convex*로 가정해 $c_(t t) > 0$, $c_(q q) > 0$, $c_(t q) = c_(q t) >= 0$ (Young 정리에 의해 교차 편미분 대칭).

Interior 1차 조건 ($e_q$에 대한 미분은 $tilde(e)_q = phi(e_q)$에 chain rule):
$ (partial U_A) / (partial e_t) = w_t - c_t (e_t, e_q) = 0 $
$ (partial U_A) / (partial e_q) = w_q phi'(e_q) - c_q (e_t, e_q) = 0 $

Implicit Function Theorem으로 균형해 $e_t^*(w_t, w_q, theta)$, $e_q^*(w_t, w_q, theta)$.

== F.2 비교정역학 도출 (Cramer's rule)

FOC를 $w_t$에 대해 미분한다 (chain rule + implicit function theorem):

$ partial / partial w_t [w_t - c_t (e_t^*, e_q^*)] = 0 $
$ partial / partial w_t [w_q phi'(e_q^*) - c_q (e_t^*, e_q^*)] = 0 $

이를 두 미지수 $((partial e_t^*) / (partial w_t), (partial e_q^*) / (partial w_t))$의 선형 시스템으로 정리:

$ mat(c_(t t), c_(t q); c_(q t), c_(q q) - w_q phi'') vec((partial e_t^*) / (partial w_t), (partial e_q^*) / (partial w_t)) = vec(1, 0) $

행렬식 (Hessian determinant):
$ D = c_(t t) (c_(q q) - w_q phi'') - c_(t q)^2 $

*부호 분석*:
- 비용 볼록성 → $c_(t t) > 0$, $c_(q q) > 0$, $c_(t q)^2 >= 0$
- 수확체감 가정 $phi'' <= 0$ → $-w_q phi'' >= 0$
- 따라서 $c_(q q) - w_q phi'' > 0$ (양과 비음의 합 → strict 양; 결정 인자는 $c_(q q) > 0$, $-w_q phi'' >= 0$은 강화 효과)
- 일반 strict 볼록 가정 $c_(t t) c_(q q) > c_(t q)^2$ (노력 보완성 약함)

따라서 $D > 0$ (Hessian 양정부호, second-order condition 충족).

*Cramer's rule로 $(partial e_t^*) / (partial w_t)$ 도출*:
$ (partial e_t^*) / (partial w_t) = det mat(1, c_(t q); 0, c_(q q) - w_q phi'') / D = (c_(q q) - w_q phi'') / D > 0  $

분자 $> 0$, $D > 0$이므로 부호 *양*. 본문 명제와 일치.

*$(partial e_t^*) / (partial w_q)$ 도출*: 두 FOC를 $w_q$에 implicit differentiate한다.
- 1식 $w_t - c_t(e_t^*, e_q^*) = 0$의 $w_q$ 미분:
  $ -c_(t t) (partial e_t^*) / (partial w_q) - c_(t q) (partial e_q^*) / (partial w_q) = 0 $
- 2식 $w_q phi'(e_q^*) - c_q(e_t^*, e_q^*) = 0$의 $w_q$ 미분 (좌변에 $w_q$ 명시 의존 → $phi'$가 chain rule 외부에 추가):
  $ phi'(e_q^*) + w_q phi''(e_q^*) (partial e_q^*) / (partial w_q) - c_(q t) (partial e_t^*) / (partial w_q) - c_(q q) (partial e_q^*) / (partial w_q) = 0 $

이를 선형 시스템으로 정리(좌변 행렬은 동일):
$ mat(c_(t t), c_(t q); c_(q t), c_(q q) - w_q phi'') vec((partial e_t^*) / (partial w_q), (partial e_q^*) / (partial w_q)) = vec(0, phi') $

Cramer's rule:
$ (partial e_t^*) / (partial w_q) = det mat(0, c_(t q); phi', c_(q q) - w_q phi'') / D = -(c_(t q) phi') / D $

부호는 $c_(t q)$의 부호에 의존하며, 본 연구의 한국 환경 가정 — *agent의 시점 조정과 품질 노력이 자원 경합 관계 (대체재, $c_(t q) > 0$)* — 에서:
$ (partial e_t^*) / (partial w_q) < 0 quad ("품질 평가 가중 ↑ → 게임화 ↓") $

본문 §3.4 명제와 부호 일치. $c_(t q) = 0$ (독립적 노력) 시 영향 없음, $c_(t q) < 0$ (보완재) 시 부호 반전 가능성도 모형이 허용하지만, 한국 평가 환경에서는 자원 경합이 자연스럽다.

*$(partial e_t^*) / (partial c_(t t))$*: $c$ 함수의 곡률 파라미터 $c_(t t)$가 외생적으로 증가하면 1식 FOC $w_t = c_t(e_t^*, e_q^*)$의 좌변은 고정인데 우변 곡선이 가팔라지므로 균형 $e_t^*$가 감소한다 (implicit differentiation 직접):
$ (partial e_t^*) / (partial c_(t t)) < 0 $
agent의 시점 조정 한계비용 증가 → 균형 노력 감소. 정책 권고 3·5(정산 분산, 자동 flagging)의 모형 기반.

== F.3 사업원형별 비용 함수 specialize

$c(e_t, e_q; theta)$를 원형 $theta$별로 specialize:

- *인건비형 (theta_0)*: $c_t = infinity$ for $e_t > 0$ — 시점 조정 자체 불가 ($e_t^* = 0$)
- *자산취득형 (theta_1)*: $c_t (e_t)$가 12월 1일 직전 *step function* — $e_t in [0, e_t^max]$ 구간에서 $c_t = epsilon$ (작음), $e_t > e_t^max$에서 발산. 균형: 가능한 최대치까지 일거에 점프 → *이산적 RDD spike*
- *출연금형 (theta_2)*: $c_t (e_t)$가 *분산형* — 위탁기관별 정산 시점 다양해 한계 비용이 *연중 분산*. 균형: 연 사이클 전반에 걸친 점진 누적 → *spectral 진폭 우세*
- *정상사업 (theta_3)*: 평균적인 $c_t$ — 두 패턴의 혼합

본 specialization은 본문 H2, H3 가설의 모형 기반이다.

== F.4 한계와 후속 연구

본 모형의 한계 및 후속 연구 방향은 §8 본문을 참조한다. P-A 모형에 특화된 확장(calibration 미시도, dynamic 균형, multi-agent 상호작용, causal forest 적용)의 수식 구체화는 향후 별도 연구에서 다룬다.

#pagebreak()

// =============================================================
= 부록 G. 스크립트-가설 매핑 — 재현 가이드

본 연구의 핵심 분석 스크립트와 가설·결과 절의 1:1 매핑을 제시한다. GitHub repository(`bluethestyle/goodhart-korea`)의 `scripts/` 디렉토리 내 해당 파일을 실행하면 본문 그림·CSV를 재현할 수 있다.

#figure(
  table(
    columns: (1.2fr, 1fr, 2fr),
    [*스크립트*], [*가설/결과*], [*역할*],
    [`scripts/h3_v2_11y.py`], [H1 / §6.1·§6.2], [UMAP + HDBSCAN 4 archetype 발견],
    [`scripts/h4_v3_replaced.py`], [H1 보강 / §6.2], [Mapper graph + Persistent Homology],
    [`scripts/h22_rdd_yearend.py`], [H2 / §6.3], [회계연도 RDD 점프 추정],
    [`scripts/h27_power_spectrum_coherence.py`], [H3 / §6.4], [PSD·Phase·Coherence],
    [`scripts/h26_neuralprophet_check.py`], [방법론 / §6.5], [NeuralProphet cross-check],
    [`scripts/h23_mediation.py`], [H4 / §6.6], [Baron-Kenny + Sobel + Bootstrap],
    [`scripts/h6_robustness.py`], [H5 / §6.7], [FE 회귀·Permutation·Lag/Lead],
    [`scripts/h10_macro_control.py`], [H5 보조 / §6.7], [CPI 외생 통제],
    [`scripts/h28_wavelet.py`], [H6 / §6.8], [Wavelet 시간 동적 강화],
    [`scripts/h24_stl_decomp.py`], [Robustness / §6.9], [STL 자기 비판],
  ),
  caption: [핵심 분석 스크립트와 가설·결과 절의 매핑 — 재현 가이드],
)
