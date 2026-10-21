# Heart — generic generative instrument controller

**Latest scope:** Grid faders/knobs and the separate master knob are mapped natively in Resolume. Heart’s priority is clip navigation and playing motion relationships. PS4 operates the interface. Trackpad/custom layouts are deferred. Recovery is Base and Safe only, without a general preset system. This governs the historical exploration below.

**Current sequencing:** [SHOW-CHECKLIST.md](SHOW-CHECKLIST.md) retains the complete show requirements. [MVP-SPEC.md](MVP-SPEC.md) defines the core playing workflow first. Heart must work fully with mouse and keyboard before whole-Grid mapping and PS4 navigation are integrated in the final phase. Separate big knob, trackpad and custom layout/Grab workflows remain deferred.

User direction, September 11, 2026. This contract governs the show build alongside SHOW-FEATURE-PLAN-2026-09-11.md. Latest priority: complete functional Heart workflows through mouse and keyboard; integrate controllers last. Operational clarity and portability remain requirements; aesthetic refinement is optional polish after the functional build. The reference board and visual specimen do not block backend work.

## Product boundary

Heart is a generic controller for generative instruments rendered by Resolume. Soup, Feedback Machine and Portal are examples used to exercise the system. Their names, counts, layer numbers, shader names and particular geometry must not become application logic.

The tool discovers native targets and capabilities, applies declared organizational conventions, and presents the same control language across instruments. Specialized performance views bind to real controls through configuration. They do not assume that every shader implements the same behavior or silently manufacture an equivalent.

## Transferable organization

| Concept | Generic meaning | Current example |
|---|---|---|
| Instrument | A configured source, effect or cooperating set of targets | Soup source/processing setup |
| Group | Actual native membership, plus explicitly configured associations where required | Soup render group; stage group |
| Role | Optional declared purpose used to organize controls and actions | source, processing, feedback, stage; mask/outline within stage |
| Capability | A native control or explicitly configured action | level, color, reset event, envelope, clip launch |
| Stage mapping | Opacity control over existing stage layers and groups | Portal frame |
| Performance bank | Chosen targets/clips/actions arranged for playing | A selected subset of the imported library |

Keep the existing exact `__stage__` group convention as the recognized stage entry point. Use actual group membership; an associated mask outside that group requires an explicit association. No inference from the word “Portal” or from a remembered layer index. Broader role syntax remains a design decision; do not proliferate reserved prefixes before a concrete need.

Discovery and configuration must distinguish display labels from binding identity. A display rename must not silently point a mapping at a different control. Repeated effects, absent roles, different group sizes and changed runtime IDs require explicit handling. Ambiguous bindings remain unresolved; ordinary untagged compositions still get generic controls.

For the current show build, Stage Mapping controls stage-layer/group opacity only. Feedback remains an ordinary composition instrument, independent of this feature. Physical geometry, mask editing, projector setup and other stage editing are handled elsewhere. Stage Mapping must support a second layout with different names and a different member count without code changes. This does not imply building automatic projector calibration, edge blending or an output-mapping editor today.

## Performance layouts and Grab

The reusable playing unit is a named performance layout. A composition supplies its targets; a layout assigns playable roles. The performer grabs a prepared layout instead of remapping devices during a phrase.

A layout defines:

- Named continuous controls and button actions, with resolved target sets.
- Associations to physical faders/knobs, trackpad regions and PS4 controls.
- Range, takeover and release behavior for each control.
- Scope for shared musical rate and intensity controls.

The same control can drive one opacity or a configured set. Set membership is explicit. Preserve the intended balance between members through saved weights or deliberately captured reference levels. Equal-value control is a separate explicit choice. A zero live level must not become a permanent zero weight by accident. Do not infer group membership from names or temporarily zero layer values.

Grab resolves exact bindings and seeds input state. Touches or held buttons already present cannot fire new actions. The active layout remains visibly named. Exact bindings stay fixed until layout release. An explicitly configured follow-selection binding resolves at each gesture start and stays fixed for that gesture. Browsing cannot redirect a held action or active touch. Switching layouts settles/releases active gestures before new ones acquire control. Missing targets remain visible and unresolved. Taking one layout must not stop unrelated drives.

The user's earlier Portal composition provides a performance-layout example. This layout spans ordinary composition layers and stage opacity sets:

| Control | Role |
|---|---|
| Fader 1 | Inner-ring opacity set |
| Fader 2 | Wings/balls/squares opacity set |
| Fader 3 | Underlying video opacity |
| Fader 4 | Feedback-layer opacity |
| Upper knobs | Outline, background and master opacity |

The feedback fader addresses the composition’s ordinary feedback layer. It is not a stage-feedback subsystem. The present composition also has a feedback layer. Stage Mapping neither owns nor creates feedback; the performance layout can address both independently. Actual signal routing remains whatever the composition defines.

These are configurable role bindings. No Portal-specific source code or fixed layer indexes. A differently organized generative instrument can bind the same four-control layout to different sets.

