# Changelog

## 0.3.0 — 2026-03-22

### Added
- Excel attendance extraction pipeline: LLM detects column schema once, then rows are extracted programmatically
- New ABCs: SchemaDetector, SpreadsheetReader
- New implementations: LlmSchemaDetector (with caching), OpenpyxlReader
- ExcelPipeline orchestrator in core/ for Excel-based features
- ExcelFeatureConfig in FeatureRegistry for Excel features
- LanguageModel.extract_from_text() method for plain text LLM calls
- excel_attendance feature with Hebrew schema detection prompt
- 18 new tests (record builder, schema detector, pipeline orchestration)

## 0.2.0 — 2026-03-20

### Added
- Attendance feature: extract employee attendance records from scanned PDFs
- Image preprocessing pipeline: PageRotator (sideways detection), PageDeskewer (skew correction), ImageEnhancer (contrast/sharpness)
- Fallback response saving in GeminiModel to prevent data loss
- Non-fatal cost logging (continues on failure)
- Debug page saving for visual inspection of preprocessed images
- Architecture boundary tests to enforce library-extractable core pipeline

### Changed
- Pipeline outputs JSON instead of Excel (Excel mapping is a future step)
- Upgraded to gemini-3.1-pro-preview model
- PageRotator rewritten with variance-based sideways content detection

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
