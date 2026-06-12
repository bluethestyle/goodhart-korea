검수 결과: **최신 `conference_v1(2).typ`에는 delta 패치가 아직 대부분 미반영**되어 있다.
상태는 **완료 0 / 부분 반영 1 / 미반영 6**으로 보면 된다.

| 항목                   | 현재 상태 | 판단          |
| -------------------- | ----: | ----------- |
| 서론 첫 문장 패러독스-forward |   미반영 | 교체 필요       |
| H2 가설 문장 이질성 검정화     |   미반영 | 교체 필요       |
| H2 헤딩 라벨 완화          |   미반영 | 교체 필요       |
| RDD 표 캡션 라벨 완화       |   미반영 | 교체 필요       |
| 방법론 위계 선언            | 부분 반영 | 1문장 수정 권장   |
| 국문초록 softening       |   미반영 | 교체 권장       |
| 영문초록 강도 조절           |   미반영 | 문장 일부 교체 권장 |

아래는 **정확한 교체 문구**만 정리한 패치안이다.

---

## 1. 서론 첫 문장 — 미반영

현재:

```typst
한국 중앙정부의 연말 집행 집중은 오래 관찰되어 온 현상이다. 본 연구는 이를 측정 지표에 대한 대리인의 전략적 반응이라는 시각에서 다시 본다.
```

교체:

```typst
집행률은 중앙정부 예산관리에서 가장 널리 관리되는 지표지만, 바로 그 측정 가능성 때문에 사업 수행자의 집행 시점 선택을 왜곡할 수 있다. 본 연구는 한국 중앙정부의 연말 집행 집중을 이 측정 지표에 대한 대리인의 전략적 반응이라는 시각에서 다시 본다.
```

---

## 2. H2 가설 문장 — 미반영

현재:

```typst
*H2.* 자산취득형은 12월 1일 직후 비용이 급감해 RDD 점프가 가장 크다.
```

교체:

```typst
*H2.* 회계연도 경계 전후 집행 점프의 크기는 사업원형에 따라 다르며, 자산취득형에서 가장 크다.
```

바로 아래 H2 캐비엇도 같이 교체하는 게 좋다.

현재:

```typst
다만 H2는 RDD에서 관찰된 점프 패턴을 모형 입력으로 받아들인 것이므로, 순수한 사전 예측이라기보다 원형 간 비교(자산취득 3.42배 대 출연금 1.10배 대 인건비 1.12배)에서 검증력을 갖는다.
```

교체:

```typst
다만 H2는 자산취득형의 절대 점프 크기를 순수하게 사전 예측한다기보다, 회계연도 경계 전후 점프가 원형별로 다르게 나타난다는 이질성 검정으로 읽어야 한다. 따라서 검증력은 자산취득형 3.42배 자체보다 자산취득 3.42배 대 출연금 1.10배 대 인건비 1.12배의 원형 간 대비에 있다.
```

---

## 3. H2 헤딩 — 미반영

현재:

```typst
== H2: 자산취득형 회계연도 12월 RDD 점프
```

교체:

```typst
== H2: 사업원형별 회계연도 경계 전후 일평균 집행 배율
```

---

## 4. RDD 표 캡션 — 미반영

현재:

```typst
caption: [사업원형 × 분기말 마감(cutoff) RDD 점프 배율($e^beta$)],
```

교체:

```typst
caption: [사업원형 × 분기말·회계연도 경계 전후 일평균 집행 배율($e^beta$)],
```

같은 라벨 정합성 차원에서 아래 본문 표현도 같이 낮추는 것을 추천한다.

현재:

```typst
자산취득형의 RDD 점프(3.42배)는 비용 함수가 12월 직전 낮은 한계비용을 갖는다는 데이터 패턴이며, 모형은 이를 입력으로 수용했으므로 진정한 모형 검증은 원형 간 비교(자산취득 3.42배 대 출연금 1.10배 대 인건비 1.12배)에 있다.
```

교체:

```typst
자산취득형의 회계연도 경계 전후 집행 배율(3.42배)은 비용 함수가 12월 직전 낮은 한계비용을 갖는다는 데이터 패턴이며, 모형은 이를 입력으로 수용했으므로 진정한 모형 검증은 원형 간 비교(자산취득 3.42배 대 출연금 1.10배 대 인건비 1.12배)에 있다.
```

