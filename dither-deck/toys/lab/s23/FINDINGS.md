# S23 — SHIMMER (findings)

**Identity:** one wave machine — every state is an honest superposition of
plane / spherical waves, thresholded at the per-frame 45th percentile; the
slider crossfades regime *amplitudes*, which is itself wave superposition,
so even the transitions are physics.

## Maths

Five waypoint landscapes on the 680² canvas, all cosine wave fields:

| k | state | field | regime |
|---|-------|-------|--------|
| 0.00 | BEATS | cos k(x·c+y·s) + cos k(x·c−y·s), λ=26, θ=±3.5° | two detuned plane waves; beat period λ/(2 sin 3.5°) ≈ 213 px → three envelope bands |
| 0.25 | ZONE PLATE | cos(πr²/ρ²), ρ=80 | paraxial spherical wave section (Fresnel chirp); edge pitch ρ²/r ≈ 19 px, 9 cycles |
| 0.50 | RIPPLE TANK | cos(2πr₁/λ)+cos(2πr₂/λ), sources at (340±130, 340), λ=22 | textbook two-source interference, sources inside field |
| 0.75 | HERRINGBONE | same equation, sources at (340±140, −580), λ=26 | far regime: hyperbolae straighten into a nested chevron fan |
| 1.00 | CHECKER MOIRÉ | cos kx + cos ky + cos kx′ + cos ky′, λ=26, rotation 8° | two square lattices; moiré cell λ/(2 sin 4°) ≈ 186 px |

Traversal: F = (1−t)·Lᵢ + t·Lᵢ₊₁, threshold at exact 45th percentile
(histogram technique from 02.html). No stops, no blue-noise mask — the
blend pours the morph through the landscape's own valleys.

## The k-journey (named states)

- **k=0** — "the tide": vertical stripe carrier crossed by three slow
  horizontal beat bands. Implied motion: strong (water).
- **k=0.25** — "the bullseye": clean Fresnel zone plate.
- **k=0.5** — "two stones": classic ripple-tank photograph — two ring
  systems + hyperbolic fringe lattice between them.
- **k=0.75** — "the feather": herringbone / chevron fan opening downward.
- **k=1** — "the baskets": checker moiré of woven diamond tiles.
- Mid-states (0.125, 0.375, 0.625, 0.875) read as genuine hologram
  fringes — rings sheared by carrier waves, wavy fans, laced tiles —
  reaction, not mush. Verified visually (f680_*.png, v2_*.png).

## Measurements

- Ink coverage: 0.4500 at every sampled k (numpy, quantile threshold);
  JS histogram-threshold run: 0.4495–0.4516 across the 200-step sweep
  (same bin-quantization behaviour as 02).
- Worst flip per 1/200 k-step: **1.84 %** (numpy, step 24; JS, step 23 —
  beats→zone-plate seam). Under the 2.5 % law.
- Performance: precompute ≈ 2 s of trig at load (five 680² landscapes);
  apply() ≈ 5 ms per slider move (node, headless).

## Deviations

None from 02's law. Ink law is the standard 0.45. No mask embedded.

## Dead ends

1. Beat detune 2.5°: only ~1.2 bands across the canvas — read as
   "stripes with a fault line", not beats. Fixed at 7° (three bands).
2. Three-wave 120° hex lattice state: pretty, but thresholds into a
   uniform dot grid — too close to the SCREENS direction and to a plain
   halftone; killed by the one-law-of-feel, replaced by the herringbone
   (far-regime two-source interference), which is unmistakable.

## Verdict

Earns its place. Five nameable, mutually distinct states; the static
1-bit fields genuinely imply motion (beats read as tide, chevrons as
flow, zone plate as a lens breathing). All numbers inside the laws, and
the machine is one idea stated once: add waves, pin the ink.
