"""Render Spike's Life Plant gadget reticle — indirect/thrown placement type.
Different shape family from Shelly's cone (which is direct-fire)."""
import math
from pathlib import Path

# Data pulled from csv_logic (verified 2026-05-18, v67.264):
# CactusBonusSkillCover: CastingRange=22 → 7.33 tiles
# Projectile: Indirect=true (thrown), Gravity=240
# Spawned CactusCover: CollisionRadius=120 (~0.5 tile assuming 480 units/tile)
# CactusCoverHeal (area_effects.csv): Radius=1000 (~2.08 tiles), Damage=-30 (heal)
RANGE_TILES = 22 / 3.0
CACTUS_RADIUS_TILES = 120 / 480.0
HEAL_RADIUS_TILES = 1000 / 480.0

TILE_PX = 30
CANVAS = 600
COLOR = '#4ade80'  # gadget green

cx, cy = CANVAS / 2, CANVAS - 100  # Spike at bottom-center, aim up
target_x, target_y = cx, cy - RANGE_TILES * TILE_PX

# tile grid
grid_lines = []
for x in range(0, CANVAS + 1, TILE_PX):
    grid_lines.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{CANVAS}" stroke="#2a3142" stroke-width="0.5"/>')
for y in range(0, CANVAS + 1, TILE_PX):
    grid_lines.append(f'<line x1="0" y1="{y}" x2="{CANVAS}" y2="{y}" stroke="#2a3142" stroke-width="0.5"/>')

# trajectory arc (indirect/thrown — visualize as bezier)
mid_x = (cx + target_x) / 2
mid_y = min(cy, target_y) - 60  # arc upward

# range indicator (faded circle at max range)
range_px = RANGE_TILES * TILE_PX
cactus_radius_px = CACTUS_RADIUS_TILES * TILE_PX
heal_radius_px = HEAL_RADIUS_TILES * TILE_PX
HEAL_COLOR = '#f87171'  # red-pink for the heal pulse, distinct from gadget green

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {CANVAS} {CANVAS}" style="background:#0d1117;font-family:sans-serif">
  <rect width="{CANVAS}" height="{CANVAS}" fill="#1a1f2e"/>
  {''.join(grid_lines)}

  <!-- Max range ring (where the cactus CAN be placed) -->
  <circle cx="{cx}" cy="{cy}" r="{range_px}" fill="none" stroke="{COLOR}" stroke-width="1.5" stroke-dasharray="4,4" opacity="0.5"/>

  <!-- Trajectory arc (indicates indirect/thrown projectile) -->
  <path d="M {cx},{cy} Q {mid_x},{mid_y} {target_x},{target_y}" fill="none" stroke="{COLOR}" stroke-width="2" stroke-dasharray="6,3" opacity="0.7"/>

  <!-- Aim line (faint, straight) -->
  <line x1="{cx}" y1="{cy}" x2="{target_x}" y2="{target_y}" stroke="{COLOR}" stroke-width="1" opacity="0.25"/>

  <!-- Landing target marker -->
  <circle cx="{target_x}" cy="{target_y}" r="14" fill="none" stroke="{COLOR}" stroke-width="3"/>
  <circle cx="{target_x}" cy="{target_y}" r="4" fill="{COLOR}"/>
  <line x1="{target_x-20}" y1="{target_y}" x2="{target_x+20}" y2="{target_y}" stroke="{COLOR}" stroke-width="1.5"/>
  <line x1="{target_x}" y1="{target_y-20}" x2="{target_x}" y2="{target_y+20}" stroke="{COLOR}" stroke-width="1.5"/>

  <!-- Heal-burst-on-death radius (larger faded pulse) -->
  <circle cx="{target_x}" cy="{target_y}" r="{heal_radius_px}" fill="{HEAL_COLOR}" fill-opacity="0.12" stroke="{HEAL_COLOR}" stroke-width="2" stroke-dasharray="6,4"/>
  <text x="{target_x + heal_radius_px + 8}" y="{target_y - heal_radius_px + 12}" font-family="monospace" font-size="11" fill="{HEAL_COLOR}">heal burst on death</text>
  <text x="{target_x + heal_radius_px + 8}" y="{target_y - heal_radius_px + 26}" font-family="monospace" font-size="10" fill="#888">radius {HEAL_RADIUS_TILES:.2f} tiles, allies only</text>

  <!-- Cactus footprint (small, what physically spawns) -->
  <circle cx="{target_x}" cy="{target_y}" r="{cactus_radius_px}" fill="{COLOR}" fill-opacity="0.5" stroke="{COLOR}" stroke-width="2"/>
  <text x="{target_x + 25}" y="{target_y + heal_radius_px - 8}" font-family="monospace" font-size="11" fill="{COLOR}">cactus body</text>
  <text x="{target_x + 25}" y="{target_y + heal_radius_px + 6}" font-family="monospace" font-size="10" fill="#888">blocks shots, 1750 HP</text>

  <!-- Spike token -->
  <circle cx="{cx}" cy="{cy}" r="12" fill="#fff" stroke="{COLOR}" stroke-width="3"/>
  <text x="{cx}" y="{cy+4}" font-family="monospace" font-size="11" fill="#000" text-anchor="middle" font-weight="bold">Sp</text>

  <!-- Title + labels -->
  <text x="20" y="30" font-family="monospace" font-size="18" fill="#fff" font-weight="bold">Spike — Life Plant gadget reticle</text>
  <text x="20" y="52" font-family="monospace" font-size="12" fill="#aab">card: Cactus_Cover   skill: CactusBonusSkillCover</text>
  <text x="20" y="70" font-family="monospace" font-size="12" fill="#aab">range: 22u  =  {RANGE_TILES:.2f} tiles (placement)</text>
  <text x="20" y="88" font-family="monospace" font-size="12" fill="#aab">projectile: Indirect (thrown, gravity 240) — arc, not direct-fire</text>
  <text x="20" y="106" font-family="monospace" font-size="12" fill="#aab">spawns: CactusCover (1750 HP, ~{CACTUS_RADIUS_TILES*2:.2f} tile collision)</text>
  <text x="20" y="124" font-family="monospace" font-size="12" fill="#aab">cooldown: 20s     charges: 1     heal: on death</text>
  <text x="20" y="142" font-family="monospace" font-size="12" fill="{HEAL_COLOR}">heal-burst: {HEAL_RADIUS_TILES:.2f} tile radius, -30 dmg = heal (scales w/ HP)</text>

  <text x="20" y="{CANVAS - 20}" font-family="monospace" font-size="10" fill="#666">1 tile = {TILE_PX}px  |  reticle type = "indirect placement" (same family as throwers)</text>
</svg>'''

out = Path(__file__).parent / 'spike_lifeplant_reticle.svg'
out.write_text(svg)
print(f'wrote {out} ({len(svg):,} bytes)')
