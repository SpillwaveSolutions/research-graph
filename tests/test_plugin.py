#!/usr/bin/env python3
from __future__ import annotations
import json, re, unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
VERSION = json.loads((REPO / "plugin.json").read_text())["version"]
NAME = "research-graph"


class PluginPackagingTests(unittest.TestCase):
    def test_lockstep(self):
        claude = json.loads((REPO / ".claude-plugin/plugin.json").read_text())
        codex = json.loads((REPO / ".codex-plugin/plugin.json").read_text())
        cursor = json.loads((REPO / ".cursor-plugin/plugin.json").read_text())
        root = json.loads((REPO / "plugin.json").read_text())
        grok = json.loads((REPO / ".grok-plugin/marketplace.json").read_text())
        found = {claude["version"], codex["version"], cursor["version"], root["version"], grok["version"], grok["plugins"][0]["version"]}
        self.assertEqual(found, {VERSION})

    def test_names(self):
        for path in ("plugin.json", ".claude-plugin/plugin.json", ".codex-plugin/plugin.json", ".cursor-plugin/plugin.json"):
            self.assertEqual(json.loads((REPO / path).read_text())["name"], NAME)

    def test_skills(self):
        for skill in sorted((REPO / "skills").glob("*/SKILL.md")):
            text = skill.read_text()
            self.assertRegex(text, r"(?m)^name: [a-z0-9-]+$")


if __name__ == "__main__":
    unittest.main()
