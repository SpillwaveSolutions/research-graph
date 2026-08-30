# Changelog

## Unreleased

## 0.1.1 — 2026-08-30

- `rg_ask.py` actually runs ripgrep as retrieval-ladder step 1 when `rg` is on
  PATH (or `OKF_RG_PATH`). AND-search over `knowledge/research/**`. Missing rg
  is not an error; pack/index steps still run. `--no-rg` skips the step.

## 0.1.0

- Initial projector: RKC OKF → Agent Brain (Chroma + BM25 + Kuzu). Owns no nouns.
