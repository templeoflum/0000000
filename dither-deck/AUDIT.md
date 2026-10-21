# the ontology audit — atoms, molecules, and the derivation architecture

read after VISION.md. this document classifies every shipped machine under the
law: **an atom is one equation family, one phenomenon, one honest k-axis. if it
does two things, it is a molecule. molecules are derived from atoms by
reference, never by copy.**

## the classification rule

for each machine: what is the equation? what is k? one phenomenon or a
portfolio? three verdicts:

- **ATOM** — one equation, one physical k. keep.
- **BOND-IN-ATOM-CLOTHING** — multiple mechanisms, configs, or regimes stitched
  by dissolve. recast or retire.
- **DUPLICATE TERRITORY** — slider held, it answers to the same name as another
  machine. one of them is wrong (the one law of feel, applied deck-wide).

---

## atoms

| atom | equation | k-axis | verdict |
|---|---|---|---|
| S01 | anchored block-pyramid coarsening | condensation level | **ATOM** — the foundational operator |
| S02 | percentile-conservation law, 4 waypoint landscapes | landscape morph | **ATOM, grandfathered** — the constitution itself; note it is the only permitted multi-waypoint atom, because the journey *is* the law demonstrating itself |
| S03 | randomness-character morph, median-pinned | spectral character | **ATOM** |
| S04 | fixed-anchor ancestor-tree dot coalescence | coalescence level | **ATOM** |
| S05 | the rising floor | floor height | **ATOM** |
| S06 | stroke-direction comb toward a *hidden form* | comb amount | **BORDERLINE** — "hidden figure" is figure×ground, which is bond territory (M2, M4 live there). either S06 drops the hidden form (pure stroke-field atom) or it is a molecule |
| S07 | **two** rulings tilted apart, beat Λ=p/2sin(θ/2) | detune angle | **BOND-IN-ATOM-CLOTHING** — two screens bonded is a bond. also DUPLICATE TERRITORY with M6 and S22 (all three are the detuned-pair beat) |
| S08 | leaky error carry on the route family | route fold depth | **ATOM** — the soil |
| S09 | Floyd–Steinberg on the same route ladder | route | **ATOM** — sibling of 08 by design, documented |
| S10 | Bayer nest levels + one blue-noise stop | nest level | **ATOM, noted** — its final stop is a miniature bond ("the two great screen families meeting" — its own header confesses) |
| S11 | AM press dot, in-place subdivision | ruling | **ATOM** — pure AM |
| S12 | potential flow past cylinder + circulation | Γ̃ | **ATOM in structure, WRONG PHENOMENON** — level sets of Ψ can never end (no minutiae possible) and bunch with flow speed (real prints hold constant pitch). **REBUILD on the zero-pole orientation-field model** (Sherlock–Monro 1993; Vizcaya–Gerhardt 1996): singularities = cores/deltas, phase dislocations = endings/bifurcations, k moves singularities through arch→loop→whorl |
| S13 | Gray–Scott, Pearson spot regime | time | **ATOM** — k is one physical parameter of one integrator. the portfolio-that-isn't |
| S16 | Barkley excitable medium | **configuration index** (6 frozen seeds, dissolve) | **BOND-IN-ATOM-CLOTHING** — one equation but six unrelated seeds; k is not a physical parameter. honest path exists: integrate the medium *between* states (wave death/birth are Barkley dynamics). rebuild transitions or demote |
| S20 | Worley F1/F2−F1 | **three mechanisms** (metric morph, rank blend, anneal) | **BOND-IN-ATOM-CLOTHING** + felt verdict "parlor trick". recast as pure crystallization kinetics (colliding growth fronts ARE Worley; walls→honeycomb is grain annealing) or retire |
| S21 | two-source interference, a(r)=√(λ/(r+r₀)) | source separation | **ATOM** — the cleanest of the new batch. degrain (bigger λ) |
| S22 | **two** AM screens detuned + **third** screen fades in | detune + trio weight | **BOND-IN-ATOM-CLOTHING** (two mechanisms) + DUPLICATE TERRITORY (S07, M6). recast as the deck's single screen-clash molecule: S11×S11 |
| S23 | **five** wave regimes amplitude-crossfaded | regime index | **BOND-IN-ATOM-CLOTHING** — a portfolio machine; its two-source states collide with S21, its checker-moiré with S22. rebuild as one identity or retire |

## molecules

