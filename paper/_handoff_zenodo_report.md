# [새 세션 프롬프트 ①] Zenodo 기술보고서 최종화 — `main_v2.typ` (84p 풀버전)

> 아래 블록 전체를 새 세션에 붙여넣어 시작.

---

## 작업
완성된 84페이지 학술 모노그래프 `paper/main_v2.typ`를 **Zenodo 업로드용 기술보고서(Technical Report)**로 최종 마감한다. **친절한 reader-first 문체를 그대로 유지**한다(이게 풀버전의 강점). 학회 축약본은 *다른 세션*에서 따로 작업하므로 여기선 건드리지 않는다.

## 배경 (맥락)
- 정본: `paper/main_v2.typ` — 한국어 학술 논문 "한국 정부 재정 집행의 굿하트 게임". 주인-대리인(P-A) 모형 + 신호처리(FFT·웨이블릿) + 차원축소(UMAP) + 위상수학(Mapper·Persistent Homology) + 인과(RDD·매개분석). 6가설 H1~H6.
- §3 이론모형 ~ §8·결론·행정 섹션까지 **reader-first 재작성 완료**(비유·풀이·각주·표준약어 글로스). 부록 A~G는 reader-first 미적용 — 상세 레퍼런스 성격이라 그대로 둬도 무방.
- Zenodo는 분량 제한 없음. **이 풀버전 = 확장 기술보고서**, 축약본 = 『재정학연구』 투고 논문(version of record). 두 버전이 다른 독자를 위해 공존.
- 중복게재 측면 안전: 재정학연구 규정은 "다른 **학술지** 중복"만 금지 → **연구보고서/Zenodo는 학술지가 아니라 무관**. 단 Zenodo 등록 타입은 "**Report / Technical report**"(저널논문 아님)로 선택하고, 익명심사 리스크 회피 위해 **공개는 학회 게재 확정 후** 권장.

## 할 일
1. **앞부속(front-matter) 확인·보완** (preamble 약 1~184행 점검):
   - 제목(국·영문), 저자·소속(+ORCID 자리), 국문초록·영문초록, 핵심주제어(국·영 5개 내외), **JEL 분류기호**(추천: `H61` 예산제도·`H50` 정부지출·`D73` 관료제 + `D82`/`D86` 정보비대칭·계약).
   - 표지/메타: 문서유형 "Technical Report", 버전 v1.0, 작성일(2026), 라이선스 **CC BY 4.0**, 권장 인용(suggested citation), DOI 자리표시자.
   - 한 줄 명시: "본 기술보고서는 동일 연구의 확장판이며, 축약본을 한국재정학회 『재정학연구』에 별도 투고함."(공개 시점은 게재 확정 후 권장)
2. **(선택) 부록 reader-first 일관성 패스** — 부록 C~G에 남은 영문/코드 jargon을 본문 수준으로 글로스. *대규모이므로 시간 여유 시에만*. 보고서엔 상세 유지가 자연스러워 필수 아님.
3. **최종 QA**:
   - `refs.bib` 가짜 인용 재유입 없는지 확인(과거 AI 환각 KCI 인용 3건 제거 이력 — `kim2022biyong` 등으로 교체됨).
   - 컴파일 broken ref·중복 라벨·경고 0, 페이지수 확인.
   - 그림 36개 참조 무결, 루트 `논문_참조_차트.zip` 최신(36개) 유지. 갱신 필요 시 `main_v2.typ`의 `image("figures/...")` 참조를 추출해 `paper/figures/...` 구조로 재빌드.
4. **산출**: 안전 해상도로 최종 PDF 렌더(업로드용), Zenodo 메타데이터(제목/저자/초록/키워드/JEL/라이선스/타입=Report) 정리.

## 절대 금지
- **terse화·축약 금지** — 친절한 비유·풀이·각주를 유지(이건 모노그래프용 강점). 압축은 학회본 세션의 일.
- `main_v2.typ`의 **수치·인용·결과 변경 금지**(편집은 앞부속·메타·선택적 부록 글로스에 한정).

## 프로젝트 정보·규칙 (공통)
- 작업 디렉터리: `d:\workspace\재정자료분석`
- 컴파일: `typst compile paper/main_v2.typ --font-path paper/fonts paper/main_v2.pdf`
- 한국어 폰트: `paper/fonts/Pretendard-*.otf`.
- git: main 브랜치. 섹션 단위 커밋 + 끝마다 push. 메시지 끝에 `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`.
- **typst 함정**: `@label`/`#cite` 뒤 한글 조사 직결 금지(명사 뒤 괄호 참조 `시계열(@fig-x)은` 또는 `#cite(<k>, form: "prose")`); `(@key)` 이중괄호 버그; 숫자~숫자는 `\~`/en-dash; 볼드 `*한글*(English)조사`; 헤딩에 `#cite` 금지.
- **이미지**: Read 전 사이즈 확인 필수(`python -c "from PIL import Image; print(Image.open('PATH').size)"`), ≥2000px Read 금지(≤1280px). PDF 페이지 렌더 `fitz.Matrix(1.7,1.7)`(≈1012px).
- 편집 후 반드시 컴파일 검증. 병렬 서브에이전트는 `model: "sonnet"` 명시.

## 시작
1. preamble(1~184행)과 §1 서론, 결론을 읽어 현재 front-matter 상태 파악.
2. 위 1)~4) 순서로 진행. 친절 문체 보존. 완료 시 커밋·푸시 + 업로드용 PDF 렌더.
