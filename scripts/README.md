# scripts/

분석·시각화 스크립트 모음. 최종 산출물(`paper/main_v2.typ` 논문 · `figma_exports/` 슬라이드)을
만드는 데 **현재 쓰이는** 스크립트만 이 폴더에 두고, 대체·폐기된 것은 `_archive/`로 격리한다.
(현재 active 146개 · 격리 20개)

## 명명 규칙

| 접두 | 역할 | 출력 |
|---|---|---|
| `h{N}_*` | 가설/분석 단위 | `data/results/*.csv` (warehouse 쿼리 → 분석값) |
| `redo_fig*` | 논문 그림 재생성 (paper-style, A4 가이드) | `paper/figures/` (대개 `_preview/` 경유) |
| `build_slide*` · `build_*` | 슬라이드/figma 자산 빌더 | `paper/figures/`, figma용 PNG·SVG |
| `fetch_*` | 외부 지표 수집 (KOSIS·ECOS·GIR 등) | warehouse / `data/external/` |
| `generate_v3_charts.py` · `build_report_figures.py`* | 다중 그림 일괄 빌더 | `paper/figures/`, `paper/figures_en/` |

(*`build_report_figures.py`는 옛 `analysis_report.typ` 전용이라 `_archive/`로 이동됨.)

## `_archive/` — 격리된 스크립트 (참고 보존, 재실행 대상 아님)

대체·폐기됐지만 이력 보존을 위해 git에 남긴 20개. 2026-05-31 구조 정리에서 이동.
판정 기준: **논문이 참조하는 33개 그림의 빌더·소스 사슬에 들지 않고**(워크플 provenance 역추적),
더 새 버전이 존재하거나 어디서도 산출물이 안 쓰임 + active 스크립트가 import하지 않음(전수 확인).

- **단계적 대체 (구버전 분석)** — `h1_mechanism_full`(→`h3_v2_11y`·`h6_robustness`) · `h13_ict_outcome`(→`h20_broadband_outcome`) · `goodhart_freq`(→`h27_power_spectrum_coherence`) · `load_kosis_outcomes`(→`h7_outcome_load`) · `plot_h2_results`(→`h6_robustness`)
- **AI 지출 탐색 — Goodhart-RDD로 전환되며 폐기** — `analyze_ai_item` · `deep_ai_analysis` · `plot_ai_breakdown` · `probe_ai_spending`
- **1회성/탐색·미연결** — `eda`(warehouse 탐색) · `build_dashboard_mockup`(목업 PNG, 논문 미참조) · `build_docs`(mkdocs 생성) · `fetch_data_go_kr`(placeholder API) · `fetch_nara_g2b`(키 필요, 미사용)
- **폐기 슬라이드 덱 전용 빌더** — `build_wireframes`(→`build_overview_figma_slides`) · `build_ppt_assets`(→`build_slide_extras`) · `build_slide28_scaleogram_postprocess`(→`build_slide28_scaleogram`) · `build_slide29_34`(→`build_slide29_np_decomposition`·`build_slide34_*`) · `slides_figs_new`
- **미사용 그림 변형** — `redo_fig01_umap_horizontal`(`h3_umap_h.png` 가로형 — 논문 미참조)

> ⚠️ 주의: 파일명의 `_replaced` 접미는 **outcome 변수만 교체한 최종본** 표기이지 폐기가 아니다.
> `h4_v3_replaced` · `h6_robustness`(구 `h6_v3_replaced` 후속) · `h8_v3_replaced` · `h10_v3_replaced` · `h14_v2_replaced`는
> 모두 **active**이며 논문 부록 스크립트 표에 등재돼 있다. (그래서 `_archive`로 옮기지 않았다.)

## 값 계보(provenance)

각 그림이 어느 빌더 → 어느 분석 스크립트 → 어느 CSV에서 나오는지는 [`../data/PROVENANCE.md`](../data/PROVENANCE.md) 참조.
새 수치를 논문·슬라이드에 넣을 땐 그 표에 행을 추가하고 원천을 명시할 것.
