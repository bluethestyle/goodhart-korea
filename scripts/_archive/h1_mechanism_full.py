"""H1 메커니즘 회귀 + 추가 outcome 적재.

목적:
  1. 추가 KOSIS outcome (국토·지역=GRDP, 교통=자동차등록, 환경=폐기물) 적재
  2. H1 메커니즘 회귀: 게임화 강도 ~ 사업비 구성 (출연·운영·직접투자 등)
     gaming_it = α + β1·chooyeon_pct + β2·operating_pct + β3·direct_invest_pct + γ_t + ε
"""
import os, sys, io, json, time, urllib.request, urllib.parse
import duckdb
import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
for f in ['Malgun Gothic','NanumGothic','AppleGothic','Noto Sans CJK KR']:
    try: plt.rcParams['font.family']=f; break
    except: pass
plt.rcParams['axes.unicode_minus']=False

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, 'data', 'warehouse.duckdb')
FIG = os.path.join(ROOT, 'data', 'figs', 'h1_mech'); os.makedirs(FIG, exist_ok=True)
RES = os.path.join(ROOT, 'data', 'results')

KEY = 'ZTBmMWE5NDZlYjQ3MzkyZTg0YWFjOWNmNDBhNTIxZjc='
H = {'User-Agent':'Mozilla/5.0'}

def call_kosis(**params):
    p = {'method':'getList','apiKey':KEY,'format':'json','jsonVD':'Y', **params}
    qs = urllib.parse.urlencode(p)
    url = f'https://kosis.kr/openapi/Param/statisticsParameterData.do?{qs}'
    req = urllib.request.Request(url, headers=H)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode('utf-8'))
    except Exception as e:
        return {'_err': str(e)}

# === Step 1: 추가 outcome 적재 ===
print('='*70); print('Step 1: 추가 outcome 적재'); print('='*70)

# A. 국토·지역 — DT_1C82 지역내총부가가치 (전국 시계열)
print('\n[국토·지역] DT_1C82 지역내총부가가치 (전국)')
d = call_kosis(orgId='101', tblId='DT_1C82', itmId='T03', objL1='00', objL2='U10',
               prdSe='Y', newEstPrdCnt='20')
grdp_records = []
if isinstance(d, list):
    for r in d:
        try:
            grdp_records.append(('국토및지역개발', int(r['PRD_DE']), 'grdp_national',
                                 float(r['DT']) * 1e9, 'KOSIS_DT_1C82', 'KRW'))  # 백만원→원: ×1e6, 그러나 백만원 단위 자체 사용해도 OK. ×1e9는 잘못. 수정.
        except: pass
print(f'  rows: {len(grdp_records)}')

# 백만원 그대로 사용 (×1e6 적용은 추후 분석 시)
grdp_records = []
if isinstance(d, list):
    for r in d:
        try:
            grdp_records.append(('국토및지역개발', int(r['PRD_DE']), 'grdp_national',
                                 float(r['DT']), 'KOSIS_DT_1C82', '백만원'))
        except: pass
print(f'  최종 rows: {len(grdp_records)}')
import os
os.makedirs('data/external/kosis_data', exist_ok=True)
if isinstance(d, list):
    json.dump(d, open('data/external/kosis_data/grdp_national.json','w',encoding='utf-8'), ensure_ascii=False)

# === Step 2: indicator_panel에 추가 적재 ===
print('\n=== Step 2: indicator_panel 추가 적재 ===')
con = duckdb.connect(DB)

# grdp_national 추가
con.execute("DELETE FROM indicator_panel WHERE metric_code = 'grdp_national'")
con.execute("DELETE FROM indicator_metadata WHERE metric_code = 'grdp_national'")
if grdp_records:
    con.executemany(
        "INSERT INTO indicator_panel (fld_nm, year, metric_code, value, source, unit) VALUES (?, ?, ?, ?, ?, ?)",
        [(str(a),int(b),str(c),float(d),str(e),str(f)) for a,b,c,d,e,f in grdp_records]
    )
    con.execute("INSERT INTO indicator_metadata VALUES (?, ?, ?, ?, ?, ?)",
                ('grdp_national','지역내총부가가치(전국)','outcome',
                 'KOSIS DT_1C82 시도별 경제활동별 — 전국 총부가가치 명목',
                 'https://kosis.kr/statHtml/statHtml.do?orgId=101&tblId=DT_1C82', -1))

