> **Withdrawn 2026-09-08:** Do not implement this proposal. Smart Params already provide the motion relationships. Current priority is playable global controls and content readiness; see ../PROGRESS.md.

# Heart as a modulation instrument — audited roadmap

September 8, 2026. This supersedes scene-first tuning in the coherent-instrument
plan. Audit/design only: no engine, preset, composition or live performance changes.

## Finding

Heart has a shared clock and shared math, but not shared, independently existing
modulation sources. Every Slot currently owns its oscillator and destination.
The new JSON recall removes composition interruptions; it still serializes those
per-target slots. It is not yet the intended synthesizer-style modulation system.

The reusable musical object is a relationship structure. Parameters are assignable
destinations. Lo/Hi are optional destination adjustments, not the preset's identity.

## Documentation and precedence

- [Original parameter-loop catalog](</Users/donovan/work/0000000/polyform/parameter loop system.md>): Layer 2 ratio vocabulary and N-member pattern definitions.
- [Operator-confirmed ratio frame](</Users/donovan/work/0000000/mind not map/2.structure-maintains-order/21.labor-installs-practice/211.motion-builds-form/kit/docs/frame.ratio-system.f1.20260619-051247.md>): ratio, signed multiplier, phase offset, signal pickoff separation. Explicitly trusts the earlier catalog, not its old phase/resolver design.
- [Kit ratio math](</Users/donovan/work/0000000/mind not map/2.structure-maintains-order/21.labor-installs-practice/211.motion-builds-form/kit/src/ratio.js>) and [ratio control](</Users/donovan/work/0000000/mind not map/2.structure-maintains-order/21.labor-installs-practice/211.motion-builds-form/kit/src/ratio-system.js>): period normalization, cycles/turn, reverse, bookmarks, sync readouts. Plain JS reference, not the running Python engine.
- [Earlier Heart interpretation](../../PARAMETER-LOOP-HOME.md): correctly notes partial catalog coverage, phase integration and stable named pendulum members. Its Home/profile tuning is historical, not the new architecture.

Do not copy the old direct phase formula into runtime rate changes: changing r or m
in fract(H*m*r+o) can jump phase even when H never wraps. Preserve Heart's integrated
phase and smooth rate changes. The frame's constant time-delay discussion also
must not define a new delay implementation: constant-rate phase offset equivalence
does not depend on rational versus irrational rate; a true time delay matters for
changing signals/rates. Actual sample/history delay remains a separate signal node.

## What the running code actually provides

| Component | Evidence | Reuse / change |
|---|---|---|
| Clock / transport | `heart.py` main loop; `transport.py` | Reuse tempo and integration. Explicit downbeat currently resets H and slot phases: separate monotonic clock from alignment origin in the new model, preserving deliberate rephase semantics. |
| Oscillator and destination | `heart.py: Slot.eff_cfg/step/value` | Extract generator phase, rate and shape from destination binding, manual pose, range conversion and ownership. Do not run both old and new oscillators on one destination. |
| Relationships | `heart.py: term`, `motion.py: recipe_rate` | Reuse formulas under versioned legacy identities. Pendulum recipe is independent of live count when member IDs exist, but members are currently parameter names. |
| Parameter order | `Clip` and `EffectMotion.refresh` assign `sl.index` | Default families derive terms from slot index. Stable generator member IDs must replace destination order as the musical identity. |
| Envelope behavior | `Effect.press/pulse/step` | Reuse tested ramp/pulse behavior as reference; currently attached to one effect amount, not a routable shared envelope. |
| Discovery / ownership | `targets.py`, `claim_slot`, `OwnershipObserver` | Retain native units/types, takeover, missing/stale checks and release safety. |
| Output scheduling | `delivery.py`, `step_motion` | Keep bounded latest-value queue and existing per-destination cadence. Evaluate each generator once per engine tick; fan out its signal. |
| JSON performance presets | `live_presets.py` | Keep non-reloading apply, transition, Undo and batch persistence. Add versioned graph content; current v1 remains a per-target snapshot. |
| Surface | `workspace.js`, `status.html` | Keep layout, A/B, effects and faders. Add generator-to-destination visibility within existing space after engine proof. |
| Instrument definitions | `instruments.json` | Reuse identities, source-only containment and primary-control lists. These lists are not yet a universal semantic routing map. |

## Catalog differences to preserve explicitly

These are existing behaviors, not silently correctable spelling differences:

| Catalog pattern | Heart today |
|---|---|
| Fibonacci Ascent: consecutive values normalized by first | `fibpair` returns adjacent-number ratios |
| Lucas Ascent | adjacent Lucas ratios |
| Harmonic Series: 1,2,3,... | reciprocal 1/(k+1) |
| Powers of Two / Three: ascending powers | descending reciprocal powers, with finite wrap |
| Coprime Primes: spread prime selection | reciprocal consecutive primes |
| Pendulum stepped: n + k*s | named recipe normalizes by n; legacy family uses (8+k)/8 |
| Near-Unison cluster with tightness | fixed (n+1)/n sequence |
| Near-phi cluster by approximations | reciprocal-phi linear detune |
| Metallic Ascent | reciprocal metallic constants |

