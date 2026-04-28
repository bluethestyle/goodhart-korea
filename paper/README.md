# 논문 (Typst)

`main.typ`가 본문, `refs.bib`가 참고문헌(BibTeX).

## 컴파일

```bash
# Typst 설치: https://typst.app/docs/install/
# 또는: cargo install --locked typst-cli

cd paper/
typst compile main.typ main.pdf
```

## 미리보기 (라이브)

```bash
typst watch main.typ main.pdf
```

## VS Code

[Tinymist Typst extension](https://marketplace.visualstudio.com/items?itemName=myriad-dreamin.tinymist) 설치 시 실시간 미리보기.

## 한글 폰트

`main.typ`는 `Noto Sans KR` 사용. 설치 안 됐으면:
- macOS/Linux: Google Fonts에서 다운로드
- Windows: `winget install Google.NotoSansKR` 또는 [Noto Fonts 페이지](https://fonts.google.com/noto/specimen/Noto+Sans+KR)

## 구조

```
paper/
├── main.typ      논문 본문 (~3000 단어 draft)
├── refs.bib      26개 핵심 참고문헌 (REFERENCES.md에서 추출)
├── README.md     본 문서
└── figures/      (TODO) main.typ에서 import할 figure
```

## TODO

- [ ] 핵심 figure 8-10개를 `figures/` 에 high-res로 복사 + Typst `#figure` 삽입
- [ ] 표 (수식·결과)를 Typst `#table()` 로 정리
- [ ] 한국정책학회보 또는 한국행정학보 양식 정확히 모방
- [ ] 저자명·소속·이메일 입력
- [ ] 영문 abstract 추가 (KCI 표준)

## AI 도구 사용

본 논문은 Anthropic Claude(claude-opus-4-7) Claude Code 환경에서 데이터 파이프라인·분석 코드·시각화·문서화를 보조 받아 작성됨. 자세한 내용은 `main.typ`의 "AI 도구 사용 명시" 섹션 참조.
