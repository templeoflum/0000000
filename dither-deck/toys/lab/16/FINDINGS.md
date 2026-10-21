# S16 "the excitable medium" — certification report: PASS

**Verdict: earns its place. Cleanest of the 2024 batch — passed every gate first try.**

## identity

The other reaction-diffusion family: the Barkley model of an excitable medium
(Barkley 1991, Physica D 49:61–70) — spiral-wave equations of cardiac tissue
and the BZ reaction. ∂u = ∇²u + (1/ε)u(1−u)(u−(v+b)/a), ∂v = u−v; a=0.75,
b=0.02, ε=0.02, dt=0.1, explicit Euler, 5-point Laplacian, periodic, 340².
The knob travels six **frozen** honest states: targets → ripple → pinwheel →
carousel → fiddleheads → worms (meander-breakup debris, a=0.9 b=0.1 regime).

## measured at certification (headless node, 200-step sweep)

- ink: 0.4448 – 0.4510 (45th-percentile cut of F=1−u per frame)
- worst flip: **1.33%** per 1/200 step (law ≤ 2.5%)
- apply ≈ 0.74 ms; load 9 ms (frames precomputed offline, embedded)
- contract: `let k=0`, `function apply(`, rail cut-point, `window.atom` "S16", node --check clean

## eye test (lab/16/montage_states.png)

Six unmistakably distinct, nameable states. Concentric BZ rings, two-pacemaker
interference ("an owl"), single spiral, 2×2 chirality-alternating spiral lattice,
4×4 small curls, wave-debris cuneiform. Nothing else in the deck owns spirals.

## notes / deviations

- States are precomputed frozen frames, not live integration (S13's precedent).
- Watch item for deck integration: S16's first two states (rings, two-source
  ripple) are *cousins* of S21's tank states. The journeys diverge hard after
  that (spirals/lattices/debris vs ripple-tank separations), so both can ship —
  but compare with the slider held at k≈0.1–0.2 before final deck assembly.
- near-threshold speckle on trailing wave edges is the honest field, documented
  in the toy header.

Prototype tooling and regime search PNGs in this folder (`brk_*.png`,
`meander_*.png`, `F_*_wave.png` raw fields vs `F_*_p45.png` thresholded states).
