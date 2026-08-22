---
name: research-ask
description: Answer from OKF ContextPack first. BM25/Chroma next. Kuzu last. Never cite a blob.
---

# research-ask

```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/rg_ask.py --root knowledge --question "..."
```

Ladder:

1. `rg` over `knowledge/research/**`
2. `/research-pack` (RKC spine)
3. BM25 / Chroma over the projection
4. Kuzu last, for typed paths

Citations must resolve Finding → Claim → Evidence → source-asset. If the packer cannot reach Evidence, say so. Do not quote a vector blob.
