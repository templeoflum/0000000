# Home rests; Open explores — September 8, 2026

Donovan separated two intentions that previously shared Home: returning to a calm,
readable state and opening the instrument's full motion range.

- **Home** stops all Heart drives on the selected source/effect, disables that
  target's auto-shuffle, and morphs to its saved pose or prepared profile centers.
  Unprofiled controls settle at their current visible values. A selected effect
  also fades to zero with its existing release time; pending triggers, held
  envelopes and pulses are cancelled. Other targets and the layer mix are untouched.
- **Open** explicitly enables every numeric drive, including whole-step count
  controls, unlocks those axes and opens normalized Lo/Hi to 0–1. It preserves
  speed, timing family and relationships, and sets modulation depth to one.
  A selected effect fades to full using its attack time. Choice menus, switches,
  colors and events remain deliberate manual controls.
- Figure Size/X/Y retain their prepared profile bounds, or existing bounds when
  no profile is available. Source containment code is unchanged; downstream effects
  remain unrestricted. This does not certify every imported source's framing.
- Both commands create one Undo entry. Undo restores the prior drive/range/pose
  configuration and the effect's previous steady envelope target; Home also restores
  the prior auto-shuffle setting on Undo. It does not replay an interrupted pulse.
- **Set Home** captures the visible pose, including driven values, for future rest.
  Existing saved Homes remain on disk and supply their poses; their old enabled-drive
  flags no longer make Home animate. Older relationship and preset formats remain intact.

Home stops Heart-controlled motion, not a shader's independent internal time or
other layers' effects. These are target-scoped controls, not a global composition reset.
Buttons appear in A/B, selected-source Play tools and the legacy card toolbar.

## Verification

150 Python checks and 22 isolated DOM checks passed. New cases cover Home/Open,
count ranges, effect fades, cancellation, Undo, visible-pose saving, old motion
Homes, selected-target dispatch and Figure framing bounds. Pointer and fader
checks and script parsing also pass.

At 1280×720, Home/Open/Shuffle/Undo/speed fit on one row in the effect panel
without page overflow. Heart's engine was reloaded from fresh live state and the
native surface refreshed; all three Open buttons, connection and running motion
were verified. No test Home/Open was fired over Donovan's ongoing performance.

Recovery source/config copies are in `before/`. These are references, not an
instruction to overwrite subsequent live edits. No composition was recalled or saved.
