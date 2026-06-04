"""견고성 검증 C7 — 두 층(비용=원형 / 결과=분야) 직교성.

질문: 원형 구성이 분야와 독립인가(교락 아닌가)?
방법: 활동을 분야(FLD_NM)×원형(C0~C3)으로 교차표. χ²·Cramér's V·정규화 상호정보량(NMI).
      활동 수 가중 + EP(집행액) 가중 둘 다.
판정: 연관 약하면(Cramér's V 작고 분야마다 원형 믹스 유사) → 두 층 근사 직교
      = H1+H5 양립 방어 가능. 강하면 → 교락 인정·두 층 논거 약화.
      어느 쪽이든 교차표 투명 제시 자체가 신뢰도↑.

자기 정직성: 수치를 먼저, 서술은 그 뒤.
"""
import os, sys, io
import numpy as np
import pandas as pd
import duckdb
from scipy.stats import chi2_contingency
from sklearn.metrics import normalized_mutual_info_score
import warnings

warnings.filterwarnings('ignore')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RES = os.path.join(ROOT, 'data', 'results')
DB = os.path.join(ROOT, 'data', 'warehouse.duckdb')
ARCH_KR = {0: 'C0인건비', 1: 'C1자산취득', 2: 'C2출연금', 3: 'C3정상'}

df = pd.read_csv(os.path.join(RES, 'H3_activity_embedding_11y.csv'))
df['arch'] = df['cluster'].map(ARCH_KR)

# 활동별 총 EP(집행액) 조인 (EP 가중용)
con = duckdb.connect(DB, read_only=True)
ep = con.execute("""
    SELECT FLD_NM, OFFC_NM, PGM_NM, ACTV_NM, SUM(EP_AMT) AS ep
    FROM monthly_exec
    WHERE FSCL_YY BETWEEN 2015 AND 2025 AND EXE_M BETWEEN 1 AND 12
    GROUP BY 1,2,3,4
""").fetchdf()
con.close()
df = df.merge(ep, on=['FLD_NM', 'OFFC_NM', 'PGM_NM', 'ACTV_NM'], how='left')
df['ep'] = df['ep'].fillna(0)


def cramers_v(ct):
    chi2, p, dof, _ = chi2_contingency(ct)
    n = ct.values.sum()
    r, k = ct.shape
    phi2 = chi2 / n
    # bias-corrected (Bergsma 2013)
    phi2c = max(0, phi2 - (k - 1) * (r - 1) / (n - 1))
    rc = r - ((r - 1) ** 2) / (n - 1)
    kc = k - ((k - 1) ** 2) / (n - 1)
    V = np.sqrt(phi2 / min(k - 1, r - 1))
    Vc = np.sqrt(phi2c / max(1e-12, min(kc - 1, rc - 1)))
    return chi2, p, dof, V, Vc


print('=' * 74)
print('견고성 C7 — 분야 × 원형 직교성')
print('=' * 74)
print(f'활동 N = {len(df)},  분야 {df.FLD_NM.nunique()}개,  원형 4개')

# ── 활동 수 가중 교차표 ───────────────────────────────────────
ct = pd.crosstab(df['FLD_NM'], df['arch'])
ct = ct[list(ARCH_KR.values())]
ct = ct.loc[ct.sum(axis=1).sort_values(ascending=False).index]
chi2, p, dof, V, Vc = cramers_v(ct)
nmi = normalized_mutual_info_score(df['FLD_NM'], df['arch'])
print('\n' + '-' * 74)
print('(1) 활동 수 가중 — 분야 × 원형 교차표 (행 비율 %)')
print('-' * 74)
ct_pct = ct.div(ct.sum(axis=1), axis=0).mul(100).round(1)
ct_pct['n'] = ct.sum(axis=1)
print(ct_pct.to_string())
print(f'\n  χ² = {chi2:.1f}  (dof={dof})  p = {p:.2e}')
print(f'  Cramér\'s V = {V:.3f}   (bias-corrected = {Vc:.3f})')
print(f'  정규화 상호정보량 NMI = {nmi:.3f}')

# 전체 평균 원형 믹스 (비교 기준선)
overall = (df['arch'].value_counts(normalize=True) * 100).reindex(list(ARCH_KR.values())).round(1)
print(f'\n  전체 평균 원형 믹스(%): {dict(overall)}')

# ── EP(집행액) 가중 교차표 ───────────────────────────────────
print('\n' + '-' * 74)
print('(2) EP(집행액) 가중 — 분야 × 원형 (집행액 비율 %)')
print('-' * 74)
ctep = df.pivot_table(index='FLD_NM', columns='arch', values='ep',
                      aggfunc='sum', fill_value=0)
