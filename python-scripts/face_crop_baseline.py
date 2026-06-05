"""
Heuristic face crop baseline for early pipeline evidence.

This is NOT the final detector. It uses OpenCV Haar detection when available and
falls back to a simple skin-region heuristic. The final mobile detector should be
BlazeFace or SCRFD-lite.

Usage:
    python face_crop_baseline.py --input samples/private/real_faces --output assets/evidence/face_detection_real
"""

from __future__ import annotations

import argparse
import csv
import sys
import time
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from clahe_preprocess import apply_clahe_luminance


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
LOCAL_PACKAGE_DIR = Path(__file__).resolve().parents[1] / "local-python-packages"

if LOCAL_PACKAGE_DIR.exists():
    sys.path.insert(0, str(LOCAL_PACKAGE_DIR))

try:
    import cv2
except ImportError:
    cv2 = None

OPENCV_DETECTOR = None


def iter_images(input_path: Path):
    if input_path.is_file() and input_path.suffix.lower() in IMAGE_EXTENSIONS:
        yield input_path
        return

    if input_path.is_dir():
        for path in sorted(input_path.rglob("*")):
            if path.suffix.lower() in IMAGE_EXTENSIONS:
                yield path


def skin_mask(image: Image.Image, max_size: int = 640):
    scale = min(1.0, max_size / max(image.size))
    small_size = (int(image.width * scale), int(image.height * scale))
    small = image.resize(small_size).convert("YCbCr")
    array = np.array(small)
    y = array[:, :, 0]
    cb = array[:, :, 1]
    cr = array[:, :, 2]

    mask = (
        (y > 35)
        & (cb >= 77)
        & (cb <= 140)
        & (cr >= 133)
        & (cr <= 185)
    )
    return mask, scale


def connected_components(mask: np.ndarray):
    height, width = mask.shape
    visited = np.zeros_like(mask, dtype=bool)
    components = []

    for start_y in range(height):
        for start_x in range(width):
            if visited[start_y, start_x] or not mask[start_y, start_x]:
                continue

            queue = deque([(start_x, start_y)])
            visited[start_y, start_x] = True
            min_x = max_x = start_x
            min_y = max_y = start_y
            area = 0

            while queue:
                x, y = queue.popleft()
                area += 1
                min_x = min(min_x, x)
                max_x = max(max_x, x)
                min_y = min(min_y, y)
                max_y = max(max_y, y)

                for next_x, next_y in (
                    (x + 1, y),
                    (x - 1, y),
                    (x, y + 1),
                    (x, y - 1),
                ):
                    if (
                        0 <= next_x < width
                        and 0 <= next_y < height
                        and not visited[next_y, next_x]
                        and mask[next_y, next_x]
                    ):
                        visited[next_y, next_x] = True
                        queue.append((next_x, next_y))

            components.append(
                {
                    "area": area,
                    "box": (min_x, min_y, max_x + 1, max_y + 1),
                }
            )

    return components


