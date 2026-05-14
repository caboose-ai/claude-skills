# Session Start Git Triage

Inspect a Git repository at session start or resume, classify dirty and
untracked work, and identify the next safe action without taking ownership of
unrelated changes.

## Install

```bash
npx skills add caboose-ai/ai-skills@session-start-git-triage -g
```

## Use When

- starting work in a repo with unknown state
- resuming a previous branch
- the user asks "what now" or "continue"
- there are untracked, modified, staged, stashed, ahead/behind, or unpushed
  changes

## What It Produces

- branch and tracking state
- committed vs uncommitted work
- grouped untracked files
- PR/check state when available
- the safest next command or decision
