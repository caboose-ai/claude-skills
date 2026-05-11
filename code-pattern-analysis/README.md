# code-pattern-analysis

Analyze code patterns and conventions in a repository, then produce actionable do/don't guidance for developers and AI agents.

## Usage

```
/code-pattern-analysis
/code-pattern-analysis src/api/
```

## What it does

1. **Inventories** the repo structure, languages, and tooling config
2. **Dispatches 6 specialist agents** to analyze patterns in parallel:
   - Naming & Formatting
   - File & Project Structure
   - Imports & Dependencies
   - Error Handling & Control Flow
   - API & Interface Design
   - State & Data Patterns
3. **Asks you** about conflicting patterns (when the codebase is inconsistent)
4. **Produces 3 artifacts:**
   - `docs/code-patterns-report.md` — full analysis with citations and frequencies
   - `docs/code-conventions.md` — concise DO/DON'T rules
   - CLAUDE.md patch — proposed section for agent guidance

## Output format

Each rule in the conventions file cites file paths as evidence:

```markdown
## Naming & Formatting
- DO: use camelCase for functions — see `src/utils/parser.ts:12`
- DON'T: use Hungarian notation — found in `legacy/oldModule.ts:45` (legacy code, being phased out)
```

## Scoping

By default, analyzes the entire repository. Pass a subdirectory to scope the analysis:

```
/code-pattern-analysis packages/frontend/
```
