# M8 — findings

**Machine:** molecule M8 — "the reaction in the river" (bond of S12 × S13).
**Identity, one line:** Gray–Scott's coat advected by the potential-flow field
past a cylinder with circulation — the substrate gel-immobilized, the activator
combed downstream; k is the coupling strength c.

## the maths

- **Reaction (S13's certified machine):** Gray–Scott, Du=0.21, Dv=0.105,
  F=0.0545, kill=0.062 (Pearson 1993 spot regime), nine-point Laplacian
  (0.2 orthogonal / 0.05 diagonal), dt=1 explicit Euler, periodic edges,
  224² lattice, seeded with 8% static (u=v=0.5 in 8% of cells, seed 42).
- **Flow (S12's field, fixed):** potential flow past a cylinder,
  U=1, R=110 device px ≈ 36.2 cells, circulation Γ̃=0.6, vertical stream
  (α=−π/2). Velocity from the polar form
  v_r = U cos(θ−α)(1−R²/r²), v_θ = −U sin(θ−α)(1+R²/r²) + Γ/(2πr),
  Γ = Γ̃·4πUR. The cylinder is solid: no reaction inside r<R.
- **The bond:** advection of the activator only,
  ∂v = Dv∇²v + uv² − (F+k)v − c·(w·∇v), first-order upwind, while ∂u
  carries no advection term — the CIMA gel-reactor arrangement (one species
  bound to the matrix, one free to flow). The knob is c ∈ [0, 0.45].
- **Stops:** 13, c = 0, .025, .05, .075, .10, .13, .16, .20, .24, .28, .33,
  .39, .45; t=520 for c=0 (S13's mature-coat time), t=700 otherwise.
  Frames precomputed offline, bitpacked MSB-first base64 (S13's precedent);
  between stops, 08's blue-noise dissolve.

## the k-journey (named states)

- **k=0 (c=0):** the coat — isotropic Gray–Scott texture around the white
  disc of the solid core (same machine and regime as S13, sibling
  realization: different seed, plus the core).
- **k≈0.25 (c≈0.05–0.08):** the worm tide — spots connect downstream into
  worms and maze fragments visibly bowing around the core.
- **k≈0.5 (c≈0.13–0.16):** the gathering storm — worms lock into
  reaction-wave ridges combed along the streamlines.
- **k≈0.75 (c≈0.24–0.28):** the typhoon — long bold ridges winding around
  the eye of the circulation.
- **k=1 (c=0.45):** the gale with static islands — maximal swirl, and the
  fingerprint's deltas appear as fine-grain checkerboard patches where the
  flow stalls and the reaction returns to TV static.

Neither parent shows these states: S12's ridges are smooth constructions of
cos(2πΨ/P); M8's are born of the reaction and break, fork, and wobble.
S13's coat is isotropic; M8's is combed by the river. (Weakest transition:
k=0.5 → 0.75 is "the storm tightens" — same family, growing wavelength.
Recorded honestly; every other boundary crosses a named territory.)

## measured laws

- **Ink:** S13's coat law, inherited and declared in the header — each frame
  cut at the 74th percentile of the activator field, cover 0.26.
  Offline: 0.2600 at all 13 stops. In-browser (playwright, canvas pixels):
  0.2597–0.2605 across k = 0, .25, .5, .75, 1.
- **Granularity:** worst flip per 1/200 k-step = 0.0236 offline on the
  1-bit frames; **0.0242** measured end-to-end in chromium over the full
  200-step sweep (limit ~0.025). Poured in blue-noise order.
- **Static states:** frames frozen at fixed (c, t); the knob only dissolves.

## performance

apply() is a 224² (50 176 px) dissolve loop — instant. Load unpacks 13
bitpacked frames (106 KB base64 total) — instant. File size 155 KB.

## deviations (all in the header)

1. |w| capped at 2.2 cells/step (raw peak 3.17 on the core's skin) so the
   upwind CFL ≤ 1 at c=0.45 (0.99 measured); only the thin fast layer near
   the surface is touched.
2. Frames embedded, not integrated in the browser (S13's precedent: the
   integration cannot run inside an instant switch).
3. Grain 224→680 ≈ 3 device px per cell (S13 uses 2 px at 340²).
4. The c=0 anchor is a sibling realization of S13's coat, not a pixel copy:
   same equations, regime, and seeding recipe; different seed, plus the
   solid core.

## dead ends

- **Advecting both species:** the flow washes activator *and substrate*
  downstream; the upstream half of the field goes permanently barren
  (block-ink min 0.00 at c≥0.16, t=520 and t=1500 alike). A dying pattern,
  not a state. Killed after four renders.
- **Couple-after-birth** (grow the coat pure, then switch the flow on):
  same wash-out, one transit time later. Killed.
- The gel-immobilized substrate (activator-only advection) is what let the
  coat survive the river — and it is the physically honest arrangement
  (CIMA-class gel reactors immobilize one species).

## felt verdict

Earns its place. The bond is bonding: five named states, neither parent
shows them, both laws measured green end-to-end, and the k=0.75 typhoon is
a state I have not seen anywhere else in the deck. The checkerboard delta
patches at k=1 are the honest signature of stagnation — keep them.

## files

- `toys/m8.html` — the toy (155 KB, standalone, contract-verified:
  `let k=0`, `function apply(`, rail cut point, `window.atom` name "M8",
  02.html tail verbatim, node syntax-checked).
- `lab/m8/proto*.py`, `final.py` — offline prototypes and the final ladder.
- `lab/m8/build_m8.py` — assembler (S13 plumbing + 02 rail/tail + frames).
- `lab/m8/verify.py` — playwright harness (ink + 200-step sweep + shots).
- `lab/m8/F_*.png`, `web_k*.png`, `journey*.png` — the eye-test renders.
- NOT done (parent's call): adding "m8" to MANIFEST_MOLS in build_deck.py
  and rebuilding the deck — the assignment forbids me to touch those files.
