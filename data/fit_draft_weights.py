#!/usr/bin/env python3
"""Fit interpretable draft weights from pro picks/bans + ladder win rates.

Model: ridge regression over NAMED attribute × map-geometry × mode features.
The label per (brawler, mode, map) is the pro draft-presence z-score
Bayesian-shrunk toward the ranked-ladder win-rate z-score (pro = gold but
thin; ladder = dense). Because features are brawler ATTRIBUTES (range/HP/
mobility/thrower/...), not identities, the model generalizes to new maps and
survives balance patches: a patch changes a brawler's inputs, not the model.

Inputs:  brawlers.json, ability_mechanics.json, map_descriptors.json,
         map_name_map.json, pro_drafts.json, draft_stats/<latest>.json
Output:  draft_ai.json — weights + baked brawler attrs + per-(mode,map) stats
         tables consumed by the whiteboard Draft tab.
"""

import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
OUT = HERE / "draft_ai.json"

K_SHRINK = 25        # pro games at which pro signal outweighs ladder prior
RIDGE_GRID = [1.0, 3.0, 10.0, 30.0, 100.0, 300.0, 1000.0]
MIN_LADDER_PICKS = 50
MIN_PRO_GAMES = 4

# mode families: internal grid modes + stat-source spellings all normalize here
MODE_FAM = {
    "gemgrab": "Gemgrab", "gem grab": "Gemgrab",
    "bounty": "Wanted", "wanted": "Wanted",
    "heist": "Bankheist", "bankheist": "Bankheist",
    "brawlball": "Ball", "brawl ball": "Ball", "brawlballv2": "Ball",
    "laserball": "Ball", "airhockey": "Ball", "brawl hockey": "Ball",
    "hotzone": "KingOfHill", "hot zone": "KingOfHill", "kingofhill": "KingOfHill",
    "knockout": "Knockout",
}
MODES = ["Gemgrab", "Wanted", "Bankheist", "Ball", "KingOfHill", "Knockout"]


