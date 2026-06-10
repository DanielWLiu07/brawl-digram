# Draft advisor — knowledge layer design (2026-06-10)

Answers "should we use RAG?" and "what's the best way to encode pro knowledge
(thrower lists, counters)?" Based on two research passes (MOBA draft tooling +
retrieval architecture literature) and an audit of our own baked data.

## 1. RAG verdict: no vector RAG for Phase 2

**Use deterministic structured retrieval** — select KB slices by exact keys we
already hold (map, mode, picked/banned brawlers, patch), stuff ~4–8K tokens
into the prompt. Reasons (full citations in the research report):

- The KB is structured data queried by known keys — the textbook case where
  embedding search is wasted overhead.
- 8B-class models (Llama 3.1 8B / Qwen 2.5 7B) degrade well before their 128k
  windows (Qwen F1 cliff at ~40–50% of window; Granite-8B effective ≈32k), so
  "stuff the whole KB" is worse than selecting hard, even though it fits.
- Groq latency favors small prompts; drafting is on a pick clock.
- The only future RAG candidate is **long-form pro prose notes** — and only
  once key-filtered prose for one (map, mode) context regularly exceeds the
  ~8K budget (≈ >15–30 long notes per map). Even then: embedding **rerank
  within the key-filtered set**, never a global vector index.

Pipeline: key-select map entry + draft-relevant brawler records + their
counter/synergy rows + patch-tagged stats → key-filter prose notes → stuff.

## 2. Matchup representation: signed deltas, not raw win rates

Follow DraftGap (the proven LoL analog): store counter/synergy as **signed
win-rate deltas vs the independence baseline** in rating (log-odds) space —
synergy symmetric, counters directional — each with a `reason` string and
`confidence`/sample size. A ~50-line deterministic scorer sums deltas per
candidate (own map win rate + counter terms vs enemy picks + synergy terms
with allies) and produces a ranked shortlist with contributing terms.

**Division of labor:** scorer proposes (and supplies every number); the LLM
picks among top candidates on comp-identity grounds (the thing pairwise
matrices provably miss) and writes the explanation, citing only supplied KB
fields. Guardrail: any numeric claim not traceable to a supplied field is
flagged. This is the documented anti-hallucination pattern (FACTS Grounding).

## 3. What we auto-derive vs what pros must author

Audit of `data/brawlers.json` (2026-06-10): much of the "which character is a
thrower" document is **already machine-derivable** — don't ask pros for it.

| Attribute | Source | Status |
| --- | --- | --- |
| Class (Tank/Assassin/Marksman/Artillery/Controller/Support/Damage Dealer) | official `class` field | ✅ 87/104; 17 newer = "Unknown", backfill from wiki |
| Thrower | attack shape ∈ {placement, cluster} ∧ passesWalls | ✅ derives the exact real list (15: Barley, Dyna, Tick, Sprout, Grom, Willow, Juju, L&L…) |
| Range class (sniper ≥9t / mid / short) | `variants[].params.rangeTiles` | ✅ |
| Tankiness | `hp` tiers | ✅ |
| Mobility | `speedTilesPerSec` + dash/jump mechanics in `ability_mechanics.json` | ✅ |
| Wall interaction | `passesWalls`, wall-break supers (mechanics catalog) | ✅ |
| Counter edges + reasons | — | ❌ pro/community authored |
| Per-map pick priority + lane plans | — | ❌ pro authored (per-map win rates as objective prior) |
| Comp archetypes (e.g. bush camp, poke, dive) | — | ❌ pro authored |

## 4. KB schema v1 (`data/kb/`)

```
data/kb/
  meta.json                 { patchVersion, exportedAt }
  brawlers/<Hash>.json      auto-derived attributes + authored notes
  matrix.json               sparse pairwise edges
  maps/<InternalName>.json  per-map entries
  notes/<id>.md             long-form pro notes w/ frontmatter tags
```

