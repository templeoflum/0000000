# Character Reference

Characters are the agents that persist across movements. Where the spline tells us *what happens*, the Character Reference tells us *who it happens with* and *who carries it forward*.

A character has continuity. The figure who reaches in I is the same figure who is contained at IV and walks on at VII. The character is not just a body — it is a body with a posture, a voice when it speaks, an arc, identifying marks. Different mediums render the character differently, but the character is the same.

This reference specifies how characters are constructed, how they modulate across mediums, and how they connect to the spline's per-movement signals.

---

## The Character Function

```
Character: [name]

Inputs:
  From spline (per movement): which characters appear, in what role, with what state
  From Identity signal: universal context per movement

Per-character definition (composed from four sub-functions):
  Visual identity — how the character appears across renderings
  Voice identity — how the character sounds when they speak
  Arc — what the character carries through the work; what changes
  Continuity invariants — what every realization must preserve

Per-character response:
  Per-movement state (where they are, what they carry, how they act)
  Medium modulation (how the character is rendered in each modality)

Output:
  Specification consumable by surface layers, voice, narrative, script
```

### Construction guide

To add a character to *Spatium Dimensio*:

1. Name the character (a short descriptive phrase, not a personal name — *Spatium Dimensio*'s characters are archetypal)
2. Specify visual identity across all four sub-function axes (figure type, posture-set, identifying marks, costume/dress)
3. Specify voice identity (which register, stance, positioning the character uses when speaking; whether they speak at all)
4. Specify the arc (what the character carries from movement to movement; what transforms; what is preserved)
5. Declare continuity invariants (the spec-level commitments any realization must honor)
6. Specify per-movement state (which movements the character appears in, in what role)
7. Specify medium modulation (how the character renders visually, sonically, narratively, in script)

---

## Sub-Functions

### 1. Visual identity

How the character appears across visual renderings.

**Sub-axes:**

- **Figure type** — human, archetypal-human, abstracted-human, animal, elemental, compound. Most *Spatium Dimensio* characters are archetypal-human (classical figure, no specific identity), but other types are possible.
- **Posture-set** — characteristic body positions across movements. A character has a small set of recognizable postures (reaching, holding, kneeling, walking) and the realization renders those postures consistently across all the character's appearances.
- **Identifying marks** — what makes the character recognizable across renderings. For mythic characters: drapery color, gesture habits, presence of light. For modern characters: specific objects carried, specific gestures. The marks should be few but consistent.
- **Costume/dress** — what the character wears or doesn't wear. Across realizations, this is the most variable axis (Sacred Ritual gives classical drapery; Chrome-Glitch gives chrome surface). But within a realization, the character's costume should remain consistent across movements.

### 2. Voice identity

How the character sounds when they speak.

**Sub-axes:**

- **Register × stance × positioning** — the four-sub-function voice spec for this character (when they speak). Voice Reference's standard taxonomy applies.
- **Speech frequency** — how often the character speaks. Some characters narrate throughout. Some speak only in specific movements. Some never speak (they are present but silent — the witnesses of VI may not speak, only be witnessed by the celebrant's voice).
- **Voice continuity** — whether the character's voice register holds constant or shifts across movements. The celebrant's stance shifts (idealist → realist → idealist) across movements; the register holds (mythic).
- **Sonic signature** — when the character speaks, what sonic environment accompanies them. The celebrant in Sacred Ritual is accompanied by drone and breath; the rod-maker character would be accompanied by the pitched voice arriving.

### 3. Arc

What the character carries through the work; what changes; what is preserved.

**Sub-axes:**

- **What is carried** — what the character holds, knows, embodies that persists across movements. The figure carries the body's reach across all seven movements.
- **What transforms** — what changes about the character as the work moves. The figure's posture changes (reaching, working with the rod, contained, radiating, walking on), but the body is the same body.
- **What is learned** — if applicable. The figure begins with the reach as pre-understanding (I); ends with the reach as post-understanding (VII). The arc is a learning that returns to its starting place transformed.
- **What is preserved** — the deepest invariants. The figure's body persists across all movements; the figure's inner light persists from I through VII (small at IV, intensifying at V, settled at VI, soft at VII); the figure never speaks unless explicitly assigned voice (typically the figure is the body being witnessed, with the celebrant speaking).

### 4. Continuity invariants

Spec-level commitments any realization must honor.

**Per-character invariants** (declared in the character's spec):

- Identity continuity — same body, same character, across all movement appearances
- Spatial continuity — when the character appears in successive movements, their position must make sense (the figure ends IV at the center; the figure begins V at the center; the figure ends VII having walked out)
- Symbolic weight — the character's symbolic function must not invert between movements (the figure cannot become the rod's enemy in IV; the figure is contained, not opposed)
- Voice continuity (if they speak) — register holds; stance may shift if declared in arc; positioning typically holds

---

## Medium Modulation

How the same character renders across different output modalities.

### Visual modulation

The character has visual form. Each visual rendering instantiates the character in the medium × visual world spec for the realization and movement.

- **Painted realizations** (Sacred Ritual, Critique): the character rendered in the painted idiom of the realization
- **Drawn realizations** (Fairytale, Children's Book): the character rendered with the line and palette of the realization
- **3D-rendered realizations** (Chrome-Glitch): the character rendered as 3D form, with the chrome/specular logic of the realization
- **Schematic realizations** (Technical Essay, Lecture): the character may not appear visually at all, or appears as abstract figure (silhouette, schematic body)

Across all visual renderings, the character's posture-set and identifying marks must remain recognizable.

### Audio modulation

The character has sonic form when they speak (and sometimes when they don't — a character can have a sonic signature even in silence).

- **When they speak:** the voice spec from voice identity applies; rendered through the realization's audio aesthetic
- **When they are present in silence:** the character may have an accompanying sonic signature (a drone for the celebrant, a pitched voice for the rod-maker, a particular timbre for the witnesses)
- **When they are absent:** silence or the work's baseline drone

### Narrative modulation

The character appears in the narrative as described, named, or quoted.

- **Described:** "the figure walked into the field" — narrator's reference to the character's action
- **Named:** "the celebrant continued" — narrator names the character's role
- **Quoted:** "the celebrant said: 'the body opened'" — character's own voice rendered directly

The same character can be rendered in all three modes within a single movement, as appropriate.

### Script modulation

The character appears in the script as a voice cue and stage direction subject.

- **Voice cue:** named header (CELEBRANT, FIRST VOICE, CHILD), italic action, or margin cue depending on script preset
- **Stage direction subject:** "the figure bends down" — the character as the subject of staged action
- **Gesture cue:** "the figure extends the arm" — the character's posture-set called out as performance direction

---

## Canonical Characters of *Spatium Dimensio*

The work has six canonical characters, organized by their role across the spline.

### The Figure (the body)

**Visual identity:**
- Figure type: archetypal human
- Posture-set: reaching (I), laying-down-the-rod (II), watching-the-many-traditions (III, often silent), contained-at-center (IV), radiating-from-within (V), gathered-with-witnesses (VI), bending-down-to-set-down-the-rod and walking-on (VII)
- Identifying marks: inner light (painted-from-within), classical contour, body present in every movement
- Costume: realization-dependent (classical drapery in Sacred Ritual; chrome surface in Chrome-Glitch; everyday clothing in Children's Book)

**Voice identity:**
- The figure typically does not speak. The figure is the body being witnessed; the celebrant or narrator speaks of the figure.
- In some realizations (Children's Book, Personal Letter), the figure may have voice — typically child register or first-person caretaker register.
- Sonic signature when silent: the drone of the work; the body's breath audible under the celebrant's voice

**Arc:**
- Carries: the body, the reach, the inner light, the continuity of self
- Transforms: posture (extension → containment → radiating → walking on), relationship to the rod (none → user → contained-by → setting-down)
- Learns: the reach of I as pre-understanding becomes the reach of VII as post-understanding
- Preserved: the body is one body, the inner light persists, the figure walks on

**Continuity invariants:**
- Same body across all seven movements (visual recognition required)
- Inner light persists (small at IV; never extinguished)
- Figure never destroys the rod or the cathedral
- Figure walks on at VII (the work ends on the body, not the apparatus)

**Per-movement state:**
- I: alone in the field, reaching
- II: laying down the rod with reverence
- III: present among many traditions, observing
- IV: contained at the center, breathing, inner light small
- V: radiating, light passing through the cage walls
- VI: gathered with the witnesses in stillness
- VII: setting down the rod, walking on

### The Celebrant (the voice)

**Visual identity:**
- Figure type: archetypal human or simply the work's narrative voice (may not appear visually)
- The celebrant is often *not the same as* the figure — the celebrant is the voice; the figure is the body
- In some realizations, the celebrant is visible (the celebrant in Sacred Ritual may be one of the witnesses, or may be the figure itself depending on staging)
- Identifying marks: the voice itself

**Voice identity:**
- Register: realization-keyed (mythic in Sacred Ritual, scientist in Lecture, engineer-cynic in Critique, etc.)
- Speech frequency: throughout the work; the celebrant is the work's continuous narrator
- Voice continuity: register holds; stance shifts (idealist → realist → idealist across the arc)
- Sonic signature: the drone of the work, with the realization's audio aesthetic

**Arc:**
- Carries: the work's voice; the gathering function (calls the audience together)
- Transforms: stance shifts; pacing shifts (slow in I, declarative in IV, opening in V, quiet in VI, spacious in VII)
- Learns: the celebrant's idealism of I becomes post-understanding idealism of VII
- Preserved: the celebrant is the same voice across all movements; the same register holds throughout

**Continuity invariants:**
- Same voice (same register) across all movements
- The celebrant never breaks the realization's voice spec
- The celebrant gathers — never isolates, never excludes
- The closing words of VII echo the opening words of I (full circle)

### The Chorus (the gathered)

**Visual identity:**
- Figure type: archetypal multiple — five voices in III, the gathered witnesses in VI
- Each chorus member is distinct but the chorus functions as a collective
- Identifying marks: posture of recognition; classical drapery in Sacred Ritual; varies by realization

**Voice identity:**
- Register: realization-keyed; in Sacred Ritual, mythic × realist × congregational
- Speech frequency: appears at III (parallel naming), V (layered voices), VI (call-and-response)
- Voice continuity: the chorus expands and contracts across movements
- Sonic signature: distributed sources, ambient cathedral reverb in Sacred Ritual

**Arc:**
- Carries: the plurality of traditions; the gathered recognition; the witnessing
- Transforms: parallel naming (III) → layered registers (V) → quiet call-and-response (VI)
- Preserved: the chorus refuses hierarchy at every appearance

**Continuity invariants:**
- The chorus never ranks its members
- The chorus speaks only when configuration calls for it (III, V, VI)
- The five voices of III, the five layered voices of V, and the chorus of VI are conceptually the same gathering — different configurations of the same plurality

### The Rod-Maker

**Visual identity:**
- Figure type: archetypal human, often distinct from the figure
- The rod-maker may be implied (someone laid the rod) rather than shown
- In some realizations, the rod-maker is shown laying the rod against the body of the figure
- Identifying marks: holding the rod, the gesture of laying-down

**Voice identity:**
- Often silent — the celebrant narrates the rod-maker's action
- When voiced, register varies by realization (engineer in Critique, scientist in Lecture, mythic in Sacred Ritual)
- Sonic signature: the pitched voice that arrives with the rod at II

**Arc:**
- Carries: the gift of the apparatus; the act of measurement as offering
- Appears only at II (the rod-maker's act is the structural function of II)
- Preserved: the rod-maker's intention is reverent — the rod is gift, not conquest

**Continuity invariants:**
- The rod-maker is not the antagonist
- The rod-maker's gesture is offering
- The rod-maker may be the figure themselves (in some realizations the figure makes the rod) or a separate character

### The Witnesses

**Visual identity:**
- Figure type: archetypal multiple, sparse
- Distinct from the chorus — the witnesses are gathered in stillness, not speaking
- Each witness in their own posture: kneeling, sitting, looking
- Identifying marks: postures of recognition; sparse arrangement; each fully painted, fully present

**Voice identity:**
- The witnesses do not speak. They are witnessed by the celebrant's voice and by the chorus's call-and-response in VI.
- In some realizations, the witnesses may have voice (the recognitions of VI could be voiced by witnesses rather than chorus) — but the canonical configuration is silent.
- Sonic signature: presence in the drone; quiet breath; no foreground voice

**Arc:**
- Appear at VI in their postures of recognition
- Remain at VII (the witnesses are still in their stations as the figure walks on)
- Preserved: the witnesses are not new at VI — they have been there all along; VI is when the figure sees them

**Continuity invariants:**
- The witnesses are honored equally — no witness foregrounded
- The witnesses remain at VII; they do not leave with the figure
- The witnesses gathered each other; the witnesses gather those who come after

### The Five Voices (of V's layered configuration)

**Visual identity:**
- Visually, these voices may not have figures — they may be voices only
- In some realizations, they are rendered as figures within the polyptych panels of V (mythic-scientist as one figure, mythic-mathematician as another, etc.)
- Identifying marks: each voice is associated with one of V's non-Euclidean spaces (scientist with configuration space, mathematician with function space, artist with Hilbert space, child with fractal dimension)

**Voice identity:**
- Register: each voice is a mythic-inflected version of a standard register (mythic-scientist, mythic-mathematician, mythic-artist, mythic-child) — see Voice Reference
- Speech frequency: appears only at V
- Voice continuity: enters in succession, layers, then quiets at the transition to VI
- Sonic signature: each voice associated with a different sonic primitive (configuration space → many independent parameters; function space → manifold drone; Hilbert space → microtonal opening; fractal → recursive harmonic)

**Arc:**
- Carry: the recognition that the body has many openings; that the cage cannot contain the body's actual dimensionality
- Transform: from layered chorus (V) into quietude (VI's transition)
- Preserved: the voices are not new at V; they are the body's existing capacities being voiced

**Continuity invariants:**
- The voices are mythic-inflected — they do not break into modern technical register
- The voices honor the cage (they do not destroy it; they exceed it)
- The voices fall away one by one at V → VI transition (child first, then artist, then mathematician, then scientist, leaving celebrant alone)

---

## How Character Reference Connects to the Kit

The Character Reference reads the spline's character signal per movement and provides the specifications consumable by all downstream layers.

**Inputs from spline:**
- Per-movement signal declaring which characters appear, in what role, in what state
- Identity signal for universal per-movement context

**Outputs consumed by:**
- **Surface layers** (Medium, Visual World, Audio Aesthetic) — read character specs to render characters visually and sonically per movement
- **Voice Reference** — reads character specs to determine which characters have voice in this movement, and what their voice spec is
- **Prompt Construction** — uses character specs to maintain continuity across triplet outputs (image, audio, narrative)
- **Script Reference** — uses character specs for voice cues and stage directions

**Sibling references:**
- Object Reference (parallel content layer)
- Motif Reference (parallel content layer)
- Math Visual / Math Audio (parallel content layers)

Characters, objects, motifs, and math primitives all describe content present in a movement. Surface layers integrate all four when rendering.

The character reference is open. New characters can be added by following the construction guide and appending to the canonical character list (or specifying realization-specific characters in individual realization specs).
