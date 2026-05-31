# 값 계보 (PROVENANCE)

> 논문(`paper/main_v2.typ`)과 슬라이드(`figma_exports/`)에 등장하는 정량값이 *어느 원천에서 나오는지* 고정하는 단일 진실원천 표.
> **계기**: 2026-05 "12월 집행 비중 37.2%" 버그값이 보고서·슬라이드 여러 곳에 박혀, 원천(CSV) 수정 뒤에도 다운스트림 문서에 옛값이 남았던 사건. (상세: [`../슬라이드_수정사항.md`](../슬라이드_수정사항.md))
>
> **규칙**
> 1. 논문·슬라이드에 새 수치를 넣으면 *반드시* 이 표(또는 §1 그림 계보)에 행을 추가하고 원천을 명시한다.
> 2. ⚠️ 표시 빌더는 값을 **코드에 하드코딩**한다 — 원천 CSV가 바뀌어도 자동 갱신되지 않으므로, CSV를 고치면 빌더도 함께 고쳐야 한다(37.2% 버그의 직접 원인).
> 3. 원천 데이터 위치: `data/warehouse.duckdb`(표 `monthly_exec`, 2015–2026 약 41만 행) · `data/results/*.csv`(분석 산출) · `data/external/`(외부 지표).

---

## 0. 37.2% 사건 — 무엇이 틀렸고 무엇이 정본인가

초기 EDA 쿼리가 `activity_yearly`를 `GROUP BY (FSCL_YY, ACTV_CD, ACTV_NM)`로 묶고 JOIN은 `(FSCL_YY, ACTV_CD)`로만 해서, 한 `ACTV_CD`에 여러 `ACTV_NM`이 달린 활동(38.8%)에서 월 집행액이 **fan-out 중복 합산**됐다(12개월 비중 합 317%, 약 3배 부풀림). `scripts/fig2_monthly_exec.py`가 `GROUP BY (FSCL_YY, ACTV_CD)`로 고쳐 정본값을 낸다.

| 값 ID | 버그값 | **정본값** | 의미 | 원천 |
|---|---|---|---|---|
| `dec_share` | 37.2% | **12.1%** | 12월 정규화 집행 비중(각 사업 100% 정규화 후 월평균) | warehouse `monthly_exec` via `scripts/fig2_monthly_exec.py` |
| `nov_share` | 17.7% | **5.5%** | 11월 정규화 집행 비중 | 〃 |
| `ratio_dec_nov` | ×2.11 | **×2.2** | 12월/11월 배율 | 〃 |
| `eq_ratio` | 4.5배 | **약 1.5배** | 균등(8.33%) 대비 12월 배율 | 〃 |
| `dec_raw_amt_ratio` | — | **×1.52** | raw 금액가중 12월/11월 배율 | warehouse |

**slide-02 막대 12개월 정본 프로파일**(합 100%): `1월 8.8 · 2월 10.2 · 3월 12.9 · 4월 9.5 · 5월 7.1 · 6월 9.9 · 7월 6.7 · 8월 5.1 · 9월 6.4 · 10월 5.9 · 11월 5.5 · 12월 12.1`. → **3월(12.9) ≈ 12월(12.1) 쌍봉**이므로 "12월 단독 정점" 단정 회피(분기말 3·6·12 사이클 + 회계연도말).

### ⚠️ 버그값이 아직 살아있는 위치 (정정 대기 — SVG는 Figma에서 직접 수정)

| 파일 | 위치 | 비고 |
|---|---|---|
| `figma_exports/intro_sequence/slide-02-observation.svg` | L32 `17.7%` · L35 `37.2%` | **슬라이드 정본 — 무대 #1 위험.** 막대 높이도 12개월 재산정 필요 |
| `paper/재정데이터 분석 ppt/tokens.svg` | L116 `37.2` · L119 `17.7` | 디자인 토큰 SVG의 KPI 예시값 |
| `scripts/build_overview_figma_slides.py` | L148 `vals=[...,17.7,37.2]` · L156 `annot` | figma overview 막대 빌더 하드코딩 |

> 옛 `build_wireframes.py`의 버그값은 스크립트가 `scripts/_archive/`로 격리되며 함께 비활성화됨.
> 논문(`main_v2.typ`)·스토리보드 본문은 정정 완료. 위 3곳은 *값 교체*만 남았다(구조 변경 아님).

---

## 1. 그림 → 빌더 → 분석 스크립트 → CSV 계보 (논문 참조 33개)

`paper/main_v2.typ`이 참조하는 그림 전부. 빌더를 다시 돌릴 땐 *source 스크립트가 만든 CSV*가 최신인지 먼저 확인.
CSV 경로는 별도 표기 없으면 `data/results/` 기준. `HC=⚠️`는 빌더가 일부 수치를 하드코딩(폴백 beta·라벨 n수·행렬 등) — §3 참조.

