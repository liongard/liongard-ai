#!/usr/bin/env bash
# Sync the canonical plugin skills/commands/agents into the repo-root .claude/ mirror.
#
# Source of truth:  plugins/liongard/{skills,commands,agents}
#   (this is what `/plugin install liongard` ships to partners).
# Mirror:           .claude/{skills,commands,agents}
#   (a convenience copy so Claude Code auto-loads skills/commands when you
#    launch it directly inside this repo for development).
#
# Edit skills/commands ONLY under plugins/liongard/. Then run this script to
# refresh the .claude/ mirror. Never hand-edit .claude/skills or .claude/commands.
#
# Usage:
#   bash scripts/sync-plugin-to-claude.sh           # apply
#   bash scripts/sync-plugin-to-claude.sh --check    # verify in sync (CI / pre-commit), no writes

set -euo pipefail
cd "$(dirname "$0")/.."

SRC_SKILLS="plugins/liongard/skills"
SRC_CMDS="plugins/liongard/commands"
SRC_AGENTS="plugins/liongard/agents"
DST_SKILLS=".claude/skills"
DST_CMDS=".claude/commands"
DST_AGENTS=".claude/agents"

check_only=false
[ "${1:-}" = "--check" ] && check_only=true

sync_dir() {
  local src="$1" dst="$2"
  if $check_only; then
    if ! diff -rq "$src" "$dst" >/dev/null 2>&1; then
      echo "OUT OF SYNC: $dst differs from canonical $src"
      echo "  Run: bash scripts/sync-plugin-to-claude.sh"
      return 1
    fi
  else
    mkdir -p "$dst"
    rsync -a --delete "$src/" "$dst/" 2>/dev/null || cp -Rf "$src/." "$dst/"
  fi
}

rc=0
sync_dir "$SRC_SKILLS" "$DST_SKILLS" || rc=1
sync_dir "$SRC_CMDS" "$DST_CMDS" || rc=1
if [ -d "$SRC_AGENTS" ]; then
  sync_dir "$SRC_AGENTS" "$DST_AGENTS" || rc=1
fi

if $check_only; then
  [ $rc -eq 0 ] && echo ".claude/ mirror is in sync with plugins/liongard/ (canonical)."
else
  [ $rc -eq 0 ] && echo "Synced .claude/ mirror from plugins/liongard/ (canonical)."
fi
exit $rc
