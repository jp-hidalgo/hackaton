"""Executable checks for the matrix rows the weekend can actually run."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from harness.pep import Event, Policy
from harness.runner import replay, write_digest
from harness.traces import july_chain, recon_burst
from harness.wrap_misw import agent_root, probe_class_agent


class JulyChainTests(unittest.TestCase):
    def test_unexpected_egress_stops_at_a1_before_later_hops(self):
        result = replay(july_chain(), Policy(), name="july")
        self.assertEqual(result.stopped_at, 2)
        self.assertEqual(result.stop_control, "A1")
        self.assertIn("huggingface.co", result.log[1]["reason"])

    def test_kill_criteria_stop_proxy_admin(self):
        events = [e for e in july_chain() if e.step in {1, 3}]
        # step 1 is allowlisted; step 3 is the admin flag
        events[1].step = 2
        result = replay(events, Policy())
        self.assertEqual(result.stop_control, "A3")

    def test_shared_credential_across_workloads_is_a2(self):
        events = [e for e in july_chain() if e.step in {1, 4}]
        events[1].step = 2
        result = replay(events, Policy())
        self.assertEqual(result.stop_control, "A2")

    def test_harness_mode_refuses_open_internet(self):
        event = [e for e in july_chain() if e.zone == "B" and e.step == 5][0]
        result = replay([event], Policy(harness_mode=True))
        self.assertEqual(result.stop_control, "B3")

    def test_canary_pages_b4(self):
        event = [e for e in july_chain() if e.step == 6][0]
        result = replay([event], Policy())
        self.assertEqual(result.pages, ["B4"])
        self.assertFalse(result.stopped)

    def test_dataset_local_path_is_c1(self):
        event = [e for e in july_chain() if e.step == 7][0]
        result = replay([event], Policy())
        self.assertEqual(result.stop_control, "C1")

    def test_imds_is_c2(self):
        event = [e for e in july_chain() if e.step == 8][0]
        result = replay([event], Policy())
        self.assertEqual(result.stop_control, "C2")

    def test_pastebin_class_is_c7(self):
        event = [e for e in july_chain() if e.step == 9][0]
        result = replay([event], Policy())
        self.assertEqual(result.stop_control, "C7")
        self.assertEqual(result.log[0]["verdict"], "delay")

    def test_secret_canary_pages_c8(self):
        event = [e for e in july_chain() if e.step == 10][0]
        result = replay([event], Policy())
        self.assertEqual(result.pages, ["C8"])

    def test_recon_burst_pages_c6(self):
        result = replay(recon_burst(10), Policy(burst_page_after=8))
        self.assertIn("C6", result.pages)
        page_row = next(row for row in result.log if row["control"] == "C6")
        self.assertGreaterEqual(page_row["step"], 8)

    def test_allowlisted_package_install_passes(self):
        event = july_chain()[0]
        decision = Policy().mediate(event)
        self.assertEqual(decision.verdict, "allow")

    def test_digest_is_written(self):
        result = replay(july_chain()[:2], Policy())
        path = write_digest([result], path=ROOT / "artifact" / "egress-digest.json")
        text = path.read_text(encoding="utf-8")
        self.assertIn("sha256", text)
        self.assertIn("package-index", text)


class ClassAgentProbeTests(unittest.TestCase):
    @unittest.skipUnless(agent_root() is not None, "class agent repo not present")
    def test_probe_does_not_require_llm_and_classifies_destinations(self):
        probes = probe_class_agent()
        names = {p.name for p in probes}
        self.assertTrue(names)
        self.assertIn("consultar_productos", names)
        # Localhost API is allowlisted. A configured public RAG host is not.
        rag = next((p for p in probes if p.name == "consultar_politicas"), None)
        api = next((p for p in probes if p.name == "consultar_productos"), None)
        self.assertIsNotNone(api)
        if api and api.dest in {"localhost", "127.0.0.1"}:
            self.assertEqual(api.verdict, "allow")
        if rag and rag.dest and rag.dest not in {"localhost", "127.0.0.1"}:
            self.assertEqual(rag.verdict, "stop")
            self.assertEqual(rag.control_id, "A1")
            self.assertNotIn("password", rag.reason.lower())
            self.assertNotIn("@", rag.dest or "")


if __name__ == "__main__":
    unittest.main()
