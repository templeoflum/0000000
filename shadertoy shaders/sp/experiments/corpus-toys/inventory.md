# Corpus toy audit — 2026-09-09

Scope correction: intended sources are Memory Lattice / Mind Not Map toy factory. No further MET3OR conversion. This task only read sources and wrote this folder; no build, browser execution, installation, runtime operation, ledger reconciliation, or GPU inference.

## Ledger and mirrors

- Ledger arithmetic matches its rows: **147 rows = 99 confirmed + 33 queued + 9 pending + 5 fix + 1 rejected**. It contains **146 unique paths**.
- Canonical 122/toys shelf and `/Users/donovan/work/toys` each contain **113 distinct toy HTML files**, excluding signoff paperwork. All 113 matching files are byte-identical (SHA-256). No untracked toy HTML, missing mirror or differing mirror was found. `114` existing rows in JSON counts the duplicate twice.
- `the-slack` (operator confirmed, 20260712-145657) and `slack` (queued) both point to `slack.html`. This is a conflicting duplicate, not evidence of another unbuilt toy. Do not promote or delete either row automatically.
- The 32 other queued paths are absent; rejected `wagon-wheel` is absent. Every confirmed, pending and fix path exists. Pending and fix mean review remains outstanding even though bytes exist.
- Five operator fix rows: escapement (alignment/accuracy complaint), the-mirror (snapping back), same-point (no point to drag), two-clocks (bugginess/text overlap), the-wheel (text overlap). Full verbatim notes/timestamps remain in JSON.
- Later keeper atomicity audit at 20260713-102156 postdates ledger update 20260713-095403. Parsed body has **112 AUDIT rows: 47 pass, 65 fail**, rather than its approximate headline of 113 toys. `cast-and-spread` has no row. **51 ledger-confirmed toys have later atomicity fail verdicts.** Operator confirmation and keeper gate are separate facts; no statuses changed here.
- `toyreconcile.py` only adds new basenames and changes landed `in-progress` rows to pending. Its code neither removes duplicate paths nor ingests keeper failures; running it would not resolve these discrepancies. It was read, not run.

Machine evidence: [ledger-audit.json](ledger-audit.json) includes every ledger row, source/mirror paths and SHA-256, missing-file classifications, duplicate path and later audit comparison. [motion-geometry-candidates.json](motion-geometry-candidates.json) contains eight independent candidate reads and corpus links.

## Candidate decisions

The main task owns barberpole, stepping-feet and pinna-brelstaff. The following are additional candidates, not build approvals. Existing Smart Params would be the adjustable-control layer. Proof controls deliberately weaken/remove an illusion and must not be silently auto-modulated as if all settings preserve the illusion. Figure means a centered contained stimulus with external placement; Field may fill the frame.

### cafe-wall — Field

priority. Ledger: confirmed; later atomicity: pass.

**Invariant:** Horizontal row boundaries remain straight and parallel; alternating dark/light tiles and intermediate gray mortar create context.

**Adjustable:** Offset 0–50% of 88px tile, Home 50%; mortar 0–14px, Home 7. Tile row height 60; grayscale 20/235/128.

Alignment and zero-mortar endpoints are proof states, not failed renders. Do not animate actual row tilt.

[Toy source](/Users/donovan/work/0000000/mind not map/1.presence-minds-awareness/12.thought-grasps-sense/122.creativity-carries-potential/toys/cafe-wall.html) (lines 50–101); [corpus object](/Users/donovan/work/memory lattice/0/corpus/records/object.cafe-wall-illusion.f0.20260706-080000.md).

### fraser-spiral — Figure with contained checkerboard

priority. Ledger: confirmed; later atomicity: pass.

**Invariant:** Bar centers lie on five separate closed circles of radii 70/120/170/220/270; never replace them with a spiral path.

**Adjustable:** Twist 0–100 maps to 0–45° off tangent; trace 0–100 controls opacity of a dashed true circle at radius 220.

Keep checkerboard contextual ground (42px cells), two-tone 26×9 bars and proof circle. Normalized modulation may alter tilt but must not move bar centers off circles.

[Toy source](/Users/donovan/work/0000000/mind not map/1.presence-minds-awareness/12.thought-grasps-sense/122.creativity-carries-potential/toys/fraser-spiral.html) (lines 54–112); [corpus object](/Users/donovan/work/memory lattice/0/corpus/records/object.fraser-spiral-illusion.f0.20260706-080000.md).

### hering — Field (radiating context)

priority. Ledger: confirmed; later atomicity: pass.

**Invariant:** The two test lines stay exactly straight and parallel; only the fan context changes.

**Adjustable:** Fan line count 12–180, Home 120; fan opacity 0–1, Home 1.

Fan extends beyond frame in the toy. For a Figure adaptation, contain the complete stimulus panel; do not crop away required context or curve the target lines.

[Toy source](/Users/donovan/work/0000000/mind not map/1.presence-minds-awareness/12.thought-grasps-sense/122.creativity-carries-potential/toys/hering.html) (lines 41–46, 67–94); [corpus object](/Users/donovan/work/memory lattice/0/corpus/records/object.hering-illusion.f0.20260706-080000.md).

### rotating-snakes — Figure

review source invariant before port. Ledger: confirmed; later atomicity: pass.

**Invariant:** The stimulus is physically stationary; perceived motion arises from asymmetric luminance ordering, not actual texture rotation.

**Adjustable:** Asymmetry 0–1 blends [18,242,18,242] toward [18,92,242,168]; fixation control is a boolean at >0.5.

