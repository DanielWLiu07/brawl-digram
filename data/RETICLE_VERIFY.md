# Reticle Verification Checklist

Mark `[x]` for each variant you've verified looks correct in-game. Mark `[!]` if it's wrong — then add a `note` to `data/reticle_overrides.json` and re-run `python3 data/render_all_reticles.py`.

**Coverage**: 85 of 105 playable brawlers (38 have manual overrides). 20 newest brawlers absent until CSVs are refreshed from a newer tailsjs version.

**Gallery**: `open data/reticles/index.html` in browser to view each brawler's SVG side-by-side.

---

## A

### Alli ([SVG](./reticles/Alli.svg))
- [ ] **Attack** — dash — 0.67 tiles  `StalkerWeaponDash`
- [ ] **Super** — self-AoE (no aim)  🔧 `StalkerUlti`
- [ ] **Hypercharged Attack (+25%)** — dash — 0.83 tiles  `StalkerWeaponDash`
- [ ] **Hypercharged Super (+25%)** — self-AoE (no aim)  🔧 `StalkerUlti`
- Notes: 

### Amber ([SVG](./reticles/Amber.svg))
- [ ] **Attack** — line — 8.33 tiles, ~0.5 wide  🔧 `FireDudeWeapon`
- [ ] **Super** — placement — 7.33 tiles (no splash data)  `FireDudeUlti`
- [ ] **Hypercharged Attack (+25%)** — line — 10.41 tiles, ~0.5 wide  🔧 `FireDudeWeapon`
- [ ] **Hypercharged Super (+25%)** — placement — 9.17 tiles (no splash data)  `FireDudeUlti`
- Notes: 

### Angelo ([SVG](./reticles/Angelo.svg))
- [ ] **Attack** — line — 10.00 tiles, ~0.6 wide  `InsectManWeapon`
- [ ] **Super** — self-AoE (no aim)  🔧 `InsectManUlti`
- [ ] **Hypercharged Attack (+25%)** — line — 12.50 tiles, ~0.6 wide  `InsectManWeapon`
- [ ] **Hypercharged Super (+25%)** — self-AoE (no aim)  🔧 `InsectManUlti`
- Notes: 

### Ash ([SVG](./reticles/Ash.svg))
- [ ] **Attack** — line — 4.67 tiles, ~1.0 wide  `KnightWeapon`
- [ ] **Super** — placement — 5.00 tile range, 1.25 tile splash  `KnightUlti`
- [ ] **Hypercharged Attack (+25%)** — line — 5.83 tiles, ~1.0 wide  `KnightWeapon`
- [ ] **Hypercharged Super (+25%)** — placement — 6.25 tile range, 1.56 tile splash  `KnightUlti`
- Notes: 

## B

### Barley ([SVG](./reticles/Barley.svg))
- [ ] **Attack** — placement — 7.33 tile range, 1.25 tile splash  `BarkeepWeapon`
- [ ] **Super** — cluster (quincunx) — 9.33 tile range, 1.25 tile splash × 5  🔧 `BarkeepUlti`
- [ ] **Hypercharged Attack (+25%)** — placement — 9.17 tile range, 1.56 tile splash  `BarkeepWeapon`
- [ ] **Hypercharged Super (+25%)** — cluster (quincunx) — 11.66 tile range, 1.56 tile splash × 5  🔧 `BarkeepUlti`
- Notes: 

### Bea ([SVG](./reticles/Bea.svg))
- [ ] **Attack** — line — 10.00 tiles, ~0.8 wide  `BeeSniperWeapon`
- [ ] **Super** — cone — 9.00 tiles, 30°  `BeeSniperUlti`
- [ ] **Hypercharged Attack (+25%)** — line — 12.50 tiles, ~0.8 wide  `BeeSniperWeapon`
- [ ] **Hypercharged Super (+25%)** — cone — 11.25 tiles, 30°  `BeeSniperUlti`
- Notes: 

### Belle ([SVG](./reticles/Belle.svg))
- [ ] **Attack** — line — 10.00 tiles, ~0.6 wide  `ElectroSniperWeapon`
- [ ] **Super** — line — 10.67 tiles, ~0.6 wide  `ElectroSniperUlti`
- [ ] **Hypercharged Attack (+25%)** — line — 12.50 tiles, ~0.6 wide  `ElectroSniperWeapon`
- [ ] **Hypercharged Super (+25%)** — line — 13.33 tiles, ~0.6 wide  `ElectroSniperUlti`
- Notes: 

### Berry ([SVG](./reticles/Berry.svg))
- [ ] **Attack** — placement — 6.33 tile range, 1.04 tile splash  🔧 `PainterWeapon`
- [ ] **Super** — dash — 8.33 tiles  `PainterUlti`
- [ ] **Hypercharged Attack (+25%)** — placement — 7.91 tile range, 1.30 tile splash  🔧 `PainterWeapon`
- [ ] **Hypercharged Super (+25%)** — dash — 10.42 tiles  `PainterUlti`
- Notes: 

### Bibi ([SVG](./reticles/Bibi.svg))
- [ ] **Attack** — cone — 3.67 tiles, 300°  `BaseballWeapon`
- [ ] **Super** — line — 40.00 tiles, ~1.0 wide  `BaseballUlti`
- [ ] **Hypercharged Attack** — cone — 3.67 tiles, 300°  `BaseballOverchargedWeapon`
- [ ] **Hypercharged Super (+25%)** — line — 50.00 tiles, ~1.0 wide  `BaseballUlti`
- [ ] **Gadget: Sticky** — wave — 5 projectiles across 30°, 1.56 tile splash each  `BaseballGadgetSkillSticky`
- Notes: 

### Bo ([SVG](./reticles/Bo.svg))
- [ ] **Attack** — cone — 8.67 tiles, 30°  `BowDudeWeapon`
- [ ] **Super** — cluster (triangle) — 8.67 tile range, 0.84 tile splash × 3  🔧 `BowDudeUlti`
- [ ] **Hypercharged Attack** — cone — 8.67 tiles, 30°  `BowDudeOverchargedWeapon`
- [ ] **Hypercharged Super (+25%)** — cluster (triangle) — 10.84 tile range, 1.05 tile splash × 3  🔧 `BowDudeUlti`
- [ ] **Gadget: Totem** — placement — 7.33 tiles (no splash data)  `BowDudeGadgetSkillTotem`
- Notes: 

