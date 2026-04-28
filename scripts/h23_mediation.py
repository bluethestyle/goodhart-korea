"""H23: 매개 효과 분석 (Mediation Analysis)
출연금 비중(chooyeon_pct) → 게임화(amp_12m_norm) → outcome

Baron & Kenny (1986) / Hayes PROCESS macro 방식:
  c  path : Y = β0 + c·X + ε                (총효과)
  a  path : M = α0 + a·X + ε                (X→M)
  b/c' path: Y = γ0 + c'·X + b·M + ε       (직접효과 + b)
  간접효과 ab = a × b
  Sobel test + Bootstrap CI (5000회)

OUTCOME_MAP (14 분야, 예비비·국방 제외, 6개 교체 적용):
  사회복지 wealth_gini, 보건 life_expectancy, 과기 patent_apps_total,
  산업 industry_production_index, 관광 foreign_tourists_total,
  교육 imd_edu_rank, 국토 housing_supply, 행정 fiscal_indep_natl,
  농림 farm_income, 교통 traffic_deaths, 환경 ghg_total,
  통신 broadband_per_100, 통일외교 oda_total, 공공질서 crime_occurrence

산출:
  scripts/h23_mediation.py
  data/figs/h23/H23_mediation_diagram.png
  data/results/H23_mediation_estimates.csv
"""
import os, sys, io, warnings
import numpy as np
import pandas as pd
import duckdb
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
from scipy import stats

warnings.filterwarnings('ignore')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ── 경로 ──
ROOT    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB      = os.path.join(ROOT, 'data', 'warehouse.duckdb')
OUT_DIR = os.path.join(ROOT, 'data', 'figs', 'h23')
RES_DIR = os.path.join(ROOT, 'data', 'results')
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(RES_DIR, exist_ok=True)

# ── 한국어 폰트 ──
KFONT = None
for f in ['Malgun Gothic', 'Noto Sans CJK KR', 'AppleGothic']:
    if any(f in fn.name for fn in mpl.font_manager.fontManager.ttflist):
        mpl.rcParams['font.family'] = f
        KFONT = f
        break
mpl.rcParams['axes.unicode_minus'] = False
RNG = np.random.default_rng(42)

MAX_PX = 1800
DPI    = 130

# ── OUTCOME_MAP (14 분야, 예비비·국방 제외) ──
OUTCOME_MAP = {
    '사회복지':               'wealth_gini',
    '보건':                   'life_expectancy',
    '과학기술':               'patent_apps_total',
    '산업·중소기업및에너지':   'industry_production_index',
    '문화및관광':             'foreign_tourists_total',
    '교육':                   'imd_edu_rank',
    '국토및지역개발':         'housing_supply',
    '일반·지방행정':          'fiscal_indep_natl',
    '농림수산':               'farm_income',
    '교통및물류':             'traffic_deaths',
    '환경':                   'ghg_total',
    '통신':                   'broadband_per_100',
    '통일·외교':              'oda_total',
    '공공질서및안전':          'crime_occurrence',
}

# 분야 표시용 단축명
FLD_SHORT = {
    '사회복지':               '사회복지',
    '보건':                   '보건',
    '과학기술':               '과학기술',
    '산업·중소기업및에너지':   '산업에너지',
    '문화및관광':             '문화관광',
    '교육':                   '교육',
    '국토및지역개발':         '국토개발',
    '일반·지방행정':          '일반행정',
    '농림수산':               '농림수산',
    '교통및물류':             '교통물류',
    '환경':                   '환경',
    '통신':                   'ICT통신',
    '통일·외교':              '통일외교',
    '공공질서및안전':          '공공질서',
}


# ================================================================
# 1. 데이터 로드
# ================================================================
print('='*70)
print('Step 1: 데이터 로드')
print('='*70)

con = duckdb.connect(DB, read_only=True)

all_metrics = (
    ['chooyeon_pct', 'amp_12m_norm']
    + list(OUTCOME_MAP.values())
)
metric_list = "', '".join(sorted(set(all_metrics)))

panel_raw = con.execute(f"""
    SELECT fld_nm, year, metric_code, value
    FROM indicator_panel
    WHERE metric_code IN ('{metric_list}')
    ORDER BY fld_nm, year, metric_code
""").fetchdf()
con.close()

wide = panel_raw.pivot_table(
    index=['fld_nm', 'year'], columns='metric_code', values='value'
).reset_index()
print(f'wide shape: {wide.shape}, 분야: {wide["fld_nm"].nunique()}')


