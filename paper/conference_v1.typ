// 한국 정부 재정 집행의 굿하트 게임 — 「예산정책연구」(국회예산정책처 NABO, KCI) 투고 규격 축약본 초안
// ※ 본 typst 파일은 내용·구조·분량·그림배치·절번호·초록 검증용 초안이며,
//    최종 제출본은 NABO 지정 한글(HWP) 양식(journal_sample.pdf)으로 이식해야 한다(typst PDF 자체는 제출 불가).
//    NABO 규격: A4 25매 이내·국문초록 400자 이내·주제어 5개 이내·HY신명조 11pt·줄간격 180%·상하여백 30mm,
//    절 Ⅰ./항 1./목 가./(1)/(가), 표·그림 [표 N]·[그림 N] 중앙 상단+자료 하단, 온라인투고 nabo.jams.or.kr.
// 풀버전 모노그래프(main_v2.typ, ~84p)는 Zenodo 기술보고서로 별도 아카이빙.
// 컴파일: typst compile paper/conference_v1.typ --font-path paper/fonts paper/conference_v1.pdf

#set document(
  title: "한국 정부 재정 집행의 굿하트 게임 — Principal-Agent 균형 분석과 사업원형별 인과 식별",
)

// 헤딩·제목용 글꼴(가독 강조)
#let head-font = ("Pretendard", "Malgun Gothic", "Noto Sans KR", "Times New Roman", "HYGothic")

#set page(
  paper: "a4",
  // NABO 「예산정책연구」: 상하 여백 30mm. 좌우는 견본 근사(30mm); 정확값은 HWP 양식에서.
  margin: (top: 30mm, bottom: 25mm, left: 30mm, right: 30mm),
  numbering: none,
  // 머리글: 1쪽 제외, 우측에 약식 제목 + 쪽번호(견본 형식)
  header: context {
    let p = counter(page).get().first()
    if p == 1 { return [] }
    set text(size: 9pt, fill: rgb("#555"), font: head-font)
    align(right)[한국 정부 재정 집행의 굿하트 게임 #h(1.2em) #p]
  },
)

// 본문 명조 = Noto Serif KR / 영문 Times New Roman / 한글 fallback
#set text(
  font: ("Times New Roman", "Noto Serif KR", "HYSinMyeongJo", "Batang"),
  size: 11pt,
  lang: "ko",
)

// 본문 11pt·줄간격 ~180%·들여쓰기 2(≈1em)
#set par(
  justify: true,
  leading: 1.0em,
  first-line-indent: (amount: 1em, all: true),
  spacing: 1.2em,
)

// NABO 절 번호 체계: 節 Ⅰ. / 項 1. / 目 가. / (1) / (가)
#let cjk-roman = ("Ⅰ","Ⅱ","Ⅲ","Ⅳ","Ⅴ","Ⅵ","Ⅶ","Ⅷ","Ⅸ","Ⅹ")
#set heading(numbering: (..n) => {
  let nums = n.pos()
  let d = nums.len()
  if d == 1 { cjk-roman.at(nums.last() - 1) + "." }
  else if d == 2 { numbering("1.", nums.last()) }
  else if d == 3 { numbering("가.", nums.last()) }
  else if d == 4 { numbering("(1)", nums.last()) }
  else { numbering("(가)", nums.last()) }
})

// 節(14pt 진하게, 중앙) > 項(12pt 진하게) > 目(11pt 진하게)
#show heading.where(level: 1): it => block(width: 100%, breakable: false)[
  #v(1.0em)
  #align(center)[#text(font: head-font, size: 14pt, weight: "bold")[#it]]
  #v(0.45em)
]
#show heading.where(level: 2): it => [
  #v(0.6em)
  #text(font: head-font, size: 12pt, weight: "bold")[#it]
  #v(0.2em)
]
#show heading.where(level: 3): it => [
  #v(0.4em)
  #text(font: head-font, size: 11pt, weight: "bold")[#it]
  #v(0.12em)
]

// figure 분리: image→그림, table→표
#show figure.where(kind: image): set figure(supplement: [그림])
#show figure.where(kind: table): set figure(supplement: [표])

// 표·그림 번호+제목은 상단(중앙), NABO 형식 [표 N]/[그림 N]
#show figure: set figure(numbering: "1")
#show figure.caption: it => context {
  let n = it.counter.display(it.numbering)
  set align(center)
  set text(weight: "bold", size: 10pt, font: head-font)
  [\[#it.supplement #n\] #it.body]
}
#set figure.caption(position: top)

// 표 디자인 — 학술지 표준(상·하 굵은 선, 본문 얇은 회색)
#set table(
  stroke: (x, y) => (
    top: if y == 0 { 1.0pt + black } else { 0pt },
    bottom: if y == 0 { 1.0pt + black } else { 0.3pt + rgb("#bbb") },
  ),
  fill: none,
  inset: (x: 8pt, y: 6pt),
)
#show table.cell: it => { set par(leading: 0.45em); it }
#show table.cell.where(y: 0): set text(
  weight: "bold", font: ("Times New Roman", "Malgun Gothic", "HYGothic", "Batang"),
)

// 표 하단 주(註) 헬퍼
#let tnote(body) = block(width: 100%, above: 4pt)[
  #set par(first-line-indent: 0pt, leading: 0.5em)
  #text(size: 8.5pt, fill: rgb("#333"))[#body]
]

// =============================================================
// 표지 — 제목 / 저자(익명) / 국문초록(회색 바, 400자 이내) / 주제어  (NABO 견본 형식)
// =============================================================
#let graybar(body) = block(fill: rgb("#d9d9d9"), width: 100%, inset: (x: 6pt, y: 5pt), above: 6pt, below: 8pt)[
  #align(center)[#text(weight: "bold", size: 11pt, font: head-font)[#body]]
]

#align(center)[
  #v(6pt)
  #text(size: 17pt, weight: "bold", font: head-font)[한국 정부 재정 집행의 굿하트 게임#footnote[익명 심사용 원고. 저자명·소속·직위·이메일, 논문투고일, 연구비 지원, 코드·데이터 공개 저장소 정보는 NABO 편집부 양식에 따라 최종 게재 시 기재한다.]]
  #v(5pt)
  #text(size: 12.5pt, weight: "bold", font: head-font)[— 주인-대리인(Principal-Agent) 균형 분석과 사업원형별 인과 식별 —]
  #v(8pt)
  #text(size: 10.5pt, fill: rgb("#444"))[저자명 (최종논문 제출 시에만 기입)]
]

#v(8pt)

#graybar[국문초록]

#pad(x: 4mm)[
  #set text(size: 10pt)
  #set par(first-line-indent: (amount: 1em, all: false), leading: 0.62em, justify: true, spacing: 0.7em)
  본 연구는 한국 중앙정부 재정 집행의 굿하트 효과를 주인-대리인 균형 모형으로 도출해 6개 가설을 11년(2015–2025) 월별 패널 1,557개 활동으로 검증한다. 집행률은 완벽히 측정되나 사업 품질은 측정되지 않는 측정성 격차가 합리적 대리인을 시점 조정 노력으로 편향시킨다. 활동 단위 임베딩으로 4개 사업원형을 도출하며, 분야 고정효과의 게임화 설명력은 0인 반면 사업원형은 유의해 분산의 단위가 사업원형임을 확인한다. 12월 회귀불연속에서 자산취득형은 전체(1.91배) 대비 3.42배의 연말 점프를 보이고, 출연금형 게임화는 표본 기간 +554% 강화된다. 견고한 발견은 집행 산출 측에 있으며 결과 측 연관은 미확증으로, 집행률이 정책 결과를 검증할 미시 데이터를 갖추지 못함을 보고한다.

  #v(4pt)
  #set par(first-line-indent: 0pt)
  □ #text(weight: "bold")[주제어:] 굿하트 법칙, 주인-대리인 모형, 다업무 계약, 회귀불연속, 사업원형
]

#v(6pt)