현재:

```typst
출연금형은 RDD 점프는 약하나 연 사이클에서 우세하다.
```

교체:

```typst
출연금형은 경계 전후 집행 배율은 약하나 연 사이클에서 우세하다.
```

---

## 5. 방법론 위계 선언 — 부분 반영

현재 방법론 첫 문단에 위계 선언이 일부 있다.

```typst
핵심 식별 도구는 RDD·매개분석·CPI 통제이고, 사이클 측정 도구는 FFT·STL·NeuralProphet·웨이블릿이다.
```

다만 이 문장은 우리가 정한 위계와 약간 다르다. 핵심은 “RDD·매개분석·CPI”가 아니라 **월별 집행 패널 × 사업원형 × 회계연도 경계 전후 배율**이다.

교체:

```typst
이 중 본문 핵심 식별은 월별 집행 패널, 편성목 기반 사업원형, 회계연도 경계 전후 일평균 집행 배율의 결합에 있고, FFT·웨이블릿은 사이클 강도와 시간 동학의 1차 측정, STL·NeuralProphet·위상 분석은 추세 혼재·구조 안정성·강건성을 점검하는 보조 장치로 사용한다.
```

이 한 문장만 바꾸면 된다. 대규모 방법론 재배치는 필요 없다.

---

## 6. 국문초록 softening — 미반영

현재:

```typst
이 측정성 격차 아래 합리적 대리인일수록 노력을 집행 시점 조정으로 돌린다.
```

교체:

```typst
이 측정성 격차는 모형상 합리적 대리인이 사업 품질 노력보다 집행 시점 조정 노력에 더 큰 유인을 갖게 한다.
```

이 교체 후에도 국문초록은 약 391자 수준이라 400자 제한 안에 들어간다.

---

## 7. 영문초록 강도 조절 — 미반영

현재 영문초록은 본문 캐비엇보다 조금 강하다. 전체를 새로 쓸 필요는 없고, 아래 조각만 교체하면 된다.

### 7-1. `biases` 문장 완화

현재:

```typst
A measurability gap—execution rates are perfectly measured while program quality is not—biases a rational agent’s resources toward timing-adjustment effort, which we formalize through a multitasking-contract framework.
```

교체:

```typst
A measurability gap—execution rates are highly structured and frequently measured while program quality is harder to observe—creates stronger incentives for a rational agent to allocate effort toward timing adjustment, which we formalize through a multitasking-contract framework.
```

### 7-2. `establishing` 완화

현재:

```typst
establishing the archetype—not the field—as the unit of variance.
```

교체:

```typst
identifying the archetype, rather than the field, as the main unit of variation.
```

### 7-3. `regression discontinuity` 라벨 완화

현재:

```typst
In a fiscal-year-end regression discontinuity, asset-acquisition programs exhibit a strong December jump (3.42×) relative to the overall mean (1.91×),
```

교체:

```typst
In a fiscal-year-end discontinuity comparison, asset-acquisition programs exhibit a strong December jump (3.42×) relative to the overall mean (1.91×),
```

### 7-4. `non-reversing` 완화

현재:

```typst
continuous wavelet analysis shows that grant-type gaming intensified in a ratchet-like, non-reversing pattern over the sample period.
```

교체:

```typst
continuous wavelet analysis shows that grant-type gaming intensified in a ratchet-like level shift that does not revert to its pre-COVID level within the sample period.
```

### 7-5. `policy prescription` 완화

현재:

```typst
The policy prescription is not newly invented: the contribution is to pinpoint, with data, the model’s three comparative-static levers and their empirical targets.
```

교체:

```typst
The policy implication is not to propose entirely new instruments, but to pinpoint, with data, the model’s three comparative-static levers and their empirical targets.
```

---

## 최종 적용 우선순위

바로 적용할 것은 이 6개다.

1. 서론 첫 문장 교체
2. H2 가설 문장 교체
3. H2 캐비엇 문장 교체
4. H2 헤딩·표 캡션 라벨 완화
5. 방법론 위계 선언 1문장 교체
6. 국문초록·영문초록 softening

이 정도면 0단계 delta 패치는 충분하다.
제목, 구조, TDA·웨이블릿 위치, 정책권고 본체는 건드릴 필요 없다.
