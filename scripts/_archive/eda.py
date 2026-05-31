"""warehouse 전체 탐색 — 시계열, 분포, 변동성, 구조."""
import os, sys, io, duckdb
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
for f in ['Malgun Gothic','NanumGothic','AppleGothic','Noto Sans CJK KR']:
    try: plt.rcParams['font.family']=f; break
    except: pass
plt.rcParams['axes.unicode_minus']=False

sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG=os.path.join(ROOT,'data','figs','eda'); os.makedirs(FIG, exist_ok=True)
con=duckdb.connect(os.path.join(ROOT,'data','warehouse.duckdb'), read_only=True)

def show(title, sql):
    print(f'\n{"="*78}\n{title}\n{"="*78}')
    df=con.execute(sql).fetchdf()
    print(df.to_string(index=False, max_rows=30))
    return df

print('#'*78); print('# 1. 테이블 구조와 시계열 범위'); print('#'*78)

show('1.1) 테이블별 행 수와 시간 범위', """
WITH t AS (
    SELECT 'expenditure_budget' AS tbl, count(*)::INT AS rows,
           min(FSCL_YY)::INT AS yr_min, max(FSCL_YY)::INT AS yr_max
    FROM expenditure_budget
    UNION ALL
    SELECT 'expenditure_item', count(*), min(FSCL_YY), max(FSCL_YY) FROM expenditure_item
    UNION ALL
    SELECT 'revenue_budget',   count(*), min(FSCL_YY), max(FSCL_YY) FROM revenue_budget
    UNION ALL
    SELECT 'debt_monthly',     count(*), min(CAST(OJ_YY AS INT)), max(CAST(OJ_YY AS INT)) FROM debt_monthly
    UNION ALL
    SELECT 'debt_yearly',      count(*), min(CAST(OJ_YY AS INT)), max(CAST(OJ_YY AS INT)) FROM debt_yearly
    UNION ALL
    SELECT 'openapi_catalog',  count(*), null, null FROM openapi_catalog
    UNION ALL
    SELECT 'kodas_catalog',    count(*), null, null FROM kodas_catalog
)
SELECT * FROM t
""")

print('\n'+'#'*78); print('# 2. 16대 분야 예산 점유율 시계열'); print('#'*78)

# 본예산 회차0만, 5년 점유율
fld_share = show('2.1) 분야별 본예산 점유율 (2020~2026 회차0)', """
WITH base AS (
    SELECT FSCL_YY, FLD_NM, sum(Y_YY_DFN_KCUR_AMT) AS amt
    FROM expenditure_budget WHERE SBUDG_DGR=0
    GROUP BY FSCL_YY, FLD_NM
),
total AS (SELECT FSCL_YY, sum(amt) AS tot FROM base GROUP BY FSCL_YY)
SELECT b.FSCL_YY, b.FLD_NM,
       round(b.amt/1e6,1) AS amt_eok,
       round(b.amt*100.0/t.tot,1) AS pct
FROM base b JOIN total t USING (FSCL_YY)
WHERE b.FSCL_YY IN (2020, 2023, 2026)
ORDER BY b.FSCL_YY DESC, b.amt DESC
""")

# 분야별 변화율 5년치
show('2.2) 분야별 5년 변화율 (2020 → 2026)', """
WITH a AS (
    SELECT FLD_NM, sum(Y_YY_DFN_KCUR_AMT) AS y20
    FROM expenditure_budget WHERE SBUDG_DGR=0 AND FSCL_YY=2020 GROUP BY FLD_NM
),
b AS (
    SELECT FLD_NM, sum(Y_YY_DFN_KCUR_AMT) AS y26
    FROM expenditure_budget WHERE SBUDG_DGR=0 AND FSCL_YY=2026 GROUP BY FLD_NM
)
SELECT a.FLD_NM,
       round(a.y20/1e6, 0) AS amt_2020_eok,
       round(b.y26/1e6, 0) AS amt_2026_eok,
       round((b.y26 - a.y20) / a.y20 * 100, 1) AS growth_pct,
       round(b.y26 / a.y20, 2) AS ratio
FROM a JOIN b USING (FLD_NM)
ORDER BY ratio DESC
""")

print('\n'+'#'*78); print('# 3. 부처 단위 분석'); print('#'*78)

show('3.1) 부처별 점유율 — 2026 본예산 Top 15', """
WITH t AS (SELECT sum(Y_YY_DFN_KCUR_AMT) AS tot
           FROM expenditure_budget WHERE FSCL_YY=2026 AND SBUDG_DGR=0)
SELECT OFFC_NM,
       round(sum(Y_YY_DFN_KCUR_AMT)/1e6, 0) AS amt_eok,
       round(sum(Y_YY_DFN_KCUR_AMT)*100.0/(SELECT tot FROM t), 2) AS pct,
       count(DISTINCT SACTV_NM) AS sactv_n
FROM expenditure_budget WHERE FSCL_YY=2026 AND SBUDG_DGR=0
GROUP BY OFFC_NM ORDER BY amt_eok DESC LIMIT 15
""")

