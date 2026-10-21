# Motif Reference

Motifs are recurring patterns that persist across movements. Where objects are particular things and characters are particular agents, motifs are patterns — shapes that re-emerge across the work in any medium that can express them.

A motif is not an instance. It is the *shape* of what recurs. "The reach" is a motif: the body's extension into what is not the body. It appears as a painted gesture in I, as the laying-down of the rod in II (the same reaching extended into measurement), as the chorus's reaching-across-traditions in III, as the figure's contained breath in IV (the reach interrupted), as light passing through the cage walls in V (the reach exceeded), as the witnesses' postures of recognition in VI (the reach gathered), as the body walking on at VII (the reach recovered). Different instantiations; same pattern.

A motif is medium-agnostic at the level of pattern. Its instantiations are medium-specific.

This reference specifies how motifs are constructed, how they instantiate across mediums, and how they connect to the spline's per-movement signals.

---

## The Motif Function

```
Motif: [name]

Inputs:
  From spline (per movement): which motifs are invoked, at what intensity, in what context
  From Identity signal: universal context per movement

Per-motif definition (composed from four sub-functions):
  Pattern shape — the medium-agnostic description of the recurring pattern
  Symbolic weight — what the pattern carries within the work
  Recurrence behavior — how the motif returns and varies across movements
  Continuity invariants — what every realization must preserve about the motif

Per-motif response:
  Per-movement invocation (where it appears, in what intensity, in what context)
  Medium instantiation (how the pattern manifests in each modality)

Output:
  Specification consumable by surface layers, voice, narrative, script
```

### Construction guide

To add a motif to *Spatium Dimensio*:

1. Name the motif (a short phrase capturing the pattern — "the reach," "the field gathers")
2. Specify pattern shape (the medium-agnostic description; what the pattern *is* before being instantiated)
3. Specify symbolic weight (what the motif means within the work)
4. Specify recurrence behavior (where the motif appears, how it varies, what stays the same)
5. Declare continuity invariants (the spec-level commitments any realization must preserve)
6. Specify per-movement invocation (which movements invoke the motif, at what intensity)
7. Specify medium instantiation (how the pattern appears visually, sonically, in narrative, in script, in gesture)

---

## Sub-Functions

### 1. Pattern shape

The medium-agnostic description of the recurring pattern.

**Sub-axes:**

- **Pattern type** — what kind of pattern this is. Patterns can be:
  - *Gestural* (a movement pattern: the reach, the laying-down, the bending-down)
  - *Verbal* (a phrase pattern: "the field gathers us," "nothing was counted")
  - *Compositional* (a spatial arrangement pattern: figure-at-center, three-rods-at-a-corner, polyptych-around-center)
  - *Sonic* (a sound pattern: drone-and-figure, call-and-response, ascending interval)
  - *Conceptual* (a structural pattern of meaning: "it was true at its scale," settlement-among-settlements)
- **Shape description** — what the pattern looks/sounds/reads like in its abstract form
- **Anchor elements** — the parts of the pattern that must be present for it to register as the motif
- **Variation tolerance** — how much the pattern can vary while remaining recognizable

### 2. Symbolic weight

What the pattern carries within the work.

**Sub-axes:**

- **Carried meaning** — what the motif embodies. "The reach" carries: the body's primitive act of extension; the desire to know what is beyond the body; the gesture that precedes measurement.
- **Symbolic relationships** — how the motif relates to other content. "The reach" relates to the rod (which extends the reach, replaces it, is set down to recover it); to the figure (who reaches); to the horizon (which is reached toward).
- **Function across the spline** — what work the motif does for the work's coherence. Some motifs carry continuity across movements; some mark transitions; some establish thematic returns.
- **Symbolic invariants** — what the motif cannot become without breaking the work. "The reach" cannot become grasping; "the field gathers us" cannot become "the field demands us."

### 3. Recurrence behavior

How the motif returns and varies across movements.

**Sub-axes:**

