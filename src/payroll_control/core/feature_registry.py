from dataclasses import dataclass

from ..abstractions.data_extractor import DataExtractor
from ..abstractions.excel_mapper import ExcelMapper


@dataclass(frozen=True)
class FeatureConfig:
    name: str
    extractor: DataExtractor
    mapper: ExcelMapper


class FeatureRegistry:
    _features: dict[str, FeatureConfig] = {}

    @classmethod
    def register(cls, config: FeatureConfig) -> None:
        cls._features[config.name] = config

    @classmethod
    def get(cls, name: str) -> FeatureConfig:
        if name not in cls._features:
            available = ", ".join(cls._features.keys()) or "(none)"
            raise KeyError(f"Feature '{name}' not registered. Available: {available}")
        return cls._features[name]

    @classmethod
    def list_features(cls) -> list[str]:
        return list(cls._features.keys())

    @classmethod
    def clear(cls) -> None:
        cls._features.clear()
