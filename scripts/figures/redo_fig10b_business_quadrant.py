"""세부사업 단위 정책 사분면 (fig_slide38_business_quadrant) — paper용 재생성기.

PROVENANCE 上 'NOT_FOUND (수동 생성)'이던 차트를 재현 가능한 스크립트로 복원.
(2026-06-01 신규 작성 — 부처 버전 redo_fig10_quadrant.py 와 한 쌍.)

축 정의 (모두 커밋된 CSV에서 재현):
  x = 굿하트 노출 점수 = 활동이 속한 부처의 H5 exposure_score
      (data/results/H5_ministry_exposure_11y.csv, OFFC_NM 매핑)
  y = 활동이 속한 분야의 outcome 상관 (Pearson r, CPI 통제 전)
      (data/results/H10_macro_control_corr_v3.csv corr_raw, FLD_NM 매핑)
  색 = 체질(archetype) cluster 0~3 (TDA+HDBSCAN)
  점 크기 = log_annual (사업 규모)
  검은 원 = 분야 평균 (x=분야 내 활동 평균 노출, y=corr_raw, 크기=활동 수)

축이 모두 비-결과(노출)와 분야 대리 결과로 구성됨을 명시 — 사업 단위 outcome은
측정 공백이라 분야값으로 대리하며, 그래서 같은 분야의 점은 가로 띠를 이룬다.

source 데이터: H3_activity_embedding_11y.csv(1,557) ∩ corr ∩ exposure → 1,548.

레이아웃 개선(기존 수동본 대비): x축 라벨과 하단 각주가 겹치던 문제를
   하단 여백 확보 + 각주를 figure 최하단 단독 배치로 해소.
"""
import os, sys, io, warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from PIL import Image

warnings.filterwarnings('ignore')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from _paper_style import apply_paper_style
apply_paper_style()

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RES = os.path.join(ROOT, 'data', 'results')

emb = pd.read_csv(os.path.join(RES, 'H3_activity_embedding_11y.csv'), encoding='utf-8-sig')
h10 = pd.read_csv(os.path.join(RES, 'H10_macro_control_corr_v3.csv'), encoding='utf-8-sig')
h5 = pd.read_csv(os.path.join(RES, 'H5_ministry_exposure_11y.csv'), encoding='utf-8-sig')

# ── 병합: 분야 outcome 상관(y) + 부처 노출(x)
df = (emb.merge(h10[['fld', 'corr_raw']], left_on='FLD_NM', right_on='fld', how='left')
         .merge(h5[['OFFC_NM', 'exposure_score']], on='OFFC_NM', how='left'))
df = df.dropna(subset=['corr_raw', 'exposure_score']).copy()
df['x'] = df['exposure_score'].astype(float)
df['y'] = df['corr_raw'].astype(float)
print(f'활동 점: {len(df):,} (분야 {df["FLD_NM"].nunique()}개)')

# 점 크기: log_annual 정규화 → 8~58
la = df['log_annual'].astype(float)
df['psize'] = 8 + 50 * (la - la.min()) / (la.max() - la.min() + 1e-9)

# ── 체질(archetype) 색/순서: 비교군 뒤, 분석 대상 앞
ARCH = {
    3: ('C3 정상사업 (비교군)',   '#BFC7D2', 0.32, 0),
    0: ('C0 인건비형 (비교군)',   '#8C5A8F', 0.55, 1),
    2: ('C2 출연금형 (분석 대상)', '#E67E22', 0.78, 2),
    1: ('C1 자산취득형 (분석 대상)', '#C0392B', 0.82, 3),
}

EXPO_THRESH = 0.30

# ── Figure (부처 버전과 동일한 1280×800 프레임)
fig, ax = plt.subplots(figsize=(12.8, 8.0), dpi=100,
                       gridspec_kw={'left': 0.075, 'right': 0.97,
                                    'top': 0.91, 'bottom': 0.205})

x1 = max(df['x'].max() + 0.04, 0.85)
y0_lim = min(df['y'].min() - 0.08, -0.85)
y1_lim = max(df['y'].max() + 0.08, 0.72)

# 4분면 배경
ax.fill_between([EXPO_THRESH, x1], 0, y1_lim, color='#ffe0e0', alpha=0.40, zorder=0)
ax.fill_between([EXPO_THRESH, x1], y0_lim, 0, color='#fff3e0', alpha=0.40, zorder=0)
ax.fill_between([0, EXPO_THRESH], 0, y1_lim, color='#e8f4f8', alpha=0.28, zorder=0)
ax.fill_between([0, EXPO_THRESH], y0_lim, 0, color='#e8f8ee', alpha=0.28, zorder=0)
ax.axhline(0, color='#666', lw=0.9, zorder=1)
ax.axvline(EXPO_THRESH, color='#666', lw=0.9, zorder=1)

