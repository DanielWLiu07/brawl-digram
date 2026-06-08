"""Expanded version of build_map_name_map.py: walks every locations.csv row (not
just ranked_locations.csv) plus the leftover internal map names in maps-all.json,
and bridges to Brawlify hashes via the same credit-unique / position-by-id logic.

Output is data/map_name_map.json with the same schema as build_map_name_map.py:
  - modeMap: unchanged DEFAULT_MODE_MAP (csv map-prefix -> Brawlify gameMode)
  - maps:    { brawlifyHash: internalCSVName }
  - matchAudit: list of per-internal records with matchedBy + confidence

Collisions (two internals match the same Brawlify hash) keep the higher-
confidence entry; the loser is recorded with collisionWith in matchAudit and
its confidence is downgraded to "low".

Re-uses match_one() from build_map_name_map.py via import. Adds a richer
CSV_MODE_TO_BRAWLIFY covering all variations that have a clean 1-to-1 Brawlify
gameMode. CSV variations that don't have a clean Brawlify counterpart
(JellyCatch, CTF, Invasion, Spirit Wars compositions, ProtectKing, Tutorial,
test modes, etc.) are intentionally skipped.

Run with `python3 data/build_map_name_map_all.py`. The narrower ranked-only
script (data/build_map_name_map.py) is unchanged and still works."""

import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import build_map_name_map as ranked_builder

REPO = Path(__file__).resolve().parent.parent

# Expanded CSV GameModeVariation -> Brawlify gameMode name. Only modes with a
# clean 1-to-1 Brawlify counterpart are included. Modes that Brawlify merges
# under a different / composite gameMode (e.g. CTF + Invasion -> "Spirit Wars",
# or "ProtectKing" -> historical Hot Zone) are deliberately excluded so we
# don't fabricate matches.
CSV_MODE_TO_BRAWLIFY = {
    # Ranked / 3v3 core
    "GemGrab":           "Gem Grab",
    "BrawlBall":         "Brawl Ball",
    "BrawlBallV2":       "Brawl Ball",
    "Heist":             "Heist",
    "KingOfHill":        "Hot Zone",
    "Knockout":          "Knockout",
    "Bounty":            "Bounty",
    # 5v5
    "GemGrab5v5":        "Gem Grab 5v5",
    "BrawlBall5v5":      "Brawl Ball 5v5",
    "Knockout5v5":       "Knockout 5v5",
    "Deathmatch5v5":     "Wipeout 5v5",
    # 2v2 (party / community)
    "GemGrab2v2":        "Gem Grab 2v2",
    "BrawlBall2v2":      "Brawl Ball 2v2",
    "KingOfHill2v2":     "Hot Zone 2v2",
    "Knockout2v2":       "Knockout 2v2",
    "BasketBrawl2v2":    "Basket Brawl 2v2",
    "AirHockey2v2":      "Brawl Hockey 2v2",
    # Showdown family
    "Showdown":          "Solo Showdown",
    "DuoShowdown":       "Duo Showdown",
    "TrioShowdown":      "Trio Showdown",
    "ShowdownLimbo":     "Solo Showdown Limbo",
    "LoadedShowdown":    "Loaded Showdown",
    "LoadedDuoShowdown": "Loaded Duo Showdown",
    "KnockoutLimbo":     "Knockout Limbo",
    # Other PvP / featured
    "TagTeam":           "Duels",
    "Deathmatch":        "Wipeout",
    "TreasureHunt":      "Treasure Hunt",
    "VolleyBrawl":       "Volley Brawl",
    "BasketBrawl":       "Basket Brawl",
    "AirHockey":         "Brawl Hockey",
    "Payload":           "Payload",
    "PaintBall":         "Paint Brawl",
    "LoneStar":          "Lone Star",
    "Takedown":          "Takedown",
    # PvE-ish / special events
    "BigGame":           "Big Game",
    "BossFight":         "Boss Fight",
    "RoboRumble":        "Robo Rumble",
    "LastStand":         "Last Stand",
    "KillConfirmed":     "Soul Collector",
    "TrailRun":          "Subway Run",
}


def utc_now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_locations_rows():
    """Return every locations.csv row as (Map, GameModeVariation, CommunityCredit)."""
    with (REPO / "data/csv_logic/locations.csv").open() as f:
        r = csv.reader(f)
        headers = next(r)
        next(r)
        rows = list(r)
    idx = {h: i for i, h in enumerate(headers)}
    out = []
    for row in rows:
        if not row:
            continue
        m = row[idx["Map"]] if idx.get("Map") is not None else ""
        if not m:
            continue
        out.append({
            "internal":  m,
            "variation": row[idx["GameModeVariation"]],
            "credit":    row[idx["CommunityCredit"]],
            "csvName":   row[idx["Name"]],
        })
    return out


def confidence_rank(c):
    return {"high": 3, "med": 2, "low": 1}.get(c, 0)


