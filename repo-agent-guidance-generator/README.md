# Repo Agent Guidance Generator

Generates repository-specific agent guidance from read-only analysis.

## Install

```bash
npx skills add caboose-ai/ai-skills@repo-agent-guidance-generator -g
```

## What It Produces

The skill coordinates a safe repo inventory, focused specialist research, and synthesis into:

- `docs/agent-guidance-report.md`
- proposed root `AGENTS.md`
- proposed nested `AGENTS.md` files where useful
- optional compatibility pointers for `CLAUDE.md`, `GEMINI.md`, and `.github/copilot-instructions.md`

It is designed to avoid source-code changes and to avoid exposing secret values.
