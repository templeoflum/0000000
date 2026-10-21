# Toy shader pilot batch — 2026-09-09

Review status: two experimental Figure pilots, compiled and rendered offscreen; not installed or tested in Wire/Arena. All output stays in this folder. Existing identities, engine, patches and live composition were untouched.

## Delivered

`SP Toy Transit Figure 01.fs` is a fresh ISF identity derived from `/Users/donovan/work/met3or/instruments/transit.html` (rev 1.2.1). `build.py` reads existing `sp_header.py` and embeds `sp.glsl` verbatim; it deliberately does not call the helper’s installing `emit()` function. The `.sp.json` groups the existing Smart Param controls. No new modulation engine is introduced.

- Phase: normalized 0–1, original relative x = -250 + 500 × phase.
- Impact: normalized 0–1 maps to the source’s b = 0–1.05; y = b × 46, downward in source canvas coordinates.
- Star radius 46; occultor radius 13.8 (ratio 0.30); source gradient stops and blue rim preserved. Dark occultor has opacity, so it obscures the star instead of punching a transparent hole.
- Home: phase 0.5, impact 0, both Drive toggles off. Enable Phase Drive with the existing cosine/sway behavior for a continuous back-and-forth crossing; manual or Heart-driven values work through existing slots. Heart integration has not been exercised in Arena.
- Figure: centered source coordinate system, measured against the shorter frame dimension. No placement/scale controls; external Figure Transform owns those. Full phase travel fits in frame. The star looks small at Home because the original 500-unit travel span is preserved; enlarging the external Transform can intentionally crop that travel.

This is a scene-only adaptation. The source flux sampling, curve plot, readout, contact vesicas, datum and canvas shadow glow are omitted. No claim of flux accuracy is made. Source play advanced by frame count; this pilot uses existing Smart Params instead. Output is straight RGBA. No assets or input textures required.

## Source inventory and conversion decisions

The intended sources were identified in the sibling MET∃OR project. Its `LIBRARY.md` identifies recovered toys; `instruments/README.md` describes the active contract-A drop zone. The build menu contains proposals as well as completed toys, so it was not treated as proof of implementation.

| Existing candidate | Source under `/Users/donovan/work/` | Proposed role | Decision |
|---|---|---|---|
| Transit | `met3or/instruments/transit.html` | Figure | Implemented scene-only pilot; deep inspection below |
| φ-Quasicrystal | `met3or/lore/recovered/met3or_quasicrystal.html` | Figure | Implemented as a baked point plate with Smart Param rotation |
| Autocollimator | `met3or/instruments/autocollimator.html` | Figure | Candidate: returned reticle displacement; retain coincidence mechanism |
| Compass rose | `met3or/instruments/compass_rose.html` | Figure | Candidate: graduated concentric rings; preserve relative orientation |
| Astrolabe | `met3or/instruments/astrolabe.html` | Figure | Candidate: rete and fixed plate; geometry/text extraction needed |
| Nomogram | `met3or/instruments/nomogram.html` | Figure | Candidate: alignment/straightedge; meaningful without labels needs review |
| Stepping feet | `0000000/optical illusions/reports/stepping-feet-illusion.md` | Field | Report is a stub with abstract, has_demos=false; no executable toy found here |
| Moiré interference | `met3or/brand/docs/met3or_toy_study_menu.md` | Field | Proposed study; not used as an invented replacement |

Figure means a centered contained source whose placement belongs to external Transform. Field may cover the full frame. No Field is delivered in this batch; a grid-based illusion is a plausible later Field, but documentation alone is not an existing executable toy.

## Deep inspection

Transit: `Ox`, `Oy`, `drawScene`, `computeFlux`, `contacts`, and the contract-A message receiver separate appearance from measurement. The source uses a 400×190 scene, star at (200,95), radius 46, ratio 0.30, and 500-unit x travel. Its flux uses a 1.4-unit sample grid with linear limb darkening u1=0.6 across 260 phase samples; this is distinct from its visual gradient. Copying only the visual gradient cannot reproduce flux. The pilot therefore makes no measurement output. Contact I–IV are geometric intersections and flashes are optional source events; these were omitted explicitly.

