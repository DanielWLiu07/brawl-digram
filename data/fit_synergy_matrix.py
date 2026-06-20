#!/usr/bin/env python3
"""Fit pairwise SYNERGY and COUNTER matrices from brawltime pair win-rate data.

INPUT DATA (draft_stats/<latest>.json):
  _meta        — fetch provenance; seasonsIncluded gives patch window
  ranked       — list of {brawler, mode, map, winRate, winRateAdj, useRate, picks}
                 Win rate in the ranked (powerplay / draft) queue, per-map.
                 NOTE: winRateAdj is heavily sample-corrected and NOT used here;
                 raw winRate is used.
  ladderHigh   — same shape but trophyRange>=10, all modes (broader sample)
  allies       — list of {brawler, ally, winRate, picks}
                 Semantics: conditional win rate of `brawler` in games where
                 `ally` is on the SAME team.  Asymmetric — (A|B) ≠ (B|A) because
                 brawltime counts each player's own row separately (pick-based
                 perspective, not game-based).
                 Self-pairs (brawler == ally) exist when both teams field the same
                 brawler — unusual, skipped in this analysis.
  enemies      — list of {brawler, enemy, winRate, picks}
                 Semantics: conditional win rate of `brawler` in games where
                 `enemy` is on the OPPOSING team.
                 IMPORTANT: WR(A vs B) + WR(B vs A) ≈ 1.20 (NOT 1.0).  This is
                 because brawltime counts from each player's perspective in a 3v3
                 game; high-trophy players on both sides of a match both show
                 above-50% win rates since the cube excludes low-trophy games.
                 Consequently, raw WR cannot be used as a zero-sum counter signal
                 without correcting for each brawler's population baseline.

METHODOLOGY — Bayesian-shrunk signed-delta approach:

  BASELINES
  ---------
  For SYNERGY, the baseline for brawler A is computed as:
    base_A = weighted average of WR(A|B) over all tracked partners B
  This keeps the comparison within the ally-tracking population (same trophy
  slice and mode distribution) and avoids cross-population noise.

  For COUNTER, the baseline for brawler A is:
    base_A = weighted average of WR(A vs E) over all tracked enemies E
  Again, staying in-population for the enemy-tracking cube.

  SYNERGY DELTA
  -------------
  For unordered pair {A, B}, average the conditional WRs from both directions
  (weighted by sample size), then subtract the average of A's and B's baselines:
    raw_delta_syn = mean_w(WR(A|B), WR(B|A)) - mean(base_A, base_B)
  Positive = pair performs better together than their individual baselines suggest.
  Negative = pair is worse together (e.g. two brawlers who need the same lane type).

  COUNTER DELTA
  -------------
  For unordered pair {A, B}, combine both perspectives as relative deviations:
    from_A = WR(A vs B) - base_A      # A outperforms/underperforms its own mean vs B
    from_B = -(WR(B vs A) - base_B)   # B's perspective flipped to A's POV
    raw_delta_ctr = weighted_mean(from_A, from_B)
  Positive = A has an advantage over B relative to both brawlers' baselines.
  The canonical edge is stored with the higher-delta side first (positive delta).

  SHRINKAGE
  ---------
  Bayesian shrinkage toward 0: δ_shrunk = δ * n / (n + PRIOR_N)
  where PRIOR_N is set so a pair at ~100 picks retains ~50% of its observed delta.
  Edges below ABS_THRESHOLD (after shrinkage) are dropped.
  Sample count is preserved on every edge so the advisor can cite it, e.g.:
    "MORTIS beats BARLEY by +9.8% relative WR (n=38,395 games)"

OUTPUT: data/draft_synergy_matrix.json
  _meta           — provenance, method summary, all thresholds
  brawlerStrength — {name: {baseWR, baseEnemyWR, picks, rank}} per-brawler baselines
  synergy         — edge list sorted by |delta| descending
                    {a, b, delta, rawDelta, picks, confidence}
                    positive = a+b better together than their solo baselines
                    negative = a+b worse together (scheduling conflict / lane clash)
  counter         — edge list sorted by delta descending
                    {a, b, delta, rawDelta, picks, confidence}
                    positive = a has advantage over b relative to both baselines
                    ALL stored as positive (a is the advantaged brawler)

NAMING: ALL-CAPS as in the source CSV (e.g. "STARR NOVA", "LARRY & LAWRIE").
The advisor normalises to display names at render time via brawlers.json.

Delta semantics: raw win-rate delta (range approximately [-0.15, +0.15]).
To convert to log-odds units (compatible with kb/matrix.json deltaRating):
  logit(0.5 + delta) - logit(0.5) ≈ 4 * delta  for |delta| < 0.1
"""

