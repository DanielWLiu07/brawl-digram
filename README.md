# brawl-digram

Collaborative Brawl Stars drafting + whiteboard. Drag brawlers onto tile-accurate maps, see attack reticles, multiple people in the same room. Eventually an LLM advisor on top, fed by pro-curated map notes.

Status: building Phase 1 (whiteboard MVP). Frontend isn't scaffolded yet — currently all the data prep lives in `data/`.

## What's in here

- `data/csv_logic/` — Brawl Stars game CSVs (v67.264, ~18 MB). Source of truth for brawler stats, skill geometry, tile encoding, map layouts. Pulled from the [tailsjs mirror](https://github.com/tailsjs/brawl-stars-assets).
- `data/brawlers.json` — flat per-brawler JSON for the frontend (attack/super/hyper/gadget reticles in tile units, plus asset paths). Built by `build_brawlers_json.py`.
- `data/maps.json` — 409 ranked-mode maps decoded into 2D tile grids + tile legend. Built by `build_maps_json.py`.
- `data/maps-all.json` — same but every map (989 total). Compact JSON, used by tooling that needs the full corpus.
- `data/map_name_map.json` — bridge from Brawlify display name (hash slug) → internal CSV name, for the 18 ranked maps. Built by `build_map_name_map.py`.
- `data/brawlify/` — snapshot of Brawlify catalog endpoints (events, maps, brawlers, gamemodes). Refreshed by `fetch_brawlify.py`.
- `data/ranked-rotation.json` — current ranked rotation derived from `brawlify/events.json`. Empty between seasons.
- `data/reticles/` — generated SVG reticle gallery for 85 brawlers (one file per brawler + an `index.html`).
- `assets/` — Brawlify CDN PNGs (brawler portraits, gadgets, star powers, maps, game modes) + a manifest. Pulled by `download_assets.py`.

See [`ROADMAP.md`](ROADMAP.md) for the full plan and [`CLAUDE.md`](CLAUDE.md) for the design constraints I keep tripping over (units in tiles everywhere, CSV capitalization is inconsistent, etc.).

## Scripts

Everything's a `python3 data/<file>.py` call. No build system, no Make, no Node yet.

| Script | What it does |
|---|---|
| `download_assets.py` | Pull all PNGs from Brawlify CDN into `assets/`. Idempotent — skips existing files. Re-run after major patches. |
| `fetch_brawlify.py` | Refresh `data/brawlify/*.json` from the Brawlify API. JSON only, no images. Cron weekly. |
| `build_brawlers_json.py` | Bake `data/brawlers.json` from the CSVs + reticle overrides. |
| `build_maps_json.py` | Decode `csv_logic/maps.csv` into `data/maps.json` + `data/maps-all.json`. |
| `build_map_name_map.py` | Auto-match the 18 ranked CSV maps to Brawlify hashes by community credit + Brawlify-id position. |
| `build_map_compare.py` | Render `data/maps_compare.html` — side-by-side CSV grid vs Brawlify PNG for visually verifying the bridge. |
| `render_all_reticles.py` | Generate `data/reticles/*.svg` from the CSV classifier + per-skill overrides. |

## Map bridge — how it works

Brawl Stars CSVs only know internal names like `Gemgrab_42`. Brawlify only knows display names like `Hard Rock Mine`. There's no field that bridges them — `build_map_name_map.py` infers it:

1. If the CSV row has a `CommunityCredit` that uniquely matches one Brawlify map of the same game mode, that's the match. (Confirmed by spot-checking against credit-confirmed cases — works.)
2. Otherwise, take the Nth Brawlify map of that mode ordered by id ascending, where N is the integer suffix of the internal name. (Brawlify ids are sequential by release date and align with Supercell's internal indexing.)
3. If both fail or disagree, flag confidence=low for manual review in `maps_compare.html`.

Current result: 7 high, 9 medium, 2 low confidence — all 18 ranked maps bridged. The two low ones point to Brawlify maps marked `disabled` and need eyeball verification.

## License

All extracted assets and CSV data are Supercell IP. Used under the [Supercell Fan Content Policy](https://www.supercell.com/fan-content-policy). Non-commercial only.
