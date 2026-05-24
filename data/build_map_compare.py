"""Generate maps_compare.html — CSV tile grid (SVG) side-by-side with the
Brawlify PNGs for each ranked map. Click a thumbnail to pair it; export the
bridge from the top bar."""

import csv
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

CSV_MODE_TO_BRAWLIFY = {
    "Bounty": "Bounty",
    "BrawlBall": "Brawl Ball",
    "GemGrab": "Gem Grab",
    "Heist": "Heist",
    "KingOfHill": "Hot Zone",
    "Knockout": "Knockout",
    "BrawlHockey": "Brawl Hockey",
}

OPEN_BG = "#7fb56a"
TILE_COLOR = {
    "M": "#2c1d12",  # Wall1 — dark brown
    "X": "#3c2a1a",  # Wall2
    "Y": "#c08a3a",  # Crate
    "C": "#a36028",  # Barrel
    "I": "#1a1a1a",  # Indestructible — near black
    "F": "#1f6f3a",  # Forest (bush) — dark green
    "R": "#256b34",  # RespawningForest
    "W": "#2870c0",  # Water — bright blue
    "T": "#7a5a3a",  # Themed
    "B": "#d97a4c",  # Fragile
    "N": "#6b4a26",  # Fence
    "J": "#1a1a1a",  # InvisibleIndestructible
    "V": "#2870c0",  # InvisibleWater
    "E": "#5a3a1a",  # IndestructibleFence
    "a": "#a07840",  # RopeFence
    "b": "#5e5e5e",  # PayloadTrack
    "o": "#e8e8e8",  # Bouncer
    "x": "#d62828",  # Damage
    "z": "#3aa3c0",  # Slow
    "w": "#f4c430",  # Fast
    "v": "#a02828",  # IntervalDamage
    "S": "#f0f4f8",  # Snow
    "q": "#a4def5",  # Ice
    "1": "#1f7ad6",  # team1 spawn — blue
    "2": "#e63946",  # team2 spawn — red
    "c": "#f7d340",  # gem spawn / token
}


def hex_color_for(ch: str) -> str:
    if ch in TILE_COLOR:
        return TILE_COLOR[ch]
    if ch.isdigit():
        return "#e63946"  # other digit = objective marker
    # exotic chars (È/É/Ê/Ë/À/Á/Â/Ã and others) — neutral
    return "#94a3b8"