// =============================================================
= 서론

  Bevan and Hood(2006)는 영국 NHS 사례에서 "측정되는 것이 중요해진다"는 명제 아래 평가지표 게임화의 세 패턴(threshold·ratchet·output distortion)을 식별했다. 이는 Goodhart(1975)와 Campbell(1979)이 통화정책과 사회과학 일반에서 제시한 명제 — 지표가 정책 도구로 채택되는 순간 측정 신뢰도가 하락한다 — 의 행정학적 구체화다. 같은 기제가 한국 중앙정부 재정 집행에서도 작동하는가. 이에 답하려면 게임화를 측정 가능한 양으로 정의하고, 분야·부처·사업 형태에 걸친 이질성을 분리하며, 자연 경기 순환이나 추세 같은 경합 가설을 배제해야 한다.

  본 연구는 이 세 과제를 단계적으로 수행한다. 분석은 이론이 아니라 11년 월별 집행 패널이 드러낸 세 관찰에서 출발한다. 첫째, 각 사업을 연 집행액 100%로 정규화하면 12월 비중 평균이 12.1%로 11월(5.5%)의 2.2배이며, 이 쏠림은 소규모 사업(Q1 15.4%)에서 대규모(Q4 10.9%)로 단조 감소한다. 둘째, 분기말 사이클의 강도와 위상은 같은 부처·분야 안에서도 사업마다 갈린다. 셋째, 집행률은 90% 이상에 압축되어 분야 간 거의 같으나(천장 효과) 결과지표의 분산은 훨씬 크며, 천장(99–100%)에 도달한 사업의 12월 비중은 균등 가정(8.33%)에 가깝지만 95% 미달 사업은 약 19%에 쏠린다(Welch $t > 20$, $p < 10^(-100)$). 세 관찰은 각각 시점 압력의 원인·단위·산출–결과(output–outcome) 대리 가능성을 묻는 질문으로 이어지며, 본 연구의 이론과 실증 골격을 결정한다.

  본 연구의 직접 선례는 Liebman and Mahoney(2017)다. 이들은 미국 연방조달에서 회계연도 마감(9월 30일) 직전 주의 지출이 4.9배 증가하고 동시에 품질 점수가 하락함을 회귀불연속(RDD)으로 입증했다 — 미사용 예산이 이월되지 않는 use-it-or-lose-it 구조가 만드는 측정 왜곡의 인과 식별 사례다. 본 연구는 동일한 RDD 설계를 한국 회계연도(12월 31일 종료)에 적용하되, 월 단위 집계 자료를 고려해 11월 대 12월 일평균 집행을 비교하고, 점프 규모의 사업원형별 이질성을 새로 식별한다.

  한국 재정에서 연말 집행 쏠림·불용·이월은 오래 다뤄진 주제다. 그러나 기존 논의는 대체로 "불용은 비효율, 집행률은 성과"라는 관리·효율 관점에 서 있으며, 표준 처방도 조기집행·신속집행으로 집행률을 높여 불용을 줄이는 방향을 향한다(양인용·배기수, 2019; 양지숙·오현주, 2020; 한국재정정보원, 2022). 불용액의 결정요인과 그 차기 예산 효과를 다룬 연구도 축적되어 있으나(강윤호·정여희·김보영, 2024; 김용수·노희천, 2021), 이들 역시 불용을 줄여야 할 비효율로 전제한다. 본 연구의 관점은 이와 상반된다 — 집행률을 평가지표로 강조하는 것 자체가 모형의 시점 가중 $w_t$를 키워 12월 게임화를 유발하는 원인이며, 집행률 제고를 향한 표준 처방은 게임화를 완화하기보다 강화하는 방향으로 작동할 수 있다. 측정 게임화·다업무 계약의 관점에서 한국 재정 집행을 분석한 연구는 드물며, 본 연구는 잘 알려진 현상을 이 관점으로 재정의해 표준 처방의 역설을 드러낸다.

  본 연구의 기여는 셋이다. 첫째(이론), 주인-대리인 균형 분석으로 한국에서 굿하트 효과가 발현하는 미시 기제를 도출하고 6개 검증 가능 가설을 산출한다 — 대리인의 비합리성이 아니라 합리성이 측정성 격차 환경에서 자원을 시점 조정으로 쏠리게 한다. 둘째(분석 단위), 한국 행정학·재정학이 표준으로 써온 분야 단위 분석이 게임화에 무효($Delta R^2 = 0.000$)임을 보이고, 데이터에 단위를 묻는 비지도 군집으로 게임화가 갈리는 축이 분야가 아니라 정부 회계의 편성목 구성(form)임을 특정한다. 이는 숨은 새 분류의 발명이 아니다 — 군집은 편성목 구성비만으로 재현되므로(재군집 ARI 0.895) 회계상 이미 존재하는 편성목 구조의 재확인에 가깝다. 기여는 표준 분석이 분야에 가려 놓친 이 편성목 축이 게임화의 단위임을 지목하고, 그 축이 시점이 아니라 구성에 있음(디커플링)을 활동 임베딩으로, 구조의 표본 안정성을 위상 분석으로 확립한 데 있다. 셋째(인과 식별과 정직한 한계), 자산취득형 RDD 점프 3.42배·출연금형 사이클 우세·+554% 시간 강화라는 견고한 산출 측 발견을 보이는 한편, 14개 분야 결과 연관은 어느 것도 확증되지 않음을 정직하게 보고하고, 그 측정 공백 자체를 정책 진단으로 전환한다.

  이 진단은 시민 후생과 직결된다. 견고하게 확인되는 것은 측정성 격차의 직접 귀결 — 측정이 어려운 사업 품질 노력이 측정이 쉬운 시점 조정에 체계적으로 밀려 공공서비스 품질이 희생되는 것 — 이며, 복지 수혜·농가 실수령·환경 결과 같은 결과 측 경로는 본 분석으로 확증되지 않아 탐색적으로 남는다. 어느 쪽이든, 600조 원대 재정의 평가 체제가 자원 배분을 어느 방향으로 비트는지를 데이터로 특정하는 것이 본 연구의 실천적 동기다.

= 이론 모형: 주인-대리인 굿하트 게임

  본 절은 세 이론 전통을 한국 평가 제도에 맞춰 하나의 정식 모형으로 다듬는다. (i) Goodhart(1975)·Campbell(1979)의 굿하트-캠벨 법칙과 신공공관리(NPM)의 측정 패러독스, (ii) Holmström and Milgrom(1991)의 다업무 계약 모형 — 측정성 격차가 큰 업무 구성에서는 어떤 인센티브 강도도 1차 최적이 될 수 없다는 불가능성 정리, (iii) Kornai(1980)의 연성 예산 제약(공공·출연기관이 모기관 보전을 기대하며 예산 규율이 약화)이다. 핵심 주장은 대리인이 부도덕해서가 아니라 합리적 대리인이 주어진 평가 규칙 아래 최선을 다할 때 그 선택이 게임화를 낳는다는 것이다.

== 측정성 격차와 모형 설정

  한국의 사업 수행 기관은 네 겹의 평가에 동시에 노출된다 — 집행률 평가(회계연도 말까지의 집행 비율, 날짜별로 정확히 측정), 사업 성과 평가(KPI, 지표 정의가 제각각이고 대리 지표 의존), 출연기관 경영평가(집행률 가중이 높음), 감사원 정기 감사(절차 위반 적발 중심). 네 평가를 관통하는 비대칭은 집행률은 완벽히 측정되는 반면 사업의 진짜 성과는 거의 측정되지 않는다는 점이다. 이 간극을 측정성 격차라 한다(Holmström and Milgrom, 1991). 본 연구가 주목하는 격차는 두 노력 사이에 있다 — 시점 조정 노력 $e_t$(언제 집행하는가; 월별 기록에 완벽히 남음)와 사업 품질 노력 $e_q$(사회 기여; 여러 해 뒤에야 나타나고 다른 원인과 뒤섞여 측정이 어려움).

  하나의 활동 $i$와 회계연도 $t$를 한 판으로 보는 게임을 둔다. 주인(정부·부처 $P$)은 사회적 결과를 얻되 예산 비용을 아끼려 한다.
  $ U_P = E[Y(e_q, e_t)] - C(I) $
  여기서 $Y$는 사회적 결과, $I$는 대리인에게 지급한 예산, $C(I)$는 그 재정 비용이다. 품질 노력은 결과를 끌어올리나($(partial Y)\/(partial e_q) > 0$), 집행 시점은 결과에 거의 영향이 없다($(partial Y)\/(partial e_t) approx 0$). 단 분야별 정렬 함수 $alpha(theta_("field")) := (partial Y)\/(partial e_t)$는 양 끝에서 예외를 갖는다 — 사회복지에서 양(우연한 정렬), 환경에서 음, 나머지 12분야에서 0 근방이다. 이 정렬은 대리인이 의도한 것이 아니라 분야 $alpha$가 우연히 0이 아니었던 데서 오는 부수 효과다.

  대리인(사업 수행 부처·출연기관 $A$)은 사회적 결과가 아니라 평가 점수에서 노력 비용을 뺀 값을 최대화한다.
  $ U_A = w_t thin e_t + w_q thin tilde(e)_q - c(e_t, e_q; theta) $
  $w_t$는 시점 조정 평가 가중치(집행률·경영평가에서 큼), $w_q$는 측정 가능 품질 가중치(KPI·감사에 반영되나 작음), $tilde(e)_q = phi(e_q)$는 품질 노력 중 평가 시스템이 실제로 잡아내는 부분으로 $phi(0)=0$, $0 < phi'(dot) < 1$이다. $phi'(dot) < 1$이 측정성 격차의 수학적 표현이며, Baker(1992)의 왜곡 계수에 직접 대응한다. 비용 $c(dot; theta)$는 사업원형 $theta$별로 다르고 볼록·증가다. 사회적 결과 $Y$는 대리인의 목적함수에 들어 있지 않으므로, 어떤 $Y$ 개선이든 전부 우연한 정렬의 산물이다. 비용은 사업원형별로, 결과는 분야별로 갈린다는 두 축의 분리가 본 모형의 골격이다 — 이로써 "분야는 행동을 설명하지 못한다(H1)"와 "사회복지에서만 결과가 정렬된다"가 한 모형 안에서 모순 없이 공존한다.

