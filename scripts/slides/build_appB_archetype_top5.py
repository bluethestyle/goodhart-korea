"""App-B 재설계 — 4 archetype × top 5 대표 사업 (log_annual desc) 월별 평균 비중 시계열.

각 archetype 안의 사업 다양성 시각 — 본 슬라이드 16~19의 *대표 1개*에서 *5개*로 확장.

출력: paper/figures/eda/fig_appB_archetype_top5.png (1280×800, 4 row × 5 col grid)
"""
import sys, io
import numpy as np
import pandas as pd
import duckdb
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(__file__).resolve().parent.parent.parent
font_path = ROOT / 'paper' / 'fonts' / 'Pretendard-Regular.otf'
if font_path.exists():
    fm.fontManager.addfont(str(font_path))
    plt.rcParams['font.family'] = 'Pretendard'
plt.rcParams['axes.unicode_minus'] = False

DB_PATH  = ROOT / 'data' / 'warehouse.duckdb'
EMB_PATH = ROOT / 'data' / 'results' / 'H3_activity_embedding_11y.csv'
OUT_PATH = ROOT / 'paper' / 'figures' / 'eda' / 'fig_appB_archetype_top5.png'

# Archetype 색 + 라벨 (Slide 28 통일)
CLUSTER_INFO = {
    0: {'color': '#888888', 'label': 'C0 인건비형',  'short': 'C0', 'emphasis': False},
    1: {'color': '#C0392B', 'label': 'C1 자산취득형', 'short': 'C1', 'emphasis': True},
    2: {'color': '#E67E22', 'label': 'C2 출연금형',  'short': 'C2', 'emphasis': True},
    3: {'color': '#9B9B9B', 'label': 'C3 정상사업',  'short': 'C3', 'emphasis': False},
}

def shorten_name(name, maxlen=20):
    return name if len(name) <= maxlen else name[:maxlen-1] + '…'

# ── 1) 각 cluster top 5 추출 ──────────────────────────────────────────
emb = pd.read_csv(EMB_PATH)
top5 = {}
for c in [0, 1, 2, 3]:
    sub = emb[emb['cluster'] == c].nlargest(5, 'log_annual').reset_index(drop=True)
    top5[c] = sub[['ACTV_NM', 'OFFC_NM', 'log_annual', 'dec_pct']]

# ── 2) 각 사업 월별 평균 비중 추출 ───────────────────────────────────
con = duckdb.connect(str(DB_PATH), read_only=True)

# 20개 사업명 리스트
all_actv = pd.concat([top5[c] for c in [0,1,2,3]])['ACTV_NM'].unique().tolist()

# DuckDB 임시 등록
actv_df = pd.DataFrame({'ACTV_NM': all_actv})
con.register('actv_tmp', actv_df)

# 각 사업 × 월별 비중 (11년 평균)
ts = con.execute("""
    WITH yearly AS (
        SELECT m.ACTV_NM, m.FSCL_YY, m.EXE_M,
               SUM(m.EP_AMT) AS monthly_sum,
               SUM(SUM(m.EP_AMT)) OVER (PARTITION BY m.ACTV_NM, m.FSCL_YY) AS annual_sum
        FROM monthly_exec m JOIN actv_tmp a ON m.ACTV_NM = a.ACTV_NM
        WHERE m.FSCL_YY BETWEEN 2015 AND 2025
        GROUP BY m.ACTV_NM, m.FSCL_YY, m.EXE_M
    )
    SELECT ACTV_NM, EXE_M,
           AVG(CASE WHEN annual_sum > 0 THEN monthly_sum / annual_sum * 100 ELSE 0 END) AS pct
    FROM yearly
    GROUP BY ACTV_NM, EXE_M
    ORDER BY ACTV_NM, EXE_M
""").fetchdf()
con.close()

# pivot: ACTV_NM × month (1-12)
ts_pivot = ts.pivot(index='ACTV_NM', columns='EXE_M', values='pct').fillna(0)
print('월별 비중 추출:', ts_pivot.shape)
print(ts_pivot.head())

# ── 3) 4 row × 5 col grid 차트 ──────────────────────────────────────
fig, axes = plt.subplots(4, 5, figsize=(16, 10), dpi=80,
                         gridspec_kw={'hspace': 0.55, 'wspace': 0.25,
                                      'left': 0.05, 'right': 0.97,
                                      'top': 0.91, 'bottom': 0.06})

for row, c in enumerate([0, 1, 2, 3]):
    info = CLUSTER_INFO[c]
    color = info['color']
    emphasis = info['emphasis']
    for col, (_, biz) in enumerate(top5[c].iterrows()):
        ax = axes[row, col]
        actv = biz['ACTV_NM']
        if actv in ts_pivot.index:
            vals = ts_pivot.loc[actv].values
            months = ts_pivot.columns.values
        else:
            vals = np.zeros(12); months = np.arange(1, 13)

        # bar + line 동시 (시각 풍부)
        bar_colors = [color if m == 12 else '#cccccc' for m in months]
        ax.bar(months, vals, color=bar_colors, alpha=0.85,
               edgecolor='none', width=0.7, zorder=2)
        # 균등 가정 8.3% 점선
        ax.axhline(8.33, color='#999', lw=0.7, linestyle=':', alpha=0.5, zorder=1)

        # title
        title = shorten_name(actv, 18)
        title_color = color if emphasis else '#222'
        title_weight = 'bold' if emphasis else 'normal'
        ax.set_title(title, fontsize=10, color=title_color,
                     fontweight=title_weight, pad=4, loc='left')

        # KPI subtitle
        dec = biz['dec_pct'] * 100
        ax.text(0.99, 0.95, f'12월 {dec:.1f}%', transform=ax.transAxes,
                ha='right', va='top', fontsize=8.5, color='#555',
                fontweight='semibold')

        # axis
        ax.set_xlim(0.3, 12.7)
        ax.set_xticks([1, 6, 12])
        ax.set_xticklabels(['1', '6', '12'], fontsize=8)
        # y range — 사업별 자동 (visualization)
        ymax = max(15, vals.max() * 1.2)
        ax.set_ylim(0, ymax)
        ax.tick_params(axis='y', labelsize=7)
        ax.grid(True, axis='y', alpha=0.2, linestyle=':', zorder=0)
        for s in ['top', 'right']:
            ax.spines[s].set_visible(False)

        # 좌측 row 라벨
        if col == 0:
            ax.set_ylabel(f"{info['label']}\n", fontsize=11,
                          color=color, fontweight='bold')

# 전체 title
fig.suptitle('4 Archetype × Top 5 대표 사업 — 월별 평균 비중 (11년 평균, 사업 규모 desc)',
             fontsize=15, fontweight='bold', y=0.97, color='#0F172A')

# footer
fig.text(0.5, 0.018,
         '회색 막대 = 1~11월 · 색 막대 = 12월 · 점선 = 균등 가정 8.3%',
         ha='center', fontsize=10, color='#64748B', style='italic')

OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(OUT_PATH, dpi=80, facecolor='white')
plt.close()

from PIL import Image
print(f'\nSaved: {OUT_PATH}')
print(f'Size:  {Image.open(OUT_PATH).size}')

# KPI 요약 출력
print('\n=== 4 archetype × top 5 사업 ===')
for c in [0,1,2,3]:
    info = CLUSTER_INFO[c]
    print(f"\n{info['label']}:")
    for _, biz in top5[c].iterrows():
        print(f"  {shorten_name(biz['ACTV_NM'], 25):<28s} dec={biz['dec_pct']*100:5.1f}%  (log_annual={biz['log_annual']:.2f})")