Quasicrystal: five integer coordinates each range -2…2 (3,125 tuples). Physical basis angles are k×72°, perpendicular basis k×144°. Intensity exp(-0.30|q|²) is culled below 0.12, with physical radius cutoff r×21≤176. Source sorts ascending intensity and then deduplicates rounded three-pixel bins, retaining the first encounter (not necessarily the brightest). Shell colors use rounded log(r/2)/log(1.618) modulo three. The SVG has core+halo circles, a 188-unit guide ring, five axes, and 96-second CSS rotation. The second pilot precomputes the source-selected point list and uses a texture lookup. A sum-of-cosines field would be a different mechanism. Do not put the 3,125-tuple enumeration inside every fragment. No performance savings claimed without a render benchmark.

## Evidence and reproduction

`provenance.json` records SHA-256 of both deeply inspected toys and shared Smart Param sources. `evidence/validation.json` records actual image alpha bounds and compiler result. PNGs: central Home at 640×360; grazing at 360×640 with phase=.6, impact=1; endpoint at 360×360 with phase=1, impact=1. Home and grazing images were visually inspected.

Run from project root:

```sh
python3 sp/experiments/toy-shaders/build.py
python3 sp/lint_isf.py 'sp/experiments/toy-shaders/SP Toy Transit Figure 01.fs'
sp/qa/.venv/bin/python sp/experiments/toy-shaders/render_pilot.py 'sp/experiments/toy-shaders/SP Toy Transit Figure 01.fs' -o sp/experiments/toy-shaders/evidence/home.png -w 640 -H 360 --rgba
```

`render_pilot.py` is an isolated copy of the project offscreen harness, with bool uniforms declared as GLSL bool so existing Smart Params compile. The initial sandbox render failed with `cannot choose pixel format`; the same small offscreen render succeeded with approved graphics access. The initial Transit validation rendered three single frames sequentially; the second pilot adds ten frames as described below. These establish GLSL compilation and example pixels, not Wire import, live playback, frame rate, exhaustive ranges, or show readiness.

Read before work: project HANDOFF, WORKERS.md, local Ollama and benchmark READMEs, sp_header/sp.glsl and existing Figure source conventions. Local LLM inference was intentionally left idle during live rehearsal because the documented workers share GPU/unified memory with Resolume. No model loading/unloading or cloud source transmission was performed.


## Second pilot: Quasicrystal Figure 01

Added after review requested visible variation from an existing illusion-oriented toy. `build_quasicrystal.py` reproduces the five-dimensional tuple enumeration, source intensity sorting and rounded-bin deduplication: 1,485 accepted tuples, 821 retained points. Coordinates are recorded in `quasicrystal-points.json`. `quasicrystal-points.png` is a transparent 800×800 plate baked at 1600×1600 then downsampled. It preserves shell colors, core/halo opacity, and center circles. Guide axes and outer ring are omitted. Python floating-point and Pillow rasterization are not claimed pixel-identical to browser SVG. This is a projected-point seal, not an invented wave-interference field.

`SP Toy Quasicrystal Figure 01.fs` imports that relative PNG via standard ISF IMPORTED. Keep the shader and PNG together; Wire resource packaging remains untested. Turn is a cyclic existing Smart Param; enable its Drive to animate rotation. Home remains still. Reveal fades faint coverage progressively (a performance extension, not a source parameter). The square plate spans .88 of the short dimension; the source’s radial point support stays contained under rotation. There is no local placement or size input. Texture filtering limits detail under strong enlargement.

`render_pilot.py` additionally handles imported texture declarations and bindings, solely for this isolated validation. The quasicrystal compiled in the actual offscreen OpenGL renderer; stock project lint does not declare imported samplers and was not used to claim success for this file. Both original and variant were rendered at 480×480. Eight additional actual shader renders at 320×320, Turn=0…0.0875, create `evidence/quasicrystal-motion.gif`; this is a discrete parameter preview, not a measured real-time recording. No local LLM or sustained GPU job ran. `evidence/contact-sheet.jpg` compares five pilot states.
