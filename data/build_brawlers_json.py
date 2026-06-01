"""Bake the reticle classifier output into a static brawlers.json for the frontend.

Reuses classification logic from render_all_reticles.py — same infer_shape, same
collect_variants, same per-skill overrides — but emits JSON instead of SVG.

Adds per-brawler mechanics (hp, reload, damage, projectile speed, etc.), Brawlify
star power / gadget / hypercharge descriptions, attackStyle tags, and specialMechanics
plain-English flags. All geometry in TILES, all times in SECONDS, damage as raw int.
"""
import json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render_all_reticles import (  # noqa: E402
    skills, projectiles, characters, load_csv, _overcharge_cards, brawlify_brawlers,
    overrides, infer_shape, collect_variants,
    HYPER_RANGE_MULTIPLIER, HYPER_SPLASH_MULTIPLIER,
)

OUT_PATH = Path(__file__).resolve().parent / 'brawlers.json'

# Speed in characters.csv / projectiles_logic.csv → tiles/sec (same unit system as movement)
SPEED_UNITS_PER_TILE_PER_SEC = 300

PROJECTION_SHAPES = {'placement', 'wave', 'cluster', 'self-aoe', 'area-follow'}

# ---------------------------------------------------------------------------
# Description cleaning — strip Brawlify template tokens that look like noise.
# Keep tokens that are meaningful but unresolved (e.g. "x" placeholders are
# already human-readable as-is; we only strip the internal markup syntax).
# ---------------------------------------------------------------------------
_TOKEN_RE = re.compile(r'<!card\.[^>]+>')

def clean_description(desc: str) -> str:
    if not desc:
        return ''
    # Remove the template markup wrapper (<!card.…>) leaving just the surrounding text.
    # The visible "x" or number placeholders in the plain text are kept.
    cleaned = _TOKEN_RE.sub('?', desc)
    # Collapse multiple spaces / non-breaking spaces
    cleaned = re.sub(r'[ \s]+', ' ', cleaned).strip()
    return cleaned


# ---------------------------------------------------------------------------
# Hypercharge cards index: internal_name → card row
# ---------------------------------------------------------------------------
_all_cards = load_csv('cards.csv')
# MetaType=6 "_overcharge" entries (exclude Buddy variants)
_hc_cards = {
    r['Name'].replace('_overcharge', ''): r
    for r in _all_cards
    if r.get('MetaType') == '6'
    and r.get('Name', '').endswith('_overcharge')
    and not r.get('Name', '').endswith('_Buddy_Overcharge')
}


# ---------------------------------------------------------------------------
# Projectile helper
# ---------------------------------------------------------------------------
def _proj_info(proj_name: str) -> dict | None:
    if not proj_name:
        return None
    # Some skills list multiple projectiles separated by ';'; take the first
    first = proj_name.split(';')[0].strip()
    p = projectiles.get(first.lower())
    if not p:
        return None
    raw_speed = int(p.get('Speed') or 0)
    raw_radius = int(p.get('Radius') or 0)
    bounce_raw = p.get('BouncePercent', '')
    return {
        'indirect': p.get('Indirect') == 'true',
        'bouncePercent': int(bounce_raw) if bounce_raw.strip().lstrip('-').isdigit() else 0,
        'pierce': p.get('PiercesCharacters') == 'true',
        'isBouncing': p.get('IsBouncing') == 'true',
        'speedTilesPerSec': round(raw_speed / SPEED_UNITS_PER_TILE_PER_SEC, 2) if raw_speed else None,
        'radiusTiles': round(raw_radius / 480.0, 3) if raw_radius else 0.0,
    }


