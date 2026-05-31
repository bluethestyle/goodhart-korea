"""H2 (Decoupling) 결과 시각화 — 분야별 게임화-outcome 관계 이질성.

산출:
  data/figs/h2/T1_panel_overview.png        분야별 시계열 (게임화 + outcome)
  data/figs/h2/T2_scatter_levels.png        수준 산점도 (분야별 색상)
  data/figs/h2/T3_scatter_diff.png          차분 산점도 (Δgaming vs Δlnoutcome)
  data/figs/h2/T4_correlation_summary.png   분야별 상관관계 막대그래프
"""
import os, sys, io, duckdb
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

for f in ['Malgun Gothic','NanumGothic','AppleGothic','Noto Sans CJK KR']:
    try: plt.rcParams['font.family']=f; break
    except: pass
plt.rcParams['axes.unicode_minus']=False
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG = os.path.join(ROOT, 'data', 'figs', 'h2'); os.makedirs(FIG, exist_ok=True)
con = duckdb.connect(os.path.join(ROOT, 'data', 'warehouse.duckdb'), read_only=True)

# 데이터 로드
df = con.execute("""
WITH g AS (SELECT fld_nm, year, value AS gaming FROM indicator_panel WHERE metric_code='amp_12m_norm'),
     o AS (SELECT p.fld_nm, p.year, p.metric_code AS ovar, p.value AS outcome, p.unit
           FROM indicator_panel p JOIN indicator_metadata m USING (metric_code)
           WHERE m.category='outcome')
SELECT g.fld_nm, g.year, g.gaming, o.ovar, o.outcome, o.unit
FROM g JOIN o USING (fld_nm, year)
ORDER BY g.fld_nm, g.year
""").fetchdf()

# 분야별 색상
fld_color = {
    '보건': '#1f77b4',
    '문화및관광': '#ff7f0e',
    '산업·중소기업및에너지': '#2ca02c',
    '과학기술': '#d62728',
    '사회복지': '#9467bd',
}

# ============================================================
# T1. 분야별 시계열 (게임화 + outcome 듀얼축)
# ============================================================
fields = list(fld_color.keys())
fig, axes = plt.subplots(len(fields), 1, figsize=(10, 2.5*len(fields)), sharex=True)

for i, fld in enumerate(fields):
    ax = axes[i]
    g = df[df.fld_nm == fld].sort_values('year')
    if g.empty: continue
    color = fld_color[fld]
    # 게임화
    ax.plot(g['year'], g['gaming'], 'o-', color=color, label='게임화 강도(amp_12m_norm)', linewidth=2, markersize=7)
    ax.set_ylabel('게임화 강도', color=color)
    ax.tick_params(axis='y', labelcolor=color)
    # outcome (오른쪽 축)
    ax2 = ax.twinx()
    ovar_label = g['ovar'].iloc[0]
    unit = g['unit'].iloc[0]
    ax2.plot(g['year'], g['outcome'], 's--', color='#444', label=f'{ovar_label} ({unit})', alpha=0.7)
    ax2.set_ylabel(f'{ovar_label}\n({unit})', color='#444')
    ax2.tick_params(axis='y', labelcolor='#444')
    ax.set_title(f'{fld}', loc='left', fontsize=11)
    ax.grid(alpha=0.3)
axes[-1].set_xlabel('연도')
plt.suptitle('분야별 게임화 강도 vs Outcome 시계열', fontsize=13, y=1.0)
plt.tight_layout()
plt.savefig(f'{FIG}/T1_panel_overview.png', dpi=140, bbox_inches='tight')
plt.close()
print(f'saved {FIG}/T1_panel_overview.png')

# ============================================================
# T2. 수준 산점도 (분야별 색상, 정규화 outcome)
# ============================================================
fig, ax = plt.subplots(figsize=(11, 7))
df['outcome_z'] = df.groupby('fld_nm')['outcome'].transform(lambda x: (x-x.mean())/x.std() if x.std()>0 else x*0)

