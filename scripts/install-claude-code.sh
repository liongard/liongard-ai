#!/usr/bin/env bash
# Install the Liongard MCP server into Claude Code.
#
# Usage:
#   ./scripts/install-claude-code.sh [--scope user|local|project] [--dry-run]
#
# The script prompts for the instance hostname and Access Token, then runs
# `claude mcp add` with the right flags.

set -euo pipefail

SCOPE="user"
DRY_RUN="false"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --scope)
      SCOPE="$2"
      shift 2
      ;;
    --dry-run)
      DRY_RUN="true"
      shift
      ;;
    -h|--help)
      sed -n '2,10p' "$0" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

if ! command -v claude >/dev/null 2>&1; then
  echo "Claude Code is not installed or not on PATH." >&2
  echo "Install it with:  curl -fsSL https://claude.ai/install.sh | sh" >&2
  exit 1
fi

case "$SCOPE" in
  user|local|project) ;;
  *)
    echo "Invalid --scope: $SCOPE (must be user, local, or project)" >&2
    exit 2
    ;;
esac

printf 'Liongard instance hostname (e.g. acme.app.liongard.com): '
read -r INSTANCE

# Allow bare subdomain (e.g. "acme").
if [[ "$INSTANCE" != *"."* ]]; then
  INSTANCE="${INSTANCE}.app.liongard.com"
fi

# Reject anything that looks like a URL.
if [[ "$INSTANCE" == *"://"* || "$INSTANCE" == *"/"* ]]; then
  echo "Enter only the hostname, not a URL." >&2
  exit 2
fi

URL="https://${INSTANCE}/api/mcp"

if claude mcp get liongard >/dev/null 2>&1; then
  printf 'A Liongard MCP server is already registered. Remove and re-add? [y/N] '
  read -r REPLY
  if [[ "$REPLY" =~ ^[Yy]$ ]]; then
    claude mcp remove liongard
  else
    echo "Aborting. Run 'claude mcp remove liongard' manually if you change your mind." >&2
    exit 1
  fi
fi

printf 'Liongard MCP token (<accessKeyId>:<accessKeySecret>): '
stty -echo
read -r TOKEN
stty echo
echo

if [[ ! "$TOKEN" =~ ^lg_mcp_.+:.+$ ]]; then
  echo "Token format looks wrong. Expected <accessKeyId>:<accessKeySecret> starting with lg_mcp_." >&2
  exit 2
fi

if [[ "$DRY_RUN" == "true" ]]; then
  node "$(dirname "$0")/liongard-mcp-config.js" --client claude-code --instance "$INSTANCE" --token "$TOKEN" --scope "$SCOPE" --print
  exit 0
fi

claude mcp add --scope "$SCOPE" --transport http liongard "$URL" \
  --header "Authorization: Bearer ${TOKEN}"

echo
claude mcp list
echo
echo "Done. Launch Claude Code and try: 'List my Liongard environments.'"