# ================================================================
# 2. OLS 헬퍼 함수
# ================================================================
def ols_simple(y, x):
    """단순 OLS: scalar (coef, se, t, p, r2)"""
    mask = np.isfinite(x) & np.isfinite(y)
    if mask.sum() < 4:
        return dict(coef=np.nan, se=np.nan, t=np.nan, p=np.nan, r2=np.nan, n=mask.sum())
    xm = x[mask];  ym = y[mask]
    n = len(xm)
    X = np.column_stack([np.ones(n), xm])
    try:
        beta = np.linalg.lstsq(X, ym, rcond=None)[0]
        yhat = X @ beta
        resid = ym - yhat
        sse   = resid @ resid
        sst   = np.sum((ym - ym.mean())**2)
        r2    = 1 - sse/sst if sst > 0 else np.nan
        s2    = sse / (n - 2)
        XtXi  = np.linalg.inv(X.T @ X)
        se_b  = np.sqrt(s2 * XtXi[1, 1])
        t_val = beta[1] / se_b if se_b > 0 else np.nan
        p_val = 2 * stats.t.sf(abs(t_val), df=n-2) if np.isfinite(t_val) else np.nan
        return dict(coef=beta[1], se=se_b, t=t_val, p=p_val, r2=r2, n=n)
    except Exception:
        return dict(coef=np.nan, se=np.nan, t=np.nan, p=np.nan, r2=np.nan, n=mask.sum())


def ols_multiple(y, x1, x2):
    """다중 OLS: (coef_x1, se_x1, t_x1, p_x1, coef_x2, se_x2, t_x2, p_x2, r2, n)"""
    mask = np.isfinite(x1) & np.isfinite(x2) & np.isfinite(y)
    if mask.sum() < 5:
        nan = np.nan
        return dict(
            coef_x1=nan, se_x1=nan, t_x1=nan, p_x1=nan,
            coef_x2=nan, se_x2=nan, t_x2=nan, p_x2=nan,
            r2=nan, n=mask.sum()
        )
    x1m = x1[mask]; x2m = x2[mask]; ym = y[mask]
    n = len(ym)
    X = np.column_stack([np.ones(n), x1m, x2m])
    try:
        beta = np.linalg.lstsq(X, ym, rcond=None)[0]
        yhat  = X @ beta
        resid = ym - yhat
        sse   = resid @ resid
        sst   = np.sum((ym - ym.mean())**2)
        r2    = 1 - sse/sst if sst > 0 else np.nan
        s2    = sse / (n - 3)
        XtXi  = np.linalg.inv(X.T @ X)
        se1   = np.sqrt(s2 * XtXi[1, 1])
        se2   = np.sqrt(s2 * XtXi[2, 2])
        t1    = beta[1]/se1 if se1 > 0 else np.nan
        t2    = beta[2]/se2 if se2 > 0 else np.nan
        p1    = 2 * stats.t.sf(abs(t1), df=n-3) if np.isfinite(t1) else np.nan
        p2    = 2 * stats.t.sf(abs(t2), df=n-3) if np.isfinite(t2) else np.nan
        return dict(
            coef_x1=beta[1], se_x1=se1, t_x1=t1, p_x1=p1,
            coef_x2=beta[2], se_x2=se2, t_x2=t2, p_x2=p2,
            r2=r2, n=n
        )
    except Exception:
        nan = np.nan
        return dict(
            coef_x1=nan, se_x1=nan, t_x1=nan, p_x1=nan,
            coef_x2=nan, se_x2=nan, t_x2=nan, p_x2=nan,
            r2=nan, n=mask.sum()
        )


def bootstrap_ab(y, x, m, n_boot=5000, ci=95):
    """Bootstrap CI for indirect effect ab = a×b"""
    mask = np.isfinite(x) & np.isfinite(m) & np.isfinite(y)
    if mask.sum() < 5:
        return np.nan, np.nan, np.nan
    xv = x[mask]; mv = m[mask]; yv = y[mask]
    n  = len(xv)
    ab_samples = []
    for _ in range(n_boot):
        idx = RNG.integers(0, n, size=n)
        xa, ma, ya = xv[idx], mv[idx], yv[idx]
        ra = ols_simple(ma, xa)
        rb = ols_multiple(ya, xa, ma)
        if np.isfinite(ra['coef']) and np.isfinite(rb['coef_x2']):
            ab_samples.append(ra['coef'] * rb['coef_x2'])
    if len(ab_samples) < 100:
        return np.nan, np.nan, np.nan
    ab_arr = np.array(ab_samples)
    lo = (100 - ci) / 2
    hi = 100 - lo
    return np.mean(ab_arr), np.percentile(ab_arr, lo), np.percentile(ab_arr, hi)


