# PRD — research-graph (Layer 1)

Companion to `research-knowledge-capture`. This plugin owns **no** types.

## Job

Project validated OKF (`accepted|reviewed`) into Agent Brain:

- Chroma (vectors)
- BM25 (lexical)
- Kuzu (typed graph)

`GRAPH_USE_LLM_EXTRACTION=false`. Projector stays in this plugin until a second consumer needs the Protocol in core.

## Retrieval

`rg` → `/research-pack` (L0) → BM25/Chroma → Kuzu last.

Citations resolve in OKF, never in the index.

## v0.1

Stub projector writes `projection/manifest.json`. Live Kuzu/Chroma wiring is the next ticket.
