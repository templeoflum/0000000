## 2026-09-09 — Effect readback and prototype boundaries

Effect envelopes now observe fresh native bypass/opacity during existing discovery polls. Idle envelope state follows Arena; active fades/pulses and newer gestures are protected from stale snapshots. Rack indicators use observed bypass and amount: Bypassed / On / Zero, with stored amount shown when bypassed. Refresh follows the existing approximately 3-second composition census, not a streaming guarantee. 172 engine tests pass including stale-readback and fade cases; live Hue Rotate, LUT Corrupt and ColourLoop bypass values agree, while animated opacity values naturally differ between separate samples.

User priorities: continue Figure then Field/processing live inventory; Glyph is new and out of current inventory priority. FPS is contextual screening only while unplugged/shared GPU. Build current prototype forward, but any shader source change must create a NEW shader identity/file so the original shader and old compositions continue to work. No shader modifications in this pass.

---

## 2026-09-08 — Play tabs and trackpad assignments

Correction: global Open now preserves every effect envelope target and level; it opens Smart Param drives without activating effects. Settle still fades effects out.

Play has Clips / Trackpad tabs with global performance controls remaining below both. Trackpad exposes the existing four-lane probe controller: layer assignment selectors, region-to-fader drag assignment, absolute / relative / spring behavior, and Grab trackpad. Assignment changes persist through the existing surface configuration. New assignments include layer-name guards so renamed/replaced targets become unavailable. Physical mouse-down after the grab grace period releases capture; Escape, blur, probe loss and pointer-lock loss also release. Grab is disabled without the probe, Resolume or an available assignment.

Verified 167 engine tests and 27 DOM checks, inline JavaScript syntax, and the live tab / four assignment selectors. No physical multi-finger performance test performed; user touch testing remains. Mixed two-fader/four-button layouts and arbitrary action destinations remain next-stage work, not implemented here. Existing assignments were left unchanged (currently unassigned).

---

## 2026-09-08 — Performance first: global Play

The shared-generator direction is withdrawn. Smart Params remain the motion system. Its unused prototype and UI hooks were removed from the engine; a rollback copy is in `sp/audit/play-global-before`.

Play now has composition-wide Settle all, Open all and Shuffle all, Hold/Resume, musical/irrational/stable shuffle selection, motion speed, tap BPM and downbeat. Existing per-target controls remain in A/B. Global gestures update existing integrators in memory without composition recall or per-parameter configuration persistence. Shuffle affects active, unlocked timing only; Settle rests Heart-owned controls, stops auto shuffle and fades all effect envelopes out. Open starts adapted numeric drives and effect motion, preserving Figure framing limits. These gestures are live controls, not saved scenes.

Verified: 166 engine tests and 25 DOM checks. Live Shuffle affected 49 controls with the clock advancing; Settle left zero active drives. Prior Heart settings restored. Open-all coverage is automated only: full live expansion of all 217 effect controls remains unverified. Content has not yet been reorganized or comprehensively audited.

Next: back up and inventory Soup, sort misplaced content within its existing layer roles, audit source control compatibility and GPU behavior in batches. Prioritize a coherent playable set for departure. Defer preset redesign, generator architecture and analytics.

---

# Execution checklist

## Current direction — modulation instrument; audit complete

[Audited roadmap](modulation-instrument/README.md) supersedes scene-first tuning. Confirmed original catalog/kit references, per-Slot oscillator coupling, family-definition differences and current JSON limitations. Reuse integrated phase, ownership/adapters, delivery, surface and non-reloading JSON; introduce persistent generator IDs and explicit routes. Next: one shared generator driving source + Cloner across destination/clip changes, then graph presets and expression. Audit changed documentation only; no live state or engine code changed.


## September 8 — JSON-only performance presets

Main bar now applies named JSON source/effect settings with transition time and Undo. Composition loading moved under Setup / recovery. New Live warp preset saved and live-tested: identical Arena composition identity, continuous connection/motion, restored parameter, no setup operation. 161 Python and 24 DOM checks pass. [Implementation, scope and evidence](json-presets/README.md). Prior full-patch studies are setup snapshots, not lightweight performance presets.


