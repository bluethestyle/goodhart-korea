# 외부 데이터 출처 정리 (검증된 직접 다운로드 링크)

분석 사용 12개 분야 outcome + 거시 통제변수 + 보조 데이터의 정확한 출처.
**사용자가 클릭만으로 받을 수 있는 검증된 링크**.

---

## I. 적재 완료 — 12분야 outcome

### KOSIS API 자동 fetch (KOSIS_KEY 등록되어 자동 호출됨)

| 분야 | metric | 통계표 | 시계열 | 적재 스크립트 |
|---|---|---|---|---|
| 사회복지 | `wealth_gini` | 101/DT_1HDAAD04 순자산 지니계수 | 2017~2025 (9y) | `load_kosis_outcomes.py` |
| 보건 | `life_expectancy` | 101/DT_1B41 0세 기대여명 | 2010~2024 (15y) | `load_kosis_outcomes.py` |
| 과학기술 | `rd_total` | 101/DT_1EP1322 산업R&D비 | 2006~2024 (19y) | (직접 패치) |
| 산업·중기 | `industry_production_index` | 101/DT_1JH20201 전산업생산지수 | 2011~2025 (15y) | `load_kosis_outcomes.py` |
| 문화관광 | `tourists_sample` | 113/DT_113_STBL_1027329 | 2014~2022 (7y) | `load_kosis_outcomes.py` |
| 교육 | `private_edu_hours` | 101/DT_1PE103 사교육 시간 | 2007~2025 (19y) | `h7_outcome_load.py` |
| 국토·지역 | `housing_supply` | 116/DT_MLTM_2100 주택보급률 | 2005~2024 (20y) | `h7_outcome_load.py` |
| 일반·지방행정 | `local_tax_per_capita` | 110/DT_11001N_2013_A012 | 2009~2020 (12y) | `h7_outcome_load.py` |
| 농림수산 | `farm_income` | 101/DT_1EA1501 농가소득 | 2003~2024 (22y) | `h7_outcome_load.py` 추가 |

### 공공데이터포털 API (DATA_GO_KR_KEY 활용신청 후)

| 분야 | metric | API endpoint | 시계열 |
|---|---|---|---|
| 교통·물류 | `traffic_deaths` | `apis.data.go.kr/B552061/lgStat/getRestLgStat` (도로교통공단) | 2015~2024 (10y) |

### 한국은행 ECOS (BOK_KEY)

| 분야 | metric | 통계표 | 시계열 |
|---|---|---|---|
| 통신 | `ict_value_added` | 200Y158 정보통신산업 부가가치 (실질) | 1995~2025 (31y) |
| 거시 통제 | `cpi` | 901Y009 소비자물가지수 | 1990~2025 (36y) |

### 정적 다운로드 (사용자 수동, 검증됨)

