#!/usr/bin/env python3
"""Retrieval ladder stub: prefer RKC pack, then say index is unprojected."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def try_pack(root: Path, root_id: str | None):
    rkc = Path(__file__).resolve().parent.parent.parent / "research-knowledge-capture" / "scripts" / "rkc_pack.py"
    if root_id and rkc.exists():
        proc = subprocess.run(
            [sys.executable, str(rkc), root_id, "--root", str(root)],
            capture_output=True,
            text=True,
        )
        if proc.returncode == 0:
            return json.loads(proc.stdout)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, required=True)
    ap.add_argument("--question", required=True)
    ap.add_argument("--pack-root", default=None, help="Optional RKC node id to pack first")
    args = ap.parse_args()
    packed = try_pack(args.root, args.pack_root)
    print(
        json.dumps(
            {
                "question": args.question,
                "ladder": ["rg", "research-pack", "bm25/chroma", "kuzu"],
                "pack": packed,
                "index": "unprojected — run /research-project. GRAPH_USE_LLM_EXTRACTION=false.",
                "citation_rule": "Finding → Claim → Evidence → source-asset. Never cite a blob.",
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
