#!/usr/bin/env python3
"""Build a labelled contact sheet so a folder of photos can be reviewed at a glance."""
import sys, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
try:
    import pillow_heif; pillow_heif.register_heif_opener()
except ImportError: pass

src = Path(sys.argv[1]); out = Path(sys.argv[2])
cols = int(sys.argv[3]) if len(sys.argv) > 3 else 4
CELL, LABEL, PAD = 420, 30, 8
files = sorted([p for p in src.iterdir()
                if p.suffix.lower() in ('.jpg','.jpeg','.png','.heic')])
rows = math.ceil(len(files)/cols)
sheet = Image.new("RGB",(cols*(CELL+PAD)+PAD, rows*(CELL+LABEL+PAD)+PAD),(28,22,20))
d = ImageDraw.Draw(sheet)
try:
    f = ImageFont.truetype("render/fonts/SourceSans3.ttf", 21); f.set_variation_by_name("SemiBold")
except Exception:
    f = ImageFont.load_default()
for i,p in enumerate(files):
    try:
        im = ImageOps.exif_transpose(Image.open(p)).convert("RGB")
    except Exception as e:
        print("skip", p.name, e); continue
    im.thumbnail((CELL,CELL), Image.LANCZOS)
    x = PAD + (i%cols)*(CELL+PAD); y = PAD + (i//cols)*(CELL+LABEL+PAD)
    sheet.paste(im, (x+(CELL-im.width)//2, y+(CELL-im.height)//2))
    d.text((x+2, y+CELL+4), f"{i+1}. {p.stem}", font=f, fill=(232,196,182))
sheet.save(out, quality=88)
print(f"{len(files)} photos -> {out} ({sheet.size[0]}x{sheet.size[1]})")
