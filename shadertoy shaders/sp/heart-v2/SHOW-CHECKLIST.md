Show build · September 11

# Heart · complete show plan

**September 12 · Rack controls and fade toggles:** Quick LUT/Color Loop amounts on all non-feedback rows; Feedback keeps Invert A. Removed rack RGB/Factor, Blur/Sharpen amounts and per-effect alpha controls. Hits have individual saved beat lengths; native triggers keep their own timing. Feedback Mirrors and Figure Linear Cloner + three Mirrors fade on/off, with separate ⅛–8 beat times and remembered strengths. Cloner’s internal drives continue. Toggles stay out of kick/snare choices. Backend and compact/wide mock UI checks passed; all five installed rows are ready. Standalone Feedback Mirror fade and original-state return verified; Figure additions validated through installed state and mock interaction. Musical feel remains performer acceptance. See [Rack timing](RACK-TIMING.md).

**September 12 · Figure one-shots:** Infinite Zoom and Low Rez are back in Figure’s rack with separate hit buttons and kick/snare choices. The current native looks are retained, and detail controls start collapsed. 41 backend checks, compact/wide mocked interaction and installed standalone availability passed. Live feel remains performer acceptance.

**September 12 · Steady-motion investigation:** Installed a separate process for saving changed relationships, compacted untouched defaults, and batched simultaneous clip updates. The original 57 ms clock pause was traced to persistence overhead. All 157 affected backend checks pass. Latest delivery intervals are about 10.8 ms p95, with recent engine gaps below 15 ms, but a separate 201.6 ms interruption occurred when native control replies slowed and destination checks expired. Smooth rendered playback remains open. See [Motion timing](MOTION-TIMING.md).

**September 12 · Remember last relationships:** Installed automatic per-clip/effect motion recall through clip changes and Heart restarts. Family, shuffled positions, ratios, Mult, offsets, Amount, locks and explicit Drive off persist. Resolume retains native ranges/programs; reloaded drives join the shared clock. 142 backend checks passed, including full-process mock restart; 1,243 matching numeric settings carried across installation and all 41 prepared drives later matched. Controller one-shot design remains a discussion. See [Motion recall](MOTION-MEMORY.md).

**September 12 · Shared motion and fast handoff:** Installed one accumulated beat clock, shared scope/source timing, independent Amount / Range offset / Phase offset, and coherent latest-frame delivery. Native clip ranges and timeline programs remain in Resolume. Persistent discovery now sends only changed controls; live stage autoplay exposed and helped fix whole-catalogue update overhead. 130 affected backend checks and compact/wide mock UI passed. Restored 39 matching drives; live sampling delivered 37,479 updates in ~8 seconds with 3.37 ms p95 frame age, zero waiting destinations/errors, and an unchanged paused program on a moving stage parameter. Performer assessment of handoff and musical feel remains open. See [Shared motion](SHARED-MOTION.md).

**September 12 · Clip-change output stall:** Fixed a blocked phase frame that could spin the output worker and stop every drive while Heart still showed Driven. The old stall was reproduced; command responsiveness and fresh-binding delivery now pass. After reload, native Rings motion resumed within its saved bounds and unchanged paused program; 14,280 updates were sent during the check. The 31 affected output/recovery checks passed.

**September 12 · Mult buttons, stage Family and shader fix:** Source, layer, group, stage sections and Global now have ¼×/½×/1×/2×/4× buttons plus custom values down to 0.001×, easing over one beat. Stage has matching Family/Mult/Shuffle controls; BPM shortcuts are 60/70/120/140. Fixed native OSC names containing `+` and parentheses, verified on 4D Voronoi and 16 Dimensional Julia with restored probes. 68 backend checks and compact/wide mocked interaction passed; standalone display and restored live drives checked. Automatic approval review blocked the all-motion live speed test; musical acceptance remains open. See [Motion multipliers](MOTION-MULTIPLIERS.md).

**September 12 · Stage motion:** Perform now has Shuffle per stage section and Shuffle stage. Base, Background, Blades, Squares, Balls, Rings, Outline and Shared effects are configured by native identity. The user prepares timelines in Resolume; Heart only shuffles active unlocked phase drives. Live Rings changed five relationships and stage-wide changed all 16 prepared layer timelines; native ranges/programs, multipliers/shapes and Drive states were preserved. 56 affected backend checks plus compact/wide surface checks passed. See [Stage motion](STAGE-MOTION.md).