== 균형과 비교정역학

  대리인은 $U_A$를 최대화하는 노력 조합을 고른다. 1차 조건(FOC)은
  $ w_t = (partial c)\/(partial e_t), quad w_q phi'(e_q) = (partial c)\/(partial e_q) $
  이다. 각 노력은 "평가상 보상 = 한계 비용"에서 멈추는데, 시점 쪽 보상은 $w_t$ 그대로인 반면 품질 쪽 보상은 측정 누설을 거친 실효 품질 가중치 $w_q phi'(e_q)$다. 한국 평가 제도는 $w_t >> w_q$에 측정 누설($phi' < 1$)이 겹쳐, 균형에서 시점 노력이 품질 노력을 압도한다($e_t^* >> e_q^*$). 측정성 격차는 두 경로로 균형을 비튼다 — 평가 가중의 비대칭과 품질 노력의 측정 누설이다. Holmström and Milgrom(1991)의 불가능성 정리에 의해, 측정성 격차가 큰 환경에서는 가중치 $(w_t, w_q)$를 어떻게 조합해도 1차 최적에 도달할 수 없다.

  비교정역학은 정책 레버를 식별한다(전체 미분 전개·헤세 행렬은 지면 관계상 생략).
  $ (partial e_t^*)\/(partial w_t) > 0, quad (partial e_t^*)\/(partial w_q) < 0, quad (partial e_t^*)\/(partial c_(t t)) < 0 $
  부호의 방향이 곧 처방의 방향이다 — 시점 평가를 덜 보상하라($w_t$↓), 품질을 더 보상하라($w_q$↑), 시점 맞추기를 더 비싸게 만들라($c_(t t)$↑). 이 세 레버는 정책 함의(Ⅵ장)의 권고 1–3과 1:1 대응한다. 한편 출연금형에서 두드러지는 기관 간 동조(여러 기관이 같은 시점에 함께 몰림)는 정적 모형을 집단 평판 반복 게임으로 확장하면 사회적 학습 — 동료 기관 점수로 숨은 평가 기준을 추론 — 의 결과로 설명되나(Holmström, 1999; Morris and Shin, 2002), 본 연구의 H1–H6 검증에는 정적 균형으로 충분하므로 동적 확장의 정식 도출은 지면 관계상 생략한다.

== 사업원형별 균형 예측

  비용 함수 $c(e_t, e_q; theta)$와 평가 가중 $(w_t, w_q)$가 원형 $theta$별로 다르면 균형 시점 노력 $e_t^*$의 모양도 갈린다. 다음 예측(@tbl-archetype-pred)이 Ⅴ장에서 데이터로 확인할 대상이다.

  #figure(
    table(
      columns: (auto, auto, auto, auto, auto),
      align: (left, center, center, center, left),
      table.hline(y: 1, stroke: 1.0pt + black),
      [*원형*], [*$w_t$*], [*$w_q$*], [*$partial c\/partial e_t$*], [*예측 $e_t^*$ 패턴*],
      [인건비형], [0], [작음], [매우 큼], [$approx 0$ — 매월 균등 (구조 제약)],
      [자산취득형], [큼], [작음], [작음 (12월 1일 가능)], [큼, 12월 이산적 점프],
      [출연금형], [큼], [작음], [중간 (분산 가능)], [큼, 연 사이클 분산],
      [정상사업], [중간], [중간], [중간], [중간],
    ),
    caption: [사업원형별 전략적 균형 예측],
  ) <tbl-archetype-pred>

  모형은 6개 검증 가능 가설을 낳는다. H1: 비용 함수의 단위는 분야가 아니라 사업원형이다(분야 더미 $Delta R^2 approx 0$, 원형 상호작용 $Delta R^2 > 0$). H2: 자산취득형은 12월 1일 직후 비용이 급감해 RDD 점프가 가장 크다. H3: 출연금형은 비용이 연중 분산되어 1년 주기 사이클이 가장 강하다. H4: 출연→시점 조정→결과 매개 경로의 세기가 원형별로 달라 한데 묶은 매개효과는 미유의하다. H5: 시점이 결과에 도움이 될 가능성이 있어도 자동 소득이전이면 시점과 무관하므로, 최강 상관조차 메커니즘이 없으면 기각된다. H6: 가중 비율 $w_t\/w_q$ 또는 비용 채널의 시간 변화로 게임화 강도가 강해진다. 다만 H2는 RDD에서 관찰된 점프 패턴을 모형 입력으로 받아들인 것이므로, 순수한 사전 예측이라기보다 원형 간 비교(자산취득 3.42배 대 출연금 1.10배 대 인건비 1.12배)에서 검증력을 갖는다.

= 데이터

  본 연구는 게임화를 측정할 원인 측 데이터(재정 집행 패턴)와 그 효과를 검증할 결과 측 데이터(분야별 성과지표)를 분야 코드를 공통 키로 결합한다. 원인 측은 열린재정정보 월별 집행 테이블(VWFOEM, 2015–2025, 활동 1,557건)과 편성목 테이블(2020–2025, 활동 단위 출연금·자산취득·인건비 비중)이며, 외생 통제변수로 한국은행 ECOS 소비자물가지수(CPI)를 쓴다. 결과 측은 14개 분야 성과지표다. 원자료 분야 분류는 17개이나 활동이 분포하는 분야는 16개, 결과변수를 확보한 분야는 15개(국방 포함), 매개·상관 분석 대상은 14개다. 임베딩·군집·RDD는 활동(1,557) 단위로 수행되므로 분야 수에 의존하지 않는다. 분석 대상 활동(세부사업) 1,557건은 12개 특성변수를 산출할 월별 집행·편성목 자료를 갖춘 사업으로 한정된다. 분야 목표와 동떨어지거나 시계열이 짧은 결과변수 6개는 외부 검토를 거쳐 교체했다(@tbl-data). 국방·예비비는 측정 가능한 결과변수가 없어 제외했다.

  #figure(
    table(
      columns: 4,
      align: (left, left, center, left),
      table.hline(y: 1, stroke: 1.0pt + black),
      [*분야*], [*결과변수*], [*시계열*], [*출처*],
      [사회복지], [순자산 지니계수], [9년], [KOSIS DT_1HDAAD04],
      [보건], [기대수명], [15년], [KOSIS DT_1B41],
      [과학기술], [특허 출원/등록], [22년], [지식재산처],
      [산업·중기], [전산업생산지수], [15년], [KOSIS DT_1JH20201],
      [문화관광], [방한 외래관광객], [35년], [한국관광공사],
      [교육], [IMD 교육경쟁력 순위], [17년], [IMD],
      [국토], [주택보급률], [20년], [KOSIS DT_MLTM_2100],
      [일반·지방행정], [지방재정자립도], [29년], [행정안전부],
      [농림수산], [농가소득], [22년], [KOSIS DT_1EA1501],
      [교통], [교통사고 사망], [10년], [도로교통공단],
      [환경], [총 온실가스 배출], [34년], [GIR 국가 인벤토리],
      [통신], [초고속인터넷 가입률], [27년], [과기정통부],
      [통일외교], [ODA 원조규모], [24년], [OECD DAC],
      [공공질서], [범죄 발생], [29년], [경찰청],
    ),
    caption: [14개 분야별 결과변수(성과지표) 매핑],
  ) <tbl-data>

