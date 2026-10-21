# Pipeline State — the unification investigation

> **Living document.** Update the timestamp and append to the change log whenever the state moves.
> Keep the status tags honest — promote a claim only when it is actually verified, and *retract in writing* if it overreached.

**Last updated:** 2026-05-31 (CDT) — caught up through the grid rebuild, both research dives, Sweep A, the hole-centric reframe, and the instrument.html fork.
**Keystone:** `proportional.html` — the sole rigorously verified construction. Everything rests on it.
**Active build:** `instrument.html` — forked from the now-locked `ellipsoid.html`, where research integration (the slices) happens.

---

## What this is: the Trajectoscope (instrument identity)

This is **an instrument** in the literal scientific sense — on the bench beside the microscope and the oscilloscope, but its own distinct thing. Its identity is **making high-dimensional trajectory-structure visible with precision and fidelity.**

- A microscope isn't "for biology" — biology is one thing you point it at; it *makes the very small visible*. An oscilloscope isn't "for electronics" — it *makes time-varying signals visible*. The **Trajectoscope** *makes the structure of trajectories through high-dimensional rotation-space visible.* What it studies is downstream of what it fundamentally does.
- **This reframes everything we've built:**
  - Extreme **timebases**, **aliasing**, **Nyquist / wagon-wheel** behavior = the instrument's *optics* (its sample-rate-vs-bandwidth art, the oscilloscope-equivalent).
  - The **verification discipline** ("verified not trusted," retractions, this catalog) = *calibration*. An instrument that lies is not an instrument; every verified rung is a calibration mark. This is *why* the rigor matters.
  - **Precision without physics is fully valuable** — the forms, the immersion, the meeting structure are real mathematical objects worth seeing clearly for their own sake. Fidelity *is* the value (a microscope on a crystal does no less than one on a cell).
- **Physics is a MODE, not the mission.** The instrument's identity is fidelity-to-trajectory-structure, so physics is one *configuration* (add coupling → it shows interaction-like behavior; coupling off → pure form, same fidelity). Switching modes does not change its identity.
- **This dissolves the "richness vs. rigor" tension:** the verified baseline (proportional, clean kinematic worldlines) is the instrument's **calibrated zero**. Modes (coupling, physics, deformation) are *excursions on top of it* that you can always switch off to return to known-good. You never lose the keystone by adding a mode — you keep it as the reference and make the mode a knob.

---

## Status legend

| Tag | Meaning |
|---|---|
| ✅ **VERIFIED** | Derived and checked numerically (≈1e-12 or tighter) against an independent computation, across the relevant range. Safe to build on. |
| 🟡 **TESTED INSTANCE** | Confirmed in at least one concrete case, not yet across the board. Suggestive, not load-bearing. |
| 🔵 **HYPOTHESIS** | A framing or conjecture with reasoning behind it but no/insufficient verification. Do not build claims on it. |
| 🟠 **REFINED / CAVEATED** | Was stated too cleanly; now corrected with cases. Use the caveated form only. |
| ⛔ **RETRACTED** | Claimed, then shown false or overreaching. Recorded so we don't repeat it. |
| 🔬 **SKETCH** | Unverified exploratory code/idea (e.g. the old Trajectoscope formulas). Makes no established claim. |

---

## The keystone (what we actually know)

✅ **proportional.html's rule.** Each cycle = [rotate, rotate, translate]; seed `[D,0,0]`; plane schedule `SCHED=[[0,1],[1,2],[0,2],[1,2],…]` (XY,YZ,XZ,YZ…). Self-scaling displacement law:
> **d = k·(k+1)^(C−1)·D**   (k = kHole, default 2; C = cycle)
Holds the central spherical hole at a **constant proportion** (k−1)/(k+1) self-similarly. **Verified self-similar to level 19** (holeRatio 0.3505, outerErr 0.993, comRel 0.0099, PCA flat-ring signature on-pattern). The earlier "breaks at L9" was an undersampling artifact, since corrected.

✅ **Construction = homogeneous 4×4 matrix product**, identical to the procedural scalar form to ~1e-13.

---

## The unification picture (the pipeline)

The working frame derived this session:

```
   OPERATIONS  ──Stage 1──▶  PARAMETERIZATION  ──Stage 2──▶  3D FORM
```

🔵 **HYPOTHESIS (overall).** That *every* form in the lineage is this one pipeline, with Stage 1 overridable (compose visible operations **or** state a closed-form coordinate function) and a shared Stage-2 projection. This is a lens to TEST, **not** a proven unification. The old formulas are 🔬 sketches, not evidence for it.

### Verified rungs of the pipeline (on proportional only)

1. ✅ **Operations ≡ parameterization** (Stage 1). proportional's operation-stack equals an INDEPENDENT hand-derived closed-form coordinate parameterization (nested cos/sin with interleaved coordinate-translations) to ~1e-14 across the **whole verified ladder L1–L4** (circle, sphere, torus, torus-sphere — incl. the non-trivial translation cases). Procedural-coord vs matrix matches to ~1e-12 out to L12. → *The op-stack IS a parameterization generator.*

2. ✅ **Intrinsically 3D; Stage 2 trivial.** Every operation maps ℝ³→ℝ³; no 4th coordinate is ever created. Output is literally `[x,y,z]`. So proportional needs **no projection** — unlike `freed` (builds 4D/5D, divides by `(R·1.4 − w)`, a real lossy projection). The paradigm difference lives at **Stage 2**, not Stage 1.

3. ✅ **Intrinsic manifold = L-torus immersed in ℝ³.** Jacobian rank → 3 at L≥3 (locally fills 3-space) while parameterized by L independent phases. So it's an L-dimensional torus *immersed* (self-intersecting), not projected from higher D. (Rank-2 samples at L3 are measure-zero tangent folds, expected.)

### The worldline thread (deepest, most pushed-on)

4. ✅ **Single tracing point → embedded worldline.** A point follows `(x(t),y(t),z(t),t)`. Since position is single-valued in t, the worldline **never self-intersects** — for ANY rates (rational or irrational). *(Corrected an earlier slip that tied this to irrationality; rationality governs closure/periodicity, NOT touching.)*

5. 🟠 **"Immersion with self-crossings" is one PROJECTION of the embedded worldline** — the particular projection you get by collapsing the time dimension to view the whole surface at once. It is a *choice*, not the only or the poorest option (deliberately avoid "shadow"/"silhouette": a silhouette discards everything but an outline and is the least expressive projection; a projection in general can preserve far more, and which one you take is up to you). Motion supplies the disambiguating dimension that would otherwise need a 4th spatial axis. **Caveat (permanent):** faithful as a *trace*; the instantaneous image is a single point; the full surface only exists as the time-integral (persistence/afterglow), and THAT time-collapsed projection is the immersed self-crossing one — collapsing time is just one projection among many.

6. ✅ **Apparent reversal = temporal aliasing (wagon-wheel).** Time is monotonic forward; a rotation *appears* to reverse exactly when its per-sample advance exceeds **π (Nyquist)**. Under the (1/π)^k cascade the OUTER (fastest) rotations cross Nyquist first, so different rotations in one form can read opposite apparent directions at once — pure sampling artifact. This is what `strobe`/`cpf` expose, and it is the same Nyquist relation as analog scan-rate-vs-bandwidth.

7. ⛔ **RETRACTED: the blanket "nothing ever touches."** True for ONE dot (rung 4); **false for the two-dot system** (see below). Use only the caveated two-dot form.

### The two-dot refinement (the precision the worldline claim missed)

