"""data/*.json을 사람이 읽기 좋은 docs/ 마크다운으로 정리.

생성물:
- docs/README.md
- docs/openapi/INDEX.md
- docs/openapi/{slug}.md (분류별 명세)
- docs/kodas/INDEX.md
- docs/kodas/{slug}.md (분류별 카탈로그)
"""
import json, os, re, sys, io
from collections import defaultdict, Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, 'docs')
OPENAPI_DIR = os.path.join(DOCS, 'openapi')
KODAS_DIR = os.path.join(DOCS, 'kodas')
os.makedirs(OPENAPI_DIR, exist_ok=True)
os.makedirs(KODAS_DIR, exist_ok=True)

LOAD_PRD = {  # dtaLoadPrdCd 코드 매핑 (관찰값)
    'RECY00': '비주기/단발', 'RECY02': '월간', 'RECY03': '분기', 'RECY05': '연간', 'RECY07': '실시간',
}
SVC_TY = {  # rlsSvIxNm 코드 (관찰값)
    'S-1,A-2': '통계(기본)+OpenAPI', 'A-1': 'OpenAPI 단독',
    'S-1,A-2,C-3': '통계+OpenAPI+다운로드', 'S-1,C-2,A-3': '통계+다운로드+OpenAPI',
    'A-1,S-2': 'OpenAPI(기본)+통계',
}

def slug(s):
    s = re.sub(r'[\\/:*?"<>|]', '-', s or '_unsorted')
    return s.strip().replace(' ', '_')[:60]

def md_table(rows, headers):
    """rows: list of list. headers: list of str. Returns markdown table string."""
    if not rows:
        return '_(없음)_\n'
    out = ['| ' + ' | '.join(headers) + ' |',
           '|' + '|'.join(['---'] * len(headers)) + '|']
    for r in rows:
        cells = []
        for c in r:
            v = '' if c is None else str(c)
            v = v.replace('|', '\\|').replace('\n', ' ').strip()
            cells.append(v)
        out.append('| ' + ' | '.join(cells) + ' |')
    return '\n'.join(out) + '\n'

def group_openapi(specs):
    """2단계 분류 기준 그룹핑. 분류 미지정 + odtNm '(OPEN API)' prefix → 'raw_예산편성' 그룹."""
    groups = defaultdict(list)
    for s in specs:
        cat = s.get('category')
        nm = s.get('odtNm') or ''
        if not cat and nm.startswith('(OPEN API)'):
            key = ('raw_예산편성', '예산편성·집행 원시 데이터')
        elif cat:
            parts = cat.split('>')
            # normalize: 상세재정통계>... → 중앙정부>상세재정통계>...
            if parts[0] == '상세재정통계':
                parts = ['중앙정부'] + parts
            top = parts[0]
            sub = parts[1] if len(parts) > 1 else '기타'
            key = (f'{top}_{sub}', f'{top} / {sub}')
        else:
            key = ('기타', '기타')
        groups[key].append(s)
    return groups

def render_openapi_dataset(d):
    out = []
    out.append(f"### {d['odtNm']}")
    out.append('')
    out.append(f"- **odtId**: `{d['odtId']}`")
    if d.get('category'):
        out.append(f"- **분류**: {d['category']}")
    out.append(f"- **생산기관**: {d.get('producer') or '-'}")
    if d.get('sourceSystem'):
        out.append(f"- **원천**: {d['sourceSystem']}")
    cycle = LOAD_PRD.get(d.get('updateCycleCode'), d.get('updateCycleCode') or '-')
    out.append(f"- **공표주기**: {cycle}")
    sty = SVC_TY.get(d.get('serviceTypes'), d.get('serviceTypes') or '-')
    out.append(f"- **서비스유형**: {sty}")
    if d.get('license'):
        out.append(f"- **라이선스**: {d['license']}")
    if d.get('opeDt'):
        out.append(f"- **개시일**: {d['opeDt']}")
    if d.get('apiUrl'):
        out.append(f"- **API URL**: `{d['apiUrl']}`")
    if d.get('description'):
        out.append('')
        out.append(f"> {d['description'].strip()}")
    out.append('')
    out.append('**요청 파라미터**')
    out.append('')
    out.append(md_table(
        [[p['name'], p['koName'], p['description'], '✓' if p['required'] else ''] for p in d.get('requestParams') or []],
        ['파라미터', '한글명', '설명', '필수']
    ))
    out.append('')
    out.append('**응답 필드**')
    out.append('')
    out.append(md_table(
        [[f.get('order'), f.get('name'), f.get('koName'), f.get('description')] for f in d.get('responseFields') or []],
        ['#', '필드명', '한글명', '설명']
    ))
    out.append('')
    return '\n'.join(out)

