# S20 "the cell" — certification report: PASS (after one repair)

**Verdict: earns its place. Failed granularity on arrival; fixed at certification
by rebalancing the rail, not touching a single state.**

## identity

Worley's 1996 basis functions on a jittered hexagonal lattice (spacing 34 px,
jitter 0.36·s). Two nearest sites under a Minkowski metric d=(|dx|^m+|dy|^m)^{1/m};
feature distances F1 (cell body) and W=F2−F1 (cell wall). Four regimes:
pebbles→diamonds (m:2→1) → diamonds→tiles (m:1→16≈L∞) → walls grow
(rank-space blend R(F1)→R(W)) → crystallization (jittered→bare hex, m:16→2).

## measured at certification (headless node, 200-step sweep)

As arrived: ink 0.442–0.454 ✓ but worst flip **3.77%** at k≈0.92 ✗.
**Repair:** the crystallization lerp was compressed into k∈[0.90,1.00]. A
smoothstep ease was tried first and *rejected by measurement* (4.47% — it
slowed the ends but the underlying pour rate peaks mid-lerp). The boundary
moved to k=0.82 instead: walls segment tightens slightly, crystallization
breathes over 1.8× the rail.

After repair: ink 0.4418 – 0.4546; worst flip **2.33%** at k=0.705 ✓;
apply ≈ 4.6 ms; load ≈ 4 s (field precompute).

## eye test (lab/20/k*.png montage)

Distinct and nameable at every regime: pebbles, diamonds, mosaic tiles,
craquelure, perfect honeycomb. Mild watch-item: the two metric-morph segments
(k 0–0.4) are the same-y part of the journey — dots changing shape. The
back half (walls → honeycomb) is where the toy earns its keep.

## deviations (documented in the toy header)

- ±0.5% ink wobble from histogram bin quantization — same family as M9's
  documented 0.448–0.454 drift.
- Rail boundary 0.90→0.82 recorded in both the header journey table and the
  inline comment at the segment.

Prototype PNGs (`k*.png`, `h*.png` = holdout variants) in this folder.
