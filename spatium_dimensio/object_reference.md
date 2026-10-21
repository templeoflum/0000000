# Object Reference

Objects are the particular perceivable things that persist across movements. Where characters are agents with continuity, objects are material entities with continuity. The rod that arrives at II is the same rod that becomes architecture at IV and the same rod that is set down at VII. Different mediums render the rod differently, but the rod is the same rod.

An object has identity — singular instance, identifiable, with material persistence. This is distinct from a motif (recurring pattern) or a math primitive (abstract content). The rod is an object. "Three rods at a corner" is what the object enables; "the laying-down gesture" is a motif; "basis vector" is the math primitive the rod instantiates. The object is the thing itself.

This reference specifies how objects are constructed, how they modulate across mediums, and how they connect to the spline's per-movement signals.

---

## The Object Function

```
Object: [name]

Inputs:
  From spline (per movement): which objects are present, in what state, with what function
  From Identity signal: universal context per movement

Per-object definition (composed from four sub-functions):
  Material identity — what the object is as a thing
  Symbolic weight — what the object means / carries within the work
  Transformation state — how the object changes (or doesn't) across movements
  Continuity invariants — what every realization must preserve about the object

Per-object response:
  Per-movement state (where it is, what condition, what role)
  Medium modulation (how the object is rendered in each modality)

Output:
  Specification consumable by surface layers, voice, narrative, script
```

### Construction guide

To add an object to *Spatium Dimensio*:

1. Name the object (concrete and specific — "the rod," "the cathedral," not "tool" or "structure")
2. Specify material identity (what the object is physically; its components, its scale, its material)
3. Specify symbolic weight (what the object means within the work; what it carries beyond its material form)
4. Specify transformation state (how the object appears, changes, or is altered across the movements it appears in)
5. Declare continuity invariants (what every realization must preserve)
6. Specify per-movement state (which movements the object appears in, in what condition)
7. Specify medium modulation (how the object renders visually, sonically, narratively, in script)

---

## Sub-Functions

### 1. Material identity

What the object is as a thing.

**Sub-axes:**

- **Form** — physical structure, components, geometry. The rod's form is: linear, marked with units, gilded along its length, with two ends.
- **Scale** — relative size in the work. The rod is hand-sized; the cathedral is monumental; the horizon is vast. Scale is part of the object's identity because it determines how the object operates in scenes.
- **Material substance** — what the object is made of. Wood, gold leaf, stone, light, sound, breath. Some objects are non-physical (the drone is an audible object made of sound).
- **Sensory mode** — which senses register the object. Most objects are visible-and-tactile; some are audible (the drone, the bell); some are conceptual but rendered (the inscription on the vault is visible text carrying conceptual content).

### 2. Symbolic weight

What the object means within the work. This is the work's relationship to the object, not generic symbolism.

**Sub-axes:**

- **Function in the work** — what the object does structurally. The rod is the measuring apparatus; the cathedral is the architecture of measurement asserted as world; the horizon is the unmeasured field's signature.
- **Carried meanings** — what the object embodies. The rod carries the gift of measurement, the danger of measurement-becoming-world, and the possibility of measurement-set-down. These meanings travel with the object.
- **Symbolic relationships** — how the object relates to other objects, characters, and motifs. The rod relates to the figure (the figure uses, is contained by, sets down). The rod relates to the cathedral (the rod's basis becomes the cathedral's architecture). The rod relates to the reach motif (the rod replaces the open reach; the rod is set down to recover the reach).
- **Symbolic invariants** — what the object cannot become without breaking the work. The rod cannot become enemy. The cathedral cannot be destroyed. The horizon cannot be reached.

### 3. Transformation state

