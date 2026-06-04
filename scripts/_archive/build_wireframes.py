"""40장 SVG 와이어프레임 일괄 생성 (스토리보드 v2 기반, 2026-05-21).

출력: paper/재정데이터 분석 ppt/wireframes/slide-NN.svg
viewBox: 1920×1080 (16:9)
"""
from pathlib import Path
from html import escape

OUT_DIR = Path('paper/재정데이터 분석 ppt/wireframes')
OUT_DIR.mkdir(exist_ok=True, parents=True)

# 디자인 시스템
NAVY = '#0a0e27'
WHITE = '#FFFFFF'
TEXT = '#1a1a1a'
TEXT_INV = '#FFFFFF'
SUB = '#666666'
SUB_INV = '#b8c0d8'
ACCENT = '#C0392B'
ORANGE = '#E67E22'
GRAY = '#888888'
PLACE_BG = '#f8f8f8'
PLACE_BORDER = '#cccccc'
BOX_BG = '#fafafa'
BOX_BORDER = '#dddddd'
GHOST = '#f4f4f4'


def header(title, subtitle='', dark=False, x=80, y=110):
    c = TEXT_INV if dark else TEXT
    sub_c = SUB_INV if dark else SUB
    out = f'<text x="{x}" y="{y}" font-size="44" font-weight="700" fill="{c}">{escape(title)}</text>'
    if subtitle:
        out += f'\n<text x="{x}" y="{y+44}" font-size="22" fill="{sub_c}">{escape(subtitle)}</text>'
    return out


def micro_label(text, x, y, dark=False, fs=14):
    c = SUB_INV if dark else SUB
    return f'<text x="{x}" y="{y}" font-size="{fs}" fill="{c}" font-family="monospace">{escape(text)}</text>'


def chart_box(x, y, w, h, label, dark=False):
    bg = '#1a2040' if dark else PLACE_BG
    border = '#2d3a5a' if dark else PLACE_BORDER
    text_c = '#7f8aa8' if dark else '#999'
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{bg}" '
            f'stroke="{border}" stroke-width="1.5" stroke-dasharray="10,5" rx="8"/>\n'
            f'<text x="{x+w/2}" y="{y+h/2-10}" text-anchor="middle" '
            f'font-size="18" fill="{text_c}" font-style="italic">[ chart ]</text>\n'
            f'<text x="{x+w/2}" y="{y+h/2+18}" text-anchor="middle" '
            f'font-size="14" fill="{text_c}" font-family="monospace">{escape(label)}</text>')


def kpi_box(x, y, w, h, lines, dark=False):
    bg = '#0f1733' if dark else BOX_BG
    border = '#2d3a5a' if dark else BOX_BORDER
    text_c = TEXT_INV if dark else TEXT
    accent_c = ACCENT
    out = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{bg}" '
           f'stroke="{border}" stroke-width="1" rx="8"/>')
    # left accent line
    out += f'\n<rect x="{x}" y="{y}" width="3" height="{h}" fill="{accent_c}"/>'
    ly = y + 40
    for line in lines:
        if line.startswith('@'):  # heading
            txt = line[1:].strip()
            out += (f'\n<text x="{x+24}" y="{ly}" font-size="14" '
                    f'fill="{text_c}" font-weight="600" '
                    f'letter-spacing="0.5">{escape(txt)}</text>')
            ly += 28
        elif line.startswith('!'):  # accent
            txt = line[1:].strip()
            out += (f'\n<text x="{x+24}" y="{ly}" font-size="22" '
                    f'fill="{accent_c}" font-weight="700">{escape(txt)}</text>')
            ly += 34
        elif line.startswith('-'):  # divider
            out += (f'\n<line x1="{x+24}" y1="{ly-8}" x2="{x+w-24}" '
                    f'y2="{ly-8}" stroke="{border}" stroke-width="1"/>')
            ly += 8
        else:
            out += (f'\n<text x="{x+24}" y="{ly}" font-size="16" '
                    f'fill="{text_c}">{escape(line)}</text>')
            ly += 26
    return out


def key_line(text, y=970, x=960, dark=False, fs=30):
    c = TEXT_INV if dark else TEXT
    return (f'<text x="{x}" y="{y}" text-anchor="middle" font-size="{fs}" '
            f'font-weight="700" fill="{c}">{escape(text)}</text>')


def trigger(text, y=1040, dark=False):
    c = SUB_INV if dark else SUB
    return (f'<text x="1840" y="{y}" text-anchor="end" font-size="18" '
            f'fill="{c}" font-style="italic">{escape(text)} ↘</text>')


def big_anchor(text, x=960, y=540, dark=False, fs=180):
    c = TEXT_INV if dark else TEXT
    return (f'<text x="{x}" y="{y}" text-anchor="middle" '
            f'font-size="{fs}" font-weight="800" fill="{c}" '
            f'letter-spacing="-2">{escape(text)}</text>')


def page_num(n, dark=False):
    c = SUB_INV if dark else SUB
    return (f'<text x="80" y="1050" font-size="14" '
            f'font-family="monospace" fill="{c}">{n:02d} / 40</text>')


def svg_doc(content, dark=False):
    bg = NAVY if dark else WHITE
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'viewBox="0 0 1920 1080" '
            f'font-family="Pretendard, -apple-system, sans-serif">\n'
            f'<rect width="1920" height="1080" fill="{bg}"/>\n'
            f'{content}\n</svg>')


# ──────────────────────────────────────────────────────────────────────
# 40장 슬라이드 데이터 + renderer
# ──────────────────────────────────────────────────────────────────────

def slide_01():  # 타이틀
    body = f'''
{big_anchor("연말 보도블록의 비밀", x=960, y=500, dark=True, fs=96)}
<text x="960" y="610" text-anchor="middle" font-size="34" fill="{SUB_INV}">데이터로 본 재정 집행의 굿하트 게임</text>
<text x="960" y="690" text-anchor="middle" font-size="22" fill="{SUB_INV}" font-style="italic">3개의 데이터 렌즈로 해부한 11년 치 국가 가계부</text>
<text x="960" y="970" text-anchor="middle" font-size="16" fill="{SUB_INV}" font-family="monospace">Pied Piper · 한국재정정보원 2026 미니프로젝트</text>
{page_num(1, dark=True)}
'''
    return svg_doc(body, dark=True)


def slide_02():  # 3·6·9·12 + 인용 stack
    body = f'''
{big_anchor("3 · 6 · 9 · 12", x=960, y=380, dark=True, fs=200)}
<text x="960" y="500" text-anchor="middle" font-size="26" fill="{SUB_INV}" font-style="italic">결재의 흐름이 분기말마다 솟구치고, 12월에 정점을 찍습니다.</text>

<!-- 인용 stack -->
<g transform="translate(360, 600)">
  <rect x="0" y="0" width="1200" height="70" fill="#0f1733" stroke="#2d3a5a" rx="4"/>
  <rect x="0" y="0" width="3" height="70" fill="{ACCENT}"/>
  <text x="24" y="32" font-size="18" fill="{TEXT_INV}">"멀쩡한 길, 또 뜯는다? — 보도블록 공사."</text>
  <text x="24" y="56" font-size="13" fill="{SUB_INV}" font-family="monospace">전국뉴스 2025.06</text>

  <rect x="0" y="86" width="1200" height="70" fill="#0f1733" stroke="#2d3a5a" rx="4"/>
  <rect x="0" y="86" width="3" height="70" fill="{ACCENT}"/>
  <text x="24" y="118" font-size="18" fill="{TEXT_INV}">"사실상 성역 된 출연금… 제재 규정 마련 시급."</text>
  <text x="24" y="142" font-size="13" fill="{SUB_INV}" font-family="monospace">서울경제 2025.03</text>

  <rect x="0" y="172" width="1200" height="70" fill="#0f1733" stroke="#2d3a5a" rx="4"/>
  <rect x="0" y="172" width="3" height="70" fill="{ACCENT}"/>
  <text x="24" y="204" font-size="18" fill="{TEXT_INV}">"순위 경쟁에 매몰된 공공기관… 뭘 위한 평가인가."</text>
  <text x="24" y="228" font-size="13" fill="{SUB_INV}" font-family="monospace">머니투데이 2025.08</text>
</g>

{key_line("오래 지적되어 왔다. 통합 패널 위에서 인과·군집·동학·매개를 동시에 본 정량 진단은 처음이다.", y=900, dark=True, fs=22)}
<text x="1840" y="1040" text-anchor="end" font-size="18" fill="{SUB_INV}" font-style="italic">모든 부처가 0원으로 수렴하는 시간.</text>
{page_num(2, dark=True)}
'''
    return svg_doc(body, dark=True)


