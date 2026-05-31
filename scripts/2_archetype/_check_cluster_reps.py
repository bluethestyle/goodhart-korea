"""C0~C3 클러스터별 (a) 클러스터 평균 (b) 현재 대표 (c) 추천 대표 비교.

narrative 가설:
  C0 인건비형 → 매월 균등
  C1 자산취득형 → 12월 절벽 (12월 비중 매우 높음)
  C2 출연금형 → 분기·반기 사이클 (1·4·7·10 또는 3·6·9·12 집중)
  C3 정상사업 → 평균 부근 (비교군)
"""
import duckdb
import pandas as pd
import numpy as np
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

con = duckdb.connect('data/warehouse.duckdb', read_only=True)
h3 = pd.read_csv('data/results/H3_activity_embedding_11y.csv')

CLUSTER_INFO = {
    0: ('C0 인건비형', '매월 균등', '노인일자리지원'),
    1: ('C1 자산취득형', '12월 절벽', '신공항건설'),
    2: ('C2 출연금형', '분기·반기 사이클', '고속도로건설'),
    3: ('C3 정상사업', '평균 부근', '우주발사체개발'),
}

def monthly_dist(actv_list):
    """활동 리스트의 월별 평균 비중 12개 반환 (각 활동 연-비중 평균의 평균)."""
    if not actv_list:
        return None
    ph = ','.join(['?'] * len(actv_list))
    q = f"""
    WITH ay AS (
      SELECT FSCL_YY, ACTV_NM, EXE_M, SUM(EP_AMT) AS s
      FROM monthly_exec
      WHERE ACTV_NM IN ({ph}) AND FSCL_YY BETWEEN 2015 AND 2025
      GROUP BY 1, 2, 3
    ),
    yt AS (SELECT FSCL_YY, ACTV_NM, SUM(s) AS yr FROM ay GROUP BY 1, 2 HAVING yr > 0),
    mp AS (SELECT FSCL_YY, ACTV_NM, EXE_M, s*1.0/yr AS p FROM ay JOIN yt USING (FSCL_YY, ACTV_NM)),
    pa AS (SELECT ACTV_NM, EXE_M, AVG(p) AS pct FROM mp GROUP BY 1, 2)
    SELECT EXE_M, AVG(pct)*100 AS m, STDDEV(pct)*100 AS sd
    FROM pa GROUP BY EXE_M ORDER BY EXE_M
    """
    rows = con.execute(q, actv_list).fetchall()
    return rows

def render_dist(rows, label):
    print(f'  {label}')
    for m, pct, sd in rows:
        bar = '█' * int(pct * 2)
        print(f'    {m:2d}월 {pct:5.2f}% {bar}')
    arr = np.array([r[1] for r in rows])
    sd12 = arr.std()
    print(f'    → 12개월 sd = {sd12:.2f}%p, 12월 = {arr[11]:.1f}%, '
          f'분기첫달(1·4·7·10) = {arr[[0,3,6,9]].sum():.1f}%, '
          f'분기말(3·6·9·12) = {arr[[2,5,8,11]].sum():.1f}%')
    return arr

def find_closest(cluster_acts, ref_pattern, n_top=5, score='l2'):
    """ref_pattern(12개)과 가장 가까운 활동 Top n."""
    ph = ','.join(['?'] * len(cluster_acts))
    q = f"""
    WITH ay AS (
      SELECT FSCL_YY, ACTV_NM, EXE_M, SUM(EP_AMT) AS s
      FROM monthly_exec
      WHERE ACTV_NM IN ({ph}) AND FSCL_YY BETWEEN 2015 AND 2025
      GROUP BY 1, 2, 3
    ),
    yt AS (SELECT FSCL_YY, ACTV_NM, SUM(s) AS yr FROM ay GROUP BY 1, 2 HAVING yr > 0),
    mp AS (SELECT FSCL_YY, ACTV_NM, EXE_M, s*1.0/yr AS p FROM ay JOIN yt USING (FSCL_YY, ACTV_NM))
    SELECT ACTV_NM, EXE_M, AVG(p)*100 AS pct, SUM(yr) AS yr_total
    FROM mp JOIN yt USING (FSCL_YY, ACTV_NM)
    GROUP BY ACTV_NM, EXE_M
    """
    df = con.execute(q, cluster_acts).fetchdf()
    if df.empty:
        return None
    piv = df.pivot_table(index='ACTV_NM', columns='EXE_M', values='pct', fill_value=0)
    yr_tot = df.groupby('ACTV_NM')['yr_total'].max()  # 연 평균 규모
    # 12개월 완비된 활동만
    piv = piv.reindex(columns=range(1, 13), fill_value=0)
    valid = (piv > 0).any(axis=1)
    piv = piv[valid]
    ref = np.array(ref_pattern)
    if score == 'l2':
        dist = ((piv.values - ref)**2).sum(axis=1) ** 0.5
        piv['_score'] = dist
        piv = piv.sort_values('_score', ascending=True)
    out = piv.head(n_top).copy()
    out['_yr_avg_kw'] = [yr_tot.get(a, 0) / 11 / 1e8 for a in out.index]  # 억원
    out['_dec_pct'] = out[12]
    out['_q1m_sum'] = out[[1, 4, 7, 10]].sum(axis=1)
    out['_q1m3_sum'] = out[[3, 6, 9, 12]].sum(axis=1)
    return out

# C0 인건비형 narrative pattern: 매월 균등 = [8.33] * 12
# C1 자산취득형 narrative: 12월 절벽 — 12월 매우 큼
# C2 출연금형 narrative: 분기·반기 사이클 (3·6·9·12 또는 1·4·7·10 집중)
# C3 정상사업 narrative: 평균 부근

# 각 클러스터 평균을 narrative 검증의 reference로 우선 출력 → 사용자가 보고 판단
for cid, (name, narr, curr) in CLUSTER_INFO.items():
    acts = h3[h3['cluster'] == cid]['ACTV_NM'].tolist()
    print('=' * 75)
    print(f'{name}  (n={len(acts)}, narrative = "{narr}", 현재 대표 = "{curr}")')
    print('=' * 75)
    cluster_rows = monthly_dist(acts)
    cluster_arr = render_dist(cluster_rows, '【클러스터 평균】')
    print()
    curr_rows = monthly_dist([curr])
    if curr_rows:
        curr_arr = render_dist(curr_rows, f'【현재 대표 "{curr}"】')
        match_l2 = ((curr_arr - cluster_arr)**2).sum() ** 0.5
        print(f'    ↳ 클러스터 평균과의 L2 거리 = {match_l2:.2f}')
    print()
    print('  【클러스터 평균과 가장 가까운 Top 5】')
    top = find_closest(acts, cluster_arr.tolist(), n_top=5)
    if top is not None:
        for actv, row in top.iterrows():
            print(f'    L2={row["_score"]:5.2f} | 12월={row["_dec_pct"]:5.1f}% '
                  f'| q1m={row["_q1m_sum"]:5.1f}% | q3m={row["_q1m3_sum"]:5.1f}% '
                  f'| 연평균 {row["_yr_avg_kw"]:7.1f}억 | {actv}')
    print()
