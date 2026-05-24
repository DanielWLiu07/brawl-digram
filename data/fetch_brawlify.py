"""Refresh upstream info that changes (rotation, catalog deltas) from Brawlify.

Lightweight, JSON-only. Does NOT download PNGs — that's `download_assets.py`'s
job. Run weekly via cron; ranked pools change per season (~2 months), so
weekly is plenty.

Outputs (all under `data/brawlify/`):
  events.json     — /v1/events response (active + upcoming slots)
  maps.json       — /v1/maps catalog (full index, disabled flag included)
  brawlers.json   — /v1/brawlers catalog
  gamemodes.json  — /v1/gamemodes catalog

Plus a derived top-level file:
  data/ranked-rotation.json — slim view of the current ranked map pool,
                              derived from events.active filtered to slots
                              whose `slot.name` contains "Ranked" (case-insensitive).
                              Always written, even if active=[] (between
                              seasons), so downstream code can rely on the
                              file existing.

Each output file has a `fetchedAt` ISO-8601 UTC timestamp at the top.
"""

import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT_DIR = REPO / "data" / "brawlify"
ROTATION_FILE = REPO / "data" / "ranked-rotation.json"

BRAWLIFY = "https://api.brawlify.com/v1"
ENDPOINTS = {
    "events":    f"{BRAWLIFY}/events",
    "maps":      f"{BRAWLIFY}/maps",
    "brawlers":  f"{BRAWLIFY}/brawlers",
    "gamemodes": f"{BRAWLIFY}/gamemodes",
}

HDRS = {"User-Agent": "Mozilla/5.0 (brawl-digram dev)"}


def utc_now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def fetch(url, retries=3, backoff=2.0):
    last_err = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=HDRS)
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read())
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
            last_err = e
            if attempt < retries - 1:
                time.sleep(backoff ** attempt)
    raise RuntimeError(f"failed to fetch {url}: {last_err}")


def write_json(path: Path, payload: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False))


def is_ranked_slot(slot: dict) -> bool:
    """Brawlify event slots include a `slot` sub-object with a `name` like
    'Ranked', 'Trio Showdown', 'Brawl Ball', etc. We treat anything whose
    slot.name contains 'ranked' as the ranked pool. This is heuristic — if
    Brawlify changes its labelling, the script keeps working but rotation
    may go empty until updated."""
    slot_meta = slot.get("slot") or {}
    name = (slot_meta.get("name") or "").lower()
    return "ranked" in name


def derive_rotation(events: dict) -> dict:
    """Pull current ranked maps out of /v1/events.active. Each active entry
    is a slot containing `map` and `slot` sub-objects."""
    active = events.get("active") or []
    ranked = []
    for slot in active:
        if not is_ranked_slot(slot):
            continue
        m = slot.get("map") or {}
        gm = m.get("gameMode") or {}
        ranked.append({
            "mapId":       m.get("id"),
            "mapName":     m.get("name"),
            "mapHash":     m.get("hash"),
            "gameMode":    gm.get("name"),
            "startTime":   slot.get("startTime"),
            "endTime":     slot.get("endTime"),
            "slotName":    (slot.get("slot") or {}).get("name"),
        })
    return {
        "fetchedAt": utc_now_iso(),
        "source": "brawlify /v1/events filtered to slot.name~=ranked",
        "count": len(ranked),
        "maps": ranked,
    }


def run():
    print(f"Fetching {len(ENDPOINTS)} endpoints from {BRAWLIFY}...")
    snapshots = {}
    for name, url in ENDPOINTS.items():
        print(f"  {name}: {url}")
        data = fetch(url)
        snapshots[name] = data
        write_json(OUT_DIR / f"{name}.json", {
            "fetchedAt": utc_now_iso(),
            "source": url,
            "data": data,
        })

    rotation = derive_rotation(snapshots["events"])
    write_json(ROTATION_FILE, rotation)

    print()
    print("=== summary ===")
    for name, data in snapshots.items():
        if isinstance(data, dict) and "list" in data:
            count = len(data["list"])
            note = f"{count} entries"
        elif name == "events":
            note = f"active={len(data.get('active') or [])}, upcoming={len(data.get('upcoming') or [])}"
        else:
            note = "ok"
        print(f"  {name:10s} {note}")
    print(f"  ranked     {rotation['count']} maps -> {ROTATION_FILE.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(run())
