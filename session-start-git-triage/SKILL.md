---
name: session-start-git-triage
description: Use when starting or resuming work in a Git repository where status may contain untracked, modified, staged, stashed, ahead/behind, or unpushed changes and the agent needs to decide the next safe action.
---

# Session Start Git Triage

## Principle

Do not start repo work blind. When a session begins, resumes, or the user asks
"what now", first reconstruct branch state and classify any dirty or untracked
work before editing, staging, committing, or pushing.

## Workflow

1. Confirm the repository and branch:
   ```bash
   git rev-parse --show-toplevel
   git status --short --branch
   git branch -vv
   git log --oneline --decorate --max-count=8
   ```
2. If the worktree is dirty, inspect shape without taking ownership:
   ```bash
   git diff --stat
   git diff --cached --stat
   git ls-files --others --exclude-standard
   git stash list
   ```
3. Group changes as:
   - `current branch work`: files that match the branch/user request
   - `likely generated/local`: logs, cache, evidence, binaries, request blobs
   - `ambiguous`: anything that may be user work or secret-adjacent
   - `unrelated`: files outside the apparent branch scope
4. For untracked files, inspect names first. Read contents only when needed to
   classify them, and never quote secrets. Do not `git add -A` by default.
5. If a branch has an upstream or a PR likely exists, check it:
   ```bash
   gh pr view --json number,title,url,state,isDraft,mergeStateStatus,statusCheckRollup
   ```
   If no PR exists, use `gh pr list --head <branch>`.
6. Report the next action in concrete terms:
   - branch and tracking state
   - committed vs uncommitted work
   - untracked files and likely ownership
   - checks or PR state if known
   - the safest next command or decision

## Guardrails

- Never delete, reset, checkout, or overwrite dirty files unless explicitly
  requested.
- Preserve unrelated user changes. If unrelated changes block the task, explain
  the conflict and ask for direction.
- If the user says `continue`, `resume`, or `go`, proceed with the safest next
  step after this triage instead of asking them to restate context.
- If the next step is a PR, switch to the pre-PR review workflow before pushing.
