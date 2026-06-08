"""Translate BrawlMapGen's preset (data/tile_sprites_official/_preset.json) into
a flat tile-code → SVG list mapping the frontend can consume.

Source assets: bloodwiing/BrawlMapGen (GPLv3 code, Supercell fan-content SVGs).
"""

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PRESET = REPO / "data" / "tile_sprites_official" / "_preset.json"
OUT = REPO / "data" / "tile_sprite_index.json"

preset = json.loads(PRESET.read_text())

tile_chars = {}
for t in preset.get("tiles", []):
    code = t.get("tileCode")
    if not code:
        continue
    assets = [tt["asset"] for tt in t.get("tileTypes", []) if tt.get("asset")]
    tile_chars[code] = {
        "name": t.get("tileName") or t.get("display"),
        "display": t.get("display"),
        "assets": assets,
        "default": assets[0] if assets else None,
    }

OUT.write_text(json.dumps({
    "source": "bloodwiing/BrawlMapGen presets/brawlstars.json",
    "license": "Code: GPLv3 (bloodwiing/BrawlMapGen). Art: Supercell IP under Fan Content Policy.",
    "ignoreTiles": preset.get("ignoreTiles", []),
    "tiles": tile_chars,
}, indent=2))
print(f"wrote {OUT.relative_to(REPO)} — {len(tile_chars)} tile codes mapped")