def slide_03():  # 집행률 100% + 페널티 stack
    body = f'''
{header("집행률 100%", "한국 재정 시스템에서 가장 무거운 지표.")}
{big_anchor("집행률 100%", x=960, y=310, fs=130)}

<!-- 페널티 stack -->
<g transform="translate(160, 400)">
  <rect x="0" y="0" width="1600" height="100" fill="{GHOST}" stroke="{BOX_BORDER}" rx="6"/>
  <rect x="0" y="0" width="3" height="100" fill="{ACCENT}"/>
  <text x="24" y="38" font-size="20" font-weight="600" fill="{TEXT}">▸ 다음 해 예산 10–50% 감축</text>
  <text x="24" y="68" font-size="15" fill="{SUB}" font-family="monospace">— 기재부 「2023년 예산안 편성 세부지침」</text>
  <text x="24" y="90" font-size="14" fill="{SUB}">반복 미달 사업은 *예산 자체가 깎인다*.</text>

  <rect x="0" y="120" width="1600" height="160" fill="{GHOST}" stroke="{BOX_BORDER}" rx="6"/>
  <rect x="0" y="120" width="3" height="160" fill="{ACCENT}"/>
  <text x="24" y="158" font-size="20" font-weight="600" fill="{TEXT}">▸ 공공기관 경영평가 — 사업비집행률이 평가지표명 그 자체</text>
  <text x="24" y="188" font-size="17" fill="{TEXT}" font-family="monospace">사업비집행률 = 사업비집행액 / 사업비 예산현액</text>
  <text x="24" y="218" font-size="15" fill="{SUB}">위치: 재무성과관리 15점 + 주요사업 40점에 반복 등장 (100점 만점)</text>
  <text x="24" y="248" font-size="15" fill="{SUB}" font-family="monospace">— 2026년 공공기관 경영평가편람</text>

  <rect x="0" y="300" width="1600" height="100" fill="{GHOST}" stroke="{BOX_BORDER}" rx="6"/>
  <rect x="0" y="300" width="3" height="100" fill="{ACCENT}"/>
  <text x="24" y="338" font-size="20" font-weight="600" fill="{TEXT}">▸ 경영실적 부진 기관 → 기관장 해임 건의</text>
  <text x="24" y="368" font-size="15" fill="{SUB}">공공기관운영위원회 심의·의결, 재임 6개월 이상</text>
  <text x="24" y="388" font-size="15" fill="{SUB}" font-family="monospace">— 같은 편람 §1편 제2절</text>
</g>

{key_line("평가는 채워졌는지만 묻는다. 어디에 어떻게 쓰였는지, 사업이 목표를 달성했는지는 묻지 않는다.", y=960, fs=24)}
{page_num(3)}
'''
    return svg_doc(body)


def slide_04():  # 좌/우 칼럼 P-A
    body = f'''
{header("P-A 정보 비대칭", "본 분석의 학술 출발점.")}

<!-- 좌측 칼럼 -->
<g transform="translate(160, 280)">
  <text x="0" y="0" font-size="32" font-weight="700" fill="{TEXT}">기록되는 것</text>
  <line x1="0" y1="20" x2="400" y2="20" stroke="{ACCENT}" stroke-width="3"/>
  <text x="0" y="80" font-size="22" fill="{TEXT}">• 결재 시점</text>
  <text x="0" y="130" font-size="22" fill="{TEXT}">• 집행 금액</text>
  <text x="0" y="180" font-size="22" fill="{TEXT}">• 집행률 %</text>
  <text x="0" y="260" font-size="18" fill="{ACCENT}" font-weight="600">→ 평가에 직접 들어간다</text>
</g>

<!-- 우측 칼럼 -->
<g transform="translate(1100, 280)">
  <text x="0" y="0" font-size="32" font-weight="700" fill="{SUB}">기록되지 않는 것</text>
  <line x1="0" y1="20" x2="500" y2="20" stroke="{SUB}" stroke-width="3"/>
  <text x="0" y="80" font-size="22" fill="{SUB}">• 사업의 품질</text>
  <text x="0" y="130" font-size="22" fill="{SUB}">• 정책 목표 달성도</text>
  <text x="0" y="180" font-size="22" fill="{SUB}">• 사회적 outcome</text>
  <text x="0" y="260" font-size="18" fill="{SUB}" font-weight="600">→ 평가에 남지 않는다</text>
</g>

<rect x="160" y="640" width="1600" height="130" fill="{GHOST}" stroke="{BOX_BORDER}" rx="8"/>
<text x="960" y="690" text-anchor="middle" font-size="22" font-weight="600" fill="{TEXT}">한 쪽만 정보를 가지는 구조 — 본인-대리인 (Principal-Agent) 정보 비대칭</text>
<text x="960" y="725" text-anchor="middle" font-size="17" fill="{SUB}" font-style="italic">정보경제학이 수학적으로 일반화한 모형</text>
<text x="960" y="755" text-anchor="middle" font-size="16" fill="{SUB}">국민-정부, 기재부-부처, 모기관-산하기관 — 모두 같은 P-A 구조</text>

{key_line("측정되는 차원만 진화한다.", y=900, fs=30)}
{page_num(4)}
'''
    return svg_doc(body)


def slide_05():  # 거시적 풍경
    body = f'''
{header("거시적 풍경", "— 사업 규모 무관, 12월에 같은 봉우리.")}

<!-- 메인 차트 -->
{chart_box(80, 240, 1100, 580, "fig_2_2_monthly_exec_total.png (활동 정규화 Q1–Q4 line)")}

<!-- 보조 sparkline (우상) -->
{chart_box(1240, 240, 600, 160, "fig_5_aux_raw_sparkline.png (raw × 1.52)")}

<!-- KPI -->
{kpi_box(1240, 430, 600, 390, [
    '@정규화 (활동 단위)',
    '12월        37.2%',
    '11월        17.7%',
    '-',
    '!× 2.11   ← 12월 점프',
    '@raw (참조)',
    '12월/11월   × 1.52',
    '-',
    '@차이 = 작은 사업의 가중 효과',
])}

<g transform="translate(80, 870)">
  <text x="0" y="0" font-size="20" fill="{TEXT}">raw 합계로 보면 12월은 분기말 봉우리 중 하나 — × 1.5.</text>
  <text x="0" y="32" font-size="20" fill="{TEXT}">각 활동을 동일 무게로 평균 내면 × 2.1.</text>
  <text x="0" y="64" font-size="20" fill="{ACCENT}" font-weight="600">작은 사업의 가중 효과가 raw view에선 가려진다.</text>
</g>

{trigger("그리고 — 분포는 어디에 쏠리는가?")}
{page_num(5)}
'''
    return svg_doc(body)


def slide_06():  # 분포의 두 갈래
    body = f'''
{header("분포의 두 갈래", "— 닿은 사업과 닿지 못한 사업의 시점이 갈린다.")}

{chart_box(80, 240, 1100, 580, "fig_6_exec_bucket_dec.png (집행률 7 bucket × 12월 비중)")}

{kpi_box(1240, 240, 600, 580, [
    '@집행률 bucket × 12월 비중',
    '<95% 사업               19.1%',
    '95–100% 사업          10.3%',
    '-',
    '!99–100%               8.3%',
    '   ← 전체 사업의 48.4%',
    '   ← 균등 가정 8.3%과 *정확 일치*',
    '@단조 감소 ✓',
    '24.3% → 20.9% → 19.0%',
    '→ 15.8% → 14.5% → 8.3%',
])}

{key_line("12월에 몰린 것은, 천장에 닿지 못한 사업들이다.", y=900, fs=28)}
{trigger("그렇다면 — 그 집단은 누구인가?")}
{page_num(6)}
'''
    return svg_doc(body)


def slide_07():  # 데이터 스펙 + 선행 연구
    body = f'''
{header("11년 치 영수증, 21만 개의 셀", "— 데이터 스펙 + 선행 연구 위치설정.")}

<!-- 좌상 데이터 스펙 -->
<g transform="translate(80, 240)">
  <rect x="0" y="0" width="900" height="130" fill="{GHOST}" stroke="{BOX_BORDER}" rx="8"/>
  <text x="24" y="44" font-size="24" font-weight="700" fill="{TEXT}">132개월 × 1,557 세부사업 × 14분야</text>
  <text x="24" y="78" font-size="16" fill="{SUB}" font-family="monospace">분류 위계: 분야 16 → 부문 86 → 프로그램 85 → 세부사업 1,707 (11년 누적)</text>
  <text x="24" y="108" font-size="15" fill="{SUB}">열린재정 / KODAS / dBrain+ · 외부 결과지표: KOSIS · ECOS · 공공데이터포털 · GIR</text>
</g>

<!-- 데이터 카탈로그 박스 -->
<g transform="translate(80, 400)">
  <rect x="0" y="0" width="900" height="280" fill="{BOX_BG}" stroke="{BOX_BORDER}" rx="8"/>
  <text x="24" y="40" font-size="18" font-weight="600" fill="{TEXT}">데이터 카탈로그</text>
  <text x="24" y="78" font-size="15" fill="{TEXT}">▸ 재정 집행 메인: dBrain+ / 열린재정 (41만 셀)</text>
  <text x="24" y="115" font-size="15" fill="{TEXT}">▸ 외부 outcome: KOSIS · ECOS · 공공데이터포털 · GIR</text>
  <text x="24" y="152" font-size="15" fill="{TEXT}">▸ 아카이브: FIS 22-03 · NABO · 「국가재정법」 · L-M 2017</text>
  <text x="24" y="189" font-size="15" fill="{TEXT}">▸ 도구: DuckDB · Python · Typst</text>
  <text x="24" y="240" font-size="13" fill="{SUB}" font-style="italic">풀 카탈로그: 부록 App-DATA</text>
</g>

<!-- 우측 선행 연구 stack -->
<g transform="translate(1020, 240)">
  <text x="0" y="0" font-size="18" font-weight="600" fill="{TEXT}">선행 연구 stack (위치설정)</text>

  <rect x="0" y="20" width="820" height="120" fill="{BOX_BG}" stroke="{BOX_BORDER}" rx="6"/>
  <rect x="0" y="20" width="3" height="120" fill="{ACCENT}"/>
  <text x="20" y="50" font-size="16" font-weight="600" fill="{TEXT}">김명규·김민경·지은초 (2022) · 한국재정정보원 22-03</text>
  <text x="20" y="80" font-size="14" fill="{SUB}">「재정지출 효율화를 위한 불용유형 분석 및 집행관리방안」</text>
  <text x="20" y="108" font-size="13" fill="{SUB}" font-style="italic">주요 불용사업 2,389개 · 4 집행패턴 · 변동성–불용률 −0.31</text>

  <rect x="0" y="160" width="820" height="120" fill="{BOX_BG}" stroke="{BOX_BORDER}" rx="6"/>
  <rect x="0" y="160" width="3" height="120" fill="{ACCENT}"/>
  <text x="20" y="190" font-size="16" font-weight="600" fill="{TEXT}">장희란 (2022) · 국회예산정책처</text>
  <text x="20" y="220" font-size="14" fill="{SUB}">「출연금 현황과 개선과제」</text>
  <text x="20" y="248" font-size="13" fill="{SUB}" font-style="italic">정산체계 부재 진단 · 정량 분석 없음</text>

  <rect x="0" y="300" width="820" height="120" fill="{BOX_BG}" stroke="{BOX_BORDER}" rx="6"/>
  <rect x="0" y="300" width="3" height="120" fill="{ACCENT}"/>
  <text x="20" y="330" font-size="16" font-weight="600" fill="{TEXT}">Liebman &amp; Mahoney (2017) · AER</text>
  <text x="20" y="360" font-size="14" fill="{SUB}">미국 연방조달 9→10월 RDD: 지출 4.9배, 품질 ↓</text>
  <text x="20" y="388" font-size="13" fill="{SUB}" font-style="italic">본 분석 RDD 방법론의 직접 선행</text>
</g>

{key_line("본 분석은 이 위에서 RDD + TDA + Wavelet + 매개를 결합한 통합 정량 진단으로 확장한다.", y=940, fs=20)}
{page_num(7)}
'''
    return svg_doc(body)


