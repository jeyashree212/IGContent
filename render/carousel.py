#!/usr/bin/env python3
"""
True Homes Realty carousel renderer.

Turns one config.json into branded slides at both Instagram (1080x1350) and
TikTok (1080x1920) sizes, so a single carousel cross-posts without recropping.

    python3 render/carousel.py workspace/<slug>
    python3 render/carousel.py workspace/<slug> --format ig
    python3 render/carousel.py workspace/<slug> --slide 3

Brand tokens, the brokerage disclosure, and the profile come from
config/brand.json. Nothing about the look lives in this file's callers.
"""

import argparse
import json
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance

try:
    import pillow_heif
    pillow_heif.register_heif_opener()
    HEIC = True
except ImportError:          # pip install pillow-heif
    HEIC = False

ROOT = Path(__file__).resolve().parent.parent
FONT_DIR = Path(__file__).resolve().parent / "fonts"
BRAND_DIR = ROOT / "brand"

FORMATS = {
    "ig": (1080, 1350),
    "tiktok": (1080, 1920),
}

# Type scale, keyed by format. TikTok is taller, not wider, so only the
# vertical rhythm changes; point sizes hold so the two read as one system.
MARGIN = 88
FOOTER_H = 96


# --------------------------------------------------------------------------
# brand
# --------------------------------------------------------------------------

def load_brand():
    with open(ROOT / "config" / "brand.json") as f:
        return json.load(f)


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def load_fonts():
    """Playfair Display for display type, Source Sans 3 for everything else."""
    playfair = FONT_DIR / "PlayfairDisplay.ttf"
    source = FONT_DIR / "SourceSans3.ttf"

    def pf(size, weight="Bold"):
        f = ImageFont.truetype(str(playfair), size)
        f.set_variation_by_name(weight)
        return f

    def ss(size, weight="Regular"):
        f = ImageFont.truetype(str(source), size)
        f.set_variation_by_name(weight)
        return f

    return {
        "stat":        pf(210, "Bold"),
        "stat_sm":     pf(150, "Bold"),
        "over":        pf(92, "Bold"),
        "over_sm":     pf(72, "Bold"),
        "hook":        pf(104, "Bold"),
        "hook_sm":     pf(84, "Bold"),
        "title":       pf(76, "Bold"),
        "title_sm":    pf(60, "Bold"),
        "cta_name":    pf(64, "Bold"),
        "subtitle":    ss(40, "Regular"),
        "body":        ss(42, "Regular"),
        "body_semi":   ss(42, "SemiBold"),
        "bullet":      ss(40, "Regular"),
        "eyebrow":     ss(26, "SemiBold"),
        "footer":      ss(26, "Regular"),
        "footer_semi": ss(26, "SemiBold"),
        "button":      ss(36, "SemiBold"),
        "disclosure":  ss(24, "Regular"),
    }


# --------------------------------------------------------------------------
# text helpers
# --------------------------------------------------------------------------

def parse_accents(text):
    """'a *b* c' -> [('a ', False), ('b', True), (' c', False)]"""
    out = []
    for i, part in enumerate(text.split("*")):
        if part:
            out.append((part, i % 2 == 1))
    return out


TRAILING_PUNCT = ".,;:!?)—-"


def wrap_accented(draw, text, font, max_width):
    """Wrap to lines of (word, is_accent) tuples, preserving accent spans."""
    words = []
    for seg, is_accent in parse_accents(text):
        # Punctuation immediately after a closing '*' belongs to the word it
        # follows, or it renders as an orphan floating after a space.
        if words and seg and seg[0] in TRAILING_PUNCT and not seg.startswith(" "):
            stuck = ""
            while seg and seg[0] in TRAILING_PUNCT:
                stuck, seg = stuck + seg[0], seg[1:]
            prev, prev_acc = words[-1]
            words[-1] = (prev + stuck, prev_acc)
        for w in seg.split():
            words.append((w, is_accent))

    lines, current = [], []
    for word, acc in words:
        trial = " ".join([w for w, _ in current] + [word])
        if draw.textlength(trial, font=font) <= max_width or not current:
            current.append((word, acc))
        else:
            lines.append(current)
            current = [(word, acc)]
    if current:
        lines.append(current)
    return lines


def line_height(font, factor):
    asc, desc = font.getmetrics()
    return int((asc + desc) * factor)


