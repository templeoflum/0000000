# Live inventory pilot — 8 September 2026

Status: three entries sampled, not a complete inventory or performance acceptance. No content fixes or moves. Original active clips, layer faders, solo flags and Heart motion settings restored; readbacks stored. Source static settings restored. Quantum Carpets Wave Count remains under its original native Random timeline rather than frozen at a snapshot value.

## Method and limits

Live composition monitor PNG samples at 1920×1080, five baseline frames followed by three frames at each of two settings for three controls: 23 live samples per clip, 69 total. These are timestamped live sequences, not cached thumbnails. They are sparse temporal observations, not 60-FPS video inspection, so no fine-grained smoothness certification. Solo isolates the tested layer; global effect envelope targets were faded to zero; existing clip Transform/AutoMask configuration remains part of the test. Heart motion held, but native source animation may continue. No local LLM ran during measurement. FPS is whole-output telemetry while sampling, not shader-only GPU timing. Telemetry was under one second old.

Parameter ownership was inspected after capture and revealed one confound. Future runs must inspect it BEFORE writes, verify values at every step, and label native animation explicitly. No scale-up until the stricter pilot is checked.

## Observed entries

### L6C40 CloudVortex

Live sequence: full-frame blue cloud/tunnel motion. The radius quarter sample (native 0) largely loses visible tunnel detail into a diffuse blue field; the three-quarter sample (native 2) has a strong bright opening and structured cloud walls. Rate and roto also sampled at −2.5/+2.5 and −0.5/+0.5. These three controls report static ownership. Remaining loops/turbulance not exercised.

Output telemetry: approximately **8–11 FPS** in this run. Saved `loops=200`, its exposed maximum, is a candidate cost contributor, not a proven cause; this needs a controlled loops test. Flag this configuration as a performance concern. Field-like output observed under these conditions; final layer role still for discussion.

### L5C39 Quantum Carpets

Baseline sequence is an evolving colorful central mass with dark surrounding space. At Zoom=3.25 (quarter of exposed range), it expands beyond the image boundaries. This defeats a containment conclusion based on the small cached thumbnail. Zoom=7.75 was also sampled. Source includes a native Random timeline driving Wave Count; its attempted 4.5/9.5 interventions are **confounded**, not validated manual response. Speed=.75/2.25 also sampled, but changing Wave Count means speed attribution needs a controlled repeat.

Output telemetry: approximately **60 FPS**. This is not yet a Figure acceptance: extent changes with zoom, and reliable containment must include the full intended motion domain. No range or shader fix made.

### L5C65 Gradient Bars

Baseline sequence shows full-height grayscale strips with evolving intensity/gradients. Columns=8.75 produces broader strips than Columns=24.25. Speed=.25/.75 and offset=4/12 also sampled. All three tested controls report static ownership. It reaches the frame edges in the sampled states; not a contained Figure in this configuration. Potential field/pattern material, pending discussion and broader control coverage.

Output telemetry: approximately **60 FPS**. This is only one configuration and selected control samples, not a comprehensive performance profile.

## Worker division

- Quality reviewer: independent schema/census and live-method/restoration review.
- Local schema worker: must extract exact controls and distinguish source/effect scope while abstaining from unsupported visual claims. Cloud attempt rejected by automatic approval review; local fallback runs only after live capture, then unloads its own model.
- Root: owns live Resolume operations and reviews sampled rendered output. Workers cannot mutate the shared live instrument in parallel.

## Full inventory gate

The 281-entry current-deck census is structural only. Record every entry as untested, pilot-partial, live-reviewed, blocked, or diagnostic; no silent promotion. Include all decks in the census before claiming composition-wide completeness. Required evidence: exact identity and stack; native ownership; default temporal sample; verified control interventions; source/composite distinction; containment where applicable; dependencies and reset behavior; performance at documented settings; successful restoration. Review every evidence packet, with an independent sample check before growing batches.

Next pilot improvements: ownership preflight, per-step readback, fresh isolation readback, measurement without PNG capture, and a controlled CloudVortex loops study. Keep fixes and reorganization paused until the inventory is ready for discussion.

## Quality-check outcome

Local qwen3:8b returned correct schema content on 12/12 independent checks, but met 13/16 output-contract checks (wrong field name in three records). This is qualified checked extraction only. Its model was unloaded after the call. Independent review accepts the rendered pilot as partial evidence only: composition-monitor images are soloed-layer output, not certified raw shader output; GPU is device-wide and FPS is monitor acquisition during sampling. Native Wave Count interventions invalidated.

Review caught map/level/shell morph durations changing from 3 to 1 second during recovery. These were restored with fresh controller instance checks; final-heart.json and restoration-check.json record the repair. coverage.json explicitly leaves 278 entries not live-reviewed and 3 pilot-partial. No shader, placement or composition content fixes made.