# ── 활동 점 (체질별, 그리기 순서)
for cl, (lab, col, al, order) in sorted(ARCH.items(), key=lambda k: k[1][3]):
    s = df[df['cluster'] == cl]
    ax.scatter(s['x'], s['y'], s=s['psize'], c=col, alpha=al,
               edgecolors='none', zorder=2 + order,
               label=f'{lab} (n={len(s):,})')

# ── 분야 평균 검은 원 (x=평균 노출, y=corr_raw, 크기 ∝ 활동 수)
fld_avg = (df.groupby('FLD_NM')
             .agg(x=('x', 'mean'), y=('y', 'first'), n=('y', 'size'))
             .reset_index())
ax.scatter(fld_avg['x'], fld_avg['y'],
           s=60 + fld_avg['n'] / fld_avg['n'].max() * 340,
           facecolors='none', edgecolors='#111', linewidths=1.6,
           zorder=7, label=f'{len(fld_avg)}개 분야 평균 (크기 = 사업 수)')

# ── 분야 라벨 (검은 원 옆) — adjustText 충돌 회피
texts = []
try:
    from adjustText import adjust_text
    for _, r in fld_avg.iterrows():
        t = ax.text(r['x'], r['y'], str(r['FLD_NM']),
                    fontsize=12, color='#1a1a1a', fontweight='bold', zorder=8)
        texts.append(t)
    adjust_text(texts, ax=ax,
                arrowprops=dict(arrowstyle='-', color='#888', lw=0.5),
                expand_points=(1.8, 1.8), expand_text=(1.6, 1.6),
                force_text=(0.8, 1.0), force_points=(0.5, 0.8), lim=200)
except ImportError:
    for _, r in fld_avg.iterrows():
        ax.annotate(str(r['FLD_NM']), (r['x'], r['y']),
                    xytext=(5, 5), textcoords='offset points',
                    fontsize=12, fontweight='bold', color='#1a1a1a', zorder=8)

# ── 4분면 코너 라벨 (부처 버전과 동일 framework)
qbox = dict(boxstyle='round,pad=0.4', fc='white', ec='#bbb', lw=0.8, alpha=0.92)
ax.text(x1 - 0.01, y1_lim - 0.02, 'Q2 위험 (점검 필요)', ha='right', va='top',
        fontsize=13, color='#c0392b', fontweight='bold', bbox=qbox)
ax.text(x1 - 0.01, y0_lim + 0.02, 'Q1 자동분배', ha='right', va='bottom',
        fontsize=13, color='#c05000', fontweight='bold', bbox=qbox)
ax.text(0.005, y1_lim - 0.02, 'Q4 안전 (양 상관)', ha='left', va='top',
        fontsize=13, color='#1a6fa0', fontweight='bold', bbox=qbox)
ax.text(0.005, y0_lim + 0.02, 'Q3 안전 (음 상관)', ha='left', va='bottom',
        fontsize=13, color='#1a7a4a', fontweight='bold', bbox=qbox)

ax.set_xlim(0, x1)
ax.set_ylim(y0_lim, y1_lim)
ax.set_xlabel('굿하트 노출 점수  (활동이 속한 부처의 H5 exposure_score)',
              fontsize=13, labelpad=8)
ax.set_ylabel('분야 outcome 상관  (Pearson r, CPI 통제 전)', fontsize=13)
ax.set_title(f'세부사업 단위 정책 사분면 (n={len(df):,})  ·  체질이 4분면 분포를 가른다',
             fontsize=15.5, fontweight='bold', pad=12)
ax.tick_params(labelsize=11)
ax.grid(alpha=0.18)
for spine in ['top', 'right']:
    ax.spines[spine].set_visible(False)

# 범례 — x축 라벨 아래 한 줄, 각주와 분리
ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.105),
          fontsize=10.5, framealpha=0.9, ncol=5, frameon=False,
          columnspacing=1.4, handletextpad=0.4)

# 각주 — figure 최하단 단독 배치 (x축 라벨/범례와 겹치지 않게)
fig.text(0.5, 0.018,
         '점 크기 = 사업 규모(log_annual)  ·  색 = 체질(TDA+HDBSCAN 자동 분류)  ·  '
         '같은 분야 = 같은 y(분야 대리 결과)이므로 가로 띠로 나타남',
         ha='center', va='bottom', fontsize=10, color='#666')

out = os.path.join(ROOT, 'paper', 'figures', 'eda', 'fig_slide38_business_quadrant.png')
os.makedirs(os.path.dirname(out), exist_ok=True)
fig.savefig(out, dpi=100, facecolor='white')
plt.close()
print(f'Saved: {out}  {Image.open(out).size}')
