# Heart hardware input bring-up

2026-09-09: Mac detects KnobX1 through CoreMIDI and DUALSHOCK 4 Wireless Controller through Apple's GameController framework. No 4-fader controller connected yet.

Native Heart loads monitor/Hardware.h. Play shows connected devices and last MIDI/button input. This is a read-only input check: no parameter assignment or navigation armed yet. Input history is bounded and no global keyboard capture is used. Knob pages/encoder encoding need actual input samples before mapping; PS4 navigation will target layers directly, not follow the editor selection. Sticks are omitted from this initial readout to avoid idle drift masking useful events.

Agreed roles: future MIDI desk for feedback/delay sculpting; KnobX1 master intensity and separate speed page; PS4 direct/multi-layer navigation; trackpad expressive temporary gestures.

## PS4 surface navigation first pass
Native Heart now samples the first connected gamepad on its existing 60 Hz input timer, with at most one web delivery in flight. L1/R1 change panes; D-pad selects visible enabled controls; Cross activates or explicitly edits a numeric/select input; Circle cancels an edit. Left stick scrolls; right stick adjusts grabbed numeric inputs. Select edits use D-pad and commit on Cross. Gold focus/pink edit HUD explains the state. Options shows navigation help. Inputs suspend when the app is inactive, sleeping, or pointer capture is engaged. Reconnect seeds held button states without replaying actions. Removed targets are dropped rather than silently rebound.

Validation: native build and JS syntax pass; test_navigation.cjs covers focus, pane changes, activate, edit/cancel, reconnect suppression, removed targets. Physical controller feel remains the user's live trial. Text entry uses keyboard; pointer-only fader gestures and momentary pad actions are not synthesized by this navigation pass.

## Controller access revision

The generic focus pass missed Heart's custom controls. Added explicit adapters for layer levels, numeric Smart Params and scrubs; focusable layer selection/bypass/config and drive toggles; Square opens parameter depth controls. Numeric edits are staged until Cross applies; Circle cancels without writing to the show. Effect holds use their existing key-down/key-up handlers and release on focus loss/disconnect. Pane navigation follows visual order and remembers focus within each pane. Popovers trap focus and return it on close. Options exposes global controls; a controller keyboard handles searches and preset/patch naming; color inputs have RGB editing. Arrange's split handles have numeric controller adapters.

Quality evidence: navigation-qa/check.cjs loads the real Heart page in a rendered browser, intercepts outgoing commands, then navigates via simulated controller frames. 16 workflow assertions cover fader stage/cancel/apply, parameter drive/depth, Melt press/release, envelope focus/back, keyboard search/cancel, global menu and preset naming. Results and a real surface screenshot are in navigation-qa/. Native build, navigation safety checks, and49 workspace checks pass. This verifies routing/access with intercepted commands, not physical controller ergonomics or live-effect output. Remaining experiential issues should be reported specifically; not an exhaustive certification of every possible application/OS dialog.

## Configurable Controller MVP
Play → Controller now offers saved mappings for Cross, Square, L1, R1 and right-stick X. Assign source Home/Open/Shuffle, effect In/Out/native events, Strobe hold or MELT_LOCK hold, and a scalar source/effect parameter for the axis. Grab captures exact current instances; Circle, app blur, disconnect, or replacement releases holds and exits. Held buttons at grab are ignored until released; the axis uses relative movement with a .2 dead zone. Axis release retains its last value; no spring behavior yet. Config persists in surface.json workspace.controller. The first pass uses dropdown assignment; no drag-to-map or multiple layouts yet. The speculative stick-area jump is kept as an experiment, not enabled.

16 rendered-browser checks passed with show commands intercepted, plus50 workspace checks including saved unavailable-target retention. The live app is rebuilt; physical performance output remains a user trial. Tests: navigation-qa/controller.cjs and controller-results.json.
