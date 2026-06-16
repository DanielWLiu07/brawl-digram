"""Data-integrity tests for brawl-digram draft-advisor artifacts.

Run from the repo root:
    python3 -m unittest discover -s data/tests -t .

All paths are resolved relative to the repo root (the parent of data/).
No network access; no modification of any data files.
"""

import json
import math
import os
import unittest
from collections import Counter
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent.parent  # …/brawl-digram
DATA = REPO_ROOT / "data"

DRAFT_SEED = DATA / "draft_seed.json"
DRAFT_AI = DATA / "draft_ai.json"
MAP_DESCRIPTORS = DATA / "map_descriptors.json"
PRO_DRAFTS = DATA / "pro_drafts.json"
MAP_NAME_MAP = DATA / "map_name_map.json"
BRAWLERS_JSON = DATA / "brawlers.json"
KB_DIR = DATA / "kb"
KB_META = KB_DIR / "meta.json"
KB_MATRIX = KB_DIR / "matrix.json"
KB_BRAWLERS_DIR = KB_DIR / "brawlers"

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def load_json(path: Path):
    with open(path) as f:
        return json.load(f)


def _brawler_display_names():
    """Return the set of display names from brawlers.json."""
    data = load_json(BRAWLERS_JSON)
    return {b["name"] for b in data["brawlers"]}


# ---------------------------------------------------------------------------
# ATTR_NAMES / GEO_NAMES from fit_draft_weights.py (hardcoded mirror)
# IMPORTANT: these lists must stay in sync with data/fit_draft_weights.py's
# ATTR_NAMES and GEO_NAMES constants.  If the model is retrained with
# different feature sets, update here too.
# ---------------------------------------------------------------------------

EXPECTED_ATTR_NAMES = [
    "thrower", "sniper", "shortRange", "tank", "fast",
    "rangeN", "hpN", "speedN", "melee",
]

EXPECTED_GEO_NAMES = [
    "wallPct", "bushPct", "openPct", "sightlineFrac",
    "midOpenness", "chokesPerRowN", "avgLaneWidthN",
]

EXPECTED_MODES = ["Gemgrab", "Wanted", "Bankheist", "Ball", "KingOfHill", "Knockout"]

# Confidence values the KB design allows.
KB_CONFIDENCE_VALUES = {"pro", "stats", "community", "llm-draft"}


# ===========================================================================
# 1. draft_seed.json
# ===========================================================================

class TestDraftSeed(unittest.TestCase):
    """Tests for data/draft_seed.json."""

    @classmethod
    def setUpClass(cls):
        raw = load_json(DRAFT_SEED)
        cls.edges = raw["edges"]
        cls.valid_names = _brawler_display_names()

    def test_seed_edges_have_required_fields(self):
        """Every edge must carry {a, b, type, delta, reason, confidence, source}."""
        required = {"a", "b", "type", "delta", "reason", "confidence", "source"}
        bad = [
            (i, required - set(e.keys()))
            for i, e in enumerate(self.edges)
            if required - set(e.keys())
        ]
        self.assertFalse(
            bad,
            f"{len(bad)} edges missing required fields. First: {bad[:3]}",
        )

    def test_seed_edges_no_self_loops(self):
        """Every edge must have a != b."""
        self_loops = [(i, e["a"]) for i, e in enumerate(self.edges) if e["a"] == e["b"]]
        self.assertFalse(self_loops, f"Self-loop edges found: {self_loops}")

    def test_seed_edges_no_duplicate_directed_pairs(self):
        """No two edges may share the same (a, b) directed pair."""
        pairs = [(e["a"], e["b"]) for e in self.edges]
        counts = Counter(pairs)
        dupes = {p: c for p, c in counts.items() if c > 1}
        self.assertFalse(dupes, f"Duplicate directed pairs: {dupes}")

    def test_seed_edges_have_no_contradictions(self):
        """The bake script claims to drop contradictory pairs where both (a,b) and (b,a)
        exist. Verify that invariant holds."""
        pair_set = {(e["a"], e["b"]) for e in self.edges}
        contradictory = [(a, b) for (a, b) in pair_set if (b, a) in pair_set]
        self.assertFalse(
            contradictory,
            f"{len(contradictory)} contradictory directed pairs found "
            f"(both (a,b) and (b,a) present). First: {contradictory[:5]}",
        )

    def test_seed_edges_a_names_in_brawlers(self):
        """All 'a' brawler names must be valid display names from brawlers.json.

        Note: pro_drafts.json uses 'Jae-yong', 'Mr.P', 'Glowbert' which are
        NOT valid brawler display names (known Liquipedia parse artifacts).
        Those aliases are intentionally NOT accepted here — the seed bake
        script is expected to already resolve or drop them.
        """
        unknown = {e["a"] for e in self.edges if e["a"] not in self.valid_names}
        self.assertFalse(unknown, f"Unknown 'a' names in draft_seed: {unknown}")

    def test_seed_edges_b_names_in_brawlers(self):
        """All 'b' brawler names must be valid display names from brawlers.json."""
        unknown = {e["b"] for e in self.edges if e["b"] not in self.valid_names}
        self.assertFalse(unknown, f"Unknown 'b' names in draft_seed: {unknown}")

    def test_seed_edges_delta_is_positive_finite(self):
        """delta must be a finite positive number on every edge."""
        bad = [
            (i, e["delta"])
            for i, e in enumerate(self.edges)
            if not isinstance(e.get("delta"), (int, float))
            or not math.isfinite(e["delta"])
            or e["delta"] <= 0
        ]
        self.assertFalse(bad, f"Edges with invalid delta: {bad[:5]}")


