# Heart effects — live output audit, 2026-09-08

## What was actually exercised

35 distinct native effect instances: 8 composition, 14 Figure, 8 Feedback and 5 Sculpt. Each received Heart press/release and zero commands, with native bypass/opacity readback and before/on/off composition-monitor PNGs. Additional passes retested repaired settings. Full-resolution live frames are retained alongside JSON; these are not clip thumbnails.

The test source was the running 4D Voronoi + Hopf Fibration figure. Heart motion was held temporarily, but the source's own time animation continued. Therefore ordinary inter-frame differences alone do NOT prove an effect works. Comparisons below rely on recognizable effects. Sampling was not full-frame-rate video and cannot certify temporal smoothness, subtle mirroring or intermittent triggers.

Feedback/Sculpt faders were zero in their saved starting state. Their 13 button/transport checks succeeded, but their composition frames do NOT verify rendered functionality. They need a later test with visible input. Field/Delay had no active visible input and were not exercised. Glyph was excluded as requested. Active clip-specific effects and all other clip stacks remain outside this pass.

## Confirmed control failures fixed

- LUT Corrupt and ColourLoop opacity still had native Timeline animation. Twitch opacity had Timeline / Play Once & Clear. Heart now claims opacity's native phase source before an explicit envelope gesture; this happens off the render loop and validates the current instance.
- A requested full fade could finish near 0.915 because delayed feedback rewrote Heart's target. Heart now retains its target until matching terminal feedback arrives. Poll snapshots cannot override a pending endpoint.
- Enabling an effect no longer depends on the 'bypass at zero' preference. Native bypass changes seen during a Heart fade are accounted for.
- Global Open leaves parked/bypassed effect settings alone. It no longer opens all of their numeric drives invisibly. Active effects can still be explored; Home is the recovery path.
- Rack information now distinguishes layer-at-zero, bypassed parent layer and no clip from an effect's own state.

## Settings recovery

Many unrelated numeric effect parameters had all reached normalized 0.026752586657. Examples: Radial Cloner scales ~2.68%, Iterate starting opacity ~2.68%, Hue saturation ~2.68%, LUT input and output levels equal. This explains disappearing, grayscale and flat-color results despite successful activation.

93 parameter assignments were applied and individually checked against live native readback. Most came from the preserved original Feedback Machine composition, including its distinct Figure LUT and Twitch values. Omitted controls were resolved through native factory reset/readback, not guessed: Hue Scale=1, Saturation=.5, Global Twitch=1, VOLTMIX=1, Iterate StartOpacity=1, Pixel Melt FX_AREA=2 and MOSHLINES=1. Existing LUT choice strings were retained where the old file's resource path did not map unambiguously to a current option. Event values were not replayed as settings.

Twelve recovered poses were saved through existing Home controls. The prior Home file and all pre-repair native/Heart values are backed up here. These are static captured settings from the original, not reconstruction of its old independent native animation timelines. Linear Cloner settings were preserved.

## Visual findings

| Scope / effect | Result on the test source |
|---|---|
| Composition Stroke Volt | Colored edge/outline visible after recovery. |
| Composition Pixel Melt | Unresolved: no convincing melt in sampled output, including MELT_TRIGGER and native area defaults. Do not call visually verified. |
| Composition Hue Rotate | Recovered saturation; visible color shift rather than accidental grayscale. |
| Composition LUT Corrupt | No longer a uniform solid fill; strongly blue/green processed detail. Native LUT look is intentionally aggressive. |
| Composition ColourLoop | Clearly varied, detailed color remapping after recovery. |
| Composition Twitch | Visible shape/color displacement after recovery; no longer clears its envelope unexpectedly. Temporal smoothness not certified. |
| Composition StrokeDiffuse | Strong visible diffusion/feedback structure. |
| Composition Strobe | Brightness attenuation seen across captured states; full temporal behavior not certified by this sampling. |
| Figure LUT Corrupt | Solid blue fill replaced by detailed multicolor processing using Figure's own original settings. |
| Figure Linear Cloner | Clear repeated forms extending beyond frame, as intended. |
| Figure Radial Cloner | No longer nearly vanishes; visible scaled/overlapping clones. Needs more expressive spacing/tuning. |
| Figure Iterate | No longer black after restoring StartOpacity. Original TransformStrength=0 leaves a nearly identity look; expressive setup remains unfinished. |
| Figure Infinite Zoom | Black output replaced by visible expanding/repeated image. |
| Figure Displace | Near-total disappearance replaced by visible displaced structure; aggressive at full mix. |
| Figure Distortion | Visible sliced/distorted image. |
| Figure ASCII | Visible large character conversion. |
| Figure Gradient Shadow | Visible offset shadow. |
| Figure Twitch | Activation/values verified and original settings restored; convincing temporal behavior remains unverified in sampled frames. |
| Figure Mirror / Mirror Y / Mirror XY | Activation verified; this centered, changing source is inadequate for certifying axis behavior. Need asymmetric test input. |
| Figure LoRez | Activation verified; perceptual effect not clear enough in this pass. |
| Feedback / Sculpt effects | Transport only. Faders were zero; no visual pass claimed. |

## Evidence and restoration

- `results-before-fix.json`: original envelope failures.
- `results.json`, `comparison.png`: composition after control fix, before look recovery.
- `figure/results.json`, `figure/comparison-*.png`: initial Figure checks.
- `repaired/results.json`, `repaired/figure-recovery.png`: recovered settings retest.
- `final-three/results.json`, `final-three/comparison.png`: final Pixel Melt, Figure Twitch and Figure LUT checks.
- `settings-repair.json`, `extras-repair.json`: all 93 assignments, original values, sources and verified native values.
- `original-control-values.json`, `figure-original-extra.json`: original-file provenance.
- `home-before-recovery.json`: Home backup.

Each testing pass restored its saved envelope amounts/bypass values and Heart hold in a finally block; clip selection and faders were not deliberately changed. A snapshot timeout interrupted one pass; restoration ran, and remaining checks resumed with fresh state. Native feedback buffers cannot be restored exactly. Corrected parameters, opacity ownership and recovered Homes intentionally remain applied to the current prototype. No shader files or original composition files were edited.

Validation: 186 Python tests pass; workspace DOM checks pass. This audit is intentionally NOT an all-effects working certification. Remaining visual failures and insufficient test inputs are listed above.
