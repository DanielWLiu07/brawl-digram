"""Tests for build_advisor_context.py — the Phase-2 key-select retrieval
assembler. Run from repo root: python3 -m unittest discover -s data/tests -t .
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from build_advisor_context import ContextBuilder, TOP_CANDIDATES


def make_builder():
    if not hasattr(make_builder, "b"):
        make_builder.b = ContextBuilder()   # loads all artifacts once
    return make_builder.b


class TestMapResolution(unittest.TestCase):
    def test_display_name_resolves_to_internal_grid(self):
        internal, display, fam = make_builder().resolve_map("Hard Rock Mine")
        self.assertEqual(internal, "Gemgrab_1")
        self.assertEqual(fam, "Gemgrab")

    def test_internal_name_passes_through(self):
        internal, _, fam = make_builder().resolve_map("Knockout_1")
        self.assertEqual(internal, "Knockout_1")
        self.assertEqual(fam, "Knockout")

    def test_ball_family_covers_all_three_internal_modes(self):
        b = make_builder()
        for query in ("AirHockey_1", "Laserball_1", "BrawlBallV2_1"):
            self.assertEqual(b.resolve_map(query)[2], "Ball", query)

    def test_unknown_map_raises(self):
        with self.assertRaises(KeyError):
            make_builder().resolve_map("Not A Real Map")


class TestContextBuild(unittest.TestCase):
    def build(self, **kw):
        args = dict(map_query="Hard Rock Mine", blue=["Gene", "Pam"],
                    red=["Piper"], bans_blue=[], bans_red=[])
        args.update(kw)
        return make_builder().build(**args)

    def test_unknown_brawler_raises(self):
        with self.assertRaises(KeyError):
            self.build(blue=["Gene", "Notabrawler"])

    def test_candidates_exclude_taken_and_respect_cap(self):
        ctx = self.build()
        cands = ctx["meta"]["candidates"]
        self.assertLessEqual(len(cands), TOP_CANDIDATES)
        self.assertTrue(cands, "shortlist empty on the richest pro map")
        for name in ("Gene", "Pam", "Piper"):
            self.assertNotIn(name, cands)

    def test_numeric_core_survives_tight_budget(self):
        ctx = self.build(budget=800)
        self.assertLessEqual(ctx["tokenEstimate"], 800 * 1.1)
        for title in ("Draft state", "Map geometry [computed]"):
            self.assertIn(title, ctx["sections"], title)
        for dropped in ctx["droppedSections"]:
            self.assertTrue(dropped.startswith(("Knowledge-base", "Community wiki")),
                            f"dropped a numeric section: {dropped}")

    def test_grounding_rules_present(self):
        ctx = self.build()
        self.assertIn("Cite ONLY numbers", ctx["markdown"])

    def test_no_duplicate_matchup_edges(self):
        ctx = self.build()
        lines = ctx["sections"].get(
            "Matchup edges (directional; Δ in rating units)", [])
        pairs = [l.split(" (")[0] for l in lines]   # "B beats A"
        self.assertEqual(len(pairs), len(set(pairs)), pairs)

    def test_kb_edge_outranks_seed_for_same_pair(self):
        # Piper>Hank exists in kb/matrix.json; if it fires, the rendered line
        # must carry a KB confidence tag, not the community seed's.
        ctx = self.build()
        lines = ctx["sections"].get(
            "Matchup edges (directional; Δ in rating units)", [])
        for l in lines:
            if l.startswith("- Piper beats Hank"):
                self.assertIn("[llm-draft]", l)
                return
        # edge only fires when Hank is in the pool; pool shifts with stats are OK

    def test_ban_phase_builds_on_empty_draft(self):
        ctx = self.build(blue=[], red=[], phase="ban", team="red",
                         map_query="Ends Meet")
        self.assertEqual(ctx["meta"]["map"]["internal"], "Knockout_1")
        self.assertIn("BAN", ctx["markdown"])

    def test_token_estimate_matches_markdown(self):
        ctx = self.build()
        self.assertEqual(ctx["tokenEstimate"], round(len(ctx["markdown"]) / 4))


if __name__ == "__main__":
    unittest.main()
