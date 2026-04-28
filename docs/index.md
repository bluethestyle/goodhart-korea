# 한국 정부 재정 집행의 굿하트 효과

> *Multi-method robustness analysis of Goodhart's Law in Korean public spending*
>
> "What's measured is what matters" — Bevan & Hood (2006)

---

## 한 페이지 요약

[열린재정 정보](https://www.openfiscaldata.go.kr/) 월별 집행 데이터 **11년치**(2015~2026)와 KOSIS·한은 ECOS·공공데이터포털·GIR **14분야 outcome**을 통합해 한국 정부 재정 집행의 **Goodhart 효과**를 다각도로 측정·검증.

### 7가지 핵심 발견

=== "1. 분야 라벨 trivial"
    `ΔR² = 0.000` (5y/11y/v3 일관)

    **"분야가 다르니 outcome도 다를 것"**이라는 직관 정량 반증. 분야 FE만으로는 outcome 변동을 설명 못함. 사업 형태가 진짜 단위.

=== "2. 사업 형태가 진짜 단위"
    **4 archetypes** (UMAP+HDBSCAN, Persistent Homology 30+15)

    인건비형 / 자산취득형 (신규) / 출연금형 / 정상사업. 위상 안정성 입증 (bootstrap 50회 95% CI).

=== "3. 사회복지 자동분배 효과 ★"
    `r = −0.762, p = 0.035` / CPI 통제 후 `−0.86, p = 0.007`

    사회복지 정상사업 게임화↑ → 빈곤격차↓. **굿하트 도식과 정반대 방향**의 직관 반대 발견.

=== "4. 회계연도 12월 점프 (인과 식별)"
    1.91x 전체, **출연금형 3.42x** (H22 RDD)

    **Liebman & Mahoney (2017, AER) 한국판**. 미국 5x 대비 한국 1.9x. 출연금형이 Multitasking 가설(Holmstrom-Milgrom 1991) 실증.

=== "5. 부호 반전 클러스터"
    사회복지 chooyeon `+0.53` vs normal `−0.55`

    같은 분야 안 사업 형태별 정반대 부호 → **회계 cycle 가설 기각**.

=== "6. CPI 통제 견고성"
    **14/14 부호+70% 유지 (100%)**

    한은 ECOS CPI 외생 통제 후에도 모든 분야 부호 일관 → 자연 cycle 가설 완전 기각.

=== "7. STL trend 한계 명시 (자기 비판)"
    사회복지 신호 STL 후 `r=+0.003, p=0.991`로 소멸

    **메인 결과의 trend 혼재 가능성** 자기 비판. 정직한 한계 명시.

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
- **인프라 공사형 (자산취득)** = 12월 점프 큼, 단순 노이즈일 수도

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

- 📜 [전체 분석 여정 JOURNEY](analysis/JOURNEY.md) — H1~H24, ~1700 lines
- 📚 [참고문헌 REFERENCES](REFERENCES.md) — 39 references 9 categories
- 🌐 [데이터 출처 SOURCES](../data/external/SOURCES.md) — 정합성 검증
- 📊 [산출 CSV INDEX](../data/results/INDEX.md) — 49+ 결과 파일

---

## 인용

```bibtex
@misc{korea_goodhart_2026,
  title  = {Goodhart's Law in Korean Public Spending: A Multi-Method
            Robustness Analysis with Heterogeneous Effects},
  year   = {2026},
  url    = {https://github.com/bluethestyle/goodhart-korea},
  doi    = {10.5281/zenodo.{TBD}}
}
```

