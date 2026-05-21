import csv, math
from pathlib import Path

CSV = Path(__file__).parent / 'csv_logic'

def load(name):
    with open(CSV / name) as f:
        return list(csv.DictReader(f))[1:]

skills = load('skills.csv')
def get(n): return next(r for r in skills if r['Name']==n)

# (label, skill_name, shape, tag_color)
# tag_color is only used on the token rim so we can distinguish variants in this demo;
# the reticle itself is white (the in-game default). Per-brawler color override is an editor feature.
VARIANTS = [
    ('Base attack',                 'ShotgunGirlWeapon',            'cone', '#ff6b35'),
    ('Super',                       'ShotgunGirlUlti',              'cone', '#ffd23f'),
    ('Hypercharged attack',         'ShotgunGirlOverchargedWeapon', 'cone', '#b14aff'),
    ('Gadget: Clay Pigeons',        'ShotgunGirlClayPigeons',       'cone', '#4ade80'),
    ('Gadget: Fast Forward (Dash)', 'ShotgungirlGadgetSkillReload', 'dash', '#4ade80'),
]

TILE_PX = 25
PANEL = 400
PAD = 20
TITLE_H = 40
COLS, ROWS = 3, 2
CANVAS_W = COLS * PANEL + (COLS+1) * PAD
CANVAS_H = ROWS * PANEL + (ROWS+1) * PAD + TITLE_H

# In-game Brawl Stars reticles have a HARD SHARP OUTER EDGE (no blur) with a
# RADIAL GRADIENT INSIDE that fades from white at the perimeter inward to fully
# transparent at the brawler position. Verified against an in-game screenshot
# 2026-05-20 (Kenji sweep attack). The fade is contained within the shape — the
# outside of the outer edge is hard and crisp, not glowing outward.
OUTER_STROKE_OPACITY = 0.95
OUTER_STROKE_WIDTH = 3.0
# Radial gradient stops (offset, opacity) — applied to wedge fill,
# anchored at brawler vertex with r=range_px in userSpaceOnUse.
FADE_STOPS = [
    (0.00, 0.00),  # brawler position: fully transparent
    (0.50, 0.00),  # inner half: still essentially transparent
    (0.78, 0.28),  # transition zone
    (0.94, 0.65),  # bright near the outer arc
    (1.00, 0.90),  # peak white right before the hard edge
]

def wedge(cx, cy, r, spread, direction=-90):
    half = spread / 2
    a1, a2 = math.radians(direction - half), math.radians(direction + half)
    x1, y1 = cx + r*math.cos(a1), cy + r*math.sin(a1)
    x2, y2 = cx + r*math.cos(a2), cy + r*math.sin(a2)
    large = 1 if spread > 180 else 0
    return f"M {cx},{cy} L {x1:.1f},{y1:.1f} A {r},{r} 0 {large},1 {x2:.1f},{y2:.1f} Z"

def grid(px, py, w, h):
    out = [f'<rect x="{px}" y="{py}" width="{w}" height="{h}" fill="#0f1320"/>']
    for x in range(0, w+1, TILE_PX):
        out.append(f'<line x1="{px+x}" y1="{py}" x2="{px+x}" y2="{py+h}" stroke="#1e2538" stroke-width="0.5"/>')
    for y in range(0, h+1, TILE_PX):
        out.append(f'<line x1="{px}" y1="{py+y}" x2="{px+w}" y2="{py+y}" stroke="#1e2538" stroke-width="0.5"/>')
    return '\n'.join(out)

def render_cone(cx, cy, range_px, spread_deg, gid):
    """All three edges (arc + 2 sides) glow white and fade inward to transparent center.
    Technique: clip-path = the wedge, then a thick blurred stroke INSIDE the clip
    creates an inward-only band along every edge. A separate unblurred outer stroke
    provides the crisp hard outline."""
    path = wedge(cx, cy, range_px, spread_deg)
    band_w = range_px * 0.22         # thinner inward stroke — keeps the interior mostly transparent
    blur_std = band_w / 4            # softens the inner edge into a gradient
    return [
        f'<defs>'
        f'<clipPath id="clip-{gid}"><path d="{path}"/></clipPath>'
        f'<filter id="blur-{gid}" x="-30%" y="-30%" width="160%" height="160%">'
        f'<feGaussianBlur stdDeviation="{blur_std:.2f}"/>'
        f'</filter>'
        f'</defs>',
        # Inward band along ALL edges (arc + sides). Thick stroke is centered on
        # the path; the clip removes everything outside the wedge so only the
        # inward half remains, and the blur turns it into a gradient.
        f'<g clip-path="url(#clip-{gid})">'
        f'<path d="{path}" fill="none" stroke="white" stroke-width="{band_w}" stroke-opacity="0.5" stroke-linejoin="round" filter="url(#blur-{gid})"/>'
        f'</g>',
        # Hard, sharp outer outline (no blur, full opacity)
        f'<path d="{path}" fill="none" stroke="white" stroke-width="{OUTER_STROKE_WIDTH}" stroke-opacity="{OUTER_STROKE_OPACITY}" stroke-linejoin="round"/>'
    ]

