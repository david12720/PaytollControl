import json
from pathlib import Path

from ..abstractions.cache_manager import CacheManager
from ..abstractions.schema_detector import SchemaDetector
from ..abstractions.spreadsheet_reader import SpreadsheetReader
from ..abstractions.status_tracker import StatusTracker
from .feature_registry import ExcelFeatureConfig

HEADER_ROWS_TO_READ = 5


class ExcelPipeline:
    def __init__(
        self,
        feature: ExcelFeatureConfig,
        reader: SpreadsheetReader,
        schema_detector: SchemaDetector,
        cache: CacheManager,
        status: StatusTracker,
    ):
        self._feature = feature
        self._reader = reader
        self._schema_detector = schema_detector
        self._cache = cache
        self._status = status

    def run(self, input_files: list[Path], output_path: Path) -> Path:
        file_key = self._feature.name

        if self._status.is_complete(file_key):
            print(f"[{file_key}] All stages complete -- skipping.")
            return output_path

        cached = self._cache.load_json(file_key)
        if cached is not None:
            print(f"[{file_key}] Loaded results from JSON cache.")
            self._status.set_status(file_key, "extract", "success")
            self._status.set_status(file_key, "cache", "success")
            return self._write_json(cached, output_path, file_key)

        first_file = input_files[0]
        first_sheet = self._reader.get_sheet_names(first_file)[0]
        headers_text = self._format_headers(first_file, first_sheet)
        mapping = self._schema_detector.detect(headers_text)
        self._status.set_status(file_key, "prepare", "success")

        all_records: dict[str, list[dict]] = {}
        for file_path in input_files:
            file_records: list[dict] = []
            for sheet in self._reader.get_sheet_names(file_path):
                rows = self._reader.read_data_rows(file_path, sheet, mapping.data_start_row)
                records = self._feature.record_builder(rows, mapping, sheet)
                file_records.extend(records)
            all_records[file_path.name] = file_records

        self._cache.save_json(file_key, all_records)
        self._status.set_status(file_key, "extract", "success")
        self._status.set_status(file_key, "cache", "success")
        total = sum(len(v) for v in all_records.values())
        print(f"[{file_key}] Extracted {total} record(s) from {len(input_files)} file(s).")
        return self._write_json(all_records, output_path, file_key)

    def _format_headers(self, path: Path, sheet: str) -> str:
        rows = self._reader.read_header_rows(path, sheet, max_rows=HEADER_ROWS_TO_READ)
        lines: list[str] = []
        for row_idx, row in enumerate(rows, start=1):
            cells = [str(cell) if cell is not None else "" for cell in row]
            lines.append(f"Row {row_idx}: {' | '.join(cells)}")
        return "\n".join(lines)

    def _write_json(self, data: dict | list, output_path: Path, file_key: str) -> Path:
        json_path = output_path.with_suffix(".json")
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"[{file_key}] Saved output -> {json_path}")
        self._status.set_status(file_key, "json_output", "success")
        return json_path
