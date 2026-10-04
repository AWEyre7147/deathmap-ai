"""Command-line entry point for bounded DeathMap-AI metadata evaluations."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from deathmap_ai.orcs import load_access_key, run_metadata_probe


def build_parser() -> argparse.ArgumentParser:
    """Define explicit inputs so credentials and output locations are never guessed."""

    parser = argparse.ArgumentParser(description="Run the metadata-only ORCS pilot.")
    parser.add_argument("--key-file", type=Path, required=True, help="Local ORCS key file.")
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("outputs/orcs/cache/probes"),
        help="Ignored directory for raw metadata and pilot outputs.",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=None,
        help="Optional total runtime budget; individual requests remain bounded.",
    )
    parser.add_argument("--review-sample-size", type=int, default=10)
    return parser


def main() -> None:
    """Load the key securely, run the probe, and print only non-secret summary data."""

    args = build_parser().parse_args()
    access_key = load_access_key(args.key_file)
    paths, summary = run_metadata_probe(
        access_key,
        args.output_root,
        timeout_seconds=args.timeout_seconds,
        review_sample_size=args.review_sample_size,
    )
    print(json.dumps({"output_directory": str(paths.run_dir), "summary": summary}, indent=2))


if __name__ == "__main__":
    main()
