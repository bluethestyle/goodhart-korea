# 국회 예산정책처 (NABO) — 산출물 패키지

## 목적

부처별 예산 심사 시 *게임화 노출도 + 결과변수 동시 검토* 자료. 점검 자원을 *Q2(게임화↑ + 결과 악화 동행)* 부처에 우선 배분하는 의사결정 도구.

## 파일

### 1. `ministry_quadrant.{parquet,csv}` — 부처×결과변수 4분면 (7 부처)

outcome 시계열이 충분히 확보된 7개 부처에 대해 *게임화 노출과 결과변수 부호의 4분면 배치*.

| 분면 | 의미 | 정책 함의 |
|---|---|---|
| **Q2 (위험: 측정 왜곡)** | 게임화 노출↑ + outcome 악화 동행 | **우선 점검** |
| Q1 (주의: 자동분배) | 게임화 노출↑ + outcome 개선 동행 | 우연한 alignment 가능성 검토 |
| Q3, Q4 | 게임화 노출↓ | 본 분석 우선순위 외 |

### 2. `ministry_diagnosis.{parquet,csv}` — 51 부처 전체 진단표

#### 컬럼

| 컬럼 | 의미 |
|---|---|
| `ministry` | 부처명 |
| `n_activities` | 해당 부처 활동 수 |
| `exposure_score` | 게임화 노출 (활동별 가중 평균) |
| `exposure_budget_weighted` | 예산 가중 노출 |
| `co_cluster_id` | Spectral Co-clustering 부처 커뮤니티 (0~4) |
| `pct_grant_program` | 출연금 편성목 비중 |
| `pct_extreme_gaming` | 극단 게임화 활동(sub05) 비중 |
| `pct_mild_gaming` | 경도 게임화 활동(sub01) 비중 |

## 활용 시나리오 — 예산결산 심사

1. **예산안 심사 (8~12월)**: Q2 부처를 우선 검토. ministry_quadrant.csv를 부처별 의견조회에 첨부
2. **결산 심사 (4~6월)**: ministry_diagnosis.csv로 51 부처 전체 노출도 비교. 노출도 + 출연금 비중 결합이 높은 부처에 결산 보고서 요청
3. **개별 사업 심사**: [audit_board/extreme_50_activities](../audit_board/) 와 교차 참조해 부처×활동 단위 점검

## 본 분석 기준 Q2 부처 (우선 점검)

- **과학기술정보통신부**: 게임화 노출 0.560 + 결과변수 양의 차분 상관 0.152
- 추가 Q2 부처는 outcome 매핑 보강 시 식별 가능

## 한계

- ministry_quadrant는 outcome 시계열 N≥6년인 부처에 한정 (현재 7개)
- 분야 단위 outcome 매핑이 부처 단위로 완벽히 정렬되지 않을 수 있음