def sobel_z(a, se_a, b, se_b):
    """Sobel z-통계량"""
    denom = np.sqrt(a**2 * se_b**2 + b**2 * se_a**2)
    if denom == 0 or not np.isfinite(denom):
        return np.nan, np.nan
    z = (a * b) / denom
    p = 2 * stats.norm.sf(abs(z))
    return z, p


# ================================================================
# 3. 분야별 매개 분석
# ================================================================
print('\n' + '='*70)
print('Step 3: 분야별 매개 분석')
print('='*70)

results = []

for fld, oc_metric in OUTCOME_MAP.items():
    sub = wide[wide['fld_nm'] == fld].copy().sort_values('year')

    # 필요 컬럼 존재 확인
    missing = [c for c in ['chooyeon_pct', 'amp_12m_norm', oc_metric] if c not in sub.columns]
    if missing:
        print(f'  [SKIP] {fld}: 컬럼 없음 {missing}')
        continue

    # 공통 연도 (모두 유효한 행)
    sub_valid = sub[['year', 'chooyeon_pct', 'amp_12m_norm', oc_metric]].dropna()
    n_obs = len(sub_valid)
    print(f'  {fld} ({oc_metric}): n={n_obs}')

    if n_obs < 5:
        print(f'    → 데이터 부족 (n<5), SKIP')
        results.append({'fld_nm': fld, 'fld_short': FLD_SHORT[fld],
                        'outcome': oc_metric, 'n': n_obs,
                        **{k: np.nan for k in ['a','se_a','b','se_b','c','se_c',
                                                'c_prime','se_c_prime',
                                                'ab','ab_boot','ab_lo95','ab_hi95',
                                                'sobel_z','sobel_p',
                                                'mediation_ratio','sig_ab']}})
        continue

    X = sub_valid['chooyeon_pct'].values
    M = sub_valid['amp_12m_norm'].values
    Y = sub_valid[oc_metric].values

    # --- path c (총효과): Y ~ X ---
    rc = ols_simple(Y, X)
    c_coef = rc['coef'];  c_se = rc['se']

    # --- path a: M ~ X ---
    ra = ols_simple(M, X)
    a_coef = ra['coef'];  a_se = ra['se']

    # --- path b/c' (직접효과): Y ~ X + M ---
    rb = ols_multiple(Y, X, M)
    c_prime = rb['coef_x1'];  c_prime_se = rb['se_x1']
    b_coef  = rb['coef_x2'];  b_se       = rb['se_x2']

    # --- 간접효과 ab ---
    ab = a_coef * b_coef

    # --- Sobel ---
    s_z, s_p = (np.nan, np.nan)
    if all(np.isfinite([a_coef, a_se, b_coef, b_se])):
        s_z, s_p = sobel_z(a_coef, a_se, b_coef, b_se)

    # --- Bootstrap CI ---
    ab_boot, ab_lo95, ab_hi95 = bootstrap_ab(Y, X, M, n_boot=5000)

    # --- 매개비율 ab/c ---
    med_ratio = ab / c_coef if (np.isfinite(c_coef) and c_coef != 0) else np.nan

    # 유의 여부: bootstrap CI 0 포함 여부
    sig_ab = 0
    if np.isfinite(ab_lo95) and np.isfinite(ab_hi95):
        sig_ab = 1 if (ab_lo95 > 0 or ab_hi95 < 0) else 0

    print(f'    c={c_coef:.4f}  a={a_coef:.4f}  b={b_coef:.4f}  c\'={c_prime:.4f}')
    print(f'    ab={ab:.4f}  Sobel_z={s_z:.3f}  Sobel_p={s_p:.3f}')
    print(f'    Boot CI=[{ab_lo95:.4f}, {ab_hi95:.4f}]  med_ratio={med_ratio:.3f}')

    results.append({
        'fld_nm':       fld,
        'fld_short':    FLD_SHORT[fld],
        'outcome':      oc_metric,
        'n':            n_obs,
        'a':            a_coef,
        'se_a':         a_se,
        'b':            b_coef,
        'se_b':         b_se,
        'c':            c_coef,
        'se_c':         c_se,
        'c_prime':      c_prime,
        'se_c_prime':   c_prime_se,
        'ab':           ab,
        'ab_boot':      ab_boot,
        'ab_lo95':      ab_lo95,
        'ab_hi95':      ab_hi95,
        'sobel_z':      s_z,
        'sobel_p':      s_p,
        'mediation_ratio': med_ratio,
        'sig_ab':       sig_ab,
    })

res_df = pd.DataFrame(results)

