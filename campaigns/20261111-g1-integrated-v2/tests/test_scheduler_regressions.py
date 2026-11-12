"""Focused regression tests for the G1 scheduling and campaign bookkeeping fixes.

Run in the provisioned WSL project with Python dependencies installed:
python3 -m unittest discover -s campaigns/20261111-g1-integrated-v2/tests -v
"""
from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[3]
PACKAGE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "simulator/ns-3.48/contrib/iboran"))
sys.path.insert(0, str(PACKAGE / "scripts"))

from model.iboran_controller.iboran_dapp_algos.dapp_algo_ue_selection_round_robin import (
    DAppAlgoUeSelectionRoundRobin,
)
from model.iboran_controller.iboran_dapp_algos.dapp_algo_ue_selection_top_k import (
    DAppAlgoUeSelectionTopK,
)
from run_g1_integrated_campaign import plan, latest_success, attempt_number
from analyze_g1_integrated_campaign import unique_planned_cells


def indication(cqis=(15, 15, 15), frame=0):
    return SimpleNamespace(
        frameNo=frame, subframeNo=0, linkDirection=0,
        timestamp=10_240_000_000,
        ue=[SimpleNamespace(rnti=25 + i, cqi=cqi) for i, cqi in enumerate(cqis)],
    )


class TestSchedulerFixes(unittest.TestCase):
    def test_rr_never_served_first_across_frame_wrap(self):
        p = DAppAlgoUeSelectionRoundRobin.__new__(DAppAlgoUeSelectionRoundRobin)
        p.k = 1
        p.process([0, 1, 2], indication(frame=0), None,
                  _hist_link_rnti_subframe={0: {25: 1_161_000_000}})
        self.assertEqual(p.selected_idx_k, [1])

    def test_rr_oldest_served_first(self):
        p = DAppAlgoUeSelectionRoundRobin.__new__(DAppAlgoUeSelectionRoundRobin)
        p.k = 1
        p.process([0, 1, 2], indication(), None,
                  _hist_link_rnti_subframe={0: {
                      25: 4_000_000_000, 26: 3_000_000_000, 27: 9_000_000_000}})
        self.assertEqual(p.selected_idx_k, [1])

    def test_topk_preserves_primary_cqi_ranking(self):
        p = DAppAlgoUeSelectionTopK.__new__(DAppAlgoUeSelectionTopK)
        p.k = 1
        p._get_metric_of_candidates = lambda r, cand, **kw: [r.ue[i].cqi for i in cand]
        p.process([0, 1, 2], indication(cqis=(1, 15, 1)), None,
                  _hist_link_rnti_subframe={0: {26: 9_000_000_000}})
        self.assertEqual(p.selected_idx_k, [1])

    def test_topk_equal_score_prefers_unserved(self):
        p = DAppAlgoUeSelectionTopK.__new__(DAppAlgoUeSelectionTopK)
        p.k = 1
        p._get_metric_of_candidates = lambda r, cand, **kw: [r.ue[i].cqi for i in cand]
        p.process([0, 1, 2], indication(), None,
                  _hist_link_rnti_subframe={0: {25: 3_000_000_000}})
        self.assertEqual(p.selected_idx_k, [1])

    def test_plan_has_160_unique_cells(self):
        cells = plan()
        self.assertEqual(len(cells), 160)
        self.assertEqual(len({c["cell_id"] for c in cells}), 160)

    def test_directional_cells_are_subset_not_extras(self):
        base = plan()
        directional = [c for c in base if c["load"] in ("dl-contending", "ul-contending")]
        self.assertEqual(len(directional), 80)
        self.assertEqual(len(unique_planned_cells(base, directional)), 160)

    def test_attempt_numbers_sort_numerically(self):
        self.assertGreater(attempt_number(Path("attempt-10")),
                           attempt_number(Path("attempt-09")))

    def test_resume_requires_exact_policy_source_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            cell_dir = Path(tmp) / "cell"
            attempt = cell_dir / "attempt-10"
            logs = attempt / "logs"
            logs.mkdir(parents=True)
            (attempt / "exit-status.txt").write_text("0\n")
            (attempt / "run-metadata.json").write_text(json.dumps({
                "packet_measurement_schema": "serialized-app-header-v1",
                "source_sha256": {"file": "old"},
            }))
            (logs / "kpi.json").write_text("{}")
            (logs / "packet-events.csv").write_text(
                "event,time_ns,ue_index,direction,sequence,tx_time_ns,bytes\nTX,1,1,0,1,1,512\n"
            )
            (logs / "mac-grants.csv").write_text(
                "time_ns,rnti,direction,rbg_count,mcs\n1,25,DL,1,1\n"
            )
            (logs / "mac-demand.csv").write_text(
                "time_ns,rnti,direction,buffer_bytes,cqi\n1,25,0,512,1\n"
            )
            self.assertFalse(latest_success(cell_dir, {"file": "new"}))
            self.assertTrue(latest_success(cell_dir, {"file": "old"}))


if __name__ == "__main__":
    unittest.main()
