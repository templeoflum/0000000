# Heart worker guide

Updated September 7, 2026. Start here for local/cloud worker setup and evidence.

## Purpose and current status

Heart is the performance instrument for Resolume. Workers help turn imported
shaders into playable instruments with meaningful controls, useful Home settings,
portable parameter relationships, and measured performance.

Working now: local inference through Claude Code; configured cloud endpoint
smoke tests; a small verified tool-use benchmark; local concurrency measurements.
The memory-lattice factory floor, automatic job queue, multi-worker integration,
and general shader-editing workflow are **not implemented yet**. Kimi Desktop and
Claude's subscription-backed CLI have not been integrated as separate workers.

## Recommended starting arrangement

- One **Qwen3-Coder 30B** local worker for bounded, reviewable extraction tasks.
- **Qwen3 8B** as a smaller candidate for the same kind of work.
- Cloud helpers for synthetic/public material or project material explicitly
  authorized for the destination. Start with the verified endpoints below.
- Keep local inference out of live VJ performances: it shares GPU and unified
  memory with Resolume. Unload models when a batch finishes.
- One integration owner reviews results before changes reach Heart or Resolume.

These are starting choices from a tiny test, not general model rankings. A vague
first Qwen audit made several mistakes; the later structured task passed. Clear
work orders and independent checks matter as much as model choice.

## What was verified

| Local model | Solo task | Checks |
|---|---:|---:|
| qwen3-coder:30b | 31.28 s | 7/7 |
| qwen3:8b | 39.01 s | 7/7 |
| gemma4:12b | 56.92 s | 6/7 |

Gemma repeatedly described the declared Scale type as “linear” instead of “float.”
The coder + Gemma pair took 75.83 s versus 88.20 s sequentially. All three together
took 101.59 s versus 127.21 s sequentially, with 33.98 GB peak model GPU allocation.
All three were resident together; this does not establish simultaneous GPU kernel
execution. Batch throughput improved while individual response latency worsened.
Tests used 8K context, one trial per condition, and unloading between conditions.
Background activity and filesystem caches were not controlled.

| Cloud alias | Configured model / provider | Tool-test result |
|---|---|---|
| copilot | gpt-4o-mini-2024-07-18 / Copilot | 7/7, 2.00 s |
| kimik3 | moonshotai/kimi-k3 / OpenRouter | 7/7, 4.19 s |
| gflash | gemini-flash-latest / Gemini | 7/7, 7.90 s on retry after 503 |
| bonsai | prism-ml/Ternary-Bonsai-27B-gguf / Hugging Face | 7/7, 9.12 s |
| g35 | gemini-3.5-flash / Gemini | 7/7, 10.03 s |

The cloud fixture was a newly authored synthetic shader; the local fixture was a
copy of Ground. Do not compare their latency as equal workloads. Both tests
required read_shader followed by submit_audit and checked seven source facts.
The benchmark used a minimal controlled harness, not the full Hermes agent or
Claude Code. General coding, edits, long contexts, and production reliability
remain untested.

Unavailable in the endpoint smoke test: Nous HY3/Fable credentials, Gemini 2.5
model/route, Grok access, NVIDIA authentication, and credits for HF Kimi K2.5 and
DeepInfra. These are test-time statuses, not permanent judgments.

## Setup, commands, and evidence

Run these commands from this project root. They use existing installations and
credentials; do not copy secrets into this project.

| Task | Command / documentation |
|---|---|
| Ollama through Claude Code, read-only pilot | `zsh sp/workers/ollama/run-audit.sh` |
| Local solo/pair/trio benchmark | `~/.hermes/hermes-agent/venv/bin/python sp/workers/benchmark/run.py` |
| Cloud synthetic tool tests | `~/.hermes/hermes-agent/venv/bin/python sp/workers/benchmark/cloud-synthetic.py` |
| Retry a cloud alias | Append its alias, e.g. `gflash`, to the preceding command |
| Configured endpoint smoke tests | `~/.hermes/hermes-agent/venv/bin/python sp/workers/hermes/smoke.py` |
| Inspect loaded local models | `ollama ps` |
| Manually unload a model | `ollama stop MODEL_NAME` |

- [Ollama/Claude setup](sp/workers/ollama/README.md)
- [First pilot review: mistakes caught](sp/workers/ollama/pilot/REVIEW.md)
- [Hermes endpoint results](sp/workers/hermes/README.md)
- [Benchmark method](sp/workers/benchmark/README.md)
- [Measured comparison](sp/workers/benchmark/RESULTS.md)
- Raw evidence: [local](sp/workers/benchmark/local.json),
  [cloud](sp/workers/benchmark/cloud.json),
  [cloud retry](sp/workers/benchmark/cloud-retry.json),
  [residency](sp/workers/benchmark/residency.json).

The Claude pilot uses the local heart-audit alias (Qwen3-Coder 30B, 64K context),
Read-only tools, restricted mode, and no MCP servers. Its environment overrides
apply only to that process. Its launcher unloads the model on exit. The local
benchmark also unloads its models. No permanent Ollama scheduling settings or
normal Claude configuration were changed.

## Work orders and integration

User preference (September 7, 2026): use the tested workers wherever they can
reduce primary-assistant token usage. Default to delegating bounded inventories,
source extraction, comparisons, and first-pass checks to local workers. Use
deterministic scripts for mechanical work. Keep briefs small, reuse saved results,
and request concise evidence with file/line references rather than full transcripts.
The primary assistant owns design decisions, reviews, and integration. Delegate
when the expected savings exceed dispatch and review overhead; do not rerun smoke
tests or duplicate audits without a relevant change or unresolved failure.
This preference does not expand cloud data-sharing authorization or remove the
live-performance GPU constraint above.

A batch should have a brief, isolated source copies, an explicit output contract,
results, checks, and a review decision. Give each worker a bounded role. Do not
allow independent workers to edit the shared engine or live composition together.
Unknown parameters start still; do not invent safe ranges or GPU savings. Validate
claims against source, then rendering/performance evidence where applicable.

The user authorized testing existing Hermes APIs as free-or-unavailable. No credit
purchases, paid fallback, or new subscriptions were authorized or attempted.
Endpoint responses alone do not verify pricing. Automatic approval review blocked
sending private shader code to those endpoints, so only the synthetic fixture was
sent. Obtain explicit destination-specific authorization before cloud project-code
work. Keep tokens, keys, and raw credential-bearing errors out of logs and reports.

Next factory-floor trial: one small shader family, verified input extraction,
reviewed instrument design, isolated implementation, then independent validation
and a single integration handoff. Preserve the original parameter-loop relationship
system; do not rebuild it from guesses or from the old MIDI mappings alone.
