# Players Contract Feature — Implementation Plan

## Goal

Extract financial compensation data from Israeli Football Association (IFA) player contracts (PDF).
**Only season 2025-2026. Exclude achievement-based bonuses (מענקים מותנים בהשגים).**

## Fields to Extract

| Field | Hebrew | Source in PDF | Notes |
|-------|--------|--------------|-------|
| `player_name` | שם השחקן | Page 14 (IFA form) | **Handwritten** |
| `player_id` | מספר ת.ז. | Page 14 (IFA form) | **Handwritten** (e.g., 325604198) |
| `team_name` | שם הקבוצה | Page 14 (IFA form) | **Handwritten** |
| `season` | עונה | Page 16, section 5 | Always "2025/26" for this task |
| `base_salary_monthly` | שכר בסיס חודשי | Section 3.1 / Section 6 | Typed. e.g., 623,250 ₪ |
| `bonuses_monthly` | בונוסים חודשיים | Section 3.1 / Section 6 | Non-achievement bonuses only |
| `global_bonus` | גמול גלובאלי | Section 6 (page 16) | Global bonus amount |
| `credit_points` | נקודות זיכוי | Compensation section | May be null if not specified |
| `housing_allowance_yearly` | שכר דירה שנתי | Section 3.1 | e.g., 360,000 ₪/year |
| `housing_allowance_monthly` | שכר דירה חודשי | Section 3.1 | Derived from yearly / num_payments |
| `car_allowance_monthly` | שכר רכב חודשי | Section 3.5 / Section 6 | e.g., 2,000 ₪/month |
| `source_file` | — | Auto-populated | File name |
| `page_in_document` | — | Auto-populated | Page number |

## PDF Structure (roy_example.pdf)

- **Pages 1-13**: Main contract body (typed Hebrew, RTL)
  - Section 3 (pages 2-3): Salary details per season (3.1=2025/26, 3.2=2026/27, 3.3=2027/28)
  - Section 3.5: Per-game bonuses with housing/car components
  - Section 3.6: Clarification that no achievement bonuses exist beyond section 3.5
- **Page 14**: IFA standard player agreement form (טופס הסכם שחקנים) — has handwritten fields
- **Pages 15-19**: IFA form continued — compensation rules, section 6 (התמורה)
- **Pages 20-25**: IFA regulations appendix (תקנון משמעת)

### Key financial data locations for 2025/26:

**Section 3.1 (page 2):**
- Total monthly salary: 623,250 ₪
- Bonuses/grants component: 69,250 ₪/month
- Housing: up to 360,000 ₪/year (9 monthly payments → 40,000/month)

**Section 3.5.1 (page 2):**
- Per-game bonus base: 3,640 ₪
- Housing+vehicle gross: 2,000 ₪/month

**Section 6 (page 16):**
- Base salary (שכר בסיס) — 80% of monthly salary
- Global bonus (גמול גלובאלי)
- Rest-day work compensation rules

## Architecture

### Project Structure

```
projects/players-contract/
├── PLAN.md                     # This file
├── CLAUDE.md                   # Project instructions
├── pyproject.toml              # Package config (depends on pdf-pipeline)
├── run.py                      # CLI entry point
├── src/
│   └── players_contract/
│       ├── __init__.py
│       ├── factories/
│       │   ├── __init__.py
│       │   └── factory.py      # bootstrap() + create_pipeline()
│       └── features/
│           ├── __init__.py
│           └── contract_salary/
│               ├── __init__.py
│               ├── model.py    # PlayerContractSalary dataclass
│               ├── prompt.py   # LLM prompt (Hebrew instructions)
│               ├── extractor.py # ContractSalaryExtractor(DataExtractor)
│               ├── mapper.py   # ContractSalaryMapper(ExcelMapper)
│               └── register.py # register() → FeatureRegistry
└── tests/
    └── unit/
        └── test_contract_salary_extractor.py
```