Heart has 19 family entries including per-slot, not an exhaustive catalog port.
Its ratio bookmarks include 1:1 and 3:2; frame prose says r<1 while the kit control
also permits 1:1. Preserve current numeric rates on migration, expose effective
cycles/turn, and choose canonical storage explicitly rather than clamping old rates.

## Proposed runtime model

1. **Clock and alignment:** running independently of visible controls and clips.
2. **Generators:** persistent IDs; LFO phase, shape, signed rate, offset and envelope
   state. Related members receive rates from a versioned catalog recipe.
3. **Routes:** generator output → destination reference. Many destinations may read
   the same output. Routes carry optional inversion/depth/polarity; member identity
   never comes from current parameter position.
4. **Destination adapters:** resolve live parameters, handle native ranges, cyclic
   wrap, static/discrete types and source containment. Optional Lo/Hi stays here.
5. **Expression:** layer/scene modulation-depth envelopes plus explicit effect
   gates. Closing modulation is distinct from fading the rendered layer out.

Generators continue when routes are absent or clips change. Existing members keep
rates/phases when members are added/removed. Assignments may change without changing
the recipe. A finite generator bank may feed any number of destinations; expanding
that bank is an explicit operation, never an accidental consequence of parameter count.

For arbitrary imported shaders, do not invent semantic equivalence. Use explicit
assignments or known instrument mappings; show unresolved routes. A deliberate
assignment shuffle can select from eligible numeric controls. Discovery alone does
not animate every new parameter. Static choices/counts need explicit opt-in policy.

One generator feeding multiple destinations is the first goal. Combining several
generators at one destination needs an explicit mixing rule; defer it until the
single-input route contract is proven. No arbitrary feedback graph/cycles in phase 2.

## Preset and migration contract

Versioned graph preset stores generator IDs, recipe ID/version/seed/member mapping,
rate/shape settings, routes and expression/rest state. No transient Arena IDs or
required parameter count. Instrument mapping and optional destination transforms
remain distinguishable from musical structure.

Normal apply preserves running phases for matching generator IDs and transitions
changed settings. Explicit retrigger/downbeat can rephase. Exact checkpoint/restore
of phases is a separate recovery policy, not an automatic musical preset behavior.

Keep current performance JSON readable. Deterministic migration gives each old
slot its own generator first, preserving rates, shapes, ranges and destinations.
Do not automatically merge two slots just because their current settings coincide.
Promote deliberate shared relationships afterward. Keep originals and record version.
Full composition setup remains separate from graph recall.

## Implementation order and acceptance gates

### Phase 1 — audit (complete)
This document identifies authoritative sources, current coupling, catalog differences
and the migration direction. No runtime architecture changed during the audit.

### Phase 2 — independent generator bank (next)
Extract existing integrated oscillator math into a generator bank with stable IDs.
Introduce single-input routes through existing adapters. Begin with legacy-compatible
ratio/shape behavior plus named Pendulum; do not port the whole catalog first.

First proof: one persistent generator drives one source control and a Cloner control;
replace the source destination, then switch the source clip. The Cloner keeps moving,
the generator keeps its phase, and a newly bound destination joins the existing signal
with a controlled transition. Missing routes remain visible and inactive. Removing
or adding a destination changes neither rate nor generator count.

Tests: steady-rate equivalence; rate morph continuity; fan-out equality; stable member
identity under reordering/count changes; stale/replaced target release; bounded output
queue. Live check: a short representative run, same resolution, no local GPU inference.
Do not infer smooth rendering solely from a moving readout or a still image.

### Phase 3 — adaptable assignments and graph JSON
Separate route editing from generator editing; scope mappings to known instruments.
Migrate old performance JSON without changing its behavior. Verify apply/Undo/clip
switching without composition reload or generator restart.

### Phase 4 — playable expression and legibility
Layer and scene scopes; Open/Close expression, Settle rest state, Vary relationships
or assignments, and visible active routes/effects. Reuse the surface; no redesign.
Reusable envelope routing follows the same source/destination contract. Preserve the
meaning of per-target Home versus global recovery; no silent renaming of actions.

### Phase 5 — pilot acceptance, then expansion
Same relationship graph through 3D, Shell and Seed plus effects. User confirms fluid
movement, useful variation and understandable recovery. Then expand 3–5 shaders per
batch, followed by hardware/Beatpad. Scene tuning, visual decoration, usage recording
and worker infrastructure must not displace phases 2–4.

No local model loaded for this audit: bounded filesystem comparison was sufficient,
and the live VJ scene retains its GPU resources. No live controls were changed.
