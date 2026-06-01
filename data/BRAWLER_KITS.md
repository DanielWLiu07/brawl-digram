# Brawler Kits (wiki-grounded)

Per-brawler attack reference. Numeric stats (HP, range, splash, damage, reload, ammo) come from the v67.264 CSV dump (`data/brawlers.json`). Kit prose (attack/super/hypercharge/star powers/gadgets/quirks) is grounded in the [Brawl Stars Fandom wiki](https://brawlstars.fandom.com/wiki/Brawl_Stars_Wiki).

- All ranges in tiles, reload in seconds. Damage is per projectile (raw CSV value, before level scaling).
- Brawlers absent from the CSV (post-dump or event-only brawlers) are marked _CSV mechanics N/A_.
- Cross-checked stats notes are in the "Wiki-vs-CSV discrepancies" section at the bottom.

---

### 8-Bit (Arcade) — Damage Dealer
Fires a volley of six straight, very long-ranged laser beams.
- HP: 5200 · Speed: 1.93 t/s · Reload: ~1.5s · Ammo: 3
- Attack: 10.00-tile, 18° cone, 340 dmg.
- Super: 5.00-tile, 3.12-tile splash, indirect.
- **Super:** Drops a Damage Booster turret that buffs damage for 8-Bit and allies standing in its radius.
- **Hypercharge: Aimbot** — Turret gains more health and starts firing long-ranged laser beams of its own.
- Star Powers: **Boosted Booster** — Damage Booster gains larger radius and a bigger damage buff. · **Plugged In** — 8-Bit moves significantly faster while standing next to his Damage Booster.
- Gadgets: **Cheat Cartridge** — Instantly teleports 8-Bit to his Damage Booster. · **Extra Credits** — Next attack fires triple the number of laser projectiles.
- Quirks: Slowest movement speed in the game; Super spawns a persistent turret.
*Source: brawlstars.fandom.com/wiki/8-Bit*

### Alli (Stalker) — Assassin
Short dash on the ground; in bushes or over water she jumps over obstacles and slams down for area damage on landing.
- HP: 3900 · Speed: 2.57 t/s · Reload: ~2.1s · Ammo: 3
- Attack: 0.67-tile, 1300 dmg.
- Super: —.
- **Super:** Enters an enraged Stalker state where she becomes intermittently invisible and her first attack deals bonus damage scaled to enemy health.
- **Hypercharge: Swamp Snacking** — Attacks heal her when they connect.
- Star Powers: **Lizard Limbs** — Begins regenerating health sooner while enraged. · **You Better Run You Better Take Cover** — Reloads faster while enraged.
- Gadgets: **Feed The Gators** — Next attack heals her based on damage dealt. · **Cold-Blooded** — Becomes enraged for a short duration when an enemy is visible.
- Quirks: Attack IS a dash (no projectile); Terrain changes attack: bush/water gives a jump; Super produces partial invisibility.
*Source: brawlstars.fandom.com/wiki/Alli*

### Amber (FireDude) — Controller
Sprays a continuous, long-ranged stream of fire from her flamethrower that pierces enemies.
- HP: 3400 · Speed: 2.40 t/s · Reload: ~0.2s · Ammo: 40
- Attack: 8.33-tile, 210 dmg, pierces.
- Super: 7.33-tile, 0.00-tile splash, indirect.
- **Super:** Throws a flask of fire fluid that puddles on the ground; her attack stream ignites the puddle, burning enemies that stand in it.
- **Hypercharge: Oil Spill** — Increases the radius of her Super's flammable puddle.
- Star Powers: **Wild Flames** — Two puddles can exist at once and Super charges passively when she stands near one. · **Scorchin Siphon** — Reloads faster when standing near a fire fluid puddle.
- Gadgets: **Fire Starters** — Runs forward leaving a flammable trail behind that ignites like her Super puddle. · **Dancing Flames** — Spawns three flames that orbit her, damaging enemies on contact.
- Quirks: Attack drains a fuel meter (continuous beam, not discrete shots); Super interacts with attack: throw puddle, then ignite with stream; Attack pierces multiple targets.
*Source: brawlstars.fandom.com/wiki/Amber*

### Angelo (InsectMan) — Marksman
Long-ranged charged arrow shot; holding the attack joystick charges damage up to a maximum after ~2.5 seconds.
- HP: 3100 · Speed: 2.73 t/s · Reload: ~0.1s · Ammo: 1
- Attack: 10.00-tile, 2000 dmg.
- Super: 500 dmg.
- **Super:** Places a toxic puddle on the ground; standing in it makes his attacks apply poison damage over time.
- **Hypercharge: In My Element** — His Super's puddle now follows him as he moves.
- Star Powers: **Empower** — Heals over time while standing in his Super puddle. · **Flow** — Gains a movement speed boost while hovering on water.
- Gadgets: **Stinging Flight** — Launches into the air, damaging nearby enemies and healing himself. · **Master Fletcher** — Next attack pierces obstacles and enemies.
- Quirks: Attack damage scales with charge time; Single-ammo design (1 ammo slot, fast individual reload); Can hover on water.
*Source: brawlstars.fandom.com/wiki/Angelo*

### Ash (Knight) — Tank
Smashes his broom on the ground sending a piercing shockwave; damage scales with his Rage meter.
- HP: 5900 · Speed: 2.40 t/s · Reload: ~1.4s · Ammo: 3
- Attack: 4.67-tile, 800 dmg, pierces.
- Super: 5.00-tile, 1.25-tile splash, indirect.
- **Super:** Releases a swarm of robotic rats that chase the nearest enemy and explode on contact.
- **Hypercharge: Rat King** — Super spawns double the number of robotic rats.
- Star Powers: **First Bash** — Gains extra Rage on hit while ammo is full. · **Mad As Heck** — Reload speed scales with Rage.
- Gadgets: **Chill Pill** — Heals based on how much Rage is currently stored. · **Rotten Banana** — Trades current health for an instant Rage boost.
- Quirks: Rage meter charges on damage dealt and received; boosts speed and damage; Third-highest HP in the game; Attack projectile pierces.
*Source: brawlstars.fandom.com/wiki/Ash*

### Barley (Barkeep) — Artillery
Lobs a bottle of harmful liquid over walls that creates a damaging puddle on the ground for a few seconds.
- HP: 2700 · Speed: 2.40 t/s · Reload: ~2.0s · Ammo: 3
- Attack: 7.33-tile, 1.25-tile splash, 800 dmg, indirect.
- Super: 9.33-tile, 1.25-tile splash, 800 dmg, indirect.
- **Super:** Lobs five flaming bottles in a wider spread that travel further and create larger lingering puddles.
- **Hypercharge: Bottled-Up Rage** — Super now lobs three large bottles covering a wider area and destroying bushes.
- Star Powers: **Medical Use** — Heals himself a small amount with every attack thrown. · **Extra Noxious** — Adds more damage-per-second to attack puddles.
- Gadgets: **Sticky Syrup Mixer** — Drops a slowing puddle of syrup around himself. · **Herbal Tonic** — Lobs healing bottles around himself and allies.
- Quirks: Attack and Super lob over walls; Damage-over-time puddle (not direct impact).
*Source: brawlstars.fandom.com/wiki/Barley*

### Bea (BeeSniper) — Marksman
Fires a long-ranged bee dealing moderate damage; hitting an enemy Supercharges her next shot to deal massive damage.
- HP: 2800 · Speed: 2.40 t/s · Reload: ~0.9s · Ammo: 1
- Attack: 10.00-tile, 800 dmg.
- Super: 9.00-tile, 30° cone, 100 dmg × 7.
- **Super:** Releases a swarm of seven bee drones that fan out, dealing damage and slowing enemies hit.
- **Hypercharge: Protect the Queen** — Super projectiles split into two on hit or at max range.
- Star Powers: **Insta Beaload** — If she misses a Supercharged shot, the next one is also Supercharged. · **Honeycomb** — Gains a shield while a Supercharged shot is loaded.
- Gadgets: **Honey Molasses** — Drops a beehive surrounded by a slowing honey puddle. · **Rattled Hive** — Sends four spiraling bees that deal more damage the further they fly.
- Quirks: Charged-shot mechanic: every hit Supercharges the next attack; Single-ammo design.
*Source: brawlstars.fandom.com/wiki/Bea*

### Belle (ElectroSniper) — Marksman
Long-ranged Electro-Bolt that chains to nearby enemies on hit.
- HP: 2900 · Speed: 2.40 t/s · Reload: ~1.4s · Ammo: 3
- Attack: 10.00-tile, 1040 dmg.
- Super: 10.67-tile, 550 dmg.
- **Super:** Marks an enemy with a tracer that increases all damage taken until the target is defeated or she fires another Super.
- **Hypercharge: Magnetic** — Super projectile homes in on enemies.
- Star Powers: **Positive Feedback** — Gains a brief shield whenever her attack hits an enemy Brawler. · **Grounded** — Marked enemies cannot reload for a short duration.
- Gadgets: **Nest Egg** — Places an invisible trap that slows and damages enemies on trigger. · **Reverse Polarity** — Next attack bounces off walls.
- Quirks: Attack chains between enemies; Super is a damage-amplification mark (no direct burst).
*Source: brawlstars.fandom.com/wiki/Belle*

### Berry (Painter) — Support
Lobs an ice cream scoop that splashes on impact and leaves a lingering puddle that damages enemies and heals allies who stand in it.
- HP: 2600 · Speed: 2.40 t/s · Reload: ~2.4s · Ammo: 3
- Attack: 6.33-tile, 1.04-tile splash, 660 dmg, indirect.
- Super: 8.33-tile, 1520 dmg.
- **Super:** Dashes forward in a wild spin, leaving a long trail of ice cream behind him that behaves like his attack puddle.
- **Hypercharge: Double Scoops** — Super dash leaves two parallel ice cream trails.
- Star Powers: **Floor Is Fine** — Reloads faster while standing on his own ice cream puddle. · **Making A Mess** — Attack does bonus impact damage on tiles without existing ice cream.
- Gadgets: **Friendship Is Great** — Knocks back enemies and heals nearby allies. · **Healthy Additives** — Next attack puddle lasts longer.
- Quirks: Same projectile damages enemies and heals allies (puddle field); Super is a damaging/healing dash, not a burst.
*Source: brawlstars.fandom.com/wiki/Berry*

### Bibi (Baseball) — Tank
Swings her baseball bat in a wide arc; charging up a Home Run meter while not attacking lets her next swing knock enemies back several tiles.
- HP: 5000 · Speed: 2.73 t/s · Reload: ~0.8s · Ammo: 3
- Attack: 3.67-tile, 300° cone, 1400 dmg.
- Super: 40.00-tile, 900 dmg, pierces, bounces.
- **Super:** Bats a bouncing bubblegum ball that pierces enemies and bounces off walls for several seconds.
- **Hypercharge: Out of Bounds** — Super gum ball lasts longer and bounces further.
- Star Powers: **Home Run** — Gains movement speed while the Home Run meter is full. · **Batting Stance** — Gains a damage-reduction shield while the Home Run meter is full.
- Gadgets: **Vitamin Booster** — Heals herself over several seconds. · **Extra Sticky** — Next Super slows enemies it hits.
- Quirks: Home Run charge mechanic (stationary buildup); Super pierces and bounces off walls.
*Source: brawlstars.fandom.com/wiki/Bibi*

### Bo (BowDude) — Controller
Fires three explosive arrows in a slight sweeping spread that deal splash damage on impact.
- HP: 3800 · Speed: 2.40 t/s · Reload: ~1.7s · Ammo: 3
- Attack: 8.67-tile, 30° cone, 640 dmg.
- Super: 8.67-tile, 0.84-tile splash, 1440 dmg, indirect.
- **Super:** Lobs an arrow over obstacles that places three proximity mines on the ground that explode on enemy contact.
- **Hypercharge: Catch a Bear** — Super deploys five mines instead of three (stacks with existing mines).
- Star Powers: **Circling Eagle** — Sees into bushes from a much longer distance than normal. · **Snare A Bear** — Mines stun enemies briefly instead of knocking them back.
- Gadgets: **Super Totem** — Places a totem that boosts allies' Super-charge rate. · **Tripwire** — Manually detonates all his placed mines on a short fuse.
- Quirks: Star Power gives expanded bush-vision (key recon role); Super places persistent mines on the map.
*Source: brawlstars.fandom.com/wiki/Bo*

### Bolt (Rock) — Damage Dealer
Rolls into enemies dealing impact damage that scales with his current movement speed; the first target hit takes double damage.
- HP: 5400 · Speed: 1.80 t/s · Reload: ~2.2s · Ammo: 2
- Attack: 0.50-tile splash.
- Super: —.
- **Super:** Enters overdrive mode, gaining a speed boost, damage-reduction shield, and a lightning trail that burns enemies who touch it.
- **Hypercharge:** none.
- Star Powers: **Toss Up** — Knocks enemies upward when he is at top speed. · **Unstoppaball** — Immune to crowd control and gains extra top speed during Super.
- Gadgets: **Oil Change** — Grants a shield scaled by current movement speed. · **Bouncy Ball** — Jumps to a target location, damaging on landing but resetting his speed.
- Quirks: Attack IS the dash (no projectile); Speed scales damage; speed builds up by moving; Super charges while moving (trait).
*Source: brawlstars.fandom.com/wiki/Bolt*

### Bonnie (CannonGirl) — Marksman
In her sniper form, fires a long-ranged Star Launcher shot; in her cannon form (after Super), fires a huge tooth at long range.
- HP: 5000 · Speed: 2.07 t/s · Reload: ~1.0s · Ammo: 1
- Attack: 9.00-tile, 1120 dmg.
- Super: 7.33-tile, 1000 dmg.
- **Super:** Transforms her into Clyde the cannon (or back), launching her a long distance and knocking back enemies on landing.
- **Hypercharge: Daredevil** — Super fires teeth in all directions on takeoff and landing while stunning nearby enemies.
- Star Powers: **Black Powder** — Increases the range of her cannon form's Super relaunch. · **Wisdom Tooth** — Cannon-form attack splits into smaller projectiles on hit.
- Gadgets: **Sugar Rush** — Boosts movement and reload speed while in cannon form. · **Crash Test** — Dashes forward, knocking back enemies in her path.
- Quirks: Alt-form Brawler: sniper form + cannon form with different attacks/supers; Super is a long re-positioning launch.
*Source: brawlstars.fandom.com/wiki/Bonnie*

### Brock (RocketGirl) — Marksman
Fires a long-ranged rocket that explodes on impact, dealing splash damage in a small radius.
- HP: 3000 · Speed: 2.40 t/s · Reload: ~2.1s · Ammo: 3
- Attack: 9.00-tile, 1160 dmg.
- Super: 8.33-tile, 160° cone, 0.94-tile splash, 1040 dmg, indirect.
- **Super:** Rocket Rain — fires a barrage of rockets in a fan that destroys obstacles and deals heavy area damage.
- **Hypercharge: Rocket Barrage** — Super fires four waves of seven rockets each.
- Star Powers: **More Rockets** — Super fires additional rockets. · **Rocket No. 4** — Adds a fourth ammo slot, increasing his ammo capacity.
- Gadgets: **Rocket Laces** — Blasts the ground, jumping into the air and damaging nearby enemies. · **Rocket Fuel** — Next rocket is bigger, faster, and destroys walls.
- Quirks: Attack deals splash on impact (not just direct hit).
*Source: brawlstars.fandom.com/wiki/Brock*

### Bull (BullDude) — Tank
Fires two waves of close-range shotgun shells from his dual barrels, dealing massive damage at point-blank.
- HP: 5000 · Speed: 2.57 t/s · Reload: ~1.6s · Ammo: 3
- Attack: 5.33-tile, 90° cone, 440 dmg/pellet × 5 = 2200 max.
- Super: 11.00-tile, 1000 dmg.
- **Super:** Charges in a straight line, damaging enemies and destroying obstacles in his path; two charges can be queued.
- **Hypercharge: Jaws of Steel** — Gains a damage-reduction shield while his Super is active.
- Star Powers: **Berserker** — Doubles reload speed when his health drops below a threshold. · **Tough Guy** — Grants a damage-reduction shield when his health drops below a threshold.
- Gadgets: **T-Bone Missile** — Throws a long-ranged projectile that heals him on hit. · **Stomper** — Slows nearby enemies; stuns enemies already slowed.
- Quirks: Super is a charging dash (destroys walls); Two stockable Super charges.
*Source: brawlstars.fandom.com/wiki/Bull*

### Buster (ShieldTank) — Tank
Projects a light wave in a wide cone, dealing more damage to enemies closer to him; the wave pierces multiple targets.
- HP: 5000 · Speed: 2.57 t/s · Reload: ~1.8s · Ammo: 3
- Attack: 5.33-tile, 90° cone, 1380 dmg/pellet × 3 = 4140 max, pierces.
- Super: 3.00-tile, 120° cone, 800 dmg.
- **Super:** Deploys a barrier in front of him that blocks projectiles and reflects them back as a damaging counterattack.
- **Hypercharge: Plot Armor** — Super becomes a full 360-degree barrier reflecting projectiles from all directions.
- Star Powers: **Blockbuster** — Attack damage increases per ally in his Super charging area. · **Kevlar Vest** — Reduces damage and grants crowd-control immunity while Super is active.
- Gadgets: **Utility Belt** — Heals himself and nearby allies (scales with ally count). · **Slo-Mo Replay** — Next attack pulls enemies toward him.
- Quirks: Super is a projectile-blocking shield wall; Attack pierces multiple targets; Charges Super faster while allies are near him.
*Source: brawlstars.fandom.com/wiki/Buster*

### Buzz (RopeDude) — Assassin
Whips out a quick spread of piercing sound waves from his whistle in a short cone.
- HP: 5000 · Speed: 2.57 t/s · Reload: ~1.0s · Ammo: 3
- Attack: 2.67-tile, 165° cone, 420 dmg/pellet × 3 = 1260 max, pierces.
- Super: 10.00-tile.
- **Super:** Throws a grappling buoy; on hitting a wall or enemy, he is pulled to it and stuns nearby enemies on arrival (stun duration scales with travel distance).
- **Hypercharge: Buzzwatch** — Super instantly recharges when Buzz grapples to a wall.
- Star Powers: **Tougher Torpedo** — Doubles the minimum stun duration of his Super. · **Eyes Sharp** — Increases his Super charging trait area.
- Gadgets: **Reserve Buoy** — Instantly charges his Super (but it won't stun on hit). · **X-Ray-Shades** — Reveals enemies in bushes within his Super-charging trait area.
- Quirks: Super charges passively when enemies enter his trait radius; Grapple-to-wall mobility; Attack pierces multiple targets.
*Source: brawlstars.fandom.com/wiki/Buzz*

### Buzz Lightyear — Damage Dealer (Time-Limited Disney Collab)
_CSV mechanics N/A — kit description from wiki only._
Has three modes — Laser Mode shoots damage-over-time laser blasts; Saber Mode swings a close-range arc; Wing Mode fires twin lasers that hit harder up close.
- **Super:** Mode-dependent — Laser fires a sweeping spread of lasers; Saber jumps over walls and area-damages on landing; Wing flies above the ground dropping bombs.
- **Hypercharge: Bravado** — Stat buffs only (damage / speed / shield) for the active mode; no Super change.
- Star Powers: **(no star powers)** — Buzz Lightyear ships without star powers.
- Gadgets: **Turbo Boosters** — Dashes a short distance forward.
- Quirks: Three switchable modes (Laser / Saber / Wing) with totally different attacks and supers; No star powers; Time-limited brawler (Brawlidays 2024 / Pizza Planet event) — removed from the game.
*Source: brawlstars.fandom.com/wiki/Buzz_Lightyear*

### Byron (SnakeOil) — Support
Fires a very long-ranged dart that damages enemies over time and heals allies over time.
- HP: 2600 · Speed: 2.40 t/s · Reload: ~1.4s · Ammo: 3
- Attack: 10.00-tile.
- Super: 7.33-tile, 1.67-tile splash, 1500 dmg, indirect.
- **Super:** Lobs a vial that splashes on impact, damaging all enemies and healing all allies in its splash radius over time.
- **Hypercharge: Unstable Concoction** — Super additionally fires six radial darts outward from the impact point.
- Star Powers: **Malaise** — Enemies hit by his Super receive reduced healing from any source for a duration. · **Injection** — Periodically, his next attack pierces through targets.
- Gadgets: **Shot In The Arm** — Consumes one ammo to heal himself over time. · **Booster Shots** — Next attack fires three darts (each deals less damage/healing).
- Quirks: Same projectile damages enemies AND heals allies; Very long range, dual-target healer/sniper.
*Source: brawlstars.fandom.com/wiki/Byron*

### Carl (Whirlwind) — Damage Dealer
Throws his pickaxe in a straight line; it returns to him like a boomerang and only reloads once retrieved.
- HP: 4200 · Speed: 2.40 t/s · Reload: ~2.0s · Ammo: 1
- Attack: 8.33-tile, 740 dmg, pierces.
- Super: 2.33-tile splash, 500 dmg.
- **Super:** Tailspin — spins around at greatly increased movement speed, damaging enemies he touches repeatedly.
- **Hypercharge: Flamespin** — Super leaves a trail of hot rocks behind him that ignite enemies.
- Star Powers: **Power Throw** — Pickaxe travels and returns faster, effectively reducing reload time. · **Protective Pirouette** — Damage taken during Super is reduced.
- Gadgets: **Heat Ejector** — Next pickaxe leaves a trail of burning rocks behind it. · **Flying Hook** — Next pickaxe pulls Carl to the farthest point of its range.
- Quirks: Boomerang attack — must wait for return to reload; Super is a self-AoE spin, not a projectile; Attack pierces multiple targets.
*Source: brawlstars.fandom.com/wiki/Carl*

### Charlie (Cocooner) — Controller
Slings her yo-yo forward; it damages enemies on its outward trip and on its return, reloading her single ammo only after returning.
- HP: 3700 · Speed: 2.40 t/s · Reload: ~2.0s · Ammo: 1
- Attack: 9.00-tile, 800 dmg.
- Super: 9.00-tile.
- **Super:** Fires a hair bundle that traps an enemy in a cocoon, immobilizing them for several seconds (cocoon has its own HP).
- **Hypercharge: Pestilence** — Super spawns three additional spiders around the cocoon.
- Star Powers: **Digestive** — Cocooned enemies lose health over time while cocooned. · **Slimy** — Super leaves a slowing slime trail.
- Gadgets: **Spiders** — Summons three spiders that chase down nearby enemies. · **Personal Space** — Cocoons herself, healing for a percentage of max health.
- Quirks: Yo-yo attack hits on both outbound and return; single-ammo design; Super is a hard CC (cocoon).
*Source: brawlstars.fandom.com/wiki/Charlie*

### Chester (Jester) — Damage Dealer
Cycles through a four-step bell sequence — first attack fires 1 bell, then 2, then 3, then 4 bells in widening spreads.
- HP: 3800 · Speed: 2.57 t/s · Reload: ~1.9s · Ammo: 3
- Attack: 8.33-tile, 30° cone, 670 dmg/pellet × 4 = 2680 max.
- Super: 6.33-tile, 0.00-tile splash, 1880 dmg, indirect.
- **Super:** Randomly picks one of five Supers — damaging shockwave, stunning candy boxer, salt cloud DoT, slow zone, or large self-heal.
- **Hypercharge: Crunchy Chewy Gooey** — Combines three Supers into one — high-damage shot, salt cloud DoT, and slow.
- Star Powers: **Single Bellomania** — First bell in the attack sequence does increased damage. · **Sneak Peek** — Reveals which Super he will get next before charging.
- Gadgets: **Spicy Dice** — Re-rolls his current Super to a different random one. · **Candy Beans** — Eats a random candy granting a random buff (speed/reload/damage/heal).
- Quirks: Attack damage scales through a fixed 4-stage sequence; Random Super — five possible effects.
*Source: brawlstars.fandom.com/wiki/Chester*

### Chuck (Conductor) — Damage Dealer
Fires three clouds of steam in a slight cone that deal more damage at close range and pierce enemies.
- HP: 4700 · Speed: 2.57 t/s · Reload: ~2.0s · Ammo: 3
- Attack: 6.67-tile, 30° cone, 540 dmg, pierces.
- Super: 10.00-tile, 0.42-tile splash, 400 dmg, indirect.
- **Super:** Places a Post on the ground; if a Post already exists nearby, he dashes between Posts damaging and knocking back enemies in his path.
- **Hypercharge: Full Steam Ahead** — Next dash has unlimited range and trails clouds of steam that damage enemies behind him.
- Star Powers: **Pit Stop** — Increases maximum number of active Posts. · **Tickets Please** — Next dash removes ammo from any enemy it hits and refunds it to Chuck.
- Gadgets: **Rerouting** — Removes the nearest Post and recharges his Super. · **Ghost Train** — Next dash passes through obstacles.
- Quirks: Super is a dash between placed Posts (rail mechanic); Attack projectile pierces.
*Source: brawlstars.fandom.com/wiki/Chuck*

### Clancy (Crab) — Damage Dealer
Power Wash — has three stages that upgrade automatically as he gains tokens by hitting enemies; Stage 1 fires one paintball, Stage 2 fires two, Stage 3 adds two diagonals.
- HP: 3800 · Speed: 2.40 t/s · Reload: ~2.0s · Ammo: 3
- Attack: 7.67-tile, 700 dmg.
- Super: 5.67-tile, 220° cone, 600 dmg × 2.
- **Super:** Fires a barrage of projectiles in a fan whose range and damage scale with his current Stage.
- **Hypercharge: Recall of Duty** — Super paintballs return to him after firing, dealing damage again on the way back.
- Star Powers: **Recon** — Starts the match with 2 tokens already accumulated. · **Pumping Up** — Fully reloads all ammo on every enemy Brawler defeat.
- Gadgets: **Snappy Shooting** — Doubles token-gain rate for a short duration. · **Tactical Retreat** — Dashes backward and reloads ammo.
- Quirks: Token-stage progression — attack and Super grow stronger over the match; Tokens earned by hitting enemies.
*Source: brawlstars.fandom.com/wiki/Clancy*

### Colette (Percenter) — Damage Dealer
Fires a long-ranged bowtie that deals a percentage of the enemy's current HP rather than flat damage.
- HP: 3600 · Speed: 2.40 t/s · Reload: ~1.6s · Ammo: 3
- Attack: 8.67-tile, 1100 dmg.
- Super: 11.00-tile, 2200 dmg.
- **Super:** Charges forward then dashes back, damaging all enemies in her path based on their maximum HP.
- **Hypercharge: Teen Spirit** — Summons a smaller spirit that follows her Super, dealing extra damage in its path.
- Star Powers: **Push It** — Enemies hit by her Super are dragged to the far end and stunned briefly. · **Mass Tax** — Reduces damage taken during Super and grants a shield on hit.
- Gadgets: **Na-Ah** — Briefly charms an enemy Brawler (loses control). · **Gotcha** — Attack heals her by a percentage of damage dealt for several shots.
- Quirks: Percent-health damage on both attack and Super (counters tanks); Super is a dash that goes forward AND back.
*Source: brawlstars.fandom.com/wiki/Colette*

### Colt (Gunslinger) — Damage Dealer
Rapidly fires six straight long-ranged bullets from his dual revolvers in a single burst.
- HP: 3100 · Speed: 2.40 t/s · Reload: ~1.3s · Ammo: 3
- Attack: 9.00-tile, 360 dmg.
- Super: 11.00-tile, 320 dmg, pierces.
- **Super:** Bullet Storm — fires a much longer and more powerful stream of bullets that destroys walls and pierces enemies.
- **Hypercharge: Dual Wielding** — Super width is greatly increased.
- Star Powers: **Slick Boots** — Increases his movement speed. · **Magnum Special** — Increases attack range and bullet speed.
- Gadgets: **Speedloader** — Fires two quick slowing shots. · **Silver Bullet** — Next shot destroys walls and pierces Brawlers.
- Quirks: Attack is a multi-bullet burst (each pellet rolls independently); Super pierces multiple targets.
*Source: brawlstars.fandom.com/wiki/Colt*

### Cordelius (Duelist) — Assassin
Fires two medium-range mushroom projectiles from his garden tool.
- HP: 3500 · Speed: 2.73 t/s · Reload: ~1.2s · Ammo: 3
- Attack: 5.33-tile, 800 dmg.
- Super: 9.00-tile.
- **Super:** Shoots a large mushroom that, on hitting an enemy, transports both Cordelius and the target to the Shadow Realm — a 1v1 isolated arena.
- **Hypercharge: Complete Darkness** — Slows enemies inside the Shadow Realm.
- Star Powers: **Comboshrooms** — Hitting the same target with the second mushroom of an attack deals bonus damage. · **Mushroom Kingdom** — Spawns mushrooms in the Shadow Realm that heal allies / damage enemies.
- Gadgets: **Replanting** — Jumps over terrain quickly. · **Poison Mushroom** — Next attack prevents the enemy from attacking for several seconds.
- Quirks: Super sends target + caster to an isolated Shadow Realm (no Super/Gadget/Hyper inside).
*Source: brawlstars.fandom.com/wiki/Cordelius*

### Crow (Crow) — Assassin
Throws three long-ranged daggers in a tight cone that apply poison-DoT and reduce healing.
- HP: 3000 · Speed: 2.73 t/s · Reload: ~1.4s · Ammo: 3
- Attack: 8.67-tile, 45° cone, 320 dmg/pellet × 3 = 960 max.
- Super: 320 dmg.
- **Super:** Leaps a long distance, throwing poisoned daggers in all directions on takeoff and landing.
- **Hypercharge: Utility Knives** — Super daggers return to him after the leap, dealing damage on the way back.
- Star Powers: **Extra Toxic** — Poisoned enemies deal reduced damage. · **Carrion Crow** — Deals bonus damage to enemies below a health threshold.
- Gadgets: **Instapoison** — Instantly applies all remaining poison damage to poisoned enemies; gains a small shield. · **Slowing Toxin** — Throws a kunai that slows, damages, and poisons the first enemy hit.
- Quirks: Attacks apply healing-reduction debuff (anti-healer); Super is a long mobility leap that doubles as damage.
*Source: brawlstars.fandom.com/wiki/Crow*

### Damian — Tank
_CSV mechanics N/A — kit description from wiki only._
Power Trio — first two attacks are piercing punches, the third is an explosive kick that marks enemies and sets them on fire.
- **Super:** Mosh Pit — leaps a long distance and creates a mosh-pit zone on landing that knocks enemies into speakers for repeated damage.
- **Hypercharge: Jump in the Fire** — Super sets the ground on fire on landing, burning enemies who walk on it.
- Star Powers: **Crowdkill** — Knocking an enemy into a wall stuns them briefly. · **Vulgar Display Of Punch** — Fist is flaming during Super, burning enemies hit.
- Gadgets: **Spiritual Healing** — Throws a mic; first ally to pick it up is healed. · **Wall Of Sound** — Summons a wall of indestructible amps for a short duration.
- Quirks: Attack rotates through a 3-hit combo (piercing punches then explosive kick); Super traps enemies in a mosh pit that bounces them off walls.
*Source: brawlstars.fandom.com/wiki/Damian*

### Darryl (BarrelBot) — Tank
Fires two waves of ten close-range shotgun shells from dual barrels, dealing massive damage at point-blank.
- HP: 5500 · Speed: 2.57 t/s · Reload: ~1.8s · Ammo: 3
- Attack: 6.00-tile, 80° cone, 240 dmg/pellet × 5 = 1200 max.
- Super: 7.00-tile, 650 dmg.
- **Super:** Barrel Roll — rolls a long distance damaging enemies and bouncing off walls; gains a damage-reduction shield while rolling. Two charges available.
- **Hypercharge: Barrel o' Bullets** — Super additionally fires pellets in all directions around him while rolling.
- Star Powers: **Steel Hoops** — Damage taken is reduced for a short window after Super ends. · **Rolling Reload** — Doubles reload speed for a few seconds after using Super.
- Gadgets: **Recoiling Rotator** — Spins in place spraying pellets in all directions. · **Tar Barrel** — Creates a slowing tar puddle around himself.
- Quirks: Super auto-charges over time (trait); Two stockable Super charges; Super bounces off walls.
*Source: brawlstars.fandom.com/wiki/Darryl*

### Doug (Reviver) — Support
Splashes the ground around him, damaging enemies and healing allies in a self-centered radius.
- HP: 5200 · Speed: 2.57 t/s · Reload: ~1.5s · Ammo: 3
- Attack: 2.08-tile splash, 1200 dmg.
- Super: 9.33-tile.
- **Super:** Plants a hot dog at his location; if an ally is defeated within range of it, they respawn at the hot dog instead of base.
- **Hypercharge: Free Toppings** — Super hot dog now makes allies mirror Doug's attacks.
- Star Powers: **Fast Food** — Heals to full health when reviving an ally. · **Self Service** — Heals himself when he attacks.
- Gadgets: **Double Sausage** — Next attack only heals (no damage), but heals double. · **Extra Mustard** — Next attack only damages (no heal), but deals double damage.
- Quirks: Super grants ally REVIVE — unique mechanic; Attack heals allies AND damages enemies in same swing; Super charges by healing (trait).
*Source: brawlstars.fandom.com/wiki/Doug*

### Draco (DragonRider) — Tank
Thrusts his lance forward, piercing enemies and dealing more damage at maximum range.
- HP: 5600 · Speed: 2.40 t/s · Reload: ~1.0s · Ammo: 3
- Attack: 4.00-tile, 700 dmg, pierces.
- Super: —.
- **Super:** Mounts his dragon, transforming into an alternate form with new attacks; stays mounted until defeated.
- **Hypercharge: Fire and Flames** — Dragon-form attack has more range and ignites a wider area.
- Star Powers: **Expose** — Periodically, next lance stab marks enemies, amplifying damage they take. · **Shredding** — Heals on activating Super.
- Gadgets: **Upper Cut** — Next lance throws enemies into the air briefly. · **Last Stand** — Cannot fall below 1 HP for a short window.
- Quirks: Alt-form Brawler: foot soldier + dragon-mounted; Damage increases with range (inverse falloff); Super charges from damage taken (trait).
*Source: brawlstars.fandom.com/wiki/Draco*

### Dynamike (TntDude) — Artillery
Lobs two sticks of dynamite over walls that explode in a medium radius, dealing high damage.
- HP: 3000 · Speed: 2.57 t/s · Reload: ~1.6s · Ammo: 3
- Attack: 7.33-tile, 1.67-tile splash, 800 dmg/pellet × 2 = 1600 max, bounces, indirect.
- Super: 7.33-tile, 1.67-tile splash, 2200 dmg, bounces, indirect.
- **Super:** Throws a large TNT barrel that explodes in a large radius, destroying obstacles and knocking enemies back.
- **Hypercharge: Boomer** — Super spawns eight smaller bombs around the main explosion.
- Star Powers: **Dyna-Jump** — Can ride the blast of his own dynamite to jump over obstacles. · **Demolition** — Increases Super damage substantially.
- Gadgets: **Fidget Spinner** — Spins with a speed boost while throwing dynamite in a ring around himself. · **Satchel Charge** — Next attack stuns enemies briefly.
- Quirks: Attacks lob over walls; Star Power enables a self-launch jump (Dyna-Jump); Attack/Super projectiles bounce off walls.
*Source: brawlstars.fandom.com/wiki/Dynamike*

### Edgar (Enrager) — Assassin
Two short, fast piercing punches that heal Edgar for a portion of damage dealt.
- HP: 3700 · Speed: 2.73 t/s · Reload: ~0.7s · Ammo: 3
- Attack: 2.00-tile, 540 dmg, pierces.
- Super: 6.67-tile.
- **Super:** Vault — leaps a long distance over walls toward a target location, gaining a temporary speed boost on landing.
- **Hypercharge: Outburst** — After using Super, his Super-charge rate and reload speed are significantly increased.
- Star Powers: **Hard Landing** — Super deals area damage on landing. · **Fisticuffs** — Receives more healing from the damage he deals.
- Gadgets: **Lets Fly** — Throws a scarf that pulls him to the nearest Brawler or wall. · **Hardcore** — Grants a decaying shield.
- Quirks: Heals on every attack hit (life-steal); Super auto-charges over time (trait); Attack pierces multiple targets.
*Source: brawlstars.fandom.com/wiki/Edgar*

### El Primo (Luchador) — Tank
Throws four close-range flurry of punches.
- HP: 6500 · Speed: 2.57 t/s · Reload: ~0.8s · Ammo: 3
- Attack: 3.00-tile, 380 dmg, pierces.
- Super: 9.00-tile, 960 dmg.
- **Super:** Flying Elbow Drop — leaps to a target area, dealing damage and knockback on landing, destroying walls.
- **Hypercharge: Gravity Leap** — Super pulls enemies hit toward him and reveals bushes/invisible enemies in landing zone.
- Star Powers: **El Fuego** — Enemies caught by Super burn for damage over time. · **Meteor Rush** — Gains a speed boost after using Super.
- Gadgets: **Suplex Supplement** — Grabs the closest enemy and flips them over his shoulders. · **Asteroid Belt** — Summons a meteor on the nearest enemy that damages and destroys walls.
- Quirks: Super is a long jump (wall-skipping mobility); Second-highest HP in the game; Super charges from damage taken (trait); Attack pierces multiple targets.
*Source: brawlstars.fandom.com/wiki/El_Primo*

### Emz (Mummy) — Controller
Sprays hairspray in a wide cone that deals damage over time; the center stream deals the most damage.
- HP: 3900 · Speed: 2.40 t/s · Reload: ~2.0s · Ammo: 3
- Attack: 6.67-tile, 80° cone, 560 dmg/pellet × 5 = 2800 max, pierces.
- Super: 240 dmg.
- **Super:** Releases a large damaging cloud in a self-centered radius that slows enemies and damages them over time.
- **Hypercharge: Overhyped Haze** — Super pushes nearby enemies away from her and sends a wave of spray around her.
- Star Powers: **Bad Karma** — Each tick of attack damage on the same target increases. · **Hype** — Heals over time while enemies are inside her Super cloud.
- Gadgets: **Friendzoner** — Pushes enemies back with a hairspray blast. · **Acid Spray** — Next attack passes through walls.
- Quirks: Attack is a damage-over-time spray (not a single hit); Attack projectile pierces.
*Source: brawlstars.fandom.com/wiki/Emz*

### Eve (Flea) — Damage Dealer
Fires three eggs of increasing size at long range; the largest egg deals the most damage.
- HP: 3100 · Speed: 2.40 t/s · Reload: ~1.6s · Ammo: 3
- Attack: 9.33-tile, 400 dmg.
- Super: 5.00-tile, 0.00-tile splash, indirect.
- **Super:** Drops a nest egg that hatches into three hatchlings; hatchlings chase down and poison the nearest enemies.
- **Hypercharge: Generations** — Nest egg spawns a hatchling every second while it remains alive (plus the original brood).
- Star Powers: **Unnatural Order** — Reverses attack order — largest egg fires first. · **Happy Surprise** — Periodically the biggest egg spawns a hatchling on hit.
- Gadgets: **Gotta Go** — Jumps away, leaving a hatchling behind. · **Motherly Love** — Next Super's hatchlings heal allies instead of damaging enemies.
- Quirks: Three-shot ramping damage attack; Super spawns persistent spawnable units (hatchlings).
*Source: brawlstars.fandom.com/wiki/Eve*

### Fang (KickerDude) — Assassin
Kicks his shoe forward; if it doesn't hit an enemy at close range, it travels a longer distance dealing less damage.
- HP: 4800 · Speed: 2.57 t/s · Reload: ~1.0s · Ammo: 3
- Attack: 2.67-tile, 1360 dmg.
- Super: 10.00-tile, 1500 dmg.
- **Super:** Sneak Ahead — flying kick that bounces between up to four enemies in range, dealing damage to each.
- **Hypercharge: Dragon Kick** — Super passes through walls and drops popcorn pieces along the way.
- Star Powers: **Fresh Kicks** — Instantly recharges Super if it kills an enemy. · **Divine Soles** — Periodically reduces damage from the next enemy hit.
- Gadgets: **Corn-Fu** — Throws popcorn around him that pops with damage on contact. · **Roundhouse Kick** — Spins, stunning nearby enemies briefly.
- Quirks: Attack range adapts: short range high damage, long range lower damage; Super chains between multiple enemies (kill chain).
*Source: brawlstars.fandom.com/wiki/Fang*

### Finx (Chronomancer) — Controller
Fires three parallel long-ranged projectiles — center deals more damage than the side projectiles.
- HP: 3700 · Speed: 2.57 t/s · Reload: ~1.3s · Ammo: 3
- Attack: 8.33-tile, 900 dmg/pellet × 3 = 2700 max.
- Super: 7.33-tile, 0.63-tile splash, indirect.
- **Super:** Time Warp — places a zone that speeds up Finx's and allies' projectiles inside it and slows enemies' projectiles.
- **Hypercharge: Temporal Traveling** — Spawns a second Time Warp zone that follows Finx around.
- Star Powers: **Hieroglyph Halt** — Enemies hit by attack have reduced reload speed. · **Primer** — Hits with speed-boosted projectiles extend Super duration.
- Gadgets: **Back To The Finxture** — Marks his current position; teleports back there a few seconds later with the ammo he had then. · **No Escape** — Next attack freezes enemies — they can't act but are also damage-immune.
- Quirks: Super alters projectile speeds (zone affects both teams asymmetrically); Gadget rewinds him to past position + state.
*Source: brawlstars.fandom.com/wiki/Finx*

### Frank (HammerDude) — Tank
Swings his hammer with a wind-up delay (delay shrinks as HP drops), sending a piercing shockwave.
- HP: 6800 · Speed: 2.57 t/s · Reload: ~0.8s · Ammo: 3
- Attack: 6.00-tile, 130° cone, 1160 dmg/pellet × 4 = 4640 max, pierces.
- Super: 7.00-tile, 130° cone, 1240 dmg × 4, pierces.
- **Super:** Larger, longer-ranged shockwave that destroys obstacles and stuns enemies it hits — with a longer wind-up.
- **Hypercharge: Seismic Smash** — Super hits all enemies in a circular area around him instead of in a line.
- Star Powers: **Power Grab** — Defeating an enemy temporarily boosts his damage. · **Sponge** — Permanently increases maximum health.
- Gadgets: **Active Noise Canceling** — Becomes immune to stuns/slows/knockbacks; fires a damaging soundwave. · **Irresistible Attraction** — Long-range attack that pulls enemies toward him.
- Quirks: Attack has a wind-up delay (telegraphed); Wind-up shrinks at lower HP (rewards aggressive play); Super charges from damage taken (trait); Attack pierces multiple targets.
*Source: brawlstars.fandom.com/wiki/Frank*

### Gale (Blower) — Controller
Long-ranged waves of damaging snowballs in a slight spread.
- HP: 4000 · Speed: 2.40 t/s · Reload: ~1.2s · Ammo: 3
- Attack: 8.33-tile, 300 dmg/pellet × 6 = 1800 max.
- Super: 10.00-tile, 600 dmg × 4, pierces.
- **Super:** Polar Vortex — wide gust of wind that knocks all enemies back significantly.
- **Hypercharge: Blizzard** — Super width is increased and a second gust of wind/snow is added.
- Star Powers: **Blustery Blow** — Super stuns enemies briefly if they are pushed into a wall. · **Freezing Snow** — Attack snowballs slow enemies on hit.
- Gadgets: **Spring Ejector** — Drops a bounce pad that launches anyone (friend or foe) who steps on it. · **Twister** — Creates a tornado wall that enemies cannot pass through.
- Quirks: Super is a long-range knockback (positional control, not damage burst); Super projectile pierces.
*Source: brawlstars.fandom.com/wiki/Gale*

### Gene (HookDude) — Controller
Smoke ball that travels forward and splits into a fan after a fixed range.
- HP: 3800 · Speed: 2.40 t/s · Reload: ~2.0s · Ammo: 3
- Attack: 5.67-tile, 1000 dmg.
- Super: 7.67-tile.
- **Super:** Magic Hand — extends a giant hand that grabs the first enemy hit and pulls them back to Gene's position.
- **Hypercharge: Hyper Hands** — Super now fires three hands simultaneously.
- Star Powers: **Magic Puffs** — Heals all friendly Brawlers around him over time. · **Spirit Slap** — Magic Hand deals damage on hit (not just pull).
- Gadgets: **Lamp Blowout** — Pushes all nearby enemies back and heals himself slightly. · **Vengeful Spirits** — Fires homing missiles at all visible enemies.
- Quirks: Attack splits into multiple projectiles after a range threshold; Super is a single-target hard CC (pull).
*Source: brawlstars.fandom.com/wiki/Gene*

### Gigi (Daredevil) — Damage Dealer
Briefly sent into a continuous spin, gaining speed and damaging enemies she gets close to.
- HP: 4100 · Speed: 2.73 t/s · Reload: ~0.2s · Ammo: 10
- Attack: 1.46-tile splash, 600 dmg.
- Super: 7.33-tile, 1.46-tile splash, 1300 dmg.
- **Super:** Teleports to a target after a short delay, dealing damage to enemies when she returns to her original position.
- **Hypercharge: Shadow Puppet Reveal** — Hypercharged Super deals instant damage on teleport landing.
- Star Powers: **Plie Protection** — Super-charge rate increases when she avoids damage for a few seconds. · **A Helping Hand** — Super heals her after the charge-up window.
- Gadgets: **Longer Strings** — Increases her Super-charging trait area. · **Disappearing Act** — Creates an invisibility tent for herself and allies inside it.
- Quirks: Attack IS a spin self-AoE (no projectile); Super is a delayed teleport-and-return; Super charges passively from enemy projectiles near her (trait).
*Source: brawlstars.fandom.com/wiki/Gigi*

### Glowy — Support
_CSV mechanics N/A — kit description from wiki only._
Fires a glow beam that creates a tether — damaging enemies it sticks to and healing allies it sticks to; one of each can be active.
- **Super:** Creep from the Deep — wide cone fear effect that briefly causes enemies to flee and disables their attacks.
- **Hypercharge:** none.
- Star Powers: **Biotic Ecosystem** — While tethered to an enemy AND ally simultaneously, enemy damage drops and ally damage increases. · **Parasitism** — Tethering to an enemy heals Glowy for a portion of damage dealt.
- Gadgets: **Slippery Savior** — Dashes in a direction, healing himself and nearby allies on arrival. · **More Lumens** — Temporarily doubles tether damage / healing rate.
- Quirks: Tether mechanic — one ally + one enemy linked simultaneously; Super is a fear effect (unique CC: enemies run away).
*Source: brawlstars.fandom.com/wiki/Glowy*

### Gray (DoorMan) — Support
Long-ranged finger-pistol shot.
- HP: 3400 · Speed: 2.40 t/s · Reload: ~1.4s · Ammo: 3
- Attack: 9.00-tile, 1160 dmg.
- Super: —.
- **Super:** Dimensional Doors — places two portals; any ally (or himself) who steps on one teleports to the other after a brief delay.
- **Hypercharge: Another Dimension** — Whoever uses his teleporters gains a shield; second portal pair can co-exist with the first.
- Star Powers: **Fake Injury** — When at full HP, the next damage taken is reduced. · **New Perspective** — Allies who use his portals heal a percentage of max HP.
- Gadgets: **Walking Cane** — Next attack pulls enemy back slightly. · **Grand Piano** — Drops a piano on the attack target's location, destroying walls and knocking back.
- Quirks: Super is a TEAM teleporter — works for any ally, not just himself.
*Source: brawlstars.fandom.com/wiki/Gray*

### Griff (AssaultShotgun) — Damage Dealer
Fires three waves of three coins each in a wide cone.
- HP: 3700 · Speed: 2.40 t/s · Reload: ~1.6s · Ammo: 3
- Attack: 8.33-tile, 30° cone, 280 dmg/pellet × 3 = 840 max.
- Super: 9.00-tile, 150° cone, 720 dmg × 5, pierces.
- **Super:** Throws five banknotes that travel forward and return; they deal more damage the further they fly.
- **Hypercharge: Tax Rebate** — Super passes through walls and pierces; a second wave of bills returns after a delay.
- Star Powers: **Keep The Change** — Attack gets a fourth wave of coins and slightly wider spread. · **Business Resilience** — Periodically heals a portion of missing HP.
- Gadgets: **Piggy Bank** — Throws a piggy bank that explodes after a delay, destroying obstacles. · **Coin Shower** — Showers coins on a target area dealing damage over time.
- Quirks: Coin-toss attack — 3×3 cone pattern (curtain of damage); Super projectile pierces and damages on outbound + return.
*Source: brawlstars.fandom.com/wiki/Griff*

### Grom (CrossBomber) — Artillery
Throws his walkie-talkie over walls that explodes in a cross-pattern blast on contact.
- HP: 3000 · Speed: 2.40 t/s · Reload: ~2.0s · Ammo: 3
- Attack: 7.67-tile, 6.25-tile splash, 1030 dmg, indirect.
- Super: 8.33-tile, 6.25-tile splash, 1600 dmg, indirect.
- **Super:** Larger TNT-style explosive that bursts into four projectiles in a cross pattern, destroying obstacles and knocking back.
- **Hypercharge: Grom Bomb Goes Boom!** — Super bounces in place then explodes again into another cross pattern.
- Star Powers: **Foot Patrol** — Gains movement speed while Super is charged. · **X-Factor** — Cross-split projectiles deal more damage at longer travel distances.
- Gadgets: **Watchtower** — Drops a watchtower that grants bush-vision to nearby allies. · **Radio Check** — Next attack throws three walkie-talkies in succession.
- Quirks: Cross-pattern explosion (not radial); Lobs over walls.
*Source: brawlstars.fandom.com/wiki/Grom*

### Gus (SoulCollector) — Support
Throws a long-ranged balloon; a charge bar fills as he hits enemies, and a full bar makes his next attack spawn a healing spirit.
- HP: 3300 · Speed: 2.40 t/s · Reload: ~1.5s · Ammo: 3
- Attack: 9.33-tile, 1080 dmg.
- Super: 9.33-tile.
- **Super:** Grants himself or a teammate a decaying shield while pushing all nearby enemies back.
- **Hypercharge: Spooky Pop** — Super shoots spirits in all directions when self-targeted, or spirals around allies when targeted on them.
- Star Powers: **Health Bonanza** — Doubles healing from his spawned spirits. · **Spirit Animal** — Recipient of his Super temporarily gains a damage boost.
- Gadgets: **Kooky Popper** — Detonates all active spirits, damaging nearby enemies. · **Soul Switcher** — Trades current HP for instant Super-bar progress.
- Quirks: Attack charge meter spawns persistent pickup spirits (heal pads); Super grants ally shields with knockback utility.
*Source: brawlstars.fandom.com/wiki/Gus*

### Hank — Tank
_CSV mechanics N/A — kit description from wiki only._
Inflates a water balloon that grows in size and damage while held; releases as a single large area-of-effect explosion.
- **Super:** Fires torpedoes in all directions while healing a portion of missing HP.
- **Hypercharge: Homing Fish-iles** — Super torpedoes home in on nearby enemies.
- Star Powers: **Its Gonna Blow** — Gains movement speed while balloon is heavily charged. · **Take Cover** — Reduces damage taken while standing near a wall.
- Gadgets: **Water Balloons** — Next attack slows enemies on hit. · **Barricade** — Temporarily reduces damage taken.
- Quirks: Attack charges while held (variable range and damage); Super heals + 360-degree torpedo barrage; Super charges from damage taken (trait).
*Source: brawlstars.fandom.com/wiki/Hank*

### Jacky (Driller) — Tank
Smashes the ground with her jackhammer, damaging all enemies in a self-centered radius (no aim required).
- HP: 5000 · Speed: 2.57 t/s · Reload: ~1.8s · Ammo: 3
- Attack: 2.08-tile splash.
- Super: —.
- **Super:** Holey Moley — burrows underground and pulls all enemies in a radius toward her location, briefly preventing them from acting.
- **Hypercharge: Seismic Event** — Enemies hit by her Super are slowed.
- Star Powers: **Counter Crush** — Converts a portion of incoming damage into a Groundbreaker counterattack. · **Hardy Hard Hat** — Permanently reduces all damage taken.
- Gadgets: **Pneumatic Booster** — Briefly moves faster. · **Rebuild** — Reconstructs walls/bushes in a small radius around her.
- Quirks: Attack is a self-centered AoE (no projectile); Super is a pull (hard CC); Gadget can rebuild destroyed walls — unique terrain interaction.
*Source: brawlstars.fandom.com/wiki/Jacky*

### Jae-Yong (Alternator) — Support
Alternates modes: in work mode, drops slipstreams that speed up allies who walk over them; in party mode, lobs bottles that damage enemies and heal allies.
- HP: 3700 · Speed: 2.57 t/s · Reload: ~1.5s · Ammo: 3
- Attack: 8.33-tile, 750 dmg, pierces.
- Super: —.
- **Super:** Mix It Up — switches between work and party modes while either boosting nearby allies' speed (work) or instantly healing them (party).
- **Hypercharge: Encore** — Doubles up super effects on the active mode.
- Star Powers: **The Crowd Goes Mild** — Movement speed scales with number of nearby teammates. · **Extra High Note** — Attack damage scales per target pierced.
- Gadgets: **Weekend Warrior** — Self-AoE damage; temporarily switches mode and boosts damage. · **Time For A Slow Song** — Self-AoE slow; switches mode and makes attacks apply slow.
- Quirks: Alt-mode brawler (work vs. party) — Super swaps modes; Attack projectile pierces.
*Source: brawlstars.fandom.com/wiki/Jae-yong*

### Janet (JetpackGirl) — Marksman
High Note — fires a music note that focuses (narrows + extends range) the longer the attack button is held; wide and short by default.
- HP: 3400 · Speed: 2.40 t/s · Reload: ~1.5s · Ammo: 3
- Attack: 4.00-tile, 160° cone, 1000 dmg/pellet × 4 = 4000 max, pierces.
- Super: 2.33-tile, 1.25-tile splash, 800 dmg, indirect.
- **Super:** Crescendo — jetpacks into the air, becoming invulnerable to direct damage while attacking enemies from above.
- **Hypercharge: Magnum Opus** — Super lets her be controlled more easily in the air, with bonus stats.
- Star Powers: **Stage View** — Reveals enemies in bushes while she's in the air. · **Vocal Warm Up** — Attack focuses faster.
- Gadgets: **Drop The Bass** — Deploys a speaker that damages enemies in its radius until destroyed. · **Backstage Pass** — Next attack also pushes her backward (over walls if held).
- Quirks: Attack focus mechanic — range/spread varies with charge; Super grants invulnerability (airborne); Attack projectile pierces.
*Source: brawlstars.fandom.com/wiki/Janet*

### Jessie (Mechanic) — Damage Dealer
Long-ranged electric orb that bounces between nearby enemies for reduced damage per bounce.
- HP: 3300 · Speed: 2.40 t/s · Reload: ~1.8s · Ammo: 3
- Attack: 9.00-tile, 1060 dmg.
- Super: 5.00-tile, 2.71-tile splash, indirect.
- **Super:** Deploys Scrappy, a turret that auto-fires at the nearest enemy with moderate health and damage.
- **Hypercharge: Scrappy 2.0** — Next turret has more health and more damage.
- Star Powers: **Energize** — Can heal her turret by hitting it with her attacks. · **Shocky** — Turret now fires bouncing energy orbs instead of straight shots.
- Gadgets: **Spark Plug** — Turret emits a shockwave that slows nearby enemies. · **Recoil Spring** — Turret attack speed doubled for a few seconds.
- Quirks: Attack chains between enemies; Super spawns a persistent turret.
*Source: brawlstars.fandom.com/wiki/Jessie*

### Juju (Voodoo) — Artillery
Lobs a voodoo toy that explodes on impact; the effect depends on the terrain Juju is standing on (more damage on ground, more range in bush, slows in water).
- HP: 3100 · Speed: 2.40 t/s · Reload: ~1.6s · Ammo: 3
- Attack: 6.33-tile, 0.50-tile splash, 1000 dmg, indirect.
- Super: 5.00-tile, 0.35-tile splash, indirect.
- **Super:** Spawns Gris-Gris, a voodoo doll that fires needles at enemies and stays on the map.
- **Hypercharge: Bokor** — Gris-Gris gains health, speed, damage and needle size.
- Star Powers: **Guarded Gris-Gris** — Gris-Gris spawns with a shield. · **Numbing Needles** — Gris-Gris's needles slow on hit.
- Gadgets: **Voodoo Chile** — Next attack combines all three terrain buffs. · **Elementalist** — Self-buff based on terrain (ground = shield, bush = invisibility, water = speed).
- Quirks: Terrain-dependent attacks/effects (ground/bush/water); Super spawns a persistent damage-dealing pet.
*Source: brawlstars.fandom.com/wiki/Juju*

### Kaze (Geisha) — Assassin
Has two aspects — Geisha dashes a short distance and strikes the nearest target (hitting a Strike Spot doubles damage); Ninja throws two knives that deal more damage at close range.
- HP: 4100 · Speed: 2.73 t/s · Reload: ~1.0s · Ammo: 3
- Attack: 2.67-tile, 750 dmg.
- Super: 7.33-tile, 3.12-tile splash, 650 dmg, indirect.
- **Super:** Geisha summons a Fan Storm vortex zone; Ninja teleports to mark targets and detonates them on the next attack.
- **Hypercharge: Ancient Energy** — Geisha Super damages enemies over time; Ninja Super dashes faster and instantly detonates marks.
- Star Powers: **Advanced Techniques** — Geisha: Strike-Spot hits slow enemies. Ninja: detonating marks damages nearby enemies. · **Gratuity Included** — Geisha: Fan Storm removes ammo from enemies inside. Ninja: gadgets last longer.
- Gadgets: **Gracious Host** — Switching to Ninja gives speed boost; switching to Geisha heals. · **Hensojutsu** — Switching to Ninja grants brief invisibility; switching to Geisha dashes forward.
- Quirks: First Ultra-Legendary brawler; Two aspects (Geisha melee / Ninja ranged) with totally different mechanics; Geisha attack is a dash with directional 'Strike Spot' (positional buff).
*Source: brawlstars.fandom.com/wiki/Kaze*

### Kenji — Assassin
_CSV mechanics N/A — kit description from wiki only._
Alternates between two attacks — first a forward dash dealing low damage, then a wide close-range katana swing dealing moderate damage.
- **Super:** Slashimi — lobs a fish over walls, disappears, and reappears at the landing point performing a cross-pattern slash that splash-damages enemies.
- **Hypercharge: Sake Bomb** — Super gains additional slashes and a wider area.
- Star Powers: **Studied The Blade** — Super slashes have longer range. · **Nigiri Nemesis** — After avoiding damage, gains a shield against the next enemy attack.
- Gadgets: **Dashi Dash** — Next several attacks all dash forward (skip the wide-swing alternation). · **Hosomaki Healing** — Instantly heals a portion of recently lost health.
- Quirks: Attack alternates dash + slash; Super disappears him and re-appears at landing point (positional teleport); Heals on attack hit (trait).
*Source: brawlstars.fandom.com/wiki/Kenji*

### Kit (Attacher) — Support
Short-range claw swipe in a wide cone hitting multiple enemies.
- HP: 3100 · Speed: 2.73 t/s · Reload: ~0.8s · Ammo: 3
- Attack: 3.67-tile, 150° cone, 1000 dmg.
- Super: 6.67-tile, 1000 dmg.
- **Super:** Jumps at a target — on enemies, deals damage and stuns; on allies, attaches to them, healing them and throwing exploding hairballs from atop.
- **Hypercharge: Making Biscuits** — Attached form gains extended range and Super on enemies stuns them.
- Star Powers: **Power Hungry** — More Power Cube benefits from each pickup. · **Overly Attached** — Attaches to allies for longer.
- Gadgets: **Cardboard Box** — Becomes invisible in a box; doubles Super-charge rate while inside. · **Cheeseburger** — Heals himself and the attached ally.
- Quirks: Super has two modes — enemy target damages, ally target attaches/heals; Attached mode is essentially a second form Kit rides on a teammate; Power Cube interaction (Showdown-relevant).
*Source: brawlstars.fandom.com/wiki/Kit*

### Larry & Lawrie — Artillery
_CSV mechanics N/A — kit description from wiki only._
Larry lobs a bundle of tickets at long range — first explodes in a small radius, then explodes again in a larger radius (double-tap damage).
- **Super:** Spawns his twin brother Lawrie, a controlled spawn with his own attacks (waves of plug projectiles in cones).
- **Hypercharge: The Three-Bot Problem** — Super spawns a second, beefier Lawrie alongside the first.
- Star Powers: **Protocol Protect** — Some damage Larry takes is redirected to Lawrie instead. · **Protocol Assist** — Lawrie's damage reloads ammo for Larry.
- Gadgets: **Order Swap** — Larry and Lawrie swap their attacks. · **Order Fall Back** — Both dash to each other, healing on contact.
- Quirks: Twin-brawler kit — Lawrie is a persistent spawnable ally; Attack double-explodes (two damage hits per shot).
*Source: brawlstars.fandom.com/wiki/Larry_%26_Lawrie*

### Leon (Ninja) — Assassin
Flicks four Spinner Blades in a narrow cone; sweeps left-to-right and deals more damage up close.
- HP: 3300 · Speed: 2.73 t/s · Reload: ~1.9s · Ammo: 3
- Attack: 9.67-tile, 35° cone, 480 dmg.
- Super: —.
- **Super:** Smoke Bomb — makes Leon invisible for several seconds; visibility breaks briefly when he attacks, picks up gems, or when enemies are within close range.
- **Hypercharge: Limbo** — Stays invisible even while attacking during the Hypercharge duration.
- Star Powers: **Smoke Trails** — Gains a movement-speed boost while invisible. · **Invisiheal** — Heals over time while his Super is active.
- Gadgets: **Clone Projector** — Creates a decoy that attacks enemies for low damage. · **Lollipop Drop** — Places a lollipop zone that grants invisibility to allies inside.
- Quirks: Stealth mechanic — actual invisibility, not bush hiding; Enemies within 4 tiles can see his outline.
*Source: brawlstars.fandom.com/wiki/Leon*

### Lily (Ambusher) — Assassin
Short-range thorn jabs in a quick close-range hit.
- HP: 4200 · Speed: 2.73 t/s · Reload: ~0.8s · Ammo: 2
- Attack: 2.00-tile, 1060 dmg, pierces.
- Super: 9.00-tile, 500 dmg.
- **Super:** Flourish — fires a large fruit; on hitting an enemy Brawler, teleports Lily directly behind them, damaging them on arrival.
- **Hypercharge: Germinate** — Super bounces off walls and isolates her and the hit target in the Shadow Realm briefly.
- Star Powers: **Spiky** — Next attack after teleport deals bonus damage. · **Vigilance** — Gains speed while an enemy is in her trait area.
- Gadgets: **Vanish** — Temporarily moves to the Shadow Realm (untargetable). · **Repot** — Next Super lobs over obstacles; teleports her to landing point.
- Quirks: Super is a teleport-to-target on hit (Shaco-style flank); Super charges passively when enemies are near her (trait); Attack projectile pierces.
*Source: brawlstars.fandom.com/wiki/Lily*

### Lola — Damage Dealer
_CSV mechanics N/A — kit description from wiki only._
Fires six jewels in a tight long-range pattern.
- **Super:** Summons her Ego, a clone that mirrors her movement and attacks — same direction and timing, but lower stats.
- **Hypercharge: Inflated Ego** — Ego gains more health and damage during Hypercharge.
- Star Powers: **Improvise** — Gains extra damage when down to her last ammo. · **Sealed With A Kiss** — Ego's attacks heal allies for a portion of damage dealt.
- Gadgets: **Freeze Frame** — Ego freezes in place but gains a shield (still attacks/changes direction). · **Stunt Double** — Switches places with Ego; both heal a portion of HP.
- Quirks: Super spawns a mirror clone — same attack as Lola, half stats; Clone charges Super at half rate compared to Lola.
*Source: brawlstars.fandom.com/wiki/Lola*

### Lou (IceDude) — Controller
Throws snow cones that apply Frost to enemies; filling the Frost meter stuns them.
- HP: 3500 · Speed: 2.40 t/s · Reload: ~1.1s · Ammo: 3
- Attack: 9.33-tile, 440 dmg.
- Super: 7.67-tile, 2.29-tile splash, 40 dmg, indirect.
- **Super:** Can-Do — creates a large ice rink that slows enemies who walk on it.
- **Hypercharge: Slushie Storm** — Super additionally stuns nearby enemies on placement.
- Star Powers: **Supercool** — Enemies in his Super area fill their Frost meter faster. · **Hypothermia** — Frosted enemies deal reduced damage.
- Gadgets: **Ice Block** — Becomes immobile but invulnerable for a short duration. · **Cryo Syrup** — Instantly fills the Frost meter of enemies in his Super.
- Quirks: Frost meter mechanic — multi-hit stun setup; Super is a slowing terrain zone.
*Source: brawlstars.fandom.com/wiki/Lou*

### Lumi (Morningstar) — Damage Dealer
Throws a morning star forward; with both maces thrown, the third attack recalls them to her, damaging enemies on the return path and slowing them.
- HP: 3500 · Speed: 2.40 t/s · Reload: ~?s · Ammo: 2
- Attack: 8.00-tile, 600 dmg, pierces.
- Super: 7.33-tile, 0° cone, 3.67-tile splash, 1000 dmg, pierces, indirect.
- **Super:** Blast Beat — creates three increasingly large explosive areas (the biggest stuns).
- **Hypercharge: Drum Solo** — Adds one more explosion on each side of the largest one (total of five explosions).
- Star Powers: **42% Burnt** — Super leaves a fire patch on the largest explosion area. · **Half-Time** — Recalled maces slow enemies longer.
- Gadgets: **Hit The Lights** — Ignites fire around her on-ground maces. · **Grim And Frostbitten** — Creates an icy slow zone around her on-ground maces.
- Quirks: Attack has throw/recall cycle (two outbound + one recall pattern); Super is a sequential multi-explosion (size escalation); Attack/Super projectiles pierce.
*Source: brawlstars.fandom.com/wiki/Lumi*

### Maisie (Maisie) — Marksman
Pressure Rocket — fires a cloud that starts slow and accelerates the further it travels (sweet spot mechanic).
- HP: 4000 · Speed: 2.40 t/s · Reload: ~1.5s · Ammo: 3
- Attack: 8.67-tile, 1500 dmg.
- Super: 3.12-tile splash.
- **Super:** Wide shockwave that knocks all enemies in a self-centered radius back and damages them.
- **Hypercharge: Aftermath** — Super fires main-attack rockets in all directions around her.
- Star Powers: **Pinpoint Precision** — Pressure Rocket deals more damage at max range. · **Tremors** — Super shockwave also slows hit enemies.
- Gadgets: **Disengage** — Dashes a few tiles back while stunning nearby enemies. · **Finish Them** — Instantly reloads ammo and next attack deals bonus damage based on target's missing HP.
- Quirks: Attack speeds up with travel distance (sweet-spot range); Super is a self-centered knockback.
*Source: brawlstars.fandom.com/wiki/Maisie*

### Mandy (Beamer) — Marksman
Fires a candy projectile from her dispenser; holding still charges a Focus bar that extends her range and projectile speed.
- HP: 3000 · Speed: 2.40 t/s · Reload: ~1.5s · Ammo: 3
- Attack: 9.00-tile, 1300 dmg.
- Super: 40.00-tile, 2500 dmg, pierces.
- **Super:** Sugar blast — extremely long-ranged piercing beam that travels through obstacles.
- **Hypercharge: Sugar for All!** — Super fires two additional angled projectiles to the left and right.
- Star Powers: **In My Sights** — Attack speed increases while Focused. · **Hard Candy** — Grants a shield while Focused.
- Gadgets: **Caramelize** — Next attack slows on hit. · **Cookie Crumbs** — Next attack pierces walls and enemies.
- Quirks: Stand-still Focus mechanic (range and speed boost); Super passes through walls.
*Source: brawlstars.fandom.com/wiki/Mandy*

### Max (Speedy) — Support
Rapidly fires four long-ranged projectiles in a slight spread per ammo use.
- HP: 3500 · Speed: 2.73 t/s · Reload: ~1.3s · Ammo: 4
- Attack: 6.67-tile, 320 dmg.
- Super: —.
- **Super:** Run N Gun — temporarily boosts her own and nearby allies' movement speed.
- **Hypercharge: Unlimited Energy** — Speed boost from Super is sustained longer; she gains additional speed.
- Star Powers: **Super Charged** — Super passively charges while she moves. · **Run N Gun** — Reloads faster while moving.
- Gadgets: **Phase Shifter** — Dashes forward, immune to damage during the dash. · **Sneaky Sneakers** — After a delay, teleports back to a marked location with the HP she had then.
- Quirks: Super charges from movement (not damage); Movement-centric kit.
*Source: brawlstars.fandom.com/wiki/Max*

### Meeple (Meeple) — Controller
Fires pawn projectiles that slightly home in on enemies.
- HP: 3300 · Speed: 2.40 t/s · Reload: ~1.7s · Ammo: 3
- Attack: 7.67-tile, 1260 dmg.
- Super: 5.00-tile, 1.88-tile splash, indirect.
- **Super:** Throws a giant d20 die that creates a zone where Meeple and allies can attack THROUGH obstacles.
- **Hypercharge: The Last Rulebender** — Super zone is larger and lets Meeple and allies walk through obstacles and water.
- Star Powers: **Do Not Pass Go** — Bonus damage when shots travel through environment in Super zone. · **Rule Bending** — Allies in Super zone gain reload speed.
- Gadgets: **Mansions Of Meeple** — Next attack spawns dice towers in a wall pattern, trapping/damaging enemies inside. · **Ragequit** — Stun and knockback nearby enemies (effect scales inversely with current HP).
- Quirks: Super grants 'shoot through walls' to allies (terrain bypass); Attacks home in slightly.
*Source: brawlstars.fandom.com/wiki/Meeple*

### Meg (MechaDude) — Damage Dealer
Fires two quick bolts in a slight spread.
- HP: 2400 · Speed: 2.73 t/s · Reload: ~1.3s · Ammo: 3
- Attack: 9.00-tile, 300 dmg.
- Super: —.
- **Super:** Transforms into Mecha — a much tankier alt-form with new bolt attacks and a sweeping Super.
- **Hypercharge: Tungsten Toughness** — Mecha-form Super range increases, or post-Mecha shield is granted.
- Star Powers: **Force Field** — When Mecha is destroyed, Meg gains a damage-reduction shield. · **Heavy Metal** — Mecha explodes on destruction, damaging and knocking back nearby enemies.
- Gadgets: **Jolting Volts** — Heals the Mecha while it's active. · **Toolbox** — Drops a toolbox boosting nearby allies' reload speed until destroyed.
- Quirks: Alt-form Brawler (foot vs. Mecha); Lowest base HP in the game — but Mecha is huge.
*Source: brawlstars.fandom.com/wiki/Meg*

### Melodie — Assassin
_CSV mechanics N/A — kit description from wiki only._
Long-ranged note projectile that does low direct damage; on hit, spawns a note orbiting Melodie that deals high damage to enemies who touch it.
- **Super:** Three sequential dashes that can each be used individually.
- **Hypercharge: Flash Mob** — Each Super dash also spawns an orbiting note.
- Star Powers: **Fast Beats** — Movement speed scales with the number of notes orbiting her. · **Extended Mix** — Notes last longer before vanishing.
- Gadgets: **Perfect Pitch** — Orbit speed and radius increase temporarily. · **Interlude** — Grants a shield scaling with active notes.
- Quirks: Persistent orbiting projectiles (collide with enemies); Super is a 3-charge dash.
*Source: brawlstars.fandom.com/wiki/Melodie*

### Mico (Leaper) — Assassin
Mic Boom — jumps forward a short distance, then deals area damage on landing (invulnerable mid-air).
- HP: 3500 · Speed: 2.73 t/s · Reload: ~2.4s · Ammo: 3
- Attack: 4.00-tile, 1140 dmg.
- Super: —.
- **Super:** Out of Frame — longer leap that deals damage and knockback on landing.
- **Hypercharge: Sound Check** — Super stuns enemies briefly on landing.
- Star Powers: **Monkey Business** — Periodically, next attack removes ammo from enemies hit and refunds it. · **Record Smash** — Deals bonus damage to non-Brawler targets.
- Gadgets: **Clipping Scream** — Long-range scream slows and damages the nearest enemy. · **Presto** — Next jump has extended range.
- Quirks: Attack IS a jump (no projectile); Invulnerable while airborne mid-attack.
*Source: brawlstars.fandom.com/wiki/Mico*

### Mina — Assassin
_CSV mechanics N/A — kit description from wiki only._
Three-stage combo — Attack 1 is long range narrow, Attack 2 medium/medium, Attack 3 is short range wide cone; resets if she doesn't keep attacking.
- **Super:** Furacao 3000 — fires a hurricane that damages enemies and launches them into the air (briefly stunning).
- **Hypercharge: Wind Up** — Super becomes wider and lasts longer.
- Star Powers: **Zum Zum Zum** — Third combo attack heals her on damage dealt. · **Blown Away** — Super roots enemies on top of the launch effect.
- Gadgets: **Windmill** — Creates a wind wall that blocks projectiles. · **Capo-What?** — Next Super recharges instantly if it hits.
- Quirks: Attack rotates through a fixed 3-stage combo (timing-based); Super launches enemies airborne.
*Source: brawlstars.fandom.com/wiki/Mina*

### Moe — Damage Dealer
_CSV mechanics N/A — kit description from wiki only._
Throws a rock that shatters on impact into four smaller stones in cross directions, then each fragment shatters again on second impact.
- **Super:** Drills underground transforming into Driller form; surfaces in a target direction, knocking back enemies. In Driller form, he attacks with a continuous short-range drill.
- **Hypercharge: Foul Play** — Driller form moves faster and deals more damage.
- Star Powers: **Skipping Stones** — Normal-form attack fragments one additional time. · **Speeding Ticket** — Driller form moves faster.
- Gadgets: **Dodgy Digging** — Temporarily increases Super-charge rate. · **Rat Race** — Driller form dashes forward destroying walls.
- Quirks: Attack fragments multiple times (shotgun-like spread from one shot); Alt-form Brawler (above ground / Driller).
*Source: brawlstars.fandom.com/wiki/Moe*

### Mortis (Undertaker) — Assassin
Dashes forward swinging his shovel, damaging enemies in his path; after a wait, his next dash gets significantly longer range.
- HP: 4000 · Speed: 2.73 t/s · Reload: ~2.4s · Ammo: 3
- Attack: 2.67-tile, 1000 dmg.
- Super: 10.00-tile, 900 dmg, pierces.
- **Super:** Sends a swarm of bats forward through walls, damaging the first enemy hit and healing Mortis for the full damage dealt.
- **Hypercharge: Blood Boomerang** — Super bats return to him after going forward, dealing a second wave of damage and healing.
- Star Powers: **Creepy Harvest** — Heals to a portion of max HP on each enemy Brawler defeated. · **Coiled Snake** — Longer-dash recharge time is reduced.
- Gadgets: **Combo Spinner** — Spins his shovel instantly damaging nearby enemies. · **Creature Of The Night** — Turns into bats, becoming untargetable and passing over walls.
- Quirks: Attack IS a dash (no projectile); Charged-up long dash after waiting; Super passes through walls and heals on hit (life-steal Super).
*Source: brawlstars.fandom.com/wiki/Mortis*

### Mr. P (SpawnerDude) — Controller
Throws a suitcase that bounces on impact (over walls/enemies), dealing area damage on landing.
- HP: 3700 · Speed: 2.40 t/s · Reload: ~1.6s · Ammo: 3
- Attack: 7.00-tile, 760 dmg.
- Super: 5.00-tile, 0.94-tile splash, indirect.
- **Super:** Deploys a home base that periodically spawns robo-porters which follow enemies and attack them.
- **Hypercharge: Super Porters! Assemble!** — Home base has more health, porters are faster/tougher, and up to two are active at once.
- Star Powers: **Handle With Care** — Periodically, next suitcase deals more damage after bouncing. · **Revolving Door** — Home-base porters have more health and damage.
- Gadgets: **Service Bell** — Buffs current porter's HP and damage. · **Porter Reinforcements** — Next attack spawns a weak porter at the attack's endpoint.
- Quirks: Attack bounces over obstacles (range extender); Super spawns persistent recurring spawnable units.
*Source: brawlstars.fandom.com/wiki/Mr._P*

### Najia — Controller
_CSV mechanics N/A — kit description from wiki only._
Throws a jar with a paper snake inside that can be redirected mid-flight; deals poison damage over time on hit.
- **Super:** Damage Noodles — lobs three jars that release snakes which chase down and poison nearby enemies.
- **Hypercharge: Asp Strike** — Super snakes are larger and more aggressive.
- Star Powers: **Poisonous Protector** — Brawlers defeated while poisoned spawn a snake on their tile. · **Venomous** — Poison damage scales with target's current HP percentage.
- Gadgets: **Poison Puddles** — Currently-poisoned enemies leave behind poison puddles. · **Najia Jar** — Hides inside a vase; on destruction, knocks back nearby enemies.
- Quirks: Attack projectile can be steered mid-flight (curve aim); Poison-based DoT kit.
*Source: brawlstars.fandom.com/wiki/Najia*

### Nani (Controller) — Marksman
Three light orbs fired in a diamond pattern that converge at a specific range.
- HP: 2500 · Speed: 2.40 t/s · Reload: ~1.8s · Ammo: 3
- Attack: 8.67-tile, 50° cone, 800 dmg/pellet × 3 = 2400 max.
- Super: 3.33-tile, 1800 dmg.
- **Super:** Detaches Peep, a drone she manually steers; explodes on enemy contact for huge damage and destroys walls.
- **Hypercharge: Big Peep** — Peep grows larger and deals more damage as it travels.
- Star Powers: **Autofocus** — Peep gains bonus damage based on travel distance. · **Tempered Steel** — Damage-reduction shield while Peep is active.
- Gadgets: **Warpin Time** — Teleports to Peep's location and ends the Super. · **Return To Sender** — Reflects the next incoming projectile as a counterattack.
- Quirks: Super detaches a player-controlled drone (Peep); Attack converges at a sweet-spot range.
*Source: brawlstars.fandom.com/wiki/Nani*

### Nita (Shaman) — Damage Dealer
Rupture — sends a piercing shockwave forward that hits multiple enemies in its path.
- HP: 4200 · Speed: 2.40 t/s · Reload: ~1.1s · Ammo: 3
- Attack: 6.00-tile, 960 dmg, pierces.
- Super: 5.00-tile, 2.08-tile splash, indirect.
- **Super:** Summons Bruce, a bear with high HP that auto-attacks the nearest enemy in melee.
- **Hypercharge: Hyperbearing** — Next bear has more health and moves faster.
- Star Powers: **Bear With Me** — Hitting an enemy heals Bruce; Bruce hitting an enemy heals Nita. · **Hyper Bear** — Bruce attacks faster.
- Gadgets: **Bear Paws** — Bruce slams the ground, stunning nearby enemies. · **Faux Fur** — Bruce gains a shield for a short duration.
- Quirks: Attack pierces multiple targets; Super spawns a controllable-by-AI persistent pet (Bruce).
*Source: brawlstars.fandom.com/wiki/Nita*

### Ollie (Skater) — Controller
Soundwave in a narrow cone that pierces all targets.
- HP: 5400 · Speed: 2.57 t/s · Reload: ~1.8s · Ammo: 3
- Attack: 6.33-tile, 27° cone, 900 dmg/pellet × 2 = 1800 max, pierces.
- Super: 5.67-tile.
- **Super:** Dashes forward creating a soundwave that damages and hypnotizes enemies — hypnotized enemies walk toward Ollie and can't act.
- **Hypercharge: All Time High** — Super hypnotizes longer and damages more.
- Star Powers: **Kick Push** — Gains speed while near walls. · **Renegade** — Decaying shield after Super dash.
- Gadgets: **Regulate** — Jumps and hypnotizes enemies in a circle on landing. · **All Eyez On Me** — Next attack hypnotizes enemies hit.
- Quirks: Super has a hypnotize CC — pulls enemies toward him and disables them; Super charges from damage taken (trait); Attack projectile pierces.
*Source: brawlstars.fandom.com/wiki/Ollie*

### Otis (Silencer) — Controller
Shoots three paint blobs in a slight spread.
- HP: 3600 · Speed: 2.40 t/s · Reload: ~1.5s · Ammo: 3
- Attack: 9.00-tile, 500 dmg.
- Super: 9.00-tile, 340 dmg.
- **Super:** Silent Seabed — fires his starfish Cil that attaches to an enemy and silences them (no Super/Gadget/attack) for a duration while damaging them.
- **Hypercharge: Silent Stunner** — Super additionally stuns enemies for a duration on impact.
- Star Powers: **Stencil Glue** — Increases Super silence duration. · **Ink Refills** — Attack fires four projectiles instead of three.
- Gadgets: **Dormant Star** — Next Super stays on the ground if it misses, triggering on enemy proximity. · **Phat Splatter** — Next attack creates an ink puddle that damages over time.
- Quirks: Super applies SILENCE (unique disable: can't attack/Super/gadget).
*Source: brawlstars.fandom.com/wiki/Otis*

### Pam (MinigunDude) — Support
Sprays a wide burst of scrap metal in a sweeping cone.
- HP: 5000 · Speed: 2.40 t/s · Reload: ~1.3s · Ammo: 3
- Attack: 9.00-tile, 60° cone, 300 dmg.
- Super: 5.00-tile, 0.00-tile splash, indirect.
- **Super:** Deploys a healing turret that heals her and allies inside its radius continuously.
- **Hypercharge: Mama's Love** — Super turret also grants a decaying shield to anyone inside.
- Star Powers: **Mamas Hug** — Attacks hitting enemies heal Pam and nearby allies a small amount. · **Mamas Squeeze** — Healing turret also damages enemies inside its radius.
- Gadgets: **Pulse Modulator** — Turret emits a healing pulse to nearby allies. · **Scrapsucker** — Next attack removes enemy ammo and reloads Pam's.
- Quirks: Super spawns a persistent healing turret; Attack heals on hit through Star Power.
*Source: brawlstars.fandom.com/wiki/Pam*

### Pearl (Cooker) — Damage Dealer
Sprays a spread-out burst of cookies in a sweeping pattern; damage scales with her Heat meter (depletes as she fires).
- HP: 4300 · Speed: 2.40 t/s · Reload: ~1.5s · Ammo: 3
- Attack: 9.00-tile, 40° cone, 280 dmg.
- Super: —.
- **Super:** Pyrolitic Smash — wide self-centered shockwave that destroys obstacles and deals heavy damage.
- **Hypercharge: Pyrolitic** — Super leaves a burning area behind that ignites enemies who touch it.
- Star Powers: **Heat Retention** — Super consumes less Heat when used. · **Heat Shield** — Reduces damage taken while Heat is high.
- Gadgets: **Overcooked** — Next attack fires burning cookies that DoT enemies. · **Made With Love** — Next attack heals allies it passes (skips enemies).
- Quirks: Heat meter — damage scales with how charged her oven is; Heat refills over time, drains on attacks.
*Source: brawlstars.fandom.com/wiki/Pearl*

### Penny (ArtilleryDude) — Artillery
Fires a pouch of gold that bursts on impact into a splash of coins (multi-target splash).
- HP: 3500 · Speed: 2.40 t/s · Reload: ~2.0s · Ammo: 3
- Attack: 8.67-tile, 980 dmg.
- Super: 5.00-tile, 1.67-tile splash, indirect.
- **Super:** Deploys a Mortar Cannon — a long-ranged turret that lobs cannonballs at high damage and sets the ground on fire briefly.
- **Hypercharge: New Lobber** — Mortar grows larger and lobs two cannonballs per shot.
- Star Powers: **Heavy Coffers** — Attack splash spreads wider on hit. · **Master Blaster** — Mortar damages nearby enemies on landing and knocks them back.
- Gadgets: **Salty Barrel** — Drops a barrel that blocks enemy projectiles. · **Trusty Spyglass** — Mortar fires once at every visible enemy in range.
- Quirks: Attack splashes after hitting (creates secondary damage cone); Super spawns a persistent mortar.
*Source: brawlstars.fandom.com/wiki/Penny*

### Pierce (Bulletstorm) — Marksman
Fires water that drops a shell on the ground when it hits a target; picking up the shell triggers an automatic follow-up shot through obstacles.
- HP: 3000 · Speed: 2.40 t/s · Reload: ~?s · Ammo: 3
- Attack: 10.00-tile, 950 dmg.
- Super: 8.33-tile, 0.54-tile splash, indirect.
- **Super:** Marks all targets in a radius after a delay, then automatically fires homing projectiles at them.
- **Hypercharge: Second Wave** — Super fires a second weaker wave of homing projectiles.
- Star Powers: **Mission Swimpossible** — His last-ammo shot slows enemies hit. · **Slip N Snipe** — Movement-speed boost on collecting a shell.
- Gadgets: **Bottomless Mags** — Reloads ammo and drops a shell next to him. · **You Only Brawl Twice** — Absorbs shells for shield value and pushes back enemies.
- Quirks: Two-stage attack — hit drops a shell, picking it up fires automatic homing shot; Super has homing projectiles.
*Source: brawlstars.fandom.com/wiki/Pierce*

### Piper (Sniper) — Marksman
Fires a very long-ranged bullet from her umbrella that deals more damage the further it travels.
- HP: 2500 · Speed: 2.40 t/s · Reload: ~2.3s · Ammo: 3
- Attack: 10.00-tile, 1700 dmg.
- Super: 8.67-tile, 900 dmg.
- **Super:** Pops grenades at her feet then jumps a long distance away, dealing damage at her takeoff point.
- **Hypercharge: Boppin'** — Super pops more grenades and travels further while destroying terrain.
- Star Powers: **Ambush** — Bonus damage at max range when firing from a bush. · **Snappy Sniping** — Hitting an enemy reloads an ammo instantly.
- Gadgets: **Auto Aimer** — Fires a defensive shot at the closest enemy, pushing them back. · **Homemade Recipe** — Next attack homes in on enemies.
- Quirks: Damage scales with travel distance (sniper falloff inverse); Super doubles as escape mobility.
*Source: brawlstars.fandom.com/wiki/Piper*

### Poco (DeadMariachi) — Support
Plays his guitarrón, sending damaging musical notes in a wide cone.
- HP: 4000 · Speed: 2.40 t/s · Reload: ~1.6s · Ammo: 3
- Attack: 7.00-tile, 130° cone, 760 dmg/pellet × 4 = 3040 max, pierces.
- Super: 9.33-tile, 130° cone, 2100 dmg × 3, pierces.
- **Super:** Encore — wider, faster healing wave that heals himself and all allies it passes through.
- **Hypercharge: Medic's Melody** — Super overheals allies with a decaying shield.
- Star Powers: **Da Capo** — Attack notes also heal allies they hit. · **Screeching Solo** — Super also damages enemies it hits.
- Gadgets: **Tuning Fork** — Heals self and nearby allies in a self-centered radius. · **Protective Tunes** — Cleanses status effects on allies in a large radius and grants immunity.
- Quirks: Super HEALS allies (no damage by default); Star Power lets attack heal allies (dual-purpose); Attack projectile pierces.
*Source: brawlstars.fandom.com/wiki/Poco*

### R-T — Damage Dealer
_CSV mechanics N/A — kit description from wiki only._
Fires a single projectile that marks an enemy on hit; any subsequent damage on the marked enemy consumes the mark for bonus damage.
- **Super:** Splits R-T into two — his legs are left behind, both halves move and attack independently (short-range marking attacks) with increased mobility.
- **Hypercharge: 360-Degree Surveillance** — Small radars revolve around both halves during alt-form, each dealing damage.
- Star Powers: **Quick Maths** — Marks last longer. · **Recording** — Both halves take reduced damage while split.
- Gadgets: **Out Of Line** — Instantly charges Super. · **Hacks** — Instantly triggers all active marks on all enemies.
- Quirks: Mark-then-burst mechanic on attack; Super splits him in two — multiple simultaneous active forms.
*Source: brawlstars.fandom.com/wiki/R-T*

### Rico (TrickshotDude) — Damage Dealer
Long-ranged bullets that bounce off walls and continue traveling.
- HP: 3000 · Speed: 2.40 t/s · Reload: ~1.2s · Ammo: 3
- Attack: 9.67-tile, 15° cone, 300 dmg, bounces.
- Super: 13.33-tile, 20° cone, 360 dmg, pierces, bounces.
- **Super:** Bouncy Bullets — fires a piercing long-range burst that bounces off walls.
- **Hypercharge: Trick Shot King** — Super projectiles bounce significantly further.
- Star Powers: **Super Bouncy** — Attack and Super bullets deal bonus damage after their first bounce. · **Robo Retreat** — Moves faster when at low health.
- Gadgets: **Multiball Launcher** — Blasts bouncing bullets in all directions around him. · **Bouncy Castle** — Next attack heals him per bullet bounce.
- Quirks: Attack AND Super bounce off walls (creative angle setups); Super pierces multiple targets.
*Source: brawlstars.fandom.com/wiki/Rico*

### Rosa (Rosa) — Tank
Three short-ranged punches from her boxing gloves.
- HP: 5400 · Speed: 2.57 t/s · Reload: ~1.0s · Ammo: 3
- Attack: 3.67-tile, 130° cone, 500 dmg/pellet × 3 = 1500 max, pierces.
- Super: —.
- **Super:** Gains a significant damage-reduction shield (tough-vine skin) for several seconds.
- **Hypercharge: Grasping Roots** — Super creates a slow zone around her for the duration.
- Star Powers: **Plant Life** — Heals over time while inside a bush. · **Thorny Gloves** — Attack damage boosted while Super is active.
- Gadgets: **Grow Light** — Spawns bushes instantly around her. · **Unfriendly Bushes** — Damages and slows all enemies hiding in bushes.
- Quirks: Super grants raw damage reduction (no offensive component); Super charges from damage taken (trait); Heals in bushes; can spawn bushes; Attack projectile pierces.
*Source: brawlstars.fandom.com/wiki/Rosa*

### Ruffs (Ruffs) — Support
Two parallel laser blasts that bounce off walls.
- HP: 3000 · Speed: 2.40 t/s · Reload: ~1.4s · Ammo: 3
- Attack: 9.00-tile, 600 dmg/pellet × 2 = 1200 max, bounces.
- Super: 7.67-tile, 1.46-tile splash, 1000 dmg, indirect.
- **Super:** Calls a supply drop from the sky that damages enemies and leaves a power-up that buffs ally damage and HP on pickup.
- **Hypercharge: The Goodest Boy** — Super damage increased; instantly charges all allies' Hypercharges.
- Star Powers: **Air Superiority** — Super destroys obstacles and deals more damage. · **Field Promotion** — Allies near Ruffs gain increased max HP continuously.
- Gadgets: **Take Cover** — Drops three sandbags as cover. · **Air Support** — Calls a missile barrage near the closest enemy.
- Quirks: Attack projectiles bounce off walls; Super drops a power-up pickup that buffs allies.
*Source: brawlstars.fandom.com/wiki/Ruffs*

### Sam (WeaponThrower) — Assassin
Two close-range punches with his Knuckle Busters; deals more damage when wearing them than when bare-fisted.
- HP: 5700 · Speed: 2.57 t/s · Reload: ~1.6s · Ammo: 3
- Attack: 3.00-tile, 100° cone, 800 dmg, pierces.
- Super: 8.67-tile, 1400 dmg, pierces.
- **Super:** Throws his Knuckle Busters or recalls them; while they're flying he loses his fists (lower attack damage) but gains speed.
- **Hypercharge: Knockout Punch** — Knuckle Busters travel faster and fully recharge his Super on a hit.
- Star Powers: **Hearty Recovery** — Heals a portion of missing HP on recalling Knuckle Busters. · **Remote Recharge** — Knuckle Busters on the ground passively charge his Super if enemies are near.
- Gadgets: **Magnetic Field** — On-ground Busters pull enemies in. · **Pulse Repellent** — Next Super landing knocks back enemies in a pulse.
- Quirks: Two stances — with/without Knuckle Busters (different damage profiles); Super is a throwable+recall weapon (ground-state mechanic); Starts each match with Super already charged (trait); Attack pierces multiple targets.
*Source: brawlstars.fandom.com/wiki/Sam*

### Sandy (Sandstorm) — Controller
Throws piercing pebbles in three clusters across a wide cone (each enemy can be hit by one cluster).
- HP: 4100 · Speed: 2.57 t/s · Reload: ~1.8s · Ammo: 3
- Attack: 6.00-tile, 80° cone, 900 dmg/pellet × 3 = 2700 max, pierces.
- Super: 7.33-tile, 2.08-tile splash, indirect.
- **Super:** Throws a star-shape that creates a sandstorm zone — Sandy and allies inside are invisible.
- **Hypercharge: Swift Winds** — Sandstorm grants speed boost to allies AND prevents enemies inside from attacking or using abilities.
- Star Powers: **Rude Sands** — Sandstorm damages enemies over time. · **Healing Winds** — Sandstorm heals allies inside.
- Gadgets: **Sleep Stimulator** — Falls asleep briefly and restores all HP. · **Sweet Dreams** — Next attack puts enemies to sleep (wakes on damage).
- Quirks: Super creates a team invisibility zone (concealment for whole squad); Attack pierces multiple targets.
*Source: brawlstars.fandom.com/wiki/Sandy*

### Shade (Ghost) — Assassin
Hugs in a wide close-range arc, dealing double damage if the center of the swing hits.
- HP: 3700 · Speed: 2.73 t/s · Reload: ~0.8s · Ammo: 3
- Attack: 3.67-tile, 300° cone, 800 dmg.
- Super: 3.33-tile.
- **Super:** Incorporeal Form — dashes forward passing through obstacles.
- **Hypercharge: The Frightener** — All attacks during Hypercharged Super deal max (centered) damage.
- Star Powers: **Spooky Speedster** — Center-attack hits grant a movement-speed boost. · **Hardened Hoodie** — Damage reduction while in Incorporeal Form.
- Gadgets: **Longarms** — Next attack has extended range. · **Jump Scare** — Creates a ghost ring around himself that slows nearby enemies.
- Quirks: Center-of-attack sweet-spot damage; Super passes through walls (Incorporeal); Super charges from enemy proximity (trait); moves over water (trait).
*Source: brawlstars.fandom.com/wiki/Shade*

### Shelly (ShotgunGirl) — Damage Dealer
Fires a burst of five shotgun pellets that spread in a cone — dealing maximum damage at point-blank range.
- HP: 3900 · Speed: 2.57 t/s · Reload: ~1.5s · Ammo: 3
- Attack: 7.67-tile, 60° cone, 300 dmg/pellet × 5 = 1500 max.
- Super: 7.67-tile, 100° cone, 320 dmg × 9, pierces.
- **Super:** Super Shell — a wider, more powerful burst of nine pellets that pierces enemies, knocks them back, and destroys obstacles.
- **Hypercharge: Double Barrel** — Super spread increases significantly and projectile count rises from 9 to 12.
- Star Powers: **Shell Shock** — Super shells slow enemies hit. · **Band-Aid** — Charges a passive heal that triggers when she drops below a health threshold.
- Gadgets: **Fast Forward** — Dashes a few tiles forward, instantly reloading all ammo. · **Clay Pigeons** — Next three attacks have narrower spread and longer range.
- Quirks: Shotgun-cone damage falloff (close range > distance); Super projectile pierces.
*Source: brawlstars.fandom.com/wiki/Shelly*

### Sirius — Marksman
_CSV mechanics N/A — kit description from wiki only._
Binary Starr — fires two simultaneous projectiles: a long-ranged Shadow Strike and a Starr Bomb that explodes in a small splash radius.
- **Super:** Shadow Summon — deploys all the Brawler Shadows he's collected through the match; each Shadow mimics that Brawler's attack at lower stats.
- **Hypercharge: Constellation** — Shadows summoned during Hypercharge are tougher.
- Star Powers: **Dusk Runners** — Shadows move faster. · **The Darkest Starr** — Each Shadow Strike hit collects two Brawler Shadows instead of one.
- Gadgets: **A Starr Is Born** — Fires a projectile that spawns a Shadow on hit and slows the target. · **Master Of Shadows** — Recalls Shadows to Sirius, healing them.
- Quirks: Collects 'Brawler Shadows' by hitting enemies — Super spawns mini-clones of them; Super auto-charges over time (trait); Ultra Legendary rarity.
*Source: brawlstars.fandom.com/wiki/Sirius*

### Spike (Cactus) — Damage Dealer
Throws a cactus that explodes on impact, releasing spikes in all directions from the explosion center.
- HP: 3000 · Speed: 2.40 t/s · Reload: ~2.0s · Ammo: 3
- Attack: 7.67-tile, 490 dmg.
- Super: 7.67-tile, 1.67-tile splash, 400 dmg, indirect.
- **Super:** Stick Around — lobs a thorny zone that slows and damages enemies inside for several seconds.
- **Hypercharge: Blooming Season** — Super radius is increased.
- Star Powers: **Fertilize** — Super heals Spike for a portion of damage dealt. · **Curveball** — Spikes from cactus grenades curve, making them easier to hit.
- Gadgets: **Popping Pincushion** — Fires a wave of needles outward (multi-shot). · **Life Plant** — Drops a healing plant; on destruction, it heals nearby allies.
- Quirks: Attack is explosion + radial spike spray (not single projectile); Super is a persistent damage/slow zone.
*Source: brawlstars.fandom.com/wiki/Spike*

### Sprout (Wally) — Artillery
Lobs a seed bomb that bounces and explodes on contact or after a fuse.
- HP: 3200 · Speed: 2.40 t/s · Reload: ~1.7s · Ammo: 3
- Attack: 5.00-tile, 0.10-tile splash, 1040 dmg, indirect.
- Super: 7.67-tile, 0.83-tile splash, indirect.
- **Super:** Throws a Super Seed that creates a small wall hedge on landing — a temporary barrier.
- **Hypercharge: Thorns** — Hedge from Super damages enemies who touch it.
- Star Powers: **Overgrowth** — Periodically, next attack has a larger explosion radius. · **Photosynthesis** — Damage-reduction shield while in bushes.
- Gadgets: **Garden Mulcher** — Consumes a nearby bush tile and heals. · **Transplant** — Destroys current hedge and refunds full Super.
- Quirks: Super places a temporary WALL (physical terrain modifier); Attacks bounce off walls.
*Source: brawlstars.fandom.com/wiki/Sprout*

### Squeak (StickyBomb) — Controller
Shoots a blob of goo that sticks to enemies/obstacles then explodes after a delay.
- HP: 3800 · Speed: 2.40 t/s · Reload: ~2.1s · Ammo: 3
- Attack: 7.67-tile, 1160 dmg.
- Super: 8.33-tile, 0.83-tile splash, 1000 dmg, indirect.
- **Super:** Throws a giant ball that splits into six smaller blobs which each explode after a delay (carpet bomb).
- **Hypercharge: Bouncy Blob** — Super spawns a second volley of sticky blobs after the first.
- Star Powers: **Chain Reaction** — Attack damage increases per enemy in its explosion radius. · **Super Sticky** — Super blobs slow enemies on explosion.
- Gadgets: **Windup** — Next attack has more range and damage. · **Residue** — Next attack also reveals bushes/invisible enemies and slows.
- Quirks: Delayed-fuse explosions on attack and Super; Sticks to walls/enemies before detonation.
*Source: brawlstars.fandom.com/wiki/Squeak*

### Starr Nova — Assassin
_CSV mechanics N/A — kit description from wiki only._
Fires two piercing sparkles from her hair (right then left).
- **Super:** Transforms her into her sword-wielding alt-form for a duration; the alt-form swings a sword in a close arc that heals her on hit.
- **Hypercharge: Galactic Halo** — Alt-form duration extended; more damage.
- Star Powers: **Power Level Maximum** — Alt-form damage stacks per target hit, up to a cap. · **Mystical Starr Technique** — Main-form attack heals allies for a portion of damage dealt.
- Gadgets: **Floaty Time** — Deploys an anti-gravity device that lets allies fly over obstacles in its area. · **Shining Starr Of Friendship And Justice** — Fires an energy ball that damages and heals; she can teleport to it mid-flight.
- Quirks: Alt-form brawler — main form is ranged, alt-form is melee dash sword; Heal-on-hit in alt-form.
*Source: brawlstars.fandom.com/wiki/Starr_Nova*

### Stu (Roller) — Assassin
Razzle Dazzle — fires two long-range pyrotechnics in quick succession; each hit fully charges his Super.
- HP: 3500 · Speed: 2.40 t/s · Reload: ~1.5s · Ammo: 3
- Attack: 7.67-tile, 540 dmg.
- Super: 2.33-tile.
- **Super:** Nitro Boost — short dash leaving a burning trail behind that damages enemies who touch it.
- **Hypercharge: Infinitro** — Super instantly recharges when used — infinite supers for the Hypercharge duration.
- Star Powers: **Zero Drag** — Super dash distance is significantly longer. · **Gaso-Heal** — Heals when using Super.
- Gadgets: **Speed Zone** — Drops a booster that speeds up allies in its radius. · **Breakthrough** — Next Super dash destroys obstacles and sends debris that damages enemies.
- Quirks: Each successful attack fully charges his Super (rapid mobility loop); Super charges from his attack hits (no enemy damage required to charge faster).
*Source: brawlstars.fandom.com/wiki/Stu*

### Surge (PowerLeveler) — Damage Dealer
Fires a shot of juice that splits in two perpendicular directions when it hits an enemy.
- HP: 3300 · Speed: 2.17 t/s · Reload: ~2.0s · Ammo: 3
- Attack: 6.67-tile, 1180 dmg.
- Super: 3.33-tile, 1000 dmg.
- **Super:** Party Tricks — leaps over walls, damaging enemies on landing and upgrading himself one stage (Stage 1 speed, 2 range, 3 multi-split attacks).
- **Hypercharge: Stage 5** — Adds a fourth and fifth Super stage with even more range and shot splits.
- Star Powers: **To The Max** — Attack also splits when hitting walls. · **Serve Ice Cold** — Respawns with Stage 1 upgrade already applied.
- Gadgets: **Power Surge** — Overloads his circuits, advancing his stage for a few seconds. · **Power Shield** — Absorbs the next damage and reloads ammo from the energy.
- Quirks: Upgrade-stage system: Super-charge advances Surge through tiered buffs; Stages reset on death by default.
*Source: brawlstars.fandom.com/wiki/Surge*

### Tara (BlackHole) — Damage Dealer
Throws three piercing tarot cards in a tight cone.
- HP: 3300 · Speed: 2.40 t/s · Reload: ~2.0s · Ammo: 3
- Attack: 8.00-tile, 50° cone, 480 dmg/pellet × 3 = 1440 max, pierces.
- Super: 6.67-tile, 2.50-tile splash, 800 dmg, indirect.
- **Super:** Gravity — throws a black hole that pulls all enemies in a radius inward, then explodes dealing splash damage.
- **Hypercharge: Supermassive** — Super pull radius and explosion radius both increased.
- Star Powers: **Black Portal** — Super spawns a shadowy Tara clone that chases enemies. · **Healing Shade** — Super spawns a shadowy Tara that heals teammates.
- Gadgets: **Psychic Enhancer** — Reveals enemies in bushes and invisible enemies for several seconds. · **Support From Beyond** — Surrounds her with three weak shadows that fight for her briefly.
- Quirks: Super is a hard CC PULL (single AoE that groups enemies); Attack pierces multiple targets.
*Source: brawlstars.fandom.com/wiki/Tara*

### Tick (ClusterBombDude) — Artillery
Lobs three mines over obstacles that explode on enemy contact or after a fuse delay.
- HP: 2400 · Speed: 2.40 t/s · Reload: ~2.4s · Ammo: 3
- Attack: 8.67-tile, 1.56-tile splash, 680 dmg, indirect.
- Super: 3.33-tile, 1.04-tile splash, indirect.
- **Super:** Detaches his head, sending it chasing the nearest enemy; the head explodes on contact, knocking back and damaging.
- **Hypercharge: Headstrong** — Head moves faster and on explosion drops six smaller mines.
- Star Powers: **Well Oiled** — Begins self-healing sooner after taking no damage. · **Automa-Tick Reload** — Reload time is reduced.
- Gadgets: **Mine Mania** — Next attack fires double the number of mines. · **Last Hurrah** — Grants a temporary shield that explodes outward when it ends.
- Quirks: Attack mines arm on contact / fuse (proximity damage); Super sends a controlled chase projectile (Tick's head).
*Source: brawlstars.fandom.com/wiki/Tick*

### Trunk (Domain) — Tank
Spins after a brief delay, instantly damaging enemies in a circular self-AoE and leaving ants behind that buff Trunk's speed and damage.
- HP: 5200 · Speed: 2.57 t/s · Reload: ~1.5s · Ammo: 3
- Attack: 2.08-tile splash, 1400 dmg.
- Super: 7.00-tile, 150 dmg.
- **Super:** Dashes forward leaving an ant trail that behaves like his attack ants.
- **Hypercharge: Retread** — Super's ant trail deals damage over time to enemies on it.
- Star Powers: **New Insect Overlords** — Enemies on ants deal reduced damage. · **Colony Scouts** — Ants reveal hidden enemies on them.
- Gadgets: **For The Queen** — Instantly spreads ants in a large area. · **Worker Ants** — Heals from the first damage source taken for the next few seconds.
- Quirks: Ant-trail buff/debuff field — central kit mechanic; Super charges from damage taken (trait).
*Source: brawlstars.fandom.com/wiki/Trunk*

### Willow (Puppeteer) — Controller
Lobs a lantern that creates a small puddle dealing damage and damage over time to enemies in it.
- HP: 3300 · Speed: 2.40 t/s · Reload: ~2.0s · Ammo: 3
- Attack: 7.33-tile, 1.25-tile splash, indirect.
- Super: 8.33-tile.
- **Super:** Hex — fires a tadpole; on hitting an enemy Brawler, she takes control of them while gaining a damage-reduction shield.
- **Hypercharge: Psychic Safety** — She is immune to damage while controlling an enemy.
- Star Powers: **Love Is Blind** — Poisoned enemies have reduced reload speed. · **Obsession** — Controlled enemy gains movement speed (forces them into bad positions faster).
- Gadgets: **Spellbound** — Next attack deals all its poison damage instantly. · **Dive** — Becomes immobile but invulnerable briefly.
- Quirks: Super takes CONTROL of an enemy Brawler (mind control — they walk into walls/dangers); Lobs attacks over walls.
*Source: brawlstars.fandom.com/wiki/Willow*

### Ziggy — Damage Dealer
_CSV mechanics N/A — kit description from wiki only._
Calls down a lightning strike on a target location (long-range pinpoint damage).
- **Super:** Conjures a large electrical storm that travels across the map, slowing on contact with enemies caught inside.
- **Hypercharge: Storm Surge** — Storm is bigger and slows enemies more.
- Star Powers: **Thunderstruck** — Enemies hit by Super are slowed. · **The Great Ziggini** — Hitting an enemy with a lightning strike boosts the next attack's damage.
- Gadgets: **Electric Shuffle** — Auto-strikes nearest enemy every second for a few seconds (no ammo cost). · **Now You See Me** — Next lightning strike teleports him to its target location.
- Quirks: Top-down lightning strike attack (no projectile travel); Super is a slow-spreading storm wave.
*Source: brawlstars.fandom.com/wiki/Ziggy*

---

## Wiki-vs-CSV discrepancies

Stats are trusted from the CSV when they differ. Most discrepancies below are wiki under-specification rather than disagreement.

- **Bull** — Super range: CSV says **11 tiles (Super charge)**; wiki says *wiki text varies: charges in a straight line, no precise tile figure*. Bull's Super dash distance — wiki describes it qualitatively but doesn't give a tile number; CSV is the authority.
- **Buster** — Attack range: CSV says **5.33 tiles**; wiki says *wiki phrasing 'cone of light' without explicit distance*. No conflict, just noting wiki under-specifies.
- **Edgar** — Attack range: CSV says **2 tiles**; wiki says *'extremely short cooldown … two quick short-ranged punches'*. Wiki has no tile number; consistent with CSV.
- **8-Bit** — Movement speed: CSV says **1.93 t/s (CSV)**; wiki says *wiki calls it 'slowest movement speed of any Brawler'*. Consistent — 8-Bit IS the slowest. CSV confirms.
- **Buzz Lightyear** — All stats: CSV says **absent from CSV (event brawler)**; wiki says *Wiki notes Buzz Lightyear is time-limited / removed*. Kit data from wiki only; brawler is no longer in active play.
- **Lola** — Super (Ego): CSV says **no separate super entry in CSV**; wiki says *Wiki: Ego is a mirror clone with ~half stats*. CSV doesn't model Ego — wiki provides the kit understanding.
- **Buzz** — Super range: CSV says **10 tiles**; wiki says *Wiki describes 'grapples to wall or enemy' with variable distance*. Consistent — CSV value is the max grapple distance.
- **Stu** — Super range: CSV says **2.33 tiles**; wiki says *Wiki: 'short-range dash'*. Consistent.
- **Crow** — Super: CSV says **no super range in CSV (jump-based)**; wiki says *Wiki: jumps and throws daggers on takeoff/landing*. Super is mobility + radial damage, not a directional range.
- **Mortis** — Super range: CSV says **10 tiles**; wiki says *Wiki: bats 'have a long range' (qualitative)*. Consistent — Super is the bat swarm direction.
- **Larry & Lawrie** — All stats: CSV says **absent from CSV (post-dump brawler)**; wiki says *wiki provides full mechanics*. CSV mechanics N/A.
- **Damian** — All stats: CSV says **absent from CSV (post-dump brawler)**; wiki says *wiki provides full mechanics*. CSV mechanics N/A.
- **Kenji** — All stats: CSV says **absent from CSV (post-dump brawler)**; wiki says *wiki provides full mechanics*. CSV mechanics N/A.
- **Melodie** — All stats: CSV says **absent from CSV (post-dump brawler)**; wiki says *wiki provides full mechanics*. CSV mechanics N/A.
- **Moe** — All stats: CSV says **absent from CSV (post-dump brawler)**; wiki says *wiki provides full mechanics*. CSV mechanics N/A.
- **Hank** — All stats: CSV says **absent from CSV (post-dump brawler)**; wiki says *wiki provides full mechanics*. CSV mechanics N/A.
- **R-T** — All stats: CSV says **absent from CSV (post-dump brawler)**; wiki says *wiki provides full mechanics*. CSV mechanics N/A.
- **Lola** — All stats: CSV says **absent from CSV (event brawler)**; wiki says *wiki provides full mechanics including Ego clone*. CSV mechanics N/A.
- **Mina** — All stats: CSV says **absent from CSV (post-dump brawler)**; wiki says *wiki provides full 3-combo attack and hurricane Super*. CSV mechanics N/A.
- **Starr Nova** — All stats: CSV says **absent from CSV (post-dump brawler)**; wiki says *wiki provides full alt-form mechanics*. CSV mechanics N/A.
- **Najia** — All stats: CSV says **absent from CSV (post-dump brawler)**; wiki says *wiki provides full kit*. CSV mechanics N/A.
- **Sirius** — All stats: CSV says **absent from CSV (post-dump brawler)**; wiki says *wiki: Ultra Legendary, collects Brawler Shadows*. CSV mechanics N/A.
- **Glowy** — All stats: CSV says **absent from CSV (post-dump brawler)**; wiki says *wiki provides tether mechanic*. CSV mechanics N/A.
- **Ziggy** — All stats: CSV says **absent from CSV (post-dump brawler)**; wiki says *wiki provides lightning strike + storm*. CSV mechanics N/A.
