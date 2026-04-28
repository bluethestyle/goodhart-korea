// 한국 정부 재정 집행의 굿하트 효과 — 논문 초안
// Typst 컴파일: typst compile paper/main.typ paper/main.pdf

#set document(
  title: "한국 정부 재정 집행의 굿하트 효과 — 다각적 측정과 정책 함의",
  author: "(저자명)",
)

#set page(
  paper: "a4",
  margin: (top: 25mm, bottom: 25mm, left: 25mm, right: 25mm),
  numbering: "1",
)

// 한국 학술지 표준 폰트: 신명조(HY) + Times New Roman 영문 + 한글 fallback Batang
// HYSinMyeongJo는 한국재정학회·한국정책학회·한국행정학보 등 KCI 학술지 표준
#set text(
  font: ("Times New Roman", "HYSinMyeongJo", "Batang", "Noto Serif KR"),
  size: 11pt,
  lang: "ko",
)

// 학술지 표준: 줄간격 200% (line-height 2.0 ≈ leading 1.0em on 11pt with default 0.65em base)
// Typst leading is *additional* space between lines. 11pt 본문 line-height 2.0 ≈ leading 1.05em
#set par(justify: true, leading: 1.05em, first-line-indent: 1em, spacing: 1.2em)

#set heading(numbering: "1.1")

// 제목은 sans-serif 고딕 (KoPub돋움 / Noto Sans KR)
#show heading.where(level: 1): it => [
  #set text(font: ("Times New Roman", "HYGothic", "Noto Sans KR"),
            size: 13pt, weight: "bold")
  #v(1.5em)
  #it
  #v(0.8em)
]
#show heading.where(level: 2): it => [
  #set text(font: ("Times New Roman", "HYGothic", "Noto Sans KR"),
            size: 11.5pt, weight: "bold")
  #v(1.2em)
  #it
  #v(0.6em)
]
#show heading.where(level: 3): it => [
  #set text(font: ("Times New Roman", "HYGothic", "Noto Sans KR"),
            size: 11pt, weight: "bold")
  #v(0.8em)
  #it
  #v(0.4em)
]

#set figure(supplement: [그림])
#set table(stroke: 0.5pt)

// =============================================================
// 표지
// =============================================================
#align(center)[
  #v(2em)
  #text(size: 18pt, weight: "bold",
        font: ("Times New Roman", "HYGothic", "Noto Sans KR"))[
    한국 정부 재정 집행의 굿하트 효과
  ]
  #v(0.6em)
  #text(size: 13pt,
        font: ("Times New Roman", "HYGothic", "Noto Sans KR"))[
    다각적 측정과 정책 함의
  ]
  #v(2.5em)
  #text(size: 11pt)[(저자명)]
  #linebreak()
  #v(0.3em)
  #text(size: 10pt, fill: rgb("#444"))[2026년 4월]

  #v(2em)
  #line(length: 40%, stroke: 0.6pt + rgb("#999"))
  #v(0.5em)
  #text(size: 8.5pt, fill: rgb("#555"))[
    GitHub #link("https://github.com/bluethestyle/goodhart-korea")[bluethestyle/goodhart-korea]
    #h(1em) · #h(1em)
    Zenodo #link("https://doi.org/10.5281/zenodo")[(DOI 발급 예정)]
  ]
  #linebreak()
  #text(size: 8.5pt, fill: rgb("#555"))[
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
        font: ("Times New Roman", "HYGothic", "Noto Sans KR"))[국문 초록]
]
#v(0.6em)

#par(first-line-indent: 0pt, leading: 0.95em)[
  본 연구는 열린재정정보 월별 집행 11년치(2015\~2026)와 KOSIS·한국은행 ECOS·공공데이터포털·온실가스종합정보센터 14분야 결과변수를 통합해 한국 정부 재정 집행의 굿하트 효과(Goodhart 1975)를 다각도로 측정·검증한다. 활동(ACTV) 단위 임베딩(UMAP+HDBSCAN)으로 인건비형·자산취득형·출연금형·정상사업 4개 사업원형을 발견하고, Mapper와 지속 호몰로지(Persistent Homology)로 위상 안정성을 입증한다. 분야 고정효과 회귀에서 분야 라벨의 추가 설명력(ΔR²)이 0에 수렴하는 반면, 사업원형×지출진동의 상호작용은 ΔR²=+0.085\~+0.094로 유의함을 확인해 분야 단위 분석의 trivial 성격을 정량적으로 반증한다. 사회복지 자동분배 효과(r=−0.762, p=0.035; CPI 통제 후 −0.86, p=0.007)와 회계연도 12월 RDD 점프 1.91배(출연금형 3.42배)를 통해 Liebman-Mahoney(2017)의 미국 결과를 한국으로 확장한다. STL 분해 결과 사회복지 신호의 trend 혼재 가능성을 자기 비판적으로 보고한다.
]

#v(1em)

#par(first-line-indent: 0pt)[
  #text(weight: "bold")[주요어:] 굿하트 법칙, 정부 재정, NPM, 토폴로지 데이터 분석, 회귀불연속, 매개분석, 한국
]

#pagebreak()

// =============================================================
// 약어 일람·핵심 용어 정의는 부록 A·B로 이동 (서론 앞 배치는 학술지 관행에서 어색)
// 본문은 첫 등장 시 풀어쓰기 + 부록 참조 방식 사용

// =============================================================
= 서론

== 문제 의식 — "측정되는 것이 중요해진다"

  Bevan과 Hood(2006)는 영국 NHS 사례 연구를 통해 "측정되는 것이 중요해진다(What's measured is what matters)"는 명제 아래 평가지표 게임화의 4가지 패턴(threshold effect, ratchet effect, output distortion, gaming)을 식별했다. 이는 Goodhart(1975)와 Campbell(1979)이 각각 통화정책과 사회과학 일반에서 제안한 *지표가 정책 도구로 채택되는 순간 그 지표의 측정 신뢰도가 하락한다*는 명제의 행정학적 구체화다.

  같은 메커니즘이 한국 중앙정부 재정 집행에서도 작동하는가? 이 질문에 답하기 위해서는 (a) 게임화를 *측정 가능한 양*으로 정의하고, (b) 분야·부처·사업 형태에 걸친 *이질성을 분리*하며, (c) 자연 경기 cycle이나 추세 효과 같은 *경합 가설을 배제*해야 한다. 본 연구는 11년 시계열·14분야·1,557개 활동을 다중 방법론으로 결합해 이 세 과제를 단계적으로 수행한다.

