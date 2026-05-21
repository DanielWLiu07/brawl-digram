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

- [ ] `data-loader` → `data/brawlers.json` (validate vs Shelly's known values).
- [ ] `data-loader` → `data/maps.json` (decode tile encoding in `maps.csv` for ranked pool only — filter via Brawlify's ranked field; ~25 maps).
- [ ] `frontend` picks stack (recommend: SvelteKit or Next + Konva/PixiJS for canvas + **Y.js for collaboration**) and scaffolds.
- [ ] Render a ranked map tile grid; place single brawler with base-attack reticle.
- [ ] Full reticle library (cone/line/arc/circle/indirect/self-AoE/placement) wired to all `AttackVariant`s.
- [ ] Drag-and-drop placement + rotation to set aim direction.
- [ ] **Map builder mode** — toggle to edit-mode, paint tiles from a palette, save custom layouts. Doubles as validation: if the builder can reproduce game maps, the renderer is correct.
- [ ] `backend` stands up minimal Y.js sync server (y-websocket on Node, or Hocuspocus).
- [ ] `backend` cron: weekly fetch of Brawlify ranked pool → write `data/ranked-rotation.json`. Bake season's map list into config; refresh per season.
- [ ] Multi-user same-canvas presence (cursors, selections, additions).
- [ ] Room URLs you can share.

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