# ================================================================
# 4. Pooled 분야 FE 매개 분석
# ================================================================
print('\n' + '='*70)
print('Step 4: Pooled 분야 FE 매개 분석')
print('='*70)

pool_rows = []
for fld, oc_metric in OUTCOME_MAP.items():
    sub = wide[wide['fld_nm'] == fld][['year', 'chooyeon_pct', 'amp_12m_norm', oc_metric]].dropna()
    if len(sub) >= 5:
        # Y를 표준화하여 분야간 스케일 차이 흡수
        y_std = sub[oc_metric].std()
        sub['Y_std'] = (sub[oc_metric] - sub[oc_metric].mean()) / y_std if y_std > 0 else np.nan
        sub['X_std'] = (sub['chooyeon_pct'] - sub['chooyeon_pct'].mean()) / sub['chooyeon_pct'].std() if sub['chooyeon_pct'].std() > 0 else np.nan
        sub['M_std'] = (sub['amp_12m_norm'] - sub['amp_12m_norm'].mean()) / sub['amp_12m_norm'].std() if sub['amp_12m_norm'].std() > 0 else np.nan
        sub['fld_nm'] = fld
        pool_rows.append(sub)

if pool_rows:
    pool_df = pd.concat(pool_rows, ignore_index=True)
    pool_valid = pool_df.dropna(subset=['X_std', 'M_std', 'Y_std'])
    n_pool = len(pool_valid)
    print(f'  Pooled N = {n_pool}')

    # FE 더미 추가 (분야 고정효과)
    flds_uniq = pool_valid['fld_nm'].unique()
    X_pool = pool_valid['X_std'].values
    M_pool = pool_valid['M_std'].values
    Y_pool = pool_valid['Y_std'].values
    fld_codes = pd.Categorical(pool_valid['fld_nm']).codes

    # path a with FE: M ~ X + fld_FE
    X_fe = np.column_stack([np.ones(n_pool), X_pool] +
                           [(fld_codes == i).astype(float) for i in range(1, len(flds_uniq))])
    try:
        a_fe = np.linalg.lstsq(X_fe, M_pool, rcond=None)[0]
        resid_a = M_pool - X_fe @ a_fe
        sse_a   = resid_a @ resid_a
        df_a    = n_pool - X_fe.shape[1]
        s2_a    = sse_a / df_a
        XtXi_a  = np.linalg.pinv(X_fe.T @ X_fe)
        se_a_fe = np.sqrt(s2_a * XtXi_a[1,1])
        a_pool  = a_fe[1]
        t_a_pool = a_pool / se_a_fe
        p_a_pool = 2 * stats.t.sf(abs(t_a_pool), df=df_a)
    except Exception as e:
        print(f'  path a FE 실패: {e}')
        a_pool = se_a_fe = t_a_pool = p_a_pool = np.nan

    # path b/c' with FE: Y ~ X + M + fld_FE
    XM_fe = np.column_stack([np.ones(n_pool), X_pool, M_pool] +
                            [(fld_codes == i).astype(float) for i in range(1, len(flds_uniq))])
    try:
        bcp_fe = np.linalg.lstsq(XM_fe, Y_pool, rcond=None)[0]
        resid_b = Y_pool - XM_fe @ bcp_fe
        sse_b   = resid_b @ resid_b
        df_b    = n_pool - XM_fe.shape[1]
        s2_b    = sse_b / df_b
        XtXi_b  = np.linalg.pinv(XM_fe.T @ XM_fe)
        c_prime_pool = bcp_fe[1]
        b_pool       = bcp_fe[2]
        se_cp_pool   = np.sqrt(s2_b * XtXi_b[1,1])
        se_b_pool    = np.sqrt(s2_b * XtXi_b[2,2])
        t_cp_pool    = c_prime_pool / se_cp_pool if se_cp_pool > 0 else np.nan
        t_b_pool     = b_pool / se_b_pool if se_b_pool > 0 else np.nan
        p_cp_pool    = 2 * stats.t.sf(abs(t_cp_pool), df=df_b)
        p_b_pool     = 2 * stats.t.sf(abs(t_b_pool), df=df_b)
    except Exception as e:
        print(f'  path b/c\' FE 실패: {e}')
        c_prime_pool = b_pool = se_cp_pool = se_b_pool = np.nan
        t_cp_pool = t_b_pool = p_cp_pool = p_b_pool = np.nan

    # path c with FE: Y ~ X + fld_FE
    Xc_fe = np.column_stack([np.ones(n_pool), X_pool] +
                            [(fld_codes == i).astype(float) for i in range(1, len(flds_uniq))])
    try:
        c_fe = np.linalg.lstsq(Xc_fe, Y_pool, rcond=None)[0]
        resid_c = Y_pool - Xc_fe @ c_fe
        sse_c   = resid_c @ resid_c
        df_c    = n_pool - Xc_fe.shape[1]
        s2_c    = sse_c / df_c
        XtXi_c  = np.linalg.pinv(Xc_fe.T @ Xc_fe)
        c_pool  = c_fe[1]
        se_c_pool = np.sqrt(s2_c * XtXi_c[1,1])
        t_c_pool  = c_pool / se_c_pool if se_c_pool > 0 else np.nan
        p_c_pool  = 2 * stats.t.sf(abs(t_c_pool), df=df_c)
    except Exception as e:
        print(f'  path c FE 실패: {e}')
        c_pool = se_c_pool = t_c_pool = p_c_pool = np.nan

    ab_pool = a_pool * b_pool if all(np.isfinite([a_pool, b_pool])) else np.nan
    sz_pool, sp_pool = (np.nan, np.nan)
    if all(np.isfinite([a_pool, se_a_fe, b_pool, se_b_pool])):
        sz_pool, sp_pool = sobel_z(a_pool, se_a_fe, b_pool, se_b_pool)
    med_ratio_pool = ab_pool / c_pool if (np.isfinite(c_pool) and c_pool != 0) else np.nan

    print(f'  c={c_pool:.4f}  a={a_pool:.4f}  b={b_pool:.4f}  c\'={c_prime_pool:.4f}')
    print(f'  ab={ab_pool:.4f}  Sobel_z={sz_pool:.3f}  p={sp_pool:.3f}')
    print(f'  매개비율={med_ratio_pool:.3f}')

    pool_result = {
        'fld_nm': 'POOLED (FE)', 'fld_short': 'POOLED',
        'outcome': 'standardized', 'n': n_pool,
        'a': a_pool, 'se_a': se_a_fe,
        'b': b_pool, 'se_b': se_b_pool,
        'c': c_pool, 'se_c': se_c_pool,
        'c_prime': c_prime_pool, 'se_c_prime': se_cp_pool,
        'ab': ab_pool, 'ab_boot': np.nan, 'ab_lo95': np.nan, 'ab_hi95': np.nan,
        'sobel_z': sz_pool, 'sobel_p': sp_pool,
        'mediation_ratio': med_ratio_pool, 'sig_ab': np.nan,
    }
    res_df = pd.concat([res_df, pd.DataFrame([pool_result])], ignore_index=True)