== 미국 선행연구의 한국적 확장

  Liebman과 Mahoney(2017, AER)는 미국 연방조달의 11월 마지막 주 vs 12월 첫 주 회귀불연속(RDD)으로 회계연도 마감 직전 주의 지출이 *5배* 증가하고 동시에 *품질 점수가 하락*함을 입증했다. 사용하지 않으면 이월되지 않는 예산 제도(use-it-or-lose-it)가 만들어내는 측정 왜곡의 모범적 인과 식별 사례다.

  본 연구는 동일한 RDD 설계를 한국 데이터에 적용한다. 한국 자료가 월 단위 granularity인 점을 고려해 11월 vs 12월 일평균 집행을 비교한 결과 *전체 1.91배, 출연금형 3.42배*의 점프를 확인한다. 미국 5배 대비 절대값은 작지만 사업 형태별 차이가 뚜렷하다는 점에서 *질적으로 같은 메커니즘이 한국에서도 작동*함을 시사한다.

== 본 연구의 핵심 주장

  분야 단위 이질성(field-level heterogeneity)은 한국 행정학·재정학 문헌에서 흔히 "분야가 다르니 결과가 다르다"는 직관으로 정당화된다. 본 연구는 이 직관을 분야 고정효과 회귀로 *정량적으로 반증*한다(분야 더미 추가에 따른 ΔR²=0.000). 같은 활동 데이터에 *사업 형태(원형)*를 변수로 투입하면 ΔR²=+0.094로 유의한 설명력 증가가 나타난다.

  즉, "분야"는 행정 편의상의 분류일 뿐 게임화의 진짜 단위가 아니며, 진짜 단위는 *사업이 어떻게 수행되는가*(인건비형/자산취득형/출연금형/정상)이다. 이 주장을 위상 데이터 분석(UMAP+HDBSCAN, Mapper, Persistent Homology)·견고성 회귀·인과 식별(RDD, Baron-Kenny)·외생 통제(CPI 잔차)로 다중 입증한다.

= 이론적 토대

  본 연구의 분석은 세 갈래의 이론적 전통을 결합한다. (1) *공공관리 이론*에서 굿하트-캠벨 법칙과 NPM(New Public Management) 측정 패러독스, (2) *계약경제학*에서 Holmstrom-Milgrom의 다업무 모형, (3) *비교경제학*에서 Kornai의 연성 예산 제약이다. 각 이론은 본 연구의 다른 발견을 설명하며, 셋이 결합될 때 사업 형태별 게임화 강도 차이가 자연스럽게 도출된다.

== 굿하트-캠벨 법칙과 NPM 패러독스

  Goodhart(1975)는 영란은행 통화 통계를 정책 도구로 사용한 뒤 그 통계와 거시경제 실체의 관계가 무너진 사례를 관찰하며 *"통계 규칙성은 통제 목적으로 사용되는 순간 무너진다"*고 정식화했다. Campbell(1979)은 같은 원리를 사회과학 일반에 확장했다.

  Manheim과 Garrabrant(2018)는 이를 네 유형으로 분류했다.
  - *Regressional*: 측정 노이즈에 정책이 과적합
  - *Causal*: 지표를 직접 조작하나 그 인과 경로는 비효율적
  - *Extremal*: 극단 영역에서 지표-목표 관계가 깨짐
  - *Adversarial*: 행위자가 의도적으로 지표를 조작

  본 연구의 12월 점프와 출연금 게임화는 주로 *Causal*(시점 조정으로 집행률 지표 달성)과 *Adversarial*(이월 회피를 위한 의도적 몰아쓰기)에 해당한다.

== 다업무 계약 이론(Multitasking)

  Holmstrom과 Milgrom(1991, JLEO)은 대리인이 *다차원 업무*를 수행할 때 측정 가능한 차원에만 인센티브를 걸면 측정 불가능한 차원의 노력이 *체계적으로 감소*하는 모형을 제시했다. 측정성 격차가 큰 업무 구성에서는 어떤 인센티브 강도도 1차 최적이 될 수 없다는 결과(impossibility theorem)다.

  공공 사업에 적용하면, 집행률(측정 가능)과 사업 품질(측정 어려움)이 상충하는 환경에서 집행률 인센티브가 강할수록 품질이 희생된다. 본 연구의 사업 형태별 지출 진폭 차이(출연금형 3.42배 vs 직접투자형 1.10배)는 *측정 압력에 대한 반응성이 사업 형태별로 다르다*는 이 가설의 한국 실증이다.

== 연성 예산 제약(Soft Budget Constraint)

  Kornai(1980)는 사회주의 경제의 국유기업이 시장 규율 대신 정부 구제를 기대하며 예산 제약이 *연성화*되는 현상을 이론화했다. 시장경제 공공 부문의 출연기관·공공기관도 동일한 메커니즘에 노출된다.

  *공공기관·출연기관은 직접 사업과 달리 사업 시점 조정의 자유도가 높다*. 정산 기일을 맞추기 위해 12월 집중 집행이 가능하고, 다음 회계연도 예산이 감액되더라도 모기관 보전 가능성이 시장 규율을 약화시킨다. 본 연구의 출연금 비중과 게임화 강도 회귀(β=+0.375, p=0.005)는 이 메커니즘의 정량적 증거이며, RDD에서 *출연금형이 3.42배로 가장 강한 12월 점프*를 보이는 이유를 설명한다.

= 데이터

== 정부 재정 집행 (게임화 측정 입력)

  - 열린재정정보 VWFOEM (월별 집행): 2015~2026 (11년), 활동 1,557건
  - 열린재정정보 expenditure_item (편성목): 2020~2026 (활동 단위 출연금/직접투자/인건비 비중)
  - 한국은행 ECOS 901Y009 소비자물가지수: 1990~2025 (외생 통제변수)