# HHI 부처 집중도 시계열
show('3.2) 부처 집중도 HHI 시계열 (전체, 본예산)', """
WITH s AS (
    SELECT FSCL_YY, OFFC_NM, sum(Y_YY_DFN_KCUR_AMT) AS amt
    FROM expenditure_budget WHERE SBUDG_DGR=0
    GROUP BY FSCL_YY, OFFC_NM
),
sh AS (
    SELECT FSCL_YY, OFFC_NM, amt*1.0 / sum(amt) OVER (PARTITION BY FSCL_YY) AS share
    FROM s
)
SELECT FSCL_YY,
       round(sum(share*share), 4) AS hhi,
       count(*) AS n_offc,
       round(1.0/sum(share*share), 1) AS effective_n
FROM sh GROUP BY FSCL_YY ORDER BY FSCL_YY
""")

print('\n'+'#'*78); print('# 4. 사업당 평균 금액 분포'); print('#'*78)

show('4.1) 사업당 평균 금액 분포 통계 (FSCL_YY × percentile)', """
WITH s AS (
    SELECT FSCL_YY, SACTV_NM, sum(Y_YY_DFN_KCUR_AMT) AS amt
    FROM expenditure_budget WHERE SBUDG_DGR=0
    GROUP BY FSCL_YY, SACTV_NM
)
SELECT FSCL_YY, count(*) AS n_sactv,
       round(avg(amt)/1e6, 2) AS mean_eok,
       round(median(amt)/1e6, 2) AS median_eok,
       round(quantile_cont(amt, 0.9)/1e6, 1) AS p90_eok,
       round(quantile_cont(amt, 0.99)/1e6, 1) AS p99_eok,
       round(stddev(amt)/avg(amt), 2) AS cv
FROM s GROUP BY FSCL_YY ORDER BY FSCL_YY
""")

print('\n'+'#'*78); print('# 5. 통계목(CITM) 분포 — 어디로 흘러가나'); print('#'*78)

show('5.1) 정부 전체 편성목별 비중 (2026 본예산)', """
WITH t AS (SELECT sum(Y_YY_DFN_KCUR_AMT) AS tot
           FROM expenditure_item WHERE FSCL_YY=2026 AND SBUDG_DGR=0)
SELECT CITM_NM,
       round(sum(Y_YY_DFN_KCUR_AMT)/1e6, 0) AS amt_eok,
       round(sum(Y_YY_DFN_KCUR_AMT)*100.0/(SELECT tot FROM t), 2) AS pct
FROM expenditure_item WHERE FSCL_YY=2026 AND SBUDG_DGR=0
GROUP BY CITM_NM ORDER BY amt_eok DESC LIMIT 15
""")

show('5.2) 분야별 출연금 비중 (2026 본예산)', """
WITH base AS (
    SELECT FLD_NM, sum(Y_YY_DFN_KCUR_AMT) AS tot
    FROM expenditure_item WHERE FSCL_YY=2026 AND SBUDG_DGR=0 GROUP BY FLD_NM
),
ch AS (
    SELECT FLD_NM, sum(Y_YY_DFN_KCUR_AMT) AS chooyeon
    FROM expenditure_item WHERE FSCL_YY=2026 AND SBUDG_DGR=0
      AND CITM_NM IN ('일반출연금','연구개발출연금','출연금')
    GROUP BY FLD_NM
)
SELECT b.FLD_NM,
       round(b.tot/1e6, 0) AS total_eok,
       round(coalesce(c.chooyeon,0)/1e6, 0) AS chooyeon_eok,
       round(coalesce(c.chooyeon,0)*100.0/b.tot, 1) AS chooyeon_pct
FROM base b LEFT JOIN ch c USING (FLD_NM)
ORDER BY total_eok DESC
""")

print('\n'+'#'*78); print('# 6. 본예산 vs 추경 패턴 (수정·반영 의미 검증)'); print('#'*78)

show('6.1) Y_YY_DFN_KCUR_AMT vs Y_YY_MEDI_KCUR_AMT 차이 (몇 행이나 다른가?)', """
SELECT FSCL_YY, SBUDG_DGR,
       count(*) AS rows,
       sum(CASE WHEN Y_YY_MEDI_KCUR_AMT != Y_YY_DFN_KCUR_AMT THEN 1 ELSE 0 END) AS diff_rows,
       round(sum(Y_YY_DFN_KCUR_AMT)/1e6, 0) AS dfn_eok,
       round(sum(Y_YY_MEDI_KCUR_AMT)/1e6, 0) AS medi_eok
FROM expenditure_budget GROUP BY FSCL_YY, SBUDG_DGR
ORDER BY FSCL_YY, SBUDG_DGR
""")

