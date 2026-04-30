# 한계 (정직한 명시)

---

## 1. 인과 식별 약점

- **DID 통제군 부재**: 한국 단일 정부 → 정책 효과 비교군 없음
- **자연 실험 부재**: KPI 도입 시점 점진적 (2007~), 명확한 cutoff 없음
- **RDD 한계**: 회계연도 12월 1일 cutoff는 *시간 차원*만 식별, 정책 처치 cutoff 아님
- **McCrary 검정 미수행**: 공식 McCrary (2008) 밀도 검정 미수행. 서술적 정당화로 대체
  (행정적 외생성·활동 단위 조작 불가성·자기보고 편향 부재). 후속 연구에서 일·주 단위
  데이터 확보 시 추가 가능 (paper §C.10.1).

→ **Triangulation 전략**으로 보강:
   - CPI 통제 / STL trend / permutation / bootstrap / RDD / mediation 상호 보완.
   - 도구 간 발산(H5 FFT vs STL 사회복지)도 자기 비판의 출발점으로 기록.

---

## 2. STL trend 혼재 ★ 핵심 자기 비판

H24 STL 분석 결과:
- 사회복지 FFT `r=−0.762, p=0.037` → STL `r=+0.003, p=0.991`
- 신호 완전 소멸 + 부호 반전

**해석**: 사회복지 신호는 *trend (복지 확대 추세) × seasonal (12월 집중)* 결합 가능성.

→ FFT와 STL 둘 다 보고. *어떤 metric이 진짜 게임화인가*는 추가 연구 필요. NeuralProphet (H26) 역시 비선형 분해이지만 trend/seasonal 분리는 ad-hoc 정의에 의존하므로 동일한 한계 공유.

---

## 3. 표본 제약

- outcome 시계열 분야별 5~35년 다양
- 차분 후 N=8~12 (분야)
- Sobel test pooled N=70 (Mediation 미유의 p=0.481)
- Permutation null이 [-0.5, +0.5]에 퍼져 검정력 한계

---

## 4. 분야 매핑 한계

- **국방**: 안보 outcome 비공개, 영업이익률은 출연금 목적 충돌
- **예비비**: 분야 아닌 예산 항목
- **자동차등록**: outcome 부적합 (노출 변수)
- **현재**: 14/15 (예비비 제외 100%) 매핑

---

## 5. Mediation 매개 효과 — 분야 이질성 ★ 정정

- **Pooled FE**: ab=0.018β, p=0.481 → *귀무가설 기각 실패*. 이는 "이질성의 증거"가
  아니라 시스템 평균 매개 효과의 통계 미달.
- **농림수산 단독**: Sobel z=−2.897, p=0.004 (음의 매개, 통계 유의)
- **사회복지**: 매개비율 57%이나 통계 미달 (§5 참조, Bonferroni 보정 후 더욱 약화)
- **주의**: pooled 미유의 ≠ 분야 간 이질성 증거; 분야별 분해에서 이질성 *식별*.

→ **진짜 메커니즘은 분야별 이질성**, 그러나 농림수산 외 분야에서 개별 추가 검증 필요.

---

## 5-A. 다중 비교 보정 — 가설 수준 발견의 정직 명시 ★

H5 사회복지 fortuitous alignment (*r*=−0.762, *p*=0.035)는 14분야 동시 permutation test
결과 중 하나다. **Bonferroni 보정 임계값** α=0.05/14=0.0036 적용 시 사회복지 *p*=0.035는
통과 미달이다.

본 연구의 결론 robustness 보강 근거:
1. **부호 일관성**: 14분야 모두 음 상관 방향 (CPI 통제 후 *r*=−0.86 강화)
2. **사전 가설**: 사회복지 자동분배 메커니즘 사전적 추론
3. **이론적 일관성**: alignment 함수 α의 분야별 이질성

그러나 strict 기준에서는 **"후속 검증을 위한 가설 수준 발견"**으로 해석되어야 함.
Bonferroni 보정 통과 미달 사실을 논문 §8 및 본 절에서 명시적으로 인정.

