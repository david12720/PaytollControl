import json
import re

from ..abstractions.cache_manager import CacheManager
from ..abstractions.language_model import LanguageModel
from ..abstractions.schema_detector import ColumnMapping, SchemaDetector

CACHE_KEY = "schema"


class LlmSchemaDetector(SchemaDetector):
    def __init__(self, language_model: LanguageModel, prompt: str, cache: CacheManager):
        self._llm = language_model
        self._prompt = prompt
        self._cache = cache

    def detect(self, headers_text: str) -> ColumnMapping:
        cached = self._load_cached()
        if cached is not None:
            print("[schema] Loaded column mapping from cache.")
            return cached

        raw = self._llm.extract_from_text(headers_text, self._prompt)
        self._cache.save_raw(CACHE_KEY, raw)
        mapping = self._parse_response(raw)
        self._cache.save_json(CACHE_KEY, [self._mapping_to_dict(mapping)])
        print(f"[schema] Detected columns: date={mapping.date_column}, "
              f"from={mapping.from_time_column}, to={mapping.to_time_column}, "
              f"header_row={mapping.header_row}, data_start={mapping.data_start_row}")
        return mapping

    def _load_cached(self) -> ColumnMapping | None:
        data = self._cache.load_json(CACHE_KEY)
        if data is None:
            return None
        entry = data[0]
        return ColumnMapping(
            date_column=entry["date_column"],
            from_time_column=entry["from_time_column"],
            to_time_column=entry["to_time_column"],
            header_row=entry["header_row"],
            data_start_row=entry["data_start_row"],
        )

    def _parse_response(self, raw_text: str) -> ColumnMapping:
        cleaned = self._extract_json_text(raw_text)
        data = json.loads(cleaned)
        return ColumnMapping(
            date_column=str(data["date_column"]),
            from_time_column=str(data["from_time_column"]),
            to_time_column=str(data["to_time_column"]),
            header_row=int(data["header_row"]),
            data_start_row=int(data["data_start_row"]),
        )

    def _extract_json_text(self, raw_text: str) -> str:
        fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw_text)
        if fence_match:
            return fence_match.group(1).strip()
        brace_match = re.search(r"(\{[\s\S]*\})", raw_text)
        if brace_match:
            return brace_match.group(1).strip()
        raise ValueError(f"Could not find JSON in LLM response: {raw_text[:200]}")

    def _mapping_to_dict(self, mapping: ColumnMapping) -> dict:
        return {
            "date_column": mapping.date_column,
            "from_time_column": mapping.from_time_column,
            "to_time_column": mapping.to_time_column,
            "header_row": mapping.header_row,
            "data_start_row": mapping.data_start_row,
        }
