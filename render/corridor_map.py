#!/usr/bin/env python3
"""
Stylized NC-55 corridor map in True Homes brand colors.

Drawn from scratch rather than sourced, so there is no third-party image
licence attached to anything that goes out on the account. Positions are
schematic — this is a diagram of the corridor, not a survey map.

    python3 render/corridor_map.py workspace/highway-55/images/corridor-map.png
"""
import json
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = Path(__file__).resolve().parent / "fonts"

W, H = 1080, 1350

# Schematic positions as fractions of the canvas. NC 55 runs top-left to
# bottom, with Raleigh sitting off to the northeast of the corridor.
CORRIDOR = [
    ("Morrisville",   0.40, 0.10),
    ("Cary",          0.50, 0.30),
    ("Apex",          0.42, 0.50),
    ("Holly Springs", 0.36, 0.68),
    ("Fuquay-Varina", 0.47, 0.87),
]
CROSSINGS = [("I-540", 0.19), ("US 1", 0.585)]
RALEIGH = ("Downtown Raleigh", 0.76, 0.235)


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def smooth(points, steps=26):
    """Catmull-Rom through the town points so the road reads as a road."""
    pts = [points[0]] + list(points) + [points[-1]]
    out = []
    for i in range(len(pts) - 3):
        p0, p1, p2, p3 = pts[i:i + 4]
        for s in range(steps):
            t = s / steps
            t2, t3 = t * t, t * t * t
            out.append((
                0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t
                       + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2
                       + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3),
                0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t
                       + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2
                       + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)))
    out.append(points[-1])
    return out


def main():
    out_path = Path(sys.argv[1] if len(sys.argv) > 1 else "corridor-map.png")
    brand = json.load((ROOT / "config" / "brand.json").open())
    C = {k: v["hex"] for k, v in brand["colors"].items()}
    blush, brick, black = hexrgb(C["blush"]), hexrgb(C["brick"]), hexrgb(C["black"])
    faint = (198, 174, 158)

    img = Image.new("RGB", (W, H), blush)
    d = ImageDraw.Draw(img)

    def pf(size, weight="Bold"):
        f = ImageFont.truetype(str(FONTS / "PlayfairDisplay.ttf"), size)
        f.set_variation_by_name(weight)
        return f

    def ss(size, weight="Regular"):
        f = ImageFont.truetype(str(FONTS / "SourceSans3.ttf"), size)
        f.set_variation_by_name(weight)
        return f

    # crossings first, so the corridor sits on top of them
    for label, fy in CROSSINGS:
        y = fy * H
        for x in range(60, W - 60, 26):
            d.line([(x, y), (x + 13, y)], fill=faint, width=5)
        d.text((W - 74, y - 30), label, font=ss(27, "SemiBold"), fill=(150, 124, 108),
               anchor="ra")

    # the corridor
    pts = [(x * W, y * H) for _, x, y in CORRIDOR]
    path = smooth(pts)
    for i in range(len(path) - 1):
        d.line([path[i], path[i + 1]], fill=brick, width=15)
    d.ellipse([path[0][0] - 7, path[0][1] - 7, path[0][0] + 7, path[0][1] + 7], fill=brick)

    # Raleigh, off the corridor, joined by a dotted spur
    rx, ry = RALEIGH[1] * W, RALEIGH[2] * H
    cx, cy = CORRIDOR[1][1] * W, CORRIDOR[1][2] * H
    steps = 30
    for s in range(steps):
        if s % 2:
            continue
        t0, t1 = s / steps, (s + 1) / steps
        d.line([(cx + (rx - cx) * t0, cy + (ry - cy) * t0),
                (cx + (rx - cx) * t1, cy + (ry - cy) * t1)], fill=faint, width=5)

    def town(x, y, label, big=False, above=False):
        r = 19 if big else 15
        d.ellipse([x - r - 7, y - r - 7, x + r + 7, y + r + 7], fill=blush)
        d.ellipse([x - r, y - r, x + r, y + r], fill=brick if big else black)
        f = pf(46 if big else 40, "Bold")
        if above:
            # Raleigh sits near the right edge, so its label stacks above the
            # dot instead of running off the canvas.
            for i, line in enumerate(label.split()):
                d.text((x, y - r - 26 - (len(label.split()) - i) * 52 + 52),
                       line, font=f, fill=black, anchor="ma")
        else:
            d.text((x + r + 20, y), label, font=f, fill=black, anchor="lm")

    for name, fx, fy in CORRIDOR:
        town(fx * W, fy * H, name)
    town(rx, ry, RALEIGH[0], big=True, above=True)

    # NC 55 shield, bottom-left
    sx, sy, sw, sh = 78, H - 210, 132, 132
    d.rounded_rectangle([sx, sy, sx + sw, sy + sh], radius=16, fill=brick)
    d.text((sx + sw / 2, sy + 30), "NC", font=ss(30, "SemiBold"),
           fill=(232, 200, 186), anchor="ma")
    d.text((sx + sw / 2, sy + 58), "55", font=pf(62, "Bold"),
           fill=(255, 255, 255), anchor="ma")

    d.text((sx + sw + 26, sy + 44), "The corridor", font=pf(46, "Bold"),
           fill=black, anchor="la")
    d.text((sx + sw + 28, sy + 96), "Schematic, not to scale",
           font=ss(26), fill=(140, 116, 102), anchor="la")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)
    print(f"corridor map -> {out_path} ({W}x{H})")


if __name__ == "__main__":
    main()
