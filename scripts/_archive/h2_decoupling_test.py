"""H2 Decoupling 가설 검증: 게임화 강도 ↑ → 결과지표 ↓?

전제: indicator_panel에 다음이 적재됨
  - gaming 카테고리: amp_12m_norm, hhi_period, gini_period, q1_pct, dec_pct
  - budget 카테고리: budget_total, budget_yoy_growth_pct, chooyeon_pct, ...
  - outcome 카테고리: rd_total, gdp, patents, life_expectancy, ... (KOSIS 적재 후)

분석:
  M1. 단순 상관 — gaming × outcome (분야 평균)
  M2. Two-way FE 패널회귀 — outcome_it = α + β·gaming_i + γ_t + δ_i + ε
  M3. Fixed effects 분야 더미 + 연도 더미
"""
import os, sys, io, duckdb
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.iolib.summary2 import summary_col

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, 'data', 'warehouse.duckdb')
con = duckdb.connect(DB, read_only=True)

GAMING = 'amp_12m_norm'  # 메인 게임화 지표

# 결과 변수 후보 (외부 데이터 적재 후 채워짐)
OUTCOMES = ['rd_total','gdp','life_expectancy','patents','tourists',
            'industrial_production','poverty_rate','co2_emission']

def load_panel(gaming_metric, outcome_metric):
    return con.execute("""
        WITH g AS (
          SELECT fld_nm, year, value AS gaming
          FROM indicator_panel
          WHERE metric_code = ? AND fld_nm != '예비비'
        ),
        o AS (
          SELECT fld_nm, year, value AS outcome
          FROM indicator_panel
          WHERE metric_code = ?
        )
        SELECT g.fld_nm, g.year, g.gaming, o.outcome
        FROM g JOIN o USING (fld_nm, year)
    """, [gaming_metric, outcome_metric]).fetchdf()

def m1_correlation(df):
    if len(df) < 5: return None
    return df[['gaming','outcome']].corr().iloc[0,1]

def m2_panel_fe(df):
    if len(df) < 10: return None
    # 분야 더미
    fld_dummies = pd.get_dummies(df['fld_nm'], prefix='fld', drop_first=True).astype(float)
    yr_dummies  = pd.get_dummies(df['year'].astype(int), prefix='yr', drop_first=True).astype(float)
    X = pd.concat([df[['gaming']], fld_dummies, yr_dummies], axis=1)
    X = sm.add_constant(X)
    y = df['outcome']
    try:
        model = sm.OLS(y, X.astype(float), missing='drop').fit(cov_type='cluster', cov_kwds={'groups': df['fld_nm']})
        return {
            'beta':    model.params['gaming'],
            'se':      model.bse['gaming'],
            'p':       model.pvalues['gaming'],
            'r2':      model.rsquared,
            'n':       int(model.nobs),
        }
    except Exception as e:
        return {'err': str(e)}

if __name__ == '__main__':
    # 어떤 outcome metric_code가 indicator_panel에 있는지 점검
    available = con.execute("""
        SELECT m.metric_code, m.metric_nm, count(p.value) AS n
        FROM indicator_metadata m
        LEFT JOIN indicator_panel p USING (metric_code)
        WHERE m.category = 'outcome'
        GROUP BY m.metric_code, m.metric_nm
        ORDER BY n DESC
    """).fetchdf()
    print('=== indicator_panel 내 outcome 변수 ===')
    print(available.to_string(index=False) if not available.empty else '(아직 적재된 outcome 없음)')

    if available.empty:
        print('\nKOSIS 등에서 outcome 데이터 적재 후 실행하세요.')
        sys.exit(0)

    # 모든 outcome × 게임화 페어
    print(f'\n=== 단순 상관 (gaming = {GAMING}) ===')
    for _, r in available.iterrows():
        df = load_panel(GAMING, r['metric_code'])
        if df.empty:
            print(f'  {r["metric_code"]}: 데이터 없음')
            continue
        rho = m1_correlation(df)
        print(f'  {r["metric_code"]:20} (n={len(df)}): corr={rho:.3f}')

    print(f'\n=== Two-way FE 패널 회귀 ===')
    for _, r in available.iterrows():
        df = load_panel(GAMING, r['metric_code'])
        if df.empty: continue
        res = m2_panel_fe(df)
        if res and 'err' not in res:
            sig = '***' if res['p']<0.01 else '**' if res['p']<0.05 else '*' if res['p']<0.1 else ''
            print(f'  {r["metric_code"]:20} β={res["beta"]:>10.4f} (se={res["se"]:.4f}) p={res["p"]:.3f} {sig}  R²={res["r2"]:.3f} n={res["n"]}')

    con.close()