## September 8 — depth studies rejected; fluid-warp revision

User rejected the first depth studies as too slow/jumpy. Corrected 32–64-second Cloner periods, inherited triangle shape and multipliers. Saved Fluid warp - 3D/Shell/Seed with explicit cosine curves and 4–6-second Cloner periods, broader motion and source speed 1. User acceptance remains pending; still images and state traces do not prove rendered smoothness. [Evidence and limits](pilot-refinement/fluid-warp/README.md).


## September 8 — three saved depth-study candidates

Built Depth study - 3D, Depth study - Shell and Depth study - Seed with four bounded Cloner relationships, static density, resting Sculpt and original Map Zoom/Rotate. Reviewed native full-output images and removed inherited effects that obscured the study. Seed shows the clearest repeated depth spread; 3D needs further spacing exploration. Restored current scene with matching relationships/tempo/Hold. [Recipes, images and limits](pilot-refinement/depth-study/README.md).


## September 8 — pilot switching and full effect-motion recovery

Fixed a live save blocker for Arena native Feedback sources while retaining dependency validation; 154 engine checks pass. Fresh save → Figure depth → 3D/Shell/Seed motion checks → current-scene recovery completed. Exact source and Linear Cloner motion relationships, tempo and Hold matched after restore. This verifies the newer effect-motion recall, not full artistic or sustained-GPU acceptance. [Evidence and remaining work](pilot-refinement/README.md).


## Current next steps — September 8

Delay pattern shortcuts are now visible beside source parameters and in the effect pane: Shuffle taps, Reset taps and Golden taps send the existing native ParamEvent actions. They are separate from Heart motion Home/Shuffle. Unique clip-effect resolution, instance replacement and ambiguity guards are covered; 24 workspace checks pass. Native Heart refreshed and all three buttons verified in the Delay source view; no pattern fired during inspection.

Fader physical-click release is activated and user accepted; hover scrolling no longer captures, and saved per-fader spring milliseconds are visible. Monitor design remains frozen. Next: refine 3D/Shell/Seed with Cloner/Sculpt/Delay/Feedback, verify whole-patch recall including effect motion, then expand in complete 3–5-source batches. Home rests; Open explores. Earlier Home-motion wording in the original plan is superseded by home-open/README.md. Full-resolution sustained performance and broad manual containment remain unverified.


## September 8 — performance quality of life

Click-latched faders, immediate effect triggers, Composition/Selected layer rack shortcuts, and complete layer-label refreshes are implemented. 153 Python and 23 DOM checks pass. Native Force Touch pressure support is built but awaiting approval for app restart; ordinary click-again release loads via surface refresh. [Details](performance-qol.md).

## September 8 — separate Home and Open

Home now rests the selected target and fades a selected effect out. Open explicitly enables numeric drives and full ranges while retaining timing and Figure framing bounds. Set Home records the visible resting pose; both actions support Undo. 150 engine and 22 DOM checks pass; updated controls loaded and verified in native Heart. [Behavior and evidence](home-open/README.md).

## September 8 — musical performance surface and shared effect motion

Implemented combined A/B with independent scrolling/targets, separate clip library, all-eight-layer Play, tap BPM/downbeat with real drive alignment, shared numeric effect drives/Home/relationships, opposite-direction pulses, and captured scroll/hold fader gestures. Existing native automation is preserved until explicit takeover. 146 engine checks, 21 DOM checks, pointer/fader/resume and native session/TV checks pass. Native End Scale motion and 1→0→1 pulse readback verified; user's ongoing scene/tempo retained. Beatpad remains inactive and usage recording deferred. Details, recovery and remaining live recall/artistic limits: [performance-pass/README.md](performance-pass/README.md).

**Current direction: [Heart + Generative Soup — one coherent instrument](COHERENT-INSTRUMENT-PLAN.md), agreed September 8.** Its next milestone is three playable Figure sources through the complete stack. Figure containment is source-only; downstream effects may extend offscreen. Entries and phase statuses below retain the historical implementation record.

