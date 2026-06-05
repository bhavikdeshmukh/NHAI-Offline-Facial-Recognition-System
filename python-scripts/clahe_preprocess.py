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
import csv
import time
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def _tile_lut(tile: np.ndarray, clip_limit: float) -> np.ndarray:
    histogram = np.bincount(tile.ravel(), minlength=256).astype(np.float64)
    clip_threshold = max(1.0, clip_limit * tile.size / 256)
    excess = np.maximum(histogram - clip_threshold, 0).sum()
    histogram = np.minimum(histogram, clip_threshold)
    histogram += excess / 256
    cdf = histogram.cumsum()
    cdf = (cdf - cdf.min()) / max(cdf.max() - cdf.min(), 1)
    return np.clip(cdf * 255, 0, 255).astype(np.uint8)


def apply_clahe_luminance(
    image: Image.Image,
    clip_limit: float = 2.0,
    tile_grid_size: int = 8,
) -> Image.Image:
    """Apply CLAHE to the luminance channel while preserving color."""
    ycbcr = image.convert("YCbCr")
    y_channel, cb_channel, cr_channel = ycbcr.split()
    luminance = np.array(y_channel, dtype=np.uint8)
    height, width = luminance.shape
    tile_h = int(np.ceil(height / tile_grid_size))
    tile_w = int(np.ceil(width / tile_grid_size))

    luts = []
    for tile_y in range(tile_grid_size):
        row = []
        y0 = tile_y * tile_h
        y1 = min((tile_y + 1) * tile_h, height)
        for tile_x in range(tile_grid_size):
            x0 = tile_x * tile_w
            x1 = min((tile_x + 1) * tile_w, width)
            row.append(_tile_lut(luminance[y0:y1, x0:x1], clip_limit))
        luts.append(row)
    lut_grid = np.array(luts)

    y_positions = np.arange(height, dtype=np.float32) / tile_h
    x_positions = np.arange(width, dtype=np.float32) / tile_w
    y_low = np.floor(y_positions).astype(np.int32)
    x_low = np.floor(x_positions).astype(np.int32)
    y_high = np.clip(y_low + 1, 0, tile_grid_size - 1)
    x_high = np.clip(x_low + 1, 0, tile_grid_size - 1)
    y_low = np.clip(y_low, 0, tile_grid_size - 1)
    x_low = np.clip(x_low, 0, tile_grid_size - 1)
    y_weight = (y_positions - y_low).reshape(height, 1)
    x_weight = (x_positions - x_low).reshape(1, width)

    top_left = lut_grid[y_low[:, None], x_low[None, :], luminance]
    top_right = lut_grid[y_low[:, None], x_high[None, :], luminance]
    bottom_left = lut_grid[y_high[:, None], x_low[None, :], luminance]
    bottom_right = lut_grid[y_high[:, None], x_high[None, :], luminance]

    top = (1 - x_weight) * top_left + x_weight * top_right
    bottom = (1 - x_weight) * bottom_left + x_weight * bottom_right
    enhanced = ((1 - y_weight) * top + y_weight * bottom).astype(np.uint8)

    enhanced_y = Image.fromarray(enhanced, mode="L")
    return Image.merge("YCbCr", (enhanced_y, cb_channel, cr_channel)).convert("RGB")


def iter_images(input_path: Path):
    if input_path.is_file() and input_path.suffix.lower() in IMAGE_EXTENSIONS:
        yield input_path
        return

    if input_path.is_dir():
        for path in sorted(input_path.rglob("*")):
            if path.suffix.lower() in IMAGE_EXTENSIONS:
                yield path


def save_side_by_side(original: Image.Image, enhanced: Image.Image, output_path: Path):
    width, height = original.size
    canvas = Image.new("RGB", (width * 2, height + 34), "white")
    canvas.paste(original.convert("RGB"), (0, 34))
    canvas.paste(enhanced.convert("RGB"), (width, 34))
    draw = ImageDraw.Draw(canvas)
    draw.text((12, 10), "Before", fill=(20, 33, 46))
    draw.text((width + 12, 10), "After CLAHE", fill=(20, 33, 46))
    canvas.save(output_path)


def process_image(image_path: Path, output_dir: Path, clip_limit: float, tile_grid_size: int):
    try:
        image = Image.open(image_path).convert("RGB")
    except OSError:
        return None

    start = time.perf_counter()
    enhanced = apply_clahe_luminance(
        image,
        clip_limit=clip_limit,
        tile_grid_size=tile_grid_size,
    )
    elapsed_ms = (time.perf_counter() - start) * 1000

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{image_path.stem}_clahe.png"
    comparison_path = output_dir / f"{image_path.stem}_comparison.png"
    enhanced.save(output_path)
    save_side_by_side(image, enhanced, comparison_path)

    return {
        "input": str(image_path),
        "output": str(output_path),
        "comparison": str(comparison_path),
        "elapsed_ms": round(elapsed_ms, 3),
    }


def main():
    parser = argparse.ArgumentParser(description="Apply CLAHE to image files.")
    parser.add_argument("--input", required=True, help="Input image or directory")
    parser.add_argument("--output", required=True, help="Output directory")
    parser.add_argument("--csv", help="Optional CSV path for timing results")
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

    if args.csv:
        csv_path = Path(args.csv)
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        with csv_path.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(
                csv_file,
                fieldnames=["input", "output", "comparison", "elapsed_ms"],
            )
            writer.writeheader()
            writer.writerows(results)
        print(f"Wrote timing CSV: {csv_path}")


if __name__ == "__main__":
    main()