= 방법론

  본 연구는 가정이 직교하는 도구를 병행하는 상보적 삼각검증(triangulation)을 따른다. 도구 간 일치는 강건성(robustness)을, 불일치는 어느 가정이 위배되는지의 진단 정보를 준다 — 일치는 충분조건이지 필요조건이 아니다. 핵심 인과 도구는 RDD·매개분석·CPI 통제이고, 사이클 측정 도구는 FFT·STL·NeuralProphet·웨이블릿이다. 게임화는 직접 관측되지 않는 잠재 행동이므로, 집행 시계열의 모양 — 외생적 회계 일정에 종속된 1년 주기 패턴 — 에서 그 흔적을 추출한다. FFT의 12개월 주기 진폭이 1차 강도를, 연속 웨이블릿 변환이 그 강도의 시간 진화(H6)를 재며, STL 계절강도와 NeuralProphet 연간 계절성은 FFT 신호가 추세 혼재의 산물인지 검증하는 참고(교차검증·자기비판) 측도다. 네 도구의 역할·가정·약점은 다음과 같다(@tbl-triangulation).

  #figure(
    table(
      columns: (auto, auto, auto, auto),
      align: (left, left, left, left),
      table.hline(y: 1, stroke: 1.0pt + black),
      [*도구*], [*역할*], [*가정*], [*약점*],
      [FFT (12개월 진폭)], [게임화 강도 1차 측정], [정상성·주기 일정], [추세 흡수·경계 효과],
      [웨이블릿 (CWT-Morlet)], [강도의 시간 진화 측정 (H6)], [국소 정상성], [경계 효과(영향원뿔)·스케일 분해능],
      [STL (계절강도)], [추세 혼재 자기비판 (참고)], [가법 분해·LOESS 평활], [점프를 추세로 흡수],
      [NeuralProphet], [변화점 보정 교차검증 (참고)], [구간 선형 추세+푸리에], [소표본 과적합],
    ),
    caption: [시계열 분해 도구의 역할·가정·약점],
  ) <tbl-triangulation>

  *인과 식별.* 회계연도 12월 1일은 연속적 시간에 그어진 행정적 절단점이다. 사업의 본질적 필요와 무관하게 이 선 직전·직후로 집행이 점프하면 외생적 회계 주기에 의한 것으로 식별된다(Imbens and Lemieux, 2008; Lee and Lemieux, 2010). 본 연구는 활동 단위 11월 대 12월 일평균 비율로 점프 배수를 보고한다(Liebman and Mahoney(2017)의 4.9배 형식과 비교 가능). 절단점(회계연도 말)은 「국가재정법」상 12월 31일로 고정되어 표본 기간 내내 불변이고 모든 부처에 동시 적용되며 개별 활동이 조작할 수 없다. 절단점이 달력(12/31)이라 실행변수 밀도의 조작이 원천적으로 불가능해 McCrary 밀도검정이 겨냥하는 조작 우려는 발생하지 않으나, 자료가 월 단위로 집계되어 연속 실행변수가 없으므로 본 설계는 국지선형 RDD라기보다 활동·연도 고정효과하에 회계연도 경계 전후를 비교하는 이산 불연속 설계에 가깝다(이하 편의상 RDD로 표기). 매개분석은 출연금 비중($X$)→시점 조정 노력($M$)→분야 결과($Y$) 경로를 Baron and Kenny(1986) 회귀·Sobel z-검정·부트스트랩 1,000회로 분해한다. CPI는 한국은행이 통화정책으로 결정해 재정 행정에 외생적이므로, Frisch-Waugh-Lovell 잔차회귀로 자연 경기 순환 가설을 기각하는 통제변수로 쓴다.

  *사이클 측정.* FFT는 연도-내 시계열에서 12개월 주기 진폭 비중을 추출한다 — 게임화 신호의 주파수가 사전에 알려진 1년이므로 주파수 영역 분해가 적합하다(Bevan and Hood, 2006). 진폭이 추세 혼재의 산물인지 가리려고 STL(추세를 LOESS로 흡수한 뒤 계절강도 측정)과 NeuralProphet(구간별 선형 추세 + 변화점 보정 + 푸리에 계절)을 교차 적용하며, FFT의 정상성 가정을 넘어 진폭의 시간 변화를 보려고 연속 웨이블릿 변환(complex Morlet)을 쓴다. 강건성은 순열검정 1,000회·시차/선행 분석·변동계수 대안 지표로 점검한다.

  *사업원형 도출·검증.* 사업원형은 사전 분류가 아니라 데이터에 단위를 물어 도출한 군집이며, 세 도구의 역할은 구분된다 — UMAP+HDBSCAN은 단위를 군집화하고, Mapper·지속적 호몰로지는 그 구조의 표본 안정성을 *검증*하며(발견이 아님), 연속 웨이블릿(Ⅴ.6)은 그 강도의 시간 동학을 잰다. 1,557개 활동을 12개 스칼라 피처(편성목 구성비 4개·FFT 요약 2개·집중도·규모·추세 등)로 표현하고, UMAP(McInnes et al., 2018)으로 2차원에 사영한 뒤 HDBSCAN(Campello et al., 2013) 밀도 군집으로 4개 원형을 도출했다. 군집이 알고리즘 우연이 아님을 Mapper 그래프(연결성분 10개)와 지속적 호몰로지(부트스트랩 50회; 다이어그램 거리 검증에서 관측 Wasserstein-2 평균 0.885 대 피처 치환 귀무 1.524, $p < 0.0001$)로 확인했다(Singh et al., 2007; Edelsbrunner and Harer, 2008). 단 군집은 12개월 시점 시퀀스가 아니라 편성목 유형 공간에서 정의되므로(원본 피처 공간 실루엣 0.240 대 시점 공간 $-0.179$, 군집 라벨의 월별 비중 ANOVA $R^2 = 0.065$) "편성목 유형 군집"으로 해석하며, RDD 등 원형별 추정치는 군집 내부의 월별 이질성을 감안해 읽는다. 군집이 게임화 신호의 동어반복이 아님은 게임화 피처를 제외한 대조 재군집으로 점검하며, 편성목 구성만으로 원형이 재현되는 반면 게임화 피처만으로는 재현되지 않는다(정량 결과 Ⅴ.1) — 따라서 본 파이프라인이 특정하는 것은 숨은 새 분류가 아니라 게임화를 가르는 기존 편성목 축이다. 차원 축소·위상 분석의 알고리즘 정의·매개변수 민감도·PH 루프의 출연금형 내부 세부 이질성은 지면 관계상 생략한다.#footnote[모형의 전체 도출(1차 조건·헤세 행렬·Cramer's rule 비교정역학), 위상·신호처리 도구의 상세 알고리즘·전체 강건성, 확장 분석(시간 진화 TDA·구조 보정·ALIO)은 지면 관계상 생략한다.]

= 실증 결과

  본 절은 6개 가설을 차례로 검증한다. 핵심 인과 발견인 H2(RDD)를 충실히 다루고, 나머지는 요약한다. 각 결과는 여러 도구가 수렴할 때만 보고한다.

== H1: 분야는 무효, 사업원형이 분석 단위

  Pooled 고정효과 회귀에서 분야 고정효과만 추가하면 $R^2$는 0.014에서 변하지 않는다(분야 FE 단독 $Delta R^2 = 0.000$). 사업원형×진폭변화 상호작용을 더하면 $R^2$는 0.038로 증가한다($Delta R^2 = +0.025$). 탐색적으로도, 51개 중앙 부처 전부에서 12월 집행 비중 평균이 균등 가정 8.33%를 초과하고(51/51), 분야 내부 12월 비중의 사분위범위(평균 약 15%p)가 분야 간 중앙값 격차(국방 약 17%에서 교육 약 1%)에 맞먹어 분야 평균이 내부 다양성을 가리므로, 부처·분야 라벨은 시점 압력 변동의 단위가 아니다.

  진짜 단위를 데이터에 물으면 UMAP+HDBSCAN이 4개 안정 군집을 산출한다(@fig-umap). 각 군집의 z-score 프로파일은 실무 사업 형태와 일치한다(부록 A) — 인건비형 C0(n=129, 인건비 비중 z=+3.07, 게임화 진폭 z=$-1.30$), 자산취득형 C1(n=99, 자산취득 비중 z=+3.28), 출연금형 C2(n=154, 출연금 비중 z=+2.89, 진폭 z=+0.83), 정상사업 C3(n=1,175, 평균 부근). 다만 이 군집은 숨은 새 분류의 발명이 아니다 — 대조 재군집에서 게임화 유도 피처만으로는 원형이 거의 재현되지 않으나(ARI 0.018) 편성목 구성비 4개만으로는 거의 그대로 재현되어(ARI 0.895), 비지도 군집이 가리킨 것은 정부 회계상 이미 존재하는 편성목 축임이 드러난다. 따라서 본 연구의 발견은 숨은 분류가 아니라, 표준 분석이 분야에 가려 놓친 이 편성목 축이 게임화의 단위라는 데 있으며, 이는 비용 함수 $c(dot; theta)$의 단위가 분야가 아니라 사업원형이라는 모형 가설과 정합한다. 군집이 알고리즘 우연이 아님은 위상 도구로 검증된다 — Mapper 그래프는 노드 32·엣지 38·연결성분 10으로 군집들이 위상적으로 분리되고, 지속적 호몰로지 부트스트랩 50회는 다이어그램 전체 거리 검증(관측 Wasserstein-2 평균 0.885 대 피처 치환 귀무 1.524, $p < 0.0001$)으로 표본 변동에 대한 안정성을 확인한다(발견이 아니라 견고성 검증이다).

  이 단위가 시점이 아니라 구성에 있다는 점 자체가 비자명한 발견이다. 군집 입력은 12개월 시점 시퀀스가 아니라 활동마다 뽑은 12개 요약 피처(편성목 구성비·FFT 진폭·집중도·규모·추세)이므로, 군집은 "편성목 유형 군집"으로 해석해야 한다. 실루엣 점수가 원본 피처 공간에서는 0.240인 반면 12개월 시점 벡터 공간에서는 $-0.179$로, 활동은 시점 패턴으로는 갈리지 않고 편성목 구성으로 갈리며, 그 구성이 이후 시점 행동(Ⅴ.2 RDD 이질성)을 예측한다. 군집 라벨이 월별 비중 변동을 직접 설명하는 정도는 ANOVA $R^2 = 0.065$에 그치며, 이 구성·시점 디커플링은 회귀가 아니라 활동 임베딩의 기하가 드러낸 결과다. 따라서 RDD 등 원형별 추정치는 편성목 군집 단위로 묶어 낸 평균이며 같은 군집 안에도 월별 집행의 이질성이 남아 있음을 감안해 읽는다. 또한 PH 루프가 시사한 C2 출연금형 내부 이질성은 시점 프로파일 재군집에서 "연초집중도" 축의 약한 2분(연초 일괄형 n=50·분산형 n=104; silhouette 0.20, 부트스트랩 ARI 0.62)으로 부분 확인되나, 1분기 비중 분포가 우편향 연속(bimodality 0.56)이라 새 이산 원형이라기보다 정도의 연속에 가깝다 — 4개 원형이 분류의 종점이 아님을 드러낸다.

  #figure(
    image("figures/h3_umap.png", width: 84%),
    caption: [활동 임베딩(UMAP)과 4개 사업원형],
  ) <fig-umap>

