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
| `eda/fig_slide38_business_quadrant.png` | `redo_fig10b_business_quadrant.py` | h3/h5/h10 결합 | H3_activity_embedding_11y.csv · H5_ministry_exposure_11y.csv · H10_macro_control_corr_v3.csv | |
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
| `h28_evolution.png` | `redo_fig15_evolution.py`(논문) | h28_wavelet.py | H28_wavelet_12m_evolution.csv | |
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
> **슬라이드용 H28 진화 차트는 별도**: `build_slide28_evolution.py` → `paper/figures/slides/h28_evolution.png` (발표 가독성용 가로형·외부 legend, Figma 플레이스홀더 자산). 논문용(`redo_fig15`)과 출력 경로·레이아웃 분리 — 서로 덮어쓰지 않는다.


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

### 트라이앵귤레이션 — 두 종류 구분 (2026-05-31 정정)

이전 메모가 **서로 다른 두 그림을 혼동**했음. 명확히 구분:

1. **`h30_triangulation.png` (논문 §6.5.3)** — `build_slide30_triangulation.py`가 `H26_field_outcome_corr_np.csv`에서 읽는 **15분야 × 3도구 outcome 상관 heatmap**. CSV 기반·정상. (이전 메모의 "build_slide30이 `[0.097,0.172,…]` 하드코딩"은 오기 — 그 매트릭스는 아래 ②다.)
2. **`paper/figures/slides/triangulation_archetype.png` (슬라이드 전용, 신규)** — `build_slide_triangulation_archetype.py`가 만드는 **3도구 × 4 archetype 매트릭스**(FFT 12m PSD · Wavelet 시간강화 · NP seasonality). FFT행=`H27_psd_archetype_avg.csv`(12m=`psdnorm_k1`), Wavelet행=`H28_wavelet_12m_evolution.csv` window 배율에서 **직접 읽어** 생성. 옛 figma 하드코딩 오류(FFT C1 0.172→**0.155**, C3 0.115→**0.172**)를 CSV 기반으로 정정. 정본: FFT `[0.097,0.155,0.332,0.172]` · Wavelet `[0.99,2.74,6.54,4.14]`. NP행 `[0.274,0.281,0.458,0.390]`만 추적 CSV 없어 하드코딩+주석 유지(C2 최댓값이라 메시지 보존). 세 행 모두 C2 출연금형 최강.

> ⚠️ **figma 직접 수정 대기**: ②의 옛 하드코딩 값은 `build_app_wav_slides.py`의 App-WAV 부록 SVG 표·figma 슬라이드에도 남아 있다(스크립트가 CSV 미연결). before→after는 [`../슬라이드_수정사항.md`](../슬라이드_수정사항.md) 참조. 새 `triangulation_archetype.png`를 figma 플레이스홀더에 교체 투입하면 ②는 해소.

> **근본 해결 방향**: 하드코딩 빌더를 *CSV에서 값을 읽도록* 리팩터. 그 전까지는 위 ⚠️ 값을 §2 정본 레퍼런스와 1:1 대조할 것.

---

## H2 RDD placebo (마감 vs 비마감 월전이) — 2026-06 추가

- **원천 스크립트**: `scripts/h22_placebo_months.py` → 산출 `data/results/H22_placebo_months.csv`, 요약 `data/results/H22_placebo_summary.txt`
- **입력**: `warehouse.duckdb::monthly_exec` (2015~2025, 전체 활동 ACTV_CD, EP_AMT 월별 집행액). 활동×연도 월 daily-avg(=EP_AMT/월일수)의 m/m-1 로그비, exp(평균)=배수.
- **논문 인용값(conference_v1.typ §Ⅴ.2)**: 12/11=1.94(표 4의 전체 1.91과 정합), 마감월 평균 1.47, **비마감월 7개 중 6개 <1.0·중앙값 0.82**, 유일 예외 1→2월=1.62(1월 저집행 기저효과).
- **용도**: 12월 점프가 계절성이 아니라 회계연도·분기 마감 제도효과임을 placebo로 입증.

---

## 식별 견고성 검증 (C4·C7·C6) — 2026-06-04 추가

논리 감사(커밋 90ab5fa)가 §8.2에 인정한 세 식별 결함을 데이터로 직접 검정. 결과는 §6 "식별 견고성 검증" 절 + §8.2 해당 3항 갱신. **정직성 원칙: 결함 "해소"가 아니라 "심각도 정량화" — 셋 다 부분 완화 + 잔존.** 적대적 검증 4-에이전트(workflow)가 전 수치 재현 확인 + 과대해석 교정.

- **C4 군집 순환성** — `scripts/2_archetype/robust_c4_recluster.py` → `robust_c4_recluster_ari.csv`·`_gaming_by_cluster.csv`, 로그 `_robust_c4_log.txt`. 입력 `H3_activity_embedding_11y.csv`(12피처+cluster). ARI: 편성목4-only 0.895 / 비게임화6 0.369 / 게임화6 0.018 / UMAP+HDBSCAN6 0.344 / 전체12 0.263. 그림 `figures/robust_c4_recluster.png`.
- **C7 층 직교성** — `scripts/2_archetype/robust_c7_orthogonality.py` → `robust_c7_field_archetype_pct.csv`·`_ep_pct.csv`·`_association_stats.csv`, 로그 `_robust_c7_log.txt`. χ²=251.6 p<1e-29; 보정 Cramér V 활동수 0.21·EP가중 0.51·비C3 0.38; NMI 0.042. 그림 `figures/robust_c7_field_archetype.png`.
- **C6 사회복지 시점 외생성** — `scripts/2_archetype/robust_c6_socialwelfare.py` → `robust_c6_field_dec_share.csv`·`_monthly_profile.csv`·`_dec_nov_ratio.csv`, 로그 `_robust_c6_log.txt`. 입력 `warehouse.duckdb::monthly_exec`. 사회복지 12월 비중 중앙 7.8%(균등 이하), 12월/11월 일평균 배율 1.29배(14분야 최저), 월 표준편차 1.9%p. 그림 `figures/robust_c6_socialwelfare.png`.

### ★ §6.1 EDA 분야 12월 비중 수치 정정 (재현 불가 값 교체)
- **종전(오류)**: "통일·외교 100.0% vs 사회복지 13.4%, 7.5배 격차, IQR 평균 83%p·중앙 91%p".
- **정정(재현값, fig3 정의 = 활동×연도·연집행 1억 초과·12월/연집행·cap 1.0·분야 median)**: 국방 17.0%(최고)·통일외교 13.4%·사회복지 7.8%(균등 8.3% 이하)·교육 0.9%(최저); 분야 내 IQR 평균 ≈15%p.
- **오류 원인**: 종전 100%는 단일 활동(2016 민간협력차관)의 *최댓값*이며, 13.4%는 사실 통일·외교의 중앙값(사회복지와 뒤바뀜). IQR 83~91%p는 EP_AMT 음수(0.46%)·미필터·cap 조합의 0/100 양극화 artifact로, 7가지 대안 정의 어디서도 재현 불가.
- **하드코딩 정정**: `scripts/_archive/build_wireframes.py` L382-383 (통일·외교 100%→국방 17.0%, 사회복지 13.4%→7.8%). ⚠️ `paper/conference_v1.typ`에도 동일 옛 수치 잔존 — 별도 정정 필요(이번 작업 범위 외, main_v2.typ만 정정).
