# AGENTS.md — research-graph

Layer 1. Owns **no** OKF types. Projects RKC into Agent Brain.

- `/research-project` — accepted|reviewed only. `GRAPH_USE_LLM_EXTRACTION=false`.
- `/research-ask` — rg → pack → BM25/Chroma → Kuzu last.
- Never cite a vector/graph blob. Citations are OKF locators.
- Destroying the index is always safe.
