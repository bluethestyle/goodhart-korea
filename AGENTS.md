# 프로젝트 가드레일 (재정자료분석)

## 이미지 처리 — Hard Stop (절대 위반 금지)

### 0. Read 전 사이즈 확인은 **무조건 선행**. 예외 없음.

**어떤 PNG/JPG/스크린샷이든 Read 도구 호출 전에 width를 먼저 확인하라.** 새로 생성한 차트, 갓 캡처한 이미지, PDF에서 추출한 페이지, 사용자가 가리킨 자산 모두 동일. 사이즈를 모른 채 Read하지 말 것.

확인 명령(반드시 Read 직전):
```bash
python -c "from PIL import Image; print(Image.open('PATH').size)"
```
또는 디렉터리 일괄:
```bash
python -c "from PIL import Image, os; \
[print(f, Image.open(f).size) for f in sorted(os.listdir('.')) if f.endswith('.png')]"
```

### 1. 임계값 — 2000px

width(또는 height) **2000px 이상이면 그대로 Read 금지**. 권장 작업폭은 **1280px 이하**.

위반 시 발생하는 실제 에러 문구 (이게 뜨면 즉시 작업 중단·리사이즈):
> An image in the conversation exceeds the dimension limit for many-image requests (2000px). Start a new session with fewer images.

이 메시지가 출현하면 **세션 자체가 위태로워진다** — 컨텍스트 폭증·재현 비용 증가·작업 흐름 단절.

### 2. 적용 절차
1. **캡처/추출 단계에서부터** width ≤ 1280로 출력
   - Playwright/Puppeteer: `viewport: { width: 1280, height: 720 }`
   - PDF 페이지 추출: dpi ≤ 150 (`pdftoppm -r 150` 또는 `pdf2image dpi=150`, PyMuPDF `fitz.Matrix(zoom, zoom)` with zoom ≤ 0.6)
   - matplotlib 저장: `figsize × dpi ≤ 1280` (예: `figsize=(7,4), dpi=180` → 1260×720)
2. **이미 큰 원본만 있을 때**는 Read 직전에 PIL로 다운샘플:
   ```python
   from PIL import Image
   im = Image.open(src)
   if im.width > 1280:
       h = im.height * 1280 // im.width
       im.resize((1280, h), Image.LANCZOS).save(dst)
   ```
   원본은 보존하고 별도 폴더(`_v/`, `_v_full/`, `samples_small/` 등)에 small 버전 저장. **Read는 small 버전만**.
3. 자체 생성한 PNG도 **저장 후 size 출력 → 확인 → Read** 순서 유지.
4. width를 모르는 상태로 Read를 시도하지 말 것. 못 보면 못 본 채 다음 단계로 넘기지도 말 것 — 다른 검증 수단(matplotlib에서 figsize·dpi 직접 계산, 또는 `subprocess`로 size 확인) 사용.

### 기존 작업 폴더 규약
- `paper/slides/_audit_pages/` — 캡처 원본 (1280px 이하로 출력)
- `paper/slides/_v/` — Read용 다운샘플 (1024~1280px)

## 발표/슬라이드 작업 메모
- 트라이앵귤레이션은 "만장일치 합의"가 아닌 **상호 보완** framing — 도구 간 발산은 자기 비판의 출발점.
- 강한 매개 분야는 **농림수산** (사회복지 아님). 발표자료/문서에서 사회복지로 적힌 부분 발견 시 즉시 정정.

## 분석보고서(paper/analysis_report.typ) 작성 가드레일

### 자기 위치 — 학술 "연구"가 아니라 **미니프로젝트 분석**
- 한국재정정보원 주최 *2026년 재정데이터 분석 미니프로젝트* 출품작.
- 본문에서 "본 연구" 금지 → **"본 분석" / "본 보고서"**. 평가자가 학술 과대 포장으로 느낌.
- 평가자 = 재정정보원 담당자·실무 공무원. "망가진다·게임화·왜곡·함정" 같은 공격 어휘는 자기 기관 비판으로 들려 금지. 대신 "측정 적응 / 격차 / 불일치 / 사이클".

### 문체 — 사고 흐름형 (블로그 톤도, 결론-우선 학술 톤도 아님)
- 흐름: **시각화 → 의문 → 다른 각도 → 확인 → 새 질문**. "본 패널의 가장 두드러진 관찰 결과는 ~이다" 같은 결론-우선 표현 금지.
- 사고 동사 살리기: "그려본다 / 들여다보면 / 다른 각도로 본다 / 다음 질문이 떠오른다 / 그렇다면 ~".
- 자기지시("본 패널/본 분석") 빈도 절제. 평이체·중립체 유지하되 캐주얼("어 진짜 그렇네?", "그냥", "큰 돈", "그 막대")은 금지.
- 이전 수상작 톤 매칭: "OO 분석" · "OO에 대한 이해" · "OO은 어디에 ~하는가 : 데이터로 본 ~". 표지·헤딩에서 시적/도발적 카피 회피.

