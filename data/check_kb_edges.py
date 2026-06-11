#!/usr/bin/env python3
"""Cross-check llm-draft counter edges against brawltime pair win rates.

For an edge "b beats a", look up the enemies table (winner's win rate when
facing that enemy) in the latest draft_stats snapshot. The population mean is
well above 0.5 (tracked players are strong), so contradictions are judged
against the table's own mean, not 0.5. Edges contradicted at large sample
get flagged for removal/pro review; supported edges get noted.
"""

import json
import statistics
from pathlib import Path

HERE = Path(__file__).parent
MIN_PICKS = 3000
TOL = 0.015  # win-rate delta below mean that counts as contradiction


def main():
    snap = sorted((HERE / "draft_stats").glob("*.json"))[-1]
    stats = json.load(open(snap))
    pairs = {(r["brawler"].lower(), r["enemy"].lower()): (r["winRate"], r["picks"])
             for r in stats["enemies"]}
    mean_wr = statistics.mean(r["winRate"] for r in stats["enemies"]
                              if r["picks"] >= MIN_PICKS)

    matrix = json.load(open(HERE / "kb" / "matrix.json"))
    print(f"pair-table mean WR (n>={MIN_PICKS}): {mean_wr:.3f}  [{snap.name}]")
    for e in matrix["edges"]:
        key = (e["b"].lower(), e["a"].lower())
        if key not in pairs:
            print(f"  ? {e['b']} > {e['a']}: no pair data")
            continue
        wr, n = pairs[key]
        if n < MIN_PICKS:
            verdict = f"thin (n={n})"
        elif wr >= mean_wr + 0.01:
            verdict = "SUPPORTED"
        elif wr <= mean_wr - TOL:
            verdict = "CONTRADICTED — flag for review"
        else:
            verdict = "neutral"
        print(f"  {e['b']} > {e['a']}: pair WR {wr:.3f} (n={n:,}) → {verdict}")


if __name__ == "__main__":
    main()
