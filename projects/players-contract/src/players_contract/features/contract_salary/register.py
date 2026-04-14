from pathlib import Path

from pdf_pipeline.abstractions.excel_mapper import ExcelMapper
from pdf_pipeline.abstractions.language_model import LanguageModel
from pdf_pipeline.abstractions.ocr_engine import OcrEngine
from pdf_pipeline.core.feature_registry import FeatureConfig, FeatureRegistry
from .extractor import ContractSalaryExtractor

FEATURE_NAME = "contract_salary"


class _NullMapper(ExcelMapper):
    """Satisfies pdf_pipeline's required FeatureConfig.mapper field; never invoked.
    Real Excel export lives in players_contract.export."""

    def write(self, records: list[dict], output_path: Path) -> Path:
        return output_path


def register(
    language_model: LanguageModel,
    raw_pdf: bool = True,
    ocr_engine: OcrEngine | None = None,
    **_kwargs,
) -> None:
    extractor = ContractSalaryExtractor(language_model=language_model)
    FeatureRegistry.register(FeatureConfig(
        name=FEATURE_NAME,
        extractor=extractor,
        mapper=_NullMapper(),
        raw_pdf=raw_pdf,
        ocr_engine=ocr_engine,
    ))
