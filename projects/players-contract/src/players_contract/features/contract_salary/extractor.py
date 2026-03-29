import json
import re

from pdf_pipeline.abstractions.data_extractor import DataExtractor
from pdf_pipeline.abstractions.file_preparator import PreparedFile
from pdf_pipeline.abstractions.language_model import LanguageModel
from .prompt import PROMPT


class ContractSalaryExtractor(DataExtractor):
    def __init__(self, language_model: LanguageModel):
        self._llm = language_model

    def extract(self, prepared_files: list[PreparedFile]) -> list[dict]:
        if not prepared_files:
            return []

        if prepared_files[0].mime_type == "application/pdf":
            raw = self._llm.extract_from_pdf(prepared_files[0].data, PROMPT)
        else:
            raw = self._llm.extract_from_images(
                [pf.data for pf in prepared_files], PROMPT
            )

        record = self._parse_response(raw)
        self._compute_points_total(record)
        record["_llm_raw_text"] = raw
        record["source_file"] = prepared_files[0].source_path.name
        record["page_in_document"] = prepared_files[0].page_index + 1
        return [record]

    def parse_cached_response(self, raw_text: str) -> list[dict]:
        record = self._parse_response(raw_text)
        self._compute_points_total(record)
        record["_llm_raw_text"] = raw_text
        return [record]

    def _compute_points_total(self, record: dict) -> None:
        per_point = record.get("points_bonus_per_point")
        max_points = record.get("max_points_for_bonus")
        if per_point is not None and max_points is not None:
            record["points_bonus_total"] = per_point * max_points
        else:
            record["points_bonus_total"] = None

    def _parse_response(self, raw_text: str) -> dict:
        cleaned = self._extract_json_text(raw_text)
        parsed = json.loads(cleaned)
        if isinstance(parsed, list):
            if len(parsed) == 1:
                return parsed[0]
            raise ValueError(
                f"Expected a single JSON object, got list with {len(parsed)} items."
            )
        return parsed

    def _extract_json_text(self, raw_text: str) -> str:
        fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw_text)
        if fence_match:
            return fence_match.group(1).strip()

        brace_match = re.search(r"(\[[\s\S]*\]|\{[\s\S]*\})", raw_text)
        if brace_match:
            return brace_match.group(1).strip()

        raise ValueError(
            f"Could not find JSON in LLM response: {raw_text[:200]}"
        )
