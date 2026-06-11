#!/usr/bin/env python3
"""Mirror per-(brawler, map, mode) ladder/ranked stats from brawltime.ninja.

brawltime's Cube.js API is de-facto open: the site mints 1-hour JWTs from a
public, auth-free tRPC endpoint. We treat the source as BORROWED — it is
undocumented and could close at any time — so every pull is mirrored into a
patch-tagged snapshot under draft_stats/ that the advisor reads instead of
hitting the API live.

What we pull (current season window):
  - map cube, powerplay=1  → RANKED per-(brawler, mode, map) win/use/picks —
    ranked IS the draft mode, so this is the primary ladder signal.
  - map cube, powerplay=0, trophyRange>=10 → high-ladder fallback (denser).
  - brawlerAllies / brawlerEnemies cubes → pair win rates (synergy/counter
    seed validation), season-scoped, mode-agnostic to keep volume sane.

Usage: python3 fetch_brawltime_stats.py [--seasons N]
Output: draft_stats/<season-end-date>.json
"""

import json
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).parent
OUTDIR = HERE / "draft_stats"

TOKEN_URL = "https://brawltime.ninja/api/trpc/auth.getToken"
CUBE_URL = "https://cube.brawltime.ninja/cubejs-api/v1/load"
UA = "brawl-digram/0.1 (draft-advisor; contact@example.com)"


def http_json(url, data=None, headers=None, retries=4):
    req = urllib.request.Request(
        url, data=data, headers={"User-Agent": UA, **(headers or {})}
    )
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read())
        except Exception as e:
            if attempt == retries - 1:
                raise
            wait = 5 * (attempt + 1)
            print(f"  retry after {e} ({wait}s)")
            time.sleep(wait)


def get_token():
    d = http_json(TOKEN_URL, data=b"{}", headers={"Content-Type": "application/json"})
    return d["result"]["data"]["json"]["token"]


def cube_load(token, query):
    """Run a Cube query, following 'Continue wait' pre-aggregation responses."""
    qs = urllib.parse.urlencode({"query": json.dumps(query)})
    for _ in range(20):
        d = http_json(CUBE_URL + "?" + qs, headers={"Authorization": token})
        if d.get("error") == "Continue wait":
            time.sleep(2)
            continue
        if "error" in d:
            raise RuntimeError(d["error"])
        return d
    raise RuntimeError("cube query did not settle")


def cube_all_rows(token, query, page=50000):
    rows, offset = [], 0
    while True:
        d = cube_load(token, dict(query, limit=page, offset=offset))
        batch = d["data"]
        rows += batch
        if len(batch) < page:
            return rows, d.get("lastRefreshTime")
        offset += page


def latest_seasons(token, n):
    d = cube_load(
        token,
        {
            "measures": ["map.picks_measure"],
            "dimensions": ["map.season_dimension"],
            "order": {"map.season_dimension": "desc"},
            "limit": n,
        },
    )
    return [r["map.season_dimension"] for r in d["data"]]


def season_filter(cube, seasons):
    return {
        "member": f"{cube}.season_dimension",
        "operator": "gte",
        "values": [min(seasons).split("T")[0]],
    }


def main():
    n_seasons = 2
    if "--seasons" in sys.argv:
        n_seasons = int(sys.argv[sys.argv.index("--seasons") + 1])

    OUTDIR.mkdir(exist_ok=True)
    token = get_token()
    seasons = latest_seasons(token, n_seasons)
    print(f"seasons: {seasons}")
    season_key = max(seasons).split("T")[0]

    def map_slice(extra_filters, label):
        q = {
            "measures": [
                "map.winRate_measure",
                "map.winRateAdj_measure",
                "map.useRate_measure",
                "map.picks_measure",
            ],
            "dimensions": [
                "map.brawler_dimension",
                "map.mode_dimension",
                "map.map_dimension",
            ],
            "filters": [season_filter("map", seasons)] + extra_filters,
        }
        rows, refresh = cube_all_rows(token, q)
        print(f"{label}: {len(rows)} rows (lastRefresh {refresh})")
        out = []
        for r in rows:
            out.append(
                {
                    "brawler": r["map.brawler_dimension"],
                    "mode": r["map.mode_dimension"],
                    "map": r["map.map_dimension"],
                    "winRate": round(float(r["map.winRate_measure"] or 0), 4),
                    "winRateAdj": round(float(r["map.winRateAdj_measure"] or 0), 4),
                    "useRate": round(float(r["map.useRate_measure"] or 0), 6),
                    "picks": int(r["map.picks_measure"] or 0),
                }
            )
        return out

    ranked = map_slice(
        [{"member": "map.powerplay_dimension", "operator": "equals", "values": ["1"]}],
        "ranked (powerplay=1)",
    )
    ladder_high = map_slice(
        [
            {"member": "map.powerplay_dimension", "operator": "equals", "values": ["0"]},
            {"member": "map.trophyRange_dimension", "operator": "gte", "values": ["10"]},
        ],
        "high ladder (powerplay=0, trophyRange>=10)",
    )

    def pair_slice(cube, other_dim, label):
        q = {
            "measures": [f"{cube}.winRate_measure", f"{cube}.picks_measure"],
            "dimensions": [
                f"{cube}.brawler_dimension",
                f"{cube}.{other_dim}_dimension",
            ],
            "filters": [
                season_filter(cube, seasons),
                {
                    "member": f"{cube}.trophyRange_dimension",
                    "operator": "gte",
                    "values": ["10"],
                },
            ],
        }
        rows, _ = cube_all_rows(token, q)
        print(f"{label}: {len(rows)} rows")
        return [
            {
                "brawler": r[f"{cube}.brawler_dimension"],
                other_dim: r[f"{cube}.{other_dim}_dimension"],
                "winRate": round(float(r[f"{cube}.winRate_measure"] or 0), 4),
                "picks": int(r[f"{cube}.picks_measure"] or 0),
            }
            for r in rows
        ]

    allies = pair_slice("brawlerAllies", "ally", "allies")
    enemies = pair_slice("brawlerEnemies", "enemy", "enemies")

    out = {
        "_meta": {
            "source": "brawltime.ninja Cube API (undocumented; treat as borrowed)",
            "fetchedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "seasonsIncluded": seasons,
            "note": "ranked = powerplay battles (the in-game draft mode); "
            "ladderHigh = trophyRange>=10; pairs are mode-agnostic, "
            "trophyRange>=10, for synergy/counter seed validation",
        },
        "ranked": ranked,
        "ladderHigh": ladder_high,
        "allies": allies,
        "enemies": enemies,
    }
    path = OUTDIR / f"{season_key}.json"
    path.write_text(json.dumps(out, indent=1))
    print(
        f"wrote {path.relative_to(HERE)}: ranked={len(ranked)} ladder={len(ladder_high)} "
        f"allies={len(allies)} enemies={len(enemies)}"
    )


if __name__ == "__main__":
    main()