for fld, color in fld_color.items():
    g = df[df.fld_nm == fld]
    if g.empty: continue
    ax.scatter(g['gaming'], g['outcome_z'], color=color, s=120, alpha=0.7, label=fld, edgecolor='black', linewidth=0.5)
    # 연도 라벨
    for _, r in g.iterrows():
        ax.annotate(str(int(r['year'])), (r['gaming'], r['outcome_z']),
                    fontsize=7, ha='center', va='bottom', xytext=(0,4), textcoords='offset points')
    # 회귀선
    if len(g) >= 3:
        z = np.polyfit(g['gaming'], g['outcome_z'], 1)
        x_range = np.linspace(g['gaming'].min(), g['gaming'].max(), 50)
        ax.plot(x_range, np.poly1d(z)(x_range), '--', color=color, alpha=0.4, linewidth=1.5)

ax.axhline(0, color='gray', linewidth=0.5)
ax.set_xlabel('게임화 강도 (amp_12m_norm)', fontsize=12)
ax.set_ylabel('Outcome (분야별 정규화 z-score)', fontsize=12)
ax.set_title('분야별 게임화 강도 vs Outcome — 수준 산점도', fontsize=13)
ax.legend(loc='best', fontsize=10)
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(f'{FIG}/T2_scatter_levels.png', dpi=140)
plt.close()
print(f'saved {FIG}/T2_scatter_levels.png')

# ============================================================
# T3. 차분 산점도 — 시간 트렌드 제거 후 진짜 관계
# ============================================================
df['ln_outcome'] = np.log(df['outcome'].clip(lower=1e-6))
df = df.sort_values(['fld_nm', 'year']).reset_index(drop=True)
df['d_gaming'] = df.groupby('fld_nm')['gaming'].diff()
df['d_ln_outcome'] = df.groupby('fld_nm')['ln_outcome'].diff()
diff = df.dropna(subset=['d_gaming', 'd_ln_outcome'])

fig, ax = plt.subplots(figsize=(11, 7))
for fld, color in fld_color.items():
    g = diff[diff.fld_nm == fld]
    if g.empty: continue
    rho = g[['d_gaming','d_ln_outcome']].corr().iloc[0,1] if len(g) >= 3 else None
    label = f'{fld} (n={len(g)}, ρ={rho:+.2f})' if rho is not None else f'{fld} (n={len(g)})'
    ax.scatter(g['d_gaming'], g['d_ln_outcome'], color=color, s=140, alpha=0.7,
               label=label, edgecolor='black', linewidth=0.5)
    # 회귀선
    if len(g) >= 3 and g['d_gaming'].std() > 0:
        z = np.polyfit(g['d_gaming'], g['d_ln_outcome'], 1)
        x_range = np.linspace(g['d_gaming'].min(), g['d_gaming'].max(), 50)
        ax.plot(x_range, np.poly1d(z)(x_range), '--', color=color, alpha=0.4, linewidth=2)

ax.axhline(0, color='gray', linewidth=0.5)
ax.axvline(0, color='gray', linewidth=0.5)
ax.set_xlabel('Δ 게임화 강도 (전년 대비 변화)', fontsize=12)
ax.set_ylabel('Δ log(Outcome) (전년 대비 변화율)', fontsize=12)
ax.set_title('1차 차분 산점도 — 시간 트렌드 제거 후 게임화↔Outcome 관계', fontsize=13)
ax.legend(loc='best', fontsize=10)
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(f'{FIG}/T3_scatter_diff.png', dpi=140)
plt.close()
print(f'saved {FIG}/T3_scatter_diff.png')

# ============================================================
# T4. 분야별 상관관계 요약 (수준 + 차분)
# ============================================================
summary = []
for fld in fld_color.keys():
    g_lvl = df[df.fld_nm == fld]
    g_dif = diff[diff.fld_nm == fld]
    rho_lvl = g_lvl[['gaming','outcome']].corr().iloc[0,1] if len(g_lvl) >= 3 else None
    rho_dif = g_dif[['d_gaming','d_ln_outcome']].corr().iloc[0,1] if len(g_dif) >= 3 else None
    ovar = g_lvl['ovar'].iloc[0] if not g_lvl.empty else ''
    summary.append({'fld': fld, 'ovar': ovar, 'rho_level': rho_lvl, 'rho_diff': rho_dif,
                    'n_lvl': len(g_lvl), 'n_dif': len(g_dif)})