== H2: 자산취득형 회계연도 12월 RDD 점프

  사업 본질에 따른 정상 변동과 회계 게임화를 분리하기 위해 같은 활동의 11월 대 12월 일평균 집행을 비교한다. 며칠 차이의 변동은 사업 본질로 설명할 수 없고 12월 1일이라는 행정적 절단점만 작동하므로, 분야·기관·사업 특성이 자동 통제되는 준실험이다. 전체 평균 12월 점프는 1.91배다($p < 10^(-124)$). 사업원형별 분해(@tbl-cutoff-archetype)에서 자산취득형은 3.42배(C1 군집 풀링, n=99)로 가장 크고 — 공정률 마감과 회계연도 마감이 12월 1일 직후에 결합 — 정상사업 2.24배, 인건비형 1.12배(구조상 평탄), 출연금형 1.10배(통계 미달)가 뒤따른다. 분야별로는 국방·국토·교통이 가장 크나(@fig-rdd-field), 분야 구분의 추가 설명력은 $Delta R^2 = 0.000$(Ⅴ.1)으로 무효여서 사업원형이 진짜 단위다. 점프 순서는 use-it-or-lose-it 압력이 공정률·자산취득 사업에서 가장 강하게 작동함을 보인다. 국내 결산 자료에서도 주요 불용사업의 다수(약 63%)가 하반기 집행형으로 분류되어(한국재정정보원, 2022), 본 RDD의 연말 집중 패턴과 결산 측면에서 정합적이다.

  #figure(
    image("figures/h22_rdd_field.png", width: 94%),
    caption: [분야별 회계연도 12월 점프 배수],
  ) <fig-rdd-field>

  미국 4.9배 대 한국 1.91배 격차의 일부는 집계 단위 차이(미국 주별 대 한국 월별)에서 온다 — 12월 첫째 주의 집중 신호가 월 단위 집계에서 한 달 전체로 희석되기 때문이다. 한국 자료를 가상 주별로 쪼개면, 주별 균등 배분 시 1.85배, 12월 첫 7일에 35%·50%를 집중시키면 각각 2.87배·4.10배로 추정된다. 가장 적극적인 전반 집중(front-load) 가정(첫 7일 50%)에서도 4.10배로 미국 4.9배에 미달해, 양국 차이는 측정 단위만의 산물이 아니라 조달 유형·회계 분권화 등 제도 구조 차이가 본질적 요인이다.

  11년 평균 시계열은 12월뿐 아니라 3·6·9월에도 부수 점프를 보인다 — 기획재정부 분기별 집행관리제도의 흔적으로, 절단점이 12월 하나가 아니라 분기마다 점검이 몰리는 다중 구조임을 시사한다. 12월이 압도적인 이유는 분기 마감·회계연도 마감·차년도 이월 차단의 세 마감이 12월에 겹치기 때문이다. 분기말 절단점×원형 분해(@tbl-cutoff-archetype)에서 C1 자산취득형은 4개 절단점 모두 유의(6월 2.50배·9월 1.80배·12월 3.42배·3월 1.53배)한 반면, C2 출연금형은 4개 모두 통계 미달이다 — RDD가 못 잡는 출연금형 연 사이클은 Ⅴ.3에서 별도 도구로 드러난다. 원형마다 절단점 반응이 다르다는 점 자체가 H2(점프)와 H3(사이클)에 서로 다른 도구를 쓴 경험적 근거다.

  #figure(
    table(
      columns: (auto, auto, auto, auto, auto, auto),
      align: (left, center, center, center, center, center),
      table.hline(y: 1, stroke: 1.0pt + black),
      [*원형*], [*3월/2월*], [*6월/5월*], [*9월/8월*], [*12월/11월*], [*n*],
      [전체], [×1.18], [×1.39], [×1.24], [×1.91], [1,557],
      [인건비형 C0], [×1.12], [×1.08], [×1.28], [×1.12], [129],
      [자산취득형 C1], [×1.53], [×2.50], [×1.80], [*×3.42*], [99],
      [출연금형 C2], [×0.90 (ns)], [×1.06 (ns)], [×1.07 (ns)], [×1.10 (ns)], [154],
      [정상사업 C3], [×1.27], [×1.44], [×1.22], [×2.24], [1,175],
    ),
    caption: [사업원형 × 분기말 마감(cutoff) RDD 점프 배율($e^beta$)],
  ) <tbl-cutoff-archetype>
  #tnote[주: 표기 없는 셀은 $p < 0.001$, ns는 통계 미달($p > 0.10$). 추정식은 일별 로그 집행액을 절단점 전후·연도로 회귀하고 활동코드 단위로 표준오차를 군집화한 것이다.]

  12월 점프가 마감의 제도효과인지 일반 계절성인지는 비(非)마감 월 전이를 placebo로 두어 가른다(전체 활동×연도 월별 일평균의 로그비, 활동코드 클러스터). 마감이 아닌 7개 월 전이 중 6개가 배수 1.0 미만(중앙값 0.82)으로 점프가 없는 반면, 마감월(3·6·9·12)은 모두 1을 넘고 12월이 가장 크다 — 분기말 분해(@tbl-cutoff-archetype)의 전체 12월 배수 1.91과 정합한다. 12월 집중이 계절적 추세가 아니라 회계연도·분기 마감에 결속됨을 보이는 결과다. 유일한 예외인 1→2월 전이(1.62배)는 회계연도 초 1월 집행이 구조적으로 낮은 데 따른 기저효과로, 마감과 무관하다.

  자산취득형의 RDD 점프(3.42배)는 비용함수가 12월 직전 낮은 한계비용을 갖는다는 데이터 패턴이며, 모형은 이를 입력으로 수용했으므로 진정한 모형 검증은 원형 간 비교(자산취득 3.42배 대 출연금 1.10배 대 인건비 1.12배)에 있다.

== H3: 출연금형 사이클 우세

  출연금형은 RDD 점프는 약하나 연 사이클에서 우세하다. 12개월 주기 전력스펙트럼밀도(PSD) k=1 진폭이 0.332(타 원형 0.097–0.172의 2–3.4배), 활동 간 위상 일관성(phase coherence)이 0.54(C1·C3 0.08–0.13의 4–7배; 인건비형 0.41은 매월 균등 급여 사이클의 구조적 동조), 웨이블릿 진폭의 시간 진화가 +554%다. 세 측도 모두 출연금형이 1년 주기 게임화에 가장 강하게 결속됨을 가리킨다. 자산취득형이 12월 직전 단발 점프로, 출연금형이 위탁기관 정산 일정에 따른 분산 누적으로 발현된다는 원형별 시간 구조 차이가 확인된다. 세 사이클 측도(FFT·STL·NeuralProphet)의 활동-연도 패널 상호 상관은 모두 0 근방($|r| < 0.13$)이어서, 셋이 같은 신호가 아니라 서로 다른 차원을 재는 상보적 측도임을 보인다.

== H4: 매개 경로의 원형 이질성(미확증)

  출연금 비중→시점 조정 노력→분야 결과의 매개 경로를 검정한 결과, 14개 분야 평균 매개효과는 미유의다(Sobel $p = 0.481$). 한데 묶어 미유의라는 것은 '매개 없음' 귀무가설을 기각하지 못했다는 뜻일 뿐 이질성의 직접 증거는 아니다. 분야별 분해에서 농림수산만 Sobel z=$-2.897$($p = 0.004$)로 유의하나 부트스트랩 95% 신뢰구간이 0을 포함해 미확증이며(연 단위 $n = 5$), 사회복지($n = 6$)·환경($n = 4$)은 표본 제약으로 미달 또는 추정 불가다. 비용 함수의 원형 이질성은 산출 측(RDD·웨이블릿)에서 견고하게 지지되나, 결과 측 매개 경로는 어느 분야에서도 확증되지 않았다. 분야별 시계열 확장(>10년)이 검정력 확보의 핵심 과제다.

