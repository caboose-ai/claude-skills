---
name: maximum-effort-statusline
description: Powerline-style Claude Code status bar with dynamic segments (directory, model, cost, git) and a rotating quips easter egg when effort is set to max
---

# Maximum Effort Status Line

A powerline-style status bar for Claude Code that shows directory, model, cost/tokens, and git info — plus a rotating quips easter egg when you crank effort to max.

![Maximum Effort Status Line](https://raw.githubusercontent.com/caboose-ai/claude-skills/main/maximum-effort-statusline/assets/statusline-preview.png)

## What It Does

Adds a colorful, dynamically-sized status line to Claude Code with these segments:

- **📂 Directory** — current working directory with smart truncation (purple)
- **🧠/⚡/🚀 Model** — detected model with emoji (green)
- **💀 Max Effort Quips** — rotating one-liners when effort is set to max (red) — a fun motivational easter egg
- **💵 Cost/Tokens** — session spend and token count (yellow)
- **Git Info** — branch, status, and diff stats via `ccstatusline` (dark)

Segments use powerline-style arrow transitions between colored blocks.

## Installation

When the user asks to install this skill, follow these steps:

### Step 1: Create the status line script

Write this file to `~/.claude/hooks/statusline.sh`:

```bash
#!/usr/bin/env bash

# Maximum Effort Status Line for Claude Code
# Reads session context from stdin (JSON) and outputs a powerline-style status bar

# Read stdin (session context JSON) with timeout
if command -v timeout &> /dev/null; then
  SESSION_DATA=$(timeout 1 cat 2>/dev/null || echo '{}')
else
  SESSION_DATA=$(cat 2>/dev/null || echo '{}')
fi

# Get terminal width (default to 80 if unavailable)
TERM_WIDTH=${COLUMNS:-$(tput cols 2>/dev/null || echo 80)}

# Get current working directory
CWD="${PWD}"
HOME_DIR="${HOME}"

# Shorten directory path (replace home with ~)
if [[ "$CWD" == "$HOME_DIR"* ]]; then
  CWD_SHORT="~${CWD#$HOME_DIR}"
else
  CWD_SHORT="$CWD"
fi

# Calculate available width for directory (reserve space for other segments)
DIR_MAX_WIDTH=$((TERM_WIDTH - 70))
if [[ $DIR_MAX_WIDTH -lt 20 ]]; then
  DIR_MAX_WIDTH=20
fi

# Truncate path dynamically based on available width
if [[ ${#CWD_SHORT} -gt $DIR_MAX_WIDTH ]]; then
  if [[ $DIR_MAX_WIDTH -lt 30 ]]; then
    BASENAME=$(basename "$CWD_SHORT")
    PARENT=$(dirname "$CWD_SHORT" | xargs basename 2>/dev/null || echo "")
    if [[ -n "$PARENT" ]]; then
      CWD_SHORT="…/${PARENT}/${BASENAME}"
    else
      CWD_SHORT="…/${BASENAME}"
    fi
  else
    IFS='/' read -ra PATH_PARTS <<< "$CWD_SHORT"
    NUM_PARTS=${#PATH_PARTS[@]}
    CWD_SHORT="${PATH_PARTS[$((NUM_PARTS-1))]}"
    for ((i=NUM_PARTS-2; i>=0; i--)); do
      TEST_PATH="${PATH_PARTS[$i]}/${CWD_SHORT}"
      if [[ ${#TEST_PATH} -lt $((DIR_MAX_WIDTH - 2)) ]]; then
        CWD_SHORT="$TEST_PATH"
      else
        CWD_SHORT="…/${CWD_SHORT}"
        break
      fi
    done
  fi
fi

# Parse session data with jq (if available)
if command -v jq &> /dev/null && [[ -n "$SESSION_DATA" ]]; then
  MODEL=$(echo "$SESSION_DATA" | jq -r 'if (.model | type) == "object" then .model.id // .model.display_name // empty elif .model then .model else empty end' 2>/dev/null)
  TOKENS=$(echo "$SESSION_DATA" | jq -r '.total_input_tokens // .tokensUsed // empty' 2>/dev/null)
  COST=$(echo "$SESSION_DATA" | jq -r '.total_cost_usd // .costUSD // empty' 2>/dev/null)
  EFFORT=$(echo "$SESSION_DATA" | jq -r '.effort.level // empty' 2>/dev/null)
else
  MODEL=""
  TOKENS=""
  COST=""
  EFFORT=""
fi

# ANSI color codes
RESET="\033[0m"
BOLD="\033[1m"
BG_PURPLE="\033[48;2;150;100;200m"
BG_GREEN="\033[48;2;120;200;120m"
BG_YELLOW="\033[48;2;255;200;100m"
BG_DARK="\033[48;2;35;40;52m"
FG_BLACK="\033[38;2;31;36;48m"
FG_PURPLE="\033[38;2;150;100;200m"
FG_GREEN="\033[38;2;120;200;120m"
FG_YELLOW="\033[38;2;255;200;100m"

# Build segments
SEGMENTS=""

# Directory segment
DIR_SEGMENT="${BOLD}${FG_BLACK}${BG_PURPLE} 📂 ${CWD_SHORT} ${RESET}"
SEGMENTS="${DIR_SEGMENT}"
LAST_BG="${FG_PURPLE}"

# Model segment with emoji (if available)
if [[ -n "$MODEL" ]]; then
  case "$MODEL" in
    *opus*|*Opus*) MODEL_EMOJI="🧠" ;;
    *sonnet*|*Sonnet*) MODEL_EMOJI="⚡" ;;
    *haiku*|*Haiku*) MODEL_EMOJI="🚀" ;;
    *) MODEL_EMOJI="🤖" ;;
  esac

  MODEL_SHORT="$MODEL"
  MODEL_SHORT=$(echo "$MODEL_SHORT" | sed 's/^[a-z]*\.anthropic\.//; s/^anthropic\.//')
  MODEL_SHORT=$(echo "$MODEL_SHORT" | sed 's/^claude-//; s/-v[0-9].*//; s/-[0-9]*-[0-9]*$//; s/\[.*\]//')

  MODEL_SEGMENT="${LAST_BG}${BG_GREEN}${RESET}${BOLD}${FG_BLACK}${BG_GREEN} ${MODEL_EMOJI} ${MODEL_SHORT} ${RESET}"
  SEGMENTS="${SEGMENTS}${MODEL_SEGMENT}"
  LAST_BG="${FG_GREEN}"
fi

# Maximum effort quips easter egg
if [[ "$EFFORT" == "max" ]]; then
  QUIPS=(
    "MAXIMUM EFFORT"
    "CHIMICHANGA TIME"
    "4th wall? what wall"
    "this is gonna hurt"
    "DANGER NOODLE MODE"
    "time to get weird"
    "merc with a mouth"
    "did I leave the stove on"
    "superhero landing incoming"
    "please don't make the suit green"
    "wow this is big boy stuff"
    "from the studio that brought you no other movies"
    "I had another quip but I forgot it"
    "have you seen my chimichangas"
    "zip it Thanos"
  )
  QUIP_IDX=$(( $(date +%s) / 4 % ${#QUIPS[@]} ))
  QUIP="${QUIPS[$QUIP_IDX]}"

  BG_RED="\033[48;2;200;40;40m"
  FG_RED="\033[38;2;200;40;40m"
  FG_WHITE="\033[38;2;255;255;255m"

  DP_SEGMENT="${LAST_BG}${BG_RED}${RESET}${BOLD}${FG_WHITE}${BG_RED} 💀 ${QUIP} ${RESET}"
  SEGMENTS="${SEGMENTS}${DP_SEGMENT}"
  LAST_BG="${FG_RED}"
fi

# Cost/tokens segment (if available)
if [[ -n "$COST" ]] || [[ -n "$TOKENS" ]]; then
  COST_TEXT=""

  if [[ -n "$COST" ]]; then
    COST_FORMATTED=$(printf "%.2f" "$COST" 2>/dev/null || echo "$COST")
    COST_TEXT="\$${COST_FORMATTED}"
  fi

  if [[ -n "$TOKENS" ]]; then
    if [[ $TOKENS -gt 1000 ]]; then
      TOKENS_K=$(awk "BEGIN {printf \"%.0fk\", $TOKENS/1000}" 2>/dev/null || echo "${TOKENS}k")
      TOKENS_TEXT="${TOKENS_K}"
    else
      TOKENS_TEXT="${TOKENS}"
    fi
    COST_TEXT="${COST_TEXT:+$COST_TEXT }${TOKENS_TEXT}"
  fi

  COST_SEGMENT="${LAST_BG}${BG_YELLOW}${RESET}${BOLD}${FG_BLACK}${BG_YELLOW} 💵 ${COST_TEXT} ${RESET}"
  SEGMENTS="${SEGMENTS}${COST_SEGMENT}"
  LAST_BG="${FG_YELLOW}"
fi

# Get git info from ccstatusline (try bunx, fall back to npx)
if command -v bunx &> /dev/null; then
  GIT_INFO=$(echo "$SESSION_DATA" | bunx -y ccstatusline@latest 2>/dev/null)
elif command -v npx &> /dev/null; then
  GIT_INFO=$(echo "$SESSION_DATA" | npx -y ccstatusline@latest 2>/dev/null)
else
  GIT_INFO=""
fi

# Add transition to git section
if [[ -n "$GIT_INFO" ]]; then
  SEGMENTS="${SEGMENTS}${LAST_BG}${BG_DARK}${RESET}${GIT_INFO}"
else
  SEGMENTS="${SEGMENTS}${RESET}"
fi

echo -e "${SEGMENTS}"
```

### Step 2: Make it executable

Run: `chmod +x ~/.claude/hooks/statusline.sh`

### Step 3: Configure Claude Code settings

Add the following to the user's `~/.claude/settings.json` (merge into existing config):

```json
{
  "statusLine": {
    "type": "command",
    "command": "~/.claude/hooks/statusline.sh",
    "padding": 0,
    "refreshInterval": 4
  }
}
```

Use the `~` path so it works across machines.

### Step 4: Verify

Tell the user to restart Claude Code. They should see the powerline status bar immediately. To trigger the max effort easter egg, run `/effort` and set it to max.

## Requirements

- `jq` — for parsing session JSON (most systems have it; `brew install jq` on macOS)
- `ccstatusline` — optional npm package for git info segment (auto-installed via npx/bunx on first run)
- A terminal that supports 24-bit (truecolor) ANSI — iTerm2, WezTerm, Ghostty, Kitty, Windows Terminal all work

## Customization

Users can customize the quips array, colors, or segment order by editing `~/.claude/hooks/statusline.sh` directly after installation. The script is self-contained with no external dependencies beyond `jq`.