sm_df = pd.DataFrame(summary)
print('\n=== 분야별 상관관계 요약 ===')
print(sm_df.to_string(index=False))

fig, ax = plt.subplots(figsize=(11, 6))
y = np.arange(len(sm_df))
h = 0.35

# 수준 상관
ax.barh(y - h/2, sm_df['rho_level'], h, label='수준 (raw)',
        color=[fld_color[f] for f in sm_df['fld']], alpha=0.5)
# 차분 상관
ax.barh(y + h/2, sm_df['rho_diff'], h, label='차분 (시간 트렌드 제거)',
        color=[fld_color[f] for f in sm_df['fld']], alpha=1.0,
        edgecolor='black', linewidth=0.5)

ax.set_yticks(y)
ax.set_yticklabels([f"{r['fld']}\n({r['ovar']}, n={r['n_dif']})" for _, r in sm_df.iterrows()], fontsize=9)
ax.invert_yaxis()
ax.axvline(0, color='gray', linewidth=0.8)
ax.set_xlabel('상관계수 ρ (게임화 ↔ outcome)')
ax.set_title('분야별 게임화-Outcome 상관관계 — H2 가설 검증')
ax.legend(loc='best')
ax.grid(axis='x', alpha=0.3)
ax.set_xlim(-1, 1)

# 가설 방향 주석
ax.text(-0.95, len(sm_df)-0.3, '← H2 입증\n(게임화↑→결과↓)', fontsize=9, color='#d62728', va='top')
ax.text(0.55, len(sm_df)-0.3, 'H2 반박 →\n(게임화↑→결과↑)', fontsize=9, color='#7f7f7f', va='top')

plt.tight_layout()
plt.savefig(f'{FIG}/T4_correlation_summary.png', dpi=140)
plt.close()
print(f'saved {FIG}/T4_correlation_summary.png')

# ============================================================
# T5. 보너스 — 게임화 vs outcome 변동성 (분야간 단면)
# ============================================================
# 각 분야의 게임화 평균 + outcome 변동성 (CV)
agg = df.groupby('fld_nm').agg(
    gaming_mean=('gaming','mean'),
    outcome_cv=('outcome', lambda x: x.std()/x.mean() if x.mean() else 0),
    n=('outcome','count'),
).reset_index()
print('\n=== 분야 간 단면 — 게임화 평균 vs outcome CV ===')
print(agg.to_string(index=False))

fig, ax = plt.subplots(figsize=(9, 6))
for _, r in agg.iterrows():
    ax.scatter(r['gaming_mean'], r['outcome_cv']*100, s=200,
               color=fld_color.get(r['fld_nm'], '#888'), edgecolor='black', alpha=0.8)
    ax.annotate(r['fld_nm'], (r['gaming_mean'], r['outcome_cv']*100),
                fontsize=10, ha='center', xytext=(0, 12), textcoords='offset points')
ax.set_xlabel('분야별 평균 게임화 강도')
ax.set_ylabel('Outcome 변동계수 (CV, %)')
ax.set_title('분야별 게임화 vs Outcome 변동성 — 단면 비교')
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(f'{FIG}/T5_field_crosssection.png', dpi=140)
plt.close()
print(f'saved {FIG}/T5_field_crosssection.png')

con.close()

# 결과 CSV로도 저장
RES = os.path.join(ROOT, 'data', 'results')
sm_df.to_csv(f'{RES}/H2_correlation_summary.csv', index=False, encoding='utf-8-sig')
df.to_csv(f'{RES}/H2_panel_levels.csv', index=False, encoding='utf-8-sig')
diff.to_csv(f'{RES}/H2_panel_diff.csv', index=False, encoding='utf-8-sig')
print(f'\nCSV 저장: H2_correlation_summary, H2_panel_levels, H2_panel_diff')