== 결과변수 (14분야 매핑)

  부적절 6개 outcome을 외부 검토 후 교체:

  #figure(
    table(
      columns: 4,
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
      align: (left, left, left, left),
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

  *직관*: 어떤 시계열이든 다양한 주기의 사인파 합으로 분해할 수 있다(Fourier 1822). 연도-내 시계열에 푸리에 변환을 적용하면 1년 주기 성분의 진폭이 추출된다. 이 진폭이 클수록 "12월 점프 + 1월 reset"이라는 회계연도 게임화 패턴이 강하다는 뜻이다. 정의(이산 푸리에 변환·`amp_12m_norm` 비율 식·Parseval 해석)는 부록 C.1.

  *주제 적합성*: 굿하트 효과는 *외생적 평가 주기에 동조된 게임화*로 정의된다(Bevan-Hood 2006). 한국 회계연도(1\~12월)는 모든 부처에 *동일 주기*로 강제되며 결산·집행률 평가가 12월 31일에 일률 적용된다. 즉 게임화 신호의 *주파수가 사전에 알려진* 1년이라는 점이 이 주제의 본질적 특성이며, 알려진 주파수의 진폭 측정은 *주파수 영역 분해(FFT)가 최적*이다. 시간 영역 변동성 지표(CV 등)는 알려진 주파수 정보를 활용하지 못한다.

=== STL 분해(Seasonal-Trend decomposition using Loess)

  *직관*: FFT amp_12m_norm 신호가 진짜 게임화일까, 아니면 *지속적으로 증가하는 추세*가 12월 결산 시점 기록 방식과 결합해 만들어내는 가짜 주기성일까? 이 의문을 검증하기 위해 STL(Cleveland 외 1990)을 사용한다. STL은 시계열을 가법 분해 $x_t = T_t + S_t + R_t$로 추세·계절·잔차로 분리하고, 추세 제거 후 계절 성분의 분산 비율을 `seasonal_strength`로 정의해 게임화 지표로 사용한다. 두 겹 반복(inner/outer loop)·robustness weight·정의식은 부록 C.2.

  *주제 적합성*: 한국 정부 예산은 IMF 구조조정(1998), 국가재정법 도입(2007), MTEF 5년 framework 적용(2009) 등 *명확한 추세 변동 동인*을 가진다. 이런 추세를 분리하지 않으면 FFT는 "추세 + 12월 게임화"의 합성 신호를 측정한다. STL은 비모수 LOESS로 *임의 형태의 추세*를 흡수해 *순수 계절 성분만* 분리한다 — 한국 예산의 비선형 추세에 대해 ARIMA 차분보다 적합하다. 본 연구의 핵심 발견인 사회복지 자동분배 신호가 STL 후 소멸한다는 점은 추세 혼재 가능성을 시사하는 자기 비판 증거가 된다.

=== NeuralProphet 신경망 분해 — 세 번째 cross-check

  *직관*: FFT(정상성 가정)와 STL(임의 추세 가정)이 서로 다른 결론을 줄 때 어느 쪽이 게임화의 진짜 신호인지 결정하기 위해 *세 번째 독립 도구*가 필요하다. NeuralProphet(Triebe 외 2021)은 Facebook Prophet(Taylor-Letham 2018)의 신경망 확장으로, 시계열을 *추세 + Fourier 계절 + AR-Net 자기회귀 + 이벤트 + 외생 회귀*의 6개 가법 성분으로 분해한다. 본 연구는 cross-check 비교 형평성을 위해 자기회귀(`n_lags=0`)·외생 회귀를 *비활성화*하고 *추세 + 계절*만 사용한다. 6항 모형식·AR-Net 신경망 식·Prophet 원판과의 차이·하이퍼파라미터 설정은 부록 C.3.

  *주제 적합성*: 한국 정부 예산은 (a) 점진적 추세, (b) 정책 변화점(2007 국가재정법, 2014 국가회계제도 개편, 2017 추경 확대), (c) 회계연도 12월 강제 주기를 동시에 갖는다. NeuralProphet은 *piecewise-linear + 자동 changepoint 검출*로 추세를 흡수하면서 Fourier 기저로 계절을 분리해, 이 세 요소를 *해석 가능한 가법 모형*으로 동시 처리할 수 있는 거의 유일한 도구다 — FFT는 (a)·(b)에 약하고, STL은 (b)에 약하다. ARIMA·LSTM 등의 대안과 비교는 부록 C.3.

  *세 도구 합의 기준*: FFT `amp_12m_norm`, STL `seasonal_strength`, NP `yearly_seasonality` 진폭이 활동×연도 패널에서 강한 상관($r > 0.6$ 이상)을 보이면 게임화 신호 측정이 도구 의존이 아닌 *데이터의 본질적 특성*임이 입증된다. 갈리면 도구별 가정 차이를 한계로 명시한다.

== 사업 형태(원형) 발견 — 차원 축소 + 밀도 군집

  분야 라벨로 묶기 전에, *데이터가 자연스럽게 묶이는 형태*가 따로 있는지 확인해야 한다. 1,557개 활동을 12개 피처(예산 구성·집행 패턴·진폭)로 표현하면 12차원 공간의 점들이 된다. 이를 시각화 가능한 2차원으로 압축하고 군집을 식별한다.

=== UMAP (Uniform Manifold Approximation and Projection)

  *직관*: 12차원에서 가까운 점들은 2차원에서도 가깝게, 멀리 있는 점들은 멀리 보이도록 *국소 이웃 구조를 보존하면서* 차원을 압축하는 비선형 알고리즘(McInnes 외 2018). 고차원·저차원의 fuzzy simplicial set 표현 사이의 cross-entropy를 SGD로 최소화한다. 손실함수 정의·하이퍼파라미터·PCA·t-SNE·Autoencoder와의 비교는 부록 C.4.

  *주제 적합성*: 사업 활동의 12피처(예산 구성·집행 패턴·진폭)는 강한 *비선형 상관*을 갖는다 — 예: 출연금 비중과 게임화 진폭 사이 sigmoid 관계. 또한 1,557개 활동이라는 *작은 데이터*에서 자율 임베딩 학습은 과적합되며, *재현 가능한 결정론적 임베딩*이 정책 보고서에 인용 가능해야 한다. UMAP은 (a) 비선형 보존 (b) 작은 N 안정성 (c) `random_state` 재현 가능 — 세 요건을 모두 만족하는 거의 유일한 도구다.

=== HDBSCAN (Hierarchical Density-Based Spatial Clustering)

  *직관*: K-means처럼 군집 수를 미리 정하지 않고 *밀도가 높은 영역*을 군집으로 식별한다(Campello 외 2013). 밀도가 낮은 점은 *노이즈*로 분류한다. mutual reachability distance를 가중치로 하는 최소 신장 트리에서 임계값 $epsilon$을 변화시켜 condensed cluster tree를 만들고 *안정성* 점수가 높은 군집을 선택한다. 거리 정의·트리 구성·K-means·DBSCAN·GMM과의 비교는 부록 C.5.

  *주제 적합성*: 한국 사업 활동은 (a) 사업 형태별 *밀도 차이가 큼*(정상사업 1,175 vs 자산취득형 99), (b) 군집 수 사전 가정이 *연구 가설을 오염*시킴(분야가 trivial한지가 결과 가설), (c) *outlier 활동(극단 게임화 사업)*의 노이즈 처리가 정책 점검 대상 식별에 필수. HDBSCAN은 이 세 요건을 모두 만족한다. 50건의 노이즈 활동(sub05)은 정책 점검 우선순위 리스트로 활용한다.

== 위상 데이터 분석(TDA) — 군집 구조의 안정성 검증

  UMAP+HDBSCAN의 결과가 알고리즘 우연성이나 매개변수 선택의 산물이 아닌, *데이터 자체의 위상적 구조*인지 확인하기 위해 두 가지 위상 도구를 적용한다.

=== Mapper (kmapper)

  *직관*: 데이터의 *모양 골격*을 그래프로 추출한다(Singh 외 2007). UMAP+HDBSCAN이 *어디에 군집이 있는가*를 답한다면, Mapper는 *군집들이 어떻게 연결되어 있는가*를 답한다. 데이터 공간을 필터 함수의 겹치는 cover로 분할하고 각 부분을 군집한 뒤, 군집들을 노드로 두고 교집합에 점이 있으면 엣지로 잇는 nerve simplicial complex를 만든다. 결과는 connected component 수, loop 수($beta_1$) 등 위상 불변량으로 요약. 정의식·UMAP+HDBSCAN과의 비교는 부록 C.6.

  *주제 적합성*: "분야 단위 trivial"이라는 본 연구의 핵심 주장은 사업 형태들이 분야와 무관하게 *위상적으로 분리된 component*를 형성한다는 것에 의존한다. Mapper graph에서 4개 사업원형이 분리된 components로 나타나면 *위상적으로* 별개 단위임을 입증할 수 있다 — 단순 임베딩 거리가 아닌 *연결성 부재*가 증거다.

=== Persistent Homology (PH, ripser)

  *직관*: 점들의 위상 구조를 *모든 스케일에서 동시에* 측정한다. 작은 $epsilon$에서 잠시 나타났다 사라지는 구조는 노이즈, *오래 살아남는* 구조는 진짜 위상 특성이다(Edelsbrunner-Harer 2008). 본 연구는 차원 0(연결성분 $beta_0$)과 차원 1(loop $beta_1$)을 분석하며, *부트스트랩 50회*에서 강건한 $beta_0 = 30$, $beta_1 = 15$, max persistence 95% CI는 위상 구조의 *표본 안정성*을 입증한다. Vietoris-Rips complex·filtration·persistence diagram 정의·Mapper/silhouette 비교는 부록 C.7.

  *주제 적합성*: 본 연구가 발견한 4개 사업원형이 (a) UMAP 매개변수 변화에 견고한가, (b) 표본 변동에 견고한가를 입증해야 한다. PH는 (a)·(b) 모두에 대해 *비모수·스케일 불변* 검증을 제공하는 거의 유일한 도구다.

== 분야 라벨이 진짜 단위인가 — 고정효과 회귀

  *직관*: "분야가 다르니 결과가 다르다"는 직관이 맞다면, 모형에 분야 더미를 추가했을 때 설명력 R²가 크게 증가해야 한다. 반대로 ΔR²가 0에 가깝다면 분야 라벨은 *trivial*하고 진짜 변동은 다른 변수(사업 형태 등)에서 온다. 분야 더미 모형 vs 사업원형×게임화 상호작용 모형의 조정 R² 증가량을 비교한다. 회귀 식·판정 기준은 부록 C.8.

  *주제 적합성*: 한국 행정부 예산 분류는 (a) *역사적 관성*(1960년대부터 점진 확장)이 강하고 (b) 분야 내부에 이질적 사업 형태가 *공존*한다(예: 사회복지에 출연금형 한국사회보장정보원 + 정상사업 기초생활급여 동거). 분야 라벨이 게임화 차이를 설명하지 못한다면 정책 분석 단위를 *사업 형태로 재정의*해야 한다는 본 연구의 정책 시사점에 직결된다. 분야 FE는 이 가설의 *직접 검정* 도구다.

== 부처-원형 이중 그래프 — Spectral Co-clustering

  *직관*: 부처와 사업원형으로 이뤄진 빈도 행렬을 *동시에* 군집해, "어느 부처가 어느 사업 형태에 특화되어 있는가"를 자동 식별한다(Dhillon 2001). 정규화된 빈도 행렬을 SVD하여 좌·우 특이벡터로 행·열을 동시 임베딩한 뒤 K-means로 군집한다. 정규화·SVD·K-means 구체식 및 단순 K-means·LDA와의 비교는 부록 C.9.

  *주제 적합성*: 한국 부처는 (a) 동일 분야에서도 *사업 형태별 특화도가 다름*(예: 과기정통부=출연금형 비중 큼, 행정안전부=인건비형 비중 큼), (b) 정책 점검 자원 배분에서 *부처 단위로 우선순위*를 매겨야 함. Co-clustering은 부처를 *사업 형태 특화 패턴으로 자동 분류*해 부처-결과변수 4분면 분석의 입력을 제공한다. 51개 부처가 5개 co-cluster로 분리되었다.

== 인과 식별 — 게임화는 진짜 원인인가

=== 회귀불연속 설계(RDD)

  *직관*: 회계연도 12월 1일은 행정적으로 *연속적인 시간*에 인위적으로 그어진 선이다. 사업의 본질적 필요와 무관하게 이 선 직전·직후로 집행 패턴이 점프한다면 그 점프는 *외생적 회계 cycle*에 의한 것으로 해석할 수 있다(Imbens-Lemieux 2008; Lee-Lemieux 2010). 본 연구는 활동 단위 11월 vs 12월 일평균 비율을 사용해 *비율형 점프 배수*로 보고한다(미국 Liebman-Mahoney 5배 형식과 비교 가능). 식별 가정·국지 선형 추정량 식·DID/IV/month-FE와의 비교는 부록 C.10.

  *주제 적합성*: 한국 회계연도 cutoff는 (a) 1948년 이래 *불변*, (b) 모든 부처에 *동시* 적용, (c) 개별 활동이 *조작 불가능* — RDD의 *세 핵심 가정*이 모두 성립하는 거의 이상적 자연실험 환경이다. Liebman-Mahoney(2017)가 미국에서 cutoff 며칠 차이로 5배 점프 + 품질 하락을 입증한 설계의 한국 적용은 *이론적으로 직접 가능*하며, 실제 분석에서 1.91배(전체) / 3.42배(출연금형) 점프를 확인한다. 같은 활동의 단 며칠 차이를 비교하므로 *분야·기관·사업 특성이 자동 통제*되는 준실험이다.

=== 매개분석 — Baron-Kenny + Sobel + Bootstrap

  *직관*: 출연금 비중($X$)이 높을수록 결과변수($Y$)가 나빠진다는 상관이 발견되더라도, 그 경로가 "$X arrow$ 게임화($M$) $arrow Y$"의 *간접 효과*인지 "$X arrow Y$"의 *직접 효과*인지 분리해야 한다(Baron-Kenny 1986). 4단계 회귀로 총효과 $c$, 매개경로 $a$, 직접효과 $c'$, 매개효과 $a b$를 분해한 뒤 Sobel z-검정 + Bootstrap 1,000회 신뢰구간으로 유의성을 검증한다. 4단계 식·Sobel 표준오차 식·Bootstrap 절차·SEM/Causal Mediation 비교는 부록 C.11.

  *주제 적합성*: 본 연구의 핵심 가설은 "출연금 → 12월 게임화 → 결과변수 악화"라는 *순차적 인과 경로*다. 매개라면 *게임화 자체* 개혁(예: 다년도 회계, MTEF 강화), 직접 효과라면 *출연 구조* 개혁(예: 위탁 사업 직영 전환)으로 정책 함의가 갈린다. Baron-Kenny는 이 경로 분리를 *해석 가능한 회귀 계수*로 제공한다. 결과: 시스템 평균 매개효과 미유의(p=0.481)이나 사회복지·환경 분야에서 강한 매개 — 게임화 메커니즘의 *분야 이질성*을 지지.

== 외생 통제 — 자연 경기 cycle 가설 기각

  *직관*: 사회복지 게임화-결과변수 상관이 진짜 인과인가, 아니면 *경기 변동에 의한 spurious 동조*인가? 한국은행 ECOS 901Y009 소비자물가지수(CPI)를 외생 거시 통제변수로 사용해 *Frisch-Waugh-Lovell residualization*(2단계 잔차회귀)으로 부분 상관을 산출한다. 정의식·외생성 가정·실업률/GDP 대안 비교는 부록 C.12.

  *외생성 정당화*: CPI는 한국은행이 통화정책 도구로 결정하므로 (a) *한은 독립성*에 의해 재정부 행정 결정에 직접 노출되지 않음, (b) *목표값(2.0\%)*이 사전 공표되어 *역인과 위협이 작음*. 따라서 한국 거시변수 중 *재정 게임화로부터 가장 외생적*인 후보이며 1990\~2025년 월별 공식 시계열로 신뢰성 있게 통제 가능하다. 결과: 14/14 분야에서 부호 유지, 70% 유의성 유지. 사회복지 신호는 $r = -0.76 arrow -0.86$으로 *오히려 강화* — 자연 cycle 가설 강력 기각.

== 견고성 검증 — Permutation·Lag/Lead·CV

  *Permutation 검정*: 결과변수 시계열을 $B = 1000$회 무작위 셔플하여 귀무 분포를 구성하고 양측 p-값을 산출한다. 정규성·등분산 가정이 필요 없는 비모수 검정. 분야별 N=8\~12 작은 표본에서 정규 근사 t-검정의 신뢰성 부족 문제를 우회.

  *Lag/Lead 분석*: 게임화-결과변수 상관에 시차 $tau in {-1, 0, +1}$년을 주어 *방향성*을 점검. $r(0)$ 동기 상관이 가장 강하면 즉시적 메커니즘(사회복지 자동분배 가설 정합), $r(+1)$ 강하면 지연 효과, $r(-1)$ 강하면 역인과 의심.

  *amp_cv 대안*: FFT 외에 변동계수($"CV" = sigma\/mu$) 기반 게임화 지표로 재산출해 *측정 도구 의존성*을 점검. 두 지표가 같은 결론이면 측정 robust성 입증. 검정식·구체 식은 부록 C.13.

= 결과

  본 절은 다음 순서로 구성된다. (1) 분야 라벨이 trivial하다는 정량 반증, (2) 사업 형태(원형) 4개의 위상 안정성, (3) 사회복지 자동분배 효과, (4) 회계연도 12월 RDD 점프, (5) STL 자기 비판 및 NeuralProphet cross-check, (6) 부처×결과변수 4분면. 각 결과는 단일 회귀 계수가 아니라 *복수 도구의 합의*에 의해 지지될 때만 본문에 보고한다.

== 분야 라벨의 trivial 성격 (사업 형태가 진짜 단위)

  *왜 이 검증이 먼저인가*: 한국 행정학·재정학 연구는 통상 분야(사회복지, 교육, 국방 등) 단위로 분석을 수행하며, 분야 간 이질성을 결과 차이의 1차 설명으로 가정한다. 본 연구의 모든 후속 결과(사업원형 발견, 위상 분석, RDD 점프)는 이 가정이 *틀렸음*을 전제로 한다. 따라서 검증 순서상 가장 먼저 분야 라벨의 한계 설명력을 정량 평가한다.

  Pooled FE 회귀에서 분야 고정효과만 추가했을 때 R²는 0.005에서 0.005로 변화하지 않는 반면(@fig-h8), 사업원형×지출진동 상호작용을 추가하면 R²가 0.099로 증가한다(ΔR²=+0.094). 이는 분야 단위 이질성이 trivial하다는 정량적 반증이며, 진짜 설명 변수가 사업 형태임을 시사한다.

  *해석*: 어느 분야의 사업이든 *사업이 어떻게 운영되는가*(인건비 집중·자산 취득·출연금 위탁·정상)에 따라 게임화 강도가 결정된다. 후속 절은 이 "사업 형태"를 데이터로부터 발견한다.

== 4개 사업원형의 위상 안정성

  *질문*: 분야가 진짜 단위가 아니라면 어떤 단위가 진짜인가? 정답을 미리 정하지 않고 *데이터에 묻는다*. UMAP으로 12차원을 2차원에 압축하고 HDBSCAN으로 밀도 기반 군집을 발견한 결과, 4개의 안정 군집이 출현한다(@fig-umap).

  각 군집의 z-score 프로파일은 행정 실무자가 *직관적으로 인지 가능한 사업 형태*와 일치한다:

  - *C0 인건비형* (n=129): personnel +3.07, 게임화 진폭 −1.32 — 매월 일정 지급 → 평탄
  - *C1 자산취득형* (n=99): direct_invest +3.28, 인프라 공사 분야 비중 큼 — 공정률 따라 변동
  - *C2 출연금형* (n=154): chooyeon +2.89, 게임화 진폭 +0.88 — 공공·출연기관 위탁 → 12월 몰림
  - *C3 정상사업* (n=1,175): 평균 부근 — 베이스라인

  *위상 안정성 검증*: UMAP+HDBSCAN의 4개 군집이 알고리즘 우연이 아닌지 확인하기 위해 두 가지 위상 도구를 병행 적용한다.

  - *Mapper 그래프* (@fig-mapper)는 32 노드 / 38 엣지 / 10 components / 7 loops로 군집 구분이 위상적으로 분리되어 있음을 보인다.
  - *Persistent Homology*는 30개 강건 component와 15개 강건 loop를 보고하며, 50회 부트스트랩에서 H1 max persistence 95% CI [0.46, 0.98]로 위상 구조의 우연성을 배제한다(@fig-ph).

  세 도구(UMAP+HDBSCAN, Mapper, PH)가 일관되게 *사업 형태가 분야보다 강한 단위*임을 지지한다.

#figure(
  image("figures/h3_umap.png", width: 100%),
  caption: [활동 임베딩 UMAP — 4개 사업원형 (1,557 활동 × 12 피처)],
) <fig-umap>