def build_openapi_docs():
    specs = json.load(open(os.path.join(ROOT, 'data', 'api_specs.json'), encoding='utf-8'))
    specs.sort(key=lambda s: (s.get('category') or 'zz', s.get('odtNm') or ''))
    groups = group_openapi(specs)
    # sort group keys with 중앙정부 first
    order = lambda kv: (0 if kv[0][1].startswith('중앙정부') else 1, kv[0][1])
    sorted_groups = sorted(groups.items(), key=order)

    # per-group files
    file_map = []
    for (gslug, gname), items in sorted_groups:
        fn = f'{slug(gslug)}.md'
        path = os.path.join(OPENAPI_DIR, fn)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(f'# {gname}\n\n')
            f.write(f'> {len(items)}개 데이터셋 · 상위 인덱스: [../INDEX.md](INDEX.md)\n\n')
            f.write('## 목차\n\n')
            for d in items:
                anchor = re.sub(r'[^\w가-힣 -]', '', d['odtNm']).strip().replace(' ', '-').lower()
                f.write(f'- [{d["odtNm"]}](#{anchor})\n')
            f.write('\n---\n\n')
            for d in items:
                f.write(render_openapi_dataset(d))
                f.write('\n---\n\n')
        file_map.append((gname, fn, len(items)))

    # INDEX.md
    with open(os.path.join(OPENAPI_DIR, 'INDEX.md'), 'w', encoding='utf-8') as f:
        f.write('# 열린재정 Open API 명세 인덱스\n\n')
        f.write(f'총 **{len(specs)}개** 데이터셋 · 출처: <https://www.openfiscaldata.go.kr/op/ko/ds/UOPKODSA06>\n\n')
        f.write('## 분류별 문서\n\n')
        f.write('| 분류 | 건수 | 문서 |\n|---|---:|---|\n')
        for gname, fn, n in file_map:
            f.write(f'| {gname} | {n} | [{fn}]({fn}) |\n')
        f.write('\n## 통계\n\n')
        f.write('### 생산기관\n\n')
        for k, v in Counter(s.get('producer') for s in specs).most_common():
            f.write(f'- {k}: {v}\n')
        f.write('\n### 공표주기\n\n')
        for k, v in Counter(LOAD_PRD.get(s.get('updateCycleCode'), s.get('updateCycleCode')) for s in specs).most_common():
            f.write(f'- {k}: {v}\n')
        f.write('\n### 서비스유형\n\n')
        for k, v in Counter(SVC_TY.get(s.get('serviceTypes'), s.get('serviceTypes')) for s in specs).most_common():
            f.write(f'- {k}: {v}\n')
        f.write('\n## 전체 데이터셋 목록\n\n')
        f.write(md_table(
            [[s['odtNm'], s.get('category') or '-', s.get('producer') or '-',
              f'`{s["apiUrl"].split("/")[-1]}`' if s.get('apiUrl') else '-',
              len(s.get('requestParams') or []), len(s.get('responseFields') or [])]
             for s in specs],
            ['데이터셋명', '분류', '생산기관', 'API코드', '요청파라미터', '응답필드']
        ))
    print(f'[openapi] 그룹 {len(file_map)}개, 데이터셋 {len(specs)}개')

