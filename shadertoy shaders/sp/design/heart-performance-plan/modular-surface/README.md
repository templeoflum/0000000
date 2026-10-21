# Modular Heart surface — first working pass

Superseded by the [performance pass](../performance-pass/README.md): combined A/B, separate clip browsing, all-layer Play and musical timing, shared effect drives and expressive gestures are now implemented. The following records the earlier pass.

September 8, 2026. Implements the first surface stage of the [coherent instrument plan](../COHERENT-INSTRUMENT-PLAN.md). Effect modulation and final pilot refinement are subsequent stages, not claimed complete here.

The [updated stage 2 plan](../COHERENT-INSTRUMENT-PLAN.md#2-build-the-playable-modular-surface-then-connect-effect-motion) records subsequent playing notes: a combined workspace retaining independently scrolling A/B sections, separate clip browsing, all-layer triggers and tap BPM/downbeat in Play, effect drives and expressive gestures. Beatpad is a future inactive placeholder; usage recording is deferred. Those revisions are not implemented by the first pass described below.

## Using it

- **Layer faders:** eight levels, four over four, in Resolume order. Click a layer name to select it. Click a fader to capture the pointer; click again or Esc releases.
- **Play:** previous/random/next within the current bank, source Home/shuffle/undo and adjacent speed, searchable source bank, clear selected layer, and trackpad lane assignments.
- **Effects rack:** selected layer, another layer, composition, or all scopes. Click an effect's name to open its controls in B. Its separate On/Off control retains latch/momentary/one-shot envelope behavior. Existing effect keys still work. Gear opens envelope settings.
- **Parameters A / B:** independently choose a source or scoped effect. A initially follows the selected source; B initially pins Figure's Linear Cloner. Pin keeps the exact source name, role and column. Missing/ambiguous targets remain unavailable rather than falling through to another source. Either pane can show the same target if desired.
- **Arrange:** drag the vertical/horizontal dividers or exchange modules with a header selector; Lock layout hides these handles. Reset layout restores the six-area geometry. Geometry and pane targets persist under `surface.workspace`, outside performance patches.
- **Heart Monitor:** the existing GPU renderer occupies the monitor pane. Detach retains the accepted retro TV housing, pinning and independent small/large remembered window frames. Fit/1:1 and explicit Resume remain accessible from the dock header. The renderer is moved, not duplicated. Detaching frees its grid cell: the adjacent module expands vertically, and Dock monitor restores the six-area layout.

The full parameter list is available inside each independently scrolling pane. No six-parameter cap, bottom variation launcher, or page-wide source-button wall. Source Heart controls keep existing Home, shuffle, locks, speed and relationship menus. Scroll over a source parameter name to expose its existing timing/range menus; click its name to toggle Drive. Edit reveals Set Home.

**Ordinary effect controls are manual in this pass.** Native units are shown; whole-count controls step in integers. Linear Cloner does not yet get Heart drives, an animated effect Home or cross-source/effect relationship presets. That is the next planned stage. Existing native Resolume automation is left intact until an explicit manual edit takes ownership of that parameter. No new Home was applied and no shader/stack was replaced by this surface update.

## Preview orientation correction

The Metal monitor sampled Arena's shared image with the wrong vertical orientation. Four read-only paired Syphon/Resolume snapshots gave correlation 0.937–0.961 after vertical inversion, versus 0.698–0.898 without it; animation accounts for the remaining frame differences. `orientation.json` records the samples. The fix changes vertical sampling in the existing GPU draw. It does not touch a shader, layer Transform or composition output, and adds no video copy or extra render pass.

## Verification

- 130 engine checks pass, including replaced/missing target rejection and effect automation takeover (a failed takeover sends no value write).
- Native TV ownership/dock checks include the new in-surface dock, a detach/dock round trip, one retained render view and preserved suspension.
- Session checks and pointer capture/resume adapter checks pass. Wake does not automatically resume rendering or capture.
- Browser interaction: independent source pin survives selecting another layer; parameter modules exchange places; reset and reload restore saved settings. At 1100×700 all six panes remain within the viewport and scroll internally. No JavaScript errors observed.
- Manual Cloner End Scale tested in the UI: 74.71 → 75.71 → 74.71, with its native automation confirmed static before the test. This is a binding check, not artistic range validation.
- Native visual inspection confirms the monitor occupies its dock with all six regions visible. Current output continues at its original source resolution. No new broad performance benchmark is claimed; the user continued changing the running composition during this work.
- Removed parameter widgets now dispose their global gesture listeners. This prevents listener accumulation when switching sources or pane targets.

A small local Qwen3 8B review was requested with CPU inference (`num_gpu=0`) and unloaded afterward. `local-review.json` retains the response. Missing-target cases were useful; its vague layer-resizing cases were not treated as validation. Integration, targeting tests and native verification were performed separately.

## Recovery and files

`before/` contains the previous page, service, surface config and native source. `before-heart.json` / `before-live.json` are read-only observations at the start, not an instruction to overwrite subsequent user performance changes. The native app and controller service were rebuilt/reloaded; Resolume was not restarted and its current composition was not recalled or saved over.

Implementation: `sp/engine/workspace.js`, `workspace.css`, their hooks in `status.html`, the asset/instance checks in `heart.py`, and dock/orientation changes in `sp/monitor/Heart.m`. The accepted TV illustration/design was retained.
