# 기관별 산출물 패키지 (Deliverables)

본 폴더는 한국 정부 재정 굿하트 분석의 *현장 활용 산출물*을 기관별로 분류한 것이다. 학술 산출물(논문·전체 CSV/PNG)은 [paper/](../paper/), [data/results/](../data/results/)에 있다.

## 폴더 구조

| 폴더 | 대상 기관 | 활용 시나리오 |
|---|---|---|
| [audit_board/](audit_board/) | 감사원 | 정기·정책감사 대상 사전 선정 — 극단 게임화 활동 50건 |
| [npbo/](npbo/) | 국회 예산정책처 | 부처별 예산 심사 — 부처×결과변수 4분면 + 51 부처 진단표 |
| [moef/](moef/) | 기획재정부 | 출연기관 평가 지표 전환 — 사업 원형별 cycle 지표 |
| [moi/](moi/) | 행정안전부 | 정부혁신실 자체 점검 dashboard 도입 |
| [kfi/](kfi/) | 한국재정정보원 (KODAS 운영) | KODAS 자율평가 ↔ 게임화 강도 연계 분석 제안 |

## 파일 형식

각 폴더는 동일한 데이터를 두 형식으로 동봉한다.

- **`.parquet`** — 정본. 컬럼 압축·dtype 보존. DuckDB·pandas·Spark에서 즉시 로드.
- **`.csv`** — 핸드오프본 (UTF-8 BOM). Excel에서 한글 깨짐 없이 즉시 열림.

## 빠른 시작

```python
import duckdb
con = duckdb.connect()
df = con.execute("""
  SELECT * FROM read_parquet('deliverables/audit_board/extreme_50_activities.parquet')
""").fetchdf()
```

또는 pandas로:

```python
import pandas as pd
df = pd.read_parquet('deliverables/audit_board/extreme_50_activities.parquet')
```

## 재생성

```bash
python scripts/h29_extreme_50_activities.py   # audit_board 갱신
python scripts/build_deliverables.py          # 그 외 패키지 일괄 갱신
```

## 라이선스 / 출처 표시

- **데이터**: CC BY 4.0
- **분석 코드**: MIT License
- **원자료 출처**: 열린재정정보, KOSIS, 한국은행 ECOS, GIR, KODAS — 각 출처 라이선스는 [data/external/SOURCES.md](../data/external/SOURCES.md)
- **인용**: [README.md](../README.md) 인용 섹션 참조

## 한계 / 주의

- 본 산출물은 *공개 자료 기반 데이터 분석 결과*이며, 개별 사업·부처에 대한 행정 처분의 직접 근거가 아니다.
- 극단 활동 50건은 *우선 점검 후보*이지 *비위 적발 결과*가 아니다 — 실제 점검은 행정 절차에 따른 별도 조사 필요.
- 본 분석은 2015~2025 11년치 월별 집행 자료에 기반하며, 분석 시점 이후 변동은 반영되지 않는다.
