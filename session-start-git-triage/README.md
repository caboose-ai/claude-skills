# Session Start Git Triage

Reconstructs repository state at the start of a session or resume, then gives a
concrete summary and the safest next action.

## Install

```bash
claude plugin install session-start-git-triage@caboose-ai-skills
```

Standalone skill install:

```bash
npx skills add caboose-ai/ai-skills@session-start-git-triage -g
```

## When To Use

Use this when opening a repo, resuming a prior session, or asking "what now" in
a worktree that might have dirty, untracked, staged, stashed, ahead/behind, or
unpushed changes.

## What It Reports

- branch and upstream tracking state
- recent commits and committed vs uncommitted work
- dirty, staged, untracked, generated, ambiguous, and unrelated files
- stash state
- PR and check state when a PR likely exists
- the safest next command or decision
