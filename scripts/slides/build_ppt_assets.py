"""PPT 보조 차트 생성 (2026-05-20 v2):

- Slide 5 sparkline (× 1.52 라벨)
- Slide 6 bucket × 12월 비중 line (라벨 위치 v2 — 균등선·점유율 겹침 fix)
- App-A top-K 12월 집중 ranking (lookup JSON 기반)
- App-C 14분야 × 사업 단위 12월 비중 box plot
- Slide 6 KPI 정밀화용 집단 mean print

자산: paper/figures/eda/
"""
import duckdb
import json
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from pathlib import Path

# 한국어 폰트
font_path = Path('paper/fonts/Pretendard-Regular.otf')
if font_path.exists():
    fm.fontManager.addfont(str(font_path))
    plt.rcParams['font.family'] = 'Pretendard'
plt.rcParams['axes.unicode_minus'] = False

con = duckdb.connect('data/warehouse.duckdb', read_only=True)
out_dir = Path('paper/figures/eda')
out_dir.mkdir(exist_ok=True, parents=True)

# ──────────────────────────────────────────────────────────────────────
# Slide 5: raw 월합계 11년 평균 sparkline
# ──────────────────────────────────────────────────────────────────────
df5 = con.execute("""
    SELECT EXE_M,
           SUM(EP_AMT) / COUNT(DISTINCT FSCL_YY) / 1e12 AS avg_trillion
    FROM monthly_exec
    WHERE FSCL_YY BETWEEN 2015 AND 2025
    GROUP BY 1 ORDER BY 1
""").fetchdf()

fig, ax = plt.subplots(figsize=(4.2, 1.3), dpi=140)
colors_5 = ['#a0a0a0'] * 12
colors_5[11] = '#555555'
ax.bar(df5['EXE_M'], df5['avg_trillion'], color=colors_5, width=0.7)
ax.set_xticks(range(1, 13))
ax.set_xticklabels([f'{m}' for m in range(1, 13)], fontsize=7, color='#666666')
ax.set_yticks([])
for spine in ['top', 'right', 'left']:
    ax.spines[spine].set_visible(False)
ax.spines['bottom'].set_color('#cccccc')
ax.tick_params(axis='x', length=0)
ax.text(0.98, 1.05, 'raw 월합계 (조원)', transform=ax.transAxes,
        ha='right', va='bottom', fontsize=8, color='#666666')
nov, dec_val = df5.iloc[10]['avg_trillion'], df5.iloc[11]['avg_trillion']
ratio = dec_val / nov
ax.text(0.02, -0.15, f'12월/11월 × {ratio:.2f}', transform=ax.transAxes,
        ha='left', va='top', fontsize=8, color='#333333', weight='bold')
plt.tight_layout()
out5 = out_dir / 'fig_5_aux_raw_sparkline.png'
plt.savefig(out5, dpi=140, bbox_inches='tight', facecolor='white')
plt.close()
print(f'[Slide 5] {out5} | ratio = {ratio:.3f}')

# ──────────────────────────────────────────────────────────────────────
# Slide 6: 집행률 bucket × 12월 비중 line (v2 — 라벨 위치 fix)
# ──────────────────────────────────────────────────────────────────────
df6 = con.execute("""
    WITH act_year AS (
      SELECT FSCL_YY, ACTV_CD,
             MAX(ANEXP_BDG_CAMT) AS budget,
             SUM(EP_AMT) AS annual_exec,
             SUM(CASE WHEN EXE_M=12 THEN EP_AMT ELSE 0 END) AS dec_exec
      FROM monthly_exec WHERE FSCL_YY BETWEEN 2015 AND 2025
      GROUP BY 1,2
    ),
    bucketed AS (
      SELECT CASE
        WHEN annual_exec*1.0/budget < 0.50 THEN '0–50%'
        WHEN annual_exec*1.0/budget < 0.80 THEN '50–80%'
        WHEN annual_exec*1.0/budget < 0.90 THEN '80–90%'
        WHEN annual_exec*1.0/budget < 0.95 THEN '90–95%'
        WHEN annual_exec*1.0/budget < 0.99 THEN '95–99%'
        WHEN annual_exec*1.0/budget <= 1.001 THEN '99–100%'
        ELSE '>100%' END AS bucket,
        annual_exec, dec_exec
      FROM act_year WHERE budget>0 AND annual_exec>0
    )
    SELECT bucket, COUNT(*) AS n, AVG(dec_exec*1.0/annual_exec) AS dec_share
    FROM bucketed GROUP BY 1
""").fetchdf()
order_6 = ['0–50%', '50–80%', '80–90%', '90–95%', '95–99%', '99–100%', '>100%']
df6 = df6.set_index('bucket').loc[order_6].reset_index()
df6_main = df6[df6['bucket'] != '>100%'].reset_index(drop=True)
total_n = df6_main['n'].sum()

