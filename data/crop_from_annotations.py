"""Crop an atlas PNG into named sprite PNGs using rectangles from the
atlas annotator (prototype/atlas_annotator.html).

Usage:
  python3 data/crop_from_annotations.py <annotations.json> [out_dir]

Where annotations.json is the JSON the annotator exports — e.g. pipe in
via `pbpaste > /tmp/level.json` after pressing Copy JSON in the browser.
"""

import json
import sys
from pathlib import Path
from PIL import Image

REPO = Path(__file__).resolve().parent.parent


def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    ann_path = Path(sys.argv[1])
    out_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else (REPO / "data" / "named_tiles")
    out_dir.mkdir(parents=True, exist_ok=True)

    data = json.loads(ann_path.read_text())
    atlas_path = REPO / "data" / "sc_textures" / data["atlas"]
    if not atlas_path.exists():
        sys.exit(f"atlas not found at {atlas_path}")

    img = Image.open(atlas_path).convert("RGBA")
    used_names = {}
    for r in data["rects"]:
        name = r["name"] or f"unnamed_{r['x']}x{r['y']}"
        used_names[name] = used_names.get(name, 0) + 1
        if used_names[name] > 1:
            name = f"{name}_{used_names[name]}"
        crop = img.crop((r["x"], r["y"], r["x"] + r["w"], r["y"] + r["h"]))
        out_path = out_dir / f"{name}.png"
        crop.save(out_path)
        print(f"  {name}.png  ({r['w']}x{r['h']})")

    print(f"\nwrote {len(data['rects'])} crops to {out_dir.relative_to(REPO)}/")


if __name__ == "__main__":
    main()
