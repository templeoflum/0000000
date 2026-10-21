# Heart controller layouts

Current show plan: [SHOW-CHECKLIST.md](SHOW-CHECKLIST.md). Hardware mapping is phase 5, after Heart works fully with mouse and keyboard. Map the whole Grid and PS4 navigation onto existing actions. The layout instructions below document existing implementation; custom layout/Grab setup is not a prerequisite. Separate big knob and trackpad workflows remain deferred.

Open **Performance** in the native Heart surface. **New** takes up to four ordinary layers from the current mixer bank. Names and IDs come from discovery. Edit the layout name and destinations, then **Save**. **Grab layout** activates its saved bindings; **Arm control** enables output. Saving edits does not retarget an already grabbed layout: release and grab to apply them.

Each fader/pad has **Setup**. Controls can address one parameter, weighted groups, Rate, Intensity, or an action. The target chooser includes stage groups/layers through the same catalog. Weights are saved explicitly and do not derive from temporarily zero live opacity. Exact targets stay fixed. **Follow selection** is explicit and freezes at gesture start.

**Learn input** consumes the next meaningful MIDI or controller movement without playing it. Multiple devices can share a control. Each input row's **Edit** selects its own encoding, sensitivity, polarity, dead zone and trigger threshold. Use the format observed from actual knob messages: absolute CC, two's complement, binary offset or sign/magnitude. No KnobX1 encoding has been inferred from the product name. Clear removes only that assignment.

Trackpad regions are four faders or eight pads in two rows of four. **Grab trackpad** captures native pointing/scrolling/gesture input; Escape releases. Physical force-click release is implemented but still needs a human hardware check. Existing contacts are consumed on grab. A contact keeps its initial region across drift; the first contact owns a region and another must lift before acquiring it. Release can hold, return to zero or return to a reference with an adjustable duration. The backend guards release springs against newer intent.

PS4 sticks default to relative rate with a dead zone, retaining the parameter on centering. Absolute position is explicit. Triggers can be continuous or threshold buttons with hysteresis. **PS4 · Navigate** uses the D-pad for layer/target navigation and suppresses performance bindings; it never synthesizes focused-button clicks. Native identity uses model/category. Identical connected controllers are marked ambiguous instead of sharing an assignment silently. PS4 touchpad, motion sensors and rumble are not implemented.

Mapped momentary actions support matching press/release destinations. IN/OUT reverse the existing envelope; toggles use boolean state or numeric endpoints. A newer parameter or Hold action prevents an old release from overriding it. Cross-target momentary release is rejected. Deliberate disarm and final-client disconnect finish still-owned release endpoints before the worker disarms. An output disconnection cannot deliver a final write and still requires explicit rearm.

The existing main-pane MIDI assignments remain available outside a layout's assigned inputs. Grabbing a layout releases the old single-axis gamepad prototype. Saved settings live in `layouts.json`; transient contacts and current playback state do not.

## Verification and current limits

- Backend suite: 45 tests. Controller decoder fixture covers simultaneous contacts, all eight pads, contact drift/collision, held reconnect state, MIDI encodings, stick/trigger behavior and navigation isolation.
- Isolated browser fixtures cover layout creation/save/grab, separate encodings for two devices sharing one control, synthetic four-contact play, momentary pad setup/play, capture cleanup and existing surface regression.
- Native UI: saved “Controller check,” dragged its Texture fader, verified actual Resolume level 0.176923 → 0.328706. Native trackpad capture and Escape release verified.
- Physical PS4 and MIDI were disconnected. Human multi-contact play, maximum simultaneous contacts, force-click release, real knob format and full rendered-output rehearsal remain pending. Contact area is not calibrated per-finger pressure.

## Build

`zsh build-surface.sh` builds the standalone native app with Cocoa, WebKit, CoreMIDI, GameController and CoreGraphics. `Inputs.h` adapts the existing raw MultitouchSupport contact format into native frames. JavaScript decodes input only; `performance.py` owns bindings/gestures and the existing engine owns musical/output state. Server surface versions include the controller scripts and stylesheet, so those edits use the same safe surface-update flow.
