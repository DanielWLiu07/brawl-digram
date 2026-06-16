#!/usr/bin/env python3
"""Assemble the Phase-2 LLM advisor's retrieval context for one draft turn.

Implements the deterministic key-select pipeline from
docs/draft-advisor-kb-design.md §1: NO vector RAG — select KB slices by exact
keys we already hold (map, mode, picked/banned brawlers, patch) and stuff a
budgeted ~4-8K-token context. Sections are priority-ordered; when the budget
overflows, low-priority prose is truncated, then dropped, before any numeric
section is touched.

The output carries the anti-hallucination contract from §2: the LLM may only
cite numbers present in the context, and every section is provenance-tagged.

Usage:
  python3 data/build_advisor_context.py --map "Hard Rock Mine" \
      --blue Gene,Pam --red Piper --bans-blue Hank --bans-red Juju \
      --phase pick --team blue [--budget 6000] [--json out.json]

With no arguments, runs a Hard Rock Mine demo draft.
"""

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent

DEFAULT_BUDGET_TOKENS = 6000
CHARS_PER_TOKEN = 4          # crude but stable; budget is approximate by design
TOP_CANDIDATES = 8
WIKI_BRAWLER_CHARS = 400
WIKI_MAP_CHARS = 600

# internal grid-name prefix -> mode family used by draft_ai.json stats keys
PREFIX_FAM = {
    "Gemgrab": "Gemgrab", "Wanted": "Wanted", "Bankheist": "Bankheist",
    "BrawlBallV2": "Ball", "Laserball": "Ball", "AirHockey": "Ball",
    "KingOfHill": "KingOfHill", "Knockout": "Knockout",
}


def _kebab(s):
    return re.sub(r"[^A-Za-z0-9]+", "-", (s or "").strip()).strip("-")


def _load(name):
    return json.load(open(HERE / name))