# ===========================================================================
# 2. draft_ai.json
# ===========================================================================

class TestDraftAI(unittest.TestCase):
    """Tests for data/draft_ai.json."""

    @classmethod
    def setUpClass(cls):
        cls.ai = load_json(DRAFT_AI)
        cls.valid_names = _brawler_display_names()

    def test_ai_meta_has_required_fields(self):
        """_meta must contain builtAt, proGames, trainRows, lambda, cvR2."""
        required = {"builtAt", "proGames", "trainRows", "lambda", "cvR2"}
        meta = self.ai.get("_meta", {})
        missing = required - set(meta.keys())
        self.assertFalse(missing, f"_meta missing fields: {missing}")

    def test_ai_attr_names_match_expected(self):
        """attrNames must equal the 9 expected attribute names (mirrors
        ATTR_NAMES in data/fit_draft_weights.py)."""
        self.assertEqual(self.ai["attrNames"], EXPECTED_ATTR_NAMES)

    def test_ai_geo_names_match_expected(self):
        """geoNames must equal the 7 expected geometry names (mirrors
        GEO_NAMES in data/fit_draft_weights.py)."""
        self.assertEqual(self.ai["geoNames"], EXPECTED_GEO_NAMES)

    def test_ai_weights_keys_consistent_with_feature_schema(self):
        """Weights dict must contain exactly one key per (attr, main/geo/mode)
        combination: attr, attr*geo, attr@mode for every combination.
        Total expected: 9 * (1 + 7 + 6) = 126."""
        attr_names = self.ai["attrNames"]
        geo_names = self.ai["geoNames"]
        modes = self.ai["modes"]
        expected_keys = set()
        for a in attr_names:
            expected_keys.add(a)
            for g in geo_names:
                expected_keys.add(f"{a}*{g}")
            for m in modes:
                expected_keys.add(f"{a}@{m}")
        actual_keys = set(self.ai["weights"].keys())
        self.assertEqual(actual_keys, expected_keys)

    def test_ai_weights_all_finite(self):
        """Every weight value must be a finite float."""
        bad = [
            (k, v)
            for k, v in self.ai["weights"].items()
            if not isinstance(v, (int, float)) or not math.isfinite(v)
        ]
        self.assertFalse(bad, f"Non-finite weight values: {bad[:5]}")

    def test_ai_intercept_is_finite(self):
        """intercept must be present and finite."""
        intercept = self.ai.get("intercept")
        self.assertIsNotNone(intercept, "'intercept' key missing from draft_ai.json")
        self.assertTrue(
            isinstance(intercept, (int, float)) and math.isfinite(intercept),
            f"intercept is not finite: {intercept}",
        )

    def test_ai_attrs_covers_all_brawlers(self):
        """attrs table must have exactly one entry per brawler in brawlers.json."""
        attrs_names = set(self.ai["attrs"].keys())
        self.assertEqual(
            attrs_names,
            self.valid_names,
            f"Mismatch: extra={attrs_names - self.valid_names}, "
            f"missing={self.valid_names - attrs_names}",
        )

    def test_ai_attrs_have_all_9_keys(self):
        """Every brawler's attr dict must contain exactly the 9 expected attr keys."""
        expected = set(EXPECTED_ATTR_NAMES)
        bad = [
            (name, set(vals.keys()) ^ expected)
            for name, vals in self.ai["attrs"].items()
            if set(vals.keys()) != expected
        ]
        self.assertFalse(bad, f"Attr dicts with wrong keys: {bad[:3]}")

    def test_ai_attrs_values_in_0_1(self):
        """All attr values must be in [0, 1]."""
        bad = [
            (name, field, val)
            for name, vals in self.ai["attrs"].items()
            for field, val in vals.items()
            if not (0.0 <= val <= 1.0)
        ]
        self.assertFalse(bad, f"Attr values out of [0, 1]: {bad[:5]}")

    def test_ai_modes_list_matches_expected(self):
        """modes list must equal the 6 expected mode families."""
        self.assertEqual(sorted(self.ai["modes"]), sorted(EXPECTED_MODES))

    def test_ai_stats_mode_families_are_known(self):
        """Every key in stats must be 'modeFamily|mapId'; the mode family prefix
        must be one of the known modes."""
        known = set(EXPECTED_MODES)
        bad = [
            k
            for k in self.ai["stats"].keys()
            if k.split("|")[0] not in known
        ]
        self.assertFalse(bad, f"Stats keys with unknown mode family: {bad[:5]}")

    def test_ai_mode_stats_keys_are_known_modes(self):
        """Every key in modeStats must be one of the known mode families."""
        known = set(EXPECTED_MODES)
        bad = [k for k in self.ai["modeStats"].keys() if k not in known]
        self.assertFalse(bad, f"Unknown mode keys in modeStats: {bad}")


