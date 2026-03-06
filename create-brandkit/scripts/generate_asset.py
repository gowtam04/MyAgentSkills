#!/usr/bin/env python3
"""Generate a brand asset via the BrandKit API.

Submits a generation job, polls until complete, decodes the base64 image,
and saves it to the specified output path. Optionally resizes to multiple
sizes and generates .ico files.

Usage:
    python3 generate_asset.py --prompt "..." --output ./logo.png [options]

    # Multi-size favicon with .ico:
    python3 generate_asset.py --prompt "..." --output ./public/favicon.png \
        --width 512 --height 512 --background transparent \
        --sizes 16,32,180,192,512 --ico
"""

import argparse
import base64
import io
import json
import os
import struct
import sys
import time
import urllib.error
import urllib.request

API_BASE = "https://brandkit-api.fly.dev"
POLL_INTERVAL = 3  # seconds between polls
MAX_POLLS = 120  # give up after ~6 minutes


def api_post(path: str, data: dict) -> dict:
    url = f"{API_BASE}{path}"
    body = json.dumps(data).encode()
    req = urllib.request.Request(
        url, data=body, headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def api_get(path: str) -> dict:
    url = f"{API_BASE}{path}"
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def submit_job(prompt: str, width: int, height: int, fmt: str, background: str) -> str:
    payload = {
        "prompt": prompt,
        "width": width,
        "height": height,
        "format": fmt,
        "background": background,
    }
    print("Submitting generation job...")
    result = api_post("/generate", payload)
    job_id = result["job_id"]
    print(f"Job created: {job_id}")
    return job_id


def poll_job(job_id: str) -> dict:
    poll_url = f"/jobs/{job_id}"
    for i in range(MAX_POLLS):
        result = api_get(poll_url)
        status = result["status"]

        if status == "completed":
            print("\nGeneration completed.")
            return result
        elif status == "failed":
            error = result.get("error", {})
            msg = error.get("message", "Unknown error")
            code = error.get("error_code", "unknown")
            retryable = error.get("retryable", False)
            print(f"Generation failed: [{code}] {msg}", file=sys.stderr)
            if retryable:
                print("This error is retryable.", file=sys.stderr)
            else:
                action = error.get("suggested_action", "")
                if action:
                    print(f"Suggested action: {action}", file=sys.stderr)
            sys.exit(1)
        else:
            if i == 0:
                print(f"Status: {status} — waiting for completion", end="", flush=True)
            else:
                print(".", end="", flush=True)
            time.sleep(POLL_INTERVAL)

    print(f"\nTimed out waiting for job {job_id}", file=sys.stderr)
    sys.exit(1)


def save_image(image_data_b64: str, output_path: str):
    image_bytes = base64.b64decode(image_data_b64)
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(image_bytes)
    print(f"Saved {len(image_bytes)} bytes to {output_path}")
    return image_bytes


def resize_image(image_bytes: bytes, size: int, fmt: str) -> bytes:
    """Resize image to size x size using Pillow."""
    try:
        from PIL import Image
    except ImportError:
        print("Pillow is required for --sizes. Install with: pip install Pillow", file=sys.stderr)
        sys.exit(1)

    img = Image.open(io.BytesIO(image_bytes))
    img = img.resize((size, size), Image.LANCZOS)
    output = io.BytesIO()
    pil_format = "PNG" if fmt == "png" else "WEBP"
    img.save(output, format=pil_format)
    return output.getvalue()


def generate_sizes(image_bytes: bytes, output_path: str, sizes: list[int], fmt: str) -> list[str]:
    """Generate resized copies at each specified size. Returns list of created file paths."""
    base, ext = os.path.splitext(output_path)
    created = []
    for size in sizes:
        resized = resize_image(image_bytes, size, fmt)
        size_path = f"{base}-{size}x{size}{ext}"
        with open(size_path, "wb") as f:
            f.write(resized)
        print(f"Saved {len(resized)} bytes to {size_path} ({size}x{size})")
        created.append(size_path)
    return created


def generate_ico(image_bytes: bytes, output_path: str):
    """Generate a .ico file containing 16x16 and 32x32 versions."""
    try:
        from PIL import Image
    except ImportError:
        print("Pillow is required for --ico. Install with: pip install Pillow", file=sys.stderr)
        sys.exit(1)

    img = Image.open(io.BytesIO(image_bytes))

    base, _ = os.path.splitext(output_path)
    ico_path = f"{base}.ico"

    img_16 = img.resize((16, 16), Image.LANCZOS)
    img_32 = img.resize((32, 32), Image.LANCZOS)

    img_32.save(ico_path, format="ICO", sizes=[(16, 16), (32, 32)],
                append_images=[img_16])
    ico_size = os.path.getsize(ico_path)
    print(f"Saved {ico_size} bytes to {ico_path} (ICO 16x16 + 32x32)")


def main():
    parser = argparse.ArgumentParser(description="Generate a brand asset via BrandKit API")
    parser.add_argument("--prompt", required=True, help="Image generation prompt")
    parser.add_argument("--output", required=True, help="Output file path")
    parser.add_argument("--width", type=int, default=1024, help="Image width (512-4096, default 1024)")
    parser.add_argument("--height", type=int, default=1024, help="Image height (512-4096, default 1024)")
    parser.add_argument("--format", dest="fmt", default="png", choices=["png", "webp"], help="Output format (default png)")
    parser.add_argument("--background", default="opaque", choices=["transparent", "opaque"], help="Background type (default opaque)")
    parser.add_argument("--sizes", default=None, help="Comma-separated list of sizes to resize to (e.g., 16,32,180,192,512)")
    parser.add_argument("--ico", action="store_true", help="Also generate a .ico file (requires --sizes with 16 and 32)")
    args = parser.parse_args()

    sizes = None
    if args.sizes:
        sizes = [int(s.strip()) for s in args.sizes.split(",")]

    if args.ico and (not sizes or 16 not in sizes or 32 not in sizes):
        print("--ico requires --sizes to include 16 and 32", file=sys.stderr)
        sys.exit(1)

    try:
        job_id = submit_job(args.prompt, args.width, args.height, args.fmt, args.background)
        result = poll_job(job_id)
        img = result["result"]
        image_bytes = save_image(img["image_data"], args.output)
        print(f"Asset: {img['width']}x{img['height']} {img['format']}, {img['size_bytes']} bytes")

        if sizes:
            generate_sizes(image_bytes, args.output, sizes, args.fmt)

        if args.ico:
            generate_ico(image_bytes, args.output)

    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        print(f"API error {e.code}: {body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Connection error: {e.reason}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