ctep = ctep[list(ARCH_KR.values())]
ctep = ctep.loc[ctep.sum(axis=1).sort_values(ascending=False).index]
ctep_pct = ctep.div(ctep.sum(axis=1), axis=0).mul(100).round(1)
print(ctep_pct.to_string())
overall_ep = (df.groupby('arch')['ep'].sum() / df['ep'].sum() * 100).reindex(list(ARCH_KR.values())).round(1)
print(f'\n  전체 EP 평균 원형 믹스(%): {dict(overall_ep)}')
# EP 가중 Cramér's V (집행액을 빈도처럼 χ²) — 소수 초대형 계정 영향 주의
ctep_round = ctep.round().astype('int64')
chi2e, pe, dofe, Ve, Vce = cramers_v(ctep_round[ctep_round.sum(axis=1) > 0])
print(f'  EP 가중 Cramér\'s V = {Ve:.3f} (보정 {Vce:.3f})  '
      f'[주의: 경찰 인건비 등 소수 초대형 계정 지배 → 예산 집중도 반영]')
# 비C3(소수 원형) 하위집합 연관 — 기저율 억제 제거
sub = df[df['arch'] != 'C3정상']
ctsub = pd.crosstab(sub['FLD_NM'], sub['arch'])
ctsub = ctsub[ctsub.sum(axis=1) >= 5]
chi2s, ps, dofs, Vs, Vcs = cramers_v(ctsub)
nmisub = normalized_mutual_info_score(sub['FLD_NM'], sub['arch'])
print(f'  비C3(소수원형 {len(sub)}개) 하위집합: Cramér\'s V 보정 = {Vcs:.3f}, NMI = {nmisub:.3f}  '
      f'(C3 기저율 75.5% 억제 제거 시 연관 강화)')

# ── 분야별 우세 원형 & 집중도 ────────────────────────────────
print('\n' + '-' * 74)
print('(3) 분야별 우세(최빈) 원형과 그 비율 — 단일 원형이 분야를 지배하나?')
print('-' * 74)
dom = ct_pct.drop(columns='n').idxmax(axis=1)
dompct = ct_pct.drop(columns='n').max(axis=1)
for fld in ct_pct.index:
    flag = '  ← C3(정상)' if dom[fld] == 'C3정상' else '  ★ 비정상원형 우세'
    print(f'  {fld:16s} 우세={dom[fld]:9s} {dompct[fld]:5.1f}%{flag}')
n_c3dom = (dom == 'C3정상').sum()
print(f'\n  {n_c3dom}/{len(dom)} 분야에서 C3(정상사업)이 다수 — '
      f'특정 게임화 원형이 분야를 지배하는 경우는 {len(dom)-n_c3dom}개')

# ── 사회복지 초점 (H5 기각 논리 관련) ────────────────────────
print('\n' + '-' * 74)
print('(4) 사회복지 원형 구성 — H5 기각(자동분배) 논리 점검')
print('-' * 74)
if '사회복지' in ct_pct.index:
    sw = ct_pct.loc['사회복지'].drop('n')
    print(f'  사회복지 원형 믹스(%): {dict(sw.round(1))}')
    print(f'  전체 평균 대비:        {dict(overall.round(1))}')
    print('  → 사회복지가 게임화 강한 원형(C1자산·C2출연금)에 과대/과소 노출?')
    for a in ['C1자산취득', 'C2출연금']:
        diff = sw[a] - overall[a]
        print(f'     {a}: 사회복지 {sw[a]:.1f}% vs 전체 {overall[a]:.1f}%  '
              f'({"과소" if diff < 0 else "과대"} {abs(diff):.1f}%p)')

# ── 판정 ─────────────────────────────────────────────────────
print('\n' + '=' * 74)
print('판정')
print('=' * 74)
if Vc < 0.2:
    verd = '약한 연관 → 두 층 근사 직교 (H1+H5 양립 방어 가능)'
elif Vc < 0.35:
    verd = '중간 연관 → 부분 교락 (완전 직교 아님; 정직 명시 필요)'
else:
    verd = '강한 연관 → 교락 인정 (두 층 논거 약화)'
print(f'  Cramér\'s V(보정) = {Vc:.3f}, NMI = {nmi:.3f} → {verd}')

# 저장
ct_pct.to_csv(os.path.join(RES, 'robust_c7_field_archetype_pct.csv'), encoding='utf-8-sig')
ctep_pct.to_csv(os.path.join(RES, 'robust_c7_field_archetype_ep_pct.csv'), encoding='utf-8-sig')
pd.DataFrame([{'metric': 'chi2', 'value': chi2}, {'metric': 'dof', 'value': dof},
              {'metric': 'p', 'value': p}, {'metric': 'cramers_v', 'value': V},
              {'metric': 'cramers_v_corrected', 'value': Vc},
              {'metric': 'nmi', 'value': nmi},
              {'metric': 'cramers_v_ep', 'value': Ve},
              {'metric': 'cramers_v_ep_corrected', 'value': Vce},
              {'metric': 'cramers_v_nonC3_corrected', 'value': Vcs},
              {'metric': 'nmi_nonC3', 'value': nmisub}]).to_csv(
    os.path.join(RES, 'robust_c7_association_stats.csv'), index=False, encoding='utf-8-sig')
print(f'\n  저장: robust_c7_field_archetype_pct.csv / _ep_pct.csv / _association_stats.csv')
