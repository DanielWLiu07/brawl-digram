"""Bake the reticle classifier output into a static brawlers.json for the frontend.

Reuses the classification logic from render_all_reticles.py — same `infer_shape`,
same `collect_variants`, same per-skill overrides — but emits JSON instead of SVG.

Adds two things the SVG renderer doesn't need but the frontend does:
  1. `passesWalls` per variant — whether the reticle should ignore wall collisions
     when drawn on a real map. Throwers / indirect projectiles / self-AoE all
     pass walls; direct-fire cones/lines/dashes are clipped by walls.
  2. Asset paths (portrait, render) so the frontend can `<img src>` directly.

Output: data/brawlers.json (one entry per playable brawler, all values in TILES
per project convention).
"""
import json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render_all_reticles import (  # noqa: E402
    skills, projectiles, characters, _overcharge_cards, brawlify_brawlers,
    overrides, infer_shape, collect_variants,
    HYPER_RANGE_MULTIPLIER, HYPER_SPLASH_MULTIPLIER,
)

OUT_PATH = Path(__file__).resolve().parent / 'brawlers.json'

# Reticle shapes that don't intersect with the world (projection-style)
PROJECTION_SHAPES = {'placement', 'wave', 'cluster', 'self-aoe', 'area-follow'}

def passes_walls(skill_row, shape):
    """Whether this reticle is a *projection* that ignores walls (True),
    or a *solid* shape that should be clipped by walls (False).

    Rule:
      - All projection-style shapes ignore walls (the splash/AoE just appears
        at the landing point regardless of intermediate geometry).
      - Direct-fire shapes (cone/line/dash) are blocked by walls unless the
        projectile explicitly has Indirect=true or IgnoreCloseWalls=true.
    """
    if shape in PROJECTION_SHAPES:
        return True
    proj_name = (skill_row.get('Projectiles') or '').strip()
    if proj_name:
        proj = projectiles.get(proj_name.lower())
        if proj and (proj.get('Indirect') == 'true' or proj.get('IgnoreCloseWalls') == 'true'):
            return True
    return False

# Map snake_case classifier params → camelCase JSON keys (frontend convention)
PARAM_KEY_MAP = {
    'range_tiles':   'rangeTiles',
    'splash_tiles':  'splashTiles',
    'width_tiles':   'widthTiles',
    'spread_deg':    'spreadDeg',
    'spacing_tiles': 'spacingTiles',
    'count':         'count',
    'pattern':       'pattern',
    'equip':         'equip',
}

def normalize_params(params):
    """Convert classifier param dict to JSON-friendly camelCase keys."""
    return {PARAM_KEY_MAP.get(k, k): v for k, v in params.items()}

def variant_to_json(label, skill_name, skill_row, hyper_mode):
    """Run the classifier on one variant, apply hyper modifier if needed, emit JSON."""
    result = infer_shape(skill_row)
    if not (isinstance(result, tuple) and result[0]):
        return {
            'label': label,
            'skillName': skill_name,
            'shape': None,
            'params': {},
            'passesWalls': False,
            'isHyper': bool(hyper_mode),
            'hyperModified': hyper_mode == 'hyper-modified',
            'unrecognized': True,
            'reason': str(result[1]) if isinstance(result, tuple) else 'unknown',
        }

    shape, params = result
    # Apply +25% modifier for hyper-modified variants (matches the SVG renderer)
    if hyper_mode == 'hyper-modified':
        params = dict(params)
        for k in ('range_tiles', 'splash_tiles'):
            if k in params and isinstance(params[k], (int, float)):
                params[k] *= HYPER_RANGE_MULTIPLIER if k == 'range_tiles' else HYPER_SPLASH_MULTIPLIER

    return {
        'label': label,
        'skillName': skill_name,
        'shape': shape,
        'params': normalize_params(params),
        'passesWalls': passes_walls(skill_row, shape),
        'isHyper': bool(hyper_mode),
        'hyperModified': hyper_mode == 'hyper-modified',
        'hasOverride': skill_name in overrides,
    }

def build_brawler_entry(b):
    """One playable brawler's entry. Returns None if no characters.csv match."""
    b_hash = b['hash']
    char = next(
        (c for c in characters.values()
         if (c.get('ItemName') or '').lower() == b_hash.lower()),
        None,
    )
    if not char:
        return None

    variants_raw = collect_variants(char, b_hash)
    variants_json = []
    for v in variants_raw:
        # collect_variants returns 4-tuples; legacy 3-tuple support kept for safety
        if len(v) == 4:
            label, sname, srow, hyper_mode = v
        else:
            label, sname, srow = v
            hyper_mode = False
        variants_json.append(variant_to_json(label, sname, srow, hyper_mode))

    return {
        'id': b['id'],
        'hash': b_hash,
        'name': b['name'],
        'internalName': char['Name'],
        'class': b.get('class', {}).get('name'),
        'rarity': b.get('rarity', {}).get('name'),
        'hasHypercharge': char['Name'] in _overcharge_cards,
        'assets': {
            'portrait': f'/assets/brawlers/{b_hash}/portrait.png',
            'render':   f'/assets/brawlers/{b_hash}/render.png',
            'emoji':    f'/assets/brawlers/{b_hash}/emoji.png',
        },
        'variants': variants_json,
    }

def main():
    entries = []
    skipped = []
    for b in brawlify_brawlers:
        entry = build_brawler_entry(b)
        if entry:
            entries.append(entry)
        else:
            skipped.append(b['hash'])

    payload = {
        '_meta': {
            'generatedFrom': 'data/render_all_reticles.py + data/reticle_overrides.json',
            'csvVersion': '67.264',
            'brawlerCount': len(entries),
            'skippedNewBrawlers': skipped,
            'units': 'All geometry values are in TILES (1 tile = standard Brawl Stars grid square). '
                     'rangeTiles, splashTiles, widthTiles, spacingTiles are tile distances. '
                     'spreadDeg is degrees. See data/SCHEMA_FLOW.md for CSV unit conventions.',
            'passesWalls': 'true → reticle projects over walls (placements, throwers, indirect projectiles); '
                           'false → solid reticle that should be clipped against wall tiles when rendered on a map.',
        },
        'brawlers': entries,
    }

    OUT_PATH.write_text(json.dumps(payload, indent=2))
    total_variants = sum(len(b['variants']) for b in entries)
    unrec = sum(1 for b in entries for v in b['variants'] if v.get('unrecognized'))
    passes = sum(1 for b in entries for v in b['variants'] if v['passesWalls'])

    print(f'Wrote {OUT_PATH}')
    print(f'  brawlers: {len(entries)} (skipped {len(skipped)} not in CSVs)')
    print(f'  variants: {total_variants} total, {unrec} unrecognized')
    print(f'  passesWalls=true: {passes} ({passes*100//total_variants}%)')
    print(f'  file size: {OUT_PATH.stat().st_size/1024:.1f} KB')

if __name__ == '__main__':
    main()