**September 12 · Figure card and compact rack:** Figure is restored in the effect rack and Drives. All five rack cards start with sliders collapsed; Controls expands color, alpha and loop settings in place. Standalone display and compact/wide mocked interaction passed. Six pre-reload Ancient Temple drives retained their ratio, multiplier, phase offset and shape settings; all rack bindings report ready. See `checks/figure-card-collapsed/`.

**September 12 · Native ranges and automatic detection:** The performer accepted Shell’s native-range pilot. The same rule now applies generically to numeric source/effect/native controls: Timeline + paused prepares a Heart phase drive; static controls stay manual and playing timelines remain native. Figure’s second Transform automatically detected Position X, Position Y and Scale. Native motion, play/pause handoff, Drive off retention and static manual adjustment passed; all captured Transform ranges, programs and static values were preserved. Heart no longer loads imported profiles or a hardcoded phase opt-in file. See [Native phase control](NATIVE-PHASE-PILOT.md). Existing Heart drives remain disposable; composition saving is a user action.

---

**Goal:** use Heart for sources, shared movement, relationships and effects; native MIDI handles mixing and Portal/stage levels. Figure tuning has resumed alongside the existing Stage, Field + Content and Feedback workflows. Recover and continue with Base/Safe.

**Now:** **Source / Perform** is the playing interface. Perform combines the FX rack and Drive bank. Content is excluded from Drives. Layer/effect buttons show opacity and accept hover-scroll; the crossfader also accepts scroll. The effects browser is two columns, and opacity gestures do not scroll the surrounding panels.

**Current batch:** Simplified rack and independent hit/fade times are installed, including Figure Linear Cloner and three Mirrors. Performer feel remains open. The separate interruption during delayed native control replies still needs investigation and rendered acceptance. PS4 is intended for Tap, Downbeat, kick/snare effect selection and straight 4/4 or alternating kick/snare patterns; no new controller bindings have been applied.

**Field status:** Nine core clips passed native parameter-motion checks. Ground/Room/Void then received wider, faster starting camera motion after the performer reported their initial motion was not useful. The strengthened profiles preserve their saved poses and pass bounded waveform checks; performer confirmation of the current rendered result remains open. No native clips were deleted or moved. A browser-only duplicate cleanup was explicitly rejected and was not applied.

**Output performance:** Investigation stopped at the performer's direction before showtime. Powered baseline was 60 FPS; the combined sample averaged 30.2 FPS with one 28 FPS second. This is recorded evidence, not a passed 30 FPS minimum. No further performance reduction or delay substitution was made.

**Handoff:** [Current session record](SESSION-HANDOFF-2026-09-11.md). Live dashboard: http://127.0.0.1:8877/. Base and Safe functionality is verified; deliberate show looks still need to be captured. Hardware work remains outside this session. Historical records below describe their original tested behavior; the current batch above supersedes earlier one-column, separate Drives/Rack and click-to-toggle browser descriptions.

Checkboxes mark verified phase outcomes. Existing implementation is recorded separately below. Work follows dependencies, without time blocks.

**Build rule:** every function has a working Heart control and uses the shared backend action. Later controller mappings call that same action.

## 1 · Core playing workflow

- [ ] **Layer playing:** current clip, previous/next/random/eject, level/visibility and focused browsing across discovered layers.
- [ ] **FX rack:** layer/group/composition effects, distinct bypass and opacity, IN/OUT, momentary and linked actions.
- [ ] **Detail and state:** A/B follow/pin, full parameter access and local settings. Show destinations, motion ownership, pending/errors and relevant hidden/master/opacity context.
- [ ] **Usable surface:** compact stable positions, mouse operation and keyboard focus/activation. Sources, effects, layers and groups use the existing engine and shared actions.

**Minimum outcome:** select content, mix it and play effects entirely inside Heart without external controllers. Repair backend gaps as each workflow requires them.

## 2 · Instrument workflows