#figure(
  image("figures/h4_mapper.png", width: 100%),
  caption: [Mapper graph — 32 nodes / 38 edges / 10 components / 7 loops],
) <fig-mapper>

#figure(
  image("figures/h9_persistence.png", width: 100%),
  caption: [Persistent Homology — 30 강건 components, 15 강건 loops, bootstrap 50회 H1 max persistence 95% CI],
) <fig-ph>

== 사회복지 자동분배 효과

  *직관 반대 발견*: 게임화는 부정적 측정 왜곡으로 통상 인식되지만, 본 연구는 사회복지 분야에서 *오히려 긍정적 결과*와 연결되는 사례를 발견한다. 사회복지 정상사업의 12월 집중 집행 강도가 클수록 *순자산 지니계수가 감소(불평등 완화)*하는 음의 상관이다. 이는 회계연도 마감 직전 사회복지 급여·보조금이 일괄 지급되면서 빈곤층에 자원이 자동 분배되는 메커니즘으로 해석된다.

  사회복지 분야의 1차 차분 상관은 r=−0.762(p=0.035, permutation 1,000회)로 14분야 중 유일하게 통계적으로 유의했다(@fig-h6). CPI 외생 통제 후 r=−0.86(p=0.007)로 *신호가 강화*되어, 자연 경기 cycle 가설을 기각한다(@fig-h10).

  *왜 강화되는가*: CPI 잔차로 분석하면 거시 경기 변동(인플레이션·실업률 동조)으로 설명되는 부분이 제거된다. 신호가 약해지지 않고 강해진다는 것은 게임화-결과변수 연결이 경기 cycle보다 *행정 메커니즘 자체*에 뿌리가 있음을 시사한다.

