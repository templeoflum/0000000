# Performance quality of life — September 8

## Spring speed and hover scrolling

Each fader now exposes its saved spring return time in milliseconds (0–3000).
Lower is tighter; unsaved defaults are 150 ms, existing saved times are retained.
Hover scrolling changes a lasting level without pointer capture, overlays or an
idle unlock timer. Shift-scroll remains fine adjustment. Scrolling cancels an
older release spring so it cannot fight the new value. Physical latch behavior
is unchanged. Gesture checks and 23 workspace checks pass. Native page refreshed;
all eight spring inputs are visible at 150 ms, Resolume connected, 44 drives running.

## Physical-click release correction

Tap-to-click can arrive while raw contact is still present. Removed the contact
heuristic: in raw trackpad mode mouse/pointer down and context-menu events cannot
unlatch. Native pressure stage 1 (ordinary physical click) releases after the
opening finger lifts; stage 2 Force Click is not required. Finger lift only springs
the value. Escape, focus loss and probe loss remain safety exits.

Regression checks cover taps during contact and after lift, opening-click pressure,
sub-click pressure, and stage-1 release. Native pressure bridge activated by the user-approved Heart restart. Resolume
reconnected with 44 drives running and live 1920×1080 output at 58 FPS; detached
monitor restored. Physical playing acceptance is still pending. The earlier
claim below that the existing click bridge was sufficient is superseded.

## Fader correction: latch and contact are separate

The earlier mouse-movement gesture below was insufficient. A hard click now
latches the fader without jumping its value. Lift the opening finger, then each
light contact uses the trackpad's absolute vertical position; lifting springs to
zero while the latch remains engaged. Retouch interrupts the spring. A physical
press while in contact unlatches; tap-to-click after a lift is ignored. Mouse
movement cannot fight raw touch position. Probe loss releases the gesture safely.

This uses the already-connected 8770 raw-touch feed, with no new recording or
inference process. Unchanged values are skipped, moving contact updates are capped
at 60 Hz, and initial contacts jump immediately. The existing spring-time setting
controls each return. Gesture tests cover latch/contact separation, repeated
touches, release, retouch, tap-to-click and final unlatch. Native surface refreshed;
probe connected at 60.1 Hz. Physical playing acceptance remains with Donovan.

The correction works with the existing physical-click bridge and needs no native
restart. The additional pressure-stage handler mentioned below remains pending.

- Clicking a fader captures the pointer and selects an absolute level. Initial
  mouseup keeps capture. Light movement needs no held button. The next press
  releases capture and springs to zero; Escape/focus loss/sleep still release safely.
  Wheel capture continues to set a lasting level. A short protective overlay
  consumes the releasing click, with bounded cleanup if native mouseup is lost.
- Native pressure-stage forwarding is built: a Force Touch stage-2 event can also
  release an armed fader. The opening press cannot immediately release itself.
  **Native activation pending:** automatic approval review rejected Cmd+Q to reload
  Heart. Surface refresh loads click-again release; pressure-stage forwarding needs
  the user's approval to restart the native app. Do not bypass the rejection.
- Effect press dispatch ignores legacy quantize settings and takes effect
  immediately. Attack/release durations and one-shot behavior remain. The obsolete
  quantize control is removed from the envelope panel; ratio timing is unchanged.
- Effects rack has Composition and Selected layer buttons, with selected-state
  feedback, plus the dropdown for specific layers or all effects.
- Layer rebuilds publish complete rows instead of a cleared/partially filled
  shared list. Clip labels retain confirmed values through failed or single empty
  polls, update to incoming clips, and clear after confirmed empty reads. An explicit
  successful Heart Clear updates the label immediately.

153 Python checks, 23 DOM checks, pointer/fader checks and surface script parsing
passed. Native app builds. Surface shortcuts were verified in the refreshed native
window; backend reloaded from fresh performance state. Physical Force Touch testing
is pending native restart. No Resolume composition recall/save was performed.