- [ ] **Generative controls:** Drive, ranges, Amount/Rate, Open/Settle/Shuffle, Hold and per-target Home. Keep scoped musical Rate/Intensity without overwriting authored settings.
- [ ] **Feedback:** expose actual movement, gain/decay, shaping and reset capabilities. Verify input routing, accumulation and recovery in real output.
- **Stage accents:** dedicated Melt/Blok/Twitch and Color row on the existing Stage group. Native MIDI handles stage mixing; geometry and masks stay outside Heart.
- [ ] **Color:** native color access in A/B and appropriate controls, preserving alpha.

**Minimum outcome:** access generative source, movement, feedback and effect controls quickly. Composition names remain test configurations, never application logic.

## 3 · Recall and recovery

- [ ] **Base:** explicitly set and return to the useful starting state in the current composition.
- [ ] **Safe:** one deliberate recovery state with motion/feedback behavior verified in output. No look library or general preset system.
- [ ] **Distinct recovery:** stop motion, reset feedback and restore a useful look are separate reachable actions.
- [ ] **Continuity:** clip changes and Base/Safe returns preserve unrelated motion; replaced or missing targets never receive stale or guessed writes.
- [ ] **Resume:** saved show state survives reopening. Disconnection clears pending intent; reconnect/rearm restores deliberate control without stale replay.

**Minimum outcome:** change the instrument, return to Base or Safe and keep playing from Heart without controllers or restarting. Output geometry stays outside recall.

## 4 · Complete Heart verification

- [ ] **Complete phrase:** select content → shape movement/feedback → apply effects → change clips → recover → continue. Native MIDI handles mixing and stage accents.
- [ ] **Actual output:** intended media, routing, dimensions and effects run together without control stalls, stuck actions or missing content.
- [ ] **Transfer:** confirm a differently organized instrument/stage works through configuration alone.
- [ ] **Closure:** fix functional blockers and repeat the affected playing sequence. Essential controls remain reachable at the actual native window size.

**Minimum outcome:** the complete application works independently of hardware controllers. Core features do not wait for MIDI, PS4 or a device-specific setup.

## 5 · Hardware mapping and final play

- [x] **Native Grid faders/knobs:** user reports a useful performance mapping directly in Resolume. Keep it as the mixing path.
- [ ] **Remaining inputs:** add only needed Grid buttons or Heart assignments; verify continuous, trigger/toggle and momentary behavior where used.
- [ ] **Bindings:** multiple assignments coexist, persist, and can be changed or cleared. Fixed destinations remain stable while browsing; grouped controls retain their weights.
- [ ] **PS4 rhythm selection:** Tap, Downbeat, kick/snare effect selection and straight 4/4 or alternating kick/snare patterns through shared Heart actions. Preserve useful interface navigation; direct button-played Hit/Hold is not the requested workflow.
- [ ] **Final play:** repeat the verified phrase using Grid and PS4 together. Check saved assignments after reopen/reconnect and fix input-specific blockers.

**Show-ready:** the complete workflow works repeatedly at the intended output, with or without the performance controllers. Hardware changes how controls are reached, not what Heart can do.

## Existing implementation

**Current behavior supersedes the native-only and opacity-pulse notes below.** See [Clip starting points](AUTHORED-CLIPS.md). Older evidence records the implementation tested at that time; it is not proof of the corrected rack semantics.

- [x] **Performance Rack:** Stage / Figure / Field + video, each with Decon, Pixel Melt, Color and Clear. Pixel Melt is MTK_PXLMELT, separate from LUT MELT. Beat-length and Strength controls; automatic zero return, rapid retrigger, keyboard activation and Hold-safe release. Existing native layers/groups retained. Three color timelines have different phases; Field/video stay together.

