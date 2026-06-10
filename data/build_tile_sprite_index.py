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

def parts(tt):
    """Read tileParts (top/mid/bot/left/right in 1000ths-of-a-tile).
    Default to mid=1000 only — a square 1×1 sprite — when not specified."""
    p = tt.get("tileParts") or {}
    return {
        "top":   int(p.get("top",   0)),
        "mid":   int(p.get("mid",   1000)),
        "bot":   int(p.get("bot",   0)),
        "left":  int(p.get("left",  0)),
        "right": int(p.get("right", 0)),
    }

# Bridge BrawlMapGen's friendly mode names → our internal CSV mode names
# (the `mode` field on each map in maps-all.json, derived from the CSV name
# prefix like "Gemgrab_42" → "Gemgrab").
INTERNAL_MODE_FOR = {
    "Gem Grab":         ["Gemgrab", "GemGrab5v5", "GemGrab2v2", "GemGrab4x3", "TrioGemgrab"],
    "Heist":            ["Bankheist", "Bombheist"],
    "Bounty":           ["Wanted"],
    "Brawl Ball":       ["BrawlBall", "BrawlBallV2", "BrawlBall5v5"],
    "Showdown":         ["Survival", "SurvivalTrio"],
    "Solo Showdown":    ["Survival"],
    "Duo Showdown":     ["DuoSurvival"],
    "Big Game":         ["Biggame"],
    "Robo Rumble":      ["Invasion"],
    "Boss Fight":       ["BossFight"],
    "Siege":            ["Siege", "SiegeSmall"],
    "Railed Gem Grab":  ["GemGrabRail"],
    "Takedown":         ["KingHunt", "KingHuntShowdown"],
    "Present Plunder":  ["TreasureHunt"],
    "Hot Zone":         ["KingOfHill", "KingOfHill2v2"],
    "Hot Zone (mod)":   ["KingOfHill"],
    "Super City Rampage": ["Godzilla", "MegaBoss"],
    "Trophy Thieves":   ["Wipeout", "Wipeout5v5", "Wipeout4x3"],
    "Volley Brawl":     ["VolleyBrawl"],
    "Basket Brawl":     ["BasketBrawl", "BasketBrawl2v2"],
}

tile_chars = {}
for t in preset.get("tiles", []):
    code = t.get("tileCode")
    if not code:
        continue
    variants = [
        {"asset": tt["asset"], "parts": parts(tt)}
        for tt in t.get("tileTypes", []) if tt.get("asset")
    ]
    entry = {
        "name":     t.get("tileName") or t.get("display"),
        "display":  t.get("display"),
        "variants": variants,
        "default":  variants[0] if variants else None,
    }
    # tileLinks = BrawlMapGen autotile rules. Drives neighbor-aware variant
    # selection for things like benches (4 orientations), fences (~100 vars),
    # and water (binary-named asset per neighbor mask). Frontend reads this
    # for picking the right variant per cell.
    if t.get("tileLinks"):
        entry["tileLinks"] = t["tileLinks"]
    tile_chars[code] = entry

# Biome → tile-name → variant-index lookups (e.g. snowy + blocking1 → ice_block)
biomes = {}
for b in preset.get("biomes", []):
    biomes[b["name"]] = {d["tile"]: d.get("type", 0) for d in (b.get("defaults") or [])}
default_biome = {d["tile"]: d.get("type", 0)
                 for d in (preset.get("defaultBiome", {}).get("defaults") or [])}

# Build mode-level + (mode + biome) overrides from BrawlMapGen's gamemodes[]
gamemode_overrides = {}        # internal_mode_name → { tile_name → variantIdx }
gamemode_biome_overrides = {}  # internal_mode_name → biome → { tile_name → variantIdx }
for gm in preset.get("gamemodes", []):
    friendly = gm.get("name")
    internals = INTERNAL_MODE_FOR.get(friendly, [])
    # Top-level overrideBiome → mode override
    for ob in gm.get("overrideBiome") or []:
        for internal in internals:
            gamemode_overrides.setdefault(internal, {})[ob["tile"]] = ob.get("type", 0)
    # variants[biome].overrideBiome → mode + biome combo override
    vrs = gm.get("variants") or {}
    if isinstance(vrs, dict):
        for biome_name, vd in vrs.items():
            for ob in vd.get("overrideBiome") or []:
                for internal in internals:
                    gamemode_biome_overrides.setdefault(internal, {}).setdefault(biome_name, {})[ob["tile"]] = ob.get("type", 0)

# Post-fix on preset-derived overrides: the preset pins Brawl Ball's
# objective to variant 4 (brawlball.svg, the old leather ball that reads as
# a barrel at tile size) — prefer 17 (soccerball.svg, the modern ball).
for _mode, _ov in gamemode_overrides.items():
    if _mode.startswith("BrawlBall") and _ov.get("objective") == 4:
        _ov["objective"] = 17