### Bolt ([SVG](./reticles/Bolt.svg))
- [ ] **Attack** — area-attack (follows brawler) — 0.50 tile radius  🔧 `RockWeapon`
- [ ] **Super** — self-AoE (no aim)  🔧 `RockUlti`
- [ ] **Gadget: Jump** — dash — 4.00 tiles  `RockGadgetJump`
- Notes: 

### Bonnie ([SVG](./reticles/Bonnie.svg))
- [ ] **Attack** — line — 9.00 tiles, ~0.6 wide  `CannonGirlWeapon`
- [ ] **Super** — dash — 7.33 tiles  `CannonGirlUlti`
- [ ] **Hypercharged Attack (+25%)** — line — 11.25 tiles, ~0.6 wide  `CannonGirlWeapon`
- [ ] **Hypercharged Super (+25%)** — dash — 9.17 tiles  `CannonGirlUlti`
- Notes: 

### Brock ([SVG](./reticles/Brock.svg))
- [ ] **Attack** — line — 9.00 tiles, ~0.6 wide  `RocketGirlWeapon`
- [ ] **Super** — wave — 5 projectiles across 160°, 0.94 tile splash each  `RocketGirlUlti`
- [ ] **Hypercharged Attack (+25%)** — line — 11.25 tiles, ~0.6 wide  `RocketGirlWeapon`
- [ ] **Hypercharged Super (+25%)** — wave — 5 projectiles across 160°, 1.17 tile splash each  `RocketGirlUlti`
- Notes: 

### Bull ([SVG](./reticles/Bull.svg))
- [ ] **Attack** — cone — 5.33 tiles, 90°  `BullDudeWeapon`
- [ ] **Super** — dash — 11.00 tiles  `BullDudeUlti`
- [ ] **Hypercharged Attack** — cone — 4.67 tiles, 90°  `BullDudeOverchargedWeapon`
- [ ] **Hypercharged Super (+25%)** — dash — 13.75 tiles  `BullDudeUlti`
- [ ] **Gadget: Stomp** — area-attack (follows brawler) — 1.67 tile radius  `BullDudeGadgetSkillStomp`
- Notes: 

### Buster ([SVG](./reticles/Buster.svg))
- [ ] **Attack** — cone — 5.33 tiles, 90°  `ShieldTankWeapon`
- [ ] **Super** — cone — 3.00 tiles, 120°  `ShieldTankUlti`
- [ ] **Hypercharged Attack (+25%)** — cone — 6.67 tiles, 90°  `ShieldTankWeapon`
- [ ] **Hypercharged Super (+25%)** — cone — 3.75 tiles, 120°  `ShieldTankUlti`
- Notes: 

### Buzz ([SVG](./reticles/Buzz.svg))
- [ ] **Attack** — cone — 2.67 tiles, 165°  `RopeDudeWeapon`
- [ ] **Super** — line — 10.00 tiles, ~0.6 wide  `RopeDudeUlti`
- [ ] **Hypercharged Attack (+25%)** — cone — 3.33 tiles, 165°  `RopeDudeWeapon`
- [ ] **Hypercharged Super (+25%)** — line — 12.50 tiles, ~0.6 wide  `RopeDudeUlti`
- Notes: 

### Byron ([SVG](./reticles/Byron.svg))
- [ ] **Attack** — line — 10.00 tiles, ~0.6 wide  `SnakeOilWeapon`
- [ ] **Super** — placement — 7.33 tile range, 1.67 tile splash  `SnakeOilUlti`
- [ ] **Hypercharged Attack (+25%)** — line — 12.50 tiles, ~0.6 wide  `SnakeOilWeapon`
- [ ] **Hypercharged Super (+25%)** — placement — 9.17 tile range, 2.08 tile splash  `SnakeOilUlti`
- Notes: 

## C

### Carl ([SVG](./reticles/Carl.svg))
- [ ] **Attack** — line — 8.33 tiles, ~1.0 wide  `WhirlwindWeapon`
- [ ] **Super** — area-attack (follows brawler) — 2.33 tile radius  🔧 `WhirlwindUlti`
- [ ] **Hypercharged Attack (+25%)** — line — 10.42 tiles, ~1.0 wide  `WhirlwindWeapon`
- [ ] **Hypercharged Super (+25%)** — area-attack (follows brawler) — 2.91 tile radius  🔧 `WhirlwindUlti`
- Notes: 

### Charlie ([SVG](./reticles/Charlie.svg))
- [ ] **Attack** — line — 9.00 tiles, ~0.6 wide  `CocoonerWeapon`
- [ ] **Super** — line — 9.00 tiles, ~0.8 wide  `CocoonerUlti`
- [ ] **Hypercharged Attack (+25%)** — line — 11.25 tiles, ~0.6 wide  `CocoonerWeapon`
- [ ] **Hypercharged Super (+25%)** — line — 11.25 tiles, ~0.8 wide  `CocoonerUlti`
- Notes: 

### Chester ([SVG](./reticles/Chester.svg))
- [ ] **Attack** — cone — 8.33 tiles, 30°  `JesterWeapon`
- [ ] **Super** — placement — 6.33 tiles (no splash data)  `JesterUltiExploding`
- [ ] **Hypercharged Attack (+25%)** — cone — 10.42 tiles, 30°  `JesterWeapon`
- [ ] **Hypercharged Super** — placement — 6.33 tile range, 1.67 tile splash  `JesterOverchargedUlti`
- Notes: 

### Chuck ([SVG](./reticles/Chuck.svg))
- [ ] **Attack** — cone — 6.67 tiles, 30°  🔧 `ConductorWeapon`
- [ ] **Super** — placement — 10.00 tile range, 0.42 tile splash  🔧 `ConductorUltiSpawn`
- [ ] **Hypercharged Attack (+25%)** — cone — 8.34 tiles, 30°  🔧 `ConductorWeapon`
- [ ] **Hypercharged Super (+25%)** — placement — 12.50 tile range, 0.53 tile splash  🔧 `ConductorUltiSpawn`
- Notes: 

