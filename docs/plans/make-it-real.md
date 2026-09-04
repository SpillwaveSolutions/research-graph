# Plan: Make research-graph real (L1 projector → live Agent Brain)

**Date:** 2026-09-03
**Status:** Gap A (Agent Brain `POST /graph/project`) shipped in [agent-brain v10.7.0](https://github.com/SpillwaveSolutions/agent-brain/releases/tag/v10.7.0) (#235 / #246). Remaining work is this repo.
**Contract source:** [research-knowledge-capture](https://github.com/SpillwaveSolutions/research-knowledge-capture) — no changes.
**Supersedes:** the Agent Brain-side sequencing in `agent-brain/docs/plans/research-graph-make-it-real.md` (Gap A / Phase B item 6). That file is a historical design; this file is the execution plan.

---

## 0. Decisions locked by review (2026-09-03)

These override earlier drafts. Do not reopen them in Phase A/B PRs.

| Decision | Choice |
|---|---|
| Graph backend | **`GRAPH_STORE_TYPE=simple`**. Disposable per-root index; JSON persist under the state dir. Avoids the kuzu crash class the server isolates against. Kuzu is an operator override later, not the projector default. |
| Graph rebuild | **`replace: true`** on every `/graph/project`. Typed facts are small. No incremental graph. |
| Vector rebuild (v0.2) | **Always `POST /index/add`**, then **destroy + re-add** for a clean rebuild. Keep `source_hash` in manifest v2 for the convergence assertion. Do **not** skip unchanged hashes in the client — Agent Brain already has a per-folder tracker; the case that matters is a node *leaving* `accepted`, and prune-on-delete is not confirmed. Incremental prune is deferred. |
| `informs` | **Do not write.** Query-only inverse of content-media `Article → draws_from → Finding`. We do not own `Article`. Sample corpus has none. Follow-on ticket, not v0.3. |
| CI | **Fake `BrainClient` only.** No live Agent Brain in GitHub Actions. One optional **manual** E2E against RKC `sample-knowledge`. |
| Transport | **TCP only.** Stdlib `urllib` cannot speak UDS. Read `base_url` + API key from the CLI state dir (or env). |
| Version pin | **Runtime**, not pip. Plugin is bare `python3 scripts/…`. Phase B: `GET /health` → fail closed if server `< 10.7.0`. |
| YAML | **Try-import PyYAML, else vendored `_mini_yaml`** (copy of RKC `rkc_common._mini_yaml`). No required pip dep. |
| Graph index flag | **`ENABLE_GRAPH_INDEX=false` in Phase A.** Extractor is `none`, so a graph-enabled add would run an empty graph build every time. Turn it on in Phase B. |
| Embeddings | **Not “zero LLM” for vectors.** Indexing needs an embedding provider. Default: **Ollama** (no cloud key). If `OPENAI_API_KEY` is set, OpenAI. Else fail closed with a message that names both. This gates the manual E2E. |
| `/index/add` | **Async 202 + job id.** Project must poll to `COMPLETED`/`FAILED` before success. `DELETE /index` returns **409** while a job runs — destroy waits for idle too. |

---

## 1. Architecture

Three layers, one job each. Nouns stay in L0. The index never invents edges.

```
L0 RKC                         L1 research-graph                      Agent Brain >= 10.7.0
knowledge/research/**          scan accepted|reviewed                 POST /index/add  (202 + job)
  8 types, 12 rels, locators     projection/corpus/<id>.md              Chroma + BM25
                                 projection/manifest.json v2          POST /graph/project (Phase B)
                                 projection/.agent-brain/               typed facts, replace=true
                                   STATE_DIR + config.json            GET /graph/entity/okf:Type/id
                                 BrainClient (TCP + bearer)
                                 rg_ask ladder
                                   1 rg (OKF_RG_PATH fail-closed)
                                   2 rkc_pack (RKC_PACK_PATH / sibling)
                                   3 POST /query → remap via manifest
                                   4 GET /graph/entity spine
```

**Fail-closed writes / fail-soft reads**

- `/research-project` — server missing, unhealthy, job failed, or (Phase B) version `< 10.7.0` → exit nonzero.
- `/research-ask` — missing rg / missing pack / missing server → that rung is `unavailable`; lower rungs still answer.

**Path containment.** `agent-brain init` with `AGENT_BRAIN_STATE_DIR=<root>/projection/.agent-brain` makes the project root `<root>/projection` (parent of a directory literally named `.agent-brain`). Corpus at `<root>/projection/corpus` is inside that root, so `/index/add` accepts it.

**Auth and URL.** `init` writes `config.json` (mode 0600) with a generated `api_key`. `start` advertises `base_url` on TCP and passes the key to the server as bearer. `BrainClient` reads both from the state dir. Overrides: `AGENT_BRAIN_URL`, `AGENT_BRAIN_API_KEY`. Never UDS.

**Query hit → OKF locator.** `/query` `source` is the absolute path of the indexed file. Corpus files are named `<id>.md`. Manifest maps `id` → root-relative `okf_path` (`research/findings/…md`). Citation is that path, never a chunk id or graph blob.

**`POST /graph/project` 400.** The server rejects any relation whose `src`/`dst` is not an entity id **in the same payload** (`unknown_relation_endpoint`). The “both ends `accepted|reviewed`” filter is mandatory, not a nicety.

---

## 2. Env table (per-root instance)

Set by `/research-project` when it `init`/`start`s the instance.

| Variable | Phase A | Phase B |
|---|---|---|
| `AGENT_BRAIN_STATE_DIR` | `<root>/projection/.agent-brain` | same |
| `GRAPH_DOC_EXTRACTOR` | `none` | `none` |
| `GRAPH_USE_LLM_EXTRACTION` | `false` | `false` |
| `ENABLE_GRAPH_INDEX` | `false` | `true` |
| `GRAPH_STORE_TYPE` | `simple` | `simple` |
| Embedding provider | Ollama, or OpenAI if key present | same |

Require `agent-brain-cli` on PATH for instance management. Server package is `agent-brain-rag`; CLI pin of `^10.4` is fine — the **runtime** health check enforces 10.7.0 in Phase B.

---

## 3. L0 → graph payload

Only `accepted|reviewed`. Only edges whose **both** ends are in that set (and therefore in `entities[]`).

```json
{
  "source_tag": "research-graph",
  "replace": true,
  "entities": [
    {
      "type": "okf:Finding",
      "id": "finding.loop-policy.01J8X000000000000000000005",
      "properties": {
        "okf_path": "research/findings/finding.loop-policy.01J8X000000000000000000005.md",
        "title": "Detector holds false civic alerts at 1.4%"
      }
    }
  ],
  "relations": [
    {
      "src": "finding.loop-policy.01J8X000000000000000000005",
      "predicate": "asserts",
      "dst": "claim.loop-policy.01J8X000000000000000000006"
    }
  ]
}
```

Twelve RKC rels pass through as snake_case: `has_subject`, `related_to`, `has_task`, `ingested_from`, `asks`, `answers`, `produced`, `asserts`, `evidenced_by`, `contradicts`, `supersedes`, `same_as`.

Sample spine (verified): Finding `…0005` `asserts` Claims `…0006` and `…0008`, `answers` Question `…0004`. Claim `…0006` `evidenced_by` Evidence `…0007`, locator `research/source-assets/3134…/original.md` lines 3–3.

---

## 4. Manifest v2

Paths are **root-relative** (`research/…`), never absolute. Destroy + rebuild must converge across machines.

```json
{
  "projector": "research-graph",
  "version": "0.2.0",
  "graph_use_llm_extraction": false,
  "status_filter": ["accepted", "reviewed"],
  "node_count": 11,
  "nodes": [
    {
      "id": "finding.loop-policy.01J8X000000000000000000005",
      "type": "Finding",
      "status": "accepted",
      "okf_path": "research/findings/finding.loop-policy.01J8X000000000000000000005.md",
      "corpus_path": "projection/corpus/finding.loop-policy.01J8X000000000000000000005.md",
      "source_hash": "sha256:…"
    }
  ]
}
```

`source_hash` is sha256 of the **source OKF file bytes**. Used to assert rebuild convergence. Not used to skip `/index/add` in v0.2.

---

## 5. Sequenced work

### PR 0 — unblock CI (this repo, before Phase A)

Main is red since v0.1.1.

1. **Lockstep version** — `tests/test_plugin.py` hard-codes `VERSION = "0.1.0"` while every manifest is `0.1.1`. Read `plugin.json` instead of a constant.
2. **`find_rg` fail-closed** — an explicit `OKF_RG_PATH` that is not an executable file currently falls through to `shutil.which("rg")`. Invalid override must return `None` and **not** consult PATH. Unblocks `test_missing_rg_is_not_an_error` on machines with ripgrep.
3. **Pack discovery** — `try_pack` walks three directories above the script (`…/research-knowledge-capture/scripts/rkc_pack.py`). That is sibling-checkout only; marketplace installs never see it. Add `RKC_PACK_PATH` (same pattern as `OKF_RG_PATH`): explicit override fail-closed, else sibling fallback.

### Phase A — v0.2.0  vectors + lexical

4. Frontmatter: try PyYAML, else vendored `_mini_yaml` (list-of-maps `links:`).
5. Corpus writer `<root>/projection/corpus/<id>.md`. Drafts never copied.
6. Manifest v2, root-relative paths, `source_hash`.
7. `BrainClient` protocol: `health`, `index_add` (poll job), `query`, `wait_idle`, `delete_index`. Fake in tests; TCP+bearer in prod. Discover URL/key from state dir.
8. Instance `init`/`start` with the Phase A env table. Unreachable → project fails closed.
9. `rg_project` → `POST /index/add` on the corpus folder; poll to completion.
10. Destroy path: wait idle → `DELETE /index` → delete `projection/corpus` (+ keep manifest rewrite on next project).
11. `rg_ask` step 3: hybrid `/query`, remap `source` basename → manifest → `{node_id, okf_path}`.
12. **Rung 2 without `--pack-root`:** parse node ids from rung-1 hits (and/or corpus/manifest) and feed them to `rkc_pack`. Bare questions must still walk the L0 spine. `--pack-root` remains an override.
13. **Tests**
    - Fake brain: drafts never reach `index_add`; job is polled; destroy waits through 409.
    - **Synthetic fixture** with `draft` / `rejected` / `superseded` / `accepted` nodes. All eleven `sample-knowledge` nodes are `accepted` — the sample cannot prove exclusion, and the YAML `links` parser needs those cases too.
    - Discover RKC sample via sibling or `RKC_SAMPLE` env; drop the hard-coded `/workspace/repos/…` skip.
    - CI runs `test_plugin.py`, `test_ask.py`, `test_project.py`, new projector tests.
14. Release v0.2.0 (lockstep manifests, CHANGELOG, todo item 2 partial).

### Phase B — v0.3.0  typed graph

15. Flip `ENABLE_GRAPH_INDEX=true`. Health check: fail closed if version `< 10.7.0`.
16. `rg_project` → `POST /graph/project` from parsed `links`, `source_tag=research-graph`, `replace=true`, both ends in payload.
17. `rg_ask` step 4: `GET /graph/entity/okf:<Type>/<id>` on step-3 hits; walk `asserts` / `evidenced_by` / `answers`.
18. **Manual E2E** on `sample-knowledge` (Ollama or OpenAI): project → ask `"false alert rate"` → cite `evidence.loop-policy…0007` locator. Destroy + rebuild → identical manifest (relative paths).
19. Release v0.3.0. Todo items 2 and 3 done.

### Phase C — family, not on the critical path

Worklog/ULID hooks, README disambiguation vs AGER’s “research graph” sample, okf-plugin family roster. Demo + posts is distribution, not the ladder.

---

## 6. What we will not do

- No further Agent Brain changes for this ladder.
- No RKC changes.
- No frontmatter extractor inside Agent Brain.
- No writing `informs` / `Article` edges.
- No live Agent Brain in CI.
- No UDS.
- No client-side “skip unchanged hash” `/index/add` in v0.2.
- No Forge integration.

---

## 7. Acceptance

- `/research-project` on RKC `sample-knowledge` fills a per-root instance (Chroma + BM25; Kuzu-shaped facts in Phase B on the **simple** store), only `accepted|reviewed`, extractor off.
- `/research-ask "false alert rate"` walks all four rungs (Phase B); citations resolve `Finding → Claim → Evidence → source-asset` in OKF.
- Destroy + rebuild converges on **relative** manifest paths.
- Drafts are test-enforced absent (synthetic fixture).
- Missing rg / RKC / server each drop one rung without failing the ladder.
- CI green on every push, including projector and ladder tests, with no live index.
