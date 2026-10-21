# Heart performance instrument — phased specification

**Current agreed direction (September 8): [Heart + Generative Soup — one coherent instrument](COHERENT-INSTRUMENT-PLAN.md).** Follow its execution order for the next work; retain this specification as the technical reference. Figure containment applies to the source before its effect stack. Downstream effects, especially Linear Cloner, may intentionally carry instances offscreen.

Status: phases 0–4 authorized by the user on September 7, 2026; implementation underway. See PROGRESS.md for actual completion and blocked validation. Scope follows the user's request to plan a substantial coordinated build. Baseline: [Feedback Machine comparison](../feedback-machine-comparison/README.md). Worker policy: [WORKERS.md](../../../WORKERS.md).

## Current priority — user correction

September 8: prioritize one complete playable path with 3D, shell and one imported Figure source, then expand in small batches under the shared instrument definition. The reference bank/stacks are imported; use the restoration inventory instead of repeating broad audits. Portal/Treehouse image links now use `work/Visuals/infra`; their restoration is separate from the current instrument milestone. Unfinished benchmark/acceptance gates do not block this work. Address performance where it prevents use, preserve saves, and keep verification proportionate. Use deterministic extraction and bounded existing worker workflows to conserve usage.

## Intended outcome

Open Heart, start a working generative patch, browse and play eight layers, shape feedback and color, invoke musical motion, recall relationships, and recover from connection problems without opening Resolume's controls. Resolume remains the renderer. Heart becomes the performance instrument.

Preserve eight faders in two rows of four, in Resolume order, full parameter access, trackpad capture, direct speed multipliers, native live output and the existing relationship library. Keep the removed variations strip and bottom Faders/Variations buttons absent. Layer effects belong in their layer cards. Preserve the current composition as a reference and implement composition changes in a named working copy.

## Execution boundaries

The first substantial execution pass is phases 0–4: infrastructure, complete control access, one finished feedback instrument and reliable starting-patch recall. These phases form a usable release. Phases 5–8 extend the same foundation; they must not delay that release. Continue across ordinary implementation decisions and passing checkpoints without repeated permission requests once execution is approved. Stop dependent work only for missing aesthetic decisions, unavailable required plugins or a failed gate with no safe resolution; continue independent work.

No promise of identical rendering or zero latency. Target full-resolution 1920 × 1080 at 60 FPS, measured against a controlled baseline. Never silently lower resolution, frame rate or texture quality. Expensive artistic combinations can be marked heavy; a measured standard performance patch must meet the release budget. Hardware-specific tests remain pending until that hardware is connected.

## Phase 0 — baseline, recovery and work orders

Deliver:
- Capture current project changes, composition copy, Heart configuration, user Homes/presets and relationship documentation references. Save baseline metadata and reproducible restore instructions; do not overwrite user changes.
- Record installed plugin availability, current clip/effect inventory and routing. Verify router inputs and feedback source/reset behavior before effect placement. Record live versus saved discrepancies.
- Use the existing worker harness for small isolated work orders: brief, input manifest, result contract, output, review decision. Start with local Qwen3-Coder 30B; use scripts for mechanical inventories. No new scheduler/framework is required for this release.
- Establish an identical render scene and capture output FPS/frame intervals, Heart work/queue, dimensions, monitor state and background apps. Measure idle, normal patch and feedback/effect stress patch separately. Label GPU percentage as system-wide; local inference is unloaded during measurements.

Gate: the working copy can be restored; all dependencies and uncertainties are recorded; no archived stack is assumed active or equivalent merely because it exists in XML.

## Phase 1 — stable control and connection foundation

