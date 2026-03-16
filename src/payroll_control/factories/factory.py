import os
from pathlib import Path

from ..abstractions.file_preparator import PreparationPipeline
from ..config.settings import CACHE_DIR_NAME, COST_LOG_FILE_NAME, GEMINI_MODEL, STATUS_FILE_NAME
from ..core.feature_registry import FeatureRegistry
from ..core.pipeline import FeaturePipeline
from ..features.placeholder.register import register as register_placeholder
from ..implementations.csv_cost_logger import CsvCostLogger
from ..implementations.file_cache_manager import FileCacheManager
from ..implementations.gemini_model import GeminiModel
from ..implementations.json_status_tracker import JsonStatusTracker
from ..implementations.page_rotator import PageRotator
from ..implementations.pdf_to_image_converter import PdfToImageConverter
from ..implementations.xlwings_mapper import XlwingsMapper


def bootstrap(work_dir: Path) -> None:
    """Create shared infrastructure and register all features."""
    cost_logger = CsvCostLogger(work_dir / COST_LOG_FILE_NAME)

    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY environment variable is not set.")

    llm = GeminiModel(api_key=api_key, model=GEMINI_MODEL, cost_logger=cost_logger)
    base_mapper = XlwingsMapper()

    register_placeholder(language_model=llm, base_mapper=base_mapper)


def create_pipeline(feature_name: str, work_dir: Path) -> FeaturePipeline:
    feature = FeatureRegistry.get(feature_name)

    converter = PdfToImageConverter()
    rotator = PageRotator()
    preparation = PreparationPipeline(converter=converter, steps=[rotator])

    cache = FileCacheManager(work_dir / CACHE_DIR_NAME / feature_name)
    status = JsonStatusTracker(work_dir / STATUS_FILE_NAME)

    return FeaturePipeline(
        feature=feature,
        preparation=preparation,
        cache=cache,
        status=status,
    )
