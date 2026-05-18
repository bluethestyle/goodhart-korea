# 감사원 (Board of Audit and Inspection) — 산출물 패키지

## 목적

정기·정책감사 대상 사전 선정을 위한 *극단 게임화 활동 우선 점검 리스트*.

## 파일

- **`extreme_50_activities.parquet`** / **`.csv`** — 극단 게임화 활동 TOP 50
  - 1,557개 활동 중 *amp_12m_norm × dec_pct 상위 50건*
  - 12월 집행 비중이 평균(8.33%)의 3배 이상인 활동만 후보

## 컬럼 정의

| 컬럼 | 의미 |
|---|---|
| `rank` | exposure_score 기준 순위 (1~50) |
| `field` | 14분야 분류 (열린재정 기준) |
| `ministry` | 부처명 (열린재정 OFFC_NM) |
| `program` | 프로그램명 (PGM_NM) |
| `activity` | 활동명 (세부사업, ACTV_NM) |
| `archetype` | 사업 원형: 인건비형 / 자산취득형 / 출연금형 / 정상사업 |
| `exposure_score` | amp_12m_norm × dec_pct (게임화 강도 × 12월 쏠림) |
| `amp_12m_norm` | FFT 12개월 진폭 (정규화) — 게임화 강도 지표 |
| `dec_pct` | 12월 집행 비중 (0~1) — flat 기준 8.33% |
| `dec_jump_ratio` | dec_pct / (1/12) — 12월 쏠림 배수 |
| `chooyeon_pct` | 출연금 편성목 비중 (0~1) |
| `direct_invest_pct` | 직접투자 편성목 비중 |
| `personnel_pct` | 인건비 편성목 비중 |
| `total_budget` | 11년 누적 예산 (천 원) |
| `year_n` | 데이터 가용 연수 (1~11) |

## 활용 시나리오 — 감사원 정기 감사 사이클

1. **매년 1월**: 직전 12월 집행 자료 갱신 → `scripts/h29_extreme_50_activities.py` 재실행
2. **2~3월**: 50건 리스트를 정기 감사 대상 *후보 풀*에 입력. 자산취득형(직접투자) + 12월 쏠림 결합 활동 우선
3. **감사 착수 전 사전 점검**: `archetype` + `dec_jump_ratio` + `total_budget` 조합으로 점검 우선순위 산출
4. **결과 환류**: 감사 결과를 archetype 분류에 환류해 차년도 알고리즘 검증

## 점검 시 주의 사항

- *exposure_score 상위 = 비위 의심*이 아님. 사업 구조상 12월 정산이 정당한 활동(예: 결산 처리, 연말 일괄 계약)도 포함될 수 있음. 행정 절차 점검 시 *맥락 확인 필수*.
- 정상사업(cluster 3)이 36건으로 다수인 것은 cluster 3 활동 수가 많기 때문(1,175개). 자산취득형은 99개 중 13건이 TOP 50에 포함되어 *비율로는 13.1%* (정상사업 3.1% 대비 4배 이상).
- 본 리스트는 데이터 분석 결과이며, 단독으로 행정 처분의 근거가 되지 않는다.

## 알고리즘 재현

```python
import pandas as pd
df = pd.read_csv('data/results/H3_activity_embedding_11y.csv')
df = df[df['dec_pct'] >= 1/12 * 3]                 # 12월 쏠림 3배 이상
df['exposure'] = df['amp_12m_norm'] * df['dec_pct']
top50 = df.nlargest(50, 'exposure')
```
