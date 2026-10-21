# UX / UI Restructure Plan — organizing the instrument around what the parts ARE

> 2026-05-31. The instrument grew capability fast; the layout lagged the *meaning*. This pass reorganizes
> controls so the structure reflects the conceptual split we arrived at: **OBSERVATION** (watching what the
> form does) vs **MEASUREMENT** (deliberately measuring against a reference frame). Plus ergonomic cleanup:
> consistent arrow-steppers on every dropdown, scrub-matched styling, controls grouped by the act they serve.
> Write the plan, agree it, THEN edit — measure twice, cut once.

## THE ORGANIZING PRINCIPLE
Two distinct acts, each with its own tools + readouts (the uncertainty-principle framing the user named:
you either observe or you measure, not both):
- **OBSERVATION** — what the form *is/does*, live: the dynamics, shape, breathing. Tools = how you look
  (camera, beam/optics, expression knobs). Readout = the observational panel (PCA/FA/breathing/point pos).
- **MEASUREMENT** — deliberate reading against a reference frame, done when frozen. Tools = the grid (the
  reference frame) + the caliper (the measuring jaws). Readout = measurement values, LIVING WITH the tools.

## SECOND ORGANIZING TACTIC: PROGRESSIVE DISCLOSURE (minimize the default surface)
Everything is always-visible now → overwhelming. Each zone shows only its COMMON controls by default;
advanced controls live in `<details>` folds. The instrument should look SIMPLE until you need depth.
This is the primary real-estate win.

## CURRENT ZONES (before)
1. NAV (above canvas): orbit, X/Y/Z, reset · freeze, step, level
2. expression: HOLES (k), RATES (ratio + per-level overrides)
3. beam & optics: speed/timebase/cpf/strobe/render%/afterglow/zoom/dot · normalize/auto-fit/beam-off/save
4. overlays: master + 14 feature toggles · CALIPER (enable + target dropdown)  ← caliper is mis-homed here
5. grid & measurement: PLANE · GRIDS · PROJECTION · OSCILLATE · POINTS · DERIVED · BEAM 2 · TIMING
6. (below) bar, desc, measurement-readout (collapsible), log controls

Problems: caliper (the measuring tool) sits in "overlays" as if it's décor; its readout is mixed into the
general panel; nav mixes camera controls (observation) with freeze/step (measurement gate) and level
(an expression knob); "grid & measurement" is overloaded with non-measurement stuff (oscillate, beam2).