def build_kodas_docs():
    items = json.load(open(os.path.join(ROOT, 'data', 'kodas_catalog.json'), encoding='utf-8'))
    by_cat = defaultdict(list)
    for it in items:
        by_cat[it.get('dtaCtlgNm') or '(미분류)'].append(it)
    ordered = sorted(by_cat.items(), key=lambda kv: (-len(kv[1]), kv[0]))

    file_map = []
    for cat, lst in ordered:
        fn = f'{slug(cat)}.md'
        path = os.path.join(KODAS_DIR, fn)
        lst.sort(key=lambda x: x.get('dsHgNm') or '')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(f'# KODAS · {cat}\n\n')
            f.write(f'> {len(lst)}개 데이터 · 상위 인덱스: [../INDEX.md](INDEX.md)\n\n')
            f.write(md_table(
                [[d['dsHgNm'], d.get('instNm') or '-', d.get('alyDataDtaPrdDes') or '-',
                  d.get('lastMdfcnTdtTxt') or '-', f'`{d.get("dsId")}`',
                  ((d.get('dsHgEpl') or '').replace('\\n', ' ').strip()[:160])]
                 for d in lst],
                ['데이터명', '자료제공처', '분석기간', '최종수정', 'dsId', '설명(요약)']
            ))
        file_map.append((cat, fn, len(lst)))

    with open(os.path.join(KODAS_DIR, 'INDEX.md'), 'w', encoding='utf-8') as f:
        f.write('# KODAS 제공 데이터 카탈로그 인덱스\n\n')
        f.write(f'총 **{len(items)}개** 데이터 · 출처: <https://www.openfiscaldata.go.kr/op/ko/sb/UOPKOSBZ01>\n\n')
        f.write('## 분류별 문서\n\n')
        f.write('| 분류 | 건수 | 문서 |\n|---|---:|---|\n')
        for cat, fn, n in file_map:
            f.write(f'| {cat} | {n} | [{fn}]({fn}) |\n')
        f.write('\n## 자료제공처 분포 (상위 20)\n\n')
        for k, v in Counter(it.get('instNm') for it in items).most_common(20):
            f.write(f'- {k}: {v}\n')
    print(f'[kodas]   분류 {len(file_map)}개, 데이터 {len(items)}개')

def build_root_readme():
    with open(os.path.join(DOCS, 'README.md'), 'w', encoding='utf-8') as f:
        f.write('''# 재정자료 데이터 명세 정리

열린재정 정보공개시스템(<https://www.openfiscaldata.go.kr>)의 두 가지 데이터 자원 명세서.

## 1. 열린재정 Open API — 167건

실시간/주기적으로 호출 가능한 공식 OpenAPI. 인증키 발급 후 `https://openapi.openfiscaldata.go.kr/{서비스코드}` 형태로 호출.

→ **[openapi/INDEX.md](openapi/INDEX.md)**

## 2. KODAS 제공 데이터 카탈로그 — 1,707건

데이터분석서비스(KODAS)에서 분석용으로 제공하는 융복합 데이터셋. 직접 호출 API는 없고 KODAS 신청 후 센터 방문 또는 분석환경에서 활용.

→ **[kodas/INDEX.md](kodas/INDEX.md)**

## 원본·중간 산출물

| 위치 | 내용 |
|---|---|
| `data/all_apis.json` | Open API 카탈로그 메타 (167건) |
| `data/api_specs.json` | Open API 명세 정제 (요청/응답 필드 포함) |
| `data/api_specs.csv` | 위 항목의 표 형식 |
| `data/api_specs_raw.json` | Open API 명세 원본 응답 백업 |
| `data/kodas_catalog.json` | KODAS 카탈로그 정제 (1,707건) |
| `data/kodas_catalog.csv` | KODAS 카탈로그 CSV |
| `data/kodas_catalog_raw.json` | KODAS 원본 응답 |
| `raw/list_pages/` | Open API 목록 페이지 원본 (페이지별 JSON) |
| `raw/detail_probe/` | Open API 상세 페이지 네트워크 캡처 |
| `raw/kodas_probe/` | KODAS 페이지 네트워크 캡처 |
| `scripts/` | 수집·문서 생성 스크립트 |

## 재생성

```bash
python scripts/fetch_specs.py    # Open API 명세 167건
python scripts/fetch_kodas.py    # KODAS 카탈로그 1,707건
python scripts/build_docs.py     # 위 결과 → docs/ 마크다운
```

## 발견한 내부 엔드포인트

| 기능 | 엔드포인트 | 페이로드 |
|---|---|---|
| Open API 목록 | `POST /op/ko/ds/selectOpenApiList.do` | form: `pageIndex, page, rowPerPage` |
| 서비스 상세메타 | `POST /op/ko/sd/dtsStats/selectSrvDtlInfoList.do` | json: `{opKoSdDtsStatsDVO:{odtId}}` |
| 명세+응답구조 | `POST /op/ko/sd/dtsStatsAcol/selectAcolViewList.do` | json: `{odtId, rlsSvTyCd:'A', odtSvSeq}` |
| KODAS 카탈로그 | `POST /op/ko/sb/selectCatalogList.do` | json: `{pageIndex, pageSize, totalCnt}` |
''')

def main():
    build_openapi_docs()
    build_kodas_docs()
    build_root_readme()
    # listing
    print('\n생성된 파일:')
    for r, _, fs in os.walk(DOCS):
        for n in sorted(fs):
            p = os.path.join(r, n)
            print(f'  {os.path.relpath(p, ROOT)}  ({os.path.getsize(p):,} bytes)')

if __name__ == '__main__':
    main()
