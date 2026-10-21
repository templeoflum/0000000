# Pilot review

Harness PASS: Claude Code connected to local Ollama heart-audit (qwen3-coder:30b),
completed in 72.8 seconds / 3 turns, without edit/shell/MCP tools. Original and
copied shader hashes match. Model occupied about 25 GB with 64k context and was
unloaded after the task. Future launcher runs automatically unload on exit and
use restricted mode. No persistent Claude configuration was changed.

Content NOT APPROVED for implementation:
- Scale is float (lines 102–109) and continuously sets frequency at line 220;
  calling it discrete or unsafe to animate is incorrect.
- No TIME expression exists. Saying motion depends on both TIME and external
  positions contradicts the actual source.
- Haze and Bands do not establish GPU savings merely by reducing visual detail.
- fract/smoothstep cost claims need profiling; no evidence for the proposed
  bottleneck was provided. Do not turn these guesses into shader edits.
- Lens is a discrete choice; some quoted expressions are correctly extracted.

Next suitable task: structured extraction of INPUTS and exact expressions,
validated mechanically against the source. Escalate interpretation and instrument
range design to reviewed work. One local worker at a time, outside performances.

Claude's result metadata includes generic cost/context labels for this unknown
model. Those are harness estimates, not evidence of paid Anthropic inference or
the actual context allocation; Ollama reported 65536 context.