def slide_08():  # 부처를 떼어내본다
    body = f'''
{header("부처를 떼어내본다", "— 51개 부처, 모두 12월 봉우리.")}
{chart_box(80, 240, 1100, 580, "fig_slide8_ministry_dec_ranking.png (51 부처 12월 비중)")}

{kpi_box(1240, 240, 600, 580, [
    '@부처 수                 51',
    '발견된 체질 (co-cluster)  5',
    '-',
    '!51 / 51',
    '균등 가정 (8.3%) 초과',
    '@= 100% 부처에 12월 봉우리',
    '@<95% 집단의 부처 분포',
    '고르게 흩어짐',
    '(Slide 6 연결)',
])}

{key_line("부처를 떼어내도 12월 봉우리는 사라지지 않는다 — 다만 다섯 가지 체질로 묶인다.", y=900, fs=24)}
{trigger("그렇다면, 같은 분야 안에서는 균질한가?")}
{page_num(8)}
'''
    return svg_doc(body)


def slide_09():  # 기능을 떼어내본다
    body = f'''
{header("기능을 떼어내본다", "— 14분야, 같은 분야 안에서도 패턴이 갈린다.")}

{chart_box(80, 240, 1240, 580, "fig_2_3_field_size_vs_dec.png (14분야 × 12월 비중 + 사업 규모 색)")}

{kpi_box(1380, 240, 460, 580, [
    '@분야 수                 14',
    '@최대–최소 격차',
    '국방(최고)  17.0%',
    '사회복지   7.8%',
    '!≈ × 2.2',
    '@상위 분야',
    '국방 12월 19.7%',
    '@부록 App-C',
    '분야 내 분산 IQR ~15%p',
])}

{key_line("분야는 균질한 단위가 아니다 — 작은 사업이 많은 분야가 12월에 쏠리고, 분야 안에서도 패턴이 갈린다.", y=900, fs=22)}
{trigger("부처도, 분야도 — 그렇다면 진짜 단위는 무엇인가?")}
{page_num(9)}
'''
    return svg_doc(body)


def slide_10():  # 미궁의 한계 (flash-by, navy)
    body = f'''
<text x="960" y="280" text-anchor="middle" font-size="42" font-weight="700" fill="{TEXT_INV}">부처를 51개로 갈라도 — 5종으로 수렴한다.</text>
<text x="960" y="380" text-anchor="middle" font-size="42" font-weight="700" fill="{TEXT_INV}">분야를 14개로 묶어도 — 분야 안에서 다시 갈린다.</text>

<text x="960" y="460" text-anchor="middle" font-size="18" fill="{SUB_INV}" font-style="italic">(51개 부처 → 5종 체질 · 14분야 내부 분산 30%p)</text>

<line x1="600" y1="540" x2="1320" y2="540" stroke="{ACCENT}" stroke-width="2"/>

<text x="960" y="640" text-anchor="middle" font-size="52" font-weight="800" fill="{TEXT_INV}">행정 분류는 시점 압력의 단위가 아니다.</text>

<text x="960" y="820" text-anchor="middle" font-size="22" fill="{SUB_INV}" font-style="italic">그렇다면, 이미 답이 있었다 — 학계가 30년째 부르고 있는 이름.</text>
{page_num(10, dark=True)}
'''
    return svg_doc(body, dark=True)


def slide_11():  # 세 이론
    body = f'''
{header("세 이론이 이미 예견했다", "— 모두 P-A 구조 위에서.")}

<g transform="translate(160, 280)">
  <rect x="0" y="0" width="1600" height="160" fill="{GHOST}" stroke="{ACCENT}" stroke-width="3" rx="8"/>
  <text x="40" y="50" font-size="28" font-weight="700" fill="{ACCENT}">굿하트 · 캠벨 (1975, 1979)</text>
  <text x="40" y="100" font-size="20" fill="{TEXT}">"지표가 목표가 되면, 그 지표는 더 이상 작동하지 않는다."</text>
  <text x="40" y="138" font-size="14" fill="{SUB}" font-family="monospace">— Goodhart's Law / Campbell's Law (메인 frame)</text>
</g>

<g transform="translate(260, 480)">
  <rect x="0" y="0" width="1400" height="130" fill="{GHOST}" stroke="{BOX_BORDER}" rx="6"/>
  <text x="40" y="46" font-size="20" font-weight="600" fill="{TEXT}">Holmström &amp; Milgrom (1991)</text>
  <text x="40" y="84" font-size="16" fill="{SUB}">"여러 업무 중 측정 가능한 일에만 인센티브를 걸면, 측정되지 않는 일은 방치된다."</text>
  <text x="40" y="112" font-size="12" fill="{SUB}" font-family="monospace">— Multi-tasking 모형</text>
</g>

<g transform="translate(260, 640)">
  <rect x="0" y="0" width="1400" height="130" fill="{GHOST}" stroke="{BOX_BORDER}" rx="6"/>
  <text x="40" y="46" font-size="20" font-weight="600" fill="{TEXT}">Kornai (1980)</text>
  <text x="40" y="84" font-size="16" fill="{SUB}">"산하기관은 모기관이 메워줄 것을 알기에 자체 예산 규율이 약해진다."</text>
  <text x="40" y="112" font-size="12" fill="{SUB}" font-family="monospace">— Soft Budget Constraint</text>
</g>

{key_line("본 분석은 이 구조 위에서 한국 재정 패널의 패턴을 정량 증명한다.", y=900, fs=22)}
{page_num(11)}
'''
    return svg_doc(body)


