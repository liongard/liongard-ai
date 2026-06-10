#!/usr/bin/env bash
# Install the Liongard MCP server into Cursor.
#
# Usage:
#   ./scripts/install-cursor.sh [--project] [--dry-run] [--no-backup]

set -euo pipefail

ARGS=(--client cursor --write --backup)

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project)
      ARGS+=(--project)
      shift
      ;;
    --dry-run)
      ARGS+=(--dry-run)
      shift
      ;;
    --no-backup)
      NEXT_ARGS=()
      for item in "${ARGS[@]}"; do
        [[ "$item" == "--backup" ]] || NEXT_ARGS+=("$item")
      done
      ARGS=("${NEXT_ARGS[@]}")
      shift
      ;;
    -h|--help)
      sed -n '2,8p' "$0" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    *)
      ARGS+=("$1")
      shift
      ;;
  esac
done

node "$(dirname "$0")/liongard-mcp-config.js" "${ARGS[@]}"

echo
echo "Open Cursor and reconnect the server in Settings -> MCP (or restart Cursor)."
