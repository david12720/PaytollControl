import os
from pathlib import Path

from pdf_pipeline.abstractions.file_preparator import PreparationPipeline
from pdf_pipeline.config.settings import (
    CACHE_DIR_NAME,
    COST_LOG_FILE_NAME,
    GEMINI_MODEL_HANDWRITING,
    STATUS_FILE_NAME,
)
from pdf_pipeline.core.feature_registry import FeatureConfig, FeatureRegistry
from pdf_pipeline.core.pipeline import FeaturePipeline
from pdf_pipeline.implementations.csv_cost_logger import CsvCostLogger
from pdf_pipeline.implementations.file_cache_manager import FileCacheManager
from pdf_pipeline.implementations.gemini_model import GeminiModel
from pdf_pipeline.implementations.image_enhancer import ImageEnhancer
from pdf_pipeline.implementations.json_status_tracker import JsonStatusTracker
from pdf_pipeline.implementations.line_remover import LineRemover
from pdf_pipeline.implementations.page_deskewer import PageDeskewer
from pdf_pipeline.implementations.page_rotator import PageRotator
from pdf_pipeline.implementations.pdf_to_image_converter import PdfToImageConverter

from ..export.contract_salary_mapper import ContractSalaryMapper
from ..export.excel_mapper import ExcelMapper
from ..features.contract_salary.register import register as register_contract_salary

_EXCEL_MAPPERS: dict[str, type[ExcelMapper]] = {
    "contract_salary": ContractSalaryMapper,
}


def create_excel_mapper(feature_name: str) -> ExcelMapper:
    if feature_name not in _EXCEL_MAPPERS:
        available = ", ".join(_EXCEL_MAPPERS.keys()) or "(none)"
        raise KeyError(f"No Excel mapper for feature '{feature_name}'. Available: {available}")
    return _EXCEL_MAPPERS[feature_name]()


def bootstrap(work_dir: Path, enable_ocr: bool = False) -> None:
    """Create shared infrastructure and register all features."""
    cost_logger = CsvCostLogger(work_dir / COST_LOG_FILE_NAME)
    fallback_dir = work_dir / CACHE_DIR_NAME / "fallback"

    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY environment variable is not set.")

    llm = GeminiModel(
        api_key=api_key,
        model=GEMINI_MODEL_HANDWRITING,
        cost_logger=cost_logger,
        fallback_dir=fallback_dir,
    )

    ocr_engine = None
    if enable_ocr:
        from pdf_pipeline.implementations.cloud_vision_ocr import CloudVisionOcr
        ocr_engine = CloudVisionOcr(api_key=api_key, cost_logger=cost_logger)

    register_contract_salary(language_model=llm, ocr_engine=ocr_engine)


def _default_steps() -> list:
    return [PageRotator(), PageDeskewer(), LineRemover(), ImageEnhancer()]


def _build_preparation(feature: FeatureConfig) -> PreparationPipeline:
    converter = PdfToImageConverter()
    steps = feature.preparation_steps if feature.preparation_steps is not None else _default_steps()
    return PreparationPipeline(converter=converter, steps=steps)


def create_pipeline(feature_name: str, work_dir: Path) -> FeaturePipeline:
    feature = FeatureRegistry.get(feature_name)
    cache = FileCacheManager(work_dir / CACHE_DIR_NAME / feature_name)
    status = JsonStatusTracker(work_dir / STATUS_FILE_NAME)
    preparation = _build_preparation(feature)
    return FeaturePipeline(
        feature=feature,
        preparation=preparation,
        cache=cache,
        status=status,
    )