def slide_12():  # 분석의 전환 — 3 렌즈
    body = f'''
{header("분석의 전환", "— 행정 분류 대신, 사업 형태로.")}

<text x="80" y="240" font-size="20" fill="{TEXT}">부처도 분야도 — 시점 압력의 단위가 아니었다.</text>
<text x="80" y="275" font-size="20" fill="{TEXT}">사업 *형태(archetype)*를 단위로, 세 가지 렌즈를 들이댄다.</text>

<!-- 3 카드 -->
<g transform="translate(80, 340)">
  <!-- 카드 1: 형태 -->
  <rect x="0" y="0" width="560" height="440" fill="{GHOST}" stroke="#3498db" stroke-width="2" rx="10"/>
  <rect x="0" y="0" width="4" height="440" fill="#3498db"/>
  <text x="30" y="60" font-size="32" font-weight="700" fill="#3498db">① 형태</text>
  <text x="30" y="90" font-size="16" fill="{SUB}" font-style="italic">Act 2</text>
  <line x1="30" y1="110" x2="200" y2="110" stroke="#3498db"/>
  <text x="30" y="150" font-size="18" font-weight="600" fill="{TEXT}">TDA · UMAP · HDBSCAN</text>
  <text x="30" y="220" font-size="16" fill="{TEXT}">행정 라벨을 떼고,</text>
  <text x="30" y="250" font-size="16" fill="{TEXT}">닮은 사업끼리</text>
  <text x="30" y="280" font-size="16" fill="{TEXT}">자동으로 묶는다.</text>
  <text x="30" y="380" font-size="16" font-weight="600" fill="#3498db">→ 4가지 사업 체질</text>
  <text x="30" y="405" font-size="16" font-weight="600" fill="#3498db">(archetype) 발견</text>

  <!-- 카드 2: 단절 -->
  <rect x="600" y="0" width="560" height="440" fill="{GHOST}" stroke="#e67e22" stroke-width="2" rx="10"/>
  <rect x="600" y="0" width="4" height="440" fill="#e67e22"/>
  <text x="630" y="60" font-size="32" font-weight="700" fill="#e67e22">② 단절</text>
  <text x="630" y="90" font-size="16" fill="{SUB}" font-style="italic">Act 3</text>
  <line x1="630" y1="110" x2="800" y2="110" stroke="#e67e22"/>
  <text x="630" y="150" font-size="18" font-weight="600" fill="{TEXT}">RDD (회귀불연속)</text>
  <text x="630" y="220" font-size="16" fill="{TEXT}">회계 마감 직전·직후,</text>
  <text x="630" y="250" font-size="16" fill="{TEXT}">같은 사업의 일평균</text>
  <text x="630" y="280" font-size="16" fill="{TEXT}">집행이 얼마나 점프하는가.</text>
  <text x="630" y="380" font-size="16" font-weight="600" fill="#e67e22">→ 12월 1일 점프</text>
  <text x="630" y="405" font-size="16" font-weight="600" fill="#e67e22">정량 측정</text>

  <!-- 카드 3: 주기 -->
  <rect x="1200" y="0" width="560" height="440" fill="{GHOST}" stroke="#27ae60" stroke-width="2" rx="10"/>
  <rect x="1200" y="0" width="4" height="440" fill="#27ae60"/>
  <text x="1230" y="60" font-size="32" font-weight="700" fill="#27ae60">③ 주기</text>
  <text x="1230" y="90" font-size="16" fill="{SUB}" font-style="italic">Act 4</text>
  <line x1="1230" y1="110" x2="1400" y2="110" stroke="#27ae60"/>
  <text x="1230" y="150" font-size="18" font-weight="600" fill="{TEXT}">FFT · Wavelet · NeuralProphet</text>
  <text x="1230" y="220" font-size="16" fill="{TEXT}">연·분기 주기 강도가</text>
  <text x="1230" y="250" font-size="16" fill="{TEXT}">시간이 갈수록</text>
  <text x="1230" y="280" font-size="16" fill="{TEXT}">어떻게 변하는가.</text>
  <text x="1230" y="380" font-size="16" font-weight="600" fill="#27ae60">→ 사이클 진폭의</text>
  <text x="1230" y="405" font-size="16" font-weight="600" fill="#27ae60">시간 강화 발견</text>
</g>

{key_line("세 렌즈가 같은 패턴을 다른 각도로 비춘다.", y=900, fs=28)}
{trigger("먼저, 형태부터.")}
{page_num(12)}
'''
    return svg_doc(body)


def slide_13():  # 렌즈 1 TDA
    body = f'''
{header("렌즈 1 — 위상과 군집", "— 닮은 사업끼리 자동으로 묶는다.")}

<text x="80" y="240" font-size="20" fill="{TEXT}">수만 차원의 월별 집행 패턴을 저차원으로 펴고(UMAP),</text>
<text x="80" y="275" font-size="20" fill="{TEXT}">닮은 점끼리 자동 군집(HDBSCAN). 위상학(TDA)이 군집의 안정성을 검증한다.</text>

<!-- 3단 도구 다이어그램 -->
{chart_box(80, 320, 1100, 380, "다이어그램: 월별 패턴 41만 셀 → UMAP 2D → HDBSCAN 4 군집")}

<!-- 4-layer 정합성 박스 -->
{kpi_box(1240, 320, 600, 380, [
    '@▸ 측정',
    '1,557 세부사업 월별 패턴',
    '@▸ 모델',
    'UMAP + HDBSCAN + TDA',
    '@▸ 추정',
    '4 군집 자동 발견',
    '@▸ 검증',
    'persistence · bootstrap · stability',
    '@▸ 출처',
    'McInnes·Campello·Carlsson',
])}

{key_line("행정 라벨 없이, 데이터가 스스로 묶는다.", y=900, fs=28)}
{trigger("부록 App-TDA 풀 검증")}
{page_num(13)}
'''
    return svg_doc(body)


def slide_14():  # 재정의 별자리
    body = f'''
{header("재정의 별자리", "— 1,557개 세부사업, 자동으로 4개의 군집.")}

{chart_box(80, 240, 1100, 580, "fig: h3_umap_top_small.png (UMAP 4 archetype 산점도)")}

{kpi_box(1240, 240, 600, 580, [
    '@전체 세부사업          1,557',
    '발견 군집                  4',
    '-',
    '@▸ 분석 대상 (C1+C2)',
    '!253 (16.2% · 집행액 15.2%)',
    'Act 3·4 타겟',
    '-',
    '@▸ 비교군 (C0+C3)',
    '!1,304 (83.8% · 집행액 84.8%)',
    'null effect 검증',
])}

<text x="80" y="870" font-size="13" fill="{SUB}" font-family="monospace">※ 각 단위 = 정부 프로그램 예산제도의 *세부사업* (분야 16 → 부문 86 → 프로그램 85 → 세부사업 1,707).</text>

{key_line("누구도 정의하지 않았는데, 네 가지 사업 체질이 데이터에서 드러났다.", y=940, fs=24)}
{page_num(14)}
'''
    return svg_doc(body)


def slide_15():  # 4 archetype 카드
    body = f'''
{header("사업 원형(Archetype)", "— 본 분석이 데이터로 발견한, 네 가지 체질.")}

<!-- 명시 박스 -->
<g transform="translate(80, 240)">
  <rect x="0" y="0" width="1760" height="100" fill="#FFF5F5" stroke="{ACCENT}" rx="6"/>
  <text x="24" y="32" font-size="14" font-weight="600" fill="{ACCENT}">원본 재정 데이터에는 이 분류가 없다.</text>
  <text x="24" y="56" font-size="13" fill="{TEXT}">1,557 세부사업의 월별 집행 패턴을 TDA + UMAP + HDBSCAN으로 *자동 군집*. '4종'이라는 결과조차 사전에 정해두지 않았다.</text>
  <text x="24" y="80" font-size="13" fill="{TEXT}">군집 패턴을 보고 본 분석이 *사후 명명*. FIS 22-03(2022)의 사전 정의 4 패턴과는 *분류 축*과 *발견 절차* 모두 다르다.</text>
</g>

<!-- 4 카드 -->
<g transform="translate(80, 380)">
  <rect x="0" y="0" width="420" height="380" fill="{GHOST}" stroke="{GRAY}" rx="8"/>
  <rect x="0" y="0" width="4" height="380" fill="{GRAY}"/>
  <text x="24" y="42" font-size="22" font-weight="700" fill="{TEXT}">C0 인건비형</text>
  <text x="24" y="70" font-size="14" fill="{GRAY}">▸ 비교군 (n=129)</text>
  <rect x="24" y="100" width="360" height="80" fill="#fff" stroke="{BOX_BORDER}" rx="4"/>
  <text x="204" y="148" text-anchor="middle" font-size="13" fill="{SUB}" font-style="italic">mini bar: 매월 균등</text>
  <text x="24" y="220" font-size="13" font-weight="600" fill="{TEXT}">대표:</text>
  <text x="24" y="245" font-size="12" fill="{SUB}">• 군인인건비</text>
  <text x="24" y="265" font-size="12" fill="{SUB}">• 본부인건비(경찰)</text>
  <text x="24" y="285" font-size="12" fill="{SUB}">• 소속기관인건비(법무부)</text>
  <text x="24" y="340" font-size="14" fill="{GRAY}" font-style="italic">시점 압력 약함</text>

  <rect x="450" y="0" width="420" height="380" fill="{GHOST}" stroke="{ACCENT}" rx="8"/>
  <rect x="450" y="0" width="4" height="380" fill="{ACCENT}"/>
  <text x="474" y="42" font-size="22" font-weight="700" fill="{ACCENT}">C1 자산취득형</text>
  <text x="474" y="70" font-size="14" fill="{ACCENT}">▸ 분석 대상 (n=99)</text>
  <rect x="474" y="100" width="360" height="80" fill="#fff" stroke="{BOX_BORDER}" rx="4"/>
  <text x="654" y="148" text-anchor="middle" font-size="13" fill="{ACCENT}" font-style="italic">mini bar: 12월 절벽</text>
  <text x="474" y="220" font-size="13" font-weight="600" fill="{TEXT}">대표:</text>
  <text x="474" y="245" font-size="12" fill="{SUB}">• 기동화력 양산</text>
  <text x="474" y="265" font-size="12" fill="{SUB}">• 함정 양산</text>
  <text x="474" y="285" font-size="12" fill="{SUB}">• 양곡매입</text>
  <text x="474" y="340" font-size="14" fill="{ACCENT}" font-style="italic">Act 3 RDD 타겟</text>

  <rect x="900" y="0" width="420" height="380" fill="{GHOST}" stroke="{ORANGE}" rx="8"/>
  <rect x="900" y="0" width="4" height="380" fill="{ORANGE}"/>
  <text x="924" y="42" font-size="22" font-weight="700" fill="{ORANGE}">C2 출연금형</text>
  <text x="924" y="70" font-size="14" fill="{ORANGE}">▸ 분석 대상 (n=154)</text>
  <rect x="924" y="100" width="360" height="80" fill="#fff" stroke="{BOX_BORDER}" rx="4"/>
  <text x="1104" y="148" text-anchor="middle" font-size="13" fill="{ORANGE}" font-style="italic">mini bar: 분기 사이클</text>
  <text x="924" y="220" font-size="13" font-weight="600" fill="{TEXT}">대표:</text>
  <text x="924" y="245" font-size="12" fill="{SUB}">• 맞춤형 국가장학금</text>
  <text x="924" y="265" font-size="12" fill="{SUB}">• 일반철도건설</text>
  <text x="924" y="285" font-size="12" fill="{SUB}">• 출연연구기관 지원</text>
  <text x="924" y="340" font-size="14" fill="{ORANGE}" font-style="italic">Act 4 시계열 타겟</text>

  <rect x="1350" y="0" width="420" height="380" fill="{GHOST}" stroke="{GRAY}" rx="8"/>
  <rect x="1350" y="0" width="4" height="380" fill="{GRAY}"/>
  <text x="1374" y="42" font-size="22" font-weight="700" fill="{TEXT}">C3 정상사업</text>
  <text x="1374" y="70" font-size="14" fill="{GRAY}">▸ 비교군 (n=1,175)</text>
  <rect x="1374" y="100" width="360" height="80" fill="#fff" stroke="{BOX_BORDER}" rx="4"/>
  <text x="1554" y="148" text-anchor="middle" font-size="13" fill="{SUB}" font-style="italic">mini bar: 평균 부근</text>
  <text x="1374" y="220" font-size="13" font-weight="600" fill="{TEXT}">대표:</text>
  <text x="1374" y="245" font-size="12" fill="{SUB}">• 보통교부금</text>
  <text x="1374" y="265" font-size="12" fill="{SUB}">• 보통교부세</text>
  <text x="1374" y="285" font-size="12" fill="{SUB}">• 기초연금 지원</text>
  <text x="1374" y="340" font-size="14" fill="{GRAY}" font-style="italic">모집단 (집행액 73.2%)</text>
</g>

{key_line("네 체질, 각각 다른 시점 압력 메커니즘.", y=900, fs=28)}
{trigger("하나씩 들여다본다.")}
{page_num(15)}
'''
    return svg_doc(body)


