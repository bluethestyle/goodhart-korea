"""남은 자산 일괄 생성:
- Slide 16·17·18·19: 4 archetype representative mini bar
- Slide 8: 5 co-cluster × 12개월 line (H3 community 매핑)
"""
import duckdb
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import pandas as pd
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding='utf-8')

font_path = Path('paper/fonts/Pretendard-Regular.otf')
if font_path.exists():
    fm.fontManager.addfont(str(font_path))
    plt.rcParams['font.family'] = 'Pretendard'
plt.rcParams['axes.unicode_minus'] = False

con = duckdb.connect('data/warehouse.duckdb', read_only=True)
out_dir = Path('paper/figures/eda')
out_dir.mkdir(exist_ok=True, parents=True)

# ──────────────────────────────────────────────────────────────────────
# Slide 16·17·18·19 — 4 archetype representative mini bar
# ──────────────────────────────────────────────────────────────────────
REPS = [
    ('Slide 16', 'C0 인건비형 (비교군)', '사회복무지원', '#888888',
     'fig_slide16_c0_rep.png',
     '매월 균등 — 시점 압력이 새겨질 자리가 없다'),
    ('Slide 17', 'C3 정상사업 (비교군)', '소속기관기본경비', '#9b9b9b',
     'fig_slide17_c3_rep.png',
     '평균 부근 — 시점 압력의 모집단 비교군'),
    ('Slide 18', 'C1 자산취득형 (분석 대상)', '평택당진항 개발', '#C0392B',
     'fig_slide18_c1_rep.png',
     '12월 절벽 — Act 3 RDD가 정량 측정하는 결정 사례'),
    ('Slide 19', 'C2 출연금형 (분석 대상)', '원자력연구개발사업', '#E67E22',
     'fig_slide19_c2_rep.png',
     '분기말 cycle — Act 4 Wavelet이 사이클을 분해한다'),
]

for slide, label, name, color, fname, msg in REPS:
    # 연 평균 dec_share 통일 (App-A·메모리 정합) — 각 연도 normalize 후 평균
    q = f"""
    WITH ay AS (
      SELECT FSCL_YY, EXE_M, SUM(EP_AMT) AS s
      FROM monthly_exec
      WHERE ACTV_NM = '{name}' AND FSCL_YY BETWEEN 2015 AND 2025
      GROUP BY 1, 2
    ),
    yr_total AS (
      SELECT FSCL_YY, SUM(s) AS annual FROM ay GROUP BY 1
    )
    SELECT a.EXE_M, AVG(a.s * 1.0 / y.annual) * 100 AS pct_avg
    FROM ay a JOIN yr_total y USING(FSCL_YY)
    WHERE y.annual > 0
    GROUP BY a.EXE_M ORDER BY a.EXE_M
    """
    df = con.execute(q).fetchdf()
    df = df.rename(columns={'pct_avg': 'pct'})

    max_m = int(df.loc[df['pct'].idxmax(), 'EXE_M'])
    colors_bar = [color if m == max_m else '#dddddd' for m in df['EXE_M']]

    fig, ax = plt.subplots(figsize=(8, 3.8), dpi=140)
    ax.bar(df['EXE_M'], df['pct'], color=colors_bar,
           edgecolor='#444', linewidth=0.5)
    ax.axhline(8.33, color='#888', linestyle='--', linewidth=0.7)
    ax.text(11.5, 8.6, '균등 8.3%', fontsize=8, color='#888', ha='right')

    for m, p in zip(df['EXE_M'], df['pct']):
        if p > 5:
            ax.text(m, p + 0.5, f'{p:.1f}', ha='center', fontsize=8,
                    color='#333')

    ax.set_xticks(range(1, 13))
    ax.set_xlabel('월', fontsize=10)
    ax.set_ylabel('월별 집행 비중 (%)', fontsize=10)
    ax.set_title(f'{slide}. {label} 대표: {name}', fontsize=11.5, pad=8)
    ax.text(0.5, -0.30, msg, transform=ax.transAxes,
            ha='center', fontsize=9.5, color=color, style='italic')
    for s in ['top', 'right']:
        ax.spines[s].set_visible(False)
    ax.grid(True, axis='y', alpha=0.25, linestyle=':')
    plt.tight_layout()
    out = out_dir / fname
    plt.savefig(out, dpi=140, bbox_inches='tight', facecolor='white')
    plt.close()
    dec_pct = df.loc[df['EXE_M'] == 12, 'pct'].iloc[0] if 12 in df['EXE_M'].values else 0
    print(f'[{slide}] {name} dec={dec_pct:.1f}% -> {out}')

