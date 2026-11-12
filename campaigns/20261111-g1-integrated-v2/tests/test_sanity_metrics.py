"""Small pure-data checks for the high-throughput/starvation sanity report."""
from __future__ import annotations

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from sanity_g1 import jain, longest_backlogged_grant_gap


class TestSanityKpis(unittest.TestCase):
    def test_jain_equal_throughput_is_one(self):
        self.assertAlmostEqual(jain([5, 5, 5, 5, 5, 5]), 1.0)

    def test_jain_starvation_reduces_fairness(self):
        self.assertAlmostEqual(jain([0, 0, 0, 0, 0, 20]), 1 / 6)

    def test_no_queue_demand_is_not_starvation(self):
        samples = [(i * 100_000_000, 0) for i in range(30)]
        self.assertEqual(longest_backlogged_grant_gap(samples, []), 0.0)

    def test_backlogged_no_grant_detects_starvation(self):
        samples = [(i * 100_000_000, 500) for i in range(26)]
        self.assertGreater(longest_backlogged_grant_gap(samples, []), 1.0)

    def test_actual_grants_reset_backlog_gap(self):
        samples = [(i * 100_000_000, 500) for i in range(26)]
        grants = [i * 100_000_000 for i in range(26)]
        self.assertLess(longest_backlogged_grant_gap(samples, grants), 1.0)

    def test_nonempty_queue_followed_by_idle_resets_backlog(self):
        samples = [(i * 100_000_000, 500 if i % 5 < 4 else 0) for i in range(26)]
        self.assertLess(longest_backlogged_grant_gap(samples, []), 1.0)


if __name__ == "__main__":
    unittest.main()