| 분야 | metric | 출처 + 검증된 다운로드 링크 | 시계열 |
|---|---|---|---|
| 환경 | `ghg_total/net/energy` | [GIR 국가 인벤토리 (data.go.kr/data/15049589)](https://www.data.go.kr/data/15049589/fileData.do) → 외부 redirect → [GIR 사이트](https://www.gir.go.kr/) | 1990~2023 (34y) |

---

## II. 추가 진행 가능 — 잔여 3분야 outcome

### ✅ 검증된 e-나라지표 직접 다운로드 (사용자 1-click)

| 분야 | 지표명 | URL (검증) | 시계열 | 적합도 |
|---|---|---|---|---|
| **통일·외교** | ODA 원조규모 | [idx_cd=1687](https://www.index.go.kr/unity/potal/main/EachDtlPageDetail.do?idx_cd=1687) | **1990~2024 (35y)** | ★★★ OECD Data 기반 |
| **통일·외교** (보조) | GNI 대비 ODA 비율 | [idx_cd=1688](https://www.index.go.kr/unity/potal/main/EachDtlPageDetail.do?idx_cd=1688) | 동일 | ★★ |
| **공공질서** | 총범죄 발생 및 검거 | [idx_cd=1606](https://www.index.go.kr/unity/potal/main/EachDtlPageDetail.do?idx_cd=1606) | 경찰청 발표 (1년 단위) | ★★★ |
| **국방** (보조) | 방산업체 경영실태 (매출·영업이익) | [idx_cd=1703](https://www.index.go.kr/unity/potal/main/EachDtlPageDetail.do?idx_cd=1703) | 1995~2023 (29y) | ★★ (수출이 아니라 매출) |

각 페이지 상단의 **"파일다운로드"** 버튼 → Excel 받아 루트에 두시면 자동 적재.

### ❌ 부정확/부적합 (이전 답변 정정)

내가 이전 답변에서 잘못 알려드렸던 idx_cd:
- ❌ idx_cd=**1610** = 실종아동 신고 (범죄 X)
- ❌ idx_cd=**1632** = 화재발생 현황 (방산수출 X)
- ❌ idx_cd=**1265, 1268** = 존재 불확실 (병력·국방예산 추정값이었음)

**병력은 청년인구 trend 종속 변수라 outcome 부적합** (사용자 지적 정확).

### 그 외 옵션 (활용신청 또는 API 키 필요)

| 분야 | 후보 | 출처 |
|---|---|---|
| 공공질서 (대안) | 5대범죄 시도별 시계열 | 공공데이터포털 `경찰청_경찰청 범죄통계` 활용신청 |
| 통일·외교 (대안) | 한국 ODA 사업 단위 | [koica.go.kr](https://www.koica.go.kr/) 또는 OECD DAC API (키 불필요) |

---

## III. 분석 입력 데이터 (게임화 측정)

| 출처 | 용도 | 인증 |
|---|---|---|
| **OPENFISCAL** VWFOEM | 월별 집행 (amp_12m 등 게임화 시그니처) | OPENFISCAL_KEY |
| **OPENFISCAL** 예산·항목 | 활동별 출연금/운영비/직접투자 비중 | OPENFISCAL_KEY |

시계열: 2015~2026 (11.5년).

---

## IV. 보조·메타 데이터

```
data/external/
├── bok_data/                   한은 ECOS 캐시 (CPI, ICT)
├── data_go_kr/                 공공데이터포털 캐시 (도로교통공단)
├── gir/                        GIR 국가 인벤토리 1990~2023 ★
├── kosis_data/                 KOSIS API 캐시 (10 분야)
├── kosis_meta/                 KOSIS 카탈로그 (24MB) + outcome 발굴 csv
├── molit/                      통계누리 자동차등록 raw 4개 (보류)
└── SOURCES.md                  본 문서
```

---

## V. API 키 등록 (.env, gitignore됨)

```
OPENFISCAL_KEY     열린재정정보 (https://www.openfiscaldata.go.kr/)
KOSIS_KEY          KOSIS 국가통계포털 (https://kosis.kr/openapi/)
BOK_KEY            한국은행 ECOS (https://ecos.bok.or.kr/)
DATA_GO_KR_KEY_*   공공데이터포털 (https://www.data.go.kr/) — encoded/decoded
```

---

## VI. 출처 정합성 검증 (2026-04-28 기준)

웹 직접 검증 완료:
- ✅ idx_cd=1687 ODA 원조규모 (1990~2024, 35y)
- ✅ idx_cd=1606 총범죄 발생 및 검거 (경찰청)
- ✅ idx_cd=1703 방산업체 경영실태 (1995~2023, 29y)
- ✅ data.go.kr/data/15056770 도로교통공단 lgStat
- ✅ data.go.kr/data/15049589 GIR 국가 인벤토리
- ✅ BOK 200Y158 정보통신산업 부가가치
- ✅ KOSIS 모든 표 (orgId/tblId 형식 표준)

부정확/부적합 명시:
- ❌ idx_cd=1610 (실종아동), 1632 (화재), 1265/1268 (존재 불확실)
- ❌ vehicle_total (자동차등록): 통계누리 CSV 형식 깨짐 + 등록대수=노출 변수
- ❌ KOSIS DT_11001N_2013_A054 (폐기물), A033 (자동차) 등 한국도시통계 → 일반 KOSIS API 미지원