```jsonc
// matrix.json — one edge
{ "a": "Piper", "b": "Mortis", "type": "counter",   // directional: b beats a
  "deltaRating": -0.35,                              // log-odds delta vs independence
  "reason": "Mortis closes the gap on long reload; Piper has no escape once dashed on",
  "modeContext": ["Knockout", "Wanted"],             // null = mode-agnostic; counters often don't transfer across modes
  "confidence": "pro",                               // pro | stats | community | llm-draft
  "patchVersion": "67.301", "lastVerified": "2026-06-10" }

// maps/<name>.json
{ "map": "Gemgrab_42", "mode": "Gemgrab",
  "archetype": ["open-mid", "double-bush-flank"],   // controlled vocabulary
  "descriptors": { "bushPct": 0.18, "wallPct": 0.22, "chokeCount": 3 },  // computed from grid
  "pickPriority": [ { "brawler": "Gene", "score": 9, "why": "mid control + pull through center wall" } ],
  "comps": [ { "name": "double thrower siege", "brawlers": ["Tick","Barley","Gene"], "why": "..." } ],
  "patchVersion": "67.301", "lastVerified": "2026-06-10" }
```

Every record carries `patchVersion` + `lastVerified`; the whole KB snapshots
per patch in git; the advisor caveats anything older than the live patch and
the UI badges it. Coverage-drift (share of KB past staleness threshold) is the
re-curation trigger for the pro-curator track.

## 5. Counter-matrix bootstrap (before any pro signs on)

1. Auto-derive attribute layer (section 3) — free, objective.
2. Seed counter edges from attribute RULES, not vibes: thrower > stationary
   tank behind wall; assassin > sniper without escape; etc. Each rule emits
   edges with `confidence: "llm-draft"` and a rule-generated reason.
3. Cross-check edges against per-(map,brawler) stats where available.
4. Pros review/correct the seeded matrix (review is 10× cheaper than authoring
   blank); their edits get `confidence: "pro"`.

## 6. Bootstrap data sources (survey results, 2026-06-10)

**Roles/attributes:** Brawlify `GET /v1/brawlers/{id}` (no key, no stated
limits) returns the official `class` per brawler — walk IDs from 16000000 up.
Fandom wiki infobox (`| Class =`, Mediawiki parse API, CC-BY-SA) backfills the
17 "Unknown" newer brawlers. (Most of this we already have baked.)

**Counters:** NO public machine-readable counter matrix exists anywhere.
Closest: zathong.com/brawl-stars-counter/ — human-curated HTML tables
("Weak/Strong Against", 5–9 entries each, ~70–80 brawlers). Usable only as a
seed with `confidence: "community"`; NOT mode-contextualized (hence the
`modeContext` field). SpenLC's per-season ranked cheat sheets (zleague.gg) are
prose but encode ban priorities + per-map picks worth manual extraction.

**Per-map win rates — CORRECTION to the earlier investigation doc:** the
Brawlify public `GET /v1/maps/{id}` endpoint has `stats[]`/`teamStats[]` in
its schema but **returns empty arrays** (verified on 5 active maps). The
website shows the data; the public API doesn't serve it. Options, in order:
(1) ask Brawlify via their Discord about stats access; (2) ask schneefux
(brawltime.ninja, one-person project, Bayesian-smoothed per-map win rates,
Cube API gated 403) for a non-commercial data-share; (3) self-collect from
the official battle-log API (what DraftStars/brawl-ai did) — needs a key and
an aggregation pipeline. Scraping BTN's server-rendered pages works but is
fragile/ToS-gray — fallback only.

**Open-source drafters:** none ship reusable data (devkennyy/drafter is a UI
shell over SpenLC's sheet; DraftStars/brawl-ai keep embeddings + DBs
off-repo). Reusable pattern only: self-collect from the official API.

**Pick-order**: still absent from every public source — Phase 3 gate stands.
