"""Deterministic unit tests for run-level statistics and interaction contrasts."""
from __future__ import annotations

from pathlib import Path
import sys
import unittest

PACKAGE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE / "scripts"))

from analyze_g1_integrated_campaign import (
    build_policy_channel_interactions,
    mean_sd_ci,
    policy_channel_difference_in_differences,
    quantile,
)


class TestAnalysisHelpers(unittest.TestCase):
    def test_type7_quantile_interpolates(self):
        self.assertAlmostEqual(quantile([0.0, 10.0, 20.0, 30.0], .95), 28.5)

    def test_seed_interval_uses_independent_seed_values(self):
        mean, sd, low, high, n = mean_sd_ci([1.0, 2.0, 3.0, 4.0, 5.0])
        self.assertEqual(n, 5)
        self.assertEqual(mean, 3.0)
        self.assertAlmostEqual(sd, 1.5811388300841898)
        self.assertLess(low, mean)
        self.assertGreater(high, mean)

    def test_policy_channel_difference_in_differences(self):
        self.assertEqual(policy_channel_difference_in_differences(100, 110, 200, 240), 30)

    def test_interaction_pipeline_matches_four_policy_channel_cells(self):
        ue_rows = []
        grant_rows = []
        values = {
            ("all-los", "RoundRobin"): 100.0,
            ("all-los", "TopKCqi"): 110.0,
            ("ue6-nlos", "RoundRobin"): 200.0,
            ("ue6-nlos", "TopKCqi"): 240.0,
        }
        for (channel, policy), value in values.items():
            ue_rows.append({"channel": channel, "mobility": "stationary", "load": "light",
                            "policy": policy, "seed": 11, "direction": "DL", "ue_index": 1,
                            "rx_goodput_bps": value, "pdr": .9, "mean_latency_ms": value / 10,
                            "p95_latency_ms": value / 5, "p99_latency_ms": value / 4,
                            "received_latency_n": 1500})
            grant_rows.append({"channel": channel, "mobility": "stationary", "load": "light",
                               "policy": policy, "seed": 11, "direction": "DL", "ue_index": 1,
                               "prb_symbols": int(value)})
        by_seed, summary = build_policy_channel_interactions(ue_rows, grant_rows)
        goodput = next(row for row in by_seed if row["metric"] == "rx_goodput_bps")
        self.assertEqual(goodput["policy_effect_all_los"], 10.0)
        self.assertEqual(goodput["policy_effect_ue6_nlos"], 40.0)
        self.assertEqual(goodput["policy_effect_difference_in_differences"], 30.0)
        self.assertEqual(goodput["p99_interaction_adequacy"], "not-applicable")
        grant = next(row for row in by_seed if row["metric"] == "prb_symbols")
        self.assertEqual(grant["policy_effect_difference_in_differences"], 30)
        self.assertTrue(summary)


if __name__ == "__main__":
    unittest.main()
