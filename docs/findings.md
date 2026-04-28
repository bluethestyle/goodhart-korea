# 핵심 결과

본 페이지는 H1~H24 분석의 핵심 결과를 figure 중심으로 요약.

---

## H6 — 견고성 검증 (분야 14)

### Permutation test (1000회)

![H6 robustness panel](../data/figs/h6/H6_robustness_panel.png)

| 분야 | corr_diff | p (양측) |
|---|---:|---:|
| 사회복지 wealth_gini | **−0.762** | **0.035** ★ |
| 산업·중기 industry | +0.594 | 0.073 |
| 교육 imd_edu_rank | −0.588 | 0.085 |
| 보건 life_expectancy | +0.579 | 0.117 |

### Lag/Lead 분석

![H6 lag lead](../data/figs/h6/H6_lag_lead.png)

---

## H10 — CPI 외생 통제

![H10 CPI control](../data/figs/h10/H10_macro_control_compare.png)

**부호+70% 유지 14/14 = 100%** ⇒ 자연 cycle 가설 완전 기각.

---

## H3/H4 — 활동 임베딩 + 위상 (TDA)

### UMAP + HDBSCAN 4 archetypes

![H3 v2 UMAP](../data/figs/h3_embed_11y/H3_umap_scatter.png)

### Mapper graph

![H4 Mapper](../data/figs/h4_11y_v3/H4_mapper_graph_11y_v3.png)

### Persistent Homology

![H9 PH](../data/figs/h9_11y/H9_persistence_diagram_11y.png)

---

## H5 — 부처 시그니처 그래프

![H5 ministry graph](../data/figs/h5_11y/H5_ministry_graph.png)

5 co-clusters (CC0 행정 / CC1 사업 / CC2 분기말 / CC3 직접투자 / CC4 출연금)

---

## H8 — 비판적 자기평가

![H8 panel](../data/figs/h8_v3/H8_within_field_panel_v3.png)

분야 FE ΔR² = 0.000, +원형×Δamp ΔR² = +0.024

---

## H14 — 부처 노출 × outcome 4분면

![H14 risk quadrant](../data/figs/h14_v2/H14_risk_quadrant_v2.png)

**Q2 (점검 필요)**: 국무조정실, 과기정통부

---

## H22 — 회계연도 RDD (Liebman-Mahoney 한국판)

![H22 RDD main](../data/figs/h22/H22_rdd_main.png)

12월 점프 1.91x (p<10⁻¹²⁴), 출연금형 **3.42x**

![H22 RDD by field](../data/figs/h22/H22_rdd_by_field.png)

---

## H23 — Mediation Analysis

![H23 mediation](../data/figs/h23/H23_mediation_diagram.png)

농림수산 Sobel z=−2.90, p=0.004 (유일 강한 매개) / Pooled FE p=0.481

---

## H24 — STL trend 자기 비판 ★

![H24 STL examples](../data/figs/h24/H24_stl_examples.png)

![H24 STL vs FFT](../data/figs/h24/H24_seasonal_vs_amp12m.png)

사회복지 FFT r=−0.762 → STL r=+0.003 → **trend 혼재 가능성** 자기 비판
