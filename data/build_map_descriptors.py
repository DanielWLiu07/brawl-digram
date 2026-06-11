#!/usr/bin/env python3
"""Compute objective per-map geometry descriptors from decoded grids.

These are the map-side features for the draft-advisor weight fit (and the
grounding for "open map, long sightlines -> snipers" explanations). All
fractions are over the playable area; distances in tiles.

Output: map_descriptors.json keyed by internal map name (Gemgrab_1 ...),
with display-name aliases from map_name_map.json.
"""

import json
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / "map_descriptors.json"

MIN_SIGHTLINE = 10  # tiles of unbroken projectile path that count as "long"
CHOKE_MAX_W = 3     # passable gap narrower than this is a choke


def classify(legend):
    blocks_move, blocks_proj, bush, water, breakable = set(), set(), set(), set(), set()
    for ch, t in legend.items():
        if t["blocksMovement"]:
            blocks_move.add(ch)
        if t["blocksProjectiles"]:
            blocks_proj.add(ch)
        if t["isForest"]:
            bush.add(ch)
        if t["name"] in ("Water", "InvisibleWater"):
            water.add(ch)
        if t["isDestructible"] and t["blocksMovement"]:
            breakable.add(ch)
    return blocks_move, blocks_proj, bush, water, breakable


def descriptors(grid, sets):
    blocks_move, blocks_proj, bush, water, breakable = sets
    h, w = len(grid), len(grid[0])
    playable = [(r, c) for r in range(h) for c in range(w) if grid[r][c] != "="]
    n = len(playable) or 1

    def frac(charset):
        return round(sum(1 for r, c in playable if grid[r][c] in charset) / n, 4)

    wall_pct = frac(blocks_proj)
    bush_pct = frac(bush)
    water_pct = frac(water)
    open_pct = round(
        sum(
            1
            for r, c in playable
            if grid[r][c] not in blocks_move
            and grid[r][c] not in bush
            and grid[r][c] not in water
        )
        / n,
        4,
    )

    # Long vertical sightlines (teams spawn top/bottom on 3v3 maps): fraction
    # of columns containing an unbroken projectile path >= MIN_SIGHTLINE.
    long_cols = 0
    for c in range(w):
        run = best = 0
        for r in range(h):
            if grid[r][c] != "=" and grid[r][c] not in blocks_proj:
                run += 1
                best = max(best, run)
            else:
                run = 0
        if best >= MIN_SIGHTLINE:
            long_cols += 1
    sightline_frac = round(long_cols / w, 4)

    # Mid-band structure: walkable segments across the middle third of rows.
    chokes, lane_widths = 0, []
    for r in range(h // 3, 2 * h // 3):
        width = 0
        for c in range(w + 1):
            walkable = c < w and grid[r][c] != "=" and grid[r][c] not in blocks_move
            if walkable:
                width += 1
            elif width:
                lane_widths.append(width)
                if width <= CHOKE_MAX_W:
                    chokes += 1
                width = 0
    rows_scanned = max(1, 2 * h // 3 - h // 3)
    avg_lane_w = round(sum(lane_widths) / len(lane_widths), 2) if lane_widths else 0.0

    # Openness of the center region (mid control fights happen here).
    cr, cc, k = h // 2, w // 2, 3  # 7x7
    center = [
        (r, c)
        for r in range(cr - k, cr + k + 1)
        for c in range(cc - k, cc + k + 1)
        if 0 <= r < h and 0 <= c < w and grid[r][c] != "="
    ]
    mid_open = round(
        sum(1 for r, c in center if grid[r][c] not in blocks_move) / (len(center) or 1),
        4,
    )
    mid_cover = round(
        sum(1 for r, c in center if grid[r][c] in blocks_proj) / (len(center) or 1), 4
    )

    return {
        "width": w,
        "height": h,
        "playableTiles": n,
        "wallPct": wall_pct,
        "bushPct": bush_pct,
        "waterPct": water_pct,
        "openPct": open_pct,
        "breakablePct": frac(breakable),
        "sightlineFrac": sightline_frac,
        "chokesPerRow": round(chokes / rows_scanned, 2),
        "avgLaneWidth": avg_lane_w,
        "midOpenness": mid_open,
        "midCover": mid_cover,
    }


def main():
    doc = json.load(open(HERE / "maps.json"))
    legend = doc["tileLegend"]
    sets = classify(legend)

    bridge = json.load(open(HERE / "map_name_map.json"))
    display = {}
    for slug, internal in bridge["maps"].items():
        display.setdefault(internal, []).append(slug.replace("-", " "))

    out = {}
    for name, m in doc["maps"].items():
        d = descriptors(m["grid"], sets)
        d["mode"] = m["mode"]
        d["displayNames"] = display.get(name, [])
        out[name] = d

    OUT.write_text(json.dumps(out, indent=1))
    print(f"wrote {OUT.name}: {len(out)} maps")

    # Sanity panel: archetype extremes should look right.
    def show(label, names):
        for nm in names:
            if nm in out:
                d = out[nm]
                print(
                    f"  {label:14} {nm:14} ({(d['displayNames'] or ['?'])[0]:20}) "
                    f"wall={d['wallPct']:.2f} bush={d['bushPct']:.2f} "
                    f"sight={d['sightlineFrac']:.2f} midOpen={d['midOpenness']:.2f}"
                )

    inv = {s: i for i, ss in display.items() for s in ss}
    show("sniper map", [inv.get("Shooting Star", "")])
    show("bushy map", [inv.get("Hideout", "")])
    show("brawlball", [inv.get("Backyard Bowl", "")])


if __name__ == "__main__":
    main()