Execution underway. The earlier apparent lock was a thermal-sleep incident (see sleep-incident/README.md). Native access recovered. Snapshot save/clear/recall/reconnect now passes for four instruments; full performance acceptance remains pending. No phase is marked complete solely because its code exists.

| Phase | Status | Exit evidence |
|---|---|---|
| 0 — baseline and recovery | Baseline saved; GPU/routing checks pending | Restorable composition/config copy, inventory, routing and performance baseline |
| 1 — control foundation | Implemented core adapters; 29 checks pass; full migration/ownership coverage still pending | Identity/migration/reconnect/ownership checks |
| 2 — performance surface | Navigation and effect panels verified in browser; native interaction checks pending | All layers and existing effects playable without Edit |
| 3 — feedback instrument | Separate loop instrument staged; buffer reset passes GPU correctness test; live tuning pending | Reviewed movement/color behaviors and verified reset |
| 4 — starting patch and recall | Four-instrument save/clear/recall/reconnect passed; Start saved; reliability acceptance still pending | Cold start, partial-failure recovery and performance session |
| 5 — remaining current instruments | Pending | Clip readiness matrix and reviewed Homes |
| 6 — shader families | Pending | First 3–5-candidate family reviewed and measured |
| 7 — hardware and mappings | Pending | Available-device tests; Portal/Treehouse mapping audit |
| 8 — monitor and configuration | Detached TV live; compact borderless Trinitron-inspired revision underway | Dock/undock, window and performance checks |

First execution release: phases 0–4. Later phases follow the same target and manifest contracts.

## Initial worker work orders

1. Inventory worker/script: compare current live/saved Soup, installed dependencies and reference stacks. Produce exact differences; no live writes.
2. Identity review worker: extract repeated parameter/effect names and legacy preset shapes from isolated inputs; propose migration examples and mark ambiguities. Primary assistant owns the schema decision.
3. Feedback worker: extract old movement/color source settings and automation with source references. Do not guess routing enum meanings or artistic equivalence.
4. Validation worker/script: build fixture cases for duplicate identities, missing targets, interrupted recall and reconnect generation changes. Primary assistant reviews whether each checks real behavior.

Dispatch only when inputs are available. Local inference must finish and unload before visual-performance measurements. General-purpose worker queue implementation is deferred.

## Current handoff

- Baseline: `baseline/manifest.json`, `baseline/live-saved.avc`, `baseline/live-composition.json`, installed effect/source lists and local API schema. Recovery instructions in `baseline/RESTORE.md`. No Git repository is present.
- Code: `sp/engine/targets.py`, `patches.py`, `heart.py`, `delivery.py`, `status.html`, `test_targets.py` and updated effect-key expectations in `test_heart.py`.
- New target adapters cover source/clip/layer/group/composition discovery, repeated-effect scoping and typed conversion. Numeric SP atom slots preserve distinct identities; instance-specific control settings now use `controls.json`. Legacy motion settings are read as fallback and scoped on the next write.
- Surface: visible per-layer previous/next/random/clear, clip/group effects, effect parameter panels, linked Blur/Sharpen, active-drive counts, factory Home through right-click on Return home, and saved-patch controls. Recall and Start remain disabled until validated.
- Native monitor binary has not changed. Its currently loaded web page may require reopening the monitor after unlocking to load new surface markup.
- Remaining engineering gaps before phase 1 completion: broader ownership monitoring for automation changed in Resolume after initial discovery, and verified compatibility for reordered indistinguishable duplicate effects. Legacy duplicate Drive-slot groups now have qualified names and a regression check; complete real-composition migration validation remains pending. Their current occurrence identities cannot prove a swap of identical instances.
- Remaining phase 2 gap: curated performance banks still use the existing populated-clip list.
- Current composition is idle following the diagnostic clear. Diagnostic snapshot saved as `Connection check`; no finished Start patch was promoted.