### Key Decisions

| Decision | Choice | Reason |
|----------|--------|--------|
| Project location | Standalone `projects/players-contract/` | Separate domain from payroll |
| Pipeline mode | `raw_pdf=True` | Contract is mostly typed, PDF mode works well |
| LLM model | `GEMINI_MODEL_HANDWRITING` | Some fields are handwritten (name, ID, team) |
| OCR | Optional (same pattern as employment_contract) | Fallback for hard-to-read handwriting |
| Season filter | In prompt instructions | Tell LLM to extract only 2025/26 data |

### Dependency Flow

```
run.py → factories/factory.py → pdf_pipeline.implementations.*
                               → pdf_pipeline.core.*
         features/             → pdf_pipeline.abstractions.* (ONLY)
```

## Implementation Steps

### Step 1: Project Scaffolding
- [x] Create `pyproject.toml` (depends on `pdf-pipeline`)
- [x] Create `__init__.py` files for all packages
- [x] Create `CLAUDE.md` with project instructions and structure map

### Step 2: Feature — contract_salary
- [x] `model.py` — `PlayerContractSalary` dataclass
- [x] `prompt.py` — Hebrew LLM prompt targeting salary/bonus/housing/car fields, excluding achievement bonuses, filtered to 2025/26 season
- [x] `extractor.py` — `ContractSalaryExtractor(DataExtractor)` using raw PDF mode
- [x] `mapper.py` — `ContractSalaryMapper(ExcelMapper)` (minimal, returns JSON path)
- [x] `register.py` — registers feature with `FeatureConfig(raw_pdf=True)`

### Step 3: Factory
- [x] `factory.py` — `bootstrap()` creates GeminiModel (handwriting), registers feature; `create_pipeline()` returns configured FeaturePipeline

### Step 4: CLI
- [x] `run.py` — argparse CLI with `run` and `history` commands (same pattern as payroll-control)

### Step 5: Tests
- [x] `test_contract_salary_extractor.py` — unit test with mock LLM response

### Step 6: Integration
- [x] Update root `CLAUDE.md` to mention `players-contract` project
- [x] Test with `roy_example.pdf` (successfully extracted)

### Post-implementation refinements
- [x] Use fictional values in prompt example to prevent LLM from parroting them
- [x] Add `max_points_for_bonus` (LLM-detected); compute `points_bonus_total` programmatically in extractor
- [x] Merge `goal_bonus`, `assist_bonus`, `penalty_bonus` into single `goal_assist_penalty_bonus`
- [x] Fix Hebrew gershayim in team names: use `״` (U+05F4) instead of straight `"`
- [x] Remove page-number references from prompt (keep descriptions generic)

## Cache & Status

To force a full re-run, delete both:
```powershell
rm cache, status.json -Recurse -Force
```
`status.json` lives in the working directory alongside `run.py` and tracks pipeline stage completion independently of the cache folder.

## Final Field Schema

| Field | Source | Notes |
|-------|--------|-------|
| `player_name` | IFA form (handwritten) | |
| `player_id` | IFA form (handwritten) | |
| `team_name` | IFA form / stamp | Use ״ for Hebrew abbreviations |
| `season` | Contract | Always "2025/26" |
| `base_salary_monthly` | Salary section | |
| `bonuses_monthly` | Salary section | Fixed only |
| `global_bonus` | Compensation section | Null if absent |
| `credit_points` | Contract | Null if absent |
| `housing_allowance_yearly` | Salary section | |
| `housing_allowance_monthly` | Salary section | |
| `car_allowance_monthly` | Salary/bonus section | |
| `points_bonus_per_point` | LLM | Per league point amount |
| `max_points_for_bonus` | LLM | Cap for points bonus calculation |
| `points_bonus_total` | Computed | `per_point × max_points` |
| `goal_assist_penalty_bonus` | Achievements section | Individual performance only |