# ===========================================================================
# 3. map_descriptors.json
# ===========================================================================

class TestMapDescriptors(unittest.TestCase):
    """Tests for data/map_descriptors.json.

    Field notes:
    - chokesPerRow (unnormalized, range [0, 3.09]) — NOT chokesPerRowN.
      fit_draft_weights.py normalises it at runtime: min(x, 3) / 3.
    - avgLaneWidth (tiles, range [3.34, 21.0]) — NOT avgLaneWidthN.
      fit_draft_weights.py normalises it at runtime: min(x, 10) / 10.
    The *N suffix fields in draft_ai.json geoNames refer to the on-the-fly
    normalised versions; the raw file stores the unnormalized originals.
    """

    UNIT_FIELDS = ["wallPct", "bushPct", "openPct", "sightlineFrac", "midOpenness"]
    # chokesPerRow: max observed 3.09, physiologically bounded at ~3
    CHOKES_MAX = 4.0
    # avgLaneWidth: max observed 21.0 tiles (open 5v5 maps)
    AVG_LANE_MAX = 25.0

    @classmethod
    def setUpClass(cls):
        cls.md = load_json(MAP_DESCRIPTORS)

    def test_map_descriptors_is_nonempty_dict(self):
        self.assertIsInstance(self.md, dict)
        self.assertGreater(len(self.md), 0)

    def test_map_descriptors_unit_fields_present_on_all_entries(self):
        """wallPct, bushPct, openPct, sightlineFrac, midOpenness must exist on
        every map entry."""
        for field in self.UNIT_FIELDS:
            missing = [k for k, v in self.md.items() if field not in v]
            self.assertFalse(
                missing,
                f"Field '{field}' missing from {len(missing)} map entries: {missing[:5]}",
            )

    def test_map_descriptors_chokes_per_row_present(self):
        """chokesPerRow must be present on every entry (raw, unnormalised)."""
        missing = [k for k, v in self.md.items() if "chokesPerRow" not in v]
        self.assertFalse(missing, f"chokesPerRow missing from: {missing[:5]}")

    def test_map_descriptors_avg_lane_width_present(self):
        """avgLaneWidth must be present on every entry (raw, in tiles)."""
        missing = [k for k, v in self.md.items() if "avgLaneWidth" not in v]
        self.assertFalse(missing, f"avgLaneWidth missing from: {missing[:5]}")

    def test_map_descriptors_unit_fields_are_finite(self):
        """All unit-fraction fields must be finite numbers."""
        for field in self.UNIT_FIELDS:
            bad = [
                (k, v[field])
                for k, v in self.md.items()
                if field in v and not math.isfinite(v[field])
            ]
            self.assertFalse(bad, f"Non-finite {field} values: {bad[:3]}")

    def test_map_descriptors_unit_fields_in_0_1(self):
        """wallPct, bushPct, openPct, sightlineFrac, midOpenness must all be
        in [0, 1]. openPct can reach 1.0 on fully-open maps."""
        for field in self.UNIT_FIELDS:
            bad = [
                (k, v[field])
                for k, v in self.md.items()
                if field in v and not (0.0 <= v[field] <= 1.0)
            ]
            self.assertFalse(
                bad, f"'{field}' out of [0, 1]: {bad[:3]}"
            )

    def test_map_descriptors_chokes_per_row_nonneg_and_bounded(self):
        """chokesPerRow must be non-negative and <= 4.0 (observed max is 3.09)."""
        bad = [
            (k, v["chokesPerRow"])
            for k, v in self.md.items()
            if "chokesPerRow" in v
            and not (0.0 <= v["chokesPerRow"] <= self.CHOKES_MAX)
        ]
        self.assertFalse(bad, f"chokesPerRow out of [0, {self.CHOKES_MAX}]: {bad[:3]}")

    def test_map_descriptors_avg_lane_width_positive_and_bounded(self):
        """avgLaneWidth must be positive and <= 25.0 tiles."""
        bad = [
            (k, v["avgLaneWidth"])
            for k, v in self.md.items()
            if "avgLaneWidth" in v
            and not (0.0 < v["avgLaneWidth"] <= self.AVG_LANE_MAX)
        ]
        self.assertFalse(
            bad, f"avgLaneWidth out of (0, {self.AVG_LANE_MAX}]: {bad[:3]}"
        )


