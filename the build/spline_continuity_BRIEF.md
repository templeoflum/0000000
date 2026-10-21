# Spline Continuity — Cold-Start Development Brief

> **Purpose of this doc:** a fresh session with NO memory, handed only (a) the toy-catalog entry and (b) this
> brief, should be able to pick up the Spline Continuity project and develop it correctly — knowing what exists,
> what's verified, what's open, the conventions, and the one big risk. Everything below is grounded in the actual
> files in this directory (read them; don't trust this summary over the code). Written 2026-06-01.

---

## 0. WHAT THIS PROJECT IS (one paragraph)

Spline Continuity is **the keystone toy** of a larger self-taught "synthesist" study — the project owner's OLDEST
intuition (from a 2022 oscilloscope meditation) made to meet the math most directly. The intuition: a *felt
break* — in a curve, a motion, a sound, a narrative, an emotion — is **one mathematical structure**, a
discontinuity at some order of the derivative ladder (C⁰ position / C¹ velocity / C² curvature / C³ jerk / …).
The toy makes that ladder VISIBLE and the claim TESTABLE: one spline drives many signals at once; break it at a
chosen order and watch the same break appear (or not) in every driven medium simultaneously. The deeper purpose
is QUALITY CONTROL on the whole synthesist project — the toy is how you tell a *real* cross-domain identity from
a seductive *false rhyme*. (That phrase, "real insight vs false rhyme," is the owner's recurring north star.)

---

## 1. WHAT ALREADY EXISTS (files — READ THESE FIRST)

- **`spline_continuity_v2.html`** (~1001 lines) — ★ THE CURRENT BUILD. Title: "Continuity across mediums — the
  derivative ladder." This is the developed version. It has:
  - Three spline MODES: `local spline` (piecewise, local control), `coupled spline`, `global polynomial`
    (one polynomial through all knots — sets up Runge's phenomenon).
  - A **derivative ladder** readout: shows f, f′, f″, f‴… and highlights exactly which order the break lives at.
  - **Driven domains** (one spline → real parameters, "every medium at once"): position, scale, rotation, skew
    (motion/transform family); hue, brightness, saturation, opacity (color family); plus DISCRETE **gates** (knot
    gate, peak gate at f′=0, zero-cross gate) — continuous curve → discrete events.
  - **Per-medium derivative picker** (`d:N`): choose WHICH derivative drives each medium. The key move — drive a
    medium with the order that's broken (e.g. f‴ on a C² spline) and the break JUMPS into that medium. This is
    the toy's sharpest teaching device: it shows a break is invisible until you look at (or drive from) the order
    it lives at.
  - **unipolar / bipolar** signal modes; **play** (animate the trajectory); **new shape** (randomize knots).
  - Runge's phenomenon deliberately reachable: crank the order way past where anyone bothers and the curve
    oscillates between knots — framed as "a texture, not just a cost."
  - Self-description: "Purely abstract, purely trajectory." (No audio in v2's visible domain list — see §3 gap.)
- **`spline_continuity_toy.html`** (~301 lines) — the ORIGINAL v1, simpler. One spline drives a curve, a ball's
  motion, and a TONE; toggle C⁰/C¹/C² and watch which break vanishes. v1 HAS the audio/tone domain that v2's
  domain grid doesn't foreground — worth checking whether v2 dropped audio or just relocated it. (Don't assume;
  diff the two.)

**Read both before developing.** v2 is the front line; v1 is the leaner original and the audio reference.

---

## 2. WHAT'S VERIFIED (confirmed findings — safe to build on)

From the project records (master_plan.md, session_log.md):
- The cross-domain claim is **CONFIRMED for curve + motion + tone**: the same continuity-order break is the same
  felt/seen/heard break across those three. The "aesthetic smoothness = C² judgment" reading held for them.
- The derivative-ladder framing works: a break at order n is invisible in derivatives < n and screams in
  derivative n. The per-medium driver picker demonstrates this directly and is the strongest part of the toy.

---

## 3. WHAT'S OPEN / THE GENUINELY-NEW QUESTION (where development should go)

- ★ **Narrative and emotion continuity is the OPEN question** — explicitly flagged as the genuinely-new part,
  NOT yet tested against the formalism. The visual/motion/perceptual domains are "known-and-formalizable"
  (splines drive parameters; standard). The hard, original claim is whether a felt break in NARRATIVE (a plot
  discontinuity, a tonal whiplash) or EMOTION (an affective jump) is *literally* the same C⁰/C¹/C² structure or
  only a metaphor. This is the part worth specialist conversation and the part most exposed to FALSE RHYME.
  Developing this honestly is the project's real frontier — and the place to be most rigorous about not
  overclaiming (see §5).
- **Gaps the toy could grow into** (candidate, not committed): a narrative/discourse domain driven by the spline
  (event ordering, pacing); an "emotion curve" domain; a side-by-side "is this break the same break?" comparator.

---

## 4. CONVENTIONS & METHOD (how this owner works — FOLLOW THESE)

These are hard-won disciplines from the broader project; a cold session must honor them:
- **Validate after every edit:** extract the `<script>` body and check it parses (`node -e "new Function(body)"`);
  sweep that every `getElementById` ref resolves to an `id`. Verify any math/behavior claim BEFORE asserting it.
- **Build ONE verified rung at a time.** State predictions BEFORE running a test; report negative results as
  results. Believe the empirical test over the elegant story.
- **Don't oversell.** The owner has repeatedly (and correctly) caught the assistant building a satisfying
  narrative ahead of the evidence. When you find a "result," check whether the INPUT was what you assumed before
  concluding anything. Mark interpretation as interpretation, fact as fact.
- **Naming/lineage (if this project adopts the TS convention):** working file named for the WORK; frozen priors
  keep their work-name (not "checkpoint"); "frozen" status lives in a state doc, not the filename. Advance =
  copy current → new file. (TS uses `TS_<work>.html`; spline could use `spline_<work>.html`.)
- **Tone:** the owner is very visual, self-taught, learns by play-then-formalize. Goal is *functional fluency +
  rigor-sense*, NOT research-mathematician depth. Concise, honest, no preamble. Don't repeatedly say "good
  stopping point" — they return on their own.
- **present_files after edits** so the owner can see the artifact.

---

## 5. THE ONE BIG RISK (read this twice)

This project is **the single most exposed to false rhyme** in the whole catalog, BY DESIGN — its entire thesis
is "these different-feeling breaks are the SAME structure," which is exactly the kind of satisfying cross-domain
claim that is sometimes true and sometimes a seductive illusion. The toy EXISTS to tell those apart. So when
developing — especially into narrative/emotion (§3) — the rigor bar is: can you point to an *actual formal
correspondence* (a real spline, a real derivative, a real discontinuity order), or are you pattern-matching a
metaphor? "Smooth narrative = C² narrative" must EARN the equals sign or be marked as analogy. The toy's own
"lies" line (from the catalog) applies to its development too: a clean cross-domain mapping is itself a
theoretical stance, not a fact. Build the thing that could DISPROVE the claim, and want to know either way.

---

## 6. LINEAGE (where this sits)

- Parent: **toy_catalog.md** — Spline Continuity is the "keystone" grown toy. Its original-domain toy is
  plausibly **T4 (function space as points)** or a continuity-specific sandbox; the catalog flags this as
  unconfirmed. NOTE: the catalog header earlier guessed spline = "felt-sense of high-dim relational continuity"
  — that was a memory-drift GUESS; the actual artifacts show it's the concrete C⁰/C¹/C² derivative-ladder toy
  described here. Trust the files. (A first dev task could be: pin which catalog toy this truly descends from.)
- Sibling grown project: **TS (Trajectoscope)** — the dimension/identity/fingerprint instrument (TS_formulas.html
  etc.), grown from T8. Shares the owner, the conventions, and the "real vs false rhyme" north star, but is a
  SEPARATE project with its own files and brief. Spline and TS both descend from the same 2022 origin vision
  (dimension-as-rotational + coupled planes + spline-continuity-as-cross-domain-truth) but are now distinct.
- Records to consult for deeper context: master_plan.md (the synthesist vision + why spline is the keystone),
  session_log.md (chronological build history). These are background, not the front line — the front line is
  the two HTML files and this brief.

---

## 7. FIRST MOVES FOR A COLD SESSION (suggested, not prescribed)

1. Open `spline_continuity_v2.html` and `spline_continuity_toy.html`; read what's actually there. Verify v2
   parses + ids resolve (it should — it's the working build).
2. Decide the development edge WITH the owner — most likely the narrative/emotion frontier (§3), which is the
   genuinely-new, expert-conversation-worthy part — and approach it with the false-rhyme rigor of §5.
3. If advancing the file, adopt the naming/lineage convention (§4) and a small state doc.

*This brief is the cold-start package. The two HTML files + the catalog entry + this doc = enough to resume.*