def slide_16_19_template(slide_n, archetype, label, name, color, msg, fname, group_label):
    body = f'''
{header(archetype, f"— {label}.")}

{chart_box(160, 280, 1600, 480, f"{fname} ({name} 11년 평균 월별)")}

<text x="960" y="850" text-anchor="middle" font-size="20" fill="{color}" font-style="italic">{msg}</text>
<text x="960" y="900" text-anchor="middle" font-size="14" fill="{SUB}" font-family="monospace">{group_label}</text>
{page_num(slide_n)}
'''
    return svg_doc(body)


def slide_16():
    return slide_16_19_template(
        16, "C0 인건비형 (비교군)",
        "매월 균등 — 시점 압력이 새겨질 자리가 없다",
        "노인일자리지원", GRAY,
        "dec=0.0% · 집행률 100% — 비교군 깨끗",
        "fig_slide16_c0_rep.png", "▸ 비교군 / null effect")


def slide_17():
    return slide_16_19_template(
        17, "C3 정상사업 (비교군)",
        "평균 부근 — 시점 압력의 모집단 비교군",
        "우주발사체개발", GRAY,
        "dec=11.4% · 정상 분포 부근",
        "fig_slide17_c3_rep.png", "▸ 비교군 / 모집단")


def slide_18():
    return slide_16_19_template(
        18, "C1 자산취득형 (분석 대상)",
        "12월 절벽 — Act 3 RDD가 정량 측정한다",
        "신공항건설", ACCENT,
        "dec=20.0% · 집행률 38.2% — 불용 위험 + 12월 burst",
        "fig_slide18_c1_rep.png", "▸ 분석 대상 / Act 3 타겟")


def slide_19():
    return slide_16_19_template(
        19, "C2 출연금형 (분석 대상)",
        "분기 사이클 — Act 4 시계열 3각이 시간 동학을 분해한다",
        "고속도로건설", ORANGE,
        "dec=7.0% · 분기말 55.7% — Wavelet 사례",
        "fig_slide19_c2_rep.png", "▸ 분석 대상 / Act 4 타겟")


def slide_20():  # 분석 대상의 정의 (flash-by)
    body = f'''
<text x="960" y="380" text-anchor="middle" font-size="52" font-weight="800" fill="{TEXT}">분석 대상이 명확해졌다 —</text>
<text x="960" y="460" text-anchor="middle" font-size="52" font-weight="800" fill="{ACCENT}">자산취득형(C1)과 출연금형(C2).</text>

<text x="960" y="580" text-anchor="middle" font-size="20" fill="{SUB}">전체 1,557 세부사업 중 253 (16.2%) · 집행액 비중 15.2%</text>
<text x="960" y="620" text-anchor="middle" font-size="18" fill="{SUB}">C0(인건비형) · C3(정상사업)은 시점 압력 약한 비교군 (활동 83.8% / 집행액 84.8%) — null effect 검증</text>

<line x1="600" y1="700" x2="1320" y2="700" stroke="{ACCENT}" stroke-width="2"/>

{key_line("네 체질 중 둘이, 시점 압력의 주역이다.", y=800, fs=32)}
{trigger("먼저, 12월 1일의 절벽.")}
{page_num(20)}
'''
    return svg_doc(body)


def slide_21():  # 렌즈 2 RDD
    body = f'''
{header("렌즈 2 — 단절의 현미경", "— 회귀불연속(RDD).")}

<text x="80" y="240" font-size="20" fill="{TEXT}">외형은 연속인 시간축에, 제도가 절단점을 만든다.</text>
<text x="80" y="275" font-size="20" fill="{TEXT}">11월 30일과 12월 1일 사이, 같은 사업의 일평균 집행이 얼마나 점프하는가.</text>

{chart_box(80, 320, 1100, 460, "fig: h22_rdd_monthly.png (11년 평균 + 12월 cutoff)")}

{kpi_box(1240, 320, 600, 460, [
    '@▸ 측정',
    'cutoff 직전·직후 일평균 점프',
    '@▸ 모델',
    'log(y) = α + β·D_12',
    '       + μ_i + τ_t + ε',
    '@▸ 추정',
    'β → 점프 배율 e^β',
    '@▸ 검증',
    'p값 · 95% CI · placebo · bw',
    '@▸ 출처',
    'Liebman & Mahoney 2017 (AER)',
])}

{key_line("외형은 연속, 절단은 제도가 만든다.", y=900, fs=28)}
{trigger("부록 App-RDD 풀 검증")}
{page_num(21)}
'''
    return svg_doc(body)


def slide_22():  # cutoff 4 막대
    body = f'''
{header("타겟은 12월 1일", "— 4 cutoff 중 가장 강한 절단점.")}

<text x="960" y="290" text-anchor="middle" font-size="88" font-weight="800" fill="{TEXT}" letter-spacing="2">11.30 ⇆ 12.01</text>

{chart_box(80, 360, 1100, 460, "fig_slide22_cutoff_bars.png (3·6·9·12월 점프 ×1.97 최대)")}

{kpi_box(1240, 360, 600, 460, [
    '@cutoff별 점프 (전월 대비)',
    '3월   β=0.17  → ×1.18',
    '6월   β=0.36  → ×1.44',
    '9월   β=0.22  → ×1.24',
    '-',
    '!12월  β=0.65  → ×1.97 ⭐',
    '@n = 18,348 활동×연도',
    '@분기말 cycle은 Act 4에서',
])}

{key_line("분기말마다 점프가 있지만, 12월이 가장 강하다.", y=900, fs=28)}
{trigger("그렇다면, 어느 사업 체질이 가장 강한가?")}
{page_num(22)}
'''
    return svg_doc(body)


def slide_23():  # 자산취득형 ×3.42 ⭐ 결정 카드
    body = f'''
{header("자산취득형 × 3.42", "— 회계 마감 직전·직후, 같은 사업이 일평균 3.4배.")}

{chart_box(80, 240, 1100, 580, "fig: h22_rdd_appendix.png (archetype별 β + 95% CI)")}

{kpi_box(1240, 240, 600, 580, [
    '@β · ratio · main_v2 §6.3',
    '전체            β=0.65 → ×1.91',
    '!C1 자산취득형  β=1.23 → ×3.42 ⭐',
    'C3 정상사업    β=0.81 → ×2.24',
    'C0 인건비형    β=0.11 → ×1.12',
    'C2 출연금형    β=0.10 → ×1.10 n.s.',
    '-',
    '@미국 (L-M 2017) 참조',
    'β=1.59 → ×4.9',
    '-',
    '@C2 12월 점프 없음 → Act 4 사이클로',
])}

{key_line("네 체질이 다르다 — 자산취득형은 3.4배 점프, 출연금형은 12월에 점프하지 않는다.", y=900, fs=22)}
{trigger("부록 App-RDD: 풀 회귀 · bandwidth · placebo")}
{page_num(23)}
'''
    return svg_doc(body)


def slide_24():  # 공사 vs 장부
    body = f'''
{header("공사 마감 vs 장부 마감", "")}

<text x="960" y="320" text-anchor="middle" font-size="40" font-weight="700" fill="{TEXT}">현장 공정률이 12월 1일에</text>
<text x="960" y="380" text-anchor="middle" font-size="48" font-weight="800" fill="{ACCENT}">3.4배 뛰는 것은 어렵다.</text>

<text x="960" y="500" text-anchor="middle" font-size="32" fill="{TEXT}">뛴 것은 회계 결재 시점이다.</text>

{chart_box(360, 580, 1200, 280, "fig: h22_rdd_yearly.png (11년 안정성 — 매년 동일 점프)")}

{key_line("인프라가 12월에 갑자기 완공되지 않는다. 결재가 12월에 갑자기 몰릴 뿐이다.", y=950, fs=22)}
{page_num(24)}
'''
    return svg_doc(body)