# ===========================================================================
# 4. pro_drafts.json
# ===========================================================================

class TestProDrafts(unittest.TestCase):
    """Tests for data/pro_drafts.json.

    Cross-team ban duplication (both teams ban the same brawler) is VALID in
    the Brawl Stars draft format (teams ban independently), so it is NOT tested
    as an error here.

    Known data issues (Liquipedia parser artifacts, not tested as errors):
    - 'Jae-yong' (lowercase y) appears instead of 'Jae-Yong'.
    - 'Mr.P' (no space) appears instead of 'Mr. P'.
    - 'Glowbert' appears instead of 'Glowy'.
    - 6 games have a brawler appearing in both picks and bans (scraper bug).
    - 1 game has a duplicate in picks (game 423, 'Gus' twice).
    - 18 games have null values in bans (missing ban data from Liquipedia).
    These are reported in the data issues section; the test suite tests the
    structurally-correctable properties only.
    """

    @classmethod
    def setUpClass(cls):
        raw = load_json(PRO_DRAFTS)
        cls.meta = raw["_meta"]
        cls.games = raw["games"]

    def test_pro_drafts_game_count_matches_meta(self):
        """len(games) must equal _meta.games."""
        self.assertEqual(
            len(self.games),
            self.meta["games"],
            f"Expected {self.meta['games']} games, got {len(self.games)}",
        )

    def test_pro_drafts_map_names_nonempty(self):
        """Every game must have a non-empty map name."""
        bad = [
            (i, g.get("map"))
            for i, g in enumerate(self.games)
            if not g.get("map")
        ]
        self.assertFalse(bad, f"Games with empty map: {bad[:5]}")

    def test_pro_drafts_picks_each_team_has_3(self):
        """Both teams must have exactly 3 picks per game."""
        bad = [
            (i, t, len(team_picks))
            for i, g in enumerate(self.games)
            for t, team_picks in enumerate(g.get("picks", []))
            if len(team_picks) != 3
        ]
        self.assertFalse(bad, f"Teams without exactly 3 picks: {bad[:5]}")

    def test_pro_drafts_bans_each_team_no_more_than_3(self):
        """Each team's bans list must not exceed 3 entries."""
        bad = [
            (i, t, len(team_bans))
            for i, g in enumerate(self.games)
            if g.get("bans")
            for t, team_bans in enumerate(g["bans"])
            if len(team_bans) > 3
        ]
        self.assertFalse(bad, f"Teams with more than 3 bans: {bad[:5]}")

    def test_pro_drafts_no_duplicate_within_picks(self):
        """No brawler should appear twice within one game's combined picks.

        Previously failed on Game 423 ('Gus' picked twice, a Liquipedia scraper
        bug); resolved by the latest pro_drafts refresh.
        """
        bad = []
        for i, g in enumerate(self.games):
            all_picks = [p for team in g.get("picks", []) for p in team if p]
            counts = Counter(all_picks)
            dupes = {k: v for k, v in counts.items() if v > 1}
            if dupes:
                bad.append((i, dupes))
        self.assertFalse(bad, f"Games with duplicate brawler in picks: {bad[:5]}")

    def test_pro_drafts_no_brawler_in_both_picks_and_bans(self):
        """A brawler that was banned should not also appear in picks.

        Previously failed on 6 games (306, 582, 847, 1019, 1491, 1679) from
        Liquipedia scraper parsing errors; resolved by the latest pro_drafts
        refresh.
        """
        bad = []
        for i, g in enumerate(self.games):
            picks_set = {p for team in g.get("picks", []) for p in team if p}
            bans_set = {b for team in g.get("bans", []) for b in team if b} \
                if g.get("bans") else set()
            overlap = picks_set & bans_set
            if overlap:
                bad.append((i, overlap))
        self.assertFalse(
            bad,
            f"{len(bad)} games where a brawler appears in both picks and bans: "
            f"{bad[:5]}",
        )

    def test_pro_drafts_picks_have_two_teams(self):
        """Every game must have exactly 2 teams' picks."""
        bad = [
            (i, len(g.get("picks", [])))
            for i, g in enumerate(self.games)
            if len(g.get("picks", [])) != 2
        ]
        self.assertFalse(bad, f"Games without exactly 2 teams' picks: {bad[:5]}")