fig, ax = plt.subplots(figsize=(8.0, 4.8), dpi=140)
ax.plot(range(len(df6_main)), df6_main['dec_share'] * 100,
        marker='o', markersize=11, linewidth=2.6, color='#C0392B')
# 균등 가정 점선 + 라벨 — 좌상으로
ax.axhline(8.3, color='#888888', linestyle='--', linewidth=1.0)
ax.text(0.05, 9.2, '균등 가정 8.3%', color='#666666', fontsize=10, ha='left')
# 값 라벨 — 99-100%만 위쪽에 (균등선과 분리)
for i, row in df6_main.iterrows():
    val = row['dec_share'] * 100
    if row['bucket'] == '99–100%':
        ax.annotate(f"{val:.1f}%",
                    xy=(i, val),
                    xytext=(0, 18), textcoords='offset points',
                    ha='center', fontsize=10.5, color='#C0392B', weight='bold')
    else:
        ax.annotate(f"{val:.1f}%",
                    xy=(i, val),
                    xytext=(0, 14), textcoords='offset points',
                    ha='center', fontsize=9.5, color='#333333')
# 99-100% 점유율 라벨 — 별도 callout 박스, 우측 분리
for i, row in df6_main.iterrows():
    if row['bucket'] == '99–100%':
        pct = row['n'] / total_n * 100
        ax.annotate(f"전체 사업의 {pct:.1f}%\n— 천장 도달",
                    xy=(i, row['dec_share'] * 100),
                    xytext=(-130, 50), textcoords='offset points',
                    fontsize=10, color='#555555', ha='left',
                    arrowprops=dict(arrowstyle='->', color='#bbbbbb', lw=0.8,
                                    connectionstyle='arc3,rad=0.2'),
                    bbox=dict(boxstyle='round,pad=0.4', facecolor='#f8f8f8',
                              edgecolor='#cccccc'))
ax.set_xticks(range(len(df6_main)))
ax.set_xticklabels(df6_main['bucket'], fontsize=10.5)
ax.set_xlabel('집행률 bucket', fontsize=11)
ax.set_ylabel('12월 비중 평균 (%)', fontsize=11)
ax.set_ylim(0, 32)
for spine in ['top', 'right']:
    ax.spines[spine].set_visible(False)
ax.grid(True, axis='y', alpha=0.3, linestyle=':')
plt.tight_layout()
out6 = out_dir / 'fig_6_exec_bucket_dec.png'
plt.savefig(out6, dpi=140, bbox_inches='tight', facecolor='white')
plt.close()
print(f'[Slide 6 v2] {out6}')

# ──────────────────────────────────────────────────────────────────────
# Slide 6 KPI 정밀화: <95% / 95–100% 집단 mean
# ──────────────────────────────────────────────────────────────────────
group_mean = con.execute("""
    WITH act_year AS (
      SELECT FSCL_YY, ACTV_CD, MAX(ANEXP_BDG_CAMT) AS budget,
             SUM(EP_AMT) AS annual_exec,
             SUM(CASE WHEN EXE_M=12 THEN EP_AMT ELSE 0 END) AS dec_exec
      FROM monthly_exec WHERE FSCL_YY BETWEEN 2015 AND 2025
      GROUP BY 1,2
    ),
    bucketed AS (
      SELECT CASE
        WHEN annual_exec*1.0/budget < 0.95 THEN '<95%'
        WHEN annual_exec*1.0/budget <= 1.001 THEN '95–100%'
        ELSE '>100%' END AS grp,
        annual_exec, dec_exec
      FROM act_year WHERE budget>0 AND annual_exec>0
    )
    SELECT grp, COUNT(*) AS n, AVG(dec_exec*1.0/annual_exec)*100 AS dec_share_pct
    FROM bucketed GROUP BY 1
""").fetchdf()
print('\n[Slide 6 KPI 집단 mean 정밀화]')
print(group_mean.to_string(index=False))

# ──────────────────────────────────────────────────────────────────────
# App-A: top-20 12월 집중 ranking (lookup JSON 기반)
# ──────────────────────────────────────────────────────────────────────
lookup_path = Path('paper/재정데이터 분석 ppt/_mentoring_lookup_raw.json')
with open(lookup_path, 'r', encoding='utf-8') as f:
    lookup = json.load(f)

businesses = []
for cat, recs in lookup['detail'].items():
    if isinstance(recs, list):
        for r in recs:
            if (r.get('dec_share') is not None
                    and r.get('total_exec_eok', 0) > 1000):
                businesses.append({
                    'name': r['ACTV_NM'][:28],
                    'cat': cat.split('·')[0].strip(),
                    'dec_share': r['dec_share'],
                    'exec_rate': r.get('exec_rate') or 0,
                    'eok': r['total_exec_eok'],
                })

