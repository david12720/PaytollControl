# Payroll Control — Architecture Decisions

For shared infrastructure decisions (preprocessing pipeline, chunk size, caching, fallback saving, dual pipeline architecture, OCR), see [`libs/pdf-pipeline/CONTEXT.md`](../../libs/pdf-pipeline/CONTEXT.md).

## 1. Why this architecture?

The project processes multiple document types ("features") that share the same pipeline but differ in data fields, prompts, and Excel mappings. The core pipeline lives in `libs/pdf-pipeline/` as a shared library; this project consumes it and adds domain-specific features on top. Adding a new feature requires only adding a new subpackage — zero changes to existing code (Open/Closed Principle).

## 2. Feature as subpackage

Each feature is a self-contained directory with 5 files (prompt, model, extractor, mapper, register). This colocation makes features easy to find, understand, and delete.

## 3. Dependency inversion (application layer)

The library owns abstractions, implementations, config, and pipeline orchestration. This project owns only `features/` and `factories/`:

- `features/` depend only on `pdf_pipeline.abstractions` — never on concrete implementations
- `factories/` is the only place that knows about concrete classes from `pdf_pipeline.implementations`
- `run.py` wires everything together via factories

```
run.py -> factories/ -> pdf_pipeline.implementations.*
                      -> pdf_pipeline.core.*
          features/  -> pdf_pipeline.abstractions.* (only abstractions)
```

## 4. Extension guide

### Adding a new feature (this project)

Create `src/payroll_control/features/<name>/` with the 5-file recipe (see CLAUDE.md). Register it in `factories/factory.py:bootstrap()`. No changes to the library needed.

### Adding a new LLM provider or preparation step (library-level)

These live in `libs/pdf-pipeline/`. See the library's [CONTEXT.md](../../libs/pdf-pipeline/CONTEXT.md) extension guide.

## 5. Reference

Architecture ported from the tamtzit_rishu project's proven patterns (LanguageModel ABC, ExcelProcessor ABC, CostLogger, retry logic).
