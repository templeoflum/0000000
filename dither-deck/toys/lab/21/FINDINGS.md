# S21 "the tank" — certification report: PASS (after one repair)

**Verdict: earns its place. Failed ink conservation on arrival; fixed at
certification with the deck's own blue-noise tie-break.**

## identity

The ripple-tank photograph, computed: two coherent in-phase point sources with
honest cylindrical spreading a(r)=√(λ/(r+r₀)) (energy flux constant → 1/√r),
ψ = a(r₁)cos(2πr₁/λ) + a(r₂)cos(2πr₂/λ). The knob is source separation in
wavelengths, quantized to 8 stops {0, 0.6, 1.2, 2, 3, 4.5, 6.5, 10}λ because
moving a source rephases the whole field (S12's reason); blue-noise dissolve
between stops (08's law). Bonus phenomenon: from d≈3λ the field is
unmistakably a face — pareidolia out of two cosines.

## measured at certification (headless node, 200-step sweep)

As arrived: worst flip 2.34% ✓ but ink **0.4319 – 0.4481** ✗ — the ring
crests pile whole wavebands inside single histogram bins, so the bin-edge cut
landed below the 45th percentile (tie disease, mild strain).
**Repair:** pour one bin-width of blue-noise rank into the field before the
histogram (02's jitter law) and interpolate the cut *inside* the target bin.
One localized change inside `stopField()`, documented inline.

After repair: stops exact at **0.4490 – 0.4501**; full sweep 0.4467 – 0.4527
(residual ±0.3% lives only in dissolve midpoints — inherent to pixel-swap
tweens when the rephase zone's black fractions differ between stops; same
structure as S13/M8's accepted wobble); worst flip **2.35%** ✓;
apply ≈ 3.6 ms; load ≈ 3.9 s (8 stop-fields at 680²).

## eye test (lab/21/montage3.png)

Bullseye → pinch → eye → two eyes → opening fan → wide fan → standing lattice.
The dashed-ring texture (thresholded crests/troughs) is distinct from S16's
organic BZ rings, but the k≤0.2 states are cousins — compare with the slider
held before deck assembly.

## deviations

- ±0.3% ink wobble at dissolve midpoints (documented above and here).
- λ=24 px, r₀=λ source softening; stops quantized per the granularity law.

Prototype PNGs (`p2_*`, `p3_*`, `final_*`, `decay_*`) and `check21.js` in this folder.