== H5: 사회복지 최강 상관의 기각(메커니즘 규율)

  사회복지에서 12월 집중 강도가 클수록 순자산 지니계수가 감소하는 음의 상관이 14개 분야 중 가장 강하다(1차 차분 $r = -0.762$, $p = 0.035$, 순열검정 1,000회). CPI를 외생 통제하면 $r = -0.86$으로 오히려 강화되어 자연 경기 순환 가설과 구분되고, Spearman($-0.833$)·Kendall($-0.714$)·8회 Leave-One-Out(최악 $-0.539$)·95% 부트스트랩 신뢰구간 $[-0.988, -0.153]$ 전반에서 음 부호가 일관된다(단 신뢰구간 상한이 0에 가까워 $n = 8$ 표본 한계를 반영한다). 그러나 14개 동시 검정의 Bonferroni 임계값($0.05\/14 = 0.0036$)에 미달하며, 더 결정적으로 기초연금·기초생활보장 등 사회복지 이전은 자동 소득이전이라 12월 시점 조정에 거의 반응하지 않는다(12월 비중 7.8%로 14개 분야 중 가장 낮고 균등 가정 미만) — 12월 쏠림이 빈곤 격차를 좁힌 것이 아니라 어차피 분배될 예산이 그 시점에도 분배된 것이다. 본 연구는 이 최강 상관을 메커니즘 부재를 이유로 기각한다. 상관의 세기가 아니라 메커니즘으로 거르는 규율의 사례이며, 모형에서 대리인의 목적함수에 $Y$가 없다는 점이 음 상관을 인과로 읽지 않는 이론적 근거다. 측도를 STL 계절강도로 바꾸면 신호가 $r = +0.003$으로 소멸하는데(NeuralProphet 중재는 $r = -0.24$로 부분 회복), 이 측도 의존성은 추세-계절 분리 가정에 대한 자기 비판으로 함께 보고한다. 본 발견은 단일 측도가 아니라 여러 도구의 부분 합의에 의존한다.

== H6: 시간 동적 강화

  FFT 진폭은 11년 평균을 재므로 시간 변화를 보지 못한다. 연속 웨이블릿 변환으로 12개월 주기 진폭의 시간 진화를 보면(@tbl-h6-evol, @fig-h28-evol), 출연금형은 이른 시기(2015–2017)에서 늦은 시기(2023–2025)로 +553.5%(반올림 +554%) 강화되고, 정상사업 +314.3%, 자산취득형 +174.1%, 인건비형 $-1.4%$다. 인건비형은 매월 균등 지급이라 시점 조정 자체가 불가능한 통제군이며, 변화 없음이 도구가 잡음이 아니라 진짜 동적 신호만 잡아냄을 보강한다.

  #figure(
    table(
      columns: (auto, auto, auto, auto),
      align: (left, center, center, center),
      table.hline(y: 1, stroke: 1.0pt + black),
      [*원형*], [*이른 시기 (2015–17)*], [*늦은 시기 (2023–25)*], [*변화율*],
      [인건비형], [0.007], [0.007], [$-1.4%$ (통제)],
      [자산취득형], [0.055], [0.151], [$+174.1%$],
      [출연금형], [0.201], [1.316], [*$+553.5%$*],
      [정상사업], [0.057], [0.237], [$+314.3%$],
    ),
    caption: [원형별 12개월 주기 웨이블릿 파워의 시간 진화],
  ) <tbl-h6-evol>

  다만 시기 3분할에서 +554%의 상당 부분은 단조적 학습 적응이 아니라 코로나 확장재정 충격에서 비롯한다 — 코로나 이전(2015–2018)의 완만한 강화(연 +0.068)가 코로나기(2019–2021)에 급격히 증폭되고(구간 전환 +295.8%), 코로나 이후에는 높은 수준에서 고원을 이룬다(연 $-0.215$, 코로나 이전 수준으로 미회귀). 외부 평가편람에서 역산한 가중 비율 $w_t\/w_q$는 재정사업자율평가 기준 2005년 이래 0.75로 안정적이어서, +554% 강화는 가중치 경로가 아니라 비용 경로($c_(t t)$ 감소; 2018년 부처 자체평가 전환으로 중앙 감독 약화)와 외생 충격으로 재해석된다. 원형 간 순서는 어느 시기로 잘라도 보존되어 H6의 비용 함수 이질성 예측과 일치한다.

  #figure(
    image("figures/h28_evolution.png", width: 76%),
    caption: [사업원형별 12개월 주기 진폭의 연도별 진화],
  ) <fig-h28-evol>

  시간 진화 위상분석(공간 위상)과 웨이블릿(시간 위상)은 서로 무관하며($r = 0.242$, $p = 0.473$) — 원형 구조는 시간에 안정적이고 주기 진폭은 변한다는 두 발견을 보완적으로 묶는다. 부분 구조 보정과 ALIO 거시지표 보완 등 확장 분석은 지면 관계상 생략한다.

= 정책 함의

  세 발견을 종합하면, (1) 게임화의 실질 단위는 분야가 아니라 사업원형이고(H1), (2) 견고한 신호는 집행 산출 측에 있어 자산취득형 RDD 점프·출연금형 사이클·+554% 시간 강화로 나타나며(H2·H3·H6), (3) 결과 측 연관은 미확증으로 남아 집행률이 정책 결과를 검증할 기반을 갖추지 못했다(H5). 본 절은 진단과 처방의 두 층위로 정책 권고를 도출한다.

== 진단: 부처×결과변수 4분면

  가로축에 시점 집중 노출, 세로축에 결과변수 상관 부호를 놓고 분석 단위를 네 칸에 배치하면(@fig-quadrant), 노출이 같아도 결과 부호가 다른 단위를 갈라낼 수 있다. 시점 집중과 결과 악화가 동시에 나타나는 Q2(추가 분석 우선)에 국무조정실·과학기술정보통신부 등이 분류된다. 부처 라벨이 Q 분류를 만든 원인은 부처 내부의 사업원형 구성에 있으므로($Delta R^2 = 0.000$ 대 원형×진폭변화 $Delta R^2 = +0.025$), 부처 4분면은 1차 진단, 사업원형 4분면(출연금형·자산취득형이 고노출 영역에 몰림)이 2차 진단으로 결합된다. 결과 미측정 분야(국방·공공질서 등)는 본 진단의 사각지대로 남으며, 이 측정 공백 자체가 데이터 인프라 권고의 직접 근거다.

  #figure(
    image("figures/h14_quadrant.png", width: 86%),
    caption: [부처별 굿하트 노출 × 결과변수 4분면],
  ) <fig-quadrant>

== 처방: 모형 레버의 행정 액션 매핑

  처방은 새로 발명하지 않고, 비교정역학이 식별한 세 레버에 직접 대응하는 권고 1–3과 실증 발견에서 파생된 권고 4–6으로 나눈다(@tbl-policy-lever). 부호만 읽으면 시점 평가를 키우면 게임화가 늘고($partial e_t^*\/partial w_t > 0$), 품질 평가를 키우거나 시점 맞추기를 더 비싸게 만들면 게임화가 준다.

  #figure(
    table(
      columns: (auto, 1.3fr, 2.9fr),
      align: (left + top, left + top, left + top),
      table.hline(y: 1, stroke: 1.0pt + black),
      [*레버*], [*기대 효과*], [*행정 액션 후보*],
      [$w_t$ ↓], [$e_t^*$ ↓ (게임화 완화)], [집행률 평가 완화·다년도 회계·중기재정계획(MTEF) 강화·출연기관 경영평가에서 집행률 비중 축소],
      [$w_q$ ↑], [$tilde(e)_q$ ↑ (단 측정성 격차로 한계)], [사업 성과 측정 인프라 강화·KPI 정의 표준화·결과지표 활용 확대],
      [$c_(t t)$ ↑], [$e_t$ 한계 비용 ↑ → 시점 조정 ↓], [출연기관 정산 시점 분산(분기/반기)·12월 몰림 자동 표시·실시간 모니터링],
    ),
    caption: [주인-대리인 모형 정책 레버 → 한국 행정 실행 과제 연결],
  ) <tbl-policy-lever>

  *권고 1 — 다년도 회계 도입 확대($w_t$↓).* 단년도 예산 마감은 미사용 예산을 자동 소멸시켜 12월 31일을 실질 절단점으로 만든다. 「국가재정법」의 이월 제한 조항을 개정해 자산취득성 사업의 자동 이월·다년도 세출 배정을 허용하고, 중기재정계획을 실제 회계 집행 단위로 격상하면 $w_t$가 크게 줄어 $e_t^*$도 따라 준다(미국 GPRA 다년도 예산배정 참조). 이는 집행률을 높여 불용을 줄이려는 조기집행·신속집행 기조와 정반대 방향이다 — 후자는 모형상 $w_t$↑로 게임화를 오히려 강화하기 때문이다. 핵심은 예산을 "다 쓰느냐"가 아니라 "언제·어떻게 쓰느냐"다.

  *권고 2 — 출연기관 평가 지표 전환($w_t$↓ + $w_q$↑).* 출연금형의 위상 일관성 0.54 + PSD 진폭 0.332는 모기관-위탁기관의 12월 일률 정산 압력을 보여준다. 경영평가에서 집행률 비중을 축소하고 사업 품질 평가 가중을 확대하면 두 레버가 동시에 움직인다. 단 $w_q$ 증가 효과는 불가능성 정리로 인해 제한적이다.

  *권고 3 — 출연기관 정산 시점 분산($c_(t t)$↑).* 위탁계약별 정산 주기를 분기·반기로 분산하면 12월 직후 시점 조정의 한계 비용이 올라 $e_t^*$가 분산된다. 「공공기관운영법 시행령」의 연 1회 출연금 정산 주기를 개정하는 방안이 있다.

  *권고 4–6.* 데이터 인프라 강화(주별·일별 세분도로 RDD 식별력 + $w_q$ 측정 인프라 동시 확보), 자동 모니터링($c_(t t)$↑; 극단 게임화 활동 상시 식별), 시간 가중 점검(H6 직접 적용; 정책 점검을 최근 3년 자료에 가중)이다. 모형은 $w_t$ 변화 폭이 큰 권고 1의 효과가 가장 크다고 방향상 예측하나, 절대 효과 크기는 자연 실험 보정 없이는 추정할 수 없다. 가장 빠른 도입 가능성은 권고 5다. 측정성 격차가 본질적이므로 이 처방들은 균형점을 옮길 뿐 완전한 해결을 약속하지 않는다(불가능성 정리).

