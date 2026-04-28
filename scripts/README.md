# Scripts 분류

총 59개 스크립트, 4그룹.

---

## 1. 환경 / 데이터 수집 (`fetch_*`, `load_*`)

| 스크립트 | 역할 | 키 |
|---|---|---|
| `_env.py` | `.env` 자동 로드 (의존성 없음) | — |
| `fetch_specs.py` | 열린재정 OPEN API 명세 167건 | OPENFISCAL |
| `fetch_kodas.py` | KODAS 카탈로그 1,707건 | OPENFISCAL |
| `fetch_monthly_exec.py` | VWFOEM 월별집행 2020~2026 (★ 게임화 측정 입력) | OPENFISCAL |
| `fetch_monthly_exec_2015_2019.py` | 2015~2019 확장 | OPENFISCAL |
| `fetch_kosis_catalog.py` | KOSIS 통계표 트리 64,996 | KOSIS |
| `fetch_kosis_outcomes.py` | KOSIS outcome 키워드 검색 | KOSIS |
| `load_kosis_outcomes.py` | 보건/관광/산업 outcome 적재 | KOSIS |
| `fetch_bok_macro.py` | 한은 ECOS CPI/ICT | BOK |
| `fetch_data_go_kr.py` | 공공데이터포털 4 API 점검 | DATA_GO_KR |
| `fetch_nara_g2b.py` | 나라장터 (보조) | — |
| `fetch_monthly_exec.py` (재실행) | 동일 | — |

## 2. Warehouse / 도구 (`build_*`, `query_*`, `probe_*`)

| 스크립트 | 역할 |
|---|---|
| `build_warehouse.py` | DuckDB warehouse 빌드 |
| `build_indicator_panel.py` | 분야×연도×지표 long-format |
| `build_docs.py` | OPEN API 명세 마크다운 변환 |
| `query_warehouse.py` | 임시 쿼리 도구 |
| `probe_ai_spending.py`, `analyze_ai_item.py`, `deep_ai_analysis.py`, `plot_ai_breakdown.py`, `eda.py`, `eda_goodhart.sql`, `goodhart_freq.py` | 초기 EDA (Goodhart 가설 탐색) |

## 3. 가설별 분석 (`h{N}_*`)

### 핵심 회귀 (H1~H2)
| 스크립트 | 역할 |
|---|---|
| `h1_mechanism_full.py` | 출연금 → 게임화 회귀 (β=+0.375, p=0.005) |
| `h2_decoupling_test.py` | 분야 단위 디커플링 |

### 활동 임베딩 (H3, H4)
| 스크립트 | 역할 |
|---|---|
| `h3_activity_embedding.py` | UMAP+HDBSCAN 5y baseline (3 archetype) |
| `h3_v2_11y.py` | 11y 재추출 (4 archetype 신규 분리) ★ |
| `h4_mapper_outcome.py` | Mapper TDA 5y |
| `h4_v2_11y.py` | Mapper 11y |
| `h4_v3_replaced.py` | Mapper 11y + 교체 outcome ★ |

### 부처 그래프 (H5)
| 스크립트 | 역할 |
|---|---|
| `h5_ministry_archetype.py` | Spectral Co-clustering 5y |
| `h5_v2_11y.py` | 11y (CC4 자산취득 신규) ★ |

### 견고성 (H6, H8)
| 스크립트 | 역할 |
|---|---|
| `h6_robustness.py` | FE/permutation/lag/cv ★ |
| `h6_v3_replaced.py` | 교체 outcome 재실행 |
| `h8_within_field.py` | 분야 trivial 검증 5y |
| `h8_v2_11y.py` | 11y |
| `h8_v3_replaced.py` | 11y + 교체 outcome ★ |

### outcome 발굴 + 적재 (H7, H11~H21)
| 스크립트 | 역할 |
|---|---|
| `h7_outcome_discovery.py` | KOSIS 카탈로그 outcome 후보 발굴 |
| `h7_outcome_load.py` | 교육/국토/행정/농림 적재 |
| `h11_traffic_outcome.py` | 도로교통공단 |
| `h11_load_motor_csv.py` | 자동차등록 (보류) |
| `h12_ghg_outcome.py` | GIR 온실가스 |
| `h13_ict_outcome.py` | 한은 ICT |
| `h14_exposure_outcome.py` | 부처 노출 × outcome 4분면 |
| `h14_v2_replaced.py` | 교체 outcome ★ |
| `h15_oda_outcome.py` | ODA |
| `h16_crime_outcome.py` | 범죄 |
| `h17_defense_outcome.py` | 방산경영 (보류) |
| `h18_patent_outcome.py` | 특허 (과기 교체) ★ |
| `h19_tourism_finance_outcome.py` | 관광/재정자립 (교체) ★ |
| `h20_broadband_outcome.py` | 초고속인터넷 (통신 교체) ★ |
| `h21_imd_defense_outcome.py` | IMD 교육 (교체) ★ |

### TDA (H9), CPI 통제 (H10)
| 스크립트 | 역할 |
|---|---|
| `h9_persistent_homology.py` | PH 5y |
| `h9_v2_11y.py` | PH 11y ★ |
| `h10_macro_control.py` | CPI 외생 통제 ★ |
| `h10_v3_replaced.py` | 교체 outcome 재실행 |

### 인과 식별 (H22~H24)
| 스크립트 | 역할 |
|---|---|
| `h22_rdd_yearend.py` | 회계연도 RDD (한국판 Liebman-Mahoney) ★ |
| `h23_mediation.py` | Baron-Kenny + Sobel 매개분석 ★ |
| `h24_stl_decomp.py` | STL trend 자기 비판 ★ |

### 시각화 (H25)
| 스크립트 | 역할 |
|---|---|
| `h25_export_viz_json.py` | 인터랙티브 viz용 JSON export |
| `plot_h2_results.py` | H2 plot (구) |

## 4. 사용 권장 워크플로우

### 새로 시작하는 경우
```
1) fetch_specs.py + fetch_kodas.py + fetch_monthly_exec*.py + load_kosis_outcomes.py + h{7,11~21}_*_outcome.py
2) build_warehouse.py + build_indicator_panel.py
3) h1, h2 (회귀)
4) h3_v2_11y.py (★ 임베딩)
5) h4_v3, h5_v2, h6, h8_v3, h9_v2, h10, h14_v2, h22, h23, h24 (분석)
6) h25 (viz JSON export)
```

### ★ 표시 = 최신/권장 버전 (v3, v2 등)
구 버전(`*_baseline`, `h3_activity_embedding`, `h4_mapper_outcome` 등)은 변경 추적·재현용으로 보존.
