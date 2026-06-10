#!/usr/bin/env python3
"""Bake the community counter seed for the draft advisor.

Source: zathong.com/brawl-stars-counter/ (human-curated "Weak Against" /
"Strong Against" lists, scraped 2026-06-10). This is a SEED, not truth:
every edge is tagged confidence="community" so the scorer can down-weight
it and pros can override later. Contradictory pairs (listed both ways for
the same two brawlers) are dropped.

Edge semantics match docs/draft-advisor-kb-design.md: {a, b, type:"counter"}
means "b beats a"; delta is the log-odds-ish rating bonus credited to b
when a is on the enemy team.
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).parent

# Raw scrape, one line per brawler (kept verbatim for provenance/refresh).
RAW = """
Shelly | W: Bull, El Primo, Darryl, Mortis, Crow, Nita, Pam, Frank | S: Colt, Brock, Piper, Spike, Penny, Rico
Nita | W: Darryl, Tara, Mortis, Poco, El Primo | S: Dynamike, Rico, Spike, Leon, Shelly, Brock, Bull
Colt | W: Shelly, El Primo, Bull, Piper, Tara | S: Spike, Rico, Dynamike, Brock, Barley, Penny, Mortis
Bull | W: Nita, El Primo, Darryl, Mortis, Pam, Leon | S: Rico, Shelly, Piper, Spike, Poco, Colt, Crow
Jessie | W: Shelly, El Primo, Pam, Bull, Mortis, Poco | S: Darryl, Barley, Colt, Rico, Brock, Frank, Bo
Brock | W: Pam, Nita, Poco, Bull, Piper | S: Dynamike, Barley, Mortis, El Primo, Penny, Leon
Dynamike | W: Barley, Colt, Rico, Pam, Poco, Frank | S: Mortis, Crow, Leon, Piper, Brock
Bo | W: Mortis, Frank, Nita, Pam, Poco | S: Colt, Crow, Spike, Rico, Shelly
Tick | W: Mr. P | S: Mortis, Crow, Leon, Barley
8-Bit | W: Max | S: Leon, Penny
Emz | W: Ash | S: Mortis, El Primo, Colt
Stu | W: Edgar | S: Bull, Shelly, Mortis, Jacky, Nani, Max, Darryl, Lou
El Primo | W: Darryl, Mortis, Poco, Barley, Dynamike | S: Bull, Pam, Shelly, Crow, Colt, Bo
Barley | W: Colt, Rico, Pam, Poco, Frank, Nita | S: Mortis, Crow, Leon, Piper, Brock, Dynamike
Poco | W: Pam, Shelly, Leon, Tara | S: Crow, Jessie, Penny, Dynamike, Mortis
Rosa | W: Pam, Hank | S:
Rico | W: Shelly, Nita, Colt, Bull, Jessie, Bo, Spike, Crow | S: Dynamike, Barley, Frank, Leon
Darryl | W: Mortis, Penny, Colt, Brock, Piper, Spike, Crow | S: Leon, Bull, El Primo, Pam, Frank, Bo
Penny | W: Jessie, Pam, Poco, El Primo | S: Dynamike, Barley, Crow, Spike, Leon, Bull, Brock
Jacky | W: Stu | S: Carl
Piper | W: Frank, Pam, Jessie, Brock, Crow, Darryl | S: Mortis, Barley, Dynamike, Bull, Colt
Pam | W: Crow, El Primo, Nita, Darryl, Poco | S: Barley, Penny, Dynamike, Spike, Tara, Bull, Bo
Frank | W: Mortis, Nita, Pam, Poco, Darryl, El Primo | S: Bull, Piper, Dynamike, Barley, Rico, Brock
Bibi | W: Mortis | S: Jessie
Bea | W: Ash, Edgar | S: Sandy
Nani | W: Stu | S: Carl
Edgar | W: Lou, Buzz, Stu, Squeak | S: Shelly, Bull
Griff | W: Penny, Hank, Shelly | S: Buzz
Mortis | W: Brock, Spike, Penny, Darryl, Colt, Tara, Piper | S: Bull, El Primo, Shelly, Leon, Pam, Poco, Jessie, Nita
Tara | W: Pam, Poco, Crow, Darryl, Nita, Frank, El Primo | S: Leon, Colt, Barley, Dynamike, Bull, Spike
Gene | W: Amber, Sprout | S:
Max | W: Stu | S: Crow, Gale, 8-Bit, Pam, Nita
Mr. P | W: Colette, Sprout | S: Barley, Tick
Sprout | W: Amber | S: Mr. P, Gene
Byron | W: Tick, Mandy | S: Colette
Squeak | W: Hank, Carl, Bea | S: Edgar, Mortis
Spike | W: Colt, El Primo, Pam, Poco, Jessie, Penny, Tara | S: Rico, Dynamike, Barley, Crow, Leon, Bull
Leon | W: Pam, El Primo, Brock, Dynamike, Barley, Colt, Rico | S: Bull, Shelly, Darryl, Piper, Bo, Tara
Amber | W: Surge, 8-Bit | S: Sprout, Gene, Spike
Sandy | W: Gale | S: Tara
Doug | W: Nani, Brock | S: Chester, Lola
Cordelius | W: Frank, Bull | S: Piper
Crow | W: El Primo, Tara, Darryl, Dynamike, Barley, Nita | S: Shelly, Bull, Piper, Colt, Spike, Leon, Rico, Frank
Gale | W: Max | S: Bull, Frank, Sandy, Nita
Surge | W: Amber | S: Poco, Jessie
Colette | W: Byron | S: Mr. P, Frank, Leon, Nita, Jessie
Lou | W: Belle, Stu | S: Edgar
Ruffs | W: Maisie | S: Darryl, Mortis
Belle | W: Crow, Hank | S: Lou, Frank
Buzz | W: Griff | S: Edgar
Ash | W: Nita, Crow, Emz | S: Bea
Grom | W: Maisie, Willow | S:
Buster | W: Tara, Mortis, Hank | S:
Lola | W: Hank | S:
Fang | W: Gray, Buzz, Shelly | S:
Eve | W: Hank, Mandy, Piper | S:
Janet | W: Brock, Hank, Tara | S:
Meg | W: Bea, Hank, Spike | S:
Otis | W: Hank, Mortis, 8-Bit | S:
Sam | W: Bibi, Hank | S:
Bonnie | W: Crow, Mr. P, Hank | S:
Gus | W: Mr. P, Shelly, Bonnie | S:
Chester | W: Hank | S:
Mandy | W: Crow, Bonnie, Nani | S:
Gray | W: Piper, Mandy, Surge | S:
Angelo | W: Edgar, Leon, Crow, Mortis | S: Hank, Buster, Meg
Kit | W: Mico, Melodie, Poco | S: Grom, Sprout
Pearl | W: Ash, Jacky, Bibi | S: Nani, Bea, Piper
Charlie | W: Penny | S: Mortis, Piper, Bea, Bull, Chuck
Larry & Lawrie | W: Nita, Shelly | S: R-T, Chester
Chuck | W: Sandy, Bo, Emz | S: Edgar, Nani, Brock
Melodie | W: Darryl, Bull, Rosa | S: Nani, Brock, Frank
"""

ALIAS = {"Morti": "Mortis", "Colonel Ruffs": "Ruffs"}

def main():
    known = {b["name"] for b in json.load(open(HERE / "brawlers.json"))["brawlers"]}
    edges = {}      # (a, b) -> edge ; "b beats a"
    dropped = []

    def norm(n):
        n = ALIAS.get(n.strip(), n.strip())
        return n if n in known else None

    for line in RAW.strip().splitlines():
        m = re.match(r"(.+?) \| W: ?(.*?) \| S: ?(.*)$", line.strip())
        if not m:
            continue
        b = norm(m.group(1))
        if not b:
            dropped.append(("brawler", m.group(1)))
            continue
        weak = [norm(x) for x in m.group(2).split(",") if x.strip()]
        strong = [norm(x) for x in m.group(3).split(",") if x.strip()]
        for x in weak:           # x beats b
            if x and x != b:
                edges[(b, x)] = True
        for x in strong:         # b beats x
            if x and x != b:
                edges[(x, b)] = True

    # Drop contradictions (both "x beats y" and "y beats x" claimed).
    contradictions = {tuple(sorted(k)) for k in edges if (k[1], k[0]) in edges}
    out = [
        {"a": a, "b": b, "type": "counter", "delta": 0.25,
         "reason": f"{b} listed as a counter to {a} (community)",
         "modeContext": None, "confidence": "community",
         "source": "zathong.com/brawl-stars-counter/", "scraped": "2026-06-10"}
        for (a, b) in sorted(edges)
        if tuple(sorted((a, b))) not in contradictions
    ]
    json.dump({"edges": out}, open(HERE / "draft_seed.json", "w"), indent=1)
    print(f"{len(out)} edges  ({len(contradictions)} contradictory pairs dropped, "
          f"{len(dropped)} unknown names skipped)")

if __name__ == "__main__":
    main()