### Clancy ([SVG](./reticles/Clancy.svg))
- [ ] **Attack** — line — 7.67 tiles, ~0.6 wide  `CrabWeapon1`
- [ ] **Super** — cone — 5.67 tiles, 220°  `CrabUlti1`
- [ ] **Hypercharged Attack (+25%)** — line — 9.58 tiles, ~0.6 wide  `CrabWeapon1`
- [ ] **Hypercharged Super (+25%)** — cone — 7.08 tiles, 220°  `CrabUlti1`
- Notes: 

### Colette ([SVG](./reticles/Colette.svg))
- [ ] **Attack** — line — 8.67 tiles, ~0.6 wide  `PercenterWeapon`
- [ ] **Super** — dash — 11.00 tiles  `PercenterUlti`
- [ ] **Hypercharged Attack** — line — 8.67 tiles, ~0.6 wide  `PercenterOverchargedWeapon`
- [ ] **Hypercharged Super (+25%)** — dash — 13.75 tiles  `PercenterUlti`
- [ ] **Gadget: Lifesteal** — line — 8.33 tiles, ~0.6 wide  `PercenterLifestealAttack`
- [ ] **Gadget: CharmAttack** — line — 8.33 tiles, ~0.6 wide  `PercenterCharmAttack`
- Notes: 

### Colt ([SVG](./reticles/Colt.svg))
- [ ] **Attack** — line — 9.00 tiles, ~0.6 wide  `GunslingerWeapon`
- [ ] **Super** — line — 11.00 tiles, ~0.6 wide  `GunslingerUlti`
- [ ] **Hypercharged Attack** — line — 9.00 tiles, ~0.6 wide  `GunslingerOverchargedWeapon`
- [ ] **Hypercharged Super (+25%)** — line — 13.75 tiles, ~0.6 wide  `GunslingerUlti`
- [ ] **Gadget: Reload** — line — 11.00 tiles, ~0.6 wide  `GunslingerGadgetSkillDoubleShot`
- [ ] **Gadget: BigBullet** — line — 11.00 tiles, ~0.6 wide  `GunslingerGadgetSkillSilverBullet`
- Notes: 

### Cordelius ([SVG](./reticles/Cordelius.svg))
- [ ] **Attack** — line — 5.33 tiles, ~0.6 wide  `DuelistWeapon`
- [ ] **Super** — line — 9.00 tiles, ~0.8 wide  `DuelistUlti`
- [ ] **Hypercharged Attack (+25%)** — line — 6.67 tiles, ~0.6 wide  `DuelistWeapon`
- [ ] **Hypercharged Super (+25%)** — line — 11.25 tiles, ~0.8 wide  `DuelistUlti`
- Notes: 

### Crow ([SVG](./reticles/Crow.svg))
- [ ] **Attack** — cone — 8.67 tiles, 45°  `CrowWeapon`
- [ ] **Super** — self-AoE (no aim)  🔧 `CrowUlti`
- [ ] **Hypercharged Attack** — cone — 8.67 tiles, 45°  `CrowOverchargedWeapon`
- [ ] **Hypercharged Super (+25%)** — self-AoE (no aim)  🔧 `CrowUlti`
- [ ] **Gadget: PoisonDagger** — line — 8.33 tiles, ~0.6 wide  `CrowThrowPoisonDagger`
- Notes: 

## D

### Darryl ([SVG](./reticles/Darryl.svg))
- [ ] **Attack** — cone — 6.00 tiles, 80°  `BarrelBotWeapon`
- [ ] **Super** — dash — 7.00 tiles  `BarrelBotUlti`
- [ ] **Hypercharged Attack (+25%)** — cone — 7.50 tiles, 80°  `BarrelBotWeapon`
- [ ] **Hypercharged Super (+25%)** — dash — 8.75 tiles  `BarrelBotUlti`
- Notes: 

### Doug ([SVG](./reticles/Doug.svg))
- [ ] **Attack** — area-attack (follows brawler) — 2.08 tile radius  `ReviverWeapon`
- [ ] **Super** — line — 9.33 tiles, ~0.8 wide  `ReviverUlti`
- [ ] **Hypercharged Attack (+25%)** — area-attack (follows brawler) — 2.60 tile radius  `ReviverWeapon`
- [ ] **Hypercharged Super (+25%)** — line — 11.67 tiles, ~0.8 wide  `ReviverUlti`
- Notes: 

### Draco ([SVG](./reticles/Draco.svg))
- [ ] **Attack** — line — 4.00 tiles, ~0.8 wide  `DragonRiderWeapon`
- [ ] **Super** — self-AoE (no aim)  🔧 `DragonRiderUlti`
- [ ] **Hypercharged Attack (+25%)** — line — 5.00 tiles, ~0.8 wide  `DragonRiderWeapon`
- [ ] **Hypercharged Super (+25%)** — self-AoE (no aim)  🔧 `DragonRiderUlti`
- Notes: 

### Dynamike ([SVG](./reticles/Dynamike.svg))
- [ ] **Attack** — cluster (pair) — 7.33 tile range, 1.67 tile splash × 2  🔧 `TntDudeWeapon`
- [ ] **Super** — placement — 7.33 tile range, 1.67 tile splash  `TntDudeUlti`
- [ ] **Hypercharged Attack (+25%)** — cluster (pair) — 9.16 tile range, 2.09 tile splash × 2  🔧 `TntDudeWeapon`
- [ ] **Hypercharged Super (+25%)** — placement — 9.17 tile range, 2.08 tile splash  `TntDudeUlti`
- Notes: 

## E

### Edgar ([SVG](./reticles/Edgar.svg))
- [ ] **Attack** — line — 2.00 tiles, ~1.2 wide  `EnragerWeapon`
- [ ] **Super** — dash — 6.67 tiles  `EnragerUlti`
- [ ] **Hypercharged Attack** — line — 2.00 tiles, ~0.8 wide  `EnragerOverchargedWeapon`
- [ ] **Hypercharged Super (+25%)** — dash — 8.33 tiles  `EnragerUlti`
- [ ] **Gadget: Gadget LetsFly** — line — 6.67 tiles, ~0.6 wide  `EnragerPull`
- Notes: 

