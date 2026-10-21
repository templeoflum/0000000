# *Spatium Dimensio*

A composition in seven movements about how mathematics treats space — and what gets left behind when measurement is mistaken for the thing measured.

> **⚠ Quarantined during Calibration iteration.** This work and its files are intentionally not being updated while Compositional Algebra is being iterated through the Calibration spline score. Spatium-specific docs may contain references to older workflow patterns, vocabulary, or layer signatures than the current framework. They will receive a single coordinated update once the framework stabilizes. See `DEV_LOG.md` for the quarantine decision and exit conditions.

---

## What this is

*Spatium Dimensio* is a spline score authored within the [Compositional Algebra](../../README.md) framework. The spline is the score; each realization is a performance of the score across a chosen medium — essay, fairytale, audiovisual performance, album, set, installation, ritual, lecture.

No realization is canonical. The score is the work.

---

## The spline

Seven movements, in order:

| # | Movement | Function |
|---|---|---|
| I | The Reach | ground before measurement |
| II | The Rod | the tool arrives |
| III | The Many Names | parallel settlements |
| IV | The Cage | the join hardens |
| V | The Body That Exceeds | the field returns |
| VI | Quiet Recognitions | convergence across time |
| VII | Set Down the Rod | release without erasure |

Continuity grades between movements: I→II C¹ · II→III C² · III→IV C¹ · IV→V C² · V→VI C¹ · VI→VII C².

Full per-movement signals (Identity including Shape, Math vocabulary, Audio, Visual, Voice, Transition notes) in [spline_reference.md](spline_reference.md).

---

## What this work's content layers contain

The framework's layer references are work-agnostic vocabularies; *Spatium Dimensio*'s content layers add the work-specific material that travels through those vocabularies:

- **[Spline Reference](spline_reference.md)** — the seven movements with their typed signals and invariants
- **[Transition Reference](transition_reference.md)** — the six joins with full continuity specs
- **[Character Reference](character_reference.md)** — the figures who recur across movements (the Maker, the Seeker, the Witnesses, the Child Who Walks Past)
- **[Object Reference](object_reference.md)** — the material things with continuity across movements (the Rod, the Cathedral, the Stick, the Three Rods, the Field)
- **[Motif Reference](motif_reference.md)** — recurring patterns (the Call-and-Response, the Through-Drone, the I↔VII Frame, others)
- **[Provenance Notes](provenance_notes.md)** — intellectual and material lineage of the work

The work-agnostic vocabularies — what mediums exist, what visual worlds exist, what voice options exist, what realization patterns exist — live in the [framework directory](../../framework/) and are shared across all spline scores.

---

## Rules specific to this work

These are *Spatium Dimensio*'s own rules, distinct from the framework's general discipline:

1. Seven movements in order, none skipped or reordered
2. Continuity grades respected between movements (per transition reference)
3. Math content uses defined visual/audio language regardless of aesthetic — the math primitives are the work's content; surface layers render but don't replace them
4. The rod is shown as a tool, not a villain
5. The work ends on the body, not the tool
6. No realization is canonical — the score is the work

---

## Realizations of this work

Realization specs that Spatium ships (Sacred Ritual, Field Notebook, Cosmic Horror, Existential Thriller, Funeral Rite, Technical Essay, Fairytale, Lecture, Critique, Personal Letter, Chrome-Glitch Audiovisual, Children's Book, Bedtime Lullaby) live in [realizations/](realizations/) as individual spec files. Each is a complete cross-layer compositional treatment.

For *Spatium Dimensio* specifically, the canonical realization is the user's own — Chrome-glitch audiovisual, which sits closest to the work's visual lineage. Other realizations stand as demonstrations of the spline's flexibility and as invitations: the same score can be a sacred ritual or a children's book or a field notebook or a cosmic-horror testimony, and each is a true performance.

---

## How to read or perform this work

To **read about the work**: start with this README, then the spline reference for the seven movements' material.

To **construct a realization**: read the [framework's realization workflow](../../framework/realization_workflow_reference.md), choose a realization from [realizations/](realizations/) (or construct a new one), and run the work's spline through the framework's eight composition passes.

To **author your own spline score** rather than realizing this one: see [Compositional Algebra README](../../README.md) for framework guidance, and study this work's spline and content layers as a worked example.

---

## A note on origin

*Spatium Dimensio* was the work that motivated the construction of Compositional Algebra. The framework's tier system, lock concept, signal-flow architecture, layer references, and realization workflow all emerged in the course of authoring this spline score. The framework became formal enough to apply to other works only after *Spatium Dimensio* had been worked through with sufficient discipline that its construction methods could be named and reused.

The framework is now independent of this work, but the work and the framework remain in close conversation: extensions to the framework that come up while authoring *Spatium Dimensio* (new sub-function options, new presets, new realization patterns) get added in the framework's layer references first, then used in this work.

---

## Current status

*Spatium Dimensio* is **on hold** while Compositional Algebra is iterated through the [Calibration spline score](../calibration/README.md). Calibration is a three-movement test/calibration suite that doubles as fast-iteration harness and verification of framework claims. The framework changes happening during Calibration work (Shape sub-field, audio-first surface composition, polish elimination, 12-pass workflow with cross-modal Pass 6 substitution and Pass 7 outline, Voice translation, translation discipline) will be back-applied to *Spatium Dimensio* once the framework stabilizes.

Spatium's current spec includes preliminary Shape additions per movement, but these are draft — there is an open finding (see `DEV_LOG.md`) about whether Spatium's declared continuity grades (some C¹, some C²) reconcile cleanly with its draft Shapes. Resolution deferred until Calibration confirms the framework's continuity-grade rules.
