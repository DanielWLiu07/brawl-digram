# Pro-curated knowledge base (Phase 2)

Schema per `docs/draft-advisor-kb-design.md` §4. Every record carries
provenance:

- `confidence`: `pro` | `stats` | `community` | `llm-draft` — who vouches.
- `source`: URL of the text the entry was drafted from (required for
  `llm-draft` and `community`; wiki-derived text is CC-BY-SA 3.0 and the
  attribution lives here).
- `patchVersion` + `lastVerified`: staleness tracking; the advisor caveats
  anything older than the live patch.

## Bootstrap pipeline (no manual authoring)

1. `fetch_wiki_tips.py` mines raw Tips wikitext → `kb_sources/wiki/`.
2. An LLM pass drafts structured entries from those sources into
   `brawlers/`, `matrix.json`, `maps/` with `confidence: "llm-draft"`.
3. Drafted counter edges are cross-checked against brawltime pair stats
   (`draft_stats/<patch>.json` `enemies` table): edges contradicted by
   large-sample pair win rates get dropped or flagged.
4. Pros review the seeded entries (10× cheaper than authoring blank);
   their edits get `confidence: "pro"`.

## Layout

```
meta.json                 { patchVersion, exportedAt }
brawlers/<Name>.json      auto-derived attributes + drafted notes
matrix.json               sparse counter/synergy edges (signed deltas)
maps/<Internal>.json      per-map entries (archetype, pick priority, comps)
notes/<id>.md             long-form notes w/ frontmatter tags
```
