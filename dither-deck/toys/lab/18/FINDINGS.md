# S18 "DEEP MASK" — certification report: RETURNED TO LAB

**Verdict: FAIL as shipped. Concept is alive; the machine needs a rebuild, not a patch.**

## what it is

One binary mask (136² torus, 45% ink) converged by Ulichney's void-and-cluster
(verified local optimum). The knob is the Gaussian scale-space of that mask:
`F = G_sigma * P`, sigma = 7·k², tiled 5×5 to 680², thresholded at the 45th
percentile per frame. Journey: circuit maze → melting curds → coral →
cow hide → world map.

## measured at certification (headless node harness, 200-step sweep)

- ink: **0.364 – 0.549** (law: pinned at stated tone 0.45)
- worst flip: **17.24%** per 1/200 step at k≈0.68 (law: ≤ ~2.5%)
- apply ≈ 6.6 ms (fine); load 131 ms (fine)

## diagnosis (two independent failures)

1. **Tie disease kills the percentile cut at the extremes.**
   At k=0 the landscape takes exactly two values (the raw mask's 0/1), and the
   45th-percentile cut lands wherever the bin edge falls: ink 0.4075, not 0.45.
   At k→1 the blurred field collapses toward its mean and huge pixel masses
   share a handful of values; the cut again lands off-target: ink 0.5366–0.5493.
   Mid-journey (σ moderate, values smooth) ink is fine: 0.4421–0.4493.
   *The same disease S21 had, terminal here instead of mild.*

2. **Scale-space morphing pours.** At σ mid-range the landscape's contrast is
   low and wide regions sit within ε of the threshold; a 1/200 k-step (Δσ small
   but global) crosses 17% of the field. No remap can fix this: the metamorphosis
   is intrinsically fast in the middle of the rail.

## prescription (for whoever rebuilds it)

- Quantize σ to ~8–10 stops; precompute each stop's thresholded bit-field with
  a **blue-noise tie-break** poured into the field before the cut (the fix that
  saved S21: `F += (BN−½)·binwidth`, then interpolate the cut inside the target
  bin — ink becomes exactly 0.45 even with tie masses).
- Dissolve between stops in blue-noise order (S13/S21 pattern). Per-step flip
  then ≈ stop-to-stop difference / steps-per-interval — engineer the σ ladder
  so that ratio ≤ 2%. Expect the ladder to be non-uniform (dense at mid-σ).
- **Open feel question:** k=0 (raw mask) reads as fine static at display size —
  possible collision with S08's floor. The rebuild should consider starting the
  journey at the curds state, or making the raw-mask state visibly a *circuit
  maze* at display scale. Judge with the slider held against S08.

## assets

- `mask_forced.png`, `final_k*.png`, `journey_k*.png` — the eye-test states
- `verify_vc2.py` — the void-and-cluster optimality check (this part passed)
- `granularity.py`, `build18.py`, `diag.js` — prototype tooling

The mask itself is good. The scale-space idea is good. The threshold-and-pour
engineering is what failed — and the deck already owns the cure.