Deliver:
- A common action layer for UI, trackpad and future MIDI: previous/next/random clip, launch, layer level/bypass/clear, parameter set, drive toggle, speed, Home, effect press/release, Hold, patch recall and reconnect.
- Stable target identity: layer role + clip/instrument identity + scope + effect instance identity + parameter key. Display names are labels. Repeated effects and repeated names such as Gain remain distinct. Runtime Resolume IDs are resolved afresh.
- Discovery covers source, clip, layer, group and composition parameters. Parameter adapters handle continuous, cyclic, integer, choice, boolean, color and trigger values explicitly. Never infer trigger semantics from an ordinary numeric range.
- Migrate existing Homes and presets without dropping data. Keep backup and schema version; ambiguous old bindings are reported for repair rather than assigned arbitrarily. Missing controls skip safely with visible status; new controls begin undriven.
- One motion owner per parameter: Heart, shader or Resolume automation. Prevent double animation. Manual takeover and release follow a defined policy, with no jump from stale state.
- Connection states: connecting, discovering, ready, degraded and disconnected. Reconnect clears stale writes, rediscovers identities and restores eligible motion only after targets resolve. Reload or schema change invalidates the old target generation so queued actions cannot hit reused IDs.
- Clip/effect discovery reads current state without writing. Do not reset layer levels or effects just by selecting a card.

Gate: meaningful tests cover duplicate names/effects, reordered parameters, removed controls, clip switch during writes, reconnect/reload, migration and motion ownership. Existing engine checks pass. Engine work stays bounded as parameter count increases.

## Phase 2 — complete the playable surface

Deliver:
- Every layer card shows layer/clip name, level fader, previous/next, bypass and clear. Previous/next wraps populated entries in the selected performance bank. Random avoids the current clip when alternatives exist. If nothing is playing, next starts at the first entry and previous at the last.
- Keep layer order and two rows of four faders. Show compact layer FX and active clip FX in each card; group/global FX have a distinct compact rack. Controls for the selected effect expand when needed rather than filling all cards with every parameter.
- Effect controls expose useful parameters, not only opacity. Support momentary and latch behavior; linked actions can operate Blur and Sharpen together. Releasing a press, losing window focus or disconnecting must not leave a momentary effect stuck on. When possible restore the pre-press state rather than assuming zero.
- The selected instrument exposes all controls in responsive groups. No six-parameter cap. Continuous controls, choices, colors and triggers use appropriate widgets.
- Home, speed multiplier and shuffle are adjacent. Show active-drive count and distinguish applied Home from unrefined fallback. Parameter names and current clip state stay visible while playing.
- Keep trackpad lock/Escape behavior; buttons, effect presses and fader interaction cannot leak clicks to other windows during capture. Keyboard focus must not turn text editing into performance commands.

Gate: eight layers can be browsed and controlled without Edit or Resolume; existing native map-clip FX are reachable; resizing has no inaccessible controls; focus loss safely releases gestures and momentary effects.

## Phase 3 — one complete feedback instrument

Build in dependency order within the composition working copy:
1. Verify and document what signal enters, recirculates and leaves each stage. Confirm resolution and source sizing. Define where processing persists as clips change.
2. Establish usable movement: rotation, translation and scale; level/decay; linked blur/sharpen; inversion and fold/mirror. Reuse existing processing before adding plugins.
3. Restore specific color behaviors from the reference: hue rotation, RGB inversion, channel delay and masking. Do not substitute Colorize. Validate effect order and whether processing is inside the feedback loop or output-only.
4. Create a small initial behavior bank: turn, drift, grow/shrink and fold, with tuned variation and speed. These are design candidates whose ranges must be derived from the actual controls and rendered result.
5. Define separate operations: Motion Home, Hold Heart motion, layer clear, and feedback reset. Hold does not claim to freeze shader TIME or feedback evolution. A reset is implemented only after its buffer/source semantics are verified; never label a temporary black frame as a proven buffer clear.

Each behavior records the intended visual result, active drives, relationships, motion ownership, bounded ranges, static choices and reset behavior. Homes should visibly move the intended features without indiscriminately enabling every control. Respect explicit saved user Homes and allow factory Home to be requested separately.