# === Step 3: H1 메커니즘 회귀 ===
print('\n' + '='*70); print('Step 3: H1 메커니즘 회귀'); print('='*70)

# 분야×연도 게임화 + 예산 구성 패널
df = con.execute("""
WITH gaming AS (SELECT fld_nm, year, value AS gaming FROM indicator_panel WHERE metric_code='amp_12m_norm'),
     b1 AS (SELECT fld_nm, year, value AS chooyeon_pct FROM indicator_panel WHERE metric_code='chooyeon_pct'),
     b2 AS (SELECT fld_nm, year, value AS local_pct  FROM indicator_panel WHERE metric_code='local_transfer_pct'),
     b3 AS (SELECT fld_nm, year, value AS personnel_pct FROM indicator_panel WHERE metric_code='personnel_pct'),
     b4 AS (SELECT fld_nm, year, value AS operating_pct FROM indicator_panel WHERE metric_code='operating_pct'),
     b5 AS (SELECT fld_nm, year, value AS direct_pct FROM indicator_panel WHERE metric_code='direct_invest_pct'),
     b6 AS (SELECT fld_nm, year, value AS budget_total FROM indicator_panel WHERE metric_code='budget_total')
SELECT g.fld_nm, g.year, g.gaming,
       b1.chooyeon_pct, b2.local_pct, b3.personnel_pct,
       b4.operating_pct, b5.direct_pct, b6.budget_total
FROM gaming g
LEFT JOIN b1 USING (fld_nm, year)
LEFT JOIN b2 USING (fld_nm, year)
LEFT JOIN b3 USING (fld_nm, year)
LEFT JOIN b4 USING (fld_nm, year)
LEFT JOIN b5 USING (fld_nm, year)
LEFT JOIN b6 USING (fld_nm, year)
WHERE g.fld_nm != '예비비'
ORDER BY fld_nm, year
""").fetchdf()
print(f'\n분야×연도 패널: {len(df)} 셀, {df["fld_nm"].nunique()} 분야')

# log(budget) 추가
df['ln_budget'] = np.log(df['budget_total'].clip(lower=1e6))

# Model 1: 단순 회귀 (예산 구성 → 게임화)
print('\n--- Model 1: gaming ~ chooyeon + operating + direct ---')
m1_data = df.dropna(subset=['gaming','chooyeon_pct','operating_pct','direct_pct'])
X = sm.add_constant(m1_data[['chooyeon_pct','operating_pct','direct_pct']])
y = m1_data['gaming']
m1 = sm.OLS(y, X.astype(float)).fit(cov_type='cluster', cov_kwds={'groups': m1_data['fld_nm']})
print(f'N={int(m1.nobs)}, R²={m1.rsquared:.3f}')
for v in ['const','chooyeon_pct','operating_pct','direct_pct']:
    if v in m1.params.index:
        sig = '***' if m1.pvalues[v]<0.01 else '**' if m1.pvalues[v]<0.05 else '*' if m1.pvalues[v]<0.1 else ''
        print(f'  {v:18}: β={m1.params[v]:>+.4f} se={m1.bse[v]:.4f} p={m1.pvalues[v]:.3f} {sig}')