def run():
    loc_records = load_locations_rows()
    bf = json.loads((REPO / "data/brawlify/maps.json").read_text())["data"]["list"]
    maps_all = json.loads((REPO / "data/maps-all.json").read_text())["maps"]

    # Swap in the expanded mode map for match_one's lookup
    ranked_builder.CSV_MODE_TO_BRAWLIFY = CSV_MODE_TO_BRAWLIFY

    bridge = {}             # brawlifyHash -> internal CSV name
    bridge_entry = {}       # brawlifyHash -> the audit entry that owns it
    audit = []
    seen_pair = set()       # de-dupe identical (internal, variation) rows

    for rec in loc_records:
        key = (rec["internal"], rec["variation"])
        if key in seen_pair:
            continue
        seen_pair.add(key)

        bf_map, how, conf = ranked_builder.match_one(
            rec["internal"], rec["variation"], rec["credit"], bf,
        )
        entry = {
            "internal":  rec["internal"],
            "csvName":   rec["csvName"] or None,
            "mode":      rec["variation"],
            "csvCredit": rec["credit"] or None,
            "matchedBy": how,
            "confidence": conf,
        }
        if bf_map:
            h = bf_map["hash"]
            entry.update({
                "brawlifyHash":     h,
                "brawlifyName":     bf_map["name"],
                "brawlifyDisabled": bool(bf_map.get("disabled")),
                "brawlifyCredit":   bf_map.get("credit"),
            })
            prev_internal = bridge.get(h)
            if prev_internal is None or prev_internal == rec["internal"]:
                bridge[h] = rec["internal"]
                bridge_entry[h] = entry
            else:
                # collision: keep whichever has higher confidence
                prev_entry = bridge_entry[h]
                if confidence_rank(conf) > confidence_rank(prev_entry["confidence"]):
                    prev_entry["collisionWith"] = rec["internal"]
                    prev_entry["confidence"] = "low"
                    bridge[h] = rec["internal"]
                    bridge_entry[h] = entry
                else:
                    entry["collisionWith"] = prev_internal
                    entry["confidence"] = "low"
        audit.append(entry)

    # Also attempt internals that are in maps-all.json but NOT in locations.csv
    # (rare; usually train / hidden / new maps). Drive them off the maps-all
    # mode prefix and the DEFAULT_MODE_MAP -> Brawlify lookup.
    known_internals = {r["internal"] for r in loc_records}
    for internal, m in maps_all.items():
        if internal in known_internals:
            continue
        bf_mode = ranked_builder.DEFAULT_MODE_MAP.get(m.get("mode"))
        if not bf_mode:
            audit.append({
                "internal":  internal,
                "csvName":   None,
                "mode":      m.get("mode"),
                "csvCredit": None,
                "matchedBy": "not-in-locations.csv,no-mode-map",
                "confidence": "low",
            })
            continue
        # Reverse-lookup which CSV variation key matches that Brawlify mode
        csv_variation = next(
            (k for k, v in CSV_MODE_TO_BRAWLIFY.items() if v == bf_mode),
            None,
        )
        if not csv_variation:
            audit.append({
                "internal":  internal,
                "csvName":   None,
                "mode":      m.get("mode"),
                "csvCredit": None,
                "matchedBy": "not-in-locations.csv,mode-not-bridged",
                "confidence": "low",
            })
            continue
        bf_map, how, conf = ranked_builder.match_one(internal, csv_variation, "", bf)
        entry = {
            "internal":  internal,
            "csvName":   None,
            "mode":      m.get("mode"),
            "csvCredit": None,
            "matchedBy": "not-in-locations.csv," + how,
            "confidence": "low",  # always downgrade since no credit
        }
        if bf_map:
            h = bf_map["hash"]
            entry.update({
                "brawlifyHash":     h,
                "brawlifyName":     bf_map["name"],
                "brawlifyDisabled": bool(bf_map.get("disabled")),
                "brawlifyCredit":   bf_map.get("credit"),
            })
            if h not in bridge:
                bridge[h] = internal
                bridge_entry[h] = entry
            else:
                entry["collisionWith"] = bridge[h]
        audit.append(entry)

    payload = {
        "fetchedAt": utc_now_iso(),
        "modeMap":   ranked_builder.DEFAULT_MODE_MAP,
        "maps":      bridge,
        "matchAudit": audit,
    }
    out_path = REPO / "data/map_name_map.json"
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False))

    matched = [a for a in audit if "brawlifyHash" in a]
    ctr = Counter(a["confidence"] for a in matched)
    print(f"wrote {out_path.relative_to(REPO)}")
    print(f"  {len(loc_records)} locations.csv rows -> {len(audit)} audit entries")
    print(f"  bridged {len(bridge)} brawlify hashes ({len(matched)} successful matches)")
    print(f"  confidence: high={ctr['high']}, med={ctr['med']}, low={ctr['low']}")
    print(f"  unbridged audit entries: {len(audit) - len(matched)}")


if __name__ == "__main__":
    run()
