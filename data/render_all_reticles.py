"""Generate per-brawler attack-reticle SVGs for every playable brawler.

For each brawler in the Brawlify manifest:
  1. Look up internal name (ItemName → characters.csv) and its skills.
  2. Resolve gadget skills via accessories.csv (NOT cards.csv — see SCHEMA_FLOW.md).
  3. Classify each skill into a reticle shape primitive (cone / line / arc / dash /
     placement / self-aoe / circle).
  4. Render each variant as an SVG panel using the in-game style:
     hard white outer edge + radial fade-from-all-edges-inward (see
     feedback_reticle_styling memory).

Output: data/reticles/<BrawlerHash>.svg + data/reticles/index.html for browsing.

This is the inverse of "the data-loader" — it goes straight from CSVs to SVG.
The actual loader (which emits brawlers.json for the frontend) will reuse this
shape-classification logic.
"""
import csv, math, json
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent
CSV_DIR = ROOT / 'csv_logic'
ASSETS_DIR = ROOT.parent / 'assets'
OUT_DIR = ROOT / 'reticles'
OUT_DIR.mkdir(exist_ok=True)

# ---- visual constants ----
TILE_PX = 20
PANEL_W = 320
PANEL_H = 340
PAD = 14
TITLE_H = 36
COLS = 3
OUTER_STROKE_WIDTH = 2.5
OUTER_STROKE_OPACITY = 0.95
INNER_BAND_OPACITY = 0.5
TOKEN_SIZE = 28  # brawler portrait diameter (~1.4 tiles at TILE_PX=20)

# ---- CSV loading ----
def load_csv(name):
    """Skip the 2nd 'type-declaration' row Supercell CSVs include."""
    with open(CSV_DIR / name) as f:
        rows = list(csv.DictReader(f))
    return rows[1:] if rows else []

def index_by_name(rows):
    return {r['Name'].lower(): r for r in rows if r.get('Name')}

skills      = index_by_name(load_csv('skills.csv'))
projectiles = index_by_name(load_csv('projectiles_logic.csv'))
area_effects = index_by_name(load_csv('area_effects.csv'))
characters  = {r['Name']: r for r in load_csv('characters.csv') if r.get('Name')}

# accessories.csv has no Target column — link by Name prefix matching brawler's internal name.
# E.g. 'ShotgunGirl_Dash' belongs to 'ShotgunGirl'.
_accessories_all = load_csv('accessories.csv')
accessories_for = defaultdict(list)
for a in _accessories_all:
    if not a.get('Name') or not a.get('Skill'):
        continue
    if '_' not in a['Name']:
        continue
    brawler = a['Name'].split('_', 1)[0]
    accessories_for[brawler].append(a)

# Brawlify manifest for display names + portrait paths
manifest = json.loads((ASSETS_DIR / 'manifest.json').read_text())
brawlify_brawlers = manifest['brawlers']

# Per-skill reticle overrides (for brawlers whose shape can't be inferred from CSVs alone)
OVERRIDES_PATH = ROOT / 'reticle_overrides.json'
_raw_overrides = json.loads(OVERRIDES_PATH.read_text()) if OVERRIDES_PATH.exists() else {}
overrides = {k: v for k, v in _raw_overrides.items() if not k.startswith('_')}

# Hypercharge detection — every brawler with a MetaType=6 "_overcharge" card has a
# hypercharge. The card type can be `overcharge_default` (universal +25 % stats with
# no unique shape change) or a brawler-specific type (e.g. `overcharge_weapon_spread`
# for Shelly). For now we render a hyper variant for ANY brawler with an overcharge
# card; the variant uses an explicit overcharged-skill row when one exists, otherwise
# applies a +25 % modifier to the base skill's range/splash.
_overcharge_cards = {c['Name'].replace('_overcharge', ''): c
                     for c in load_csv('cards.csv')
                     if c.get('Name', '').endswith('_overcharge')}
HYPER_COLOR = '#c084fc'  # purple — matches Brawl Stars hypercharge UI tint
HYPER_RANGE_MULTIPLIER = 1.25
HYPER_SPLASH_MULTIPLIER = 1.25

# Map internal characters.csv name → Brawlify hash (display-ready slug)
# characters.csv has an 'ItemName' field that's lowercased; matches Brawlify hash lowercased.
internal_to_hash = {}
for c in characters.values():
    item = (c.get('ItemName') or '').lower()
    for b in brawlify_brawlers:
        if b['hash'].lower() == item:
            internal_to_hash[c['Name']] = b['hash']
            break

# ---- shape inference ----
def safe_int(s):
    s = (s or '').strip()
    return int(s) if s.lstrip('-').isdigit() else 0

def _strip_skill_suffixes(name):
    """Strip skill/projectile suffixes to get the brawler internal-name prefix.
    'GeishaUltiProjectile' → 'Geisha'; 'BarkeepUlti' → 'Barkeep'."""
    for suffix in [
        'OverchargedUltiProjectile', 'TransformedUltiProjectile',
        'OverchargedUlti', 'TransformedUlti', 'TransformedWeapon',
        'OverchargedWeapon', 'BonusSkillCover', 'BonusSkillPoppin',
        'BonusSkill', 'GadgetSkill', 'UltiProjectile', 'Projectile',
        'Ulti', 'Weapon',
    ]:
        if name.endswith(suffix):
            return name[:-len(suffix)]
    return name

