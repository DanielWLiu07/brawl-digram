#!/usr/bin/env python3
"""Mine strategy text from the Brawl Stars Fandom wiki for the reasoning KB.

Pulls each brawler page's "Tips" section (and each ranked map page's "Tips")
via the MediaWiki API into kb_sources/wiki/ as raw wikitext. These are the
LLM-drafting INPUTS — a human/LLM pass turns them into data/kb/ entries with
confidence:"llm-draft" and per-entry source attribution.

License: Fandom text is CC-BY-SA 3.0 — every KB entry derived from these
files must carry a source URL (the kb schema's `source` field).

Usage: python3 fetch_wiki_tips.py [--maps-only|--brawlers-only]
"""

import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
OUTDIR = HERE / "kb_sources" / "wiki"

API = "https://brawlstars.fandom.com/api.php"
UA = "brawl-digram/0.1 (KB research; contact@example.com)"
SLEEP = 1.2

# our display name -> wiki page title, where they differ
TITLE_FIX = {"R-T": "R-T", "8-Bit": "8-Bit", "Mr. P": "Mr. P",
             "Larry & Lawrie": "Larry & Lawrie"}


def api(params, retries=3):
    params = dict(params, format="json")
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read())
        except Exception as e:
            if attempt == retries - 1:
                raise
            time.sleep(5 * (attempt + 1))
            print(f"  retry after {e}")


def tips_section(title):
    d = api({"action": "parse", "page": title, "prop": "sections"})
    if "error" in d:
        return None, None
    secs = d["parse"]["sections"]
    for s in secs:
        if s["line"].strip().lower() in ("tips", "strategy", "strategies"):
            return s["index"], s["line"]
    return None, None


def fetch_tips(title, slug):
    out = OUTDIR / f"{slug}.txt"
    if out.exists():
        return "cached"
    idx, label = tips_section(title)
    time.sleep(SLEEP)
    if idx is None:
        out.write_text("")  # cache the miss
        return "no-tips"
    d = api({"action": "parse", "page": title, "prop": "wikitext", "section": idx})
    time.sleep(SLEEP)
    wt = d["parse"]["wikitext"]["*"]
    url = f"https://brawlstars.fandom.com/wiki/{urllib.parse.quote(title.replace(' ', '_'))}"
    out.write_text(f"SOURCE: {url}\nSECTION: {label}\nLICENSE: CC-BY-SA 3.0\n---\n{wt}")
    return f"{len(wt)} chars"


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    mode = sys.argv[1] if len(sys.argv) > 1 else ""

    if mode != "--maps-only":
        brawlers = json.load(open(HERE / "brawlers.json"))["brawlers"]
        for b in brawlers:
            name = b["name"]
            title = TITLE_FIX.get(name, name)
            slug = "brawler_" + name.replace(" ", "_").replace("&", "and").replace(".", "")
            print(f"{name:18} {fetch_tips(title, slug)}")

    if mode != "--brawlers-only":
        # ranked-relevant maps with stats cells (the ones the advisor serves)
        try:
            ai = json.load(open(HERE / "draft_ai.json"))
            displays = sorted({e["display"] for e in ai["stats"].values()})
        except FileNotFoundError:
            displays = []
        for disp in displays:
            slug = "map_" + disp.replace(" ", "_").replace(".", "")
            print(f"{disp:24} {fetch_tips(disp, slug)}")

    n = len(list(OUTDIR.glob("*.txt")))
    nonempty = sum(1 for p in OUTDIR.glob("*.txt") if p.stat().st_size > 10)
    print(f"done: {n} files, {nonempty} with content, in {OUTDIR.relative_to(HERE)}")


if __name__ == "__main__":
    main()
