# Heart + Generative Soup — one coherent instrument

**Superseded execution order, September 8:** [Modulation-instrument audit and roadmap](modulation-instrument/README.md) is now authoritative for next work. Build independent generators and routes before more clip-specific scenes. Preserve the original Figure containment rule and useful implementation evidence below; the scene-first milestone sequence is historical.


Agreed with Donovan, September 8, 2026. This is the current direction and execution order. The earlier [specification](SPEC.md) remains the technical reference; [progress](PROGRESS.md) records evidence of completed work. This document records decisions and planned work, not implementation completion.

## Outcome

Generative Soup and Heart become one performance instrument, with Resolume running underneath. Open Heart, choose a few sources, press Home, and get an immediately alive, understandable setup that can be played, changed and returned to without opening Resolume's controls.

Keep Soup's eight-layer layout and evolve Feedback Machine's capabilities within it. The reference library and effect stacks have been imported; that provides material for instrument design, not proof that every shader is finished. See the [restoration record](../../restored-compositions/soup-restoration/README.md).

## Foundational Figure rule — source containment only

**The source figure must remain completely within the frame, with breathing room. It must not touch the edges throughout its permitted source animation.** This applies at the source output, before the downstream effect stack.

**The effect stack does not share that constraint.** Linear Cloner and other effects may intentionally spread, scale, repeat and carry instances offscreen. The contained source gives the effects room to create the illusion of depth through many iterations and instances of a complete subject.

The intended relationship is: contained source figure → cloning and transformation → repeated forms extending through and beyond the frame.

- Source framing, position and permitted motion ranges belong in each Figure instrument definition and its Home.
- Validate containment on the isolated source, then evaluate the downstream effect result separately. Offscreen clones are not containment failures.
- Consider combinations of source controls, not just individually bounded parameters. Home, shuffle and allowed source modulation must respect the source envelope together.
- Cropping an oversized subject is not a successful contained source. Avoid reactive automatic resizing that introduces unintended size pumping.
- Do not constrain, clip or automatically shrink the final layer/effect output to enforce this source rule.
- Exact clearance and useful source motion ranges require visual review per instrument; no universal numeric margin has been agreed.

## Layer responsibilities

These are design responsibilities to check against the actual saved and live routing. They are not a claim that the current signal path already implements every responsibility.

| Soup role | Performance purpose |
|---|---|
| Feedback | Sustain, accumulate, recirculate and erase |
| Sculpt | Shape and color what enters feedback |
| Field | Establish the environment and underlying movement |
| Delay | Create echoes, trails and temporal separation |
| Figure | Supply complete, contained source subjects to an unconstrained effect stack |
| Glyph | Add symbols, structures and graphic gestures |
| Texture | Change the surface and character of the image |
| Grain | Add fine detail, noise and finishing energy |

## Execution order

### 1. Establish the actual signal path and shared instrument definition

Trace source, clip, layer, group and composition processing. Record where Figure enters its stack, what Sculpt processes, what Feedback actually remembers, and where Delay taps the image. Distinguish shader-owned history from effects processing the output of that shader. Reuse existing routing evidence and obtain fresh readback where the active composition differs.

Define one versioned instrument description for Heart to read, drawing on the existing target, parameter and relationship systems. It should cover:

- Stable source/instrument identity, role and family, with display names kept separate from binding identity.
- Useful controls, parameter types, ranges, static choices, abrupt-change controls and motion ownership.
- Source framing and containment envelope when the instrument is a Figure.
- Home values, active drives, relationships, speed and useful variation ranges.
- Routing requirements, relevant effect controls, history/reset behavior and performance observations.

Use the existing parameter-loop relationship library. Presets hold relationships and scoped parameter bindings, not an assumed parameter count or transient Resolume IDs. Preserve user presets; missing or ambiguous controls must be visible, and newly discovered controls must not silently acquire motion.

Exit: the working path is documented from actual evidence, and the first instruments can use the same definition without another parallel configuration system.

### 2. Build the playable modular surface, then connect effect motion

