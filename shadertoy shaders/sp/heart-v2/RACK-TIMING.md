# Rack controls and timing · September 12

LUT and Color Loop quick amounts are always visible on Composition, Stage, Figure and Field + video. Feedback has Invert A only. RGB/Factor, Blur/Sharpen amounts, generic effect-alpha sliders and pad wheel-alpha gestures are removed from the rack; full native detail remains available through the effect editor.

Hits (Twitch, Infinite Zoom, Low Rez, Cut/Prism/Split) have separate saved beat lengths. Decon/Blok retain native event timing. Persistent toggles and Pixel Melt lock are excluded from kick/snare choices. Pattern assignments remain behind the collapsed Pattern button. LUT power preserves the dialed amount.

Feedback's four Mirrors and Figure Linear Cloner, Mirror X, Mirror Y and Mirror XY use soft toggles. Their default fade is ½ beat, individually adjustable from ⅛ to 8 beats. Timing lives in the current composition's row/pad preferences in session-settings.json. Hit lengths use the legacy row length until individually set. Releases follow the shared beat clock through tempo changes and motion Hold. Downbeat preserves an in-flight release's elapsed beat distance.

Soft toggles claim only effect opacity and bypass, leaving other drives running. Fade-in confirms the starting amount before enabling the effect; fade-out confirms zero before bypass and restores remembered strength while hidden. Reversal starts from the current amount. Every awaited native action checks ownership, identity and session state, and completion fences queued output. Native ranges, animation programs, effect settings, geometry and MIDI assignments are not authored by this update.

Validation:

- 162 backend regression checks passed after the final output-return fence (`checks/rack-timing/backend-final.txt`). The subsequent LUT amount-preservation change passed 47 affected checks; Figure bindings/timing passed 11 checks.
- Isolated UI at 639×734, 1440×900 and 480×800 verifies nine quick sliders, independent timing, typed actions, Figure fades, excluded toggle loop choices, keyboard use, disabled states and contained scrolling. See `checks/rack-timing/surface-final.txt` and screenshots.
- Initial rack install: all five rows ready, no error, armed at native 70 BPM. Eighteen matching observed native-phase settings retained Drive, lock and motion values.
- Standalone Feedback Mirror X: native sampling recorded intermediate opacity during fade-in. The sampling window ended before the later off action; a separate native read after off confirmed the original opacity 1, bypass true and static program. Zero-before-bypass ordering and fade-out progression are covered by the runtime test. See `mirror-native.json` and `verification.json`.
- Final Figure additions: exact existing LinearCloner and three Mirror bindings validate; installed state reports four fade controls at ½ beat and all five rows ready. Mouse/keyboard behavior is covered by the final mock UI. No additional live Figure fade probe was run while the performer was actively using Heart. See `checks/rack-figure-fades/installed.json`.

Current server PID is recorded in `checks/rack-figure-fades/installed-pid.txt`. Backups and restart state are retained in the check folders. No native composition save was performed. Performer feel remains open. The separate native-response/output interruption described in MOTION-TIMING.md is not resolved by this batch. No new PS4 mappings were added.