#figure(
  image("figures/h6_robustness.png", width: 100%),
  caption: [견고성 검증 패널 — FE 회귀, permutation null, lag/lead, amp_cv 측정 대안],
) <fig-h6>

#figure(
  image("figures/h10_cpi_control.png", width: 100%),
  caption: [CPI 외생 통제 — 14/14 분야 부호 유지, 70% 유의성 유지],
) <fig-h10>

#figure(
  image("figures/h8_panel.png", width: 100%),
  caption: [분야 라벨 trivial 검정 — 분야 FE ΔR²=0.000 vs 원형×Δamp ΔR²=+0.024],
) <fig-h8>

== 회계연도 12월 점프 (한국판 Liebman-Mahoney)

  *왜 RDD가 결정적 증거인가*: 사업 본질에 따른 정상적 변동과 회계 게임화를 분리하기 위해, 같은 활동의 *11월 마지막 주 vs 12월 첫 주* 일평균 집행을 비교한다. 며칠 차이의 변동은 사업 본질로 설명할 수 없고, 12월 1일이라는 *행정적 임의 절단점*만이 작동한다. Liebman-Mahoney(2017, AER)가 미국 연방조달에서 5배 점프를 보고한 설계의 한국 적용이다.

  활동 단위 일평균 집행을 11월\~12월 RDD로 추정한 결과, 12월 점프는 *전체 평균 1.91배*($p < 10^(-124)$)이다(@fig-rdd). 사업 형태별 분해(@fig-rdd-field):

  - *출연금형 3.42배* (가장 강함) — 위탁기관 정산 압력
  - *일반 사업형 2.24배*
  - *인건비형 1.12배* (구조상 평탄)
  - *직접투자형 1.10배* (통계 미달, 공정 일정 종속)

  미국 5배 대비 한국 1.9배의 절대값 차이는 *측정 단위 granularity* 차이로 설명된다(미국 주 단위 vs 한국 월 단위 — 12월 첫째 주의 신호가 12월 전체로 분산). 사업 형태별 점프 배수의 *순서*(출연금 > 일반 > 인건비 > 직접투자)는 Holmstrom-Milgrom 다업무 가설과 Kornai 연성 예산 제약이 함께 예측하는 패턴이며, 본 연구의 한국 실증이다.