| 그림 (`paper/figures/`) | 빌더 스크립트 | source 분석 | 읽는 CSV | HC |
|---|---|---|---|---|
| `eda/fig_slide22_cutoff_bars.png` | `build_slide_extras.py` | h22_quarterly_cutoffs.py | H22_quarterly_cutoffs.csv | |
| `eda/fig_slide38_business_quadrant.png` | **NOT_FOUND (수동 생성)** | — | (warehouse) | ⚠️ |
| `eda/fig_slide38_ministry_quadrant.png` | `redo_fig10_quadrant.py` | h14_v2_replaced.py | H5_ministry_exposure_11y.csv · H3_activity_embedding_11y.csv | ⚠️ |
| `h10_cpi_control.png` | `h10_replot.py` | h10_v3_replaced.py · h10_macro_control.py | H10_macro_control_corr_v3.csv | |
| `h10_v3_robustness.png` | `generate_v3_charts.py` | — | H10_v3_alt_correlations.csv · H10_v3_socialwelfare_loo.csv | ⚠️ |
| `h14_quadrant.png` | `redo_slidefig_h14_quadrant.py` | h14_v2_replaced.py | H5_ministry_exposure_11y.csv · H3_activity_embedding_11y.csv | ⚠️ |
| `h22_rdd_appendix.png` | `redo_fig16_appendix.py` | h22_rdd_yearend.py | H22_field_rdd.csv · H22_rdd_estimates.csv | |
| `h22_rdd_archetype_forest.png` | `build_slide23_archetype_forest.py` | h22_rdd_yearend.py | H22_field_rdd.csv · H22_rdd_estimates.csv | ⚠️ |
| `h22_rdd_field.png` | `build_report_figures.py` | h22_rdd_yearend.py | H22_field_rdd.csv | ⚠️ |
| `h22_rdd_field_forest.png` | `build_slide23_field_forest.py` | h22_rdd_yearend.py | H22_field_rdd.csv · H22_rdd_estimates.csv | ⚠️ |
| `h22_rdd_monthly.png` | `redo_fig07_rdd.py` | h22_rdd_yearend.py | H22_rdd_estimates.csv (+ warehouse) | |
| `h22_rdd_yearly.png` | `build_slide24_yearly.py` | h22_rdd_yearend.py | H22_rdd_estimates.csv (+ warehouse) | ⚠️ |
| `h24_stl_bars.png` | `redo_fig09_stl.py` | h24_stl_decomp.py | H24_h6_replication.csv | |
| `h24_stl_scatter.png` | `redo_fig09_stl.py` | h24_stl_decomp.py | H24_h6_replication.csv | ⚠️ |
| `h27_coherence.png` | `build_report_figures.py` | h27_power_spectrum_coherence.py | H27_coherence_intra_archetype.csv | ⚠️ |
| `h27_phase.png` | `redo_fig12_phase.py` | h27_power_spectrum_coherence.py | H27_phase_distribution.csv | ⚠️ |
| `h27_psd.png` | `build_slide27_psd.py` | h27_power_spectrum_coherence.py | H27_psd_archetype_avg.csv | |
| `h28_evolution.png` | `build_slide28_evolution.py` | h28_wavelet.py | H28_wavelet_12m_evolution.csv | |
| `h28_scaleogram.png` | `build_slide28_scaleogram.py` | (h28 계열) | H3_activity_embedding_11y.csv (+ warehouse) | |
| `h29_np_forecast.png` | `build_slide29_np_forecast.py` | (NeuralProphet) | H3_activity_embedding_11y.csv (+ warehouse) | ⚠️ |
| `h30_triangulation.png` | `build_slide30_triangulation.py` | h26_neuralprophet_check.py | H26_field_outcome_corr_np.csv | ⚠️ |
| `h3_umap.png` | `build_report_figures.py` | h3_v2_11y.py | H3_activity_embedding_11y.csv | ⚠️ |
| `h4_mapper_amp.png` | `redo_fig02_mapper.py` | h4_v3_replaced.py | H3_activity_embedding_11y.csv | |
| `h4_mapper_cluster.png` | `redo_fig02_mapper.py` | h4_v3_replaced.py | H3_activity_embedding_11y.csv | ⚠️ |
| `h6_lag_amp.png` | `redo_fig04_robustness.py` | h6_robustness.py | H6_fe_regression · H6_permutation_pvals · H6_lag_lead_corr · H6_natural_vs_gaming | |
| `h6_robustness.png` | `redo_fig04_robustness.py` | h6_robustness.py | (위 4종 동일) | |
| `h8_panel.png` | `build_report_figures.py` | h8_v3_replaced.py | H8_field_archetype_decomp_v3.csv | ⚠️ |
| `h9_barcode.png` | `redo_fig03_persistence.py` | h9_v2_11y.py | H3_activity_embedding_11y.csv · H9_persistence_pairs_11y.csv | |
| `h9_bootstrap.png` | `redo_fig03_persistence.py` | h9_v2_11y.py | H3_activity_embedding_11y.csv · H9_persistence_pairs_11y.csv | ⚠️ |
| `h9_pd.png` | `redo_fig03_persistence.py` | h9_v2_11y.py | H3_activity_embedding_11y.csv · H9_persistence_pairs_11y.csv | ⚠️ |
| `h9_v3_time_evo.png` | `generate_v3_charts.py` | h9_v3_time_evolution_tda.py | H9_v3_topology_wavelet_alignment.csv | |
| `v3_alio_grades.png` | `generate_v3_charts.py` | — | `data/external/v3_micro_eval_alio.csv` | ⚠️ |
| `v3_calibration.png` | `generate_v3_charts.py` | — | v3_calibration_wt_wq_ratios.csv | ⚠️ |

