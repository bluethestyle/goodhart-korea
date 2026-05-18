# 기획재정부 (MOEF) — 산출물 패키지

## 목적

*출연기관 경영평가 지표 전환* 및 *MTEF 격상* 권고의 근거 자료. 사업 원형별 cycle 지표 + 시간 동적 변화를 신호처리 영역에서 정량화.

## 파일

### 1. `archetype_psd.{parquet,csv}` — 사업 원형별 Power Spectral Density

각 archetype의 주파수 영역 진폭. k=1은 12개월 cycle.

- 출연금형(cluster 2): psdnorm_k1 = 0.332 — *다른 archetype의 2~6배*
- 출연금형의 강한 12개월 cycle은 모기관-위탁기관 12월 일률 정산 압력의 직접 신호

### 2. `archetype_coherence.{parquet,csv}` — Phase Coherence

archetype 내부 활동들이 *동시에* 12월 정산을 받는지 측정.

- 출연금형 phase_coherence = 0.54 (12개월 주기): archetype 내부 절반 이상이 phase 동조
- *연성 예산 제약* 메커니즘의 신호처리적 증거

### 3. `wavelet_period_split.{parquet,csv}` — 시기별 Wavelet Power

2015~17 vs 2018~20 vs 2021~25 시기별 12개월 cycle 진폭.

### 4. `wavelet_transitions.{parquet,csv}` — 시기 전이 분석

시기 간 진폭 변화율. 출연금형의 +554% 누적 강화 (2015~17 → 2023~25 평균 비).

## 정책 권고 (P-A 모형 비교정역학 매핑)

| 권고 | 모형 레버 | 근거 산출물 |
|---|---|---|
| **출연기관 경영평가 지표 전환**: 집행률 비중 축소($w_t$↓) + 사업 품질 평가 가중 확대($w_q$↑) | $w_t$↓, $w_q$↑ | archetype_psd (출연금형 cycle 우세), archetype_coherence |
| **MTEF 다년도 회계 격상**: 5년 framework을 실제 회계 단위로 | $w_t$↓ | wavelet_transitions (시간 강화는 단년 마감 압력 누적) |
| **출연기관 정산 시점 분산**: 분기/반기 정산으로 12월 일률 회피 | $c_{tt}$↑ | archetype_coherence 0.54 → 분산 시 감소 |
| **자동 감사 flagging**: 실시간 모니터링 dashboard | $c_{tt}$↑ | wavelet_period_split (시기별 추이 추적) |

## 한계 — Holmstrom-Milgrom impossibility

$w_q$ 증가의 효과는 *측정성 격차 함수* $\phi'(\cdot) < 1$의 본질적 한계로 일부에 그친다. 사업 품질 측정 인프라(행정연구원 사업평가센터 등) 강화가 전제 조건.
