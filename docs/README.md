# 재정자료 데이터 명세 정리

열린재정 정보공개시스템(<https://www.openfiscaldata.go.kr>)의 두 가지 데이터 자원 명세서.

## 1. 열린재정 Open API — 167건

실시간/주기적으로 호출 가능한 공식 OpenAPI. 인증키 발급 후 `https://openapi.openfiscaldata.go.kr/{서비스코드}` 형태로 호출.

→ **[openapi/INDEX.md](openapi/INDEX.md)**

## 2. KODAS 제공 데이터 카탈로그 — 1,707건

데이터분석서비스(KODAS)에서 분석용으로 제공하는 융복합 데이터셋. 직접 호출 API는 없고 KODAS 신청 후 센터 방문 또는 분석환경에서 활용.

→ **[kodas/INDEX.md](kodas/INDEX.md)**

## 원본·중간 산출물

| 위치 | 내용 |
|---|---|
| `data/all_apis.json` | Open API 카탈로그 메타 (167건) |
| `data/api_specs.json` | Open API 명세 정제 (요청/응답 필드 포함) |
| `data/api_specs.csv` | 위 항목의 표 형식 |
| `data/api_specs_raw.json` | Open API 명세 원본 응답 백업 |
| `data/kodas_catalog.json` | KODAS 카탈로그 정제 (1,707건) |
| `data/kodas_catalog.csv` | KODAS 카탈로그 CSV |
| `data/kodas_catalog_raw.json` | KODAS 원본 응답 |
| `raw/list_pages/` | Open API 목록 페이지 원본 (페이지별 JSON) |
| `raw/detail_probe/` | Open API 상세 페이지 네트워크 캡처 |
| `raw/kodas_probe/` | KODAS 페이지 네트워크 캡처 |
| `scripts/` | 수집·문서 생성 스크립트 |

## 재생성

```bash
python scripts/fetch_specs.py    # Open API 명세 167건
python scripts/fetch_kodas.py    # KODAS 카탈로그 1,707건
python scripts/build_docs.py     # 위 결과 → docs/ 마크다운
```

## 발견한 내부 엔드포인트

| 기능 | 엔드포인트 | 페이로드 |
|---|---|---|
| Open API 목록 | `POST /op/ko/ds/selectOpenApiList.do` | form: `pageIndex, page, rowPerPage` |
| 서비스 상세메타 | `POST /op/ko/sd/dtsStats/selectSrvDtlInfoList.do` | json: `{opKoSdDtsStatsDVO:{odtId}}` |
| 명세+응답구조 | `POST /op/ko/sd/dtsStatsAcol/selectAcolViewList.do` | json: `{odtId, rlsSvTyCd:'A', odtSvSeq}` |
| KODAS 카탈로그 | `POST /op/ko/sb/selectCatalogList.do` | json: `{pageIndex, pageSize, totalCnt}` |
