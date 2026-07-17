#!/usr/bin/env bash
# Capture the current Claude Code session as trace.tar.gz (challenge-format trajectory:
# every tool call + the agent's reasoning). This is the raw source your FEEDBACK_AUDIT.md quotes.
#
# Usage: bash make_trace.sh [SANITY_KEYWORD]
#   SANITY_KEYWORD — optional; a distinctive string from this run (a metric, a term, a CLI version).
#                    The script checks it appears in the captured trajectory so you don't ship the
#                    wrong session.
set -euo pipefail

KW="${1:-}"
REPO="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$REPO"

# Claude Code stores sessions under ~/.claude/projects/<cwd with '/' replaced by '-'>
ENC="$(pwd | sed 's#/#-#g')"
SESS="$HOME/.claude/projects/$ENC"
if [ ! -d "$SESS" ]; then
  echo "session dir not found: $SESS" >&2
  echo "Point --session-dir at your ~/.claude/projects/<encoded-cwd> manually and re-run." >&2
  exit 1
fi

if ! command -v pier >/dev/null 2>&1; then
  echo "pier not found. Install with:" >&2
  echo "  uv tool install \"pier @ git+https://github.com/allenai/pier\"" >&2
  exit 1
fi

echo "== pier capture (session dir: $SESS) =="
pier capture --session-dir "$SESS" -a claude-code

echo "== pier traces -> trace.tar.gz =="
pier traces -o trace.tar.gz
ls -la trace.tar.gz

# Sanity check: confirm the captured trajectory is actually this session.
TRAJ="$(ls -td .pier/trials/*/agent/trajectory.json 2>/dev/null | head -1 || true)"
if [ -n "$TRAJ" ] && [ -n "$KW" ]; then
  n=$(grep -c -- "$KW" "$TRAJ" 2>/dev/null || echo 0)
  echo "sanity: '$KW' appears $n time(s) in the captured trajectory"
  if [ "$n" -eq 0 ]; then
    echo "WARNING: keyword not found — this may be the wrong session. Verify before shipping." >&2
  fi
fi

echo "Done. Commit trace.tar.gz so the audit's quotes are verifiable against the raw source."