- **Movements of invocation** — list of movements where the motif appears
- **Variation per movement** — how the motif modulates with the movement's felt weight. The reach varies: open (I), instrumental (II), parallel (III), interrupted (IV), exceeded (V), recognized (VI), recovered (VII). Same pattern, different inflection.
- **Intensity per movement** — how foregrounded or backgrounded the motif is per movement. The reach is foregrounded at I and VII; backgrounded at IV (it survives even where it is interrupted).
- **Phase relationships** — how the motif relates to other motifs across the work. "The reach" is in counterpoint with "the field gathers" — both are present together; the reach is the body's gesture, the field's gathering is what meets the gesture.

### 4. Continuity invariants

Spec-level commitments any realization must preserve.

**Per-motif invariants** (declared in the motif's spec):

- Pattern recognition — the motif must be recognizable across all its invocations within a realization (the realization's instantiations of the motif must share recognizable shape)
- Symbolic invariants — the meanings the motif cannot lose or invert
- Recurrence integrity — the motif must appear in the spline-declared movements; it cannot be skipped
- Variation legitimacy — only variations consistent with the motif's nature; the reach can become exceeded but cannot become abandoned

---

## Medium Instantiation

How the same pattern manifests across different output modalities.

A motif is medium-agnostic at the level of pattern. Each medium has its own way of instantiating the pattern. Some motifs instantiate primarily in one medium (a verbal motif like "the field gathers us" is primarily verbal but can also be sonic in its phrase shape or gestural in its evocation). Most motifs instantiate across multiple mediums.

### Visual instantiation

How the pattern appears in image.

- *Gestural motifs:* rendered as body posture, depicted action, frozen mid-movement (the reach as an outstretched arm; the laying-down as a figure bending; the bending-down at VII as the figure crouching to place the rod)
- *Compositional motifs:* rendered as spatial arrangement (figure-at-center as a literal central figure; three-rods-at-a-corner as the visible basis; polyptych-around-center as the literal panel structure)
- *Verbal motifs:* may not instantiate visually, or may instantiate as inscription (the formula on the vault is a verbal motif rendered as visual text)
- *Conceptual motifs:* rendered through composition, palette, or compositional weight that signals the conceptual content

### Sonic instantiation

How the pattern manifests in sound.

- *Gestural motifs:* rendered as sonic gesture — the reach as an ascending interval or swell; the laying-down as a settling phrase; the bending-down as a descending phrase that resolves
- *Verbal motifs:* rendered as spoken word with characteristic phrasing; or as melodic phrase if the motif is sung
- *Sonic motifs:* the motif IS sound — drone-and-figure as a texture; call-and-response as a structural pattern; ascending interval as a melodic shape
- *Compositional motifs:* rendered as sonic spatial arrangement — center-as-source for figure-at-center; distributed-sources for polyptych-around-center

### Narrative instantiation

How the pattern appears in voice content.

- *Verbal motifs:* directly rendered as the phrase ("the field gathers us")
- *Gestural motifs:* rendered as verb or described action ("the body opened," "someone bent down")
- *Compositional motifs:* rendered as scene description ("the figure stood at the exact center")
- *Conceptual motifs:* rendered as the voice's structural claim ("it was true at its scale" — a phrase the voice uses to invoke the conceptual motif)

### Script instantiation

How the pattern appears in performance staging.

- *Gestural motifs:* rendered as stage direction calling the gesture ("the figure bends down"; "the celebrant extends an arm")
- *Compositional motifs:* rendered as spatial staging direction ("witnesses arranged sparse around central figure")
- *Verbal motifs:* rendered as the spoken phrase, called by the voice cue
- *Conceptual motifs:* rendered through pacing, tone, and dynamic specification

---

## Canonical Motifs of *Spatium Dimensio*

The work has nine canonical motifs across five pattern types. Some motifs invoke in every movement; others appear in specific configurations.

### Gestural motifs

#### The Reach

**Pattern shape:**
- Type: gestural
- Shape description: the body's extension into what is not the body; an outward-and-toward movement; the gesture before grasping
- Anchor elements: the body; an extension (arm, eye, foot); a direction (toward something not the body)
- Variation tolerance: the extension can be any direction; the body can be in any posture as long as the gesture-toward is recognizable

**Symbolic weight:**
- Carried meaning: the primitive act of meeting the world; the body's first verb; the gesture that precedes measurement
- Symbolic relationships: with the figure (who reaches); with the horizon (which is reached toward); with the rod (which extends, replaces, is set down to recover the reach); with the field (which meets the reach)
- Function across spline: the motif that opens and closes the work — the reach of I is the reach of VII, transformed
- Symbolic invariants: the reach is never grasping; the reach does not arrive (the reach is always reach-toward); the reach is recoverable

**Recurrence behavior:**
- Movements of invocation: I (foregrounded), II (the rod extends the reach), III (the chorus reaches across traditions), IV (the reach interrupted but survives in the figure's breath), V (the light reaches past the cage walls), VI (the gathered have reached and are still reaching), VII (the reach recovered, the body walks)
- Variation per movement: open (I) → instrumental (II) → plural (III) → interrupted (IV) → exceeded (V) → recognized (VI) → recovered (VII)
- Intensity: foregrounded at I, II, VII; backgrounded but present at III, IV, V, VI

**Continuity invariants:**
- The reach is present in every movement (even at IV where it is interrupted)
- The reach is always reach-toward, never reach-and-grasp
- The reach is recoverable (VII commits to this)
- The opening reach (I) and the closing reach (VII) are the same gesture, transformed

#### The Laying-Down

**Pattern shape:**
- Type: gestural
- Shape description: the body bending or extending to place something on the ground or against another thing; a movement of placement, not abandonment
- Anchor elements: a body; an object; a placing action; a ground or receiving surface
- Variation tolerance: any object; any surface; the bending can be subtle or full

**Symbolic weight:**
- Carried meaning: reverent placement; the act of measurement as offering; the act of release at the close
- Symbolic relationships: with the rod (which is laid down at II to mark, and laid down at VII to release); with the figure (who does the laying); with the field (which receives)
- Function across spline: appears at II as the first measurement, returns at VII as the final release — the same gesture, transformed in meaning
- Symbolic invariants: the laying-down is reverent; the laying-down is not abandonment

**Recurrence behavior:**
- Movements of invocation: II (the rod laid against the body, the rod laid down to form the basis), VI (the witnesses' postures include kneeling — a form of laying-down), VII (the rod set down at the threshold)
- Variation per movement: instrumental (II) → reverent gathered (VI) → released (VII)
- Intensity: foregrounded at II and VII; backgrounded at VI

**Continuity invariants:**
- The laying-down is reverent in every appearance
- The object laid down is never destroyed in the act
- The laying-down at VII echoes the laying-down at II — same gesture, full circle

#### The Bending-Down

**Pattern shape:**
- Type: gestural
- Shape description: the body lowering to ground level — to place, to gather, to attend
- Anchor elements: a body in vertical posture lowering; a downward motion; an attention to ground level
- Variation tolerance: full bend, kneel, crouch; the bending can be brief or sustained

**Symbolic weight:**
- Carried meaning: humility before what is being attended; the body acknowledging what is small and present; the necessary precursor to laying-down
- Symbolic relationships: with the laying-down (the bending precedes); with the witnesses (who are in postures including bending)
- Function across spline: marks the moments of reverence — at II when the rod is first placed, at VI in the witnesses' postures, at VII when the rod is set down

**Recurrence behavior:**
- Movements of invocation: II (someone bends to lay the rod against the body), VI (the witnesses in postures including bending), VII (the figure bends to set down the rod)
- Variation per movement: working (II) → recognizing (VI) → releasing (VII)

**Continuity invariants:**
- The bending-down is voluntary, not collapse
- The bending-down attends to something — never aimless

### Verbal motifs

#### "The Field Gathers Us"

**Pattern shape:**
- Type: verbal
- Shape description: a phrase asserting the field's active gathering of the body; the field as agent of gathering
- Anchor elements: "the field"; "gather"; a sense of receiving rather than imposing
- Variation tolerance: tense can shift (gathers / gathered / will gather); the addressee can shift (us / them / what comes after); the phrase can be elaborated or compressed

**Symbolic weight:**
- Carried meaning: the field is not passive; the field receives and holds; the body is not alone but met
- Symbolic relationships: with the field (which gathers); with the reach (which is met by the field's gathering)
- Function across spline: the work's structural commitment that the body is held; appears in I's opening, V's expansion, VI's gathering, VII's close
- Symbolic invariants: the phrase always frames the field as gentle, holding, receiving — never demanding or seizing

**Recurrence behavior:**
- Movements of invocation: I ("the field gathers us; before we know it gathers us, it gathers us"), V ("the field gathers us; the field has always gathered us; even inside the cage, the field was gathering us"), VI ("the field gathered them; the field gathers us; the field will gather what comes after"), VII ("the field gathered us; the field gathers us; the field will gather what comes after us")
- Variation per movement: present-becoming (I) → continuous-recognition (V) → across-time-witnessing (VI) → full-arc-statement (VII)

**Continuity invariants:**
- The phrase opens and closes the work — it is the structural through-line in voice
- The phrase always implies passive grace from the field, never coercion
- The closing invocation at VII completes the full arc: gathered (past), gathers (present), will gather (future)

#### "Nothing Was Counted"

**Pattern shape:**
- Type: verbal
- Shape description: a phrase naming the pre-measurement condition; the absence of counting as positive condition
- Anchor elements: "nothing"; "counted" or "measured" or equivalent
- Variation tolerance: tense can vary; the phrase can be compressed or extended

**Symbolic weight:**
- Carried meaning: the field's primary condition is not the absence of measurement but the prior reality that precedes measurement; the body's pre-measurement life is real life
- Symbolic relationships: with the rod (the rod introduces counting); with the reach (which precedes counting); with the field (which doesn't require counting)
- Function across spline: opens the work at I; returns at VII as the recovered condition

**Recurrence behavior:**
- Movements of invocation: I ("nothing was counted"), VII ("nothing is counted")
- Variation per movement: past (I, before the rod) → present (VII, after the rod is set down)

**Continuity invariants:**
- The phrase is not nostalgic — the pre-measurement is not innocent; it is full
- The phrase frames absence-of-counting as positive, not lacking

#### "It Was True at Its Scale"

**Pattern shape:**
- Type: verbal / conceptual hybrid
- Shape description: a phrase asserting that a settlement, formula, or framing is correct within its operational scope, without making universal claims
- Anchor elements: "true"; "at its scale" or equivalent (within its scope, in its way, for what it does)
- Variation tolerance: the structure is fixed; the subject varies (the rod was true at its scale; the cathedral was true at its scale; each settlement was true at its scale)

**Symbolic weight:**
- Carried meaning: operational truth; the refusal of single-frame absolutism; the affirmation that settlements work within their domains
- Symbolic relationships: with the rod, the cathedral, the polyptych panels — all are affirmed as true at their scale
- Function across spline: the realization's commitment that the cage is preserved; the chorus's commitment that no settlement is ranked
- Symbolic invariants: the phrase is affirmative, not dismissive; "true at its scale" honors the truth while limiting the claim

**Recurrence behavior:**
- Movements of invocation: III (each of the five settlements: "It was true at its scale"), IV (the cathedral named as true at its scale), V (the cathedral was not wrong, the cathedral was only one settlement), VI ("the cathedral was not wrong about the shape, the cathedral was only wrong about being the only naming")
- Variation per movement: pluralistic (III) → preserving (IV) → relativizing (V) → reconciling (VI)

**Continuity invariants:**
- The phrase always affirms before limiting
- The phrase preserves the truth of what is named; only the scope is limited

#### "We Knew This Before We Had Words for It"

**Pattern shape:**
- Type: verbal / conceptual hybrid
- Shape description: a phrase asserting that recognition precedes vocabulary; that the body's knowing is older than language
- Anchor elements: "we knew"; "before we had words" or equivalent (older than naming, before language, in the bones)
- Variation tolerance: addressee can shift; the phrase can be expanded or compressed

**Symbolic weight:**
- Carried meaning: bodily knowledge precedes conceptual knowledge; recognition is older than vocabulary; what the work names was always there to be named
- Symbolic relationships: with the witnesses (whose recognitions are old); with the body (which knew before the rod arrived)
- Function across spline: the realization's commitment to anti-progressivism — the recognitions of V and VI are not new discoveries

**Recurrence behavior:**
- Movements of invocation: V ("we knew this before we had words for it; we knew this in our bones, in our breath, in our weight against the ground"), VI ("the recognitions were not new; the seeing that was named was old")
- Variation per movement: from-the-bones (V) → across-the-ages (VI)

**Continuity invariants:**
- The phrase honors the body's primary knowledge
- The phrase locates wisdom in lineage, not in this moment's discovery

### Compositional motifs

#### Figure-at-Center

**Pattern shape:**
- Type: compositional
- Shape description: the body positioned at the central point of the spatial field
- Anchor elements: a body; a central position; spatial composition arranged around the body
- Variation tolerance: the scale of "center" can vary (center of the painting, center of the cathedral, center of the gathered space); the figure's posture varies

**Symbolic weight:**
- Carried meaning: the body as reference point; the body as what is gathered around; the body as the work's subject
- Symbolic relationships: with the figure (who is centered); with the cathedral (whose architecture centers the figure); with the polyptych (whose panels surround the figure)
- Function across spline: visual structural through-line — the figure is at center in every movement
- Symbolic invariants: the figure is always at center; the centering is not domination but reference

**Recurrence behavior:**
- Movements of invocation: I (the figure alone in the field), II (the figure with the rod), III (the figure across the polyptych panels), IV (the figure contained at the exact center), V (the figure radiating from center), VI (the figure with witnesses gathered around), VII (the figure walking from center toward horizon)
- Variation per movement: alone (I) → working (II) → distributed (III) → contained (IV) → radiating (V) → gathered-with (VI) → departing (VII)

**Continuity invariants:**
- The figure is at center in every movement (compositionally if not literally)
- The figure is the work's spatial reference

#### Three-at-a-Corner

**Pattern shape:**
- Type: compositional
- Shape description: three elements meeting at a single point, extending in three independent directions
- Anchor elements: three elements; a meeting point; three directions
- Variation tolerance: the elements can be rods, columns, sun rays, gold threads; the directions can vary as long as they are three and independent

**Symbolic weight:**
- Carried meaning: the basis; the structure of three-dimensional naming; the architectural seed of the cathedral
- Symbolic relationships: with the rod (which makes the corner); with the cathedral (whose columns are the corner scaled up); with the math primitive "basis" (which is what the corner instantiates)
- Function across spline: appears in II as the rod's basis; returns in IV as the cathedral's architecture; appears in VII as the rod set down (echoing the basis even in release)
- Symbolic invariants: there are always three (not two, not four); the meeting is at a corner (not a center of mass); the elements extend in independent directions

**Recurrence behavior:**
- Movements of invocation: II (the three rods at a corner — the basis), IV (the three columns rising to the vault — the basis as architecture), VII (the three rods placed together at the threshold)
- Variation per movement: rods (II) → columns (IV) → rods again (VII)

**Continuity invariants:**
- The three is preserved (not two, not four)
- The corner is preserved (not a different arrangement)

#### Polyptych-Around-Center

**Pattern shape:**
- Type: compositional
- Shape description: multiple panels or panels-equivalent arranged around a central position
- Anchor elements: multiple panels; a central position; arrangement that honors all panels equally
- Variation tolerance: number of panels (five at III, many at V); arrangement (linear at III, three-dimensional at V)

**Symbolic weight:**
- Carried meaning: plurality without hierarchy; multiple settlements; the visual form of "many names"
- Symbolic relationships: with the chorus (which voices what the polyptych shows); with the cage (which is one panel among many at V)
- Function across spline: appears at III as the visual form of the chorus of settlements; returns at V as the form of the field exceeding the cage; backgrounded at VI and VII

**Recurrence behavior:**
- Movements of invocation: III (five panels in sequence), V (many panels surrounding the central cathedral, hinged out), VI (visible as the witnesses' surroundings), VII (visible in the background as the figure walks out)
- Variation per movement: sequential (III) → expanded (V) → settled (VI) → memory (VII)

**Continuity invariants:**
- Panels are equal in scale and reverence
- No panel is foregrounded over others
- The polyptych is the same polyptych across all four appearances

### Sonic motifs

#### Drone-and-Figure

**Pattern shape:**
- Type: sonic
- Shape description: a sustained sound (drone) under a moving or sustained foreground voice (figure)
- Anchor elements: a sustained ground; a foreground voice against it; the two coexisting
- Variation tolerance: the drone can vary in pitch and texture; the figure can be voice, instrument, or spatial event

**Symbolic weight:**
- Carried meaning: the field (drone) holding the body's expression (figure); the through-line beneath the foreground; the continuity beneath any specific event
- Symbolic relationships: with the drone object (which is the sonic ground); with the reach motif (the figure-against-drone is the sonic form of the body's reaching against the field's gathering)
- Function across spline: structural — the drone holds beneath every movement; specific figures emerge against the drone per movement

**Recurrence behavior:**
- Movements of invocation: I (drone alone, figure-as-silence), II (drone with the rod's pitched voice as figure), III (drone with polytonal figures), V (drone with layered figures), VI (drone with quiet call-and-response figure), VII (drone with quieter figures, returning toward drone-alone)
- Variation per movement: subdued at I and VII; layered at III and V; balanced at II and VI

**Continuity invariants:**
- The drone is continuous (does not stop)
- The figure varies but is always against the drone, not replacing it

#### Call-and-Response

**Pattern shape:**
- Type: sonic / verbal hybrid
- Shape description: one voice calls; another voice or voices respond; the response is shorter, briefer, completing
- Anchor elements: a calling voice; a responding voice (or voices); the alternation
- Variation tolerance: the calling and responding can be solo-to-chorus, voice-to-voice, or solo-to-multiple-soloists

**Symbolic weight:**
- Carried meaning: the gathered acknowledgement; the structural rendering that recognition is shared, not soloed; the antiphonal pattern of liturgy
- Symbolic relationships: with the chorus character; with the witnesses (who are present even when silent — the call-and-response happens in their spatial field)
- Function across spline: foregrounded at VI (the recognitions); echoed faintly at III (where the chorus speaks in turn, a variant of call-and-response without the explicit response)

**Recurrence behavior:**
- Movements of invocation: VI (the three recognitions as call-and-response), VII (a faint final call-and-response at close — celebrant invokes, the work ends without explicit response, the silence is the response)
- Variation per movement: structured (VI) → released-into-silence (VII)

**Continuity invariants:**
- The response is briefer than the call (settling, not elaborating)
- The call and response together complete the structural unit; neither alone is the motif

---

## How Motif Reference Connects to the Kit

The Motif Reference reads the spline's motif signal per movement and provides specifications consumable by all downstream layers.

**Inputs from spline:**
- Per-movement signal declaring which motifs are invoked, at what intensity, in what context
- Identity signal for universal per-movement context

**Outputs consumed by:**
- **Surface layers** (Medium, Visual World, Audio Aesthetic) — read motif specs to instantiate motifs visually and sonically per movement
- **Voice Reference** — reads motif specs to determine which verbal motifs the voice invokes
- **Prompt Construction** — uses motif specs to thread continuity across triplet outputs and across movements
- **Script Reference** — uses motif specs for staging consistency (recurring gestures, recurring phrases, recurring compositions)

**Sibling references:**
- Character Reference (parallel content layer)
- Object Reference (parallel content layer)
- Math Visual / Math Audio (parallel content layers)

Motifs are the work's recurrence engine. While characters carry agentic continuity and objects carry material continuity, motifs carry pattern continuity. The work's coherence across seven movements depends on motifs at least as much as on characters and objects — the reach connects I to VII; "the field gathers us" connects all four movements where the voice gathers; "it was true at its scale" connects III's chorus to IV's cathedral to V's relativization to VI's reconciliation.

The motif reference is open. New motifs can be added by following the construction guide and appending to the canonical motif list (or specifying realization-specific motifs in individual realization specs).
