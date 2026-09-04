#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
from rg_ask import try_rg  # noqa: E402

FAKE_RG = REPO / "tests/fixtures/fake_rg.py"


class AskRgTests(unittest.TestCase):
    def test_missing_rg_is_not_an_error(self):
        env = os.environ.get("OKF_RG_PATH")
        os.environ["OKF_RG_PATH"] = "/definitely/not/rg"
        try:
            out = try_rg(Path("/tmp"), "anything")
            self.assertIsNone(out["engine"])
            self.assertEqual(out["hits"], [])
            self.assertIn("rg not on PATH", out["note"])
        finally:
            if env is None:
                os.environ.pop("OKF_RG_PATH", None)
            else:
                os.environ["OKF_RG_PATH"] = env

    def test_explicit_bad_override_does_not_fall_through_to_path(self):
        """Invalid OKF_RG_PATH must not consult PATH (ripgrep may be installed)."""
        from rg_ask import find_rg

        env = os.environ.get("OKF_RG_PATH")
        os.environ["OKF_RG_PATH"] = "/definitely/not/rg"
        try:
            self.assertIsNone(find_rg())
        finally:
            if env is None:
                os.environ.pop("OKF_RG_PATH", None)
            else:
                os.environ["OKF_RG_PATH"] = env

    def test_hits_when_fake_rg_present(self):
        FAKE_RG.chmod(0o755)
        tmp = Path(tempfile.mkdtemp())
        try:
            claims = tmp / "research" / "claims"
            claims.mkdir(parents=True)
            (claims / "claim.md").write_text(
                "---\ntype: Claim\ntitle: loop policy\n---\nThe loop policy holds.\n",
                encoding="utf-8",
            )
            os.environ["OKF_RG_PATH"] = str(FAKE_RG)
            out = try_rg(tmp, "loop", limit=5)
            self.assertEqual(out["engine"], "rg")
            self.assertGreaterEqual(out["count"], 1)
        finally:
            os.environ.pop("OKF_RG_PATH", None)
            shutil.rmtree(tmp)


class PackDiscoveryTests(unittest.TestCase):
    def test_missing_override_is_none(self):
        from rg_ask import find_rkc_pack

        env = os.environ.get("RKC_PACK_PATH")
        os.environ["RKC_PACK_PATH"] = "/definitely/not/rkc_pack.py"
        try:
            self.assertIsNone(find_rkc_pack())
        finally:
            if env is None:
                os.environ.pop("RKC_PACK_PATH", None)
            else:
                os.environ["RKC_PACK_PATH"] = env

    def test_override_file_is_used(self):
        from rg_ask import find_rkc_pack

        tmp = Path(tempfile.mkdtemp())
        fake = tmp / "rkc_pack.py"
        fake.write_text("# fake\n", encoding="utf-8")
        env = os.environ.get("RKC_PACK_PATH")
        os.environ["RKC_PACK_PATH"] = str(fake)
        try:
            self.assertEqual(find_rkc_pack(), fake)
        finally:
            if env is None:
                os.environ.pop("RKC_PACK_PATH", None)
            else:
                os.environ["RKC_PACK_PATH"] = env
            shutil.rmtree(tmp)


if __name__ == "__main__":
    unittest.main()
