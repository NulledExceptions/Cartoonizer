#!/usr/bin/env python3
"""Generate the Cartoonizer app icon PNGs and ICNS bundle."""
from __future__ import annotations

import math
import os
import struct
import zlib
import binascii
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
ICONSET = ASSETS / "Cartoonizer.iconset"
BASE_SIZE = 1024


def render_base(size: int = BASE_SIZE):
    cx = size / 2
    cy = size / 2 + 50
    lens_radius = 250
    smile_y = cy - 40
    smile_r = 320
    data = []
    for y in range(size):
        t = y / (size - 1)
        top = (70, 60, 180)
        bottom = (40, 150, 160)
        base = [int(top[i] * (1 - t) + bottom[i] * t) for i in range(3)]
        row = []
        for x in range(size):
            r, g, b = base
            dx = (x - size / 2) / size
            dy = (y - size / 2) / size
            dist = math.sqrt(dx * dx + dy * dy)
            if dist > 0.7:
                fade = min((dist - 0.7) / 0.3, 1)
                r = int(r * (1 - fade) + 20 * fade)
                g = int(g * (1 - fade) + 20 * fade)
                b = int(b * (1 - fade) + 30 * fade)

            glow_dx = (x - size / 2) / 350
            glow_dy = (y - (size * 0.45)) / 350
            glow = math.exp(-(glow_dx * glow_dx + glow_dy * glow_dy))
            r = min(255, int(r + 80 * glow))
            g = min(255, int(g + 70 * glow))
            b = min(255, int(b + 40 * glow))

            d = math.hypot(x - cx, y - cy)
            if d < lens_radius:
                t2 = d / lens_radius
                lens_color = (255, 210, 140)
                alpha = 0.75
                mix = alpha * (1 - t2 * 0.3)
                r = int(r * (1 - mix) + lens_color[0] * mix)
                g = int(g * (1 - mix) + lens_color[1] * mix)
                b = int(b * (1 - mix) + lens_color[2] * mix)
                if lens_radius - 10 < d < lens_radius:
                    r = int(r * 0.7)
                    g = int(g * 0.7)
                    b = int(b * 0.7)

            hx = cx - 90
            hy = cy - 90
            if ((x - hx) / 160) ** 2 + ((y - hy) / 120) ** 2 < 1:
                r = min(255, int(r * 0.6 + 255 * 0.4))
                g = min(255, int(g * 0.6 + 255 * 0.4))
                b = min(255, int(b * 0.6 + 255 * 0.4))

            hx2 = cx + 120
            hy2 = cy - 10
            if ((x - hx2) / 90) ** 2 + ((y - hy2) / 60) ** 2 < 1:
                r = min(255, int(r * 0.7 + 255 * 0.3))
                g = min(255, int(g * 0.7 + 255 * 0.3))
                b = min(255, int(b * 0.7 + 255 * 0.3))

            if abs(x - cx) < smile_r:
                val = smile_r ** 2 - (x - cx) ** 2
                if val >= 0:
                    arc_y = smile_y + math.sqrt(val)
                    if smile_y - 10 < y < arc_y + 5 and abs(y - arc_y) < 4:
                        r, g, b = 200, 90, 70

            bx = (x - (cx + 40))
            by = (y - (cy - 250))
            proj = (bx * 0.6 + by * 0.8)
            perp = (-bx * 0.8 + by * 0.6)
            if 0 < proj < 420 and abs(perp) < 55:
                r = 255
                g = int(140 + perp * 0.2)
                b = 100

            hx_rect1 = cx + 150
            hy_rect1 = cy - 50
            if hx_rect1 < x < hx_rect1 + 70 and hy_rect1 < y < hy_rect1 + 280:
                r, g, b = 60, 50, 80

            tx = cx + 180
            ty = cy + 230
            if tx < x < tx + 80 and ty < y < ty + 120:
                r, g, b = 240, 210, 150

            for sx, sy in [(220, 260), (780, 260), (230, 800), (700, 820)]:
                if (x - sx) ** 2 + (y - sy) ** 2 < 35 ** 2:
                    r = g = b = 255
                    break

            row.append((r, g, b, 255))
        data.append(row)
    return data


def resize(pixels, target):
    src = len(pixels)
    if target == src:
        return [row[:] for row in pixels]
    result = []
    denom = max(target - 1, 1)
    for j in range(target):
        y = j * (src - 1) / denom
        y0 = int(math.floor(y))
        y1 = min(src - 1, y0 + 1)
        wy = y - y0
        row = []
        for i in range(target):
            x = i * (src - 1) / denom
            x0 = int(math.floor(x))
            x1 = min(src - 1, x0 + 1)
            wx = x - x0
            c00 = pixels[y0][x0]
            c01 = pixels[y0][x1]
            c10 = pixels[y1][x0]
            c11 = pixels[y1][x1]

            def interp(a, b, t):
                return a * (1 - t) + b * t

            top = [interp(c00[k], c01[k], wx) for k in range(4)]
            bottom = [interp(c10[k], c11[k], wx) for k in range(4)]
            blended = [int(interp(top[k], bottom[k], wy) + 0.5) for k in range(4)]
            row.append(tuple(blended))
        result.append(row)
    return result


def save_png(pixels, path: Path):
    height = len(pixels)
    width = len(pixels[0])
    raw = bytearray()
    for row in pixels:
        raw.append(0)
        for r, g, b, a in row:
            raw.extend((r, g, b, a))
    compressed = zlib.compress(bytes(raw))

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", binascii.crc32(tag + data) & 0xFFFFFFFF)
        )

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", compressed) + chunk(b"IEND", b"")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(png)


def build_iconset(base_pixels):
    ICONSET.mkdir(parents=True, exist_ok=True)
    for size in (16, 32, 128, 256, 512):
        normal = resize(base_pixels, size)
        save_png(normal, ICONSET / f"icon_{size}x{size}.png")
        double = resize(base_pixels, size * 2)
        save_png(double, ICONSET / f"icon_{size}x{size}@2x.png")


def build_icns():
    entries = [
        ("ic10", "icon_512x512@2x.png"),
        ("ic09", "icon_512x512.png"),
        ("ic14", "icon_256x256@2x.png"),
        ("ic08", "icon_256x256.png"),
        ("ic13", "icon_128x128@2x.png"),
        ("ic07", "icon_128x128.png"),
        ("ic12", "icon_32x32@2x.png"),
        ("ic11", "icon_16x16@2x.png"),
        ("ic05", "icon_32x32.png"),
        ("ic04", "icon_16x16.png"),
    ]
    chunks = []
    for tag, name in entries:
        data = (ICONSET / name).read_bytes()
        chunks.append((tag.encode("ascii"), data))
    total_len = 8 + sum(len(data) + 8 for _, data in chunks)
    out = bytearray()
    out.extend(b"icns")
    out.extend(struct.pack(">I", total_len))
    for tag, data in chunks:
        out.extend(tag)
        out.extend(struct.pack(">I", len(data) + 8))
        out.extend(data)
    (ASSETS / "Cartoonizer.icns").write_bytes(bytes(out))


def main():
    base_pixels = render_base()
    save_png(base_pixels, ASSETS / "cartoonizer_icon_1024.png")
    build_iconset(base_pixels)
    build_icns()
    save_png(resize(base_pixels, 512), ASSETS / "cartoonizer_web_icon.png")
    print("Icon assets written to", ASSETS)


if __name__ == "__main__":
    main()