Source comment at 75 claims alternate rings drift opposite, but (i+2)%4 is a cyclic phase shift, not reversal. M=round((ri+ro)*.16) gives 26,40,54,68 segments; two rings truncate the 4-step sequence at the seam. Preserve and flag actual construction; do not silently claim verified opposite drift.

[Toy source](/Users/donovan/work/0000000/mind not map/1.presence-minds-awareness/12.thought-grasps-sense/122.creativity-carries-potential/toys/rotating-snakes.html) (lines 50–94); [corpus object](/Users/donovan/work/memory lattice/0/corpus/records/object.rotating-snakes-illusion.f0.20260706-080000.md).

### anorthoscope — Figure

candidate with explicit adaptation limits. Ledger: confirmed; later atomicity: pass.

**Invariant:** A fixed vertical slit reveals a moving fixed-shape five-point star; image integration is temporal.

**Adjustable:** Slit width 6–300px, Home 16; ghost 0–1 maps to 0–0.5 opacity of a stationary outline. Star radii 88/38.

Travel x=320−88+(timestamp_ms*.10 mod 176) resets every 1760ms; reset can be visible at wide slit. Corpus describes a rotating-disc apparatus; this HTML is a translating-star study, not an exact historical apparatus.

[Toy source](/Users/donovan/work/0000000/mind not map/1.presence-minds-awareness/12.thought-grasps-sense/122.creativity-carries-potential/toys/anorthoscope.html) (lines 51–103); [corpus object](/Users/donovan/work/memory lattice/0/corpus/records/object.anorthoscope.f0.20260706-080000.md).

### apparent-motion — Figure

timing-sensitive candidate. Ledger: confirmed; later atomicity: pass.

**Invariant:** Two fixed dot centers (210,175),(410,175), radius30. They alternate visibility, never interpolate position.

**Adjustable:** Rate 0–1 maps to full-cycle duration 1500−1280*rate ms; Home .8 yields 476ms. Both >.5 reveals both dots.

The Smart Param clock must determine event phase without physically sliding dots. Frame timing and perception need later render/audition validation.

[Toy source](/Users/donovan/work/0000000/mind not map/1.presence-minds-awareness/12.thought-grasps-sense/122.creativity-carries-potential/toys/apparent-motion.html) (lines 51–87); [corpus object](/Users/donovan/work/memory lattice/0/corpus/records/object.apparent-motion.f0.20260706-080000.md).

### line-motion — Figure

timing-sensitive; corpus citation conflict. Ledger: confirmed; later atomicity: pass.

**Invariant:** Cue precedes the whole line appearing at once. Never animate a growing line to simulate the effect.

**Adjustable:** Cue opacity 0–1, Home1; side switches left/right at .5. Fixed cycle1150ms: cue140ms, line720ms, blank290ms.

Object source list is empty. Keeper report flags attribution conflict (Neumann/Klotz vs Hikosaka); do not repeat attribution as verified. Timing ratios are source invariants until an explicitly reviewed adaptation changes them.

[Toy source](/Users/donovan/work/0000000/mind not map/1.presence-minds-awareness/12.thought-grasps-sense/122.creativity-carries-potential/toys/line-motion.html) (lines 51–95); [corpus object](/Users/donovan/work/memory lattice/0/corpus/records/object.line-motion-illusion.f0.20260706-080000.md).

### epicycles — Figure

defer: later atomicity audit fails. Ledger: confirmed; later atomicity: fail.

**Invariant:** Integer harmonic frequencies and target-specific Fourier coefficients determine the same endpoint and plotted sum; no arbitrary independent orbit amplitudes if claiming that reconstruction.

**Adjustable:** Target square/saw/triangle; nonzero harmonic count1–12; phase sweep0–1; spin toggle. Coefficients are defined at lines78–80.

Toy has one slider plus six buttons; later keeper gate fails atomicity despite ledger confirmed. Corpus Fourier-series object is settled, but direct toy-to-record build provenance is not embedded; mapping follows the implemented formulas.

[Toy source](/Users/donovan/work/0000000/mind not map/1.presence-minds-awareness/12.thought-grasps-sense/122.creativity-carries-potential/toys/epicycles.html) (lines 75–112, 218–219); [corpus object](/Users/donovan/work/memory lattice/0/corpus/records/object.fourier-series.f0.20260614-140356.md).

## Provenance limits

The illusion object records above are `state: float`, `formalized: false` and explicitly describe thin stub intake. Their linked source records exist, but this audit did not independently verify the publications or the perceptual strength of the HTML. Line-motion has no linked source and a separate keeper report flags attribution conflict. Fourier-series is a fuller `state: settled` record. Candidate-to-record mappings are by matching name/mechanism/formula and local audit references; the toy HTML does not carry an embedded corpus record ID, so these are grounded links rather than a verified historical build chain.

Additional local evidence:

- `/Users/donovan/work/memory lattice/0/corpus/docs/audit.toy-atomicity.f0.20260713-102156.md`
- `/Users/donovan/work/memory lattice/0/corpus/records/draft.audit-toys-b2.apprentice.md` (epicycles/Fraser/line-motion source inventory)
- `/Users/donovan/work/memory lattice/0/corpus/docs/report.keeper-state.f0.20260712-053911.html` (line-motion attribution issue, line332)

Priority for a subsequent reviewed conversion: Café Wall or Fraser Spiral for straightforward geometry and explicit proof endpoints; Hering for a Field. Keep Rotating Snakes stationary and review its phase-shift comment; retain genuine event timing for Apparent Motion/Line Motion. Epicycles needs an atomicity decision before conversion. No replacement mechanisms have been invented.