def find_landing_aoe_tiles(skill, projectile_name):
    """Find the radius of the actual landing AoE for an indirect skill.

    Strategy:
      1. Try standard <Projectile>Explosion / <Prefix>UltiExplosion conventions.
      2. Fall back to a prefix-scan: find area_effects whose name starts with
         the brawler's internal name (extracted from skill/projectile) and that
         have Radius > 0. Score by relevance (Damage > Storm > Area > Explosion)
         and pick the largest matching radius.

    This catches non-convention names like GeishaStormDamage that 'Explosion'
    suffix lookup misses, while preferring ulti-specific effects over weapon
    effects when scoring a super skill."""
    # 1) Standard naming conventions
    if projectile_name:
        for cand in (projectile_name.replace('Projectile', 'Explosion'),
                     projectile_name + 'Explosion',
                     projectile_name.replace('Projectile', '') + 'Explosion'):
            ae = area_effects.get(cand.lower())
            if ae:
                r = safe_int(ae.get('Radius'))
                if r > 0:
                    return r / 480.0

    # 2) Prefix-scan fallback
    prefix = _strip_skill_suffixes(skill['Name']) if skill else ''
    if not prefix and projectile_name:
        prefix = _strip_skill_suffixes(projectile_name)
    if not prefix:
        return 0.0

    kind = (skill.get('EquipType') or '') if skill else ''
    is_ulti   = kind == 'ulti'
    is_gadget = kind == 'bonusSkill'
    is_weapon = kind == 'weapon'

    # Exclude AOE names belonging to a DIFFERENT skill type than the current one,
    # so a gadget's prefix scan doesn't accidentally pick up the super's explosion
    # (Spike Life Plant gadget was matching CactusUltiExplosion otherwise).
    def is_wrong_kind(nl):
        if is_gadget and any(s in nl for s in ('ulti', 'overcharged', 'weapon', 'attack')):
            return True
        if is_ulti and any(s in nl for s in ('cover', 'heal', 'bonusskill', 'gadget', 'weapon')):
            return True
        if is_weapon and any(s in nl for s in ('ulti', 'cover', 'bonusskill', 'gadget')):
            return True
        return False

    candidates = []
    for ae in area_effects.values():
        n = ae.get('Name', '')
        if not n.startswith(prefix):
            continue
        rest = n[len(prefix):]
        skill_is_transformed = skill and 'Transformed' in (skill.get('Name') or '')
        if rest.startswith('Transformed') and not skill_is_transformed:
            continue
        if not rest.startswith('Transformed') and skill_is_transformed:
            continue
        nl = n.lower()
        if is_wrong_kind(nl):
            continue
        r = safe_int(ae.get('Radius'))
        if r <= 0:
            continue
        # Relevance scoring
        score = 0
        if 'damage' in nl: score += 3
        if 'storm' in nl:  score += 2
        if 'area' in nl:   score += 1
        if 'explosion' in nl: score += 1
        if is_ulti and ('ulti' in nl or 'storm' in nl): score += 2
        if 'warning' in nl: score -= 2
        if 'visibility' in nl: score -= 1
        candidates.append((score, r, n))

    if not candidates:
        return 0.0
    candidates.sort(key=lambda c: (-c[0], -c[1]))
    return candidates[0][1] / 480.0

# Backward-compat shim — keep the old name for the wave-classifier call site
def find_splash_radius_tiles(projectile_name):
    return find_landing_aoe_tiles({'Name': '', 'EquipType': ''}, projectile_name)

def area_effect_radius_tiles(ae_name):
    """Direct lookup for an explicitly-referenced area effect (e.g. from
    skill.AreaEffectObject for Trunk/Gigi). Returns tile radius or 0."""
    if not ae_name:
        return 0.0
    ae = area_effects.get(ae_name.lower())
    if ae:
        return safe_int(ae.get('Radius')) / 480.0
    return 0.0

