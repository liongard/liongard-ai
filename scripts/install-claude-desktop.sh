#!/usr/bin/env bash
# Install the Liongard MCP server into Claude Desktop.
#
# Usage:
#   ./scripts/install-claude-desktop.sh [--dry-run] [--no-backup]

set -euo pipefail

ARGS=(--client claude-desktop --write --backup)

while [[ $# -gt 0 ]]; do
  case "$1" in
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
      sed -n '2,7p' "$0" | sed 's/^# \{0,1\}//'
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
echo "Fully quit and relaunch Claude Desktop."