show('6.2) 본예산 → 1차 추경 분야별 변화율 (2025년)', """
WITH d0 AS (
    SELECT FLD_NM, sum(Y_YY_DFN_KCUR_AMT) AS amt
    FROM expenditure_budget WHERE FSCL_YY=2025 AND SBUDG_DGR=0 GROUP BY FLD_NM
),
d1 AS (
    SELECT FLD_NM, sum(Y_YY_DFN_KCUR_AMT) AS amt
    FROM expenditure_budget WHERE FSCL_YY=2025 AND SBUDG_DGR=1 GROUP BY FLD_NM
)
SELECT d0.FLD_NM,
       round(d0.amt/1e6, 0) AS base_eok,
       round(d1.amt/1e6, 0) AS supp1_eok,
       round((d1.amt - d0.amt) / d0.amt * 100, 2) AS chg_pct
FROM d0 JOIN d1 USING (FLD_NM)
ORDER BY abs((d1.amt - d0.amt) / d0.amt) DESC
""")

print('\n'+'#'*78); print('# 7. 채무·세입 측면'); print('#'*78)

show('7.1) 월별 국가채무 시계열 — 최근 24개월 + 증가율', """
WITH t AS (
    SELECT (CAST(OJ_YY AS INT)*100 + CAST(OJ_M AS INT)) AS ym,
           OJ_YY, OJ_M,
           CAST(GOD_SUM_AMT AS DOUBLE) AS amt
    FROM debt_monthly
)
SELECT OJ_YY, OJ_M, round(amt, 1) AS debt_chowon,
       round(amt - LAG(amt) OVER (ORDER BY ym), 1) AS mom_change
FROM t ORDER BY ym DESC LIMIT 24
""")

show('7.2) 세입 회계별 5년 추이', """
WITH s AS (
    SELECT FSCL_YY, ACCT_NM,
           sum(Y_YY_DFN_KCUR_AMT) AS amt
    FROM revenue_budget WHERE SBUDG_DGR=0 AND ACCT_NM IS NOT NULL
    GROUP BY FSCL_YY, ACCT_NM
)
SELECT FSCL_YY, ACCT_NM, round(amt/1e6, 0) AS amt_eok
FROM s WHERE ACCT_NM IN ('일반회계')
ORDER BY FSCL_YY
""")

print('\n'+'#'*78); print('# 8. 디지털·AI 라벨 (분야 코드 + 부문 기반)'); print('#'*78)

# 텍스트 키워드 의존 줄이고 분야·부문 코드 기반
show('8.1) 정보통신·과학기술 부문 부처별 분포 (2026 본예산)', """
SELECT OFFC_NM, FLD_NM, SECT_NM,
       count(DISTINCT SACTV_NM) AS sactv_n,
       round(sum(Y_YY_DFN_KCUR_AMT)/1e6, 0) AS amt_eok
FROM expenditure_budget
WHERE FSCL_YY=2026 AND SBUDG_DGR=0
  AND (SECT_NM ILIKE '%정보통신%' OR SECT_NM ILIKE '%산업기술%'
       OR SECT_NM ILIKE '%과학기술%' OR SECT_NM ILIKE '%정보보호%'
       OR SECT_NM ILIKE '%정보화%' OR SECT_NM ILIKE '%연구개발%')
GROUP BY OFFC_NM, FLD_NM, SECT_NM
ORDER BY amt_eok DESC LIMIT 25
""")

# 시각화 4종
fig, ax = plt.subplots(figsize=(11,6))
df=fld_share[fld_share.FSCL_YY==2026].head(16)
ax.barh(df['FLD_NM'][::-1], df['amt_eok'][::-1], color='#1f77b4')
ax.set_xlabel('금액 (억원)')
ax.set_title('2026 본예산 — 16대 분야 분포')
plt.tight_layout(); plt.savefig(f'{FIG}/fld_share_2026.png', dpi=140); plt.close()

