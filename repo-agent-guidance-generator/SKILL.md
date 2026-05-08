---
name: repo-agent-guidance-generator
description: Use when asked to crawl a repository and generate agentic coding guidance, AGENTS.md proposals, nested guidance candidates, or compatibility pointer files for coding agents. Coordinates read-only repo inventory, parallel specialist reviews, and synthesis into proposed guidance artifacts while avoiding secrets and source-code changes.
---

# Repo Agent Guidance Generator

Use this skill to produce repository-specific instructions for coding agents.

## Workflow

1. Confirm the repository root with `git rev-parse --show-toplevel`. If the current directory is not a Git repository, identify the nearest obvious source repository and state the assumption before writing outputs.
2. Check for existing guidance files before drafting:
   - `AGENTS.md`
   - `CLAUDE.md`
   - `GEMINI.md`
   - `.github/copilot-instructions.md`
   - nested `AGENTS.md`
3. Run `scripts/repo_inventory.py <repo-root>` to collect a safe, redacted inventory. Do not inspect or quote secrets.
4. For broad audits, split read-only research across focused agents:
   - architecture and repo map
   - build/run/test/lint/format/CI commands
   - code style, naming, typing, framework, and dependency conventions
   - testing strategy and quality gates
   - security, secrets, data, migrations, infra, and risky directories
   - documentation gaps, nested `AGENTS.md` candidates, and compatibility files
5. Require every research result to cite file paths, distinguish observed facts from recommendations, avoid secret values, and include confidence levels.
6. Synthesize outputs using:
   - `references/AGENTS_TEMPLATE.md` for root and nested guidance
   - `references/SUBAGENT_PROMPTS.md` for delegation prompts
   - `assets/report-template.md` for the final report

## Output Rules

- Do not modify source code.
- Do not overwrite existing guidance files. Create proposed files, patches, or clearly named candidates instead.
- Prefer `docs/agent-guidance-report.md` for the synthesis report.
- If root `AGENTS.md` exists, write `docs/proposed-AGENTS.md`.
- If compatibility files already exist, write proposed versions under `docs/` or include patches in the report.
- Recommend nested `AGENTS.md` only for directories with meaningfully different commands, conventions, risks, or ownership.
- Keep guidance concise and operational. Agent instructions should be specific enough to prevent mistakes without restating generic software engineering advice.
