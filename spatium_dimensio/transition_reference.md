# Transition Reference

Transitions are the joins between movements. Each transition is a constructable spec — not just a continuity grade but a typed function specifying what carries, what shifts, what bridges the gap.

*Spatium Dimensio* has six transitions (I→II, II→III, III→IV, IV→V, V→VI, VI→VII). The spline declares each transition's grade and prose "what must connect"; this reference specifies the full transition function and provides implementations for all six.

---

## The Transition Function

```
Transition: [N → N+1]

Inputs:
  From spline:
    — Prior movement (N) closing state
    — Next movement (N+1) opening state
    — Declared continuity grade
  From all layer outputs at end of movement N:
    — Math Visual output (primitives present)
    — Math Audio output (sonic primitives present)
    — Character Reference output (characters present, their state)
    — Object Reference output (objects present, their state)
    — Motif Reference output (motifs invoked, their intensity)
    — Visual surface output (medium × visual world rendering)
    — Audio surface output (audio aesthetic rendering)
    — Voice output

Per-transition definition:
  Grade (C⁰ / C¹ / C²)
  Felt quality of the join (cut / shift / unfold)

Per-transition response:
  Identity carry
    — Invariants across the join (what every realization must preserve)
    — Flexibility at the join (what may vary by realization)
  Math primitive carry
    — Visual primitives that persist (and at what density change)
    — Sonic primitives that persist
    — New primitives introduced at N+1 that emerge from N
  Character carry
    — Which characters persist from N to N+1
    — Character state at the join (what they carry forward)
    — Characters that enter or depart at the join
  Object carry
    — Which objects persist from N to N+1
    — Object state at the join (condition, scale, role)
    — Objects that appear or recede at the join
  Motif carry
    — Which motifs continue from N into N+1
    — Motif intensity change across the join
    — Motifs that enter or quiet at the join
  Surface continuity
    — Medium sub-functions: which hold, which shift
    — Visual world sub-functions: which hold, which shift
    — Audio aesthetic sub-functions: which hold, which shift
  Voice continuity
    — Register continuity (carry, shift, or break)
    — Stance continuity
    — Positioning continuity
    — Configuration shift (and how — collapse, expand, persist)
  Bridging elements
    — Specific anchors that span the join (shared palette element, shared primitive, shared phrase rhythm)

Output:
  Continuity polish specifications for Prompt Construction
  Anti-drift requirements for the join
```

### Continuity grades

Continuity grades are now derived from the Shape sub-field of Identity (departure tangent of movement N vs approach tangent of movement N+1):

- **C⁰ (cut):** direction mismatch permitted. Sharp break, no carryover required. Position match only. The join is meant to be felt as discontinuity.
- **C¹ (shift):** direction must match (both rising, both falling, both held); magnitude may differ. Pacing or core rhythm holds; content shifts. The join is felt as continued motion changing direction.
- **C² (unfold):** direction *and* magnitude must match (steep-to-steep, gradual-to-gradual). The new state emerges from within the previous; both are felt at the moment of join. The join is not felt as a join.

Transitions still author the join's content (what carries, what bridges, what shifts); Shape constrains the join's smoothness at the tangent level.

### Note on higher-order continuity (C³+)

The current Shape vocabulary supports continuity grades up to C². Higher-order grades (C³ jerk-match, C⁴ snap-match, C^∞ analytic continuation) are mathematically valid and could be added when authoring needs warrant.

Adding them would require extending Shape with a fourth sub-function specifying tangent-of-tangent (how the acceleration itself changes at the knot). Currently no spline score requires this granularity; the framework caps at C² honestly rather than claiming finer continuity than its vocabulary can verify.

This is a deliberate open extension point: add C³+ vocabulary when a spline score genuinely needs the distinction, not before.

### Felt quality

- **Cut:** abrupt; the listener/reader registers the change
- **Shift:** continued attention with redirected focus; the eye/ear follows
- **Unfold:** continuous becoming; the new arrives from inside the old

Grade and felt quality are correlated but not identical. A C¹ join can be felt as a shift or as an unfold depending on bridging. A C² join cannot be felt as a cut.

### How to Construct a New Transition