# 분야별 변화율 (2020 vs 2026)
df2=con.execute("""
WITH a AS (
    SELECT FLD_NM, sum(Y_YY_DFN_KCUR_AMT) AS y20
    FROM expenditure_budget WHERE SBUDG_DGR=0 AND FSCL_YY=2020 GROUP BY FLD_NM
),
b AS (
    SELECT FLD_NM, sum(Y_YY_DFN_KCUR_AMT) AS y26
    FROM expenditure_budget WHERE SBUDG_DGR=0 AND FSCL_YY=2026 GROUP BY FLD_NM
)
SELECT a.FLD_NM, (b.y26 - a.y20) / a.y20 * 100 AS chg
FROM a JOIN b USING (FLD_NM) ORDER BY chg DESC
""").fetchdf()
fig, ax = plt.subplots(figsize=(11,6))
colors=['#d62728' if c<20 else '#2ca02c' if c>80 else '#7f7f7f' for c in df2['chg']]
ax.barh(df2['FLD_NM'][::-1], df2['chg'][::-1], color=colors[::-1])
ax.set_xlabel('변화율 (%)')
ax.set_title('분야별 5년 본예산 변화율 (2020→2026)')
ax.axvline(0, color='black', lw=0.5)
plt.tight_layout(); plt.savefig(f'{FIG}/fld_growth.png', dpi=140); plt.close()

# 사업당 평균 금액 분포 시계열
df3=con.execute("""
WITH s AS (
    SELECT FSCL_YY, SACTV_NM, sum(Y_YY_DFN_KCUR_AMT) AS amt
    FROM expenditure_budget WHERE SBUDG_DGR=0 GROUP BY FSCL_YY, SACTV_NM
)
SELECT FSCL_YY,
       median(amt)/1e6 AS p50,
       quantile_cont(amt, 0.75)/1e6 AS p75,
       quantile_cont(amt, 0.25)/1e6 AS p25,
       quantile_cont(amt, 0.9)/1e6 AS p90
FROM s GROUP BY FSCL_YY ORDER BY FSCL_YY
""").fetchdf()
fig, ax = plt.subplots(figsize=(10,5))
ax.fill_between(df3['FSCL_YY'], df3['p25'], df3['p75'], alpha=0.3, color='#1f77b4', label='25-75 분위')
ax.plot(df3['FSCL_YY'], df3['p50'], 'o-', color='#1f77b4', label='중앙값')
ax.plot(df3['FSCL_YY'], df3['p90'], 's--', color='#d62728', alpha=0.6, label='90 분위')
ax.set_ylabel('사업당 금액 (억원, log)'); ax.set_yscale('log')
ax.set_xlabel('회계연도'); ax.set_title('사업당 평균 금액 분포 시계열')
ax.legend(); ax.grid(alpha=0.3)
plt.tight_layout(); plt.savefig(f'{FIG}/sactv_size_trend.png', dpi=140); plt.close()

# HHI 부처 집중도 시계열
df4=con.execute("""
WITH s AS (
    SELECT FSCL_YY, OFFC_NM, sum(Y_YY_DFN_KCUR_AMT) AS amt
    FROM expenditure_budget WHERE SBUDG_DGR=0 GROUP BY FSCL_YY, OFFC_NM
),
sh AS (
    SELECT FSCL_YY, OFFC_NM, amt / sum(amt) OVER (PARTITION BY FSCL_YY) AS share FROM s
)
SELECT FSCL_YY, sum(share*share) AS hhi FROM sh GROUP BY FSCL_YY ORDER BY FSCL_YY
""").fetchdf()
fig, ax = plt.subplots(figsize=(10,5))
ax.plot(df4['FSCL_YY'], df4['hhi'], 'o-', color='#9467bd', linewidth=2)
ax.set_ylabel('HHI'); ax.set_xlabel('회계연도')
ax.set_title('정부 본예산의 부처 집중도 (HHI) 시계열')
ax.grid(alpha=0.3)
plt.tight_layout(); plt.savefig(f'{FIG}/hhi_offc.png', dpi=140); plt.close()

# 채무 시계열
df5=con.execute("""
SELECT (CAST(OJ_YY AS INT)*100 + CAST(OJ_M AS INT)) AS ym,
       CAST(OJ_YY AS INT) + (CAST(OJ_M AS INT)-1)/12.0 AS yr,
       CAST(GOD_SUM_AMT AS DOUBLE) AS amt
FROM debt_monthly ORDER BY ym
""").fetchdf()
fig, ax = plt.subplots(figsize=(11,5))
ax.plot(df5['yr'], df5['amt'], '-', color='#d62728', linewidth=1.5)
ax.set_ylabel('국가채무 (조원)'); ax.set_xlabel('연도')
ax.set_title(f'월별 국가채무 시계열 ({df5.iloc[0]["yr"]:.1f} ~ {df5.iloc[-1]["yr"]:.1f})')
ax.grid(alpha=0.3)
plt.tight_layout(); plt.savefig(f'{FIG}/debt_monthly.png', dpi=140); plt.close()

print(f'\n시각화 5종 저장: {FIG}')
con.close()