def infer_shape(skill):
    """Map a skills.csv row to a reticle primitive + geometry.
    Returns (shape, dict-of-params) or (None, reason)."""
    if not skill:
        return None, 'no-skill'

    # Per-skill overrides win over everything else — for brawlers whose shape can't
    # be inferred from the CSVs (Barley super = quincunx, etc.).
    if skill.get('Name') in overrides:
        ov = overrides[skill['Name']]
        return ov['shape'], dict(ov.get('params', {}))

    range_u   = safe_int(skill.get('CastingRange'))
    max_range = safe_int(skill.get('MaxCastingRange'))
    spread    = safe_int(skill.get('Spread'))
    bullets   = safe_int(skill.get('NumBulletsInOneAttack'))
    pattern   = safe_int(skill.get('AttackPattern'))
    proj_name = (skill.get('Projectiles') or '').strip()
    summon    = (skill.get('SummonedCharacters') or '').strip()
    behavior  = (skill.get('BehaviorType') or '').strip()

    proj = projectiles.get(proj_name.lower()) if proj_name else None
    indirect = proj and proj.get('Indirect') == 'true'

    effective_range = max(range_u, max_range)
    range_tiles = effective_range / 3.0

    # 1. Charge-type skill = dash (Shelly Fast Forward, Edgar Hardcore, etc.)
    if behavior == 'Charge' and effective_range > 0:
        return 'dash', {'range_tiles': range_tiles}

    # 2. Indirect projectile = placement (target circle at landing point).
    #    Wave variant: when AttackPattern=9 (Barley super, Brock super: 5 projectiles
    #    in a fan across the spread arc) OR bullets>1 (Dyna attack: 2 sticks at spread
    #    angle). Single-bullet "spread" without those flags is just aim variance —
    #    render as plain placement (Sprout attack, Tick attack).
    if indirect:
        splash_tiles = find_landing_aoe_tiles(skill, proj_name)
        is_wave = (pattern == 9) or (bullets > 1 and spread > 0)
        # Supers and gadgets in-game don't show a "throwable area" ring; only the
        # landing zone. Attacks DO show the range to the player. Pass equip-type
        # through so the renderer can adapt.
        equip = (skill.get('EquipType') or '').strip()
        if is_wave:
            n = 5 if pattern == 9 else bullets
            return 'wave', {
                'range_tiles': range_tiles,
                'splash_tiles': splash_tiles,
                'spread_deg': spread or 30,
                'count': n,
                'equip': equip,
            }
        return 'placement', {
            'range_tiles': range_tiles,
            'splash_tiles': splash_tiles,
            'equip': equip,
        }

    # 3. Has spread = cone (shotgunners, sweeps, narrow flame streams).
    #    NOTE: NumBulletsInOneAttack=1 + Spread>0 still renders as cone because the
    #    multi-projectile count is often encoded elsewhere (Bo fires 3 arrows despite
    #    NumBulletsInOneAttack=1). Cones with very narrow spread (Amber ~30°) will
    #    visually look stream-like, which matches in-game.
    if effective_range > 0 and spread > 0:
        return 'cone', {'range_tiles': range_tiles, 'spread_deg': spread}

    # 4. Has range, has projectile, no spread = line (snipers: Brock, Piper, Belle)
    if effective_range > 0 and proj_name:
        proj_radius_u = safe_int(proj.get('Radius')) if proj else 0
        width_tiles = max(0.6, (proj_radius_u * 2) / 480.0) if proj_radius_u else 0.8
        return 'line', {'range_tiles': range_tiles, 'width_tiles': width_tiles}

    # 5. AreaEffectObject attack (no projectile) — Trunk (Domain), Gigi (Daredevil), etc.
    #    These are direct-AoE attacks that don't fire a projectile. If the area follows
    #    the brawler, treat as self-aoe; otherwise as placement at the target tile.
    ae_obj = (skill.get('AreaEffectObject') or '').strip()
    if effective_range > 0 and ae_obj:
        ae_radius = area_effect_radius_tiles(ae_obj)
        follow = (skill.get('AreaEffectFollowType') or '').strip().lower() == 'follow'
        if follow:
            return 'area-follow', {'splash_tiles': ae_radius or 1.5}
        return 'placement', {'range_tiles': range_tiles, 'splash_tiles': ae_radius or 1.0}

    # 6. Has range, has summon (no projectile), not indirect = placement (Jessie turret, Pam station)
    if range_u > 0 and summon:
        return 'placement', {'range_tiles': range_tiles}

    # 7. No range = self-AoE (rage abilities, instant-ring supers like El Primo)
    if range_u == 0:
        return 'self-aoe', {}

    return None, f'unrecognized (range={range_u}, spread={spread}, proj={proj_name}, behavior={behavior})'

# ---- SVG rendering primitives ----
DEFS = '''<defs>
  <filter id="blur4" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="4"/></filter>
</defs>'''

def grid(px, py, w, h):
    out = [f'<rect x="{px}" y="{py}" width="{w}" height="{h}" fill="#0f1320"/>']
    for x in range(0, w + 1, TILE_PX):
        out.append(f'<line x1="{px+x}" y1="{py}" x2="{px+x}" y2="{py+h}" stroke="#1e2538" stroke-width="0.5"/>')
    for y in range(0, h + 1, TILE_PX):
        out.append(f'<line x1="{px}" y1="{py+y}" x2="{px+w}" y2="{py+y}" stroke="#1e2538" stroke-width="0.5"/>')
    return '\n'.join(out)

def wedge_path(cx, cy, r, spread_deg, direction=-90):
    half = spread_deg / 2
    a1, a2 = math.radians(direction - half), math.radians(direction + half)
    x1, y1 = cx + r*math.cos(a1), cy + r*math.sin(a1)
    x2, y2 = cx + r*math.cos(a2), cy + r*math.sin(a2)
    large = 1 if spread_deg > 180 else 0
    return f"M {cx},{cy} L {x1:.1f},{y1:.1f} A {r},{r} 0 {large},1 {x2:.1f},{y2:.1f} Z"