def _skill_mechanics(skill_row: dict) -> dict:
    """Extract numeric combat mechanics from a skills.csv row."""
    if not skill_row:
        return {}
    raw_damage  = skill_row.get('Damage', '')
    raw_reload  = skill_row.get('RechargeTime', '')
    raw_ammo    = skill_row.get('MaxCharge', '')
    raw_bullets = skill_row.get('NumBulletsInOneAttack', '')
    proj_name   = (skill_row.get('Projectiles') or '').strip()
    summon      = (skill_row.get('SummonedCharacters') or '').strip()

    def safe(s):
        s = (s or '').strip()
        return int(s) if s.lstrip('-').isdigit() else None

    damage  = safe(raw_damage)
    reload_ms = safe(raw_reload)
    ammo    = safe(raw_ammo)
    bullets = safe(raw_bullets)

    mech = {}
    if damage is not None:
        mech['damage'] = damage
    if reload_ms is not None:
        # RechargeTime is in milliseconds — confirmed: Shelly 1500ms = 1.5s reload
        mech['reloadSec'] = round(reload_ms / 1000.0, 3)
    if ammo is not None:
        mech['ammoCount'] = ammo
    if bullets and bullets > 1:
        mech['numProjectiles'] = bullets
    if summon:
        mech['spawnedEntity'] = summon

    proj_info = _proj_info(proj_name)
    if proj_info:
        mech['projectile'] = proj_info

    return mech


# ---------------------------------------------------------------------------
# attackStyle inference
# ---------------------------------------------------------------------------

# Brawlers whose attack IS a dash — BehaviorType=Charge on the weapon skill with a
# melee range. Mortis/Undertaker is the canonical example; Leaper, Geisha also dash.
_DASH_ATTACK_INTERNALS = {
    'Undertaker',  # Mortis
    'Leaper',      # Fang
    'GeishaWeapon', # Kaze — handled via BehaviorType
    'Samurai',     # Mico — SamuraiWeaponDash
}

# Turret-spawning supers — any ulti skill with a SummonedCharacters value that looks
# like a persistent entity (not a short-lived projectile spawn). We detect this by
# checking the SummonedCharacters field AND the summon being a known turret entity.
# The data already reveals: Jessie(MechanicTurret), Penny(ArtilleryDudeTurret),
# Pam(HealingStation), Mr.P(SpawnerDudeTurret), 8-Bit(DamageBooster).
_TURRET_SUMMONS = {
    'mechanicturret', 'artillerydudeturret', 'healingstation',
    'spawnerdude turret', 'spawnerdueturret', 'spawnerdueturret',
    'damagebooster', 'spawnerdueturret',
}

def _infer_attack_style(char_row: dict, weapon_skill: dict | None, weapon_proj: dict | None,
                        ulti_skill: dict | None) -> str:
    """Return the best-fit attackStyle tag for a brawler."""
    if not weapon_skill:
        return 'unknown'

    internal = char_row.get('Name', '')
    behavior = (weapon_skill.get('BehaviorType') or '').strip()
    spread   = int(weapon_skill.get('Spread') or 0)
    range_u  = int(weapon_skill.get('CastingRange') or 0)
    range_tiles = range_u / 3.0
    bullets  = int(weapon_skill.get('NumBulletsInOneAttack') or 1)
    summon_w = (weapon_skill.get('SummonedCharacters') or '').strip()
    proj_name = (weapon_skill.get('Projectiles') or '').strip()

    # 1. Dash attack — BehaviorType=Charge on the weapon skill
    if behavior == 'Charge':
        return 'dash-attack'

    # 2. Melee — very short range (≤3 tiles) and no meaningful projectile or wide cone
    if range_tiles <= 3.0:
        return 'melee'

    # 3. Thrower — indirect projectile
    if weapon_proj and weapon_proj.get('indirect'):
        return 'thrower'

    # 4. Bouncer — primary projectile bounces
    if weapon_proj and (weapon_proj.get('isBouncing') or (weapon_proj.get('bouncePercent', 0) or 0) > 0):
        return 'bouncer'

    # 5. Shotgun-cone — spread weapon with multiple projectiles
    if spread >= 30 and (bullets > 1 or spread >= 50):
        return 'shotgun-cone'

    # 6. Sniper — long range (≥10 tiles), narrow or zero spread, fast projectile
    if range_tiles >= 10.0 and spread <= 15:
        proj_speed = (weapon_proj or {}).get('speedTilesPerSec') or 0
        if proj_speed >= 10 or range_tiles >= 10:
            return 'sniper'

    # 7. Long-range shot — range ≥9, no spread, direct fire
    if range_tiles >= 9.0 and spread == 0:
        return 'long-range-shot'

    # 8. Default: long-range if range > 6, else melee-ish
    if range_tiles >= 6.0:
        return 'long-range-shot'

    return 'melee'


