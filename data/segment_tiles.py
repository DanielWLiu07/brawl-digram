"""Segment level.sc texture atlas into per-tile PNGs.
Writes:
  data/tile_sprites/tile_NNN_WxH.png   — one crop per region
  data/tile_sprites/_manifest.json     — atlas coordinates per crop, for a
                                         later 'merge bad cuts' cleanup pass
"""

import json
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage
from skimage.segmentation import watershed
from skimage.feature import peak_local_max

REPO = Path(__file__).resolve().parent.parent
ATLAS = Path("/tmp/bd_apk_check/tiles/level_tex_0_886x1792.png")
OUT_DIR = REPO / "data" / "tile_sprites"
OUT_DIR.mkdir(parents=True, exist_ok=True)
for f in OUT_DIR.glob("*.png"): f.unlink()

atlas = Image.open(ATLAS).convert("RGBA")
arr = np.array(atlas)
mask = arr[..., 3] > 128
dist = ndimage.distance_transform_edt(mask)

peaks = peak_local_max(dist, min_distance=40, threshold_abs=12,
                       exclude_border=False, labels=mask.astype(int))
markers = np.zeros_like(dist, dtype=np.int32)
for i, (y, x) in enumerate(peaks, 1):
    markers[y, x] = i
labels = watershed(-dist, markers, mask=mask)

manifest = []
for i, sl in enumerate(ndimage.find_objects(labels), 1):
    if sl is None: continue
    y0, y1 = sl[0].start, sl[0].stop
    x0, x1 = sl[1].start, sl[1].stop
    w, h = x1 - x0, y1 - y0
    region = (labels[y0:y1, x0:x1] == i)
    if region.sum() < 800 or w < 28 or h < 28: continue
    sub = arr[y0:y1, x0:x1].copy()
    sub[..., 3] = np.where(region, sub[..., 3], 0).astype(np.uint8)
    name = f"tile_{len(manifest):03d}_{w}x{h}.png"
    Image.fromarray(sub).save(OUT_DIR / name)
    manifest.append({
        "name": name,
        "atlas_x": int(x0),
        "atlas_y": int(y0),
        "width":   int(w),
        "height":  int(h),
        "label":   int(i),
        "pixels":  int(region.sum()),
    })

(OUT_DIR / "_manifest.json").write_text(json.dumps({
    "source": "level_tex_0_886x1792.png",
    "atlas_width":  int(arr.shape[1]),
    "atlas_height": int(arr.shape[0]),
    "method": "alpha>128 mask, distance-transform + watershed, peak min_distance=40, threshold_abs=12",
    "sprites": manifest,
}, indent=2))

print(f"wrote {len(manifest)} sprites + _manifest.json")
