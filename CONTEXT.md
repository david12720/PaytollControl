# PaytollControl — Architecture Decisions

## Why this architecture?

The project processes multiple document types ("features") that share the same pipeline but differ in data fields, prompts, and Excel mappings. The architecture ensures adding a new feature requires only adding a new subpackage — zero changes to existing code (Open/Closed Principle).

## Key decisions

### 1. ABCs over duck typing
Every swappable component has an explicit ABC. This makes contracts visible, enables IDE support, and catches integration errors early.

### 2. Feature as subpackage
Each feature is a self-contained directory with 5 files. This colocation makes features easy to find, understand, and delete.

### 3. Dependency Inversion
- `core/` and `features/` depend only on `abstractions/`
- `implementations/` depend on `abstractions/` + external libraries
- `factories/` is the only place that knows about concrete classes

### 4. xlwings over openpyxl
xlwings uses Excel's COM engine — preserves all existing styles, charts, and formatting. Requires Excel installed (Windows only for now).

### 5. File-based cache and status
Simple JSON/text files for cache and status. No database needed. Enables resume capability — if a run crashes, re-running skips completed stages.

## Extension guide

### Adding a new LLM provider
1. Create `implementations/new_model.py` implementing `LanguageModel`
2. Update `factories/factory.py` to use it (config-driven)

### Adding a new preparation step
1. Create `implementations/new_step.py` implementing `PreparationStep`
2. Add it to the steps list in `factories/factory.py`

### Adding a new feature
See CLAUDE.md for the 5-file recipe.

## Reference
Architecture ported from the tamtzit_rishu project's proven patterns (LanguageModel ABC, ExcelProcessor ABC, CostLogger, retry logic).
