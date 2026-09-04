#!/usr/bin/env python3
"""Retrieval ladder: rg over research Markdown, then RKC pack, then unprojected index."""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


def find_rg() -> str | None:
    for var in ("OKF_RG_PATH", "PKC_RG_PATH", "SECOND_BRAIN_RG_PATH"):
        override = (os.environ.get(var) or "").strip()
        if not override:
            continue
        p = Path(override)
        if p.is_file() and os.access(p, os.X_OK):
            return str(p.resolve())
        found = shutil.which(override)
        if found:
            return found
        # Explicit override that is not usable: fail closed. Do not fall
        # through to PATH — operators and tests set this to disable rg.
        return None
    return shutil.which("rg")


def try_rg(root: Path, question: str, *, limit: int = 10) -> dict:
    """Step 1 of the ladder: lexical hits over knowledge/research/**."""
    rg = find_rg()
    research = root / "research" if (root / "research").is_dir() else root
    if not research.exists():
        return {"engine": None, "hits": [], "note": f"no research tree at {root}"}
    terms = [t for t in re.split(r"\s+", question.strip()) if t]
    if not rg:
        return {
            "engine": None,
            "hits": [],
            "note": "rg not on PATH; install ripgrep or set OKF_RG_PATH. Search still works via /research-pack.",
        }
    if not terms:
        return {"engine": "rg", "hits": []}
    # AND: intersect file lists per term, then take the first `limit` paths.
    matched: set[Path] | None = None
    for term in terms:
        cmd = [
            rg, "-l", "--no-messages", "--color", "never",
            "-i", "--glob", "*.md", "--glob", "!**/source-assets/**",
            "--", term, str(research),
        ]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30, check=False)
        except (OSError, subprocess.TimeoutExpired):
            return {"engine": None, "hits": [], "note": "rg invocation failed; falling through the ladder"}
        if proc.returncode not in (0, 1):
            return {"engine": None, "hits": [], "note": proc.stderr.strip() or "rg error"}
        files = set()
        for line in proc.stdout.splitlines():
            line = line.strip()
            if line:
                files.add(Path(line))
        matched = files if matched is None else (matched & files)
        if not matched:
            break
    hits = []
    for path in sorted(matched or [])[:limit]:
        try:
            rel = str(path.relative_to(root))
        except ValueError:
            rel = str(path)
        hits.append({"path": rel})
    return {"engine": "rg", "hits": hits, "count": len(hits)}


def find_rkc_pack() -> Path | None:
    """Locate rkc_pack.py. Explicit override fail-closed; else sibling checkout."""
    for var in ("RKC_PACK_PATH", "OKF_RKC_PACK"):
        override = (os.environ.get(var) or "").strip()
        if not override:
            continue
        p = Path(override)
        return p if p.is_file() else None
    sibling = (
        Path(__file__).resolve().parent.parent.parent
        / "research-knowledge-capture"
        / "scripts"
        / "rkc_pack.py"
    )
    return sibling if sibling.is_file() else None


def try_pack(root: Path, root_id: str | None):
    rkc = find_rkc_pack()
    if root_id and rkc is not None:
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
    ap.add_argument("--no-rg", action="store_true", help="Skip the ripgrep step")
    ap.add_argument("--limit", type=int, default=10)
    args = ap.parse_args()
    lexical = None if args.no_rg else try_rg(args.root, args.question, limit=args.limit)
    packed = try_pack(args.root, args.pack_root)
    print(
        json.dumps(
            {
                "question": args.question,
                "ladder": ["rg", "research-pack", "bm25/chroma", "kuzu"],
                "rg": lexical,
                "pack": packed,
                "index": "unprojected — run /research-project. GRAPH_USE_LLM_EXTRACTION=false.",
                "citation_rule": "Finding → Claim → Evidence → source-asset. Never cite a blob.",
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
