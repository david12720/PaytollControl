# Workspace Root

This is a monorepo workspace. **Do not work from here** — navigate to the relevant sub-project:

- **`libs/pdf-pipeline/`** — Generic PDF-to-JSON extraction pipeline via LLM (shared library)
- **`projects/payroll-control/`** — Payroll document processing application (consumes pdf-pipeline)
- **`projects/players-contract/`** — Player contract salary extraction from IFA contracts (consumes pdf-pipeline)

Each sub-project has its own `CLAUDE.md` with architecture details, commands, and conventions.

## Workspace Structure

```
Arye/
├── libs/
│   └── pdf-pipeline/          # Shared library (package: pdf_pipeline)
│       ├── src/pdf_pipeline/
│       │   ├── abstractions/  # ABCs (LanguageModel, DataExtractor, ...)
│       │   ├── core/          # Pipeline orchestration (FeaturePipeline, ExcelPipeline)
│       │   ├── config/        # Settings, pricing
│       │   └── implementations/ # Concrete classes (Gemini, image processing, ...)
│       └── tests/
├── projects/
│   ├── payroll-control/       # Payroll app (consumes pdf_pipeline)
│   │   ├── src/payroll_control/
│   │   │   ├── factories/     # Wires implementations to features
│   │   │   └── features/      # Domain features (attendance, payslip, pension, ...)
│   │   ├── tests/
│   │   └── run.py             # CLI entry point
│   └── players-contract/      # Player contract salary extraction (consumes pdf_pipeline)
│       ├── src/players_contract/
│       │   ├── factories/     # Wires implementations to features
│       │   └── features/      # Domain features (contract_salary)
│       ├── tests/
│       └── run.py             # CLI entry point
└── CLAUDE.md                  # This file
```

## Quick Start

```bash
# Install all packages (editable, for development)
pip install -e libs/pdf-pipeline
pip install -e projects/payroll-control
pip install -e projects/players-contract

# Run library tests
cd libs/pdf-pipeline && python -m pytest tests/ -v

# Run payroll-control tests
cd projects/payroll-control && python -m pytest tests/ -v

# Run players-contract tests
cd projects/players-contract && python -m pytest tests/ -v
```

## AI Navigation Guide

### Key Files (Fast-Track)

| File | Role |
|:-----|:-----|
| `libs/pdf-pipeline/src/pdf_pipeline/abstractions/` | All contracts — start here to understand the system |
| `libs/pdf-pipeline/src/pdf_pipeline/core/pipeline.py` | Main orchestration loop |
| `projects/payroll-control/src/payroll_control/factories/factory.py` | Wires payroll-control parts together |
| `projects/payroll-control/run.py` | Payroll-control CLI entry point |
| `projects/players-contract/src/players_contract/factories/factory.py` | Wires players-contract parts together |
| `projects/players-contract/run.py` | Players-contract CLI entry point |

### Token-Saving Rules

- **DO NOT** read `libs/pdf-pipeline/src/pdf_pipeline/implementations/` unless debugging a specific image processing or API issue
- **DO NOT** read more than one `features/` subfolder unless comparing logic between two document types
- **PREFER** reading `abstractions/` over `core/` to understand what the system can do
- **TRUST** the `factory.py` for understanding how the system is currently configured
- **IGNORE** `__pycache__`, `.pytest_cache`, and `tests/` unless explicitly verifying a fix
