# Final scope correction · 2026-09-11T22:42:31.132792-05:00

Composition-wide Goo with all controls exposed; Stage-only Goo disabled. All rack sections open by default. Melt hit removed from buttons and loop choices. Invert A remains visible and verified.

- Composition Goo effect1789543152090 is position10 before final Mask (Mask remains final); Stage Goo bypass true. New Output/Composition row has all native Goo controls, plus on/off and alpha. All existing rows remain expanded.
- Typed rack controls support boolean switches and exact native choices; 36 focused backend tests pass. Five config checks pass.
- Actual native Black Background, Blend Mode and Resolution change/readback/restore passed; all rack rows ready, armed, Hold off, no error. Native output snapshot confirms continuing content with final mask. Evidence: checks/session-composition-goo-live.json.
- Server PID92405;185 current parameter settings and two running drives restored.
- No native save. Earlier Stage Goo records below are historical and superseded.

---

# Tonight’s final controls · 2026-09-11T22:36:44.198350-05:00

- Current Perform: Stage, Field + Content, Feedback. Figure preserved in effect-rack.json parked_rows and native content; omitted from Drives.
- Stage effect browser uses configured group bindings independently of selected source layer. Goo/Distort toggles and opacity; Goo speed/X/Y, Distort amount/radius, Twitch Power and existing color controls visible.
- Native Twitch Global .82; Stage max X/Y .12/.09, Field+Content .14/.10; all max scale .34, position frequency .85, scale frequency .78. Delivered and checked. Figure Twitch untouched.
- Stage Goo started at mix .4, speed .17, X .22, Y .16. Distort available without changing its preceding program.
- Twitch contrast_hit pulses work from full alpha and restore; 34 focused tests pass. Five exact binding/config tests pass.
- Feedback native Invert A exposed separately from mix opacity. Native 0/1 delivery passed; preceding A1 restored.
- Final server PID91929, armed, Hold off, 208 captured parameter settings restored including two running drives. Native output snapshot showed continuing composition. No native save.
- Evidence: checks/session-tonight-native.json, checks/session-tonight-applied.json. Native before-values: checks/session-tonight-applied.before.json. Prechange configuration and parked Figure row: checks/session-before-tonight/.
- Original field duplicate cleanup remains unresolved; performance remains explicitly deferred.

---

# Heart session handoff · September 11

Installed and live: Source / Perform. Perform contains the FX rack and Drive bank together. Content is omitted from Drives; its layer and Field + video effects remain available.

## Playing controls

- Layers and effects: hover-scroll changes opacity, Shift gives fine control, and the fill grows right to left. Effect selection opens the editor. Effects are arranged in two columns. Scrolling over a level control does not pan the surrounding container, including while Heart is disarmed.
- Crossfader: native A/B, draggable or hover-scroll, with Shift for fine control. Native bus assignments are retained.
- Stage / Figure / Field + video: LUT enable and Decon, Pixel Melt latch, Blok, Melt hit, Twitch, and Cut / Prism / Split stacks. Color Factor/RGB and rhythm assignments expand in place.
- Feedback: Mirror X, Mirror Y, Mirror XY, offset Mirror, Invert RGB, Blur and Sharpen. Each has an independent on/off switch and Alpha slider. Blur, X/Y blur distance, sharpening and radius stay visible. Alpha means effect opacity, not inversion of the image's alpha channel.
- Kick/Snare: either 4/4 Kick or alternate Kick/Snare. Assign effects in each section. A hit flashes a bypassed Feedback effect or dips an already-visible one, then restores its preceding level and bypass. Loop playback does not automatically restart after opening Heart.
- Relationship Family, Rate and Shuffle remain in the same Perform view. Source opens the current instrument editor. Heart must be armed for its generated motion and writing controls.
- Set… captures Base and Safe. These are two deliberate returns, with no additional look library. Native color animations and edited clip-motion settings survived live recovery checks. Temporary verification captures were cleared.

## Verification and current limits

Original three rack rows: native Factor/RGB takeover, pulse restoration, both rhythm patterns and crossfader passed. Base/Safe restored native color clocks and an edited source across a clip change. Evidence: `checks/session-rack-live.json`.

Feedback: all seven switches, alpha adjustment without changing bypass, five shaping controls and a complete alternating four-beat loop passed. The previous values were restored. Evidence: `checks/session-feedback-live.json`. The standalone panel exposes the new controls. Focused backend/config and compact/wide mocked interface checks pass, including the two-column browser and wheel ownership.

Layer/effect scroll and click-to-edit were checked in the standalone interface against native readback. Crossfader scroll passed its focused interface check; its native parameter path passed the rack check. The user was continuing to operate the panel during the final update.

Nine original core clips passed native starting-motion checks; 20 new drives were added without changing the 339 existing timeline programs. Ground/Room/Void were subsequently strengthened: Travel .30 span, Sway .30, Bob .20, with approximately 16/24/32-second motion at the current 70 BPM. Saved poses and other settings remain unchanged. The stronger profiles passed offline first-frame and range checks. Current performer confirmation remains open. Evidence: `checks/session-native-verification.json` and `checks/session-field-motion-strengthened.json`.

Native clip cleanup remains unresolved. Ground/Room/Void are distinct sources, not duplicate versions. QField2 and QuarternionSwell each have an original and a repaired editable version. No clips were deleted, moved, or hidden to imply that the native problem was solved.

Performance investigation was stopped at the user's direction. The powered baseline held 60 FPS. A combined Figure/Room/feedback/delay rehearsal averaged 30.2 FPS, with one 28 FPS second. This does not establish a 30 FPS floor. No further performance changes were made. The test's temporary levels were restored after correcting its cleanup ordering.

SP Atom Script's exact-output optimization is installed in its source, installed resource and generator. It passed 324 byte-identical offscreen comparisons. The current Glyph layer has no clip, so runtime reload was not verified and no native FPS improvement is claimed.

## Remaining performer input

1. Confirm the stronger Ground/Room/Void motion works in the output; resolve any still-static Field clip before calling that part complete.
2. Choose the actual show looks to capture as Base and Safe.
3. 1d retains its saved opacity of zero; decide whether its starting look should be visible.

Native composition saving remains a user action. Native mixing, group order, geometry and masks were retained. Backups and scoped restoration snapshots are in `checks/session-before-install`, `checks/session-before-refinement`, and `checks/session-before-feedback`.
