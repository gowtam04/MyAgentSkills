#!/usr/bin/env python3
"""
Fix Excalidraw files that store text directly on shape elements.

Some diagram generators (including excalidraw-diagram-generator) store text
properties (text, fontSize, fontFamily, textAlign, verticalAlign) directly on
container elements (rectangles, ellipses, diamonds). The standard Excalidraw
format uses separate text elements linked via containerId/boundElements.

excalirender only renders text in the standard format, so this script converts
the non-standard format to standard before rendering.

Usage:
    python fix-bound-text.py input.excalidraw [-o output.excalidraw]

If -o is omitted, writes to <input>.fixed.excalidraw
"""

import json
import sys
import argparse
import uuid
import hashlib


def generate_id(seed_text):
    """Generate a deterministic short ID from seed text."""
    h = hashlib.md5(seed_text.encode()).hexdigest()[:8]
    return f"txt_{h}"


def fix_bound_text(data):
    """Convert direct text on shapes to proper bound text elements."""
    elements = data.get("elements", [])
    new_elements = []
    modified = 0

    for el in elements:
        el_type = el.get("type")
        el_text = el.get("text")

        # Only process container types that have text directly on them
        if el_type in ("rectangle", "ellipse", "diamond") and el_text:
            container_id = el.get("id")

            # Create a bound text element
            text_id = generate_id(f"{container_id}_text")

            # Calculate text position (centered in container)
            cx = el.get("x", 0) + el.get("width", 100) / 2
            cy = el.get("y", 0) + el.get("height", 50) / 2

            font_size = el.get("fontSize", 16)
            font_family = el.get("fontFamily", 5)

            # Estimate text dimensions
            lines = el_text.split("\n")
            max_line_len = max(len(line) for line in lines)
            text_width = min(max_line_len * font_size * 0.6, el.get("width", 100) - 10)
            text_height = len(lines) * font_size * 1.35

            text_element = {
                "id": text_id,
                "type": "text",
                "x": cx - text_width / 2,
                "y": cy - text_height / 2,
                "width": text_width,
                "height": text_height,
                "angle": el.get("angle", 0),
                "strokeColor": el.get("strokeColor", "#1e1e1e"),
                "backgroundColor": "transparent",
                "fillStyle": "solid",
                "strokeWidth": 1,
                "strokeStyle": "solid",
                "roughness": el.get("roughness", 0),
                "opacity": el.get("opacity", 100),
                "groupIds": el.get("groupIds", []),
                "frameId": el.get("frameId"),
                "index": el.get("index", "a0"),
                "roundness": None,
                "seed": abs(hash(text_id)) % (2**31),
                "version": 1,
                "versionNonce": abs(hash(text_id + "v")) % (2**31),
                "isDeleted": False,
                "boundElements": None,
                "updated": el.get("updated", 1706659200000),
                "link": None,
                "locked": False,
                "text": el_text,
                "rawText": el_text,
                "fontSize": font_size,
                "fontFamily": font_family,
                "textAlign": el.get("textAlign", "center"),
                "verticalAlign": el.get("verticalAlign", "middle"),
                "containerId": container_id,
                "originalText": el_text,
                "autoResize": True,
                "lineHeight": 1.25,
            }

            # Update the container to reference the new text element
            bound_elements = el.get("boundElements") or []
            bound_elements.append({"type": "text", "id": text_id})
            el["boundElements"] = bound_elements

            # Remove text properties from the container
            for key in ("text", "fontSize", "fontFamily", "textAlign", "verticalAlign", "originalText", "rawText"):
                el.pop(key, None)

            new_elements.append(el)
            new_elements.append(text_element)
            modified += 1
        else:
            new_elements.append(el)

    data["elements"] = new_elements
    return data, modified


def main():
    parser = argparse.ArgumentParser(description="Fix Excalidraw bound text format")
    parser.add_argument("input", help="Input .excalidraw file")
    parser.add_argument("-o", "--output", help="Output file (default: <input>.fixed.excalidraw)")
    args = parser.parse_args()

    with open(args.input) as f:
        data = json.load(f)

    data, modified = fix_bound_text(data)

    output_path = args.output or args.input.replace(".excalidraw", ".fixed.excalidraw")
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Fixed {modified} elements with direct text -> bound text")
    print(f"Output: {output_path}")


if __name__ == "__main__":
    main()
