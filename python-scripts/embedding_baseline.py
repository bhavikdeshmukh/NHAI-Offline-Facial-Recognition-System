"""
Temporary embedding baseline for end-to-end offline matching evidence.

This is NOT MobileFaceNet. It creates a deterministic 128-number vector from a
112x112 face crop using image statistics. The purpose is to test the enrollment,
verification, cosine similarity, and benchmark flow today. Replace this with
MobileFaceNet INT8 TFLite as soon as the model source is finalized.
"""

from __future__ import annotations

import argparse
import csv
import itertools
import math
import time
from pathlib import Path

import numpy as np
from PIL import Image


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def iter_images(input_path: Path):
    if input_path.is_file() and input_path.suffix.lower() in IMAGE_EXTENSIONS:
        yield input_path
        return

    if input_path.is_dir():
        for path in sorted(input_path.rglob("*")):
            if path.suffix.lower() in IMAGE_EXTENSIONS:
                yield path


def normalize(vector: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(vector)
    if norm == 0:
        return vector
    return vector / norm


def cosine_similarity(vector_a: np.ndarray, vector_b: np.ndarray) -> float:
    vector_a = normalize(vector_a)
    vector_b = normalize(vector_b)
    return float(np.dot(vector_a, vector_b))


def temporary_embedding(image_path: Path) -> tuple[np.ndarray, float]:
    image = Image.open(image_path).convert("L").resize((112, 112))
    start = time.perf_counter()
    array = np.asarray(image, dtype=np.float32) / 255.0

    blocks = []
    for y_index in range(8):
        for x_index in range(8):
            block = array[y_index * 14 : (y_index + 1) * 14, x_index * 14 : (x_index + 1) * 14]
            blocks.append(block.mean())

    gradient_y, gradient_x = np.gradient(array)
    magnitude = np.sqrt(gradient_x**2 + gradient_y**2)
    for y_index in range(8):
        for x_index in range(8):
            block = magnitude[
                y_index * 14 : (y_index + 1) * 14,
                x_index * 14 : (x_index + 1) * 14,
            ]
            blocks.append(block.mean())

    vector = normalize(np.array(blocks, dtype=np.float32))
    elapsed_ms = (time.perf_counter() - start) * 1000
    return vector, elapsed_ms


def write_embeddings(output_path: Path, rows: list[dict]):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["sample", "embedding_dim", "elapsed_ms", "embedding"]
    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_matches(output_path: Path, rows: list[dict]):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["sample_a", "sample_b", "score", "is_match", "threshold"]
    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description="Generate temporary face embeddings.")
    parser.add_argument("--input", required=True, help="Input crop image or directory")
    parser.add_argument("--embeddings-csv", required=True)
    parser.add_argument("--matches-csv", required=True)
    parser.add_argument("--threshold", type=float, default=0.9)
    args = parser.parse_args()

    embeddings = []
    embedding_rows = []
    for image_path in iter_images(Path(args.input)):
        if "_crop_112" not in image_path.stem:
            continue
        vector, elapsed_ms = temporary_embedding(image_path)
        embeddings.append((image_path.stem, vector))
        embedding_rows.append(
            {
                "sample": image_path.stem,
                "embedding_dim": len(vector),
                "elapsed_ms": round(elapsed_ms, 3),
                "embedding": " ".join(f"{value:.6f}" for value in vector),
            }
        )
        print(f"{image_path.stem}: dim={len(vector)} ({elapsed_ms:.3f} ms)")

    match_rows = []
    for (sample_a, vector_a), (sample_b, vector_b) in itertools.combinations(embeddings, 2):
        score = cosine_similarity(vector_a, vector_b)
        match_rows.append(
            {
                "sample_a": sample_a,
                "sample_b": sample_b,
                "score": round(score, 6),
                "is_match": score >= args.threshold,
                "threshold": args.threshold,
            }
        )
        print(f"{sample_a} vs {sample_b}: score={score:.6f}")

    write_embeddings(Path(args.embeddings_csv), embedding_rows)
    write_matches(Path(args.matches_csv), match_rows)

    if embedding_rows:
        average_ms = sum(row["elapsed_ms"] for row in embedding_rows) / len(embedding_rows)
        print(f"Average temporary embedding time: {average_ms:.3f} ms")


if __name__ == "__main__":
    main()