def render_dash(cx, cy, length_px, gid):
    """Same all-edges-glow technique as the cone, applied to a rectangle.
    All four edges have an inward white fade; interior is transparent."""
    track_w = 28
    end_y = cy - length_px
    rect_path = f'M {cx-track_w/2},{end_y} h {track_w} v {length_px} h {-track_w} Z'
    # Smaller shape → use a finer band so the rectangle doesn't blow out
    band_w = min(track_w, length_px) * 0.3
    blur_std = band_w / 4
    rect_attrs = f'x="{cx-track_w/2}" y="{end_y}" width="{track_w}" height="{length_px}"'
    return [
        f'<defs>'
        f'<clipPath id="clip-{gid}"><rect {rect_attrs}/></clipPath>'
        f'<filter id="blur-{gid}" x="-30%" y="-30%" width="160%" height="160%">'
        f'<feGaussianBlur stdDeviation="{blur_std:.2f}"/>'
        f'</filter>'
        f'</defs>',
        f'<g clip-path="url(#clip-{gid})">'
        f'<rect {rect_attrs} fill="none" stroke="white" stroke-width="{band_w}" stroke-opacity="0.5" stroke-linejoin="miter" filter="url(#blur-{gid})"/>'
        f'</g>',
        f'<rect {rect_attrs} fill="none" stroke="white" stroke-width="{OUTER_STROKE_WIDTH}" stroke-opacity="{OUTER_STROKE_OPACITY}" stroke-linejoin="miter"/>'
    ]

def panel(px, py, label, skill_name, shape, tag_color):
    s = get(skill_name)
    range_units = int(s.get('CastingRange') or 0)
    spread_str = s.get('Spread') or ''
    spread_deg = int(spread_str) if spread_str.isdigit() else 0
    range_tiles = range_units / 3.0
    range_px = range_tiles * TILE_PX
    proj = s.get('Projectiles') or '(movement skill — no projectile)'

    cx, cy = px + PANEL/2, py + PANEL - 80
    parts = [grid(px, py, PANEL, PANEL)]

    gid = f'g-{skill_name}-{int(px)}-{int(py)}'
    if shape == 'cone':
        parts.extend(render_cone(cx, cy, range_px, spread_deg, gid))
        reticle_desc = f'cone — {range_tiles:.2f} tiles, {spread_deg}°'
    elif shape == 'dash':
        parts.extend(render_dash(cx, cy, range_px, gid))
        reticle_desc = f'dash — {range_tiles:.2f} tiles forward'

    # Shelly portrait — sized to roughly her in-game character footprint (~1 tile)
    # No lens highlight: in-game the reticle vertex is crisp at the brawler's feet.
    token_size = 32
    parts.append(f'<image href="../assets/brawlers/Shelly/portrait.png" x="{cx-token_size/2}" y="{cy-token_size/2}" width="{token_size}" height="{token_size}"/>')

    # Labels
    parts.append(f'<text x="{px+12}" y="{py+22}" font-family="monospace" font-size="13" fill="#fff" font-weight="bold">{label}</text>')
    parts.append(f'<text x="{px+12}" y="{py+40}" font-family="monospace" font-size="10" fill="#9ba3b8">skill: {skill_name}</text>')
    parts.append(f'<text x="{px+12}" y="{py+56}" font-family="monospace" font-size="10" fill="#9ba3b8">{reticle_desc}</text>')
    parts.append(f'<text x="{px+12}" y="{py+72}" font-family="monospace" font-size="10" fill="#9ba3b8">proj: {proj}</text>')
    return '\n'.join(parts)

panels = []
for i, (label, sn, shape, tag) in enumerate(VARIANTS):
    col, row = i % COLS, i // COLS
    px = PAD + col * (PANEL + PAD)
    py = PAD + TITLE_H + row * (PANEL + PAD)
    panels.append(panel(px, py, label, sn, shape, tag))

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {CANVAS_W} {CANVAS_H}" style="background:#0a0d18;font-family:sans-serif">
  <text x="{CANVAS_W/2}" y="28" text-anchor="middle" font-family="monospace" font-size="18" fill="#fff" font-weight="bold">Shelly — attack reticles (hard outer edge + inner radial fade to transparent)</text>
  {''.join(panels)}
</svg>'''

out = Path(__file__).parent / 'shelly_reticles.svg'
out.write_text(svg)
print(f'wrote {out} ({len(svg):,} bytes)')
