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

# 분야명 정합 — H3의 FLD_NM과 H10의 field 매핑
# H3 FLD_NM 예: 공공질서및안전·과학기술·교육·교통및물류·국방·국토및지역개발 ...
# H10 field 예: 사회복지·보건·... (동일 형식 가정)
emb['outcome_r'] = emb['FLD_NM'].map(field_corr)
matched = emb['outcome_r'].notna().sum()
print(f'분야 outcome r 매칭: {matched}/{len(emb)} 세부사업')

# 매칭된 세부사업만 사용
df = emb[emb['outcome_r'].notna()].copy()
print(f'시각화 대상: {len(df)} 세부사업')

# cluster 색 + 라벨
cluster_color = {0: '#a0a0a0', 1: '#C0392B', 2: '#E67E22', 3: '#cccccc'}
cluster_label = {0: 'C0 인건비형 (비교군)', 1: 'C1 자산취득형 (분석 대상)',
                 2: 'C2 출연금형 (분석 대상)', 3: 'C3 정상사업 (비교군)'}

# 점 크기 (log_annual normalize)
size_min, size_max = df['log_annual'].quantile([0.05, 0.95])
df['size'] = ((df['log_annual'] - size_min) / (size_max - size_min)).clip(0.1, 1.0) * 50 + 8

# 사분면 라인 (x_thr = exposure 75% quantile, y_thr = 0)
# amp_12m_norm은 절댓값 분포 (0~1.92, median 0.49). 75% percentile = 0.74를
# 임계로 — 상위 25%를 *위험/주의 군* 라벨.
x_thr = df['amp_12m_norm'].quantile(0.75)
y_thr = 0.0
print(f'x_thr (75% percentile) = {x_thr:.3f}, y_thr = {y_thr}')

fig, ax = plt.subplots(figsize=(9, 7), dpi=140)

# 4분면 라인 + 배경 (h14 quadrant 컬러 스킴)
# 배경은 axvspan/axhspan 조합. 4분면 명확 구분.
ymin_data, ymax_data = df['outcome_r'].min(), df['outcome_r'].max()
xmin_data, xmax_data = df['amp_12m_norm'].min(), df['amp_12m_norm'].max()
margin_x = (xmax_data - xmin_data) * 0.05
margin_y = (ymax_data - ymin_data) * 0.10
ax.set_xlim(xmin_data - margin_x, xmax_data + margin_x)
ax.set_ylim(ymin_data - margin_y, ymax_data + margin_y)

# 4분면 배경 (좌상·우상·좌하·우하)
from matplotlib.patches import Rectangle
rect_q2 = Rectangle((x_thr, y_thr), xmax_data + margin_x - x_thr,
                     ymax_data + margin_y - y_thr,
                     facecolor='#F8E0E0', alpha=0.3, zorder=0)
rect_q1 = Rectangle((x_thr, ymin_data - margin_y), xmax_data + margin_x - x_thr,
                     y_thr - (ymin_data - margin_y),
                     facecolor='#FFE8D6', alpha=0.3, zorder=0)
rect_q4 = Rectangle((xmin_data - margin_x, y_thr), x_thr - (xmin_data - margin_x),
                     ymax_data + margin_y - y_thr,
                     facecolor='#E0F0F8', alpha=0.3, zorder=0)
rect_q3 = Rectangle((xmin_data - margin_x, ymin_data - margin_y),
                     x_thr - (xmin_data - margin_x),
                     y_thr - (ymin_data - margin_y),
                     facecolor='#E0F0E8', alpha=0.3, zorder=0)
for r in [rect_q2, rect_q1, rect_q4, rect_q3]:
    ax.add_patch(r)

# cluster별 산점
for c in [3, 0, 2, 1]:  # C1 최상위 그리도록
    sub = df[df['cluster'] == c]
    ax.scatter(sub['amp_12m_norm'], sub['outcome_r'],
               s=sub['size'], c=cluster_color[c],
               label=f'{cluster_label[c]} (n={len(sub)})',
               alpha=0.65, edgecolors='#444', linewidths=0.4, zorder=2)

# 4분면 라인
ax.axvline(x_thr, color='#555', linewidth=0.8, zorder=1)
ax.axhline(y_thr, color='#555', linewidth=0.8, zorder=1)

# 4분면 라벨 (각 사분면 가운데 위치)
xmin_ax, xmax_ax = ax.get_xlim()
ymin_ax, ymax_ax = ax.get_ylim()
ax.text((x_thr + xmax_ax) / 2, ymax_ax * 0.85, 'Q2 위험\n(점검 필요)',
        ha='center', fontsize=10.5, color='#A04040', weight='bold')
ax.text((x_thr + xmax_ax) / 2, ymin_ax * 0.85, 'Q1 자동분배',
        ha='center', fontsize=10.5, color='#A06030')
ax.text((xmin_ax + x_thr) / 2, ymax_ax * 0.85, 'Q4 안전\n(양 상관)',
        ha='center', fontsize=10.5, color='#406080')
ax.text((xmin_ax + x_thr) / 2, ymin_ax * 0.85, 'Q3 안전\n(음 상관)',
        ha='center', fontsize=10.5, color='#406050')

ax.set_xlabel('시점 압력 지수 (amp_12m_norm, Z-score)', fontsize=11)
ax.set_ylabel('사업이 속한 분야의 outcome 상관 (Pearson r 평균)', fontsize=11)
ax.set_title(f'세부사업 단위 정책 사분면 (n={len(df)} 세부사업)\n'
             f'분석 단위 layer — 부처 사분면(h14)과 좌우 병치',
             fontsize=12, pad=12)
ax.legend(loc='lower right', fontsize=9, framealpha=0.9)
ax.grid(True, alpha=0.25, linestyle=':')
for spine in ['top', 'right']:
    ax.spines[spine].set_visible(False)

# footnote
ax.text(0.01, -0.10,
        '※ 점 크기 = log_annual(사업 규모). 색 = TDA+HDBSCAN 자동 군집(C0~C3).',
        transform=ax.transAxes, fontsize=8, color='#666', ha='left')

plt.tight_layout()
out = Path('paper/figures/eda/fig_slide40_business_quadrant.png')
out.parent.mkdir(exist_ok=True, parents=True)
plt.savefig(out, dpi=140, bbox_inches='tight', facecolor='white')
plt.close()
print(f'\n[Slide 40] {out}')

# 사분면별 카운트
print('\n=== 사분면 분포 ===')
df['quadrant'] = df.apply(
    lambda r: 'Q2 위험' if r['amp_12m_norm']>=x_thr and r['outcome_r']>=y_thr
    else ('Q1 자동분배' if r['amp_12m_norm']>=x_thr and r['outcome_r']<y_thr
    else ('Q4 안전(양)' if r['amp_12m_norm']<x_thr and r['outcome_r']>=y_thr
    else 'Q3 안전(음)')), axis=1)
print(df.groupby(['quadrant', 'cluster']).size().unstack(fill_value=0))
