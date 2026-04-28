# 분석 산출 CSV 인덱스

## 가설별 산출

### H1 — 출연금→게임화 메커니즘
- `H1_mechanism_panel.csv` — 분야별 회귀 패널 (N=90, β=+0.375 p=0.005)

### H2 — 분야 단위 디커플링
- `H2_correlation_summary.csv` — 분야별 amp_12m × outcome 상관
- `H2_panel_levels.csv` — 수준 패널
- `H2_panel_diff.csv` — 1차 차분 패널

### H3 — 활동 단위 임베딩 (5y)
- `H3_activity_embedding.csv` — 1,641 활동 × 12 피처 + UMAP + 클러스터
- `H3_cluster_profile.csv` — 1차 3 클러스터 z-score 프로파일
- `H3_field_x_cluster.csv` — 분야 × 클러스터 분포
- `H3_cluster2_subembedding.csv` — 정상사업 내부 15 sub
- `H3_ministry_community.csv` / `H3_ministry_community_v2.csv` — 부처 커뮤니티
- `H3_field_ks_amp12m.csv` — 분야 105 pair amp_12m KS

### H3 v2 — 활동 단위 임베딩 (11y)
- `H3_*_11y.csv` (위와 동일 구조) — 1,557 활동 × 4 cluster (자산취득형 신규 분리)

### H4 — Mapper(TDA) + 활동 단위 outcome
- `H4_mapper_nodes.csv` — Mapper 26 노드 메타
- `H4_cluster_outcome_corr.csv` — 클러스터별 outcome 차분 상관

### H5 — 부처 × 사업원형 이분그래프
- `H5_ministry_exposure.csv` — 부처별 굿하트 노출 점수 (51 부처)
- `H5_cocluster_assignment.csv` — Spectral Co-clustering 5개

### H6 — 견고성 검증
- `H6_fe_regression.csv` — FE 회귀 3개 모델 (N=14→65)
- `H6_permutation_pvals.csv` — 11분야 permutation p값
- `H6_lag_lead_corr.csv` — 분야×outcome × lag(-2..+2)
- `H6_natural_vs_gaming.csv` — 분야별 amp_12m 시간 cv
- `H6_ministry_outcome_corr.csv` — 부처 가중 outcome 상관

### H8 — 비판적 자기평가
- `H8_archetype_outcome.csv` — 분야×원형 outcome 결합 부호 (40 cells)
- `H8_field_archetype_decomp.csv` — R² 분해 (분야 FE → +원형 ΔR² = +0.094)

### H9 — Persistent Homology
- `H9_persistence_pairs.csv` — H0/H1 birth-death pairs (PH 결과)

### H10 — CPI 외생 통제
- `H10_macro_control_corr.csv` — 11분야 raw vs CPI-residual 상관

## 초기 EDA (T·A~E 코드)

- `T1_fld_freq.csv` — 분야별 주기성 강도
- `T2_sect_clusters.csv` — 부문 클러스터 매핑
- `T3_actv_gaming.csv` / `T3_fld_distribution.csv` — 활동·분야 게임화 지수
- `A_chooyeon_flow.csv` — 출연금 흐름 분석
- `B_pgm_compare.csv` — 프로그램 비교
- `C_dual_routing.csv` — 이중 routing
- `D_top20_breakdown.csv` — 상위 20 분해
- `E_2026_supp_new_ai.csv` / `E_yearly_new_in_supp.csv` — 2026 추경 신규 AI

## 외부 데이터 (data/external/)

```
bok_data/         한은 ECOS (CPI 36y)
data_go_kr/       공공데이터포털 (도로교통공단 11y)
gir/              GIR 국가 인벤토리 (온실가스 1990~2023, 34y)
kosis_data/       KOSIS outcome 캐시 (10분야)
kosis_meta/       KOSIS 카탈로그 24MB (보강용)
molit/            국토부 통계누리 자동차등록 4개 raw (자동 파싱 부정확, 보류용)
```