Gate: perform movement, shaping and color from Heart; return to a recognizable starting condition; demonstrate a real reset; compare with the old composition using controlled visual examples. Record expensive configurations and dependency gaps. Native third-party effects are not presumed equivalent to possible future shader replacements.

## Phase 4 — starting patch and semantic recall

Deliver:
- One explicit Start patch that launches the required clips, sets layer levels/bypass, applies verified routing and effect state, then activates each instrument's Home. Keep this separate from per-card Home and from the existing Return home behavior; labels must make the scope clear.
- A versioned patch contains stable instrument/target identities, static settings, layer/effect states, routing, motion relationships, range/phase/speed configuration and reference to Home definitions. It must not depend on parameter count or persist runtime IDs as authoritative identities.
- Recall preflight resolves targets and required dependencies. Critical routing/source failures abort before mutation. Optional missing controls are listed. Sequence launches, rediscovery, static state and motion deliberately, with acknowledgement/timeouts rather than arbitrary sleeps.
- Capture pre-recall controllable state for recovery. If recall fails midway, attempt restoration and clearly report any partial state. GPU feedback history cannot be restored by parameter undo; document this limitation. Buffer reset is an explicit recall option, not implicit in every preset.
- Serialize patch recalls under one operation identity. A second recall replaces the pending request; it cannot interleave writes with the current recall. Manual performance input cancels the affected recall before taking control, discarding its remaining writes. Suspend motion writers for affected targets during apply/recovery, then resume only against the confirmed target generation. Test rapid recall A/B, manual fader movement during recall, clip changes and disconnect during rollback.
- Order routing dependencies before downstream state application and recheck them after launches. Focus loss releases momentary ownership through the effect state machine, including mid-envelope transitions; it must not undo an independent latched setting. Test overlapping press/release, latch and recall actions on the same effect.
- Save a small set of reviewed whole-instrument patches through a compact chooser. Do not restore the removed six empty variation cards.

Gate: recall still works after reload and parameter reorder; missing optional parameters do not break valid bindings; critical missing sources do not yield a half-applied patch silently. From a cold launch, reach the standard performance patch without operating Resolume's UI. Repeat after reconnect.

### First release acceptance (phases 0–4)

Play a 20-minute session using Heart alone: start, browse every layer, alter movement/color/effects, change speed, invoke Home, hold/release, clear/reset, recall and reconnect. Exercise reload recovery in a separate controlled test. No stale writes, stuck gestures, duplicate motion owners or growing queues. Run performance checks with local workers unloaded.

Proposed budget: at 1080p/60, standard patch median output acquisition rate at least 59 FPS, 95th-percentile acquired-frame interval at most 33.4 ms, and no recurring Heart-attributable stalls above 100 ms over a 60-second sample. Record the native frame measurement method: Syphon acquisition is not proof of renderer presentation timing. Compare Heart-open versus baseline in at least three matched samples; investigate more than 5% throughput loss. These are proposed release criteria, not current verified results. If the renderer baseline fails, tune the scene or report the limiting effect instead of hiding it through downscaling.

## Phase 5 — figure, field and supporting layers

- Apply the same instrument contract to figure and field first: Ground, Room, Solid/3D, then remaining figure variants. Ensure palette/color controls visibly affect the intended component.
- Add selected clone/mirror/displacement and background treatments after confirming plugins and ordering. Restore global accents progressively, with momentary/latch behavior and useful intensity controls.
- Then refine glyph, texture, grain and delay. Separate ordinary performance entries from diagnostic and legacy clips without deleting them.
- Publish a readiness matrix for all 37 currently populated clips: source/control support, Home, reset, routing, dependency availability and measured cost. Pass-through and diagnostic clips may be intentionally static; do not call them broken because they lack drives.

Gate: every promoted entry has a useful role, predictable controls and a reviewed visual result. Existing Homes retain user changes through schema evolution.

## Phase 6 — shader family production batches