Repeated direct fader pulses feed and remove content from feedback. Preserve continuous, unquantized response; beat quantization is not an implied requirement. PS4 navigation and effect triggers are the initial trial layout, not a fixed final assignment.

The large knob gets explicit Rate and Intensity modes. Rate changes use musical ratios and retain phase continuity. Initial scope is eligible Heart-owned drives; native animation requires an explicit supported binding. Intensity changes the motion amount/span without overwriting authored low/high ranges. Scope is visible and configurable. Neither mode silently rewrites composition BPM, source defaults or every exposed parameter. Final feel is determined through playing, not presumed now.

## Trackpad continuity

Four simultaneous fader lanes and eight pads (two rows of four) are required modes. Existing implementation: `../engine/trackpad_mapping.js`; raw capture and release logic: `../engine/status.html`; input probe: `../lab/trackpad/mt_probe.py`. Keep these old files intact as behavior references. Adapt to the v2 shared action system; do not restart the v1 engine.

- Bind trackpad regions to layout controls and actions, including opacity sets and IN/OUT. No separate trackpad target vocabulary.
- Support simultaneous contacts. Physical faders, knobs and trackpad can work together. A new intentional gesture takes ownership of its destinations after any required pickup. An older spring or release cannot overwrite that newer gesture. Unrelated targets keep running.
- Faders retain absolute, relative and pickup entry behavior; release can hold, spring to zero or return to a configured reference. Spring time is adjustable. Retouch interrupts the return continuously.
- Pads carry press/release, momentary or one-shot action semantics. Envelope reversal/retrigger behavior remains the common action's behavior.
- Track contact identity through a gesture. Region crossing and multiple contacts in one region need deterministic ownership; do not trigger neighboring actions from incidental drift.
- Grab consumes normal pointer/scroll/pinch gestures. Physical click or Escape releases. Opening click, tap-to-click and subsequent physical release are distinct. Blur, disconnect, missing targets and sleep clear held actions without phantom reactivation.
- Provide spatial touch/contact feedback in the layout, not a stream of explanatory status text.
- The current raw probe exposes contact identity, position, velocity, size and shape. Native force-click events are separate. Verify supported simultaneous contact count and usable pressure behavior on actual hardware; contact size is not calibrated per-finger force. Do not cap the architecture at one mouse pointer or claim ten independent pressure channels without evidence.

Returning four faders/eight pads and testing multi-contact playing is required before treating the redesigned surface as usable. New exploratory gestures must not displace these established modes.

## Controller contract

For this show, native Resolume assignments cover the Grid faders/knobs and master knob. PS4 navigation is the remaining Heart input priority. Mouse/keyboard controls must work first. The following adapter capabilities describe existing/future support, not additional show gates.

- One mapping interaction: enter Learn, select a visible action/parameter, operate a physical input, see the compact assignment. Multiple devices and mappings coexist. Clear/reassign is explicit.
- PS4 buttons and D-pad map to actions with press/release semantics. Sticks and analog triggers map to continuous controls, with configurable range, polarity, dead zone and appropriate absolute/relative behavior. Trigger-as-button uses a threshold with hysteresis. Verify which inputs the actual native adapter exposes; do not assume motion sensors or touchpad support.
- Distinguish direct performance assignments from navigating/editing the UI. A button mapped to a show action must not also activate the focused control. Modes and shifted banks, if used, have a persistent compact indication.
- A binding may address an exact instrument/parameter or an explicitly chosen follow-selection scope. The mode is visible; selection changes never silently retarget an exact binding.
- MIDI knobs accept the actual device encoding: absolute CC with defined takeover/pickup behavior, or relative encoder deltas with sensitivity. Determine KnobX1 encoding from actual input samples, not its name. Button encoders, where exposed, use the same discrete action path.
- Axis return behavior is explicit: retain the parameter value or spring to a configured value. Physical stick centering must not unexpectedly send every target to zero.
- Disconnect, focus change, mode change and replaced targets release held actions and clear stale axis intent. Reconnect seeds current button/axis state; a held input does not generate a phantom new press.
- Saved profiles carry device/control identity, target binding, mode, ranges and release semantics. Missing devices or ambiguous targets remain visibly unresolved instead of acquiring a guessed binding.
- Show assignments spatially on a controller view when configuring them; keep prose and protocol details out of the performance surface.

Earlier native PS4 navigation and configurable-controller work is documented in `../hardware/README.md`. Reuse viable adapters and tested behavior. V2 currently has CoreMIDI and a single browser-gamepad axis grab, not the old full native controller implementation. Neither earlier simulated checks nor device detection establish current physical performance acceptance.

## Cognitive design and narrator bleed

Located exact user feedback in `/Users/donovan/.claude/projects/-Users-donovan-work-met3or/memory/no-graffiti.md`. It calls explanatory chrome “graffiti” and “narrator bleed” and places explanation in documentation, outside the rendered work. That note came from visual studies; here it reinforces the user's current explicit requirement for a compact instrument map.

