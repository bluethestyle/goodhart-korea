# graphify 도입·운영 지침 (다른 챗봇 / 다른 프로젝트 portable)

## 0. 한눈 요약

graphify는 폴더(코드+문서+산출물)를 `graph.json`으로 변환해, AI 어시스턴트가 BFS 부분 그래프 쿼리로만 접근하도록 만드는 도구. **사용자 인지 부담 절감 + 토큰 절감** 두 효과. 운영 자동화는 git post-commit 훅으로 해결.

## 1. One-time Setup (5분)

```bash
# 1. 설치 (PyPI 이름은 'graphifyy', CLI는 'graphify')
pip install graphifyy

# 2. 사용 중인 어시스턴트에 스킬 등록 (선택)
graphify install --platform claude     # 또는 codex / cursor / opencode / aider / gemini / ...

# 3. 첫 그래프 빌드 (LLM 0, 무료, 수 초)
graphify update .

# 4. 자동 갱신 훅 설치 (post-commit + post-checkout)
graphify hook install
graphify hook status                   # installed 확인

# 5. 산출물 gitignore
echo "graphify-out/" >> .gitignore
```

선택: 한국어 본문·코드 의미까지 잡으려면 분기에 한 번 `graphify extract . --backend gemini` (semantic, API 키·비용 필요).

## 2. AGENTS.md(또는 cursorrules / GEMINI.md / .codex-instructions)에 박을 블록

````markdown
## graphify 그래프 사용 — Hard Rule

`graphify-out/graph.json` (보통 수십만 토큰 분량) **절대 직접 Read 금지**.

### 사용 트리거 — 챗봇이 graphify를 백엔드로 먼저
사용자가 프로젝트 내부 개념·가설·산출물·함수·연결 관계에 대해 묻거나 설명을 요청하면,
답하기 전에 graphify CLI를 먼저 호출해 부분 그래프를 받고, 결과 + 본인 추론을 합쳐 답한다.
grep/Read보다 graphify가 우선.

매핑:
- "X가 뭐야 / X 설명해줘"          → `graphify explain "X"`
- "X 관련 코드·문서·자료 어디?"    → `graphify query "X 관련 ..."`
- "X와 Y 관계 / X에서 Y까지 연결?"  → `graphify path "X" "Y"`
- 광범위 탐색                       → `graphify query "..." --budget 3000`

### Read해도 되는 산출물
- `graphify-out/GRAPH_REPORT.md` — onboarding 시 1회만
- `graphify-out/graph.html`      — 브라우저 전용, Read 무의미

### 갱신 자동화
- post-commit/post-checkout 훅 설치 시 모든 commit·branch 전환 직후 `graphify update .` 자동 실행
- 훅 확인: `graphify hook status` · clone한 새 머신에선 `graphify hook install` 재실행 필요
- 커밋 없이 큰 수정 중 query 신뢰 필요할 때만 수동 `graphify update .`

### 예외 / 보강
- 일반 코딩·환경·문법 질문 (프로젝트 맥락 아님) → graphify 우회
- 사용자가 명시적으로 빠른 답·메모리만 요구 → 우회
- query 결과가 얕거나 옛 코드 가리킬 때 → 그 노드의 source_file만 Read로 보강 (graph.json 전체 Read는 금지 유지)

### Anti-pattern (즉시 멈출 것)
- `Read graphify-out/graph.json` — 위반 1순위
- `Grep`/`json.load`로 graph.json 전체 dump
- 매 작업마다 `graphify extract` 재실행
- stale 의심 결과를 검증 없이 신뢰
````

## 3. 챗봇 첫 세션 체크리스트

- [ ] `graphify hook status` — installed가 아니면 `graphify hook install`
- [ ] `graphify-out/graph.json` 존재 — 없으면 `graphify update .`
- [ ] `.gitignore`에 `graphify-out/` — 없으면 추가
- [ ] AGENTS.md(도구별 instruction 파일)에 위 가드레일 블록이 박혀있는지
- [ ] 시범 한 번: `graphify query "이 프로젝트 핵심 모듈"` 결과 살펴보고 graph가 의미 있게 비어있지 않은지 확인

## 4. 비용·속도 표 (참고용)

| 동작 | 토큰 | 시간 | 발생 시점 |
|---|---|---|---|
| `graphify update .` | 0 | 수 초~수 분 | post-commit/post-checkout 자동 |
| `graphify query` (기본 budget 2000) | ~2K | <1초 | 사용자 질문 시 |
| `graphify explain` | ~1~2K | <1초 | 사용자 질문 시 |
| `graphify path` | <1K | <1초 | 사용자 질문 시 |
| `graphify extract --backend ...` | 수만~수십만 | 분~수십분 | 분기 1회 권장 |
| `GRAPH_REPORT.md` Read | 수K~수십K | 즉시 | onboarding 1회 |
| graph.json 직접 Read | **수십만 (금지)** | — | 절대 금지 |
| SKILL.md (Claude 등) | ~18K | 즉시 | `/graphify` 호출 시만 |

## 5. 어시스턴트별 platform 이름

`graphify install --platform <name>`:

`claude` · `codex` · `cursor` · `opencode` · `aider` · `gemini` · `windows` · `claw` · `droid` · `trae` · `trae-cn` · `antigravity` · `hermes` · `kiro` · `pi`

(전체 목록·최신 추가는 `graphify --help` 출력 확인)

## 6. ROI 검증 — 도입 후 첫 주

새 프로젝트에 setup 후 챗봇에게 프로젝트 개념 질문 5개 던지고 다음을 체크:

1. 챗봇이 graphify CLI를 자동으로 백엔드 호출하는가? (가드레일 박힌 효과)
2. 답이 grep+Read 방식 대비 빠른가?
3. 새 인사이트(예: 예상외 community 클러스터링) 나오는가?

3개 중 2개 이상 yes면 도입 성공. 0~1개면 가드레일 미작동(AGENTS.md 위치·표현 점검) 또는 그래프가 너무 비어있음(`extract` 1회 권장).

## 7. 자주 새기는 함정

- **PyPI 이름이 `graphify`가 아니라 `graphifyy`** (이름 reclaim 중). 헷갈리면 그대로 `pip install graphifyy`.
- **`.git/hooks/`는 trackable하지 않음** — 다른 머신/clone마다 `graphify hook install` 재실행.
- **PowerShell/Windows에서 `python -m graphify` 실패할 수 있음** — pip이 깔린 Python과 기본 `python`이 다를 때. `graphify.exe`(또는 `where graphify`)를 직접 사용.
- **그래프가 비어있으면 가치 0** — 코드만 있고 문서·산출물 없는 프로젝트는 graphify ROI 낮음. scripts/만 있는 작은 repo면 IDE call graph로 충분.
