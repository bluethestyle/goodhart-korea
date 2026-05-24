"""Slide 40 세부사업 단위 정책 사분면 신규 차트.

narrative: 분석 단위(세부사업) vs 도구 단위(부처) 2-layer 구조 중
*분석 단위* layer 시각화. h14_quadrant(부처 단위)와 좌우 병치.

축:
- x: amp_12m_norm (Wavelet 12m 진폭 정규화) — 시점 압력 지수
- y: 사업이 속한 분야의 outcome r 평균 (H10 분야별)
- 색: cluster (C0 회색·C1 빨강·C2 주황·C3 옅은 회색)
- 점 크기: log_annual (사업 규모)

사분면 (h14와 일관):
- Q2 위험 (우상, x>0.3 & y>0)
- Q1 자동분배 (우하, x>0.3 & y<0)
- Q4 안전 양상관 (좌상, x<0.3 & y>0)
- Q3 안전 음상관 (좌하, x<0.3 & y<0)
"""
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Pretendard 폰트
font_path = Path('paper/fonts/Pretendard-Regular.otf')
if font_path.exists():
    fm.fontManager.addfont(str(font_path))
    plt.rcParams['font.family'] = 'Pretendard'
plt.rcParams['axes.unicode_minus'] = False

# 데이터 로드
emb = pd.read_csv('data/results/H3_activity_embedding_11y.csv')
print(f'세부사업 임베딩: {len(emb)} 행')

# 분야 outcome r 매핑
h10 = pd.read_csv('data/results/H10_v3_alt_correlations.csv')
field_corr = h10.groupby('field')['pearson_r'].mean().to_dict()
print(f'H10 분야 outcome r 매핑: {len(field_corr)} 분야')
emb['outcome_r'] = emb['FLD_NM'].map(field_corr)

# 부처 exposure_score 매핑 (부처 사분면과 x축 통일)
h5 = pd.read_csv('data/results/H5_ministry_exposure_11y.csv')
ministry_expo = h5.set_index('OFFC_NM')['exposure_score'].to_dict()
emb['exposure_score'] = emb['OFFC_NM'].map(ministry_expo)
print(f'부처 exposure_score 매칭: {emb["exposure_score"].notna().sum()}/{len(emb)} 세부사업')

# 매칭된 세부사업만 사용 (분야 outcome + 부처 exposure 둘 다 있어야)
df = emb[emb['outcome_r'].notna() & emb['exposure_score'].notna()].copy()
print(f'시각화 대상: {len(df)} 세부사업')

# x축 jitter — 같은 부처 사업들이 수직 라인 분포 회피
import numpy as np
np.random.seed(42)
df['x_jitter'] = df['exposure_score'] + np.random.uniform(-0.015, 0.015, len(df))

# cluster 색 + 라벨
cluster_color = {0: '#a0a0a0', 1: '#C0392B', 2: '#E67E22', 3: '#cccccc'}
cluster_label = {0: 'C0 인건비형 (비교군)', 1: 'C1 자산취득형 (분석 대상)',
                 2: 'C2 출연금형 (분석 대상)', 3: 'C3 정상사업 (비교군)'}

# 점 크기 (log_annual normalize)
size_min, size_max = df['log_annual'].quantile([0.05, 0.95])
df['size'] = ((df['log_annual'] - size_min) / (size_max - size_min)).clip(0.1, 1.0) * 50 + 8

# 사분면 라인 — 부처 사분면과 통일 (x_thr = 0.3 = EXPO_THRESH)
x_thr = 0.3
y_thr = 0.0
print(f'x_thr (75% percentile) = {x_thr:.3f}, y_thr = {y_thr}')

fig, ax = plt.subplots(figsize=(12.8, 8.0), dpi=100,
                       gridspec_kw={'left': 0.09, 'right': 0.96,
                                    'top': 0.91, 'bottom': 0.20})

# 4분면 라인 + 배경 (h14 quadrant 컬러 스킴)
# 배경은 axvspan/axhspan 조합. 4분면 명확 구분.
ymin_data, ymax_data = df['outcome_r'].min(), df['outcome_r'].max()
xmin_data, xmax_data = 0.0, max(df['exposure_score'].max() + 0.05, 0.85)
margin_y = (ymax_data - ymin_data) * 0.10
ax.set_xlim(xmin_data, xmax_data)
ax.set_ylim(ymin_data - margin_y, ymax_data + margin_y)

# 4분면 배경 — 부처 사분면과 동일 컬러 스킴
from matplotlib.patches import Rectangle
rect_q2 = Rectangle((x_thr, y_thr), xmax_data - x_thr,
                     ymax_data + margin_y - y_thr,
                     facecolor='#ffe0e0', alpha=0.45, zorder=0)
rect_q1 = Rectangle((x_thr, ymin_data - margin_y), xmax_data - x_thr,
                     y_thr - (ymin_data - margin_y),
                     facecolor='#fff3e0', alpha=0.45, zorder=0)
rect_q4 = Rectangle((xmin_data, y_thr), x_thr - xmin_data,
                     ymax_data + margin_y - y_thr,
                     facecolor='#e8f4f8', alpha=0.30, zorder=0)
rect_q3 = Rectangle((xmin_data, ymin_data - margin_y),
                     x_thr - xmin_data,
                     y_thr - (ymin_data - margin_y),
                     facecolor='#e8f8ee', alpha=0.30, zorder=0)