### 학술 frame 등장 위치 — § 6에서만
- § 5까지는 *일상 어휘만으로 서술*. 굿하트-캠벨·다업무 계약·연성 예산 같은 학술 frame은 § 6 통합 매칭 챕터에서 처음 등장.
- 본문에서 학술 용어 막힌 독자는 부록 A 용어집으로.

### typst 작성 함정 (반복 발견)
1. **`~` 가 nbsp 처리됨**. 숫자 범위 "95~100%" → 화면에 "95 100%"로 깨짐. 해결: `–` (en dash) 사용 → `95–100%`.
2. **한국어 조사 + dict 키 충돌**. `#meta.team이`를 typst 파서가 `team이` 키로 해석 → 에러. 해결: `#(meta.team)이`처럼 괄호 토큰 분리.
3. **함수 + content block trailing 호출 충돌**. `term(name, en: none, body)` 같이 positional 인자를 named로 호출(`term(name: "X")[body]`)하면 trailing content가 `name` 자리에 바인딩되어 body missing. 해결: positional 호출 (`term("X", en: "Y")[body]`).
4. **`counter(...).display("01")` padding이 n≥10에서 "010"으로 깨짐**. 해결: 직접 pad 함수 `let pad2 = (n) => if str(n).len() == 1 { "0" + str(n) } else { str(n) }` 정의 후 `counter.display((..ns) => pad2(ns.pos().first()))`.
5. **`set heading(numbering: ...)` 없으면 카운터 자동 increment 안 됨** → 모든 헤딩 번호 "00". 해결: `#set heading(numbering: "1.")` 추가. show rule이 `it.body`만 가져오니 prefix는 본문에 안 보임.
6. **FIG + caption + grid를 한 페이지에 묶으려면 통째 block(breakable: false)** — grid만 block 묶고 chart는 별도면 chart-slot이 작은 페이지로 떨어져 빈 페이지 발생. 셋 다 묶음.
7. **§ N.M 헤딩 orphan** (페이지 끝에 헤딩만 떨어지고 본문은 다음 페이지). 해결: 헤딩까지 block(breakable: false) 안에 포함.
8. **KPI 카드 디자인 패턴** — 단순 stroke top 1.2pt만으로는 카드 묶음 약함. `fill: ghost + stroke: (left: 2pt + accent, rest: 0.5pt + line-c) + radius: (right: 4pt) + inset: 14pt + spacing: 8pt`. 내부 v 압축 (label → v(-10pt) → value → v(-10pt) → sub, 사용자 직접 음수 vstack 지정).
9. **헤딩 부제 (메인/부제 2계층)** — "메인 — 부제" em dash 패턴은 사용자가 어색하다 지적. inline `linebreak + text(size: 18pt)`로 헤딩 본문에 부제 넣으면 *목차에 부제가 메인보다 크게 표시*되는 부작용. 해결: 부제를 헤딩 본문에서 분리하여 별도 block paragraph로. helper `h1sub/h2sub`는 `block(inset: (top: <음수>))`로 헤딩 show rule v 간격 흡수. 호출은 헤딩 다음 줄 별도 paragraph. 그러면 outline에는 메인만, 본문에는 두 줄 디자인.

### 데이터·자산 위치
- `data/warehouse.duckdb` → 표 `monthly_exec` (FSCL_YY × EXE_M × OFFC_NM × FLD_NM × ACTV_NM, **EP_AMT = 월별 집행액**, 2015–2026, 41만 행).
- `paper/main_v2.typ` — 학술 논문 버전. 정확한 RDD 추정치 (전체 1.91배·자산취득형 3.42배 등) 인용 시 참조.
- `paper/fonts/Pretendard-*.otf` — matplotlib에서 한국어 폰트 깨짐 방지하려면 `font_manager.fontManager.addfont(path)`로 직접 등록 후 `rcParams['font.family'] = 'Pretendard'`.
- `paper/figures/eda/` — § 2 EDA 차트 저장 폴더. 차트는 dpi=140, figsize 7~11 inch로 width 1000~1600px.
- 이전 미디어 인용은 §1.1 박스 + 부록 E (한국재정정보원·서울경제·머니투데이·전국뉴스 등).
