"""원자력연구개발사업·국방과학연구소·함정 연구개발 월별 패턴 확인."""
import duckdb
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

con = duckdb.connect('data/warehouse.duckdb', read_only=True)

CANDIDATES = ['원자력연구개발사업', '국방과학연구소', '함정 연구개발',
              '국립대학병원 여건개선', '농산물가격안정및수급조절(농특)']

for actv in CANDIDATES:
    q = """
    WITH ay AS (
      SELECT FSCL_YY, EXE_M, SUM(EP_AMT) AS s
      FROM monthly_exec
      WHERE ACTV_NM = ? AND FSCL_YY BETWEEN 2015 AND 2025
      GROUP BY 1, 2
    ),
    yt AS (SELECT FSCL_YY, SUM(s) AS yr FROM ay GROUP BY 1 HAVING yr > 0)
    SELECT EXE_M, AVG(s*1.0/yr)*100 AS pct
    FROM ay JOIN yt USING (FSCL_YY)
    GROUP BY EXE_M ORDER BY EXE_M
    """
    rows = con.execute(q, [actv]).fetchall()
    if not rows:
        print(f'NOT FOUND: {actv}')
        continue
    print(f'\n=== {actv} ===')
    for m, pct in rows:
        bar = '█' * int(pct * 2)
        flag = ' ← 분기 첫달' if m in (1,4,7,10) else (' ← 분기말' if m in (3,6,9,12) else '')
        print(f'  {m:2d}월 {pct:5.2f}% {bar}{flag}')
    arr = [r[1] for r in rows]
    print(f'  분기 첫달(1·4·7·10) 합: {sum(arr[i-1] for i in (1,4,7,10)):.1f}%')
    print(f'  분기말(3·6·9·12) 합  : {sum(arr[i-1] for i in (3,6,9,12)):.1f}%')
