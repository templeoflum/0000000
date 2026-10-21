# Hermes configured-provider smoke test

Tested existing credentials and routing through Hermes's provider resolver, then
sent a tiny direct inference request: reply exactly HEART_OK. No project data,
file tools, shell tools, fallback routing, or live Resolume access were sent.
This verifies endpoint inference only, not Hermes agent/tool reliability or cost.
The user authorized these configured endpoints as free-or-unavailable; no credit
purchases or paid fallbacks were attempted.

Passed:
- gflash: gemini-flash-latest (2.32 s)
- g35: gemini-3.5-flash (1.23 s on 256-token retry)
- bonsai: HF prism-ml/Ternary-Bonsai-27B-gguf (6.07 s on 256-token retry)
- kimik3: OpenRouter moonshotai/kimi-k3 (3.68 s)
- copilot: discovered gpt-4o-mini-2024-07-18 (1.14 s)

Unavailable in this test:
- hy3 and fable5 through Nous: credential resolution failed
- g25: model/route 404
- kimik2 through Hugging Face and DeepInfra Llama 3.3: credit/payment required
- grok: access denied
- NVIDIA discovered yi-large: authentication rejected

The first pass allowed 64 output tokens; two incomplete responses passed when
retried at 256. Thinking models may need room before their visible answer.

smoke-results.json and smoke-retry.json contain sanitized results. smoke.py reads
credentials in memory and never includes credentials or raw errors in reports.
Use the installed Hermes venv to execute it. A positional alias list restricts a
retry. Model discovery for providers without configured aliases chooses a text
model, not a benchmark recommendation. Latency includes request overhead and
is not a throughput comparison. No model quality conclusions from this test.
