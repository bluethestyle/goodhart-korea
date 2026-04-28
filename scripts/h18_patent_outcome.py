"""H18: 과학기술 outcome — 특허 등 출원/등록건수 (e-나라지표 idx_cd=2787).

소스: 지식재산처 「지식재산통계연보」, e-나라지표 정적.
시계열: 2003~2024 (22년)

분야: 과학기술
metric: patent_apps_total      산업재산권 출원 계
        patent_apps_patent     특허 출원
        patent_grants_total    산업재산권 등록 계
        patent_grants_patent   특허 등록

해석:
  출원(application) = 권리 *요청* 행위
  등록(grant) = 실제 권리 *부여* (심사 통과)
  → 등록이 outcome 적합도 높음 (정부 R&D 사업의 산출물)

대체 대상: rd_total (산업R&D비) — 입력 변수와 outcome 동일 문제
교체: patent_apps_total (또는 patent_grants_total)
"""
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import duckdb

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, 'data', 'warehouse.duckdb')

years = list(range(2003, 2025))

# 출원
data = {
    'patent_apps_total':    [306001,327516,359207,372520,380203,372697,364990,362074,371116,396996,
                             430164,434047,475802,463862,457955,480245,510968,557256,592615,556436,556600,560629],
    'patent_apps_patent':   [118652,140115,160921,166189,172469,170632,163523,170101,178924,188915,
                             204589,210292,213694,208830,204775,209992,218975,226759,237998,237633,243310,246245],
    'patent_grants_total':  [155840,165375,198094,250557,227606,193939,145927,159977,214013,243869,
                             280691,288542,274424,286586,289656,286657,306522,303669,341873,326740,359263,333925],
    'patent_grants_patent': [44165,49068,73512,120790,123705,83523,56732,68843,94720,113467,
                             127330,129786,101873,108875,120662,119012,125661,134766,145882,135180,134734,127806],
}
nm_map = {
    'patent_apps_total':    '산업재산권 출원 (총계)',
    'patent_apps_patent':   '특허 출원',
    'patent_grants_total':  '산업재산권 등록 (총계)',
    'patent_grants_patent': '특허 등록',
}
sign_map = {k: 1 for k in data}  # 모두 +1 (높을수록 outcome 좋음)

con = duckdb.connect(DB)
codes = "', '".join(data.keys())
con.execute(f"DELETE FROM indicator_panel WHERE metric_code IN ('{codes}')")
con.execute(f"DELETE FROM indicator_metadata WHERE metric_code IN ('{codes}')")

records = []
for code, vals in data.items():
    for y, v in zip(years, vals):
        records.append(('과학기술', y, code, float(v),
                        'eNaraJiPyo_idx2787', '건'))

con.executemany("INSERT INTO indicator_panel (fld_nm, year, metric_code, value, source, unit) VALUES (?,?,?,?,?,?)", records)

meta = [(code, nm_map[code], 'outcome',
         f'지식재산처 지식재산통계연보 — {nm_map[code]} (e-나라지표 2787)',
         'https://www.index.go.kr/unity/potal/main/EachDtlPageDetail.do?idx_cd=2787', sign_map[code])
        for code in data.keys()]
con.executemany("INSERT INTO indicator_metadata (metric_code, metric_nm, category, description, source_url, expected_sign) VALUES (?,?,?,?,?,?)", meta)

print(f'적재: panel {len(records)}, meta {len(meta)}')
print('\n=== 검증 ===')
v = con.execute(f"""
SELECT metric_code, COUNT(*) n, MIN(year) y0, MAX(year) y1, ROUND(AVG(value),0) avg
FROM indicator_panel WHERE metric_code IN ('{codes}') GROUP BY 1 ORDER BY 1
""").fetchdf()
print(v.to_string(index=False))
con.close()
