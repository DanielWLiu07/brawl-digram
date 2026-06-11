# Draft advisor v1 — data acquisition & training plan (2026-06-10)

Research only, no implementation. Ranks the real acquisition methods for the
agreed v1 design: **agentic + classical-ML hybrid** where the ML learns
factor-weights on brawler *attributes* (range/HP/mobility/super + computed map
geometry) — not sparse identity matchups — so it generalizes and survives
balance patches. Primary signal = pro picks/bans per map; ladder rates as the
high-volume fallback; candidate pool constrained to popular/pro picks.

Three parallel research agents (pro pick/ban sources, official-API +
ladder-stats endpoints, text-mining + CV) plus first-hand verification of every
load-bearing claim. ✅ = verified by live request from this machine today.

## 0. Headline findings (both change the earlier plan)

1. ✅ **Liquipedia records pro picks AND bans per map**, in clean `{{Map}}`
   wikitext templates, fetchable through its free MediaWiki API. Verified on
   BSC 2026 Season 2 EMEA Monthly Finals: 35 games, 30 with full 3+3 bans
   (`t1c1..t1c3`, `t1b1..t1b3`, `map=`, `maptype=`, score). This is the gold
   ban signal we assumed didn't exist in machine-readable form.
2. ✅ **brawltime.ninja's Cube API is openly usable** — the 403 we hit before
   was just a missing token, and the site mints tokens from a public,
   auth-free endpoint. Verified end-to-end: `POST
   https://brawltime.ninja/api/trpc/auth.getToken` (empty body) → 1-hour JWT →
   `cube.brawltime.ninja/cubejs-api/v1/load` returns real per-(brawler, map)
   data, e.g. Mr. P on Hard Rock Mine: 65.6% win rate over **926k picks**,
   refreshed today. Cubes include `map` (winRate/useRate/picks by brawler, map,
   mode, season, trophyRange) and `brawlerAllies`/`brawlerEnemies` (synergy /
   counter pair stats — directly seeds the KB matrix).

This supersedes kb-design §6–7's "no per-map stats without asking or
self-collecting": we can pull populated per-map ladder stats **today**.

## 1. Ranked acquisition methods

### #1 — Liquipedia pro pick/ban scraper (gold signal) — ~0.5–1 day

- **Yields:** per pro game: event, stage, date, mode, map, both lineups (3
  picks/team), **3 bans/team**, set score, winner. `firstpick=` exists in the
  template but editors leave it blank → **pick order still not captured**
  (Phase 3 gate stands).
- **How:** `liquipedia.net/brawlstars/api.php?action=parse&page=<Page>&prop=wikitext`
  → regex the `{{Map ...}}` blocks. Enumerate pages via
  `list=prefixsearch&pssearch=Brawl_Stars_Championship/2026` (+ World Finals,
  Brawl Cup, LCQ). Hard requirements (406 otherwise): gzip Accept-Encoding,
  descriptive User-Agent, ≤1 req/2s general, ≤1 parse req/30s. Optional
  upgrade: apply for the LPDB API key (non-commercial tier, 60 req/hr) for
  structured `match2game` records instead of wikitext parsing.
- **Volume:** ~1,000–1,300 pro games/yr (5 regions × 6 monthly finals + Worlds
  + Brawl Cup). World Finals 2025: 104/104 games with full picks+bans.
  Per-(map, season) samples are thin — expect 20–60 games per map — which is
  exactly why the v1 ML learns attribute weights, not identity matchups.
- **Reliability / patch-resilience:** high — volunteer-maintained within days
  of each broadcast, canonical esports wiki, template schema stable across
  2025–2026. ~10–15% ban-field gaps on some pages. License CC-BY-SA 3.0
  (attribute Liquipedia; fine for our non-commercial posture).

### #2 — brawltime Cube API pull (ladder fallback + counter seed) — hours

