# Changelog

## Unreleased

- Plan for live Agent Brain wiring: `docs/plans/make-it-real.md` (Agent Brain Gap A is shipped in 10.7.0; remaining work is this repo).
- Lockstep test reads `plugin.json` instead of a hard-coded `0.1.0`.
- `OKF_RG_PATH` / `RKC_PACK_PATH` that are set but unusable fail closed (no PATH / sibling fall-through). CI runs `test_ask.py` and `test_project.py`.

## 0.1.1 — 2026-08-30

- `rg_ask.py` actually runs ripgrep as retrieval-ladder step 1 when `rg` is on
  PATH (or `OKF_RG_PATH`). AND-search over `knowledge/research/**`. Missing rg
  is not an error; pack/index steps still run. `--no-rg` skips the step.

## 0.1.0

- Initial projector: RKC OKF → Agent Brain (Chroma + BM25 + Kuzu). Owns no nouns.