def annular_sector_path(cx, cy, r_inner, r_outer, spread_deg=80, direction=-90):
    """Donut wedge for throwers (min range to max range)."""
    half = spread_deg / 2
    a1, a2 = math.radians(direction - half), math.radians(direction + half)
    x1o, y1o = cx + r_outer*math.cos(a1), cy + r_outer*math.sin(a1)
    x2o, y2o = cx + r_outer*math.cos(a2), cy + r_outer*math.sin(a2)
    x1i, y1i = cx + r_inner*math.cos(a1), cy + r_inner*math.sin(a1)
    x2i, y2i = cx + r_inner*math.cos(a2), cy + r_inner*math.sin(a2)
    return (f"M {x1o:.1f},{y1o:.1f} A {r_outer},{r_outer} 0 0,1 {x2o:.1f},{y2o:.1f} "
            f"L {x2i:.1f},{y2i:.1f} A {r_inner},{r_inner} 0 0,0 {x1i:.1f},{y1i:.1f} Z")

def reticle_svg(shape, params, cx, cy, gid):
    """Render any shape primitive in the established 'hard edge + inward fade' style.
    Returns a list of SVG element strings to insert into the panel."""
    parts = []

    if shape == 'cone':
        r_px = params['range_tiles'] * TILE_PX
        spread = params['spread_deg']
        path = wedge_path(cx, cy, r_px, spread)
        band_w = r_px * 0.22
        blur = band_w / 4
        parts.extend(_clipped_band(path, gid, band_w, blur))
        parts.append(f'<path d="{path}" fill="none" stroke="white" stroke-width="{OUTER_STROKE_WIDTH}" stroke-opacity="{OUTER_STROKE_OPACITY}" stroke-linejoin="round"/>')

    elif shape == 'dash':
        # Uniform translucent rectangle — fill and stroke share the same color and
        # opacity (so the edge isn't a separate brighter band) but BOTH are present
        # so the shape reads clearly against any background.
        r_px = params['range_tiles'] * TILE_PX
        w = TILE_PX * 1.0
        x, y = cx - w/2, cy - r_px
        parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{r_px}" fill="white" fill-opacity="0.65"/>')

    elif shape == 'line':
        r_px = params['range_tiles'] * TILE_PX
        w = max(8, params['width_tiles'] * TILE_PX)
        x, y = cx - w/2, cy - r_px
        parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{r_px}" fill="white" fill-opacity="0.65"/>')

    elif shape == 'arc':
        # Thrower: annular sector from ~30% of range to 100% of range, ~80° spread
        r_outer = params['range_tiles'] * TILE_PX
        r_inner = r_outer * 0.30
        spread = 80
        path = annular_sector_path(cx, cy, r_inner, r_outer, spread)
        band_w = (r_outer - r_inner) * 0.22
        blur = band_w / 4
        parts.extend(_clipped_band(path, gid, band_w, blur))
        parts.append(f'<path d="{path}" fill="none" stroke="white" stroke-width="{OUTER_STROKE_WIDTH}" stroke-opacity="{OUTER_STROKE_OPACITY}" stroke-linejoin="round"/>')

    elif shape == 'placement':
        # Simplified: one primary aim point, dotted line that STOPS at the landing
        # center (doesn't extend past it), and the splash AoE drawn at that center.
        # Range ring is shown lightly for attacks (player sees throwable area
        # in-game) but hidden/much fainter for supers (in-game super UI only shows
        # the landing zone, not a big circle around the brawler).
        r_px = params['range_tiles'] * TILE_PX
        splash_px = params.get('splash_tiles', 0) * TILE_PX
        equip = params.get('equip', '')
        is_super = equip == 'ulti'

        # Primary aim point — for supers the landing reads more naturally at max
        # range (you see the full reach); for attacks at 70 % gives breathing room
        # for the splash to sit clearly inside the throwable area.
        aim_frac = 0.92 if is_super else 0.70
        ptx, pty = cx, cy - r_px * aim_frac

        # Range outline: faint dashed circle. Much fainter for supers since the
        # in-game UI doesn't emphasize this for supers.
        ring_opacity = 0.22 if is_super else 0.55
        parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r_px}" fill="none" stroke="white" stroke-width="1.0" stroke-dasharray="4,5" stroke-opacity="{ring_opacity}"/>')

        # Single dotted line from brawler to landing center — stops exactly at the
        # splash center, doesn't extend past.
        parts.append(f'<line x1="{cx}" y1="{cy}" x2="{ptx}" y2="{pty}" stroke="white" stroke-width="1.5" stroke-dasharray="3,4" stroke-opacity="0.55"/>')

        # Splash AoE at landing point — gradient inward-fade treatment.
        if splash_px > 0:
            circ_path = f'M {ptx-splash_px},{pty} a {splash_px},{splash_px} 0 1,0 {2*splash_px},0 a {splash_px},{splash_px} 0 1,0 {-2*splash_px},0 Z'
            band_w = splash_px * 0.25
            blur = max(1.5, band_w / 4)
            parts.extend(_clipped_band(circ_path, gid + '-splash', band_w, blur))
            parts.append(f'<circle cx="{ptx}" cy="{pty}" r="{splash_px}" fill="none" stroke="white" stroke-width="{OUTER_STROKE_WIDTH}" stroke-opacity="{OUTER_STROKE_OPACITY}"/>')
        else:
            # No splash data — small crosshair marker at landing point.
            parts.append(f'<circle cx="{ptx}" cy="{pty}" r="9" fill="white" fill-opacity="0.2" stroke="white" stroke-width="{OUTER_STROKE_WIDTH}" stroke-opacity="{OUTER_STROKE_OPACITY}"/>')
            parts.append(f'<line x1="{ptx-12}" y1="{pty}" x2="{ptx+12}" y2="{pty}" stroke="white" stroke-width="1.5" stroke-opacity="0.7"/>')
            parts.append(f'<line x1="{ptx}" y1="{pty-12}" x2="{ptx}" y2="{pty+12}" stroke="white" stroke-width="1.5" stroke-opacity="0.7"/>')

    elif shape == 'cluster':
        # Multi-projectile pattern at a target point (Barley super quincunx etc.).
        # Single trajectory hint to the cluster center, then 5 splashes arranged
        # according to the pattern.
        r_px = params['range_tiles'] * TILE_PX
        splash_px = params.get('splash_tiles', 1.0) * TILE_PX
        spacing_px = params.get('spacing_tiles', 2.0) * TILE_PX
        pattern = params.get('pattern', 'quincunx')
        tx, ty = cx, cy - r_px

        # Range ring (faded) + straight dotted line to cluster center
        parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r_px}" fill="none" stroke="white" stroke-width="1.2" stroke-dasharray="4,5" stroke-opacity="0.4"/>')
        parts.append(f'<line x1="{cx}" y1="{cy}" x2="{tx}" y2="{ty}" stroke="white" stroke-width="1.5" stroke-dasharray="3,4" stroke-opacity="0.55"/>')

        # Compute splash centers per pattern
        if pattern == 'quincunx':
            # 5 points: 1 center + 4 diagonal corners (Barley super)
            offsets = [(0, 0), (-spacing_px, -spacing_px), (spacing_px, -spacing_px),
                       (-spacing_px, spacing_px), (spacing_px, spacing_px)]
        elif pattern == 'plus':
            # 5 points: 1 center + 4 axis-aligned
            offsets = [(0, 0), (0, -spacing_px), (0, spacing_px),
                       (-spacing_px, 0), (spacing_px, 0)]
        elif pattern == 'triangle':
            # 3 points in an equilateral triangle around the target (Tick attack, Bo super)
            h = spacing_px * 0.866  # sin(60°)
            offsets = [(0, -spacing_px), (-h, spacing_px * 0.5), (h, spacing_px * 0.5)]
        elif pattern == 'pair':
            # 2 points side-by-side perpendicular to aim direction (Dynamike attack —
            # two bombs land left + right of the target)
            offsets = [(-spacing_px, 0), (spacing_px, 0)]
        elif pattern == 'hexagon':
            # 6 perimeter points + center = 7 (Squeak super sticky-bomb spread)
            import math as _m
            offsets = [(0, 0)] + [(spacing_px * _m.cos(_m.radians(60*i - 90)),
                                   spacing_px * _m.sin(_m.radians(60*i - 90))) for i in range(6)]
        else:
            offsets = [(0, 0)]

        for i, (ox, oy) in enumerate(offsets):
            sx, sy = tx + ox, ty + oy
            circ_path = f'M {sx-splash_px},{sy} a {splash_px},{splash_px} 0 1,0 {2*splash_px},0 a {splash_px},{splash_px} 0 1,0 {-2*splash_px},0 Z'
            band_w = splash_px * 0.22
            blur = max(1.2, band_w / 4)
            parts.extend(_clipped_band(circ_path, f'{gid}-c{i}', band_w, blur))
            parts.append(f'<circle cx="{sx}" cy="{sy}" r="{splash_px}" fill="none" stroke="white" stroke-width="{OUTER_STROKE_WIDTH}" stroke-opacity="{OUTER_STROKE_OPACITY}"/>')

    elif shape == 'wave':
        # Multi-projectile thrower super (Barley super, etc.) — N splash circles
        # arranged in a fan at the target distance across the spread arc.
        r_px = params['range_tiles'] * TILE_PX
        splash_px = params.get('splash_tiles', 0.7) * TILE_PX or 14
        spread = params['spread_deg']
        n = params['count']
        # Range ring (faded)
        parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r_px}" fill="none" stroke="white" stroke-width="1.2" stroke-dasharray="4,5" stroke-opacity="0.4"/>')
        # Each splash in the fan
        half = spread / 2
        for i in range(n):
            t = i / (n - 1) if n > 1 else 0.5
            ang_deg = -90 - half + t * spread
            ang = math.radians(ang_deg)
            sx = cx + r_px * math.cos(ang)
            sy = cy + r_px * math.sin(ang)
            # Straight dotted line per bottle (no arc)
            parts.append(f'<line x1="{cx}" y1="{cy}" x2="{sx}" y2="{sy}" stroke="white" stroke-width="1" stroke-dasharray="3,4" stroke-opacity="0.3"/>')
            # Splash circle
            circ_path = f'M {sx-splash_px},{sy} a {splash_px},{splash_px} 0 1,0 {2*splash_px},0 a {splash_px},{splash_px} 0 1,0 {-2*splash_px},0 Z'
            band_w = splash_px * 0.22
            blur = max(1.2, band_w / 4)
            parts.extend(_clipped_band(circ_path, f'{gid}-w{i}', band_w, blur))
            parts.append(f'<circle cx="{sx}" cy="{sy}" r="{splash_px}" fill="none" stroke="white" stroke-width="{OUTER_STROKE_WIDTH}" stroke-opacity="{OUTER_STROKE_OPACITY}"/>')

    elif shape == 'area-follow':
        # Brawler-centered AoE that moves with them (Gigi spin, etc.). Render as a
        # circle around the brawler with the gradient treatment.
        r_px = params.get('splash_tiles', 1.5) * TILE_PX
        path = f'M {cx-r_px},{cy} a {r_px},{r_px} 0 1,0 {2*r_px},0 a {r_px},{r_px} 0 1,0 {-2*r_px},0 Z'
        band_w = r_px * 0.22
        blur = max(1.2, band_w / 4)
        parts.extend(_clipped_band(path, gid, band_w, blur))
        parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r_px}" fill="none" stroke="white" stroke-width="{OUTER_STROKE_WIDTH}" stroke-opacity="{OUTER_STROKE_OPACITY}"/>')

    elif shape == 'self-aoe':
        # Default radius (no range data) — use 2.5 tiles as a placeholder
        # Will look uniform for all self-aoe; that's accurate since these are usually
        # short instant rings (rage activations, El Primo super, etc.)
        r_px = 2.5 * TILE_PX
        path = f'M {cx-r_px},{cy} a {r_px},{r_px} 0 1,0 {2*r_px},0 a {r_px},{r_px} 0 1,0 {-2*r_px},0 Z'
        band_w = r_px * 0.22
        blur = band_w / 4
        parts.extend(_clipped_band(path, gid, band_w, blur))
        parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r_px}" fill="none" stroke="white" stroke-width="{OUTER_STROKE_WIDTH}" stroke-opacity="{OUTER_STROKE_OPACITY}"/>')

    return parts

