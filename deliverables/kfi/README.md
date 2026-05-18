# 한국재정정보원 (KFI / KODAS 운영) — 산출물 패키지

## 목적

KODAS(Korea Open Data Analysis System) 자율평가 결과 ↔ 본 분석의 게임화 강도 *직접 상관 분석* 연계 제안. KODAS 카탈로그를 본 프로젝트 warehouse에 사전 적재한 1차 작업 결과 동봉.

## 파일

- **`kodas_catalog_summary.{parquet,csv}`** — KODAS 카탈로그 기관×데이터셋군 요약
  - 1,707건 카탈로그 메타 (warehouse `kodas_catalog` 테이블)
- **`kodas_field_summary.{parquet,csv}`** — KODAS 분야별 데이터셋 분포

## 연계 분석 제안

### 핵심 가설

> KODAS 재정사업 자율평가에서 *높은 점수*를 받은 사업이 *높은 게임화 강도*를 보이는가?

### 검증 설계

1. **자료 결합**: KODAS 자율평가 점수 (사업별·연도별) × 본 분석 활동별 amp_12m_norm
2. **회귀**: gaming_score ~ self_eval_score + archetype + ministry FE + year FE
3. **예측 부호**:
   - 양 상관 → 평가 시스템이 게임화를 *보상*하는 직접 증거 (Holmstrom-Milgrom multitask 한국 발현)
   - 음 상관 → 평가 시스템이 게임화를 *통제*하는 증거 (정책 의도 작동)
   - 무 상관 → 자율평가가 *측정 가능 task*에만 가중을 둬서 게임화와 무관 (별개 메커니즘)

### 어느 결과든 정책 시사

세 경우 모두 *재정사업 자율평가 지표 설계 재검토* 근거. 본 분석의 P-A 모형 비교정역학(${\partial e_t^*}/{\partial w_t} > 0$)과 결합해 평가 지표 가중치 조정 방향 도출 가능.

## 추가 요청 자료 (협의 사항)

본 미니프로젝트 기간 내에 다음 자료 제공 가능 여부 협의 요청:

1. **재정사업 자율평가 결과** — 2015~2025, 사업별·연도별 점수 (정량평가 + 정성평가 분리)
2. **결산 자료** — 부처별·세부사업별 결산액 vs 예산액 차이 (잔여 예산 12월 처리 패턴 검증)
3. **출연기관 경영평가 상세** — 알리오 공시 외 *문항별 점수* (집행률 평가 가중치 직접 측정용)

## 본 분석 → KODAS 환류 제안

본 프로젝트의 부산물을 KODAS 활용 사례로 등록할 수 있도록 협의:

- `data/results/extreme_50_activities.parquet` — KODAS 분석 사례 라이브러리 등재
- `paper/main_v2.typ` 결론부 — KODAS 자율평가 ↔ 게임화 강도 연계 분석 white paper
- `scripts/` 분석 코드 30+개 — KODAS 분석 도구 라이브러리 기여

## 데이터 출처 (현재)

- `kodas_catalog` 테이블: KODAS 공개 카탈로그 API (1,707건 메타, dtaLoadCnt=0)
- 자율평가·결산 등 *실데이터*는 별도 신청·승인 후 결합 예정
