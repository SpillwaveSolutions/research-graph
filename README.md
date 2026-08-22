# research-graph

Layer 1 of the research second brain. Projects [RKC](https://github.com/SpillwaveSolutions/research-knowledge-capture) OKF into Agent Brain (Chroma + BM25 + Kuzu). **Owns no nouns.**

```
python3 scripts/rg_project.py --root ../research-knowledge-capture/sample-knowledge
python3 scripts/rg_ask.py --root ../research-knowledge-capture/sample-knowledge \
  --question "false alert rate" --pack-root subject.loop-policy.01J8X000000000000000000001
```

`GRAPH_USE_LLM_EXTRACTION=false`. Default project `accepted|reviewed`. Destroying the index is always safe.

Hosts: Claude Code, Grok Build, Codex, Cursor, Agent Plugins 1.0.
