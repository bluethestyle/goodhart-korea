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
