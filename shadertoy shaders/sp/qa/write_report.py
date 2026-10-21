from pathlib import Path
import json,statistics
root=Path(__file__).resolve().parents[1];audit=root/'audit/20260907-070411'
rows=json.loads((audit/'library/catalog.json').read_text())
lines=['# Heart and rendering audit — 7 September 2026','','## Measured results','',
'Hardware: Apple M5 Max. Composition: 1920×1080, 8bpc. Arena displayed 60 FPS in the initial UI snapshot. GPU counters below are whole-system activity, not per-shader timings.','',
'| Comparison | Original | Alternative |','|---|---:|---:|',
'| Delay: median system GPU activity | 51.5% | 38.0% |',
'| Delay: reported graphics system memory | 11.40 GB | 8.31 GB |',
'| Hopf: standalone synchronized render | 12.65 ms Full | 8.57 ms Balanced / 6.38 ms Performance |','',
'Delay comparison: motion held, 10-second history warm-up per case, eight GPU samples per case. Original clip and hold state restored. The alternate preserves timing and taps while reducing the long history texture dimensions by half; echoes become softer. The final mix and direct current-frame route retain full resolution. The short RGB delay remains unchanged. Alternative loaded successfully in Arena and its visible output was checked.','',
'Hopf comparisons use the same renderer and resolution but are short independent runs while other applications remain active. Full quality matched the backed-up original image exactly at the checked frame. These are useful screening measurements, not guarantees of Arena performance or exhaustive worst-case tests.','',
'## Live controller','',
'- Stable eight-layer bank in layer-number order, explicit focused target, six featured parameters, full controls in Edit.',
'- Return home, Undo, Mutate armed and Hold motion remain visible. Space mutates the focused target.',
'- Variation pads: tap to keep, hold to visit, release to return. Save and name variations in Edit.',
'- Trackpad gestures capture their target at contact; disconnect/blur releases momentary visits. Pad settings migrate from browser storage to engine-owned surface.json.',
'- Latest unsent value per parameter, bounded storage, fair dispatch and a common maximum 60 Hz cadence for continuous controls; boolean state changes are immediate.',
'- Interface snapshots generated at 15 Hz; phase calculation remains 240 Hz. Synchronous effect bypass writes removed from the clock.',
'- Presets capture semantic slot configuration, global timing and drive state. Overlapping visits use an ordered stack. Range mutation now works within the configured bounds, and Look also respects those bounds.',
'- Atom writes are debounced and replaced atomically. UI mutation work uses a serial executor.',
'- Preview capture is demand-driven at 24 Hz if started; no preview process was running during the measured baseline.',
'- Automatic clip-size matching is now opt-in via --match-sizes so lower-resolution sources can remain lower resolution.','',
'## Available patches','',
'- SP Delay Performance is installed separately. The composition has a nonplaying alternative at layer 4, column 12: figure · light delay. The original delay is playing.',
'- Hopf fibers Performance is installed separately with Render Quality exposed in Arena. Tested in an empty slot and then removed from that slot; the source remains available.',
'- Original installed patches remain intact. Source and patch archives are in this audit directory. composition-last-saved.avc is a copy of the last saved composition; composition-before.json captures the live API state. Native Save As was gated by the connector, so these should not be represented as a newly saved copy of all unsaved native state. Arena composition changes remain unsaved.','',
'## Standalone shader catalog','',
'All 38 local SP shader files compiled and rendered. Their installed shader resources matched before changes. Tests use 1920×1080, 12 warm-up frames and 30 measured frames at defaults. Effect inputs are blank in this smoke test; input-dependent performance and artistic behavior need further scene-specific tests. Multi-pass buffers are supported. CPU submission plus synchronized GPU completion is timed, excluding output readback. Arena remains running, so contention can affect results.','',
'| Shader | Median ms | P95 ms |','|---|---:|---:|']
for r in sorted(rows,key=lambda x:x.get('median_ms',0),reverse=True):lines.append(f"| {Path(r['shader']).stem} | {r.get('median_ms',0):.3f} | {r.get('p95_ms',0):.3f} |")
lines += ['', '## Validation and remaining limits','',
'Seven automated tests cover coalescing/fairness, output cadence and terminal value delivery, bounded queue reset, atom state round trips, overlapping preset returns, bounded range mutation/undo, and cancellation of a released quantized effect. Python compilation and JavaScript syntax checks pass. The live UI was checked in performance and edit modes; target selection, state updates and settings persistence were verified.','',
'Engine before/after samples both had a median empty queue under the sampled load. Earlier observed queue pressure was not consistently reproduced, so no large measured engine speedup is claimed. The update removes known scheduling and correctness hazards. Local queue age is not end-to-end Arena latency.','',
'Not yet established: a show-length soak; exhaustive shader parameter combinations; 4K/multiple-output headroom; reconnects across an Arena restart; hard GPU timing for the native Wire delay graph. Presets saved under the old format cannot recover configuration they never captured. The 94 root Shadertoy exports are archival source material and were not included in this 38-shader SP performance catalog.','']
(audit/'REPORT.md').write_text('\n'.join(lines))
(root/'PERFORMANCE.md').write_text('''# Heart performance controller

Open http://localhost:8765 while the heart is running. Launch with `sp/start.sh` as before.

Select a layer by its name. The central panel follows that layer; changing focus does not launch a clip. Clip buttons below the bank launch alternatives on the selected layer. Edit exposes all shader parameters, routing assignments and shuffle targeting.

- Click a parameter name to toggle its drive. Scrub its value as before.
- Mutate armed / Space changes only the focused clip's armed, unlocked controls.
- Hold motion pauses the heart clock; effect fades and in-progress morphs can continue.
- Return home and Undo use that focused clip.
- Variation pads: tap to recall and keep; hold to visit, release to return. Overlapping visits return to the last still-held variation, then to the pre-visit state.
- In Edit, enter a variation name, click Save variation, then tap its destination pad.
- L grabs the trackpad faders; F grabs variations; Escape releases it.

The original delay stays available. Try “figure · light delay” on layer 4 for smaller history textures and softer echoes. “Hopf fibers Performance” is a separate source with Full, Balanced and Performance quality choices. Full preserves the original.

Audit and measurements: [REPORT.md](audit/20260907-070411/REPORT.md).

Backups: workspace-before.tar.gz, installed-patches-before.tar.gz, composition-last-saved.avc and composition-before.json in the audit directory. The composition has not been saved over the original.
''')
print(audit/'REPORT.md')
