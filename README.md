# 재정자료 분석 프로젝트

열린재정 재정정보공개시스템(<https://www.openfiscaldata.go.kr>)과 KODAS 데이터 분석서비스의 데이터·명세를 수집·정리하고, DuckDB 웨어하우스로 통합한 분석 프로젝트.

배경: 2026년 재정데이터 분석 미니프로젝트 신청 준비.

분석 주제: **정부 재정 집행의 굿하트 효과 — 분야별 게임화 강도 측정과 정책 결과지표와의 Decoupling**.

전체 분석 여정은 **[docs/analysis/JOURNEY.md](docs/analysis/JOURNEY.md)** 참고.

## 구조

```
.
├── scripts/        수집 + 빌드 + 분석 스크립트
│   ├── fetch_specs.py            OPEN API 명세 167건 수집
│   ├── fetch_kodas.py            KODAS 카탈로그 1,707건 수집
│   ├── fetch_monthly_exec.py     ★ 월별 단위사업 집행 5년치 (게임화 분석 핵심)
│   ├── build_warehouse.py        DuckDB warehouse 빌드
│   ├── build_docs.py             분류별 마크다운 생성
│   ├── eda.py                    광역 EDA (분야·부처·통계목)
│   ├── eda_goodhart.sql          굿하트 가설 SQL EDA
│   └── goodhart_freq.py          ★ 주기성 분석 (FFT + STL + Coherence)
├── data/           정제 데이터 (JSON+CSV) + DuckDB 웨어하우스 + 시각화
│   ├── figs/                     시각화 PNG (eda/, freq/)
│   └── results/                  분석 결과 CSV
├── docs/           사람이 읽기 쉬운 분류별 명세 + 분석 리포트
│   ├── openapi/                  OPEN API 167 명세 마크다운
│   ├── kodas/                    KODAS 1,707 카탈로그
│   └── analysis/                 ★ 분석 리포트
├── raw/            (gitignore) 페이지 캡처·프로브 원본
└── 자료/           기존 자료 (touch 안 함)
```

## 데이터 자산

### 카탈로그
- **OPEN API 명세 167건** → [docs/openapi/INDEX.md](docs/openapi/INDEX.md)
- **KODAS 카탈로그 1,707건** → [docs/kodas/INDEX.md](docs/kodas/INDEX.md)

### DuckDB 통합 웨어하우스 (`data/warehouse.duckdb`)
| 테이블 | 행수 | 단위 | 시간 범위 |
|---|---:|---|---|
| `expenditure_budget` | 120,077 | 세부사업 × 회차 | 2020~2026 |
| `expenditure_item` | 611,027 | 편성목/세목 | 2020~2026 |
| `revenue_budget` | 20,745 | 세입 × 회차 | 2020~2026 |
| **`monthly_exec`** | **227,709** | **단위사업 × 월** | **2020~2026.03** |
| `debt_monthly` | 134 | 월 | 2015~2026.02 |
| `debt_yearly` | 15 | 연 | 2010~2024 |
| `openapi_catalog` | 167 | 명세 | - |
| `kodas_catalog` | 1,707 | 메타 | - |

총 DB 크기: ~28MB

## 분석 리포트

- **[JOURNEY.md](docs/analysis/JOURNEY.md)** — ★ 전체 분석 여정, 가설 진화, 핵심 발견
- [AI_spending_leak_pattern.md](docs/analysis/AI_spending_leak_pattern.md) — 사전 탐색 단계 (보조)

## 재생성

```bash
export OPENFISCAL_KEY='your-key-here'

# 카탈로그 + 명세
python scripts/fetch_specs.py
python scripts/fetch_kodas.py
python scripts/build_docs.py

# 웨어하우스 (편성·결산 데이터)
python scripts/build_warehouse.py

# 월별 단위사업 집행 (게임화 분석 핵심)
python scripts/fetch_monthly_exec.py

# 분석
python scripts/eda.py
python scripts/goodhart_freq.py
```

## 발견한 내부 엔드포인트

| 기능 | 엔드포인트 | 페이로드 |
|---|---|---|
| Open API 목록 | `POST /op/ko/ds/selectOpenApiList.do` | form: `pageIndex, page, rowPerPage` |
| 서비스 상세메타 | `POST /op/ko/sd/dtsStats/selectSrvDtlInfoList.do` | json: `{opKoSdDtsStatsDVO:{odtId}}` |
| 명세+응답구조 | `POST /op/ko/sd/dtsStatsAcol/selectAcolViewList.do` | json: `{odtId, rlsSvTyCd:'A', odtSvSeq}` |
| KODAS 카탈로그 | `POST /op/ko/sb/selectCatalogList.do` | json: `{pageIndex, pageSize, totalCnt}` |
| OPEN API 호출 | `GET https://openapi.openfiscaldata.go.kr/{서비스코드}` | `Key=...&Type=json&pIndex=&pSize=` (max 1000) |
| 부처 코드 사전 | `POST /op/ko/cm/selectItgFiCdList.do` | json: `{opKoCmItgFiCdList:[{condType:'YR_OFFC_CD',acntYr}]}` |
| 월별 집행 (VWFOEM) | `GET https://openapi.openfiscaldata.go.kr/VWFOEM` | `FSCL_YY, EXE_M, OFFC_CD(필수)` (3자리) |

## 주의

- `OPENFISCAL_KEY`(인증키)는 `.gitignore`로 커밋 제외. 환경변수로만 전달.
- `data/warehouse.duckdb`는 28MB → gitignore. 재현은 위 명령으로 (~30~45분 소요).
- `data/budget/raw/`도 gitignore (재생성 가능, 350MB 이상).