= 한계와 결론

  본 연구의 한계는 모형과 실증으로 나뉜다. 모형은 비교정역학 방향만 식별하고 절대값을 보정하지 못하며(자연 실험 필요), 정적 균형 가정으로 반복 게임의 동적 균형을 담지 못하고, 부처 간 파급을 무시한다. 실증은 외부 통제군 부재(단일 정부 체제), STL 추세 혼재, 분야별 소표본(결과 상관 $N = 8$–$12$, 매개 $n = 4$–$6$), 국방·예비비 결측, 월별 자료의 세분도 부재, 다중 비교 보정의 한계를 안는다. 또한 본 연구가 지목한 분석 단위(사업원형)는 정부 회계의 편성목 구성과 상당 부분 일치하므로(재군집 ARI 0.895) 새로운 잠재 분류의 발견이라기보다 게임화를 가르는 기존 편성목 축의 식별로 한정해 해석해야 하며, 위상 분석이 시사한 출연금형 내부 세분은 후속 과제다. 특히 사회복지 음 상관($r = -0.86$)은 부호가 견고하나 Bonferroni 보정 후 단일 분야의 유의를 주장할 수 없고 메커니즘이 부재하므로 기각된 사례로 보고한다 — 모형이 정렬 함수 $alpha$의 분야별 이질성을 미리 인정한 것이 그 이론적 근거다. 끝으로 분석 대상은 중앙정부이며, 본 연구의 use-it-or-lose-it 압력은 「국가재정법」의 단년도 이월 차단에 기인한다. 지방자치단체에서는 불용이 차기 예산 삭감으로 직결되지 않고 오히려 증가와 연관되기도 해(김용수·노희천, 2021), 이 메커니즘의 지방 일반화에는 지방 예산정치에 대한 별도 고려가 필요하다.

  본 연구는 한국 중앙정부 재정 집행의 게임화를 원리·실증·정책의 3축으로 통합 분석했다. 이론적으로 합리적 대리인의 균형 행동이 측정성 격차 환경에서 자원을 시점 조정으로 쏠리게 함을 도출했고, 실증적으로 분야 단위 분석이 무효($Delta R^2 = 0.000$)이며 게임화의 진짜 단위가 분야가 아니라 편성목 구성(사업원형)임을 데이터로 특정했다 — 군집은 편성목 구성만으로 재현되므로(재군집 ARI 0.895) 기존 편성목 축의 재확인이고, 위상 분석은 그 구조의 안정성을 검증한다. 견고한 발견은 산출 측에 있다 — 자산취득형 RDD 점프 3.42배(H2), 출연금형 사이클 우세(PSD 0.332·phase coherence 0.54, H3), +554% 시간 강화(H6). 결과 측에서는 부트스트랩으로 확증된 분야 연관이 없었으며(H4·H5), 이 측정 공백 자체가 집행률이 정책 결과를 검증할 기반을 갖추지 못했음을 보여주는 진단이다. 정책 처방은 모형의 세 레버에서 직접 도출되며, 불가능성 정리의 본질적 한계를 정직하게 명시한다. 이로써 본 연구는 한국 재정의 오랜 관심사인 연말 쏠림·불용을 "불용=비효율" 관리 프레임에서 측정 게임화 프레임으로 옮겨, 집행률 제고를 향한 표준 처방이 오히려 게임화를 강화할 수 있음을 드러낸다. 한국 재정 집행의 굿하트 게임이 고정 패턴이 아니라 진행 중인 동적 현상이라는 발견은 평가 제도가 측정 대상 행동의 분포를 바꾼다는 수행적 예측(performative prediction)의 인접 사례로 해석되며(Hardt et al., 2016; Perdomo et al., 2020), 후속 자연 실험·국제 비교가 동적 강화를 억제하는 제도 조건을 밝힐 과제로 남는다.

#v(0.6em)

#[
  #set par(first-line-indent: 0pt)
  #text(size: 9.5pt, fill: rgb("#555"))[
    *저자 기여 및 AI 도구 사용 명시(익명화).* 저자 기여는 CRediT 표준에 따라 개념화·이론 도출, 모형·수학 검증, 데이터 정비·재현 점검, 고급 방법론(위상·신호처리) 감수로 분담되었으며 구체적 매핑은 게재 확정 후 공개한다. 데이터 수집·정제·분석 코드 작성·시각화에 생성형 AI 도구(Claude)를 보조적으로 사용했으며, 연구 설계·가설 설정·결과 해석·정책 함의는 전적으로 저자가 결정·검토했고 그 학술적 책임은 저자에게 있다. 코드·데이터·결과는 게재 확정 후 공개 저장소에 공개한다.
  ]
]

// =============================================================
// 부록 (본문 끝 ~ 참고문헌 사이)
// =============================================================
#set heading(numbering: none)

// 부록은 본 연구의 방법론적 기여(기존 재정 연구가 시도하지 않은 분석 단위 발견·검증
// 파이프라인)를 showcase. 상세 도출·전체 강건성은 지면 관계상 생략(게재 후 별도 공개 가능).

= 부록 A. 사업원형의 위상학적 발견·검증(TDA)

기존 재정 연구는 분야·부처라는 행정 분류를 분석 단위로 전제했으나, 본 연구는 활동 단위 임베딩과 위상 데이터 분석(TDA)으로 분석 단위 자체를 데이터에서 발견·검증한다 — 재정 집행 연구에서 시도된 바 없는 접근이다. 본문의 UMAP+HDBSCAN 4개 군집(@fig-umap)이 알고리즘·매개변수의 우연이 아님을, 밀도가 아니라 점들의 "연결 구조"를 보는 Mapper와 "덩어리·구멍"을 모든 거리 척도에서 추적하는 지속적 호몰로지(PH)로 교차 검증한다.

#figure(
  image("figures/h4_mapper_cluster.png", width: 72%),
  caption: [Mapper 그래프 — 밀도 군집(HDBSCAN) 사업원형 색상],
) <fig-mapper>
#tnote[주: 노드 32·엣지 38·연결성분 10. 4개 사업원형이 위상적으로 분리된 연결성분으로 나타나, 밀도 기반 군집(UMAP+HDBSCAN) 결과와 독립적으로 수렴한다.]

#figure(
  image("figures/h9_bootstrap.png", width: 82%),
  caption: [지속적 호몰로지(PH) 부트스트랩 50회 — 다이어그램 거리 검증],
) <fig-ph>
#tnote[주: 피처 무작위 치환(귀무) 분포 대비 Wasserstein-2 거리 — 관측 평균 0.885 vs 귀무 1.524, $p < 0.0001$. 구조의 개수가 아니라 다이어그램 전체 수준에서 4개 원형의 표본 변동 강건성을 입증한다.]

이 위상 검증을 통과한 4개 군집의 z-score 프로파일은 행정 실무 사업 형태와 일치한다(@tbl-zscore). 군집은 12개월 시점 시퀀스가 아니라 편성목 유형 공간에서 정의되므로(실루엣 0.240 대 시점 공간 $-0.179$) "편성목 유형 군집"으로 해석하며, 월별 집행 패턴은 군집 평균으로 사후 서술된다(월별 비중 ANOVA $R^2 = 0.065$).

#figure(
  table(
    columns: (auto, auto, auto, auto, auto),
    align: (left, center, center, center, left),
    table.hline(y: 1, stroke: 1.0pt + black),
    [*군집*], [*n*], [*핵심 피처 z*], [*게임화 진폭 z*], [*해석*],
    [C0 인건비형], [129], [인건비 비중 +3.07], [$-1.30$], [매월 균등 지급, 평탄],
    [C1 자산취득형], [99], [자산취득 비중 +3.28], [중간], [공정률 따라 변동, 12월 점프],
    [C2 출연금형], [154], [출연금 비중 +2.89], [+0.83], [위탁 정산, 연 사이클(연초 집중·12월 최저)],
    [C3 정상사업], [1,175], [평균 부근], [평균 부근], [베이스라인 잔류 군집],
  ),
  caption: [4개 사업원형의 z-score 프로파일 (1,557개 활동)],
) <tbl-zscore>

