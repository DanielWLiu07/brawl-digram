#!/usr/bin/env python3
"""Scrape pro pick/ban data from Liquipedia Brawl Stars into pro_drafts.json.

Liquipedia match pages store one {{Map}} template per game with map, mode,
3 picks + 3 bans per team, and score. License: CC-BY-SA 3.0 (attribution
required — carried in the output's _meta).

API etiquette (enforced server-side, 406 on violation):
  - gzip Accept-Encoding + descriptive User-Agent
  - action=parse  <= 1 request / 30 s
  - other actions <= 1 request / 2 s
Raw wikitext is cached under liquipedia_cache/ so re-runs only fetch new or
explicitly refreshed pages.

Usage:
  python3 fetch_liquipedia_drafts.py            # fetch missing pages + rebuild
  python3 fetch_liquipedia_drafts.py --offline  # rebuild json from cache only
  python3 fetch_liquipedia_drafts.py --refresh-current  # refetch current-year pages
"""

import gzip
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).parent
CACHE = HERE / "liquipedia_cache"
OUT = HERE / "pro_drafts.json"

API = "https://liquipedia.net/brawlstars/api.php"
UA = "brawl-digram/0.1 (draft-advisor research; contact@example.com)"
PARSE_INTERVAL = 31  # seconds between action=parse calls
QUERY_INTERVAL = 2.5

PREFIXES = [
    "Brawl_Stars_Championship/2025",
    "Brawl_Stars_Championship/2026",
    "Brawl_Stars_World_Finals/2024",
    "Brawl_Stars_World_Finals/2025",
    "Brawl_Stars_World_Finals/2026",
]

# Pages that carry per-game draft data. Open qualifiers / leaderboards /
# showmatches / statistics subpages don't (or aren't representative).
INCLUDE = re.compile(
    r"(Monthly Finals$|World Finals/\d{4}$|/Brawl Cup$|Last Chance Qualifier$"
    r"|Pre-Season Invitational/|Champions Invitational$|/Finals$"
    r"|Decider Playoffs$|Regional League/)"
)
EXCLUDE = re.compile(r"(Showmatch|Additional|Leaderboards|Statistics|Overview)")

_last_call = {"parse": 0.0, "query": 0.0}


def _throttle(kind):
    interval = PARSE_INTERVAL if kind == "parse" else QUERY_INTERVAL
    wait = _last_call[kind] + interval - time.time()
    if wait > 0:
        time.sleep(wait)
    _last_call[kind] = time.time()


def api_get(params, kind, retries=4):
    params = dict(params, format="json")
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(
        url, headers={"User-Agent": UA, "Accept-Encoding": "gzip"}
    )
    for attempt in range(retries):
        _throttle(kind)
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                raw = r.read()
                if r.headers.get("Content-Encoding") == "gzip":
                    raw = gzip.decompress(raw)
                return json.loads(raw)
        except Exception as e:  # includes 429/5xx/fork-adjacent network blips
            if attempt == retries - 1:
                raise
            backoff = 30 * (attempt + 1)
            print(f"  retry {attempt + 1} after error: {e} (sleep {backoff}s)")
            time.sleep(backoff)


def list_pages():
    titles = []
    for prefix in PREFIXES:
        offset = 0
        while True:
            d = api_get(
                {
                    "action": "query",
                    "list": "prefixsearch",
                    "pssearch": prefix,
                    "pslimit": 200,
                    "psoffset": offset,
                },
                "query",
            )
            batch = d.get("query", {}).get("prefixsearch", [])
            titles += [p["title"] for p in batch]
            cont = d.get("continue", {}).get("psoffset")
            if cont is None:
                break
            offset = cont
    keep = sorted(
        {t for t in titles if INCLUDE.search(t) and not EXCLUDE.search(t)}
    )
    return keep


def cache_path(title):
    return CACHE / (re.sub(r"[^A-Za-z0-9._-]+", "_", title) + ".wikitext")


