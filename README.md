# Maximum Effort Status Line

Powerline-style status bar for Claude Code with dynamic segments and a rotating quips easter egg when effort is set to max.

![Maximum Effort Status Line](https://raw.githubusercontent.com/caboose-ai/claude-skills/main/maximum-effort-statusline/assets/statusline-preview.png)

## Segments

- **📂 Directory** — smart-truncated working directory (purple)
- **🧠/⚡/🚀 Model** — detected model with emoji (green)
- **💀 Max Effort Quips** — rotating one-liners when effort is max (red)
- **💵 Cost/Tokens** — session spend and token count (yellow)
- **Git** — branch, status, and diff stats (dark)

## Install

```bash
npx skills add caboose-ai/claude-skills@maximum-effort-statusline -g
```

Then restart Claude Code. Run `/effort` and set to max to trigger the easter egg.

## Requirements

- `jq` — for parsing session JSON (`brew install jq` on macOS)
- `ccstatusline` — optional, for git segment (auto-installed via npx/bunx)
- Truecolor terminal (iTerm2, WezTerm, Ghostty, Kitty, Windows Terminal)

## License

MIT
