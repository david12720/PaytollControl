from pathlib import Path

from ..abstractions.cache_manager import CacheManager
from ..abstractions.file_preparator import PreparationPipeline
from ..abstractions.status_tracker import StatusTracker
from .feature_registry import FeatureConfig


class FeaturePipeline:
    def __init__(
        self,
        feature: FeatureConfig,
        preparation: PreparationPipeline,
        cache: CacheManager,
        status: StatusTracker,
    ):
        self._feature = feature
        self._preparation = preparation
        self._cache = cache
        self._status = status

    def run(self, input_files: list[Path], output_path: Path) -> Path:
        file_key = self._feature.name

        if self._status.is_complete(file_key):
            print(f"[{file_key}] All stages complete — skipping.")
            return output_path

        records = self._try_load_from_cache(file_key)
        if records is None:
            records = self._extract(input_files, file_key)

        return self._write_excel(records, output_path, file_key)

    def _try_load_from_cache(self, file_key: str) -> list[dict] | None:
        if not self._cache.has_cache(file_key):
            return None

        json_data = self._cache.load_json(file_key)
        if json_data is not None:
            print(f"[{file_key}] Loaded {len(json_data)} records from JSON cache.")
            self._status.set_status(file_key, "extract", "success")
            self._status.set_status(file_key, "cache", "success")
            return json_data

        raw = self._cache.load_raw(file_key)
        if raw is not None:
            print(f"[{file_key}] Parsing cached raw response...")
            records = self._feature.extractor.parse_cached_response(raw)
            self._cache.save_json(file_key, records)
            self._status.set_status(file_key, "extract", "success")
            self._status.set_status(file_key, "cache", "success")
            return records

        return None

    def _extract(self, input_files: list[Path], file_key: str) -> list[dict]:
        print(f"[{file_key}] Preparing files...")
        prepared = self._preparation.prepare(input_files)
        self._status.set_status(file_key, "prepare", "success")

        print(f"[{file_key}] Extracting data from {len(prepared)} prepared file(s)...")
        try:
            records = self._feature.extractor.extract(prepared)
            self._status.set_status(file_key, "extract", "success")
        except Exception as e:
            self._status.set_status(file_key, "extract", f"failed: {e}")
            raise

        self._cache.save_json(file_key, records)
        self._status.set_status(file_key, "cache", "success")
        print(f"[{file_key}] Cached {len(records)} record(s).")
        return records

    def _write_excel(self, records: list[dict], output_path: Path, file_key: str) -> Path:
        print(f"[{file_key}] Writing {len(records)} record(s) to Excel...")
        try:
            result_path = self._feature.mapper.write(records, output_path)
            self._status.set_status(file_key, "excel", "success")
            print(f"[{file_key}] Done → {result_path}")
            return result_path
        except Exception as e:
            self._status.set_status(file_key, "excel", f"failed: {e}")
            raise
