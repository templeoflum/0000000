# Heart performance controller

Launch with `sp/start.sh` to open the native Heart window with its direct GPU output monitor. With the engine already running, open `monitor/Heart.app`. The browser controls remain at http://localhost:8765. See [monitor details](monitor/README.md).

The fader bank follows Resolume's top-to-bottom layer order, left to right (8 → 1 in the current composition).

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

The bank is now two rows of four. Each card has a speed multiplier beside shuffle. **Home** starts its prepared animation; **Set motion Home** in Edit saves your own choice of moving axes, ranges, relationship, and speed. The initial profiles are intentionally restrained and still need refinement by feel. FADERS/VARIATIONS capture buttons are at the bottom. [Parameter-loop documentation and implementation notes](design/PARAMETER-LOOP-HOME.md).

Surface density update: all discovered parameters on the selected card are visible in an adaptive grid; there is no six-parameter display limit. The two-row fader bank uses compact horizontal cards. Variation pads, flavor buttons, the pad status row, and the bottom FADERS/VARIATIONS buttons are parked off the surface. The F variation shortcut is disabled; L still supports the existing fader capture workflow. Stored variations remain available for a future UI pass.

Home drive coverage update: prepared profiles now enable shell 30 axes, void 14, glyph 11, dither 8, level 7, map 6, delay 5, and grain 4. Home speed remains 0.25×; this change addresses the active drive set. Continuous parameters use bounded per-axis ranges; selectors and resource counts remain manual. Layer effect controls now appear within their own fader cards, independent of selected layer. Composition effects remain in the separate rack. Shell's expanded Home was applied and verified live; Undo retains its prior state.

3D Tumble correction: SP Atom Solid previously used `TIME * tumble * 1.5`, so animating Tumble changed accumulated orientation according to elapsed time. It now reads Tumble as a 0–1 rotation phase, marked cyclic in Heart. The 3D Home uses continuous rotation, centered X/Y (0.42–0.58), Size 0.44–0.56, and Axis 0.25–0.4; other authored drives remain. Generator and installed shader resource both updated; prior files are backed up under audit/20260907-3d-phase. Existing saved 3D values that treated Tumble as speed have different semantics; recall the new Home. The playing shell was not switched during this correction. Arena's cached shader instance may require a source reload to use an updated resource.