How the object changes (or doesn't) across the movements it appears in.

**Sub-axes:**

- **Movements of appearance** — the list of movements where the object is present
- **State per movement** — the object's condition, role, scale of presence per movement
- **Transformation arc** — how the object's appearance and role evolves. The rod arrives small and useful (II), repeated and basis-forming (II close), foregrounded as one settlement among many (III), elevated to architectural scale (IV), preserved at architectural scale while being exceeded (V), present as memory in the gold leaf and craquelure (VI), returned to small and set-down (VII).
- **What is conserved** — what about the object stays the same despite transformation. The rod's gilded surface stays. The rod's unit marks stay. The rod's identity as object stays. What changes is its scale, its role, and its relationship to the figure.

### 4. Continuity invariants

Spec-level commitments any realization must honor.

**Per-object invariants** (declared in the object's spec):

- Material continuity — the same object across all movement appearances (visual recognition required)
- Spatial continuity — when the object appears in successive movements, its position must make sense
- Symbolic invariants — the meanings the object cannot lose or invert
- Transformation legitimacy — only transformations consistent with the object's nature; the rod can become architecture but cannot become a different kind of tool

---

## Medium Modulation

How the same object renders across different output modalities.

### Visual modulation

The object has visual form. Each visual rendering instantiates the object in the medium × visual world spec for the realization and movement.

- **Painted realizations:** the object rendered in the painted idiom (gilded rod in egg tempera for Sacred Ritual; ink-and-wash rod for Fairytale)
- **Drawn realizations:** the object rendered with the line and palette of the realization
- **3D-rendered realizations:** the object rendered as 3D form
- **Schematic realizations:** the object may appear as abstract symbol or named diagram

Across all visual renderings, the object's material identity and identifying features must remain recognizable.

### Audio modulation

Some objects have audible signatures; some are objects of sound directly.

- **Audible objects** (drone, bell, pitched voice as the rod's sonic counterpart): the object IS its sound; rendered through the realization's audio aesthetic
- **Objects with sonic signatures** (rod, cathedral, horizon): when the object enters or transforms, a sonic event may mark it (the rod arriving carries a pitched voice entering; the cathedral closing carries the metronomic pulse beginning; the horizon returning carries the drone's recovery)
- **Silent objects:** some objects have no sonic signature; they appear only in visual and narrative renderings

### Narrative modulation

The object appears in the narrative as described, named, or referenced.

- **Described:** "the rod was gilded along its length, with unit marks burnished into the gold"
- **Named:** "the cathedral closed around the body"
- **Referenced through action:** "someone bent down and lifted the rod" — the object appears through the action involving it

The narrative can dwell on an object (extended description for the rod's setting-down at VII) or reference it briefly. The realization determines tonal weight.

### Script modulation

The object appears in the script as stage direction subject, sensory cue, or production specification.

- **Stage direction subject:** "the rod is placed on the ground at the threshold"
- **Sensory cue:** when the object's appearance is audible or visible, marked as cue (AUDIO: pitched voice enters; VISUAL: gilded rod appears in foreground)
- **Production specification:** for objects requiring physical staging (a rod prop, a model cathedral, projected imagery), the script names what's needed

---

## Canonical Objects of *Spatium Dimensio*

The work has seven canonical objects. Six material; one audible (the drone).

### The Rod

**Material identity:**
- Form: linear, with two ends, marked with unit intervals along its length
- Scale: hand-sized; pace-able; can be laid against the body or paced along the ground
- Material substance: realization-dependent — gilded wood in Sacred Ritual, raw wood in Fairytale, chrome in Chrome-Glitch, ruler/tape in Critique, illustration in Children's Book
- Sensory mode: visible, tactile, sometimes audible (when it strikes ground, when sonified as pitched voice)

**Symbolic weight:**
- Function: the measuring apparatus; the first mark; the unit; the basis when three rods meet at a corner
- Carried meanings: the gift of measurement; the apparatus that becomes architecture; the tool that can be set down
- Symbolic relationships: with the figure (used, contained by, set down); with the cathedral (the rod's basis becomes the cathedral's columns); with the reach motif (replaces, then is set down to recover)
- Symbolic invariants: the rod is never the enemy; the rod is never destroyed; the rod is preserved at VII as set-down, available for anyone to pick up

**Transformation state:**
- II: arrives as singular tool; multiplies into three rods at a corner (basis)
- III: visible as one settlement among five (the Cartesian panel)
- IV: scales to architectural — three columns rising to vault; gold leaf identifying it as the same rod
- V: still visible at architectural scale (cage preserved); the figure radiates past the rod-architecture
- VI: appears as memory in two ways — the gilded craquelure of the witnesses' world; the crossed rods at right angle (complementary bases)
- VII: returns to hand-sized; placed on the ground at the threshold; gilded, unit-marked, intact

What is conserved: gilded surface, unit marks, the rod's identity as object useful at its scale.

**Continuity invariants:**
- Same rod across all seven appearances (visually recognizable)
- Unit marks always visible
- Gilded (or its realization-specific equivalent) throughout
- Never destroyed; never broken
- At VII: set down, not abandoned (placed with care)

### The Cathedral

**Material identity:**
- Form: architectural — columns rising to vault; inscription around perimeter; central altar or center-point where the figure stands
- Scale: monumental — large enough to contain the gathered congregation
- Material substance: stone (Sacred Ritual), concrete/steel (Critique), virtual architecture (Chrome-Glitch), illustrated structure (Children's Book)
- Sensory mode: visible, spatial (you stand inside it); audible (cathedral reverb is the cathedral)

**Symbolic weight:**
- Function: the architecture of measurement asserted as world; the cage that contains the figure at IV; the structure that opens at V and remains standing at VII
- Carried meanings: the closing of plurality into single frame; the beauty and reverence of the measurement program; the structure that preserves what was useful even as it must be exceeded
- Symbolic relationships: with the rod (the rod's basis becomes the cathedral's architecture); with the figure (contains, then is exceeded by, then is walked out of); with the field (the cathedral's interior blocks the field's view; the field remains beyond it)
- Symbolic invariants: the cathedral is beautiful, not just oppressive; the cathedral is preserved, never destroyed; the cathedral was true at its scale

**Transformation state:**
- IV: closes around the figure; the architecture fully asserts itself; the inscription is read
- V: walls hinge open (or the figure radiates past them) — the cathedral is exceeded but stands; the polyptych extends outward from the cathedral
- VI: opened, the witnesses gathered inside the opened space; the cathedral remains as architectural fact
- VII: stands behind the figure; the figure walks out; the cathedral is still there, still working, no longer the world

**Continuity invariants:**
- Same cathedral across all four movement appearances
- The three columns (basis) remain throughout
- The inscription remains visible
- The cathedral is never demolished, ruined, or abandoned
- At VII: cathedral preserved; the figure walks out, the cathedral remains

### The Inscription

**Material identity:**
- Form: text inscribed in gold leaf around the cathedral's vault perimeter; reads "d = √((x₂-x₁)² + (y₂-y₁)² + (z₂-z₁)²)" (the distance formula)
- Scale: large, ceremonial — visible from the floor of the cathedral
- Material substance: gold leaf on stone or equivalent
- Sensory mode: visible, conceptual (it's text carrying meaning)

**Symbolic weight:**
- Function: the cathedral's law; the formula as liturgy; the measurement program made readable
- Carried meanings: the seductive precision of the distance formula; the way mathematics-as-language becomes mathematics-as-decree; the truth-at-its-scale of the formula
- Symbolic relationships: with the rod (the rod's basis enables the inscription's coordinates); with the cathedral (the cathedral's law); with the figure (names the figure's position in three numbers)
- Symbolic invariants: the inscription is true at its scale; the inscription does not lie; the inscription is what it is — the limit of what can be said in three numbers

**Transformation state:**
- IV: inscribed in gold leaf around the vault; treated as liturgical text; read by the gathered
- V: still visible on the vault; relativized but not erased
- VI: visible faintly in the gilded craquelure of the witnesses' surroundings
- VII: still on the vault of the cathedral that stands behind the figure

**Continuity invariants:**
- The formula is the distance formula (not a different formula)
- The inscription is in gold leaf (or realization-specific equivalent) — the inscription is sacred-treated, not mocked
- The inscription remains at V (the formula is not erased)
- The inscription remains at VII

### The Horizon

**Material identity:**
- Form: a line at the visual far edge of the field; gold in Sacred Ritual
- Scale: vast — the limit of vision
- Material substance: light; gold leaf in painted realizations; rendered light in 3D realizations; described boundary in narrative
- Sensory mode: visible; not tactile (cannot be reached)

**Symbolic weight:**
- Function: the unmeasured field's signature; the boundary the body reaches toward but does not arrive at
- Carried meanings: the field's openness; the always-further; the destination that is the walking itself
- Symbolic relationships: with the figure (the figure reaches toward, never arrives); with the reach motif (the reach is reach-toward-the-horizon); with the Cauchy convergence at VI (the limit approached but not reached)
- Symbolic invariants: the horizon is gold (or its equivalent); the horizon is never reached; the horizon returns at VII as it was at I

**Transformation state:**
- I: present as the gold-leaf line at the far edge; the field's signature
- II–IV: present but progressively less foregrounded (in II the field is overlaid by the rod; in III the field is divided among settlements; in IV the cathedral closes the field from view)
- V: returns through the opened cathedral as the field re-emerges; visible at the edge of the polyptych panels
- VI: present in the background of the gathering
- VII: returns fully at the far edge of the open field the figure walks into; the same horizon as I

**Continuity invariants:**
- Same horizon at I and VII (visually recognizable)
- Gold (or realization-equivalent) — the field's signature color
- Never reached
- The horizon is at the edge of perception, not beyond it (it is visible but unreachable)

### The Witnesses' Postures

**Material identity:**
- Form: arrangement of figures in postures of recognition — kneeling, sitting, standing in stillness
- Scale: spread across the wide space, sparse
- Material substance: the witnesses themselves (rendered per realization)
- Sensory mode: visible; spatial

**Symbolic weight:**
- Function: the gathering's recognition made visible; the work's commitment that the recognitions are old
- Carried meanings: across-time gathering; the witness as a position of presence; the postures as the body's natural response to the recognitions
- Symbolic relationships: with the witnesses character (the witnesses adopt these postures); with the chorus (the chorus's call-and-response at VI happens in the spatial field of the postures)
- Symbolic invariants: the postures are reverent; the postures are sparse, not crowded; the witnesses do not leave at VII

**Transformation state:**
- VI: established — the witnesses in their postures
- VII: preserved — the witnesses remain in their postures as the figure walks on

**Continuity invariants:**
- The postures are honored equally — no posture foregrounded
- The witnesses remain at VII
- The postures are reverent, not performative

### The Polyptych

**Material identity:**
- Form: multi-panel painting structure — five panels in III, expanded to many panels around the opened cathedral in V
- Scale: III is congregational-altarpiece scale; V is expanded to encompass the gathered space
- Material substance: painted panels (or realization-specific equivalent — rendered panels in Chrome-Glitch, illustrated spreads in Children's Book)
- Sensory mode: visible

**Symbolic weight:**
- Function: the parallel naming made visible; the work's commitment to plurality of frames; the structural rendering that the rod is one settlement among many
- Carried meanings: equal honor across traditions; the polyptych as the visual form of the chorus's refusal of hierarchy
- Symbolic relationships: with the chorus (the polyptych is what the chorus is naming); with the cathedral (the polyptych contains the cathedral as one panel among many at V); with the witnesses (the polyptych panels surround the witnesses at VI)
- Symbolic invariants: panels are equal in scale and reverence; no panel is more central than another; the rod's settlement is one panel, not the central panel

**Transformation state:**
- III: five panels in sequence, each rendering one coordinate tradition
- V: expanded — the cathedral's walls hinge into the polyptych structure; many panels surround the central cathedral
- VI: visible as the witnesses' surroundings; the panels are now the gathered space's iconographic ground
- VII: visible in the background, behind the figure, as the figure walks out

**Continuity invariants:**
- Panels equal in scale and reverence
- No hierarchy among panels
- The polyptych continues from III to V to VI to VII (same structure, different scales)

### The Drone

**Material identity:**
- Form: sustained sound — the work's continuous through-line
- Scale: persistent throughout all seven movements
- Material substance: sound — varies by realization (acoustic breath, bowed strings, electronic drone, synthesizer pad)
- Sensory mode: audible only

**Symbolic weight:**
- Function: the work's sonic ground; the field rendered as sound; the continuity across all movement
- Carried meanings: the field that gathers; the breath of the work; the through-line that connects I to VII
- Symbolic relationships: with the field motif (the drone is the field made audible); with the figure (the drone is the body's breath made audible at scale)
- Symbolic invariants: the drone never stops; the drone enriches across the work but never becomes a different drone

**Transformation state:**
- I: pure, naked, unmeasured
- II: still present, joined by the rod's pitched voice
- III: present beneath the polytonal field
- IV: tempered to equal temperament (the just-intonation root remains, but the cage tempers the harmonic field)
- V: opens — the drone's microtonal partials emerge; the drone is enriched
- VI: settles — the drone holds a modal coloring; the partials of V become ghost overtones
- VII: returns to I's openness, but enriched — same drone, carrying everything that passed through

**Continuity invariants:**
- The drone is continuous from I to VII (it does not stop)
- The drone's fundamental is consistent across the work (same just-intonation root; same realization-equivalent)
- The drone is enriched, not replaced
- At VII: the drone is the drone of I, enriched by everything that passed through it

---

## How Object Reference Connects to the Kit

The Object Reference reads the spline's object signal per movement and provides specifications consumable by all downstream layers.

**Inputs from spline:**
- Per-movement signal declaring which objects are present, in what state, in what role
- Identity signal for universal per-movement context

**Outputs consumed by:**
- **Surface layers** (Medium, Visual World, Audio Aesthetic) — read object specs to render objects per movement
- **Voice Reference** — reads object specs to determine which objects the voice references in this movement
- **Prompt Construction** — uses object specs to maintain continuity across triplet outputs
- **Script Reference** — uses object specs for stage directions and sensory cues

**Sibling references:**
- Character Reference (parallel content layer)
- Motif Reference (parallel content layer)
- Math Visual / Math Audio (parallel content layers)

Objects, characters, motifs, and math primitives all describe content present in a movement. Surface layers integrate all four when rendering.

The object reference is open. New objects can be added by following the construction guide and appending to the canonical object list (or specifying realization-specific objects in individual realization specs).
