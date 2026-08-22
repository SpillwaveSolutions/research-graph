#!/usr/bin/env python3
"""Project accepted|reviewed RKC nodes into a rebuildable manifest.

Does not speak Kuzu/Chroma yet. Writes projection/manifest.json so the
index can be destroyed and rebuilt. GRAPH_USE_LLM_EXTRACTION must stay false.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

DEFAULT_STATUS = {"accepted", "reviewed"}


def iter_okf(root: Path):
    research = root / "research"
    if not research.exists():
        return
    fm_re = __import__("re").compile(r"^---\n(.*?)\n---", __import__("re").S)
    for p in sorted(research.rglob("*.md")):
        if "source-assets" in p.parts:
            continue
        text = p.read_text(encoding="utf-8")
        m = fm_re.match(text)
        if not m:
            continue
        fm = {}
        for line in m.group(1).splitlines():
            if ":" in line and not line.startswith(" "):
                k, v = line.split(":", 1)
                fm[k.strip()] = v.strip().strip('"').strip("'")
        yield p, fm


def project(root: Path, statuses: set[str]) -> dict:
    nodes = []
    for path, fm in iter_okf(root):
        st = fm.get("status") or "draft"
        if st not in statuses:
            continue
        nodes.append(
            {
                "id": fm.get("id") or path.stem,
                "type": fm.get("type"),
                "title": fm.get("title"),
                "status": st,
                "path": str(path),
            }
        )
    return {
        "projector": "research-graph",
        "version": "0.1.0",
        "graph_use_llm_extraction": False,
        "status_filter": sorted(statuses),
        "node_count": len(nodes),
        "nodes": nodes,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, required=True)
    ap.add_argument("--status", default="accepted,reviewed")
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()
    statuses = {s.strip() for s in args.status.split(",") if s.strip()}
    manifest = project(args.root, statuses)
    out = args.out or (args.root / "projection" / "manifest.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"wrote": str(out), "node_count": manifest["node_count"]}, indent=2))


if __name__ == "__main__":
    main()