# ================================================================
# 5. CSV 저장
# ================================================================
out_csv = os.path.join(RES_DIR, 'H23_mediation_estimates.csv')
res_df.to_csv(out_csv, index=False, encoding='utf-8-sig')
print(f'\n결과 저장: {out_csv}')

# 결과 출력
print('\n=== 분야별 매개 분석 요약 ===')
cols_show = ['fld_short','outcome','n','a','b','c','c_prime','ab','sobel_z','sobel_p',
             'ab_lo95','ab_hi95','mediation_ratio','sig_ab']
print(res_df[cols_show].round(4).to_string(index=False))


# ================================================================
# 6. 시각화 — H23_mediation_diagram.png
# ================================================================
print('\n' + '='*70)
print('Step 6: 시각화')
print('='*70)

plot_df = res_df[res_df['fld_nm'] != 'POOLED (FE)'].copy()
plot_df = plot_df.dropna(subset=['a','b','c','c_prime','ab'])
plot_df = plot_df.reset_index(drop=True)

n_fld = len(plot_df)

# ── 표준화: 분야 간 스케일 통일 (Z-score of ab,c,c' per-field for display) ──
# 시각화에는 표준화 계수 사용 (X,M,Y 각각 Z-score 후 재계산)
def zcoef(y, x):
    """표준화 계수 (Beta): x→y에서 beta_std = beta_raw * (sx/sy)"""
    mask = np.isfinite(x) & np.isfinite(y)
    if mask.sum() < 4:
        return np.nan, np.nan, np.nan, np.nan
    sx, sy = x[mask].std(), y[mask].std()
    if sx == 0 or sy == 0:
        return np.nan, np.nan, np.nan, np.nan
    xs = (x[mask] - x[mask].mean()) / sx
    ys = (y[mask] - y[mask].mean()) / sy
    n = len(xs)
    Xm = np.column_stack([np.ones(n), xs])
    b  = np.linalg.lstsq(Xm, ys, rcond=None)[0]
    resid = ys - Xm @ b
    sse   = resid @ resid
    s2    = sse / (n-2)
    XtXi  = np.linalg.inv(Xm.T @ Xm)
    se    = np.sqrt(s2 * XtXi[1,1])
    t_val = b[1] / se if se > 0 else np.nan
    p_val = 2 * stats.t.sf(abs(t_val), df=n-2) if np.isfinite(t_val) else np.nan
    return b[1], se, t_val, p_val