### Emz ([SVG](./reticles/Emz.svg))
- [ ] **Attack** — cone — 6.67 tiles, 80°  `MummyWeapon`
- [ ] **Super** — self-AoE (no aim)  `MummyUlti`
- [ ] **Hypercharged Attack** — cone — 6.67 tiles, 100°  `MummyOverchargedWeapon`
- [ ] **Hypercharged Super (+25%)** — self-AoE (no aim)  `MummyUlti`
- [ ] **Gadget: Push** — line — 4.00 tiles, ~0.6 wide  `MummyGadgetSkillFriendzoner`
- [ ] **Gadget: Acid** — cone — 6.67 tiles, 80°  `MummyGadgetSkillAcidSpray`
- Notes: 

### Eve ([SVG](./reticles/Eve.svg))
- [ ] **Attack** — line — 9.33 tiles, ~0.8 wide  `FleaWeapon`
- [ ] **Super** — placement — 5.00 tiles (no splash data)  `FleaUlti`
- [ ] **Hypercharged Attack (+25%)** — line — 11.67 tiles, ~0.8 wide  `FleaWeapon`
- [ ] **Hypercharged Super (+25%)** — placement — 6.25 tiles (no splash data)  `FleaUlti`
- Notes: 

## F

### Fang ([SVG](./reticles/Fang.svg))
- [ ] **Attack** — line — 2.67 tiles, ~1.2 wide  `KickerDudeWeapon`
- [ ] **Super** — dash — 10.00 tiles  `KickerDudeUlti`
- [ ] **Hypercharged Attack (+25%)** — line — 3.33 tiles, ~1.2 wide  `KickerDudeWeapon`
- [ ] **Hypercharged Super (+25%)** — dash — 12.50 tiles  `KickerDudeUlti`
- Notes: 

### Finx ([SVG](./reticles/Finx.svg))
- [ ] **Attack** — line — 8.33 tiles, ~0.8 wide  🔧 `ChronomancerWeapon`
- [ ] **Super** — placement — 7.33 tile range, 0.63 tile splash  🔧 `ChronomancerUlti`
- [ ] **Hypercharged Attack (+25%)** — line — 10.41 tiles, ~0.8 wide  🔧 `ChronomancerWeapon`
- [ ] **Hypercharged Super (+25%)** — placement — 9.16 tile range, 0.79 tile splash  🔧 `ChronomancerUlti`
- Notes: 

### Frank ([SVG](./reticles/Frank.svg))
- [ ] **Attack** — cone — 6.00 tiles, 130°  `HammerDudeWeapon`
- [ ] **Super** — cone — 7.00 tiles, 130°  `HammerDudeUlti`
- [ ] **Hypercharged Attack** — cone — 6.00 tiles, 130°  `HammerDudeOverchargedWeapon`
- [ ] **Hypercharged Super (+25%)** — cone — 8.75 tiles, 130°  `HammerDudeUlti`
- [ ] **Gadget: Immunity** — cone — 6.00 tiles, 45°  `HammerDudeGadgetSkillNoiseCancel`
- [ ] **Gadget: Pull** — line — 7.33 tiles, ~0.6 wide  `HammerDudeGadgetSkillAttraction`
- Notes: 

## G

### Gale ([SVG](./reticles/Gale.svg))
- [ ] **Attack** — line — 8.33 tiles, ~4.0 wide  🔧 `BlowerWeapon`
- [ ] **Super** — line — 10.00 tiles, ~4.0 wide  🔧 `BlowerUlti`
- [ ] **Hypercharged Attack (+25%)** — line — 10.41 tiles, ~4.0 wide  🔧 `BlowerWeapon`
- [ ] **Hypercharged Super (+25%)** — line — 12.50 tiles, ~4.0 wide  🔧 `BlowerUlti`
- Notes: 

### Gene ([SVG](./reticles/Gene.svg))
- [ ] **Attack** — line — 5.67 tiles, ~0.6 wide  `HookWeapon`
- [ ] **Super** — line — 7.67 tiles, ~0.8 wide  `HookUlti`
- [ ] **Hypercharged Attack (+25%)** — line — 7.08 tiles, ~0.6 wide  `HookWeapon`
- [ ] **Hypercharged Super (+25%)** — line — 9.58 tiles, ~0.8 wide  `HookUlti`
- Notes: 

### Gigi ([SVG](./reticles/Gigi.svg))
- [ ] **Attack** — area-attack (follows brawler) — 1.46 tile radius  `DaredevilWeapon`
- [ ] **Super** — placement — 7.33 tile range, 1.46 tile splash  🔧 `DaredevilUlti`
- [ ] **Hypercharged Attack (+25%)** — area-attack (follows brawler) — 1.82 tile radius  `DaredevilWeapon`
- [ ] **Hypercharged Super (+25%)** — placement — 9.16 tile range, 1.82 tile splash  🔧 `DaredevilUlti`
- Notes: 

### Gray ([SVG](./reticles/Gray.svg))
- [ ] **Attack** — line — 9.00 tiles, ~0.6 wide  `DoorManWeapon`
- [ ] **Super** — skill: DoorManWeapon  `DoorManUlti`
- [ ] **Hypercharged Attack (+25%)** — skill: DoorManUlti  `line — 11.25 tiles, ~0.6 wide`
- [ ] **Hypercharged Super (+25%)** —   ``
- Notes: 

### Griff ([SVG](./reticles/Griff.svg))
- [ ] **Attack** — cone — 8.33 tiles, 30°  `AssaultShotgunWeapon`
- [ ] **Super** — cone — 9.00 tiles, 150°  `AssaultShotgunUlti`
- [ ] **Hypercharged Attack** — cone — 8.33 tiles, 30°  `AssaultShotgunOverchargedWeapon`
- [ ] **Hypercharged Super (+25%)** — cone — 11.25 tiles, 150°  `AssaultShotgunUlti`
- [ ] **Gadget: Bomb** — placement — 7.33 tiles (no splash data)  `AssaultShotgunBonusSkillBomb`
- [ ] **Gadget: Projectiles** — placement — 7.33 tiles (no splash data)  `AssaultShotgunBonusSkillCoinShower`
- Notes: 

