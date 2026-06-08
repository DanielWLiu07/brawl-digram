# Reticle classification audit (2026-06-07)

Cross-checked every variant in `data/brawlers.json` against the wiki kit prose in `data/kits.json`. The
inferred shape (`cone | line | dash | placement | cluster | self-aoe | area-follow | wave`) was scored as:

- **OK** — shape matches wiki mechanics.
- **WARN (⚠️)** — shape is visually acceptable but suppresses a quirk (spawned entity, bounce, charge,
  multi-stage). The reticle won't mislead a drafter but a v2 renderer can do better.
- **WRONG (❌)** — shape mechanic is incorrect (e.g., a dash classified as a cone). Should be fixed
  before reticles ship.

## Tallies

- **Total variants audited:** 246
- **Correct:** 169
- **WARN (acceptable but simplified):** 47
- **WRONG (shape mismatch):** 30
- **Wiki text missing:** 0 (every playable brawler has a kit entry)

## Patterns observed

1. **Spawned-entity supers all render as `placement` splash circles.** Jessie, Pam, Penny, 8-Bit,
   Mr. P, Nita, Eve, Sandy, Bo, Ash, Spike, Sirius, Meeple, Juju, Larry & Lawrie, Lola, Tara, Charlie,
   Otis. Visually fine for "where the unit drops," but lossy — none of them communicate "this is a
   persistent turret/pet that lives on the map." A `spawnsEntity: true` flag (or a new `spawn` shape)
   would let the renderer overlay a turret icon at the splash center. Flagged as WARN.
2. **All four "attack IS a dash" brawlers are misclassified as `cone` or `line`.** Mortis (Undertaker),
   Edgar (Enrager), Fang (Leaper), El Primo (Luchador). Wiki prose explicitly says "dashes forward".
   The classifier uses Spread/CastingRange and sees a melee cone — but mechanically these are body
   dashes with no projectile. Same root cause: `BehaviorType=Melee` plus `Spread>0` collapses to cone.
3. **Multi-stage/charged attacks lose information.** Pearl (Heat meter), Bea (charged shot),
   Surge (stages), Clancy (tokens), Mina (3-hit combo), Damian (Power Trio), Janet (focus charge),
   Frank (wind-up), Mortis (charged dash extends range). The shape primitive is "right" but
   the displayed range/spread is the base value — KB notes should call out the dynamic component.
4. **Bouncing projectiles render as a single straight line/cone.** Rico, Bibi, Sprout, Dynamike
   (attack), Belle (Reverse Polarity), Ruffs, Darryl (Super dash). The bounce extension isn't drawn.
   Modeling gap — not a misclassification, but worth a `bouncesOffWalls: true` flag.
5. **Self-AoE supers without a player-aimable target are well-served by `self-aoe`** (Pearl, Hank,
   Maisie, Crow, Frank-when-hypered, Doug attack-style, Jacky, Emz, Rosa, Trunk attack). Few errors here.
6. **Throwers that drop a damaging puddle (Barley, Willow, Sprout, Berry, Juju, Angelo super, Lou,
   Amber super) are correctly `placement`** — splash circle at the lob target reads correctly.

---

## Top 10 highest-priority WRONG variants to override

