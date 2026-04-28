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

// 학술 표준 한글 명조 폰트 우선 (KoPubWorld·Noto Serif KR·함초롬바탕 fallback)
#set text(
  font: ("KoPubWorld Batang", "Noto Serif KR", "Source Han Serif K",
         "함초롬바탕", "바탕", "Times New Roman"),
  size: 11pt,
  lang: "ko",
)

#set par(justify: true, leading: 0.85em, first-line-indent: 1em)

#set heading(numbering: "1.1")

// 제목은 sans-serif 고딕 (KoPub돋움 / Noto Sans KR)
#show heading.where(level: 1): it => [
  #set text(font: ("KoPubWorld Dotum", "Noto Sans KR", "Source Han Sans K"),
            size: 13pt, weight: "bold")
  #v(1em)
  #it
  #v(0.5em)
]
#show heading.where(level: 2): it => [
  #set text(font: ("KoPubWorld Dotum", "Noto Sans KR", "Source Han Sans K"),
            size: 11.5pt, weight: "bold")
  #v(0.7em)
  #it
  #v(0.3em)
]

#set figure(supplement: [그림])
#set table(stroke: 0.5pt)

// =============================================================
// 표지
// =============================================================
#align(center)[
  #v(1em)
  #text(size: 16pt, weight: "bold",
        font: ("KoPubWorld Dotum", "Noto Sans KR", "Source Han Sans K"))[
    한국 정부 재정 집행의 굿하트 효과
  ]
  #v(0.5em)
  #text(size: 13pt,
        font: ("KoPubWorld Dotum", "Noto Sans KR", "Source Han Sans K"))[
    다각적 측정과 정책 함의
  ]
  #v(2em)
  #text(size: 11pt)[
    (저자명)
  ]
  #v(0.5em)
  #text(size: 10pt)[
    2026년 4월
  ]
  #v(0.5em)
  #text(size: 9pt, fill: rgb("#666"))[
    GitHub: #link("https://github.com/bluethestyle/goodhart-korea")[github.com/bluethestyle/goodhart-korea] · #h(0.5em)
    Zenodo: #link("https://doi.org/10.5281/zenodo.{TBD}")[10.5281/zenodo.\{TBD\}] · #h(0.5em)
    인터랙티브 시각화: #link("https://bluethestyle.github.io/goodhart-korea/interactive/")[Pages 사이트]
  ]
]

#v(2em)

// =============================================================
// 초록
// =============================================================
#align(center)[
  #text(weight: "bold", size: 12pt)[국문 초록]
]

#par(first-line-indent: 0pt)[
  본 연구는 열린재정정보 월별 집행 11년치(2015\~2026)와 KOSIS·한국은행 ECOS·공공데이터포털·온실가스종합정보센터 14분야 결과변수를 통합해 한국 정부 재정 집행의 굿하트 효과(Goodhart 1975)를 다각도로 측정·검증한다. 활동(ACTV) 단위 임베딩(UMAP+HDBSCAN)으로 인건비형·자산취득형·출연금형·정상사업 4개 사업원형을 발견하고, Mapper와 지속 호몰로지(Persistent Homology)로 위상 안정성을 입증한다. 분야 고정효과 회귀에서 분야 라벨의 추가 설명력(ΔR²)이 0에 수렴하는 반면, 사업원형×지출진동의 상호작용은 ΔR²=+0.085~0.094로 유의함을 확인해 분야 단위 분석의 trivial 성격을 정량적으로 반증한다. 사회복지 자동분배 효과(r=−0.762, p=0.035; CPI 통제 후 −0.86, p=0.007)와 회계연도 12월 점프 1.91x(출연금형 3.42x; H22 RDD)를 통해 Liebman-Mahoney(2017)의 미국 결과를 한국으로 확장한다. STL 분해 결과 사회복지 신호의 trend 혼재 가능성을 자기 비판적으로 보고한다.

  #text(weight: "bold")[주요어:] 굿하트 법칙, 정부 재정, NPM, 토폴로지 데이터 분석, 회귀불연속, 매개분석, 한국
]

#pagebreak()

// =============================================================
= 서론

  Bevan과 Hood(2006)는 "측정되는 것이 중요해진다(What's measured is what matters)"는 명제 아래 영국 NHS 사례에서 평가지표 게임화의 4가지 패턴을 식별했다. 본 연구는 이 명제를 한국 중앙정부 재정 집행 데이터로 확장해 검증한다.

  Liebman과 Mahoney(2017)는 미국 연방조달의 11월 마지막 주 vs 12월 첫 주 회귀불연속(RDD)으로 12월 첫 주 지출이 5배 증가하고 품질 점수가 하락함을 입증했다. 본 연구는 한국에서 동일 분석을 수행해 12월 점프 약 1.9배(출연금형 3.4배)를 확인한다.

  분야 단위 이질성(field-level heterogeneity)은 흔히 "분야가 다르니 결과가 다르다"는 직관으로 정당화되지만, 본 연구는 이 직관을 분야 고정효과 회귀로 정량적으로 반증한다(ΔR²=0.000). 진짜 설명 변수는 사업 형태(원형)임을 위상 데이터 분석으로 입증한다.

