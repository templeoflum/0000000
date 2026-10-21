# Pixel Melt timeout review

Reviewed `sp/show-day/integration/rehearsal/` offline. **No concrete source-derived reason establishes that FX_AREA=2, DENSITY=.99, TIMESTRETCH=.2, MOSHLINES=1 or FADETIME=1 caused the timeout.** Readable MTK_PXLMELT implementation remains unavailable in the locations inspected for EXPECTED-TEMPORAL.md. Inferring GPU loop counts, history allocation, seconds or computational cost from these labels would be speculative.

## Concrete findings

- All five values are within the native min/max recorded in rehearsal `results.json`; each is at its exposed maximum (allowing native float precision). That makes them a potentially aggressive visual pose, but **does not establish an invalid setting or expensive execution path**.
- Deterministic comparison found **zero differences in every non-opacity parameter value** between this rehearsal baseline and both September 8 `effects-live-20260908/final-three/results.json` and `trigger-and-effects-20260908/guard-pass/results.json`. Those earlier runs saved full-mix Pixel Melt readback and output samples at this same pose. Therefore the pose alone is not evidence of a repeatable failure under every input.
- `before-native.json` already shows Pixel Melt opacity=1, bypass=false; `before-heart.json` likewise has env=target=1. The script then Settles before its successful baseline. This was a re-enable following Settle and source/input change, not demonstrably the first time the plugin was enabled in this session.
- Only the baseline record and eight baseline PNGs are present in the inspected run. No successful full-mix readback was persisted between IN and the first timed-out image request. The root reports the 10-second timeout. Thus evidence localizes the failure to **snapshot capture after IN**, not to a proven renderer crash or specific shader instruction.
- The trigger line occurs after the complete `melt-before-trigger` capture. It was not reached in this reported failure. A bad MELT_TRIGGER event cannot explain this particular timeout.
- Attack/release are .05 seconds and quant=0 in before/after Heart snapshots. The one-second pre-capture wait exceeds the configured attack; a deliberately long envelope is not indicated by this saved config.
- Cleanup evidence agrees with root: `after-native.json` has Pixel Melt opacity=0, bypass=true; Heart env=target=0 and connected=true. The ~230 fps Heart value is engine loop cadence, **not native renderer FPS** and cannot establish GPU health.

## Recommendation for root

Continue RGB separately with Pixel Melt parked. Classify Pixel Melt as **unverified; monitor snapshot timed out after re-enable on moving Capsule input, before trigger**. Do not call this a confirmed parameter bug, plugin crash or trigger failure. No settings patch is justified by this evidence.

If root later elects one bounded diagnostic, prioritize separating the snapshot endpoint from native rendering: observe whether the visible native monitor continues moving and whether a fresh composition GET remains responsive during the same event. The existing failure captures neither contemporaneous renderer status nor a successful post-IN native parameter snapshot. A retry should retain normal termination and save readback before requesting the image. Only if the issue reproduces should a one-control-at-a-time comparison at equal input/resolution be considered; there is no source-backed priority among these five values. Do not blindly reduce all five and attribute improvement to one.

No live controls, rendering, shared writes or new patch were performed for this review.
