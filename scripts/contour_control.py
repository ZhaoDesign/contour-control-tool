#!/usr/bin/env python3
"""Create a lightweight contour-control image for Nano Banana references."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageOps


def parse_percent_pair(raw: str) -> tuple[float, float]:
    try:
        x, y = raw.split(",", 1)
        return float(x), float(y)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("use x,y percent format, for example 50,23") from exc


def parse_face_size(raw: str) -> tuple[float, float]:
    try:
        w, h = raw.split(",", 1)
        return float(w), float(h)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("use width,height percent format, for example 24,17") from exc


def sobel_edges(gray: Image.Image) -> tuple[list[float], int, int]:
    width, height = gray.size
    try:
        pixels = list(gray.get_flattened_data())
    except AttributeError:
        pixels = list(gray.getdata())
    edges = [0.0] * (width * height)
    max_value = 0.0

    def get(x: int, y: int) -> int:
        x = max(0, min(width - 1, x))
        y = max(0, min(height - 1, y))
        return pixels[y * width + x]

    for y in range(height):
        for x in range(width):
            a = get(x - 1, y - 1)
            b = get(x, y - 1)
            c = get(x + 1, y - 1)
            d = get(x - 1, y)
            f = get(x + 1, y)
            g = get(x - 1, y + 1)
            h = get(x, y + 1)
            i = get(x + 1, y + 1)
            gx = -a + c - 2 * d + 2 * f - g + i
            gy = -a - 2 * b - c + g + 2 * h + i
            mag = (gx * gx + gy * gy) ** 0.5
            edges[y * width + x] = mag
            if mag > max_value:
                max_value = mag

    if max_value > 0:
        edges = [value / max_value * 255.0 for value in edges]
    return edges, width, height


def thicken_lines(line: list[int], width: int, height: int, amount: int) -> list[int]:
    if amount <= 0:
        return line
    current = line
    for _ in range(amount):
        out = current[:]
        for y in range(height):
            for x in range(width):
                darkest = 255
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        xx = max(0, min(width - 1, x + dx))
                        yy = max(0, min(height - 1, y + dy))
                        darkest = min(darkest, current[yy * width + xx])
                out[y * width + x] = darkest
        current = out
    return current


def make_control_image(
    source: Path,
    output: Path,
    blur: float,
    threshold: float,
    softness: float,
    thicken: int,
    mute_face: bool,
    face_center: tuple[float, float],
    face_size: tuple[float, float],
    max_side: int,
) -> None:
    img = Image.open(source).convert("RGB")
    if max_side > 0:
        scale = min(1.0, max_side / max(img.size))
        if scale < 1.0:
            img = img.resize((round(img.width * scale), round(img.height * scale)), Image.Resampling.LANCZOS)

    gray = ImageOps.grayscale(img)
    if blur > 0:
        gray = gray.filter(ImageFilter.GaussianBlur(radius=blur))

    edges, width, height = sobel_edges(gray)
    low = threshold * 0.55
    line: list[int] = []
    for edge in edges:
        if edge >= threshold:
            value = max(0.0, 95.0 - (edge - threshold) * 1.6)
        elif softness > 0 and edge >= low:
            t = (edge - low) / max(1.0, threshold - low)
            value = 255.0 - t * softness
        else:
            value = 255.0
        line.append(round(value))

    line = thicken_lines(line, width, height, max(0, int(thicken)))
    result = Image.new("L", (width, height))
    result.putdata(line)
    result = result.convert("RGB")

    if mute_face:
        draw = ImageDraw.Draw(result)
        width, height = result.size
        cx = face_center[0] / 100.0 * width
        cy = face_center[1] / 100.0 * height
        rx = face_size[0] / 200.0 * width
        ry = face_size[1] / 200.0 * height
        box = (cx - rx, cy - ry, cx + rx, cy + ry)
        stroke = max(2, round(width / 240))
        draw.ellipse(box, fill=(255, 255, 255), outline=(156, 156, 156), width=stroke)
        draw.line((cx, cy - ry * 0.45, cx + rx * 0.08, cy + ry * 0.45), fill=(184, 184, 184), width=1)

    output.parent.mkdir(parents=True, exist_ok=True)
    result.save(output)


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert a reference photo into a lightweight contour-control PNG.")
    parser.add_argument("input", type=Path, help="source image path")
    parser.add_argument("-o", "--output", type=Path, required=True, help="output PNG path")
    parser.add_argument("--blur", type=float, default=1.4, help="blur radius for noise reduction, default: 1.4")
    parser.add_argument("--threshold", type=float, default=42.0, help="edge threshold, default: 42")
    parser.add_argument("--softness", type=float, default=56.0, help="light gray edge retention, default: 56")
    parser.add_argument("--thicken", type=int, default=1, choices=range(0, 4), help="line thickening passes, 0-3")
    parser.add_argument("--no-face-mute", action="store_true", help="do not blank out the face area")
    parser.add_argument("--face-center", type=parse_percent_pair, default=(50.0, 23.0), help="face center as x,y percent")
    parser.add_argument("--face-size", type=parse_face_size, default=(24.0, 17.0), help="face ellipse size as width,height percent")
    parser.add_argument("--max-side", type=int, default=1600, help="resize long side before processing, 0 keeps original size")
    args = parser.parse_args()

    make_control_image(
        source=args.input,
        output=args.output,
        blur=args.blur,
        threshold=args.threshold,
        softness=args.softness,
        thicken=args.thicken,
        mute_face=not args.no_face_mute,
        face_center=args.face_center,
        face_size=args.face_size,
        max_side=args.max_side,
    )


if __name__ == "__main__":
    main()
