---
name: code-pattern-analysis
description: Analyze code patterns and conventions in a repository, report on them with do's and don'ts, and produce a concise rules file plus CLAUDE.md patch. Supports optional subdirectory scoping. Dispatches parallel specialist agents for naming, structure, imports, error handling, API design, and state/data patterns. Pauses to ask the user when conflicting patterns are found.
---

# Code Pattern Analysis

Analyze a repository's code patterns and conventions, then produce actionable do/don't guidance for developers and AI agents.

## Workflow

1. **Setup**
   - Confirm the repository root with `git rev-parse --show-toplevel`.
   - If the user specified a subdirectory scope, validate it exists.
   - Check for existing guidance files: `CLAUDE.md`, `AGENTS.md`, `.github/copilot-instructions.md`, any `docs/code-conventions.md`.
   - Note the primary languages and frameworks (from package.json, go.mod, pyproject.toml, Cargo.toml, etc.).

2. **Inventory**
   - Run `scripts/repo_inventory.py <repo-root> [--scope <subdir>]` to collect structure, file stats, and language breakdown.
   - Do not inspect or quote secrets.

3. **Parallel Specialist Analysis**
   - Dispatch 6 focused read-only subagents using prompts from `references/SUBAGENT_PROMPTS.md`.
   - Each agent must:
     - Cite file paths for every claim
     - Include frequency counts (how many files follow a pattern)
     - Distinguish observed patterns from recommendations
     - Flag conflicts (places where the codebase is inconsistent)
     - Avoid secret values
     - Include confidence levels (high/medium/low)

4. **Conflict Resolution**
   - Collect all flagged conflicts from specialist agents.
   - For each significant conflict, **ask the user** which pattern should be canonical.
   - Present conflicts with context: pattern A (frequency, locations) vs pattern B (frequency, locations).
   - Accept the user's decision and record it for synthesis.

5. **Synthesis**
   - Produce three artifacts using templates from `assets/`:
     - `docs/code-patterns-report.md` — full analysis with examples, citations, frequencies
     - `docs/code-conventions.md` — concise do/don't rules for humans and agents
     - CLAUDE.md patch — proposed section to add to the repo's CLAUDE.md (or a new file if none exists)
   - Use `assets/report-template.md` for the full report.
   - Use `assets/conventions-template.md` for the rules file.
   - Use `assets/claude-md-patch-template.md` for the CLAUDE.md section.

## Output Rules

- Do not modify source code.
- Do not overwrite existing guidance files. Create proposed files or patches.
- If `docs/code-conventions.md` already exists, write to `docs/proposed-code-conventions.md`.
- If `CLAUDE.md` already exists, produce a patch section (not a full replacement).
- Every DO/DON'T rule must cite at least one file path as evidence.
- Structural pattern rules should include a brief "why" explaining the observed rationale.
- Keep rules specific to THIS codebase — no generic software engineering advice.

## Scoping

- Default: analyze the entire repository.
- Optional: user can specify a subdirectory (e.g., "analyze src/api/").
- When scoped, report title and rules should reflect the scope clearly.
