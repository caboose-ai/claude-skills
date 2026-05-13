---
name: pre-pr-review-loop
description: Use when preparing to push, publish, open, update, or mark ready a pull request after local code changes, especially when the user says pr, open pr, ship, push this, or yeet.
---

# Pre PR Review Loop

## Principle

The human is last in the loop. Before a PR reaches them, run local review,
fix actionable findings, verify, open or update the PR, request `@codex`
review, fix Codex findings, and only then summarize what remains for the human.

## Workflow

1. Confirm scope before push:
   ```bash
   git status --short --branch
   git diff --stat
   git diff --cached --stat
   git branch -vv
   ```
   If the worktree is mixed, stage only intended files. Do not include unrelated
   local state.
2. Run local review before creating or updating the PR:
   - Read the patch as a reviewer, not as the author.
   - Prioritize bugs, regressions, missing tests, security/secrets issues,
     docs/command drift, CI breakage, and deploy/runtime risks.
   - Findings must cite files/lines where possible.
   - Fix every actionable finding before pushing. If a finding is intentionally
     deferred, record why.
3. Verify with repo-appropriate checks. At minimum:
   ```bash
   git diff --check
   ```
   Also run the relevant build/test/lint commands from `AGENTS.md`, `CLAUDE.md`,
   `README.md`, or project scripts. Re-run after fixes.
4. Commit intentionally. Never commit on `main`. Use Conventional Commit style
   when the repo expects it.
5. Push and create or update a draft PR. The PR body should include what
   changed, why, validation, and known live/manual checks not run.
6. Request Codex review after the PR exists. Default trigger:
   ```bash
   gh pr comment <number> --body '@codex review'
   ```
   If the repo uses a different Codex trigger, use that. If no trigger is
   available, state the blocker.
7. Inspect Codex and CI feedback:
   ```bash
   gh pr checks <number>
   gh pr view <number> --json reviewDecision,comments,reviews,statusCheckRollup
   ```
   For unresolved inline review threads, use the GitHub review-comment workflow
   if available.
8. Loop:
   - Fix actionable Codex or CI findings.
   - Run the relevant local checks again.
   - Commit and push fixes.
   - Request or inspect Codex review again.
   - Stop only when there are no actionable automated findings, or a blocker is
     explicit.
9. Final response format:
   - PR URL and branch
   - local review findings and fixes
   - Codex findings and fixes
   - validation commands and results
   - remaining risks or manual checks
   - clear statement that the human is now the final reviewer

## Guardrails

- Do not mark a draft PR ready for review until the local and Codex loops are
  clean, unless the user explicitly asks.
- Do not merge unless the user explicitly asks.
- Do not hide findings because they were fixed. Summarize them so the human can
  see what changed before their review.
