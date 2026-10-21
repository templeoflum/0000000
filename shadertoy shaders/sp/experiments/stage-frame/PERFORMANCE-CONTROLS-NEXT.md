# Festival control pass

Priority: preserve native Portal smoothness and performance; expose playable section controls before adding further content or devices.

## Portal sections

- Background: base layer, bg1, bg2, bg3.
- Wings / blades: blades1, blades2, blades3.
- Balls: balls1, balls2.
- Squares: square1, square2.
- Rings: ring1 through ring5.
- Outline: outline/detail bank.
- Stage mask: separate output setup control, never part of a musical section level or shuffle.

Section level must operate on native layer Master (or an equivalent independent gain), preserving animated layer opacity and original Luma Key I blending. Do not replace opacity envelopes with manual opacity writes. Per-section controls: level, run/hold image shuffle, next/random, shuffle interval, transition-time multiplier, opacity animation rate. Expand for individual layer blend modes, transition modes, original ranges and animation controls. Keep layer blend and clip transition as distinct settings. Default reproduces original composition.

## Global controls

- Spring return time: shared default with explicit per-fader override.
- Effect transition-time multiplier: scales authored In and Out times without destroying their relationship. Immediate/momentary controls remain immediate.
- Motion speed and depth: independent master controls using existing Smart Params, no new generator architecture.
- Stage framing/masks excluded from global effect shuffle/settle operations where that would compromise projection alignment.

## Proposed hardware roles

Intech Grid: dedicated feedback and delay sculpting. Learn actual MIDI messages before binding; four faders, four knobs, four buttons. Show names, incoming input and current binding. Continuous absolute controls require pickup so connecting or switching bindings does not jump output.

KnobX1: master motion depth; alternate page for master motion rate. Confirm device page and encoder message behavior before activation.

PS4: navigation by default, existing explicit grab for performance mappings. Expand assignable inputs and support layer/section actions and global tools as well as effect events and parameters. Circle remains release/back. Release momentary targets on disconnect, blur, or target replacement.

Trackpad: pressure, spring, momentary fader/pad articulation.

## Delivery order

1. Portal section cards and preserved native animation controls.
2. Global spring / effect fade controls plus per-layer blend inspection.
3. MIDI Learn for the Intech; verify all twelve physical controls and pickup with user.
4. Expand PS4 mapping targets using those same actions.

Current implementation audit: CoreMIDI input detection exists, but hardware input display explicitly says not assigned. PS4 performance mapping currently exposes Cross, Square, L1, R1 and right-stick horizontal, targeting selected source/effect identities. Native Portal image banks run in Arena; section macro control UI is not implemented yet.

## Implemented control rescue (September 10)

- Target Full range and global Full range reset connected continuous slot Lo/Hi to 0–1 without changing drive switches, phase, native ownership, timing, or effect envelopes. Open applies the same expansion only to enabled continuous drives. Discrete controls are skipped. Existing saved ranges are retained until an explicit reset; dormant clips are not rewritten blindly.
- Runtime frame-guard Lo/Hi rewrites removed. Geometry projection remains only on the dedicated figure Transform; effects are unrestricted.
- Trackpad mapping supports four continuous faders (absolute / relative / spring) or eight action pads. Region drag to parameter, layer or action sets an assignment; dropdown fallback remains. Identity changes stop captured pads; release happens on unlock/blur.
- Intech tab: four faders, four knobs, four buttons; device/channel MIDI Learn, pickup, explicit Arm. PS4 exposes 18 buttons and six axes through explicit performance grab; Circle + Options or Escape releases. Device assignments support drag handles.
- Native input update compiled and Heart app relaunched; Arena left running. MIDI feed is delivered at 30 Hz. PS/Share availability depends on macOS delivery.
- Validation: 50 workspace tests, three shared-range tests, MIDI parsing/pickup/identity/disconnect tests; browser checks confirm eight pads, 12 Learn slots, 24 PS4 assignments, successful drag to Shuffle all, no page errors, and exactly-once pad press/release. Physical controller calibration remains a user check.
- Portal section macros/global spring and fade controls from the earlier proposal remain outstanding; these hardware bindings target currently available controls.

## September 10 — performance interaction repair
Open enables all numeric Smart Param drives at full range without activating effect bypasses. Shuffle uses shared relationships, independently of old armed matrices, respecting locks. Home rests at the current pose and fades the target effect out; no clip recipe. Low/High inputs cover each target or the composition and display Mixed when appropriate. Gestures use a maximum 350ms transition; persistence no longer holds the motion lock.

Layer clip navigation remains visible while mapping; clip launches preserve library button identity. Presets and diagnostics moved behind details. Mapping Arm/Grab stays at the top with wrapped assignment labels.

Verified: 50 workspace DOM checks, five shared-gesture tests, hardware mapping tests, browser drag-to-assign, and live 4D Open/range/Shuffle/Home readback. Live confirmations took 212–554ms; further latency work remains. Full-composition drive load and physical controller rehearsal are not yet verified.
