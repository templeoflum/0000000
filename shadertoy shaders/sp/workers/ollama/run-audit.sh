#!/bin/zsh
set -eu
cd "$(dirname "$0")/pilot"
export ANTHROPIC_BASE_URL=http://127.0.0.1:11434
export ANTHROPIC_AUTH_TOKEN=ollama
export ANTHROPIC_API_KEY=ollama
export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
trap '/usr/local/bin/ollama stop heart-audit >/dev/null 2>&1 || true' EXIT
"$HOME/.local/bin/claude" --bare --restricted --model heart-audit --tools Read --allowedTools Read --strict-mcp-config --mcp-config '{"mcpServers":{}}' --setting-sources '' --no-session-persistence --output-format json -p 'Read BRIEF.md, then read Ground.fs and complete the audit. Read-only task. Return findings with line references.'