def _clipped_band(path_d, gid, band_w, blur_std):
    """Helper: inward-only feathered white band along all edges of the given path."""
    return [
        f'<defs><clipPath id="clip-{gid}"><path d="{path_d}"/></clipPath>'
        f'<filter id="blur-{gid}" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="{blur_std:.2f}"/></filter></defs>',
        f'<g clip-path="url(#clip-{gid})"><path d="{path_d}" fill="none" stroke="white" stroke-width="{band_w}" stroke-opacity="{INNER_BAND_OPACITY}" stroke-linejoin="round" filter="url(#blur-{gid})"/></g>',
    ]

# ---- per-brawler rendering ----
def collect_variants(char_row, b_hash):
    """Return a list of (label, skill_name, skill_row) covering everything we want to render."""
    variants = []

    weapon = char_row.get('WeaponSkill')
    ulti   = char_row.get('UltimateSkill')
    oc_ulti_name = char_row.get('OverchargedUltimateSkill')
    has_hyper = char_row['Name'] in _overcharge_cards

    if weapon and weapon.lower() in skills:
        variants.append(('Attack', weapon, skills[weapon.lower()], False))
    if ulti and ulti.lower() in skills:
        variants.append(('Super', ulti, skills[ulti.lower()], False))

    if has_hyper:
        # Hypercharged Attack — explicit OverchargedWeapon row if present, else base + modifier
        oc_weapon = f"{char_row['Name']}OverchargedWeapon"
        if oc_weapon.lower() in skills:
            variants.append(('Hypercharged Attack', oc_weapon, skills[oc_weapon.lower()], 'hyper'))
        elif weapon and weapon.lower() in skills:
            variants.append(('Hypercharged Attack (+25%)', weapon, skills[weapon.lower()], 'hyper-modified'))

        # Hypercharged Super — explicit row from characters.csv if present, else base + modifier
        if oc_ulti_name and oc_ulti_name.lower() in skills:
            variants.append(('Hypercharged Super', oc_ulti_name, skills[oc_ulti_name.lower()], 'hyper'))
        elif ulti and ulti.lower() in skills:
            variants.append(('Hypercharged Super (+25%)', ulti, skills[ulti.lower()], 'hyper-modified'))

    # Alt-form skills (Kaze: Geisha → Ninja, etc.)
    for suffix, label in [('TransformedWeapon', 'Alt-form Attack'),
                          ('TransformedUlti', 'Alt-form Super')]:
        cand = f"{char_row['Name']}{suffix}"
        if cand.lower() in skills:
            variants.append((label, cand, skills[cand.lower()], False))

    # Gadgets via accessories.csv
    for a in accessories_for.get(char_row['Name'], []):
        skill_name = a.get('Skill')
        if not skill_name:
            continue
        if skill_name.lower() not in skills:
            continue
        if 'buddy' in skill_name.lower() or 'buddy' in a['Name'].lower():
            continue
        variants.append((f"Gadget: {a['Name'].replace(char_row['Name']+'_','').replace('_',' ')}",
                         skill_name, skills[skill_name.lower()], False))

    return variants

