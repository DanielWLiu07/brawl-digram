"""Generate prototype/tile_review.html — a static grid of all extracted tile
sprites with click-to-mark UI for triaging the ones the auto-segmentation
got wrong."""

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SPRITES = REPO / "data" / "tile_sprites"
OUT = REPO / "prototype" / "tile_review.html"

manifest_path = SPRITES / "_manifest.json"
manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else None
if manifest:
    sprite_records = manifest["sprites"]
else:
    sprite_records = [{"name": p.name, "atlas_x": 0, "atlas_y": 0,
                       "width": 0, "height": 0} for p in sorted(SPRITES.glob("*.png"))]

html = f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"/>
<title>tile sprite review · brawl-digram</title>
<style>
  :root {{ color-scheme: dark; }}
  body {{ margin:0; padding:16px; font-family:-apple-system,system-ui,sans-serif; background:#0a0f17; color:#dde; }}
  header {{ position:sticky; top:0; background:#0a0f17; padding-bottom:12px; border-bottom:1px solid #233; margin-bottom:16px; z-index:10; }}
  h1 {{ margin:0 0 6px; font-size:18px; }}
  .hint {{ font-size:12px; color:#789; line-height:1.5; }}
  .controls {{ margin-top:10px; display:flex; gap:10px; align-items:center; flex-wrap:wrap; }}
  button {{ background:#16202f; color:#dde; border:1px solid #2a3b52; padding:6px 12px; border-radius:6px; cursor:pointer; font:inherit; font-size:12px; }}
  button.primary {{ background:#5fd; color:#001; border-color:#5fd; font-weight:bold; }}
  button.danger {{ border-color:#a33; }}
  .progress {{ font-size:12px; color:#9ab; }}
  .progress b {{ color:#cde; }}
  .legend {{ display:inline-flex; gap:14px; font-size:11px; }}
  .legend .sw {{ display:inline-block; width:10px; height:10px; border-radius:2px; margin-right:4px; vertical-align:middle; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(140px,1fr)); gap:10px; }}
  .card {{ background:#0c1422; border:2px solid transparent; border-radius:6px; padding:8px; cursor:pointer; text-align:center; user-select:none; }}
  .card:hover {{ background:#13202f; }}
  .card.ok      {{ border-color:#1f6f3a; }}
  .card.merged  {{ border-color:#a32828; }}
  .card.split   {{ border-color:#f6c64a; }}
  .card.ignore  {{ border-color:#456; opacity:0.4; }}
  .card img    {{ max-width:100%; max-height:120px; image-rendering:pixelated; display:block; margin:0 auto; }}
  .card .name {{ font-size:10px; color:#9ab; margin-top:6px; word-break:break-all; }}
  .card .badge{{ display:inline-block; font-size:9px; padding:1px 5px; border-radius:3px; margin-top:4px; text-transform:uppercase; letter-spacing:.04em; }}
  .badge.ok     {{ background:#0e3b2a; color:#5fd; }}
  .badge.merged {{ background:#3b0e0e; color:#ff8888; }}
  .badge.split  {{ background:#3b2a0e; color:#f6c64a; }}
  .badge.ignore {{ background:#222; color:#789; }}
  pre.out {{ background:#000; color:#cde; padding:12px; border-radius:6px; max-height:30vh; overflow:auto; font-size:11px; margin-top:10px; }}
</style>
</head><body>
<header>
  <h1>tile sprite review — 155 auto-segmented sprites from <code>level.sc</code></h1>
  <div class="hint">
    Click a tile to cycle: <b>unmarked → ok → merged → badcut → ignore → unmarked</b>.
    <ul style="margin:6px 0; padding-left:18px">
      <li><b>ok</b>: clean single sprite, boundaries look right</li>
      <li><b>merged</b>: two or more sprites are inside one crop and need separating</li>
      <li><b>badcut</b>: this crop slices through a real sprite, OR is only a piece of a bigger sprite that got split — boundary is in the wrong place</li>
      <li><b>ignore</b>: not actually a tile (UI element, fragment, noise)</li>
    </ul>
    Selections persist in localStorage. Press <b>Export</b> when done to copy the JSON.
  </div>
  <div class="controls">
    <span class="progress" id="progress">0 / {len(files)} marked</span>
    <span class="legend">
      <span><span class="sw" style="background:#1f6f3a"></span>ok</span>
      <span><span class="sw" style="background:#a32828"></span>merged</span>
      <span><span class="sw" style="background:#f6c64a"></span>split</span>
      <span><span class="sw" style="background:#456"></span>ignore</span>
    </span>
    <button class="primary" id="exportBtn">Export JSON</button>
    <button class="danger" id="clearBtn">Clear all marks</button>
  </div>
  <pre class="out" id="out" hidden></pre>
</header>

<div class="grid" id="grid">
{"".join(
    f'<div class="card" data-name="{r["name"]}" data-x="{r["atlas_x"]}" data-y="{r["atlas_y"]}" data-w="{r["width"]}" data-h="{r["height"]}">'
    f'<img loading="lazy" src="/data/tile_sprites/{r["name"]}" alt="{r["name"]}"/>'
    f'<div class="name">{r["name"]}</div>'
    f'<div class="pos">@ {r["atlas_x"]},{r["atlas_y"]} · {r["width"]}×{r["height"]}</div>'
    f'<div class="badge"></div></div>' for r in sprite_records)}
</div>

<script>
const STORE = "brawl-digram-tile-review-v1";
const STATES = ["", "ok", "merged", "split", "ignore"];
const load = () => {{ try {{ return JSON.parse(localStorage.getItem(STORE)) || {{}}; }} catch {{ return {{}}; }} }};
const save = (s) => localStorage.setItem(STORE, JSON.stringify(s));

function render() {{
  const state = load();
  document.querySelectorAll(".card").forEach(c => {{
    const s = state[c.dataset.name] || "";
    c.className = "card" + (s ? " " + s : "");
    const badge = c.querySelector(".badge");
    badge.className = "badge" + (s ? " " + s : "");
    badge.textContent = s;
  }});
  const marked = Object.values(state).filter(Boolean).length;
  document.getElementById("progress").innerHTML = `<b>${{marked}}</b> / ${len(files)} marked`;
}}
document.querySelectorAll(".card").forEach(c => {{
  c.addEventListener("click", () => {{
    const state = load();
    const cur = state[c.dataset.name] || "";
    const i = STATES.indexOf(cur);
    const next = STATES[(i + 1) % STATES.length];
    if (next) state[c.dataset.name] = next; else delete state[c.dataset.name];
    save(state); render();
  }});
}});
document.getElementById("exportBtn").addEventListener("click", () => {{
  const state = load();
  const grouped = {{ ok: [], merged: [], split: [], ignore: [], unmarked: [] }};
  document.querySelectorAll(".card").forEach(c => {{
    const s = state[c.dataset.name] || "unmarked";
    grouped[s].push(c.dataset.name);
  }});
  const text = JSON.stringify(grouped, null, 2);
  navigator.clipboard.writeText(text).catch(() => {{}});
  const out = document.getElementById("out");
  out.hidden = false; out.textContent = text;
}});
document.getElementById("clearBtn").addEventListener("click", () => {{
  if (confirm("Clear all marks?")) {{ localStorage.removeItem(STORE); render(); }}
}});
render();
</script>
</body></html>
"""

OUT.write_text(html)
print(f"wrote {OUT.relative_to(REPO)} — {len(files)} sprites in grid")
print(f"open with: http://localhost:8753/prototype/tile_review.html")
