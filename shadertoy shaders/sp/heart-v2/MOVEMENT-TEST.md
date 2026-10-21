# Figure movement test

Use a small native Resolume composition to verify Heart's real engine and output.

- One Figure layer; two simple, visibly different clips.
- One shared layer Transform for movement; clip changes retain that Transform and its running phase.
- Position X/Y, Rotation Z and Scale are the first four controls.
- Each control has an explicit range, Drive, ratio, multiple and phase.
- Shared Amount, Rate, relationship family, Hold and Home act on that Transform.

Acceptance: move → change relationship/rate → hold/resume → switch clips while moving → return Home. Verify the native picture and parameter values together.

Keep the test composition small. No controller mapping or per-clip movement setup is required. Apply the working layer Transform convention to the show afterward.

## Verified · September 11

- [x] Shared layer Transform: X/Y, rotation and scale move native output within authored bounds.
- [x] Switch Block → Bars while the same movement continues.
- [x] Change multipliers, phase and relationship family from Heart.
- [x] Hold freezes movement; resume continues it.
- [x] Home returns X/Y/rotation to 0 and scale to 100, with authored ranges retained.
- [x] Mirror Quad IN/OUT produces native output and returns opacity to 0.
- [x] Invert RGB momentary: native opacity 1 while Space is held, 0 after release.
- [x] Clips, motion and effect triggers fit the actual 639 × 734 browser panel; motion rows scroll locally.

The small rig is saved as `checks/Heart Movement Test.avc`. This verifies the control path; applying it to the full show composition remains.