- [x] **Clips/layers:** browse, search, favorites, previous/next/random/eject, level/visibility, a continuous scrollable layer list and stable native IDs.
- [x] **FX/detail:** direct on/off pads, persistent pins across layers, matching layer colors and explicit ON/OFF labels; scoped rack including permanent Transforms, bypass/opacity, linked and momentary IN/OUT; A/B follow/pin and native animation access.
- [x] **Motion:** directly draggable Low/High numbers (Shift for fine control, click to type, limits prevent crossing) and value sliders with per-parameter manual takeover; relationship families, ratio/multiple/phase/shape, Drive, ranges, Amount/Rate, gestures/Home and scoped musical scaling. Amount/Rate preserve individual ranges.
- [x] **Drive bank:** active source/effect rows grouped by layer; persistent pins, Family/Rate/Shuffle and Shuffle layer. Shuffle changes only driven parameters within the selected family, preserving authored ranges, Amount and the driven set. Missing pins remain visibly offline. Row names open the parameter editor.
- [x] **Playing sources and Drive all:** the playing clip name opens its instrument; Source follows clip changes on the selected layer and exposes clip/source/effect buttons. Router clips open their instrument effect. Idle playing instruments remain in Drives. Drive all toggles unlocked numeric parameters together from the editor or bank; per-parameter Lock excludes them from bulk Drive and Shuffle while preserving their current Drive state.
- [x] **Instrument access:** generic weighted opacity sets, actual feedback capability view, native color/alpha.
- [x] **Value feedback:** small scoped native reads, bounded reporting and stale-binding rejection. HTTP output avoids full-composition WebSocket broadcasts; native numeric and boolean delivery verified.
- [x] **Installed panel:** full composition connected; direct layer/source/movement/effect navigation and configurable visible layers. Small-composition native acceptance passed; full-show acceptance remains.
- [ ] **Native acceptance:** output/routing, rendered feedback accumulation/reset, large-composition playing and physical PS4 navigation.

**Outline repair:** restored the outline layer canvas from 3840 × 1440 to its saved 1920 × 720 dimensions; native readback confirmed. The existing group scale remains 200%. See `checks/outline-alignment-repair-2026-09-11.json`.

**Range editing:** Low/High number dragging is installed. Pointer checks cover live range updates without stopping drives, fine adjustment, limits, typing, Escape cancellation, disabled-state rejection and unchanged row positions. The native panel reloaded and its eight running drives resumed.

**Drive bank:** installed and verified in standalone Heart. All 70 backend tests pass, including focused scope/continuity checks; the actual server protocol also passes Family/Rate/Shuffle. Isolated UI checks cover compact scrolling, stable rows, pins across navigation/reload, offline targets and direct editing. Native UI selected harmonic and 2× for Figure LinearCloner, then performed row and layer Shuffle. Eight drives retained their ranges and undriven sibling controls were unchanged; bounded native reads confirmed motion continued. Test settings restored; eight drives running and LinearCloner pinned. See `checks/drive-bank-2026-09-11.json`. Use the standalone panel only; do not open a second live Heart panel in a browser.

**Source / bulk Drive evidence:** 73 backend tests and the isolated UI sequence pass. The standalone bank stopped seven unlocked LinearCloner drives while its temporarily locked running parameter continued. Bulk ON resumed those seven; ranges were unchanged and test locks were restored. Native playing-source identity matched Heart after a clip change. Newly loaded sources remain idle until Drive all or individual Drive is used. See `checks/source-follow-drive-all-2026-09-11.json`.

**Feedback range correction:** compared all 29 feedback clips with both Feedback Machine reference files. All 26 custom timeline In/Out ranges and 33 timeline sources were intact; 158 timing-field comparisons found no differences (live bounce direction excluded). Restored one static Scale mismatch on `FM · Feedback [1.1.1]` from 202.23% to the reference 105%. Heart now seeds new drive Low/High from native In/Out; Open no longer expands them. Explicit Heart range edits survive rediscovery, while untouched defaults follow native range changes. All 79 backend tests pass, and all 26 native ranges were rechecked after installation. Eighteen existing drives and edited ranges were restored; diagnostic Hold released. Actual output acceptance remains separate. See `checks/feedback-native-range-audit-2026-09-11.json`.

**Feedback signal-path repair:** the subsequent visual complaint exposed a separate shared-layer fault: feedback Transform Position X was static at −1288.835 pixels. Every clip inherited this displacement after its own motion. Centered it at 0; native before/after snapshots show the return centered again, and a motion capture confirms accumulating, moving trails. Current composition effects were bypassed except the final Mask. Clip timelines, MIDI assignments and the output mask were unchanged. The performer confirmed “Movement looks right again.” The earlier range tests alone did not establish visual correctness. See `checks/feedback-shared-transform-repair-2026-09-11.json`. When multiple clips fail together, inspect their shared layer/parent transforms, visibility/blend and downstream effects before editing individual clip programs.