> 빌더 경로는 모두 `scripts/` 기준. `build_report_figures.py`는 옛 `analysis_report.typ` 전용이라 `scripts/_archive/`로 격리됨 — 위 그림(h22_rdd_field·h27_coherence·h8_panel·h3_umap)은 동일 데이터를 읽는 active 빌더(`redo_fig*`·`build_slide*`)가 `paper/figures/`의 정본을 생성한다. 자세한 중복 빌더 관계는 워크플 provenance 노트 참조.

---

## 2. 정본 수치 레퍼런스 (검증 통과 — 그대로 사용)

전 정량값 전수 검증(107 ok / 25 mismatch / 6 unverifiable) 후 *통과분*. 논문은 이 값들로 정정 완료.

| 값 | 정본 | 원천 |
|---|---|---|
| RDD 전체 / C1자산취득 / C3정상 / C0인건비 / C2출연금 | 1.91 / 3.42 / 2.24 / 1.12 / 1.10(ns) | `H22_rdd_estimates.csv` · `H22_field_rdd.csv` |
| cutoff 3·6·9·12월 | 1.18 / 1.39 / 1.24 / 1.91 | `H22_quarterly_cutoffs.csv` |
| Wavelet 진폭변화 C2 / C3 / C1 / C0 | +554% / +314% / +174% / −1.4% | `H28_wavelet_12m_evolution.csv` |
| PSD 0.332 · coherence 0.54 | 일치 | `H27_*` |
| 농림수산 매개 Sobel z=−2.897, p=0.004, 부트스트랩 미확증, n=5 | 일치 | `H23_mediation_estimates.csv` |
| 사회복지 r=−0.86(CPI통제) / −0.762(raw) | 일치 | `H10_*` |
| 군집 n: C0 129 / C1 99 / C2 154 / C3 1175 | 일치 | `H3_activity_embedding_11y.csv` |
| 분위 12월 Q1 15.4%(×2.58) / Q4 10.9%(×1.86) | 일치 | warehouse |
| ΔR² 분야 0.000 / 원형×Δamp +0.025 | 일치 | `H8_field_archetype_decomp_v3.csv` |
| 미국 RDD 배수(Liebman-Mahoney 2017) | ×4.9 (β≈1.59) | 원천 보고값 (≠ ×5.0) |
| FIS 22-03 주요 불용 29.3% · 2,389개 | 일치 | 원천 PDF |

> **강한 매개 분야는 농림수산**(사회복지 아님). 슬라이드·문서에서 사회복지로 적힌 곳 발견 시 정정.

---

## 3. 하드코딩 차트 — stale 위험 추적 (37.2%와 같은 부류)

matplotlib 차트 대부분은 CSV/warehouse를 읽어 계산값을 그리므로 안전. 그러나 **figma SVG 빌더와 일부 슬라이드 빌더는 값을 코드에 박아둔다** — 데이터가 바뀌어도 자동 갱신 안 됨.

- **데이터 미연결(하드코딩) figma 빌더**: `build_overview_figma_slides.py` · `build_outcome_arc.py` · `build_app_wav_slides.py` · `build_data_spec_slides.py`.
- **부분 하드코딩(폴백/라벨)**: §1 표의 ⚠️ 행. 대표적으로 `build_slide23/24_*`의 `korea_beta=0.6477` 폴백·`LM_MULT=5.0`·archetype n수 라벨.

### ❗ 미해결 — `h30_triangulation.png` (논문 §6.5.3)
1. **하드코딩 값 오류** (`build_slide30_triangulation.py`): FFT/PSD 행 `[0.097,0.172,0.332,0.115]` → 정본(`H27_psd_archetype_avg.csv`) `[0.097,0.155,0.332,0.172]`. wavelet 행도 미세 차.
2. **그림-텍스트 불일치**: 본문은 "14분야×3도구 outcome 상관"을 말하나 그림은 "3도구×4 archetype 진폭". 어느 그림을 둘지 결정 필요(상세 [`../슬라이드_수정사항.md`](../슬라이드_수정사항.md) §P3).

> **근본 해결 방향**: 하드코딩 빌더를 *CSV에서 값을 읽도록* 리팩터. 그 전까지는 위 ⚠️ 값을 §2 정본 레퍼런스와 1:1 대조할 것.
