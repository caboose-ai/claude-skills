# Maximum Effort Status Line

Powerline-style status bar for Claude Code with dynamic segments and a rotating quips easter egg when effort is set to max.

![Maximum Effort Status Line](https://raw.githubusercontent.com/caboose-ai/ai-skills/main/maximum-effort-statusline/assets/statusline-preview.png)

## Install

```bash
npx skills add caboose-ai/ai-skills@maximum-effort-statusline -g
```

Then restart Claude Code. Run `/effort` and set effort to max to trigger the easter egg.

## Segments

- **Directory**: smart-truncated working directory.
- **Model**: detected model.
- **Context Window**: context usage with color-coded thresholds.
- **Lines Changed**: session diff stats.
- **Effort Quips**: rotating one-liners when effort is xhigh or max.
- **Cost/Tokens**: session spend and token count.
- **Git**: branch with modified, untracked, and staged indicators.
- **Usage Pace**: 5h/7d rate limit pace with time-to-reset when notable.

## Requirements

- `jq` for parsing session JSON.
- Truecolor terminal such as iTerm2, WezTerm, Ghostty, Kitty, or Windows Terminal.

## Credits

Usage pace tracking inspired by [ericboehs' statusline gist](https://gist.github.com/ericboehs/c4340c6febd1b9848eb1656197bf17ca).
