# AI Draft Advisor — investigation (2026-06-10)

Investigation only, no implementation. Scope of what was previously envisioned,
what data it needs, candidate approaches, and how it plugs into the prototype.

## 1. What was previously envisioned (recovered from memory + ROADMAP.md)

The earlier conversation is well documented (project memory entries from
2026-05-18 + `ROADMAP.md` Phase 2/3):

- **Phase 2 "agentic advisor"**: an open-source LLM (Llama 3.1 8B / Qwen 2.5 7B
  class, Groq for cheap inference) reading a **pro-curated per-map knowledge
  base** (`data/kb/`, doesn't exist yet) + current draft state + tier-list
  snapshot → pick/ban recommendations **with explanations and KB citations**.
  UI: an "ask the advisor" panel beside the whiteboard.
- **Phase 3 pure-ML drafter is deprioritized and gated**: transformer with
  win-prob + next-pick heads, 1-ply expectimax — only if Phase 2 plateaus AND a
  pick-order reconstructor hits ≥80% accuracy (the API's battlelog returns
  final lineups, not pick sequence).
- **Constraints Daniel flagged himself** (memory: `project-brawl-digram-constraints`):
  meta drift (patches every few weeks), map-specific viability, pairwise
  counters + comp synergy, sequential pick/ban conditioning, pro scrim data not
  public, community tier lists lag the meta. The advisor handles these via
  prompt context (edit a tier list, not retrain a model).

## 2. Data needs vs. what we already have

| Need | Status |
| --- | --- |
| Brawler kit/stats/geometry | ✅ `data/brawlers.json` (104 brawlers), `kits.json`, `ability_mechanics.json` (521 verified records) |
| Map + mode context | ✅ `data/maps.json` (409 decoded grids w/ mode), name bridge (599 hashes), tile legend |
| **Computed map descriptors** | ✅ derivable now — we have the actual tile grids, so bush density, wall density, choke widths, lane structure, mid control area, water, map size can be computed programmatically. **No other drafter has this**; it grounds "why" explanations ("open map, long sightlines → snipers"). |
| Per-(brawler, map) win/use rates | ❌ harder than first thought (spike done 2026-06-10): Brawlify's public `/maps/{id}` endpoint has `stats[]` in schema but returns EMPTY arrays; brawltime.ninja has the data but its API is gated. Paths: ask Brawlify (Discord) / ask brawltime's dev for a non-commercial share / self-collect via official battle-log API. See draft-advisor-kb-design.md §6. |
| Counter matrix / synergies | ❌ no public source — this is exactly what the pro KB was for; interim: role-composition heuristics + LLM prior knowledge |
| Pick/ban sequence rules | ❌ encode current ranked draft as a small state machine (bans → alternating 1-2-2-1 picks); needs confirming against current season rules |
| Tier-list snapshot | ⚠️ Brawlify global stats as objective baseline; community lists (KairosTime etc.) are subjective priors |

## 3. Candidate approaches

1. **Heuristic scorer (v0, client-side, no server)** — score = map-conditioned
   win rate + tier prior + role-comp constraints (tank/support/control
   coverage) + simple counter rules. Deterministic, instant, free, works in the
   static prototype. Ceiling: no real counter knowledge, canned explanations.
2. **LLM advisor (the Phase 2 plan)** — prompt = draft state + computed map
   descriptors + per-map stats + KB snippets → ranked suggestions + reasoning.
   Meta-responsive (edit the prompt data), natural explanations. Costs: serving
   (Groq), prompt eng, and the KB is the long pole (pro recruitment).
3. **Hybrid (recommended)** — heuristic generates the candidate shortlist +
   feature table; LLM ranks and explains. Degrades gracefully to pure
   heuristic when offline/over budget. This is also the cleanest path to
   measure "did the LLM add anything" before paying for the KB effort.
4. **ML model** — unchanged: Phase 3, gated, not part of this initiative.

## 4. UI integration with the prototype

- Third tab **"Draft"** in the right panel (beside Brawlers/Tiles): mode+map
  read from the loaded map; ban row (3+3) and pick slots laid out in the real
  pick sequence; whose-turn indicator.
- Suggestion list: portrait + score + reason chips ("64% WR here", "covers
  tank gap", "counters Piper"); click-to-fill the next slot; filled picks can
  be dragged onto the map as tokens (draft state and whiteboard state stay
  linked — the differentiator vs existing drafters).
- The scene schema (`snapshotScene`) gains a `draft` object — which also makes
  draft state collaborative for free once Y.js lands.
- LLM path needs one tiny API route (can't ship a Groq key client-side) — fine
  to defer; v0 heuristic needs no backend at all.

## 5. Recommended plan (investigation → v0)

1. **Data spike (~1 day):** fetch Brawlify per-map stats for the current ranked
   pool; measure coverage/freshness; bake `data/draft_stats.json`.
2. **Map descriptor extractor (~1 day):** grid → {bushPct, wallPct, openLanes,
   chokeCount, midDist, water} in `data/map_descriptors.json`; sanity-check
   descriptors against known map archetypes (Hideout vs Shooting Star).
3. **Draft tab UI + state machine:** manual pick/ban entry first, no AI.
4. **Heuristic v0:** client-side scorer + reason chips; evaluate against a few
   known "correct" drafts from recent ranked meta.
5. **LLM upgrade behind a flag:** single API route → Groq, prompt assembled
   from the same JSON; A/B against heuristic. KB schema + pro outreach
   (the existing `pro-curator` track) proceeds in parallel — it's the long
   pole and gates advisor quality more than any code.

## 6. Open questions for Daniel

1. Target the **current ranked draft format** (confirm: 6 bans total, 1-2-2-1
   alternating picks, first-pick side known)? Any other formats (friendly
   scrims, Power League legacy)?
2. v0 as **client-side heuristic** in the prototype (no server) acceptable, or
   start straight on the Next.js app?
3. Should the advisor also suggest **token placement** (positions on the map)
   or picks/bans only for now?
4. Budget/account for **Groq** (or preference to self-host)?
5. Win-rate source preference: Brawlify stats (objective, ladder-biased) vs
   community tier lists (subjective, pro-aware) as the primary prior?
