"""유명 사업 키워드 × ACTV_NM 매칭 + 12월 비중·집행률 계산.

멘토링 피드백 대비 (2026-05-20): 평가자의 *"○○사업은 어땠나요?"* 류 개별 사업 질문에
즉답할 lookup table 생성. 결과는 paper/재정데이터 분석 ppt/_mentoring_lookup_raw.json.

데이터 단위: ACTV_CD × FSCL_YY 패널 (2015–2025).
"""
import duckdb
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

KEYWORDS = {
    'R&D · BK21': ['BK21', '두뇌한국'],
    'R&D · 기초연구': ['기초연구사업', '개인기초연구', '집단연구'],
    'R&D · 출연연 (KIST·ETRI·KAIST 등)': ['과학기술원', '전자통신', '과학기술연구원',
                                          '기계연구', '화학연구', '항공우주', '한국에너지',
                                          '원자력연구', '식품연구'],
    'R&D · 발사체': ['발사체', '누리호'],
    'SOC · 도로': ['도로건설', '국도건설', '고속도로'],
    'SOC · 철도': ['철도건설', '광역철도'],
    'SOC · 항만·공항': ['항만건설', '공항건설'],
    '복지 · 기초연금': ['기초연금'],
    '복지 · 기초생활보장 (분해)': ['생계급여', '주거급여', '교육급여', '의료급여', '자활'],
    '복지 · 아동수당': ['아동수당'],
    '복지 · 노인일자리': ['노인일자리'],
    '농수산 · 직불제': ['공익형직불', '공익직불', '직불금', '농업소득보전', '경영안정자금'],
    '농수산 · 수산': ['수산직불', '어업', '수산자원'],
    '농수산 · 농업기반': ['농업기반', '저수지', '배수장'],
    '교육 · 유아/누리': ['누리과정', '유아교육', '영유아', '어린이집'],
    '교육 · 고교무상': ['고교무상', '고등학교무상'],
    '교육 · 대학재정지원': ['대학혁신', '대학재정지원', '대학기본역량'],
    '교육 · 학자금/장학': ['국가장학금', '학자금', '등록금'],
    '환경 · 하천': ['4대강', '하천관리', '하천정비'],
    '환경 · 신재생/원전': ['신재생에너지', '원자력', '에너지전환'],
    '문화·체육': ['공연예술', '문화예술', '체육진흥'],
    '국방 · 방위력개선': ['방위력개선', '전력지원체계', '국방연구개발'],
    '특수 · 코로나/소상공인': ['코로나', '감염병', '소상공인'],
}


def archetype_hint(dec_share, qtr_share):
    if dec_share is None:
        return '데이터 부족'
    if dec_share > 0.25:
        return 'C1 자산취득형 패턴'
    if qtr_share is not None and qtr_share > 0.50 and dec_share < 0.25:
        return 'C2 출연금형 패턴'
    if dec_share < 0.12:
        return 'C0 인건비형 / C3 정상사업 패턴'
    return '혼합 패턴'


def run_match(con, keywords):
    # ACTV_NM (활동) + PGM_NM (프로그램) 동시 검색 — 활동 단위 누락 회피.
    # OFFC_NM (부처) 제외 — 너무 광범위 매칭 회피.
    cond = ' OR '.join([
        f"(ACTV_NM ILIKE '%{k}%' OR PGM_NM ILIKE '%{k}%')" for k in keywords
    ])
    q = f'''
    WITH act_year AS (
      SELECT FSCL_YY, ACTV_CD, ACTV_NM, OFFC_NM, FLD_NM,
             SUM(EP_AMT) AS annual_exec,
             MAX(ANEXP_BDG_CAMT) AS budget,
             SUM(CASE WHEN EXE_M=12 THEN EP_AMT ELSE 0 END) AS dec_exec,
             SUM(CASE WHEN EXE_M IN (3,6,9,12) THEN EP_AMT ELSE 0 END) AS qtr_exec
      FROM monthly_exec
      WHERE ({cond}) AND FSCL_YY BETWEEN 2015 AND 2025
      GROUP BY 1,2,3,4,5
    )
    SELECT ACTV_CD,
           any_value(ACTV_NM) AS ACTV_NM,
           any_value(OFFC_NM) AS OFFC_NM,
           any_value(FLD_NM) AS FLD_NM,
           AVG(CASE WHEN annual_exec>0 THEN dec_exec*1.0/annual_exec END) AS dec_share,
           AVG(CASE WHEN annual_exec>0 THEN qtr_exec*1.0/annual_exec END) AS qtr_share,
           AVG(CASE WHEN budget>0 THEN annual_exec*1.0/budget END) AS exec_rate,
           SUM(annual_exec)/1e8 AS total_exec_eok,
           COUNT(DISTINCT FSCL_YY) AS years
    FROM act_year
    GROUP BY ACTV_CD
    ORDER BY total_exec_eok DESC
    LIMIT 10
    '''
    return con.execute(q).fetchdf()


def main():
    con = duckdb.connect('data/warehouse.duckdb', read_only=True)
    results = {}
    summary = []
    for label, kws in KEYWORDS.items():
        try:
            df = run_match(con, kws)
            if len(df):
                results[label] = df.to_dict('records')
                top = df.iloc[0]
                ds = float(top['dec_share']) if top['dec_share'] is not None else None
                qs = float(top['qtr_share']) if top['qtr_share'] is not None else None
                er = float(top['exec_rate']) if top['exec_rate'] is not None else None
                summary.append({
                    'label': label,
                    'n_matched': len(df),
                    'top_actv': top['ACTV_NM'],
                    'offc': top['OFFC_NM'],
                    'fld': top['FLD_NM'],
                    'total_eok': float(top['total_exec_eok']),
                    'dec_share': ds,
                    'qtr_share': qs,
                    'exec_rate': er,
                    'archetype_hint': archetype_hint(ds, qs),
                })
            else:
                results[label] = []
                summary.append({'label': label, 'n_matched': 0})
        except Exception as e:
            results[label] = {'error': str(e)}
            summary.append({'label': label, 'error': str(e)})

    out_path = Path('paper/재정데이터 분석 ppt/_mentoring_lookup_raw.json')
    out_path.parent.mkdir(exist_ok=True, parents=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump({'summary': summary, 'detail': results},
                  f, ensure_ascii=False, indent=2, default=str)

    print(f'== Lookup Summary ({len(summary)} categories) ==')
    for s in summary:
        if 'error' in s:
            print(f"  [ERR] {s['label']}: {s['error'][:60]}")
        elif s.get('n_matched', 0) == 0:
            print(f"  [---] {s['label']}: NO MATCH")
        else:
            ds = f"{s['dec_share']*100:.1f}%" if s['dec_share'] else 'N/A'
            er = f"{s['exec_rate']*100:.1f}%" if s['exec_rate'] else 'N/A'
            print(f"  [{s['n_matched']:>2}] {s['label']:<24} | top={s['top_actv'][:30]:<30} | "
                  f"12월={ds:>6} | 집행률={er:>6} | {s['archetype_hint']}")
    print(f'\n저장: {out_path}')


if __name__ == '__main__':
    main()
