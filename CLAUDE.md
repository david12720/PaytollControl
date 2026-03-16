# PaytollControl — Claude Code Instructions

## Project Overview

Payroll control tool: extract data from scanned documents (PDF/PNG) via LLM, structure it, and map to Excel. Built with a generic pipeline — new document types ("features") are added without changing existing code.

## Architecture

- **abstractions/**: 7 ABCs defining all contracts
- **core/**: Business logic (FeaturePipeline, FeatureRegistry) — imports only from abstractions/
- **implementations/**: Concrete classes (Gemini, xlwings, file cache, etc.)
- **features/<name>/**: Self-contained feature subpackages (prompt, model, extractor, mapper, register)
- **factories/**: Wires everything together
- **config/**: Settings and pricing constants

## Dependency Rule

```
run.py → factories/ → implementations/ → abstractions/
                     → core/ → abstractions/
         features/ → abstractions/ (+ core/feature_registry)
```

**core/ and features/ NEVER import from implementations/**

## Adding a New Feature

Create `src/payroll_control/features/<name>/` with:
1. `prompt.py` — LLM prompt
2. `model.py` — dataclass for extracted fields
3. `extractor.py` — DataExtractor subclass (depends on abstractions only)
4. `mapper.py` — ExcelMapper subclass (depends on abstractions only)
5. `register.py` — registers with FeatureRegistry

Then add the registration call in `factories/factory.py:bootstrap()`.

## Commands

- Run tests: `python -m pytest tests/ -v`
- CLI help: `python run.py --help`
- Run a feature: `python run.py <feature_name> <input_files...> [-o output.xlsx]`

## Conventions

- All dependencies are injected — never instantiate concrete classes in business logic
- Tests use mocks/fakes — no real API calls
- Config constants live in `config/settings.py` and `config/pricing.py`