1. Read prior movement's closing state and next movement's opening state.
2. Read the spline's declared continuity grade.
3. Define felt quality of the join.
4. Specify Identity carry: invariants (what must hold) and flexibility (what may vary).
5. Specify Math primitive carry: which primitives persist, which emerge, with density change.
6. Specify Surface continuity at sub-function level for both audio and visual (audio first as temporal substrate).
7. Specify Voice continuity across register, stance, positioning, configuration, affect.
8. Name bridging elements: specific anchors that span the join.
9. Output continuity material for Pass 6 (substitution) and Pass 7 (outline), applied cross-modally to all three prompts.

---

## The Six Transitions

### I → II (The Reach → The Rod)

- **Grade:** C¹
- **Felt quality:** Shift — the field continues; a new element enters
- **Movement change:** ground-state extension → tool arrival

**Identity carry:**
- **Invariants:** body present and reaching; field still felt as ground; the work has just begun (no apparatus yet dominant)
- **Flexibility:** how the rod arrives (handed, found, fashioned); from where; by whom

**Math primitive carry:**
- **Visual persists:** the unmeasured line of I (now joined by vectors with arrowheads)
- **Sonic persists:** drone or breath of I (now joined by first pitched voice)
- **Newly introduced:** basis vectors, axes at origin, unit intervals; first pitched intervals, defined root note
- **Density change:** minimal → low

**Surface continuity:**
- **Medium sub-functions:** substrate holds; mark-making can shift (brush → dip pen if introducing precision); surface behavior holds; edge quality can sharpen; color holds
- **Visual world sub-functions:** palette holds; light holds; line may sharpen; figure persists; atmosphere holds
- **Audio aesthetic sub-functions:** tonality shifts from drone-based to drone-plus-pitched; texture shifts from monophonic to drone+figure; rhythm gains first pulse; pacing holds; spatialization holds; phrasing holds

**Voice continuity:**
- **Register:** holds (same speaker)
- **Stance:** holds
- **Positioning:** holds
- **Configuration:** solo → solo or character (character may emerge to deliver the rod)

**Bridging elements:**
- The drone of I sustained under the rod's first pitched note
- The body of I still visibly present as the rod arrives
- The same voice introducing both the field and the tool

**Continuity polish:**
- "Field of I still felt under II; rod arrives into the field, not as replacement"
- "Drone uninterrupted; new sonic element enters without breaking the previous texture"
- "Voice continues at same pace; new vocabulary enters but rhythm doesn't change"

---

### II → III (The Rod → The Many Names)

- **Grade:** C²
- **Felt quality:** Unfold — plurality emerges from inside the rod's arrival
- **Movement change:** singular tool → parallel settlements

**Identity carry:**
- **Invariants:** rod present (now as one tool among many); body present; field still felt; no hierarchy among the parallel settlements that emerge
- **Flexibility:** which traditions are shown; how many; in what arrangement

**Math primitive carry:**
- **Visual persists:** basis vectors of II (now joined by other coordinate systems); vector space
- **Sonic persists:** rod's pitched voice (now joined by other tonal systems)
- **Newly introduced:** polar coordinates, hexagonal tiling, manifolds, graph/network; polytonal/multi-system tonality, polyphonic texture
- **Density change:** low → medium

**Surface continuity:**
- **Medium sub-functions:** substrate may shift toward layered (to render plurality); mark-making may add additional methods; surface behavior holds or shifts toward discontinuous; edge quality holds; color may broaden
- **Visual world sub-functions:** palette may broaden; light holds; line may vary across settlements; figure may multiply or differentiate; atmosphere holds or expands
- **Audio aesthetic sub-functions:** tonality expands from single system to polytonal; texture expands to polyphonic; rhythm holds or expands to polyrhythm; pacing slows and broadens; spatialization expands to distributed; phrasing holds

**Voice continuity:**
- **Register:** may hold (single narrator) or expand to chorus of registers (the many traditions speaking in turn)
- **Stance:** holds
- **Positioning:** holds
- **Configuration:** solo or character → chorus or layered; if shifting to chorus, the original voice opens *into* the chorus rather than being replaced