class ContextBuilder:
    def __init__(self):
        self.ai = _load("draft_ai.json")
        self.descriptors = _load("map_descriptors.json")
        self.name_map = _load("map_name_map.json")["maps"]
        self.seed_edges = _load("draft_seed.json")["edges"]
        kb = HERE / "kb"
        self.kb_meta = json.load(open(kb / "meta.json"))
        self.kb_edges = json.load(open(kb / "matrix.json"))["edges"]
        self.kb_brawlers = {p.stem: json.load(open(p))
                            for p in (kb / "brawlers").glob("*.json")}
        self.kb_maps = {p.stem: json.load(open(p))
                        for p in (kb / "maps").glob("*.json")}
        self.wiki_dir = HERE / "kb_sources" / "wiki"
        # display-name set for validation
        self.known = set(self.ai["attrs"].keys())

    # ---- key resolution -----------------------------------------------------

    def resolve_map(self, query):
        """Display name, kebab, or internal grid name -> (internal, display, fam)."""
        if query in self.descriptors:
            internal = query
            display = next((k.replace("-", " ") for k, v in self.name_map.items()
                            if v == query), query)
        else:
            internal = self.name_map.get(_kebab(query))
            if not internal:
                # case-insensitive fallback
                lk = {k.lower(): v for k, v in self.name_map.items()}
                internal = lk.get(_kebab(query).lower())
            if not internal or internal not in self.descriptors:
                raise KeyError(f"unknown map: {query!r}")
            display = _kebab(query).replace("-", " ")
        prefix = internal.split("_")[0]
        fam = PREFIX_FAM.get(prefix)
        return internal, display, fam

    def _stats(self, fam, internal):
        m = self.ai["stats"].get(f"{fam}|{internal}")
        mode = self.ai["modeStats"].get(fam)
        return m, mode

    # ---- candidate shortlist (mirrors the scorer's pool: pro ∪ ladder) ------

    def shortlist(self, fam, internal, taken, k=TOP_CANDIDATES):
        m, mode = self._stats(fam, internal)
        scores = {}
        src = m if m and m.get("proGames", 0) >= 4 else mode
        if src:
            g = max(src.get("proGames", 0), 1)
            for name, (p, b) in src.get("pro", {}).items():
                scores[name] = scores.get(name, 0) + (p + b) / g
            wr_mean = src.get("wrMean", 0.5)
            for name, row in src.get("ladder", {}).items():
                wr, n = row[0], row[1]
                if n >= 500:
                    scores[name] = scores.get(name, 0) + (wr - wr_mean) * 4
        ranked = sorted(scores, key=scores.get, reverse=True)
        return [n for n in ranked if n not in taken and n in self.known][:k]

    # ---- section builders (each returns (priority, title, lines)) -----------

    def build(self, map_query, blue, red, bans_blue, bans_red,
              phase="pick", team="blue", budget=DEFAULT_BUDGET_TOKENS,
              candidates=None):
        internal, display, fam = self.resolve_map(map_query)
        for n in blue + red + bans_blue + bans_red:
            if n not in self.known:
                raise KeyError(f"unknown brawler: {n!r}")
        taken = set(blue + red + bans_blue + bans_red)
        cands = candidates or self.shortlist(fam, internal, taken)
        relevant = list(dict.fromkeys(blue + red + cands))  # bans excluded from kit detail
        m, mode = self._stats(fam, internal)

        sections = []

        # P0 — task header + draft state (never dropped)
        hdr = [
            f"Map: {display} (mode family: {fam}, internal grid: {internal}, "
            f"patch {self.kb_meta.get('patchVersion', '?')})",
            f"Draft phase: {phase.upper()} — advising team {team.upper()}.",
            f"Blue picks: {', '.join(blue) or '(none)'} | Red picks: {', '.join(red) or '(none)'}",
            f"Bans: blue removed {', '.join(bans_blue) or '(none)'}; "
            f"red removed {', '.join(bans_red) or '(none)'}",
            "RULES: choose among the listed candidates only. Cite ONLY numbers "
            "that appear below — any other numeric claim is a violation. "
            "Entries are tagged [pro]/[stats]/[community]/[llm-draft] by trust tier.",
        ]
        sections.append((0, "Draft state", hdr))

        # P1 — map geometry card (computed from the decoded grid; always true)
        d = self.descriptors[internal]
        geo = [
            f"walls {d['wallPct']:.0%}, bushes {d['bushPct']:.0%}, open {d['openPct']:.0%}, "
            f"long sightlines {d['sightlineFrac']:.0%} of rows",
            f"mid openness {d['midOpenness']:.0%}, chokepoints/row {d['chokesPerRow']:.2f}, "
            f"avg lane width {d['avgLaneWidth']:.1f} tiles "
            f"({d['width']}x{d['height']} grid, {d['playableTiles']} playable tiles)",
        ]
        sections.append((1, "Map geometry [computed]", geo))

        # P2 — per-brawler stats rows for everyone relevant
        rows = []
        for name in relevant:
            bits = []
            if m and name in m.get("ladder", {}):
                wr, n = m["ladder"][name][0], m["ladder"][name][1]
                bits.append(f"{(wr - m.get('wrMean', .5)) * 100:+.0f}% WR vs map avg "
                            f"({wr:.0%} raw, n={n:,}) [stats]")
            elif mode and name in mode.get("ladder", {}):
                wr, n = mode["ladder"][name][0], mode["ladder"][name][1]
                bits.append(f"{(wr - mode.get('wrMean', .5)) * 100:+.0f}% WR vs {fam} avg "
                            f"({wr:.0%} raw, n={n:,}) [stats]")
            if m and m.get("proGames", 0) >= 4 and name in m.get("pro", {}):
                p, b = m["pro"][name]
                bits.append(f"pro on this map: {p}x picked, {b}x banned "
                            f"over {m['proGames']} games [pro]")
            elif mode and name in mode.get("pro", {}):
                p, b = mode["pro"][name]
                bits.append(f"pro in {fam}: {p}x picked, {b}x banned "
                            f"over {mode['proGames']} games [pro]")
            if bits:
                rows.append(f"- {name}: " + "; ".join(bits))
        sections.append((2, "Win rates & pro usage (ranked ladder this patch; "
                            "ladder population skews strong — deltas are the signal)", rows))

        # P3 — candidate kit lines (auto-derived attributes)
        kit = []
        for name in cands:
            a = self.ai["attrs"].get(name, {})
            tags = [t for t, f in (("thrower", a.get("thrower")), ("sniper", a.get("sniper")),
                                   ("short-range", a.get("shortRange")), ("tank", a.get("tank")),
                                   ("fast", a.get("fast")), ("melee", a.get("melee"))) if f]
            rng = a.get("rangeN", 0) * 12
            kit.append(f"- {name}: " + (f"range {rng:.1f} tiles, " if rng else "")
                       + f"HP {a.get('hpN', 0) * 7000:,.0f}, "
                       f"speed {a.get('speedN', 0) * 3.2:.1f} t/s"
                       + (f" — {', '.join(tags)}" if tags else ""))
        sections.append((3, f"Candidates for this {phase} (shortlist = pro-played ∪ "
                            "ladder-strong here)", kit))

        # P4 — matchup edges among relevant brawlers (KB first, seed fills gaps)
        pool = set(relevant) | set(bans_blue) | set(bans_red)
        edges, seen = [], set()
        for e in self.kb_edges:
            if e["a"] in pool and e["b"] in pool:
                seen.add((e["a"], e["b"]))
                chk = f" ({e['statsCheck']})" if e.get("statsCheck") else ""
                edges.append(f"- {e['b']} beats {e['a']} (Δ{e['deltaRating']:+.2f}) "
                             f"[{e['confidence']}]: {e['reason']}{chk}")
        for e in self.seed_edges:
            if e["a"] in pool and e["b"] in pool and (e["a"], e["b"]) not in seen:
                edges.append(f"- {e['b']} beats {e['a']} (Δ{e['delta']:+.2f}) "
                             f"[community]: {e['reason']}")
        sections.append((4, "Matchup edges (directional; Δ in rating units)", edges))

        # P5 — KB notes (curated; llm-draft pending pro review)
        notes = []
        kbm = self.kb_maps.get(internal)
        if kbm:
            for n in kbm.get("notes", []):
                notes.append(f"- [map] [{n['confidence']}] {n['text']}")
        for name in relevant:
            rec = self.kb_brawlers.get(name)
            if rec:
                for n in rec["notes"]:
                    notes.append(f"- [{name}] [{n['confidence']}] {n['text']}")
        sections.append((5, "Knowledge-base notes", notes))

        # P6 — wiki prose excerpts (CC-BY-SA, community-written; lowest trust)
        prose = []
        mp = self._wiki_excerpt(f"map_{display.replace(' ', '_')}.txt", WIKI_MAP_CHARS)
        if mp:
            prose.append(f"[map tips — {mp[0]}] {mp[1]}")
        for name in cands:
            ex = self._wiki_excerpt(f"brawler_{name.replace(' ', '_')}.txt",
                                    WIKI_BRAWLER_CHARS)
            if ex:
                prose.append(f"[{name} — {ex[0]}] {ex[1]}")
        sections.append((6, "Community wiki tips (CC-BY-SA, unverified)", prose))

        return self._fit_budget(sections, budget, meta={
            "map": {"display": display, "internal": internal, "fam": fam},
            "phase": phase, "team": team,
            "candidates": cands,
            "patchVersion": self.kb_meta.get("patchVersion"),
        })

    def _wiki_excerpt(self, fname, max_chars):
        """(source URL, cleaned excerpt) or None. Strips the provenance header
        and wikitext section markers so the budget buys prose, not boilerplate;
        the URL is kept for CC-BY-SA attribution."""
        p = self.wiki_dir / fname
        if not p.exists():
            return None
        raw = p.read_text()
        url = ""
        msrc = re.search(r"^SOURCE:\s*(\S+)", raw, re.M)
        if msrc:
            url = msrc.group(1).replace("https://", "")
        body = raw.split("---", 1)[-1]
        body = re.sub(r"==+[^=]*==+", "", body)          # section headers
        body = re.sub(r"\[\[([^|\]]*\|)?([^\]]+)\]\]", r"\2", body)  # wiki links
        body = re.sub(r"\n\s*\n+", "\n", body).strip()
        if len(body) < 40:
            return None
        return url, body[:max_chars]

    # ---- budget enforcement --------------------------------------------------

    def _fit_budget(self, sections, budget, meta):
        def render(secs):
            out = []
            for _, title, lines in secs:
                if not lines:
                    continue
                out.append(f"## {title}")
                out.extend(lines)
                out.append("")
            return "\n".join(out)

        dropped = []
        secs = [s for s in sections if s[2]]
        md = render(secs)
        # drop lowest-priority non-essential sections until we fit
        while len(md) / CHARS_PER_TOKEN > budget:
            droppable = [s for s in secs if s[0] >= 5]
            if not droppable:
                break  # numeric core never dropped; budget is approximate
            worst = max(droppable, key=lambda s: s[0])
            secs.remove(worst)
            dropped.append(worst[1])
            md = render(secs)
        return {
            "meta": meta,
            "markdown": md,
            "tokenEstimate": round(len(md) / CHARS_PER_TOKEN),
            "budget": budget,
            "droppedSections": dropped,
            "sections": {t: lines for _, t, lines in secs},
        }


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--map", default="Hard Rock Mine")
    ap.add_argument("--blue", default="", help="comma-separated picks")
    ap.add_argument("--red", default="")
    ap.add_argument("--bans-blue", default="")
    ap.add_argument("--bans-red", default="")
    ap.add_argument("--phase", choices=["pick", "ban"], default="pick")
    ap.add_argument("--team", choices=["blue", "red"], default="blue")
    ap.add_argument("--budget", type=int, default=DEFAULT_BUDGET_TOKENS)
    ap.add_argument("--json", help="write full context JSON here")
    args = ap.parse_args()

    csv = lambda s: [x.strip() for x in s.split(",") if x.strip()]
    blue, red = csv(args.blue), csv(args.red)
    if not (blue or red or csv(args.bans_blue) or csv(args.bans_red)) \
            and args.map == "Hard Rock Mine":
        blue, red = ["Gene", "Pam"], ["Piper"]  # demo draft

    b = ContextBuilder()
    ctx = b.build(args.map, blue, red, csv(args.bans_blue), csv(args.bans_red),
                  phase=args.phase, team=args.team, budget=args.budget)
    if args.json:
        Path(args.json).write_text(json.dumps(ctx, indent=1))
    print(ctx["markdown"])
    print(f"--- ~{ctx['tokenEstimate']} tokens (budget {ctx['budget']}); "
          f"dropped: {ctx['droppedSections'] or 'nothing'}", file=sys.stderr)


if __name__ == "__main__":
    main()
