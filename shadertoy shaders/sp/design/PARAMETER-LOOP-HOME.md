# Parameter-loop foundation and motion Home

**September 8 update:** the animated Home behavior below is historical. Home now
rests; the separate Open button enables full numeric motion. See
[Home/Open behavior](heart-performance-plan/home-open/README.md).

Current direction, September 7: the parameter-loop library is the relationship vocabulary. Portal/Treehouse are historical evidence, not the proposed preset foundation. PBF4 Linear and Binepad knobX1 are future physical inputs to the same assignments; no hardware mapping has been configured in this pass.

## Source documentation

- [Parameter loop system: Layer 2 ratio catalog and pattern definitions](</Users/donovan/work/0000000/polyform/parameter loop system.md>) — the 13-section catalog and N-parameter generators.
- [Ratio system f1: agreed scale, sync, reverse](</Users/donovan/work/0000000/mind not map/2.structure-maintains-order/21.labor-installs-practice/211.motion-builds-form/kit/docs/frame.ratio-system.f1.20260619-051247.md>) — the later notes explicitly trust the catalog, not the older draft's phase math or Layer 4 resolver.
- [Ratio-system implementation](</Users/donovan/work/0000000/mind not map/2.structure-maintains-order/21.labor-installs-practice/211.motion-builds-form/kit/src/ratio-system.js>) — ratio and signed mult as distinct controls.

Heart retains its existing integrated-phase implementation to morph rates without phase jumps. It does not reset phase by recomputing from a wrapped master. Its pre-existing family functions are a limited port, and several definitions differ from the full catalog (for example adjacent Fibonacci ratios versus Fibonacci Ascent). They were not silently redefined in this change. A complete catalog migration needs versioned recipe identities so old presets keep their behavior.

## What is implemented

The fader bank is two rows of four, retaining Resolume's descending layer order. FADERS and VARIATIONS capture buttons are at the bottom; keyboard shortcuts remain. Each card has a speed multiplier beside its shuffle controls, from 1/16× to 16×. This scales the card's effective rates together, preserving its individual ratios, signed multipliers, offsets, and ranges. Slow values therefore do not hit the per-slot |mult| ≥ 1 floor. Rate transitions use the existing morph duration and phase integration.

Home now means an animated starting point. A custom **Set motion Home** in Edit stores the current relationship, driven axes, ranges, pose, and speed. Without a custom Home, a prepared profile selects restrained axes and ranges for the current map, level, void, delay, shell, glyph, dither, and grain instruments. Other instruments get a conservative fallback using familiar motion axes; unknown controls and pickers are not automatically animated. If no suitable axes exist, the event log asks for a motion Home to be set.

The new initial relationship recipe is the documented stepped Pendulum Wave, normalized to its first member: `(17 + index) / 17`, at 0.25× card speed. Stable named members select terms without using the live parameter count. The stored rule, its membership, and per-instrument range bindings are separate. This is one initial recipe, not an import of the full catalog. Existing harmonic/irrational/family shuffle controls remain available; selecting those explicitly leaves the Home recipe and uses their existing timing model.

Profiles live in [sweetspots.json](../engine/sweetspots.json). Their ranges are initial restrained candidates anchored to the observed instrument state, not aesthetically validated final sweet spots. Unselected axes stop being driven but retain their current pose. Home does not change layer opacity or launch clips. Delay Home currently animates the R/G/B taps gently while retaining Taps, Span, and Glide, rather than inventing a new delay topology.

Speed and active relationship persist in motion.json; variation and Home snapshots include them. Existing version-2 presets remain readable and clear a newer relationship on full recall. Home adds one Undo entry. Snapshot pose recall cannot rewind the rendered delay/feedback history.

## Evolving parameters

Schema checks detect changed names, IDs, types, ranges, and choices on discovered clips. Known atom sections learn newly exposed numeric controls with drive off. Their UI cards rebuild when names change. The relationship recipe does not require a fixed number of controls: absent saved members are ignored, existing named members retain their terms, and new unbound controls remain still. Retuning or renaming a semantic axis still requires a binding decision; the system cannot infer that a newly named parameter means the same thing as an old one. Duplicate same-named parameters across effect sections remain a limitation of the older atom discovery model.

## Validation

Ten engine regression checks pass, including rate scaling without phase reset, recipe behavior with added/removed members, and legacy preset recall. Controller JavaScript syntax passes. A live shell Home enabled exactly Turn, Spin, Double, Sweep, Thickness, and Hue; a subsequent 0.5× speed command was reflected by the engine, measured at 240.1 Hz. Undo restored the prior motion configuration. Native UI inspection confirmed the two-row bank, adjacent speed control, Home button, and capture buttons at the bottom.

GPU/FPS varied under the current composition; this was not a controlled GPU benchmark or a claim of improved render performance. Each candidate Home still needs performer-led tuning at the actual output load.

### Color access — 2026-09-07

3D (`SP Atom Solid`) ignores Hue / Loop / RGB phase offsets unless Color is
`loop`. Factory Home now resolves that option by name rather than assuming an
index. Choice parameters appear as named selectors; changing one stops its drive
and records Undo. Other figure shaders such as shell blend their palette with Wet;
Red / Green / Blue are cosine phase offsets, not channel gains.

Layer effects with a native Color parameter now expose its swatch and a smoothly
faded amount beside the layer fader. The live feedback layer has Colorize after
its existing Transform, initially cyan at 35%. This is output tinting, not a new
persistent feedback buffer or an in-loop hue accumulation algorithm. The layer
effect persists across clip switches. Its color/amount live in Arena and are not
currently included in Heart's per-clip relationship presets. The composition has
not been saved. Twelve engine checks and UI syntax validation passed.

### Ground correction and effect direction

Ground had an automatically captured all-drives-off snapshot marked `sweet_home`,
which took precedence over its motion profile. Automatic captures now pass
`user_saved=False`; explicit Set motion Home still creates an override. Ground's
old snapshot is backed up in `sp/audit/20260907-ground-home` and its override flag
cleared. Ground Home was applied and its motion checked live.

Donovan rejected Colorize on feedback as the wrong aesthetic. The added layer
effect (1788780032338) was removed. Let Donovan arrange the desired effects in
Resolume, then use that stack as the reference for Heart controls or recreation.
Do not substitute a generic tint effect for that reference.
