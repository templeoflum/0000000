# Heart — generic instrument controller, dependency-led show build

**Latest decisions:** native Resolume mappings handle Grid faders/knobs and the separate master knob. Heart prioritizes clip navigation, modulation relationships and movement; PS4 operates that interface. Recovery means one Base and one Safe state, without a preset library. These decisions supersede the broader controller/recall descriptions below.

**Current execution plan:** [SHOW-CHECKLIST.md](SHOW-CHECKLIST.md). Complete Heart with mouse and keyboard first: playing workflow, instrument controls, recall/recovery and actual output. Whole-Grid mapping and PS4 navigation are the final integration phase. The entire show feature set remains required. Separate big knob, trackpad and custom layout/Grab workflows remain deferred.

Current checklist: [SHOW-CHECKLIST.md](SHOW-CHECKLIST.md). It separates implemented features from live acceptance and keeps the full build visible.

September 11, 2026. Performance at 23:00; work is ordered by dependencies and constraints, not time blocks. User explicitly says this is a build/test session and test state/mappings need not be preserved. Existing content and output geometry remain valuable project assets.

## Governing design contract

[INTERACTION-CONTRACT.md](INTERACTION-CONTRACT.md) defines compact spatial UI, cognitive-design/no-narrator-bleed rules, required multitouch trackpad, PS4 and knob/fader mapping, generic capabilities and transferable naming/organization. Soup, Feedback Machine and Portal are acceptance examples. Stage Mapping is the reusable feature; Portal is one configuration. Latest priority is a complete functional Heart interface using the existing engine. Necessary backend work accompanies each feature; external hardware integration comes last. Visual refinement follows functionality.

## Evidence and scope

Fresh read-only Resolume inventory: Heart Portal Native, 26 layers, 2 groups, 3 decks, active deck Gradient. Eight Soup roles, 17 Portal members in `__stage__ Portal Frame`, and a separate Portal stage-mask layer. Feedback has 34 loaded clips, field 92, figure 75. Most of the reference processing is already installed: native feedback shaping, clone/mirror/iteration/displacement racks and composition accents. The restoration record reports 245 Feedback Machine clips and 43 rack instances imported; this is historical import evidence, not a fresh playback certification of every clip.

V2 source and deployed behavior take precedence over old v1 completion reports. No composition switching or new visual rehearsal was performed for this audit. Router parameters were absent in the returned sourceparams of inspected routing clips; routing is unverified, not presumed broken. Historical Portal reports list unresolved videos; tonight's selected media require a fresh check, rather than treating that old count as today's show blocker.

## Outcome

From Heart, play a complete visual phrase: select sources, mix them, grow and erase feedback, apply accents, operate a stage configuration, recover a useful state, and continue without interrupting unrelated motion or hunting in Resolume. Keep generic full parameter access. No clip-specific range restrictions or replacement modulation engine.

## Foundation — unlocks every performance surface

| ID | Feature | Why / evidence | Acceptance |
|---|---|---|---|
| F0 | Spatial UI and transferable conventions | Stable performance map, brief labels, direct gestures, progressive detail; roles/capabilities instead of composition-specific logic. See INTERACTION-CONTRACT.md. | Actual native viewport is playable without outer-page scrolling; a second differently organized instrument/stage uses the same code. |
| F1 | Scoped clip handoff | Implemented: clip launch releases only outgoing clip contracts, retaining unrelated phase, envelopes and output claims. Stale scans and queued writes are fenced. | Automated replacement/ownership tests pass; native Figure launch preserved Field drive in actual Resolume readback. Combined drive + effect-envelope show-load rehearsal remains. |
| F2 | Whole-Grid mapping and PS4 navigation input | Direct mappings for faders, knobs and buttons; saved bindings and grouped opacity controls. Custom layouts/Grab, separate big knob and trackpad are deferred workflows. | Physical Grid controls operate native parameters and shared actions independently and together. PS4 input reaches the frontend; navigation acceptance belongs to F0. |
| F3 | Common mappable actions | Reuse existing backend commands for bypass, reset where supported, launch, IN/OUT, Hold and Home. | The same action is reachable through Heart and mapped Grid controls, with correct continuous or press/release semantics. PS4 operates UI navigation, not dedicated effect bindings. |
| F4 | Visible target and effective state | Owned numeric values are commanded state; passive state is catalog-based. Portal group currently has master 0 and opacity 1, illustrating why one level alone cannot explain visibility. | Show exact destination and relevant hidden/master/opacity states, pending/error and motion owner where supported. Do not label commanded values universal native readback. |
| F5 | Missing typed controls, especially color | `scan.py` excludes ParamColor. Portal Solid Color/Gradient and composition accent colors therefore lack direct v2 access. | Native color read/edit in A/B and selected performance controls, preserving alpha. Numeric drives remain numeric. |

Latest user priority: Heart must work completely with mouse and keyboard before controllers are integrated. F0/F4 supply the usable interface and target clarity throughout; required backend fixes accompany each feature. F1 and shared F3 actions support normal UI use now. F2 physical mapping is final integration. F5 remains general typed-control access. The Boustrophedon material studies and visual specimen remain optional polish.

## Performance surfaces — built on that foundation

