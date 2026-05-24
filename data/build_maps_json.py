"""Decode `csv_logic/maps.csv` into a single JSON the frontend can import.

`maps.csv` encodes each map as N consecutive rows: row 0 has the internal name
in column "Map" plus the first tile-row in "Data"; rows 1..N-1 have an empty
Map column and a Data row. Some rows also carry a JSON "MetaData" payload
(Siege turret positions, etc.) on either the first or a later line.

Tile codes come from `tiles.csv`. Codes appearing in `maps.csv` that aren't in
`tiles.csv` (numeric spawn markers `0-9`, exotic markers like `!`/`+`/`<`/`>`
that overlay on walkable tiles) are passed through as-is — they're positional
labels, not tile types. Consumer code should treat anything not in the
legend as walkable.

Outputs:
  data/maps.json
    Ranked-pool maps only (filtered by mode prefix → likelyRanked flag),
    pretty-printed for review. ~2-3 MB. This is what the frontend imports.

  data/maps-all.json
    Every map in the CSV, compact (no indent) for size. ~9 MB, for tooling /
    KB-curation workflows that need the full corpus.

  Common schema:
    {
      fetchedAt, source, version,
      tileLegend: { char: { name, blocksMovement, blocksProjectiles,
                            isForest, isDestructible, ... } },
      maps: { <internalName>: { width, height, mode, brawlifyMode,
                                likelyRanked, grid: [str, str, ...],
                                metadata?: parsed-JSON } }
    }

  data/map_name_map.json (seed only — needs hand-curation)
    {
      modeMap: { CSVPrefix -> Brawlify gameMode.name },   # editable
      maps:    { <BrawlifyHash> -> <internalCSVName> }    # empty placeholder
    }
"""

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
OUT_NAME_MAP = REPO / "data" / "map_name_map.json"
BRAWLIFY_MAPS = REPO / "data" / "brawlify" / "maps.json"

# Heuristic bridge from CSV name prefix (mode slug) -> Brawlify gameMode.name.
# Built from observation; revise if Brawlify renames modes.
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

# Canonical Brawl Stars ranked modes (the "comp pool" that rotates per season).
# Used to flag maps in the output even when Brawlify's /v1/events is empty.
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
    """Read tiles.csv into a {tileCode: metadata} dict. Skips codes that
    are blank (e.g. ExtraBush) since those are dynamically painted."""
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
            # Many tiles share `.` (Open, SpawnPoint*, Base, Teleport*, etc.).
            # Keep the first; record overloaded codes for transparency.
            if code in legend:
                legend[code].setdefault("aliases", []).append(name)
            else:
                legend[code] = entry
    return legend


def parse_maps_csv():
    """Group maps.csv rows by map name. Returns {name: {grid, metadata}}."""
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
            # flush previous map's metadata before switching
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

    # parse the metadata JSON best-effort
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


def load_brawlify_index():
    if not BRAWLIFY_MAPS.exists():
        return []
    payload = json.loads(BRAWLIFY_MAPS.read_text())
    return (payload.get("data") or {}).get("list") or []


def seed_name_map(maps_internal, brawlify_maps):
    """Produce a placeholder bridge file with the mode-prefix mapping populated
    and an empty per-map dictionary the user can fill in by hand. Also pre-
    fills any obvious matches where the Brawlify hash slug equals the internal
    name (rare but happens for some test maps)."""
    obvious = {}
    internal_lower = {n.lower(): n for n in maps_internal}
    for bm in brawlify_maps:
        h = (bm.get("hash") or "").lower().replace("-", "")
        if h in internal_lower:
            obvious[bm["hash"]] = internal_lower[h]
    return {
        "fetchedAt": utc_now_iso(),
        "note": "Hand-curated bridge from Brawlify display names to internal CSV names. modeMap is heuristic; maps is mostly empty and must be filled in by the maintainer or pro-curator.",
        "modeMap": DEFAULT_MODE_MAP,
        "maps": obvious,
    }


def run():
    print("Reading tiles.csv legend...")
    legend = load_tile_legend()
    print(f"  {len(legend)} static tile codes")

    print("Parsing maps.csv...")
    maps = parse_maps_csv()
    print(f"  {len(maps)} maps with non-empty grids")

    brawlify_maps = load_brawlify_index()
    print(f"  {len(brawlify_maps)} Brawlify catalog entries available for cross-ref")

    # Annotate ranked-likely maps via mode prefix heuristic.
    ranked_count = 0
    for name, m in maps.items():
        bf_mode = DEFAULT_MODE_MAP.get(m["mode"])
        m["brawlifyMode"] = bf_mode
        m["likelyRanked"] = bf_mode in RANKED_MODES
        if m["likelyRanked"]:
            ranked_count += 1
    print(f"  {ranked_count} maps flagged as likelyRanked via mode heuristic")

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

    name_map = seed_name_map(maps, brawlify_maps)
    OUT_NAME_MAP.write_text(json.dumps(name_map, indent=2, ensure_ascii=False))
    print(f"  wrote {OUT_NAME_MAP.relative_to(REPO)} ({len(name_map['maps'])} obvious matches; manual curation needed for the rest)")
    return 0


if __name__ == "__main__":
    sys.exit(run())
