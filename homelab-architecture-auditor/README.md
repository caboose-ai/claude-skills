# Homelab Architecture Auditor

Audits `caboose-ai.io` homelab architecture consistency across service
manifests, Docker Compose, Authentik SSO providers, dashboard inclusion, smoke
tests, docs, and automation guardrails.

## Install

```bash
npx skills add caboose-ai/ai-skills@homelab-architecture-auditor -g
```

## What It Checks

The bundled scanner is read-only. It produces:

- a service matrix for manifests, compose, configurators, SSO, smoke coverage,
  dashboard inclusion, and docs
- severity-ranked architecture findings with concrete file references
- automation recommendations for hooks, skills, subagents, and MCPs
- scanner safety evidence showing that `.env`, generated evidence, logs,
  screenshots, and JSONL files were not read

## Usage

```bash
uv run python scripts/audit_homelab_architecture.py /path/to/caboose-ai.io --check-safety
uv run python scripts/audit_homelab_architecture.py /path/to/caboose-ai.io --output /path/to/caboose-ai.io/docs/homelab-architecture-audit.md
```

Use this before and after service additions/removals or changes that touch
SSO, dashboard links, compose services, service manifests, or smoke flows.