# ===========================================================================
# 5. map_name_map.json
# ===========================================================================

class TestMapNameMap(unittest.TestCase):
    """Tests for data/map_name_map.json.

    Structure: the file is a dict with top-level keys
    {fetchedAt, method, modeMap, maps}. The 'maps' value is the actual
    slug->descriptor-key mapping (e.g. 'Double-Swoosh' -> 'Gemgrab_16').
    """

    @classmethod
    def setUpClass(cls):
        raw = load_json(MAP_NAME_MAP)
        cls.maps_dict = raw["maps"]  # slug -> descriptor key
        cls.descriptor_keys = set(load_json(MAP_DESCRIPTORS).keys())

    def test_map_name_map_has_maps_key(self):
        """map_name_map.json must have a top-level 'maps' key."""
        raw = load_json(MAP_NAME_MAP)
        self.assertIn("maps", raw)

    def test_map_name_map_targets_exist_in_map_descriptors(self):
        """Every value in maps_dict must exist as a key in map_descriptors.json."""
        bad = [
            (slug, target)
            for slug, target in self.maps_dict.items()
            if target not in self.descriptor_keys
        ]
        self.assertFalse(
            bad,
            f"{len(bad)} map_name_map targets not in map_descriptors: {bad[:5]}",
        )

    def test_map_name_map_slugs_nonempty(self):
        """All slug keys in maps must be non-empty strings."""
        bad = [k for k in self.maps_dict.keys() if not k]
        self.assertFalse(bad, f"Empty slug keys found: {bad[:5]}")

    def test_map_name_map_values_nonempty(self):
        """All target values in maps must be non-empty strings."""
        bad = [v for v in self.maps_dict.values() if not v]
        self.assertFalse(bad, f"Empty target values found: {bad[:5]}")


