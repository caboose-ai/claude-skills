---
name: maximum-effort-statusline
description: Powerline-style Claude Code status bar with dynamic segments (directory, model, context %, lines +/-, cost, git, usage pace) and a rotating quips easter egg at xhigh/max effort
---

# Maximum Effort Status Line

A powerline-style status bar for Claude Code that shows directory, model, context window usage, lines changed, cost/tokens, git, and usage pace — plus a rotating quips easter egg when you crank effort to xhigh or max.

![Maximum Effort Status Line](https://raw.githubusercontent.com/caboose-ai/claude-skills/main/maximum-effort-statusline/assets/statusline-preview.png)

## What It Does

Adds a colorful, dynamically-sized status line to Claude Code with these segments:

- **📂 Directory** — current working directory with smart truncation (purple)
- **📊 Model** — "Model: Opus 4.6" style display (green)
- **📈 Context Window** — context % of total window, color-coded: teal < 50%, orange 50-79%, red 80%+ (teal/orange/red)
- **✏️ Lines Changed** — green `+N`, red `-N` diff stats for the session (slate)
- **💀 Effort Quips** — rotating one-liners when effort is set to xhigh or max (red) — a fun motivational easter egg
- **💵 Cost/Tokens** — session spend and token count (yellow)
- ** Git** — branch with status indicators: `!` modified, `?` untracked, `+` staged (dark)
- **📊 Usage Pace** — 5h/7d rate limit pace tracking with time-to-reset (dark, conditional)

Segments use powerline-style arrow transitions between colored blocks.

Usage pace tracking inspired by [ericboehs' statusline gist](https://gist.github.com/ericboehs/c4340c6febd1b9848eb1656197bf17ca).

## Installation

When the user asks to install this skill, follow these steps:

### Step 1: Create the status line script

Write this file to `~/.claude/hooks/statusline.sh`:

```bash
#!/usr/bin/env bash

# Maximum Effort Status Line for Claude Code
# Powerline-style status bar with directory, model, cost, git, and usage pace
# Usage pace tracking inspired by https://gist.github.com/ericboehs/c4340c6febd1b9848eb1656197bf17ca

# Read stdin (session context JSON) with timeout
if command -v timeout &> /dev/null; then
  SESSION_DATA=$(timeout 1 cat 2>/dev/null || echo '{}')
else
  SESSION_DATA=$(cat 2>/dev/null || echo '{}')
fi

NOW=$(date +%s)
TERM_WIDTH=${COLUMNS:-$(tput cols 2>/dev/null || echo 80)}

# --- Parse session data ---
if command -v jq &> /dev/null && [[ -n "$SESSION_DATA" ]]; then
  MODEL=$(echo "$SESSION_DATA" | jq -r 'if (.model | type) == "object" then .model.id // .model.display_name // empty elif .model then .model else empty end' 2>/dev/null)
  TOKENS=$(echo "$SESSION_DATA" | jq -r '.context_window.total_input_tokens // .total_input_tokens // empty' 2>/dev/null)
  COST=$(echo "$SESSION_DATA" | jq -r '.cost.total_cost_usd // .total_cost_usd // empty' 2>/dev/null)
  EFFORT=$(echo "$SESSION_DATA" | jq -r '.effort.level // empty' 2>/dev/null)
  CURRENT_DIR=$(echo "$SESSION_DATA" | jq -r '.workspace.current_dir // empty' 2>/dev/null)
  CTX_PCT=$(echo "$SESSION_DATA" | jq -r '.context_window.used_percentage // empty' 2>/dev/null)
  CTX_SIZE=$(echo "$SESSION_DATA" | jq -r '.context_window.context_window_size // empty' 2>/dev/null)
  LINES_ADDED=$(echo "$SESSION_DATA" | jq -r '.cost.total_lines_added // empty' 2>/dev/null)
  LINES_REMOVED=$(echo "$SESSION_DATA" | jq -r '.cost.total_lines_removed // empty' 2>/dev/null)
else
  MODEL=""
  TOKENS=""
  COST=""
  EFFORT=""
  CURRENT_DIR=""
  CTX_PCT=""
  CTX_SIZE=""
  LINES_ADDED=""
  LINES_REMOVED=""
fi

[[ -z "$CURRENT_DIR" ]] && CURRENT_DIR="$PWD"

# --- Directory shortening ---
CWD="$CURRENT_DIR"
HOME_DIR="${HOME}"

if [[ "$CWD" == "$HOME_DIR"* ]]; then
  CWD_SHORT="~${CWD#$HOME_DIR}"
else
  CWD_SHORT="$CWD"
fi

DIR_MAX_WIDTH=$((TERM_WIDTH - 70))
[[ $DIR_MAX_WIDTH -lt 20 ]] && DIR_MAX_WIDTH=20

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

# --- Git info (branch + status indicators) ---
GIT_BRANCH=""
GIT_INDICATORS=""
if [[ -d "$CURRENT_DIR/.git" ]] || git -C "$CURRENT_DIR" rev-parse --git-dir &>/dev/null; then
  GIT_BRANCH=$(git -C "$CURRENT_DIR" branch --show-current 2>/dev/null)
  if [[ -n "$GIT_BRANCH" ]]; then
    [[ ${#GIT_BRANCH} -gt 30 ]] && GIT_BRANCH="${GIT_BRANCH:0:29}…"
    GIT_STATUS=$(git -C "$CURRENT_DIR" status --porcelain 2>/dev/null | head -20)
    if [[ -n "$GIT_STATUS" ]]; then
      echo "$GIT_STATUS" | grep -q '^.[MD]' && GIT_INDICATORS="${GIT_INDICATORS}!"
      echo "$GIT_STATUS" | grep -q '^??' && GIT_INDICATORS="${GIT_INDICATORS}?"
      echo "$GIT_STATUS" | grep -q '^[MADRC]' && GIT_INDICATORS="${GIT_INDICATORS}+"
    fi
  fi
fi

# --- Claude usage pace tracking (5h/7d windows) ---
# Fetches usage in background, reads from cache to avoid blocking
USAGE_TEXT=""
USAGE_CACHE="/tmp/claude-usage-cache"
CACHE_MAX_AGE=120

if [[ -f "$USAGE_CACHE" ]] && [[ $(( NOW - $(stat -f%m "$USAGE_CACHE" 2>/dev/null || echo 0) )) -lt $CACHE_MAX_AGE ]]; then
  CLAUDE_USAGE=$(cat "$USAGE_CACHE")
else
  # Refresh cache in background
  (
    TOKEN=$(security find-generic-password -s "Claude Code-credentials" -w 2>/dev/null | jq -r '.claudeAiOauth.accessToken // empty' 2>/dev/null)
    if [[ -n "$TOKEN" ]]; then
      RESP=$(curl -s --max-time 5 'https://api.anthropic.com/api/oauth/usage' \
        -H "Authorization: Bearer $TOKEN" \
        -H "anthropic-beta: oauth-2025-04-20" \
        -H "Content-Type: application/json" 2>/dev/null)
      FIVE=$(echo "$RESP" | jq -r '.five_hour.utilization // empty' 2>/dev/null | cut -d. -f1)
      SEVEN=$(echo "$RESP" | jq -r '.seven_day.utilization // empty' 2>/dev/null | cut -d. -f1)
      FIVE_RESET=$(echo "$RESP" | jq -r '.five_hour.resets_at // empty' 2>/dev/null)
      SEVEN_RESET=$(echo "$RESP" | jq -r '.seven_day.resets_at // empty' 2>/dev/null)
      if [[ -n "$FIVE" ]] && [[ -n "$SEVEN" ]]; then
        FIVE_EPOCH=$(TZ=UTC date -j -f "%Y-%m-%dT%H:%M:%S" "$(echo "$FIVE_RESET" | cut -d. -f1)" +%s 2>/dev/null || echo "0")
        SEVEN_EPOCH=$(TZ=UTC date -j -f "%Y-%m-%dT%H:%M:%S" "$(echo "$SEVEN_RESET" | cut -d. -f1)" +%s 2>/dev/null || echo "0")
        echo "${FIVE}:${SEVEN}:${FIVE_EPOCH}:${SEVEN_EPOCH}" > "$USAGE_CACHE"
      fi
    fi
  ) &
  [[ -f "$USAGE_CACHE" ]] && CLAUDE_USAGE=$(cat "$USAGE_CACHE")
fi

if [[ -n "$CLAUDE_USAGE" ]]; then
  FIVE_PCT=$(echo "$CLAUDE_USAGE" | cut -d: -f1)
  SEVEN_PCT=$(echo "$CLAUDE_USAGE" | cut -d: -f2)
  FIVE_RESET_EPOCH=$(echo "$CLAUDE_USAGE" | cut -d: -f3)
  SEVEN_RESET_EPOCH=$(echo "$CLAUDE_USAGE" | cut -d: -f4)

  fmt_reset() {
    local reset_epoch=$1
    if [[ -n "$reset_epoch" ]] && [[ "$reset_epoch" -gt 0 ]] 2>/dev/null; then
      local remaining=$(( reset_epoch - NOW ))
      [[ "$remaining" -lt 0 ]] && remaining=0
      if [[ "$remaining" -lt 3600 ]]; then
        echo "$((remaining / 60))m"
      elif [[ "$remaining" -lt 86400 ]]; then
        local h=$((remaining / 3600))
        local m=$(( (remaining % 3600) / 60 ))
        if [[ "$m" -ge 45 ]]; then echo "$(( h + 1 ))h"
        elif [[ "$m" -ge 15 ]]; then echo "${h}.5h"
        else echo "${h}h"; fi
      else
        local d=$((remaining / 86400))
        echo "${d}d"
      fi
    fi
  }

  pace_ahead() {
    local usage=$1 reset_epoch=$2 window_secs=$3
    if [[ "$reset_epoch" -gt 0 ]] 2>/dev/null; then
      local remaining=$(( reset_epoch - NOW ))
      [[ "$remaining" -lt 0 ]] && remaining=0
      local elapsed=$(( window_secs - remaining ))
      [[ "$elapsed" -lt 0 ]] && elapsed=0
      local expected=$(( elapsed * 100 / window_secs ))
      echo $(( usage - expected ))
    else
      echo 0
    fi
  }

  PACE_AHEAD_THRESHOLD=10
  PACE_BEHIND_THRESHOLD=25
  USAGE_ALWAYS_SHOW=80

  # 5h window (18000s)
  if [[ "$FIVE_PCT" -gt 0 ]] 2>/dev/null; then
    FIVE_AHEAD=$(pace_ahead "$FIVE_PCT" "$FIVE_RESET_EPOCH" 18000)
    FIVE_BEHIND=$(( -FIVE_AHEAD ))
    if [[ "$FIVE_AHEAD" -ge "$PACE_AHEAD_THRESHOLD" ]] 2>/dev/null || [[ "$FIVE_BEHIND" -ge "$PACE_BEHIND_THRESHOLD" ]] 2>/dev/null || [[ "$FIVE_PCT" -ge "$USAGE_ALWAYS_SHOW" ]] 2>/dev/null; then
      if [[ "$FIVE_AHEAD" -gt 0 ]] 2>/dev/null; then
        USAGE_TEXT="5h:+${FIVE_AHEAD}%@${FIVE_PCT}%"
      else
        USAGE_TEXT="5h:${FIVE_AHEAD}%"
      fi
      if [[ "$FIVE_PCT" -ge 80 ]] 2>/dev/null; then
        FIVE_RESET_STR=$(fmt_reset "$FIVE_RESET_EPOCH")
        [[ -n "$FIVE_RESET_STR" ]] && USAGE_TEXT="${USAGE_TEXT}↻${FIVE_RESET_STR}"
      fi
    fi
  fi

  # 7d window (604800s)
  if [[ "$SEVEN_PCT" -gt 0 ]] 2>/dev/null; then
    SEVEN_AHEAD=$(pace_ahead "$SEVEN_PCT" "$SEVEN_RESET_EPOCH" 604800)
    SEVEN_BEHIND=$(( -SEVEN_AHEAD ))
    if [[ "$SEVEN_AHEAD" -ge "$PACE_AHEAD_THRESHOLD" ]] 2>/dev/null || [[ "$SEVEN_BEHIND" -ge "$PACE_BEHIND_THRESHOLD" ]] 2>/dev/null || [[ "$SEVEN_PCT" -ge "$USAGE_ALWAYS_SHOW" ]] 2>/dev/null; then
      if [[ "$SEVEN_AHEAD" -gt 0 ]] 2>/dev/null; then
        SEVEN_LABEL="7d:+${SEVEN_AHEAD}%@${SEVEN_PCT}%"
      else
        SEVEN_LABEL="7d:${SEVEN_AHEAD}%"
      fi
      if [[ "$SEVEN_PCT" -ge 80 ]] 2>/dev/null; then
        SEVEN_RESET_STR=$(fmt_reset "$SEVEN_RESET_EPOCH")
        [[ -n "$SEVEN_RESET_STR" ]] && SEVEN_LABEL="${SEVEN_LABEL}↻${SEVEN_RESET_STR}"
      fi
      [[ -n "$USAGE_TEXT" ]] && USAGE_TEXT="${USAGE_TEXT} ${SEVEN_LABEL}" || USAGE_TEXT="${SEVEN_LABEL}"
    fi
  fi
fi

# --- ANSI color codes ---
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
FG_DARK="\033[38;2;35;40;52m"
FG_WHITE="\033[38;2;220;220;220m"
FG_MUTED="\033[38;2;140;145;160m"
FG_WARN="\033[38;2;255;180;80m"
FG_CRIT="\033[38;2;255;100;100m"

# === Build segments ===
SEGMENTS=""

# Directory segment 📂
DIR_SEGMENT="${BOLD}${FG_BLACK}${BG_PURPLE} 📂 ${CWD_SHORT} ${RESET}"
SEGMENTS="${DIR_SEGMENT}"
LAST_BG="${FG_PURPLE}"

# Model segment — "Model: Opus 4.6" style
if [[ -n "$MODEL" ]]; then
  MODEL_CLEAN=$(echo "$MODEL" | sed 's/^[a-z]*\.anthropic\.//; s/^anthropic\.//; s/^claude-//')
  MODEL_FAMILY_LC=$(echo "$MODEL_CLEAN" | sed 's/-.*//')
  MODEL_FAMILY=$(echo "$MODEL_FAMILY_LC" | awk '{print toupper(substr($0,1,1)) substr($0,2)}')
  MODEL_VERSION=$(echo "$MODEL_CLEAN" | sed "s/^${MODEL_FAMILY_LC}-//; s/-v[0-9].*//; s/\[.*//; s/-[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]$//; s/-/./")
  MODEL_DISPLAY="Model: ${MODEL_FAMILY} ${MODEL_VERSION}"

  MODEL_SEGMENT="${LAST_BG}${BG_GREEN}${RESET}${BOLD}${FG_BLACK}${BG_GREEN} 📊 ${MODEL_DISPLAY} ${RESET}"
  SEGMENTS="${SEGMENTS}${MODEL_SEGMENT}"
  LAST_BG="${FG_GREEN}"
fi

# Context window segment 📈
if [[ -n "$CTX_PCT" ]]; then
  if [[ -n "$CTX_SIZE" ]] && [[ "$CTX_SIZE" -gt 0 ]] 2>/dev/null; then
    if [[ "$CTX_SIZE" -ge 1000000 ]]; then
      CTX_SIZE_FMT="$(( CTX_SIZE / 1000000 ))M"
    elif [[ "$CTX_SIZE" -ge 1000 ]]; then
      CTX_SIZE_FMT="$(( CTX_SIZE / 1000 ))k"
    else
      CTX_SIZE_FMT="$CTX_SIZE"
    fi
    CTX_DISPLAY="Ctx: ${CTX_PCT}% of ${CTX_SIZE_FMT}"
  else
    CTX_DISPLAY="Ctx: ${CTX_PCT}%"
  fi

  BG_TEAL="\033[48;2;80;180;180m"
  FG_TEAL="\033[38;2;80;180;180m"
  if [[ "$CTX_PCT" -ge 80 ]] 2>/dev/null; then
    BG_TEAL="\033[48;2;200;40;40m"
    FG_TEAL="\033[38;2;200;40;40m"
  elif [[ "$CTX_PCT" -ge 50 ]] 2>/dev/null; then
    BG_TEAL="\033[48;2;255;180;80m"
    FG_TEAL="\033[38;2;255;180;80m"
  fi

  CTX_SEGMENT="${LAST_BG}${BG_TEAL}${RESET}${BOLD}${FG_BLACK}${BG_TEAL} 📈 ${CTX_DISPLAY} ${RESET}"
  SEGMENTS="${SEGMENTS}${CTX_SEGMENT}"
  LAST_BG="${FG_TEAL}"
fi

# Lines changed segment ✏️
if [[ -n "$LINES_ADDED" ]] || [[ -n "$LINES_REMOVED" ]]; then
  LINES_ADDED=${LINES_ADDED:-0}
  LINES_REMOVED=${LINES_REMOVED:-0}
  if [[ "$LINES_ADDED" -gt 0 ]] 2>/dev/null || [[ "$LINES_REMOVED" -gt 0 ]] 2>/dev/null; then
    BG_SLATE="\033[48;2;70;80;100m"
    FG_SLATE="\033[38;2;70;80;100m"
    FG_DIFF_ADD="\033[38;2;120;220;120m"
    FG_DIFF_DEL="\033[38;2;255;120;120m"

    DIFF_SEGMENT="${LAST_BG}${BG_SLATE}${RESET}${BOLD}${BG_SLATE} ${FG_DIFF_ADD}+${LINES_ADDED}${FG_WHITE},${FG_DIFF_DEL}-${LINES_REMOVED}${RESET}${BG_SLATE} ${RESET}"
    SEGMENTS="${SEGMENTS}${DIFF_SEGMENT}"
    LAST_BG="${FG_SLATE}"
  fi
fi

# Maximum effort quips easter egg 💀
STATUSLINE_CONFIG="$HOME/.claude/hooks/statusline-config.json"
SHOW_QUIPS=$(jq -r '.showQuips // true' "$STATUSLINE_CONFIG" 2>/dev/null || echo "true")
QUIP_ROTATE=$(jq -r '.quipRotateSeconds // 30' "$STATUSLINE_CONFIG" 2>/dev/null || echo "30")
QUIP_TRIGGERS=$(jq -r '.quipTriggers // ["xhigh","max"] | .[]' "$STATUSLINE_CONFIG" 2>/dev/null || echo -e "xhigh\nmax")

EFFORT_SETTING=$(jq -r '.effortLevel // empty' ~/.claude/settings.json 2>/dev/null)
QUIP_MATCH=false
while IFS= read -r trigger; do
  [[ "$EFFORT_SETTING" == "$trigger" || "$EFFORT" == "$trigger" ]] && QUIP_MATCH=true
done <<< "$QUIP_TRIGGERS"

if [[ "$SHOW_QUIPS" == "true" ]] && [[ "$QUIP_MATCH" == "true" ]]; then
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
  if [[ "$QUIP_ROTATE" -gt 0 ]] 2>/dev/null; then
    QUIP_IDX=$(( $(date +%s) / QUIP_ROTATE % ${#QUIPS[@]} ))
  else
    QUIP_IDX=$(( RANDOM % ${#QUIPS[@]} ))
  fi
  QUIP="${QUIPS[$QUIP_IDX]}"

  BG_RED="\033[48;2;200;40;40m"
  FG_RED="\033[38;2;200;40;40m"

  DP_SEGMENT="${LAST_BG}${BG_RED}${RESET}${BOLD}\033[38;2;255;255;255m${BG_RED} 💀 ${QUIP} ${RESET}"
  SEGMENTS="${SEGMENTS}${DP_SEGMENT}"
  LAST_BG="${FG_RED}"
fi

# Cost/tokens segment 💵
if [[ -n "$COST" ]] || [[ -n "$TOKENS" ]]; then
  COST_TEXT=""

  if [[ -n "$COST" ]]; then
    COST_FORMATTED=$(printf "%.2f" "$COST" 2>/dev/null || echo "$COST")
    COST_TEXT="\$${COST_FORMATTED}"
  fi

  if [[ -n "$TOKENS" ]]; then
    if [[ $TOKENS -gt 1000000 ]]; then
      TOKENS_FMT=$(awk "BEGIN {printf \"%.1fM\", $TOKENS/1000000}" 2>/dev/null)
    elif [[ $TOKENS -gt 1000 ]]; then
      TOKENS_FMT=$(awk "BEGIN {printf \"%.0fk\", $TOKENS/1000}" 2>/dev/null || echo "${TOKENS}k")
    else
      TOKENS_FMT="${TOKENS}"
    fi
    COST_TEXT="${COST_TEXT:+$COST_TEXT }${TOKENS_FMT}"
  fi

  COST_SEGMENT="${LAST_BG}${BG_YELLOW}${RESET}${BOLD}${FG_BLACK}${BG_YELLOW} 💵 ${COST_TEXT} ${RESET}"
  SEGMENTS="${SEGMENTS}${COST_SEGMENT}"
  LAST_BG="${FG_YELLOW}"
fi

# Git segment (branch + status indicators)
if [[ -n "$GIT_BRANCH" ]]; then
  GIT_TEXT=" ${GIT_BRANCH}"
  if [[ -n "$GIT_INDICATORS" ]]; then
    GIT_TEXT="${GIT_TEXT} [${GIT_INDICATORS}]"
  fi

  GIT_SEGMENT="${LAST_BG}${BG_DARK}${RESET}${BOLD}${FG_WHITE}${BG_DARK}${GIT_TEXT} ${RESET}"
  SEGMENTS="${SEGMENTS}${GIT_SEGMENT}"
  LAST_BG="${FG_DARK}"
fi

# Usage pace segment (only shows when pace is notable)
if [[ -n "$USAGE_TEXT" ]]; then
  # Color based on severity
  if echo "$USAGE_TEXT" | grep -qE '\+[2-9][0-9]%|↻'; then
    USAGE_FG="${FG_CRIT}"
  elif echo "$USAGE_TEXT" | grep -qE '\+[1-9]'; then
    USAGE_FG="${FG_WARN}"
  else
    USAGE_FG="${FG_MUTED}"
  fi

  if [[ "$LAST_BG" == "$FG_DARK" ]]; then
    USAGE_SEGMENT="${USAGE_FG}${BG_DARK} 📊 ${USAGE_TEXT} ${RESET}"
  else
    USAGE_SEGMENT="${LAST_BG}${BG_DARK}${RESET}${USAGE_FG}${BG_DARK} 📊 ${USAGE_TEXT} ${RESET}"
  fi
  SEGMENTS="${SEGMENTS}${USAGE_SEGMENT}"
  LAST_BG="${FG_DARK}"
fi

# Final transition
SEGMENTS="${SEGMENTS}${LAST_BG}${RESET}"

echo -e "${SEGMENTS}"
```

### Step 2: Create the config file

Write this file to `~/.claude/hooks/statusline-config.json`:

```json
{
  "quipTriggers": ["xhigh", "max"],
  "quipRotateSeconds": 30,
  "showQuips": true
}
```

| Option | Default | Description |
|--------|---------|-------------|
| `quipTriggers` | `["xhigh", "max"]` | Effort levels that activate the quips segment. Matches against `effortLevel` in settings.json and the session's `effort.level`. |
| `quipRotateSeconds` | `30` | Seconds between quip rotation. Set to `0` to pick a random quip per refresh instead of cycling. |
| `showQuips` | `true` | Set to `false` to disable the quips segment entirely. |

### Step 3: Make it executable

Run: `chmod +x ~/.claude/hooks/statusline.sh`

### Step 4: Configure Claude Code settings

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

### Step 5: Verify

Tell the user to restart Claude Code. They should see the powerline status bar immediately. To trigger the effort quips easter egg, set `effortLevel` to `"xhigh"` in `~/.claude/settings.json`, or run `/effort` and set it to max.

## Requirements

- `jq` — for parsing session JSON (most systems have it; `brew install jq` on macOS)
- A terminal that supports 24-bit (truecolor) ANSI — iTerm2, WezTerm, Ghostty, Kitty, Windows Terminal all work

## Customization

- **Quip behavior** — edit `~/.claude/hooks/statusline-config.json` to control triggers, rotation speed, and visibility
- **Colors, segments, quip text** — edit `~/.claude/hooks/statusline.sh` directly

## Credits

Usage pace tracking inspired by [ericboehs' statusline gist](https://gist.github.com/ericboehs/c4340c6febd1b9848eb1656197bf17ca).