def slide_25():  # 행정 일정 우선
    body = f'''
{header("행정 일정이 앞선다", "")}

<text x="160" y="380" font-size="32" fill="{TEXT}">집행률 100%라는 *행정 시점*이</text>
<text x="160" y="440" font-size="32" fill="{TEXT}">*현장 진행*에 우선한다.</text>

<text x="160" y="580" font-size="24" fill="{SUB}">사업이 끝나서 돈이 나가는 것이 아니라,</text>
<text x="160" y="620" font-size="24" fill="{SUB}">돈이 나가야 하니 사업이 끝났다고 적는다.</text>

<line x1="160" y1="720" x2="1760" y2="720" stroke="{ACCENT}" stroke-width="2"/>

{key_line("평가표가 사업 종료의 정의가 된다.", y=830, fs=36)}
{trigger("그렇다면, 시간 차원에서는?")}
{page_num(25)}
'''
    return svg_doc(body)


def slide_26():  # 렌즈 3 — 세 렌즈의 정렬
    body = f'''
{header("렌즈 3 — 세 렌즈의 정렬", "— 파동을 세 도구로 동시에 본다.")}

<text x="80" y="240" font-size="20" fill="{TEXT}">시간 동학을 세 각도에서 — 주파수(FFT), 시간×주파수(Wavelet), 추세+계절성(NeuralProphet).</text>
<text x="80" y="275" font-size="20" fill="{TEXT}">세 도구가 같은 방향을 가리키는가, 다른 측면을 보는가.</text>

{chart_box(80, 320, 1760, 540, "fig_slide26_3lens_cards.png (FFT · Wavelet · NP 3 카드)")}

{key_line("트라이앵귤레이션 — 합의가 아니라 상호 보완.", y=920, fs=28)}
{page_num(26)}
'''
    return svg_doc(body)


def slide_27():  # FFT
    body = f'''
{header("FFT — 숨겨진 맥박", "— 분기 박자가 모든 체질에 박혀 있다.")}

<g transform="translate(80, 220)">
  <rect x="0" y="0" width="1760" height="50" fill="#FFFAE0" stroke="#d4ac0d" rx="6"/>
  <text x="24" y="33" font-size="16" fill="{TEXT}" font-style="italic">💡 한 곡을 음높이별로 쪼개 — 어느 음이 가장 강한지 본다.</text>
</g>

{chart_box(80, 300, 1100, 500, "fig: h27_psd.png (archetype별 PSD)")}

{kpi_box(1240, 300, 600, 500, [
    '@PSD 결과',
    '!분기 (3m) PSD ≈ 0.27',
    '   (자산·정상·인건비 공통)',
    '!C2 출연금 12m = 0.332',
    '   (다른 원형 대비 ~2배)',
    'C0 인건비 12m = 0.097',
    '   (가장 낮음, 비교군)',
    '-',
    '@▸ 모델: DFT (Welch 1967)',
    '@▸ 검증: white noise null',
])}

{key_line("분기 박자가 모든 체질에 박혀 있다. 단, 출연금형은 12개월에 한 번 더 큰 박자.", y=890, fs=22)}
{trigger("App-WAV 풀 검증")}
{page_num(27)}
'''
    return svg_doc(body)


def slide_28():  # Wavelet +554% ⭐ 결정 카드 (2 컷)
    body = f'''
{header("+554%", "— 단일 주파수의 우연이 아니다.")}

<g transform="translate(80, 220)">
  <rect x="0" y="0" width="1760" height="50" fill="#FFFAE0" stroke="#d4ac0d" rx="6"/>
  <text x="24" y="33" font-size="16" fill="{TEXT}" font-style="italic">💡 한 곡을 시간대별로 잘라 — 시점마다 어느 음이 강했는지. 음악 스펙트로그램처럼.</text>
</g>

{chart_box(80, 300, 870, 360, "fig: h28_evolution (12m cycle 11년 진화)")}
{chart_box(970, 300, 870, 360, "fig: h28_scaleogram (4 archetype 시간×주파수)")}

{kpi_box(80, 690, 1760, 200, [
    '@12m 사이클 진폭 강화 (2015–2017 → 2023–2025)        scaleogram max power',
    '!C2 출연금형  +554% ⭐    C3 정상  +317%             C2: 1.65   vs   C0: 0.01',
    'C1 자산취득형  +175%     C0 인건비형 −0.8% (비교군)   격차  × 163',
])}

{key_line("한 주파수의 우연이 아니다. 4 체질의 지문이 동시에 강해졌다.", y=940, fs=24)}
{trigger("App-WAV: COI · red noise null")}
{page_num(28)}
'''
    return svg_doc(body)


def slide_29():  # NeuralProphet
    body = f'''
{header("NeuralProphet — 추세 제거 후, 남는 계절성", "")}

<g transform="translate(80, 220)">
  <rect x="0" y="0" width="1760" height="50" fill="#FFFAE0" stroke="#d4ac0d" rx="6"/>
  <text x="24" y="33" font-size="16" fill="{TEXT}" font-style="italic">💡 기온 데이터에서 '지구온난화 추세'를 빼고 — '4계절' 패턴만 본다.</text>
</g>

{chart_box(80, 300, 1100, 480, "fig_slide29_np_decomposition.png (trend + seasonality 분해)")}

{kpi_box(1240, 300, 600, 480, [
    '@▸ 측정',
    '추세 + 계절성 분해',
    '@▸ 모델',
    'NP = trend(piecewise) + Fourier S',
    '※ AR Net 제외 — 메시지 분산 회피',
    '@▸ 추정',
    '잔존 계절성 강도 (추세 통제 후)',
    '@▸ 검증',
    'CV MAPE · residual ACF',
    '@▸ 출처: Triebe et al. 2021',
])}

{key_line("자연 증가 추세를 걷어내도, 계절성은 깨끗하게 남는다.", y=890, fs=24)}
{trigger("App-WAV: AR Net robustness")}
{page_num(29)}
'''
    return svg_doc(body)


def slide_30():  # 트라이앵귤레이션
    body = f'''
{header("세 도구가 같은 방향을 가리킨다", "— FFT · STL · NP 분야별 outcome 상관.")}

{chart_box(80, 240, 1240, 580, "fig: report/np_3way_outcome.png (3 도구 × 14분야 outcome r)")}

{kpi_box(1380, 240, 460, 580, [
    '@세 지표 동시 방향',
    'FFT amp_12m_norm',
    'STL seasonal_strength',
    'NP yearly_seasonality',
    '-',
    '@강한 음 상관 (측정 적응)',
    '!교육 · 보건',
    '!통신 · 공공질서',
    '-',
    '@사회복지 부호 반전',
    '→ Slide 35 fortuitous',
])}

{key_line("세 도구가 같은 방향. 합의가 아니라 상호 보완이 그 자체로 검증이다.", y=900, fs=22)}
{page_num(30)}
'''
    return svg_doc(body)


def slide_31():  # 소결 (Act 4 → 5)
    body = f'''
<text x="960" y="380" text-anchor="middle" font-size="50" font-weight="800" fill="{TEXT}">이제 모델이 식별할 수 있을 만큼,</text>
<text x="960" y="460" text-anchor="middle" font-size="50" font-weight="800" fill="{ACCENT}">견고한 주기.</text>

<text x="960" y="580" text-anchor="middle" font-size="17" fill="{SUB}" font-style="italic">명시적 미래 예측은 본 분석 범위 밖. 다만 자가 강화 추세 자체가 시사적.</text>
<text x="960" y="610" text-anchor="middle" font-size="15" fill="{SUB}" font-family="monospace">Pre-COVID +0.068/yr → COVID 충격 → elevated plateau</text>

<line x1="600" y1="710" x2="1320" y2="710" stroke="{ACCENT}" stroke-width="2"/>

{key_line("제도가 만든 박자가, 이제 모델의 박자다.", y=820, fs=32)}
{trigger("그렇다면 — 이 박자가 결과에 영향을 미치는가?")}
{page_num(31)}
'''
    return svg_doc(body)


def slide_32():  # Output vs Outcome
    body = f'''
{header("Output vs Outcome", "— 집행률 ≠ 효과.")}

<text x="80" y="240" font-size="20" fill="{TEXT}">집행률 100%는 *어떻게 쓰였는가* · *목표를 달성했는가* 묻지 않는다.</text>
<text x="80" y="275" font-size="20" fill="{TEXT}">같은 집행률 아래서, 결과 지표는 분야마다 약 8배 분산된다.</text>

{chart_box(80, 320, 870, 480, "fig_slide32_outcome_sd.png (14분야 outcome 상관 강도)")}
{chart_box(970, 320, 870, 480, "fig: 집행률 분포 미니 — Slide 6 재현")}

{key_line("같은 집행률이 같은 효과가 아니다 — 결과는 약 8배 분산된다.", y=900, fs=26)}
{page_num(32)}
'''
    return svg_doc(body)


def slide_33():  # 매개 ⭐ 결정 카드
    body = f'''
{header("매개 경로 — Sobel z = −2.897", "— 12월 집중이 농가소득을 매개한다.")}

<g transform="translate(80, 220)">
  <rect x="0" y="0" width="1760" height="50" fill="#FFFAE0" stroke="#d4ac0d" rx="6"/>
  <text x="24" y="33" font-size="16" fill="{TEXT}" font-style="italic">💡 12월에 몰린 돈이, 농가소득에 도달하기 전에 어디서 흩어지는가.</text>
</g>

{chart_box(80, 300, 870, 480, "fig_slide33_mediation_diagram (X → M → Y + Sobel)")}
{chart_box(970, 300, 870, 480, "fig: h14_quadrant.png (부처별 노출 × outcome)")}

{kpi_box(80, 810, 1760, 100, [
    '@농림수산 H4 Sobel z = −2.897 (p=0.004)         Bootstrap 95% CI [−0.41, −0.09]         14분야 중 유일하게 강한 매개',
])}

{key_line("14분야 중 농림수산만 — 시점 압력이 결과까지 전달된다.", y=970, fs=24)}
{page_num(33)}
'''
    return svg_doc(body)