def fetch_wikitext(title, refresh=False):
    p = cache_path(title)
    if p.exists() and not refresh:
        return p.read_text()
    print(f"fetching: {title}")
    d = api_get({"action": "parse", "page": title, "prop": "wikitext"}, "parse")
    if "error" in d:
        print(f"  skip ({d['error'].get('code')})")
        p.write_text("")  # cache the miss so we don't re-ask every run
        return ""
    wt = d["parse"]["wikitext"]["*"]
    p.write_text(wt)
    return wt


# ---- wikitext parsing -------------------------------------------------------

def extract_templates(text, name):
    """Return brace-balanced {{name ...}} template bodies."""
    out = []
    pat = re.compile(r"\{\{\s*" + name + r"\b", re.I)
    for m in pat.finditer(text):
        depth, i = 0, m.start()
        while i < len(text) - 1:
            if text[i : i + 2] == "{{":
                depth += 1
                i += 2
            elif text[i : i + 2] == "}}":
                depth -= 1
                i += 2
                if depth == 0:
                    out.append(text[m.start() : i])
                    break
            else:
                i += 1
    return out


def template_params(body):
    """Top-level |key=value pairs of a template body (nested {{}} skipped)."""
    params, depth, cur = {}, 0, []
    # strip outer braces and template name
    inner = body[2:-2]
    inner = inner[inner.find("|") :] if "|" in inner else ""
    i = 0
    while i < len(inner):
        c2 = inner[i : i + 2]
        if c2 == "{{" or c2 == "[[":
            depth += 1
            cur.append(c2)
            i += 2
        elif c2 == "}}" or c2 == "]]":
            depth -= 1
            cur.append(c2)
            i += 2
        elif inner[i] == "|" and depth == 0:
            seg = "".join(cur)
            if "=" in seg:
                k, _, v = seg.partition("=")
                params[k.strip().lower()] = v.strip()
            cur = []
            i += 1
        else:
            cur.append(inner[i])
            i += 1
    seg = "".join(cur)
    if "=" in seg:
        k, _, v = seg.partition("=")
        params[k.strip().lower()] = v.strip()
    return params


def load_name_canon():
    brawlers = json.load(open(HERE / "brawlers.json"))["brawlers"]
    canon = {}
    for b in brawlers:
        canon[b["name"].lower()] = b["name"]
    # Liquipedia spellings that differ from our display names. setdefault so a
    # correct entry derived from brawlers.json is never clobbered by an alias
    # (the old unconditional overwrite turned "Jae-Yong" into "Jae-yong").
    aliases = {
        "rt": "R-T", "r-t": "R-T", "8bit": "8-Bit", "8-bit": "8-Bit",
        "mr p": "Mr. P", "mr. p": "Mr. P", "mrp": "Mr. P", "mr.p": "Mr. P",
        "larry and lawrie": "Larry & Lawrie", "larry & lawrie": "Larry & Lawrie",
        "l&l": "Larry & Lawrie", "l & l": "Larry & Lawrie",
        "el primo": "El Primo", "elprimo": "El Primo", "primo": "El Primo",
        "dyna": "Dynamike", "jae": "Jae-Yong", "jae-yong": "Jae-Yong",
        "glowbert": "Glowy",  # Liquipedia uses Glowy's in-lore name
        "mico": "Mico", "moe": "Moe",
    }
    for k, v in aliases.items():
        canon.setdefault(k, v)
    # punctuation/space-insensitive fallback ("mr.p", "8 bit", ...) — built
    # last so exact keys always win
    canon["_stripped"] = {re.sub(r"[^a-z0-9]", "", k): v
                          for k, v in canon.items() if k != "_stripped"}
    return canon


def canon_name(raw, canon, unknown):
    key = raw.strip().lower()
    if not key:
        return None
    if key in canon:
        return canon[key]
    hit = canon["_stripped"].get(re.sub(r"[^a-z0-9]", "", key))
    if hit:
        return hit
    unknown[key] = unknown.get(key, 0) + 1
    return raw.strip().title()  # newer brawler than our bake — keep readable