**Motion evidence:** Five simultaneous Figure source/shared Transform drives sent 4,795 updates in the test; native sampled changes had a 13.5 ms p95 interval and 29 ms maximum, with no errors. Removed native WebSocket broadcast load (365 MB in eight seconds) and periodic full-grid reads while armed. 65 backend checks passed across the regression runs. Test settings and values restored; Heart remains armed. This measures parameter delivery, not rendered-frame cadence. See `checks/motion-delivery-2026-09-11.json`.

**Evidence:** Direct pad mouse/keyboard checks cover independent cross-layer toggles, rapid presses, retained pins and disabled missing targets. Live Delay Invert + Figure Twitch test passed; each switched independently, and their initial values were restored. 57 backend tests before the memory incident; isolated playing, surface regression and controller fixtures pass. Added subscription and reconnect limit tests pass with four affected regression tests. Earlier native clip handoff/grouped/fader checks remain historical evidence. The small native movement rig passed output acceptance on September 11; see MOVEMENT-TEST.md.

## Separate deferrals

**Hardware workflows:** trackpad four-fader/eight-pad use and custom controller layouts/Grab remain deferred. The separate big knob is a native master outside Heart.

**PS4:** navigation only. **Polish:** Boustrophedon material/aesthetic refinement follows functionality; operational legibility remains required.

Instrument, motion, effects, color and Base/Safe remain in scope. Stage accents are included through the dedicated Rack; stage mixing remains on native MIDI.

**Boundaries:** Portal/stage mixing, geometry and masks are handled elsewhere. Heart controls the requested Stage effect accents through the existing group. Feedback is an ordinary composition instrument. No new modulation engine or cross-composition reconstruction.

Detailed specification: [SHOW-FEATURE-PLAN-2026-09-11.md](SHOW-FEATURE-PLAN-2026-09-11.md). Phase 1 detail: [MVP-SPEC.md](MVP-SPEC.md). Phase 5 input check: [CONTROL-FOUNDATION-TEST.md](CONTROL-FOUNDATION-TEST.md).

**Performance Rack evidence:** all 83 backend tests passed, including exact linked identity, failed-gate cleanup, cancellation during a hit and automatic release through Hold. The compact/wide isolated interface checks passed. All nine live native hits reached approximately 0.8 and returned to exactly 0; the first observed nonzero values arrived 11–52 ms after command dispatch (sampling included). Standalone Stage Melt, Figure Twitch and Field/video Blok reached all intended destinations and released. Standalone Color set Stage/Figure/Field/video to 0.5; Clear returned the rows to neutral. Native preview remained masked. Layer order, group membership and existing non-clip parameter IDs were unchanged. A Field LUT instance that disappeared during setup was replaced and explicitly rebound; the old destination correctly disabled its linked row. Musical feel and full-show acceptance remain with the performer. See `checks/performance-rack-live-2026-09-11.json` and `checks/performance-rack-setup-2026-09-11.json`. Native effects are live in Resolume; saving the composition remains a user action.

**Authored clip correction:** Original now restores matched source and clip-effect programs from the saved Soup and Feedback Machine compositions. All 321 matched native timelines and 1,089 serialized controls across 178 clips passed current native verification; 202 timelines had become static and were repaired. Existing native timelines remain the default, with their bounds, duration, speed and playback shape. Native Shuffle permutes existing running loop timings/phases and preserves locks, paused/manual parameters and bounds. Musical Rate returns without compounding. Original is a reference return, not a preset library. Unmatched/default-only clips and unexposed/changed controls are explicitly listed in the audit; full visual equality has not been claimed. See AUTHORED-CLIPS.md.

- [x] **Original / Shuffle / Rate:** compact native clip controls installed. Live tests passed for locked timing, native ranges, rate return, pause preservation, manual takeover and Original recovery. Ten generic layer drives retained.
- [x] **Tap tempo:** fixed header Tap triggers native Resolume tap; native and Heart tempo both measured ~120 BPM from half-second taps. Restored to 60 BPM. Downbeat also triggers native resync.
- [x] **Decon / Pixel Melt rack:** replaces the earlier three-pad set. Stage, Figure and Field + video each have these two native triggers plus Color and Clear. All six live hits released to zero; a standalone Figure Pixel Melt press also reached 0.8 and released to zero. Native layer order and MIDI controls remain intact.
- [ ] **Performer visual acceptance:** compare familiar restored clips and play the new rack with music. Parameter agreement is verified; full rendered/show acceptance remains separate.