# ──────────────────────────────────────────────────────────────────────
# Slide 8 — 부처별 12월 비중 ranking (모든 부처 12월 봉우리)
# narrative: "부처를 떼어내도 패턴은 사라지지 않는다"
# (co-cluster 자료는 v1=3·v2=7로 main_v2 §6.x "5 co-cluster"와 정합 미흡 →
#  단순 부처 ranking이 메시지에 더 직접)
# ──────────────────────────────────────────────────────────────────────
q = """
WITH ay AS (
  SELECT FSCL_YY, OFFC_NM, SUM(EP_AMT) AS annual,
         SUM(CASE WHEN EXE_M=12 THEN EP_AMT ELSE 0 END) AS dec_exec
  FROM monthly_exec WHERE FSCL_YY BETWEEN 2015 AND 2025 AND EP_AMT > 0
  GROUP BY 1, 2
)
SELECT OFFC_NM, AVG(CASE WHEN annual>0 THEN dec_exec*1.0/annual END)*100 AS dec_pct
FROM ay GROUP BY OFFC_NM ORDER BY dec_pct DESC
"""
df_off = con.execute(q).fetchdf()
df_off = df_off[df_off['dec_pct'].notna()]
print(f'\n부처 수 (12월 비중 추출): {len(df_off)}')

# 상위 부처 + 하위 부처 (양 끝)
n_show = min(len(df_off), 51)
df_off = df_off.iloc[:n_show]

fig, ax = plt.subplots(figsize=(10, 11), dpi=140)
y = list(range(len(df_off)))
colors_8 = ['#C0392B' if v > 15 else ('#E67E22' if v > 10 else '#888')
            for v in df_off['dec_pct'].values]
ax.barh(y, df_off['dec_pct'].values, color=colors_8,
        edgecolor='#444', linewidth=0.3)
ax.axvline(8.33, color='#444', linestyle='--', linewidth=1)
ax.text(8.5, -0.5, '균등 가정 8.3%', fontsize=9, color='#444')

ax.set_yticks(y)
ax.set_yticklabels(df_off['OFFC_NM'].tolist(), fontsize=8)
ax.invert_yaxis()
ax.set_xlabel('연 평균 12월 집행 비중 (%)', fontsize=11)
ax.set_title(f'Slide 8. 부처 {len(df_off)}개 — 모든 부처에서 12월 봉우리\n'
             f'(빨강 >15% · 주황 >10% · 회색 ≤10%) — '
             f'"부처를 떼어내도 패턴은 사라지지 않는다"',
             fontsize=12, pad=10)
for s in ['top', 'right']:
    ax.spines[s].set_visible(False)
ax.grid(True, axis='x', alpha=0.25, linestyle=':')

# 통계 라벨
n_above_8 = (df_off['dec_pct'] > 8.33).sum()
ax.text(0.99, 0.02,
        f'※ {n_above_8}/{len(df_off)} 부처가 균등 가정(8.3%) 초과 = '
        f'{n_above_8/len(df_off)*100:.0f}%',
        transform=ax.transAxes, ha='right', fontsize=9, color='#555',
        style='italic')

plt.tight_layout()
out8 = out_dir / 'fig_slide8_ministry_dec_ranking.png'
plt.savefig(out8, dpi=140, bbox_inches='tight', facecolor='white')
plt.close()
print(f'[Slide 8] {out8} | {n_above_8}/{len(df_off)} 부처 균등 가정 초과')

print('\n=== ALL REMAINING ASSETS DONE ===')