def draw_accented(draw, lines, xy, font, fill, accent, factor=1.24, center_w=None):
    """Draw wrapped accented lines. Returns the y below the last line."""
    x, y = xy
    lh = line_height(font, factor)
    space = draw.textlength(" ", font=font)
    for line in lines:
        if center_w:
            width = sum(draw.textlength(w, font=font) for w, _ in line)
            width += space * (len(line) - 1)
            cx = x + (center_w - width) / 2
        else:
            cx = x
        for word, acc in line:
            draw.text((cx, y), word, font=font, fill=accent if acc else fill)
            cx += draw.textlength(word, font=font) + space
        y += lh
    return y


def measure(draw, text, font, max_width, factor=1.24):
    return len(wrap_accented(draw, text, font, max_width)) * line_height(font, factor)


# --------------------------------------------------------------------------
# brand devices
# --------------------------------------------------------------------------

def draw_swash(draw, x, y, width, color, scale=1.0):
    """
    The two-stroke brick underline from the Under Contract graphic.
    Two tapered, slightly-arced strokes, the lower one shorter and offset.
    """
    def stroke(x0, w, y0, thick, lift):
        pts = []
        steps = 48
        for i in range(steps + 1):
            t = i / steps
            px = x0 + w * t
            py = y0 - math.sin(t * math.pi) * lift
            pts.append((px, py))
        for i in range(len(pts) - 1):
            # taper the ends
            edge = min(t_ratio := min(i, len(pts) - 2 - i) / (len(pts) / 2), 1.0)
            tw = max(2, thick * (0.35 + 0.65 * edge))
            draw.line([pts[i], pts[i + 1]], fill=color, width=int(tw))

    t = 13 * scale
    stroke(x, width, y, t, 11 * scale)
    stroke(x + width * 0.19, width * 0.72, y + 26 * scale, t * 0.85, 8 * scale)


def circle_crop(img, size):
    big = size * 3
    img = img.convert("RGB").resize((big, big), Image.LANCZOS)
    mask = Image.new("L", (big, big), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, big, big), fill=255)
    out = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    out.paste(img, (0, 0), mask)
    return out.resize((size, size), Image.LANCZOS)


def open_photo(path, grade=True):
    """
    Open any photo she drops in — including straight-off-the-iPhone HEIC —
    with EXIF rotation baked in so portrait shots aren't sideways.
    """
    img = Image.open(path)
    img = ImageOps.exif_transpose(img).convert("RGB")
    if grade:
        img = ImageEnhance.Color(img).enhance(1.06)
        img = ImageEnhance.Contrast(img).enhance(1.04)
    return img


def scrim(img, strength=0.86, start=0.34):
    """Darken the lower part of a photo so white type reads over it."""
    w, h = img.size
    grad = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grad)
    top = int(h * start)
    for y in range(top, h):
        t = (y - top) / max(1, h - top)
        gd.line([(0, y), (w, y)], fill=(24, 14, 10, int((t ** 1.4) * 255 * strength)))
    return Image.alpha_composite(img.convert("RGBA"), grad).convert("RGB")


def corner_wedge(img, C, size=250):
    """The diagonal brick corner from her FOR SALE template, bottom-right."""
    W, H = img.size
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(layer).polygon(
        [(W, H - size), (W, H), (W - size, H)], fill=hex_to_rgb(C["brick"]) + (255,))
    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")


def cover_fit(img, w, h):
    ratio = max(w / img.width, h / img.height)
    img = img.resize((int(img.width * ratio) + 1, int(img.height * ratio) + 1), Image.LANCZOS)
    left = (img.width - w) // 2
    top = (img.height - h) // 2
    return img.crop((left, top, left + w, top + h))


def resolve_image(name, carousel_dir):
    if not name:
        return None
    path = BRAND_DIR / name[6:] if name.startswith("brand:") else carousel_dir / "images" / name
    return path if path.exists() else None


# --------------------------------------------------------------------------
# slide chrome
# --------------------------------------------------------------------------

def new_slide(W, H, C):
    return Image.new("RGB", (W, H), hex_to_rgb(C["blush"]))