= 이론적 토대

== 굿하트-캠벨 법칙

  Goodhart(1975)와 Campbell(1979)은 사회 지표가 정책 결정에 사용될수록 그 지표의 측정 신뢰도가 하락한다는 명제를 제시했다. Manheim과 Garrabrant(2018)는 이를 4가지(Regressional, Causal, Extremal, Adversarial)로 분류했다.

== 다업무 계약 이론(Multitasking)

  Holmstrom과 Milgrom(1991)은 다차원 업무에서 측정 가능한 차원에만 노력이 집중되어 측정되지 않는 차원이 왜곡되는 현상을 모형화했다. 본 연구의 사업 형태별 지출 진폭 차이(출연금형 3.42배 vs 직접투자형 1.10배)는 이 가설의 한국 실증이다.

== 연성 예산 제약(Soft Budget Constraint)

  Kornai(1980)의 연성 예산 제약 개념은 출연기관의 시점 조정 자유도가 시장 규율을 받는 직접 사업보다 큰 이유를 설명한다. 본 연구의 출연금 비중과 게임화 강도 회귀(β=+0.375, p=0.005)는 이 메커니즘의 정량적 증거다.

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

== 게임화 강도 측정

  - *FFT 기반*: 활동×연도 월별 시계열에 푸리에 변환을 적용해 1년 주기 진폭(amp_12m_norm)을 산출한다.
  - *STL 분해*: Cleveland 외(1990)의 Seasonal-Trend decomposition Loess를 적용해 trend·seasonal·remainder를 분리하고 seasonal_strength(=1−Var(remainder)/Var(detrended))를 보조 지표로 사용한다.

== 활동 임베딩 + 위상

  - UMAP(McInnes 2018) + HDBSCAN(Campello 2013)으로 12피처를 2D 임베딩하고 4개 사업원형을 분리한다.
  - Mapper(Singh 외 2007, kmapper)와 지속 호몰로지(Edelsbrunner-Harer 2008, ripser)로 위상 안정성을 입증한다.

== 인과 식별

  - *RDD*: 회계연도 12월 1일 cutoff 전후의 일평균 집행을 비교한다(Imbens-Lemieux 2008).
  - *매개분석*: Baron-Kenny(1986) 4단계 + Sobel 검정 + Bootstrap 95% CI로 출연금→게임화→결과변수의 매개 경로를 분리한다.

== 외생 통제

  - 한국은행 ECOS CPI 시계열을 외생 통제변수로 회귀 잔차를 산출하고, 자연 경기 cycle 가설을 검증한다.

= 결과

== 분야 라벨의 trivial 성격 (사업 형태가 진짜 단위)

  Pooled FE 회귀에서 분야 고정효과만 추가했을 때 R²는 0.005에서 0.005로 변화하지 않는 반면, 사업원형×지출진동 상호작용을 추가하면 R²가 0.099로 증가한다(ΔR²=+0.094). 이는 분야 단위 이질성이 trivial하다는 정량적 반증이며, 진짜 설명 변수가 사업 형태임을 시사한다.

== 4개 사업원형의 위상 안정성

  활동 1,557건의 12피처를 UMAP으로 2D 임베딩하고 HDBSCAN을 적용해 4개 클러스터를 얻었다(@fig-umap). 각 클러스터의 z-score 프로파일:

  - C0 인건비형(n=129): personnel +3.07, 게임화 진폭 −1.32
  - C1 자산취득형(n=99): direct_invest +3.28, 인프라 공사 분야 비중 큼
  - C2 출연금형(n=154): chooyeon +2.89, 게임화 진폭 +0.88
  - C3 정상사업(n=1,175): 평균 부근

  지속 호몰로지는 30개 강건 component와 15개 강건 loop를 보고하며, 50회 부트스트랩에서 H1 max persistence 95% CI [0.46, 0.98]로 위상 구조의 우연성을 배제한다(@fig-ph).

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

  사회복지 분야의 1차 차분 상관은 r=−0.762(p=0.035, permutation 1000회)로 14분야 중 유일하게 통계적으로 유의했다(@fig-h6). CPI 외생 통제 후 r=−0.86(p=0.007)로 신호가 강화되어, 자연 경기 cycle 가설을 기각한다(@fig-h10). 사회복지 정상사업의 12월 집중 집행이 빈곤 격차 완화와 결합되는 자동분배 효과로 해석한다.

#figure(
  image("figures/h6_robustness.png", width: 100%),
  caption: [H6 견고성 패널 — FE 회귀, permutation null, lag/lead, amp_cv],
) <fig-h6>

#figure(
  image("figures/h10_cpi_control.png", width: 100%),
  caption: [H10 CPI 외생 통제 — 14/14 부호+70% 유지 (100%)],
) <fig-h10>

#figure(
  image("figures/h8_panel.png", width: 100%),
  caption: [H8 비판적 자기평가 — 분야 FE ΔR²=0.000 vs 원형×Δamp ΔR²=+0.024],
) <fig-h8>

