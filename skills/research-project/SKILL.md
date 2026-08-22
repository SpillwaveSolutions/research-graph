---
name: research-project
description: Project validated RKC OKF into Agent Brain (Chroma + BM25 + Kuzu). Owns no types. Default accepted|reviewed. GRAPH_USE_LLM_EXTRACTION=false.
---

# research-project

This plugin **owns no nouns**. Writes go through RKC. Here we only project.

```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/rg_project.py --root knowledge --status accepted,reviewed
```

- Default filter: `accepted|reviewed`.
- `GRAPH_USE_LLM_EXTRACTION=false` — do not let Agent Brain invent edges.
- Projector lives in this plugin until a second consumer needs it in core.
- Destroying the index is always safe. Rebuild from `knowledge/research/**`.
