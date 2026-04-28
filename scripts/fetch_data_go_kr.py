"""data.go.kr 환경/교통 outcome fetch.

전제: data.go.kr에서 다음 4개 API "활용신청" 완료 + 활성화(1~2h):
  - 한국환경공단_에어코리아_대기오염정보 (B552584/ArpltnInforInqireSvc)
  - 한국환경공단_에어코리아_대기질_통계 (B552584/ArpltnStatsSvc) 또는 측정소별 연평균
  - 환경부_(국립환경과학원) 환경영향평가 온실가스정보
  - 도로교통공단_사망자수기준 교통사고
  - 국토교통부_자동차 등록 통계

각 API의 정확한 endpoint URL은 신청 후 페이지에서 확인 필요.
이 스크립트는 신청 끝난 API의 endpoint를 채워서 호출 → 분야 outcome 적재.
"""
import os, sys, io, urllib.request, urllib.parse, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _env import load_env
load_env()
import duckdb, pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, 'data', 'external', 'data_go_kr')
os.makedirs(RAW, exist_ok=True)
DB = os.path.join(ROOT, 'data', 'warehouse.duckdb')
KEY_ENC = os.environ['DATA_GO_KR_KEY_ENC']
H = {'User-Agent':'Mozilla/5.0'}

def call_api(url, retries=3, sleep=1.0):
    for i in range(retries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=30) as r:
                return r.read().decode('utf-8')
        except urllib.error.HTTPError as e:
            if e.code in (403, 500):
                if i == retries - 1: return f'HTTP_{e.code}'
                time.sleep(sleep * (i+1))
            else:
                return f'HTTP_{e.code}: {e.reason}'
        except Exception as e:
            if i == retries - 1: return f'ERR: {e}'
            time.sleep(sleep)
    return None

# ============================================================
# (1) 에어코리아 측정소별 연도별 평균 — 시계열 outcome
# ============================================================
def fetch_airkorea_annual(sido='서울', station='종로구', n_years=15):
    """측정소별 연도별 평균 PM2.5/PM10/O3/NO2/SO2/CO."""
    sta_q = urllib.parse.quote(station)
    url = ('http://apis.data.go.kr/B552584/ArpltnStatsSvc/getMsrstnAcctoRMmrg?'
           f'serviceKey={KEY_ENC}&returnType=json&numOfRows={n_years}&pageNo=1'
           f'&stationName={sta_q}&searchCondition=YEAR')
    return call_api(url)

# ============================================================
# (2) 환경영향평가 온실가스 — 사업 단위가 아니라 거시 통계 후보 확인
# ============================================================
def fetch_ghg_eia(year=2023, n=100):
    url = ('http://apis.data.go.kr/1480523/ScalAssesGhgsInfoInqireSvc/getScalAssesGhgsInfoInqire?'
           f'serviceKey={KEY_ENC}&pageNo=1&numOfRows={n}&type=json'
           f'&searchYear={year}')
    return call_api(url)

# ============================================================
# (3) 도로교통공단 교통사고 (시도별 사망자수 등)
# ============================================================
def fetch_traffic_accident(year=2023, sido='11', gugun='', n=100):
    url = ('http://apis.data.go.kr/B552061/AccidentDeath/getRestAccidentDeath?'
           f'serviceKey={KEY_ENC}&searchYearCd={year}&siDo={sido}&guGun={gugun}'
           f'&type=json&numOfRows={n}&pageNo=1')
    return call_api(url)

# ============================================================
# (4) 국토부 자동차 등록현황 (월/연 단위)
# ============================================================
def fetch_vehicle_reg(year_month='202301'):
    """국토부 자동차 등록 통계 — endpoint URL은 신청 후 확인."""
    # 임시 placeholder
    url = ('http://apis.data.go.kr/1611000/CarRegistrationService/getCarRegistration?'
           f'serviceKey={KEY_ENC}&pageNo=1&numOfRows=100&type=json'
           f'&searchYearMonth={year_month}')
    return call_api(url)

# ============================================================
# 실행: 모든 API 작동 확인
# ============================================================
if __name__ == '__main__':
    print('=== 활성화 점검 ===')

    print('\n1. 에어코리아 측정소별 연도별 (종로구):')
    raw = fetch_airkorea_annual('서울','종로구', 15)
    if 'HTTP_' in str(raw):
        print(f'  {raw} (활성화 대기)')
    else:
        try:
            d = json.loads(raw)
            items = d.get('response',{}).get('body',{}).get('items',[])
            print(f'  OK rows={len(items)}, sample={items[0] if items else "X"}')
            with open(f'{RAW}/airkorea_jongno.json','w',encoding='utf-8') as f:
                json.dump(d, f, ensure_ascii=False)
        except Exception as e:
            print(f'  parse err: {e}, raw[:300]={str(raw)[:300]}')

    print('\n2. 환경영향평가 온실가스 (2023):')
    raw = fetch_ghg_eia(2023, 50)
    if 'HTTP_' in str(raw):
        print(f'  {raw}')
    else:
        try:
            d = json.loads(raw)
            print(f'  raw[:400]={str(raw)[:400]}')
        except Exception as e:
            print(f'  err: {e}, raw[:300]={str(raw)[:300]}')

    print('\n3. 교통사고 (서울 2023):')
    raw = fetch_traffic_accident(2023, '11', '', 30)
    if 'HTTP_' in str(raw):
        print(f'  {raw}')
    else:
        print(f'  raw[:400]={str(raw)[:400]}')

    print('\n4. 자동차 등록 (placeholder):')
    raw = fetch_vehicle_reg('202301')
    if 'HTTP_' in str(raw):
        print(f'  {raw}')
    else:
        print(f'  raw[:300]={str(raw)[:300]}')

    print('\n=== 완료 ===')
    print('각 API 활성화 시 raw 응답에서 ITEM/PERIOD 구조 파악 → 분야 outcome 매핑 → indicator_panel 적재')
