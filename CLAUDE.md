# brawl-digram

A **collaborative** Brawl Stars drafting + whiteboard tool with an agentic advisor backed by pro-curated per-map knowledge. See `ROADMAP.md` for the full plan.

## Layout

- `data/csv_logic/` — Brawl Stars game CSVs (v67.264, ~18 MB). Source of truth for brawler/skill/projectile/card geometry. Re-pull from the [tailsjs mirror](https://github.com/tailsjs/brawl-stars-assets) for new versions.
- `data/shelly_reticles.svg` + `data/render_shelly_reticles.py` — reticle math reference / validation.
- `data/kb/` — pro-curated per-map knowledge base (Phase 2; doesn't exist yet).
- `.claude/agents/` — specialized subagent definitions.

## Subagents

- `frontend` — collaborative whiteboard UI (Konva/PixiJS canvas + Y.js)
- `backend` — Y.js sync server (Phase 1), LLM serving + API (Phase 2)
- `data-loader` — CSV→JSON pipeline + KB schema work
- `pro-curator` — pro player outreach + per-map KB curation
- `ml-researcher` — Phase 3 ML draft model (research-only, heavily gated)
- `content` — creator / social outreach for visibility

The main conversation is the **orchestrator**. Delegate concrete work to the agent that owns the area.

## Critical data facts

- **Units (user-facing):** EVERYTHING is in **tiles** in `brawlers.json`, KB entries, advisor prompts, and frontend code. The data-loader normalizes raw CSV units at the boundary. Field names bake in their unit: `rangeTiles`, `radiusTiles`, `spreadDeg`, `cooldownSec`. If you see raw `/3` or `/480` math outside the loader, that's a bug.
- **Units (raw CSV, loader-only):** Two precision systems — `CastingRange / 3 = tiles` (player-facing range, coarse), everything else uses internal 480-units-per-tile: `area_effects.Radius / 480`, `projectiles_logic.Radius / 480`, `CollisionRadius / 480`. `Spread` is already degrees. The /480 divisor is verified against ≥5 known in-game values (Spike super, Emz super, Bo/Dyna splash, brawler hitboxes) — all match within ~5%.
- **Internal names ≠ display names:** Shelly is `ShotgunGirl`, Emz is `Mummy`, etc. Look up via `characters.csv`.
- **Hypercharges are separate skill rows**, linked via `cards.csv` entries with `MetaType=6` / `Type=overcharge_*`. Many hypercharges are pure stat multipliers and don't change the reticle.
- **`projectiles.csv` doesn't exist anymore** — split in newer versions into `projectiles_logic.csv` (mechanics) and `projectiles_skin.csv` (visuals). Older modding tutorials are stale.

## Strategic decisions made (2026-05-18)

- **Headline feature is collaborative whiteboard**, not just a drafter. Y.js for CRDTs.
- **Advisor is LLM + pro-curated KB**, not pure ML. Open-source LLM (Llama 3.1 / Qwen 2.5 class) for cost.
- **Pure ML draft model deprioritized** to Phase 3 and gated on pick-order reconstruction (Brawl Stars API doesn't expose pick order).

## Stack decisions (locked 2026-05-22)

- **Frontend framework:** Next.js (App Router).
- **Canvas:** PixiJS via `@pixi/react v8`. WebGL-backed, scales fine for the 10-20-token / ~1000-tile scenes we render, and "I built it on WebGL" is better resume signal than "I used a 2D library."
- **CRDT:** Y.js + `y-websocket` (self-hosted sync server, Node, Fly.io). Free, battle-tested (Notion, Tldraw, JupyterLite); deferred until after the static whiteboard renders. Liveblocks rejected because it's lower resume signal and costs more at scale.
- **Hosting:** Vercel for the Next.js app (free tier OK for v1). Fly.io for the Y.js sync server (~$5/mo).

## Reticle rendering (current state)

- All 85 playable brawlers have generated SVGs in `data/reticles/<BrawlerHash>.svg` + an `index.html` gallery. Each shows attack / super / hyper variants (purple) / gadgets / alt-forms.
- Classifier in `data/render_all_reticles.py` infers one of 9 shape primitives per skill from the CSVs: cone, line, dash, placement, wave, cluster (quincunx/plus/triangle/pair/hexagon), area-follow, self-aoe.
- 38 per-skill overrides in `data/reticle_overrides.json` for cases where the data-driven classifier gets the shape wrong (e.g., Barley super = quincunx, Tara Black Hole = placement, Amber attack = line). Each entry has a `note` field with reasoning + source URL.
- 20 newest brawlers (Starr-Nova, Damian, Najia, Sirius, Glowy, Ziggy, Mina, Jae-Yong, etc.) are absent — they post-date the v67.264 CSV dump.
- The Python renderer needs to be ported / baked into a `brawlers.json` for the frontend. That's the next concrete step.

## Visual convention for reticles

- **Color:** default white; hypercharge variants purple (`#c084fc`).
- **Circular shapes** (cone, circle, placement splash): hard outer edge + inward white gradient fade from all edges (matches in-game Brawl Stars).
- **Rectangular shapes** (line, dash): uniform translucent white fill (~65 % opacity), no separate border.
- **Trajectory hints** (throwers, placement): single straight dotted line from brawler to landing center (NOT a parabolic arc; stops at the splash center, doesn't extend past).

## License

All extracted assets are Supercell IP, usable under the [Supercell Fan Content Policy](https://www.supercell.com/fan-content-policy) — non-commercial only until reviewed.
