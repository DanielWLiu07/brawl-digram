"""Decode maps.csv (multi-row-per-map tile grids) into maps.json + maps-all.json.
Joins with tiles.csv for per-char semantics."""

import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CSV_DIR = REPO / "data" / "csv_logic"
MAPS_CSV = CSV_DIR / "maps.csv"
TILES_CSV = CSV_DIR / "tiles.csv"
OUT_MAPS = REPO / "data" / "maps.json"
OUT_MAPS_ALL = REPO / "data" / "maps-all.json"

DEFAULT_MODE_MAP = {
    "Gemgrab":        "Gem Grab",
    "GemGrab5v5":     "Gem Grab 5v5",
    "TrioGemgrab":    "Trio Gem Grab",
    "Bankheist":      "Heist",
    "BrawlBallV2":    "Brawl Ball",
    "BrawlBall5v5":   "Brawl Ball 5v5",
    "Laserball":      "Brawl Hockey",
    "Knockout":       "Knockout",
    "Knockout5v5":    "Knockout 5v5",
    "KingOfHill":     "Hot Zone",
    "Wanted":         "Bounty",
    "Solobounty":     "Solo Bounty",
    "Survival":       "Solo Showdown",
    "DuoSurvival":    "Duo Showdown",
    "TrioSurvival":   "Trio Showdown",
    "TreasureHunt":   "Treasure Hunt",
    "Siege":          "Siege",
    "SiegeSmall":     "Siege",
    "Payload":        "Payload",
    "AirHockey":      "Brawl Hockey",
    "BasketBrawl":    "Basket Brawl",
    "VolleyBrawl":    "Volley Brawl",
    "Dribble":        "Dribble",
    "Deathmatch":     "Wipeout",
    "TagTeam":        "Duels",
    "PaintBall":      "Paint Brawl",
    "Invasion":       "Invasion",
    "BossRace":       "Boss Race",
    "CaptureTheFlag": "Capture the Flag",
}

RANKED_MODES = {
    "Gem Grab",
    "Brawl Ball",
    "Heist",
    "Hot Zone",
    "Knockout",
    "Bounty",
    "Brawl Hockey",
}


def utc_now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_tile_legend():
    legend = {}
    with TILES_CSV.open(newline="") as f:
        reader = csv.reader(f)
        headers = next(reader)
        next(reader)  # types row
        idx = {h: i for i, h in enumerate(headers)}
        for row in reader:
            if not row:
                continue
            code = row[idx["TileCode"]]
            if not code or code == "-":
                continue  # dynamic-only tiles have no static char
            name = row[idx["Name"]]
            entry = {
                "name": name,
                "blocksMovement":    row[idx["BlocksMovement"]] == "true",
                "blocksProjectiles": row[idx["BlocksProjectiles"]] == "true",
                "isDestructible":    row[idx["IsDestructible"]] == "true",
                "isForest":          row[idx["IsForest"]] == "true",
                "isBouncer":         row[idx["IsBouncer"]] == "true",
            }
            if code in legend:
                legend[code].setdefault("aliases", []).append(name)
            else:
                legend[code] = entry
    return legend


def parse_maps_csv():
    with MAPS_CSV.open(newline="") as f:
        reader = csv.reader(f)
        next(reader); next(reader)  # header + types
        rows = list(reader)

    maps = {}
    current = None
    meta_chunks = []
    for row in rows:
        if not row:
            continue
        map_col = row[0] if len(row) > 0 else ""
        data_col = row[1] if len(row) > 1 else ""
        meta_col = row[2] if len(row) > 2 else ""
        if map_col:
            if current is not None:
                maps[current]["_meta_raw"] = " ".join(meta_chunks).strip()
            current = map_col
            maps[current] = {"grid": [], "_meta_raw": ""}
            meta_chunks = []
        if current is None:
            continue
        if data_col:
            maps[current]["grid"].append(data_col)
        if meta_col:
            meta_chunks.append(meta_col)
    if current is not None:
        maps[current]["_meta_raw"] = " ".join(meta_chunks).strip()

    cleaned = {}
    for name, m in maps.items():
        if not m["grid"]:
            continue
        width = max(len(r) for r in m["grid"])
        height = len(m["grid"])
        entry = {
            "width": width,
            "height": height,
            "grid": m["grid"],
            "mode": name.split("_", 1)[0] if "_" in name else name,
        }
        if m["_meta_raw"]:
            try:
                entry["metadata"] = json.loads(m["_meta_raw"])
            except json.JSONDecodeError:
                entry["metadataRaw"] = m["_meta_raw"]
        cleaned[name] = entry
    return cleaned


def run():
    print("Reading tiles.csv legend...")
    legend = load_tile_legend()
    print(f"  {len(legend)} static tile codes")

    print("Parsing maps.csv...")
    maps = parse_maps_csv()
    print(f"  {len(maps)} maps with non-empty grids")

    ranked_count = 0
    for name, m in maps.items():
        bf_mode = DEFAULT_MODE_MAP.get(m["mode"])
        m["brawlifyMode"] = bf_mode
        m["likelyRanked"] = bf_mode in RANKED_MODES
        if m["likelyRanked"]:
            ranked_count += 1
    print(f"  {ranked_count} flagged ranked by mode prefix")

    base = {
        "fetchedAt": utc_now_iso(),
        "source": str(MAPS_CSV.relative_to(REPO)),
        "version": "v67.264 (tailsjs)",
        "tileLegend": legend,
        "rankedModes": sorted(RANKED_MODES),
    }

    ranked_only = {k: v for k, v in maps.items() if v["likelyRanked"]}
    OUT_MAPS.write_text(json.dumps({**base, "maps": ranked_only}, indent=2, ensure_ascii=False))
    print(f"  wrote {OUT_MAPS.relative_to(REPO)} ({OUT_MAPS.stat().st_size/1024:.0f} KB, {len(ranked_only)} ranked maps)")

    OUT_MAPS_ALL.write_text(json.dumps({**base, "maps": maps}, ensure_ascii=False, separators=(",", ":")))
    print(f"  wrote {OUT_MAPS_ALL.relative_to(REPO)} ({OUT_MAPS_ALL.stat().st_size/1024:.0f} KB, {len(maps)} total maps)")
    return 0


if __name__ == "__main__":
    sys.exit(run())
