
# ADR 0003 — File-backed Model Registry (Day 1)

## Context
We want transparent, easy-to-edit model manifests during early iterations.

## Decision
Read JSON files from `services/model-registry/data/models/*.json` and serve
them over HTTP.

## Consequences
- Easy to review & version in git
- Single-writer model; add DB later for multi-writer scenarios