def _infer_super_style(ulti_skill: dict | None) -> str | None:
    if not ulti_skill:
        return None
    summon = (ulti_skill.get('SummonedCharacters') or '').strip().lower()
    if summon and any(kw in summon for kw in ('turret', 'station', 'booster')):
        return 'turret-deployer'
    return None


# ---------------------------------------------------------------------------
# Special mechanics override table.
# Only entries that CANNOT be reliably inferred from CSV flags alone.
# Each value is a list of plain-English strings.
# ---------------------------------------------------------------------------
_SPECIAL_MECHANICS_OVERRIDES = {
    # Piper: damage scales with distance traveled by projectile.
    # DamagePercentStart=20, DamagePercentEnd=100 on SniperProjectile — detectable,
    # but the plain-English phrasing "charges with distance" isn't obvious from the numbers.
    'Sniper': ['Deals more damage the farther the shot travels (min 20% at close range, max 100% at full range)'],

    # Bea: charged shot mechanic (ChargedShotCount=1 on BeeSniperWeapon)
    'BeeSniper': ['Hitting an enemy charges the next attack, dealing greatly increased damage'],

    # Mortis: his "attack" is literally a dash that damages enemies in its path — Charge behavior
    # with no projectile. This is self-evident from BehaviorType=Charge but the implication
    # (it's a dash through enemies, not a ranged shot) needs a plain-English note.
    'Undertaker': ['Attack is a dash that deals damage to enemies in its path; each hit charges the super'],

    # Edgar: short-range melee punch that heals on hit — the heal isn't in the weapon skill row.
    'Enrager': ['Each melee hit heals Edgar; super launches him into the air with a grappling hook'],

    # Kaze (Geisha): melee dash in human form, transforms into Ninja form on super
    'Geisha': ['Alternates between human (melee dash) and spirit forms; transformation changes attack style'],

    # Amber (FireDude): HoldToShoot attack — player holds to spray a stream, tap to burst
    'FireDude': ['Hold to spray a continuous stream of fire; attack has limited range but high sustained damage'],

    # Nani (Controller): her super launches Peep (pet) that acts as a guided missile
    'Controller': ['Super detaches and remotely controls Peep; Peep explodes on contact or when recalled'],

    # Gale (Blower): super pushes enemies far; not derivable from shape alone
    'Blower': ['Super fires a long-range burst of wind that pushes enemies back significantly'],

    # Squeak (RedirecterSnake): gadget stickies explode with delay
    'RedirecterSnake': ['Attack projectiles (sticky bombs) explode with a short delay after landing'],
}


