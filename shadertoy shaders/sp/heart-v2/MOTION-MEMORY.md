# Heart · last-used motion

September 12, 2026

Heart automatically remembers the last motion settings for each native clip/source/effect/layer, within its composition. Returning to a clip or restarting Heart restores those settings without a separate Save action or a preset library.

Remembered settings:

- Family, spread, seed and FM; source Amount and Mult.
- Per-parameter ratio, Mult, Phase offset, shape, Amount and Range offset.
- Shuffle's exact family positions, including stage group/section assignments.
- Locks and the explicit Drive on/off choice.
- Global, group, stage-section and layer multipliers, including temporarily empty layers.

Resolume still owns native In/Out, timeline programs and the current manual pose. Recall does not restore those, armed state, accumulated phase, pending hits or native routing. A returning drive starts from the current native position and rejoins the running shared clock with its remembered relationships. A newly encountered prepared parameter retains the normal automatic-start behavior. Running/native/static modes stay undriven until prepared again; their remembered relationships survive that transition. Disarm and transport rejection do not change the saved Drive choice.

The original reset had two causes: reconciliation discarded unloaded controls and recreated them with 1:1 defaults, and there was no disk store for current relationships. `motion_memory.py` now captures settings before retiring controls and after relationship actions. Restoration requires the same composition, native target identity and parameter schema. Native bounds, animation mode and address movement are excluded from the preference identity; output bindings still use their stricter current-route validation. Replaced shaders or parameters do not inherit another destination's settings. Stage assignments are rechecked against current membership.

`motion-settings.json` is an automatic last-used store. Changes are coalesced at 250 ms and sent as small deltas to a separate save process; that process serializes the file and replaces it atomically. Orderly shutdown flushes pending settings. Untouched defaults need no stored record; configured settings and explicit Drive choices are retained. Dynamic frame values never dirty the store. Corrupt file contents are preserved separately before a replacement save. A hard kill or power loss within the short save interval can lose the most recent edit. Settings already discarded before this update cannot be reconstructed automatically. The original full-library snapshot caused timing stalls and was corrected in the later [motion timing pass](MOTION-TIMING.md).

Verification is in `checks/motion-memory/`:

- 142 affected backend checks passed, with 12 new memory tests.
- The real server/discovery/output processes ran against an isolated mock Resolume, including clip A → B → A, exact Shuffle recall, explicit Drive off, and a complete process restart. No native value/range/program writes occurred.
- Offline reconciliation of the current 2,456-parameter catalogue measured approximately 4.0 ms median and 5.2 ms p95 for incremental source updates.
- Installation carried over current settings and compared 1,243 matching numeric controls without mismatches. Native mode discovery then resumed all 41 currently prepared drives; all 41 matched their pre-install settings. Heart was armed at 140 BPM, with no waiting destinations or reported errors.

The controller discussion remains separate. The performer subsequently chose Tap, Downbeat, kick/snare effect selection, and straight 4/4 or alternating kick/snare patterns as the intended PS4 workflow. Direct button-played Hit/Hold envelopes were not accepted. No new controller mappings were installed in this batch.
