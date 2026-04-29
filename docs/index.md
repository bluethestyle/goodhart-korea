# 한국 정부 재정 집행의 굿하트 효과

> *Multi-method robustness analysis of Goodhart's Law in Korean public spending*
>
> "What's measured is what matters" — Bevan & Hood (2006)

---

## 한 페이지 요약

[열린재정 정보](https://www.openfiscaldata.go.kr/) 월별 집행 데이터 **11년치**(2015~2026)와 KOSIS·한은 ECOS·공공데이터포털·GIR **14분야 outcome**을 통합해 한국 정부 재정 집행의 **Goodhart 효과**를 다각도로 측정·검증.

### 6가설 프레임 (Principal-Agent 모형)

=== "H1. 분야 라벨 trivial"
    `ΔR² = 0.000` (5y/11y/v3 일관)

    **"분야가 다르니 outcome도 다를 것"**이라는 직관 정량 반증. 분야 FE만으로는 outcome 변동을 설명 못함. 사업 형태가 진짜 단위.

=== "H2. 자산취득형 12월 RDD 점프 ★"
    1.91x 전체, **자산취득형 3.42x** (H22 RDD)

    **Liebman & Mahoney (2017, AER) 한국판**. 미국 5x 대비 한국 1.9x. 자산취득형이 회계연도 마감 압력에 가장 강하게 반응 — Multitasking 가설(Holmstrom-Milgrom 1991) 실증.

=== "H3. 출연금형 사이클 우세 ★ (NEW)"
    PSD 평균 **0.332** (4 archetype 중 최대) / phase coherence **0.54**

    출연금형은 사업 간 12개월 cycle이 *동기화* — Career Concerns 동적 게임의 *Nash convergence* 실증. (H27 PSD·Phase·Coherence)

=== "H4. 매개 경로 이질성"
    농림수산 Sobel `z=−2.90, p=0.004` / Pooled FE `p=0.481`

    분야별 매개 경로 상이. 단일 메커니즘 가정 기각.

=== "H5. 사회복지 fortuitous alignment ★"
    `r = −0.762, p = 0.035` / CPI 통제 후 `−0.86, p = 0.007`

    사회복지 정상사업 게임화↑ → 빈곤격차↓. **굿하트 도식과 정반대 방향**의 직관 반대 발견.

=== "H6. 시간 동적 강화 ★ (NEW)"
    Wavelet: 출연금형 12개월 진폭 **2015~17 → 2023~25 +554%**

    FFT 정상성 가정 보완. 인건비형은 변화 없음 (통제군). 정책적으로 *최근 3년 자료에 가중 점검* 권고. (H28 CWT)

### 부가 발견

=== "사업 형태가 진짜 단위"
    **4 archetypes** (UMAP+HDBSCAN, Persistent Homology 30+15)

    인건비형 / 자산취득형 / 출연금형 / 정상사업. 위상 안정성 입증 (bootstrap 50회 95% CI).

=== "부호 반전 클러스터"
    사회복지 chooyeon `+0.53` vs normal `−0.55`

    같은 분야 안 사업 형태별 정반대 부호 → **회계 cycle 가설 기각**.

=== "CPI 통제 견고성"
    **14/14 부호+70% 유지 (100%)**

    한은 ECOS CPI 외생 통제 후에도 모든 분야 부호 일관 → 자연 cycle 가설 완전 기각.

=== "방법론 트라이앵귤레이션"
    FFT + STL + **NeuralProphet** (H26)

    14분야 outcome 상관 세 방법론 cross-check. STL trend 한계 (사회복지 `r=+0.003`) 자기 비판 + NeuralProphet 신경망 분해로 보완.

---

## 정책 함의

### 부처 점검 우선순위 (H14 4분면)

| 분면 | 부처 | 의미 |
|---|---|---|
| **Q2 (점검 필요)** | 국무조정실 / 과학기술정보통신부 | 굿하트 위험 + outcome 양 상관 (측정 왜곡 가능) |
| Q1 (자동분배 OK) | 행정중심복합도시건설청 등 | 굿하트 노출은 있으나 outcome 음 상관 |

### 사업 형태별 점검 의무

- **출연금형 + 극단 게임화 sub05** (50개 활동) = **1차 점검 우선**
- **사회복지 정상사업** = 자동분배 효과 (게임화 유지 OK)
- **자산취득형 (인프라 공사형)** = 12월 점프 3.42x, RDD 인과 식별 — 회계 마감 압력 점검

### 시간 가중 점검 (H6 wavelet 권고 ★)

- 출연금형 12개월 cycle 진폭이 **2015~17 → 2023~25 +554%** 강화 → **최근 3년 자료에 가중치**
- 인건비형 통제군은 변화 없음 → cycle 강화는 *출연금형 고유 동학*
- 시간 정상성 가정에 의존하는 FFT/회귀 결과는 *최근 시기 sub-sample* 재검증 권고

---

## 14분야 outcome 매핑

(부적절 4 + 의심 2 = 6 outcome 사용자 비판 반영 후 교체)

| 분야 | 최종 outcome | 시계열 | 출처 |
|---|---|---|---|
| 사회복지 | wealth_gini | 9y | KOSIS DT_1HDAAD04 |
| 보건 | life_expectancy | 15y | KOSIS DT_1B41 |
| 과학기술 | patent_apps_total | 22y | e-나라지표 1526 (rd_total 자기 인과 교체) |
| 산업·중기 | industry_production_index | 15y | KOSIS DT_1JH20201 |
| 문화관광 | foreign_tourists_total | 35y | e-나라지표 1653 (tourists_sample 표본수 교체) |
| 교육 | imd_edu_rank | 17y | e-나라지표 1526 (private_edu_hours 역지표 교체) |
| 국토 | housing_supply | 20y | KOSIS DT_MLTM_2100 |
| 일반·지방행정 | fiscal_indep_natl | 29y | e-나라지표 2458 (local_tax 징세 교체) |
| 농림수산 | farm_income | 22y | KOSIS DT_1EA1501 |
| 교통 | traffic_deaths | 10y | 도로교통공단 lgStat |
| 환경 | ghg_total | 34y | GIR 국가 인벤토리 |
| 통신 | broadband_per_100 | 27y | e-나라지표 1348 (ict_value_added 자기 인과 교체) |
| 통일외교 | oda_total | 24y | e-나라지표 1687 (OECD DAC) |
| 공공질서 | crime_occurrence | 29y | e-나라지표 1606 (경찰청) |

**제외**: 국방 (안보 outcome 측정 불가능), 예비비 (분야 아님)

---

## 관련 문서

- 📄 [paper/main_v2.typ](../paper/main_v2.typ) — Principal-Agent 모형 + 6 가설로 정렬된 정식 논문 버전 ★
- 📜 [전체 분석 여정 JOURNEY](analysis/JOURNEY.md) — H1~H28, ~1700+ lines
- 📚 [참고문헌 REFERENCES](REFERENCES.md) — 47 references 9 categories
- 🌐 [데이터 출처 SOURCES](../data/external/SOURCES.md) — 정합성 검증
- 📊 [산출 CSV INDEX](../data/results/INDEX.md) — 49+ 결과 파일
- 🖥️ [인터랙티브 시각화 (GitHub Pages)](https://bluethestyle.github.io/goodhart-korea/) — Sankey / heatmap / ministry network / RDD scatter / NeuralProphet

---

## 인용

```bibtex
@misc{korea_goodhart_2026,
  title  = {Goodhart's Law in Korean Public Spending:
            A Principal-Agent Analysis with Multi-Method Robustness},
  year   = {2026},
  url    = {https://github.com/bluethestyle/goodhart-korea},
  doi    = {10.5281/zenodo.{TBD}}
}
```

