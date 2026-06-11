# Interactable Game Simulation — Design Document (2026-06-10)

**Status:** Proposed design for Daniel's review — no implementation yet.
**Scope:** Turn placed brawler tokens into live entities with a scene-graph
outliner, simulate their attacks/supers/gadgets as real projectiles over the
map, and destroy destructible terrain on impact — layered on top of the
existing static whiteboard (`prototype/whiteboard.html`) without breaking any
current behavior.

---

## 1. Summary of the recommended architecture

**One-line recommendation: extend the existing `tokens[]` objects into "units"
with derived ability child-nodes, add a non-serialized `sim` runtime (fixed-
timestep tick driven by the existing PIXI ticker), and implement destruction
through the existing `brokenTiles` set — not through grid mutation and not
through a new ECS.**

Rationale, stated up front because everything else follows from it:

- The whiteboard already has a clean plain-data state model: `tokens[]` +
  `currentMap.grid` + `brokenTiles`, snapshotted by `snapshotScene()` for
  undo/autosave. A parallel entity system would mean two sources of truth and
  a migration of undo/autosave/Y.js plans. Instead the unit/entity **is** the
  token, enriched.
- The ability "children" in the hierarchy carry almost no state of their own —
  their geometry/params live in `brawlers.json` variants, which the token
  already references via `variantIdx`. Children are therefore **derived
  views** (brawler.variants) plus a tiny per-token state record, not
  independently serialized objects. This keeps `snapshotScene()` changes to a
  few optional fields and old autosaves loading unchanged.
- Projectiles, explosions, and debris particles are **ephemeral**: they exist
  only during a simulation run, are never serialized, never enter undo
  history, and live in a separate `sim.objects` array rendered into one new
  PIXI container. Only their *consequences* (destroyed tiles) enter scene
  state.
- `charAtTile()` already treats `brokenTiles` entries as `"."`, which means
  vision rays, movement flood-fill, reticle clipping, and draft geometry all
  *automatically* respect simulated destruction with zero extra code. This is
  the single biggest reason to use `brokenTiles` as the destruction mechanism
  rather than rewriting grid strings.

A full ECS (components + systems) is explicitly rejected for the prototype:
the scene is ≤ 20 tokens and ≤ 64 projectiles, the file is a single 3.3k-line
HTML page, and ECS indirection buys nothing at this scale. The
Next.js/`@pixi/react` port is the right place to formalize (see §10).

---

## 2. Data audit — what exists, what must be baked

### 2.1 Already available (verified against the repo)

**`data/brawlers.json`** (104 brawlers) already bakes, per brawler:

- `attack` / `super` blocks with `damage`, `reloadSec`, `ammoCount`, sometimes
  `numProjectiles` (22/104 brawlers, e.g. Shelly attack = 5, super = 9,
  Dynamike attack = 2), and a `projectile` sub-object: `{indirect,
  bouncePercent, pierce, isBouncing, speedTilesPerSec, radiusTiles}`. Speeds
  are real (Shelly pellets 10.33 t/s, Colt 13.33 t/s, Barley lob 5.83 t/s) —
  the loader already normalizes the CSV `Speed` field to tiles/sec.
- `variants[]` — the reticle records the whiteboard renders today: `{label,
  skillName, shape, params{rangeTiles, spreadDeg, widthTiles, splashTiles,
  pattern, spacingTiles, count, equip}, passesWalls, isHyper}`. Shape
  distribution across all variants: line 81, placement 58, cone 43, dash 23,
  self-aoe 19, area-follow 9, cluster 9, wave 4.

**CSV ground truth for destruction** (this is the key finding):

