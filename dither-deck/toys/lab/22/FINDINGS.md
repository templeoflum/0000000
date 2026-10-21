# S22 "SCREENS" — certification report: PASS

**Verdict: earns its place. Passed every numeric gate; one measurement ghost
exorcised along the way.**

## identity

Two AM halftone dot screens (Euclidean round dot, Gaussian dot-gain profile,
ruling 34 px) tilted Δθ apart, superposed by the density product — the standard
screen-moiré model (Amidror). k sweeps Δθ 0°→30° symmetric about 45°; at
k>0.72 a third screen at 90° fades in, closing the classic CMY-angle press
rosette (separations 30/30/60 — the rotated twin of 15/45/75). Journey: the
45° dot → the great rosette (Λ≈540 px) → rosettes → argyle → cluster field →
rings form → the press rosette.

## measured at certification (headless node, 200-step sweep)

- ink: 0.4500 – 0.4588 ✓ (cut from the top: ink = dots, F≥thr)
- worst flip: **2.27%** per 1/200 step at k=0.13 ✓ (the great-rosette beat
  sweeping fastest, as physics says it should)
- apply: **~10 ms** — see the ghost below. Load 444 ms.

## the 286 ms ghost (measurement artifact, documented for future QA)

The first sweep reported avgApplyMs 286. Chase: standalone inner-loop bench =
6–16 ms; the same loop wrapped in `eval()` = 260 ms. The QA harness evals the
toy's script to stub the DOM, and V8 refuses to optimize eval-scope variable
access in hot loops — every `XC[i]`/`GT[g]` becomes a dynamic scope lookup.
Toys with few per-pixel outer-scope reads (S16, S21) barely notice; S22 does
~6 per pixel and pays 25×. **In the deck the toys load as real `<script>`
code and this cost does not exist.** Harness artifact, not a toy defect.
Future harnesses should load via `vm.runInThisContext` or a temp module file
if timing numbers matter.

## eye test (lab/22/_mont.png, final_k*.png)

Distinct nameable states across the whole rail. Watch-item: k=0 ("the 45° dot")
is S11's home turf — but S11 is a single static screen family atom and S22's
journey immediately leaves it; the rosettes and argyle are owned by no one.
The vision name-checks rosettes; this machine prints them honestly.

## deviations

- Third-screen fade by density interpolation L·((1−w)+w·L3) — documented in header.
- A hex-lattice variant was killed by the one law of feel (see header) — the
  rosette lattice already covers that territory.

Prototype PNGs (`v3_*`, `m_*`, `w*_third.png`, `dth*_product.png`) in this folder.