# Game mode → variant overrides per tile name. The mode names match the
# `mode` field on each map in maps-all.json (internal CSV mode prefix).
# Variant indices reference tile_chars[code].variants[idx]. Indices were
# read from the variants list of the relevant tile char (objective = '8').
MODE_OVERRIDES = {
    # Heist / Bombheist → safe
    "Bankheist":   {"objective": 1},   # vault.svg
    "Bombheist":   {"objective": 1},
    # Bounty / Wanted variants → bounty star
    "Wanted":      {"objective": 2},   # bounty_star.svg
    "Solobounty":  {"objective": 2},
    "Deathmatch":  {"objective": 2},
    "DeathmatchFFA": {"objective": 2},
    # Brawl Ball variants → ball. Variant 17 soccerball.svg (modern black/
    # white ball); variant 4 brawlball.svg is the old leather ball and reads
    # as a barrel at tile size.
    "BrawlBall":      {"objective": 17},
    "BrawlBallV2":    {"objective": 17},
    "BrawlBall5v5":   {"objective": 17},
    "Dribble":        {"objective": 17},
    # Brawl Hockey / Air Hockey → ball objective. NOT variant 9: ike_blue.svg
    # is the SIEGE IKE TURRET, not a puck — it rendered a siege objective on
    # every hockey map (incl. the default Grass Knot).
    "Laserball":      {"objective": 17},
    "Laserball2v2":   {"objective": 17},
    "Laserball5v5":   {"objective": 17},
    "AirHockey":      {"objective": 17},
    "AirHockey2v2":   {"objective": 17},
    "SuperHockey":    {"objective": 17},
    # Gem Grab variants → mine (default but explicit)
    "Gemgrab":        {"objective": 0},
    "GemGrab5v5":     {"objective": 0},
    "GemGrab2v2":     {"objective": 0},
    "GemGrab4x3":     {"objective": 0},
    "TrioGemgrab":    {"objective": 0},
    # Hot Zone → hot zone
    "KingOfHill":     {"objective": 16},  # hot_zone_blue.svg
    "KingOfHill2v2":  {"objective": 16},
    # Volley Brawl → volleyball
    "VolleyBrawl":    {"objective": 29},
    # Basket Brawl → basketball
    "BasketBrawl":    {"objective": 30},
    # (AirHockey/SuperHockey objective is set to the custom puck below,
    #  after the puck variant is appended.)
    "BasketBrawl2v2": {"objective": 30},
    # Knockout has no central 8 marker normally
}

# Custom flat puck for Air Hockey — puck.svg is OURS (hand-drawn), not a
# BrawlMapGen asset. Appended as an extra objective variant; hockey modes
# point at it (a soccer ball is wrong for an air-hockey table).
_obj_variants = tile_chars["8"]["variants"]
_obj_variants.append({"asset": "puck.svg",
                      "parts": {"top": 250, "mid": 1000, "bot": 200, "left": 150, "right": 150}})
for _m in ("AirHockey", "AirHockey2v2", "SuperHockey"):
    MODE_OVERRIDES.setdefault(_m, {})["objective"] = len(_obj_variants) - 1

# "Indicator" tiles — game-engine collision but no in-game minimap sprite.
# Renderer paints a translucent gray cell for these instead of a sprite.
INDICATOR_TILES = ["J", "V"]

import os
# Every .svg on disk — feeds the JS preloader so it can also pull in
# autotile assets (water binary names like "00010110.svg", lunar fences,
# etc.) that aren't enumerated in any tile's `variants` list.
all_assets = sorted(
    f for f in os.listdir(REPO / "data/tile_sprites_official") if f.endswith(".svg")
)

OUT.write_text(json.dumps({
    "source": "bloodwiing/BrawlMapGen presets/brawlstars.json",
    "license": "Code: GPLv3 (bloodwiing/BrawlMapGen). Art: Supercell IP under Fan Content Policy.",
    "ignoreTiles": preset.get("ignoreTiles", []),
    "indicatorTiles": INDICATOR_TILES,
    "tiles": tile_chars,
    "biomes": biomes,
    "defaultBiome": default_biome,
    "allAssets": all_assets,
    # Mode overrides come from two sources:
    "gamemodeOverrides": gamemode_overrides,             # auth: BrawlMapGen gamemodes[].overrideBiome
    "gamemodeBiomeOverrides": gamemode_biome_overrides,  # auth: gamemodes[].variants[biome].overrideBiome
    "modeOverrides": MODE_OVERRIDES,                     # manual: modes BrawlMapGen doesn't cover (Laserball, AirHockey, …)
}, indent=2))
print(f"wrote {OUT.relative_to(REPO)} — {len(tile_chars)} tiles, {len(biomes)} biomes")
print(f"  gamemodeOverrides: {len(gamemode_overrides)} modes")
print(f"  gamemodeBiomeOverrides: {len(gamemode_biome_overrides)} modes")
print(f"  manual modeOverrides: {len(MODE_OVERRIDES)} modes")
