# M9 — the AM/FM axis (bond of studies 11 and 10)

**One-line identity:** one ruling, one tone; the ORDER in which a cell's grains
are claimed as ink travels from radial-from-centre (11's clustered press dot)
to Bayer's recursive ranks (10's dispersed nest) — hybrid screening, built
honestly.

## Why this pair (the felt need)

Survey of atoms 01–11 against the shipped bonds (M1=04+05, M2=01+03, M3=08+05,
M4=06+05, M5=02+01, M6=07+02, M7=08+09): atoms **10 and 11 were the only
unbonded pair**, and they are the two great families of halftone craft —
clustered AM (the press dot) and dispersed ordered FM (the threshold nest).
The deck owns both as atoms and never says what lives between them. Real
printing lives exactly there (hybrid screening: AM skeleton, FM flesh). That
was the felt gap; the bond built itself once seen.

## The maths

- **Bond axis (the coupling):** rank-field morph, not texture morph. Every
  grain carries two uniformized ranks:
  - `Uam` — rank of squared distance from the cell centre within one 64 px
    cell (32×32 grains), ties falling to raster order. Thresholding `Uam` at
    0.45 IS 11's dot: dot area = tone by construction.
  - `Uby` — the 16² Bayer nest per cell, 10's own recursive construction
    (`B1=[[0,2],[3,1]]`, `B_{n+1}=4B_n+B1`), printed at 4 px blocks = 10's
    level-4 stop, unmagnified.
  - `U(w) = (1−w)·Uam + w·Uby`, thresholded at the exact 45th percentile of
    each frame (02's histogram pin). Ink never moves; only the fill order
    travels.
- **Field:** 680² px at 2 px grain (08's grain) → 340² grains. Cells tile with
  wrap — a press-sheet crop, 10⅝ cells across.
- **Calibration:** the raw w-sweep is visually uneven (the rich dissolve lives
  in w∈[0.1,0.7]); the rail is remapped through an **equal-visual-velocity**
  table: flip-rate profile measured at 401 w-samples, cumulative-inverted,
  33 knots embedded in the file (`WR`). After remap, k-quarter states land at
  w = 0, 0.252, 0.505, 0.714, 1 — the visually sweet spots.

## The k-journey (eye-certified at deck display size, 340 CSS px)

| k | w | state |
|---|---|---|
| 0 | 0 | **press dots** — bold round dots, 11's machine on a square lattice |
| 0.125 | 0.111 | **nibbled dots** |
| 0.25 | 0.252 | **moth-eaten dots** — the nest eating the rim |
| 0.375 | 0.407 | **granular rosettes** |
| 0.5 | 0.505 | **rosette stamps** — chunky ranked colonies; the hybrid-screen state |
| 0.625 | 0.609 | **dissolving colonies** |
| 0.75 | 0.714 | **twill** — the lattice ghost woven into the checker |
| 0.875 | 0.847 | **ghost lattice** |
| 1 | 1 | **the nest** — uniform ordered speckle, 10's 16² stop at print grain |

States verified distinct from each other AND from both parents: parent 10
shows nests only through its ×8 magnifier at multiple levels; parent 11 shows
round dots on a 45° diamond lattice at rulings 136→17. M9's k=0 is the only
parent-adjacent state (by design — the bond grammar, cf. M7's certified
endpoints), and its mid-states (moth-eaten dots, rosette stamps, twill) exist
in neither parent.

## Measured (headless node run of the shipped machine itself)

- **Ink:** 0.4479–0.4535 across the whole rail (k = 0, ⅛, …, 1).
- **Granularity:** worst flip **0.79%** per 1/200 k-step (at k=0.975), mean
  0.29%, 10 of 200 steps flip nothing (extremes; the dot rim is genuinely
  stable there — documented in the header).
- **Cross-check:** JS machine vs numpy prototype disagree on 0.30–0.38% of
  grains (threshold-boundary bin effects only).
- **Performance:** 1.9 ms per apply (201 applies in 380 ms, node) — instant
  switching. Load-time precompute: one 1024-element sort + two tiled
  115,600-entry fields — negligible.

## Deviations (declared in the header)

1. **Lattice unrotated:** 11's own lattice is the 45° press diamond; M9's
   stands square so the AM cell and the Bayer cell coincide. The bond is the
   fill order, not the lattice angle.
2. **Coverage drift:** the wrapped crop holds the 256 nest ranks in slightly
   unequal numbers, so where U ties (pure-nest end) the histogram pin lands
   at 0.4535 rather than 0.4492 — 0.4% drift across the rail, invisible,
   measured.

## Dead ends

- **32² nest at 2 px grain** (10's finest stop): at deck display size it
  downsamples to featureless gray — the end state must be printable. Killed.
- **8² nest at 8 px blocks:** bold and gorgeous (`B_*.png`), but its 64 tied
  levels quantize endpoint ink to 29/64 = 0.4531 / 28/64 = 0.4375 — it broke
  02's law outright. Killed; 16² ties land at 115/256 = 0.4492, inside the
  bin.

## Verdict

**Earns its place.** The slider traverses five nameable states (press dots →
moth-eaten dots → rosette stamps → twill → the nest) that exist in neither
parent, the maths is two certified machines morphing in their native currency
(rank), and the numbers pass both laws with documented wrinkles. The mid-rail
"rosette stamp" state is the one I'd hand a stranger: it is the hybrid screen
of real printing, and it emerged from the morph rather than being drawn.