8. 🟠 **Two-dot coincidences are REAL (not sampling artifacts), and mode-determined.** With a second dot `p₂ = transform(p₁)` sharing the same t, there can be genuine same-time coincidences `p₁(t)=p₂(t)`. The meeting locus = the **fixed-point set of the transform**. *(Loci re-verified against the ACTUAL proportional.html transform code while building the meeting readout — correcting an earlier mislabeling in the standalone test script:)*
   - **polar inversion** (p → p·R²/|p|²): meet on the **sphere |p|=R** — verified, minSep 0.00, hits cluster at |p|≈R. **This is the mode with the real meeting locus.**
   - **mirror** (p → −p): coincidence needs p=−p ⟹ p=0; meeting locus is the **origin only**, which the trajectory (radius ~R) never reaches → **effectively never touches** (minSep ≈ 2R).
   - **antipodal** (p → −p rescaled to rmax): also origin-only direction-wise → **never touches** (minSep ≈ 2R, larger).
   - In-tool `measureMeeting()` reproduces all of these exactly (headless cross-check).

9. ✅ **Lag governs simultaneity.** A phase-lag between the dots pulls them to *different phases* of the path, converting real same-time touches into near-misses (mirror+lag 0.15: min sep 0.000 → 0.506, hits 1442 → 5). The meeting locus is set by the mode; the lag decides whether both dots arrive there at the same t.

---

## Honest summary of the conceptual state

- The pipeline is a **hypothesis with a few solid rungs on proportional's side** (Stage 1 = parameterization-generator ✅; proportional is intrinsically-3D, immersed, Stage-2-trivial ✅).
- The **worldline reframing is real and strong** for a single point (✅ embedded; reversal = aliasing ✅), with the immersion-as-one-projection caveat (🟠) permanently attached — the time-collapsed image is one projection among many, never to be called a "shadow."
- The **two-dot system adds genuine intrinsic structure** (a real, mode-determined meeting set 🟠, lag-controlled ✅) that the single-point picture lacks. This is *not* an artifact and is the live precision the clean slogan missed.
- **Higher-level forms breathe; they do not break.** ✅ At L8 the gross form (size, hole, envelope) is stable but PCA shape-ratios and net-rotation angle are genuinely time-varying. The form is a mildly anisotropic near-sphere (PCA radii ≈ [0.70, 0.51, 0.50], aniso ~1.4, stable over time) that *reorients and breathes* as the trajectory sweeps. The apparent "drift from concentric iteration" at high levels is this real motion (now visible via the geometric skeleton), NOT a breakdown. A frame-misalignment "drift" hypothesis was tested and **not supported** — averaged over phases the per-slot orbit ratios are stable (period-4, ~constant), so the iteration is clean on average; the visible motion is instantaneous wobble + reorientation + an early-cycle transient. (Recorded in findings.md.)
- Nothing about the old 🔬 sketches (freed/Hopf/Lissajous/torus/epicyclic) is verified; they remain lineage/exploration, not evidence.

---

## Open threads / where this points next

- **Two-dot meeting set as a first-class object.** The coincidence locus (plane / sphere / origin) is intrinsic and mode-determined. Worth studying as *structure*, not decoration — possibly the more interesting direction than the single-point worldline.
- **Critical lag.** Is there an exact lag per mode that fully eliminates same-time touches? How does it scale with level / rates?
- **Higher levels.** Does the two-dot coincidence structure persist / change shape at L≥5?
- **Stage-2 as a swappable slot.** The unification's load-bearing question: is "immerse vs project" the sole real difference between proportional and freed/Hopf, holding Stage 1 fixed? (Untested.)
- **Time as the resolving dimension.** Possible that proportional doesn't immerse OR project — it *traces a worldline*, dimensionality handled by time, not a spatial projection. freed/Hopf collapse a *static* higher-D point spatially (real loss). Untested framing.
- **The anisotropy's origin & the series/spiral intuition.** The L8 form is anisotropic (~1.4). Where does that come from — the period-4 plane schedule favoring axes? And the user's strongest live intuition: the *sequence* of orbit scales / ellipsoids across levels may have a Fibonacci/golden-ratio/Fourier-harmonic growth structure worth making visible (orbit scales grow ~(k+1)=3× per cycle in self-scaling). `ellipsoid.html` shows the per-moment shape; next rung = show the SERIES.
- **More overlays for the affine space.** It's an affine space, so many grids/frames are possible. Candidates raised: alternative coordinate grids, the vector-equilibrium (cuboctahedron) as a reference frame / measurement overlay, other reference polyhedra. Open design question.

---

## Tooling state (the instrument's controls — all built, not yet all in the catalog body)

