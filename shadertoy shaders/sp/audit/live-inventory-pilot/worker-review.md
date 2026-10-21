# Parameter-schema worker pilot

Local qwen3:8b completed this pilot after live capture and GPU measurements ended:
**12/12 independent content checks; 13/16 output-contract checks**. One inference
call took 7.28 seconds including setup and unload, using 471 prompt tokens and 455
completion tokens as reported by Ollama. Do not reuse the earlier synthetic
benchmark's success as evidence for this pilot.

All source labels, effect labels/scopes, counts, and visual abstentions were exact.
The worker used `exact_source_controls` instead of requested `source_controls` on
all three records. This is a response-contract failure requiring normalization
or a stricter output schema before automated consumption; no parameter names were
wrong. All inference lists were empty, which the "at most two" instruction permits.
The initial grader incorrectly penalized empty lists; the result preserves that
initial score and explains the correction. No extra inference call was made.

Capability demonstrated is bounded schema extraction and abstention only. No
rendered behavior, visual family, performance, live suitability, ranges, or types
were established. No names or thumbnails were available for classification.

Prepared one bounded extraction prompt using opaque fixture IDs, source control
labels, effect control labels, and counts. Clip names, composition names, paths,
thumbnails, shader source, live values, and live access are excluded.

Fixture mapping (local review only):
- fixture-1: L6C40 CloudVortex — 5 source labels; numeric count 5.
- fixture-2: L5C39 Quantum Carpets — 4 source labels; numeric count 4.
- fixture-3: L5C65 Gradient Bars — 11 source labels; numeric count 10.

The last count difference is not proof of a defect: the listing can include
controls that are not numeric. Types are not supplied by this inventory.

Independent grading has 16 checks: record count, then exact source extraction,
exact effect scope, counts, explicit observation abstention, and grounded/labeled
inference candidates for each fixture. A passing extraction score would establish
only these bounded skills, not visual classification or reliable live settings.

Execution attempts:
- Existing Copilot route: credential resolver returned sanitized `AuthError`.
- Existing Gemini Flash route in the sandbox: sanitized `ConnectionError`.
- Network escalation: automatic approval review rejected sending the sanitized
  nonpublic metadata to Gemini because it did not find explicit user authorization
  for that payload and destination. No alternate provider was used to bypass this.

No raw errors or credentials are recorded. The local model was not loaded before
the run; the harness unloaded only qwen3:8b afterward and received a successful
Ollama response. No live Resolume access or changes were attempted. No paid
fallback or purchase was attempted.

No cloud retry or approval request is needed for this completed local pilot.
Any future cloud attempt must first resolve the recorded authorization rejection.
