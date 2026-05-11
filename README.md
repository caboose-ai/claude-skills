# AI Skills

Reusable Claude/Codex skills published from `caboose-ai/ai-skills`.

Each top-level directory is an installable skill. Skill-specific documentation lives inside the skill folder.

## Available Skills

### Maximum Effort Status Line

Powerline-style status bar for Claude Code with dynamic segments and a rotating quips easter egg when effort is set to max.

![Maximum Effort Status Line](https://raw.githubusercontent.com/caboose-ai/ai-skills/main/maximum-effort-statusline/assets/statusline-preview.png)

```bash
npx skills add caboose-ai/ai-skills@maximum-effort-statusline -g
```

See [maximum-effort-statusline/README.md](maximum-effort-statusline/README.md) for details.

### Homelab Architecture Auditor

Audits `caboose-ai.io` homelab architecture consistency across service manifests, Docker Compose, Authentik SSO providers, dashboard inclusion, smoke tests, docs, and automation guardrails.

```bash
npx skills add caboose-ai/ai-skills@homelab-architecture-auditor -g
```

See [homelab-architecture-auditor/README.md](homelab-architecture-auditor/README.md) for details.

### Repo Agent Guidance Generator

Crawls a repository read-only, coordinates focused specialist reviews, and synthesizes agentic coding guidance proposals such as `AGENTS.md`, nested guidance candidates, and compatibility pointer files.

```bash
npx skills add caboose-ai/ai-skills@repo-agent-guidance-generator -g
```

See [repo-agent-guidance-generator/README.md](repo-agent-guidance-generator/README.md) for details.

### Code Pattern Analysis

Analyze code patterns and conventions in a repository, then produce actionable do/don't guidance for developers and AI agents. Dispatches parallel specialist agents for naming, structure, imports, error handling, API design, and state/data patterns.

```bash
npx skills add caboose-ai/ai-skills@code-pattern-analysis -g
```

See [code-pattern-analysis/README.md](code-pattern-analysis/README.md) for details.

## Repository Layout

- `maximum-effort-statusline/`: Claude Code status line skill.
- `homelab-architecture-auditor/`: read-only caboose-ai.io homelab architecture consistency auditor.
- `repo-agent-guidance-generator/`: read-only repository guidance generation skill.
- `code-pattern-analysis/`: read-only repository code pattern and convention analyzer.

## License

MIT