Next: unlock and inspect Resolume for any pending dialog/open. Resolve the snapshot-open timeout, verify save/clear/recall end to end, then render/tune the feedback behaviors and establish a verified reset and Start patch. Finish full-resolution performance samples and the 20-minute acceptance session with workers unloaded. Continue outstanding control-foundation coverage before claiming the first release.

## Latest validation

25 automated checks pass, including duplicate atom/legacy slot identities, typed conversion, competing/cancelled operations, snapshot dependency preflight, overlapping effect owners and release across parameter-ID replacement. JavaScript syntax check passes. Browser inspection confirmed navigation, layer effect placement and a full Hue Rotate parameter panel.

Idle samples before/after: median engine cadence 238.7/239.2 Hz; median reported worst-work interval 0.03/0.07 ms; queue stayed zero in both. These are short idle control-engine measurements, not GPU or rendered-output acceptance. No local models remain loaded.

The local phase-source API was verified read-only. At clip takeover, existing Resolume automation is preserved and those slots are not written by Heart; explicit Home/manual/drive takeover switches their phase source to static. Trigger parameters use the documented trigger endpoint.


## September 7, 16:35 continuation

- Native Heart explicitly releases capture and stops Syphon/Metal work on system sleep, screen sleep and session deactivation. Wake notifications alone do not resume it. A visible Resume monitor button is added; Heart motion remains separately held. Native notification tests pass without actual OS sleep. This does not suspend Arena or solve the machine's underlying thermal incident.
- 29 Python checks pass, including four snapshot-open verification/cancellation checks. Existing Home file ResourceWarnings remain.
- Four-instrument Start/Studio start snapshots saved and exercised with map (6 drives), level (7), ground (18), shell (30). Save, clear, recall and reconnect succeeded; full-load queue transiently reached 74 and subsequently drained to zero. Recall is enabled while connected and no patch operation is active. Repeat/cancel/failure/performance acceptance is not complete.
- Engine upgrade now preserves Hold, so restarting the engine does not undo the post-sleep hold.
- User reported apparent Resolume freeze during this pass. Arena REST and output snapshot respond; a two-second sample showed main-thread event-loop activity, not a demonstrated deadlock. Heart monitor was paused after sleep and telemetry was stale. Pause telemetry now updates with zero FPS/suspended=true. This is a confirmed monitor defect; it does not rule out an intermittent Arena UI stall. Motion temporarily held during diagnosis. No new thermal sleep events found in the checked interval.
- Corrected routing: map L1C1 Video Router Input = sculpt; level L2C1 Input = Group 1 (NOT composition). Group 1 contains field, delay, figure and glyph according to saved XML. Map source and installed resource match and contain persistent acc buffer; Study Level is not persistent. Map's trailing history is internal to its shader. Effects after Map, including its native clip FX and staged L1 FX, process output rather than the internal history. Reset must target the actual persistent buffer.
- Next: verify Resume monitor in the updated build and clarify whether the reported freeze includes Arena's own UI. Then tune feedback behaviors and implement/test true buffer reset. Do not describe phases 0–4 as finished; matched 60-second samples and a full performance session remain undone.


## Visual state feedback — September 7

Added a persistent connection/motion/pointer status row, explicit MOTION HELD and stale-status states, immediate Sent feedback followed by engine events, patch operation stage and elapsed time, per-card morph countdown/progress, named effect state and amount, and explicit bypass labels. Whole-patch versus Motion Home scope is explained in labels/tooltips. Uses the existing status stream; no additional renderer polling or GPU loop. Python checks: 30 pass. JavaScript syntax passes; native window visually inspected with five active clips, 70 enabled drives, readable effect states, 1080p/60 monitor snapshot. This snapshot is not a performance acceptance sample. Current performance and user edits preserved during the engine update; no composition recall was performed for this UI pass.

## Parallel feedback / TV continuation — September 7

