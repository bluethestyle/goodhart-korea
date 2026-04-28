# 한국 정부 재정 집행의 굿하트 효과 — 다각적 측정과 정책 함의

> *"What's measured is what matters" — Bevan & Hood (2006)*

[열린재정 정보](https://www.openfiscaldata.go.kr/) 월별 집행 11년치 + KOSIS·한은 ECOS·공공데이터포털·GIR 14분야 outcome을 통합해 한국 정부 재정 집행의 **Goodhart 효과**(측정 왜곡)를 다각도로 측정·검증한 분석 프로젝트.

- 🗂 [docs/analysis/JOURNEY.md](docs/analysis/JOURNEY.md) — 전체 분석 여정 (H1~H24, ~1700 lines)
- 📚 [docs/REFERENCES.md](docs/REFERENCES.md) — 39 참고문헌 9 카테고리
- 🌐 [data/external/SOURCES.md](data/external/SOURCES.md) — 데이터 출처 정합성 검증
- 📊 [data/results/INDEX.md](data/results/INDEX.md) — 49+ 산출 CSV 인덱스

---

## 핵심 발견

| # | 발견 | 통계 | 메시지 |
|---|---|---|---|
| 1 | **분야 라벨 trivial** | ΔR²=0.000 (5y/11y/v3 일관) | "분야 다르니 outcome 다를 것" 직관 정량 반증 |
| 2 | **사업 형태가 진짜 단위** | 4 archetypes (UMAP+HDBSCAN, PH 30+15) | 인건비/자산취득/출연금/정상 |
| 3 | **사회복지 자동분배 효과** | r=−0.762, p=0.035 ★ / CPI 통제 −0.86, p=0.007 | 사회복지 정상사업 게임화↑ → 빈곤격차↓ |
| 4 | **회계연도 12월 점프** | 1.91x 전체, **출연금형 3.42x** (H22 RDD) | Liebman-Mahoney(2017, AER) 한국판 |
| 5 | **부호 반전 클러스터** | 사회복지 chooyeon +0.53 vs normal −0.55 | 같은 분야 안 사업 형태별 정반대 (회계 cycle 가설 기각) |
| 6 | **CPI 통제 견고성** | 14/14 부호+70% 유지 (100%) | 자연 cycle 가설 기각 |
| 7 | **STL trend 한계 명시** | 사회복지 신호 STL 후 소멸 | trend 혼재 가능성 자기 비판 |

**14분야 outcome 매핑**: 사회복지/보건/과기/산업/관광/교육/국토/행정/농림/교통/환경/통신/통일외교/공공질서 (예비비·국방 제외)

**정책 점검 우선순위 (H14 Q2)**: 국무조정실, 과학기술정보통신부

---

## 빠른 시작

### 1. 환경 설정

```bash
git clone <repo-url>
cd <repo>
pip install -r requirements.txt
```

### 2. API 키 (`.env` 생성, gitignored)

```bash
# .env
OPENFISCAL_KEY=...        # https://www.openfiscaldata.go.kr/
KOSIS_KEY=...             # https://kosis.kr/openapi/
BOK_KEY=...               # https://ecos.bok.or.kr/
DATA_GO_KR_KEY_ENC=...    # https://www.data.go.kr/ (URL-encoded)
DATA_GO_KR_KEY_DEC=...    # 동일 decoded
```

### 3. 데이터 + warehouse 빌드 (~30분)

```bash
# 월별 집행 (게임화 측정 핵심)
python scripts/fetch_monthly_exec.py            # 2020~2026
python scripts/fetch_monthly_exec_2015_2019.py  # 2015~2019 확장
python scripts/build_warehouse.py

# 14분야 outcome 적재
python scripts/load_kosis_outcomes.py           # 보건/관광/산업
python scripts/h7_outcome_load.py               # 교육/국토/행정/농림
python scripts/h11_traffic_outcome.py           # 도로교통공단
python scripts/h12_ghg_outcome.py               # GIR 온실가스 (CSV 다운로드 필요)
python scripts/h13_ict_outcome.py               # ECOS ICT
python scripts/h15_oda_outcome.py               # ODA
python scripts/h16_crime_outcome.py             # 범죄
python scripts/h18_patent_outcome.py            # 특허 (과기 교체)
python scripts/h19_tourism_finance_outcome.py   # 관광/재정자립 (교체)
python scripts/h20_broadband_outcome.py         # 초고속인터넷 (통신 교체)
python scripts/h21_imd_defense_outcome.py       # IMD 교육 (교체)
python scripts/build_indicator_panel.py
```

### 4. 분석 실행 (~1시간)

```bash
# 핵심 회귀
python scripts/h1_mechanism_full.py
python scripts/h2_decoupling_test.py

# 활동 임베딩 (UMAP+HDBSCAN)
python scripts/h3_v2_11y.py                    # 11y, 4 archetypes

# TDA
python scripts/h4_v3_replaced.py               # Mapper
python scripts/h9_v2_11y.py                    # Persistent Homology

# 부처 그래프
python scripts/h5_v2_11y.py                    # 5 co-clusters
python scripts/h14_v2_replaced.py              # 4분면 점검 도구

# 견고성 + 비판적 자기평가
python scripts/h6_robustness.py                # FE/permutation/lag
python scripts/h8_v3_replaced.py               # 분야 trivial 검증
python scripts/h10_macro_control.py            # CPI 외생 통제

# 인과 식별
python scripts/h22_rdd_yearend.py              # 회계연도 RDD
python scripts/h23_mediation.py                # Baron-Kenny + Sobel
python scripts/h24_stl_decomp.py               # STL trend 자기 비판
```

---

## 디렉토리 구조

```
.
├── README.md                     본 문서
├── requirements.txt              Python 의존성 (검증된 버전)
├── .env                          API 키 (gitignored)
├── .env.example                  키 템플릿 (TODO)
│
├── scripts/                      H1~H24 분석 스크립트
│   ├── _env.py                   .env 자동 로드
│   ├── fetch_*.py                데이터 수집 (8개)
│   ├── build_warehouse.py        DuckDB 빌드
│   ├── build_indicator_panel.py  분야×연도×지표 패널
│   └── h{N}_*.py / h{N}_v{2,3}_*.py  가설별 분석 (~30 스크립트)
│
├── data/
│   ├── warehouse.duckdb          DuckDB (gitignored, ~30MB)
│   ├── budget/raw/               OPENFISCAL VWFOEM 캐시 (gitignored, 350MB+)
│   ├── external/                 외부 데이터
│   │   ├── SOURCES.md            ★ 출처 정합성 검증
│   │   ├── kosis_data/ bok_data/ data_go_kr/ gir/ molit/ kosis_meta/
│   ├── figs/                     시각화 PNG (h2~h24)
│   └── results/
│       ├── INDEX.md              ★ 49+ 산출 CSV 인덱스
│       └── H{N}_*.csv
│
└── docs/
    ├── REFERENCES.md             ★ 39 학술 참고문헌
    └── analysis/
        └── JOURNEY.md            ★ 분석 여정 H1~H24
```

---

## 방법론 종합

| 단계 | 방법 | 라이브러리 | 목적 |
|---|---|---|---|
| 측정 | FFT (amp_12m_norm) + STL (seasonal_strength) | scipy / statsmodels | 게임화 + trend 통제 |
| 임베딩 | UMAP + HDBSCAN | umap-learn / hdbscan | 활동 1,557 → 4 archetypes |
| 위상 | Mapper + Persistent Homology | kmapper / ripser / persim | 매니폴드 안정성 |
| 그래프 | cosine + Spectral Co-clustering | scikit-learn / networkx | 부처 5 커뮤니티 |
| 회귀 | FE Panel + Permutation 1000회 | numpy / scipy | 견고성 |
| 인과 | RDD + Baron-Kenny Mediation + Sobel | numpy / scipy | 식별 |
| 통제 | CPI 외생 (한은 ECOS) | (custom) | 자연 cycle 분리 |

---

## 한계

1. **인과 식별 약점**: DID 통제군 부재 (한국 단일 정부)
2. **STL trend 혼재**: 사회복지 신호 STL 후 소멸 — *trend × seasonal* 혼재 가능성
3. **표본 제약**: outcome 시계열 5~35년 분야별 / 차분 후 N=8~12
4. **국방·예비비 outcome 매핑 보류**: 측정 불가능 분야 명시
5. **Mediation pooled 미유의** (p=0.481): 시스템 평균 매개 효과 약함, 분야 이질성이 진짜 메커니즘

---

## Reproducibility

| 항목 | 상태 |
|---|---|
| ✅ requirements.txt | 검증된 라이브러리 버전 |
| ✅ random_state | UMAP/HDBSCAN/permutation random_state=42 고정 (H3, H5, H9 등) |
| ✅ API 키 분리 | .env (gitignored) + scripts/_env.py 자동 로드 |
| ✅ 결과 CSV | data/results/ 모든 산출 보관 |
| ⚠️ 데이터 라이선스 | 일부 raw 데이터 외부 redirect (사용자 다운로드 필요) |
| ⚠️ DuckDB warehouse | gitignored — 위 fetch 명령으로 재생성 (~30분) |

---

## 인용

```bibtex
@misc{korea_goodhart_2026,
  title  = {Goodhart's Law in Korean Public Spending:
            A Multi-Method Robustness Analysis with Heterogeneous Effects},
  author = {(저자명)},
  year   = {2026},
  url    = {https://github.com/bluethestyle/goodhart-korea},
  doi    = {10.5281/zenodo.{TBD}}
}
```

---

## 라이선스

- **코드**: MIT License
- **데이터**: 각 출처 라이선스 ([SOURCES.md](data/external/SOURCES.md) 참조)
  - KOSIS / BOK ECOS / 공공데이터포털 / GIR — 출처 표시 + 비영리·연구 활용
- **분석 결과 (CSV/PNG)**: CC BY 4.0
