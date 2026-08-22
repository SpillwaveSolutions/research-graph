#!/usr/bin/env python3
from __future__ import annotations
import json, sys, tempfile, unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
from rg_project import project  # noqa: E402

SAMPLE = Path("/workspace/repos/research-knowledge-capture/sample-knowledge")


class ProjectTests(unittest.TestCase):
    def test_default_skips_draft(self):
        if not SAMPLE.exists():
            self.skipTest("RKC sample missing")
        m = project(SAMPLE, {"accepted", "reviewed"})
        self.assertGreaterEqual(m["node_count"], 8)
        self.assertFalse(m["graph_use_llm_extraction"])
        types = {n["type"] for n in m["nodes"]}
        self.assertIn("Claim", types)
        self.assertIn("Finding", types)


if __name__ == "__main__":
    unittest.main()
