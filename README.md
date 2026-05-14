# AI Skills

Reusable Claude/Codex skills published from `caboose-ai/ai-skills`.

Each top-level directory is both a standalone skill bundle and a Claude Code plugin source. Skill-specific documentation lives inside the skill folder.

## Claude Code Marketplace

This repo hosts the `caboose-ai-skills` Claude Code plugin marketplace from `.claude-plugin/marketplace.json`.

Add the marketplace from GitHub:

```bash
claude plugin marketplace add caboose-ai/ai-skills
```

Then install individual plugins:

```bash
claude plugin install maximum-effort-statusline@caboose-ai-skills
claude plugin install homelab-architecture-auditor@caboose-ai-skills
claude plugin install repo-agent-guidance-generator@caboose-ai-skills
claude plugin install session-start-git-triage@caboose-ai-skills
claude plugin install code-pattern-analysis@caboose-ai-skills
```

Plugin skills are namespaced by plugin, so `repo-agent-guidance-generator` exposes `/repo-agent-guidance-generator:repo-agent-guidance-generator`.

## Available Skills

### Maximum Effort Status Line

Powerline-style status bar for Claude Code with dynamic segments and a rotating quips easter egg when effort is set to max.

![Maximum Effort Status Line](https://raw.githubusercontent.com/caboose-ai/ai-skills/main/maximum-effort-statusline/assets/statusline-preview.png)

```bash
claude plugin install maximum-effort-statusline@caboose-ai-skills
```

Standalone skill install:

```bash
npx skills add caboose-ai/ai-skills@maximum-effort-statusline -g
```

See [maximum-effort-statusline/README.md](maximum-effort-statusline/README.md) for details.

### Homelab Architecture Auditor

Audits `caboose-ai.io` homelab architecture consistency across service manifests, Docker Compose, Authentik SSO providers, dashboard inclusion, smoke tests, docs, and automation guardrails.

```bash
claude plugin install homelab-architecture-auditor@caboose-ai-skills
```

Standalone skill install:

```bash
npx skills add caboose-ai/ai-skills@homelab-architecture-auditor -g
```

See [homelab-architecture-auditor/README.md](homelab-architecture-auditor/README.md) for details.

### Repo Agent Guidance Generator

Crawls a repository read-only, coordinates focused specialist reviews, and synthesizes agentic coding guidance proposals such as `AGENTS.md`, nested guidance candidates, and compatibility pointer files.

```bash
claude plugin install repo-agent-guidance-generator@caboose-ai-skills
```

Standalone skill install:

```bash
npx skills add caboose-ai/ai-skills@repo-agent-guidance-generator -g
```

See [repo-agent-guidance-generator/README.md](repo-agent-guidance-generator/README.md) for details.

### Session Start Git Triage

Inspects Git repository state when starting or resuming a session, summarizes
what is going on, and identifies the safest next action.

```bash
claude plugin install session-start-git-triage@caboose-ai-skills
```

Standalone skill install:

```bash
npx skills add caboose-ai/ai-skills@session-start-git-triage -g
```

See [session-start-git-triage/README.md](session-start-git-triage/README.md) for details.

### Code Pattern Analysis

Analyze code patterns and conventions in a repository, then produce actionable do/don't guidance for developers and AI agents. Dispatches parallel specialist agents for naming, structure, imports, error handling, API design, and state/data patterns.

```bash
claude plugin install code-pattern-analysis@caboose-ai-skills
```

Standalone skill install:

```bash
npx skills add caboose-ai/ai-skills@code-pattern-analysis -g
```

See [code-pattern-analysis/README.md](code-pattern-analysis/README.md) for details.

## Repository Layout

- `.claude-plugin/marketplace.json`: Claude Code plugin marketplace catalog.
- `maximum-effort-statusline/`: Claude Code status line skill.
- `homelab-architecture-auditor/`: read-only caboose-ai.io homelab architecture consistency auditor.
- `repo-agent-guidance-generator/`: read-only repository guidance generation skill.
- `session-start-git-triage/`: Git session resume and dirty worktree triage skill.
- `code-pattern-analysis/`: read-only repository code pattern and convention analyzer.

## License

MIT