- Phase 3: separately identified SP Heart Feedback instrument staged, inactive, at L1C6; original Map remains active. Added history-path color/fold/detail/RGB decay and Turn/Drift/Breathe/Fold relationship candidates. Native Reset trails event is exposed; persistent-latch reset passes offscreen GPU correctness tests. Working composition saved after updating trigger schema. See `feedback-instrument/README.md`. Live artistic review and full-resolution performance acceptance remain pending. RGB decay does not reproduce native Delay RGB timing.
- Phase 8, explicitly requested alongside phase 3: native detached retro TV implemented by an independent worker. One original Syphon/Metal view moves between controller and TV. Live detach and floating window level verified; screenshot showed 1920×1080/60 FPS at that moment, not a sustained performance result. Window is resizable, picture double-click enlarges/restores, Dock TV returns it to Heart. Sleep suspension is preserved and no wake assertion added. See `sp/monitor/TV.md` for controls and test limits.
- Thirty engine checks pass after feedback integration. Existing Home file ResourceWarnings remain. Current six playing clips and motion state preserved during engine update; no Start recall or replacement of the playing Map was performed.

## Heart Monitor identity / ergonomics refinement

The detached display is now a Boustrophedon Instrument Co. **Heart Monitor**, grounded in `/Users/donovan/work/met3or/CANON.md` and the canonical Rev E physical panel. Added the source maker mark, warm aluminum palette, molded physical button caps and an inset readout. User's final placement puts buttons on the bottom silver fascia, with the dark readout separate above. Independent small/expanded window rectangles persist; hidden isolated-preference tests cover custom size/position restore and offscreen recovery. Live inspection verified the borderless face and a double-click return to the small view. Geometry restoration across launches is covered by isolated tests, not a full live relaunch acceptance run. Source resolution and the original single renderer remain unchanged.

## Parallel work restored during physical monitor redesign

Monitor visual work delegated; root resumed feedback validation. Actual staged Arena schema revealed Reset trails was dropped by numeric-only instrument discovery. Fixed event retention without adding an animated slot. Added native-schema regression checks for one-shot event delivery, replacement IDs, native parameter bounds, and stable behavior relationships under reordered/extended parameter layouts. 33 engine checks pass. Live trigger delivery to the inactive candidate succeeded; engine fix loaded while preserving six playing clips (connected, queue zero at ready check). Artistic review and active-render reset observation remain pending; no replacement of playing Map.

## Physical enclosure pass — completed

Independent worker rebuilt the monitor as a layered charcoal enclosure with feet, inset screen molding, brushed aluminum fascia, engraved button labels, raised caps with pressed travel and a separate pin indicator lens. Offline small/large/pressed/minimum-size Resume specimens reviewed before loading. Native window/geometry/button/sleep checks pass. Root reloaded only Heart's monitor, visually verified live video in the new face, and exercised Pin off/on with matching lens/state; left it pinned. Decorative geometry remains static and outside the source video. Full GPU/performance acceptance remains pending, and no sustained gain is claimed from spot FPS readouts.

## Main instrument resumed — September 7

Monitor accepted by the user and frozen; no further enclosure work in this pass.

- Activated and reviewed the separate SP Heart Feedback candidate at L1C6 after saving **Before feedback review**. Turn, Drift, Breathe and Fold were exercised live; snapshots and drive states are in `feedback-instrument/behavior-live-checks.json`. Reset reached the playing native event; precise native-buffer readback is not claimed (offscreen buffer correctness is separately tested). Original Map remains available at L1C1.
- Saved **Feedback performance** separately; Start and Studio start were not overwritten. Two consecutive recalls, including the already-open composition, reached Ready and restored six instruments/drives. Clearing all eight layers then recalling also restored the six instruments. See `feedback-instrument/repeated-recall-live.json`.
- Recall coordinator now requires acknowledgement or a fresh native open transition, covers queued work with busy state, protects newer operations against stale completion, and provides nonblocking status snapshots. Explicit slot identities cannot fall back to ambiguous names. Already-issued native open requests remain non-revocable; cancellation does not promise to undo them. See `recall-audit.md`.
- Native motion ownership is now observed off the motion loop. External automation releases Heart's drive and pending writes; explicit Home/drive-on reclaims it. Live Loop Hue takeover released in **2.342 seconds**, remained released after native automation stopped, and factory Home restored native static ownership and Heart drive. See `ownership-live.json` and `ownership-audit.md`. This live check did not cover every reconnect/ID-replacement scenario; isolated tests cover stale response guards.
- **70 engine tests pass**, including 21 ownership tests. New engine loaded preserving all six instruments; Arena and monitor were not restarted.
- Four 60-second full-resolution acquisition samples (Map, new feedback, native RGB Delay, empty scene) stayed at median 60 FPS with no >100ms intervals. Idle system GPU still measured 51%; attribution is unresolved. The telemetry reads AGX `Device Utilization %` directly and reports the whole Mac. A process snapshot shows Arena, WindowServer, WebKit and ChatGPT activity, but CPU usage does not establish GPU attribution. Do not blame a shader or app from this evidence alone.