def render_panel(px, py, label, skill_name, skill_row, brawler_hash, panel_idx, hyper_mode=False):
    """hyper_mode: False (base), 'hyper' (explicit overcharged skill row), or
    'hyper-modified' (base skill with +25 % range/splash modifier). When truthy,
    the reticle is recolored purple to indicate hypercharge state."""
    range_u = safe_int(skill_row.get('CastingRange'))
    spread  = safe_int(skill_row.get('Spread'))
    shape_result = infer_shape(skill_row)

    # Apply +25 % modifier when the variant is a synthetic hyper-modified one
    if hyper_mode == 'hyper-modified' and isinstance(shape_result, tuple) and shape_result[0]:
        shape, params = shape_result
        bumped = dict(params)
        for k in ('range_tiles', 'splash_tiles'):
            if k in bumped and isinstance(bumped[k], (int, float)):
                bumped[k] *= HYPER_RANGE_MULTIPLIER if k == 'range_tiles' else HYPER_SPLASH_MULTIPLIER
        shape_result = (shape, bumped)

    cx = px + PANEL_W / 2
    cy = py + PANEL_H - 70
    parts = [grid(px, py, PANEL_W, PANEL_H)]

    if isinstance(shape_result, tuple) and len(shape_result) == 2 and shape_result[0] is not None:
        shape, params = shape_result
        if shape is None:
            parts.append(f'<text x="{px + PANEL_W/2}" y="{py + PANEL_H/2}" text-anchor="middle" font-family="monospace" font-size="11" fill="#888">[no recognizable reticle: {params}]</text>')
        else:
            gid = f'g-{brawler_hash}-{panel_idx}'
            shape_parts = reticle_svg(shape, params, cx, cy, gid)
            # Recolor hyper variants purple — string-replace white references inside
            # the reticle SVG fragments (doesn't touch labels/grid which render outside)
            if hyper_mode:
                shape_parts = [
                    p.replace('"white"', f'"{HYPER_COLOR}"')
                     .replace('#ffffff', HYPER_COLOR)
                     .replace('#FFFFFF', HYPER_COLOR)
                    for p in shape_parts
                ]
            parts.extend(shape_parts)
            # Lens highlight under token (kept white — it's not part of the reticle)
            parts.append(f'<circle cx="{cx}" cy="{cy}" r="16" fill="white" fill-opacity="0.10"/>')
    else:
        parts.append(f'<text x="{px + PANEL_W/2}" y="{py + PANEL_H/2}" text-anchor="middle" font-family="monospace" font-size="11" fill="#888">[shape inference failed]</text>')

    # Brawler portrait
    portrait_path = ASSETS_DIR / 'brawlers' / brawler_hash / 'portrait.png'
    rel_portrait = f'../../assets/brawlers/{brawler_hash}/portrait.png'
    if portrait_path.exists():
        parts.append(f'<image href="{rel_portrait}" x="{cx-TOKEN_SIZE/2}" y="{cy-TOKEN_SIZE/2}" width="{TOKEN_SIZE}" height="{TOKEN_SIZE}"/>')
    else:
        parts.append(f'<circle cx="{cx}" cy="{cy}" r="10" fill="#fff" stroke="#aaa" stroke-width="2"/>')

    # Labels (top of panel)
    range_tiles = range_u / 3.0
    desc = ''
    if isinstance(shape_result, tuple) and shape_result[0]:
        s, p = shape_result
        if s == 'cone':
            desc = f'cone — {p["range_tiles"]:.2f} tiles, {p["spread_deg"]}°'
        elif s == 'line':
            desc = f'line — {p["range_tiles"]:.2f} tiles, ~{p["width_tiles"]:.1f} wide'
        elif s == 'dash':
            desc = f'dash — {p["range_tiles"]:.2f} tiles'
        elif s == 'arc':
            desc = f'arc — {p["range_tiles"]:.2f} tiles (thrower)'
        elif s == 'placement':
            splash = p.get('splash_tiles', 0)
            desc = f'placement — {p["range_tiles"]:.2f} tile range, {splash:.2f} tile splash' if splash else f'placement — {p["range_tiles"]:.2f} tiles (no splash data)'
        elif s == 'wave':
            desc = f'wave — {p["count"]} projectiles across {p["spread_deg"]}°, {p["splash_tiles"]:.2f} tile splash each'
        elif s == 'cluster':
            n_per_pattern = {'quincunx': 5, 'plus': 5, 'triangle': 3, 'pair': 2, 'hexagon': 7}
            n = n_per_pattern.get(p.get('pattern'), 1)
            desc = f'cluster ({p.get("pattern","?")}) — {p["range_tiles"]:.2f} tile range, {p["splash_tiles"]:.2f} tile splash × {n}'
        elif s == 'area-follow':
            desc = f'area-attack (follows brawler) — {p.get("splash_tiles", 0):.2f} tile radius'
        elif s == 'self-aoe':
            desc = f'self-AoE (no aim)'
    parts.append(f'<text x="{px+10}" y="{py+18}" font-family="monospace" font-size="12" fill="#fff" font-weight="bold">{label[:36]}</text>')
    parts.append(f'<text x="{px+10}" y="{py+34}" font-family="monospace" font-size="9" fill="#9ba3b8">skill: {skill_name[:42]}</text>')
    parts.append(f'<text x="{px+10}" y="{py+47}" font-family="monospace" font-size="9" fill="#9ba3b8">{desc}</text>')
    return '\n'.join(parts)

