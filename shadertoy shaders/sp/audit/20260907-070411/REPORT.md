# Heart and rendering audit — 7 September 2026

## Measured results

Hardware: Apple M5 Max. Composition: 1920×1080, 8bpc. Arena displayed 60 FPS in the initial UI snapshot. GPU counters below are whole-system activity, not per-shader timings.

| Comparison | Original | Alternative |
|---|---:|---:|
| Delay: median system GPU activity | 51.5% | 38.0% |
| Delay: reported graphics system memory | 11.40 GB | 8.31 GB |
| Hopf: standalone synchronized render | 12.65 ms Full | 8.57 ms Balanced / 6.38 ms Performance |

Delay comparison: motion held, 10-second history warm-up per case, eight GPU samples per case. Original clip and hold state restored. The alternate preserves timing and taps while reducing the long history texture dimensions by half; echoes become softer. The final mix and direct current-frame route retain full resolution. The short RGB delay remains unchanged. Alternative loaded successfully in Arena and its visible output was checked.

Hopf comparisons use the same renderer and resolution but are short independent runs while other applications remain active. Full quality matched the backed-up original image exactly at the checked frame. These are useful screening measurements, not guarantees of Arena performance or exhaustive worst-case tests.

## Live controller

- Stable eight-layer bank in layer-number order, explicit focused target, six featured parameters, full controls in Edit.
- Return home, Undo, Mutate armed and Hold motion remain visible. Space mutates the focused target.
- Variation pads: tap to keep, hold to visit, release to return. Save and name variations in Edit.
- Trackpad gestures capture their target at contact; disconnect/blur releases momentary visits. Pad settings migrate from browser storage to engine-owned surface.json.
- Latest unsent value per parameter, bounded storage, fair dispatch and a common maximum 60 Hz cadence for continuous controls; boolean state changes are immediate.
- Interface snapshots generated at 15 Hz; phase calculation remains 240 Hz. Synchronous effect bypass writes removed from the clock.
- Presets capture semantic slot configuration, global timing and drive state. Overlapping visits use an ordered stack. Range mutation now works within the configured bounds, and Look also respects those bounds.
- Atom writes are debounced and replaced atomically. UI mutation work uses a serial executor.
- Preview capture is demand-driven at 24 Hz if started; no preview process was running during the measured baseline.
- Automatic clip-size matching is now opt-in via --match-sizes so lower-resolution sources can remain lower resolution.

## Available patches

- SP Delay Performance is installed separately. The composition has a nonplaying alternative at layer 4, column 12: figure · light delay. The original delay is playing.
- Hopf fibers Performance is installed separately with Render Quality exposed in Arena. Tested in an empty slot and then removed from that slot; the source remains available.
- Original installed patches remain intact. Source and patch archives are in this audit directory. composition-last-saved.avc is a copy of the last saved composition; composition-before.json captures the live API state. Native Save As was gated by the connector, so these should not be represented as a newly saved copy of all unsaved native state. Arena composition changes remain unsaved.

## Standalone shader catalog

All 38 local SP shader files compiled and rendered. Their installed shader resources matched before changes. Tests use 1920×1080, 12 warm-up frames and 30 measured frames at defaults. Effect inputs are blank in this smoke test; input-dependent performance and artistic behavior need further scene-specific tests. Multi-pass buffers are supported. CPU submission plus synchronized GPU completion is timed, excluding output readback. Arena remains running, so contention can affect results.

| Shader | Median ms | P95 ms |
|---|---:|---:|
| Hopf fibers SP | 11.766 | 13.358 |
| SP Atom Script | 2.366 | 3.275 |
| SP Atom Hybrid | 1.163 | 1.672 |
| SP Atom Void | 1.126 | 1.658 |
| SP Atom 4D | 1.051 | 1.465 |
| SP Atom Glyph | 0.826 | 1.763 |
| SP Field Outdoor | 0.813 | 1.145 |
| SP Figure 3D | 0.698 | 1.251 |
| SP Atom 4D Field | 0.657 | 1.287 |
| SP Figure | 0.641 | 0.984 |
| SP Atom Figure 2D | 0.559 | 2.184 |
| Gentle Rings SP | 0.558 | 0.945 |
| SP Field | 0.533 | 1.220 |
| SP Study Mixer | 0.482 | 2.170 |
| SP Probe | 0.440 | 0.873 |
| SP Loop Shape | 0.439 | 1.250 |
| SP Loop Flow | 0.410 | 1.324 |
| SP Atom Solid | 0.404 | 0.983 |
| SP Study Fold | 0.394 | 1.270 |
| SP Loop | 0.388 | 1.226 |
| SP Field Abstract | 0.382 | 1.121 |
| SP Scan | 0.372 | 1.154 |
| SP Glyphmass | 0.366 | 1.384 |
| SP Loop Color | 0.360 | 1.298 |
| SP Study Texture | 0.355 | 1.763 |
| SP Grain | 0.316 | 1.031 |
| SP Atom Room | 0.307 | 0.869 |
| SP Study Color | 0.303 | 0.900 |
| SP Chain Map | 0.301 | 1.811 |
| SP Chain Level | 0.272 | 1.022 |
| SP Atom Ground | 0.264 | 0.658 |
| SP Atom Line | 0.257 | 0.719 |
| SP Atom Grain | 0.251 | 0.746 |
| SP Atom Dither | 0.244 | 1.441 |
| SP Study Level | 0.236 | 1.272 |
| SP Study Map | 0.234 | 0.557 |
| SP Atom Texture | 0.223 | 1.531 |
| SP Field Indoor | 0.217 | 0.673 |

## Validation and remaining limits

Seven automated tests cover coalescing/fairness, output cadence and terminal value delivery, bounded queue reset, atom state round trips, overlapping preset returns, bounded range mutation/undo, and cancellation of a released quantized effect. Python compilation and JavaScript syntax checks pass. The live UI was checked in performance and edit modes; target selection, state updates and settings persistence were verified.

Engine before/after samples both had a median empty queue under the sampled load. Earlier observed queue pressure was not consistently reproduced, so no large measured engine speedup is claimed. The update removes known scheduling and correctness hazards. Local queue age is not end-to-end Arena latency.

Not yet established: a show-length soak; exhaustive shader parameter combinations; 4K/multiple-output headroom; reconnects across an Arena restart; hard GPU timing for the native Wire delay graph. Presets saved under the old format cannot recover configuration they never captured. The 94 root Shadertoy exports are archival source material and were not included in this 38-shader SP performance catalog.
