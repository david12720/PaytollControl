# Changelog

## 0.1.0 — 2026-03-16

### Added
- Project scaffolding with SOLID architecture
- 7 ABCs: LanguageModel, FileConverter, PreparationStep, DataExtractor, ExcelMapper, CacheManager, StatusTracker, CostLogger
- Infrastructure implementations: CsvCostLogger, FileCacheManager, JsonStatusTracker
- Preparation: PdfToImageConverter, PageRotator
- GeminiModel with retry logic and cost logging
- XlwingsMapper for Excel output via COM
- Core: FeatureRegistry, FeaturePipeline with full stage tracking and resume
- Factory for dependency wiring
- Placeholder feature to prove the architecture
- CLI entry point (run.py)
- 22 tests (unit + integration), all passing