= 부록 B. 게임화 강도의 시간–주파수 분석(연속 웨이블릿)

FFT 진폭은 11년 평균이라 시간 변화를 보지 못한다. 연속 웨이블릿 변환(complex Morlet)은 시점마다 주기별 강도를 분해해 게임화의 시간 진화를 드러낸다 — 정책 변화점이 잦은 재정 시계열에 정상성 가정을 강요하지 않는, 기존 재정 연구에서 드문 접근이다. 스펙트럼 삼각검증에서 출연금형은 12개월 주기 PSD k=1 진폭 0.332·활동 간 위상 일관성 0.54로 외생 회계 주기에 가장 강하게 결속되며, 그 강도가 표본 기간 +554% 강화된다(본문 @tbl-h6-evol, @fig-h28-evol).

#figure(
  image("figures/h28_scaleogram.png", width: 86%),
  caption: [사업원형별 웨이블릿 스케일로그램(시간 × 주기 파워)],
) <fig-scaleogram>
#tnote[주: 밝을수록 강한 주기 강도. 출연금형(최대 파워 1.65)의 12개월 주기 띠가 가장 밝고 2018년 이후 갈수록 강해져 +554% 시간 강화를 직접 시각화한다. 인건비형은 띠가 거의 없어 통제군으로 기능한다.]

// =============================================================
// 참고문헌 — NABO 양식 (논문 큰따옴표·저서『』/영문 이탤릭·학술지 이탤릭·pp.면수·내어쓰기, 한글→동양어→영어→서양어 순)
// =============================================================
#v(1.0em)
#align(center)[#text(size: 14pt, weight: "bold", font: head-font)[참고문헌]]
#v(0.6em)

#[
  #set par(first-line-indent: 0pt, hanging-indent: 2em, leading: 0.9em, spacing: 0.85em, justify: false)

  강윤호·정여희·김보영, 「지방자치단체 예산불용액의 결정요인 분석: 예산운용에 대한 정치경제학적 접근」, 한국사회와 행정연구, 제35권 제3호, 2024, pp.199–226.

  김용수·노희천, 「불용액이 차기 예산편성에 미치는 영향: 지방자치단체의 특성 요인을 중심으로」, 정부회계연구, 제19권 제1호, 2021, pp.37–68.

  양인용·배기수, 「중앙정부의 불용액과 이월액에 대한 효율적 관리방안」, 경영교육연구, 제34권 제1호, 2019, pp.341–363.

  양지숙·오현주, 「지방재정관리제도가 지방자치단체 예산집행에 미치는 영향: 불용액 및 이월액을 중심으로」, 한국공공관리학보, 제34권 제3호, 2020, pp.25–48.

  한국재정정보원, 「재정지출 효율화를 위한 불용유형 분석 및 집행관리방안」, 분석보고서 22-03, 2022.

  Baker, G. P., “Incentive Contracts and Performance Measurement,” #emph[Journal of Political Economy], Vol. 100, No. 3, 1992, pp.598–614.

  Baron, R. M. and D. A. Kenny, “The Moderator-Mediator Variable Distinction in Social Psychological Research: Conceptual, Strategic, and Statistical Considerations,” #emph[Journal of Personality and Social Psychology], Vol. 51, No. 6, 1986, pp.1173–1182.

  Bevan, G. and C. Hood, “What’s Measured Is What Matters: Targets and Gaming in the English Public Health Care System,” #emph[Public Administration], Vol. 84, No. 3, 2006, pp.517–538.

  Campbell, D. T., “Assessing the Impact of Planned Social Change,” #emph[Evaluation and Program Planning], Vol. 2, No. 1, 1979, pp.67–90.

  Campello, R. J. G. B., D. Moulavi, and J. Sander, “Density-Based Clustering Based on Hierarchical Density Estimates,” in #emph[Advances in Knowledge Discovery and Data Mining (PAKDD 2013)], 2013, pp.160–172.

  Edelsbrunner, H. and J. Harer, “Persistent Homology — A Survey,” in #emph[Surveys on Discrete and Computational Geometry: Twenty Years Later], Contemporary Mathematics Vol. 453, American Mathematical Society, 2008, pp.257–282.

  Goodhart, C. A. E., “Problems of Monetary Management: The U.K. Experience,” Papers in Monetary Economics, Reserve Bank of Australia, 1975.

  Hardt, M., N. Megiddo, C. Papadimitriou, and M. Wootters, “Strategic Classification,” in #emph[Proceedings of the 2016 ACM Conference on Innovations in Theoretical Computer Science], 2016, pp.111–122.

  Holmström, B., “Managerial Incentive Problems: A Dynamic Perspective,” #emph[Review of Economic Studies], Vol. 66, No. 1, 1999, pp.169–182.

  Holmström, B. and P. Milgrom, “Multitask Principal-Agent Analyses: Incentive Contracts, Asset Ownership, and Job Design,” #emph[Journal of Law, Economics, and Organization], Vol. 7, 1991, pp.24–52.

  Imbens, G. W. and T. Lemieux, “Regression Discontinuity Designs: A Guide to Practice,” #emph[Journal of Econometrics], Vol. 142, No. 2, 2008, pp.615–635.

  Kornai, J., #emph[Economics of Shortage], North-Holland, 1980.

  Lee, D. S. and T. Lemieux, “Regression Discontinuity Designs in Economics,” #emph[Journal of Economic Literature], Vol. 48, No. 2, 2010, pp.281–355.

  Liebman, J. B. and N. Mahoney, “Do Expiring Budgets Lead to Wasteful Year-End Spending? Evidence from Federal Procurement,” #emph[American Economic Review], Vol. 107, No. 11, 2017, pp.3510–3549.

  McInnes, L., J. Healy, and J. Melville, “UMAP: Uniform Manifold Approximation and Projection for Dimension Reduction,” arXiv:1802.03426, 2018.

  Morris, S. and H. S. Shin, “Social Value of Public Information,” #emph[American Economic Review], Vol. 92, No. 5, 2002, pp.1521–1534.

  Perdomo, J., T. Zrnic, C. Mendler-Dünner, and M. Hardt, “Performative Prediction,” in #emph[Proceedings of the 37th International Conference on Machine Learning], 2020, pp.7599–7609.

  Singh, G., F. Mémoli, and G. Carlsson, “Topological Methods for the Analysis of High Dimensional Data Sets and 3D Object Recognition,” in #emph[Eurographics Symposium on Point-Based Graphics], The Eurographics Association, 2007, pp.91–100.
]

// =============================================================
// 영문 초록 (맨 끝)
// =============================================================
#pagebreak()

#align(center)[
  #v(4pt)
  #text(size: 14pt, weight: "bold", font: head-font)[The Goodhart Game in Korean Government Budget Execution: A Principal-Agent Equilibrium Analysis and Archetype-Level Causal Identification]
  #v(8pt)
  #text(size: 10.5pt, fill: rgb("#444"))[Author name (to be filled in only at final submission)]
]

#v(8pt)

#graybar[Abstract]

#[
  #set par(first-line-indent: (amount: 1em, all: true), leading: 0.7em, justify: true, spacing: 0.7em)
  #set text(size: 10.5pt)
  This study derives the micro-mechanism of Goodhart effects in Korean central-government budget execution through a principal-agent equilibrium model and tests six hypotheses on an eleven-year (2015–2025) monthly execution panel of 1,557 activities and outcome indicators for 14 policy fields. A measurability gap—execution rates are perfectly measured while program quality is not—biases a rational agent’s resources toward timing-adjustment effort, which we formalize through a multitasking-contract framework. Activity-level embedding derives four program archetypes (personnel, asset-acquisition, grant, and normal)—which largely recover the government's existing budget-line composition—and topological analysis verifies their sampling stability; field fixed effects add no explanatory power to gaming (ΔR²=0.000) whereas archetype interactions do (ΔR²=+0.025), establishing the archetype—not the field—as the unit of variance. In a fiscal-year-end regression discontinuity, asset-acquisition programs exhibit a strong December jump (3.42×) relative to the overall mean (1.91×), and continuous wavelet analysis shows that grant-type gaming intensified by +554% over the sample period. The robust findings lie on the output side; associations with field outcomes remain unconfirmed, indicating that execution rates lack the program-level micro-data needed to validate policy outcomes. The policy prescription is not newly invented: the contribution is to pinpoint, with data, the model’s three comparative-static levers and their empirical targets.

  #v(6pt)
  #set par(first-line-indent: 0pt)
  □ #text(weight: "bold")[Keywords:] Goodhart’s Law, Principal-Agent Model, Multitasking Contracts, Regression Discontinuity, Program Archetype
]