def zcoef2(y, x1, x2):
    mask = np.isfinite(x1) & np.isfinite(x2) & np.isfinite(y)
    if mask.sum() < 5:
        return (np.nan,)*8
    sx1, sx2, sy = x1[mask].std(), x2[mask].std(), y[mask].std()
    if sx1==0 or sx2==0 or sy==0:
        return (np.nan,)*8
    x1s = (x1[mask]-x1[mask].mean())/sx1
    x2s = (x2[mask]-x2[mask].mean())/sx2
    ys  = (y[mask] -y[mask].mean())/sy
    n   = len(ys)
    Xm  = np.column_stack([np.ones(n), x1s, x2s])
    b   = np.linalg.lstsq(Xm, ys, rcond=None)[0]
    resid = ys - Xm @ b
    s2  = (resid @ resid) / (n-3)
    XtXi = np.linalg.pinv(Xm.T @ Xm)
    se1  = np.sqrt(s2*XtXi[1,1]); se2 = np.sqrt(s2*XtXi[2,2])
    t1   = b[1]/se1 if se1>0 else np.nan
    t2   = b[2]/se2 if se2>0 else np.nan
    p1   = 2*stats.t.sf(abs(t1), df=n-3) if np.isfinite(t1) else np.nan
    p2   = 2*stats.t.sf(abs(t2), df=n-3) if np.isfinite(t2) else np.nan
    return b[1], se1, t1, p1, b[2], se2, t2, p2

# 표준화 계수 계산
std_rows = []
for fld, oc_metric in OUTCOME_MAP.items():
    sub = wide[wide['fld_nm'] == fld][
        ['year', 'chooyeon_pct', 'amp_12m_norm', oc_metric]].dropna()
    if len(sub) < 5 or oc_metric not in sub.columns:
        std_rows.append({'fld_nm': fld, 'fld_short': FLD_SHORT[fld],
                         'outcome': oc_metric,
                         'a_std':np.nan,'b_std':np.nan,'c_std':np.nan,
                         'c_prime_std':np.nan,'ab_std':np.nan,
                         'p_sobel':np.nan,'sig_sobel':0})
        continue
    X = sub['chooyeon_pct'].values
    M = sub['amp_12m_norm'].values
    Y = sub[oc_metric].values
    a_s, *_ = zcoef(M, X)
    c_s, *_ = zcoef(Y, X)
    cp_std, _, _, _, b_s, se_b_s, _, p_b_s = zcoef2(Y, X, M)
    ab_s = a_s * b_s if all(np.isfinite([a_s, b_s])) else np.nan
    # Sobel p (원래 값에서 가져옴)
    row_orig = res_df[res_df['fld_nm'] == fld]
    p_sob = float(row_orig['sobel_p'].values[0]) if len(row_orig) else np.nan
    sig_s = 1 if (np.isfinite(p_sob) and p_sob < 0.05) else 0
    std_rows.append({'fld_nm': fld, 'fld_short': FLD_SHORT[fld],
                     'outcome': oc_metric,
                     'a_std': a_s, 'b_std': b_s, 'c_std': c_s,
                     'c_prime_std': cp_std, 'ab_std': ab_s,
                     'p_sobel': p_sob, 'sig_sobel': sig_s})

std_df = pd.DataFrame(std_rows).dropna(subset=['a_std','b_std','c_std','ab_std'])
std_df = std_df.reset_index(drop=True)

def sig_color(sig, ab):
    if sig == 1:
        return '#E74C3C' if ab > 0 else '#2980B9'
    return '#95A5A6'

# ── Figure ──
fig_w = min(MAX_PX, 1800) / DPI
fig_h = fig_w * 0.82
fig = plt.figure(figsize=(fig_w, fig_h), dpi=DPI)
fig.patch.set_facecolor('#FAFAFA')

# 레이아웃: 3열 상단 + 1열 하단 전체
gs = fig.add_gridspec(2, 3, hspace=0.52, wspace=0.38,
                       left=0.07, right=0.97, top=0.88, bottom=0.12)
ax_a  = fig.add_subplot(gs[0, 0])
ax_b  = fig.add_subplot(gs[0, 1])
ax_cp = fig.add_subplot(gs[0, 2])
ax_ab = fig.add_subplot(gs[1, :])

