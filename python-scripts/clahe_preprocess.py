"""
CLAHE preprocessing utility for the NHAI offline face verification pipeline.

Usage:
    python clahe_preprocess.py --input path/to/image.jpg --output assets/evidence/clahe
    python clahe_preprocess.py --input path/to/folder --output assets/evidence/clahe

This is a development-time script. The final mobile app should use an optimized
native implementation, but this script lets us test parameters and collect
before/after evidence first.
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

try:
    import cv2
except ImportError as exc:
    raise SystemExit(
        "OpenCV is required. Install with: pip install opencv-python"
    ) from exc


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def apply_clahe(image, clip_limit: float = 2.0, tile_grid_size: int = 8):
    """Apply CLAHE to the luminance channel while preserving color."""
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    lightness, a_channel, b_channel = cv2.split(lab)
    clahe = cv2.createCLAHE(
        clipLimit=clip_limit,
        tileGridSize=(tile_grid_size, tile_grid_size),
    )
    enhanced_lightness = clahe.apply(lightness)
    enhanced_lab = cv2.merge((enhanced_lightness, a_channel, b_channel))
    return cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)


def iter_images(input_path: Path):
    if input_path.is_file() and input_path.suffix.lower() in IMAGE_EXTENSIONS:
        yield input_path
        return

    if input_path.is_dir():
        for path in sorted(input_path.rglob("*")):
            if path.suffix.lower() in IMAGE_EXTENSIONS:
                yield path


def process_image(image_path: Path, output_dir: Path, clip_limit: float, tile_grid_size: int):
    image = cv2.imread(str(image_path))
    if image is None:
        return None

    start = time.perf_counter()
    enhanced = apply_clahe(image, clip_limit=clip_limit, tile_grid_size=tile_grid_size)
    elapsed_ms = (time.perf_counter() - start) * 1000

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{image_path.stem}_clahe{image_path.suffix}"
    cv2.imwrite(str(output_path), enhanced)

    return {
        "input": str(image_path),
        "output": str(output_path),
        "elapsed_ms": round(elapsed_ms, 3),
    }


def main():
    parser = argparse.ArgumentParser(description="Apply CLAHE to image files.")
    parser.add_argument("--input", required=True, help="Input image or directory")
    parser.add_argument("--output", required=True, help="Output directory")
    parser.add_argument("--clip-limit", type=float, default=2.0)
    parser.add_argument("--tile-grid-size", type=int, default=8)
    args = parser.parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output)

    results = []
    for image_path in iter_images(input_path):
        result = process_image(
            image_path,
            output_dir,
            clip_limit=args.clip_limit,
            tile_grid_size=args.tile_grid_size,
        )
        if result:
            results.append(result)

    if not results:
        raise SystemExit(f"No readable images found at: {input_path}")

    for result in results:
        print(
            f"{result['input']} -> {result['output']} "
            f"({result['elapsed_ms']} ms)"
        )

    average_ms = sum(item["elapsed_ms"] for item in results) / len(results)
    print(f"Processed {len(results)} image(s). Average CLAHE time: {average_ms:.3f} ms")


if __name__ == "__main__":
    main()