For each small family (initially 3–5 candidates):
- Script extraction: parameters/types, source dependencies, TIME usage, buffers, loop bounds and potential cost sites. Static findings are hypotheses, not measured GPU conclusions.
- Local worker: evidence-backed instrument proposal and suggested exposed controls, citing source locations. Reuse the documented parameter-loop catalog; record unsupported relationships instead of approximating them silently.
- Integration owner: select useful controls, implement isolated adapter/shader changes and review ownership/identity semantics.
- Validation: compile, render, exercise extremes, inspect meaningful Home motion, reset/recall and measure performance. Promote only passing instruments into the performance bank.

Instrument manifest: stable ID/version, family/role, source/dependencies, scoped parameters/types/units, semantic roles, range and cyclic rules, motion owner, relationship configuration, static choices, factory Home, routing/reset contract, performance evidence and migration notes.

Gate: one complete family passes before expanding throughput. Preserve source licenses and provenance. Never batch-import unreviewed workers' guesses into the live instrument.

## Phase 7 — hardware, Portal and Treehouse

- Map the common action layer to connected PBF4/KnobX1 capabilities. Tentatively prioritize precise feedback control, then grain or another chosen performance role; do not hard-code a final assignment before device inspection.
- Verify actual message formats, resolution, relative/absolute behavior and feedback capabilities. Do not assume motorization or high-resolution MIDI. Support soft takeover for absolute controls and appropriate accumulation for relative encoders.
- Restore Portal/Treehouse mappings against semantic actions and the documented relationship system. Inventory existing mappings first; old layer-number mappings are not automatically correct for Soup.
- Save device profiles separately from instrument and composition state. Loss/reconnect of a device must not jump faders.

Gate: connected hardware can browse and play intended roles, with predictable reconnect and no fights between trackpad, software and physical controls. Unavailable hardware remains an explicit untested item.

## Phase 8 — configurable monitor and finishing

- Separate control and native output windows. Provide dock/undock, optional always-on-top, remembered size/position, small viewing mode and double-click expansion/restoration.
- Optional restrained retro-TV frame around the content; preserve aspect ratio, Fit/1:1 and full-resolution texture transfer. Decorations must not enter the actual Resolume output.
- Share one receiving/rendering path where possible. Avoid duplicate active monitor render loops or texture copies. Skip unnecessary redraw of unchanged content while still repainting after resize/exposure.
- Surface configuration controls density, expanded effect groups and performance banks without exposing implementation details.

Gate: minimized Resolume still delivers output; monitor changes do not disturb motion; dock/undock has no duplicate stream/render cost; full output dimensions and comparable frame timing remain intact.

## Worker allocation and token discipline

| Work | Executor | Required output |
|---|---|---|
| XML/REST inventories, parameter comparisons, migration reports | Deterministic scripts | Compact tables and reproducible artifacts |
| Source facts, control classifications, gap review | Local Qwen3-Coder 30B; smaller model for narrow extraction | Structured findings with evidence and explicit unknowns |
| Public/synthetic contract review | Verified cloud helpers when useful | Concise counterexamples; no private source without destination-specific authorization |
| Architecture, visual choices, shared-engine edits and integration | Primary assistant | Reviewed implementation and acceptance decision |
| Runtime/render/performance validation | Reproducible tools plus visual inspection | Measurements and actual observations |

Use existing harnesses, isolated inputs and one integration owner. Parallelize only independent work; never concurrent edits to shared files or concurrent local-model inference with GPU performance measurements. Start with one local model; use measured pair/trio mode only when a queued offline batch justifies it. Unload at completion. Store accepted findings so future phases read summaries rather than re-auditing whole files. Time out unproductive tasks and reroute bounded failures. Worker output is evidence to review, not authority.

## Handoff after each phase

Update a phase checklist, changed-file manifest, validation results, known limitations and next work orders in this directory. Keep rejected hypotheses separate from accepted facts. Once a gate passes, proceed to the next approved phase without rerunning unchanged checks. A failure blocks only its dependents. Final release notes should describe the playable result, the measured performance and any specific unavailable controls.
