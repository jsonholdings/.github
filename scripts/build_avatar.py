#!/usr/bin/env python3
"""Build the JSON Holdings org avatar from its single SVG source.

    python3 scripts/build_avatar.py           # (re)build assets/avatar.png
    python3 scripts/build_avatar.py --check    # exit 1 if avatar.png is stale, 0 if current

Swap the logo by replacing ONE file:
    1. Replace assets/avatar-source.svg with the new mark.
    2. Run `python3 scripts/build_avatar.py`.
    3. Upload the regenerated assets/avatar.png in GitHub org Settings -> Profile picture
       (there is no API for an org avatar -- this step is always manual).

Never compares PNG bytes to decide staleness -- the renderer (rsvg-convert, a different
version, a different machine) can legitimately produce a different but equally correct
PNG for the same source. Staleness is decided from a sha256 of the SOURCE svg, recorded
in a manifest next to the PNG; the PNG is stale if that hash no longer matches, or if the
PNG file is simply missing or older than the source on disk (a belt-and-braces check for
a manifest that was itself hand-edited or partially committed).
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(HERE, "assets", "avatar-source.svg")
OUTPUT = os.path.join(HERE, "assets", "avatar.png")
MANIFEST = os.path.join(HERE, "assets", "avatar.manifest.json")

SIZE = 500          # GitHub's own recommended minimum for an org avatar
PAD_FRACTION = 0.12  # fraction of SIZE left as padding on each side


def source_hash():
    return hashlib.sha256(open(SOURCE, "rb").read()).hexdigest()


def source_background():
    """The source's own outer <rect fill="..."> -- the brand's background colour,
    taken from the source rather than hardcoded, so a redrawn mark with a different
    background is picked up automatically."""
    text = open(SOURCE, encoding="utf-8").read()
    m = re.search(r'<rect\b[^>]*\bfill="([^"]+)"', text)
    if not m:
        raise SystemExit("avatar-source.svg has no <rect fill=\"...\"> to read a "
                          "background colour from -- add one or update this script")
    return m.group(1)


def build():
    bg = source_background()
    pad = round(SIZE * PAD_FRACTION)
    inner = SIZE - 2 * pad
    wrapper = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{SIZE}" height="{SIZE}" '
        f'viewBox="0 0 {SIZE} {SIZE}">'
        f'<rect width="{SIZE}" height="{SIZE}" fill="{bg}"/>'
        f'<image href="avatar-source.svg" x="{pad}" y="{pad}" width="{inner}" height="{inner}"/>'
        f'</svg>'
    )
    # Written into assets/ (not a scratch dir) so the relative <image href> resolves
    # against avatar-source.svg's own directory, then removed immediately after.
    fd, tmp_path = tempfile.mkstemp(suffix=".svg", dir=os.path.dirname(SOURCE))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(wrapper)
        proc = subprocess.run(
            ["rsvg-convert", "-w", str(SIZE), "-h", str(SIZE), "-o", OUTPUT, tmp_path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if proc.returncode != 0:
            raise SystemExit("rsvg-convert failed: %s" % proc.stderr.strip())
    finally:
        os.remove(tmp_path)
    json.dump({"source_sha256": source_hash(), "size": SIZE}, open(MANIFEST, "w"), indent=2)
    print("wrote %s (%dx%d) from %s" % (OUTPUT, SIZE, SIZE, os.path.basename(SOURCE)))


def check():
    if not os.path.isfile(OUTPUT) or not os.path.isfile(MANIFEST):
        print("STALE: avatar.png or its manifest is missing")
        return 1
    manifest = json.load(open(MANIFEST))
    if manifest.get("source_sha256") != source_hash():
        print("STALE: avatar-source.svg has changed since avatar.png was built "
              "-- run scripts/build_avatar.py")
        return 1
    if os.path.getmtime(OUTPUT) < os.path.getmtime(SOURCE):
        print("STALE: avatar.png is older than avatar-source.svg on disk")
        return 1
    print("avatar.png is current")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    if args.check:
        sys.exit(check())
    build()


if __name__ == "__main__":
    main()