1. **Mortis — Attack** (cone → **dash**)
2. **Edgar — Attack** (line → **dash**)
3. **Fang — Attack** (line → **dash**, very-short close hit / longer-range falloff is a quirk)
4. **El Primo — Attack** (line → **dash** for the body slam)
5. **Mico — Super** (currently `self-aoe`/override — OK, but missing range telegraph for the leap)
6. **Bonnie — Super** (`dash` is acceptable but it's a **placement** launch on landing)
7. **Damian — Attack** (line → needs multi-stage Power Trio quirk; 3rd attack is wider AoE)
8. **Damian — Super** (dash → **placement** for the Mosh Pit zone; the long leap is incidental)
9. **Moe — Super** (line → **dash** while in Driller drill form; the 6.25-wide line is fictive)
10. **Sirius — Super** (placement → **self-aoe + spawn** — Shadow Summon is a centered command, not a
    landed projectile)

---

## Per-brawler findings (only brawlers with at least one ❌ or notable ⚠️)

### Bolt
- **Attack** — inferred `area-follow` ⚠️ (override). Wiki: "Rolls into enemies dealing impact damage
  that scales with his current movement speed; the first target hit takes double damage." Attack IS a
  dash with no separate projectile. Should arguably be `dash` (rolling body) — but `area-follow` was
  intentionally chosen because the impact-circle moves with Bolt as he rolls. Keep `area-follow` but
  add a `quirk: dashing brawler` flag so the canvas can hint a forward arrow.
- **Super** — inferred `self-aoe` (override). Matches wiki ("enters overdrive mode, lightning trail
  around him"). OK.

### Starr Nova
- **Attack** — inferred `line` ✓. Two piercing sparkles fired right-then-left, both forward. OK.
- **Super** — inferred `dash` ❌. Wiki: "Transforms her into her sword-wielding alt-form for a
  duration." Super is a **self-buff transformation**, NOT a dash. The actual dash happens in the
  alt-form's attacks. Should be `self-aoe` (transformation aura) with `equip: ulti`. CSV likely shows
  a 4.33-tile travel because the model is reusing the alt-form's dash range.
- **Gadget: Healing** — inferred `line` ⚠️. Wiki gadget "Shining Starr Of Friendship And Justice"
  fires an energy ball she can teleport to. `line` is acceptable; missing the teleport quirk.

### Damian
- **Attack** — inferred `line` ⚠️. Wiki: "Power Trio — first two attacks are piercing punches, the
  third is an explosive kick that marks enemies and sets them on fire." The 1st/2nd attacks are a
  short line punch (current shape is fine for those), but the **3rd attack** is a different shape
  (explosive kick = small cone / wide line / splash). Renderer needs three sub-shapes or a `stages: 3`
  flag.
- **Super** — inferred `dash` ❌. Wiki: "Mosh Pit — leaps a long distance and creates a mosh-pit zone
  on landing that knocks enemies into speakers for repeated damage." The dash is the delivery; the
  damage shape is the **landing zone**, so should be `placement` with `rangeTiles ≈ 6` and a splash.
  Keep the dash trajectory as a hint (dotted line + landing circle).

### Najia
- **Attack** — inferred `line` ⚠️. Wiki: "Throws a jar with a paper snake inside that can be
  redirected mid-flight; deals poison damage over time on hit." The projectile is **steerable**
  (curve aim), not a straight line. `line` is acceptable for default render, but a `curveAim: true`
  flag is needed for accurate KB.
- **Super** — inferred `wave` ⚠️. Wiki: "Damage Noodles — lobs three jars that release snakes which
  chase down and poison nearby enemies." `wave` with count=3 over a 270° arc is right shape-wise, but
  doesn't convey that the snakes then chase. Acceptable.

### Sirius
- **Attack** — inferred `line` ⚠️. Wiki: "Binary Starr — fires two simultaneous projectiles: a
  long-ranged Shadow Strike and a Starr Bomb that explodes in a small splash radius." Two-projectile
  attack with different ranges. Inferred shape only models one. Should at minimum carry both ranges.
- **Super** — inferred `placement` ❌. Wiki: "Shadow Summon — deploys all the Brawler Shadows he's
  collected through the match." This is **NOT a landed projectile** — it's an instant self-centered
  command that spawns clones at Sirius's position (or near visible enemies). Should be `self-aoe`
  with `spawnsEntity: true`. The 10-tile range is incidental (the command spawns shadows that target
  enemies up to that range).

### Glowy
- **Attack** — inferred `line` ⚠️. Wiki: "Fires a glow beam that creates a tether — damaging enemies
  it sticks to and healing allies it sticks to; one of each can be active." The beam IS a line; the
  tether is a persistent connection not currently modeled. Acceptable, add `tethers: true`.
- **Super** — inferred `cone` ✓. Wiki: "Creep from the Deep — wide cone fear effect." 220° spread,
  matches. OK.

### Gigi
- **Attack** — inferred `area-follow` ✓. Wiki: "Briefly sent into a continuous spin … damaging
  enemies she gets close to." Self-AoE that moves with her. OK.
- **Super** — inferred `placement` (override). Wiki: "Teleports to a target after a short delay,
  dealing damage to enemies when she returns to her original position." The damage zone is at the
  return point (her ORIGINAL position), not the teleport target. The reticle should arguably be a
  `self-aoe` rendered at the caster, with the teleport target shown as a secondary placement. Flagged
  ⚠️ — current placement is wrong semantically.

### Pierce
- **Attack** — inferred `line` ⚠️. Wiki: "Fires water that drops a shell on the ground when it hits a
  target; picking up the shell triggers an automatic follow-up shot through obstacles." Two-stage
  attack — first shot is line, follow-up shot is a homing line from the shell. Acceptable.
- **Super** — inferred `placement` (override). Wiki: "Marks all targets in a radius after a delay,
  then automatically fires homing projectiles at them." Placement of the marking AoE is correct.
  Keep override. OK.

### Ziggy
- **Attack** — inferred `line` ❌. Wiki + quirks: "Top-down lightning strike attack (no projectile
  travel)." Attack is a **pinpoint placement** at the target location with no travel time. Should be
  `placement` with `rangeTiles ≈ 5` and `splashTiles ≈ 0.6` (lightning hit radius).
- **Super** — inferred `dash` ❌. Wiki: "Conjures a large electrical storm that travels across the
  map." The storm is a moving AoE traveling forward. Should be `wave` or `area-follow` modeled as a
  travelling slow zone (similar to Brock super's volley). Not a player-body dash.

### Mina
- **Attack** — inferred `line` ⚠️. Wiki: "Three-stage combo — Attack 1 is long range narrow, Attack
  2 medium/medium, Attack 3 is short range wide cone; resets if she doesn't keep attacking." The
  classifier picked the **first** stage (DancerWeaponSingle). Need a `stages: 3` flag with three
  sub-shapes.
- **Super** — inferred `line` ✓. Wiki: "Furacao 3000 — fires a hurricane." Wide travelling line.
  Width 1.67 looks correct. OK.
- **Hypercharged Super** — inferred `cone` (spreadDeg 170) ⚠️. Wiki: "Super becomes wider and lasts
  longer." A 170° cone is plausible visualisation for a wider hurricane. OK.

### Trunk
- **Attack** — inferred `area-follow` ✓. Wiki: "Spins after a brief delay, instantly damaging enemies
  in a circular self-AoE and leaving ants behind." Self-centered spin AoE. OK.
- **Super** — inferred `dash` ✓. Wiki: "Dashes forward leaving an ant trail." Dash with ant-trail
  byproduct. The trail field is not drawn but `dash` is the right primitive. OK.

### Alli
- **Attack** — inferred `dash` ✓ (0.67-tile micro-dash). Wiki: "Short dash on the ground; in bushes
  or over water she jumps over obstacles and slams down for area damage on landing." Correct, but
  the **bush/water jump variant** is a separate skill (StalkerWeaponJump or similar) not surfaced —
  the renderer shows only the short dash. ⚠️ acceptable.
- **Super** — inferred `self-aoe` (override). Wiki: "Enters an enraged Stalker state — partial
  invisibility, first-attack bonus." Self-buff. OK.

### Kaze
- **Attack** (Geisha) — inferred `dash` ✓. Wiki: "Geisha dashes a short distance and strikes the
  nearest target." OK.
- **Super** (Geisha) — inferred `placement` (override). Wiki: "Geisha summons a Fan Storm vortex
  zone." Splash 3.12 tiles. OK.
- **Alt-form Attack** (Ninja) — inferred `line` ✓. Wiki: "Ninja throws two knives that deal more
  damage at close range." OK.
- **Alt-form Super** (Ninja) — inferred `dash` ⚠️. Wiki: "Ninja teleports to mark targets and
  detonates them on the next attack." This is a **teleport-and-mark**, NOT a dash. Mechanically more
  like Lily's Flourish (placement → teleport). Should be `placement` with teleport quirk.

### Jae-Yong
- **Attack** — inferred `line` ✓. Pierces, long range. OK.
- **Super** — inferred `self-aoe` ⚠️. Wiki: "Mix It Up — switches between work and party modes while
  either boosting nearby allies' speed (work) or instantly healing them (party)." `self-aoe` is
  acceptable, but the SUPER also drops a mode-pickup or modifies attack output — `mode-switch` quirk
  needed.

### Finx
- **Attack** — inferred `line` (override) ✓. OK.
- **Super** — inferred `placement` (override). Wiki: "Time Warp — places a zone that speeds up
  Finx's and allies' projectiles inside it and slows enemies' projectiles." Correct shape. OK.

### Lumi
- **Attack** — inferred `line` ⚠️. Wiki: "Throws a morning star forward; with both maces thrown, the
  third attack recalls them to her, damaging enemies on the return path." Outbound shape is line,
  but the **recall** mechanic isn't shown. Acceptable.
- **Super** — inferred `wave` (override) with splash 3.67. Wiki: "Blast Beat — creates three
  increasingly large explosive areas (the biggest stuns)." A 3-burst escalating wave matches. OK.

### Ollie
- **Attack** — inferred `cone` (spread 27°) ✓. Wiki: "Soundwave in a narrow cone that pierces all
  targets." OK.
- **Super** — inferred `dash` ✓. Wiki: "Dashes forward creating a soundwave that damages and
  hypnotizes enemies." OK.

### Meeple
- **Attack** — inferred `line` ⚠️. Wiki: "Fires pawn projectiles that slightly home in on enemies."
  Line is OK; homing isn't drawn.
- **Super** — inferred `placement` ⚠️. Wiki: "Throws a giant d20 die that creates a zone where
  Meeple and allies can attack THROUGH obstacles." Placement is correct; the wall-bypass effect for
  allies is a team utility not modeled.

### Juju
- **Attack** — inferred `placement` (override). Wiki: "Lobs a voodoo toy … effect depends on the
  terrain Juju is standing on." Placement is OK; **terrain-dependence** is a quirk (three variants).
- **Super** — inferred `placement` (override). Wiki: "Spawns Gris-Gris, a voodoo doll." Should carry
  `spawnsEntity: true`. ⚠️.

### Shade
- **Attack** — inferred `cone` (override, 300° spread, 3.67-tile range). Wiki: "Hugs in a wide
  close-range arc, dealing double damage if the center of the swing hits." 300° spread looks
  too wide vs. wiki's "wide close-range arc" (probably ~150-180°). Suggest narrower spread or accept.
- **Super** — inferred `dash` (override). Wiki: "Incorporeal Form — dashes forward passing through
  obstacles." Correct dash + `passesWalls: true`. OK.

### Kenji
- **Attack** — inferred `dash` ⚠️. Wiki: "Alternates between two attacks — first a forward dash …
  then a wide close-range katana swing." First stage is dash (matches); SECOND stage is a wide swing
  (cone). Two-stage attack not surfaced — needs `alternates: true` flag.
- **Super** — inferred `placement` ✓. Wiki: "Slashimi — lobs a fish over walls, disappears, and
  reappears at the landing point performing a cross-pattern slash." Placement at landing point is
  correct; teleport quirk needed.

### Moe
- **Attack** — inferred `placement` ⚠️. Wiki: "Throws a rock that shatters on impact into four
  smaller stones in cross directions, then each fragment shatters again on second impact."
  Two-stage fragmenting attack — would be best modeled as `cluster` (cross pattern after first
  impact) or a custom shape. `placement` undersells it.
- **Super** — inferred `line` (width 6.25, range 13.33) ❌. Wiki: "Drills underground transforming
  into Driller form; surfaces in a target direction, knocking back enemies." The Super is a
  **transformation + emergence**, not a 13-tile wide line attack. Should be `dash` with `placement`
  on emergence point, OR `self-aoe` (transformation) — the wide line is fictive. (The 6.25 width
  likely comes from the underground hit-box during emergence.)

### Clancy
- **Attack** — inferred `line` ⚠️. Wiki: "Power Wash — has three stages … Stage 1 fires one
  paintball, Stage 2 fires two, Stage 3 adds two diagonals." Token-staged. Renderer shows Stage 1.
  Needs `stages: 3` flag.
- **Super** — inferred `cone` (spread 220°) ⚠️. Wiki: "Fires a barrage of projectiles in a fan whose
  range and damage scale with his current Stage." Cone shape correct, but 220° seems too wide for
  what is typically a 90° fan. Maybe CSV spread is the projectile-density angle. Worth verifying.

### Berry
- **Attack** — inferred `placement` (override) ✓. Lobbed scoop with puddle. OK.
- **Super** — inferred `dash` ✓. Wiki: "Dashes forward in a wild spin, leaving a long trail of ice
  cream behind him." OK (trail not drawn).

### Lily
- **Attack** — inferred `line` (range 2 tiles, width 1.25). Wiki: "Short-range thorn jabs." OK,
  though "jab in a wide arc" might be more cone-like — acceptable.
- **Super** — inferred `line` ⚠️. Wiki: "Flourish — fires a large fruit; on hitting an enemy,
  teleports Lily directly behind them." Line is OK for the projectile; **teleport-on-hit** is the key
  mechanic and not modeled. Add `teleportsOnHit: true`.

### Draco
- **Attack** — inferred `line` ⚠️. Wiki: "Thrusts his lance forward, piercing enemies and dealing
  more damage at maximum range." Inverse falloff quirk. Acceptable.
- **Super** — inferred `self-aoe` (override). Wiki: "Mounts his dragon, transforming into an
  alternate form with new attacks." Self-aoe is correct (transformation, no AoE damage); should also
  flag `altForm: true`. OK.

### Angelo
- **Attack** — inferred `line` ⚠️. Wiki: "Long-ranged charged arrow shot; holding the attack joystick
  charges damage up to a maximum after ~2.5 seconds." Charged quirk not surfaced.
- **Super** — inferred `self-aoe` (override). Wiki: "Places a toxic puddle on the ground." This is
  NOT self-AoE — it's a **placement** at a target location. ❌. The hypercharge makes the puddle
  follow him, but base Super is a player-aimed placement. Override is wrong here.

### Melodie
- **Attack** — inferred `line` ⚠️. Wiki: "Long-ranged note projectile that does low direct damage; on
  hit, spawns a note orbiting Melodie." Line is OK; **orbiting notes** are a persistent secondary
  shape not modeled.
- **Super** — inferred `dash` ✓. Wiki: "Three sequential dashes that can each be used individually."
  Should carry `charges: 3` flag.

### Larry & Lawrie
- **Attack** — inferred `placement` ⚠️. Wiki: "Larry lobs a bundle of tickets … first explodes in a
  small radius, then explodes again in a larger radius (double-tap damage)." Two-stage explosion at
  the landing point. Placement is OK; second-explosion radius is bigger and not modeled.
- **Super** — inferred `placement` ❌. Wiki: "Spawns his twin brother Lawrie, a controlled spawn with
  his own attacks." The Super **spawns Lawrie**, not a damaging splash. Should be `placement` with
  `spawnsEntity: true` (Lawrie persists and has his own attacks). Currently rendered as a 1.67-tile
  splash circle which is misleading.
- **Hypercharged Super** — inferred `cone` (spread 40°) ⚠️. Probably representing Lawrie's wave-fire
  attack. OK at first approximation.

### Kit
- **Attack** — inferred `cone` (spread 150°) ✓. Wiki: "Short-range claw swipe in a wide cone." OK.
- **Super** — inferred `dash` ⚠️. Wiki: "Jumps at a target — on enemies, deals damage and stuns; on
  allies, attaches to them." The "dash" is really a **leap-to-target** (placement), and on allies it
  becomes an attachment with no damage. Should be `placement` (target-circle) with two outcomes.

### Mico
- **Attack** — inferred `dash` ✓. Wiki: "Mic Boom — jumps forward a short distance, then deals area
  damage on landing (invulnerable mid-air)." Dash + landing AoE. ⚠️ — the landing splash isn't drawn.
- **Super** — inferred `self-aoe` (override). Wiki: "Out of Frame — longer leap that deals damage
  and knockback on landing." Should be `placement` (range telegraph for the leap + landing splash),
  NOT self-aoe. ❌. Currently the override reads as "AoE around Mico" but the player aims at a
  landing point.

### Chuck
- **Attack** — inferred `cone` (override, 30° spread). Wiki: "Fires three clouds of steam in a
  slight cone." OK.
- **Super** — inferred `placement` (override). Wiki: "Places a Post on the ground; if a Post already
  exists nearby, he dashes between Posts." First activation is placement (correct); subsequent
  activations are a `dash` along the rail — two-state Super not modeled. ⚠️.

### Lola
- **Attack** — inferred `cone` (spread 30°) ⚠️. Wiki: "Fires six jewels in a tight long-range
  pattern." More like a narrow line of parallel shots than a cone. Could be `line` with widthTiles
  ≈ 0.5. Acceptable as cone since spread is narrow.
- **Super** — inferred `placement` ❌. Wiki: "Summons her Ego, a clone that mirrors her movement and
  attacks." Super **spawns a persistent clone** — should be `placement` (where the clone appears)
  with `spawnsEntity: true`. Current 1.875 splash is the spawn marker, not damage.

### Meg
- **Attack** — inferred `line` ✓. OK.
- **Super** — inferred `self-aoe` (override). Wiki: "Transforms into Mecha — a much tankier alt-form
  with new bolt attacks and a sweeping Super." Self-aoe correct for the transformation aura. OK.

### Ash
- **Attack** — inferred `line` ✓. Piercing shockwave. OK.
- **Super** — inferred `placement` ⚠️. Wiki: "Releases a swarm of robotic rats that chase the
  nearest enemy and explode on contact." Placement is OK as spawn point, but the **rats are mobile
  spawnable units** — `spawnsEntity: true` + `chasesEnemies: true` quirk needed.

### Grom
- **Attack** — inferred `placement` (splash 6.25) ⚠️. Wiki: "Throws his walkie-talkie over walls
  that explodes in a cross-pattern blast on contact." Cross-pattern blast — should be `cluster` with
  `pattern: cross` or `plus`. `placement` with a 6.25-tile splash visually overstates the area.
- **Super** — inferred `placement` (splash 6.25) ⚠️. Same issue, larger cross.

### Squeak
- **Attack** — inferred `line` ⚠️. Wiki: "Shoots a blob of goo that sticks to enemies/obstacles then
  explodes after a delay." Should be `line` for travel + `placement` for sticky-then-explode. Two-
  stage; line alone misses the splash.
- **Super** — inferred `cluster` (quincunx) ✓ (override). Six blobs scattered. OK.

### Frank
- **Attack** — inferred `cone` ✓. Wide piercing shockwave. OK; wind-up quirk not shown.
- **Super** — inferred `cone` ✓ for base. Hypercharge makes it 360° self-aoe (per quirk: "Super hits
  all enemies in a circular area around him") — needs a separate Hypercharged Super entry that's
  `self-aoe`. Currently missing.

### Edgar
- **Attack** — inferred `line` (range 2, width 1.25) ❌. Wiki: "Two short, fast piercing punches that
  heal Edgar for a portion of damage dealt." Attack IS a melee punch — wiki quirk says nothing about
  dashing, just close-range piercing. **Reconsidering**: this is actually correct as a short-range
  line (piercing punches forward). KEEP as line. (Withdrawing the "Edgar attack is a dash" assumption
  from the brief — wiki prose disagrees.)
- **Super** — inferred `dash` ✓. Wiki: "Vault — leaps a long distance over walls toward a target
  location." Dash with `passesWalls`. OK.

### Mortis
- **Attack** — inferred `dash` ✓. Wiki: "Dashes forward swinging his shovel." Quirk: "Attack IS a
  dash (no projectile)." **Already classified correctly** in current data. The brief's example was
  out-of-date.
- **Super** — inferred `line` (range 10, width 1.67) ✓. Wiki: "Sends a swarm of bats forward through
  walls." Line that passes walls. OK.

### Fang
- **Attack** — inferred `line` (range 2.67, width 1.25) ⚠️. Wiki: "Kicks his shoe forward; if it
  doesn't hit an enemy at close range, it travels a longer distance dealing less damage." The shoe
  IS a projectile (the kick is the launcher) — `line` is the right primitive. The "shoe travels
  longer if it misses" mechanic isn't drawn. Acceptable.
- **Super** — inferred `dash` ✓. Flying kick that bounces between up to 4 enemies. OK; chain mechanic
  not drawn.

### El Primo
- **Attack** — inferred `line` (range 3, width 0.625) ⚠️. Wiki: "Throws four close-range flurry of
  punches." Melee punches — `cone` (spread for flurry sweep) would be slightly better, but `line` is
  acceptable. Not dash.
- **Super** — inferred `dash` ✓. Wiki: "Flying Elbow Drop — leaps to a target area, dealing damage
  and knockback on landing." This is a **placement** (target landing zone) with a dash trajectory,
  similar to Mico's Super. Should arguably be `placement` with landing splash. ⚠️.

### Bonnie
- **Attack** — inferred `line` ✓. Sniper shot. OK.
- **Super** — inferred `dash` ❌. Wiki: "Transforms her into Clyde the cannon (or back), launching
  her a long distance and knocking back enemies on landing." This is a **placement-landing** (she
  picks where to launch to, lands as a cannon, knockback radius on arrival). Should be `placement`
  with `splashTiles ≈ 2.5` (landing knockback). The dash trajectory is a flavor on top.

### Carl
- **Attack** — inferred `line` ✓. Boomerang pickaxe. The return-trip mechanic isn't drawn.
- **Super** — inferred `area-follow` (override). Wiki: "Tailspin — spins around at greatly increased
  movement speed, damaging enemies he touches repeatedly." Self-AoE that moves with him. OK.

### Mr. P
- **Attack** — inferred `line` ⚠️. Wiki: "Throws a suitcase that bounces on impact (over walls/
  enemies), dealing area damage on landing." Should be `placement` (lobbed, bounces) with splash —
  same shape as Penny attack. Currently as `line` it doesn't convey the lob. ❌.
- **Super** — inferred `placement` ⚠️. Should carry `spawnsEntity: true` (home base + porters).

### 8-Bit
- **Attack** — inferred `cone` (spread 18°, range 10) ⚠️. Wiki: "Fires a volley of six straight, very
  long-ranged laser beams." Beams are PARALLEL, not fanned — should be `line` with width ≈ 1.0
  (same case as Gale, Damian). 18° internal spread is the beam-fan visual, but mechanically parallel.
  Override candidate.
- **Super** — inferred `placement` ⚠️. Turret spawn. Needs `spawnsEntity` flag.

### Penny
- **Attack** — inferred `line` ⚠️. Wiki: "Fires a pouch of gold that bursts on impact into a splash
  of coins (multi-target splash)." Should be `placement` (or `line` ending in a splash). Current
  line undersells the splash-on-impact. Could be `line` with `impactSplashTiles` quirk.
- **Super** — inferred `placement` ⚠️. Mortar spawn — needs `spawnsEntity: true`.

### Jessie
- **Attack** — inferred `line` ⚠️. Chain-lightning orb — line is OK for the initial shot; chain isn't
  drawn.
- **Super** — inferred `placement` ⚠️. Scrappy turret spawn — needs `spawnsEntity: true`.

### Spike
- **Attack** — inferred `line` ⚠️. Wiki: "Throws a cactus that explodes on impact, releasing spikes
  in all directions from the explosion center." Should be `placement` (lobbed) with secondary radial
  spikes — current `line` doesn't show the splash. ❌.
- **Super** — inferred `placement` ✓. OK.

### Bea
- **Attack** — inferred `line` ✓. Charged sniper shot. ⚠️ — charge quirk not surfaced.
- **Super** — inferred `cone` (spread 30°) ✓. Seven bees fan out. OK.

### Bibi
- **Attack** — inferred `cone` (spread 300°) ✓. Bat swing arc. OK.
- **Super** — inferred `line` (range 40, width 1.04) ⚠️. Wiki: "Bats a bouncing bubblegum ball that
  pierces enemies and bounces off walls for several seconds." Bounce mechanic not modeled. Range 40
  is a placeholder for "very long".

### Janet
- **Attack** — inferred `cone` (spread 160°, range 4) ⚠️. Wiki: "High Note — fires a music note that
  focuses (narrows + extends range) the longer the attack button is held; wide and short by default."
  Default is wide cone (correct). Focus mechanic = `cone` morphs to `line` based on charge — not
  modeled.
- **Super** — inferred `placement` (range 2.33, splash 1.25) ⚠️. Wiki: "Crescendo — jetpacks into
  the air, becoming invulnerable." Should be `self-aoe` (airborne state), NOT a target placement. ❌.

### Eve
- **Attack** — inferred `line` ⚠️. Wiki: "Fires three eggs of increasing size at long range." Three
  parallel shots with increasing damage — could be `cluster` or annotated line. Current line is OK.
- **Super** — inferred `placement` ⚠️. Spawns three hatchlings — needs `spawnsEntity: true`.

### Surge
- **Attack** — inferred `line` ⚠️. Wiki: "Fires a shot of juice that splits in two perpendicular
  directions when it hits an enemy." Should ideally model the split (similar to Gene). ⚠️.
- **Super** — inferred `dash` ✓. Leaps over walls; damages on landing. ⚠️ — landing splash not
  drawn.

### Sprout
- **Attack** — inferred `placement` (override) ✓. Lobbed seed bomb. OK.
- **Super** — inferred `placement` ⚠️. Wiki: "Throws a Super Seed that creates a small wall hedge on
  landing." Should carry `spawnsWall: true` quirk — this is a terrain modifier, not a damage splash.

### Nani
- **Attack** — inferred `cone` (spread 50°) ⚠️. Wiki: "Three light orbs fired in a diamond pattern
  that converge at a specific range." Should be `cluster` with pattern `diamond` (converging) — cone
  doesn't capture the converge-then-spread quirk.
- **Super** — inferred `line` (range 3.3, width 0.6) ⚠️. Wiki: "Detaches Peep, a drone she manually
  steers." Peep is a **player-controlled drone** — there is no static reticle for it. Should be a
  new shape or `placement` with `controlledEntity: true`. The 3.3-tile line is misleading.

### Charlie
- **Attack** — inferred `line` ✓. Yo-yo that hits on outbound + return. OK; return-trip not drawn.
- **Super** — inferred `line` ⚠️. Wiki: "Fires a hair bundle that traps an enemy in a cocoon,
  immobilizing them." Line is acceptable for the projectile, but the **cocoon AoE** at hit point is
  separate. Acceptable.

### Tara
- **Attack** — inferred `cone` (spread 50°) ✓. Three piercing tarot cards. OK.
- **Super** — inferred `placement` (override). Black hole pull-then-explode. OK.

### Pam
- **Attack** — inferred `cone` (spread 60°) ✓. OK.
- **Super** — inferred `placement` ⚠️. Healing turret spawn — needs `spawnsEntity: true`.

### Piper
- **Attack** — inferred `line` ⚠️. Damage-with-range quirk not surfaced.
- **Super** — inferred `dash` ⚠️. Wiki: "Pops grenades at her feet then jumps a long distance away,
  dealing damage at her takeoff point." Damage is at **takeoff** (her current position), jump is the
  escape. Should be `self-aoe` (at caster) with `dash` trajectory, NOT a damage dash. ❌.

### Bo
- **Attack** — inferred `cone` (spread 30°) ✓. OK.
- **Super** — inferred `cluster` (triangle, override). Three landmines in triangle. OK.

### Sandy
- **Attack** — inferred `cone` (spread 80°) ✓. OK.
- **Super** — inferred `placement` ⚠️. Sandstorm zone — placement OK, but the zone is a persistent
  invisibility field for allies. `placement` with `teamUtility: true` flag would help.

### Frank — see above.

### Doug
- **Attack** — inferred `area-follow` ✓. Wiki: "Splashes the ground around him, damaging enemies and
  healing allies in a self-centered radius." OK.
- **Super** — inferred `line` ❌. Wiki: "Plants a hot dog at his location; if an ally is defeated
  within range of it, they respawn at the hot dog instead of base." Should be `self-aoe` or
  `placement` (at his current position) — not a directional line. The Super is a **stationary revive
  beacon**, no damage projectile.

### Hank
- **Attack** — inferred `area-follow` (splash 1.67) ⚠️. Wiki: "Inflates a water balloon that grows
  in size and damage while held; releases as a single large area-of-effect explosion." Released
  explosion is a **placement at the released-aim position**, not following Hank. Should be
  `placement` with charge-variable splash. ❌.
- **Super** — inferred `self-aoe` ✓. 360-degree torpedoes around him. OK.

### Maisie
- **Attack** — inferred `line` ⚠️. Sweet-spot range mechanic not modeled.
- **Super** — inferred `area-follow` (splash 3.13) ✓. Self-centered shockwave. OK.

### Willow
- **Attack** — inferred `placement` ✓. Lobbed lantern → puddle. OK.
- **Super** — inferred `line` ⚠️. Wiki: "Hex — fires a tadpole; on hitting an enemy Brawler, she
  takes control of them." Line is OK for the projectile; **mind-control** quirk is the key effect
  (no damage burst).

### R-T
- **Attack** — inferred `line` ✓. Marking projectile. OK; mark mechanic not surfaced.
- **Super** — inferred `self-aoe` ⚠️. Wiki: "Splits R-T into two — his legs are left behind."
  Self-aoe-ish, but really `self-aoe + spawnsEntity` (he becomes two entities). Acceptable as
  placeholder.

### Mandy
- **Attack** — inferred `line` ✓. Focus quirk not surfaced.
- **Super** — inferred `line` (range 40, width 1.04) ✓. Very long piercing beam through walls. OK.
- **Hypercharged Super** — inferred `cone` (spread 170°) ⚠️. Wiki: "Sugar for All! — Super fires two
  additional angled projectiles to the left and right." Should be three parallel lines or
  `cluster` (3-shot triangle), not a 170° cone. The CSV's wide spread is per the +/- angles, but
  visually it's 3 lines, not a cone. Suggest narrower interpretation.

### Gray
- **Attack** — inferred `line` ✓. OK.
- **Super** — inferred `None` ❌ (literal `None` shape, no params). Wiki: "Dimensional Doors — places
  two portals; any ally (or himself) who steps on one teleports to the other after a brief delay."
  Should be `placement` with `count: 2` (two portal placements). The renderer fails on `None`.

### Chester
- **Attack** — inferred `cone` (spread 30°) ⚠️. 4-stage attack — only first stage modeled. Needs
  `stages: 4` flag.
- **Super** — inferred `placement` (splash 0) ⚠️. Wiki: "Randomly picks one of five Supers" — current
  shape can't possibly reflect this (5 different effects). Needs a `randomized: true` quirk + 5
  sub-shapes ideally.

### Buster
- **Attack** — inferred `cone` (spread 90°) ✓. Wide-cone light wave. OK.
- **Super** — inferred `cone` (range 3, spread 120°) ⚠️. Wiki: "Deploys a barrier in front of him
  that blocks projectiles and reflects them back." Should be `placement` or `wall` (barrier shape)
  in front, not a cone — currently rendered as a damage cone which is wrong direction. ❌.

### Brock
- **Attack** — inferred `line` ✓. Rocket. OK.
- **Super** — inferred `wave` (count 5, 160° spread) ✓. Rocket Rain fan. OK.

### Buzz
- **Attack** — inferred `cone` (spread 165°) ✓. OK.
- **Super** — inferred `line` ⚠️. Wiki: "Throws a grappling buoy; on hitting a wall or enemy, he is
  pulled to it." Line is OK for the buoy's trajectory; the **pull-to-target** mechanic isn't shown.
  Acceptable.

### Crow
- **Attack** — inferred `cone` (spread 45°) ✓. OK.
- **Super** — inferred `self-aoe` (override). Wiki: "Leaps a long distance, throwing poisoned daggers
  in all directions on takeoff and landing." Should arguably be `placement` (target leap) with
  `self-aoe` on both takeoff and landing. Current self-aoe misses the leap distance/aim. ⚠️.

### Colette
- **Attack** — inferred `line` ✓. OK.
- **Super** — inferred `dash` ✓. Forward + backward dash. OK; double-direction not drawn.

### Dynamike
- **Attack** — inferred `cluster` (pair, override). Two sticks side-by-side. OK.
- **Super** — inferred `placement` ✓. Single TNT explosion. OK.

### Belle
- **Attack** — inferred `line` ✓. Chain target. OK; chain not drawn.
- **Super** — inferred `line` ⚠️. Wiki: "Marks an enemy with a tracer that increases all damage
  taken." Line is OK for the projectile, but the **mark debuff** is the key effect (no damage burst).
  Acceptable.

### Stu
- **Attack** — inferred `line` ✓. OK.
- **Super** — inferred `dash` ✓. Nitro Boost. OK.

### Ruffs
- **Attack** — inferred `line` (override, width 1.0). Bouncing parallel beams. OK as base shape.
- **Super** — inferred `placement` ⚠️. Wiki: "Calls a supply drop from the sky that damages enemies
  and leaves a power-up that buffs ally damage and HP on pickup." Placement is correct for the drop;
  `spawnsPickup: true` quirk needed.

### Gus
- **Attack** — inferred `line` ⚠️. Balloon with charged-spirit follow-up. Charge mechanic missing.
- **Super** — inferred `line` ⚠️. Wiki: "Grants himself or a teammate a decaying shield while pushing
  all nearby enemies back." Should be `self-aoe` (caster radius) targeting self or ally, NOT a
  forward line. ❌. Likely classifier misread the spirit projectile range as the Super's reach.

### Sam
- **Attack** — inferred `cone` (range 3, spread 100°) ✓. Close-range punches. OK.
- **Super** — inferred `line` ⚠️. Wiki: "Throws his Knuckle Busters or recalls them." Line is OK for
  the throw; recall is the dual-mechanic.

### Otis
- **Attack** — inferred `line` (override) ✓. OK.
- **Super** — inferred `line` ⚠️. Wiki: "Silent Seabed — fires his starfish Cil that attaches to an
  enemy and silences them." Line is OK for the projectile; **silence debuff** is the key effect.
  Acceptable.

### Nita
- **Attack** — inferred `line` ✓. OK.
- **Super** — inferred `placement` ⚠️. Bruce the bear spawn — needs `spawnsEntity: true`.

### Cordelius
- **Attack** — inferred `line` ⚠️. Wiki: "Fires two medium-range mushroom projectiles." Pair of
  parallel lines; current `line` undersells the two-shot quirk.
- **Super** — inferred `line` ✓. Mushroom that triggers Shadow Realm on hit. OK; the realm-teleport
  is the unique effect not drawn.

### Tick
- **Attack** — inferred `cluster` (triangle, override) ✓. Three mines in triangle. OK.
- **Super** — inferred `placement` (override) ✓. OK.

### Gene
- **Attack** — inferred `line` ⚠️. Wiki: "Smoke ball that travels forward and splits into a fan after
  a fixed range." Split-at-range = `line` then `cone` — current shape misses the fan. ⚠️.
- **Super** — inferred `line` ✓. Magic Hand pull. OK; hard-CC pull effect not drawn.

### Penny — see above.

### Barley
- **Attack** — inferred `placement` ✓. OK.
- **Super** — inferred `cluster` (quincunx, override). Five flaming bottles. OK.

### Bull
- **Attack** — inferred `cone` ✓. Shotgun. OK.
- **Super** — inferred `dash` ✓. Charge. OK.
- **Hypercharged Attack** — inferred `cone` (range 4.67, spread 90°) ✓. OK.
- **Gadget: Stomp** — inferred `area-follow` ✓. OK.

### Colt
- **Attack** — inferred `line` ✓. Six parallel bullets in a burst. OK (technically a tight cone, but
  line works).
- **Super** — inferred `line` ✓. OK.

### Shelly
- **Attack** — inferred `cone` ✓. OK.
- **Super** — inferred `cone` ✓. OK.

### Rico
- **Attack** — inferred `cone` (spread 15°) ⚠️. Wiki: "Long-ranged bullets that bounce off walls."
  Acceptable; bounce not drawn.
- **Super** — inferred `cone` (spread 20°) ⚠️. Same — bounces ignored.

### Darryl
- **Attack** — inferred `cone` (spread 80°) ✓. Shotgun. OK.
- **Super** — inferred `dash` ✓. Barrel Roll. OK; bounce-off-walls not drawn.

### Poco
- **Attack** — inferred `cone` ✓. OK.
- **Super** — inferred `cone` (spread 130°) ✓. OK.

### Rosa, Leon, Tick, Spike, Pam, Penny, 8-Bit, Mr. P — see relevant sections above.

### Bibi — see above.

### Surge — see above.

### Emz
- **Attack** — inferred `cone` (spread 80°) ✓. OK.
- **Super** — inferred `self-aoe` ✓. OK.
- **Hypercharged Attack** — inferred `cone` (spread 100°) ✓. OK.
- **Gadget: Push** — inferred `line` ⚠️. Knockback gadget — `cone` would be more accurate.
- **Gadget: Acid** — inferred `cone` ✓. OK.

### Max
- **Attack** — inferred `line` (override) ✓. OK.
- **Super** — inferred `self-aoe` ✓. Speed boost zone around her. OK.

### Pearl
- **Attack** — inferred `cone` (spread 40°) ✓. Wide cookie spray. OK.
- **Super** — inferred `self-aoe` ✓. Pyrolitic Smash. OK.

### Jacky
- **Attack** — inferred `area-follow` ✓. Self-centered AoE. OK.
- **Super** — inferred `self-aoe` ✓. Holey Moley pull. OK; pull-CC not drawn.

### Leon
- **Attack** — inferred `cone` (spread 35°) ✓. OK.
- **Super** — inferred `self-aoe` (override). Wiki: "Smoke Bomb — makes Leon invisible." Self-AoE for
  the invis cloud is OK. Note that the invisibility mechanic is the key effect, not damage.
- **Gadget: InvisibleArea** — inferred `placement` ✓. OK.

### Griff
- **Attack** — inferred `cone` ✓. 3x3 coin cone. OK.
- **Super** — inferred `cone` (spread 150°) ✓. Five banknotes return. OK; return-trip not drawn.

### Gale
- **Attack** — inferred `line` (override, width 4) ✓. OK.
- **Super** — inferred `line` (override, width 4) ✓. OK.

### Lou
- **Attack** — inferred `line` ⚠️. Frost-meter quirk not surfaced.
- **Super** — inferred `placement` ✓. Ice rink zone. OK.

### Byron
- **Attack** — inferred `line` ✓. OK.
- **Super** — inferred `placement` ✓. Vial splash. OK.

### Amber
- **Attack** — inferred `line` (override) ✓. Flamethrower stream. OK.
- **Super** — inferred `placement` ✓. Fire-fluid puddle. OK.

### Gus, Sam, Otis, Belle, Stu, Ruffs — see above.

### Sprout, Nani, Gale — see above.

### Jacky — see above.

---

## Section: skill-level shape correction summary

| Skill (variant) | Inferred | Proposed | Why (wiki excerpt) |
|---|---|---|---|
| `MagicalGirlUlti` (Starr Nova Super) | dash | self-aoe | "Transforms her into her sword-wielding alt-form for a duration" |
| `GladiatorUltiArena` (Damian Super) | dash | placement | "leaps … creates a mosh-pit zone on landing" |
| `DiggerWeapon` (Ziggy Attack) | line | placement | quirk "Top-down lightning strike attack (no projectile travel)" |
| `DiggerUlti` (Ziggy Super) | dash | wave/area-follow | "Conjures a large electrical storm that travels across the map" |
| `ShadowdemonUltiCommand` (Sirius Super) | placement | self-aoe + spawn | "Shadow Summon — deploys all the Brawler Shadows he's collected" |
| `FuryUlti` (Moe Super) | line (w=6.25) | dash + placement | "drills underground … surfaces in a target direction" |
| `TwinsUlti` (Larry & Lawrie Super) | placement | placement + spawn | "Spawns his twin brother Lawrie, a controlled spawn" |
| `DuplicatorUlti` (Lola Super) | placement | placement + spawn | "Summons her Ego, a clone that mirrors her movement" |
| `LeaperUlti` (Mico Super) | self-aoe | placement (target leap) | "longer leap that deals damage and knockback on landing" |
| `CannonGirlUlti` (Bonnie Super) | dash | placement | "launching her a long distance and knocking back enemies on landing" |
| `InsectManUlti` (Angelo Super) | self-aoe (override) | placement | "Places a toxic puddle on the ground" |
| `JetpackGirlUlti` (Janet Super) | placement | self-aoe | "Crescendo — jetpacks into the air, becoming invulnerable" |
| `ShieldTankUlti` (Buster Super) | cone | placement/wall | "Deploys a barrier in front of him that blocks projectiles" |
| `DoorManUlti` (Gray Super) | None | placement (×2) | "Dimensional Doors — places two portals" |
| `SoulCollectorUlti` (Gus Super) | line | self-aoe | "Grants himself or a teammate a decaying shield while pushing all nearby enemies back" |
| `SniperUlti` (Piper Super) | dash | self-aoe + dash | "Pops grenades at her feet then jumps a long distance away, dealing damage at her takeoff point" |
| `ReviverUlti` (Doug Super) | line | self-aoe/placement | "Plants a hot dog at his location" |
| `FishTankWeapon` (Hank Attack) | area-follow | placement (charged) | "Releases as a single large area-of-effect explosion" |
| `SpawnerDudeWeapon` (Mr. P Attack) | line | placement | "Throws a suitcase that bounces on impact" |
| `CactusWeapon` (Spike Attack) | line | placement (splash on impact) | "Throws a cactus that explodes on impact, releasing spikes in all directions" |
| `CrossBomberWeapon` (Grom Attack) | placement (splash 6.25) | cluster (cross/plus) | "explodes in a cross-pattern blast" |
| `CrossBomberUlti` (Grom Super) | placement (splash 6.25) | cluster (cross/plus) | "bursts into four projectiles in a cross pattern" |
| `ArcadeWeapon` (8-Bit Attack) | cone (spread 18°) | line (parallel, w≈1.0) | "fires a volley of six straight, very long-ranged laser beams" |
| `BeamerOverchargedUlti` (Mandy Hyper) | cone (spread 170°) | cluster (3-line) | "fires two additional angled projectiles to the left and right" |
| `ControllerUlti` (Nani Super) | line (range 3.3) | placement + controlled | "Detaches Peep, a drone she manually steers" |
| `ControllerWeapon` (Nani Attack) | cone | cluster (diamond, converge) | "Three light orbs fired in a diamond pattern that converge at a specific range" |
| `GeishaTransformedUlti` (Kaze Ninja Super) | dash | placement (teleport) | "Ninja teleports to mark targets and detonates them on the next attack" |

---

## Section: WARN-only flags (acceptable shape, but should carry quirks)

These should not change shape, but the data model should add boolean flags so the renderer/KB has the info:

- `spawnsEntity: true` — Jessie, Penny, Pam, 8-Bit, Mr. P, Nita, Eve, Sandy, Bo, Ash, Spike Super,
  Sirius, Meeple, Juju Super, Larry & Lawrie Super, Lola Super, Tara Super, Charlie Super
  (cocoon), Otis Super (starfish stuck on enemy)
- `bouncesOffWalls: true` — Rico Attack/Super, Bibi Super, Sprout Attack, Dynamike Attack/Super,
  Belle (with gadget), Ruffs Attack, Darryl Super
- `chargedShot: true` — Bea Attack, Piper Attack, Pearl Attack (Heat), Surge Attack (stages),
  Clancy Attack, Mina Attack, Damian Attack, Janet Attack, Angelo Attack, Mandy Attack (Focus),
  Frank Attack (wind-up), Hank Attack
- `stages: N` — Mina (3), Damian (3), Clancy (3), Chester (4)
- `tetherOrChain: true` — Glowy, Jessie attack, Belle attack, Lily super, Sam super
- `teleportsOnHit: true` — Lily Super, Kaze Ninja Super, Lily gadget Repot, Sirius gadget Master
- `randomized: true` — Chester Super
- `controlledEntity: true` — Nani Super (Peep)
- `altFormSwitch: true` — Bonnie, Meg, Draco, Sam, Bibi (?), Kaze, R-T, Jae-Yong, Mina (kit
  alternation), Moe, Starr Nova

---

## Ambiguous / wiki-prose-insufficient cases

None — every brawler in `brawlers.json` has a matching kit entry in `kits.json`, and every kit entry
had enough prose to make a call. If anything is genuinely ambiguous it's the **degree** of the
mismatch (e.g., "is 8-Bit's parallel-laser volley better drawn as `line` or as a `cluster`?") rather
than the kind. Those judgment calls are reflected as ⚠️ rather than as missing data.