---

## 6. Outcome 적합도 (사용자 비판 4단계 반영)

| 분야 | 기존 outcome | 문제 | 교체 |
|---|---|---|---|
| 과기 | rd_total | 입력 변수 = outcome 동일 (자기 인과) | ✅ patent_apps_total |
| 관광 | tourists_sample | 표본수 ≠ 실제 입국자 | ✅ foreign_tourists_total |
| 행정 | local_tax_per_capita | 징세 ≠ 행정 outcome | ✅ fiscal_indep_natl |
| 통신 | ict_value_added | 자기 인과 | ✅ broadband_per_100 |
| 교육 | private_edu_hours | 사교육 = 역지표 | ✅ imd_edu_rank |
| 국방 | defense_op_margin | 영업이익률 ≠ 안보 outcome | ❌ 보류 (분야 제외) |

---

## 7. 미시 데이터 부재

- 활동 단위 KPI 달성도: 비공개·부재
- 정부업무평가 등급: 시계열 비공개
- → SBERT 텍스트 임베딩 (활동명) 등 간접 접근만 가능

---

## 8. 단일 국가

- 비교 분석 없음
- OECD COFOG는 *연간*만 → 게임화 측정 불가
- → **다국가 비교는 향후 연구**

---

## 9. 이론 모형 한계

- P-A 모형: Holmstrom-Milgrom (1987) **single-period static** + Holmstrom (1999) **multi-period career concerns** *하이브리드*
- Sannikov (2008) **연속시간 동적 PA** 의 일부 동학 (HJB equation, optimal contract path) **미반영**
- → 균형 비교정학 (1차 조건)은 robust하나, off-equilibrium 동학 검증은 추가 모형 필요

---

## 9-A. H2 Step Function — 모형 가정 vs. 데이터 관찰 구분

자산취득형 RDD 3.42× 점프는 비용함수 step function 형태의 **데이터 관찰 증거**이지,
이론 모형이 step function을 *예측*한 것은 아니다. 진정한 모형 검증은 지출 유형 간
archetype 비교에 있다:

| 지출 유형 | RDD 점프 배율 |
|---|---|
| 자산취득 | 3.42× |
| 출연금 | 1.10× |
| 인건비 | 1.12× |

이 이질성이 step function 비용 구조의 실질적 근거이며, 단일 추정치 해석은 과대 해석 위험.

---

## 10. 주파수 분석 한계

### Wavelet (H28) scale 민감도
- Morlet wavelet의 시간-주파수 trade-off (**Heisenberg uncertainty**)
- **+554% 추정치는 wavelet scale 선택에 민감**
- → ricker / morlet 비교 robustness check 필요

### PSD/Coherence (H27) 표본 크기
- 활동 단위 phase coherence 추정에서 **cycle 수 ≤ 11** (11년 데이터)
- → confidence interval 넓음
- coherence **0.54** 는 의미 있으나 정확도는 제한적

---

## 11. Performative prediction 가설 한계 ★ 식별 불가

H6 wavelet **+554% 시간 강화**의 두 가지 해석:

| 해석 | 메커니즘 |
|---|---|
| Performative (이론) | agent가 KPI에 점진 학습 → 게임화 강화 |
| 측정 도구 변화 | 회계 기준·보고 의무 변경으로 12월 집중 *기록*이 늘어남 |

→ 두 메커니즘의 **식별 불가** (counterfactual: KPI 없는 정부). 시간 강화가 실재해도 인과는 약함.

---

## 12. 재현성 보강 사항

- **NeuralProphet random_seed=42** 명시 (scripts/ 전체 random_state=42 일관)
- 이전 실행 결과 대비 미세 변동 가능 (seed 미고정 버전 존재했음)
- 모든 분석 코드 GitHub 공개, `warehouse.duckdb` tracked
- 향후 결과 재생산 시 scripts/ 폴더 내 seed 설정 확인 필요