**Implementation update:** the [performance pass](performance-pass/README.md) now provides combined A/B, separate clip browsing, all-layer Play and musical timing, shared native-effect drives, pulses and fader gestures. Its evidence record distinguishes tested behavior from remaining artistic and live recall validation. The decisions below explain the design.

Updated with Donovan, September 8: surface work comes **before deeper pilot refinement**, so the instruments are tuned through their actual performance controls.

Follow-up design decisions from playing the first pass: use six outer areas—eight faders (four over four), monitor dock, Play, effects rack, a combined parameter workspace, and a separate clip browser. The areas resize and exchange positions in Arrange mode; lock geometry for performance. A starting arrangement is faders / monitor / effects above Play / parameters / clips. These revisions are implemented in the performance pass linked above.

The combined parameter workspace has a full-width top section above two side-by-side sections, A and B. Each section scrolls independently and uses a two-column parameter grid. The top section keeps target selectors, motion state and each side's controls visible while its parameter list scrolls. Each side can follow the current layer/source, follow the selected effect, or pin a chosen exact source or scoped effect. Start with A following the source and B following the selected effect. Keep each action's A/B target explicit; switching the visible target must not stop its drives. Both sides need the same Home, shuffle, speed, musical/irrational/stable timing choices, locks and relationship controls. Retain the full list without a six-parameter cap.

Play is the immediate performance area:

- Tap BPM, editable tempo, a downbeat button and visible beat/phrase position belong **inside Play**. Tempo sets rate; downbeat establishes musical phase. Connect phase alignment to the actual drives and scheduled actions, not just the displayed counter. Existing independently integrated drive phases need an explicit alignment policy.
- Keep current clip and previous / next / random triggers accessible for **all eight layers at once**, without selecting each layer first. Show the bank/scope each trigger uses. The separate clip browser handles searching, inspecting and choosing individual clips.
- Keep quick actions such as Home, shuffle, Hold and Undo visibly scoped. Reuse existing actions rather than adding an unrelated performance system.
- Reserve a clearly marked **Beatpad · later** placeholder. The eventual Grab beatpad control captures the trackpad for manually played kick/snare-style gestures mapped to chosen effect envelopes and relationships. Visible pad labels, capture state, hit feedback and a reliable release are part of that later work. The placeholder is inactive: no capture or effect writes until implemented. Selecting mappings and adding audio-reactive behavior are deferred; they must not block the current instrument milestone.

Workspace geometry and pinned targets save separately from musical patches. Retain visible target, connection, gesture, motion and operation state. No bottom variation strip. **Defer usage/session recording until the instrument is fully working**; do not add a recorder, analytics pipeline or interaction-logging overhead to this milestone. Existing operational readouts remain useful.

The first workspace implementation is recorded in [modular-surface/README.md](modular-surface/README.md). Source motion controls are connected; ordinary effect parameters are accessible manually. That initial pass did not implement effect drives or recall; the subsequent performance pass adds shared effect motion and saved patch state.

Next, make Figure + Linear Cloner a complete playable example: source in A, Cloner in B within the combined workspace, both using the existing Heart relationship system. Effects need their own drives, animated Home, locks, shuffle, speed and visible drive state. Presets must bind scoped semantic controls without depending on counts or transient IDs. Relationships should eventually span source, placement and effect controls.

Donovan wants Home to start exploration with broad, clearly visible motion and fully open Lo/Hi, then tune sweet spots through playing. Apply that intent deliberately to continuous performance controls; define the permitted ranges and coupled placement behavior so Figure source containment still holds. Static switches and discrete counts need explicit behavior, and undiscovered or newly bound controls must not silently start moving before a deliberate Home action. Existing saved Homes are user material, not disposable defaults.

Explore depth through scale, distribution and tail length, rotation relationships through the cloner's rotations, and deliberate density changes. Discrete counts must not acquire continuous sweeping by default. Tune these behaviors through actual output rather than treating candidate ranges as proven.

