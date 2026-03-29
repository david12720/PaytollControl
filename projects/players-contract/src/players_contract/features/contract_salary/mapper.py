from pathlib import Path

from pdf_pipeline.abstractions.excel_mapper import ExcelMapper


class ContractSalaryMapper(ExcelMapper):
    def write(self, records: list[dict], output_path: Path) -> Path:
        return output_path.with_suffix(".json")
