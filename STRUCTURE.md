# 프로젝트 구조 안내 (STRUCTURE)

> 처음 이 저장소를 보는 사람을 위한 *경로 지도*. 무엇이 **최종 산출물**이고, 무엇이 그것을
> 만드는 **소스/데이터/생성물**인지 4계층으로 구분한다. (분석 내용 소개는 [`README.md`](README.md))

## 한눈에 — 최종 산출물은 단 둘

| 산출물 | 위치 | 비고 |
|---|---|---|
| **논문** | [`paper/main_v2.typ`](paper/main_v2.typ) → `main_v2.pdf` | 정본. 영문판 `main_v2_en.typ`도 유지 |
| **슬라이드** | [`figma_exports/`](figma_exports/) `*.svg` | Figma 기반 SVG가 정본. 발표 내러티브는 `paper/재정데이터 분석 ppt/` |

나머지 모든 것은 이 둘을 만들기 위한 **소스 · 데이터 · 생성물**이다.

## 4계층

```
재정자료분석/
├─ ① 데이터 (값의 진실원천)
│  ├─ data/warehouse.duckdb         # 표 monthly_exec, 2015–2026 약 41만 행 (EP_AMT=월별 집행액)
│  ├─ data/results/*.csv            # 분석 산출 CSV (h*.py 가 생성)
│  ├─ data/external/                # 외부 지표 원자료 (KOSIS·ECOS·GIR 등)
│  └─ data/PROVENANCE.md            # ★ 값 계보 — 그림·수치가 어느 CSV/스크립트에서 나오는지
│
├─ ② 소스 (분석·생성 코드)
│  └─ scripts/                      # active 스크립트 142개
│     ├─ h{N}_*.py                  #   분석 단위 → data/results/*.csv
│     ├─ redo_fig*.py               #   논문 그림 재생성 → paper/figures/
│     ├─ build_slide*·build_*.py    #   슬라이드/figma 자산 빌더
│     ├─ fetch_*.py                 #   외부 지표 수집
│     ├─ _archive/                  #   대체·폐기 스크립트 24개 (git 추적, 참고 보존)
│     └─ README.md                  #   명명 규칙·archive 사유
│
├─ ③ 생성물 (코드가 만든 중간 자산)
│  ├─ paper/figures/                # 논문 그림 (main_v2.typ 참조 33개 + 부록)
│  ├─ paper/figures_en/             # 영문판 그림
│  └─ graphify-out/                 # 코드 그래프 (post-commit 훅 자동 갱신, gitignore)
│
└─ ④ 정본 산출물 (위 표의 둘)
   ├─ paper/   (main_v2.typ·main_v2.pdf·refs.bib·fonts/)
   └─ figma_exports/   (*.svg)
```

## 그 외 디렉터리

| 경로 | 용도 |
|---|---|
| `paper/재정데이터 분석 ppt/` | 슬라이드 내러티브 — 스토리보드(`00_스토리보드.md`)·부록(`App-*.md`)·`Q&A_카드.md`·`tokens.svg` |
| `docs/` | 분석 기록 (`JOURNEY.md` 등, mkdocs) |
| `deliverables/` | 기관별 제출 패키지 (moef·audit_board·kfi·npbo·moi) |
| `_archive/` | **구조 정리 격리소** (루트 — gitignore, 로컬 보관) — junk·폐기 슬라이드·고아 산출물. 비워도 무방 |

## 루트 문서

- [`README.md`](README.md) — 분석 내용·결과 소개
- [`STRUCTURE.md`](STRUCTURE.md) — (이 파일) 경로 지도
- [`data/PROVENANCE.md`](data/PROVENANCE.md) — 값 계보(단일 진실원천)
- [`슬라이드_수정사항.md`](슬라이드_수정사항.md) — 값 검증 결과 + 슬라이드 정정 체크리스트
- `CLAUDE.md` — 작업 가드레일(이미지 처리·문체·typst 함정·provenance 규약)

## 안전·정리 원칙 (2026-05-31 구조 정리)

1. 최종 산출물은 논문·슬라이드 둘. 나머지는 소스/데이터/생성물로 계층화.
2. 삭제 대신 격리 — git 추적분은 `scripts/_archive/`로 이동(이력 보존), gitignore 대상(junk·폐기 슬라이드)은 루트 `_archive/`로 로컬 이동(복구 가능).
3. **새 수치를 논문·슬라이드에 넣으면 `data/PROVENANCE.md`에 원천을 추가**한다 (37.2% 버그 재발 방지).
4. 그림은 `paper/figures/`, 슬라이드 SVG는 `figma_exports/`에만 둔다.