## THE SPINE (the pipeline — each stage consumes the previous)
**EXPRESSION (the math) → BEAMS (what the math affects) → PROJECTION (how you see it) →
GRIDS (how you map it) → MEASUREMENT (how you measure that map).**
Grids holds ALL the reference geometry (coordinate grids AND the overlays: VE, ellipsoid, bbox, axes,
skeleton, COM…) — because those are the things measurement maps and reads against. The old "overlays"
zone dissolves into GRIDS as "reference features." Camera folds into PROJECTION (it's how-you-see).

## COMPLETE CONTROL → GROUP MAPPING (agree every item before moving)

### 1. EXPRESSION — the math (the construction itself)
- VISIBLE: `__level` (level), `__kHole` (k), `rateRatio` select (+arrows)
- FOLD "rate detail ▸": per-level rate overrides (`__ro*`), `selfChk` (self-scaling)
- `__growcycles` (grow-in duration) → fold here too (it's an expression-transition param)

### 2. BEAMS — what the math affects (render/sampling of beam 1 & 2, as INDEPENDENT peers)
- VISIBLE: **beam 1 ☑** (`beam1Chk`) · **beam 2 ☐** (`beam2Chk`) — independent toggles, true peers
  (replaces the awkward `beamOffChk`; either beam on/off separately). `mult` (speed), `zoom`, `fade`.
- FOLD "beam detail ▸": `timebase`, `cpf`, `strobe`, `renderscale`, `dot`, `saveImgBtn`
- FOLD "beam 2 ▸" (when on): `__b2kHole`, `__b2RateDrive`, `__b2rad`, `__b2disp`, `b2SelfChk`, `p2lag`,
  `p1lag`, `__p2invR`, p2 rel/mode selects  (consolidates old BEAM 2 + POINTS + TIMING)
- FOLD "oscillate ▸": `oscChk`, `__oscBlend`, `__oscAmp`  (a sampling transform)
- DROP as controls: `normChk` (normalize — always-on, the unit/measurement frame needs it; keep true
  internally), `fitChk` (auto-fit — always-on default; keep true internally).

### 3. PROJECTION — how you see it (the viewing apparatus: projection mode + camera)
- VISIBLE: `gridProjSel` (perspective/ortho/stereo/iso, +arrows), `viewX`/`viewY`/`viewZ`, `orbitBtn`, `reset`
- FOLD "view detail ▸": `__orbitspd` (orbit speed)
- (zoom lives in BEAMS as the everyday control; projection-mode is the "how 3D→2D" essence)

### 4. GRIDS — how you map it (ALL reference geometry: coordinate grids + overlay features)
- VISIBLE: `gridPlaneSel` (plane, +arrows), the 5 grid toggles (`gCartChk` `gPolarChk` `gLogPolarChk`
  `gHexChk` `gSphChk`), `__gridDiv` (divisions), master `overlaysMasterChk`
- VISIBLE (common reference features): `skelChk`, `ellipChk`, `veChk`, `axesChk`
- FOLD "more references ▸": `comChk`, `frameChk`, `netAxisChk`, `anglesChk`, `rringChk`, `meetChk`,
  `scaleChk`, `skel2Chk`, `pcaChk`, `bboxChk`, `gPCAGridChk`
- NOTE: COM (`comChk`) likely REDUNDANT as a measurement target — comRel≈0.0127 (COM sits ~1.3% off
  origin), so dot→COM ≈ dot→origin. Kept for now; the instrument can confirm by measuring both. If
  comRel stays negligible across configs, COM-as-target can be dropped (origin suffices).

### 5. MEASUREMENT — how you measure that map (the measuring act + readout)
- VISIBLE: **freeze / step** (`freezeBtn` `stepBtn` — the gate; freezing = entering measurement)
- VISIBLE: **CALIPER** `calChk` enable · target-type {3D | grid} · `calTarget` (+arrows, adapts to grid coords)
- FOLD "caliper detail ▸": `__calRes` (caliper resolution)
- **MEASUREMENT READOUT** (moves here from the general panel): caliper distance/angle + per-grid
  coordinate readings (cells/polar/log-polar/hex/spherical/grid-loc) + VE-angle.

### General panel (below canvas) — OBSERVATION readouts ONLY
- level/cycle, total radius (=1), hole radius, FA/Westin shape, PCA radii, point position, COM, meet/locus.
- Stays collapsible (freeze-to-read). The MEASUREMENT readouts have moved to group 5.

### Log controls (`logBtn`/`copyLogBtn`/`clearLogBtn`) — stay at the bottom (data export, cross-cutting)

### General panel (below canvas) — OBSERVATION readouts only
- level/cycle, total radius, hole radius, FA/Westin shape, PCA radii, point position, COM, meet/locus.
- (The measurement readouts — grid coords, caliper, VE-angle — MOVED to the measurement zone.)

## ERGONOMIC / STYLE CLEANUP (applies everywhere)
- **Arrow-steppers on EVERY dropdown** (design principle): PLANE, PROJECTION, caliper target, rate-ratio
  (already has them), p2 mode, etc. ◂ ▸ to step options without opening. Reuse the rate-ratio stepper code.
- **Stepper style matches the scrub** (not the current bespoke .selar look): the ◂ ▸ should visually read
  like the scrub's ◀ ▶ arrows — same color, size, hover. Unify .selar with the scrub arrow styling.
- Consistent rlabel grouping; tight gutters; the measurement readout area visually distinct (it's results).

## CALIPER UNIFICATION (the functional piece, post-move)
One caliper tool, target is EITHER:
- **3D feature** (origin/COM/ellipsoid vertices/VE vertices) → true 3D distance  [rung 1, DONE]
- **grid location** on the face, specified in the ACTIVE grid's coordinates → in-plane face distance:
  cartesian (cell u,v) / polar (r,θ) / log-polar (ring,θ) / hex (i,j); spherical handled as 3D.
  [rung 2 — target entry adapts to grid type; VERIFIED the coord→face-position math]
Readout: distance (3D or face) in unit / cells / caliper-address + angle, in the MEASUREMENT zone.

## BUILD ORDER (rungs, each verified + parse-checked)
1. Move LEVEL nav→expression; move freeze/step nav→measurement zone. (pure relocation)
2. Move CALIPER control overlays→measurement zone; move measurement readouts panel→measurement zone.
3. Unify dropdown steppers (PLANE/PROJECTION/target/etc.) + restyle .selar to match scrub arrows.
4. Caliper rung 2: grid-location targets with grid-coord-adaptive entry.
5. Relocate the non-measurement sub-rows (oscillate/points/beam2/timing/derived) to sensible homes.
6. Final pass: tighten, verify nothing orphaned, drive-test.

## CONSTRAINTS (unchanged disciplines)
- Construction/geometry UNTOUCHED (this is pure UI/UX). Parse-check after every edit. Lock a REFERENCE
  before starting the restructure (it touches a lot of HTML). Verify no orphaned handlers after moves.

---

## DESIGN VOCABULARY & METHOD (observed lens, not a claim)

> Framing note: this is a useful LENS on how the instrument and its development are structured — "the idea,
> not the claim." Where it rhymes with the construction's self-similarity, that's noted as resemblance, not
> asserted as the same principle. Recorded because the vocabulary has proven useful for design decisions.

### The thesis
Make deep, complex parameter control + modulation easily navigable and viewable — by treating the control
surface as a **2D navigable space** with **coarse-and-fine on BOTH axes**, rather than a flat wall of widgets.
Nothing is shown until you navigate to it; both dimensions collapse to as coarse or as fine as needed.

### The three interaction primitives
- **HOLD** — a DEPTH control (vertical axis). Hold-drag the section bar to set how deep you reveal (tier 1/2/3).
  Coarse-vertical = which tier. Folds away what you're not using. (The lodzone bar.)
- **SCRUB** — a VALUE control (horizontal axis). Drag to vary a continuous parameter. Already coarse-and-fine
  horizontally: fine = the drag (log-scaled where needed); coarse = the ◀▶ arrows (jump ×10, modifiers ×100/
  ×1000/…). (The existing scrubs.)
- **SELECT** — a discrete KIND choice (orthogonal to both axes). Picks WHICH parameter-space you're in
  (plane, projection, rate-ratio, caliper target). Not a position on the depth×value plane — it chooses the
  plane. This is why it sits apart from hold/scrub; it's a mode/kind selector. (The dropdowns + steppers.)

### The development method (vertical-then-horizontal)
Observed pattern, mechanically visible in the file lineage and commit order:
- Establish ONE working path to full depth (vertical), then vary alongside it without disturbing it (horizontal).
- Instances: lock `_REFERENCE` → fork branch → override on branch while original stays intact; build one
  verified rung deep before varying sideways (caliper rung 1 → rung 2); per-level rate overrides = a default
  uniform path with the OPTION to override any single level, never forced.
- The shape: a default branch always available, but at each branch you can branch off differently — start with
  the first path, override others by choice. Override is always an option, never forced — that's how the
  self-similar shape is *maintained by choice* rather than imposed.

### The resemblance (noted, not claimed)
This "same rule available at every level, applied by choice" has a structural resemblance to the
construction's self-similarity (constant proportion (k−1)/(k+1) at every cycle). Whether it's the SAME
principle or an appealing rhyme between a branching process and a scaling object is NOT established — treat
as a generative metaphor for how to work, not a proven property.

---

## FINAL GESTURE MODEL + STATE SYSTEM (UX locked, 2026-05-31)

### Hold gesture model (refined to clean 3-gesture separation)
- **click** = toggle fully collapse ↔ fully open (0 ↔ max).
- **modifier+click** (Ctrl/Shift/Alt) = jump to a specific depth (tier 1/2/3, clamped).
- **drag down** = progressive depth.
The scrub/hold MODIFIER SYMMETRY is the key consistency: on both primitives modifiers mean "specific" —
scrub modifiers = coarser value jump (Ctrl ×10 / Shift ×100 / Alt ×1k…), hold modifiers = jump to depth N.
So the modifier vocabulary now spans BOTH interaction primitives uniformly.

### State system (controls = source of truth)
The state JSON is collected by WALKING THE CONTROLS, not a hand-maintained list — so it auto-grows with the
instrument (add a control → it's automatically in capture/export/recall). Inputs grouped by pipeline section
(DOM-derived). This is the same self-similarity-of-method idea (the structure does the work, not enumeration)
— noted as resemblance, not claimed as the construction's principle. Capture→JSON, recall→drives controls
back; round-trip confirmed working. copy=clipboard, export=file, recall=from-clipboard.

### Noted for future development (not built)
- PRESET SYSTEM (named/saved states + library) — recall-by-clipboard is the interim; the JSON schema is the
  foundation. Build backwards-compat/versioning only when the schema locks.
- SCRUB FINE-TUNING — the scrub feel (sensitivity / fine-vs-coarse / log curves) wants another pass.
