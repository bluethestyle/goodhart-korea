# MANIFEST — 외부 데이터 raw 캐시 재현 가이드

> **단축 경로**: `data/warehouse.duckdb` (56MB)는 git에 트랙되어 있습니다. clone만으로 모든 분석을 재실행할 수 있습니다 — 아래 fetch 단계는 *raw 데이터를 새로 받고 싶을 때만* 필요합니다.

본 폴더의 raw 데이터는 모두 warehouse.duckdb로 적재 완료된 상태이므로 git에서 제외(`.gitignore`)되었습니다. 새로 받아야 하는 경우 아래 fetch 명령으로 재생성하세요. 모든 명령은 repo 루트에서 실행합니다.

자세한 출처·시계열·지표 정의는 [SOURCES.md](SOURCES.md) 참조.

---

## 사전 조건: API 키 (.env, gitignored)

```bash
# .env (repo 루트)
OPENFISCAL_KEY=...        # https://www.openfiscaldata.go.kr/
KOSIS_KEY=...             # https://kosis.kr/openapi/
BOK_KEY=...               # https://ecos.bok.or.kr/
DATA_GO_KR_KEY_ENC=...    # https://www.data.go.kr/ (URL-encoded)
DATA_GO_KR_KEY_DEC=...    # 동일 decoded
```

---

## kosis_data/ — KOSIS 12분야 outcome (30MB, ~14 JSON)

KOSIS_KEY 등록 후:

```bash
python scripts/fetch_kosis_outcomes.py    # 전 분야 outcome 검색·캐시
python scripts/load_kosis_outcomes.py     # 보건/관광/산업 적재
python scripts/h7_outcome_load.py         # 교육/국토/행정/농림 추가 적재
```

생성 파일:
- `welfare_gini.json` 사회복지 순자산 지니계수 (DT_1HDAAD04)
- `life_expectancy.json` 보건 0세 기대여명 (DT_1B41)
- `industrial_production.json` 산업 전산업생산지수 (DT_1JH20201)
- `tourists.json` 문화관광 (DT_113_STBL_1027329)
- `private_edu.json` 교육 사교육 시간 (DT_1PE103)
- `housing_supply.json` 국토 주택보급률 (DT_MLTM_2100)
- `local_tax.json` 일반·지방행정 (DT_11001N_2013_A012)
- `farm_income.json` 농림수산 농가소득 (DT_1EA1501)
- `rd_total.json` / `rd_total_long.json` 산업R&D비 (DT_1EP1322)
- `grdp_national.json` / `grdp_total.json` GRDP
- `fishery_income.json` 수산소득
- `life_exp_sido.json` 시도별 기대여명

## kosis_meta/ — KOSIS 카탈로그 (23MB)

```bash
python scripts/fetch_kosis_catalog.py   # 카탈로그 트리 전체 (~64,996 통계표)
python scripts/h7_outcome_discovery.py  # outcome 후보 식별 → CSV 출력
```

생성:
- `kosis_catalog_export.tsv` 통계표 마스터
- `H7_outcome_candidates.csv` / `_overlap.csv` 후보 식별
- `H7_outcome_metadata.csv` 메타 정보

## bok_data/ — 한은 ECOS (129KB)

BOK_KEY 등록 후:

```bash
python scripts/fetch_bok_macro.py   # CPI 901Y009 + ICT 200Y158 자동 fetch
python scripts/h13_ict_outcome.py   # ICT 부가가치 적재
```

생성:
- `cpi_annual.json` 소비자물가지수 1990\~2025
- `ict_value_added.json` 정보통신산업 부가가치 1995\~2025
- `exchange_rate.json` 원/달러 환율 (보조)

## data_go_kr/ — 공공데이터포털 (1.1MB)

DATA_GO_KR_KEY 등록 후:

```bash
python scripts/h11_traffic_outcome.py   # 도로교통공단 lgStat 2015~2025
```

생성: `traffic_2015.json` \~ `traffic_2025.json` (연도별), `traffic_national_yearly.csv` 통합

## molit/ — 국토교통부 자동차등록 (5.9MB, 보류 분야)

수동 다운로드 (warehouse 미적재, 분석 보류):

링크: [통계누리 자동차등록현황](https://stat.molit.go.kr/portal/cate/statView.do?hRsId=68)
→ "시도별" 시계열 4개 분기 (201101\~201512, 201601\~202012, 202101\~202512, 202601\~202603) 각각 CSV 다운로드 → 본 폴더 저장

본 데이터는 자동차등록이 *교통 outcome으로 부적합*(노이즈 변수)으로 판정되어 **분석에서 제외**했습니다. SOURCES.md II절 참조.

생성: `motor_registration_*.csv` 4개 + 변환 결과 2개

## gir/ — GIR 국가 온실가스 인벤토리 (48KB) ★ 수동 다운로드

```
https://www.gir.go.kr/  →  국가 인벤토리 → 1990~2023 → 분야별 배출량 CSV 다운로드
또는 https://www.data.go.kr/data/15049589/fileData.do redirect
```

생성: `ghg_inventory_1990_2023.csv` (34년 시계열)

이 파일은 *공식 API가 없어 수동 다운로드만 가능*하므로 **유실 시 재획득 필요**. 영구 archive 권장.

```bash
python scripts/h12_ghg_outcome.py   # 위 CSV를 indicator_panel에 적재
```

---

## data/budget/raw/ — OpenFiscal API (557MB)

OPENFISCAL_KEY 등록 후:

```bash
python scripts/fetch_specs.py                     # API 명세 167건
python scripts/fetch_kodas.py                     # KODAS 카탈로그 1,707건
python scripts/fetch_monthly_exec.py              # VWFOEM 2020~2026 월별 집행 (★ 게임화 측정 입력)
python scripts/fetch_monthly_exec_2015_2019.py    # 2015~2019 확장
```

생성 (각 폴더는 7개 OpenFiscal 엔드포인트별):
- `VWFOEM/` 월별 집행 (★ 본 연구 핵심)
- `ExpenditureBudgetAdd7/`, `ExpenditureBudgetAdd8/` 편성목·집행목
- `BudgetRevenuesAdd2/` 세입예산
- `GovernmentDebtMonth/`, `GovernmentDebtYear/` 국가채무
- `codes/` 분류 코드

총 fetch 시간: 첫 빌드 30\~60분 (API 호출수 많음). 재실행 시 캐시 활용.

---

## warehouse 재구축

위 데이터를 모두 받은 뒤:

```bash
python scripts/build_warehouse.py        # DuckDB warehouse.duckdb 생성 (~10분)
python scripts/build_indicator_panel.py  # 분야×연도×지표 long-format 패널
```

이후 H1\~H26 분석 스크립트 실행 가능 ([README.md](../../README.md) 참조).

---

## 디스크 절약

raw 캐시는 모두 warehouse.duckdb로 적재됐으므로, 분석 재현이 끝났다면 안전하게 삭제 가능:

```bash
rm -rf data/budget/raw/                  # 557MB
rm -rf data/external/{kosis_data,kosis_meta,molit,data_go_kr,bok_data}/  # ~60MB
# data/external/gir/는 수동 다운로드만 가능하므로 보존 권장
```

warehouse만 있으면 모든 분석은 재실행 가능합니다.
