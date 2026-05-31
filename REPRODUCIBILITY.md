# 재현성 가이드 (Reproducibility)

> 논문(`paper/main_v2.typ`)·슬라이드의 모든 정량 주장을 *주장 → 분석 스크립트 → 데이터 → 그림*으로 추적하는 색인.
> 특정 수치(예: "RDD 자산취득형 3.42배")의 출처를 확인하려면 해당 테마 표에서 분석 스크립트와 입력 CSV를 찾으면 된다.
> (스크립트 분류·status는 2026-05-31 전수 매핑 기준. 폴더 재배치는 §6 참조.)

---

## 0. 재현 파이프라인 — 3단계

```
[1 데이터]  OPEN API ──fetch_*/build_warehouse──▶  data/warehouse.duckdb (monthly_exec·indicator_panel)
[2 분석]    warehouse ──h*.py──▶                    data/results/H*.csv   (모든 추정치)
[3 그림]    H*.csv ──redo_fig*/build_slide*──▶      paper/figures/*.png   (논문·슬라이드 그림)
[4 문서]    figures + 수치 ──typst──▶                paper/main_v2.pdf
```

**백본 CSV**: `data/results/H3_activity_embedding_11y.csv` (← `scripts/h3_v2_11y.py`). 1,557 세부사업 × 12 피처 + cluster 라벨. **거의 모든 downstream 분석이 이 파일을 읽는다** → 재현 시작점.

**재현 명령 예시**:
```bash
pip install -r requirements.txt
# 1) 데이터 (API 키 .env 필요 — 이미 받은 warehouse.duckdb 있으면 생략 가능)
python scripts/build_warehouse.py && python scripts/fetch_monthly_exec.py && python scripts/fetch_monthly_exec_2015_2019.py
python scripts/build_indicator_panel.py
# 2) 분석 (예: RDD)
python scripts/h22_rdd_yearend.py        # → data/results/H22_rdd_estimates.csv
# 3) 그림
python scripts/redo_fig07_rdd.py         # → paper/figures/h22_rdd_monthly.png
```

---

## 1. 데이터 구축 (`0_data`)

| 단계 | 스크립트 | 출력 (warehouse 표) |
|---|---|---|
| API → warehouse | `build_warehouse.py` | expenditure_budget·item·revenue·debt·catalog |
| 월별 집행 (핵심) | `fetch_monthly_exec.py`(2020–26) + `fetch_monthly_exec_2015_2019.py` | **monthly_exec** (EP_AMT 월별집행, 2015–25, ~41만행) |
| outcome 패널 | `build_indicator_panel.py` + `fetch_kosis_catalog/outcomes.py`·`fetch_bok_macro.py`·`h7_outcome_load.py`·`h11`~`h21_*outcome.py` | **indicator_panel** (분야×연도 결과지표 + CPI 통제변수) |
| 데이터 카탈로그 | `fetch_kodas.py`·`fetch_specs.py`·`build_docs.py` | kodas_catalog·api_specs (§4 명세 부록) |

---

## 2. 주장·그림별 재현 사슬 (테마별)

### H1 — 분석 단위: 분야 trivial, 사업원형이 진짜 단위 (§6.1–6.2)
| 주장 / 그림 | 분석 스크립트 → CSV | 그림 스크립트 → PNG | 논문 |
|---|---|---|---|
| 4 archetype (UMAP+HDBSCAN), n=129/99/154/1175 | `h3_v2_11y.py` → `H3_activity_embedding_11y.csv`·`H3_cluster_profile_11y.csv` | `redo_fig01_umap.py` → `h3_umap.png` | §6.1, L683 |
| 분야 ΔR²=0.000 / 원형×Δamp +0.025 | `h8_v3_replaced.py` → `H8_field_archetype_decomp_v3.csv` | `redo_fig06_h8panel.py` → `h8_panel.png` | §6.1, L939 |
| TDA Mapper (10 comp) | `h4_v3_replaced.py` → `H4_cluster_outcome_corr_11y_v3.csv` | `redo_fig02_mapper.py` → `h4_mapper_*.png` | §6.2, L688 |
| PH (Wasserstein-2 p<0.0001) | `h9_v2_11y.py` → `H9_persistence_pairs_11y.csv` · `h9_v2_wasserstein.py` → `H9_v2_wasserstein.csv` · `h9_v2_loop_ids.py` | `redo_fig03_persistence.py` → `h9_pd/barcode/bootstrap.png` | §6.2, L698 |

