# Heart v2 · clips and motion

Performance surface: http://localhost:8875/
Progress dashboard: http://localhost:8875/progress

Launch `launch.command`, or run `../engine/.venv/bin/python server.py` from this folder. Requires the existing engine Python environment and Resolume's API on localhost:8080. The launch script runs in a terminal; keep it open. Ports are separate from v1. This is a pilot, not a replacement declared show-ready.

## Current candidate · September 11

The combined motion, clip-launching and effects panel is installed and connected to the full show composition. Direct named layer buttons replace the primary layer dropdown; Source and shared Movement each take one click, and effects have direct on/off pads under Clip/Layer/Group/Comp tabs. Edit opens parameters; Pin adds an effect to the Pinned bank across layers. Pins retain their position while browsing, follow native state and remain disabled if their target is missing. Layer labels and matching colors identify destinations. The small native composition is saved in `checks/Heart Movement Test.avc`; the previous show snapshot is `checks/Heart Before Movement Test.avc`. Native output verified shared layer Transform movement across clip changes, relationships, Hold/Home, effect IN/OUT and momentary release. The view adapts to the actual 639 × 734 browser panel. The passive memory guard remains active; the earlier memory incident is not claimed resolved.

- Configurable visible layer buttons and one scrollable layer list, clip search/favorites, previous/next/random/eject and native identity handoff.
- Scoped FX rack with distinct opacity/bypass, linked IN/OUT and guarded momentary release. A/B follow/pin, local settings and native animation remain accessible.
- Low/High numbers support horizontal dragging, Shift for fine adjustment and click-to-type entry; dragging cannot cross the opposite bound or the native limits. Escape cancels the current drag. Range edits preserve running drives. Motion value sliders support direct mouse/touch/keyboard control within that range; manual value control stops only that parameter’s Drive.
- Motion family, spread/seed/phase modulation, per-parameter ratio/multiple/phase/shape; Amount/Rate and musical scaling preserve authored ranges and running phase.
- Generic weighted opacity sets, an explicit feedback layer capability view, and color/alpha. Stage geometry and media are untouched. Mixed set values are shown when members change independently.
- Visible target values use small HTTP reads by parameter ID. Continuous output uses the same small-request API at up to 120 Hz; no native WebSocket is opened by default. Armed discovery refreshes current clips without reloading the entire composition. Retired parameter contracts and old revisions cannot update current readouts. This observes values; it does not automatically decide ownership between competing automation sources.

Verification: **65 backend checks passed across regression runs**, including the HTTP transport and lightweight clip discovery. The focused playing-surface check passes, including shared movement selection, native-unit ranges, adjacent clip launching and narrow-panel bounds. Native verification confirmed the four shared movement parameters, two different clips, Hold/Home and effects; a keyboard-held effect read 1 while pressed and 0 after release. Full show load, feedback accumulation/reset and Base/Safe remain open.

Latest working split: Portal/stage is outside Heart’s performance workspace; the user’s native Resolume Grid faders/knobs handle mixing and stage controls; the separate big knob is a native master. Heart prioritizes clips and motion, then PS4 navigation through its interface. Recovery is one **Base** and one **Safe** state, still to implement; no general preset library.

