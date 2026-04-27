"""AI 사업 비용구조 시각화 — 신청서·결과보고서 표지 4컷용.

산출물:
  data/figs/ai_citm_2026.png       편성목 비율 (AI vs 정부평균)
  data/figs/ai_eitm_top.png        편성세목 Top 25 (AI 사업)
  data/figs/ai_top1_decompose.png  1위 사업(2,108억) 통계목 분해
  data/figs/ai_yearly_buckets.png  AI 사업 직접/간접 비율 5년 추이
"""
import os, sys, io, duckdb
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 한글 폰트
for f in ['Malgun Gothic', 'NanumGothic', 'AppleGothic', 'Noto Sans CJK KR']:
    try:
        plt.rcParams['font.family'] = f
        break
    except: pass
plt.rcParams['axes.unicode_minus'] = False

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG_DIR = os.path.join(ROOT, 'data', 'figs')
os.makedirs(FIG_DIR, exist_ok=True)
con = duckdb.connect(os.path.join(ROOT, 'data', 'warehouse.duckdb'), read_only=True)

AI_PATTERN = ("(SACTV_NM ILIKE '%AI%' OR SACTV_NM ILIKE '%인공지능%' OR "
              "SACTV_NM ILIKE '%머신러닝%' OR SACTV_NM ILIKE '%딥러닝%' OR "
              "SACTV_NM ILIKE '%LLM%' OR SACTV_NM ILIKE '%GPT%' OR "
              "SACTV_NM ILIKE '%초거대%' OR SACTV_NM ILIKE '%지능형%')")

# Fig 1: AI vs 정부평균 편성목 비율
df = con.execute(f"""
WITH ai_sum AS (SELECT CITM_NM, sum(Y_YY_DFN_KCUR_AMT) AS amt
                FROM expenditure_item WHERE FSCL_YY=2026 AND SBUDG_DGR=0 AND {AI_PATTERN}
                GROUP BY CITM_NM),
all_sum AS (SELECT CITM_NM, sum(Y_YY_DFN_KCUR_AMT) AS amt
            FROM expenditure_item WHERE FSCL_YY=2026 AND SBUDG_DGR=0
            GROUP BY CITM_NM)
SELECT a.CITM_NM,
       a.amt*100.0/(SELECT sum(amt) FROM ai_sum) AS ai_pct,
       b.amt*100.0/(SELECT sum(amt) FROM all_sum) AS all_pct
FROM ai_sum a LEFT JOIN all_sum b USING (CITM_NM)
ORDER BY ai_pct DESC LIMIT 12
""").fetchdf()

fig, ax = plt.subplots(figsize=(10,6))
y=range(len(df)); h=0.35
ax.barh([i+h/2 for i in y], df['ai_pct'], h, label='AI 사업', color='#d62728')
ax.barh([i-h/2 for i in y], df['all_pct'], h, label='정부 평균', color='#7f7f7f')
ax.set_yticks(y); ax.set_yticklabels(df['CITM_NM'])
ax.invert_yaxis(); ax.set_xlabel('전체 대비 비중 (%)')
ax.set_title('편성목별 예산 비중 — AI 사업 vs 정부 평균 (2026 본예산)')
ax.legend(); ax.grid(axis='x', alpha=0.3)
plt.tight_layout(); plt.savefig(f'{FIG_DIR}/ai_citm_2026.png', dpi=140)
plt.close()
print('saved: ai_citm_2026.png')

# Fig 2: EITM 상위 25
df = con.execute(f"""
SELECT EITM_NM, sum(Y_YY_DFN_KCUR_AMT)/1e6 AS amt_eok
FROM expenditure_item
WHERE FSCL_YY=2026 AND SBUDG_DGR=0 AND {AI_PATTERN}
GROUP BY EITM_NM ORDER BY amt_eok DESC LIMIT 25
""").fetchdf()

fig, ax = plt.subplots(figsize=(11,8))
ax.barh(df['EITM_NM'], df['amt_eok'], color='#1f77b4')
ax.invert_yaxis(); ax.set_xlabel('금액 (억원)')
ax.set_title(f'AI 사업 편성세목 Top 25 (2026 본예산, 총 {df.amt_eok.sum():.0f}억원)')
ax.grid(axis='x', alpha=0.3)
plt.tight_layout(); plt.savefig(f'{FIG_DIR}/ai_eitm_top.png', dpi=140)
plt.close()
print('saved: ai_eitm_top.png')