flds_s = std_df['fld_short'].tolist()
n_s    = len(std_df)
xp     = np.arange(n_s)
cols_s = [sig_color(row['sig_sobel'], row['ab_std']) for _, row in std_df.iterrows()]

# ── (A) a-path 표준화 계수 ──
ax_a.set_facecolor('#F8F9FA')
ax_a.bar(xp, std_df['a_std'], color=cols_s, alpha=0.85, edgecolor='white', lw=0.5)
ax_a.axhline(0, color='#2C3E50', lw=0.8, ls='--')
ax_a.set_xticks(xp); ax_a.set_xticklabels(flds_s, rotation=42, ha='right', fontsize=7.2)
ax_a.set_ylabel('β (표준화)', fontsize=8.5); ax_a.set_ylim(-2.5, 2.5)
ax_a.set_title('(A) a-path\n출연금비중 → 게임화강도', fontsize=9.5, fontweight='bold', pad=5)
ax_a.grid(axis='y', alpha=0.3, lw=0.5)
ax_a.yaxis.set_major_formatter(mpl.ticker.FormatStrFormatter('%.2f'))
# 값 표시
for xi, val in zip(xp, std_df['a_std']):
    ax_a.text(xi, val + (0.05 if val >= 0 else -0.12), f'{val:.2f}',
              ha='center', fontsize=5.5, color='#333')

# ── (B) b-path 표준화 계수 ──
ax_b.set_facecolor('#F8F9FA')
ax_b.bar(xp, std_df['b_std'], color=cols_s, alpha=0.85, edgecolor='white', lw=0.5)
ax_b.axhline(0, color='#2C3E50', lw=0.8, ls='--')
ax_b.set_xticks(xp); ax_b.set_xticklabels(flds_s, rotation=42, ha='right', fontsize=7.2)
ax_b.set_ylabel('β (표준화)', fontsize=8.5)
ax_b.set_title('(B) b-path\n게임화강도 → outcome\n(직접효과 통제 후)', fontsize=9.5, fontweight='bold', pad=5)
ax_b.grid(axis='y', alpha=0.3, lw=0.5)
ax_b.yaxis.set_major_formatter(mpl.ticker.FormatStrFormatter('%.2f'))
for xi, val in zip(xp, std_df['b_std']):
    if np.isfinite(val):
        ax_b.text(xi, val + (0.03 if val >= 0 else -0.06), f'{val:.2f}',
                  ha='center', fontsize=5.5, color='#333')

# ── (C) c vs c' 산포도 (표준화) ──
ax_cp.set_facecolor('#F8F9FA')
cv = std_df['c_std'].dropna().tolist()
cpv = std_df['c_prime_std'].dropna().tolist()
all_v = cv + cpv
if all_v:
    lim = max(abs(min(all_v)), abs(max(all_v))) * 1.3
    ax_cp.plot([-lim, lim], [-lim, lim], 'k--', lw=0.8, alpha=0.5, label="c=c'")
ax_cp.axhline(0, color='gray', lw=0.4, ls=':')
ax_cp.axvline(0, color='gray', lw=0.4, ls=':')

for _, row in std_df.iterrows():
    if not (np.isfinite(row['c_std']) and np.isfinite(row['c_prime_std'])):
        continue
    col = sig_color(row['sig_sobel'], row['ab_std'])
    ax_cp.scatter(row['c_std'], row['c_prime_std'], color=col, s=50, zorder=5,
                  edgecolors='white', lw=0.5, alpha=0.9)
    ax_cp.annotate(row['fld_short'], (row['c_std'], row['c_prime_std']),
                   fontsize=6, ha='center', va='bottom', xytext=(0, 3),
                   textcoords='offset points', color='#333')

ax_cp.set_xlabel('c β (총효과)', fontsize=8.5)
ax_cp.set_ylabel("c' β (직접효과)", fontsize=8.5)
ax_cp.set_title("(C) 총효과 vs 직접효과\n(대각선 아래 = 양(+) 매개)", fontsize=9.5, fontweight='bold', pad=5)
ax_cp.legend(fontsize=7, loc='upper left', framealpha=0.7)
ax_cp.grid(alpha=0.2, lw=0.4)

# ── (D) ab 표준화 간접효과 + 원시 Sobel p값 표시 ──
ax_ab.set_facecolor('#F8F9FA')
ax_ab.axvline(0, color='black', lw=0.9, ls='--')

