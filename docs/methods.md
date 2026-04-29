# 방법론

본 연구는 Goodhart 효과의 robustness를 *triangulation* 으로 검증.

---

## 0. 이론 모형 (Principal-Agent) ★ paper §3

### Setup
- Agent: 측정 가능한 timing effort $e_t$ + 측정 불가 quality effort $e_q$
- Cost: $c(e_t, e_q; \theta)$, $\theta$ = 사업원형 (archetype)
- Principal weight: $w_t \gg w_q$ (측정 격차)

### 1차 조건 → 정책 levers
- $\partial e_t^* / \partial w_t > 0$ : 가시 KPI 가중치 ↑ → timing 게임화 ↑
- $\partial e_t^* / \partial w_q < 0$ : 품질 가중치 ↑ → timing 게임화 ↓

### 동학 확장
- **Career Concerns** (Holmstrom 1999): Bayesian 다기간 게임 → Nash 균형이 12-month cycle로 수렴 (H27 coherence 0.54 설명)
- **Performative Prediction** (Hardt 2016, Perdomo 2020): agent 학습으로 시간 강화 (H28 +554% 설명)

### Manheim-Garrabrant (2018) 4-type 매핑
| 타입 | 가설 |
|---|---|
| Causal | H2, H3 |
| Adversarial | H6 |
| Regressional | H5 |
| Extremal | H4 |

6 hypotheses: H1 분야 trivial / H2 자산취득형 RDD 3.42x / H3 출연금형 사이클 / H4 매개 이질성 / H5 사회복지 fortuitous / H6 시간 동적 강화.

---

## 1. 게임화 측정 (3-axis triangulation)

### FFT 기반 (`amp_12m_norm`)
- monthly_exec 시계열 → 12개월 주기 FFT 진폭 / 연 평균
- 활동×연도 단위로 산출

### STL 기반 (`seasonal_strength`) ★ 자기 비판
- Cleveland (1990) STL decomposition
- `1 − Var(remainder)/Var(detrended)`
- FFT와 비교: 사회복지 신호 trend 혼재 가능성 노출

### NeuralProphet (H26)
- Triebe et al. (2021), PyTorch + Prophet 하이브리드
- trend / seasonal / residual 신경망 분해
- pytorch-lightning 백엔드, *3번째 축*으로 FFT/STL 검증

---

## 2. 활동 임베딩

- **UMAP** (McInnes 2018): 12 피처 → 2D
- **HDBSCAN** (Campello 2013): 밀도 기반 클러스터
- **결과**: 1,557 활동 → 4 archetypes (인건비/자산취득/출연금/정상)

---

## 3. 위상 (TDA)

- **Mapper** (Singh-Mémoli-Carlsson 2007): UMAP 2D filter + DBSCAN
- **Persistent Homology** (Edelsbrunner-Harer 2008, Tralie ripser):
  - Vietoris-Rips, max thresh=8.0
  - H0 30 강건 components / H1 15 강건 loops
  - Bootstrap 50회 95% CI

---

## 4. 부처 그래프

- 부처 12피처 평균 → cosine 유사도
- Greedy Modularity Communities (5 co-cluster)
- **Spectral Co-clustering** (Dhillon 2001, scikit-learn): 51 부처 × 17 archetype

---

## 5. 회귀 (견고성)

- **FE Panel**: `Δoutcome ~ Δamp + 분야 FE + 연도 FE`
- **Permutation test** (1000회): null distribution
- **Lag/Lead** (k=−2..+2): 인과 방향 탐색

---

## 6. 인과 식별

### Regression Discontinuity (H22)
- Liebman-Mahoney (2017, AER) 한국판
- Cutoff: 12월 1일 (회계연도 마지막 달)
- Bandwidth: ±1month, ±2months
- Sharp RDD with parametric local polynomial

### Mediation Analysis (H23)
- Baron-Kenny (1986) 4 단계
- Sobel test + Bootstrap CI (5000회)
- X = chooyeon_pct, M = amp_12m_norm, Y = outcome

---

## 7. 외생 통제

- **CPI 외생 통제** (한은 ECOS 901Y009): residualized regression
- **STL trend 분리**: trend 제거 후 seasonal·remainder만으로 재측정

---

## 8. 주파수 영역 분석

### Power Spectrum / Phase / Coherence (H27)
- **PSD (Welch method)**: 출연금형 평균 PSD = **0.332** (archetype 중 최고)
- **Phase distribution**: 12-month 위상 정렬 검증
- **Magnitude-squared coherence**: 12-month 위상 일치도 = **0.54**
- 해석: Career Concerns 동적 게임의 *Nash 수렴* — 다수 agent가 12개월 주기로 동기화

### Continuous Wavelet Transform (H28)
- **Morlet wavelet** (PyWavelets) — FFT의 stationarity 가정 *완화*, 시간-주파수 동시 분석
- 출연금형 12-month 진폭: 2015~17 → 2023~25 사이 **+554%** 증가
- 인건비형: 변화 없음 (control 비교)
- → Performative prediction 가설의 시간 강화 증거

---

## 라이브러리

```
duckdb 1.4.2          | pandas 2.3.3       | numpy 2.2.6
scipy 1.17.1          | scikit-learn 1.8.0 | statsmodels 0.14.6
umap-learn 0.5.12     | hdbscan 0.8.42
kmapper 2.1.0         | ripser 0.6.14      | persim 0.3.8
networkx 3.6.1        | matplotlib 3.10.8  | seaborn 0.13.2
neuralprophet 0.9.0   | pytorch-lightning  | pywavelets 1.7
```