def choose_face_box(components, image_size, scale: float):
    original_width, original_height = image_size
    scaled_width = int(original_width * scale)
    scaled_height = int(original_height * scale)
    image_area = scaled_width * scaled_height
    candidates = []

    for component in components:
        min_x, min_y, max_x, max_y = component["box"]
        width = max_x - min_x
        height = max_y - min_y
        if component["area"] < image_area * 0.01:
            continue
        if width <= 0 or height <= 0:
            continue

        aspect = width / height
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        center_bias = 1 - abs(center_x - scaled_width / 2) / (scaled_width / 2)
        upper_bias = 1 - max(0, center_y - scaled_height * 0.62) / scaled_height
        aspect_penalty = abs(aspect - 0.78)
        score = component["area"] * (0.7 + center_bias + upper_bias - aspect_penalty)
        candidates.append((score, component))

    if not candidates:
        return None

    _, best = max(candidates, key=lambda item: item[0])
    min_x, min_y, max_x, max_y = best["box"]
    inv_scale = 1 / scale
    min_x = int(min_x * inv_scale)
    min_y = int(min_y * inv_scale)
    max_x = int(max_x * inv_scale)
    max_y = int(max_y * inv_scale)

    width = max_x - min_x
    height = max_y - min_y
    side = int(max(width, height) * 1.45)
    center_x = (min_x + max_x) // 2
    center_y = (min_y + max_y) // 2
    crop_left = max(0, center_x - side // 2)
    crop_top = max(0, center_y - int(side * 0.47))
    crop_right = min(original_width, crop_left + side)
    crop_bottom = min(original_height, crop_top + side)

    if crop_right - crop_left < side:
        crop_left = max(0, crop_right - side)
    if crop_bottom - crop_top < side:
        crop_top = max(0, crop_bottom - side)

    return crop_left, crop_top, crop_right, crop_bottom


def initialize_opencv_detector():
    global OPENCV_DETECTOR
    if cv2 is None:
        return None
    if OPENCV_DETECTOR is None:
        cascade_path = Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml"
        OPENCV_DETECTOR = cv2.CascadeClassifier(str(cascade_path))
        warmup = np.zeros((160, 160), dtype=np.uint8)
        OPENCV_DETECTOR.detectMultiScale(warmup)
    return OPENCV_DETECTOR


def detect_with_opencv(image: Image.Image, max_size: int = 480):
    detector = initialize_opencv_detector()
    if detector is None:
        return None

    scale = min(1.0, max_size / max(image.size))
    detect_image = image.resize((int(image.width * scale), int(image.height * scale)))
    image_array = np.array(detect_image.convert("RGB"))
    gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
    detections = detector.detectMultiScale(
        gray,
        scaleFactor=1.08,
        minNeighbors=4,
        minSize=(80, 80),
    )

    if len(detections) == 0:
        return None

    detect_width, detect_height = detect_image.size
    image_center_x = detect_width / 2
    image_center_y = detect_height / 2

    def score(face):
        x, y, width, height = face
        area = width * height
        center_x = x + width / 2
        center_y = y + height / 2
        center_distance = (
            abs(center_x - image_center_x) / detect_width
            + abs(center_y - image_center_y) / detect_height
        )
        return area * (1.4 - center_distance)

    x, y, width, height = max(detections, key=score)
    inv_scale = 1 / scale
    x = int(x * inv_scale)
    y = int(y * inv_scale)
    width = int(width * inv_scale)
    height = int(height * inv_scale)
    side = int(max(width, height) * 1.22)
    center_x = x + width // 2
    center_y = y + height // 2
    crop_left = max(0, center_x - side // 2)
    crop_top = max(0, center_y - int(side * 0.46))
    crop_right = min(image.width, crop_left + side)
    crop_bottom = min(image.height, crop_top + side)

    if crop_right - crop_left < side:
        crop_left = max(0, crop_right - side)
    if crop_bottom - crop_top < side:
        crop_top = max(0, crop_bottom - side)

    return crop_left, crop_top, crop_right, crop_bottom


def process_image(image_path: Path, output_dir: Path):
    image = Image.open(image_path).convert("RGB")
    start = time.perf_counter()
    method = "opencv_haar"
    box = detect_with_opencv(image)
    if box is None:
        method = "skin_heuristic"
        mask, scale = skin_mask(image)
        components = connected_components(mask)
        box = choose_face_box(components, image.size, scale)
    elapsed_ms = (time.perf_counter() - start) * 1000

    output_dir.mkdir(parents=True, exist_ok=True)
    if box is None:
        return {
            "sample": image_path.stem,
            "status": "no_face_candidate",
            "method": method,
            "elapsed_ms": round(elapsed_ms, 3),
        }

    annotated = image.copy()
    draw = ImageDraw.Draw(annotated)
    draw.rectangle(box, outline=(244, 197, 66), width=max(4, image.width // 180))
    crop = image.crop(box).resize((112, 112))
    clahe_crop = apply_clahe_luminance(crop)

    annotated_path = output_dir / f"{image_path.stem}_annotated.png"
    crop_path = output_dir / f"{image_path.stem}_crop_112.png"
    clahe_path = output_dir / f"{image_path.stem}_crop_112_clahe.png"

    annotated.save(annotated_path)
    crop.save(crop_path)
    clahe_crop.save(clahe_path)

    return {
        "sample": image_path.stem,
        "status": "face_candidate",
        "method": method,
        "box": ",".join(str(value) for value in box),
        "annotated": str(annotated_path),
        "crop": str(crop_path),
        "clahe_crop": str(clahe_path),
        "elapsed_ms": round(elapsed_ms, 3),
    }


def main():
    parser = argparse.ArgumentParser(description="Create baseline face crops from images.")
    parser.add_argument("--input", required=True, help="Input image or directory")
    parser.add_argument("--output", required=True, help="Output evidence directory")
    parser.add_argument("--csv", help="Optional CSV path for crop results")
    args = parser.parse_args()

    results = []
    initialize_opencv_detector()
    for image_path in iter_images(Path(args.input)):
        result = process_image(image_path, Path(args.output))
        results.append(result)
        print(
            f"{result['sample']}: {result['status']} via {result.get('method')} "
            f"({result['elapsed_ms']} ms)"
        )

    if args.csv:
        csv_path = Path(args.csv)
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = [
            "sample",
            "status",
            "method",
            "box",
            "annotated",
            "crop",
            "clahe_crop",
            "elapsed_ms",
        ]
        with csv_path.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"Wrote CSV: {csv_path}")


if __name__ == "__main__":
    main()