Remaining release gates: matched renderer/Heart baseline and sustained 20-minute performance acceptance; full native plugin/routing preflight; remaining reference-feedback effect equivalence (RGB decay is not temporal channel delay). Keep these open rather than marking phases 0–4 complete.

Post-upgrade ownership-enabled 60-second sample: median 59.99 FPS, p95 18.28 ms, no >100 ms acquisition intervals, fresh visible 1080p throughout.

## Sleep resume repair

User reported motion could not resume after sleep. Live inspection found the engine connected and held while native telemetry remained session-suspended. Clicking Resume motion advanced H and parameter delivery, but the picture remained suspended: the two separate resume paths made successful motion look frozen. Resume motion now also sends the trusted native bridge an explicit monitor-resume request, retaining the active-app check and no automatic wake resume. Monitor-only Resume remains available. Reloaded the monitor only; verified live 1080p/60 acquisition and advancing engine motion. Native session checks and the connected/disconnected/browser Resume bridge regression checks pass. No real sleep cycle was induced and no wake assertion or OS sleep setting was changed.

## GPU isolation and native shaping restoration

- Saved **Before GPU comparison**, confirmed all eight layers empty, then measured AGX independently for 30 seconds per condition: display visible 54% median; display app closed 48%; reopened/detached 65%. Native process absence and stopped telemetry confirmed the closed interval. Visible samples varied too much to estimate precise display overhead. Substantial system GPU load persists without the display or active clips; Arena/background/window composition attribution remains open. All six instruments restored afterward. See performance/README.md.
- Independent read-only routing audit identified missing native output InvertRGB → Blur → Sharpen on the candidate. Added those installed effects after SPHeartFeedback, retaining original Map unchanged. Copied native parameter/mixer values from Map, except Opacity starts zero and bypass true. In particular copied Sharpen Strength is zero; its control is available for deliberate adjustment, not an invented sweet spot.
- All three effects and the linked Blur + Sharpen toggle passed live Heart envelope/bypass on/off checks. Returned to bypass and saved separately as **Feedback shaping**. No controlled visual-equivalence claim; output effects remain downstream of persistent shader history. Evidence: feedback-instrument/restored-native-shaping.json and shaping-live-checks.json. Existing Start and Feedback performance preserved.
- Remaining routing contract, plugin preflight, native timing/masking equivalence and sustained performance gates are itemized in feedback-instrument/remaining-gaps.md. Its priority-1 missing-stack finding is now addressed for the current Feedback shaping revision; artistic tuning and performance measurement of active stack combinations remain open.

## Dependency-checked recall

Added `sp/engine/dependencies.py` with a versioned contract covering active-deck instruments, required native source/effect identifiers, composition/source dimensions, scoped effect order, layer order, group membership and serialized Video Router settings. Inactive library clips do not become unnecessary required plugins. UUID case is normalized; display labels do not substitute for plugin IDs. Texture's omitted Input is preserved as native default serialization, not assigned a guessed semantic endpoint.