**Bridging elements:**
- The rod of II remains visible as one settlement among many
- Voices that began as one open out into many (chorus emerging from solo)
- The first pitched system of II remains audible against the new systems

**Continuity polish:**
- "Rod of II still visible/audible as one among the many of III, not absorbed into the plurality"
- "If voice shifts to chorus, the solo of II opens into the chorus rather than ceding to it"
- "Primitives of II do not disappear — they take their place alongside others"

---

### III → IV (The Many Names → The Cage)

- **Grade:** C¹
- **Felt quality:** Shift — plurality compresses, one settlement asserts itself
- **Movement change:** parallel settlements → single dominant frame

**Identity carry:**
- **Invariants:** the cage emerges from within III's plurality (a settlement choosing itself, not external imposition); the body present, now contained; the rod becomes architecture
- **Flexibility:** which settlement becomes dominant; how the closure is rendered

**Math primitive carry:**
- **Visual persists:** vectors, basis, vector space (now dominant); projection
- **Sonic persists:** pitched voices (now compressed); rhythmic elements (now metronomic)
- **Lost or backgrounded:** the other coordinate systems of III; graph/network; manifold (compressed or absent); polyphony
- **Newly introduced:** dominant ℝ³; distance formula; full projection apparatus with dashed lines and coordinate values
- **Density change:** medium → high

**Surface continuity:**
- **Medium sub-functions:** substrate may shift to canvas/panel/screen (to support compression); mark-making may shift to opaque; surface behavior shifts to opaque/layered; edge quality sharpens; color behavior shifts to opaque saturated
- **Visual world sub-functions:** palette may narrow and intensify; light may shift to theatrical chiaroscuro or flat; line sharpens; figure becomes contained; atmosphere shifts to compressed
- **Audio aesthetic sub-functions:** tonality narrows to equal temperament (or single tonal system); texture compresses to homophonic; rhythm becomes metronomic; pacing compresses; spatialization collapses to mono or centered; phrasing tightens

**Voice continuity:**
- **Register:** holds (same speaker can continue) or shifts to a more declarative register (e.g., mathematician, scientist) if the cage demands stated content
- **Stance:** may shift toward cynic (the cage exposed as cage) or realist (the cage named operationally)
- **Positioning:** may shift toward academic or specialist (the cage demands rigor)
- **Configuration:** chorus or layered → solo (the plurality of III collapses)

**Bridging elements:**
- One voice from III's chorus continues alone into IV (the dominant settlement)
- One coordinate system from III asserts itself as the frame of IV
- The polyphonic mass of III narrows into the single dominant tonal mass

**Continuity polish:**
- "Moment of compression felt as a settlement choosing itself, not as external imposition"
- "Cage of IV emerges from within III's plurality — not arriving from outside"
- "If chorus collapses to solo, one voice from the chorus continues alone"

---

### IV → V (The Cage → The Body That Exceeds)

- **Grade:** C²
- **Felt quality:** Unfold — the field returns from inside the cage's compression
- **Movement change:** single dominant frame → field exceeding the frame

**Identity carry:**
- **Invariants:** cage exceeded but not destroyed (its reality preserved); body present, now radiating; field returns larger than the cage admitted
- **Flexibility:** which non-Euclidean spaces are foregrounded; how the body's radiance is rendered

**Math primitive carry:**
- **Visual persists:** ℝ³ of IV (now shown as one space among many); the cage's projection apparatus (now relativized)
- **Sonic persists:** the dense chord of IV (now revealed as projection of a larger sonic space)
- **Newly introduced:** configuration space, function space, Hilbert space, fractal dimension, high-dimensional embedding; microtonal intervals between equal-temperament pitches, polyrhythm against the metronome, ambisonic field
- **Density change:** high → high (different content, same density)

