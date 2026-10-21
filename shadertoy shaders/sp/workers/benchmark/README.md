# Worker benchmark

Two bounded tool calls: read_shader, then submit_audit. Seven mechanically checked
facts: complete input inventory/types, TIME usage, Scale type, continuity,
exact motion expression, exact size expression, and a control-flow cost claim.
This is a supervised extraction/tool-use test, not a general coding benchmark.

Local: existing Ground shader copy; qwen3-coder:30b, gemma4:12b, qwen3:8b.
8K context, 1400 generated-token limit, temperature 0, thinking disabled.
Sequential unloaded runs, then concurrent pair and trio. Models unloaded between
conditions. One trial per condition; filesystem caching/background load may affect
latency. Residency snapshots show overlapping GPU model allocation, not precise
simultaneous GPU-kernel execution. No live shader or composition changes.

Cloud: synthetic.fs was authored specifically for public-cloud testing. No private
Ground source was transmitted. The automatic approval reviewer rejected that
original disclosure, so cloud-synthetic.py is entirely separate and reads only the
synthetic fixture. Existing Hermes credentials/routes, five parallel requests,
1800 generated-token limit. Gemini Flash retried once after HTTP 503.

Tool implementations cannot read arbitrary files, execute commands, edit files,
or access Resolume. Hermes itself and Claude Code are not the harness in these
runs: a small controlled harness isolates model/provider tool-call behavior.

Because fixtures differ, do not compare local and cloud latency as equivalent
workloads. Correctness scores are specific to each fixture. Endpoint tests don't
verify pricing, quotas, long-context reliability, or performance on coding edits.

Files:
- run.py: local benchmark only; unloads models afterward
- cloud-synthetic.py: cloud test only, optional positional alias filter
- local.json, cloud.json, cloud-retry.json: factual results and submitted answers
- residency.json: local GPU memory snapshots
