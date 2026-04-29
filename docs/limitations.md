# 한계 (정직한 명시)

---

## 1. 인과 식별 약점

- **DID 통제군 부재**: 한국 단일 정부 → 정책 효과 비교군 없음
- **자연 실험 부재**: KPI 도입 시점 점진적 (2007~), 명확한 cutoff 없음
- **RDD 한계**: 회계연도 12월 1일 cutoff는 *시간 차원*만 식별, 정책 처치 cutoff 아님

→ **Triangulation 전략**으로 보강:
   - CPI 통제 / STL trend / permutation / bootstrap / RDD / mediation 일관성

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

## 5. Mediation 매개 효과 약함

- Pooled FE: ab=0.018β, p=0.481 (시스템 평균 미유의)
- 농림수산만 Sobel p=0.004 (음의 매개)
- 사회복지 매개비율 57%이나 통계 미달

→ **분야별 이질성이 진짜 메커니즘**, 시스템 평균 게임화 효과 약함

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