| mol | bond | verdict |
|---|---|---|
| M1 | S04×S05 on a tone ramp | **TRUE BOND** — keep (the ramp is presentation, not a third machine) |
| M2 | S01×S03 — hidden figure as texture difference | **TRUE BOND** — keep |
| M3 | S08×S05, survivors spend the dead's ink | **TRUE BOND** — keep |
| M4 v4/v5 | S06×S05, engraver's floor (refusal vs compliance) | **TRUE BOND** — keep both versions |
| M5 v6/v7 | S01 pyramid × 4 screen families melting to one floor | **TRUE BOND, heavy** — a four-family melt; v6/v7 differ only in floor mask. keep as versions |
| M6 | S07×S02 detune on the lattice | **DUPLICATE TERRITORY** — S22 does this journey richer (dot gain, argyle, third screen). **RETIRE TO FOSSILS** |
| M7 | S08×S09 error-memory graph | **THE TEMPLATE** — two certified parents, one axis, documented correction. this is what every bond should look like |
| M8 | S12×S13 advected Gray–Scott | **TRUE BOND, two repairs**: (1) the white core disc blanks the typhoon's eye — shrink R, render core as ink; (2) parents are hand-*copied*, not derived — must be rebuilt on the bond surface |
| M9 | S10×S11 rank-field morph (AM/FM axis) | **TRUE BOND** — certified, exemplary |

## territory map (the bleed, named)

- **screen moiré / detuned-pair beat**: S07, M6, S22 — *three* machines, one
  phenomenon. ruling: ONE molecule owns it (S22 recast as S11×S11); S07 recast
  or retired; M6 fossilized.
- **hidden figure**: S06 (solo), M2, M4 — figure×ground is bond territory by
  definition. S06 must choose.
- **two-source interference**: S21 (pure), S23's ripple/herringbone states —
  S23 must drop them or drop out.
- **the dissolve portfolio**: S02 (grandfathered), S16, S20, S23, M5 — the
  "journey" is a legitimate *form*, but only as a molecule whose stages are
  declared parents. an atom's k is one physical parameter. S13 (time) and S21
  (separation) are the proof it can be done.

---

## the derivation architecture (builder v2)

today every molecule contains a hand-copied re-implementation of its parents'
math. drift is guaranteed; atom fixes do not propagate. the redesign:

**1. atom contract v2 — the bond surface.**
each atom's machine fragment additionally exposes named internals:

```
window.ATOM_EXPORT = {
  name: "S13",
  landscape(k)  -> Float32Array,   // the pre-threshold field at k
  cut(F, tone)  -> Uint8Array,     // its conservation cut (02's, or its own law)
  internals: { ... }               // machine-specific bond surface
}
```

examples: S12 exports `velocity(x,y)` and `psi field`; S13 exports
`integrator` (step function + u/v fields + regime params); S08/S09 export
`walk(route)` and the error state; S02 exports `conservationCut`.

**2. bonds are declarations, not machines.**
a bond file contains ONLY: parents, the coupling axis, and the journey:

```
/*@BOND parents:[S12,S13] axis:"advection coupling c" needs:[S12.velocity, S13.integrator]*/
// journey: c = k·0.45, 13 stops, blue-noise dissolve (from S08's export)
```

the builder splices parent fragments into a shared scope, then the bond code.
**edit an atom → rebuild → every bonded molecule inherits the change.** fix
S12's math and M8's river gets the new field for free.

**3. mechanical overlap lint.**
at build time: two bonds with the same parent set + axis = error. an "atom"
whose fragment references another atom's export = flagged as molecule. the
audit becomes enforceable, not aspirational.

**4. standalone pages still emit.**
the builder wraps each molecule in the rail boilerplate as today, so every
molecule still opens solo. fossils stay fossils (excluded from manifest).

## the rebuild queue (in felt-need order)

1. **S12** — zero-pole orientation-field rebuild (the flagship's math is wrong)
2. **M8** — core fix + first derivation-surface consumer (proves builder v2)
3. **screen-moiré unification** — S22→molecule, S07 ruling, M6 fossilized
4. **S16** — integrated trajectories between states, or demote
5. **S23** — one wave identity, or retire
6. **S20** — crystallization-kinetics recast, or retire
7. **S21** — degrain (bigger λ)
8. **S18** — rebuild per lab/18/FINDINGS.md prescription (stops + tie-break)

*audit basis: every shipped machine's header read in full, 2026-07-24.
classification is argument, not verdict — the owner's eye rules.*
