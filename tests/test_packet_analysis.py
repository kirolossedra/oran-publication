from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiment-scripts"))
import unittest

from analyze_packet_events import analyze_events, nearest_rank


class PacketAnalyzerGoldTests(unittest.TestCase):
    def setUp(self):
        self.flow = {
            "flow_id": "5", "ue_index": "0", "direction": "DL", "rnti_at_end": "25",
            "source_ip": "1.0.0.2", "source_port": "49153",
            "destination_ip": "7.0.0.2", "destination_port": "2000",
            "configured_rate_bps": "8000", "source_start_s": "0.0000001",
            "source_stop_s": "0.0000002", "sink_stop_s": "0.0000004",
        }

    def event(self, sequence, event_time, tx_time=None, source_port=49153):
        return {
            "event_time_ns": event_time,
            "sequence": sequence,
            "tx_time_ns": event_time if tx_time is None else tx_time,
            "payload_bytes": 100,
            "source_ip": "1.0.0.2",
            "source_port": source_port,
            "destination_ip": "7.0.0.2",
            "destination_port": 2000,
        }

    def test_nearest_rank_and_empty_sample(self):
        self.assertIsNone(nearest_rank([], .95))
        self.assertEqual(nearest_rank([40, 10, 30, 20], .50), 20)
        self.assertEqual(nearest_rank([40, 10, 30, 20], .95), 40)
        self.assertEqual(nearest_rank([40, 10, 30, 20], 1.0), 40)

    def test_duplicates_reordering_loss_unmatched_and_drain(self):
        tx = [self.event(0, 100, 100), self.event(1, 110, 110), self.event(2, 130, 130)]
        rx = [self.event(1, 150, 110), self.event(0, 210, 100),
              self.event(0, 220, 100), self.event(9, 230, 130)]
        packets, metrics = analyze_events(tx, rx, [self.flow], {})
        row = metrics[0]
        self.assertEqual(row["tx_unique_packets"], 3)
        self.assertEqual(row["rx_unique_packets"], 2)
        self.assertEqual(row["duplicate_rx_packets"], 1)
        self.assertEqual(row["missing_by_sink_stop_packets"], 1)
        self.assertEqual(row["unmatched_rx_packets"], 1)
        self.assertEqual(row["reordered_rx_packets"], 1)
        self.assertEqual(row["drained_rx_packets"], 1)
        self.assertEqual(row["received_delay_n"], 2)
        self.assertEqual(row["p50_delay_ns"], 40)
        self.assertEqual(row["p95_delay_ns"], 110)
        status = {(p["sequence"], p["status"]) for p in packets}
        self.assertIn((2, "missing_by_sink_stop"), status)
        self.assertIn((9, "unmatched_rx"), status)

    def test_endpoint_mismatch_is_not_silently_reassigned(self):
        with self.assertRaisesRegex(ValueError, "no configured FlowId mapping"):
            analyze_events([self.event(0, 100, source_port=9999)], [], [self.flow], {})


if __name__ == "__main__":
    unittest.main()
