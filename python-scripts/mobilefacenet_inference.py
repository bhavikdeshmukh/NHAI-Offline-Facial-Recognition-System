"""
MobileFaceNet inference entrypoint.

This script intentionally does not download a model automatically. Place a
licensed model at one of these paths first:

    models/mobilefacenet.tflite
    models/mobilefacenet.onnx

Then rerun this script on 112x112 face crops.
"""

from __future__ import annotations

import argparse
import csv
import time
from pathlib import Path

import numpy as np
from PIL import Image


MODEL_CANDIDATES = [
    Path("models/mobilefacenet.tflite"),
    Path("models/mobilefacenet.onnx"),
]
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def find_model() -> Path:
    for model_path in MODEL_CANDIDATES:
        if model_path.exists():
            return model_path
    raise SystemExit(
        "No MobileFaceNet model found. Add a licensed model at "
        "models/mobilefacenet.tflite or models/mobilefacenet.onnx."
    )


def iter_images(input_path: Path):
    if input_path.is_file() and input_path.suffix.lower() in IMAGE_EXTENSIONS:
        yield input_path
        return

    if input_path.is_dir():
        for path in sorted(input_path.rglob("*")):
            if path.suffix.lower() in IMAGE_EXTENSIONS and "_crop_112" in path.stem:
                yield path


def prepare_input(image_path: Path) -> np.ndarray:
    image = Image.open(image_path).convert("RGB").resize((112, 112))
    array = np.asarray(image, dtype=np.float32)
    array = (array - 127.5) / 128.0
    return np.expand_dims(array, axis=0)


def run_tflite(model_path: Path, input_tensor: np.ndarray) -> np.ndarray:
    try:
        import tensorflow as tf
    except ImportError as exc:
        raise SystemExit(
            "TensorFlow is required for .tflite inference. Install tensorflow "
            "or use an ONNX model with onnxruntime."
        ) from exc

    interpreter = tf.lite.Interpreter(model_path=str(model_path))
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    interpreter.set_tensor(input_details[0]["index"], input_tensor)
    interpreter.invoke()
    return interpreter.get_tensor(output_details[0]["index"]).reshape(-1)


def run_onnx(model_path: Path, input_tensor: np.ndarray) -> np.ndarray:
    try:
        import onnxruntime as ort
    except ImportError as exc:
        raise SystemExit(
            "onnxruntime is required for .onnx inference. Install onnxruntime "
            "or use a TFLite model with TensorFlow."
        ) from exc

    session = ort.InferenceSession(str(model_path), providers=["CPUExecutionProvider"])
    input_name = session.get_inputs()[0].name
    output = session.run(None, {input_name: input_tensor})[0]
    return np.asarray(output).reshape(-1)


def normalize(vector: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(vector)
    if norm == 0:
        return vector
    return vector / norm


def main():
    parser = argparse.ArgumentParser(description="Run licensed MobileFaceNet inference.")
    parser.add_argument("--input", required=True, help="112x112 crop image or directory")
    parser.add_argument("--output", required=True, help="Output embeddings CSV")
    args = parser.parse_args()

    model_path = find_model()
    rows = []

    for image_path in iter_images(Path(args.input)):
        input_tensor = prepare_input(image_path)
        start = time.perf_counter()
        if model_path.suffix.lower() == ".tflite":
            embedding = run_tflite(model_path, input_tensor)
        elif model_path.suffix.lower() == ".onnx":
            embedding = run_onnx(model_path, input_tensor)
        else:
            raise SystemExit(f"Unsupported model format: {model_path}")
        elapsed_ms = (time.perf_counter() - start) * 1000
        embedding = normalize(embedding)

        rows.append(
            {
                "sample": image_path.stem,
                "model": str(model_path),
                "embedding_dim": len(embedding),
                "elapsed_ms": round(elapsed_ms, 3),
                "embedding": " ".join(f"{value:.6f}" for value in embedding),
            }
        )
        print(f"{image_path.stem}: dim={len(embedding)} ({elapsed_ms:.3f} ms)")

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=["sample", "model", "embedding_dim", "elapsed_ms", "embedding"],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()

