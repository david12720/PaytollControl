"""PaytollControl — CLI entry point."""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from payroll_control.core.feature_registry import FeatureRegistry
from payroll_control.factories.factory import bootstrap, create_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(
        description="PaytollControl — extract payroll data from scanned documents and map to Excel.",
    )
    parser.add_argument("feature", help="Feature name to run (e.g., 'placeholder').")
    parser.add_argument("input_files", nargs="+", type=Path, help="Input PDF/PNG file(s).")
    parser.add_argument("-o", "--output", type=Path, default=None, help="Output Excel path.")
    parser.add_argument("-w", "--work-dir", type=Path, default=Path("."), help="Working directory for cache/status/logs.")
    parser.add_argument("--list-features", action="store_true", help="List registered features and exit.")

    args = parser.parse_args()

    work_dir = args.work_dir.resolve()
    bootstrap(work_dir)

    if args.list_features:
        print("Registered features:", ", ".join(FeatureRegistry.list_features()))
        return

    output = args.output or (work_dir / "output" / f"{args.feature}_output.xlsx")

    pipeline = create_pipeline(args.feature, work_dir)
    pipeline.run(args.input_files, output)


if __name__ == "__main__":
    main()