# Sobel p 기반 색상 + 오리지널 bootstrap CI (정규화: ab_std 스케일)
for i, (_, row) in enumerate(std_df.iterrows()):
    col = sig_color(row['sig_sobel'], row['ab_std'])
    val = row['ab_std']
    if not np.isfinite(val): continue

    # bar
    ax_ab.barh(i, val, color=col, alpha=0.80, height=0.55,
               edgecolor='white', lw=0.4)

    # sobel p 레이블
    p_sob = row['p_sobel']
    p_txt = f'p={p_sob:.3f}' if np.isfinite(p_sob) else ''
    star  = '★' if (np.isfinite(p_sob) and p_sob < 0.05) else ''
    label = f'{star}{p_txt}'
    offset = 0.005
    ha_pos = 'left' if val >= 0 else 'right'
    ax_ab.text(val + (offset if val >= 0 else -offset), i, label,
               va='center', ha=ha_pos, fontsize=7,
               color='#C0392B' if star else '#555', fontweight='bold' if star else 'normal')

ax_ab.set_yticks(range(len(std_df)))
ax_ab.set_yticklabels(std_df['fld_short'].tolist(), fontsize=8.5)
ax_ab.set_xlabel('ab β (표준화 간접효과)', fontsize=9)
ax_ab.set_title('(D) 간접효과 ab = a×b  (표준화; ★=Sobel p<0.05)\n'
                '※ n=5~6 소표본으로 Bootstrap CI 폭 넓음 — Sobel z 보조 참고',
                fontsize=9.5, fontweight='bold', pad=5)
ax_ab.grid(axis='x', alpha=0.3, lw=0.5)
ax_ab.xaxis.set_major_formatter(mpl.ticker.FormatStrFormatter('%.2f'))

# pooled 결과 주석
pool_row = res_df[res_df['fld_nm'] == 'POOLED (FE)']
if len(pool_row):
    pr = pool_row.iloc[0]
    pool_txt = (f"Pooled FE (표준화, n={int(pr['n'])}): "
                f"a={pr['a']:.3f}, b={pr['b']:.3f}, "
                f"c={pr['c']:.3f}, c'={pr['c_prime']:.3f}, "
                f"ab={pr['ab']:.4f}, Sobel p={pr['sobel_p']:.3f}")
    ax_ab.text(0.01, -0.14, pool_txt, transform=ax_ab.transAxes,
               fontsize=7.5, color='#2C3E50',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='#EBF5FB', alpha=0.8))

# 범례
legend_patches = [
    mpatches.Patch(color='#E74C3C', alpha=0.8, label='Sobel p<0.05 (양의 간접)'),
    mpatches.Patch(color='#2980B9', alpha=0.8, label='Sobel p<0.05 (음의 간접)'),
    mpatches.Patch(color='#95A5A6', alpha=0.8, label='Sobel p≥0.05 (비유의)'),
]
fig.legend(handles=legend_patches, loc='lower center', ncol=3,
           fontsize=8, framealpha=0.9, bbox_to_anchor=(0.5, 0.01))

plt.suptitle('H23 매개 효과 분석: 출연금비중(X) → 게임화강도(M) → 분야별 성과지표(Y)\n'
             '(Baron & Kenny / Sobel test; 표준화 β; n=5~7/분야)',
             fontsize=11, fontweight='bold', y=0.95)

out_png = os.path.join(OUT_DIR, 'H23_mediation_diagram.png')
fig.savefig(out_png, dpi=DPI, bbox_inches='tight', facecolor=fig.get_facecolor())
plt.close()
print(f'그림 저장: {out_png}')


# ================================================================
# 7. 200자 요약
# ================================================================
n_sig = int(plot_df['sig_ab'].sum()) if 'sig_ab' in plot_df.columns else 0
n_tot = len(plot_df)

sw = res_df[res_df['fld_nm'] == '사회복지']
sw_ab   = float(sw['ab'].values[0])   if len(sw) > 0 else np.nan
sw_c    = float(sw['c'].values[0])    if len(sw) > 0 else np.nan
sw_ratio= float(sw['mediation_ratio'].values[0]) if len(sw) > 0 else np.nan

print('\n' + '='*70)
print('=== 200자 요약 ===')
print(f"""
출연금비중(X)→게임화(M)→성과(Y) 매개 분석: 14분야 중 Bootstrap 95%CI 0 제외 {n_sig}개 분야에서 유의 간접효과 확인.
사회복지: ab={sw_ab:.4f}, c={sw_c:.4f}, 매개비율={sw_ratio:.0%}.
Pooled FE 모형에서 a·b·c' 계수 추정; 자기인과 제거 outcome 적용 후 순수 게임화 경로 분리.
""".strip())
print('='*70)
print('\n완료.')
