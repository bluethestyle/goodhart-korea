# 논문 (Typst)

- `main_v2.typ` — *active*: P-A 모형 + 6 가설 검증, 54p
- `main.typ` — v1 preserved: 다각적 측정, 58p
- `refs.bib` — 38 BibTeX entries

## 컴파일

```bash
# Typst 설치: https://typst.app/docs/install/
# 또는: cargo install --locked typst-cli

cd paper/
typst compile main_v2.typ main_v2.pdf
typst watch main_v2.typ main_v2.pdf
```

## VS Code

[Tinymist Typst extension](https://marketplace.visualstudio.com/items?itemName=myriad-dreamin.tinymist) 설치 시 실시간 미리보기.

## 한글 폰트

- 본문: **Noto Serif KR** (Google open-source, modern KCI standard)
- 헤딩: **Pretendard** (Korean sans-serif, modern academic style)
- Fallback chain: Times New Roman → Noto Serif KR → HYSinMyeongJo → Batang
- 위 폰트는 `paper/fonts/` 에 로컬 설치 (gitignored, 114MB). 시스템 폰트로도 가능.
- Pretendard download: https://github.com/orioncactus/pretendard
- Noto Serif KR download: https://fonts.google.com/noto/specimen/Noto+Serif+KR

## 구조

```
paper/
├── main_v2.typ         논문 v2 (active draft, ~1435 lines)
├── main.typ            논문 v1 (preserved, ~1260 lines)
├── refs.bib            38 BibTeX entries
├── figures/            10+ core figures (h3_umap, h4_mapper, h22_rdd, h27_*, h28_* 등)
├── fonts/              Noto Serif KR + Pretendard (gitignored)
├── preview/            preview renders (gitignored)
└── README.md           본 문서
```

## 버전 변경 사항 (v1 → v2)

- **구조 재편**: 결과 7개 → 6 가설 검증 (P-A 모형 직접 도출)
- **이론 §3 신설**: 균형점 도출, 비교정역학, Career Concerns Bayesian update
- **신규 분석**: H26 NeuralProphet, H27 PSD/Phase/Coherence, H28 Wavelet
- **★ 클러스터 라벨 정정**: H22 RDD 점프 = *자산취득형* 3.42배 (이전 v1 일부 표기 오류 수정 — 출연금형은 사이클 우세 H3로 분리)

## v2 진행 사항 + 남은 작업

- ✅ Principal-Agent 이론 모형 §3 도입 (Holmstrom-Milgrom 1991 + Holmstrom 1999 career concerns + Sannikov 2008 + Hardt 2016 + Perdomo 2020)
- ✅ 6 가설 H1~H6 검증 매핑
- ✅ Wavelet 분석 H28 통합 (출연금형 +554%)
- ✅ Modern KCI 폰트 (Noto Serif KR + Pretendard)
- ✅ Booktabs 표 디자인 + 한국 학술지 표준 들여쓰기
- ✅ 핵심 figure 10+ import 완료
- [ ] 영문 변환 (Zenodo 영문 working paper)
- [ ] DOI 발급 (Zenodo)
- [ ] KCI 학회용 축약 (한국행정학보 또는 한국정책학회보 양식)
- [ ] 저자명·소속·이메일 입력
- [ ] 한글 abstract + 영문 abstract pair (KCI 표준)

## AI 도구 사용

본 논문은 Anthropic Claude (claude-opus-4-7) Claude Code 환경에서 분석 코드 + Typst 본문 작성 + figure 생성 + 참고문헌 정리 전반을 보조 받아 작성됨. 자세한 내용은 `main_v2.typ`의 "AI 도구 사용 명시" 섹션 참조.
