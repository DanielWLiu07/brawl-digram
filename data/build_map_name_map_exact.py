#!/usr/bin/env python3
"""Rebuild map_name_map.json with an EXACT join (replaces the positional guess).

Supercell instance IDs are classId*1000000 + row index, so Brawlify map id
15000005 IS row 5 of csv_logic/locations.csv, whose `Map` column names the
internal grid (e.g. Wanted_7). Verified visually 2026-06-10: Shooting Star
(15000005) -> Wanted_7 and Hideout (15000022) -> Wanted_8 grids match the
official map images. The old heuristic bridge ("Nth map of same mode") had
swaps — e.g. it mapped Shooting Star to Wanted_6, which is actually a
forest-heavy grid.

Keeps the existing file shape ({fetchedAt, modeMap, maps: {slug: internal}})
so whiteboard.html keeps working unchanged.
"""

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / "map_name_map.json"


def main():
    rows = list(csv.reader(open(HERE / "csv_logic" / "locations.csv")))
    hdr, data = rows[0], rows[2:]
    i_map = hdr.index("Map")

    old = json.load(open(OUT))
    grids = set(json.load(open(HERE / "maps.json"))["maps"])

    bl = json.load(open(HERE / "brawlify" / "maps.json"))["data"]
    bl_list = bl["list"] if isinstance(bl, dict) and "list" in bl else bl

    entries, missing_row, missing_grid = [], 0, 0
    seen_active = set()
    # active entries win over retired duplicates of the same display slug
    for m in sorted(bl_list, key=lambda m: m.get("disabled", False)):
        if m["hash"] in seen_active:
            continue
        if not m.get("disabled"):
            seen_active.add(m["hash"])
        idx = m["id"] - 15000000
        if not (0 <= idx < len(data)):
            missing_row += 1
            continue
        internal = data[idx][i_map]
        if not internal:
            missing_row += 1
            continue
        if internal not in grids:
            missing_grid += 1
            continue
        entries.append((m["hash"], internal, not m.get("disabled", False), m["id"]))
    # Several display maps can share one grid (seasonal reskins: Ice Block Rock
    # reuses Hard Rock Mine's Gemgrab_1). Consumers invert slug->internal with
    # last-write-wins, so order entries least-preferred-first: the LAST slug
    # per internal is the active one with the lowest (most canonical) id.
    entries.sort(key=lambda e: (e[2], -e[3]))
    maps = {slug: internal for slug, internal, _a, _i in entries}

    out = {
        "fetchedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "method": "exact: brawlify id - 15000000 = locations.csv row -> Map column",
        "modeMap": old["modeMap"],
        "maps": maps,
    }
    OUT.write_text(json.dumps(out, indent=1))
    print(
        f"wrote {OUT.name}: {len(maps)} exact mappings "
        f"({missing_row} brawlify maps w/o csv row, {missing_grid} w/o decoded grid)"
    )
    # diff vs the old heuristic bridge
    changed = {
        s: (old["maps"].get(s), v)
        for s, v in maps.items()
        if s in old["maps"] and old["maps"][s] != v
    }
    print(f"{len(changed)} mappings corrected vs heuristic bridge, e.g.:")
    for s, (a, b) in list(changed.items())[:10]:
        print(f"  {s}: {a} -> {b}")


if __name__ == "__main__":
    main()
