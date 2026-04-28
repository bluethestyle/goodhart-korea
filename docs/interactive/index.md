---
hide:
  - toc
---

# 인터랙티브 시각화

<style>
.viz-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(380px, 1fr)); gap: 1.5rem; margin: 1.5rem 0; }
.viz-card { border: 1px solid var(--md-default-fg-color--lightest, #ddd); border-radius: 8px; padding: 1.2rem; transition: transform 0.15s ease, box-shadow 0.15s ease; }
.viz-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
.viz-card h3 { margin: 0 0 0.4rem 0; font-size: 1.05rem; }
.viz-card .badge { display: inline-block; padding: 0.15rem 0.5rem; font-size: 0.75rem; border-radius: 4px; background: var(--md-accent-fg-color--transparent, #f0f0f0); color: var(--md-accent-fg-color, #444); margin-right: 0.4rem; }
.viz-card p { margin: 0.4rem 0; font-size: 0.9rem; line-height: 1.5; color: var(--md-default-fg-color--light, #555); }
.viz-card a.btn { display: inline-block; margin-top: 0.6rem; padding: 0.4rem 1rem; background: var(--md-primary-fg-color, #5a67d8); color: #fff; text-decoration: none; border-radius: 5px; font-weight: 500; font-size: 0.9rem; }
.viz-card a.btn:hover { opacity: 0.85; }
</style>

> H1\~H24 분석 결과를 인터랙티브로 탐색. 모든 차트는 hover·클릭·필터 가능.

<div class="viz-grid">

<div class="viz-card">
  <h3>1. 부처 시그니처 네트워크</h3>
  <span class="badge">ECharts</span>
  <span class="badge">H5</span>
  <p>51개 부처 force-directed network. 5 co-cluster (CC0~CC4) 색·드래그·필터 가능.</p>
  <a class="btn" href="ministry_network.html">열기 →</a>
</div>

<div class="viz-card">
  <h3>2. 분야 → 사업원형 → outcome Sankey</h3>
  <span class="badge">ECharts</span>
  <span class="badge">H8</span>
  <p>같은 분야 안에서 사업 형태에 따라 outcome 부호가 정반대 — Holmstrom-Milgrom 다업무 가설 시각화.</p>
  <a class="btn" href="archetype_sankey.html">열기 →</a>
</div>

<div class="viz-card">
  <h3>3. 회계연도 12월 점프 (RDD)</h3>
  <span class="badge">Observable Plot</span>
  <span class="badge">H22</span>
  <p>한국판 Liebman-Mahoney (2017, AER) — 17 분야 × 10/11/12월 일평균 집행 + 점프 배수 + log-log scatter.</p>
  <a class="btn" href="rdd_scatter.html">열기 →</a>
</div>

<div class="viz-card">
  <h3>4. 4 archetypes × 15 outcomes 매트릭스</h3>
  <span class="badge">ECharts</span>
  <span class="badge">H4</span>
  <p>사업 형태별 outcome 차분 상관·수준 상관 비교 heatmap. 직관 반대 신호 hover.</p>
  <a class="btn" href="cluster_outcome_heatmap.html">열기 →</a>
</div>

</div>

---

## 시각화 도구

| 도구 | 역할 | 장점 |
|---|---|---|
| **ECharts 5.5** | force network, Sankey, heatmap | 풍부한 차트 종류 + 한국어 지원 |
| **Observable Plot 0.6** | RDD scatter (Mike Bostock 최신) | 데이터 저널리즘 미감 (NYT/Pudding) |
| **MkDocs Material** | 사이트 base | 한글 검색 + 다크모드 |

모두 *다크/라이트 자동 전환*, *반응형*, *PNG 저장* 지원.

## 데이터 출처

각 시각화는 [`docs/interactive/data/`](https://github.com/bluethestyle/goodhart-korea/tree/main/docs/interactive/data) JSON에서 fetch.
원본 분석은 [JOURNEY](../analysis/JOURNEY.md) H1\~H24 참조.