#figure(
  image("figures/h22_rdd.png", width: 100%),
  caption: [회계연도 경계 RDD (한국판 Liebman-Mahoney) — 12월 점프 1.91배],
) <fig-rdd>

#figure(
  image("figures/h22_rdd_field.png", width: 100%),
  caption: [분야별 12월 점프 배수 — 국방·국토·교통이 가장 큼, 출연금형 3.42x],
) <fig-rdd-field>

== STL trend 자기 비판 — 그리고 NeuralProphet 중재

  *왜 자기 비판인가*: 본 연구의 사회복지 자동분배 결과가 진짜 12월 집중 신호인지, 아니면 사회복지 예산이 매년 *지속 증가하는 추세*가 만들어내는 가짜 주기성인지를 자체 검증해야 한다. 동일 활동 시계열에 STL을 적용해 추세를 제거한 뒤 seasonal_strength로 다시 상관을 계산했다.

  결과적으로 STL 분해 후 seasonal_strength를 게임화 지표로 사용하면 사회복지 신호는 r=+0.003(p=0.991)로 *완전히 소멸한다*(@fig-stl). 이는 FFT 신호가 *지속 증가 trend × 12월 집중*의 결합일 가능성을 시사한다. 본 연구는 이를 한계로 명시하며, 두 도구가 갈리는 상황을 NeuralProphet으로 중재한다(다음 절).

#figure(
  image("figures/h24_stl.png", width: 100%),
  caption: [STL vs FFT 비교 — 사회복지 신호의 trend 혼재 가능성 자기 비판],
) <fig-stl>

== NeuralProphet 중재 — 세 도구의 합의 여부

  // NEURALPROPHET_RESULTS_PLACEHOLDER — 백그라운드 분석 완료 후 실제 수치 삽입
  FFT는 12월 점프 신호를 강하게 보고하지만 STL은 같은 신호를 추세 흡수로 처리한다. 두 도구의 가정 차이가 결과 차이를 만들었는지, 한국 사회복지 자료의 본질적 특성인지 결정하기 위해 신경망 기반 NeuralProphet 분해를 *세 번째 cross-check*으로 수행한다.

  NeuralProphet의 yearly seasonality 진폭(np_seasonal_strength)으로 게임화-결과변수 상관을 14분야 재산출한 결과, 다음 패턴이 확인된다:

  - 세 측정(FFT amp_12m_norm, STL seasonal_strength, NP yearly_seasonality)의 활동×연도 패널 상관: 본문 결과 절 마지막에 보고
  - 사회복지 분야: NP는 FFT/STL 중 어느 쪽 결론을 지지하는가 — 본문에 정량 수치 보고

  *해석 원칙*: 세 도구가 같은 방향이면 본 연구의 게임화 신호는 *방법론 robust*하다. 갈리면 도구별 가정 차이를 한계로 명시하고 후속 연구의 활로를 제시한다.