def render_brawler(b_hash, display_name, char_row):
    variants = collect_variants(char_row, b_hash)
    if not variants:
        return None, 0
    rows_needed = math.ceil(len(variants) / COLS)
    canvas_w = COLS * PANEL_W + (COLS + 1) * PAD
    canvas_h = rows_needed * PANEL_H + (rows_needed + 1) * PAD + TITLE_H

    panels = []
    for i, variant in enumerate(variants):
        # Backwards-compat: variants may be 3-tuples (legacy) or 4-tuples with hyper flag
        if len(variant) == 4:
            label, sname, srow, hyper_mode = variant
        else:
            label, sname, srow = variant
            hyper_mode = False
        col, row = i % COLS, i // COLS
        px = PAD + col * (PANEL_W + PAD)
        py = PAD + TITLE_H + row * (PANEL_H + PAD)
        panels.append(render_panel(px, py, label, sname, srow, b_hash, i, hyper_mode=hyper_mode))

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {canvas_w} {canvas_h}" style="background:#0a0d18;font-family:sans-serif">
  {DEFS}
  <text x="{canvas_w/2}" y="26" text-anchor="middle" font-family="monospace" font-size="18" fill="#fff" font-weight="bold">{display_name} — {len(variants)} reticle variant{'s' if len(variants) != 1 else ''}</text>
  {''.join(panels)}