- **Scrub system:** drag (with Ctrl ×0.1 / Ctrl+Shift ×0.01 fine), double-click to type, **L/R full-height arrows** that snap to a per-param grid. Grid is **1 for integer-valued params, 0.1 for decimal-valued**, with an **8-tier modifier-depth ladder** (none·Ctrl·Shift·Alt·Ctrl+Shift·Ctrl+Alt·Shift+Alt·Ctrl+Shift+Alt → ×1,10,100,1k,10k,100k,1M,10M). render% opts out of depth (`data-nodepth`) and is capped 50–400 with a hard 4096-px canvas-buffer clamp (fixed a white-screen crash + the canvas-squeeze bug from pinning style.width).
- **Orbit mode:** ⟳ toggle; X/Y/Z become independent, stackable auto-orbit axis toggles (none active until picked); orbit honors freeze/step. Z is a screen-space roll (camera had no roll axis). Removed the redundant ←/→ level buttons (scrub covers it).
- **Second beam:** relation switch **derived** (transform of beam 1 — meeting theorem holds) vs **independent** (own rate ratio/drive/k/self-scale/radius/disp — free detuning, theorem doesn't apply). Controllable **polar inversion radius** to stop the second dot crushing at high levels.
- **Geometric skeleton:** now visualizes the true construction geometry — each rotation's **orbit circle** around its real pivot, each **displacement as an arrow**, the central **hole as a 3D sphere** at rmin. Verified the orbit circles exactly describe the construction (point on-circle before/after each rotation; perpendicular axis fixed; displacements pure-axis of length d).
- **`ellipsoid.html` (fork):** PCA **ellipsoid** wireframe (semi-axes 2√λ along eigenvectors, reorients live) + **beam off** toggle (hide dots, keep measuring) to see shape-in-motion alone. Geometry verified against the eigenframe.

---

## Change log

- **2026-05-30 22:57 (CST)** — Initial catalog. Recorded: keystone; pipeline hypothesis; verified rungs 1–3 (ops≡param, intrinsically-3D, L-torus immersed); worldline thread 4–6 (embedded worldline, immersion-as-shadow caveat, aliasing-as-reversal); **retracted** blanket "nothing touches" (rung 7); two-dot refinement 8–9 (real mode-determined meeting set on the transform's fixed-point locus; lag controls simultaneity). Branch point: shifting attention toward the two-dot meeting structure.
- **2026-05-30 23:30 (CST)** — Built the **two-dot meeting readout** into proportional.html (measured, verified side): `measureMeeting()` dedicated 2000-sample pass → panel reports touches/apart, locus (sphere|p|=R / origin / spread), min separation, hit count, locus residual; plus a `drawMeetLocus()` overlay (closest-approach marker + dashed sphere rings) behind a "meet locus" toggle. In-tool logic headless-verified to reproduce the loci. **Correction:** reading the actual transform code revealed the standalone test had mislabeled modes — corrected rung 8: **polar inversion** is the real-meeting-locus mode (sphere |p|=R); **mirror (−p)** and **antipodal** meet only at the origin → effectively never touch. The catalog now matches the code.
- **2026-05-31 01:07 (CDT)** — Caught the catalog up to a long tooling run on proportional.html (all on the verified side, no math changes): the L/R snap-arrow scrub system with the 8-tier modifier-depth ladder (grids 1 / 0.1); orbit mode (stackable X/Y/Z auto-rotate, freeze/step-aware); second-beam **derived vs independent** relation switch + controllable polar-inversion radius (the independent-beam refactor verified: identical params ⇒ identical point); the **geometric skeleton** rewrite (orbit circles + displacement arrows + 3D hole sphere, geometry verified exact); render% crash + canvas-squeeze fixes (4096 clamp, no style.width pinning). Forked **ellipsoid.html** for the anisotropy: PCA ellipsoid wireframe + beam-off. **Finding (findings.md + summary above):** higher-level forms *breathe* (stable size/hole, time-varying PCA shape & orientation) — real motion, not drift; a frame-drift hypothesis was tested and **not supported** (per-slot orbit ratios stable on average). Live direction: the user's Fibonacci/golden-spiral/Fourier-series intuition about the *sequence* of orbit-scales/ellipsoids — show the series next. Immediate next visual work: separate skeleton toggles per beam; more affine-space overlays (vector-equilibrium / reference frames).

---

## SMART GRID / MEASUREMENT SYSTEM — design spec (2026-05-31, building)

The instrument's grid+measurement layer, rebuilt as a coherent system instead of scattered overlays. A grid is a **4-tuple of independent axes**, all sharing ONE calibrated scale so overlays agree on "1 unit":

1. **SCALE** (the ruler): default `unit = D` (seed radius) in normalized space — the construction's natural unit, L1 circle = radius 1. Selectable: D-normalized / fixed-screen / rmax / self-similar (k+1)ⁿ. (Different rulers for different jobs; log-polar's (k+1)ⁿ rings verified to land on the form's per-cycle outer radii.)
2. **PLANE** (where it sits): screen / XY / YZ / XZ / PCA (form's own frame). One basis function → 2 orthonormal in-plane vectors + normal. Fixes the current breakage where the Cartesian grid was a floor (XZ, y=0) while other grids stood up in different planes — they couldn't be read against each other.
3. **COORDINATE-TYPE** (how it's ruled): cartesian / polar / log-polar / hex. Each renderer takes (basis, unit) — never invents its own plane/scale, guaranteeing proportional agreement.
4. **PROJECTION** (the "fold", a peer axis — NOT just a render detail): orthographic (parallel, true lengths — the measurement standard) / perspective (central, spatial intuition) / stereographic (conformal, preserves angles + maps circles→circles, natural for the near-spherical circle-built forms) / isometric (parallel oblique, multi-axis measurable). Each preserves a different invariant. This is the same "fold" idea from the projection-orientation observation — choosing the projection chooses what you can measure accurately. In ortho, a screen-plane grid fills the screen as a flat measurement overlay (graph-paper behind the specimen).

Control model: plane selector + coordinate-type toggles as separate groups (mix any plane × any type), plus scale selector and projection selector.

Build order (dependencies first, each verified): SCALE → PLANE basis → COORDINATE renderers → PROJECTION → controls. Replaces the scattered drawGrid/drawSphericalGrid/drawPCAGrid/drawPolarGrid/drawLogPolarGrid toggles.

---

## CHANGE LOG — catch-up 2026-05-31 (grid rebuild → dives → reframe → fork)

- **2026-05-31 — Smart grid REBUILT to a single bounded unit (supersedes the 4-axis SCALE selector above).** The grid system was finished and then simplified: instead of a multi-mode SCALE selector + "fill screen," there is now **ONE bounded unit = the form's total bounding radius (rmax) in draw space** (`gridBounds()` → {unit, inner, outer, divisions}; `gridUnitRadius()`=rmax). The form fills exactly one unit at every level; a **`divisions` control** subdivides that one unit (cell = unit/divisions). All grids (cartesian/polar/log-polar/hex/spherical/PCA) derive from `gridBounds()` → identical bounds → **comparable across grid types AND across levels** (every level normalizes to outer=1). PLANE (screen/XY/YZ/XZ/PCA via `planeBasis()`, screen-basis verified to face viewer) and PROJECTION (perspective/ortho/stereographic[verified conformal, circles→circles]/isometric, in `proj()`) retained as axes. ✅ verified: shared bounds, divisions subdivides cleanly, comparability across levels, stereographic conformal, plane basis correct.
- **2026-05-31 — log-polar maps the HOLE (verified).** Only the log-polar grid uses `inner` (the hole radius rmin): its central singularity (log 0) is anchored to the form's hole, the bright violet inner ring sits exactly on the void boundary (verified inner ring = rmin·scale), rings step outward by the self-similar ratio (k+1) counting levels. Polar does NOT use the hole (fills center; corrected from an earlier over-application). Cartesian/hex fill through the origin (translational grids). 
- **2026-05-31 — hex grid FIXED (verified).** Was three independent stripe families (disjointed moiré); rebuilt from a proper 60° lattice basis a=(u,0), b=(u/2,u√3/2) so all three families share vertices → true connected triangular lattice (verified: all families cover the same lattice points, every vertex has 6 equal-distance neighbors), clipped to the unit radius.
- **2026-05-31 — grid system moved to its own "grid & measurement" zone**; beam-feature overlays (skel/axes/bbox/COM/PCA/ellipsoid/VE/frame/spin/meet/angles) stay in their own row (separate concern: specimen features vs measurement grid).

### FINDINGS logged this session (see findings.md for detail)
- **VE / cuboctahedron L1-touching** (🟠 refined): L1 orbit circle passes exactly through 4 of 12 VE vertices at the XY diagonals; it's an L1-pristine-circle SYMMETRY phenomenon, NOT an all-levels proportionality (stronger reading retracted; later pivots are offset).
- **Ellipsoid period-2 pattern** (✅ verified): PCA shape alternates by parity — even levels PROLATE (→[0.697,0.508,0.506], aniso~1.37), odd levels OBLATE (→[0.697,0.697,0.169], aniso~4.12); period-2, converges by ~L7; ratio-independent (geometric, not timing). Corrected user's "non-repetitive" → strongly period-2 once settled.
- **Sweep A** (✅ verified): the pattern is schedule-FAMILY-specific (reorder to XY,XZ,YZ suppresses the flip); largest radius ~k-invariant (~0.697); k controls the OBLATE short axis (r3: 0.205→0.101 as k:1.5→4.0); 0.697 not a clean named constant.

### RESEARCH DIVES completed (both un-built — feed the integration plan)
- **MATH dive** (artifact): named the object — **Stein/Lyapunov fixed-point covariance of a self-affine measure**; period-2 flip = **Floquet period-doubling** of the monodromy; rate-independence = **Birkhoff/Weyl ergodicity**. 0.697 = angle-dependent eigenvalue, not a constant. Adoptables: **FA + Westin cl/cp/cs** (replace ad-hoc aniso); **weighted Birkhoff averaging** (exp(−1/(t(1−t))) weight, super-poly convergence); **Babylonian rotation-number** method + Diophantine/golden-ratio resonance distance; **Kindlmann superquadric** α/β/γ. Caveat: the PCA-shape parity *synthesis* has no single prior cite (nearest = Floquet); raw series diverges, only NORMALIZED shape converges.
- **PRESENTATION (build) dive** (artifact): buildables — **4-tier luminance hierarchy** (#0A0E12 canvas, no #FFFFFF lines); **Viridis/Cividis + Okabe–Ito/Tol** palettes (hex given); **GUM/NIST** value±uncertainty formatting; **oscilloscope cursors + ASME calipers + radial protractor**; **10×8 graticule** specs + 0.5px snapping + LOD anti-moiré; **small multiples** layout; **Gleicher comparison** modes + DEC color + phosphor persistence; greedy **label de-confliction**.

### CONCEPTUAL REFRAME (this session — drives the integration)
- **Twin lenses, unprivileged:** form (nested shells) vs hole (nested void-boundaries; trace = rim of holes held at (k−1)/(k+1)). Same construction; both inform it.
- **unit = total bounding radius = 1** (form fills its bound; total radius is information-free). Everything reads as dimensionless unit-fractions.
- **The meaningful radius is the HOLE radius** = (k−1)/(k+1) — the only radial degree of freedom; reading it against the unit IS reading k. Already has a visual home (log-polar inner ring). Coherence check: the hole radius and the PCA ellipsoid's k-controlled short axis r3 are "the radius k controls" seen two ways.
- **k = the one shape knob;** seed radius D and absolute pixels are absorbed by normalization (zoom only).

### LINEAGE (corrected)
- `proportional.html` → keystone (verified math) · `proportional_REFERENCE.html` locked
- `ellipsoid.html` → anisotropy + grid build · **`ellipsoid_REFERENCE.html` locked** (clean ref, 2026-05-31)
- **`instrument.html`** → ACTIVE: research integration (forked from locked ellipsoid; the slices build here)

### NEXT: integration_plan.md
Eight slices, meaning→compute→display each, leverage-ordered. Slice 0 = this catalog catch-up + lock (DONE). Slice 1 = measurement-readout layer (hole-radius/unit-fractions + FA/Westin + GUM formatting) — the first real build, conceptualized this session. Then visual hygiene, cursors/calipers, small-multiples, then superquadric/Birkhoff/rotation-number. Parked: Floquet monodromy test (closes period-2), Stein closed-form, twin-lens toggle, projection probe. Discipline: one verified rung at a time, REFERENCE lock before edits, headless verify before claims.

---

## CHANGE LOG — Slices 1 & 2 complete + overlay/UX cleanup (2026-05-31, later)

**SLICE 1 — measurement-readout layer (✅ COMPLETE, all verified headless).** The instrument now reads in its own dimensionless invariant units with literature-standard anisotropy and quantified uncertainty:
- *Rung 1 (unit-fractions):* total radius → constant "1.00 unit (the bound)"; **hole radius** is now THE radius readout, shown as a unit-fraction in violet with the theoretical target "(k→0.333)". VERIFIED in real geometry: measured hole radius (rmin/rmax) = theoretical (k−1)/(k+1) across k=1.5–3.0 to ~0.004 (theory is cycle-boundary proportion, measured is whole-orbit extremum → close not exact, expected). Displacement → "k× radius/cycle".
- *Rung 2 (FA + Westin):* replaced ad-hoc "aniso=1−r2" with **Fractional Anisotropy** + **Westin cl/cp/cs** (linear/planar/spherical, sum to 1). VERIFIED against sphere(FA0)/line(FA1,cl1)/plane(cp1) and the Sweep A prolate/oblate limits. CLASSIFIER FIX: shape label gates "isotropic" on FA<0.15 then reports deviation direction (cl≥cp→prolate else oblate) — NOT "largest coefficient" (which mislabels mild anisotropy as isotropic since cs dominates until FA is large; caught by verification).
- *Rung 3 (GUM ± bands):* the breathing → honest uncertainty. Added a rolling-stats tracker (`breath{}`, ROLL_WIN=48) + `fmtPM(mean,sd,fallbackDp)` formatting value±uncertainty (uncertainty 1 sig fig, value rounded to match; plain decimals when spread~0). VERIFIED formatter. Used 1 sig fig deliberately (GUM allows 1–2; 1 is stable for a live readout).
- *Slice 1 CLEANUP (from live stress-testing):* hole radius does NOT breathe (structural rmin/rmax, not dynamic) → removed its ± band, kept FA's. Retired the **D radius scrub** (pure zoom, absorbed by normalize) — **k is the radial sculpting knob** now (tooltip says so). Removed the **displace scrub** (d=k×radius, redundant). Then, after deeper verification: removed global **rate shape/drive** and **disp shape/drive/ratio** too — all verified INERT under normalization (Δshape≈0.000 for rate, ≤0.011 sub-perceptual for disp). KEPT + PROMOTED the **per-level rate overrides** (rateOverride/`__ro`) out of their dropdown into the main RATES row — these DO reshape the form (verified Δhole=0.013; they break per-level uniformity → change relative frequencies + teleport/aliasing render). Net: the control surface is now honest — ONE shape knob (k), rate ratio, per-level rate overrides; everything else absorbed/derived. Legacy self-scaling-OFF disp branch kept (dispMult→1.0).

**SLICE 2 — visual hygiene pass (✅ COMPLETE, verified).** The full presentation-dive treatment, substrate→palette→crispness:
- *Visual system (single source of truth):* CSS vars + JS constants — Okabe–Ito colorblind-safe palette (`OK.{orange,sky,green,yellow,blue,vermillion,purple}`), 4-tier luminance bands (`TIER.{data,feature,grid,annot}`), helpers `rgba()` + `tierA()` (clamps each overlay into its tier's alpha band).
- *Applied everywhere:* canvas → #0A0E12; every stroke routed through tier+hue; the lone pure-white line (#fff) eliminated; **no #FFFFFF lines remain**.
- *Tier assignment:* grids = faint grid-tier; features (skeleton/bbox/ellipsoid/VE/hole-ring/hole-sphere) = mid feature-tier; markers/reference-rings/meet = annotation-tier.
- *Grid-hue refinement (after user feedback that one color bled together):* the 5 toggleable grids get DISTINCT hues at the SAME faint grid alpha → distinct from each other (hue axis) yet unified as the quiet layer (luminance axis): **cartesian=sky, polar=orange, log-polar=green (inner hole-ring stays feature-purple), hex=yellow, spherical=vermillion**. The XYZ axis triad + principal-axis triads also use distinct OK hues.
- *Crispness:* devicePixelRatio was already handled in resize; added **`gridLOD()`** — culls grid cells projecting below ~6px, fades them in 6→12px, *intended* to reduce moiré from sub-pixel grid lines. The cull/fade THRESHOLD MATH is verified; whether it actually eliminates moiré is a PERCEPTUAL claim NOT yet verified (needs driving to confirm). Applied to the dense grids (cartesian, hex).

**OVERLAY / UX CLEANUP (✅ COMPLETE, verified).** Beam vs overlays cleanly separated + several fixes:
- *Zone split:* beam zone keeps render controls (normalize/auto-fit/beam-off); NEW **"overlays" zone** holds all 14 feature toggles led by a **master "ALL overlays" checkbox** that gates everything on the overlay canvas (features + grids) in one click. Grid zone stays separate. Measurement (measureMeeting) stays ungated — only drawing is gated.
- *Save composite image:* the beam (#c) and overlays (#o) are separate stacked canvases, so the browser's native right-click "save image" only grabs one. Added a **"⤓ save image" button** that composites both onto a temp canvas at device resolution → timestamped PNG. (Right-click-save can't be fixed from our side — it's a browser feature that acts on one DOM element; the button is the mechanism.)
- *Ratio stepper arrows:* ◂ ▸ buttons flank the rate-ratio select to cycle ratios without opening the dropdown. FIX: build the flat id-list directly from RATIO_GROUPS so it spans ALL optgroups (first version only cycled the first group).
- *Arrow-key level nav:* ←/↓ step level down, →/↑ up (mirrors the level scrub; ignored while typing in a field).
- *TWO real rendering bugs found via user driving + targeted tests (couldn't be found by reading):*
  1. **Beam afterglow never reached zero:** a 50%-opacity fade rect halves but never erases at 8-bit depth → faint dot residue piled up. FIX: at afterglow≈0 (`fadeV<0.004`) HARD-CLEAR the beam canvas; fade only when afterglow>0 (intentional phosphor trails).
  2. **Fractional-dpr edge strip (the stubborn one):** stuck colored residue on the RIGHT + BOTTOM rows only. Cause: buffer is `Math.round(W*dpr)×Math.round(H*dpr)` device px, a fraction larger than `clearRect(0,0,W,H)` covers in the transformed space → unclearable 1px rim on the far edges where edge-reaching grids accumulated. FIX: clear `W+2,H+2` (overscan; off-canvas draws are silently clipped, so it's free) at all clear sites (per-frame overlay clear, beam clear, hardClear). The bottom/right-only asymmetry was the diagnostic tell.
- *Also:* updated the stale `note` text (was describing the removed disp ratio/shape/drive) to the current k + rate-ratio + per-level-override surface.

### STATE NOW
- **instrument.html** = the active build, with Slices 0–2 + cleanup all complete. Reads in dimensionless units (total=1, hole=(k−1)/(k+1)), FA/Westin anisotropy with GUM ± bands, 4-tier Okabe–Ito visual hierarchy with distinct grid hues, LOD grid culling (threshold math verified; moiré-elimination is an unverified perceptual claim — confirm by driving), clean canvas (both edge/afterglow bugs fixed), separated overlay layer with master toggle + composite save, ratio steppers, arrow-key nav.
- Keystone (proportional.html) + ellipsoid_REFERENCE.html remain locked. Construction/geometry UNCHANGED through all of Slice 1–2 (verified — all changes were measurement/readout/visual/UX, never the math).
- **NEXT:** Slice 3 (cursors/calipers/protractor — the measurement INTERACTION) per integration_plan.md. Parked: homology/persistent-homology research target (added this session, sharp framing logged); Floquet monodromy test; Stein closed-form r3(k); twin-lens toggle; projection probe.

---

## CHANGE LOG — Slice 3 measurement-readout layer (2026-05-31, later still)

**SLICE 3 (in progress) — relational measurement readout.** Reframed away from arbitrary cursor-pixels: measurement is RELATIONAL — the overlays/grids ARE the reference frames. The active plane + grid + divisions define the measurement frame; the tool reads the current point AGAINST that configured frame. Built + verified as rungs:

- *Rung 1 (grid-coordinate readout):* the current point read in the configured measurement plane as grid-cell coords + unit-proportion coords + an out-of-plane offset (honest: point is 3D, the frame is a 2D slice). The plane/grid/divisions selectors ARE the frame (no separate picker). Caught + fixed a DOUBLE-SCALE bug — `meas.curPt` is ALREADY draw-space (build() normalizes it), so the extra `mScale()` multiply was halving the reading (showed ~1.5 cells where the eye saw ~3). VERIFIED: point in each plane gives correct, consistent coords; off-plane offset correct (a point on +x reads in-plane in XY/XZ, pure off-plane in YZ where x is the normal).

- *Rung 2 (projection-MODE sensitivity):* the reading is ROTATION-INVARIANT (dotted onto the world-fixed plane basis → orbiting the camera never moves it) but responds to the projection MODE — using the OFF-PLANE distance as the depth (not camera depth). ortho≡iso (parallel, no warp); perspective & stereo foreshorten by depth (differ). VERIFIED: in-plane point unaffected by mode; ortho===iso at every depth; perspective≠stereo when off-plane; rotation-invariant by construction. (This is exactly the behavior the user observed and asked for: rotate ≠ change, projection-mode = change.)

- *Rung 3 (grid-LOCATION = caliper address):* a discrete address distinct from the continuous unit readout — the in-plane unit-fractions SNAPPED to a caliper resolution, shown as raw fractions over that resolution (e.g. `[ +6/16, −4/16 ] u @cal/16`). The caliper resolution (`calRes`) is INDEPENDENT of the visual grid divisions, locked to a power-of-2 ladder (2/4/8/16/32/64) so fractions NEST cleanly — VERIFIED 0.375 → 3/8 → 6/16 → 12/32 (same place, numerators scale; a vernier refines, never relabels). Design principle (user-driven): a real caliper has FIXED resolution; grid locations are always fractions, resolution just sets the depth. New `caliper /N` control added next to `divisions`.

- *Rung 4 (per-grid-type natural readings):* one readout line per ENABLED grid, each in its OWN coordinate system + color-matched to that grid's hue, all from the same projection-corrected in-plane point (spherical uses the full 3D point): **polar** r+θ; **log-polar** ring-index (counted in the construction's (k+1) self-similar step, ring 0 = hole edge) + θ; **hex** lattice (i,j) via the non-orthogonal basis 2×2 inverse; **spherical** r/lat/lon (3D). VERIFIED each: hex round-trip reconstructs the point; log-polar ring 0 = hole, ring 1 = ×(k+1) out. Caught + fixed two bugs pre-ship: invented a nonexistent `OKc()` color helper (→ `rgba(OK.x,1)`), and referenced `frame()`-scoped grid flags inside `updatePanel()` which would've thrown (→ read the checkboxes directly).

- *Live-readout interaction (the freeze-to-read coupling):* live values strobe and can't be read while moving — and a position readout on a moving point isn't a measurement of anything anyway. Wrapped the whole readout panel in a collapsible `<details>` ("measurement readout — freeze to read"), collapsed by default. **Freeze auto-OPENS it; resume auto-collapses** — the freeze button is the cue to read. Nothing hidden (can expand manually anytime); strobing values just fold away during visual exploration. Matches what measurement IS: a stop-and-read act. Existing `frozen` flag + freeze button reused; readout logic untouched (still writes `#panel`).

### DATA SNAPSHOT logged (L3, k=2, cycle 1) — construction confirmed on-theory
holeRatio 0.3333 = exactly (k−1)/(k+1); rOuter 240 / rInner 80 (D=80=rInner at L3, innermost circle not yet displaced); PCA [15251, 15031, 1575] → pcaR2=0.103 = OBLATE (two big near-equal axes + one ~10× smaller), consistent with odd-level→oblate parity; predOuter=240 outerErr=1.000 (growth law D·(k+1)^C exact); comRel 0.0127 (essentially centered); netDeg 107.6 about (0.02, 0.84, −0.54). No anomalies — readout internally consistent.

### NOTED for later
Question raised (parked, not yet built): relationships ACROSS the grid readings. Structural expectations to test by driving — (a) θ is shared/identical across polar/log-polar/spherical-lon (consistency check, not a discovery; divergence would flag a bug); (b) the meaningful one: log-polar ring = log(polar_r / hole)/log(k+1), so equal ring-steps = multiplicative radius-steps = the (k+1) self-affinity made visible; (c) polar_r vs spherical_r ratio = cos(lat) = off-plane content (cross-checks the off-plane offset); (d) hex↔cartesian = a fixed linear shear (drift would flag a bug). Whether the frames CONVERGE at clean configs (k=2, point on axis) is the open question.

### STATE NOW
- **instrument.html** = active build. Slices 0–2 complete; Slice 3 measurement-readout layer complete (rungs 1–4 + freeze-to-read interaction), all verified. Remaining Slice 3 pieces NOT yet built: the visual CALIPER (on-canvas draggable endpoints reading these units) and the VE ANGLE-reference (angles off the vector-equilibrium's known symmetry directions).
- Construction/geometry UNCHANGED throughout (all measurement/readout/visual/UX). Keystone + ellipsoid_REFERENCE + instrument_REFERENCE_slices012 remain locked.
- **NEXT:** finish Slice 3 (caliper and/or VE angles), then Slice 4 (small-multiples). Parked research: homology/persistent-homology; Floquet monodromy; Stein closed-form r3(k); twin-lens toggle; projection probe; cross-grid-reading convergence question.

---

## CHANGE LOG — Slice 3 caliper rung 1 + UX RESTRUCTURE begun (2026-05-31, later still)

**Caliper rung 1 (point → 3D feature) — DONE & verified.** The caliper is one tool, endpoint A = the dot
(trajectory point, always), endpoint B = a chosen target. Rung 1 = 3D-feature targets:
- Feature registry `caliperFeatures()`: real 3D snap targets in DRAW space — origin, COM (nrm'd), point,
  point2, the 6 ellipsoid axis vertices (±maj/mid/min at 2σ), VE vertices (when VE shown). NO arbitrary
  points → no depth ambiguity, fully relational. Reframed AWAY from proximity-snapping per user: it's
  EXPLICIT target selection (precision, not generalness) — a dropdown auto-populated with available features.
- `drawCaliper()` draws the dot→target dimension line + endpoint marks (annotation tier). Readout (in the
  freeze-to-read panel): true 3D distance in unit / cells / caliper-address + az/el angle. VERIFIED math
  (dot→origin = |dot| exactly; per-target distances correct).
- Also added the **VE angle-reference** (symmetry-as-protractor, prior rung): when VE shown, reports the
  PCA major-axis and current-point angles to the nearest VE vertex ray (0° = aligned to known symmetry).
  VERIFIED: on-vertex=0°, 3-fold axis=35.3° (exact acos√⅔), range 0–~44°.

**Caliper MODEL finalized (user-driven, the relational spec):**
- Endpoint A always the dot; B is a chosen target, of two kinds: a **3D feature** (→ true 3D distance) OR
  a **grid location on the face** (→ in-plane "face" distance, measured as if looking straight at the plane).
- Grid-location targets specified in the ACTIVE grid's coordinate system: cartesian (cell u,v) / polar (r,θ)
  / log-polar (ring,θ) / hex (i,j); spherical handled as 3D. VERIFIED all coord→face-position conversions.
- Rung 2 (grid-location targets + grid-coord-adaptive entry) NOT yet built.

**★ UX/UI RESTRUCTURE — planned, branch forked, NOT yet built.** The instrument grew capability fast; the
layout lagged the meaning. Full plan in `ux_plan.md`. Organizing spine (a pipeline, each stage consumes the
previous): **EXPRESSION (the math) → BEAMS (what the math affects) → PROJECTION (how you see it) → GRIDS
(how you map it) → MEASUREMENT (how you measure the map).** Plus progressive disclosure (common controls
visible, advanced folded) for real estate. Key decisions locked:
- GRIDS absorbs ALL overlays (skeleton/ellipsoid/VE/axes/bbox/COM/PCA/frame/…) — they ARE the map's
  reference geometry, what measurement reads against. The old "overlays" zone dissolves into GRIDS.
- Camera (X/Y/Z/orbit/reset) folds into PROJECTION (it's how-you-see); nav bar dissolves.
- MEASUREMENT zone = freeze/step gate + caliper + a measurement-readout DISPLAY.
- Beam 1 & beam 2 become INDEPENDENT toggles (`beam1Chk`/`beam2Chk`), true peers (replaces `beamOffChk`).
- DROP normalize + auto-fit as controls (always-on now; the unit/measurement frame depends on normalize;
  keep both true internally). Honest cleanup, same spirit as the Slice 1 control purge.
- Common overlays visible in GRIDS: skeleton, ellipsoid, VE, axes. Rest fold. COM flagged LIKELY-REDUNDANT
  as a measurement target (comRel≈0.0127, so dot→COM ≈ dot→origin; keep for now, let the instrument confirm).

**★ LOG-COMPLETENESS GAP found (correctness issue, fix FIRST).** `logState` reads STATE directly (vals,
kHole, a fresh measureDense pass) — so it's fully DECOUPLED from the UI; the restructure can't break logging.
BUT the log currently captures construction/PCA/rotation state and does NOT capture the newer measurement
OUTPUTS: FA, Westin cl/cp/cs, caliper distance/target, VE-angle, grid coordinates. That violates "capture
every input and output across the board." Must add these log columns (it's data integrity, separate from the
visual regroup). The measurement values are computed once in updatePanel → shown in master panel AND (to be)
in the measurement zone by the caliper; logState independently re-captures from state.

### REVISED BUILD SEQUENCE (the UX branch, instrument_ux.html)
1. **Log-completeness FIRST** (correctness): add missing columns — FA, cl/cp/cs, caliper dist+target,
   VE-angle, grid coords. + drop normChk/fitChk toggles (keep internal true) + rename beam→beam1Chk/beam2Chk.
2. **Five-group HTML restructure**: regroup ALL controls per ux_plan.md (expression/beams/projection/grids/
   measurement); COPY the measurement readout into the measurement zone (keep it in master too — one source,
   two displays).
3. **Progressive-disclosure folds** throughout + **dropdown steppers** on all selects (restyle .selar to
   match scrub arrows — arrows on every dropdown is now a design principle).
4. **Caliper rung 2**: grid-location targets with grid-coord-adaptive entry.
5. Final tighten + drive-test.

### LINEAGE (updated)
- `proportional.html` keystone · `ellipsoid.html` · both _REFERENCE locked.
- `instrument.html` = Slices 0–3 build (caliper rung 1 done) · locked `_REFERENCE_slices012` AND `_REFERENCE_preUX`.
- **`instrument_ux.html`** = ACTIVE UX-restructure branch (forked from instrument.html pre-UX).

### STATE NOW
- Active = instrument_ux.html. Construction/geometry UNCHANGED throughout (all UI/readout/measurement). 
- Slices 0–2 complete; Slice 3 = measurement readouts + VE-angle + caliper rung 1 done; caliper rung 2 +
  the UX restructure pending on the branch.
- NEXT: execute the revised build sequence above, starting with log-completeness.

---

## CHANGE LOG — UX restructure EXECUTED on instrument_ux.html (2026-05-31, continued)

The planned UX restructure (ux_plan.md) is now BUILT on the branch. Done & verified:

**Log-completeness fix (correctness, done first):** added the missing measurement-output columns to logState —
FA, Westin cl/cp/cs (computed from the dense PCA eigenvalues), veMajDeg (VE angle of major axis), calTarget,
calDistU (caliper distance as unit-fraction). The log now captures every output. (logState reads STATE
directly, so it was already decoupled from the UI — the restructure couldn't break it.)

**Five-group pipeline (the spine):** EXPRESSION → BEAMS → PROJECTION → GRIDS → MEASUREMENT, reordered so
Expression + Projection sit ABOVE the canvas (set-up-before-you-look) and Beams/Grids/Measurement below.
Dropped normalize + auto-fit toggles (always-on now, kept true internally). Beam 1 / beam 2 are now
independent peer toggles (beam1Chk/beam2Chk, replacing beamOffChk + p2Chk). GRIDS absorbed all the overlays
as "reference geometry" (the old "overlays" zone dissolved). Camera (X/Y/Z/orbit/reset) folded into PROJECTION.

**★ LOD-ZONE disclosure system (the novel UX piece):** each section is a `<section class="lodzone">` whose
header BAR is a drag control — drag DOWN to reveal depth (tiers), snapping per ~38px; click steps +1 (wraps);
depth pips (●○) show level. Replaces click-to-toggle `<details>` folds with a drag-to-reveal-depth gesture,
consistent with the scrub language (everything in the instrument is drag-driven). Tier depth per section,
content-driven (the "a fold must hide 3+ controls" rule): Expression 2, Projection 2, Beams 3, Grids 3,
Measurement 2 (12 tiers total). All sections default COLLAPSED (depth 0). MOBILE FIX: the bar handlers
stopPropagation + preventDefault on touchmove ({passive:false}) so the downward drag doesn't get hijacked by
the page/popup as a scroll/dismiss gesture (this was a real bug, fixed + confirmed on mobile).

**Measurement readout split (copy, not move):** measurement readouts (grid coords / grid-loc / per-grid
naturals / caliper / VE-angle) built once into a `measLines` var, shown in BOTH the master panel (complete
record, below canvas) AND a copy in the Measurement zone (measPanel) by the caliper. logState independently
re-captures from state, so logging stays complete regardless of display.

**Cleanup pass:** log-state + save-image moved into MEASUREMENT (capture actions). Top header stripped to a
minimal title (the verbose d=k(k+1)^(C−1)D description removed from the top). 

**★ INFO/DOCUMENTATION PANEL — STUBBED (working container, populate later):** a collapsed "ℹ how it works"
panel at the bottom holds the relocated construction description (stated mechanically) and is marked [STUB]
with the full scope + the claims discipline recorded in both visible text and an HTML comment.

### ★ NEW FUTURE SLICE — DOCUMENTATION SUBSYSTEM (logged, not built)
Comprehensive in-instrument reference. NOT the lodzone drag-fold (that's for controls); documentation is
prose+structure and needs its OWN navigation suited to a large body of words/ideas — its own design pass.
SCOPE (comprehensive): the full construction recurrence + plane schedule + the d=k(k+1)^(C−1)D derivation;
the definition of EVERY measured readout (hole ratio = measured rmin/rmax; FA + Westin cl/cp/cs from PCA
eigenvalues; grid-coordinate math per coordinate system; caliper distance); the five-group control logic;
a control reference. **CLAIMS DISCIPLINE (hard rule): describe ONLY what is mechanically verifiable and HOW
it is computed. NO claims of significance, purpose, or what anything "reveals." Pure mechanism + the math
that provably follows. A reference manual, not a sales pitch.** Orthogonal to integration-plan slices 4–7
(it's docs, not capability); slots in as its own pass after the UX restructure + caliper rung 2 finish.

### UX RESTRUCTURE — REMAINING
- `.selar` dropdown-stepper RESTYLE to match the scrub arrows (they work, still look bespoke).
- Optional: the truly-minimal "bare name+value" row rendering (tier spacing tightened; labels still shown).
- Caliper RUNG 2 (grid-location targets, grid-coord-adaptive entry).
- Then: drive-test the whole branch; if good, it becomes the main instrument.

### STATE NOW
- Active = instrument_ux.html (five-group pipeline + lodzone disclosure + log-completeness + dual readout +
  info stub). Verified: parses, no duplicate ids, all 58 JS ids resolve, construction UNTOUCHED.
- instrument.html unchanged (the pre-UX fallback, locked _REFERENCE_preUX).

---

## SESSION CHECKPOINT — UX branch consolidated (2026-05-31, session close)

Final readout/structure fixes on instrument_ux.html since the UX-execution entry above:
- **Full-state readout relocated INTO Measurement** as its own tier (tier 3, freeze-to-read). The standalone
  `measWrap` block below the canvas is gone; the complete state (`#bar` + full `#panel`) now lives in the
  Measurement section. Freeze button rewired: freezing opens Measurement to full depth (reveals the full-state
  tier), resume returns to tier 1.
- **Prose blocks moved into the info panel:** the dynamic per-level `#desc` and the static k+rate-ratio `#note`
  were standalone always-visible divs floating between sections — both now live inside the "ℹ how it works"
  info panel where they belong. No more redundant prose outside the panel.
- **Full-state header simplified:** was "level N · point (dot) · cycle M" (pulling formName); now just
  "level N · cycle M". The form-name language (point/dot/circle/…) removed from the readout.
- Measurement is now a 3-tier lodzone (freeze+caliper+log+save+meas-readout / caliper-res / full-state).
- All verified: parses, no duplicate ids, all 57 JS ids resolve, construction UNTOUCHED.

**DESIGN VOCABULARY + METHOD recorded** (in ux_plan.md, framed as lens-not-claim): the three interaction
primitives — **HOLD** (depth/vertical), **SCRUB** (continuous value/horizontal, coarse via arrows + fine via
drag), **SELECT** (discrete kind, orthogonal — picks which space). The development method: vertical-then-
horizontal (one path to depth, then vary alongside without disturbing); default branch always available,
override optional never forced. The resemblance to the construction's self-similarity noted as resemblance,
NOT asserted as the same principle.

### MILESTONE: the instrument_ux branch is a coherent, slick system
Five-group pipeline (EXPRESSION→BEAMS→PROJECTION→GRIDS→MEASUREMENT) with the novel hold-based drag-to-reveal-
depth disclosure on desktop + mobile, complete logging, dual measurement readout, full-state readout housed in
Measurement, and an honest documentation stub with the no-claims discipline baked in. Construction math
unchanged + verified throughout the entire restructure.

### ═══ NEXT STEPS (charted) ═══
**A. Finish the UX branch (small, contained):**
  1. `.selar` dropdown-stepper RESTYLE to visually match the scrub arrows (fitting — selects are a sibling
     primitive to scrubs/holds). They function; they just look bespoke.
  2. Optional: the truly-minimal "bare name+value" row rendering (currently labels still shown).
  3. DRIVE-TEST the whole branch end-to-end. If good → PROMOTE instrument_ux.html to the main instrument.html
     (lock the current instrument.html first as another reference).

**B. Then resume CAPABILITY (the integration-plan slices):**
  4. Caliper RUNG 2 — grid-location targets with grid-coord-adaptive entry (the half-built measurement piece).
  5. Slice 4 — small-multiples (where the period-2 prolate/oblate flip becomes directly VISIBLE as a sequence).
  6. Slices 5/6/7 — superquadric glyph / weighted Birkhoff / rotation-number. Floquet monodromy whenever.

**C. Orthogonal, its own pass (not blocking):**
  7. DOCUMENTATION SUBSYSTEM — populate the info-panel stub into the full comprehensive reference (its own
     navigation, NOT the lodzone). Hard claims discipline: mechanism + provable math only, zero interpretation.

**D. The investigation we keep deferring (worth doing):**
  8. Turn the verified instrument ON the specimen — drive the readouts to answer the parked questions: does
     log-polar ring vs polar radius show the (k+1) self-similarity? Do the frames converge at clean configs?
     Does the VE major-axis angle flip with the odd/even parity? (We've built measurement tools and barely
     used them to learn about the object.)

**PARKED (with reasoning, in integration_plan.md):** angular caliper / protractor (needs more angular
references first); homology/persistent-homology; Floquet monodromy test; Stein closed-form r3(k); twin-lens
toggle; projection probe.

Suggested order: A (finish + promote the branch) → D (actually investigate — high value, tools already built)
→ B4 (caliper rung 2) → B5 (small-multiples) → C (docs) → B6/7. But D could jump ahead of A if the urge is to
learn rather than polish.

---

## ★ UX LOCKED — instrument_ux.html (2026-05-31, UX restructure complete)

The UX restructure is DONE and considered locked. Final work this session beyond the prior checkpoint:

**Projection parameterized (existing modes).** The two frozen magic numbers are now tunable scrubs:
`focalLength` (perspective's 480 — focal length / viewing distance; smaller = wider FOV, stronger
foreshortening) and `stereoR` (stereographic's 320 — projection-sphere radius / field curvature). They live
in PROJECT tier 2, ADAPTIVE to the active mode (focal shows when perspective, sphere R when stereographic,
neither for ortho/iso which are parallel and have no depth param). Adaptive show/hide runs per frame via
`.projparam[data-mode]`. Globals wired into proj(); get/set added to initScrub (`__focal`, `__stereoR`).
VERIFIED parses + behaves.

**Stepper-arrow bug FIXED (functional).** The `.selar` handler was hardcoded to cycle `RATIO_FLAT`, so only
the rate-ratio stepper worked; projection/plane/caliper-target steppers were dead (their values aren't in that
list). Made GENERIC — cycles the target select's OWN `.options` (live collection; flattens optgroups, picks up
JS-populated options), wraps both directions. Audited all 4 targets (rateRatio optgrouped, gridProjSel +
gridPlaneSel static+polled, calTarget JS-populated) — all cycle correctly. Simulated the wrap headless.

**Expression cleanup.** self-scaling toggle moved to tier 1 (with level/k/ratio); tier 2 = just the per-level
rate scrubs (dropped the "per-level rate ×:" label — the L0/L1/… scrub labels are self-descriptive).

**Select-arrow sizing.** `.selstep select` padding bumped to 6px to match `.scrub .sval`, so the stepper arrows
are the same height as the scrub arrows (the selects are a sibling primitive, should look kin).

### ═══ FINALIZED PIPELINE VOCABULARY (locked) ═══
Tier-1 names are the bare, concrete thing you actively work with (no -ion/-ment/plural). Tier-2 subtitle is
the plain RESULT-NOUN — what that thing produces or is. The relationship-VERB (how it does it) lives in
tooltips/docs, NOT the label (because the relationships genuinely differ — provide/reinterpret/trace/use/
define — and a uniform suffix would flatten them).

| tier-1 (the thing) | tier-2 (result) | relationship-verb (→ tooltip/docs) |
|---|---|---|
| express  | structure       | express PROVIDES the structure |
| project  | interpretation  | project REINTERPRETS the structure many ways |
| beam     | trajectory      | the beam TRACES the trajectory |
| grid     | chart           | the grid is the CHART that measure reads against |
| measure  | relation        | measure DEFINES the relation (using the grid) |

The pipeline as a sentence: you EXPRESS to get a structure, PROJECT to interpret it, the BEAM traces a
trajectory through it, the GRID is the chart you read against, and you MEASURE to define the relation.

Two naming systems now coexist and both are recorded (this file + ux_plan.md):
- INTERACTION vocab (how you manipulate): HOLD (depth) / SCRUB (value) / SELECT (kind).
- PIPELINE vocab (what each stage does): express/project/beam/grid/measure → structure/interpretation/
  trajectory/chart/relation.

### STATE NOW
- Active = instrument_ux.html. UX LOCKED: five-group pipeline, lodzone hold-disclosure (desktop+mobile),
  parameterized projection (adaptive tier 2), generic working steppers, dual measurement readout, full-state
  readout in MEASURE tier 3, info-panel stub, finalized vocabulary. Verified: parses, no dup ids, all JS ids
  resolve, construction UNTOUCHED + verified throughout.
- instrument.html = unchanged pre-UX fallback (locked _REFERENCE_preUX).

### ═══ NEXT PATH (re-charted; agreed order A → D → B4) ═══
**A. Finish + promote the UX branch (nearly done):**
  - Add the projection TYPES that earn their place (each must reveal a DIFFERENT invariant, not just look
    different): ★ FISHEYE / equidistant (radius ∝ angle — a radial invariant, suits the form's radial/shell
    structure, natural partner to the log-polar grid) is the strongest add. GNOMONIC (project from sphere
    CENTER → straightens great circles = the rotational geodesics) is the interesting-but-niche maybe.
    SKIP oblique (drafting shear, no new structure) and equal-area (form is a curve, not an area dist).
  - Optional minimal-row rendering (probably unnecessary — structure already achieves density).
  - DRIVE-TEST end to end → if good, PROMOTE instrument_ux.html to main instrument.html (lock current first).
**D. Investigate (high value, tools built, barely used):** drive the readouts at clean configs to test the
  parked questions — log-polar ring vs polar radius (k+1) self-similarity? frame convergence? VE major-axis
  angle parity flip?
**B4. Caliper RUNG 2** — grid-location targets, grid-coord-adaptive entry (the half-built measurement piece).
Then: Slice 4 (small-multiples), docs subsystem (populate stub, hard claims discipline), Slices 5/6/7.

---

## ★★ UX OFFICIALLY LOCKED — instrument_ux.html (2026-05-31, final UX session) ★★

The UX is DONE and officially locked. This batch (beyond the prior "UX LOCKED" checkpoint) added the state
system, the final Measurement tier organization, and the hold gesture model. Everything verified: parses,
no duplicate ids, all ids resolve, construction UNTOUCHED.

### ★ STATE SYSTEM (built + round-trip confirmed working by user)
Architecture = **controls are the single source of truth** (kills the hand-maintained-list problem that let
the log fall behind). Each scrub exposes `__key`/`__read`/`__apply` on its DOM element. `collectInputs()`
walks the five pipeline sections, derives the group from each section's label (DOM-derived — no per-control
annotation), and reads every scrub/select/checkbox. Adding a control later appears automatically in
capture/export/recall — ZERO sync. JSON shape:
  `{ meta:{t,level,cycle}, inputs:{express:{…},project:{…},beam:{…},grid:{…},measure:{…}}, outputs:{…} }`
- `inputs` keys ARE the control keys → self-describing, auto-grows.
- `outputs` = the rich computed measurement set (rOuter/rInner/holeRatio, COM, PCA, FA+Westin cl/cp/cs,
  VE-angle, caliper dist, feature angles) — for ANALYSIS/COMPARISON, never recalled.
- **NO backwards-compat / versioning until the schema locks** (user directive — keep it clean).
- **Capture** = controls→JSON. **Recall** = JSON→controls (`applyInputs` drives each control via __apply /
  set+change). RECALL CONFIRMED WORKING by the user.
- UI (MEASURE tier 1): **copy** = auto-copy JSON to clipboard (silent; red-flash if blocked/empty).
  **export** = download a timestamped .json file. **recall** = read JSON from the CLIPBOARD (copy a state →
  hit recall → restores; red-flash if clipboard empty/unreadable/invalid). **log** = capture a row (green
  flash). No paste box, no row counter — removed as chrome. Button feedback = green/red flash, no text.

### ★ MEASURE — final tier organization (3 tiers)
- **tier 1 (capture/identity):** freeze · step · level·cycle (live `#lvlCount`) · log · copy · export ·
  recall · clear · save image.
- **tier 2 (caliper):** caliper toggle + target select + caliper-resolution scrub, and the caliper readout
  (`#measPanel` = grid xy + grid-loc + per-grid naturals). Level·cycle removed from here.
- **tier 3 (full state):** the freeze-to-read full readout (`#panel`) — which INTERNALLY still leads with
  level·cycle (kept). The redundant standalone level·cycle line (`#bar`) was removed.
- Freeze opens MEASURE to full depth (reveals tier 3); resume returns to tier 1.

### ★ HOLD gesture model (clean 3-gesture separation)
- **click** = toggle fully collapse ↔ fully open (0 ↔ max). Standard/predictable.
- **Ctrl/Shift/Alt + click** = jump to a specific depth (tier 1/2/3, clamped to section max).
- **drag down** = progressive depth (scrub through tiers).
This keeps the scrub/hold modifier symmetry: on both primitives, MODIFIERS = "specific" (scrub: coarser value
jump; hold: jump to depth N). Bar tooltip documents all three gestures (set programmatically in initLodzone).

### PROJECTION (recap — done this session)
4 modes, with the two tunable ones parameterized: perspective→focal (was 480), stereographic→sphere R (was
320), in PROJECT tier 2, adaptive to active mode (`.projparam[data-mode]`, shown per frame). ortho/iso have
no depth param. Stepper-arrow bug fixed (generic: cycles the target select's own options, not RATIO_FLAT).

### ═══ MARKED FOR FUTURE DEVELOPMENT (noted, not built) ═══
- **PRESET SYSTEM** — recall-by-clipboard is the interim. A real preset system (named/saved states, a library,
  maybe load-from-file) is the future feature. The state JSON schema is the foundation it'll build on.
- **SCRUB FINE-TUNING** — the scrub interaction (drag sensitivity / fine-vs-coarse feel / log curves) could
  use another tuning pass. Functional now, but room to refine the feel.
- **DOCUMENTATION SUBSYSTEM** — still stubbed; populate into the full reference (own navigation, hard claims
  discipline: mechanism + provable math only).

### STATE NOW (UX locked)
- Active = instrument_ux.html. LOCKED. Five-group pipeline (express/project/beam/grid/measure → structure/
  interpretation/trajectory/chart/relation), lodzone hold-disclosure (3-gesture model, mobile-fixed),
  parameterized adaptive projection, generic steppers, self-growing JSON state system (capture/export/
  clipboard-recall, round-trip confirmed), dual measurement readout, finalized vocabulary. Verified: parses,
  no dup ids, all ids resolve, construction UNTOUCHED + verified throughout.
- instrument.html = unchanged pre-UX fallback (locked _REFERENCE_preUX).

### ═══ NEXT PATH (UX done → investigate → caliper rung 2) ═══
**PROMOTE:** lock instrument.html as `instrument_REFERENCE_preUX2` (or similar), then promote
instrument_ux.html → instrument.html as the new main. (Branch is done; do this when ready to make it primary.)
**D. INVESTIGATE (high value, tools built + state system now makes it easy):** drive the readouts at clean
configs, USE log/copy to capture comparison rows, test the parked questions — log-polar ring vs polar radius
(k+1) self-similarity? frame convergence at clean configs? VE major-axis angle parity flip (even=prolate/
odd=oblate)? The JSON capture makes systematic comparison across configs trivial now.
**B4. Caliper RUNG 2** — grid-location targets, grid-coord-adaptive entry.
Then: projection types (fisheye/equidistant — the radial-invariant add; gnomonic maybe), Slice 4 (small-
multiples), docs subsystem, Slices 5/6/7.