def parse_event(title, wikitext, canon, unknown):
    games = []
    for match_body in extract_templates(wikitext, "Match"):
        mp = template_params(match_body)
        teams = []
        for k in ("opponent1", "opponent2"):
            t = mp.get(k, "")
            m = re.search(r"\{\{\s*TeamOpponent\s*\|([^}|]+)", t, re.I)
            teams.append(m.group(1).strip() if m else None)
        m = re.search(r"\d{4}-\d{2}-\d{2}", mp.get("date") or "")
        date = m.group(0) if m else None
        for map_body in extract_templates(match_body, "Map"):
            g = template_params(map_body)
            if not g.get("map"):
                continue
            picks = [
                [canon_name(g.get(f"t{t}c{i}", ""), canon, unknown) for i in (1, 2, 3)]
                for t in (1, 2)
            ]
            bans = [
                [canon_name(g.get(f"t{t}b{i}", ""), canon, unknown) for i in (1, 2, 3)]
                for t in (1, 2)
            ]
            if not any(picks[0]) and not any(picks[1]):
                continue  # scaffolded future game
            s1, s2 = g.get("score1", ""), g.get("score2", "")
            winner = None
            if s1.isdigit() and s2.isdigit():
                winner = 0 if int(s1) > int(s2) else (1 if int(s2) > int(s1) else None)
            games.append(
                {
                    "event": title,
                    "date": date,
                    "teams": teams,
                    "mode": g.get("maptype") or None,
                    "map": g.get("map"),
                    "picks": picks,
                    "bans": bans,
                    "firstPick": g.get("firstpick") or None,
                    "score": [s1 or None, s2 or None],
                    "winner": winner,
                }
            )
    return games


def main():
    offline = "--offline" in sys.argv
    refresh_current = "--refresh-current" in sys.argv
    CACHE.mkdir(exist_ok=True)

    if offline:
        titles = [
            p.stem.replace("_", " ") for p in sorted(CACHE.glob("*.wikitext"))
        ]
        # offline mode reparses whatever is cached; titles are display-lossy
        pages = {p.stem: p.read_text() for p in sorted(CACHE.glob("*.wikitext"))}
    else:
        titles = list_pages()
        print(f"{len(titles)} event pages selected")
        pages = {}
        for t in titles:
            refresh = refresh_current and "/2026" in t
            try:
                pages[t] = fetch_wikitext(t, refresh=refresh)
            except Exception as e:
                print(f"  FAILED {t}: {e}")

    canon = load_name_canon()
    unknown = {}
    games = []
    for title, wt in pages.items():
        if not wt:
            continue
        games += parse_event(title.replace("_", " "), wt, canon, unknown)

    # Sanitize volunteer data-entry errors (these exist on Liquipedia itself):
    # - a brawler listed twice in one team's picks -> the pick record is
    #   unusable, drop the whole game;
    # - a banned brawler also appearing in picks -> can't tell which record
    #   is wrong; picks are the load-bearing data, so blank that game's bans.
    clean, dropped_dup, bans_cleared = [], 0, 0
    for g in games:
        if any(len({p for p in team if p}) < len([p for p in team if p])
               for team in g["picks"]):
            dropped_dup += 1
            continue
        picked = {p for team in g["picks"] for p in team if p}
        if any(b in picked for team in g["bans"] for b in team if b):
            g["bans"] = [[None] * 3, [None] * 3]
            bans_cleared += 1
        clean.append(g)
    games = clean

    games_with_bans = sum(1 for g in games if any(g["bans"][0]))
    out = {
        "_meta": {
            "source": "Liquipedia Brawl Stars (liquipedia.net/brawlstars)",
            "license": "CC-BY-SA 3.0 — attribution required",
            "fetchedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "pages": len(pages),
            "games": len(games),
            "gamesWithBans": games_with_bans,
            "droppedDuplicatePicks": dropped_dup,
            "bansClearedPickOverlap": bans_cleared,
            "unmatchedNames": dict(sorted(unknown.items(), key=lambda kv: -kv[1])),
        },
        "games": games,
    }
    OUT.write_text(json.dumps(out, indent=1))
    print(
        f"wrote {OUT.name}: {len(games)} games ({games_with_bans} with bans) "
        f"from {len(pages)} pages; {len(unknown)} unmatched name variants"
    )


if __name__ == "__main__":
    main()
