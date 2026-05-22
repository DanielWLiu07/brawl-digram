# brawl-digram roadmap

A **collaborative** drafting + whiteboard tool for Brawl Stars, backed by an agentic advisor that draws on pro-curated per-map knowledge. Like Figma for Brawl drafting.

## Vision pivots (decided 2026-05-18)

After ML feasibility research:
1. **Collaborative whiteboard is the headline feature** — not just a draft picker. Coaches drafting with teams, creators using it live, training rooms. This is what makes it different.
2. **Agentic advisor uses an open-source LLM + pro-curated KB**, not pure ML. Strategies are too map-and-mode-specific for ML data volume to ever cover the long tail (25 maps × 6 modes × 80 brawlers ≈ 12k cells). Pros encode tacit knowledge into a structured KB; the LLM combines it with current draft state.
3. **Pure ML draft model is deprioritized.** Phase 3 only if Phase 2 plateaus AND we can reconstruct pick order from the API (Supercell doesn't return it directly — see [[constraints]] below). Honest assessment: the hybrid may make ML unnecessary.

## Three pillars (revised priority)

1. **Collaborative whiteboard** — drag brawlers onto tile-accurate maps, see attack reticles, multiple users in the same room in real time.
2. **Agentic advisor** — open-source LLM (Llama 3.1 8B / Qwen 2.5 7B class on Groq or self-hosted) reading a pro-curated per-map knowledge base + current draft state.
3. **ML draft model** — gated, may never be built.

## Phases

### Phase 1 — Collaborative whiteboard MVP (~6 weeks)
**Owner agents:** `data-loader`, `frontend`, `backend` (activates here for sync server)

**Stack** (decided 2026-05-22): **Next.js + PixiJS via `@pixi/react v8` + Y.js + `y-websocket`.** See CLAUDE.md for rationale.

**Pre-coding data prep:**
- [x] Reticle renderer for all 85 brawlers (`data/render_all_reticles.py`, generates `data/reticles/*.svg`).
- [x] 38 per-skill reticle overrides (`data/reticle_overrides.json`) from research across all brawlers.
- [ ] **Bake `data/brawlers.json`** — extract the Python classifier's output as a static JSON the frontend can `import`. One entry per brawler with all variants (attack/super/hyper/gadgets) and their shape primitives + tile-unit params.
- [ ] **Decode ranked-pool maps → `data/maps.json`** — single-char encoding in `maps.csv` → 2D tile arrays. Filter to ~25 current ranked maps using Brawlify's ranked-pool field.
- [ ] **Hand-curated `data/map-name-map.json`** — bridge between Brawlify display names ("Hard Rock Mine", id 15000051) and internal `maps.csv` names ("Gemgrab_42").

**Frontend scaffold:**
- [ ] `npx create-next-app brawl-digram-web` (App Router, TypeScript).
- [ ] Install `pixi.js`, `@pixi/react`, `yjs`, `y-websocket`, `y-protocols`.
- [ ] Asset folder pipeline: copy `assets/` → `brawl-digram-web/public/assets/`. Brawler portraits, gadgets, star powers, maps from Brawlify mirror.
- [ ] Static single-map renderer with PixiJS (one map, no interactivity).
- [ ] Brawler token placement (drag-drop, snap-to-tile).
- [ ] Reticle overlay (read `brawlers.json`, render per current selection — white for base, purple for hyper).
- [ ] UI for picking brawlers / toggling attack vs super vs gadget reticle.
- [ ] **Map builder mode** — paint tiles from a palette, save custom layouts.

**Sync server (do after the static whiteboard works):**
- [ ] Spin up `y-websocket` sync server (Node, separate repo, ~50 lines).
- [ ] Deploy to Fly.io with persistent volume (SQLite stores room snapshots).
- [ ] Wire frontend ↔ sync server with awareness API (live cursors, selection state).
- [ ] Room URLs (`/r/{room-id}`) + persistence (room state survives all-users-leave).

**Background tracks (in parallel with frontend coding):**
- [ ] `backend` cron: weekly fetch of Brawlify ranked pool → `data/ranked-rotation.json`.
- [ ] `pro-curator` drafts first 3-5 outreach DMs (review before sending).
- [ ] `content` drafts first build-in-public posts (r/Brawlstars, Twitter).
- [ ] Refresh `data/csv_logic/` from a newer tailsjs version to pick up the 20 missing newest brawlers.

**Done = two people in different cities can build a "what if we play this draft on this ranked map" scene together in their browsers, on any current-season ranked map, with the option to use custom user-built maps.**

### Phase 2 — Agentic advisor with pro-curated KB (~3 months)
**Owner agents:** `pro-curator` (recruits + builds KB), `backend` (LLM serving), `data-loader` (KB schema)

- [ ] `pro-curator` recruits first 3–5 pros, designs KB JSON schema for per-map knowledge.
- [ ] Build initial KB for the most-played 5 ranked maps.
- [ ] `backend` integrates Brawl Stars Official API (player lookup, recent battles, tier list snapshot).
- [ ] Wire open-source LLM (Groq for cheap inference; fall back to self-hosted if cost scales).
- [ ] Advisor takes: current draft state + map + KB entry + tier list → returns recommendations with explanation.
- [ ] UI: "ask the advisor" panel beside the whiteboard.
- [ ] Expand KB to all maps; pros maintain through balance patches.

**Done = on any current ranked map, the advisor gives recommendations that match what a top pro would suggest, with citations to the KB.**

### Phase 3 — ML draft model (GATED, may never ship)
**Owner agent:** `ml-researcher`

**Gates that must clear before any model training:**
- Phase 2 advisor is shipped and we can measure where it falls short.
- Pick-order reconstructor from API battle logs hits ≥80% accuracy validated against manually-labeled replays. **If it doesn't, abandon Phase 3.**
- Heuristic + LLM advisor has plateaued on whatever metric we care about (win-rate improvement of suggested picks vs baseline).

**If gates clear:** transformer over draft state with two heads (win-prob + next-pick), 1-ply expectimax at inference for counter-pick risk. See `ml-researcher` agent file for the full architecture brief.

## Cross-cutting tracks

### Pro recruitment + KB curation (parallel to Phase 1 — start now)
**Owner agent:** `pro-curator`

Highest-leverage track. The KB is what makes Phase 2 work; building it requires real relationships with pros and a schema that captures their knowledge without being a chore to fill in.

- [ ] First 5 pro contacts identified + initial DMs drafted.
- [ ] KB schema v1 designed and reviewed with 1–2 willing pros.
- [ ] Working agreement: what pros get in exchange (early access, attribution, optional revenue share).

### Creator / social outreach (parallel to Phase 1)
**Owner agent:** `content`

Distinct from pro recruitment — this is broader (YouTubers, streamers, Reddit, Discord).

- [ ] Target list: 20 creators + key subreddits/discords.
- [ ] Build-in-public posts as Phase 1 ships milestones.
- [ ] Demo video script once whiteboard collab is working.

### Licensing
- All extracted CSV data and any sprites are Supercell IP, used under the [Supercell Fan Content Policy](https://www.supercell.com/fan-content-policy).
- Non-commercial only without explicit Supercell approval. Defer monetization decisions.

## Agent setup

Subagent definitions live in `.claude/agents/`:

- `frontend` — collaborative whiteboard UI (canvas + Y.js)
- `backend` — sync server, API, LLM serving (active from Phase 1)
- `data-loader` — CSV→JSON pipeline + KB schema
- `pro-curator` — pro outreach + per-map KB curation
- `ml-researcher` — Phase 3 planning (research-only; gated heavily)
- `content` — creator/social outreach for visibility

The orchestrator is the main Claude Code conversation. To work in literal parallel terminal panes, open new iTerm/tmux panes and run `claude` in each — agent files are auto-discovered in every session.

## Current state (2026-05-18)

- Git repo initialized, `main` branch, nothing committed yet.
- Game data: `data/csv_logic/` (v67.264, 116 CSVs, 18 MB).
- Reticle render validated for Shelly: `data/shelly_reticles.svg` + `data/render_shelly_reticles.py`.
- Schema discovery + ML research saved to project memory.