### H2 — 회계연도 12월 RDD (§6.3, 부록 E)
| 주장 / 그림 | 분석 → CSV | 그림 → PNG | 논문 |
|---|---|---|---|
| **전체 1.91배 · 자산취득형 3.42배** | `h22_rdd_yearend.py` → `H22_rdd_estimates.csv`·`H22_field_rdd.csv` | `redo_fig07_rdd.py`→`h22_rdd_monthly/yearly` · `build_slide23_archetype_forest.py`→`h22_rdd_archetype_forest` | §6.3, L770·L1813 |
| cutoff 3·6·9·12월 (1.18/1.39/1.24/1.91) | `h22_quarterly_cutoffs.py` → `H22_quarterly_cutoffs.csv` | `build_slide_extras.py` → `fig_slide22_cutoff_bars` | §6.3·부록 E.1 |
| granularity S1–S4 (×1.85~4.10) | `h22_v2_granularity.py` → `H22_v2_granularity_brackets.csv` | (표) | 부록 E.2 |
| 견고성: bandwidth·placebo | `_bandwidth_sensitivity.py`·`_placebo_cutoff.py` (콘솔) | — | 부록 C.10 |

### H3 / H6 — 스펙트럼·시간 진화 (§6.4 / §6.8, 부록 D)
| 주장 / 그림 | 분석 → CSV | 그림 → PNG | 논문 |
|---|---|---|---|
| PSD k1 0.332 · phase coherence 0.54 | `h27_power_spectrum_coherence.py` → `H27_psd_archetype_avg.csv`·`H27_phase_distribution.csv`·`H27_coherence_intra_archetype.csv` | `redo_fig11_psd`·`redo_fig12_phase`·`redo_fig13_coherence` | §6.4, L1673·1687·1718 |
| **Wavelet +554%** (출연금형) | `h28_wavelet.py` → `H28_wavelet_12m_evolution.csv` | `redo_fig15_evolution.py`→`h28_evolution` · `redo_fig14_scaleogram.py`→`h28_scaleogram` | §6.8, L1005·1740 |
| Pre/COVID/Post 시기분할 | `h28_v2_period_split.py` → `H28_v2_period_split.csv` | (표) | §6.8.1·부록 D.4 |
| NeuralProphet cross-check | `h26_neuralprophet_check.py` → `H26_neuralprophet_summary.csv` | `build_slide29_np_forecast.py` → `h29_np_forecast` | §6.5, L859 |

### H4 — 매개분석 (§6.6, App-MED)
| 주장 / 그림 | 분석 → CSV | 그림 → PNG | 논문 |
|---|---|---|---|
| **농림수산 Sobel z=−2.897** (부트스트랩 미확증) | `h23_mediation.py` → `H23_mediation_estimates.csv` | `s33_forest_zsobel.py`·`build_slide33_sobel_bars.py` | §6.6 |

### H5 / §6.5 — outcome 상관·트라이앵귤레이션 (§6.5·6.7)
| 주장 / 그림 | 분석 → CSV | 그림 → PNG | 논문 |
|---|---|---|---|
| **사회복지 r=−0.86** (CPI 통제) | `h10_v3_replaced.py` → `H10_macro_control_corr_v3.csv` | `redo_fig05_cpi.py` → `h10_cpi_control.png` | §6.7, L934 |
| H5 강건성 (Spearman/Kendall/LOO) | `generate_v3_charts.py` (← `H10_v3_alt_correlations.csv`) | → `h10_v3_robustness.png` | §6.7, L967 |
| 견고성 (FE·permutation·lag) | `h6_v3_replaced.py` → `H6_*_v3.csv` | `redo_fig04_robustness.py` → `h6_robustness/lag_amp` | §6.6, L921 |
| STL 자기비판 | `h24_stl_decomp.py` → `H24_stl_metrics.csv`·`H24_h6_replication.csv` | `redo_fig09_stl.py` → `h24_stl_bars/scatter` | §6.9, L1112 |
| **15분야×3도구 트라이앵귤레이션** | `h26_neuralprophet_check.py` → `H26_field_outcome_corr_np.csv` | `build_slide30_triangulation.py` → `h30_triangulation.png` | §6.5.3, L869 |
| 부처×outcome 4분면 | `h5_v2_11y.py` → `H5_ministry_exposure_11y.csv` · `h14_v2_replaced.py` → `H14_*` | `redo_fig10_quadrant.py` → `fig_slide38_*` | §6.7·§7.1, L1154 |
| 시간진화 TDA | `h9_v3_time_evolution_tda.py` → `H3_yearly_embeddings.csv` | `generate_v3_charts.py` → `h9_v3_time_evo.png` | §6.10, L1044 |

### calibration / 보조
| w_t/w_q=0.75 calibration · ALIO | `generate_v3_charts.py` → `v3_calibration.png`·`v3_alio_grades.png` | §6.10·6.11, L1076·1093 |

---

## 3. 논문 그림 16종 ↔ 생성 스크립트 (1:1)

`scripts/redo_fig01..16_*.py`가 논문 본문 그림의 **정본 생성기**다(각 main_v2.typ `image()` 줄번호 매핑). 입력은 모두 `data/results/H*.csv`. 실행: `python scripts/redo_figNN_*.py` → `paper/figures/_preview/` 생성 후 `figures/` 승인 복사.

