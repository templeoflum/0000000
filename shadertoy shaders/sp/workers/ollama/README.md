# Ollama pilot worker

Backend: local qwen3-coder:30b, reused through the heart-audit alias with 64k
context and temperature 0.1. Harness: installed Claude Code, pointed at
127.0.0.1:11434 for this process only. No normal Claude settings are rewritten.

Pilot: read a copy of Ground.fs and audit it against BRIEF.md. Only Read is
available; no shell, edit, network, or Resolume MCP tools. Future launches use
Claude's restricted mode to confine file tools to the pilot directory as well.
Results are suggestions until reviewed against the shader and tested.

Run from the project: zsh sp/workers/ollama/run-audit.sh
Unload afterward: ollama stop heart-audit

Do not run inference during a live VJ performance: it shares the Mac GPU and
memory. Start with one worker at a time. No need to run the 51 GB coding model
for this initial extraction task. The alias reuses existing weights.