New saves validate installed dependencies and a fresh native snapshot before writing the named patch, then embed the contract. Existing patches without one derive it from their archived native snapshot. Recall rejects missing installed requirements before opening; after restoring layers it captures a fresh native readback and verifies dependencies/routing before applying motion relationships. Failed post-open verification enters existing recovery rather than reporting Ready. REST omits router inputs/native plugin identity here, so an archived file alone never counts as live verification.

The non-opening native readback removes any stale verification file first and restores the displayed composition name only if its runtime generation is unchanged. Save errors cannot silently reuse old evidence. No renderer restart or monitor change. Native document save-destination behavior beyond the restored name has not been separately tested.

Offline suite: **96 tests pass**, including 21 dependency checks, fresh-readback name/generation checks, and integration checks that missing plugins abort before save/open and routing failure recovers before requested motion is applied. New separately saved **Feedback checked** includes native shaping and the dependency contract; previous named patches remain available. Final live results are in dependency-live-checks.json. GPU per-process attribution remains unavailable without administrator authentication; no password or OS setting changes requested. Full sustained performance acceptance remains open.

## Start selection and acceptance preparation

Added compact **Use as Start** next to the patch chooser. It persists the selected target without recalling or overwriting a composition. Start displays its exact target, uses the acknowledged saved configuration, and disables a missing target rather than falling back silently. Configured **Feedback checked**; original Start preserved. Reconnected/reloaded UI displayed the target correctly and an actual native-window button click restored six instruments/47 drives to Ready. Isolated browser checks cover save acknowledgement, missing target, disconnect, reconnect and text safety.

Independent offline inventory corrected the bank count to **37 populated clips**: 25 atom instruments, 8 legacy relationship instruments, 3 static routes/sources and one diagnostic. Home availability/evidence and the first refinement batch are recorded in instrument-readiness.md. A scoped Home storage helper and 13 isolated tests are prepared in home_store.py/scoped-home-plan.md but deliberately **not integrated**: no runtime Home migration or change to existing Home resolution has occurred. Ambiguous legacy name handling and integration guards remain next work.

The held-effect audit fixed reconnect/ID-replacement return ownership and stale deferred returns overriding newer manual input. release_all now also unwinds owned preset visits against the exact current clip. New tests distinguish a parameter rebind of the same native effect from a new composition/effect that should keep its own observed state. Details/limits are in effect-ownership-audit.md. Runtime integration and live checks are recorded below when completed.

## Sustained run and effect-release live validation

Completed the 20-minute 1080p action/acquisition run. Median 60.00 FPS; p95 interval 18.19 ms; no >100 ms acquired gaps; all 1,201 samples visible/fresh. However minimum one-second FPS was **39**, and **172 samples (14.3%) were below 55**. Dips also occurred outside recalls. Median/frame-gap budgets pass; consistently smooth 60 FPS and GPU attribution remain open. Detailed limits and command coverage are in performance/README.md and acceptance-summary.json. No OS sleep settings or wake assertions changed.

After the timed sample, loaded the effect-ownership fixes preserving current instruments, then verified through Heart plus native opacity readback: two clients hold/release in overlapping order and restore a nonzero baseline; newer manual value survives late release; disconnect restores held baseline; reconnect restores held baseline. Original Blur mode/settings/amount restored in cleanup. Evidence: effect-ownership-live.json. A subsequent 60-second sample passed median/p95/gap thresholds, but is not a repeat of the full sustained run on the revised build.

Full offline suite **120 passing tests** (107 integrated engine checks + 13 prepared/unintegrated Home-store checks); Start-selection and sleep-resume browser checks also pass. Current setup is Feedback checked with six instruments/47 drives, shaping effects returned off, and Start configured to that patch. Remaining release work: characterize persistent FPS dips/GPU load, physical gesture/focus and full cold-launch acceptance, recall cancellation limitations already documented, Home-store integration, and remaining artistic/native feedback equivalence. Multi-client same-pad preset visits remain a separate known ownership limitation; removed variation UI stays removed.

## User priority correction