| fig | 스크립트 | 논문 figure |
|---|---|---|
| 01 | redo_fig01_umap | h3_umap |
| 02 | redo_fig02_mapper | h4_mapper_amp/cluster |
| 03 | redo_fig03_persistence | h9_pd/barcode/bootstrap |
| 04 | redo_fig04_robustness | h6_robustness/lag_amp |
| 05 | redo_fig05_cpi | h10_cpi_control |
| 06 | redo_fig06_h8panel | h8_panel |
| 07 | redo_fig07_rdd | h22_rdd_monthly/yearly |
| 08 | redo_fig08_field | h22_rdd_field |
| 09 | redo_fig09_stl | h24_stl_bars/scatter |
| 10 | redo_fig10_quadrant | fig_slide38_ministry_quadrant |
| 11–13 | redo_fig11/12/13 | h27_psd/phase/coherence |
| 14–15 | redo_fig14/15 | h28_scaleogram/evolution |
| 16 | redo_fig16_appendix | h22_rdd_appendix |
| (별도) | build_slide23/24·30·generate_v3_charts | h22_rdd_*_forest·h22_rdd_yearly·h30_triangulation·h10_v3_robustness·v3_* |

---

## 4. 슬라이드 그림 (논문과 분리)

슬라이드(figma SVG)용 그림은 `build_slide*.py`가 별도 생성(`paper/figures/eda/`·`paper/figures/slides/`). 논문 그림과 *입력 CSV는 같고 스타일만 다른* 변종이다 (commit 1e5337e "논문·슬라이드 분리"). 예: `build_slide28_evolution.py`(슬라이드) vs `redo_fig15_evolution.py`(논문).

---

## 5. ⚠️ 하드코딩 주의 (재현 불가 스크립트)

데이터를 안 읽고 값을 *손으로 박은* 스크립트 — 데이터가 바뀌어도 자동 갱신 안 됨:
- `build_overview_figma_slides.py` (slide-02 월별 막대 — **37.2% fan-out 버그값 박힘**, 정본 12.1%)
- `build_wireframes.py`(폐기)·`build_outcome_arc.py`·`build_app_wav_slides.py`·`build_slide21_rdd_concept.py`(개념도)
- → [슬라이드_수정사항.md](슬라이드_수정사항.md) 참조. 근본 해결: 빌더가 CSV에서 값을 읽도록 리팩터.

---

## 6. 폴더 구조 (적용 완료 — 2026-05-31)

`scripts/`를 **분석 단계별 하위 폴더로 재배치 완료**(128개 이동, branch `cleanup/scripts-reorg`). *경로만 봐도 어느 단계인지* 알 수 있다. 하위 폴더로 한 단계 깊어지며 깨지는 ROOT 경로(`dirname(dirname(...))`·`parents[1]`)는 89개 스크립트에서 +1 일괄 패치, `_env` import 4개는 `sys.path` shim 추가, `_env.py`만 공유 모듈로 `scripts/` 루트 유지. 논문은 `paper/figures/`(미이동)를 참조하므로 컴파일 영향 없음.

```
scripts/
├── 0_data/        # build_warehouse·fetch_*·build_indicator_panel·h7/h11-h21_outcome (21)
├── 1_eda/         # fig2-5·eda_goodhart.sql (5)
├── 2_archetype/   # h3_v2_11y·h5_v2_11y (H1 군집)
├── 3_rdd/         # h22_*·_bandwidth·_placebo·_cutoff (H2)
├── 4_spectral/    # h27_*·h28_*·h26_* (H3/H6/triangulation)
├── 5_mediation/   # h23_mediation (H4)
├── 6_outcome/     # h10_*·h6_*·h8_*·h24_*·generate_v3_charts (H5)
├── 7_tda/         # h9_*·h4_v3 (TDA)
├── 8_robustness/  # h4_v2_sensitivity 등
├── figures/       # redo_fig01..16 (논문 그림 정본)
├── slides/        # build_slide*·build_app*·build_overview·redo_slidefig* (슬라이드 그림)
├── _utils/        # _env·_downsample·_fix_tilde·_format_med·_mentoring_lookup·_audit/_check/_wf
└── _archive/      # superseded (아래)
```

**`_archive/`로 격리할 superseded (14)**: `build_report_figures.py`(analysis_report 삭제), `h10_replot.py`, `h3_activity_embedding.py`(5y 구판), `redo_fig01_umap_horizontal.py`, `build_slide34_agri_dual.py`(농가소득 역설 폐기), `build_slide_extras.py`(분리 빌더로 대체), `redo_slidefig_h27_psd/h28_evolution.py`(빈 타겟 폴더), 이미 `scripts/_archive/`에 있는 build_slide29_34·build_wireframes·h4_mapper_outcome·h9_persistent_homology 등.

> 재현 명령 경로는 이제 `python scripts/<테마>/<script>.py` 형식이다(예: `python scripts/3_rdd/h22_rdd_yearend.py`). 검증: py_compile 전체 통과 + 샘플 figure(`redo_fig07_rdd.py`) end-to-end 실행 + 논문 컴파일 통과 + `_env` import 정상. 논문 부록 G·이 문서도 갱신됨.
