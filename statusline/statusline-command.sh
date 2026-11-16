#!/bin/bash
input=$(cat)

cwd=$(echo "$input"        | jq -r '.workspace.current_dir // .cwd')
model=$(echo "$input"      | jq -r '.model.display_name // "unknown"')
ctx=$(echo "$input"        | jq -r '.context_window.used_percentage // 0')
ctx_size_raw=$(echo "$input" | jq -r '.context_window.context_window_size // 0')
fiveh=$(echo "$input"      | jq -r '.rate_limits.five_hour.used_percentage // 0')
sevenday=$(echo "$input"   | jq -r '.rate_limits.seven_day.used_percentage // 0')
effort=$(echo "$input"     | jq -r '.effort.level // "?"')
thinking=$(echo "$input"   | jq -r '.thinking.enabled // false')

# colors
RESET=$'\033[00m'
GREEN=$'\033[01;32m'
BLUE=$'\033[01;34m'
CYAN=$'\033[01;36m'
YELLOW=$'\033[01;33m'
DIM=$'\033[02m'
RED=$'\033[01;31m'
MAGENTA=$'\033[01;35m'

# ---------------------------------------------------------------------------
# Starship-like left segment (everything before the model name)
#   directory : bold cyan, ~ for $HOME, last 3 components with …/ prefix
#   git branch: "on " prefix (default color) + bold purple branch (matches [git_branch] format = "on [$branch]($style)")
#   git status: bold red, [flags] -> ? untracked, ! modified, + staged, > ahead, < behind
# ---------------------------------------------------------------------------

# directory (starship [directory], truncation_length = 3)
home_dir="${cwd/#$HOME/\~}"
IFS='/' read -ra _parts <<< "$home_dir"
clean=()
for p in "${_parts[@]}"; do [ -n "$p" ] && clean+=("$p"); done
n=${#clean[@]}
if [ "$n" -gt 3 ]; then
  dir_display="…/${clean[n-3]}/${clean[n-2]}/${clean[n-1]}"
elif [[ "$home_dir" == /* ]]; then
  dir_display="/$(IFS=/; echo "${clean[*]}")"
else
  dir_display="$(IFS=/; echo "${clean[*]}")"
fi

# git branch + status (single porcelain call)
git_segment=""
if status_out=$(git -C "$cwd" status --porcelain=v1 -b 2>/dev/null); then
  branch=""
  flags=""
  while IFS= read -r line; do
    case "$line" in
      "## "*)
        rest="${line#\#\# }"
        branch="${rest%%...*}"          # strip upstream tracking info
        branch="${branch%% *}"          # strip "[ahead/behind]" when no upstream
        case "$line" in *"ahead "*)  flags+=">" ;; esac
        case "$line" in *"behind "*) flags+="<" ;; esac
        ;;
      "??"*) [[ "$flags" == *"?"* ]] || flags+="?" ;;
      *)
        idx="${line:0:1}"   # staged (index)
        wt="${line:1:1}"    # worktree
        case "$idx" in [MADRC]) [[ "$flags" == *"+"* ]] || flags+="+" ;; esac
        case "$wt"  in [MD])    [[ "$flags" == *"!"* ]] || flags+="!" ;; esac
        ;;
    esac
  done <<< "$status_out"

  [ "$branch" = "HEAD" ] && branch=$(git -C "$cwd" rev-parse --short HEAD 2>/dev/null)
  git_segment="  on ${MAGENTA}${branch}${RESET}"
  [ -n "$flags" ] && git_segment+=" ${RED}[${flags}]${RESET}"
fi

prefix="${CYAN}${dir_display}${RESET}${git_segment}"

# ---------------------------------------------------------------------------
# Model, effort, context and rate limits
# ---------------------------------------------------------------------------

# format context window size
if   [ "$ctx_size_raw" -ge 1000000 ]; then ctx_size="$(( ctx_size_raw / 1000000 ))m"
elif [ "$ctx_size_raw" -ge 1000 ];    then ctx_size="$(( ctx_size_raw / 1000 ))k"
else                                       ctx_size="$ctx_size_raw"
fi

# thinking indicator
if [ "$thinking" = "true" ]; then
  think_icon="${YELLOW}●${RESET}"
else
  think_icon="${DIM}○${RESET}"
fi

# color context usage
if   [ "$ctx" -ge 80 ]; then ctx_color="$RED"
elif [ "$ctx" -ge 50 ]; then ctx_color="$YELLOW"
else                          ctx_color="$GREEN"
fi

# color 5h rate limit
if   [ "$fiveh" -ge 80 ]; then fiveh_color="$RED"
elif [ "$fiveh" -ge 50 ]; then fiveh_color="$YELLOW"
else                           fiveh_color="$GREEN"
fi

# color 7d rate limit
if   [ "$sevenday" -ge 80 ]; then sevenday_color="$RED"
elif [ "$sevenday" -ge 50 ]; then sevenday_color="$YELLOW"
else                              sevenday_color="$GREEN"
fi

# Session tokens: sum usage over transcript, deduped by message id because one
# API response is written to the transcript as several lines with the same usage.
# Cache reads are excluded; they re-count the whole context on every turn.
# Counted from the last /compact: the transcript keeps a compact_boundary line there.
transcript=$(echo "$input" | jq -r '.transcript_path // empty')
tok_since=0
if [ -n "$transcript" ] && [ -f "$transcript" ]; then
  tok_since=$(jq -s '
    ((to_entries | map(select(.value.type == "system" and .value.subtype == "compact_boundary") | .key) | last) // -1) as $b
    | .[$b + 1:]
    | map(select(.message.usage != null and .message.id != null))
    | unique_by(.message.id)
    | map(.message.usage | (.input_tokens // 0) + (.output_tokens // 0) + (.cache_creation_input_tokens // 0))
    | add // 0' "$transcript" 2>/dev/null)
  [[ "$tok_since" =~ ^[0-9]+$ ]] || tok_since=0
fi
tok_k=$(awk -v t="$tok_since" 'BEGIN { printf "%.1fk", t/1000 }')

# Logged-in account: Claude Code stores it in ~/.claude.json; reading it avoids
# spawning `claude auth status` on every status line refresh.
user=$(jq -r '.oauthAccount.emailAddress // .oauthAccount.displayName // empty' "$HOME/.claude.json" 2>/dev/null)
[ -z "$user" ] && user="not logged in"

printf "%s  ${CYAN}%s %s${RESET}  %s ${DIM}%s${RESET}  ctx:${ctx_color}%s%%${RESET}  5h:${fiveh_color}%s%%${RESET}  7d:${sevenday_color}%s%%${RESET}  ${DIM}%s tok${RESET}  ${DIM}%s${RESET}" \
  "$prefix" \
  "$model" "$ctx_size" "$think_icon" "$effort" \
  "$ctx" "$fiveh" "$sevenday" "$tok_k" \
  "$user"
