"""Validate the source plan, PI gates, transition evidence, and phase boundaries."""
import importlib.util
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]

def load(name,filename):
    spec=importlib.util.spec_from_file_location(name,ROOT/"experiment-scripts"/filename)
    module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module
    spec.loader.exec_module(module)
    return module

runner=load("run_los_nlos_transition","run_los_nlos_transition.py")
analysis=load("analyze_los_nlos_transition","analyze_los_nlos_transition.py")


class TestTransition(unittest.TestCase):
    def setUp(self):
        self.spec=json.loads((ROOT/"configs/los-nlos-transition.json").read_text())

    def test_missing_pi_choices_are_rejected(self):
        with self.assertRaisesRegex(ValueError,"PI must define"):
            runner.verify(self.spec)

    def test_complete_config_and_matrix(self):
        s=self.spec
        s["transition"]={"nlos_start_s":5.0,"nlos_end_s":12.0}
        s["radio"]["bandwidth_hz"]=10000000
        s["traffic_bps"]={
            "target":{"UL":1000000,"DL":20000},
            "background_per_ue":{"UL":20000,"DL":20000}}
        s["orchestrator"]["k"]=3
        runner.verify(s)
        cells=runner.plan(s)
        self.assertEqual(len(cells),8)
        cfg=runner.config_for({"common":{},"nr":{},"orchestrator":{}},s,cells[0])
        self.assertEqual(cfg["common"]["perUeUlBitRate"],[20000]*5+[1000000])
        self.assertEqual(cfg["common"]["mobilityMode"],"target-controlled-linear")
        self.assertEqual(cfg["common"]["channelConditionTargetUe"],6)

    def test_channel_evidence_is_not_just_config_flag(self):
        self.spec["transition"]={"nlos_start_s":5,"nlos_end_s":12}
        cell={"channel":"ue-transition"}
        log=("CHANNEL_TRANSITION,time_s=5.000000,ue_index=6,condition=NLOS\n"
             "CHANNEL_TRANSITION,time_s=12.000000,ue_index=6,condition=LOS\n"
             "CHANNEL_STATE,time_s=1.000000,ue_index=6,condition=LOS\n")
        runner.check_transition(log,cell,self.spec)
        with self.assertRaises(ValueError):
            runner.check_transition(log.replace("condition=NLOS","condition=LOS"),cell,self.spec)

    def test_phase_and_quantile(self):
        self.assertEqual(analysis.phase(4,5,12),"pre-los")
        self.assertEqual(analysis.phase(5,5,12),"nlos-window")
        self.assertEqual(analysis.phase(12,5,12),"post-los")
        self.assertEqual(analysis.percentile([1,2,3,4],.5),2.5)

if __name__=="__main__":
    unittest.main()
