# Toy Catalog — Full Sketch Before Building
### Visual toys + paired vocabulary + where each picture lies. Build order TBD.

> ## ★ THIS IS THE PARENT INDEX (re-established 2026-06-01)
> The toys below are the catalog. Originally 15 (the pre-build sketch); EXPANDED to 20 on 2026-06-01 with T16–T20,
> a new "Invariance, Measurement & Structure" track surfaced by the deep TS work (the concepts that turned out
> load-bearing once a toy was built all the way down — see that track's note + the second cross-track spine).
> Some toys have GROWN into standalone projects with their own deep work (files/plans/findings); most are still
> sketches awaiting a first build. This catalog is the MAP — every developed project reports its lineage back
> here, and a grown project does NOT delete its original toy: a focused, original-domain version of the same toy
> can still have independent value even after the big version outgrew the sketch. The list is meant to be
> COMPREHENSIVE — we build what we need as we need it; there's no harm in more entries than we'll build soon.
>
> **Status key:** `[SKETCH]` = catalog sketch only, nothing built · `[GROWN]` = spawned a standalone project,
> has its own files/state · `[REVISIT?]` = the grown version outran the original-domain toy, which may still be
> worth building small in its own right.
>
> **Status as of 2026-06-01 (to be confirmed per-project when we go over each):**
> - **TS (Trajectoscope)** — a large standalone project (dimension-as-relational-structure, epicycles-in-affine-
>   space, the identity/fingerprint instrument; current file TS_formulas.html, with TS_4D/TS_3D frozen priors,
>   multiple plans + findings.md). It STARTED as a toy here and grew into its own thing. Which toy it started
>   from is not pinned — closest is **T8 (planes-not-axes rotation)**, possibly drawing on **T4 (function/ path
>   as point)** too. → mark T8 `[GROWN→TS]`; T4 flagged as possibly-feeding-TS. If a focused original-domain T8
>   (or T4) still has value as its own small sandbox, that's `[REVISIT?]`.
> - **Spline / coupled-continuity thread** — also started as a toy and grew (the "felt-sense of high-dimensional
>   relational continuity" intuition; relational not spatial). Its original-domain toy is plausibly **T4** or a
>   not-yet-listed continuity sandbox. → flag pending its own brief; revisit the original if warranted.
> - **All other toys (T1–T3, T5–T7, T9–T15)** — `[SKETCH]`, unchanged, awaiting a first build.
>
> Per-project briefs (what each grown thing IS, its current state, its proper home, and whether to revisit the
> original toy) will be written ONE AT A TIME in follow-up passes.

**The loop each toy serves:** play -> see the structure -> name it (vocab) -> know its failure mode. Vocab is fused to each toy, not separate. The "where it lies" line is the rigor-guard folded into the vocab layer (replacing what proofs would otherwise catch).

**Honesty flag:** Math/signal toys = real interactive sandboxes, buildable now. Humanities toys = interactive diagrams/annotated structures, a different and softer kind of object. Marked [SANDBOX] vs [DIAGRAM] throughout.

---

## TRACK: Mathematical Foundations

**T1 — Epsilon-Delta Game** [SANDBOX]
- *sees:* a limit as a challenge-response: drag epsilon, watch the sequence tail get trapped past some N.
- *vocab:* limit, convergence, epsilon-N, "for all... there exists."
- *lies:* suggests every sequence "settles" visibly; hides sequences that converge too slowly to see, and the role of completeness.

**T2 — Cauchy vs Convergent / the holes in Q** [SANDBOX]
- *sees:* sequences bunching on themselves vs homing to a point; the rationals' "missing" limit points.
- *vocab:* Cauchy sequence, completeness, dense, limit point.
- *lies:* the holes look like gaps you could "see"; really they're invisible — that's the whole subtlety.

**T3 — Distance Is a Choice (metrics)** [SANDBOX]
- *sees:* same point-set, swap the metric, watch "nearest neighbor" and "open ball" change shape.
- *vocab:* metric, open ball, neighborhood, topology-from-metric.
- *lies:* makes "distance" feel always-geometric; hides metrics with no visual analog (function-space metrics).

**T4 — Function Space as Points** [SANDBOX] · ◇ possibly feeds TS and/or the spline/coupled-continuity thread (the function/path-as-point + relational-continuity intuition); confirm per-project. Original-domain T4 likely still valuable in its own right.
- *sees:* whole functions plotted as single points in a space; "moving" through the space morphs the function.
- *vocab:* function space, norm, the leap from finite to infinite dimensions.
- *lies:* the 2D/3D depiction of an infinite-dimensional space is a deep simplification — the most load-bearing lie in the catalog, flag it hard.

**T5 — Hilbert Projection / Fourier** [SANDBOX]
- *sees:* project a function onto sine/cosine axes, watch the approximation build term by term.
- *vocab:* inner product, orthogonality, basis, projection, Fourier series.
- *lies:* finite visual sums converge nicely; hides convergence subtleties (Gibbs, pointwise vs uniform).

## TRACK: Differential Geometry (the visual summit candidate)

**T6 — Curvature Sandbox** [SANDBOX]
- *sees:* bend a surface, watch geodesics and angle-sums-of-triangles change; flat vs sphere vs saddle.
- *vocab:* manifold, curvature, geodesic, intrinsic vs extrinsic.
- *lies:* always shows surfaces *embedded* in 3D; hides that curvature is intrinsic (doesn't need the ambient space) — the conceptual core.

**T7 — Tangent Space** [SANDBOX]
- *sees:* the flat plane that best-approximates a curved surface at a point; how it tilts as you slide the point.
- *vocab:* tangent space, local linearity, the derivative-as-map.
- *lies:* makes tangent spaces feel like literal planes sitting in space, not abstract attached vector spaces.

**T8 — Planes-Not-Axes Rotation (your instinct, made real)** [SANDBOX] · ★ `[GROWN→TS]` (see parent-index header; TS is the deep standalone descendant — TS_formulas.html etc. A focused original-domain T8 may still be worth a small build: `[REVISIT?]`)
- *sees:* rotation as happening *in a plane*, not around an axis; in 4D, two independent rotation planes at once.
- *vocab:* rotation plane, bivector, degrees of freedom = n(n-1)/2, SO(n).
- *lies:* 4D shown via projection — you see a shadow, not the thing. This is *the* toy for the dimension-rotation question you couldn't articulate.

## TRACK: Algebra of Operations (Category Theory)

**T9 — Composition Machine** [SANDBOX]
- *sees:* objects as dots, morphisms as arrows; drag to compose, watch associativity and identity hold.
- *vocab:* object, morphism, composition, identity, associativity.
- *lies:* tiny finite diagrams hide that the power is in *generality* across wildly different domains.

**T10 — Functor as Structure-Preserving Map** [SANDBOX]
- *sees:* one category mapped onto another; structure (arrows) preserved or broken under different maps.
- *vocab:* functor, structure preservation, faithful/full.
- *lies:* visual one-to-one mapping undersells what "preserves composition" really constrains.

## TRACK: Signal & Process Architecture (Denotational Design)

**T11 — Meaning vs Execution** [SANDBOX]
- *sees:* one denotation (what it *means*) with several implementations (how it *runs*); change implementation, meaning stays fixed.
- *vocab:* denotation, semantics, referential transparency, spec-vs-implementation.
- *lies:* clean separation shown; real systems leak (performance, effects) — the leaks are where design lives.

**T12 — Signal as Function of Time** [SANDBOX]
- *sees:* a signal as a continuous function; sample it, transform it, compose signals.
- *vocab:* signal, continuous-time semantics, composition of behaviors.
- *lies:* continuous depiction hides sampling/discretization reality.

## TRACK: Composition — Schenker [DIAGRAM]

**T13 — Reduction Layers**
- *sees:* a musical surface peeled back through middleground to the Ursatz; interactive layer-toggle.
- *vocab:* Ursatz, prolongation, structural level, foreground/middleground/background.
- *lies:* presents one reduction as *the* reduction; analysis is interpretive, not unique — a key humility.

## TRACK: Narrative & Voice — Genette [DIAGRAM]

**T14 — Story vs Discourse Reorderer**
- *sees:* events in chronological "story" order vs the "discourse" order they're told in; drag to reorder, see flashback/foreshadow emerge.
- *vocab:* story/discourse, order, duration, frequency, focalization, voice.
- *lies:* clean separation of story from discourse is itself a theoretical stance, not a fact.

## TRACK: Script / Performable Text — Stanislavski [DIAGRAM]

**T15 — Beat & Intention Map**
- *sees:* a script segmented into beats, each tagged with an intention/action; watch the through-line assemble.
- *vocab:* beat, objective, action, through-line, active analysis.
- *lies:* makes intention look fixed/single; performance is live and variable.

## TRACK: Invariance, Measurement & Structure (added 2026-06-01 — surfaced by the deep TS work)

*These five were not in the original sketch. They are the concepts that turned out LOAD-BEARING once a toy (TS)
was built all the way down — the ideas that kept catching errors and kept being the thing that mattered. They
read as a tight cluster: a transformation (T19, symmetry) has things it leaves unchanged (T16, invariants), you
detect those with a measurement (T17) that is always lossy and has blind spots, and you must not confuse the
form with how it's sampled (T18) or how its trajectory closes (T20). T16+T17+T19 are the partner-concepts under
half the original catalog (T8's rotation invariants, T6's intrinsic curvature, T3's metric-dependence), finally
named in their own right.*

**T16 — Invariants: What Survives a Transformation** [SANDBOX]
- *sees:* transform an object (rotate, stretch, reparameterize, change frame) and watch a panel of measured
  quantities — some HOLD STILL (invariants), some DRIFT. Identity = the set that survives.
- *vocab:* invariant, equivalence class, "identity is what's preserved," intrinsic vs frame-dependent quantity.
- *lies:* suggests the invariants you happen to measure are THE invariants; a different/coarser measurement set
  defines different equivalence classes (so "same" is relative to what you chose to measure — see T17).

**T17 — The Lossy Ruler: A Measurement Has Blind Spots** [SANDBOX]
- *sees:* two genuinely-different objects that a chosen descriptor reports as IDENTICAL; swap to a richer
  descriptor and watch the difference appear. The ruler decides what you can't distinguish.
- *vocab:* descriptor/feature vector, resolving power, blind spot, completeness of an invariant set, "absence of
  a detected difference ≠ absence of difference."
- *lies:* makes "they measured the same so they're the same" feel safe; conflation is the measurement CHOOSING
  not to see a difference, not the difference being absent. (This is the rigor-lesson the TS blind spot proved.)

**T18 — Sampling vs the Thing: When the Render Lies** [SANDBOX]
- *sees:* a form emerging from a trajectory as samples accumulate; at low fill it LOOKS like a different shape
  (a lacy "flower," a sparse wireframe) than the dense object it converges to. Slide the sample count and watch
  the apparent form change while the true form doesn't.
- *vocab:* sampling, density, fill artifact, the map vs the territory, convergence of an empirical estimate.
- *lies:* the depiction tempts you to read a fill-state as a form-feature (the "flower"/"cube-that-wasn't" trap);
  a true shape-measure must be fill-invariant, and confirming adequate sampling is a precondition for any claim.

**T19 — Symmetry: The Transformations That Leave a Thing Unchanged** [SANDBOX]
- *sees:* apply transformations to an object and collect the ones under which it looks identical — that
  collection IS its symmetry group; compose two symmetries, get another; watch group structure emerge.
- *vocab:* symmetry group, group axioms (closure/identity/inverse/associativity), generators, degrees of
  freedom, SO(n) vs SE(n) (compact vs not). Partner concept to T16 (a group's invariants are what it preserves).
- *lies:* tiny finite symmetry sets hide that the power is the GROUP STRUCTURE (which groups are the "same,"
  which aren't — e.g. SE(3) and SO(4) are both 6-dimensional yet non-isomorphic, a distinction that mattered).

**T20 — Closure: Commensurate vs Incommensurate** [SANDBOX]
- *sees:* two coupled oscillations; tune their frequency RATIO. Rational ratios CLOSE into a finite repeating
  curve; irrational ratios never close and densely FILL the available form. Drag the ratio across the boundary.
- *vocab:* commensurate/incommensurate, rational vs irrational ratio, closed orbit vs dense (ergodic) fill,
  rotation number, equidistribution (Weyl), winding.
- *lies:* near-rational ratios look closed at low sample counts (they only close much later, or never), blurring
  the rational/irrational line — which is genuinely subtle, not visually crisp (ties to T18's sampling caution).

---

## The Cross-Track Spine (why these belong together)

The catalog's hidden structure: **T8, T13, T14, T15, T11 are all the same toy** — deep structure generating faithful surface. Rotation-plane -> rotated vector. Ursatz -> musical surface. Story -> discourse. Intention -> action. Denotation -> execution. Building several makes the rhyme *felt*, not asserted. That shared structure is the knowledge base's Layer 2.

**Second spine (T16–T20, added 2026-06-01):** a second cluster that rhymes internally — *a transformation (T19) leaves invariants (T16) unchanged; you detect them with a measurement (T17) that is lossy and has blind spots; you must not confuse the form with its sampling (T18) or its closure behavior (T20).* This spine is the RIGOR layer the original catalog gestured at with each toy's "lies" line but never built as its own toys. It also connects the two spines: T8 (rotation) is an instance of T19 (symmetry), and T8's "what's preserved under rotation" is an instance of T16 (invariants). The deep TS work is essentially the first spine's T8 colliding with the entire second spine.

---

## Build-Order Considerations (not decided — for you to weigh)

- **Highest immediate payoff for your dev/design work:** likely T11, T12 (signal/denotation — nearest what you already build) and T9 (composition).
- **Highest "answers a question you already have":** T8 (the rotation-dimension instinct) and T4 (function-as-point, the path-space thread).
- **Easiest first build / fastest win:** T1 or T3 — small, self-contained, classic.
- **Most load-bearing lie to handle carefully:** T4 (infinite dimensions in 2D) and T8 (4D via projection).

*Catalog only. 15 toys sketched, vocab + failure-mode paired to each. No build order chosen, nothing built. Pick the first when ready.*