### Grom ([SVG](./reticles/Grom.svg))
- [ ] **Attack** — placement — 7.67 tile range, 6.25 tile splash  `CrossBomberWeapon`
- [ ] **Super** — placement — 8.33 tile range, 6.25 tile splash  `CrossBomberUlti`
- [ ] **Hypercharged Attack (+25%)** — placement — 9.58 tile range, 7.81 tile splash  `CrossBomberWeapon`
- [ ] **Hypercharged Super (+25%)** — placement — 10.42 tile range, 7.81 tile splash  `CrossBomberUlti`
- Notes: 

### Gus ([SVG](./reticles/Gus.svg))
- [ ] **Attack** — line — 9.33 tiles, ~0.6 wide  `SoulCollectorWeapon`
- [ ] **Super** — line — 9.33 tiles, ~0.8 wide  `SoulCollectorUlti`
- [ ] **Hypercharged Attack (+25%)** — line — 11.67 tiles, ~0.6 wide  `SoulCollectorWeapon`
- [ ] **Hypercharged Super (+25%)** — line — 11.67 tiles, ~0.8 wide  `SoulCollectorUlti`
- Notes: 

## J

### Jacky ([SVG](./reticles/Jacky.svg))
- [ ] **Attack** — area-attack (follows brawler) — 2.08 tile radius  `DrillerWeapon`
- [ ] **Super** — self-AoE (no aim)  `DrillerUlti`
- [ ] **Hypercharged Attack (+25%)** — area-attack (follows brawler) — 2.60 tile radius  `DrillerWeapon`
- [ ] **Hypercharged Super (+25%)** — self-AoE (no aim)  `DrillerUlti`
- Notes: 

### Janet ([SVG](./reticles/Janet.svg))
- [ ] **Attack** — cone — 4.00 tiles, 160°  `JetpackGirlWeapon`
- [ ] **Super** — placement — 2.33 tile range, 1.25 tile splash  `JetpackGirlUlti`
- [ ] **Hypercharged Attack (+25%)** — cone — 5.00 tiles, 160°  `JetpackGirlWeapon`
- [ ] **Hypercharged Super (+25%)** — placement — 2.92 tile range, 1.56 tile splash  `JetpackGirlUlti`
- Notes: 

### Jessie ([SVG](./reticles/Jessie.svg))
- [ ] **Attack** — line — 9.00 tiles, ~0.6 wide  `MechanicWeapon`
- [ ] **Super** — placement — 5.00 tile range, 2.71 tile splash  `MechanicUlti`
- [ ] **Hypercharged Attack (+25%)** — line — 11.25 tiles, ~0.6 wide  `MechanicWeapon`
- [ ] **Hypercharged Super (+25%)** — placement — 6.25 tile range, 3.39 tile splash  `MechanicUlti`
- Notes: 

### Juju ([SVG](./reticles/Juju.svg))
- [ ] **Attack** — placement — 6.33 tile range, 0.50 tile splash  🔧 `VoodooWeaponEarth`
- [ ] **Super** — placement — 5.00 tile range, 0.35 tile splash  🔧 `VoodooUlti`
- [ ] **Hypercharged Attack (+25%)** — placement — 7.91 tile range, 0.62 tile splash  🔧 `VoodooWeaponEarth`
- [ ] **Hypercharged Super (+25%)** — placement — 6.25 tile range, 0.44 tile splash  🔧 `VoodooUlti`
- Notes: 

## K

### Kaze ([SVG](./reticles/Kaze.svg))
- [ ] **Attack** — dash — 2.67 tiles  `GeishaWeapon`
- [ ] **Super** — placement — 7.33 tile range, 3.12 tile splash  🔧 `GeishaUlti`
- [ ] **Hypercharged Attack (+25%)** — dash — 3.33 tiles  `GeishaWeapon`
- [ ] **Hypercharged Super (+25%)** — placement — 9.16 tile range, 3.90 tile splash  🔧 `GeishaUlti`
- [ ] **Alt-form Attack** — line — 6.67 tiles, ~0.6 wide  `GeishaTransformedWeapon`
- [ ] **Alt-form Super** — dash — 9.00 tiles  `GeishaTransformedUlti`
- Notes: 

### Kit ([SVG](./reticles/Kit.svg))
- [ ] **Attack** — cone — 3.67 tiles, 150°  `AttacherWeapon`
- [ ] **Super** — dash — 6.67 tiles  `AttacherUlti`
- [ ] **Hypercharged Attack (+25%)** — cone — 4.58 tiles, 150°  `AttacherWeapon`
- [ ] **Hypercharged Super (+25%)** — dash — 8.33 tiles  `AttacherUlti`
- Notes: 

## L

### Leon ([SVG](./reticles/Leon.svg))
- [ ] **Attack** — cone — 9.67 tiles, 35°  `NinjaWeapon`
- [ ] **Super** — self-AoE (no aim)  🔧 `NinjaUlti`
- [ ] **Hypercharged Attack** — cone — 9.67 tiles, 35°  `NinjaOverchargedWeapon`
- [ ] **Hypercharged Super (+25%)** — self-AoE (no aim)  🔧 `NinjaUlti`
- [ ] **Gadget: InvisibleArea** — placement — 7.33 tiles (no splash data)  `NinjaBonusSkillInvisibleArea`
- Notes: 

### Lily ([SVG](./reticles/Lily.svg))
- [ ] **Attack** — line — 2.00 tiles, ~1.2 wide  `AmbusherWeapon`
- [ ] **Super** — line — 9.00 tiles, ~0.8 wide  `AmbusherUlti`
- [ ] **Hypercharged Attack (+25%)** — line — 2.50 tiles, ~1.2 wide  `AmbusherWeapon`
- [ ] **Hypercharged Super (+25%)** — line — 11.25 tiles, ~0.8 wide  `AmbusherUlti`
- Notes: 

### Lou ([SVG](./reticles/Lou.svg))
- [ ] **Attack** — line — 9.33 tiles, ~0.6 wide  `IceDudeWeapon`
- [ ] **Super** — placement — 7.67 tile range, 2.29 tile splash  `IceDudeUlti`
- Notes: 

