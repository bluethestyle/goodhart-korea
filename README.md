# 재정자료 분석 프로젝트

열린재정 재정정보공개시스템(<https://www.openfiscaldata.go.kr>)과 KODAS 데이터 분석서비스의 데이터·명세를 수집·정리하고, DuckDB 웨어하우스로 통합한 분석 프로젝트.

배경: 2026년 재정데이터 분석 미니프로젝트 신청 준비.

## 구조

```
.
├── scripts/        수집 + 빌드 스크립트
│   ├── fetch_specs.py        OPEN API 명세 167건 수집
│   ├── fetch_kodas.py        KODAS 카탈로그 1,707건 수집
│   ├── build_docs.py         data/*.json → docs/ 마크다운 생성
│   └── build_warehouse.py    OPEN API 시계열 + 메타 → DuckDB 단일 파일
├── data/           정제 데이터 (JSON+CSV) + DuckDB 웨어하우스
├── docs/           사람이 읽기 쉬운 분류별 명세 문서
├── raw/            (게이트키핑) 페이지 캡처·프로브 원본
└── 자료/            기존 자료 (touch 안 함)
```

## 데이터 자산

- **OPEN API 명세 167건** — 분류별 마크다운: [docs/openapi/INDEX.md](docs/openapi/INDEX.md)
- **KODAS 카탈로그 1,707건** — 분류별 마크다운: [docs/kodas/INDEX.md](docs/kodas/INDEX.md)
- **DuckDB 통합 웨어하우스** (`data/warehouse.duckdb`):
  - `expenditure_budget` — 세출 세부사업 (본예산 + 추경 모든 회차) ★
  - `revenue_budget`     — 세입 (본예산 + 추경 모든 회차)
  - `debt_monthly`       — 월별 국가채무
  - `debt_yearly`        — 연도별 국가채무 (D1)
  - `openapi_catalog`    — OPEN API 167건 명세
  - `kodas_catalog`      — KODAS 1,707건 카탈로그

## 재생성

```bash
# 1) OPEN API 명세 수집
python scripts/fetch_specs.py

# 2) KODAS 카탈로그 수집
python scripts/fetch_kodas.py

# 3) 마크다운 문서 빌드
python scripts/build_docs.py

# 4) DuckDB 웨어하우스 빌드 (인증키 필요)
export OPENFISCAL_KEY='your-key-here'
python scripts/build_warehouse.py
```

## 발견한 내부 엔드포인트

| 기능 | 엔드포인트 | 페이로드 |
|---|---|---|
| Open API 목록 | `POST /op/ko/ds/selectOpenApiList.do` | form: `pageIndex, page, rowPerPage` |
| 서비스 상세메타 | `POST /op/ko/sd/dtsStats/selectSrvDtlInfoList.do` | json: `{opKoSdDtsStatsDVO:{odtId}}` |
| 명세+응답구조 | `POST /op/ko/sd/dtsStatsAcol/selectAcolViewList.do` | json: `{odtId, rlsSvTyCd:'A', odtSvSeq}` |
| KODAS 카탈로그 | `POST /op/ko/sb/selectCatalogList.do` | json: `{pageIndex, pageSize, totalCnt}` |
| OPEN API 호출 | `GET https://openapi.openfiscaldata.go.kr/{서비스코드}` | `Key=...&Type=json&pIndex=&pSize=` (max 1000) |

## 주의

- `OPENFISCAL_KEY`(인증키)는 `.gitignore`로 커밋 제외. 환경변수로만 전달.
- `data/warehouse.duckdb`는 100MB+ 가능 → gitignore. 재현은 위 명령으로.
- `data/budget/raw/`도 gitignore (재생성 가능).