1. **Projectile-level wall-break:** `csv_logic/projectiles_logic.csv` columns
   `PiercesEnvironment`, `PiercesEnvironmentLikeButter`, `PassesEnvironment`.
   34 rows are true, including `ShotgunGirlUltiProjectile` (Shelly super),
   `GunslingerUltiProjectile` (Colt super), `GunslingerSilverBulletProjectile`
   (Colt's wall-break gadget), `HammerDudeUltiProjectile`. Semantics: the
   projectile destroys blocking tiles it touches **and keeps flying**.
2. **Explosion-level wall-break:** `csv_logic/area_effects.csv` column
   `DestroysEnvironment` (93 true rows: `TntDudeUltiExplosion`,
   `RocketGirlUltiExplosion` (Brock), `Piper_def_ulti`,
   `BlackHoleUltiExplosion` (Tara), Bo mines, Nani, Chester, etc.), plus
   `DestroysOnlyBushes` and `Radius` (480 units/tile). Semantics: destruction
   happens in a circle at the landing/explosion point.
3. **The linkage chain** (verified end-to-end for Dynamike):
   `skills.csv.Projectiles` → projectile name →
   `projectiles_skin.csv.SpawnAreaEffectObject` → `area_effects.csv` row →
   `DestroysEnvironment`. Example: `TntDudeUlti → TntDudeUltiProjectile →
   (skin) TntDudeUltiExplosion → DestroysEnvironment=true, Radius=800
   (1.67 t)`. Also useful from `skills.csv`: `NumBulletsInOneAttack`,
   `MsBetweenAttacks`, `Spread`; from `projectiles_logic.csv`: `Gravity`,
   `ConstantFlyTime`, `IsBouncing`, `MaxDistanceBounces`,
   `DistanceAddFromBounce`.

**`data/maps.json` `tileLegend`** gives per-char flags the sim needs:
`blocksProjectiles`, `blocksMovement`, `isDestructible`, `isForest`.
Destructible blockers: `M, X, Y, C, B, T, N, a, o` (walls, crates, barrels,
fences, bouncers). Destructible non-blockers: `F`, `R` (bushes). **Not**
destructible: `I` (indestructible), `J` (invisible indestructible), `E`
(indestructible fence), `W`/`V` (water), the `À–Ã` damageable set. The
whiteboard already builds `destructSet` from `isDestructible` and uses it in
manual wall-break mode.

**`data/ability_mechanics.json`** (521 records) provides modifier records
(`projectileMod`, `rangeMod`, `movementMod`, `spawnsEntity`, `statusEffects`)
with `csvVerified` flags — used for gadget/star-power children (e.g. Brock
"Rocket Fuel": next rocket destroys walls; Belle "Reverse Polarity": next
attack bounces).

### 2.2 Gaps — what the loader must newly bake

`brawlers.json` variants today carry **reticle geometry only**. The simulation
needs kinematics and destruction *per variant* (the top-level
`attack.projectile`/`super.projectile` blocks cover only two of N variants and
don't exist for gadgets). Extend `data/build_brawlers_json.py` to attach a
`sim` block to every variant:

```json
"variants": [{
  "label": "Super",
  "skillName": "ShotgunGirlUlti",
  "shape": "cone",
  "params": { "rangeTiles": 7.67, "spreadDeg": 100 },
  "passesWalls": false,
  "sim": {
    "projectileName": "ShotgunGirlUltiProjectile",
    "speedTilesPerSec": 13.77,
    "projRadiusTiles": 0.104,
    "numProjectiles": 9,
    "msBetweenAttacks": 100,
    "piercesChars": true,
    "breaksWalls": true,
    "breakMode": "pierce",
    "indirect": false,
    "isBouncing": false, "bounceAddTiles": 0, "maxBounces": 0,
    "explosion": null
  }
}]
```

(`numProjectiles` = skills.NumBulletsInOneAttack; `breaksWalls` =
PiercesEnvironment || PiercesEnvironmentLikeButter; `breakMode` = `"pierce"`
(destroy + continue) | `"explode"` (at landing); `explosion` = `{radiusTiles,
destroysWalls, bushesOnly}` or null.)

Resolution order in the loader: skill row → `Projectiles` →
`projectiles_logic` row (speed/flags/radius) → `projectiles_skin` row →
`SpawnAreaEffectObject` → `area_effects` row (`Radius/480`,
`DestroysEnvironment`, `DestroysOnlyBushes`). Where the classifier guesses
wrong, add a `data/sim_overrides.json` mirroring the proven
`reticle_overrides.json` pattern (per-skill override + `note` + source URL).
Expect ~10–20 overrides; seed it by spot-checking the known wall-breakers:
Shelly super, Colt super + Silver Bullet, Brock super + Rocket Fuel, Dynamike
super, Barley hyper, Piper super, Tara super, Bo super, Nani super, Frank
super, El Primo super (meteor: `LuchadorMeteorExplosion` is in the true-list).

This is **P0** and is pure data-loader work — no frontend risk.

---

## 3. Entity / hierarchy model

### 3.1 Token → unit

A placed brawler token becomes a **unit** by adding fields to the existing
token object created in `createTokenFromData()`:

```js
{
  // --- existing, unchanged ---
  id, brawler, variant, variantIdx, tx, ty, angle, team, el,
  kind: "brawler" | "projectile" | "spawn", spawnSpec, reachTiles,
  // --- new, all optional with defaults ---
  abilityState: {                  // keyed by variantIdx
    0: { aimAngle: -1.57, aimReach: null, locked: false },
  },
  modifiers: { stars: [], gadgetArmed: null },
}
```

Key design decision: **the existing `variantIdx` becomes the "selected
child"**. It already controls which reticle draws and is already serialized —
so "click a brawler, pick its super in the outliner, see the super reticle"
is a re-selection of `variantIdx` on a live token, not a new mechanism.
`serializeTokens()` adds `abilityState` and `modifiers` as optional fields.

**Backwards compatibility / migration:** none needed in the breaking sense.
`SCENE_KEY` stays `"wb_scene_v1"`. Old autosaves/undo snapshots simply lack
the new fields; `createTokenFromData()` defaults them (`abilityState ??= {}`).
New snapshots carry extra keys that nothing else reads. The
`kind:"projectile"` frozen-reticle tokens and `kind:"spawn"` turret tokens are
untouched — they appear in the outliner as leaf units with no children.

### 3.2 Child objects (derived, not stored)

For each unit the outliner derives children from `brawler.variants` (exactly
the same source as the `#variantRow` chips today, including the gadget-ordinal
display-name mapping in `variantClassify`):

| Child type | Source | Selecting it means | "Manipulating" it means |
|---|---|---|---|
| Attack | variant `label:"Attack"` | `token.variantIdx = i`, reticle redraws | aim (angle/reach), **Fire** |
| Super | variant `label:"Super"` | same | aim, **Fire** (with destruction) |
| Hypercharged X | `isHyper` variants | same (purple reticle) | aim, **Fire** |
| Gadget | `label:"Gadget:*"` variants | same | aim, **Fire**; dash gadgets animate the unit itself |
| Star power | `kits.stars` + `ability_mechanics` | toggle on/off (checkbox node, no reticle) | applies `rangeMod`/`projectileMod` etc. to sibling abilities |
| Spawned entity | `SPAWN_ENTITIES` table | selecting jumps to the linked spawn token if placed | (already exists as separate token) |

Star-power children are the only ones that are *pure modifiers*; v1 ships
them as display-only toggles wired to the three already-parsed mechanics
(`rangeMod.flat/multiplier`, `projectileMod.speedMultiplier`, `spreadMod`)
and ignores the rest.

---

## 4. Scene-graph / outliner UI

### 4.1 Placement in the existing panel

Recommendation: **upgrade the existing "Placed tokens" section** (`#placed`,
inside the Brawlers tab, `renderPlacedList()`) into the outliner, rather than
adding a 4th tab. Reasons: the section already exists, already syncs selection
both ways, lives where the user's eyes are during placement, and a 4th tab
would hide the hierarchy exactly when interacting on canvas. Rename its
`<summary>` to "Scene".

### 4.2 Visual design

Blender-style indented tree, reusing existing row styling:

```
▾ 🟦 Shelly                      ✕
    ◉ Attack          (cone 7.7t)
    ★ Super           (cone 7.7t) 💥   ← 💥 = breaksWalls badge
    ⚡ Hypercharged Super
    ◌ Gadget: Dash
    ◌ Gadget: Focus
    ☐ Star: Shell Shock                ← toggle
▸ 🟥 Dynamike                    ✕
▸ 🟦 Jessie's Scrappy (spawn)    ✕
```

- Unit row: team color dot + portrait thumb + name + delete ✕ (exists today).
  Click = `selectToken(id)` (exists). Disclosure triangle expands children;
  auto-expand on selection.
- Child rows: type icon recolored with the existing
  `t-attack/t-super/t-gadget/t-hyper/t-star` palette, label, compact params, a
  💥 badge when `sim.breaksWalls`. Click = set `variantIdx` + enter
  **fire-aim mode** (§7). Selected child gets the cyan `sel` treatment.
- A **Fire ▶** button and **Replay ⟲** button render inline on the selected
  child row.

### 4.3 Selection sync

- Canvas → outliner: `selectToken()` already calls `renderPlacedList()`; the
  outliner highlights the unit and its active child (`variantIdx`).
- Outliner → canvas: child click updates `variantIdx`, calls
  `positionSprite`/`redraw()` so the canvas reticle switches instantly, and
  arms fire mode.
- The sticky `#pickedCard` variant chips remain the *pre-placement* selector;
  the outliner is the *post-placement* one. Same data, two contexts — no
  behavior collision because `#pickedCard` operates on `brawlerSel.value`
  (next token) while the outliner operates on `tokens[i]`.

---

## 5. Simulation core

### 5.1 Tick loop

- **Driver:** `app.ticker` (PIXI v8's Application already runs a render
  ticker, so hooking it costs nothing new).
- **Timestep:** fixed-step accumulator at 120 Hz sim / rendered every frame,
  capped at 4 steps per frame to avoid spiral-of-death on tab-resume. Fixed
  step matters because collision is sampled along the path; 120 Hz × max
  speed ~17 t/s = 0.14 t per step, below the smallest meaningful obstacle
  features when combined with the substep rule below.
- **Start/stop:** a single `simTick` callback is registered once; a
  `sim.active` flag short-circuits it when `sim.objects` is empty.
  `sim.objects` empties → one final cleanup render → `sim.active = false`.
  No `requestAnimationFrame` bookkeeping of our own.

```js
const sim = { active: false, objects: [], accumulator: 0, STEP: 1/120, MAX_OBJECTS: 64 };
app.ticker.add((t) => { if (!sim.active) return; stepSim(t.deltaMS / 1000); drawSim(); });
```

New PIXI layer: `simLayer` inserted between `reticleLayer` and `tokenLayer`,
so projectiles render above reticles but under tokens, matching the existing
z philosophy.

### 5.2 Projectile object (tile units throughout)

```js
{ kind: "bullet" | "lob" | "splash" | "ring" | "dashGhost",
  x, y, angle, speed,            // tiles, radians, tiles/sec
  traveled: 0, maxDist,          // range termination
  radius,                        // collision + draw radius (tiles)
  flags: { breaksWalls, breakMode, pierceChars, indirect, bouncing, bouncesLeft },
  explosion,                     // { radiusTiles, destroysWalls, bushesOnly } | null
  ownerTokenId, team, color, bornAt, ttl,
  // lob-only:
  sx, sy, txT, tyT, flightT, t01 } // start, target, flight time, progress
```

### 5.3 Direct projectile stepping & collision vs grid

Per fixed step: advance `d = speed * STEP` along `angle`, but sample
`charAtTile`/`blockProjSet` at substeps of `min(0.08, radius || 0.08)` tiles —
the same 0.08 granularity `raycastTiles()` already uses, so the sim's stopping
point **pixel-matches the reticle clip** the user saw while aiming (important
for trust). On hitting a blocking tile:

- `breaksWalls && breakMode === "pierce"` → if tile char ∈ `destructSet`:
  destroy it (§6) and continue; if indestructible (`I/J/E`): stop, spawn
  impact puff.
- otherwise → stop; if `explosion` present, detonate at impact point.
- `bouncing` (Rico — P4): reflect across the wall normal inferred from which
  substep axis crossed the tile boundary; decrement `bouncesLeft`; extend
  `maxDist` by `bounceAddTiles` once.

Range termination: `traveled >= maxDist` → despawn (or detonate if
`explosion`). Map border: `charAtTile` returns `null` → treated as blocking,
never destructible.

**Collision vs entities (v1: visual only).** Each step, test distance to
every enemy-team token center against `0.5 + radius`; on hit, flash the
token's frame red for 300 ms and float the variant's `damage` number;
`pierceChars` continues, otherwise despawn. No HP bookkeeping until P4. This
is cheap (≤ 20 tokens × ≤ 64 projectiles, only while sim active).

### 5.4 Shape primitive → simulation behavior (all 9)

| Shape | Fire behavior |
|---|---|
| **cone** (Shelly, shotguns) | Spawn `sim.numProjectiles` (default 5) bullets simultaneously, angles uniform across `spreadDeg` centered on aim; each speed `sim.speedTilesPerSec`, `maxDist = rangeTiles`. Walls clip per pellet — a shotgun blast visibly wraps around cover edges. |
| **line** (Colt, Brock, Piper) | If `numProjectiles > 1`: **sequential burst**, one bullet every `msBetweenAttacks` (Colt's 6-round rattle). Bullet collision width = `widthTiles/2` or `projRadiusTiles`. |
| **dash** (Shelly gadget, Mortis) | No projectile: animate the **unit itself** along the aim ray at ~4× move speed, clamped by `raycastTiles` (walls stop dashes) unless mechanics `ignoresWalls`. Mutates `tx,ty` → one `pushHistory()` before the dash so undo restores position. |
| **placement** (Barley, Dynamike super, Piper super) | **Lob**: `flags.indirect = true`, no mid-flight wall collision. Target = current aim point clamped to `rangeTiles` (the existing `reachTiles` aim value). Flight time = `dist / speedTilesPerSec`. Ground position interpolates start→target; the **arc is purely visual**: sprite y-offset `−h·4t(1−t)·cell` with `h ≈ 0.35 + 0.15·dist` tiles, plus a ground shadow dot at the true position (sidesteps the 3D wall question — §9 problem 1). On landing: splash circle ring-expand, apply `explosion` destruction. |
| **cluster** (Dynamike attack, Barley super quincunx) | Lob to landing point, then spawn one `splash` per `clusterOffsets(pattern, spacingTiles)` offset (function already exists for reticles — reuse), staggered 60 ms apart, each applying its own explosion. |
| **wave** (Brock super: `count 5, spreadDeg 160`) | N independent lobs launched simultaneously, target points fanned across `spreadDeg` at `rangeTiles` (matching the reticle's wave arc), staggered 80 ms; each landing applies destruction. Reads exactly like Rocket Rain. |
| **area-follow** (guided) | A `splash` object that **crawls** from caster toward the aim point at `speedTilesPerSec`, ignoring walls (`passesWalls` is true for all 9 such variants), rendering its `splashTiles` circle continuously; despawns at target or `ttl`. v1 keeps it non-steerable (straight to locked aim). |
| **self-aoe** (Bolt super, El Primo-style) | Instant: ring-expand animation from the unit over 300 ms to `splashTiles`; apply explosion destruction centered on the unit if flagged. |
| **circle/default fallback** | No projectile; pulse the range ring once. Fire button still gives feedback, never errors. |

Multi-projectile **spread fan-out** rule (shared by cone & wave): angle_i =
`aim − spread/2 + spread·i/(N−1)`; for `N = 1` use aim directly. Hypercharge
variants read the same `sim` block of their base skill unless the loader baked
an overcharged projectile row (e.g. `ShotgunGirlOverchargedUltiProjectile`
exists and also pierces environment).

### 5.5 Rendering

One `PIXI.Graphics` per frame redraw inside `simLayer` (clear + redraw all
objects — at ≤ 64 circles this is trivial): bullets = small filled circles
with short motion-trail line, team-tinted; lobs = circle + shadow dot;
splashes = expanding ring with fading fill (reuse `splash()` styling);
destruction = per-tile rubble burst particle (6 dots, 400 ms, gravity-free
fade). No textures needed; the whiteboard's vector aesthetic is preserved.

---

## 6. Destructible terrain

### 6.1 Mechanism: `brokenTiles`, not grid mutation

```js
function destroyTile(x, y) {
  const ch = currentMap.grid[y]?.[x];
  if (!ch || !destructSet.has(ch) || brokenTiles.has(tk(x,y))) return false;
  brokenTiles.add(tk(x, y));
  refreshCells(x, y);        // existing incremental re-render (3×3 for autotile)
  return true;
}
```

Why this and not editing the grid string: (a) `charAtTile()` already overlays
`brokenTiles` as open ground, so **vision, movement reach, reticle
ray-clipping, and the manual wall-break mode all already understand it**;
(b) the original map stays pristine, making "Reset map" a one-liner;
(c) `snapshotScene()` already serializes `broken`, so undo/redo and autosave
work with zero schema change; (d) the manual "Break walls" click mode and
simulated destruction share one representation (a sim-broken wall can be
hand-restored by clicking it in wall-break mode — free feature).

**Which tiles break:** blocking destructibles from `destructSet`
(`M X Y C B T N a o`). Explosions with `destroysWalls` also clear bushes
(`F`, `R`) in radius (in-game behavior); `bushesOnly` explosions clear only
bushes. `I/J/E/W/V` and the border never break. Pierce-mode wall-breakers
(Shelly/Colt supers) destroy only the blocking tiles actually touched along
the path; they do not clear bushes (matches game).

**Explosion footprint:** all tiles whose **centers** lie within
`explosion.radiusTiles` of the landing point. Dynamike super r=1.67 → a
satisfying ~3-tile-wide hole, matching in-game.

### 6.2 Undo / reset semantics (chosen resolution to hard problem 3)

- **Fire = one undoable action.** `pushHistory()` is called once at the moment
  of firing *any* skill whose `sim.breaksWalls` is true (or that dashes the
  unit). ⌘Z after a Dynamike super restores all walls that volley broke in one
  step — matching how paint strokes are one undo entry. Firing a
  non-destructive skill does **not** push history (nothing in scene state
  changed; projectile flight is ephemeral and never undoable).
- **"Reset map" button** (new, next to the wall-break button):
  `pushHistory(); brokenTiles.clear(); drawMap(); redraw();` — restores all
  destruction (manual + simulated) without touching painted tile edits.
  Itself undoable.
- **Map-maker interaction:** `paintCell()` gets one added line —
  `brokenTiles.delete(tk(tx,ty))` — so painting over a broken cell resurrects
  it cleanly (today painting a broken cell leaves a stale broken key; this is
  a latent bug worth fixing in the same change). `validateMap()` keeps reading
  the raw grid (broken walls shouldn't fail spawn checks); optionally a P4
  enhancement treats broken as walkable in the reachability BFS.

### 6.3 Broken-block visuals

Today a broken tile renders as nothing + a small dark debris dot from
`drawDebris()`. That's too subtle to "demo a play". Proposal, consistent with
the official-SVG art style:

In `renderCell()`, replace the early-return for broken tiles with a **ghost
stamp**: stamp the same variant SVG the intact tile would use, wrapped in a
`tile-broken` class:

```css
#mapGrid .tile-sprite.tile-broken { opacity:.22; filter:grayscale(.8) brightness(.7); }
#mapGrid .tile-broken::after {  /* rubble: 3 small stones, inline SVG bg */
  content:""; position:absolute; inset:auto 8% 4% 8%; height:38%;
  background:url("data:image/svg+xml,...three grey polygon pebbles...") center/contain no-repeat;
}
```

The faded original silhouette tells you *what* was there (crate vs wall vs
fence — tactically relevant), the rubble tells you it's gone, and shots/units
visibly pass over it. The PIXI `drawDebris()` dots are kept (they double as
the "recently destroyed" marker) but shrunk. Persistence is automatic: visuals
derive from `brokenTiles`, which is already in autosave/undo snapshots. The
transient destruction *moment* gets a one-shot particle burst in `simLayer`
(not persisted).

---

## 7. Interact mode — input flow, modes, Esc

### 7.1 Mode model

A new top-level mode, `fireArm = { tokenId, variantIdx } | null`, is
**mutually exclusive** with paint, wall-break, and placement, enforced exactly
the way the existing modes police each other (each setter clears the others;
`refreshPlaceState()` derives the banner). Entering fire mode: click a child
ability in the outliner, or press **F** with a unit selected (arms its current
`variantIdx`). New banner state:

```
banner.className = "fire";   // new CSS: orange (#fb923c family)
banner.textContent = "🔥 Shelly · Super — aim, click to FIRE";
```

### 7.2 Aim & fire flow

1. **Arm** — `fireArm` set; `placing` derivation gains `&& !fireArm`; reticle
   for the armed variant follows the cursor using the **existing aim
   machinery** (`aimingId = tokenId`, the `pointermove` handler already
   updates `angle` + `reachTiles` and redraws — zero new aiming code;
   `reachTiles` is exactly the lob landing distance).
2. **Fire** — a map click while `fireArm` is active calls
   `fireSkill(token, variantIdx)` instead of aim-lock; also the outliner
   **Fire ▶** button and **Space**. The aim stays armed afterward (angle
   persists), so repeated clicks re-fire — good for demoing "break, then
   shoot through the gap" without re-arming. The pointertap handler gains one
   branch *above* the `aimingId` lock branch, gated on `fireArm != null`.
3. **Multi-step plays**: fire Dynamike super (wall breaks) → click Piper in
   outliner → arm attack → the attack reticle now extends through the new gap
   (automatic — `raycastTiles` consults `charAtTile` which consults
   `brokenTiles`) → fire.
4. **Replay / clear**: each unit stores `lastShot = {variantIdx, angle,
   reach}`; **⟲ Replay** re-fires it (useful after undoing destruction to
   re-demo). A **Clear effects** action (button + automatic on Esc) empties
   `sim.objects` instantly.

### 7.3 Esc cascade (extended, order matters)

1. `sim.objects.length` → clear in-flight projectiles/effects (does **not**
   undo destruction)
2. `fireArm != null` → disarm fire mode (keep token selected)
3. `aimingId != null` → cancel aim *(existing)*
4. `paintTileCode != null` → exit paint *(existing)*
5. `wallBreakMode` → off *(existing)*
6. `brawlerSel.value` → clear armed brawler *(existing)*
7. `selectedId != null` → deselect token *(existing)*

Steps 1–2 prepend; 3–7 are byte-identical to today, preserving muscle memory.

### 7.4 Keyboard summary

`F` arm/cycle fire on selected unit's current ability · `Space`/click fire ·
`Tab` cycle ability children of selected unit · `Esc` cascade above ·
everything existing (⌘Z/⇧⌘Z, arrows, Delete) unchanged.

---

## 8. Performance & ticker hygiene

- **Caps:** `MAX_OBJECTS = 64` projectiles+effects; firing while full despawns
  oldest. Worst realistic case (Brock hyper wave + Shelly hyper 12 pellets
  simultaneously) ≈ 20 objects.
- **Per-step cost:** 64 objects × ~2 substeps × O(1) `charAtTile` string
  index — microseconds. Token-collision check is 64 × 20 distance checks. The
  fixed-step accumulator caps at 4 steps/frame.
- **Render cost:** one Graphics clear+rebuild in `simLayer` per frame while
  active; PIXI already renders every frame via its default ticker, so the sim
  adds no new render loop — only the `sim.active` guard keeps idle frames at
  today's cost.
- **No DOM churn:** projectiles are PIXI-only; the HTML layers (`#mapGrid`,
  tokens) are touched only on destruction (`refreshCells`, max 9 cells per
  broken tile) — the same incremental path drag-painting already proved out.
- **Autosave:** firing non-destructive shots never calls `saveSceneSoon()`;
  destruction calls it once per fire.

---

## 9. The three genuinely hard problems & chosen resolutions

**1. Thrower arc vs. wall collision semantics.** Simulating a true 3D parabola
against 2D wall tiles invites endless edge cases. **Resolution: lobs are 2D
ground-path objects with a purely cosmetic arc offset.** `indirect`
projectiles never collide mid-flight (`passesWalls` is already true for every
placement/cluster/wave variant in the data), always land exactly at the aimed
point clamped to range, and all interaction happens at the landing splash.
This matches actual Brawl Stars behavior (throwers clear any wall regardless
of height), matches the existing reticle convention ("dotted line to landing
center, NOT a parabolic arc" — CLAUDE.md), and reduces the lob to:
interpolate, draw shadow + offset sprite, detonate. The one visible
approximation — Dynamike sticks bounce (`BouncePercent=35`) past their landing
point — is deliberately ignored in v1 and noted in the UI as "landing point
approximate".

**2. Per-skill kinematics/destruction data gaps.** `brawlers.json` has no
per-variant speed, no projectile count for 82/104 brawlers' multi-shot
patterns, and no wall-break flags at all. **Resolution: bake, don't hardcode**
(§2.2): extend `build_brawlers_json.py` to walk skill → projectile → skin →
area-effect, emit the `sim` block per variant, with `sim_overrides.json` for
the misfits, validated by a checklist of ~12 known wall-breaking skills before
any frontend work starts. The frontend treats missing `sim` blocks gracefully:
no speed → 10 t/s default and an "approx" tag in the outliner tooltip; no
`breaksWalls` data → skill simply doesn't destroy (never a false positive).

**3. Undo semantics for destroyed terrain.** Is a fired shot undoable? Is
destruction part of the map or the sim? **Resolution: ephemeral flight,
durable craters, snapshot-undo.** Only scene-state mutations (destroyed tiles,
dash-moved units) push history, one entry per fire action; `brokenTiles` stays
the single destruction ledger shared with manual wall-break mode; "Reset map"
clears it wholesale and is itself one undo entry. This keeps
`snapshotScene()`'s shape stable and means the undo stack never contains
mid-flight projectiles (which would be unserializable and meaningless).

---

## 10. Phasing, effort, risks

| Phase | Scope | Effort | Exit criteria |
|---|---|---|---|
| **P0 — Data bake** | `sim` block per variant in `build_brawlers_json.py`; `sim_overrides.json`; wall-breaker checklist verified (Shelly/Colt/Brock/Dyna/Piper/Tara/Bo/Nani/Primo/Frank + Colt & Brock gadgets) | 0.5–1 d | `brawlers.json` diff reviewed; whiteboard boots unchanged (additive JSON) |
| **P1 — Hierarchy & outliner** | Token `abilityState`; `renderPlacedList` → outliner tree; child selection drives `variantIdx`; selection sync; serialization additions | 1.5–2 d | Place Shelly → expand → click Super → super reticle live on canvas; autosave round-trips; old autosave loads |
| **P2 — Sim core + straight shots** | `simLayer`, tick loop, fire mode + banner + Esc steps 1–2, cone/line/burst projectiles, grid collision, range termination, entity hit-flash | 2–3 d | Shelly attack visibly fans 5 pellets that stop on walls; Colt burst; 60 fps |
| **P3 — Lobs, AoE & destruction** | placement/cluster/wave lobs with arc visuals, explosions, `destroyTile` + broken-tile ghost rendering + rubble, undo/reset wiring, paintCell broken-key fix | 2–3 d | Demo: Dynamike super breaks a wall, Piper then hits through the gap; ⌘Z restores wall; reset works |
| **P4 — Polish & long tail** | dash (unit move), self-aoe, area-follow, Rico bounces, star-power modifier toggles, replay button, damage popups, regression pass | ~2 d | Full 28-check regression suite green + new sim checks |

**Total ≈ 8–11 days.** Each phase is independently shippable.

**Defer to the Next.js/`@pixi/react` port** (don't build in the prototype):
formal ECS/component registry, Y.js-synced simulation events (deterministic
replay across clients needs seeded RNG + event log — design the fire event as
`{tokenId, variantIdx, angle, reach, t}` now so it ports), HP/damage
bookkeeping and kill simulation, projectile sprite art, sound, and any
React-side outliner virtualization.

**Risk list:**
- *Data quality* (med): skin→area-effect chain may miss reworked brawlers;
  mitigated by overrides file + graceful no-destroy default.
- *Mode-interaction regressions* (med): fire mode touches the pointertap
  dispatch order; mitigated by inserting exactly one guarded branch and
  keeping all existing branches untouched + Esc-cascade tests.
- *Lob believability* (low): fake arc may read flat at small cell sizes; tune
  height constant; shadow dot carries the read.
- *Outliner clutter* (low): 8-variant brawlers make tall trees;
  collapse-by-default except selected unit.
- *Undo stack growth* (low): grid copies per fire are ~1–3 KB; existing
  100-cap suffices.

---

## 11. Non-breakage contract

The destruction/sim layer must preserve every behavior in the existing manual
regression checklist (28 checks). Mechanisms, by group:

- **Placement / aim / drag / nudge / delete (checks 1–7):** `placing`
  derivation gains only `&& !fireArm` (default null ⇒ identical); fire mode
  *reuses* `aimingId` but only when armed via outliner/F; drag/nudge/delete
  code paths untouched.
- **Projectile-drop + spawn tokens (8–9):** unchanged; both appear as outliner
  leaves.
- **Overlays (10–13):** vision, movement flood-fill, all-reticles toggle, and
  reticle wall-clipping are unchanged — and *improve* automatically when walls
  break, because they already read `charAtTile`/`brokenTiles`. Sim collision
  uses the same 0.08 sampling so visuals agree with reticle clips.
- **Map maker (14–18):** only additive change is the `paintCell` stale
  broken-key fix (strictly better); incremental re-render reused for
  destruction via `refreshCells`.
- **Manual wall-break (19):** now shares the `brokenTiles` ledger with sim
  destruction — toggling a sim-broken tile restores it, consistent.
- **Undo/autosave/map-switch (20–22):** fire-with-destruction adds standard
  snapshots; schema additive; old saves load with defaulted fields; `loadMap`
  untouched (it already clears `brokenTiles`).
- **Custom maps / validation / draft tab / controls (23–26):** untouched; sim
  reads `currentMap.grid` generically; validation reads the raw grid.
- **Esc + banner (27–28):** existing five Esc steps preserved verbatim below
  two new prepended steps; new `fire` banner state renders ahead of existing
  branches, all of which behave identically when `fireArm=null`.

Verification plan: run the 28 checks after P1, P2, P3 (the phases that touch
shared code); add 8 new sim checks (fire each primitive once, destruction
undo, reset, Esc×2, autosave round-trip with broken tiles, old-autosave load).