# Model 2: + 분야 더미 + 연도 더미
print('\n--- Model 2: + 분야 FE + 연도 FE ---')
fld_d = pd.get_dummies(m1_data['fld_nm'], prefix='fld', drop_first=True).astype(float)
yr_d  = pd.get_dummies(m1_data['year'].astype(int), prefix='yr', drop_first=True).astype(float)
X2 = pd.concat([m1_data[['chooyeon_pct','operating_pct','direct_pct']], fld_d, yr_d], axis=1)
X2 = sm.add_constant(X2).astype(float)
m2 = sm.OLS(y.astype(float), X2).fit(cov_type='cluster', cov_kwds={'groups': m1_data['fld_nm']})
print(f'N={int(m2.nobs)}, R²={m2.rsquared:.3f}')
for v in ['chooyeon_pct','operating_pct','direct_pct']:
    if v in m2.params.index:
        sig = '***' if m2.pvalues[v]<0.01 else '**' if m2.pvalues[v]<0.05 else '*' if m2.pvalues[v]<0.1 else ''
        print(f'  {v:18}: β={m2.params[v]:>+.4f} se={m2.bse[v]:.4f} p={m2.pvalues[v]:.3f} {sig}')

# Model 3: + 예산 규모 (log)
print('\n--- Model 3: + ln(budget_total) ---')
m3_data = df.dropna(subset=['gaming','chooyeon_pct','operating_pct','direct_pct','ln_budget'])
X3_base = m3_data[['chooyeon_pct','operating_pct','direct_pct','ln_budget']]
fld_d = pd.get_dummies(m3_data['fld_nm'], prefix='fld', drop_first=True).astype(float)
yr_d  = pd.get_dummies(m3_data['year'].astype(int), prefix='yr', drop_first=True).astype(float)
X3 = pd.concat([X3_base, fld_d, yr_d], axis=1)
X3 = sm.add_constant(X3).astype(float)
m3 = sm.OLS(m3_data['gaming'].astype(float), X3).fit(cov_type='cluster', cov_kwds={'groups': m3_data['fld_nm']})
print(f'N={int(m3.nobs)}, R²={m3.rsquared:.3f}')
for v in ['chooyeon_pct','operating_pct','direct_pct','ln_budget']:
    if v in m3.params.index:
        sig = '***' if m3.pvalues[v]<0.01 else '**' if m3.pvalues[v]<0.05 else '*' if m3.pvalues[v]<0.1 else ''
        print(f'  {v:18}: β={m3.params[v]:>+.4f} se={m3.bse[v]:.4f} p={m3.pvalues[v]:.3f} {sig}')

# === Step 4: 시각화 — 메커니즘 산점도 ===
print('\n=== Step 4: 메커니즘 시각화 ===')

fig, axes = plt.subplots(1, 3, figsize=(16, 5))
mechs = [('chooyeon_pct', '출연금 비중', '#d62728'),
         ('operating_pct', '운영비 비중', '#ff7f0e'),
         ('direct_pct', '직접투자 비중', '#2ca02c')]

for ax, (col, label, color) in zip(axes, mechs):
    g = df.dropna(subset=['gaming', col])
    ax.scatter(g[col], g['gaming'], s=40, color=color, alpha=0.5, edgecolor='black', linewidth=0.3)
    # 회귀선
    if len(g) >= 5:
        z = np.polyfit(g[col], g['gaming'], 1)
        x_range = np.linspace(g[col].min(), g[col].max(), 50)
        ax.plot(x_range, np.poly1d(z)(x_range), '--', color=color, linewidth=2)
        rho = g[[col,'gaming']].corr().iloc[0,1]
        ax.set_title(f'{label}  (n={len(g)}, ρ={rho:+.3f})', fontsize=11)
    ax.set_xlabel(label); ax.set_ylabel('게임화 강도 (amp_12m_norm)')
    ax.grid(alpha=0.3)
plt.suptitle('H1 메커니즘 — 사업비 구성 vs 게임화 강도', fontsize=13)
plt.tight_layout()
plt.savefig(f'{FIG}/H1_mech_scatter.png', dpi=140)
plt.close()
print(f'saved {FIG}/H1_mech_scatter.png')

# 결과 저장
m3_data.to_csv(f'{RES}/H1_mechanism_panel.csv', index=False, encoding='utf-8-sig')
print('saved H1_mechanism_panel.csv')

con.close()