### Lumi ([SVG](./reticles/Lumi.svg))
- [ ] **Attack** — line — 8.00 tiles, ~0.7 wide  `MorningstarWeapon`
- [ ] **Super** — wave — 3 projectiles across 0°, 3.67 tile splash each  🔧 `MorningstarUlti`
- [ ] **Hypercharged Attack (+25%)** — line — 10.00 tiles, ~0.7 wide  `MorningstarWeapon`
- [ ] **Hypercharged Super (+25%)** — wave — 3 projectiles across 0°, 4.59 tile splash each  🔧 `MorningstarUlti`
- Notes: 

## M

### Maisie ([SVG](./reticles/Maisie.svg))
- [ ] **Attack** — line — 8.67 tiles, ~0.6 wide  `MaisieWeapon`
- [ ] **Super** — area-attack (follows brawler) — 3.12 tile radius  `MaisieUlti`
- [ ] **Hypercharged Attack (+25%)** — line — 10.83 tiles, ~0.6 wide  `MaisieWeapon`
- [ ] **Hypercharged Super (+25%)** — area-attack (follows brawler) — 3.91 tile radius  `MaisieUlti`
- Notes: 

### Mandy ([SVG](./reticles/Mandy.svg))
- [ ] **Attack** — line — 9.00 tiles, ~0.6 wide  `BeamerWeapon`
- [ ] **Super** — line — 40.00 tiles, ~1.0 wide  `BeamerUlti`
- [ ] **Hypercharged Attack (+25%)** — line — 11.25 tiles, ~0.6 wide  `BeamerWeapon`
- [ ] **Hypercharged Super** — cone — 40.00 tiles, 170°  `BeamerOverchargedUlti`
- Notes: 

### Max ([SVG](./reticles/Max.svg))
- [ ] **Attack** — line — 6.67 tiles, ~0.5 wide  🔧 `SpeedyWeapon`
- [ ] **Super** — self-AoE (no aim)  `SpeedyUlti`
- [ ] **Hypercharged Attack (+25%)** — line — 8.34 tiles, ~0.5 wide  🔧 `SpeedyWeapon`
- [ ] **Hypercharged Super (+25%)** — self-AoE (no aim)  `SpeedyUlti`
- Notes: 

### Meeple ([SVG](./reticles/Meeple.svg))
- [ ] **Attack** — line — 7.67 tiles, ~0.6 wide  `MeepleWeapon`
- [ ] **Super** — placement — 5.00 tile range, 1.88 tile splash  `MeepleUlti`
- [ ] **Hypercharged Attack (+25%)** — line — 9.58 tiles, ~0.6 wide  `MeepleWeapon`
- [ ] **Hypercharged Super (+25%)** — placement — 6.25 tile range, 2.34 tile splash  `MeepleUlti`
- Notes: 

### Meg ([SVG](./reticles/Meg.svg))
- [ ] **Attack** — line — 9.00 tiles, ~0.6 wide  `MechaDudeWeapon`
- [ ] **Super** — self-AoE (no aim)  🔧 `MechaDudeUlti`
- [ ] **Hypercharged Attack (+25%)** — line — 11.25 tiles, ~0.6 wide  `MechaDudeWeapon`
- [ ] **Hypercharged Super (+25%)** — self-AoE (no aim)  🔧 `MechaDudeUlti`
- Notes: 

### Mico ([SVG](./reticles/Mico.svg))
- [ ] **Attack** — dash — 4.00 tiles  `LeaperWeapon`
- [ ] **Super** — self-AoE (no aim)  🔧 `LeaperUlti`
- [ ] **Hypercharged Attack (+25%)** — dash — 5.00 tiles  `LeaperWeapon`
- [ ] **Hypercharged Super (+25%)** — self-AoE (no aim)  🔧 `LeaperUlti`
- Notes: 

### Mortis ([SVG](./reticles/Mortis.svg))
- [ ] **Attack** — dash — 2.67 tiles  `UndertakerWeapon`
- [ ] **Super** — line — 10.00 tiles, ~1.7 wide  `UndertakerUlti`
- [ ] **Hypercharged Attack** — dash — 2.67 tiles  `UndertakerOverchargedWeapon`
- [ ] **Hypercharged Super (+25%)** — line — 12.50 tiles, ~1.7 wide  `UndertakerUlti`
- [ ] **Gadget: Swing** — line — 2.67 tiles, ~0.8 wide  `UndertakerGadgetSkillComboSpinner`
- [ ] **Gadget: Reload** — line — 5.00 tiles, ~0.6 wide  `UndertakerGadgetSkillBats`
- Notes: 

## N

### Nani ([SVG](./reticles/Nani.svg))
- [ ] **Attack** — cone — 8.67 tiles, 50°  `ControllerWeapon`
- [ ] **Super** — line — 3.33 tiles, ~0.6 wide  `ControllerUlti`
- [ ] **Hypercharged Attack (+25%)** — cone — 10.83 tiles, 50°  `ControllerWeapon`
- [ ] **Hypercharged Super (+25%)** — line — 4.17 tiles, ~0.6 wide  `ControllerUlti`
- Notes: 

### Nita ([SVG](./reticles/Nita.svg))
- [ ] **Attack** — line — 6.00 tiles, ~1.0 wide  `ShamanWeapon`
- [ ] **Super** — placement — 5.00 tile range, 2.08 tile splash  `ShamanUlti`
- [ ] **Hypercharged Attack** — line — 6.67 tiles, ~1.0 wide  `ShamanOverchargedWeapon`
- [ ] **Hypercharged Super (+25%)** — placement — 6.25 tile range, 2.60 tile splash  `ShamanUlti`
- Notes: 

## O

### Ollie ([SVG](./reticles/Ollie.svg))
- [ ] **Attack** — cone — 6.33 tiles, 27°  `SkaterWeapon`
- [ ] **Super** — dash — 5.67 tiles  `SkaterUlti`
- [ ] **Hypercharged Attack (+25%)** — cone — 7.92 tiles, 27°  `SkaterWeapon`
- [ ] **Hypercharged Super** — dash — 6.67 tiles  `SkaterOverchargedUlti`
- Notes: 

