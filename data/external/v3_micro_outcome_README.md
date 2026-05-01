# v3 Micro Outcome Data — Collection README

**Date collected:** 2026-04-30  
**Purpose:** Goodhart paper v3 — supplement macro outcomes (Gini, IMD) with project/institution-level evaluation grades as per reviewer request.

---

## Dataset 1: 알리오 공공기관 경영평가 (`v3_micro_eval_alio.csv`)

### Source
Primary: 기획재정부 경영평가 결과 보도자료 (annual press releases)  
Secondary: 이투데이, 경향신문, 전자신문, 뉴시스, fntimes, 가스뉴스 — grade-specific break-out articles (2024 evaluation results reported by grade category on 2025-06-20)

### Field Definitions
| Field | Description |
|-------|-------------|
| `agency_name` | 공공기관명 (public institution name) |
| `year` | 평가연도 (evaluation year — year of performance) |
| `grade` | 알파벳 등급: A/B/C/D/E |
| `grade_kor` | 한국어 등급: 우수/양호/보통/미흡/아주미흡 |
| `institution_type` | 공기업 / 준정부기관 |
| `supervising_ministry` | 주무부처 (mapped manually from institutional knowledge) |
| `h3_offc_match` | 1 if supervising_ministry is in H3 OFFC_NM set, else 0 |
| `source` | Article or official source |

### Rows Collected
- **Total rows: 105**
- 2024 evaluation: 65 institutions (공기업 complete set; 준정부기관 ~33/55)
- 2023 evaluation: 22 institutions (prominently reported only)
- 2022 evaluation: 18 institutions (prominently reported only)

### Grade Distribution (2024)
| Grade | Count |
|-------|-------|
| A (우수) | 15 |
| B (양호) | 28 |
| C (보통) | 9 (C-grade news article extracted 9/31) |
| D (미흡) | 9 (6 공기업 + 3 준정부) |
| E (아주미흡) | 4 (1 공기업 + 3 준정부) |

*Note: Full 2024 total = 87 공기업+준정부기관. We captured 65/87 = 75% for 2024, ~25% for 2022-2023.*

### Coverage Limits
- **Year range captured:** 2022–2024 (partial)
- **Years NOT captured:** 2015–2021 — results are in PDF files that WebFetch cannot parse
- **C-grade 2024:** Only 9/31 C-grade institutions extracted (news articles reported D/E/A grade lists; C-grade list incomplete)
- **B-grade 2024:** 28/28 extracted (공기업 11 + 준정부 17 — full lists from 이투데이 grade-specific articles)

### Match Rate to H3 Activity Embedding
- H3 dataset contains 54 unique OFFC_NM (supervising ministries)
- ALIO `supervising_ministry` maps to H3 OFFC_NM: **102/105 rows = 97.1%**
- The 3 unmatched rows: 한국산업단지공단 (ministry unlisted), 국토교통과학기술진흥원 (ministry unlisted), 한국석유관리원 (ministry unlisted)
- **Key linkage:** ALIO agency → supervising_ministry → H3 OFFC_NM → H3 budget cycle behaviors

---

## Dataset 2: 재정사업 자율평가 (`v3_micro_eval_재정사업.csv`)

### Source
Partially extracted from: evaluation.go.kr `summary.do?menu_id=83&eval_se_cd=2` (2019 R&D data only — data rendered as PNG images for most rows)

### Field Definitions
| Field | Description |
|-------|-------------|
| `project_name` | 세부사업명 (detailed project name) |
| `ministry` | 소관 부처 |
| `year` | 회계연도 |
| `grade` | S3=우수, S2=보통, S1=미흡 (mapped) |
| `grade_kor` | 우수/보통/미흡 |
| `budget_100m` | 예산 (억원) |
| `source` | Source URL |
| `notes` | Category (R&D, 일반재정, etc.) |

### Rows Collected
- **Total rows: 6** (2019 R&D sector only)

### Coverage Limits
**CRITICAL:** The main data source (evaluation.go.kr) renders fiscal project evaluation tables as PNG images embedded in the HTML, not as text. WebFetch cannot parse image-embedded text. The full dataset exists:
- 2019: 1,189 projects (230 우수, 770 보통, 189 미흡)
- 2022+: complete data exists at evaluation.go.kr (dynamic page, data behind AJAX)
- 보건복지부 PDF: 2016–2024 annual PDFs available but all binary-compressed

**For offline access:** Download from:
- `https://www.data.go.kr/data/15047853/fileData.do` — 기획재정부 소관별 재정사업 자율평가 보고서 (requires login/download)
- `https://www.evaluation.go.kr/web/page.do?menu_id=125` — direct portal
- `https://www.openfiscaldata.go.kr/op/ko/br/UOPKOBRA03` — 열린재정 재정사업평가결과 (AJAX-rendered, needs browser)

---

## Match Rate to Existing 1,557 Activities

### ALIO → H3 linkage strategy
ALIO agencies are public corporations, not budget line items. Direct name-matching to ACTV_NM (1,397 unique) or PGM_NM (433 unique) yields 0 exact matches.

**Indirect linkage (recommended for paper):**
- ALIO agency → supervising_ministry (OFFC_NM) matching: **97.1% matched** (102/105)
- This enables aggregating ALIO evaluation grades at the ministry level (OFFC_NM)
- Then correlating with H3 budget cycle features at the same ministry level
- Example: 산업통상자원부 supervises ~30 ALIO agencies → compare ministry-level ALIO grade trend with H3 fiscal cycle behavior patterns

### 재정사업 자율평가 → H3 linkage strategy
- Direct PGM_NM match possible for programs that appear in both systems
- Project-level grade → OFFC_NM → H3 activity embedding cluster
- Currently 6 rows insufficient for statistical use

---

## Suggested Usage in Paper

### H6 / Outcomes Section
**ALIO 경영평가 grades** directly measure public institution performance — the final output that fiscal budget cycle behavior (Goodharting) should predict. Use as:
- Cross-sectional: correlate ministry-level ALIO grade distribution with ministry-level Goodhart score (H6 ministry outcome)
- Panel: track ALIO grade change (2022→2024) against H3 archetype assignment change
- Robustness check: replace IMD/Gini macro index with ALIO grade as outcome variable in H8 archetype-outcome regression

### H3 / Typology Validation
ALIO grade × institution_type can validate whether specific clusters (e.g., Cluster 1 = year-end spike) correspond to lower ALIO grades.

### Paper Framing (suggested text)
> "To address reviewer concerns about macro-level outcome measures, we supplement with institution-level management evaluation grades (경영평가 등급, S–E) from Korea's public institution disclosure system (알리오). This provides a directly measurable project-level performance outcome for 65 of 87 evaluated public corporations and quasi-governmental agencies in 2024 (source: Ministry of Economy and Finance press release, 2025-06-20), linked to their supervising ministries in our existing dataset (97.1% match rate)."

---

## Files
- `data/external/v3_micro_eval_alio.csv` — 105 rows, 2022-2024, ALIO management evaluation grades
- `data/external/v3_micro_eval_재정사업.csv` — 6 rows (stub), 2019 R&D fiscal project grades
- `data/external/v3_raw/url_log.txt` — complete URL access log with status notes

## Recommended Next Step
For full coverage of 재정사업 자율평가 (Target 1):
1. Access `evaluation.go.kr` in a browser and use browser developer tools to capture AJAX responses
2. Or use Selenium/Playwright to scrape the dynamically-rendered table at `summary.do?menu_id=83&eval_se_cd=2`
3. Target: 1,000+ project rows from 2018–2023 covering 54 ministries