def _build_special_mechanics(char_row: dict, weapon_skill: dict | None,
                              weapon_proj: dict | None, ulti_skill: dict | None,
                              ulti_proj: dict | None) -> list[str]:
    internal = char_row.get('Name', '')
    mechanics = []

    # Start with override table
    if internal in _SPECIAL_MECHANICS_OVERRIDES:
        mechanics.extend(_SPECIAL_MECHANICS_OVERRIDES[internal])

    # CSV-derivable flags
    if weapon_proj:
        if weapon_proj.get('isBouncing') or (weapon_proj.get('bouncePercent', 0) or 0) > 0:
            mechanics.append('Attack projectiles bounce off walls')
    if ulti_proj:
        if ulti_proj.get('isBouncing') or (ulti_proj.get('bouncePercent', 0) or 0) > 0:
            mechanics.append('Super projectiles bounce off walls')
        if ulti_proj.get('pierce') and not (weapon_proj and weapon_proj.get('pierce')):
            mechanics.append('Super projectile pierces through multiple enemies')

    if weapon_proj and weapon_proj.get('pierce'):
        mechanics.append('Attack projectile pierces through multiple enemies')

    # Turret-deploying super
    if ulti_skill:
        summon = (ulti_skill.get('SummonedCharacters') or '').strip().lower()
        if summon and any(kw in summon for kw in ('turret', 'station', 'booster')):
            mechanics.append('Super spawns a persistent turret or support structure')

    return mechanics


# ---------------------------------------------------------------------------
# passes_walls
# ---------------------------------------------------------------------------
def passes_walls(skill_row, shape):
    if shape in PROJECTION_SHAPES:
        return True
    proj_name = (skill_row.get('Projectiles') or '').strip()
    if proj_name:
        proj = projectiles.get(proj_name.lower())
        if proj and (proj.get('Indirect') == 'true' or proj.get('IgnoreCloseWalls') == 'true'):
            return True
    return False


# ---------------------------------------------------------------------------
# Param normalization
# ---------------------------------------------------------------------------
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
    return {PARAM_KEY_MAP.get(k, k): v for k, v in params.items()}


# ---------------------------------------------------------------------------
# Variant JSON builder
# ---------------------------------------------------------------------------
def variant_to_json(label, skill_name, skill_row, hyper_mode):
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


# ---------------------------------------------------------------------------
# Main brawler entry builder
# ---------------------------------------------------------------------------
def _normalize_for_match(s: str) -> str:
    """Strip hyphens, dots, spaces, ampersands for loose hash→ItemName matching."""
    return s.lower().replace('-', '').replace('.', '').replace(' ', '').replace('&', '')


# Brawlify hash → characters.csv ItemName for brawlers whose display name changed
# or where the hash contains more characters than the ItemName.
_HASH_TO_ITEM_OVERRIDES = {
    'Rico':     'ricochet',  # renamed from Ricochet; ItemName not updated in v67.264 CSV
    'Jae-Yong': 'jae',       # Alternator internally; Brawlify uses full "Jae-Yong" name
}


def _find_char(b_hash: str):
    """Find the characters.csv row for a Brawlify hash, trying exact then normalized match."""
    # Explicit override first (for name changes between CSV dump and Brawlify)
    if b_hash in _HASH_TO_ITEM_OVERRIDES:
        target = _HASH_TO_ITEM_OVERRIDES[b_hash].lower()
        for c in characters.values():
            if (c.get('ItemName') or '').lower() == target:
                return c
    exact_lower = b_hash.lower()
    norm = _normalize_for_match(b_hash)
    for c in characters.values():
        item = (c.get('ItemName') or '').lower()
        if item == exact_lower:
            return c
    # Normalized fallback (handles 'El-Primo'→'elprimo', '8-Bit'→'8bit', etc.)
    for c in characters.values():
        item_norm = _normalize_for_match(c.get('ItemName') or '')
        if item_norm and item_norm == norm:
            return c
    return None


