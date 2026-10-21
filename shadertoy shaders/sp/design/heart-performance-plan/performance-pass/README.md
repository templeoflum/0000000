# Heart performance pass — September 8, 2026

Implements the surface and effect-motion stage of the [coherent instrument plan](../COHERENT-INSTRUMENT-PLAN.md). Artistic refinement of the three pilots and library expansion follow.

Follow-up: [Home rests; Open explores](../home-open/README.md) supersedes this pass's animated/full-range Home behavior. Open also enables numeric count drives explicitly.

## Playing it

- Six outer areas: faders, monitor, effects rack, Play, combined Parameters A+B, and clip library. Saved arrangement and pinned references migrate from the earlier surface.
- A/B retain independent targets and independently scrolling two-column grids. Home, shuffle, Undo, speed and Stable/Musical/Irrational stay visible. More exposes the complete relationship catalog, morph time and Set Home. A pinned side stays pinned; Follow effect makes it track rack selection.
- Play keeps tap BPM, tempo, downbeat, all eight bank-scoped previous/random/next rows and selected-source quick tools together. Clip searching and bank selection live separately. The inactive Beatpad placeholder is under Play's additional-tools disclosure.
- Musical position advances independently of motion Hold. Downbeat triggers Arena resync and resets actual Heart drive phases while retaining relationship offsets. This explicit reset can visibly reposition motion. Pending quantized envelopes keep their remaining musical distance; long process pauses are not replayed as hours of beats.
- Numeric effects use the same Slot engine as sources. Effect Home explores continuous controls' full normalized spans; integer counts stay still until explicitly driven. Source Homes retain their existing containment ranges. Native automation keeps ownership until explicit manual editing, Drive or Home. Unadapted source rack entries remain manual.
- Effect values use native units and integer steps. Homes/good values and newly saved patch relationships use scoped semantic identities. New/rebound controls start still. New patch saves include Heart-owned effect controls; old patches remain readable.
- Pulse is separate from smooth on/off: move toward the opposite endpoint, then return to the prior target. Retriggering keeps that baseline; newer manual/latch intent supersedes it. In/Hold/Return times are in Envelope settings. Pulses finish during motion Hold.
- Envelope settings stay within the viewport with a sticky top close button, bottom Close, Escape and outside-click dismissal. The workspace popup omits the duplicate full parameter list already available in A/B; positioning also avoids the docked native monitor where space permits.
- Fader scrolling captures the pointer and sets a lasting level; capture ends after 180 ms without wheel events. Holding selects an absolute vertical level and springs to zero on release using the configured spring time. Esc, focus loss, sleep and disposal release capture; interrupted holds settle immediately. Parameter click-to-lock and existing PAD assignments remain separate.

No usage recorder, audio/beatpad processing or additional video renderer was added.

## Evidence and limits

- **146 Python checks pass**, including effect ownership, units, binding replacement, scoped Home/Undo, pulses, manual takeover and musical phase/tap behavior.
- **21 isolated DOM checks pass** for migration, targeting, controls, stale/missing guards, transport and disposal. Retained in `sp/engine/test_workspace.cjs` with a synthetic fixture.
- Pointer, fader gesture and explicit-resume checks pass. Native build, session/sleep and TV ownership/docking checks pass. Wake alone still does not resume the monitor; no OS sleep/security settings changed.
- Live browser at **1280×720**: all eight Play rows visible, no page overflow, and A/B grids each 155 px high with two columns. Native Heart visually inspected after refresh. Minimum usable row heights bound very small arrangements.
- Follow-up envelope bug: at 1280×720, the full Cloner envelope including Pulse settings fits within the viewport (360×319.5 px). Top close, bottom Close, Escape and outside click each removed the dialog without errors. Syntax, workspace, pointer and fader checks passed after the fix. Native Heart was refreshed; a separate native click-through check was inconclusive while the user continued interacting, so dismissal evidence is from the browser check.
- Cloner End Scale Drive was clicked from B. Native values moved **70.7116–74.6497** during a two-second sample. Original value **74.7114**, range 0–1 and Drive-off state were restored. An early check sampled the settling morph; subsequent readback confirmed restoration. Follow-up code prevents range edits from reviving a just-released drive.
- Live Cloner pulse traveled **1 → 0 → 1**. Focused evidence is in `live-motion.json` and `live-pulse.json`.
- The user continued playing. Existing events confirmed tap-tempo changes reaching Arena/Heart and downbeat resetting the phrase origin. User tempo, clips and effect choices were retained; no earlier composition/patch was recalled over them.
- Native monitor snapshots showed 1920×1080 at approximately 60 acquired FPS. This is not sustained performance acceptance for every shader/stack. Physical gesture feel still needs the user's playing feedback. New full-composition recall with effect motion was not exercised live during this pass.

A bounded Qwen3 8B review used requested CPU inference and was unloaded before live checks. Its manual-override expectations were wrong and rejected; independent tests enforce newer intent. No project code was sent to cloud workers.

## Files and recovery

Main changes: `sp/engine/heart.py`, `transport.py`, `motion.py`, `status.html`, `workspace.js`, `workspace.css`, plus native `Heart.m` and `pointer.js`. Focused tests: `test_performance_motion.py`, `test_workspace.cjs`, `test_fader_gestures.cjs`, and existing monitor checks.

`before/` and before-state JSON files are recovery/reference material, not instructions to overwrite later user edits. Engine reloads used fresh live state; native bundle was rebuilt and refreshed. Resolume was not restarted, recalled or saved over.

Next: refine the three pilots through this surface, then expand in complete batches. Verify a newly saved patch with effect motion at a suitable break in playing. Figure containment remains source-only; downstream effects remain unrestricted.
