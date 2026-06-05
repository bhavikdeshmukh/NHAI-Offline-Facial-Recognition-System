"""
Benchmark scaffold for the NHAI offline face verification pipeline.

This script starts with file-size and stage-timing helpers. As models are added,
we will plug in detection, liveness, and recognition timings here.
"""

from __future__ import annotations

import argparse
import csv
import time
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def timed_stage(stage_name: str, rows: list[dict]):
    start = time.perf_counter()
    yield
    elapsed_ms = (time.perf_counter() - start) * 1000
    rows.append({"stage": stage_name, "elapsed_ms": round(elapsed_ms, 3)})


def file_size_mb(path: Path) -> float:
    return round(path.stat().st_size / (1024 * 1024), 3)


def collect_model_sizes(model_dir: Path):
    model_extensions = {".tflite", ".onnx", ".pt", ".pth"}
    rows = []
    if not model_dir.exists():
        return rows

    for path in sorted(model_dir.rglob("*")):
        if path.suffix.lower() in model_extensions:
            rows.append({"model": str(path), "size_mb": file_size_mb(path)})
    return rows


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description="Benchmark model sizes and pipeline stages.")
    parser.add_argument("--models", default="models", help="Directory containing model files")
    parser.add_argument("--output", default="benchmarks/results", help="Output directory")
    args = parser.parse_args()

    output_dir = Path(args.output)
    model_rows = collect_model_sizes(Path(args.models))
    timing_rows = []

    with timed_stage("benchmark_scaffold", timing_rows):
        time.sleep(0.001)

    write_csv(output_dir / "model_sizes.csv", model_rows, ["model", "size_mb"])
    write_csv(output_dir / "stage_timings.csv", timing_rows, ["stage", "elapsed_ms"])

    print(f"Wrote {output_dir / 'model_sizes.csv'}")
    print(f"Wrote {output_dir / 'stage_timings.csv'}")
    if model_rows:
        total_size = sum(row["size_mb"] for row in model_rows)
        print(f"Total detected model size: {total_size:.3f} MB")
    else:
        print("No model files found yet. Add .tflite or .onnx files under models/.")


if __name__ == "__main__":
    main()