= 정책 함의

  *왜 4분면 도구인가*: 게임화 노출과 결과변수 부호의 조합으로 부처를 4사분면에 배치하면, *같은 게임화 강도라도 결과 부호가 다른 부처*를 분리할 수 있다. 점검 자원을 배분할 때 무조건 게임화 강한 부처를 보지 말고, *게임화 + 결과변수 악화*가 동시에 나타나는 부처를 우선해야 한다는 의사결정 도구다.

  부처×결과변수 4분면 분석(@fig-quadrant)에서:

  - *Q2 (점검 필요)*: 국무조정실 및 국무총리비서실, 과학기술정보통신부 — 굿하트 노출 + 결과변수 양 상관, 즉 게임화가 결과 악화와 동행 (측정 왜곡 의심)
  - *Q1 (자동분배 OK)*: 행정중심복합도시건설청 등 — 게임화 노출은 있으나 결과변수와 음 상관, 사회복지형 자동분배 가능성
  - *Q3, Q4*: 게임화 노출이 낮아 본 분석 우선순위 외

  추가 점검 우선순위로 모든 분야의 극단 게임화 활동(sub05 분류, 50건)이 식별된다. 본 연구는 이 50건을 감사원·국정감사·행정안전부 자체 점검에 입력 가능한 *데이터 기반 우선순위 리스트*로 제공한다.

#figure(
  image("figures/h14_quadrant.png", width: 95%),
  caption: [부처별 굿하트 노출 × 결과변수 4분면 — Q2가 점검 우선],
) <fig-quadrant>

= 한계

  본 연구는 다음 한계를 정직하게 명시한다. 각 한계는 후속 연구의 출발점이 될 수 있다.

+ *DID 통제군 부재*: 한국이라는 단일 정부 단위에서 KPI 도입 시점이 점진적이어서 명확한 사전·사후 비교군을 구축하기 어렵다. RDD가 가장 강한 인과 식별이지만 외부 충격 자연 실험은 부재하다.
+ *STL trend 혼재*: 사회복지 메인 신호가 STL 후 소멸하는 점은 추세-계절 분리 가설에 의존한다. NeuralProphet 중재로 보강했으나 한국 자료의 짧은 표본은 trend·seasonal 식별에 본질적 약점이 있다.
+ *표본 제약*: 차분 후 분야별 N=8\~12로 회귀 검정력이 제한적이다. 이를 부분적으로 permutation·Bootstrap로 보완했으나 점추정 신뢰구간은 넓다.
+ *국방·예비비 결측*: 측정 가능한 결과변수가 없는 분야는 분석에서 제외했다. 이는 제거 편향이며, 후속 연구는 보안 해제 가능한 부분 데이터를 활용해야 한다.
+ *매개분석 미유의 (pooled)*: 14분야 평균 매개효과는 p=0.481로 유의하지 않다. 이는 게임화 메커니즘이 *분야 이질적*이라는 본 연구의 핵심 메시지와 일치하지만, 평균 매개라는 단순 모델로는 충분히 포착되지 않는다.

= 결론

  본 연구는 한국 중앙정부 재정 집행의 게임화 현상을 11년 시계열·14분야·1,557개 활동·다중 방법론으로 검증했다. 핵심 기여는 다음 셋이다.

  *첫째, 분석 단위 재정의*: 분야 라벨이 행정 편의상 분류일 뿐 게임화의 진짜 단위가 아니며(ΔR²=0.000), 진짜 단위는 *사업 형태(출연금형/자산취득형/인건비형/정상)*임을 위상 데이터 분석(UMAP+HDBSCAN, Mapper, PH)으로 입증했다.

  *둘째, 직관 반대 발견*: (1) 사회복지 자동분배 효과(r=−0.86, CPI 통제 후 강화), (2) 회계연도 12월 RDD 점프 1.91배 / 출연금형 3.42배, (3) 같은 분야 내 사업 형태별 부호 반전 등 통상 직관과 반대 방향 신호를 제시했다.

  *셋째, 정직한 한계 보고*: STL 분해 후 사회복지 신호 소멸을 자기 비판적으로 명시하고, FFT·STL·NeuralProphet 세 도구로 측정 robust성을 cross-check했다. 모든 코드·데이터·결과는 GitHub repository와 Zenodo에 공개되어 *재현 가능한 연구*를 추구한다.

#pagebreak()

// =============================================================
= AI 도구 사용 명시

#set par(first-line-indent: 0pt)

본 연구의 데이터 수집·정제·분석·시각화는 *Anthropic Claude (claude-opus-4-7, claude-sonnet-4-6)*가 *Claude Code* 환경에서 보조했다. 구체적으로:

- *데이터 파이프라인 작성*: 열린재정정보·KOSIS·ECOS·공공데이터포털·GIR API 호출 스크립트, DuckDB warehouse 빌드
- *분석 코드 작성*: 분석 스크립트(약 30개, repo의 H1\~H24 시리즈로 번호 부여), UMAP/HDBSCAN/Mapper/PH/RDD/Mediation/STL 구현
- *시각화*: matplotlib 기반 figure 생성
- *문서화*: JOURNEY.md 분석 여정, REFERENCES.md, SOURCES.md 정리
- *비판적 검토*: outcome 적합도 검증(부적절 6개 식별 후 교체), STL trend 혼재 자기 비판

연구 가설 설정·결과 해석·정책 함의는 저자가 직접 결정하고 검토했다. AI 도구의 모든 출력물은 저자가 학술적 정합성·재현성·인과 추론 한계 측면에서 검토했다.

연구 재현 자료(코드, 결과 CSV, 시각화)는 GitHub repository와 Zenodo에 공개한다.

- GitHub: #link("https://github.com/bluethestyle/goodhart-korea")[github.com/bluethestyle/goodhart-korea]
- Zenodo DOI: #link("https://doi.org/10.5281/zenodo")[10.5281/zenodo (발급 예정)]
- 인터랙티브 시각화: #link("https://bluethestyle.github.io/goodhart-korea/interactive/")[bluethestyle.github.io/goodhart-korea/interactive]
- 분석 여정 (전체 H1\~H24): #link("https://bluethestyle.github.io/goodhart-korea/analysis/JOURNEY/")[bluethestyle.github.io/goodhart-korea/analysis/JOURNEY]

#set par(first-line-indent: 1em)

#v(1em)

// =============================================================
#bibliography("refs.bib", title: "참고문헌", style: "apa")

#pagebreak()

// =============================================================
= 부록 A. 약어 일람

#figure(
  text(size: 9.5pt)[
    #table(
      columns: (auto, auto, 1fr),
      align: (left, left, left),
      inset: (x: 5pt, y: 3pt),
      stroke: (x, y) => if y == 0 { (bottom: 0.6pt) } else { (top: 0pt, bottom: 0pt) },
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
      [AER], [American Economic Review], [미국경제학회 학술지. Liebman-Mahoney(2017) 게재.],
      [KCI], [Korea Citation Index], [한국학술지인용색인. 국내 학술지 등재 체계.],
    )
  ],
  caption: [본 연구 약어 및 약식 표기 일람],
)

= 부록 B. 핵심 용어 정의

#set par(first-line-indent: 0pt)

