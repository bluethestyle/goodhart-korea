"""H21: 교육 IMD + 국방예산 outcome 적재.

(1) 교육 — IMD 교육경쟁력 평가 (e-나라지표 idx_cd=1526)
    소스: IMD 「World Competitiveness Yearbook」
    2009~2025 (17년) / 한국 IMD 평가 다중 지표 중 종합 순위 + PISA + 이수율 등

    metric:
      imd_edu_rank             교육경쟁력 종합 순위 (낮을수록 좋음, -1 sign)
      imd_pub_edu_per_capita   국민 1인당 정부재원 교육비 ($)
      imd_higher_edu_25_34     25-34세 고등교육 이수율 (%)
      imd_pisa                 학업성취도(PISA) (점)

    교체 대상: private_edu_hours (사교육 시간, 역지표)

(2) 국방 — 국방예산추이 (e-나라지표 idx_cd=1699)
    소스: 국방부 연도별 예산서
    2006~2026 (21년)

    metric:
      defense_budget_total     국방비 총액 (억원)
      defense_arms_share       방위력개선비 구성비 (%) — 정책 방향 outcome
      defense_share_govt       정부재정 대비 국방비 비율 (%)

    보조: defense_op_margin (방산 영업이익률) — 산업 outcome으로 한정

분야 매핑 부적절 outcome 중 교육·국방 교체 완료.
"""
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import duckdb

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, 'data', 'warehouse.duckdb')

# ----------- (1) IMD 교육경쟁력 -----------
imd_years = list(range(2009, 2026))
imd_data = {
    'imd_edu_rank': [36,35,29,31,25,31,32,33,37,25,30,27,30,29,26,19,27],
    'imd_pub_edu_per_capita': [831,916,793,785,785,1002,1115,1206,1309,1409,1353,1269,1368,1490,1650,1523,1709],
    'imd_higher_edu_25_34': [53.0,56.0,58.0,63.0,65.0,64.0,66.0,67.7,69.0,70.0,69.8,69.6,69.8,69.8,69.3,69.6,69.7],
    # PISA 점수 — 2018부터 발표 (이전은 결측)
    'imd_pisa': [None]*9 + [520.0,520.0,520.0,520.0,520.0,520.0,524.0,524.0],
}
imd_meta = {
    'imd_edu_rank':           ('IMD 교육경쟁력 순위', -1, '순위'),  # 낮을수록 좋음
    'imd_pub_edu_per_capita': ('1인당 정부재원 교육비 (US$/1인)', 1, 'US$'),
    'imd_higher_edu_25_34':   ('25-34세 고등교육 이수율', 1, '%'),
    'imd_pisa':               ('학업성취도 PISA', 1, '점'),
}

# ----------- (2) 국방예산 -----------
def_years = list(range(2006, 2027))
defense_data = {
    'defense_budget_total': [225129,244972,266490,285326,295627,314031,329576,343453,357057,374560,
                              387995,403347,431581,466971,501527,528401,546112,570143,594244,612469,658642],
    'defense_arms_share':    [25.8,27.3,28.8,30.2,30.8,30.9,30.0,29.5,29.4,29.4,
                              30.0,30.2,31.3,32.9,33.3,32.2,30.6,29.7,29.7,29.1,30.3],
    'defense_share_govt':    [15.3,15.7,14.8,14.5,14.7,15.0,14.8,14.5,14.4,14.5,
                              14.5,14.7,14.3,14.1,14.1,13.9,13.0,12.8,13.2,12.9,13.0],
}
defense_meta = {
    'defense_budget_total': ('국방비 총액', 1, '억원'),
    'defense_arms_share':   ('방위력개선비 구성비 (장기 투자 비중)', 1, '%'),
    'defense_share_govt':   ('정부재정 대비 국방비 비율', 0, '%'),  # 0=중립 (입력 변수성)
}

# ============================================================
con = duckdb.connect(DB)
all_codes = list(imd_data.keys()) + list(defense_data.keys())
codes_str = "', '".join(all_codes)
con.execute(f"DELETE FROM indicator_panel WHERE metric_code IN ('{codes_str}')")
con.execute(f"DELETE FROM indicator_metadata WHERE metric_code IN ('{codes_str}')")

records = []
metas = []
for code, vals in imd_data.items():
    nm, sign, unit = imd_meta[code]
    for y, v in zip(imd_years, vals):
        if v is None: continue
        records.append(('교육', y, code, float(v), 'eNaraJiPyo_idx1526', unit))
    metas.append((code, nm, 'outcome',
                   f'IMD World Competitiveness Yearbook — {nm} (e-나라지표 1526)',
                   'https://www.index.go.kr/unity/potal/main/EachDtlPageDetail.do?idx_cd=1526', sign))

for code, vals in defense_data.items():
    nm, sign, unit = defense_meta[code]
    for y, v in zip(def_years, vals):
        records.append(('국방', y, code, float(v), 'eNaraJiPyo_idx1699', unit))
    metas.append((code, nm, 'outcome',
                   f'국방부 연도별 예산서 — {nm} (e-나라지표 1699)',
                   'https://www.index.go.kr/unity/potal/main/EachDtlPageDetail.do?idx_cd=1699', sign))

con.executemany("INSERT INTO indicator_panel (fld_nm, year, metric_code, value, source, unit) VALUES (?,?,?,?,?,?)", records)
con.executemany("INSERT INTO indicator_metadata (metric_code, metric_nm, category, description, source_url, expected_sign) VALUES (?,?,?,?,?,?)", metas)

print(f'적재: panel {len(records)}, meta {len(metas)}')
v = con.execute(f"""
SELECT fld_nm, metric_code, COUNT(*) n, MIN(year) y0, MAX(year) y1, ROUND(AVG(value),2) avg
FROM indicator_panel WHERE metric_code IN ('{codes_str}') GROUP BY 1,2 ORDER BY 1,2
""").fetchdf()
print(v.to_string(index=False))
con.close()