def draw_footer(img, draw, F, C, brand, W, H, index, total):
    y = H - 58
    handle = brand["account"]["handle"]
    draw.text((MARGIN, y), handle, font=F["footer_semi"],
              fill=hex_to_rgb(C["black"]), anchor="lm")

    label = f"{index} / {total}"
    draw.text((W - MARGIN, y), label, font=F["footer"],
              fill=hex_to_rgb(C["brick"]), anchor="rm")

    draw.line([(MARGIN, y - 40), (W - MARGIN, y - 40)],
              fill=hex_to_rgb(C["brick"]) + (0,) if False else hex_to_rgb("#C9AE9C"), width=2)


# --------------------------------------------------------------------------
# slide renderers
# --------------------------------------------------------------------------

def render_hook(cfg, slide, F, C, brand, dims, carousel_dir, index, total):
    W, H = dims
    img = new_slide(W, H, C)
    draw = ImageDraw.Draw(img)

    band_h = int(H * (0.44 if H > 1500 else 0.40))
    src = resolve_image(slide.get("image"), carousel_dir)
    if src:
        photo = cover_fit(open_photo(src), W, band_h)
        # fade the bottom of the photo into the blush ground
        ground = hex_to_rgb(C["blush"])
        grad = Image.new("RGBA", (W, band_h), (0, 0, 0, 0))
        gd = ImageDraw.Draw(grad)
        fade_from = int(band_h * 0.62)
        for yy in range(fade_from, band_h):
            t = (yy - fade_from) / max(1, band_h - fade_from)
            gd.line([(0, yy), (W, yy)], fill=ground + (int(min(255, (t ** 1.6) * 300)),))
        photo = Image.alpha_composite(photo.convert("RGBA"), grad)
        img.paste(photo.convert("RGB"), (0, 0))
        draw = ImageDraw.Draw(img)
        top = band_h + 46
    else:
        top = MARGIN + 40

    if slide.get("eyebrow"):
        draw.text((MARGIN, top), slide["eyebrow"].upper(), font=F["eyebrow"],
                  fill=hex_to_rgb(C["brick"]))
        top += 52

    content_w = W - MARGIN * 2
    avail = (H - FOOTER_H - 24) - top

    # Fit headline + swash + subtitle into the space below the photo band.
    # Step the display size down rather than letting the block run into the footer.
    sub_h = (measure(draw, slide["subtitle"], F["subtitle"], content_w, 1.30) + 22
             if slide.get("subtitle") else 0)
    for font in (F["hook"], F["hook_sm"]):
        lines = wrap_accented(draw, slide["text"], font, content_w)
        block = len(lines) * line_height(font, 1.02) + 96 + sub_h
        if block <= avail:
            break

    y = draw_accented(draw, lines, (MARGIN, top), font,
                      hex_to_rgb(C["black"]), hex_to_rgb(C["brick"]), factor=1.02)

    last = lines[-1]
    swash_w = min(content_w, sum(draw.textlength(w, font=font) for w, _ in last)
                  + draw.textlength(" ", font=font) * (len(last) - 1))
    draw_swash(draw, MARGIN, y + 20, swash_w, hex_to_rgb(C["brick"]))
    y += 74

    if slide.get("subtitle"):
        sub = wrap_accented(draw, slide["subtitle"], F["subtitle"], content_w)
        draw_accented(draw, sub, (MARGIN, y), F["subtitle"],
                      hex_to_rgb("#5C4A40"), hex_to_rgb(C["brick"]), factor=1.30)

    draw_footer(img, draw, F, C, brand, W, H, index, total)
    return img


