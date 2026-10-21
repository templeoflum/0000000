# Full-resolution acquisition samples — September 7

These are 60-second Heart Syphon acquisition samples at 1920×1080. They are not Arena presentation timestamps or a Heart-closed baseline. No local inference ran during sampling. The original native monitor renderer was retained. Playing clip identities stayed unchanged within each sample; motion continued.

| Scene | Median FPS | p95 frame interval | >100 ms intervals | System GPU median |
|---|---:|---:|---:|---:|
| current-map | 60.00 | 17.53 ms | 0 | 50.0% |
| feedback-turn | 60.00 | 17.54 ms | 0 | 51.0% |
| feedback-rgb-delay | 60.00 | 17.52 ms | 0 | 43.0% |
| all-layers-idle | 60.00 | 17.47 ms | 0 | 51.0% |

All samples remained visible with fresh telemetry and 1080p dimensions. These samples meet the proposed acquisition thresholds. Different system-wide GPU medians do not establish the cost of any individual shader/effect; app/background activity and dynamic scenes are confounders. No matched Heart-closed attribution, GPU memory measurement, or complete 20-minute performance acceptance is claimed.

RGB delay was enabled at its existing R=0, G=.15, B=.3 values then returned to zero amount. Idle cleared eight layers, then Feedback performance recall restored all six instruments and their drive counts. Before feedback review remains a saved recovery patch.

The early current-map/feedback-turn rows captured delivery counters but used obsolete names for engine Hz/work fields (null); later rows use the actual fps/worst fields. Acquisition metrics are unaffected.

Ownership observer enabled: an additional 60-second sample held median **59.99 FPS**, p95 acquisition interval **18.28 ms**, zero intervals above 100 ms, fresh visible 1080p throughout; system GPU median **53%**. This bounds observed behavior for this sample, not matched observer overhead or per-process GPU attribution.

## Independent empty-scene display comparison

Saved current state as **Before GPU comparison**, cleared eight layers and confirmed no active clips. Sampled AGX counters directly with `sp/qa/sample_system_gpu.py` (one sample/second, 30 seconds each), independent of monitor telemetry:

| Condition | Median whole-Mac GPU | Range |
|---|---:|---:|
| Heart visible, first | 54% | 0–60% |
| Heart display app closed; engine/Arena running | 48% | 0–58% |
| Heart reopened, detached, second | 65% | 50–68% |

The closed interval was verified by absence of Heart's native process and stopped telemetry timestamps. An attempted Hide shortcut did not hide the custom app (telemetry remained visible); that sample was aborted and excluded. The later reopened window may differ in layout/occlusion, and background apps were not stopped. These are not a precise subtraction-based GPU attribution: visible repeatability was poor, counters occasionally reported zero, and WindowServer/background work remains included. The supported finding is that substantial whole-system load persisted with Heart's display closed and no active clips. The engine remained running but had no drives; local inference was not running. Original six-instrument setup restored successfully afterward. Further isolation must separate Arena's empty render/output pipeline and background/window composition before attributing the remaining load.

Per-process attribution follow-up: installed `powermetrics --help` advertises `--show-process-gpu`. A three-sample, read-only invocation with noninteractive elevation could not run because macOS required administrator authentication. No password was requested or stored, no process was stopped, and no attribution result was produced. This is an OS privilege limitation, separate from Codex approval. Current evidence still cannot assign the remaining GPU load to Arena versus background/window composition.

## Twenty-minute checked-patch action run

`feedback-checked-sustained.json` captures 1,200.07 seconds / 1,201 telemetry samples. `action-exercise.json` records next/previous browsing on all eight layers, checked recalls between groups, Hold/Resume, four feedback behaviors, timing change, factory Home, native output shaping and RGB Delay, reset, reconnect and restoration. A later actual native-window **Start: Feedback checked** button click also reached Ready. Scripted checks passed and restored six instruments/47 drives. This is command-path coverage plus that native Start action, **not** physical trackpad/focus or full cold-launch acceptance.

| Measurement | Overall result |
|---|---:|
| Source dimensions | 1920×1080 throughout |
| Median acquisition FPS | 60.00 |
| Lowest one-second acquisition sample | **39.00 FPS** |
| One-second samples below 55 FPS | **172 / 1,201 (14.3%)** |
| p95 acquired-frame interval | 18.19 ms |
| Acquired intervals above 100 ms | 0 |
| Hidden/stale telemetry samples | 0 / 0 |
| Maximum reported pending-value age | 31.05 ms |
| Maximum pending target count | 52 |
| Whole-Mac GPU median / range | 51% / 0–83% |

The median/frame-gap criteria pass, but **consistent 60 FPS is not established**. Excluding documented recall windows plus two seconds still leaves 161 samples below 55 FPS and a minimum of 39 FPS. Minute 11, after the scripted action exercise, had a median near 50 FPS. Therefore recalls alone do not explain the dips. Shader-state cost versus background/window composition versus monitor acquisition scheduling remains unisolated; system GPU percentages do not prove attribution. The native Start completion timestamp was recorded after tool/UI round trips, so its excluded window is conservative. Overall figures retain all samples and do not rely on exclusion.

The effect-ownership fixes were loaded **after** this 20-minute run, avoiding an engine restart inside the sample. A subsequent 60-second `effect-release-fix.json` sample recorded median 60.00 FPS, p95 interval 32.36 ms, no >100 ms intervals, fresh visible 1080p throughout. This short check does not extend the 20-minute claim to the revised engine build. No downscaling, sleep prevention or local inference was used.