# ===========================================================================
# 6. data/kb/
# ===========================================================================

class TestKB(unittest.TestCase):
    """Tests for data/kb/meta.json, kb/matrix.json, and kb/brawlers/*.json."""

    @classmethod
    def setUpClass(cls):
        cls.meta = load_json(KB_META)
        cls.matrix = load_json(KB_MATRIX)
        cls.matrix_edges = cls.matrix["edges"]
        cls.brawler_files = list(KB_BRAWLERS_DIR.glob("*.json"))
        cls.valid_names = _brawler_display_names()

    def test_kb_meta_has_patch_version(self):
        """meta.json must have a non-empty patchVersion."""
        pv = self.meta.get("patchVersion", "")
        self.assertTrue(pv, "meta.json is missing a non-empty patchVersion")

    def test_kb_matrix_edges_have_required_fields(self):
        """Every matrix edge must carry {a, b, type, deltaRating, reason,
        confidence, source}."""
        required = {"a", "b", "type", "deltaRating", "reason", "confidence", "source"}
        bad = [
            (i, required - set(e.keys()))
            for i, e in enumerate(self.matrix_edges)
            if required - set(e.keys())
        ]
        self.assertFalse(bad, f"Edges missing required fields: {bad}")

    def test_kb_matrix_edges_confidence_is_valid(self):
        """confidence must be one of {pro, stats, community, llm-draft}."""
        bad = [
            (i, e.get("confidence"))
            for i, e in enumerate(self.matrix_edges)
            if e.get("confidence") not in KB_CONFIDENCE_VALUES
        ]
        self.assertFalse(bad, f"Invalid confidence values: {bad}")

    def test_kb_matrix_edges_a_ne_b(self):
        """Every edge must have a != b."""
        bad = [(i, e["a"]) for i, e in enumerate(self.matrix_edges) if e["a"] == e["b"]]
        self.assertFalse(bad, f"Self-loop edges in matrix: {bad}")

    def test_kb_brawlers_name_matches_filename(self):
        """Each kb/brawlers/<Name>.json must have 'name' == the filename stem."""
        bad = []
        for fpath in self.brawler_files:
            data = load_json(fpath)
            expected = fpath.stem
            if data.get("name") != expected:
                bad.append((fpath.name, data.get("name")))
        self.assertFalse(bad, f"name/filename mismatches: {bad}")

    def test_kb_brawlers_notes_have_required_fields(self):
        """Every note in every kb/brawlers file must have text, confidence,
        and source."""
        required = {"text", "confidence", "source"}
        bad = []
        for fpath in self.brawler_files:
            data = load_json(fpath)
            for j, note in enumerate(data.get("notes", [])):
                missing = required - set(note.keys())
                if missing:
                    bad.append((fpath.name, j, missing))
        self.assertFalse(bad, f"Notes missing required fields: {bad}")

    def test_kb_brawlers_have_patch_version(self):
        """Every kb/brawlers file must have a non-empty patchVersion."""
        bad = []
        for fpath in self.brawler_files:
            data = load_json(fpath)
            if not data.get("patchVersion"):
                bad.append(fpath.name)
        self.assertFalse(bad, f"Brawler files missing patchVersion: {bad}")

    def test_kb_brawlers_names_are_valid_brawler_names(self):
        """The 'name' in each kb/brawlers file must be a known display name from
        brawlers.json."""
        bad = []
        for fpath in self.brawler_files:
            data = load_json(fpath)
            name = data.get("name", "")
            if name not in self.valid_names:
                bad.append((fpath.name, name))
        self.assertFalse(bad, f"KB brawler names not in brawlers.json: {bad}")