### Otis ([SVG](./reticles/Otis.svg))
- [ ] **Attack** — line — 9.00 tiles, ~0.2 wide  🔧 `SilencerWeapon`
- [ ] **Super** — line — 9.00 tiles, ~0.8 wide  `SilencerUlti`
- [ ] **Hypercharged Attack (+25%)** — line — 11.25 tiles, ~0.2 wide  🔧 `SilencerWeapon`
- [ ] **Hypercharged Super (+25%)** — line — 11.25 tiles, ~0.8 wide  `SilencerUlti`
- Notes: 

## P

### Pam ([SVG](./reticles/Pam.svg))
- [ ] **Attack** — cone — 9.00 tiles, 60°  `MinigunDudeWeapon`
- [ ] **Super** — placement — 5.00 tiles (no splash data)  `MinigunDudeUlti`
- [ ] **Hypercharged Attack (+25%)** — cone — 11.25 tiles, 60°  `MinigunDudeWeapon`
- [ ] **Hypercharged Super (+25%)** — placement — 6.25 tiles (no splash data)  `MinigunDudeUlti`
- Notes: 

### Pearl ([SVG](./reticles/Pearl.svg))
- [ ] **Attack** — cone — 9.00 tiles, 40°  `CookerWeapon`
- [ ] **Super** — self-AoE (no aim)  `CookerUlti`
- [ ] **Hypercharged Attack (+25%)** — cone — 11.25 tiles, 40°  `CookerWeapon`
- [ ] **Hypercharged Super (+25%)** — self-AoE (no aim)  `CookerUlti`
- Notes: 

### Penny ([SVG](./reticles/Penny.svg))
- [ ] **Attack** — line — 8.67 tiles, ~0.6 wide  `ArtilleryDudeWeapon`
- [ ] **Super** — placement — 5.00 tile range, 1.67 tile splash  `ArtilleryDudeUlti`
- [ ] **Hypercharged Attack (+25%)** — line — 10.83 tiles, ~0.6 wide  `ArtilleryDudeWeapon`
- [ ] **Hypercharged Super (+25%)** — placement — 6.25 tile range, 2.08 tile splash  `ArtilleryDudeUlti`
- Notes: 

### Pierce ([SVG](./reticles/Pierce.svg))
- [ ] **Attack** — line — 10.00 tiles, ~0.6 wide  `BulletstormWeapon`
- [ ] **Super** — placement — 8.33 tile range, 0.54 tile splash  🔧 `BulletstormUlti`
- [ ] **Hypercharged Attack (+25%)** — line — 12.50 tiles, ~0.6 wide  `BulletstormWeapon`
- [ ] **Hypercharged Super (+25%)** — placement — 10.41 tile range, 0.68 tile splash  🔧 `BulletstormUlti`
- Notes: 

### Piper ([SVG](./reticles/Piper.svg))
- [ ] **Attack** — line — 10.00 tiles, ~0.6 wide  `SniperWeapon`
- [ ] **Super** — dash — 8.67 tiles  `SniperUlti`
- [ ] **Hypercharged Attack (+25%)** — line — 12.50 tiles, ~0.6 wide  `SniperWeapon`
- [ ] **Hypercharged Super (+25%)** — dash — 10.83 tiles  `SniperUlti`
- Notes: 

### Poco ([SVG](./reticles/Poco.svg))
- [ ] **Attack** — cone — 7.00 tiles, 130°  `DeadMariachiWeapon`
- [ ] **Super** — cone — 9.33 tiles, 130°  `DeadMariachiUlti`
- [ ] **Hypercharged Attack (+25%)** — cone — 8.75 tiles, 130°  `DeadMariachiWeapon`
- [ ] **Hypercharged Super (+25%)** — cone — 11.67 tiles, 130°  `DeadMariachiUlti`
- Notes: 

## R

### Rosa ([SVG](./reticles/Rosa.svg))
- [ ] **Attack** — cone — 3.67 tiles, 130°  `RosaWeapon`
- [ ] **Super** — self-AoE (no aim)  `RosaUlti`
- [ ] **Hypercharged Attack (+25%)** — cone — 4.58 tiles, 130°  `RosaWeapon`
- [ ] **Hypercharged Super (+25%)** — self-AoE (no aim)  `RosaUlti`
- Notes: 

### Ruffs ([SVG](./reticles/Ruffs.svg))
- [ ] **Attack** — line — 9.00 tiles, ~1.0 wide  🔧 `RuffsWeapon`
- [ ] **Super** — placement — 7.67 tile range, 1.46 tile splash  `RuffsUlti`
- [ ] **Hypercharged Attack (+25%)** — line — 11.25 tiles, ~1.0 wide  🔧 `RuffsWeapon`
- [ ] **Hypercharged Super (+25%)** — placement — 9.58 tile range, 1.82 tile splash  `RuffsUlti`
- Notes: 

## S

### Sam ([SVG](./reticles/Sam.svg))
- [ ] **Attack** — cone — 3.00 tiles, 100°  `WeaponThrowerWeapon`
- [ ] **Super** — line — 8.67 tiles, ~1.0 wide  `WeaponThrowerUlti`
- [ ] **Hypercharged Attack (+25%)** — cone — 3.75 tiles, 100°  `WeaponThrowerWeapon`
- [ ] **Hypercharged Super (+25%)** — line — 10.83 tiles, ~1.0 wide  `WeaponThrowerUlti`
- Notes: 

### Sandy ([SVG](./reticles/Sandy.svg))
- [ ] **Attack** — cone — 6.00 tiles, 80°  `SandstormWeapon`
- [ ] **Super** — placement — 7.33 tile range, 2.08 tile splash  `SandstormUlti`
- [ ] **Hypercharged Attack (+25%)** — cone — 7.50 tiles, 80°  `SandstormWeapon`
- [ ] **Hypercharged Super (+25%)** — placement — 9.17 tile range, 2.60 tile splash  `SandstormUlti`
- Notes: 

### Shade ([SVG](./reticles/Shade.svg))
- [ ] **Attack** — cone — 3.67 tiles, 300°  🔧 `GhostWeapon`
- [ ] **Super** — dash — 3.33 tiles  🔧 `GhostUlti`
- [ ] **Hypercharged Attack (+25%)** — cone — 4.59 tiles, 300°  🔧 `GhostWeapon`
- [ ] **Hypercharged Super (+25%)** — dash — 4.16 tiles  🔧 `GhostUlti`
- Notes: 