- Remove explanations of the tool, implementation commentary, tutorial sentences, decorative headings and redundant status narration from the playing surface.
- Preserve the minimum operational signifiers: target identity, actionable controls, values and unambiguous state. These carry the interaction; do not replace useful controls with cryptic glyphs merely to eliminate words.
- Recognition before recall: the surface keeps destinations and active relationships visible. Consistent position/proximity groups related actions. Detail unfolds at the point of interaction.
- Help is on demand; diagnostic explanation stays outside the performance map. No instructional sentences permanently repeated beneath each envelope or parameter list.
- Keep musical/action semantics consistent across PS4, knobs and mouse, so each device does not require learning a different instrument.

The named skills are located at `/Users/donovan/work/skills/_extract/*/legibility-constitution/SKILL.md` and `/Users/donovan/work/skills/_extract/*/narrator-bleed/SKILL.md` (the asterisk is a literal directory name). Both have been read and govern new surface work. They are locally available, though absent from the current Codex skill catalog.

## Surface grammar

Design as a spatial map of the instrument. Position, grouping, alignment, proximity and consistent state treatment carry the structure. A stable map does not require a freely panning node editor or a screen full of connection lines.

- One stable performance surface. Frequent controls stay visible and stationary as selection and values change.
- Layer/group strips show compact identity, active clip, level, previous/next and effect state together. Eight visible strips in two rows of four is a viewport bank, not an assumption that every instrument has eight roles.
- Effects are a compact rack in the selected scope; IN/OUT and active state remain directly playable. Envelope times/curve/range open as local detail rather than occupying every effect row permanently.
- A/B are equal detail lenses with explicit follow/pin state. Selection exposes depth without rebuilding the main playing surface or shifting other targets.
- Stage is a generic region/group view. Its content and available controls follow membership, configuration and capability. Portal names may appear as content labels.
- Clip search/browsing is a focused tray or local panel, not long launch-button prose above the controls. Keep the current selection and bank clear.
- Shared tempo/motion/recovery actions have stable locations and explicit scope. No duplicate action with subtly different meaning between mouse and MIDI.
- Labels are short and consistent. Use familiar symbols with text where needed; do not replace prose with a vocabulary of unexplained icons. Help is available on demand. Errors stay actionable and concise.
- Compactness comes from removing repeated labels, scaffolding, whitespace and permanently expanded settings—not shrinking touch targets, type or faders until they are hard to use.
- Glance groups contain at most four items, with at most three disclosure levels. The eight visible strips form two groups of four. Identity and group markers stay visible; linked controls show their relationship without requiring recall.
- Selection, playing, bypassed, driven, learning and pending are distinct states. Color supports them, but is not the only indication. Reserve animation for actual motion/progress or feedback to an action.
- Technical IDs, schemas, diagnostic counters and instructional paragraphs stay outside the performance map. “Connected”, the target name, a useful value and a meaningful error belong on it.
- Open detail within a reserved footprint or overlay; adjacent controls do not move. Use reduced-motion support and stable, persistent elements.
- No outer-page scrolling for the primary playing controls at the actual native window size. Long collections scroll locally with their headers/actions fixed. Avoid nested scroll traps.

## Implementation constraint

Reuse the existing engine, native target adapter and action vocabulary. The UI is a projection of catalog, selection and compact state, not another owner of musical behavior. Continuous updates must not rebuild the map or move controls under the pointer. Device assignments and performance layouts persist separately from temporary playback state. Output geometry remains managed outside Heart.

Legibility Constitution and Narrator Bleed provide the requested cognitive-design rules. General frontend-design guidance is supplementary. The user's instrument-specific contract here governs over any generic website aesthetic prescriptions.

## Acceptance through use

1. At the actual native window size, identify active sources, active FX, selected target, pinned target, stage state and controller-learning state without opening help.
2. Play the current scope's common action in one gesture; navigate to an ordinary offscreen target in at most two deliberate selection steps. Text entry requires no performance shortcuts to be disabled manually.
3. Operate source/mix/effect/stage actions with the same visual grammar. No name-dependent branch, hardcoded layer number, or requirement for the Portal composition.
4. Change selection and update catalog/state while interacting. Controls keep their position; unrelated motion and MIDI mappings remain intact.
5. Configure a second, differently named stage group/layout and an untagged ordinary instrument as transfer tests. Missing capabilities are reported or omitted with clear status; they are not guessed.
6. Play native Grid faders/knobs while navigating clips and motion controls with PS4. Check navigation, activation, back, scrolling and reconnect. Assess reach, accidental hits, focus and recognition. Custom layout/Grab and trackpad acceptance are deferred.

## Next concrete design output

A compact functional surface prototype using real catalog-shaped data for two differently organized instruments. Establish the spatial layout and direct gestures before building separate specialized panels. Prototype and engine/action foundation can then be integrated as one coherent batch. No broad cosmetic redesign of unrelated pages.

Deferred design direction: the surface should speak the user's Boustrophedon instrument language with the care of a precision instrument. The [surface-language reference collection](../design/heart-surface-language/README.md) is available for optional polish once functionality works. Material comparison and the actual-size visual specimen are parked. The maker's grammar remains shared across instruments; it does not tie Heart to Portal or MET∃OR lore.
