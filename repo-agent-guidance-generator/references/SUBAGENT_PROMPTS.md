# Subagent Prompts

Use these prompts when delegating read-only repo guidance research. Replace `<repo>` with the absolute repository root.

## Architecture and Repo Map

Read `<repo>` only. Map the repository architecture, major directories, entrypoints, and ownership boundaries. Cite file paths for every claim. Avoid secrets. Separate observed conventions from recommendations. Return confidence levels.

## Commands

Read `<repo>` only. Identify build, run, test, lint, format, release, and CI commands from manifests, task runners, README files, and workflows. Cite file paths. Avoid secrets. Separate observed commands from recommended agent workflow. Return confidence levels.

## Code Style and Dependencies

Read `<repo>` only. Identify naming, typing, framework, formatting, dependency, and abstraction conventions. Cite file paths. Avoid secrets. Separate observed conventions from recommendations. Return confidence levels.

## Testing and Quality

Read `<repo>` only. Identify test layout, test helpers, coverage expectations, fixtures, smoke/integration tests, and quality gates. Cite file paths. Avoid secrets. Separate observed practices from recommendations. Return confidence levels.

## Security and Risk

Read `<repo>` only. Identify secret-handling patterns, data files, migrations, infrastructure, deployment, generated artifacts, destructive commands, and risky directories. Do not reveal secret values. Cite file paths. Separate observed risks from recommendations. Return confidence levels.

## Documentation and Compatibility

Read `<repo>` only. Identify documentation gaps, existing agent guidance, candidate nested `AGENTS.md` scopes, and whether compatibility pointer files for `CLAUDE.md`, `GEMINI.md`, and `.github/copilot-instructions.md` would help. Cite file paths. Avoid secrets. Separate observed gaps from recommendations. Return confidence levels.
