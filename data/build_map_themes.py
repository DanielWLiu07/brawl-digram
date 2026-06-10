"""Bake authoritative map → theme data from the game CSVs.

`locations.csv` links every map to a `LocationTheme`; `location_themes.csv`
defines each theme including the exact `MapPreviewBGColor` (the chequerboard
color the game itself uses for that biome). Output is `data/map_themes.json`,
consumed by the prototype to set the BG color and biome variant per map
without any guessing.
"""

import csv
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LOCATIONS = REPO / "data/csv_logic/locations.csv"
THEMES = REPO / "data/csv_logic/location_themes.csv"
OUT = REPO / "data/map_themes.json"

with LOCATIONS.open(newline="") as f:
    r = csv.reader(f); h = next(r); next(r); loc_rows = list(r)
loc_idx = {x: i for i, x in enumerate(h)}

with THEMES.open(newline="") as f:
    r = csv.reader(f); h = next(r); next(r); theme_rows = list(r)
theme_idx = {x: i for i, x in enumerate(h)}


def get(row, idx, k, default=""):
    return row[idx[k]] if k in idx and idx[k] < len(row) else default


def as_int(s, default=None):
    s = (s or "").strip()
    try: return int(s)
    except ValueError: return default


# Build theme → BG/sky color + tile-set prefix
themes = {}
for row in theme_rows:
    name = get(row, theme_idx, "Name")
    if not name:
        continue
    r_, g_, b_ = (as_int(get(row, theme_idx, f"MapPreviewBGColor{c}")) for c in ("Red", "Green", "Blue"))
    sky = [as_int(get(row, theme_idx, f"MapPreviewSkyColor{c}")) for c in ("Red", "Green", "Blue")]
    themes[name] = {
        "tileSetPrefix": get(row, theme_idx, "TileSetPrefix"),
        "bgColor": [r_, g_, b_] if None not in (r_, g_, b_) else None,
        "skyColor": sky if None not in sky else None,
        "mapWidth":  as_int(get(row, theme_idx, "MapWidth"), 0),
        "mapHeight": as_int(get(row, theme_idx, "MapHeight"), 0),
        "music":     get(row, theme_idx, "Music"),
        "disabled":  get(row, theme_idx, "Disabled") == "true",
    }

# Build internal-map-name → theme name. Some maps appear under multiple
# location rows (re-used across modes); take the first definition.
map_to_theme = {}
for row in loc_rows:
    internal_map = get(row, loc_idx, "Map")
    theme = get(row, loc_idx, "LocationTheme")
    if internal_map and theme and internal_map not in map_to_theme:
        map_to_theme[internal_map] = theme

# CSV theme name → BrawlMapGen biome key (the key picks which wall/bush SVG
# variant to use). CSV has 104 themes, BrawlMapGen has 24 biomes — most CSV
# themes don't have a custom BrawlMapGen biome, so they fall back to
# grassfield (with the BG color overridden from CSV's MapPreviewBGColor*).
THEME_TO_BIOME = {
    "Default": "grassfield",
    "DefaultShowdown": "grassfield",
    "Grassfield": "grassfield",
    "Hub": "grassfield",
    "BBArena": "grassfield",
    "AirHockey": "grassfield",
    "AirHockey2v2": "grassfield",
    "Biodome": "grassfield",
    "Arcade": "arcade",
    "ArcadeShowdown": "arcade",
    "Mine": "mine",
    "MineTrainTracks": "mine",
    "Mortuary": "mortuary",
    "MortuaryShowdown": "mortuary",
    "MortuaryIslandShowdown": "mortuary",
    "MadEvilManor": "mortuary",
    "MadEvilManorShowdown": "mortuary",
    "MadEvilDungeonShowdown": "mortuary",
    "MadEvilIslandShowdown": "mortuary",
    "Bandstand": "bandstand",
    "Snowtel": "snowtel",
    "Scrapyard": "scrapyard",
    "ScrapyardShowdown": "scrapyard",
    "CoinFactory": "scrapyard",
    "CoinFactoryBB": "scrapyard",
    "GiftShop": "gift",
    "Pyramidquest": "canyon",
    "PyramidquestShowdown": "canyon",
    "PyramidquestIslandShowdown": "canyon",
    "StarrToonsStudio": "starrforce",
    "StarrToonsStudioShowdown": "starrforce",
    "StarrToonsStudioIslandShowdown": "starrforce",
    "TropicalIslandShowdown": "waterpark",
    "TropicalIslandShowdownBB": "waterpark",
    "IslandShowdown": "grassfield",
    "OdditiesShop": "town",
    "Retropolis": "retro",
    "Castle": "castle",
    "Darryl": "darryl",
    "Snowy": "snowy",
    "Town": "town",
    "Lamporium": "lamporium",
    "Jungle": "jungle",
    "ActionShow": "actionshow",
}

OUT.write_text(json.dumps({
    "source": "csv_logic/locations.csv + location_themes.csv (game data)",
    "themes": themes,
    "mapTheme": map_to_theme,
    "themeToBiome": THEME_TO_BIOME,
}, indent=2, ensure_ascii=False))
print(f"wrote {OUT.relative_to(REPO)} — {len(themes)} themes, {len(map_to_theme)} maps mapped")