**Surface continuity:**
- **Medium sub-functions:** substrate may persist (screen for chrome-glitch, canvas for sacred painting); mark-making may expand to include more layered approaches; surface behavior may expand to smooth-rendered with HDR; edge quality may include both clean rendered and soft bleed; color expands toward HDR/prismatic
- **Visual world sub-functions:** palette expands (often toward chromatic excess or prismatic); light becomes specular/prismatic or painted-from-within; line may dissolve toward smooth rendered or remain painted realism; figure radiates or fractures; atmosphere shifts to synesthetic or expansive
- **Audio aesthetic sub-functions:** tonality opens to microtonal or polytonal; texture expands to polyphonic or stratified drones; rhythm expands to polyrhythm; pacing shifts to expansion; spatialization opens to ambisonic; phrasing opens to through-composed

**Voice continuity:**
- **Register:** may hold or expand to multiple registers in layered configuration
- **Stance:** often shifts toward idealist (V's pointing-beyond)
- **Positioning:** holds or shifts toward congregational/artistic peers
- **Configuration:** solo of IV → layered (most natural for V), or solo expands by partials emerging from within the single voice

**Bridging elements:**
- The cage's compressed chord remains audible as one partial within V's expanded harmonic field
- The figure inside the cage at IV's close begins to radiate light past the cage walls
- The voice of IV continues but its assertion begins to be heard as one among many possible assertions

**Continuity polish:**
- "V emerges from inside IV's compression — as if the body inside the cage has begun to radiate past its walls"
- "Transition must not feel like victory cut; must feel like fact becoming visible"
- "The cage's reality is preserved; only its claim to be the world is relativized"

---

### V → VI (The Body That Exceeds → Quiet Recognitions)

- **Grade:** C¹
- **Felt quality:** Shift — the expansion settles into stillness
- **Movement change:** field exceeding → recognitions converging

**Identity carry:**
- **Invariants:** what V revealed persists as memory; recognitions arrive from multiple traditions; no single recognition foregrounded; no second climax
- **Flexibility:** which traditions/witnesses appear; how many; how arranged

**Math primitive carry:**
- **Visual persists:** the spaces of V as background memory (configuration space, Hilbert space, fractal — now sparse and quieter)
- **Sonic persists:** drone re-emerges enriched by V's harmonic memory
- **Lost or backgrounded:** polyphonic excess of V; high density of primitives
- **Newly introduced:** Cauchy sequence converging; complementary measurement bases (orthogonal pairs); topological invariants
- **Density change:** high → low

**Surface continuity:**
- **Medium sub-functions:** substrate may persist or shift toward paper/panel (intimate scale); mark-making may quiet; surface behavior settles; edge quality may soften; color quiets
- **Visual world sub-functions:** palette quiets (may shift toward earth-and-gold, intimate sacred, or earth-muted); light shifts toward low ambient or painted-from-within; line may soften (stippled, classical); figure settles into postures of recognition; atmosphere shifts to gathered, sacred, intimate
- **Audio aesthetic sub-functions:** tonality settles to modal or drone-based; texture thins to heterophonic or stratified drones; rhythm becomes arhythmic; pacing shifts to stillness or slow unfolding; spatialization holds positions without movement; phrasing opens to unphrased

**Voice continuity:**
- **Register:** holds or quiets
- **Stance:** may shift toward realist (the recognitions named operationally) or hold idealist
- **Positioning:** often shifts toward congregational (the gathered)
- **Configuration:** layered → call-and-response or chorus (typical) — voices fall away one by one until quiet, then the call-and-response or chorus structure emerges

**Bridging elements:**
- The drone from V quiets but persists into VI as enriched ground
- Voices from V's layered configuration fall away one at a time
- The recognitions of VI arrive in the same harmonic field V opened

**Continuity polish:**
- "VI feels like the moment after a long exhale"
- "V's expansion doesn't disappear, it settles"
- "If V was layered voice, voices fall away one by one until quiet"

---

### VI → VII (Quiet Recognitions → Set Down the Rod)

- **Grade:** C²
- **Felt quality:** Unfold — the close emerges from within the gathering
- **Movement change:** recognitions held → tool released

**Identity carry:**
- **Invariants:** rod set down (present, no longer dominant); body walks on; reach of I recovered (now informed); both rod and field present at close
- **Flexibility:** specific gesture of release; specific final image of departure; whether or how the rod is acknowledged in farewell

**Math primitive carry:**
- **Visual persists:** recognitions of VI (the witnesses, the convergence); Euclidean frame from II (returns at reduced scale); the unmeasured line of I (returns)
- **Sonic persists:** drone of VI now returning to the drone of I, enriched; rod's pitched voice from II at low volume within the drone
- **Lost or backgrounded:** Cauchy convergence (the limit is reached and released); compression apparatus
- **Newly introduced:** nothing new — VII closes with what came before, transformed
- **Density change:** low → minimal

**Surface continuity:**
- **Medium sub-functions:** substrate may shift toward paper (lightness recovered) or persist; mark-making quiets; surface behavior opens (absorbent or sparse); edge quality may soften toward soft bleed; color quiets toward translucent or monochrome
- **Visual world sub-functions:** palette quiets toward I's openness (warm earth, body-and-starlight, or earth-and-gold settled); light returns toward I's painted-from-within or low ambient; line quiets; figure walks on (resolved posture); atmosphere shifts toward intimate sacred or gentle narrative
- **Audio aesthetic sub-functions:** tonality returns toward drone-based or modal; texture returns toward monophonic or drone+figure; rhythm returns to unmetered/breath-driven; pacing returns to stillness or slow unfolding; spatialization returns to ambient or stereo; phrasing returns to open/unphrased

**Voice continuity:**
- **Register:** often returns to the opening register of I (creating arc)
- **Stance:** often returns to realist or idealist
- **Positioning:** often returns toward intimate or congregational
- **Configuration:** call-and-response/chorus of VI → solo (the work closes on the body, the body is singular)

**Bridging elements:**
- The drone of I returns enriched — the harmonic memory of everything that passed through
- The original voice of I returns at the close (or the work closes in the same register it opened)
- The rod's pitched voice from II is released — a single pitch placed against the drone, then receding

**Continuity polish:**
- "VII feels like natural consequence of VI's settling; not a new movement but the close of the gathering"
- "Drone of I returns enriched, not naive"
- "The rod must be set down, not destroyed — it remains where it lies"
- "The work ends on the body, not the tool"

---

## Cross-Transition Patterns

**Where C¹ and C² fall:**

- C¹ joins (I→II, III→IV, V→VI): shifts. New element enters or dominance shifts.
- C² joins (II→III, IV→V, VI→VII): unfolds. The new emerges from within the previous.

**Why this pattern:**

C² joins are the ones where the work most needs to feel continuous — pluralization (II→III), release (IV→V), close (VI→VII). C¹ joins are the ones where something genuinely new arrives — tool (I→II), cage (III→IV), settling (V→VI).

**Transition pairs:**

- I↔VII frames the work (drone returning enriched)
- II↔V show the apparatus arriving and being exceeded
- III↔VI show plurality and gathering (both multi-voice)
- IV stands alone as the structural center

---

## How Transitions Connect to the Spline and Other Layers

Transitions read all layer outputs at the close of movement N and prepare them for movement N+1. The transition reference is consumed by Pass 6 (substitution) and Pass 7 (outline) cross-modally for continuity across image, audio, and narrative prompts.

**To compose a transition:**
1. Read the spline's transition notes for the join (grade derived from Shape, what must connect)
2. Read all layer outputs at end of N (math, surface, voice)
3. Read all layer requirements at start of N+1
4. Apply the per-transition spec from this reference: identity carry, math carry, surface continuity, voice continuity, bridging
5. Output continuity material — routed to Pass 6 (substitution) and Pass 7 (outline) cross-modally

**Transition outputs feed:**
- **Pass 6 substitution** for cross-modal continuity (work-specific identity threading across joins in all three prompts)
- **Framework-external image/audio production** for visual and sonic continuity (reference images, shared tonality specs, human-in-the-loop polish)
- Surface layers' continuity sections (audio aesthetic changes, medium changes, visual world changes between movements — informing how realizations construct adjacent movements)
- Voice continuity across all five sub-functions (register, stance, positioning, configuration, affect)
- Math primitive carry sections in Math Audio and Math Visual

**What this layer guarantees:**
- The joins between movements are specified at the same depth as the movements themselves
- Realizations have explicit guidance on what must hold across joins and what may vary
- Continuity is not just a grade label but a typed spec of which sub-functions hold and which shift