### Shelly ([SVG](./reticles/Shelly.svg))
- [ ] **Attack** — cone — 7.67 tiles, 60°  `ShotgunGirlWeapon`
- [ ] **Super** — cone — 7.67 tiles, 100°  `ShotgunGirlUlti`
- [ ] **Hypercharged Attack** — cone — 7.67 tiles, 60°  `ShotgunGirlOverchargedWeapon`
- [ ] **Hypercharged Super (+25%)** — cone — 9.58 tiles, 100°  `ShotgunGirlUlti`
- [ ] **Gadget: Dash** — dash — 2.67 tiles  `ShotgungirlGadgetSkillReload`
- [ ] **Gadget: Focus** — cone — 10.00 tiles, 30°  `ShotgunGirlClayPigeons`
- Notes: 

### Spike ([SVG](./reticles/Spike.svg))
- [ ] **Attack** — line — 7.67 tiles, ~0.6 wide  `CactusWeapon`
- [ ] **Super** — placement — 7.67 tile range, 1.67 tile splash  `CactusUlti`
- [ ] **Hypercharged Attack** — line — 7.67 tiles, ~0.6 wide  `CactusOverchargedWeapon`
- [ ] **Hypercharged Super (+25%)** — placement — 9.58 tile range, 2.08 tile splash  `CactusUlti`
- [ ] **Gadget: ShootAround** — cone — 7.67 tiles, 60°  `CactusBonusSkillPoppin`
- [ ] **Gadget: Cover** — placement — 7.33 tile range, 1.25 tile splash  `CactusBonusSkillCover`
- Notes: 

### Sprout ([SVG](./reticles/Sprout.svg))
- [ ] **Attack** — placement — 5.00 tile range, 0.10 tile splash  🔧 `WallyWeapon`
- [ ] **Super** — placement — 7.67 tile range, 0.83 tile splash  `WallyUlti`
- [ ] **Hypercharged Attack (+25%)** — placement — 6.25 tile range, 0.12 tile splash  🔧 `WallyWeapon`
- [ ] **Hypercharged Super (+25%)** — placement — 9.58 tile range, 1.04 tile splash  `WallyUlti`
- Notes: 

### Squeak ([SVG](./reticles/Squeak.svg))
- [ ] **Attack** — line — 7.67 tiles, ~0.6 wide  `StickyBombWeapon`
- [ ] **Super** — cluster (quincunx) — 8.33 tile range, 0.83 tile splash × 5  🔧 `StickyBombUlti`
- [ ] **Hypercharged Attack (+25%)** — line — 9.58 tiles, ~0.6 wide  `StickyBombWeapon`
- [ ] **Hypercharged Super (+25%)** — cluster (quincunx) — 10.41 tile range, 1.04 tile splash × 5  🔧 `StickyBombUlti`
- Notes: 

### Stu ([SVG](./reticles/Stu.svg))
- [ ] **Attack** — line — 7.67 tiles, ~0.6 wide  `RollerWeapon`
- [ ] **Super** — dash — 2.33 tiles  `RollerUlti`
- [ ] **Hypercharged Attack (+25%)** — line — 9.58 tiles, ~0.6 wide  `RollerWeapon`
- [ ] **Hypercharged Super (+25%)** — dash — 2.92 tiles  `RollerUlti`
- Notes: 

### Surge ([SVG](./reticles/Surge.svg))
- [ ] **Attack** — line — 6.67 tiles, ~0.6 wide  `PowerLevelerWeapon`
- [ ] **Super** — dash — 3.33 tiles  `PowerLevelerUlti`
- [ ] **Hypercharged Attack (+25%)** — line — 8.33 tiles, ~0.6 wide  `PowerLevelerWeapon`
- [ ] **Hypercharged Super (+25%)** — dash — 4.17 tiles  `PowerLevelerUlti`
- Notes: 

## T

### Tara ([SVG](./reticles/Tara.svg))
- [ ] **Attack** — cone — 8.00 tiles, 50°  `BlackHoleWeapon`
- [ ] **Super** — placement — 6.67 tile range, 2.50 tile splash  🔧 `BlackHoleUlti`
- [ ] **Hypercharged Attack (+25%)** — cone — 10.00 tiles, 50°  `BlackHoleWeapon`
- [ ] **Hypercharged Super (+25%)** — placement — 8.34 tile range, 3.12 tile splash  🔧 `BlackHoleUlti`
- Notes: 

### Tick ([SVG](./reticles/Tick.svg))
- [ ] **Attack** — cluster (triangle) — 8.67 tile range, 1.56 tile splash × 3  🔧 `ClusterBombDudeWeapon`
- [ ] **Super** — placement — 3.33 tile range, 1.04 tile splash  🔧 `ClusterBombDudeUlti`
- [ ] **Hypercharged Attack (+25%)** — cluster (triangle) — 10.84 tile range, 1.95 tile splash × 3  🔧 `ClusterBombDudeWeapon`
- [ ] **Hypercharged Super (+25%)** — placement — 4.16 tile range, 1.30 tile splash  🔧 `ClusterBombDudeUlti`
- Notes: 

### Trunk ([SVG](./reticles/Trunk.svg))
- [ ] **Attack** — area-attack (follows brawler) — 2.08 tile radius  `DomainWeapon`
- [ ] **Super** — dash — 7.00 tiles  `DomainUlti`
- [ ] **Hypercharged Attack (+25%)** — area-attack (follows brawler) — 2.60 tile radius  `DomainWeapon`
- [ ] **Hypercharged Super** — dash — 7.00 tiles  `DomainOverchargedUlti`
- Notes: 

## W

### Willow ([SVG](./reticles/Willow.svg))
- [ ] **Attack** — placement — 7.33 tile range, 1.25 tile splash  `PuppeteerWeapon`
- [ ] **Super** — line — 8.33 tiles, ~0.6 wide  `PuppeteerUlti`
- [ ] **Hypercharged Attack (+25%)** — placement — 9.17 tile range, 1.56 tile splash  `PuppeteerWeapon`
- [ ] **Hypercharged Super (+25%)** — line — 10.42 tiles, ~0.6 wide  `PuppeteerUlti`
- Notes: 
