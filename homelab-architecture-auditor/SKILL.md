---
name: homelab-architecture-auditor
description: Use when auditing caboose-ai.io homelab architecture consistency across service manifests, Docker Compose, Authentik SSO providers, dashboard inclusion, smoke tests, docs, and automation guardrails.
---

# Homelab Architecture Auditor

## Overview

Run a deterministic, read-only consistency audit for the `caboose-ai.io`
homelab architecture. Use the bundled scanner first, then read the checklist
only when interpreting or extending findings.

## Workflow

1. Confirm the repo root:
   ```bash
   git rev-parse --show-toplevel
   ```
2. Run the safety check before generating a report:
   ```bash
   uv run python scripts/audit_homelab_architecture.py /path/to/caboose-ai.io --check-safety
   ```
3. Generate or refresh the report:
   ```bash
   uv run python scripts/audit_homelab_architecture.py /path/to/caboose-ai.io --output /path/to/caboose-ai.io/docs/homelab-architecture-audit.md
   ```
4. Review severity-ranked findings and fix the source-of-truth mismatch, not
   just the generated report.
5. Verify with repo checks after report or contract changes:
   ```bash
   go test ./internal/servicebuilder ./services/homarr
   git diff --check
   ```

## Scanner Contract

The scanner inspects only whitelisted repo files: service manifests, compose,
selected Go source files, README/guidance docs, and smoke-test definitions. It
does not inspect `.env`, local agent state, logs, screenshots, JSONL evidence,
or live Docker/Authentik state.

Use `--list-scanned-files` if the audit scope needs to be inspected.

## Reference

Read `references/checks.md` when adding checks, validating expected repo
contracts, or deciding whether a finding is drift, intentional policy, or a
known local-only runtime concern.
