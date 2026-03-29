from pdf_pipeline.abstractions.language_model import LanguageModel
from pdf_pipeline.abstractions.ocr_engine import OcrEngine
from pdf_pipeline.core.feature_registry import FeatureConfig, FeatureRegistry
from .extractor import ContractSalaryExtractor
from .mapper import ContractSalaryMapper

FEATURE_NAME = "contract_salary"


def register(
    language_model: LanguageModel,
    raw_pdf: bool = True,
    ocr_engine: OcrEngine | None = None,
    **_kwargs,
) -> None:
    extractor = ContractSalaryExtractor(language_model=language_model)
    mapper = ContractSalaryMapper()
    FeatureRegistry.register(FeatureConfig(
        name=FEATURE_NAME,
        extractor=extractor,
        mapper=mapper,
        raw_pdf=raw_pdf,
        ocr_engine=ocr_engine,
    ))