User reports ~3% account usage remaining and prioritizes a working shader instrument/library. Further GPU attribution and release polishing are deferred. Immediate order: cover missing bindings and usable Homes across the existing bank (17 fallback Homes identified), connect remaining source/shader batches to the shared instrument format, then restore Portal/Treehouse relationships and available hardware actions. Reuse inventory and helpers already produced; avoid another audit/planning cycle. Performance work is limited to faults that stop practical use. This expands implementation beyond the earlier phases 0–4 gate sequence.

## Original Portal/Treehouse restoration correction

User clarified: restore the existing original compositions by linking their images from Movies/infra before any new Portal/Treehouse mapping work. Created sp/restored-compositions/portal.avc and treehouse.avc, with all image-path references resolved (857 and 3198 distinct old path strings respectively; some strings refer to the same physical file). Verified only image-path attribute values changed and targets exist. Original files unchanged; not loaded into Arena. Video-library references and native playback remain unverified. Hardware/mapping redesign is not the next step.

### 2026-09-07 — Consolidated restored media links

Both restored compositions now use `work/Visuals/infra` (2,464 identical image files verified). Portal links 290 strong video matches in `work/Visuals`; 5 uncertain candidates and 140 missing videos remain unchanged. Original Documents compositions preserved. This update changes only media paths relative to the latest restored copies, preserving their existing content. See `sp/restored-compositions/README.md`. Native playback pending.

## Soup evolution — reference bank and stacks restored

User chose to retain Soup layout and adapt Feedback Machine by role. Saved the normal Generative Soup composition with all 245 reference clips appended in its active deck and 43 persistent rack instances adapted to Soup layers. Existing Soup clips/routing retained; new rack effects start bypassed. All 159 external dependencies installed; native readback preserves imported plugin identities and effect order; Heart sees 43 controls and is reconnected/unheld. Two representative shaders visibly render at 1080p; previous idle scene restored. Per-shader Home design and full artistic/performance review remain separate work. Recovery and full mapping: `sp/restored-compositions/soup-restoration/README.md`.

## September 8 — coherent instrument direction recorded

Documented the agreed five-step execution plan in `COHERENT-INSTRUMENT-PLAN.md` and linked it from the specification and progress entry points. The critical rule is source-only Figure containment; Linear Cloner and other downstream effects may intentionally extend offscreen. First milestone: 3D, shell and one imported Figure source playable through the full stack from Heart. Updated stale media-location/priority wording and corrected the fader layout description to two rows of four. Documentation only in this pass; no engine, composition or runtime changes.

## September 8 — first coherent Figure revision implemented

Shared role/source definitions now drive Homes and the three-source Forms bank (3D, Shell, Seed/z33d+). All sources remain accessible. Fixed Shell's underestimated 4D projection bound with geometry/AA reserves and a separate source margin; installed source and generator updated. Downstream effects remain unrestricted. 125 engine checks and JS syntax pass. 34 source GPU phase/extreme cases pass at 640×360; native 1080p playback/motion and cloner output inspected. Complete Homes have 13/18/6 drives. **Figure depth** saved, selected as Start and successfully recalled to Ready with Figure → existing Group/Sculpt → Map feedback path. All earlier patches/recovery copies retained. This is a playable first revision, not exhaustive artistic/performance acceptance. See `figure-milestone/README.md` for evidence, local worker review disposition and remaining manual-range/portrait/UI limits.


## September 8 — modular surface, first pass

The six-area workspace is running: faders, Play controls, effects rack, native monitor dock, and two independently targeted parameter panes. Arrangement/pins save separately from musical patches. Full effect parameters are directly accessible in native units; native automation takeover on explicit manual edits is fixed. Source motion controls reuse the existing engine. Stale gestures reject replaced instances. The monitor's upside-down sampling is corrected in its existing GPU pass.

130 engine checks plus native dock/session/pointer checks pass; browser tests cover pinning, exchange/reset/reload and the 1100×700 layout. [Evidence and limitations](modular-surface/README.md). Next is Linear Cloner's Heart drives/Home/relationship integration, followed by pilot refinement; those are not implemented by this layout pass.