def build_brawler_entry(b):
    """One playable brawler's entry. Returns None if no characters.csv match."""
    b_hash = b['hash']
    char = _find_char(b_hash)
    if not char:
        return None

    # --- speed ---
    try:
        speed_raw = int(char.get('Speed') or 0)
    except ValueError:
        speed_raw = 0
    speed_tps = round(speed_raw / SPEED_UNITS_PER_TILE_PER_SEC, 3) if speed_raw else None

    # --- HP ---
    try:
        hp = int(char.get('Hitpoints') or 0) or None
    except ValueError:
        hp = None

    # --- weapon / super skill rows ---
    weapon_name = char.get('WeaponSkill', '')
    ulti_name   = char.get('UltimateSkill', '')
    weapon_row  = skills.get(weapon_name.lower()) if weapon_name else None
    ulti_row    = skills.get(ulti_name.lower()) if ulti_name else None

    weapon_proj_info = _proj_info((weapon_row.get('Projectiles') or '').strip()) if weapon_row else None
    ulti_proj_info   = _proj_info((ulti_row.get('Projectiles') or '').strip()) if ulti_row else None

    # --- mechanics blocks ---
    attack_mech = _skill_mechanics(weapon_row) if weapon_row else {}
    super_mech  = _skill_mechanics(ulti_row)   if ulti_row   else {}

    # --- reticle variants ---
    variants_raw = collect_variants(char, b_hash)
    variants_json = []
    for v in variants_raw:
        if len(v) == 4:
            label, sname, srow, hyper_mode = v
        else:
            label, sname, srow = v
            hyper_mode = False
        variants_json.append(variant_to_json(label, sname, srow, hyper_mode))

    # --- star powers / gadgets from Brawlify ---
    star_powers = [
        {'name': sp['name'], 'description': clean_description(sp.get('description', ''))}
        for sp in b.get('starPowers', [])
    ]
    gadgets = [
        {'name': g['name'], 'description': clean_description(g.get('description', ''))}
        for g in b.get('gadgets', [])
    ]

    # --- hypercharge ---
    internal_name = char['Name']
    hc_card = _hc_cards.get(internal_name)
    hypercharge = None
    if hc_card:
        hc_type = hc_card.get('Type', '')
        hc_val  = hc_card.get('Value', '')
        hc_val2 = hc_card.get('Value2', '')
        multipliers = {}
        # Universal stat boosts (all hypercharges get +25% damage/speed/shield)
        # Unique modifiers live in Type + Value fields
        if hc_val.strip():
            multipliers['value'] = hc_val.strip()
        if hc_val2.strip():
            multipliers['value2'] = hc_val2.strip()
        hypercharge = {
            'type': hc_type,
            'multipliers': multipliers if multipliers else None,
        }

    # --- attackStyle + specialMechanics ---
    attack_style = _infer_attack_style(char, weapon_row, weapon_proj_info, ulti_row)

    # Annotate turret-deploying supers into style for the super
    super_style = _infer_super_style(ulti_row)

    special_mechanics = _build_special_mechanics(
        char, weapon_row, weapon_proj_info, ulti_row, ulti_proj_info
    )

    return {
        'id': b['id'],
        'hash': b_hash,
        'name': b['name'],
        'internalName': internal_name,
        'class': b.get('class', {}).get('name'),
        'rarity': b.get('rarity', {}).get('name'),
        'hasHypercharge': internal_name in _overcharge_cards,
        'speedTilesPerSec': speed_tps,
        'hp': hp,
        'attack': attack_mech,
        'super': super_mech,
        'attackStyle': attack_style,
        'superStyle': super_style,
        'starPowers': star_powers,
        'gadgets': gadgets,
        'hypercharge': hypercharge,
        'specialMechanics': special_mechanics,
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
            'units': (
                'All geometry in TILES (1 tile = standard Brawl Stars grid square). '
                'rangeTiles, splashTiles, widthTiles, spacingTiles are tile distances. '
                'spreadDeg is degrees. speedTilesPerSec is tiles/sec. '
                'reloadSec is seconds (converted from ms). '
                'damage is raw integer (positive=harm). '
                'See data/SCHEMA_FLOW.md for CSV unit conventions.'
            ),
            'passesWalls': (
                'true → reticle projects over walls (placements, throwers, indirect projectiles); '
                'false → solid reticle clipped against wall tiles when rendered on a map.'
            ),
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