| ID | Feature | Dependencies | Acceptance |
|---|---|---|---|
| P1 | All-layer playing strip | F0, F1, F3 | Current clip, previous/next/random among eligible clips, explicit eject, level/hidden and layer selection accessible across a bank of discovered layers; Soup’s eight roles are one test case. Search/favorites or small selected banks prevent browsing a thousand entries. |
| P2 | Compact scoped FX rack | F0, F3, F4 | See active layer/group/composition effects together; direct bypass and IN/OUT, optional momentary mode, linked actions such as Blur/Sharpen. A/B remains the detailed editor. Bypass and opacity have explicit separate semantics. |
| P3 | Feedback capability view | F0, F3, P1/P2 plus route inspection | Reach existing movement/gain/decay/reset and native shaping controls; verify input path, accumulation, reset and recovery with actual output. Surface Hold is visibly different from freezing/clearing feedback history. |
| P4 | Stage opacity controls | F0, F3; grouped-control backend | Configure opacity sets for stage regions, plus relevant outline/background/master opacity. Stage Mapping does not own feedback. A grabbed performance layout can combine these controls with ordinary content and feedback-layer controls. Geometry, masks and other stage editing remain elsewhere. |
| P5 | Base and Safe returns | F1, F3, F4, P1/P3/P4 | Explicitly capture a useful Base and define a Safe recovery state for the current composition. Restore only validated scoped controls. No look library or general preset system. Output geometry is excluded; missing dependencies are reported. |

P3 is a performance view over real existing controls, not a speculative replacement of shader feedback. Native output DelayRGB is not internal temporal channel delay; effects after a private history buffer are not automatically in its recurrence path.

P5 starts with the current working composition. General cross-composition reconstruction, migration of every historical preset and a new dependency-manifest framework are outside the minimum show build.

## Execution order

1. Deliver P1/P2 inside F0/F4: layer playing, focused browsing, scoped FX rack, A/B detail and effective state. Use shared F3 actions and existing F1 handoff. Repair backend gaps as each mouse/keyboard workflow requires them.
2. Deliver P3/P4 and F5: actual feedback capabilities/routing, generic stage opacity sets and native color. Preserve full generative/motion controls, including scoped Rate/Intensity independent of dedicated hardware.
3. Complete P5 Base and Safe returns, preserving unrelated motion and output geometry.
4. Verify the complete Heart performance phrase with mouse and keyboard, intended media and actual output. Resolve application and routing blockers before mapping hardware.
5. Integrate F2: map all intended Grid faders/knobs/buttons and PS4 navigation onto the working controls. Reuse the same backend actions. Check persistence/reconnect and repeat the phrase with hardware.

Each phase has a complete usable outcome in SHOW-CHECKLIST.md. Heart's feature set is independent of external controllers. Hardware integration changes access to working functions; it must not supply otherwise missing instrument behavior. No custom layout/Grab or comprehensive controller matrix prerequisite.

## Release constraint

The build is usable for tonight when the selected workflow can be repeated end-to-end without losing unrelated motion, confusing destinations, stuck effects or an unrecoverable feedback/output state. Demonstrate real hardware and full output at the actual show dimensions under representative combined load. Use observed delivery gaps and visual behavior, not engine tick rates alone.

Feature scope shrinks before rehearsal coverage does. Unrequired new shaders, exhaustive archive repairs, a new modulation architecture, arbitrary draggable workspace layout systems, and general-purpose cross-composition recall remain outside this dependency chain.

## Source records

- Current implementation: `server.py`, `scan.py`, `index.html`, `UPDATE-2026-09-11.md`.
- Fresh read-only composition: `/tmp/heart-show-audit-live.json`.
- Import evidence: `../restored-compositions/soup-restoration/README.md`.
- Feedback differences and earlier work: `../design/heart-performance-plan/feedback-instrument/remaining-gaps.md` and `README.md`.
- Original comparison: `../design/feedback-machine-comparison/README.md` (historical, before later imports).
- Portal archive limits: `../restored-compositions/README.md`, `../show-day/integration/STATUS.md`.

## Implementation progress

F1 backend is deployed. F2/F3 backend primitives now support durable layouts, grouped numeric bindings, normalized inputs and common actions, fixed/follow-selection target contracts, entry/release behavior and Rate/Intensity scales without rewriting authored motion settings. Per-client watch subscriptions survive navigation by another connection. Verification: 42 backend tests and checks/backend-foundation-live.json, including a native Heart clip launch with actual Resolume parameter readback.

F2/F3 adapters and the functional layout setup/Grab interface are now implemented. Native four-fader/eight-pad capture, PS4 buttons/sticks/triggers, MIDI encodings and shared actions feed the same saved bindings. Per-device settings remain independent when several devices share a control. Hold release is owner-guarded; cross-target momentary pairs are explicitly rejected. Native layout save, fader drag with real Resolume readback, and capture/Escape release were verified; 45 backend tests and the controller/browser fixtures pass. See CONTROLLERS.md and checks/controller-surface-live.json.

Physical whole-Grid mapping and PS4 navigation acceptance now belong to the final integration phase. No physical-controller certification is claimed. Trackpad/force-click and custom-layout acceptance are deferred workflows. P1/P2 playing surfaces, source/feedback routing, stage opacity grouping, color, scoped recall and complete show verification remain required subsequent phases. Visual reference work remains parked.