def render_body(cfg, slide, F, C, brand, dims, carousel_dir, index, total):
    W, H = dims
    img = new_slide(W, H, C)
    draw = ImageDraw.Draw(img)
    content_w = W - MARGIN * 2

    src = resolve_image(slide.get("image"), carousel_dir)
    has_bullets = bool(slide.get("bullets"))

    # ---- measure so the block can be vertically centred
    blocks = []
    if slide.get("eyebrow"):
        blocks.append(("eyebrow", 52))
    title_font = F["title"]
    if slide.get("title"):
        tl = wrap_accented(draw, slide["title"], title_font, content_w)
        if len(tl) > 3:
            title_font = F["title_sm"]
            tl = wrap_accented(draw, slide["title"], title_font, content_w)
        blocks.append(("title", len(tl) * line_height(title_font, 1.1) + 54))
    if slide.get("text"):
        blocks.append(("text", measure(draw, slide["text"], F["body"], content_w, 1.30) + 30))

    img_h = 0
    if src:
        photo_src = open_photo(src)
        img_h = 380 if has_bullets else int(H * 0.34)
        blocks.append(("image", img_h + 44))
    if has_bullets:
        bh = 0
        for b in slide["bullets"]:
            bh += measure(draw, b, F["bullet"], content_w - 52, 1.20) + 34
        blocks.append(("bullets", bh + 12))

    total_h = sum(h for _, h in blocks)
    usable_top = MARGIN + 20
    usable_bot = H - FOOTER_H - 30
    y = usable_top + max(0, (usable_bot - usable_top - total_h) // 2)

    # ---- draw
    if slide.get("eyebrow"):
        draw.text((MARGIN, y), slide["eyebrow"].upper(), font=F["eyebrow"],
                  fill=hex_to_rgb(C["brick"]))
        y += 52

    if slide.get("title"):
        y = draw_accented(draw, tl, (MARGIN, y), title_font,
                          hex_to_rgb(C["black"]), hex_to_rgb(C["brick"]), factor=1.1)
        draw_swash(draw, MARGIN, y + 20, 168, hex_to_rgb(C["brick"]), scale=0.8)
        y += 54

    if slide.get("text"):
        lines = wrap_accented(draw, slide["text"], F["body"], content_w)
        y = draw_accented(draw, lines, (MARGIN, y), F["body"],
                          hex_to_rgb("#3B2E28"), hex_to_rgb(C["brick"]), factor=1.30)
        y += 30

    if src:
        photo = cover_fit(photo_src, content_w, img_h)
        mask = Image.new("L", (content_w, img_h), 0)
        ImageDraw.Draw(mask).rounded_rectangle([(0, 0), (content_w, img_h)], radius=4, fill=255)
        img.paste(photo, (MARGIN, int(y)), mask)
        draw = ImageDraw.Draw(img)
        y += img_h + 44

    if has_bullets:
        for b in slide["bullets"]:
            lines = wrap_accented(draw, b, F["bullet"], content_w - 52)
            dot_y = y + line_height(F["bullet"], 1.20) * 0.42
            draw.ellipse([(MARGIN, dot_y), (MARGIN + 13, dot_y + 13)],
                         fill=hex_to_rgb(C["brick"]))
            y = draw_accented(draw, lines, (MARGIN + 52, y), F["bullet"],
                              hex_to_rgb("#3B2E28"), hex_to_rgb(C["brick"]), factor=1.20)
            y += 34

    draw_footer(img, draw, F, C, brand, W, H, index, total)
    return img


def render_cta(cfg, slide, F, C, brand, dims, carousel_dir, index, total):
    W, H = dims
    img = new_slide(W, H, C)
    draw = ImageDraw.Draw(img)
    acct = brand["account"]
    cx = W // 2
    content_w = W - MARGIN * 2

    # Brick band across the lower third, echoing the sign's diagonal block.
    # Placed after the copy is measured so black text never lands on brick.
    text = slide.get("text", "Follow for more.")
    cta_lines = wrap_accented(draw, text, F["body_semi"], content_w - 60)

    hs = BRAND_DIR / "headshot.png"
    size = 260
    top = int(H * 0.16)
    if hs.exists():
        ring = size + 22
        draw.ellipse([(cx - ring // 2, top - 11), (cx + ring // 2, top + ring - 11)],
                     fill=hex_to_rgb("#FFFFFF"))
        circ = circle_crop(open_photo(hs, grade=False), size)
        img.paste(circ, (cx - size // 2, top), circ)
        draw = ImageDraw.Draw(img)
    else:
        draw.ellipse([(cx - size // 2, top), (cx + size // 2, top + size)],
                     fill=hex_to_rgb(C["brick"]))
        draw.text((cx, top + size // 2), "JH", font=F["cta_name"],
                  fill=hex_to_rgb("#FFFFFF"), anchor="mm")
    y = top + size + 46

    draw.text((cx, y), acct["display_name"], font=F["cta_name"],
              fill=hex_to_rgb(C["black"]), anchor="ma")
    y += line_height(F["cta_name"], 1.16)

    draw.text((cx, y), acct["handle"], font=F["body"],
              fill=hex_to_rgb("#6B554A"), anchor="ma")
    y += line_height(F["body"], 1.5)

    y = draw_accented(draw, cta_lines, (MARGIN + 30, y + 10), F["body_semi"],
                      hex_to_rgb(C["black"]), hex_to_rgb(C["brick"]),
                      factor=1.36, center_w=content_w - 60)

    band_top = max(int(H * 0.70), int(y) + 52)
    band = Image.new("RGB", (W, H - band_top), hex_to_rgb(C["brick"]))
    img.paste(band, (0, band_top))
    draw = ImageDraw.Draw(img)

    # button sits on the brick band, reversed out in blush
    if slide.get("button_text"):
        label = slide["button_text"]
        tw = draw.textlength(label, font=F["button"])
        bw, bh = tw + 92, 84
        by = band_top + int((H - band_top) * 0.30) - bh // 2
        draw.rounded_rectangle([(cx - bw // 2, by), (cx + bw // 2, by + bh)],
                               radius=bh // 2, fill=hex_to_rgb(C["blush"]))
        draw.text((cx, by + bh // 2), label, font=F["button"],
                  fill=hex_to_rgb(C["brick"]), anchor="mm")

    # brokerage disclosure — hard rule, never optional
    draw.text((cx, H - 74), brand["account"]["disclosure_line"], font=F["disclosure"],
              fill=hex_to_rgb("#EBD9CE"), anchor="ma")
    draw.text((cx, H - 42), acct["website"], font=F["disclosure"],
              fill=hex_to_rgb("#D8BCAE"), anchor="ma")
    return img


def render_photo(cfg, slide, F, C, brand, dims, carousel_dir, index, total):
    """Full-bleed photo with a scrim and type over it. Built for city shots."""
    W, H = dims
    src = resolve_image(slide.get("image"), carousel_dir)
    if not src:
        return render_body(cfg, slide, F, C, brand, dims, carousel_dir, index, total)

    img = scrim(cover_fit(open_photo(src), W, H))
    draw = ImageDraw.Draw(img)
    content_w = W - MARGIN * 2

    blocks = []
    if slide.get("caption"):
        blocks.append(("caption", measure(draw, slide["caption"], F["body"], content_w, 1.30) + 26))
    font = F["over"]
    lines = wrap_accented(draw, slide["text"], font, content_w)
    if len(lines) > 3:
        font = F["over_sm"]
        lines = wrap_accented(draw, slide["text"], font, content_w)
    head_h = len(lines) * line_height(font, 1.04)

    y = H - FOOTER_H - 22 - head_h - sum(h for _, h in blocks)

    if slide.get("eyebrow"):
        draw.text((MARGIN, y - 54), slide["eyebrow"].upper(), font=F["eyebrow"],
                  fill=hex_to_rgb("#E8C4B6"))

    y = draw_accented(draw, lines, (MARGIN, y), font,
                      hex_to_rgb("#FFFFFF"), hex_to_rgb("#E9A99B"), factor=1.04)

    if slide.get("caption"):
        cl = wrap_accented(draw, slide["caption"], F["body"], content_w)
        draw_accented(draw, cl, (MARGIN, y + 22), F["body"],
                      hex_to_rgb("#E4D3C9"), hex_to_rgb("#E9A99B"), factor=1.30)

    draw.text((MARGIN, H - 58), brand["account"]["handle"], font=F["footer_semi"],
              fill=hex_to_rgb("#FFFFFF"), anchor="lm")
    draw.text((W - MARGIN, H - 58), f"{index} / {total}", font=F["footer"],
              fill=hex_to_rgb("#E8C4B6"), anchor="rm")
    return img


def render_stat(cfg, slide, F, C, brand, dims, carousel_dir, index, total):
    """One number, set huge. For growth, distances, price moves."""
    W, H = dims
    img = new_slide(W, H, C)
    draw = ImageDraw.Draw(img)
    content_w = W - MARGIN * 2

    font = F["stat"]
    if draw.textlength(slide["stat"], font=font) > content_w:
        font = F["stat_sm"]

    label_h = measure(draw, slide.get("text", ""), F["body"], content_w, 1.30) if slide.get("text") else 0
    title_h = line_height(F["title_sm"], 1.16) if slide.get("title") else 0
    block = line_height(font, 1.0) + 40 + title_h + label_h
    y = MARGIN + 40 + max(0, ((H - FOOTER_H - MARGIN - 40) - (MARGIN + 40) - block) // 2)

    if slide.get("eyebrow"):
        draw.text((MARGIN, y - 56), slide["eyebrow"].upper(), font=F["eyebrow"],
                  fill=hex_to_rgb(C["brick"]))

    draw.text((MARGIN, y), slide["stat"], font=font, fill=hex_to_rgb(C["brick"]))
    y += line_height(font, 1.0)
    draw_swash(draw, MARGIN, y + 6, min(content_w, draw.textlength(slide["stat"], font=font)),
               hex_to_rgb(C["brick"]))
    y += 46

    if slide.get("title"):
        draw.text((MARGIN, y), slide["title"], font=F["title_sm"], fill=hex_to_rgb(C["black"]))
        y += line_height(F["title_sm"], 1.16)

    if slide.get("text"):
        lines = wrap_accented(draw, slide["text"], F["body"], content_w)
        draw_accented(draw, lines, (MARGIN, y + 8), F["body"],
                      hex_to_rgb("#3B2E28"), hex_to_rgb(C["brick"]), factor=1.30)

    img = corner_wedge(img, C)
    draw = ImageDraw.Draw(img)
    draw_footer(img, draw, F, C, brand, W, H, index, total)
    return img


RENDERERS = {"hook": render_hook, "body": render_body, "cta": render_cta,
             "photo": render_photo, "stat": render_stat}


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def validate(cfg):
    errs = []
    slides = cfg.get("slides", [])
    if not 5 <= len(slides) <= 10:
        errs.append(f"need 5-10 slides, got {len(slides)}")
    if not slides or slides[0].get("type") != "hook":
        errs.append("slide 1 must be type 'hook'")
    if not slides or slides[-1].get("type") != "cta":
        errs.append("last slide must be type 'cta'")
    for i, s in enumerate(slides, 1):
        if s.get("type") not in RENDERERS:
            errs.append(f"slide {i}: unknown type {s.get('type')!r}")
        if s.get("type") == "stat" and not s.get("stat"):
            errs.append(f"slide {i}: type 'stat' needs a \"stat\" value")
        if s.get("type") == "photo" and not s.get("image"):
            errs.append(f"slide {i}: type 'photo' needs an image (falls back to body)")
        if s.get("bullets") and len(s["bullets"]) > 4:
            errs.append(f"slide {i}: {len(s['bullets'])} bullets, max 4")
    return errs


def main():
    ap = argparse.ArgumentParser(description="Render a True Homes carousel.")
    ap.add_argument("carousel", help="directory holding config.json")
    ap.add_argument("--format", choices=["ig", "tiktok", "both"], default="both")
    ap.add_argument("--slide", type=int, help="re-render one slide only")
    ap.add_argument("--validate", action="store_true", help="check config, render nothing")
    args = ap.parse_args()

    carousel_dir = Path(args.carousel)
    with open(carousel_dir / "config.json") as f:
        cfg = json.load(f)

    errs = validate(cfg)
    if errs:
        print("Config problems:")
        for e in errs:
            print("  -", e)
        sys.exit(1)
    if args.validate:
        print(f"Config OK — {len(cfg['slides'])} slides.")
        return

    brand = load_brand()
    C = {k: v["hex"] for k, v in brand["colors"].items()}
    F = load_fonts()
    slides = cfg["slides"]
    total = len(slides)

    formats = ["ig", "tiktok"] if args.format == "both" else [args.format]
    for fmt in formats:
        dims = FORMATS[fmt]
        out_dir = carousel_dir / fmt
        out_dir.mkdir(parents=True, exist_ok=True)
        for i, slide in enumerate(slides, 1):
            if args.slide and i != args.slide:
                continue
            fn = RENDERERS[slide.get("type", "body")]
            im = fn(cfg, slide, F, C, brand, dims, carousel_dir, i, total)
            path = out_dir / f"slide_{i:02d}.png"
            im.save(path, "PNG")
            print(f"  {fmt:6s} {path.name}  ({slide.get('type')})")

    print(f"\nRendered {total} slides "
          f"x {len(formats)} format(s) -> {carousel_dir}")
    if cfg.get("verify"):
        print("\nVERIFY BEFORE POSTING — factual claims in this carousel:")
        for v in cfg["verify"]:
            print(f"  [ ] {v}")


if __name__ == "__main__":
    main()
