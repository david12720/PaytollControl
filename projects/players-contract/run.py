"""Players Contract — CLI entry point."""
import argparse
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).parent / "src"))


def _resolve_path(path: Path) -> Path:
    if path.exists():
        return path
    parent = path.parent
    if not parent.exists():
        return path
    target = Counter(path.name)
    matches = [c for c in parent.iterdir() if c.is_file() and Counter(c.name) == target]
    if len(matches) == 1:
        print(f"[path] RTL-reordered filename recovered: {path.name!r} -> {matches[0].name!r}")
        return matches[0]
    return path


def cmd_run(args: argparse.Namespace) -> None:
    from pdf_pipeline.core.feature_registry import FeatureRegistry
    from pdf_pipeline.core.file_key import build_file_key
    from players_contract.factories.factory import bootstrap, create_pipeline

    work_dir = args.work_dir.resolve()
    bootstrap(work_dir, enable_ocr=args.ocr)

    if args.list_features:
        print("Registered features:", ", ".join(FeatureRegistry.list_features()))
        return

    input_files = [_resolve_path(p) for p in args.input_files]
    file_key = build_file_key(args.feature, input_files)
    output = args.output or (work_dir / "output" / f"{file_key}.json")
    pipeline = create_pipeline(args.feature, work_dir)
    pipeline.run(input_files, output)


def cmd_history(args: argparse.Namespace) -> None:
    from pdf_pipeline.config.settings import COST_LOG_FILE_NAME
    from pdf_pipeline.implementations.csv_cost_logger import CsvCostLogger

    work_dir = args.work_dir.resolve()
    logger = CsvCostLogger(work_dir / COST_LOG_FILE_NAME)
    logger.history(last=args.last)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Players Contract — extract salary data from IFA player contracts.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run a feature pipeline.")
    run_parser.add_argument("feature", help="Feature name (e.g., 'contract_salary').")
    run_parser.add_argument("input_files", nargs="+", type=Path, help="Input PDF file(s).")
    run_parser.add_argument("-o", "--output", type=Path, default=None, help="Output JSON path.")
    run_parser.add_argument("-w", "--work-dir", type=Path, default=Path("."), help="Working directory.")
    run_parser.add_argument("--ocr", action="store_true", default=False, help="Enable Cloud Vision OCR for handwriting.")
    run_parser.add_argument("--list-features", action="store_true", help="List registered features and exit.")
    run_parser.set_defaults(func=cmd_run)

    hist_parser = subparsers.add_parser("history", help="Show API cost history.")
    hist_parser.add_argument("-n", "--last", type=int, default=None, help="Show only last N entries.")
    hist_parser.add_argument("-w", "--work-dir", type=Path, default=Path("."), help="Working directory.")
    hist_parser.set_defaults(func=cmd_history)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
