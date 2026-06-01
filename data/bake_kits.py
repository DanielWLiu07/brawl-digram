"""Emit data/kits.json — wiki-grounded kit prose per brawler, keyed by hash.
Source is the WIKI dict in build_brawler_kits_md.py."""

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "data"))
from build_brawler_kits_md import WIKI  # noqa: E402

BRAWLIFY = REPO / "data" / "brawlify" / "brawlers.json"
OUT = REPO / "data" / "kits.json"

brawlify = json.loads(BRAWLIFY.read_text())["data"]["list"]

kits = {}
missing = []
for b in brawlify:
    entry = WIKI.get(b["name"])
    if not entry:
        missing.append(b["name"])
        continue
    kits[b["hash"]] = {
        "name":    b["name"],
        "class":   entry.get("class"),
        "attack":  entry.get("attack"),
        "super":   entry.get("super"),
        "hyper":   entry.get("hyper"),
        "stars":   entry.get("stars", []),
        "gadgets": entry.get("gadgets", []),
        "quirks":  entry.get("quirks", []),
    }

OUT.write_text(json.dumps({"kits": kits}, indent=2, ensure_ascii=False))
print(f"wrote {OUT.relative_to(REPO)} — {len(kits)} brawlers")
if missing:
    print(f"  no WIKI entry: {missing}")