</svg>'''
    out_path = OUT_DIR / f'{b_hash}.svg'
    out_path.write_text(svg)
    return out_path, len(variants)

# ---- main ----
def main():
    rendered = []
    skipped = []
    total_variants = 0
    no_internal = []

    # Iterate Brawlify brawlers (only playable ones); look up internal name from characters.csv via ItemName
    for b in brawlify_brawlers:
        b_hash = b['hash']
        display = b['name']
        # Find characters.csv row whose ItemName matches b['hash'] (case-insensitive)
        char_row = None
        for c in characters.values():
            if (c.get('ItemName') or '').lower() == b_hash.lower():
                char_row = c
                break
        if not char_row:
            no_internal.append(b_hash)
            continue
        out, n = render_brawler(b_hash, display, char_row)
        if out:
            rendered.append((b_hash, display, n))
            total_variants += n
        else:
            skipped.append((b_hash, 'no usable variants'))

    # ---- index.html ----
    index_html = ['<!doctype html><html><head><meta charset="utf-8"><title>brawl-digram — all reticles</title>',
                  '<style>body{background:#0a0d18;color:#ddd;font-family:system-ui,sans-serif;padding:24px;margin:0}',
                  'h1{margin-top:0}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:16px;margin-top:16px}',
                  '.card{background:#141826;border:1px solid #232a3d;border-radius:8px;padding:10px;text-decoration:none;color:inherit;transition:border-color .15s}',
                  '.card:hover{border-color:#506488}.card img.thumb{display:block;width:60px;height:60px;border-radius:50%;margin:0 auto 8px}',
                  '.name{text-align:center;font-weight:bold;margin-bottom:2px}.count{text-align:center;font-size:11px;color:#9ba3b8;font-family:monospace}',
                  '.stats{color:#9ba3b8;font-family:monospace;font-size:13px}</style></head><body>',
                  f'<h1>brawl-digram — attack reticles</h1>',
                  f'<div class="stats">{len(rendered)} brawlers, {total_variants} reticle variants total. Skipped: {len(no_internal)} not in characters.csv.</div>',
                  '<div class="grid">']
    for b_hash, display, n in sorted(rendered, key=lambda r: r[1]):
        index_html.append(
            f'<a class="card" href="./{b_hash}.svg" target="_blank">'
            f'<img class="thumb" src="../../assets/brawlers/{b_hash}/portrait.png" onerror="this.style.display=\'none\'">'
            f'<div class="name">{display}</div>'
            f'<div class="count">{n} variant{"s" if n != 1 else ""}</div>'
            f'</a>'
        )
    index_html.append('</div></body></html>')
    (OUT_DIR / 'index.html').write_text('\n'.join(index_html))

    print(f'rendered {len(rendered)} brawlers ({total_variants} variants)')
    print(f'skipped {len(no_internal)} brawlers without characters.csv match: {no_internal[:8]}{"..." if len(no_internal) > 8 else ""}')
    print(f'output: {OUT_DIR}/<hash>.svg + index.html')

if __name__ == '__main__':
    main()