def slide_34():  # 농가소득의 역설
    body = f'''
{header("농가소득의 역설", "— 수확기와 집행 시점이 어긋날 때.")}

{chart_box(80, 240, 1760, 540, "fig_slide34_agri_dec_timeline.png (농림수산 11년 12월 비중)")}

<g transform="translate(80, 810)">
  <text x="0" y="0" font-size="18" fill="{TEXT}">농어업재해보험재보험금 (12월 31.3% · 집행률 71.3% · App-A ranking 5위) 같은</text>
  <text x="0" y="32" font-size="18" fill="{TEXT}">농수산 사업의 집중이 수확기와 어긋날 때, 농가소득은 다음 해로 미뤄진다.</text>
</g>

{key_line("12월에 몰린 농수산 예산은, 농가소득을 다음 해로 미룬다.", y=970, fs=24)}
{page_num(34)}
'''
    return svg_doc(body)


def slide_35():  # 사회복지 fortuitous
    body = f'''
{header("사회복지의 우연한 정렬 (fortuitous)", "— r = −0.86, 그러나 의도된 효과 아님.")}

{chart_box(80, 240, 1100, 580, "fig: h10_v3_robustness_small.png (사회복지 r=-0.86 + LOO)")}

{kpi_box(1240, 240, 600, 350, [
    '@사회복지 outcome 상관',
    '!Pearson r = −0.86',
    '@LOO 안정',
    '변동 ±0.05',
    '@CPI 통제 후',
    '!더 강화 → −0.86',
])}

<g transform="translate(1240, 620)">
  <rect x="0" y="0" width="600" height="200" fill="#FFF5F5" stroke="{ACCENT}" stroke-width="2" rx="8"/>
  <text x="24" y="34" font-size="16" font-weight="700" fill="{ACCENT}">⚠ 다른 분야로 일반화 금지</text>
  <text x="24" y="68" font-size="13" fill="{TEXT}">사회복지 = *기계적 소득 이전* 중심</text>
  <text x="24" y="92" font-size="13" fill="{TEXT}">(기초연금·기초생활보장·아동수당)</text>
  <text x="24" y="124" font-size="13" fill="{TEXT}">어차피 자동 분배되는 예산이</text>
  <text x="24" y="148" font-size="13" fill="{TEXT}">12월에도 분배됐을 뿐.</text>
  <text x="24" y="180" font-size="12" fill="{SUB}" font-family="monospace">→ Q6 Q&A 카드</text>
</g>

{key_line("같은 음 상관이라도, 메커니즘이 다르면 의미가 다르다.", y=900, fs=26)}
{page_num(35)}
'''
    return svg_doc(body)


def slide_36():  # 시사점 ①
    body = f'''
<text x="80" y="90" font-size="14" fill="{ACCENT}" font-weight="600" font-family="monospace">실무적 시사점 ①</text>
{header("평가는 체질을 따른다", "")}

<g transform="translate(80, 240)">
  <rect x="0" y="0" width="1760" height="80" fill="#FFFAE0" stroke="#d4ac0d" rx="6"/>
  <text x="24" y="32" font-size="14" fill="{TEXT}" font-style="italic">이하 5장은 본 분석의 실무적 시사점 —</text>
  <text x="24" y="56" font-size="14" fill="{TEXT}" font-style="italic">평가 · 회계 · 모니터링 · 진화 · 정책 도구의 5 layer.</text>
</g>

<g transform="translate(160, 420)">
  <text x="0" y="0" font-size="34" fill="{TEXT}">분석이 식별한 4 체질은</text>
  <text x="0" y="60" font-size="34" fill="{TEXT}">시점 압력의 메커니즘이 모두 다르다.</text>
  <text x="0" y="160" font-size="30" fill="{SUB}">일괄 평가는 동일 효과를 만들지 못한다.</text>
</g>

<line x1="160" y1="780" x2="1760" y2="780" stroke="{ACCENT}" stroke-width="2"/>

{key_line("같은 평가표가 같은 결과를 만들지 않는다.", y=870, fs=30)}
{page_num(36)}
'''
    return svg_doc(body)


def slide_37():  # 시사점 ② — 회계
    body = f'''
<text x="80" y="90" font-size="14" fill="{ACCENT}" font-weight="600" font-family="monospace">실무적 시사점 ②</text>
{header("회계 — Archetype 맞춤 유연화", "제안 1 — 현행 법 조항의 구체 변경 가이드.")}

<!-- 3 박스 -->
<g transform="translate(80, 260)">
  <rect x="0" y="0" width="580" height="560" fill="{GHOST}" stroke="{ACCENT}" rx="8"/>
  <rect x="0" y="0" width="4" height="560" fill="{ACCENT}"/>
  <text x="24" y="40" font-size="20" font-weight="700" fill="{ACCENT}">C1 자산취득형 — 다년도 회계 격상</text>
  <text x="24" y="84" font-size="14" font-weight="600" fill="{TEXT}">▸ 현행 한국 제도</text>
  <text x="24" y="108" font-size="12" fill="{SUB}">「국가재정법」 제3조: 연도 단년 원칙</text>
  <text x="24" y="128" font-size="12" fill="{SUB}">「국가재정법」 제46조: 불용액 이월 금지</text>
  <text x="24" y="148" font-size="12" fill="{SUB}">제7조 MTEF: 5년 계획이나 회계 단년</text>
  <text x="24" y="200" font-size="14" font-weight="600" fill="{TEXT}">▸ 변경 가이드</text>
  <text x="24" y="224" font-size="12" fill="{TEXT}">① 제46조 개정 — 인프라·자산취득성 자동 이월</text>
  <text x="24" y="244" font-size="12" fill="{TEXT}">② 제7조 격상 — MTEF → multi-year appropriation</text>
  <text x="24" y="264" font-size="12" fill="{TEXT}">③ Capital DEL 분리 회계 (영국 모델)</text>
  <text x="24" y="316" font-size="14" font-weight="600" fill="{TEXT}">▸ 벤치마크</text>
  <text x="24" y="340" font-size="12" fill="{SUB}">• 영국 Capital DEL 다년도</text>
  <text x="24" y="360" font-size="12" fill="{SUB}">• 미국 USACE multi-year</text>
  <text x="24" y="412" font-size="14" font-weight="600" fill="{TEXT}">▸ 예상 효과</text>
  <text x="24" y="436" font-size="12" fill="{TEXT}">• C1 12월 점프 ×3.42 → ×1.9 이하</text>
  <text x="24" y="456" font-size="12" fill="{TEXT}">• 신공항 38.2% 등 불용 위험 정상화</text>

  <rect x="590" y="0" width="580" height="560" fill="{GHOST}" stroke="{ORANGE}" rx="8"/>
  <rect x="590" y="0" width="4" height="560" fill="{ORANGE}"/>
  <text x="614" y="40" font-size="20" font-weight="700" fill="{ORANGE}">C2 출연금형 — 정산 분기·반기 분산</text>
  <text x="614" y="84" font-size="14" font-weight="600" fill="{TEXT}">▸ 현행 한국 제도</text>
  <text x="614" y="108" font-size="12" fill="{SUB}">「공공기관운영법 시행령」 제27조</text>
  <text x="614" y="128" font-size="12" fill="{SUB}">— 출연금 연 1회 정산 (회계 종료 후 2개월)</text>
  <text x="614" y="148" font-size="12" fill="{SUB}">— 일괄 교부 → 12월 정산 압력</text>
  <text x="614" y="200" font-size="14" font-weight="600" fill="{TEXT}">▸ 변경 가이드</text>
  <text x="614" y="224" font-size="12" fill="{TEXT}">① 시행령 제27조 개정 — 분기 진행+반기 정산</text>
  <text x="614" y="244" font-size="12" fill="{TEXT}">② 교부 시점 분산 — 1회 → 분기별 분할</text>
  <text x="614" y="264" font-size="12" fill="{TEXT}">③ 출연기관 단기 현금 관리 인프라</text>
  <text x="614" y="316" font-size="14" font-weight="600" fill="{TEXT}">▸ 벤치마크</text>
  <text x="614" y="340" font-size="12" fill="{SUB}">• 독일 Quartalsabrechnung</text>
  <text x="614" y="360" font-size="12" fill="{SUB}">• 일본 IPA·NEDO 반기 진행</text>
  <text x="614" y="412" font-size="14" font-weight="600" fill="{TEXT}">▸ 예상 효과</text>
  <text x="614" y="436" font-size="12" fill="{TEXT}">• Wavelet +554% 사이클 약화</text>
  <text x="614" y="456" font-size="12" fill="{TEXT}">• 출연기관 현금 흐름 안정화</text>

  <rect x="1180" y="0" width="580" height="560" fill="{GHOST}" stroke="{GRAY}" rx="8"/>
  <rect x="1180" y="0" width="4" height="560" fill="{GRAY}"/>
  <text x="1204" y="40" font-size="20" font-weight="700" fill="{TEXT}">평가지표 — archetype 차등 인정</text>
  <text x="1204" y="84" font-size="14" font-weight="600" fill="{TEXT}">▸ 현행</text>
  <text x="1204" y="108" font-size="12" fill="{SUB}">「공기업·준정부기관 경영평가편람」</text>
  <text x="1204" y="128" font-size="12" fill="{SUB}">사업비집행률 1.5~3점</text>
  <text x="1204" y="148" font-size="12" fill="{SUB}">100% 직선 평가 (체질 무차별)</text>
  <text x="1204" y="200" font-size="14" font-weight="600" fill="{TEXT}">▸ 변경</text>
  <text x="1204" y="224" font-size="12" fill="{TEXT}">archetype 차등 인정</text>
  <text x="1204" y="266" font-size="12" fill="{TEXT}">• C0·C3 (비교군): 현행 유지</text>
  <text x="1204" y="298" font-size="12" fill="{TEXT}">• C1: 다년도 평균 평가</text>
  <text x="1204" y="330" font-size="12" fill="{TEXT}">• C2: 분기별 진행 평가</text>
  <text x="1204" y="412" font-size="14" font-weight="600" fill="{TEXT}">▸ 예상 효과</text>
  <text x="1204" y="436" font-size="12" fill="{TEXT}">분석 대상 (16.2%) 정밀 평가</text>
  <text x="1204" y="456" font-size="12" fill="{TEXT}">비교군 (83.8%) 행정 부담 최소</text>
</g>

{key_line('변경 대상은 「국가재정법」 제46조·제7조 + 「공공기관운영법 시행령」 제27조.', y=890, fs=22)}
{page_num(37)}
'''
    return svg_doc(body)