# ===========================================================================
# 7. brawlers.json
# ===========================================================================

class TestBrawlersJson(unittest.TestCase):
    """Tests for data/brawlers.json."""

    # rangeTiles == 40.0 on 3 known brawlers (Mandy super, Mandy hyper super,
    # Bibi super) — the CSV uses 40 tiles as the maximum ranged distance.
    # We test (0, 40] to allow the 40 boundary.
    RANGE_LO = 0.0
    RANGE_HI = 40.0

    HP_LO = 1000
    HP_HI = 20000

    SPEED_LO = 0.5
    SPEED_HI = 5.0

    @classmethod
    def setUpClass(cls):
        raw = load_json(BRAWLERS_JSON)
        cls.brawlers = raw["brawlers"]

    def test_brawlers_list_nonempty(self):
        self.assertGreater(len(self.brawlers), 0)

    def test_brawlers_all_have_nonempty_name(self):
        bad = [b.get("name", "") for b in self.brawlers if not b.get("name")]
        self.assertFalse(bad, f"Brawlers with missing/empty name: {len(bad)}")

    def test_brawlers_all_have_nonempty_variants(self):
        """Every brawler must have at least one variant."""
        bad = [b["name"] for b in self.brawlers if not b.get("variants")]
        self.assertFalse(bad, f"Brawlers with no variants: {bad}")

    def test_brawlers_hp_in_range_when_present(self):
        """hp (when present and non-null) must be in [1000, 20000]."""
        bad = [
            (b["name"], b["hp"])
            for b in self.brawlers
            if b.get("hp") is not None
            and not (self.HP_LO <= b["hp"] <= self.HP_HI)
        ]
        self.assertFalse(bad, f"hp outside [{self.HP_LO}, {self.HP_HI}]: {bad}")

    def test_brawlers_speed_in_range_when_present(self):
        """speedTilesPerSec (when present and non-null) must be in (0.5, 5.0)."""
        bad = [
            (b["name"], b["speedTilesPerSec"])
            for b in self.brawlers
            if b.get("speedTilesPerSec") is not None
            and not (self.SPEED_LO < b["speedTilesPerSec"] < self.SPEED_HI)
        ]
        self.assertFalse(bad, f"speedTilesPerSec outside ({self.SPEED_LO}, {self.SPEED_HI}): {bad}")

    def test_brawlers_variants_range_tiles_in_bounds(self):
        """variants[].params.rangeTiles (when present) must be in (0, 40].

        Known boundary values at exactly 40.0: Mandy super, Mandy hypercharged
        super, Bibi super. The upper bound is inclusive.
        """
        bad = [
            (b["name"], v.get("label"), rt)
            for b in self.brawlers
            for v in b.get("variants", [])
            for rt in [v.get("params", {}).get("rangeTiles")]
            if rt is not None
            and not (self.RANGE_LO < rt <= self.RANGE_HI)
        ]
        self.assertFalse(
            bad,
            f"rangeTiles outside ({self.RANGE_LO}, {self.RANGE_HI}]: {bad}",
        )

    def test_brawlers_variant_range_tiles_finite(self):
        """All rangeTiles values must be finite."""
        bad = [
            (b["name"], v.get("label"), rt)
            for b in self.brawlers
            for v in b.get("variants", [])
            for rt in [v.get("params", {}).get("rangeTiles")]
            if rt is not None and not math.isfinite(rt)
        ]
        self.assertFalse(bad, f"Non-finite rangeTiles: {bad}")

    def test_brawlers_names_are_unique(self):
        """Every brawler name in brawlers.json must be unique."""
        names = [b["name"] for b in self.brawlers]
        counts = Counter(names)
        dupes = {n: c for n, c in counts.items() if c > 1}
        self.assertFalse(dupes, f"Duplicate brawler names: {dupes}")


if __name__ == "__main__":
    unittest.main()