# 중복 제거 (이름 기준)
seen = set()
uniq = []
for b in businesses:
    key = b['name']
    if key not in seen:
        seen.add(key)
        uniq.append(b)
uniq.sort(key=lambda x: x['dec_share'], reverse=True)
top_n = uniq[:20]

fig, ax = plt.subplots(figsize=(10, 8), dpi=140)
y = list(range(len(top_n)))
colors_a = ['#C0392B' if b['exec_rate'] < 0.9 else '#888888' for b in top_n]
ax.barh(y, [b['dec_share'] * 100 for b in top_n], color=colors_a)
ax.axvline(8.3, color='#444444', linestyle='--', linewidth=1)
ax.text(8.6, -0.6, '균등 가정 8.3%', fontsize=9, color='#444444')
# 값 + 집행률 라벨
for i, b in enumerate(top_n):
    er = b['exec_rate'] * 100
    txt = f"  {b['dec_share']*100:.1f}%   (집행률 {er:.0f}%)"
    ax.text(b['dec_share'] * 100, i, txt, va='center', fontsize=8.5, color='#555555')
ax.set_yticks(y)
ax.set_yticklabels([f"{b['name']}  · {b['cat']}" for b in top_n], fontsize=9)
ax.invert_yaxis()
ax.set_xlim(0, max(b['dec_share'] for b in top_n) * 100 * 1.35)
ax.set_xlabel('12월 비중 (연 평균, %)', fontsize=11)
for spine in ['top', 'right']:
    ax.spines[spine].set_visible(False)
ax.set_title('주요 사업 12월 집중 ranking (top-20)', fontsize=13, pad=15)
ax.text(0.99, -0.07,
        '빨강 = 집행률 < 90% (불용 위험 → Slide 6 *천장 미도달 burst* 사례)',
        transform=ax.transAxes, ha='right', fontsize=9, color='#555555')
plt.tight_layout()
outA = out_dir / 'fig_appA_top_dec_ranking.png'
plt.savefig(outA, dpi=140, bbox_inches='tight', facecolor='white')
plt.close()
print(f'[App-A] {outA} | n={len(top_n)}')

# ──────────────────────────────────────────────────────────────────────
# App-C: 14분야 × 사업 단위 12월 비중 box plot
# ──────────────────────────────────────────────────────────────────────
df_c = con.execute("""
    WITH act_year AS (
      SELECT FSCL_YY, ACTV_CD, FLD_NM,
             SUM(EP_AMT) AS annual_exec,
             SUM(CASE WHEN EXE_M=12 THEN EP_AMT ELSE 0 END) AS dec_exec
      FROM monthly_exec WHERE FSCL_YY BETWEEN 2015 AND 2025
      GROUP BY 1,2,3
    )
    SELECT FLD_NM,
           CASE WHEN annual_exec>0 THEN dec_exec*1.0/annual_exec END AS dec_share
    FROM act_year WHERE annual_exec>0
""").fetchdf()

order_c = (df_c.groupby('FLD_NM')['dec_share'].median()
           .sort_values(ascending=False).index.tolist())

fig, ax = plt.subplots(figsize=(10, 6.5), dpi=140)
data = [df_c[df_c['FLD_NM'] == f]['dec_share'] * 100 for f in order_c]
bp = ax.boxplot(data, vert=False, patch_artist=True, showfliers=False,
                medianprops=dict(color='#C0392B', linewidth=2),
                whiskerprops=dict(color='#888888'),
                capprops=dict(color='#888888'))
for patch in bp['boxes']:
    patch.set_facecolor('#E8E8E8')
    patch.set_edgecolor('#888888')
ax.axvline(8.3, color='#444444', linestyle='--', linewidth=1)
ax.text(8.7, 0.5, '균등 가정 8.3%', fontsize=9, color='#444444')
ax.set_yticks(range(1, len(order_c) + 1))
ax.set_yticklabels(order_c, fontsize=10)
ax.invert_yaxis()
ax.set_xlabel('사업별 12월 비중 (%)', fontsize=11)
ax.set_title('14분야 내 사업 단위 12월 비중 분포 (분야 중앙값 정렬)',
             fontsize=12, pad=12)
for spine in ['top', 'right']:
    ax.spines[spine].set_visible(False)
ax.grid(True, axis='x', alpha=0.3, linestyle=':')
plt.tight_layout()
outC = out_dir / 'fig_appC_field_dec_box.png'
plt.savefig(outC, dpi=140, bbox_inches='tight', facecolor='white')
plt.close()
print(f'[App-C] {outC}')

print('\n=== ALL CHARTS GENERATED ===')