import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).parent
STATS_DIR = HERE / "draft_stats"
OUT = HERE / "draft_synergy_matrix.json"

# ---- thresholds ---------------------------------------------------------------
# Bayesian prior sample size.  A pair with exactly PRIOR_N picks retains 50% of
# its observed delta after shrinkage.  PRIOR_N=100 means we need ~200 picks to
# trust 67% of the signal; ~500 picks for 83%.
PRIOR_N = 100

# Minimum raw picks before a pair is even considered (pre-shrinkage gate).
MIN_ALLY_PICKS = 50
MIN_ENEMY_PICKS = 50

# Post-shrinkage absolute threshold.  Edges below this are dropped as noise.
ALLY_ABS_THRESHOLD = 0.01     # 1 pp synergy advantage; low bar by design
ENEMY_ABS_THRESHOLD = 0.015   # 1.5 pp counter advantage


# ---- helpers ------------------------------------------------------------------

def norm_key(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def load_latest_stats() -> tuple[dict, str]:
    files = sorted(STATS_DIR.glob("*.json"))
    if not files:
        raise FileNotFoundError(f"No stats files in {STATS_DIR}")
    latest = files[-1]
    return json.loads(latest.read_text()), latest.name


# ---- per-brawler baselines ----------------------------------------------------

def compute_ally_baselines(allies: list[dict]) -> dict[str, float]:
    """Marginal win rate for each brawler in the ally-tracking population.

    For brawler A: weighted average of WR(A | B) over all B (excluding self).
    This is the correct in-population baseline for computing synergy deltas,
    since the ally data comes from a different trophy/mode slice than ranked.
    """
    acc: dict[str, dict] = defaultdict(lambda: {"wsum": 0.0, "n": 0})
    for row in allies:
        a, b = row["brawler"], row["ally"]
        if a == b:
            continue
        acc[a]["wsum"] += row["winRate"] * row["picks"]
        acc[a]["n"] += row["picks"]
    return {k: v["wsum"] / v["n"] for k, v in acc.items() if v["n"] > 0}


def compute_enemy_baselines(enemies: list[dict]) -> dict[str, float]:
    """Marginal win rate for each brawler in the enemy-tracking population.

    For brawler A: weighted average of WR(A vs E) over all opponents E.
    This baseline corrects for the population-level WR inflation that
    makes both sides of a matchup show above-50% win rates.
    """
    acc: dict[str, dict] = defaultdict(lambda: {"wsum": 0.0, "n": 0})
    for row in enemies:
        acc[row["brawler"]]["wsum"] += row["winRate"] * row["picks"]
        acc[row["brawler"]]["n"] += row["picks"]
    return {k: v["wsum"] / v["n"] for k, v in acc.items() if v["n"] > 0}


def compute_ranked_baselines(ranked: list[dict], ladder_high: list[dict]) -> dict[str, dict]:
    """Per-brawler baseline from ranked (preferred) + ladderHigh (fallback).

    Used only for brawlerStrength output, not for the synergy/counter math
    (which uses its own in-population baselines).
    """
    acc: dict[str, dict] = defaultdict(lambda: {"wsum": 0.0, "n": 0, "has_ranked": False})
    for source, rows in (("ranked", ranked), ("ladderHigh", ladder_high)):
        for r in rows:
            name = r["brawler"]
            n = r["picks"]
            if n < 1:
                continue
            cell = acc[name]
            if source == "ranked":
                cell["wsum"] += r["winRate"] * n
                cell["n"] += n
                cell["has_ranked"] = True
            elif not cell["has_ranked"]:
                cell["wsum"] += r["winRate"] * n
                cell["n"] += n

    result: dict[str, dict] = {}
    for name, cell in acc.items():
        if cell["n"] == 0:
            continue
        result[name] = {"baseWR": round(cell["wsum"] / cell["n"], 6), "picks": cell["n"]}
    for rank, (name, _) in enumerate(sorted(result.items(), key=lambda kv: -kv[1]["baseWR"]), 1):
        result[name]["rank"] = rank
    return result


# ---- synergy ------------------------------------------------------------------

def fit_synergy(
    allies: list[dict],
    ally_baselines: dict[str, float],
) -> tuple[list[dict], int]:
    """Compute Bayesian-shrunk synergy deltas for all ally pairs.

    For each unordered pair {A, B}, gather both conditional WR rows:
      raw_delta = weighted_mean(WR(A|B), WR(B|A)) - mean(base_A, base_B)
    Positive = pair outperforms their individual ally-domain baselines.
    """
    # Collect both directions into symmetric pair buckets
    pair: dict[tuple[str, str], list[tuple[float, int]]] = defaultdict(list)
    for row in allies:
        a, b = row["brawler"], row["ally"]
        if a == b:
            continue
        if a not in ally_baselines or b not in ally_baselines:
            continue
        if row["picks"] < MIN_ALLY_PICKS:
            continue
        key = (min(a, b), max(a, b))
        pair[key].append((row["winRate"], row["picks"]))

    edges, n_dropped = [], 0
    for (a, b), entries in pair.items():
        total_picks = sum(p for _, p in entries)
        if total_picks < MIN_ALLY_PICKS:
            n_dropped += 1
            continue

        cond_avg = sum(wr * p for wr, p in entries) / total_picks
        baseline_avg = (ally_baselines[a] + ally_baselines[b]) / 2
        raw_delta = cond_avg - baseline_avg

        delta_shrunk = raw_delta * total_picks / (total_picks + PRIOR_N)

        if abs(delta_shrunk) < ALLY_ABS_THRESHOLD:
            n_dropped += 1
            continue

        edges.append({
            "a": a,
            "b": b,
            "delta": round(delta_shrunk, 6),
            "rawDelta": round(raw_delta, 6),
            "picks": total_picks,
            "confidence": _confidence_ally(total_picks),
        })

    edges.sort(key=lambda e: -abs(e["delta"]))
    return edges, n_dropped


def _confidence_ally(n: int) -> str:
    if n >= 5000:
        return "high"
    if n >= 500:
        return "medium"
    return "low"


# ---- counter ------------------------------------------------------------------

def fit_counters(
    enemies: list[dict],
    enemy_baselines: dict[str, float],
) -> tuple[list[dict], int]:
    """Compute Bayesian-shrunk counter deltas for all enemy pairs.

    For each unordered pair {A, B}, compute relative deviations from each
    brawler's population baseline, then average:
      from_A = WR(A vs B) - base_A
      from_B = -(WR(B vs A) - base_B)   # flipped to A's POV
      raw_delta = weighted_mean(from_A, from_B)
    Positive raw_delta = A outperforms its own mean more vs B than B's mean vs A
    (i.e. A has a matchup advantage over B).

    Each unordered pair is emitted once with a/b in the winning-side-first order
    and delta is always positive (the magnitude of the advantage).
    """
    lookup: dict[tuple[str, str], tuple[float, int]] = {}
    for row in enemies:
        lookup[(row["brawler"], row["enemy"])] = (row["winRate"], row["picks"])

    seen: set[tuple[str, str]] = set()
    edges, n_dropped = [], 0

    for (a, b), (wr_ab, picks_ab) in lookup.items():
        if (a, b) in seen or (b, a) in seen:
            continue
        seen.add((a, b))

        rev = lookup.get((b, a))
        if rev is None:
            # Single direction only — still use it if sample is large enough
            if picks_ab < MIN_ENEMY_PICKS:
                n_dropped += 1
                continue
            base_a = enemy_baselines.get(a, 0.59)
            raw_delta = wr_ab - base_a
            total_picks = picks_ab
        else:
            wr_ba, picks_ba = rev
            if picks_ab < MIN_ENEMY_PICKS and picks_ba < MIN_ENEMY_PICKS:
                n_dropped += 1
                continue
            base_a = enemy_baselines.get(a, 0.59)
            base_b = enemy_baselines.get(b, 0.59)
            from_a = wr_ab - base_a
            from_b = -(wr_ba - base_b)
            total_picks = picks_ab + picks_ba
            raw_delta = (from_a * picks_ab + from_b * picks_ba) / total_picks

        delta_shrunk = raw_delta * total_picks / (total_picks + PRIOR_N)

        # Canonical direction: winner (positive delta) stored as "a"
        canon_a, canon_b = a, b
        canon_delta = delta_shrunk
        if delta_shrunk < 0:
            canon_a, canon_b = b, a
            canon_delta = -delta_shrunk

        if canon_delta < ENEMY_ABS_THRESHOLD:
            n_dropped += 1
            continue

        edges.append({
            "a": canon_a,     # a has advantage over b
            "b": canon_b,
            "delta": round(canon_delta, 6),
            "rawDelta": round(abs(raw_delta), 6),
            "picks": int(total_picks),
            "confidence": _confidence_enemy(total_picks),
        })

    edges.sort(key=lambda e: -e["delta"])
    return edges, n_dropped


def _confidence_enemy(n: int) -> str:
    if n >= 10000:
        return "high"
    if n >= 1000:
        return "medium"
    return "low"


# ---- main --------------------------------------------------------------------

def main():
    stats, stats_file = load_latest_stats()
    print(f"Loaded {stats_file}")

    # Baselines
    ally_baselines = compute_ally_baselines(stats["allies"])
    enemy_baselines = compute_enemy_baselines(stats["enemies"])
    ranked_strength = compute_ranked_baselines(stats["ranked"], stats["ladderHigh"])

    # Merge ally/enemy baseline into brawlerStrength for output
    brawler_strength: dict[str, dict] = {}
    all_brawlers = (set(ally_baselines) | set(enemy_baselines) | set(ranked_strength))
    for name in sorted(all_brawlers):
        entry: dict = {}
        if name in ranked_strength:
            entry.update(ranked_strength[name])
        if name in ally_baselines:
            entry["allyBaseWR"] = round(ally_baselines[name], 6)
        if name in enemy_baselines:
            entry["enemyBaseWR"] = round(enemy_baselines[name], 6)
        brawler_strength[name] = entry

    # Re-rank by ranked baseWR
    ranked_items = [(k, v) for k, v in brawler_strength.items() if "baseWR" in v]
    ranked_items.sort(key=lambda kv: -kv[1]["baseWR"])
    for rank, (name, _) in enumerate(ranked_items, 1):
        brawler_strength[name]["rank"] = rank

    print(f"Brawler baselines: {len(brawler_strength)} brawlers")
    ally_vals = list(ally_baselines.values())
    enemy_vals = list(enemy_baselines.values())
    print(f"  Ally domain baseline: mean={sum(ally_vals)/len(ally_vals):.4f}  "
          f"range=[{min(ally_vals):.4f}, {max(ally_vals):.4f}]")
    print(f"  Enemy domain baseline: mean={sum(enemy_vals)/len(enemy_vals):.4f}  "
          f"range=[{min(enemy_vals):.4f}, {max(enemy_vals):.4f}]")

    # Fit edges
    synergy_edges, syn_dropped = fit_synergy(stats["allies"], ally_baselines)
    counter_edges, ctr_dropped = fit_counters(stats["enemies"], enemy_baselines)

    print(f"\nSynergy: {len(synergy_edges)} edges emitted, {syn_dropped} dropped")
    print(f"Counter: {len(counter_edges)} edges emitted, {ctr_dropped} dropped")

    # ---- sanity-check printout ------------------------------------------------
    print("\n=== Top-5 SYNERGIES (strongest positive pairs) ===")
    for e in [x for x in synergy_edges if x["delta"] > 0][:5]:
        print(f"  {e['a']} + {e['b']}: Δ={e['delta']:+.4f}  "
              f"raw={e['rawDelta']:+.4f}  n={e['picks']:,}  [{e['confidence']}]")

    print("\n=== Top-5 ANTI-SYNERGIES (worst pairings) ===")
    for e in sorted(synergy_edges, key=lambda x: x["delta"])[:5]:
        print(f"  {e['a']} + {e['b']}: Δ={e['delta']:+.4f}  "
              f"raw={e['rawDelta']:+.4f}  n={e['picks']:,}  [{e['confidence']}]")

    print("\n=== Top-5 COUNTERS (strongest matchup advantages) ===")
    for e in counter_edges[:5]:
        print(f"  {e['a']} beats {e['b']}: Δ={e['delta']:+.4f}  "
              f"n={e['picks']:,}  [{e['confidence']}]")

    print("\n=== Weakest emitted counters (just above threshold) ===")
    for e in counter_edges[-5:]:
        print(f"  {e['a']} over {e['b']}: Δ={e['delta']:+.4f}  "
              f"n={e['picks']:,}  [{e['confidence']}]")

    # ---- emit output -----------------------------------------------------------
    out = {
        "_meta": {
            "builtAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "statsSnapshot": stats_file,
            "seasonsIncluded": stats["_meta"]["seasonsIncluded"],
            "source": stats["_meta"]["source"],
            "method": (
                "Bayesian-shrunk signed win-rate deltas with in-population baselines. "
                "Synergy: baseline_A = marginal WR of A over all ally partners B "
                "(stays within ally-tracking trophy slice). "
                "delta_syn = weighted_mean(WR(A|B), WR(B|A)) - mean(base_A, base_B). "
                "Counter: baseline_A = marginal WR of A over all enemies "
                "(corrects for high-trophy population inflation where "
                "WR(A vs B) + WR(B vs A) ≈ 1.20, not 1.0). "
                "delta_ctr = weighted_mean(WR(A vs B) - base_A, "
                "-(WR(B vs A) - base_B)); positive = A advantage over B. "
                f"Shrinkage: delta *= n / (n + {PRIOR_N}). "
                f"Post-shrink thresholds: synergy |delta| >= {ALLY_ABS_THRESHOLD}, "
                f"counter delta >= {ENEMY_ABS_THRESHOLD}. "
                f"Pre-shrink pick gates: ally n >= {MIN_ALLY_PICKS}, "
                f"enemy n >= {MIN_ENEMY_PICKS}."
            ),
            "deltaSemantics": (
                "Raw win-rate delta. "
                "Synergy delta is NOT centered at 0 by construction; "
                "counter delta is approximately centered but retains ~0.02 mean "
                "due to residual population WR inflation. "
                "Convert to log-odds (kb/matrix.json deltaRating units): "
                "logit(0.5 + delta) - logit(0.5) ≈ 4 * delta for |delta| < 0.1."
            ),
            "thresholds": {
                "priorN": PRIOR_N,
                "allyAbsThreshold": ALLY_ABS_THRESHOLD,
                "enemyAbsThreshold": ENEMY_ABS_THRESHOLD,
                "minAllyPicks": MIN_ALLY_PICKS,
                "minEnemyPicks": MIN_ENEMY_PICKS,
            },
            "counts": {
                "brawlers": len(brawler_strength),
                "synergyEdges": len(synergy_edges),
                "counterEdges": len(counter_edges),
                "synergyDropped": syn_dropped,
                "counterDropped": ctr_dropped,
            },
        },
        # Per-brawler baseline strength; sorted by rank (1 = highest ranked WR)
        "brawlerStrength": brawler_strength,
        # Sorted by |delta| descending; positive = a+b better together
        "synergy": synergy_edges,
        # Sorted by delta descending; a always has advantage over b (delta > 0)
        "counter": counter_edges,
    }

    OUT.write_text(json.dumps(out, indent=1))
    print(f"\nWrote {OUT}  ({OUT.stat().st_size // 1024} KB, "
          f"{len(synergy_edges)} synergy + {len(counter_edges)} counter edges)")


if __name__ == "__main__":
    main()
