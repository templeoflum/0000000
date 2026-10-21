# TS (Trajectoscope) — Cold-Start Development Brief

> **Purpose:** a fresh session with NO memory, handed only (a) the toy-catalog entry and (b) this brief, should
> be able to resume the TS project correctly. TS is large and has many files + plans + a long findings record,
> so this brief is a FRONT DOOR: it orients, states the thesis, separates verified from open, names the one big
> risk, and points to where the real detail lives. It does NOT duplicate the detail docs — read them. Everything
> here is grounded in the actual files in this directory (trust them over this summary). Written 2026-06-01.

---

## 0. WHAT TS IS (one paragraph)

TS (Trajectoscope) is a **standalone instrument-as-argument**: a tool that builds geometric forms by sweeping a
single trajectory through composed rotations + translations (epicycles in affine space — no pre-existing mesh),
measures their frame-free invariants, and uses those measurements to investigate a thesis about **what
dimension and identity actually are.** It grew out of toy **T8 (planes-not-axes rotation)** — the owner's
instinct that "dimension is rotational" (point→circle→sphere→torus by rotation) — and became its own project.
The deepest framing: *the instrument IS the thesis made testable.* It is NOT a research-mathematician's tool;
it's a synthesist's instrument for telling a **real cross-domain identity from a seductive false rhyme** (the
owner's recurring north star).

---

## 1. THE THESIS (★ WORKING HYPOTHESIS — NOT verified; the work leads, not the claim)

Stated claim-free (this careful wording is load-bearing — do not let it drift into assertion):
- **Dimension is RELATIONAL, not intrinsic** — the count of independent references you can *verifiably relate* a
  frame-free structure to; a property of the relating, not the structure. "A cube is 3D" mistakes a measured
  relationship for an intrinsic attribute.
- **Renderings are INTERPRETATIONS, not shadows** — not lossless, but the apparatus MINIMIZES loss and
  ESTABLISHES EQUIVALENCE despite residual loss (which is why the instrument measures its own observed−true
  distortion — it quantifies its own lossiness).
- **Identity = the EQUIVALENCE CLASS across all grids & measurements** — NOT any formal dimension-count, because
  different FORMULAS can redefine the level/cycle count while reaching the same class. Invariants are
  DISCOVERED (what stays fixed across the apparatus), not pre-imposed.
- **The test of translation-vs-discovery:** name ONE distinction this framework makes that existing math
  provably can't. If none → it's a re-description (Fork A, fine). If one → it's discovery (Fork B). Held open.

**What's KEPT vs REJECTED** (hard-won, do not relitigate without cause): KEPT = the relationalist claim
(dimensionality carried by a process's relational structure, no higher embedding space needed); affine =
"no privileged frame," NOT "no dimension" (affine space HAS a definite dimension = the frame-free invariant).
REJECTED = "4D is a myth" (crank costume); dimension-as-coordinate-count as *identity*; sloppy dimensional
vocab ("shadow," "5D earth"). The spline/felt-sense intuition is real fluency in coupled RELATIONAL continuity
(high-dim in the relational sense), NOT perception of a 4th spatial axis — keep relational, not spatial.

---

## 2. CURRENT STATE (files + what's done — READ pipeline_state.md FIRST)

- **★ CURRENT WORKING FILE: `TS_formulas.html`** (~2845 lines). The expression-library arc: a pluggable formula
  bank (staged / freed / lissajous / torus / epicyclic) on the calibrated measurement spine, with the 4D camera
  gated to the staged construction only. Parses, 74 ids resolve. See `integration_plan_formulas.md`.
- **Frozen priors** (newest→oldest, each named for its WORK; the chain only GROWS):
  - `TS_fingerprint.html` — the calibrated fingerprint instrument (fingerprint slices F0/F1/F3/F2 done;
    fingerprint characterized + its blind spot found).
  - `TS_4D.html` — the verified genuinely-4D SE(4) instrument (5×5 construction, rotations in all six 4-space
    planes incl. XW/YW/ZW; 4D→3D camera).
  - `TS_3D.html` — the verified 3D keystone instrument.
  - earlier: `instrument_clean` → `instrument_ux` → `instrument` → proportional/ellipsoid/etc.
- **THE KEYSTONE (verified, unchanged throughout):** proportional.html's rule — each cycle = [rotate, rotate,
  translate], seed [D,0,0,(0,)1] (homogeneous), LEFT-multiplication, plane schedule SCHED cycling XY/YZ/XZ(/…),
  self-scaling displacement d = k·(k+1)^(C−1)·D (holds the central hole at a constant proportion; growth ×(k+1)
  per cycle). Measurement (analyzeLocus): WEYL-quasirandom sampling → PCA eigenvalues + rmin/rmax + COM.
- **THE FINGERPRINT (built + characterized this session):** a SHAPE signature = [normalized PCA eigenvalue
  ratios λ2/λ1, λ3/λ1, …, hole ratio rmin/rmax]. Scale-free, frame-free, dimension-general. It measures GROSS
  SHAPE (2nd moment) + RADIAL FILL, and is PROVABLY BLIND to higher-order ANGULAR/corner structure (confirmed:
  a smooth shell and 6 point-clusters at the same covariance+radius read as the same form). The blindness is
  SAFE for TS's own forms (connected dense fill → no independent angular structure) but real for arbitrary clouds.

---

## 3. WHAT'S VERIFIED vs OPEN (the honesty ledger — see findings.md for full detail)

**VERIFIED (safe to build on):**
- The SE(4) extension is genuinely 4D (the 4th-plane invariant is unreachable by a 3D schedule — falsification
  confirmed). 4D forms are the faithful analog of 3D (same alternating flat-torus/round-sphere by level parity).
- The fingerprint is a validated TOOL for gross-shape separation (fill-invariant; separates sphere/torus 0.87,
  k=2/k=4 0.28; trust gate passed at 245× between-class vs within-class).
- Self-scaling transfers to 4D exactly (growth ×(k+1), hole (k−1)/(k+1)) given adequate sampling (N≥16000 at
  high 4D levels — high 4D rmin undersamples below that).
- Every invariant found is a RATIO or COUNT, never an absolute (hole ratio, (k+1) growth, PCA shape ratios,
  period-2 parity, cycle count). Non-survivors are exactly the coordinate-dependent quantities.

**OPEN / NO claim verified:**
- ★ **The THESIS itself is unverified.** The formula-comparison test (F3) validated the tool and produced ONE
  data point (recipe pairs that read same-under-one-measure, different-under-another). The reading "identity is
  measurement-relative" is logged as INTERPRETATION, not result. One example ≠ general proof.
- **"Same form" is not single-valued** — surfaced (not resolved): same POINT-SET vs same DISTRIBUTION are
  different notions; the fingerprint uses distribution. Which one the thesis means is open (and the owner's
  stance, logged as interpretation: there's no privileged "same" — choosing the measurement IS the move).
- **Track A (dimensional climb to 5D/6D):** parked as a likely treadmill (machinery is dimension-general).
  Would USE the fingerprint to verify "N-D is faithful" rather than eyeball it.
- **Formula bank rate-dependence (just found):** a formula's fingerprint depends on the rate→axis assignment
  (torus reads differently under different ratios) — so viewer comparisons are of (formula + ratio), not pure
  formulas. Hold the rate fixed or note it.

---

## 4. THE PLANS (what's where — these hold the slice-level detail)

- **`pipeline_state.md`** — ★ THE CURRENT-STATE DOC. Lineage, naming convention, keystone, thesis, open
  questions. Has a "CURRENT STATE 2026-06-01" block at the thesis-priority section that supersedes older framing.
  READ THIS FIRST after this brief.
- **`integration_plan_formulas.md`** — the CURRENT arc (expression library): slices G0✅ G1✅ done, G2 (ratio
  library) next, then STOP and measure. Architecture decisions D1 (camera construction-specific), D2 (5D/6D
  parked), D3 (corner descriptor = next arc). Single-panel decided; split-view deferred.
- **`integration_plan_fingerprint.md`** — the fingerprint arc, COMPLETE (F0/F1/F3/F2 done; F4 heavier
  descriptors parked-but-trigger-now-demonstrable via the blind spot; F5 fingerprint-family parked).
- **`integration_plan.md`** — the ORIGINAL 3D-instrument arc, COMPLETE (archive).
- **`findings.md`** — the full chronological findings record (SE(4), fingerprint, blind spot, cube/expression-
  library, the audit pass). The detailed evidence. Long; read incrementally.
- **`apparatus_audit.md`** — the (rewritten) audit: the real gaps (A=fingerprint [done], B=ground-truth target
  invariant-sets, C=two-recipe comparator, D=reachability search, E=editable move-set) and the two-wings
  framing (coordinate-free invariant core = thesis wing; world-locked frame + angular reference = application
  wing).
- **`changelog.md`** — older history.

---

## 5. CONVENTIONS & METHOD (FOLLOW THESE — hard-won, the owner enforces them)

- **Validate after EVERY edit:** extract `<script>` body → `node -e "new Function(body)"` parses; sweep every
  `getElementById` ref resolves. Verify math HEADLESS before claiming behavior. present_files after edits.
- **Build ONE verified rung at a time.** State predictions BEFORE running tests; report negatives as results.
  Believe the empirical test over the elegant derivation. When you misread intent, REVERT cleanly.
- **★ DON'T OVERSELL** — the assistant has a CAUGHT, RECURRING pattern (this session ~6 times): builds a
  satisfying complete narrative, presents it with more confidence than the evidence carries; each caught by
  measurement or by the owner. The reliable fix: **measure the baseline you assumed instead of trusting it**,
  and **confirm the INPUT is what you think before concluding the TOOL/math failed.** "Absence of a
  counterexample ≠ proof of robustness" (there was a blind spot; it just hid in a corner). Mark interpretation
  as interpretation. Periodically audit the records for drift (claims harden as evidence advances and prose lags).
- **Naming/lineage (locked):** working file = `TS_<work>.html` named for the WORK; frozen priors KEEP their
  work-name (NOT "checkpoint" — that lives in pipeline_state). Linear chain, only grows. ADVANCE = copy current
  → new file. INVESTIGATE-IN-PLACE = headless sweeps (ephemeral scripts in /home/claude/), no advance.
- **Headless-first:** the construction math ports cleanly to Python (the rungs + fingerprint were all pinned
  headless before any viewer wiring). `fingerprint.py` + the build_form/expr_library scripts are the substrate.
- **Owner profile:** VJ/generative artist, self-taught, very visual, play-then-formalize. Goal = functional
  cross-domain depth + rigor-sense, employed creative-technologist lane, portfolio-first — NOT academia.
  Concise, honest, no preamble. Don't repeatedly say "good stopping point" — they return on their own.
- **Environment limits (not bugs):** screenshot-black on the pop-up browser (GPU compositing — felt/render
  behavior is only verifiable on the owner's real device); clipboard API can be blocked in webview (execCommand
  fallback exists in-file).

---

## 6. THE ONE BIG RISK

TS's thesis ("identity = equivalence-class of invariants; dimension is relational") is EXACTLY the kind of
satisfying cross-domain claim that is sometimes true and sometimes a seductive illusion — and the project's
whole point is to tell those apart. So the rigor bar on TS is: any claim that "two forms are the same" or "this
distinction is real" must be GROUNDED in a measurement, with the measurement's blind spots known, predictions
stated first, and negatives reported. The instrument is meant to be able to DISPROVE its own thesis — build
toward that, and want to know either way. The single most common failure mode (see §5) is crowning a satisfying
result before the evidence carries it; the single most common fix is measuring the baseline you assumed.

---

## 7. LINEAGE (where TS sits)

- Parent: **toy_catalog.md** — TS is a GROWN toy, descended from **T8 (planes-not-axes rotation)**, possibly
  drawing on **T4 (function/path as point)**. The catalog flags the exact origin as unconfirmed; a clean dev
  task is to pin it from the early transcripts. TS also collides with the entire new "Invariance, Measurement &
  Structure" track (T16 invariants, T17 lossy ruler, T18 sampling, T19 symmetry, T20 closure) — those five toys
  were essentially SURFACED by the TS work.
- Sibling grown project: **Spline Continuity** (`spline_continuity_v2.html` + its own brief) — the keystone toy,
  derivative-ladder continuity across mediums. Shares the owner, conventions, and "real vs false rhyme" north
  star; separate project. Both descend from the same 2022 origin vision.
- Deeper context (background, not front line): master_plan.md, session_log.md, and the transcripts in
  /mnt/transcripts/ (journal.txt catalogs them). The FRONT LINE is TS_formulas.html + the plans in §4 + this brief.

---

## 8. FIRST MOVES FOR A COLD SESSION (suggested)

1. Read this brief, then `pipeline_state.md`, then skim `integration_plan_formulas.md` (current arc) and the
   recent `findings.md` entries (fingerprint + blind spot + expression library).
2. Open `TS_formulas.html`; verify it parses + ids resolve (it should).
3. The current edge: `integration_plan_formulas.md` G2 (port the ratio library), then STOP and measure the
   formula bank live. Parked: corner/angular descriptor (the fingerprint's known blind spot — its trigger is now
   concrete), 5D/6D climb, split-view.
4. Honor §5 conventions and §6 risk throughout. Confirm any "result" against a measured baseline before claiming.

*This brief + pipeline_state.md + TS_formulas.html + the plans = the cold-start package. The detail lives in the
docs §4 points to; this is the door.*