def render_grid_svg(grid, max_px=560, min_cell=14):
    h = len(grid)
    w = max(len(r) for r in grid) if grid else 0
    if w == 0 or h == 0:
        return ""
    cell = max(min_cell, min(max_px // max(w, h), 24))
    width = cell * w
    height = cell * h
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" shape-rendering="crispEdges">']
    parts.append(f'<rect width="{width}" height="{height}" fill="{OPEN_BG}"/>')
    for y, row in enumerate(grid):
        for x, ch in enumerate(row):
            if ch == ".":
                continue
            color = hex_color_for(ch)
            parts.append(f'<rect x="{x*cell}" y="{y*cell}" width="{cell}" height="{cell}" fill="{color}"/>')
    parts.append("</svg>")
    return "".join(parts)


def load_ranked():
    with (REPO / "data/csv_logic/ranked_locations.csv").open(newline="") as f:
        r = csv.reader(f); next(r); next(r)
        names = [row[0] for row in r if row and row[0]]
    with (REPO / "data/csv_logic/locations.csv").open(newline="") as f:
        r = csv.reader(f); headers = next(r); next(r)
        rows = list(r)
    idx = {h: i for i, h in enumerate(headers)}
    out = []
    for n in names:
        m = next(row for row in rows if row[idx["Name"]] == n)
        out.append({
            "locationName": n,
            "tid": m[idx["TID"]],
            "csvMode": m[idx["GameModeVariation"]],
            "brawlifyMode": CSV_MODE_TO_BRAWLIFY.get(m[idx["GameModeVariation"]]),
            "mapInternal": m[idx["Map"]],
            "credit": m[idx["CommunityCredit"]],
        })
    return out


def load_brawlify_active():
    payload = json.loads((REPO / "data/brawlify/maps.json").read_text())
    return [m for m in payload["data"]["list"] if not m.get("disabled")]


def load_csv_grids():
    payload = json.loads((REPO / "data/maps-all.json").read_text())
    return payload["maps"]


def load_automatches():
    path = REPO / "data/map_name_map.json"
    if not path.exists():
        return {}, {}
    payload = json.loads(path.read_text())
    by_internal = {}
    confidence = {}
    for entry in payload.get("matchAudit", []):
        if entry.get("brawlifyHash"):
            by_internal[entry["internal"]] = entry["brawlifyHash"]
            confidence[entry["internal"]] = entry.get("confidence", "med")
    return by_internal, confidence


def build_html(ranked, brawlify, grids):
    automatches, confidence = load_automatches()
    cards = []
    for r in ranked:
        grid_entry = grids.get(r["mapInternal"], {})
        grid = grid_entry.get("grid", [])
        svg = render_grid_svg(grid)
        candidates = [m for m in brawlify if (m.get("gameMode") or {}).get("name") == r["brawlifyMode"]]
        auto_hash = automatches.get(r["mapInternal"])
        conf = confidence.get(r["mapInternal"], "")
        thumbs = []
        for c in candidates:
            img_path = f"../assets/maps/{c['hash']}.png"
            credit_badge = f' <small style="color:#888">credit: {c["credit"]}</small>' if c.get("credit") else ''
            auto_badge = ''
            data_auto = ''
            if auto_hash and c["hash"] == auto_hash:
                auto_badge = f' <span class="auto-flag conf-{conf}">auto: {conf}</span>'
                data_auto = ' data-auto="1"'
            thumbs.append(
                f'<button class="thumb" data-hash="{c["hash"]}" data-name="{c["name"]}" '
                f'data-internal="{r["mapInternal"]}" title="{c["name"]}"{data_auto}>'
                f'<img loading="lazy" src="{img_path}" alt="{c["name"]}"/>'
                f'<div class="lbl">{c["name"]}{credit_badge}{auto_badge}</div>'
                f'</button>'
            )
        cards.append(f'''
        <section class="card conf-{conf}" data-internal="{r["mapInternal"]}">
          <header>
            <h2>{r["mapInternal"]} <small>({r["csvMode"]} → {r["brawlifyMode"]})</small>
              {'<span class="auto-flag conf-' + conf + '">auto-matched: ' + conf + '</span>' if auto_hash else ''}
            </h2>
            <div class="meta">TID: <code>{r["tid"]}</code>{' · credit: <b>' + r["credit"] + '</b>' if r["credit"] else ''}</div>
            <div class="picked" data-internal="{r["mapInternal"]}">No match selected</div>
          </header>
          <div class="row">
            <div class="csv-side">
              <h3>CSV tile grid ({grid_entry.get("width","?")}×{grid_entry.get("height","?")})</h3>
              {svg}
            </div>
            <div class="bf-side">
              <h3>Brawlify candidates ({len(candidates)})</h3>
              <div class="thumbs">{"".join(thumbs)}</div>
            </div>
          </div>
        </section>
        ''')

    html = f'''<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"/>
<title>brawl-digram · map bridge curator</title>
<style>
  body {{ font-family: -apple-system, system-ui, sans-serif; background:#070b13; color:#dde; margin:0; padding:24px; }}
  h1 {{ margin:0 0 8px 0; }}
  header.top {{ position:sticky; top:0; background:#070b13; padding:12px 0; border-bottom:1px solid #233; z-index:10; }}
  .card {{ border:1px solid #233; border-radius:8px; padding:16px; margin:24px 0; background:#0c1320; }}
  .card header h2 {{ margin:0; font-size:18px; }}
  .card header h2 small {{ color:#789; font-weight:normal; }}
  .meta {{ font-size:12px; color:#9ab; margin:4px 0; }}
  .picked {{ font-size:13px; color:#5d8; margin:6px 0; min-height:1.2em; }}
  .picked.set {{ color:#7fc; font-weight:bold; }}
  .row {{ display:flex; gap:24px; margin-top:12px; }}
  .csv-side, .bf-side {{ flex:1; min-width:0; }}
  .csv-side svg {{ background:{OPEN_BG}; border:1px solid #233; display:block; max-width:100%; height:auto; }}
  .thumbs {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(140px,1fr)); gap:10px; }}
  .thumb {{ background:#0a1726; border:2px solid transparent; border-radius:6px; padding:6px; cursor:pointer; color:inherit; font:inherit; text-align:center; }}
  .thumb:hover {{ border-color:#467; }}
  .thumb.selected {{ border-color:#5fd; background:#163148; }}
  .thumb[data-auto="1"] {{ outline:2px dashed #f6c64a; outline-offset:1px; }}
  .auto-flag {{ display:inline-block; font-size:10px; padding:1px 6px; border-radius:3px; margin-left:6px; vertical-align:middle; font-weight:bold; }}
  .auto-flag.conf-high {{ background:#1f6f3a; color:#cfe9c4; }}
  .auto-flag.conf-med  {{ background:#a0791f; color:#fff4d0; }}
  .auto-flag.conf-low  {{ background:#a32828; color:#ffe0d0; }}
  section.card.conf-low {{ border-color:#a32828; }}
  .thumb img {{ width:100%; height:auto; display:block; border-radius:4px; }}
  .lbl {{ font-size:11px; margin-top:4px; color:#cde; }}
  .lbl small {{ display:block; color:#789; }}
  button.export {{ background:#5fd; color:#001; border:0; padding:8px 14px; border-radius:6px; font-weight:bold; cursor:pointer; }}
  pre.out {{ background:#000; padding:12px; border-radius:6px; max-height:30vh; overflow:auto; font-size:12px; }}
  .progress {{ color:#9ab; font-size:13px; }}
</style>
</head><body>
<header class="top">
  <h1>map_name_map.json curator</h1>
  <div>Click a Brawlify thumbnail to pair it with the CSV map shown to its left. Selections persist in localStorage.</div>
  <div style="margin-top:8px"><span class="progress" id="progress">0 / {len(ranked)} matched</span>
    &nbsp; <button class="export" id="exportBtn">Copy bridge JSON</button>
    &nbsp; <button id="clearBtn">Clear all</button>
  </div>
  <pre class="out" id="out" hidden></pre>
</header>
{"".join(cards)}
<script>
const STORE_KEY = 'brawl-digram-map-bridge-v1';
const TOTAL = {len(ranked)};
const AUTOMATCH = {json.dumps(automatches)};

function load() {{
  try {{
    const stored = JSON.parse(localStorage.getItem(STORE_KEY));
    if (stored) return stored;
  }} catch {{}}
  // First visit: seed from auto-matches.
  return {{...AUTOMATCH}};
}}
function save(s) {{ localStorage.setItem(STORE_KEY, JSON.stringify(s)); }}

function render() {{
  const state = load();
  document.querySelectorAll('.thumb').forEach(b => {{
    const internal = b.dataset.internal;
    b.classList.toggle('selected', state[internal] === b.dataset.hash);
  }});
  document.querySelectorAll('.picked').forEach(el => {{
    const internal = el.dataset.internal;
    if (state[internal]) {{
      el.classList.add('set');
      el.textContent = 'matched → ' + state[internal];
    }} else {{
      el.classList.remove('set');
      el.textContent = 'No match selected';
    }}
  }});
  document.getElementById('progress').textContent =
    Object.keys(state).length + ' / ' + TOTAL + ' matched';
}}

document.querySelectorAll('.thumb').forEach(b => {{
  b.addEventListener('click', () => {{
    const state = load();
    const internal = b.dataset.internal;
    if (state[internal] === b.dataset.hash) delete state[internal];
    else state[internal] = b.dataset.hash;
    save(state);
    render();
  }});
}});

document.getElementById('exportBtn').addEventListener('click', () => {{
  const state = load();
  // invert: brawlifyHash -> internalName
  const inverted = {{}};
  for (const [internal, hash] of Object.entries(state)) inverted[hash] = internal;
  const text = JSON.stringify(inverted, null, 2);
  navigator.clipboard.writeText(text).catch(() => {{}});
  const out = document.getElementById('out');
  out.hidden = false;
  out.textContent = text;
}});

document.getElementById('clearBtn').addEventListener('click', () => {{
  if (confirm('Clear all selections?')) {{ localStorage.removeItem(STORE_KEY); render(); }}
}});

render();
</script>
</body></html>'''
    return html


def run():
    ranked = load_ranked()
    bf = load_brawlify_active()
    grids = load_csv_grids()
    html = build_html(ranked, bf, grids)
    out = REPO / "data" / "maps_compare.html"
    out.write_text(html)
    print(f"wrote {out.relative_to(REPO)} ({out.stat().st_size/1024:.0f} KB)")
    print(f"  ranked maps: {len(ranked)}")
    print(f"  brawlify candidates spanning ranked modes: {len([m for m in bf if (m.get('gameMode') or {}).get('name') in CSV_MODE_TO_BRAWLIFY.values()])}")
    print(f"  open it with:  open {out}")


if __name__ == "__main__":
    run()