def norm_key(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def mode_fam(s):
    return MODE_FAM.get(norm_key(s)) or MODE_FAM.get((s or "").lower())


# ---- brawler attributes (must mirror attrsFor() in whiteboard.html) ---------

def brawler_attrs():
    brawlers = json.load(open(HERE / "brawlers.json"))["brawlers"]
    attrs = {}
    for b in brawlers:
        atk = next((v for v in b["variants"] if v["label"].lower().startswith("attack")),
                   b["variants"][0] if b["variants"] else {})
        p = atk.get("params", {})
        rng = p.get("rangeTiles") or 0
        thrower = atk.get("shape") in ("placement", "cluster") and bool(atk.get("passesWalls"))
        attrs[b["name"]] = {
            "thrower": 1.0 * thrower,
            "sniper": 1.0 * (rng >= 8.5 and not thrower),
            "shortRange": 1.0 * (0 < rng <= 4.5),
            "tank": 1.0 * ((b.get("hp") or 0) >= 4800),
            "fast": 1.0 * ((b.get("speedTilesPerSec") or 0) >= 2.6),
            "rangeN": round(min(rng, 12) / 12, 4),
            "hpN": round(min(b.get("hp") or 3000, 7000) / 7000, 4),
            "speedN": round(min(b.get("speedTilesPerSec") or 2.0, 3.2) / 3.2, 4),
            "melee": 1.0 * (b.get("attackStyle") == "melee"),
        }
    return attrs


ATTR_NAMES = ["thrower", "sniper", "shortRange", "tank", "fast",
              "rangeN", "hpN", "speedN", "melee"]
GEO_NAMES = ["wallPct", "bushPct", "openPct", "sightlineFrac",
             "midOpenness", "chokesPerRowN", "avgLaneWidthN"]


def geo_vector(d):
    return {
        "wallPct": d["wallPct"],
        "bushPct": d["bushPct"],
        "openPct": d["openPct"],
        "sightlineFrac": d["sightlineFrac"],
        "midOpenness": d["midOpenness"],
        "chokesPerRowN": min(d["chokesPerRow"], 3) / 3,
        "avgLaneWidthN": min(d["avgLaneWidth"], 10) / 10,
    }


def feature_names():
    names = []
    for a in ATTR_NAMES:
        names.append(a)                                # main effect
        names += [f"{a}*{g}" for g in GEO_NAMES]       # geometry interactions
        names += [f"{a}@{m}" for m in MODES]           # mode interactions
    return names


def feature_row(attr, geo, mode):
    row = []
    for a in ATTR_NAMES:
        av = attr[a]
        row.append(av)
        row += [av * geo[g] for g in GEO_NAMES]
        row += [av * (1.0 if mode == m else 0.0) for m in MODES]
    return row


# ---- data assembly ----------------------------------------------------------

def load_stats():
    latest = sorted((HERE / "draft_stats").glob("*.json"))[-1]
    return json.load(open(latest)), latest.name


def main():
    attrs = brawler_attrs()
    canon = {norm_key(k): k for k in attrs}
    desc = json.load(open(HERE / "map_descriptors.json"))
    bridge = json.load(open(HERE / "map_name_map.json"))["maps"]
    # display map key -> internal grid name
    disp2int = {norm_key(slug): internal for slug, internal in bridge.items()}

    stats, stats_file = load_stats()
    pro = json.load(open(HERE / "pro_drafts.json"))

    # All map keys are INTERNAL grid names (Gemgrab_1...): canonical, shared by
    # seasonal reskins, and exactly what the whiteboard has at lookup time.
    unresolved_maps = {}

    def resolve_internal(disp):
        internal = disp2int.get(norm_key(disp))
        if internal is None:
            unresolved_maps[disp] = unresolved_maps.get(disp, 0) + 1
        return internal

    # ladder table: (modeFam, internal) -> {brawler: {wr, n, ur}}, ranked preferred
    ladder = {}
    for source, rows in (("ranked", stats["ranked"]), ("ladderHigh", stats["ladderHigh"])):
        for r in rows:
            fam = mode_fam(r["mode"])
            if not fam:
                continue
            bname = canon.get(norm_key(r["brawler"]))
            if not bname:
                continue
            internal = resolve_internal(r["map"])
            if internal is None or r["picks"] < MIN_LADDER_PICKS:
                continue
            cell = ladder.setdefault((fam, internal), {}).setdefault(
                bname, {"wr": None, "n": 0, "ur": 0, "src": None}
            )
            better = (
                cell["src"] is None
                or (cell["src"] == "ladderHigh" and source == "ranked")
                or (cell["src"] == source and r["picks"] > cell["n"])
            )
            if better:
                cell.update(wr=r["winRateAdj"], n=r["picks"],
                            ur=r["useRate"], src=source)

    # pro table: (modeFam, internal) -> {games, perBrawler {p, b}}
    pro_tbl = {}
    unmatched = {}
    for g in pro["games"]:
        fam = mode_fam(g["mode"] or "")
        if not fam:
            continue
        internal = resolve_internal(g["map"])
        if internal is None:
            continue
        cell = pro_tbl.setdefault((fam, internal), {"games": 0, "display": g["map"], "per": {}})
        cell["games"] += 1
        for names, field in ((g["picks"], "p"), (g["bans"], "b")):
            for team in names:
                for nm in team or []:
                    if not nm:
                        continue
                    cn = canon.get(norm_key(nm))
                    if not cn:
                        unmatched[nm] = unmatched.get(nm, 0) + 1
                        cn = nm  # keep — newer brawler than our bake
                    rec = cell["per"].setdefault(cn, {"p": 0, "b": 0})
                    rec[field] += 1

    # training rows
    keys = set(ladder) | set(pro_tbl)
    rows, ys, infos = [], [], []
    for fam, internal in sorted(keys):
        d = desc.get(internal)
        if d is None:
            continue
        geo = geo_vector(d)
        lad = ladder.get((fam, internal), {})
        prc = pro_tbl.get((fam, internal))
        n_pro_games = prc["games"] if prc else 0

        # z-scores within this map cell
        lad_deltas = {b: c["wr"] - 0.5 for b, c in lad.items() if c["wr"] is not None}
        mu_l = np.mean(list(lad_deltas.values())) if lad_deltas else 0.0
        sd_l = np.std(list(lad_deltas.values())) or 1.0 if lad_deltas else 1.0

        pres = {}
        if prc and n_pro_games >= MIN_PRO_GAMES:
            for b, pb in prc["per"].items():
                pres[b] = (pb["p"] + pb["b"]) / n_pro_games
        mu_p = np.mean(list(pres.values())) if pres else 0.0
        sd_p = np.std(list(pres.values())) or 1.0 if pres else 1.0

        for bname, a in attrs.items():
            z_l = ((lad_deltas[bname] - mu_l) / sd_l) if bname in lad_deltas else None
            # absent from pro draft on a played map IS signal (presence 0)
            z_p = ((pres.get(bname, 0.0) - mu_p) / sd_p) if pres else None
            if z_l is None and z_p is None:
                continue
            if z_p is None:
                y = z_l
            elif z_l is None:
                y = z_p
            else:
                y = (n_pro_games * z_p + K_SHRINK * z_l) / (n_pro_games + K_SHRINK)
            rows.append(feature_row(a, geo, fam))
            ys.append(y)
            infos.append((fam, internal, bname))

    X = np.array(rows)
    y = np.array(ys)
    names = feature_names()
    print(f"training rows: {len(y)}  features: {X.shape[1]}")
    print(f"pro cells: {len(pro_tbl)}  ladder cells: {len(ladder)}  "
          f"unmatched pro names: {dict(sorted(unmatched.items(), key=lambda kv: -kv[1])[:8])}")
    if unresolved_maps:
        print(f"unresolved map names (no bridge entry): "
              f"{dict(sorted(unresolved_maps.items(), key=lambda kv: -kv[1])[:10])}")

    # standardize features, ridge with leave-map-out-ish CV (by map hash bucket)
    mu, sd = X.mean(0), X.std(0)
    sd[sd == 0] = 1.0
    Xs = (X - mu) / sd
    buckets = np.array([hash(i[1]) % 5 for i in infos])
    best = None
    for lam in RIDGE_GRID:
        errs = []
        for f in range(5):
            tr, te = buckets != f, buckets == f
            A = Xs[tr].T @ Xs[tr] + lam * np.eye(Xs.shape[1])
            w = np.linalg.solve(A, Xs[tr].T @ y[tr])
            errs.append(np.mean((Xs[te] @ w - y[te]) ** 2))
        mse = float(np.mean(errs))
        r2 = 1 - mse / float(np.var(y))
        print(f"  lambda={lam:5.1f}  cv-mse={mse:.4f}  cv-R2={r2:.3f}")
        if best is None or mse < best[1]:
            best = (lam, mse, r2)
    lam, _, cv_r2 = best
    A = Xs.T @ Xs + lam * np.eye(Xs.shape[1])
    w_std = np.linalg.solve(A, Xs.T @ y)
    # de-standardize so JS can use raw features: y = b0 + sum(w_raw * f)
    w_raw = w_std / sd
    b0 = float(-np.sum(w_std * mu / sd))

    top = sorted(zip(names, w_raw), key=lambda kv: -abs(kv[1]))[:14]
    print("top weights:")
    for n, v in top:
        print(f"  {n:28} {v:+.3f}")

    # ---- bake output ---------------------------------------------------
    stats_out = {}
    for fam, internal in sorted(keys):
        prc = pro_tbl.get((fam, internal))
        lad = ladder.get((fam, internal), {})
        entry = {
            "display": (prc or {}).get("display")
            or next((s.replace("-", " ") for s, i in bridge.items()
                     if i == internal), internal),
            "proGames": prc["games"] if prc else 0,
            "pro": {b: [v["p"], v["b"]] for b, v in (prc["per"].items() if prc else [])},
            "ladder": {
                b: [c["wr"], c["n"], round(c["ur"], 5)]
                for b, c in lad.items() if c["wr"] is not None
            },
        }
        # brawltime's tracked population wins well above 50% (~0.69 ranked
        # slice mean), so the UI must present deltas vs this mean, never raw %
        wrs = [v[0] for v in entry["ladder"].values()]
        entry["wrMean"] = round(sum(wrs) / len(wrs), 4) if wrs else 0.5
        if entry["pro"] or entry["ladder"]:
            stats_out[f"{fam}|{internal}"] = entry

    # mode-level aggregates (fallback for custom/unknown maps)
    mode_out = {}
    for fam in MODES:
        pro_agg, games = {}, 0
        lad_acc = {}
        for (f2, _mk), prc in pro_tbl.items():
            if f2 != fam:
                continue
            games += prc["games"]
            for b, v in prc["per"].items():
                a = pro_agg.setdefault(b, [0, 0])
                a[0] += v["p"]
                a[1] += v["b"]
        for (f2, _mk), lad in ladder.items():
            if f2 != fam:
                continue
            for b, c in lad.items():
                if c["wr"] is None:
                    continue
                acc = lad_acc.setdefault(b, [0.0, 0])
                acc[0] += c["wr"] * c["n"]
                acc[1] += c["n"]
        mode_ladder = {b: [round(s / n, 4), n] for b, (s, n) in lad_acc.items() if n}
        wrs = [v[0] for v in mode_ladder.values()]
        mode_out[fam] = {
            "proGames": games,
            "pro": pro_agg,
            "ladder": mode_ladder,
            "wrMean": round(sum(wrs) / len(wrs), 4) if wrs else 0.5,
        }

    out = {
        "_meta": {
            "builtAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "statsSnapshot": stats_file,
            "proGames": pro["_meta"]["games"],
            "trainRows": len(y),
            "lambda": lam,
            "cvR2": round(cv_r2, 3),
            "label": f"pro presence z shrunk to ladder wr z (K={K_SHRINK})",
            "sources": [pro["_meta"]["source"], stats["_meta"]["source"]],
        },
        "modes": MODES,
        "attrNames": ATTR_NAMES,
        "geoNames": GEO_NAMES,
        "intercept": round(b0, 5),
        "weights": {n: round(float(v), 5) for n, v in zip(names, w_raw)},
        "attrs": attrs,
        "stats": stats_out,
        "modeStats": mode_out,
    }
    OUT.write_text(json.dumps(out))
    print(f"wrote {OUT.name} ({OUT.stat().st_size // 1024} KB, "
          f"{len(stats_out)} map cells)")


if __name__ == "__main__":
    main()