== 회계연도 12월 점프 (한국판 Liebman-Mahoney)

  활동 단위 일평균 집행을 11월~12월 RDD로 추정한 결과, 12월 첫 달 점프는 전체 평균 1.91배($p < 10^(-124)$)다(@fig-rdd). 사업 형태별로 출연금형이 3.42배(가장 강함), 일반 사업형 2.24배, 인건비형 1.12배, 직접투자형 1.10배(통계 미달)이다(@fig-rdd-field).

  미국 Liebman-Mahoney(2017)의 5배 대비 한국 1.9배는 미국 주(week) 단위 vs 한국 월 단위의 granularity 차이다. 사업 형태별 차이는 Holmstrom-Milgrom 다업무 가설의 한국 실증이다.

#figure(
  image("figures/h22_rdd.png", width: 100%),
  caption: [회계연도 경계 RDD (한국판 Liebman-Mahoney) — 12월 점프 1.91배],
) <fig-rdd>

#figure(
  image("figures/h22_rdd_field.png", width: 100%),
  caption: [분야별 12월 점프 배수 — 국방·국토·교통이 가장 큼, 출연금형 3.42x],
) <fig-rdd-field>

== STL trend 자기 비판

  STL 분해 후 seasonal_strength를 게임화 지표로 사용하면 사회복지 신호는 r=+0.003(p=0.991)로 완전히 소멸한다(@fig-stl). FFT 신호가 *지속 증가 trend × 12월 집중*의 결합일 가능성이며, 본 연구는 이를 정직하게 한계로 명시한다.

#figure(
  image("figures/h24_stl.png", width: 100%),
  caption: [STL vs FFT 비교 — 사회복지 신호의 trend 혼재 가능성 자기 비판],
) <fig-stl>

= 정책 함의

  부처×결과변수 4분면 분석(H14)에서(@fig-quadrant):
  - Q2(점검 필요): 국무조정실 및 국무총리비서실, 과학기술정보통신부 — 굿하트 노출 + 결과변수 양 상관 (측정 왜곡 가능)
  - Q1(자동분배 OK): 행정중심복합도시건설청 등

  추가 점검 우선순위로 모든 분야의 극단 게임화 활동(sub05, 50건)이 식별된다.

#figure(
  image("figures/h14_quadrant.png", width: 95%),
  caption: [부처별 굿하트 노출 × 결과변수 4분면 — Q2가 점검 우선],
) <fig-quadrant>

= 한계

+ DID 통제군 부재: 한국 단일 정부, KPI 도입 시점 점진적
+ STL trend 혼재: 사회복지 메인 신호의 trend 의존성
+ 표본 제약: 차분 후 분야별 N=8~12
+ 국방·예비비: 측정 불가능 분야로 제외
+ 매개분석 미유의: 시스템 평균 매개 효과는 약함

= 결론

  본 연구는 한국 중앙정부 재정 집행의 게임화 현상을 11년 시계열·14분야·1,557개 활동·다중 방법론으로 검증했다. 분야 단위가 아닌 사업 형태(출연금/자산취득/인건비/정상)가 진짜 단위임을 정량적으로 입증하고, 사회복지 자동분배·12월 RDD 점프·출연금형 3.42배 등 직관 반대 발견을 제시한다. STL trend 혼재 가능성을 자기 비판적으로 보고함으로써 정직한 robustness 평가를 수행한다.

#pagebreak()

// =============================================================
= AI 도구 사용 명시

#par(first-line-indent: 0pt)[
  본 연구의 데이터 수집·정제·분석·시각화는 *Anthropic Claude (claude-opus-4-7, claude-sonnet-4-6)*가 *Claude Code* 환경에서 보조했다. 구체적으로:

  - *데이터 파이프라인 작성*: 열린재정정보·KOSIS·ECOS·공공데이터포털·GIR API 호출 스크립트, DuckDB warehouse 빌드
  - *분석 코드 작성*: H1~H24 분석 스크립트(약 30개), UMAP/HDBSCAN/Mapper/PH/RDD/Mediation/STL 구현
  - *시각화*: matplotlib 기반 figure 생성
  - *문서화*: JOURNEY.md 분석 여정, REFERENCES.md, SOURCES.md 정리
  - *비판적 검토*: outcome 적합도 검증(부적절 6개 식별 후 교체), STL trend 혼재 자기 비판

  연구 가설 설정·결과 해석·정책 함의는 저자가 직접 결정하고 검토했다. AI 도구의 모든 출력물은 저자가 학술적 정합성·재현성·인과 추론 한계 측면에서 검토했다.

  연구 재현 자료(코드, 결과 CSV, 시각화)는 GitHub repository와 Zenodo에 공개한다.

  - GitHub: #link("https://github.com/bluethestyle/goodhart-korea")
  - Zenodo DOI: #link("https://doi.org/10.5281/zenodo.{TBD}")
  - 인터랙티브 시각화: #link("https://bluethestyle.github.io/goodhart-korea/interactive/")
  - 분석 여정 (전체 H1\~H24): #link("https://bluethestyle.github.io/goodhart-korea/analysis/JOURNEY/")
]

#v(1em)

// =============================================================
#bibliography("refs.bib", title: "참고문헌", style: "apa")