for r in [rect_q2, rect_q1, rect_q4, rect_q3]:
    ax.add_patch(r)

# cluster별 산점 (세부사업 1557 — 배경 layer, 옅게) — x축은 부처 exposure (jitter 추가)
for c in [3, 0, 2, 1]:  # C1 최상위 그리도록
    sub = df[df['cluster'] == c]
    ax.scatter(sub['x_jitter'], sub['outcome_r'],
               s=sub['size'] * 0.4, c=cluster_color[c],
               label=f'{cluster_label[c]} (n={len(sub)})',
               alpha=0.28, edgecolors='none', zorder=2)

# 14분야 평균 dot (전경 layer, 강조) + 분야명 라벨 — 분야별 부처 exposure 평균
field_mean = df.groupby('FLD_NM').agg(
    x_mean=('exposure_score', 'mean'),
    y_mean=('outcome_r', 'mean'),
    n=('exposure_score', 'size'),
).reset_index()
print('\n14분야 평균 좌표:')
print(field_mean.to_string(index=False))

# 분야 dot — 검정 outline + 흰 fill, n에 비례하는 size
field_sizes = (field_mean['n'] / field_mean['n'].max() * 250 + 80).values
ax.scatter(field_mean['x_mean'], field_mean['y_mean'],
           s=field_sizes, c='#FFFFFF', edgecolors='#1a1a1a',
           linewidths=2.0, zorder=4,
           label=f'14분야 평균 (점 크기 = 사업 수)')

# 분야명 라벨 (옅은 색, 작게)
for _, row in field_mean.iterrows():
    ax.text(row['x_mean'], row['y_mean'] + 0.04, row['FLD_NM'],
            fontsize=10, ha='center', va='bottom', color='#222',
            fontweight='semibold', zorder=5)

# 4분면 라인
ax.axvline(x_thr, color='#555', linewidth=0.8, zorder=1)
ax.axhline(y_thr, color='#555', linewidth=0.8, zorder=1)

# 4분면 라벨 (각 사분면 가운데 위치)
xmin_ax, xmax_ax = ax.get_xlim()
ymin_ax, ymax_ax = ax.get_ylim()
# 사분면 라벨 — corner에 박스로 배치 (분야명 라벨과 충돌 회피)
qbox = dict(boxstyle='round,pad=0.4', fc='white', ec='#bbb', lw=0.8, alpha=0.92)
ax.text(xmax_ax - 0.02 * (xmax_ax - xmin_ax), ymax_ax - 0.01 * (ymax_ax - ymin_ax),
        'Q2 위험 (점검 필요)', ha='right', va='top',
        fontsize=13, color='#A04040', weight='bold', bbox=qbox)
ax.text(xmax_ax - 0.02 * (xmax_ax - xmin_ax), ymin_ax + 0.01 * (ymax_ax - ymin_ax),
        'Q1 자동분배', ha='right', va='bottom',
        fontsize=13, color='#A06030', weight='bold', bbox=qbox)
ax.text(xmin_ax + 0.02 * (xmax_ax - xmin_ax), ymax_ax - 0.01 * (ymax_ax - ymin_ax),
        'Q4 안전 (양 상관)', ha='left', va='top',
        fontsize=13, color='#406080', weight='bold', bbox=qbox)
ax.text(xmin_ax + 0.02 * (xmax_ax - xmin_ax), ymin_ax + 0.01 * (ymax_ax - ymin_ax),
        'Q3 안전 (음 상관)', ha='left', va='bottom',
        fontsize=13, color='#406050', weight='bold', bbox=qbox)

ax.set_xlabel('굿하트 노출 점수 (H5 exposure_score, 부처 매핑)', fontsize=13)
ax.set_ylabel('사업이 속한 분야의 outcome 상관 (Pearson r 평균)', fontsize=13)
ax.set_title(f'세부사업 단위 정책 사분면 (n={len(df)} 세부사업)  ·  분석 단위 layer',
             fontsize=15, fontweight='bold', pad=12)
ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.10),
          fontsize=10, framealpha=0.9, ncol=5, frameon=False)
ax.grid(True, alpha=0.25, linestyle=':')
ax.tick_params(labelsize=11)
for spine in ['top', 'right']:
    ax.spines[spine].set_visible(False)

# footnote
ax.text(0.01, -0.08,
        '※ 점 크기 = log_annual(사업 규모) · 색 = TDA+HDBSCAN 자동 군집(C0~C3)',
        transform=ax.transAxes, fontsize=10, color='#666', ha='left')

out = Path('paper/figures/eda/fig_slide38_business_quadrant.png')
out.parent.mkdir(exist_ok=True, parents=True)
plt.savefig(out, dpi=100, facecolor='white')
plt.close()
print(f'\n[Slide 40] {out}')

# 사분면별 카운트
print('\n=== 사분면 분포 ===')
df['quadrant'] = df.apply(
    lambda r: 'Q2 위험' if r['exposure_score']>=x_thr and r['outcome_r']>=y_thr
    else ('Q1 자동분배' if r['exposure_score']>=x_thr and r['outcome_r']<y_thr
    else ('Q4 안전(양)' if r['exposure_score']<x_thr and r['outcome_r']>=y_thr
    else 'Q3 안전(음)')), axis=1)
print(df.groupby(['quadrant', 'cluster']).size().unstack(fill_value=0))