Requested expressive interactions follow the surface and motion foundation: scrolling a fader captures the pointer while adjusting a lasting level; a clicked/held absolute performance gesture springs to zero on release. Finalize and verify capture/release semantics through playing, including escape, focus loss and sleep. Effects retain smooth on/off latching and gain a separate opposite-direction pulse: briefly activate an off effect or interrupt an on effect, then restore its prior level. Keep that baseline distinct from latch state and define envelope timing and retrigger behavior. This pulse is not the future trackpad beatpad implementation.

Order within this stage: consolidate A/B and separate Play from browsing; complete shared source/effect drives and Play's musical timing; implement and verify fader gestures and effect pulses. Then refine the three pilots through the resulting surface. Beatpad implementation and usage collection remain deferred.

### 3. Refine the three pilots through that surface

The pilots are **3D (SP Atom Solid), shell (SP Atom 4D Field), and z33d+**. The [first Figure milestone](figure-milestone/README.md) records their current Homes, source-frame checks and effect-path evidence. Broader manual ranges and final artistic refinement remain open.

For each:

1. Verify the complete source subject and its containment envelope.
2. Tune distinctive, visible Home motion with complementary relationships.
3. Play it against the shared Linear Cloner / Sculpt / Feedback path, allowing downstream instances offscreen.
4. Review which placement controls can move to a pre-effect Transform without changing the intended rendering. Source geometry, camera perspective and internal lighting remain shader-owned where a 2D transform is not equivalent.
5. Check Home, speed, shuffle, manual control, source switching, hold/recovery and recall from the modular surface.

Figure placement is part of the containment contract: scale and position must respect the known source bounds together. Later effects remain unrestricted. This is not permission to introduce a final-output mask or reactive size pumping.

Exit: switching among the three pilots, getting useful motion with Home, playing source and effect relationships together, understanding every action's target, and recovering the setup are dependable. Check representative GPU/FPS behavior proportionately before expansion; the pilots do not need every possible relationship exhausted first.

### 4. Expand in complete batches

Bring in roughly three to five related shaders at a time using the established definition and workflow. Each batch receives useful controls, appropriate routing, a meaningful Home, visible output checks and a proportionate performance check at the actual composition resolution. Apply source containment to Figure candidates; do not impose it on Field imagery or downstream effects.

Use deterministic scripts first for inventories and consistency checks. Use bounded local worker tasks for parameter extraction, candidate definitions and reviewable supporting work, following [WORKERS.md](../../../WORKERS.md). Visual framing, motion quality and depth require artistic review. Unload local inference before judging rendering performance. Do not build a new worker framework as a prerequisite.

Exit per batch: sources are usable instruments with recorded evidence and explicit remaining limitations. Plugin availability or successful import alone does not count as completion.

### 5. Make the whole setup returnable

Build on the existing recall and reconnect work. A complete starting patch establishes sources, levels, routing, effects and motion. Keep per-instrument motion Home distinct from whole-setup recall, Hold, layer clear and feedback reset.

Verify switching instruments, returning to the starting setup and recovering from reconnect. Then map the trackpad and available hardware onto the established actions, with assignments visible and predictable across source changes.

Exit: the complete setup can be started, played, changed and restored from Heart, with honest progress and failure feedback.

## First milestone

**Three Figure sources that can be swapped, animated with one click, spread into depth with Linear Cloner, and fed into a controllable feedback system—all from Heart.**

The source stays contained throughout its intended motion; the effect stack is free to extend its instances offscreen. Use this milestone to establish the pattern before expanding the library.

## Scope and verification

Keep the accepted Heart Monitor design stable. Reuse the existing engine, relationship library, effect adapters, reconnect and recall foundation. Preserve recovery copies before composition changes. Keep Portal/Treehouse restoration and later integration available without making them prerequisites for this milestone.

Performance remains relevant to playability, but broad benchmarking and infrastructure work must not displace instrument completion. Verify changes proportionately, retain resolution and quality, and record heavy combinations honestly. This plan does not claim every imported shader is visually reviewed, has a tuned Home, or sustains 60 FPS.

Next action: refine the three pilots through the implemented source/effect surface and verify a newly saved whole patch with effect motion at a suitable break in playing. Then expand in complete shader batches. Beatpad remains an inactive placeholder; usage recording remains deferred.
