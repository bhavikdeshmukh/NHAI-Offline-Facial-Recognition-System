"""
Create synthetic lighting samples for testing the CLAHE workflow.

These are not real biometric samples. They only prove that the preprocessing and
evidence-generation scripts run end-to-end before real consented face samples are
added.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


def draw_face(draw: ImageDraw.ImageDraw, offset_x: int = 0):
    draw.ellipse((150 + offset_x, 70, 330 + offset_x, 290), fill=(174, 118, 82))
    draw.ellipse((190 + offset_x, 150, 212 + offset_x, 166), fill=(31, 42, 54))
    draw.ellipse((268 + offset_x, 150, 290 + offset_x, 166), fill=(31, 42, 54))
    draw.line((240 + offset_x, 166, 232 + offset_x, 220), fill=(94, 60, 45), width=5)
    draw.arc((204 + offset_x, 214, 276 + offset_x, 252), 10, 170, fill=(31, 42, 54), width=5)


def make_sample(path: Path, mode: str):
    image = Image.new("RGB", (480, 360), (168, 189, 199))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 230, 480, 360), fill=(76, 88, 86))
    draw_face(draw)

    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    mask = ImageDraw.Draw(overlay)
    if mode == "harsh_sun":
        mask.polygon((0, 0, 480, 0, 380, 360, 120, 360), fill=(255, 228, 90, 95))
    elif mode == "deep_shadow":
        mask.rectangle((0, 0, 260, 360), fill=(0, 0, 0, 130))
    elif mode == "low_light":
        mask.rectangle((0, 0, 480, 360), fill=(0, 20, 45, 120))
    elif mode == "blur":
        image = image.filter(ImageFilter.GaussianBlur(radius=2.5))

    image = Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")
    image.save(path)


def main():
    output_dir = Path("samples/lighting")
    output_dir.mkdir(parents=True, exist_ok=True)
    for mode in ["normal", "harsh_sun", "deep_shadow", "low_light", "blur"]:
        make_sample(output_dir / f"{mode}.png", mode)
    print(f"Wrote synthetic samples to {output_dir}")


if __name__ == "__main__":
    main()