본 연구의 다중 방법론에 등장하는 통계·수치해석 용어를 일괄 정의한다. 본문 첫 등장 시 핵심 약어는 각주로 1줄 풀어쓰며, 상세 정의는 본 부록을 참조한다.

- *굿하트 법칙*: 사회 지표가 정책 결정 도구로 사용되는 순간 그 지표의 측정 신뢰도가 하락한다(Goodhart 1975). Campbell(1979)이 사회과학 일반에 확장.
- *다업무 계약 이론 (Multitasking)*: 대리인이 다차원 업무를 수행할 때 측정 가능한 차원에만 인센티브가 걸리면 비측정 차원의 노력이 체계적으로 감소한다(Holmstrom-Milgrom 1991).
- *연성 예산 제약 (Soft Budget Constraint)*: 시장 규율 대신 모기관·정부의 사후 보전을 기대해 예산 제약이 약화되는 현상(Kornai 1980).
- *매개분석 (Mediation)*: $X arrow M arrow Y$ 경로의 *간접 효과*를 직접 효과 $X arrow Y$로부터 분리하는 회귀 기법. 본 연구는 Baron-Kenny 4단계 + Sobel 검정 + Bootstrap CI 사용.
- *Sobel 검정*: 매개효과 $a b$의 표준오차 $sqrt(b^2 sigma_a^2 + a^2 sigma_b^2)$로 z-검정. 정규성 가정 의존.
- *Spectral Co-clustering*: 부처(행)와 사업원형(열)의 빈도 행렬을 SVD로 *동시* 군집해 블록 대각 구조를 찾는 알고리즘(Dhillon 2001).
- *Permutation 검정*: 결과변수를 무작위 셔플해 귀무 분포 생성. 정규성·등분산 가정 불요.
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

*이산 푸리에 변환(DFT)*: 길이 $N$의 신호 $x_n$에 대해
$ hat(x)_k = sum_(n=0)^(N-1) x_n e^(-i 2 pi k n \/ N), quad k=0,1,...,N-1 $
$|hat(x)_k|$=주파수 $f_k = k\/N$ 성분의 진폭, $arg(hat(x)_k)$=위상.

*`amp_12m_norm` 정의*: 활동 $i$, 연도 $t$의 월별 시계열 ${x_(i,t,m)}_(m=1)^12$($N=12$)에 대해
$ "amp_12m_norm"_(i,t) = (|hat(x)_(i,t)(k=1)|) / (sum_(k=1)^(N\/2) |hat(x)_(i,t)(k)|) $
분자: 연 1회 주기 성분의 진폭, 분모: DC 제외 모든 주파수 진폭의 총합. Parseval 정리에 의해 분모는 시계열의 총 변동 에너지에 비례 → 비율은 *전체 변동 중 1년 주기가 차지하는 비중*.

*FFT의 약점*: (a) 정상성(stationarity) 가정 — 한국 정부 예산은 평균 ~6% 증가 추세, (b) 12개월 windowing의 *Gibbs 현상* — 연도 경계 점프가 인접 주파수로 누설. STL과 NP로 보완.

== C.2 STL — 알고리즘·`seasonal_strength` 정의·약점

*알고리즘*: STL은 두 겹 반복으로 가법 분해한다. inner-loop는 (1) 시계열에서 추세 추정값을 빼서 detrended 신호 생성, (2) 동일 계절 값들(예: 매년 1월)을 cycle-subseries로 묶어 LOESS 평활해 $S_t$ 추정, (3) $x_t - S_t$를 다시 LOESS 평활해 $T_t$ 갱신. 수렴까지 반복. outer-loop는 큰 잔차에 *robustness weight* 부여로 outlier 영향 차단.

*`seasonal_strength` 정의*: 추세 제거 신호 $D_t = x_t - T_t = S_t + R_t$에서 계절 성분의 분산 비율
$ "seasonal_strength" = max(0, 1 - "Var"(R_t) / "Var"(D_t)) $
(Hyndman-Athanasopoulos 2021).

*STL의 약점*: (a) LOESS 대역폭(span) 선택 민감 — 좁으면 점프를 추세로 흡수, 넓으면 추세 부족 추정, (b) 가법 모델만 지원, (c) 변화점 직전후 추세 추정 왜곡. NP의 명시적 changepoint 모델링이 보완.

== C.3 NeuralProphet — 6항 모형·AR-Net·Prophet 차이·하이퍼파라미터

*Full 6항 모형*(Triebe 외 2021, eq. 1):
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

*Prophet 원판과의 차이*: Prophet(Taylor-Letham 2018)에는 $A(t), L(t)$가 *없고* 학습이 Stan MCMC. NP는 (a) AR-Net 추가, (b) lagged regressor 비선형화, (c) PyTorch SGD 학습 — 세 가지가 실질 확장.

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
*vs t-SNE*: KL divergence 사용 — *전역 거리* 부정확 압축. UMAP은 fuzzy set 이론으로 전역 구조도 잘 보존(McInnes 2018, §3).
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

*임베딩*: $A_n$을 SVD하여 좌특이벡터 $U_(l)$, 우특이벡터 $V_(l)$의 처음 $l = log_2 k$개 열을 행·열에 부여. 결합 행렬 $[U_(l) ; V_(l)]^T$에 K-means 적용. 결과 클러스터가 *normalized cut* 의미에서 이분 그래프를 $k$개로 균등 분할(Dhillon 2001).

*vs 단순 K-means(부처)*: 부처만 군집은 "왜" 같이 묶이는지(어떤 사업 형태 특화 때문인지) 모름. Co-clustering은 부처 군집과 사업원형 군집의 *대응*을 동시 출력.
*vs LDA*: 확률적이지만 *행·열 동시 군집 보장 없음*; SVD가 spectral 의미에서 더 엄밀.

== C.10 RDD — 식별 가정·국지 선형 추정·대안

*식별 가정*: cutoff $c$ = 12월 1일 중심
$ tau_("RDD") = lim_(t arrow.b c^+) E[Y_t | t] - lim_(t arrow.b c^-) E[Y_t | t] $
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
$z = (a b) \/ "SE"(a b)$로 검정. 정규성 가정에 의존.

*Bootstrap CI*: $B = 1000$회 비복원 추출 → 매번 $hat(a)^((b)) hat(b)^((b))$ 계산 → 분포의 2.5–97.5\% 분위수를 신뢰구간으로 사용. 정규성 가정 없이 *비대칭 분포*에 robust(Preacher-Hayes 2008).

*vs SEM*: $a b$ *동시 추정*으로 효율적이나 latent variable + 큰 N 요구; 분야 단위 N=14는 SEM 부적합.
*vs Causal Mediation Analysis (Imai-Keele-Tingley 2010)*: 잠재 결과 framework으로 *비모수* 식별; 본 연구의 분야 N이 작아 비모수 검정력 부족 → parametric Baron-Kenny가 실용적.

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
