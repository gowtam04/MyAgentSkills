#!/usr/bin/env python3
"""Quick QA for game art: size, alpha, palette adherence, opaque bounds, and a contact sheet.

Usage:
  python3 asset_qa.py img1.png [img2.png ...] [--palette palette.json] [--sheet out.png]
                      [--scale 4] [--bg "#1d1d27"] [--tolerance 0]

palette.json may be a list of hex strings, a {name: hex} object, or {"colors": [...]}
(values may also be {"hex": "#..."} objects). Fully transparent pixels are ignored for
palette checks. SVG inputs are skipped with a note - rasterize them first.
Requires Pillow (pip install pillow).
"""
import argparse
import json
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw
except ImportError:
    sys.exit("Pillow is not installed (pip install pillow). Do the checks manually and say so in your report.")


def hex_to_rgb(h):
    h = h.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def load_palette(path):
    data = json.loads(Path(path).read_text())
    if isinstance(data, dict) and "colors" in data:
        data = data["colors"]
    values = data.values() if isinstance(data, dict) else data
    out = []
    for v in values:
        if isinstance(v, dict):
            v = v.get("hex") or v.get("value")
        if isinstance(v, str) and v.strip().startswith("#"):
            out.append(hex_to_rgb(v))
    return out


def near(c, palette, tol):
    return any(all(abs(a - b) <= tol for a, b in zip(c, p)) for p in palette)


def analyze(path, palette, tol):
    img = Image.open(path).convert("RGBA")
    w, h = img.size
    counts = img.getcolors(maxcolors=w * h) or []
    opaque = [(n, c) for n, c in counts if c[3] > 0]
    has_alpha = any(c[3] < 255 for _, c in counts)
    partial_alpha = sum(n for n, c in counts if 0 < c[3] < 255)
    report = {
        "file": str(path),
        "size": f"{w}x{h}",
        "has_transparency": has_alpha,
        "semi_transparent_px": partial_alpha,
        "unique_opaque_colors": len({c[:3] for _, c in opaque}),
        "opaque_bbox": img.getchannel("A").getbbox(),
    }
    if palette:
        total = sum(n for n, _ in opaque) or 1
        off = [(n, c[:3]) for n, c in opaque if not near(c[:3], palette, tol)]
        off_px = sum(n for n, _ in off)
        report["off_palette_px"] = off_px
        report["off_palette_pct"] = round(100 * off_px / total, 2)
        report["top_off_palette_colors"] = [
            "#%02x%02x%02x" % c for _, c in sorted(off, reverse=True)[:5]
        ]
    return img, report


def contact_sheet(images, out, scale, bg):
    pad = 8 * scale
    label_h = 14
    cells = [im.resize((im.width * scale, im.height * scale), Image.NEAREST) for _, im in images]
    cols = min(len(cells), 6)
    rows = (len(cells) + cols - 1) // cols
    cw = max(c.width for c in cells) + pad
    ch = max(c.height for c in cells) + pad + label_h
    sheet = Image.new("RGBA", (cols * cw + pad, rows * ch + pad), bg + (255,))
    draw = ImageDraw.Draw(sheet)
    for i, ((name, _), cell) in enumerate(zip(images, cells)):
        x = pad + (i % cols) * cw
        y = pad + (i // cols) * ch
        sheet.alpha_composite(cell, (x, y))
        draw.text((x, y + cell.height + 2), Path(name).name[:28], fill=(230, 230, 230, 255))
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("images", nargs="+")
    ap.add_argument("--palette")
    ap.add_argument("--sheet", help="write a contact sheet PNG here")
    ap.add_argument("--scale", type=int, default=4, help="nearest-neighbor upscale for the sheet")
    ap.add_argument("--bg", default="#1d1d27", help="sheet background (use the game's background color)")
    ap.add_argument("--tolerance", type=int, default=0, help="per-channel tolerance for palette matching")
    args = ap.parse_args()

    palette = load_palette(args.palette) if args.palette else []
    if args.palette and not palette:
        print(f"warning: no colors parsed from {args.palette}")
    loaded, reports = [], []
    for p in args.images:
        if p.lower().endswith(".svg"):
            reports.append({"file": p, "note": "SVG skipped - rasterize to PNG first"})
            continue
        try:
            img, rep = analyze(p, palette, args.tolerance)
        except Exception as e:  # keep going so one bad file doesn't hide the rest
            reports.append({"file": p, "error": str(e)})
            continue
        loaded.append((p, img))
        reports.append(rep)
    for r in reports:
        print(json.dumps(r))
    if args.sheet and loaded:
        print("contact_sheet:", contact_sheet(loaded, args.sheet, args.scale, hex_to_rgb(args.bg)))


if __name__ == "__main__":
    main()