Native control protocol: [Resolume REST API](https://resolume.com/docs/restapi/). Explicit Refresh still reads the complete structure to find newly added layers/effects. The old WebSocket path remains available only through `HEART_V2_TRANSPORT=websocket` (or an explicit `HEART_V2_SOCKET`); its broadcast load makes it unsuitable for the current full composition.

## Earlier deployed foundation

- Generic discovery of exposed numeric, boolean, choice and trigger parameters from playing sources, effects and layer levels. All clips are listed for launch; only connected sources become drive targets.
- Existing Smart Param integrator and relationship constants extracted unchanged into smart_motion.py; no instrument recipes, preset store, or v1 runtime imports.
- One selected target, numeric native-value entry/scrub, individual Drive, Open, Low/High, Amount, Rate, Shuffle, Hold and Settle. Effect opacity/layer level excluded from automatic Open. Effect Settle fades opacity toward zero.
- Native CoreMIDI, GameController buttons/sticks/triggers and raw multitouch feed shared layout actions. The Performance panel supplies four faders, eight pads, saved setup and input learning. Earlier main-pane MIDI shortcuts remain available; a grabbed layout takes precedence for its assigned MIDI inputs and releases the old single-axis grab.
- Discovery in a separate process; delivery in a separate persistent worker; timing process integrates only explicitly owned numeric slots. The default output worker avoids unsolicited composition blobs entirely.
- Read-only startup. Arm refuses while a v1 `heart.py --all` process is present. Disconnection disarms, clears pending output and requires explicit rearm. Last surface disconnect disarms.
- Scoped clip handoff retains unrelated motion and output claims. Stable layer/clip identity and parameter contracts fence stale discovery and queued writes.
- Performance layouts persist grouped numeric bindings, common actions and per-device encoding/sensitivity. Inputs support absolute, relative and pickup entry, guarded release springs, and scoped musical Rate/Intensity. See CONTROLLERS.md.

## Verified so far
- Nine core tests: native ranges, Open/Settle, type validation, full composition identity changes, stale ownership removal, phase preservation on unchanged discovery, Hold/disconnect, shuffle bounds, and effect opacity separation.
- Real bridge subprocess/socket test against a fake Arena endpoint: first ownership claim, continuous native values, boolean dispatch, stale epoch rejection, no writes after disarm. This is simulated output verification, not live output certification.
- 500-slot offline integration benchmark: ~0.90ms p95 calculation time across 600 ticks on this machine. Excludes socket/native rendering and is not end-to-end latency.
- Live read-only discovery: 135 targets, 26 layers, 1,137 clips. Read-only timing tick p95 ~17.5ms; scan ~836ms outside motion process; zero writes.
- Browser desktop/mobile layout, target selection, search, stable parameter DOM, booleans and no console errors checked. Physical MIDI/gamepad behavior not yet rehearsed.

## Live handover gate
Stop the v1 engine first, keeping its files and composition intact. Start/visit v2, select one source, arm, move one parameter and verify actual output. Then test drive/range/amount/shuffle/hold/settle, followed by one effect and one physical control. Measure actual output intervals under load before expanding scope. Do not equate read-only loop timing with live smoothness.

## Deliberate pilot limits
No Base/Safe recovery, monitor docking or automatic external-automation ownership arbitration yet. The staged candidate adds the ratio editor, native color adapter and scoped value readback described above. The functional layout editor and native input adapters are deployed; physical PS4/MIDI and multi-contact rehearsal remain pending. The earlier running backend displays commanded values while owned and discovery samples while passive; the candidate replaces this with subscribed native observations when available. Layers can be levelled/hidden through their target controls. Hold freezes parameter output; it does not stop autonomous shader TIME behavior. Downbeat resets Heart phase, not Resolume transport. Resting/disarmed numeric values remain at their last sent position; this pilot does not restore prior native automation. Owned momentary release endpoints are acknowledged before deliberate disarm. Clip launch releases only replaced clip controls; unrelated controls retain ownership.

Keep these limits visible. Follow SHOW-FEATURE-PLAN-2026-09-11.md for the authorized backend-first build; aesthetic refinement remains parked.


## Live pilot update
V1 background engine stopped for authorized handover. Live 4D manual W values -0.25/+0.25 confirmed in native readback in ~50ms each. Open moved 26/26 numeric source controls. Restricted range, Shuffle, Hold, Settle checked. HueRotate Open preserved opacity/bypass; explicit activation worked and Settle reached zero opacity. Core tick p95 17.45ms / calculation p95 0.20ms with 30 owned controls; bridge last batch work 0.09ms. Those are process measurements, not end-to-end render latency. Visible source evolution captured. Prior tested settings restored; left disarmed. Physical controller and full-show load rehearsal still pending. Raw check results in checks/.
Desktop launcher: ~/Desktop/Heart v2.app — starts the server only if needed, then opens the surface.


## Home and range controls
Set Home stores the selected target’s values, drive settings and relationships in homes.json, scoped to composition and target IDs. Return Home blends numeric settings over 0.3 seconds; discrete switches change immediately. Changed parameter contracts require a new Home. Running drives retain phase continuity. Each numeric control has draggable motion-range edges and arrow-key adjustment. The desktop launcher now opens Heart Surface.app (WebKit); browser access remains available for Web MIDI, which WebKit may not expose. Restarting the server leaves control disarmed.

## Navigation, Stage and native MIDI
A follows navigation; Open in B pins the current target into a separate parameter view. Stage groups are discovered by the exact `__stage__` name prefix and actual Resolume group membership. Declared stage groups are excluded from the performance layer rail. Layers outside declared groups remain ordinary; the per-composition Layers… configuration can hide additional layers by native identity. The visible layer list scrolls continuously in reverse API order matching the top-down Resolume stack. Native CoreMIDI supplies standalone input and hotplug; the browser keeps Web MIDI as a fallback. Performance → Setup supports multiple device assignments per control, independent of the earlier main-pane mapping shortcuts.

## Native parameter animation
Animation… on numeric parameters in A/B reads Resolume’s actual source and its supported controls. Timeline direction, play mode, speed, duration and native in/out limits can be edited; native animation releases Heart ownership, while a later Drive/manual edit takes it back. Source/control writes wait for confirmed readback (bounded 1.5s). The inspector is on demand, not a polling feed. Native animation configuration is not yet included in Heart Home snapshots. Effect mixer blend mode is discovered alongside opacity and bypass.

## September 11 backend foundation

42 backend tests passed, including scoped clip replacement, queued-output invalidation, saved layouts, entry/release ownership, musical scaling and independent client readouts. A live native Heart clip launch changed Figure to 4d while Field's driven Sway continued changing in actual Resolume readback. A grouped control produced native levels 0.12 and 0.06 from saved weights 1 and 0.5. Evidence: checks/backend-foundation-live.json. This check did not use physical controllers or certify rendered output under show load. Left connected and disarmed. See UPDATE-2026-09-11.md for the remaining controller integration work.

## Controller integration update

The native Performance panel can create/save/grab a layout, edit grouped destinations and learn multiple inputs. The raw trackpad adapter runs inside Heart Surface; no v1 engine or probe service is required. GameController provides the native PS4 path. Controller decoding and the setup/playing interface pass isolated tests; native layout save, fader drag with actual Resolume readback, and trackpad capture/Escape release were verified. Evidence: checks/controller-surface-live.json. Hardware currently reports trackpad connected, PS4 and MIDI disconnected; independent finger pressure, full multitouch playing, actual encoder format and physical controller rehearsal remain unverified. Aesthetic work stays parked.

Motion transport fix: the old native WebSocket received ten complete composition messages, 365 MB in eight seconds. Switching to small HTTP parameter writes removed burst delivery; replacing armed full-grid scans removed the remaining ~300 ms read stalls. Five simultaneous Figure source/shared Transform drives produced a 13.5 ms p95 sampled native change interval (29 ms maximum), with native read latency below 12 ms and no errors. Native boolean switching also passed and its initial state was restored. See `checks/motion-delivery-2026-09-11.json`. Rendered-frame cadence and performer acceptance remain to be confirmed.

Effect pads switch bypass directly. When turning on an effect at zero opacity, they restore its remembered/configured nonzero level or full opacity; an existing nonzero level is retained. Multiple pads can stay on independently. Permanent effects without bypass/opacity remain available for editing. Pins save per composition; they do not transfer to a replacement clip effect.