# Fig 3: 1위 사업 분해
df = con.execute("""
SELECT EITM_NM, sum(Y_YY_DFN_KCUR_AMT)/1e6 AS amt_eok,
       sum(Y_YY_DFN_KCUR_AMT)*100.0/
       (SELECT sum(Y_YY_DFN_KCUR_AMT) FROM expenditure_item
        WHERE FSCL_YY=2026 AND SBUDG_DGR=0 AND SACTV_NM='AI컴퓨팅 자원 활용 기반 강화') AS pct
FROM expenditure_item
WHERE FSCL_YY=2026 AND SBUDG_DGR=0 AND SACTV_NM='AI컴퓨팅 자원 활용 기반 강화'
GROUP BY EITM_NM ORDER BY amt_eok DESC
""").fetchdf()

fig, ax = plt.subplots(figsize=(11,7))
colors = ['#d62728' if any(k in (e or '') for k in ['용역','정책연구','업무추진','여비','경비'])
          else '#2ca02c' if any(k in (e or '') for k in ['자산취득','시설','연구개발','자체연구','장비'])
          else '#7f7f7f' for e in df['EITM_NM']]
ax.barh(df['EITM_NM'], df['amt_eok'], color=colors)
ax.invert_yaxis(); ax.set_xlabel('금액 (억원)')
ax.set_title('★ AI컴퓨팅 자원 활용 기반 강화 (2,108억) — 통계목 분해\n빨강=간접비/용역, 녹색=직접투자/자산')
for i,(v,p) in enumerate(zip(df['amt_eok'], df['pct'])):
    ax.text(v+5, i, f'{v:.0f}억 ({p:.1f}%)', va='center')
ax.grid(axis='x', alpha=0.3)
plt.tight_layout(); plt.savefig(f'{FIG_DIR}/ai_top1_decompose.png', dpi=140)
plt.close()
print('saved: ai_top1_decompose.png')

# Fig 4: 5년 직접/간접 추이
df = con.execute(f"""
WITH cat AS (
  SELECT FSCL_YY,
    CASE
      WHEN CITM_NM IN ('자산취득비','유형자산','무형자산','건설비','자체연구개발비','연구개발비')
        THEN '직접투자'
      WHEN CITM_NM IN ('연구용역비','정책연구비','일반용역비')
        THEN '용역비'
      WHEN CITM_NM IN ('운영비','업무추진비','여비','특수활동비','직무수행경비','일용임금','인건비')
        THEN '운영·경비'
      WHEN CITM_NM IN ('민간이전','일반출연금','보전금','민간경상보조','민간자본보조','출연금','보조금')
        THEN '이전·출연·보조'
      ELSE '기타'
    END AS bucket,
    Y_YY_DFN_KCUR_AMT AS amt
  FROM expenditure_item WHERE SBUDG_DGR=0 AND {AI_PATTERN}
)
SELECT FSCL_YY, bucket, sum(amt)/1e6 AS amt_eok
FROM cat GROUP BY FSCL_YY, bucket ORDER BY FSCL_YY, bucket
""").fetchdf()
piv = df.pivot(index='FSCL_YY', columns='bucket', values='amt_eok').fillna(0)
order = ['직접투자','용역비','이전·출연·보조','운영·경비','기타']
piv = piv[[c for c in order if c in piv.columns]]
fig, ax = plt.subplots(figsize=(11,6))
piv.plot(kind='bar', stacked=True, ax=ax, colormap='Set2', width=0.7)
ax.set_xlabel('회계연도'); ax.set_ylabel('금액 (억원)')
ax.set_title('AI 사업 비용구조 5년 추이 (2020~2026 본예산)')
ax.legend(title='', loc='upper left'); ax.grid(axis='y', alpha=0.3)
plt.xticks(rotation=0)
plt.tight_layout(); plt.savefig(f'{FIG_DIR}/ai_yearly_buckets.png', dpi=140)
plt.close()
print('saved: ai_yearly_buckets.png')

con.close()
print(f'\n그림 4종 저장 완료: {FIG_DIR}')