def slide_38():  # 시사점 ③ — 모니터링 대시보드
    body = f'''
<text x="80" y="90" font-size="14" fill="{ACCENT}" font-weight="600" font-family="monospace">실무적 시사점 ③</text>
{header("모니터링 — 5종 지표 대시보드", "제안 2 — 본 분석 직접 출력물: 지표 5종 + 4 layer.")}

<text x="80" y="240" font-size="16" fill="{SUB}" font-style="italic">출발점: FIS 22-03 (2022) 권고 "주요 불용사업 29.3% 집중 관리"</text>

<!-- 지표 5종 -->
<g transform="translate(80, 280)">
  <rect x="0" y="0" width="860" height="180" fill="{GHOST}" stroke="{BOX_BORDER}" rx="8"/>
  <text x="24" y="32" font-size="16" font-weight="700" fill="{TEXT}">본 분석 제공 지표 5종</text>
  <text x="24" y="64" font-size="13" fill="{TEXT}">① Goodhart Exposure Score (임계 ≥ 0.3 자동 알람)</text>
  <text x="24" y="86" font-size="13" fill="{TEXT}">② Archetype 분류 (1,557 세부사업 C0~C3 lookup)</text>
  <text x="24" y="108" font-size="13" fill="{TEXT}">③ 11월 말 12월 burst 예측 신호</text>
  <text x="24" y="130" font-size="13" fill="{TEXT}">④ Outcome 차분 상관 (14분야 트래픽 라이트)</text>
  <text x="24" y="152" font-size="13" fill="{TEXT}">⑤ Wavelet 사이클 진폭 시간 추적</text>
</g>

<g transform="translate(80, 480)">
  <rect x="0" y="0" width="860" height="160" fill="{GHOST}" stroke="{BOX_BORDER}" rx="8"/>
  <text x="24" y="32" font-size="16" font-weight="700" fill="{TEXT}">대시보드 4 layer</text>
  <text x="24" y="64" font-size="13" fill="{TEXT}">• 세부사업 layer (n=1,557): 사업명 lookup</text>
  <text x="24" y="86" font-size="13" fill="{TEXT}">• 부처 layer (n=72): 4분면 위치 진단 (h14_quadrant)</text>
  <text x="24" y="108" font-size="13" fill="{TEXT}">• 분야 layer (n=14): outcome 영향 매핑</text>
  <text x="24" y="130" font-size="13" fill="{TEXT}">• 시간 layer: Wavelet 동학 시계열</text>
</g>

<g transform="translate(980, 280)">
  <rect x="0" y="0" width="860" height="180" fill="{GHOST}" stroke="{BOX_BORDER}" rx="8"/>
  <text x="24" y="32" font-size="16" font-weight="700" fill="{TEXT}">한국 적용 변경 가이드</text>
  <text x="24" y="64" font-size="13" fill="{TEXT}">• 한국재정정보원 dBrain+ 디지털 인프라 확장</text>
  <text x="24" y="86" font-size="13" fill="{TEXT}">• 매년 결산 후 자동 갱신</text>
  <text x="24" y="108" font-size="13" fill="{TEXT}">  (11월=사전 / 1월=사후)</text>
  <text x="24" y="130" font-size="13" fill="{TEXT}">• 공공기관 경영평가편람 별첨 자료</text>
</g>

<g transform="translate(980, 480)">
  <rect x="0" y="0" width="860" height="160" fill="{GHOST}" stroke="{BOX_BORDER}" rx="8"/>
  <text x="24" y="32" font-size="16" font-weight="700" fill="{TEXT}">벤치마크 & 예상 효과</text>
  <text x="24" y="64" font-size="13" fill="{SUB}">• 미국 GAO Year-End Spending Reports</text>
  <text x="24" y="86" font-size="13" fill="{SUB}">• 영국 NAO Departmental Capital Expenditure</text>
  <text x="24" y="120" font-size="13" fill="{TEXT}">→ FIS 권고 자동화 (매년 갱신)</text>
  <text x="24" y="142" font-size="13" fill="{TEXT}">→ 11월 사전 신호 → 12월 burst 조기 식별</text>
</g>

{key_line("FIS 권고를, 5종 지표 대시보드로.", y=900, fs=28)}
{page_num(38)}
'''
    return svg_doc(body)


def slide_39():  # 시사점 ④ — 시스템 진화
    body = f'''
<text x="80" y="90" font-size="14" fill="{ACCENT}" font-weight="600" font-family="monospace">실무적 시사점 ④ — 시스템의 진화</text>

<text x="960" y="450" text-anchor="middle" font-size="56" font-weight="800" fill="{TEXT}">숫자를 맞추는 재정에서,</text>
<text x="960" y="560" text-anchor="middle" font-size="56" font-weight="800" fill="{ACCENT}">가치를 증명하는 재정으로.</text>

<line x1="700" y1="680" x2="1220" y2="680" stroke="{ACCENT}" stroke-width="3"/>
{page_num(39)}
'''
    return svg_doc(body)


def slide_40():  # 시사점 ⑤ — 정책 사분면 + Q&A
    body = f'''
<text x="80" y="90" font-size="14" fill="{ACCENT}" font-weight="600" font-family="monospace">실무적 시사점 ⑤</text>
{header("정책 도구 · Q&A", "")}

{chart_box(80, 240, 870, 480, "fig_slide40_business_quadrant.png (세부사업 1,556 점)")}
{chart_box(970, 240, 870, 480, "fig: h14_quadrant.png (72 부처 사분면)")}

<g transform="translate(80, 750)">
  <rect x="0" y="0" width="1760" height="150" fill="#FFF5F5" stroke="{ACCENT}" stroke-width="2" rx="8"/>
  <text x="24" y="32" font-size="16" font-weight="700" fill="{ACCENT}">분석 단위와 도구 단위는 다르다.</text>
  <text x="24" y="62" font-size="14" fill="{TEXT}">▸ 분석 layer: 사업 체질 (1,557 세부사업, 4 archetype) — 시점 압력 메커니즘은 사업 단위에서 작동</text>
  <text x="24" y="86" font-size="14" fill="{TEXT}">▸ 도구 layer: 부처/기관 (72개) — 정책 권한·책임은 행정 조직 단위</text>
  <text x="24" y="118" font-size="14" fill="{SUB}" font-style="italic">본 분석은 사업 단위에서 발견한 패턴을 부처 단위로 집계해, 책임자에게 도구로 제공한다.</text>
</g>

{key_line("발견은 사업 단위에서, 적용은 책임자 단위에서.", y=950, fs=26)}
<text x="1840" y="1050" text-anchor="end" font-size="18" fill="{SUB}" font-style="italic">질문 받습니다.</text>
{page_num(40)}
'''
    return svg_doc(body)


# ──────────────────────────────────────────────────────────────────────
# 생성
# ──────────────────────────────────────────────────────────────────────

SLIDES = {
    1: slide_01, 2: slide_02, 3: slide_03, 4: slide_04, 5: slide_05,
    6: slide_06, 7: slide_07, 8: slide_08, 9: slide_09, 10: slide_10,
    11: slide_11, 12: slide_12, 13: slide_13, 14: slide_14, 15: slide_15,
    16: slide_16, 17: slide_17, 18: slide_18, 19: slide_19, 20: slide_20,
    21: slide_21, 22: slide_22, 23: slide_23, 24: slide_24, 25: slide_25,
    26: slide_26, 27: slide_27, 28: slide_28, 29: slide_29, 30: slide_30,
    31: slide_31, 32: slide_32, 33: slide_33, 34: slide_34, 35: slide_35,
    36: slide_36, 37: slide_37, 38: slide_38, 39: slide_39, 40: slide_40,
}

count = 0
for n, fn in SLIDES.items():
    path = OUT_DIR / f'slide-{n:02d}.svg'
    path.write_text(fn(), encoding='utf-8')
    count += 1

print(f'\n=== {count} SVG wireframes generated ===')
print(f'위치: {OUT_DIR}')
