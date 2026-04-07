# Arye — Document Data Extraction

Extract structured data from scanned documents (PDF/PNG) and Excel files using LLMs. The system converts documents to images, preprocesses them for optimal OCR/LLM accuracy, sends them to an LLM in chunks, and returns structured JSON.

## Monorepo Structure

| Path | Description |
|------|-------------|
| [`libs/pdf-pipeline/`](libs/pdf-pipeline/) | Generic PDF-to-JSON extraction pipeline (shared library). Domain-agnostic — handles PDF rendering, image preprocessing, LLM communication, and caching. |
| [`projects/payroll-control/`](projects/payroll-control/) | Payroll document processing application. Extracts attendance, payslips, pension, and employment contract data. |
| [`projects/players-contract/`](projects/players-contract/) | Player contract salary extraction from IFA contracts. |

## Quick Start

```bash
# Install all packages (editable, for development)
pip install -e libs/pdf-pipeline
pip install -e projects/payroll-control
pip install -e projects/players-contract

# Set your API key
export GEMINI_API_KEY=your_key_here

# Run a feature
cd projects/payroll-control
python run.py run attendance scanned_doc.pdf -o result.json

cd projects/players-contract
python run.py run contract_salary player_contract.pdf -o result.json

# Run tests
cd libs/pdf-pipeline && python -m pytest tests/ -v
cd projects/payroll-control && python -m pytest tests/ -v
cd projects/players-contract && python -m pytest tests/ -v
```

## How It Works

1. **PDF to images** — pages are rendered to PNG at 300 DPI
2. **Preprocessing** — rotation correction, deskew, line removal, contrast enhancement
3. **Chunking** — images are grouped into 40-page chunks
4. **LLM extraction** — each chunk is sent to the LLM with a domain-specific prompt
5. **Post-processing** — raw LLM output is parsed into structured JSON

For architecture details, see each sub-project's `CONTEXT.md`.
