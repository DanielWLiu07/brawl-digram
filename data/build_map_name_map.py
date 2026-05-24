"""Auto-match ranked_locations.csv to Brawlify hashes by community credit, then
by position (Nth Brawlify map of same gameMode, ordered by id). Writes
data/map_name_map.json with a per-entry confidence flag."""

import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

CSV_MODE_TO_BRAWLIFY = {
    "Bounty":     "Bounty",
    "BrawlBall":  "Brawl Ball",
    "GemGrab":    "Gem Grab",
    "Heist":      "Heist",
    "KingOfHill": "Hot Zone",
    "Knockout":   "Knockout",
}

DEFAULT_MODE_MAP = {
    "Gemgrab": "Gem Grab", "GemGrab5v5": "Gem Grab 5v5",
    "TrioGemgrab": "Trio Gem Grab", "Bankheist": "Heist",
    "BrawlBallV2": "Brawl Ball", "BrawlBall5v5": "Brawl Ball 5v5",
    "Laserball": "Brawl Hockey", "Knockout": "Knockout",
    "Knockout5v5": "Knockout 5v5", "KingOfHill": "Hot Zone",
    "Wanted": "Bounty", "Solobounty": "Solo Bounty",
    "Survival": "Solo Showdown", "DuoSurvival": "Duo Showdown",
    "TrioSurvival": "Trio Showdown", "TreasureHunt": "Treasure Hunt",
    "Siege": "Siege", "SiegeSmall": "Siege", "Payload": "Payload",
    "AirHockey": "Brawl Hockey", "BasketBrawl": "Basket Brawl",
    "VolleyBrawl": "Volley Brawl", "Dribble": "Dribble",
    "Deathmatch": "Wipeout", "TagTeam": "Duels",
    "PaintBall": "Paint Brawl", "Invasion": "Invasion",
    "BossRace": "Boss Race", "CaptureTheFlag": "Capture the Flag",
}


def utc_now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def norm_credit(c):
    if not c:
        return ""
    return c.strip().lower().replace("⚡", "").replace(" ", "").replace("|", "")


def load_inputs():
    with (REPO / "data/csv_logic/ranked_locations.csv").open() as f:
        r = csv.reader(f); next(r); next(r)
        ranked_names = [row[0] for row in r if row and row[0]]
    with (REPO / "data/csv_logic/locations.csv").open() as f:
        r = csv.reader(f); headers = next(r); next(r)
        rows = list(r)
    loc_idx = {h: i for i, h in enumerate(headers)}
    bf = json.loads((REPO / "data/brawlify/maps.json").read_text())["data"]["list"]
    return ranked_names, rows, loc_idx, bf


def candidates_by_mode(bf, bf_mode):
    return sorted(
        [m for m in bf if (m.get("gameMode") or {}).get("name") == bf_mode],
        key=lambda m: m["id"],
    )


def match_one(internal, csv_mode, credit, bf):
    bf_mode = CSV_MODE_TO_BRAWLIFY.get(csv_mode)
    if not bf_mode:
        return None, "no-mode-map", "low"
    cands = candidates_by_mode(bf, bf_mode)
    csv_credit_n = norm_credit(credit)
    if csv_credit_n:
        hits = [c for c in cands if norm_credit(c.get("credit")) == csv_credit_n]
        if len(hits) == 1:
            return hits[0], "credit-unique", "high"
        if len(hits) > 1:
            suffix = internal.split("_", 1)[1] if "_" in internal else ""
            m = re.match(r"^(\d+)", suffix)
            if m:
                n = int(m.group(1))
                if 1 <= n <= len(cands) and cands[n - 1] in hits:
                    return cands[n - 1], "credit+position", "high"
            return hits[0], "credit-multi-firstpick", "med"
    suffix = internal.split("_", 1)[1] if "_" in internal else ""
    m = re.match(r"^(\d+)", suffix)
    if not m:
        return None, "no-index", "low"
    n = int(m.group(1))
    if not (1 <= n <= len(cands)):
        return None, f"index-out-of-range(N={n})", "low"
    pos = cands[n - 1]
    bf_credit_n = norm_credit(pos.get("credit"))
    if csv_credit_n and bf_credit_n and csv_credit_n != bf_credit_n:
        return pos, "position-credit-conflict", "low"
    return pos, "position-only", ("low" if pos.get("disabled") else "med")


def run():
    ranked_names, loc_rows, loc_idx, bf = load_inputs()
    bridge = {}
    audit = []
    for rn in ranked_names:
        row = next(r for r in loc_rows if r[loc_idx["Name"]] == rn)
        internal = row[loc_idx["Map"]]
        csv_mode = row[loc_idx["GameModeVariation"]]
        credit = row[loc_idx["CommunityCredit"]]
        bf_map, how, conf = match_one(internal, csv_mode, credit, bf)
        entry = {
            "internal": internal,
            "mode": csv_mode,
            "csvCredit": credit or None,
            "matchedBy": how,
            "confidence": conf,
        }
        if bf_map:
            if bf_map["hash"] in bridge and bridge[bf_map["hash"]] != internal:
                entry["collisionWith"] = bridge[bf_map["hash"]]
                entry["confidence"] = "low"
            else:
                bridge[bf_map["hash"]] = internal
            entry.update({
                "brawlifyHash":     bf_map["hash"],
                "brawlifyName":     bf_map["name"],
                "brawlifyDisabled": bool(bf_map.get("disabled")),
                "brawlifyCredit":   bf_map.get("credit"),
            })
        audit.append(entry)

    payload = {
        "fetchedAt": utc_now_iso(),
        "modeMap": DEFAULT_MODE_MAP,
        "maps": bridge,
        "matchAudit": audit,
    }
    out = REPO / "data/map_name_map.json"
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    from collections import Counter
    ctr = Counter(a["confidence"] for a in audit)
    print(f"wrote {out.relative_to(REPO)}")
    print(f"  18 ranked maps -> {len(bridge)} bridge entries")
    print(f"  confidence: high={ctr['high']}, med={ctr['med']}, low={ctr['low']}")
    print(f"  verify the {ctr['low']} low-confidence entries in data/maps_compare.html")


if __name__ == "__main__":
    run()
