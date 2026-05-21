# Data lookup flow

The Brawl Stars CSV schema in `csv_logic/` is heavily normalized and has several traps that cost us time to discover. This is the canonical recipe for finding any piece of brawler data.

**Rule #1 — always search case-insensitively.** Capitalization is inconsistent across files (`ShotgunGirl` in `characters.csv` vs `Shotgungirl` lower-g in some skills). Use `.lower()` when matching names or grep with `-i`.

**Rule #2 — `cards.csv.Skill` is often stale.** The "true" card → skill link lives in `accessories.csv`. Don't trust `cards.csv.Skill` alone; cross-check `accessories.csv` first.

## How to find anything for a given brawler

Steps below use Shelly as the running example. Substitute the brawler's internal name (e.g. `Cactus` for Spike, `Mummy` for Emz — look up via the `ItemName` column in `characters.csv`).

### 1. Brawler internal name (from display name)
- `characters.csv` row where `ItemName == "shelly"` (lowercase) → `Name = "ShotgunGirl"` (internal).
- Or look in `assets/manifest.json` (Brawlify): `brawlers[].hash` = "Shelly", `brawlers[].name` = display name.

### 2. Base attack + super + hypercharged super geometry
- `characters.csv[Name=ShotgunGirl]` exposes `WeaponSkill`, `UltimateSkill`, `OverchargedUltimateSkill`.
- For each of those, look up `skills.csv[Name=<skill>]`:
  - `CastingRange` → divide by 3 for tiles.
  - `Spread` → already degrees (cones only).
  - `Projectiles` → projectile name to look up next.

### 3. Projectile mechanics (ballistics, splash)
- `projectiles_logic.csv[Name=<projectile>]`:
  - `Speed`, `Gravity`, `Indirect` (thrown vs direct-fire), `BouncePercent`.
  - `Radius` → divide by 480 for tiles (projectile splash).

### 4. Area effects (AoE on impact, on death, on detonation)
- The skill, projectile, or spawned entity points at an area-effect name via fields like `AreaEffect2DamagePercent`, `OnEnemyHitActions`, or (for spawned things) `DeathAreaEffect` in `characters.csv`.
- `area_effects.csv[Name=<effect>]`:
  - `Radius` → divide by 480 for tiles.
  - `Damage` → positive = harm, negative = heal.
  - `Effect`, `FileName` → visual asset references (not needed for geometry).

### 5. Gadgets — USE `accessories.csv`, NOT `cards.csv` alone
- **`accessories.csv[Target=<brawler internal name>]`** lists all real gadgets for that brawler. Each row has a `Skill` column pointing to the actual implementing skill.
- `cards.csv` still has the same gadget by name with card metadata (icon, price, TID) — useful for the *card* but its `Skill` field may reference a non-existent row (e.g., `ShotgunGirl_Dash` → broken). The accessory file resolves this correctly.
- Then `skills.csv[Name=<accessory skill>]` for geometry.
- Example trail: card `ShotgunGirl_Dash` (cards.csv) → accessory `ShotgunGirl_Dash` (accessories.csv) → skill **`ShotgungirlGadgetSkillReload`** (skills.csv, note the lowercase `g`) → `CastingRange=8` → 2.67 tiles dash forward.

### 6. Star powers — same pattern as gadgets
- `accessories.csv[Target=<brawler>, Type=...]` plus `cards.csv` for icon/price.

### 7. Hypercharges
- `cards.csv` rows with `MetaType=6` and `Type=overcharge_*` for the modifier metadata (e.g., `ShotgunGirl_overcharge`, `Type=overcharge_weapon_spread`).
- For shape changes: look for the modified skill in `skills.csv` — naming convention is usually `<Brawler>Overcharged<Type>` (e.g., `ShotgunGirlOverchargedWeapon`). Not every hypercharge changes geometry; many are pure stat multipliers.

### 8. Spawned entities (cactus, turrets, totems, pets)
- The skill or projectile that spawns it has `SummonedCharacters` or `SpawnCharacter` referencing the entity name.
- `characters.csv[Name=<entity>]` — `Hitpoints`, `CollisionRadius` (÷480 for tiles), `DeathAreaEffect` (chains back to step 4).

### 9. Display name lookup (internal → human-readable)
- The CSVs do NOT contain display names for maps or brawlers. Use Brawlify:
  - `assets/manifest.json.brawlers[].hash` matches `characters.csv.Name` (e.g., Brawlify `hash=Shelly` → internal `ShotgunGirl`).
  - Maps need a hand-curated mapping (see `ROADMAP.md` — "name-map.json" task).

## Unit conversions cheat sheet

| Field | Where | Convert to tiles |
|---|---|---|
| `CastingRange` | `skills.csv` | `/3` |
| `Radius` (projectile splash) | `projectiles_logic.csv` | `/480` |
| `Radius` (area effect) | `area_effects.csv` | `/480` |
| `CollisionRadius` | `characters.csv` | `/480` |
| `Spread` | `skills.csv` | (already degrees) |
| `Damage` | various | raw int (negative = heal) |

The /480 divisor is verified against ≥5 in-game references (Spike super, Emz super, Bo splash, Dyna splash, brawler hitboxes — all within ~5%).

## Files NOT needed for reticle rendering

- `locales.csv` is a language-config file, NOT a string table. There are no TID→display-name mappings in the CSVs.
- `skin_*.csv`, `emote*.csv`, `roguelite_*.csv`, `mastery_*.csv`, `competitive_pass_tiers.csv`, etc. — cosmetic / progression systems, ignore.
- `projectiles_skin.csv` — visual variants of `projectiles_logic.csv`, only useful for asset rendering (we don't need it; we render geometrically).

## Lessons learned (mistakes to not repeat)

- **Capitalization inconsistency**: `ShotgunGirl` (most places) vs `Shotgungirl` (some skill names) — search case-insensitively or grep with `-i`.
- **`accessories.csv` exists and is the source of truth for gadget→skill linkage**. `cards.csv.Skill` can be stale.
- **`area_effects.csv` has BOTH visual fields AND geometry** (`Radius`). Don't assume it's "visual only" — earlier we did and missed the cactus heal-burst radius.
- **`projectiles.csv` no longer exists** in modern versions — it was split into `projectiles_logic.csv` and `projectiles_skin.csv`. Older tutorials reference the old name.