- **Yields:** per-(brawler, map, mode, season, trophyRange) win/use/pick rates
  at millions-of-battles scale, plus ally/enemy pair win rates. Ranked-mode
  tier data exists on the site (no ban rates anywhere — bans aren't in the
  official API, see #3).
- **How:** token endpoint + Cube.js `load` queries (verified working, CORS
  open, no key). Names come back as internal-ish uppercase (`MR. P`,
  `Out in the Open`) — bridge to our display names once.
- **Reliability:** the big caveat — this is *de-facto* open, not documented.
  schneefux (one-person project) could rotate the secret or add a captcha any
  time; the code literally has a `// TODO: verify identity` comment. **Treat
  as borrowed:** mirror every pull into patch-tagged snapshots
  (`data/draft_stats/<patch>.json`), be polite (low QPS, cache the 1-h token),
  and send the courtesy data-share ask on their Discord anyway. Patch-resilient
  by construction (continuously re-aggregated from live battle logs).

### #3 — Official battle-log self-collection (durable owned path) — ~2–4 days, ongoing cron

- **Yields:** per-battle map, mode, result, both lineups, star player.
  **Ranked is included and distinguishable** (`battle.type ∈ {soloRanked,
  teamRanked}`). **No bans, no pick order, no lobby rank tier** — confirmed
  limitation.
- **How:** the key-per-IP problem on Fly.io is solved by the **RoyaleAPI
  proxy**: request `https://bsproxy.royaleapi.dev/v1/...` and whitelist its
  static IP `45.79.218.79` when minting the key (standard, free, ToS-clean).
  Seed tags from `/rankings/{country}/players` (~200 × ~190 countries),
  snowball via tags found in battle logs, poll each player's last-25 battle
  log, dedupe on `(battleTime, sorted player tags)` (each match appears in up
  to 6 logs). Few thousand active seeds polled ~30-min → hundreds of thousands
  of deduped battles/day; SQLite + cron on the existing box. Bayesian
  smoothing toward the global brawler mean for thin (map, brawler) cells.
- **Why bother given #2:** it's the path we own. If brawltime closes, this is
  the replacement; it's also the only way to get a *rank-filtered* ladder
  slice we control (resolve seed players' ranked tier ourselves). Start it
  after #1/#2 are baked, not before.

### #4 — Text-mining for the reasoning KB (LLM-draft inputs) — ~3–4 days total

Priority order by signal-per-effort:

1. **Fandom wiki** (~1 day): MediaWiki API, no auth. Brawler pages have a
   structured "Tips" section (Game Modes and Maps / Recommended Build /
   Strategies); **map pages have their own Tips sections**; there's a
   strategy-guide system with structured `DangerousBrawler` (= counter)
   fields. Actively edited (Shelly: 5 edits Apr–May 2026). CC-BY-SA → keep a
   per-entry `source` field for attribution (KB schema already has the
   provenance slot via `confidence`; add `source`).
2. **zleague SpenLC articles** (~0.5 day): written transcripts of SpenLC's
   draft/tier videos — real counter logic, synergy pairs, ban philosophy,
   per-season ranked sheets. Plain pages, easy fetch. This removes most of the
   case for YouTube caption mining.
3. **Reddit r/BrawlStarsCompetitive via Arctic Shift** (~1–2 days): Pushshift's
   successor; monthly dumps current through Apr 2026 + a free JSON API that
   returned posts from *today* when probed. ~9% of posts are flaired **"Draft
   Query"** (draft state + upvoted answers = exactly our reasoning shape);
   filter flair ∈ {Draft Query, Strategy, Guide, Advanced Mechanics} + score
   threshold. Official Reddit API only for incremental top-ups.
4. **PL Prodigy** (powerleagueprodigy.com): per-map recommended comps +
   guides, active June 2026 — small, current per-map layer.
5. **YouTube auto-captions — tier-3 backfill only:** empirically works
   (yt-dlp pulled a KairosTime SRT in seconds from a residential IP; brawler
   names mangled consistently — a ~30-entry alias table fixes ≥95%), but it's
   a real YouTube-ToS violation and mostly redundant given zleague. Use only
   for content with no text equivalent (per-map VOD draft breakdowns).
6. **Skip Discord mining** entirely (ToS-prohibited, ephemeral); Discord is
   the pro-curator's *recruiting* channel, not a data source.

### #5 — Video analysis / CV — DEFER (honest verdict)

**Not worth building for v1.** The calculus collapsed once Liquipedia turned
out to carry picks+bans: volunteers already transcribe ~80% of what
draft-screen CV would produce, for free, within days of each event.

- **The one thing CV uniquely yields is pick order** — the BSC 2026 rulebook
  confirms the broadcast shows the in-game draft sequentially (blind bans →
  alternating picks with explicit first-pick), so frame-timestamping portrait
  appearances on VODs recovers full draft order. That is precisely the Phase 3
  gate, and nothing in v1 needs it.
- **Feasibility if/when we do it:** template-matching our already-extracted
  portrait assets against a fixed draft layout is the easy kind of CV (LoL
  prior art: LeagueOCR, DeepLeague); realistic 1–2 week build, 95%+ accuracy.
  Real costs are maintenance (UI reskins every ~2 months) and volume — a few
  hundred pro drafts/yr is a *small* ML dataset even with perfect extraction.
  Archived VODs don't churn UI, so a retroactive per-season pass is the sane
  shape.
- **No programmatic replay/spectate access exists** (in-client replays export
  rendered video only). Positioning-coach CV stays a separate, later product
  question.
- **Decision rule:** build the CV pick-order extractor only at the moment we
  commit to Phase 3 — and first check whether ~1k ordered drafts/yr is even
  enough to train on.

## 2. How the data feeds the v1 hybrid

**Features** (all owned, patch-resilient): auto-derived brawler attributes
(range/HP/speed tiers, thrower, wall interaction, mobility mechanics — kb
design §3) × computed map descriptors from our decoded grids (bushPct,
wallPct, chokeCount, lane structure — no other drafter has these) × mode.

**Labels / targets, in priority order:**
1. Pro pick rate + **ban rate** per (brawler, map/mode) from Liquipedia —
   thin but gold; powers the ban-phase recommender directly.
2. Ladder per-(brawler, map) win-rate delta vs global mean (brawltime now,
   self-collected later), Bayesian-smoothed, as the dense target/prior the pro
   signal shrinks toward.

**Model:** interpretable regression (logistic / small GBM) over
attribute×geometry interaction terms predicting pick/ban propensity and
win-rate delta. Learned weights ("+sniper×openLanes", "−shortRange×bushPct
low") drop straight into the existing v0 scorer as replacements for the
hand-tuned rule weights — same term-chip UI, now data-backed. Because features
are attributes, a balance patch only moves a brawler's *inputs* (new HP/range
from the next CSV pull), not the model.

**Candidate pool (anti-hallucination):** union of (brawlers pro-picked or
pro-banned on this map in the last N events) ∪ (ladder use rate above
threshold on this map). Agent may promote an out-of-pool sleeper only with an
explicit justification citing KB fields.

**KB pipeline:** mined text (#4) → LLM drafts counter edges / map notes with
`confidence: "llm-draft"` + `source` attribution → cross-check vs
`brawlerEnemies` pair stats (#2) → human/pro review promotes to
`confidence: "pro"`. Matches kb-design §5; the new part is that pair *stats*
now exist to validate drafted edges against.

## 3. Execution order

| Step | What | Effort |
| --- | --- | --- |
| 1 | Liquipedia scraper → `data/pro_drafts.json` (event, map, picks, bans, result) | 0.5–1 d |
| 2 | brawltime Cube puller → patch-tagged `data/draft_stats/` mirror (+ ally/enemy pairs) | 0.5 d |
| 3 | Map-descriptor extractor over decoded grids (already planned, now load-bearing for features) | 1 d |
| 4 | Factor-weight fit + swap into the v0 scorer; ban recommender from pro ban rates | 1–2 d |
| 5 | Wiki + zleague + Arctic Shift mining → LLM-drafted KB entries with provenance | 3–4 d |
| 6 | Official-API collector via RoyaleAPI proxy (cron) — the durable stats path | 2–4 d, then ongoing |
| — | CV pick-order extractor | deferred to Phase 3 commit |

Parallel zero-effort asks stay open: brawltime Discord courtesy note (we're
using the open Cube endpoint; offer attribution), Brawlify Discord stats ask,
Liquipedia LPDB key application.
