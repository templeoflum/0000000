# Temporal acceptance — source availability and expected observations

Prepared September 9, offline. **Exact MTK_PXLMELT/DelayRGB algorithms and timing could not be established from readable source in the inspected locations.** Do not interpret the test expectations below as proven implementation details. No live requests, rendering, builds or patches were performed.

## What the available implementation evidence establishes

| Target | Evidence actually available | Proven / unknown |
|---|---|---|
| Native DelayRGB | Saved native schema in `sp/audit/trigger-and-effects-20260908/guard-pass/after-native.json`; installed-effects description in `sp/design/heart-performance-plan/baseline/installed-effects.json`; local native preset `~/Documents/Resolume Arena/Presets/Video Effects/Delay RGB/custom.xml`. | Built-in identity A152, description “Delay per color channel”; numeric `R delay`, `G delay`, `B delay`, each native range 0–1 in saved schema; Opacity 0–1. No event/trigger in that schema. **No readable algorithm, buffer depth, interpolation rule or native time-unit mapping located.** Preset opacity Timeline is historical configuration, not delay source code. |
| MTK_PXLMELT | Same saved native schema and installed-effects catalog; recovered settings audit. | `MELT_TRIGGER` is ParamEvent, `MELT_LOCK` boolean. No readable Wire graph/shader located for this installed effect. Trigger duration, lock semantics, fade curve, frame dependencies and the exact roles of TIMESTRETCH/FX_AREA are **not proven from source**. Preset names such as SANDFALL TRIGGER are not an algorithm specification. |
| SP Delay Chain / SP Delay Performance | Readable local `~/Documents/Resolume Wire/Patches/SP Delay Chain/SP Delay Chain.wire`; workspace `sp/patches/SP Delay Performance/SP Delay Performance.wire`; `sp/qa/build_delay_quality.py`. | A **different** effect. Chain metadata describes 480 one-frame delays, 60 taps every 8 links, six tap switches, beat span and additional 0–16-frame RGB offsets. Graph has 496 Delay nodes, consistent with a main 480-frame chain plus 16 additional delay nodes. Quality builder changes history texture dimensions while preserving timing. These facts **cannot supply the native DelayRGB time mapping**. |

Search covered workspace filenames/source references, Documents/Resolume Wire patches and backups, Arena presets/Extra Effects, installed Arena/Wire trees, their local help, and Arena's configured JuiceBar plugin directory. This is “source not located in these inspected locations,” not proof no source exists elsewhere. Pixel Melt catalog identifiers also vary across saved snapshots; discover the current native instance rather than replaying an old catalog ID.

## Root's visual acceptance

**RGB Delay — strongly supported functional expectation, exact timing unknown.** Use a white, asymmetric object moving across a dark background with an abrupt direction reversal or stop. Keep input color neutral and unrelated effects off. First capture amount 0, then amount 1 with all channel delays 0. Set R=0, G=.15, B=.30 only after checking current native names/ranges. No trigger is needed according to the saved schema.

Pass evidence is that color-channel silhouettes follow distinct earlier positions of the same object. A direction reversal should cause the delayed channels to continue the previous trajectory briefly; after stopping, the channels should eventually converge. Restore all delays to zero and require the separation to disappear. Source movement alone shifts the channels together; fixed chromatic displacement is not enough to prove history. If only a tint or static split appears, label the result inconclusive. Do not label .15/.30 “seconds,” “frames,” or a known fraction of buffer length.

**Pixel Melt — empirical acceptance, not an exact source-derived prediction.** Preserve the recovered pose first; amount must reach native maximum and bypass false. Record a moving pre-trigger interval, then issue exactly one `MELT_TRIGGER=true` via the current Heart key/instance. Record any reproducible trigger-correlated smear, retained structure or deformation, followed by OUT and ordinary-source recovery. A distinct effect temporally correlated with the trigger supports “visible trigger effect”; proving stored history additionally requires a feature from an earlier input frame to remain after that feature has moved/disappeared. Ordinary source animation and full-mix brightness change do not pass.

The earlier rehearsal's suggestion to set `MELT_LOCK=false` is a test configuration, **not a proven algorithm requirement**; snapshot and restore it. Likewise FX_AREA=2/MOSHLINES=1 are recovered native settings, not verified necessary conditions. Do not repeatedly fire or change all controls hoping for a result. If a single recorded trial at the recovered pose is unclear, retain **unverified** rather than claim a plugin failure.

## Minimum useful temporal sampling

No exact minimum interval or observation window can be derived for the two native effects without their time mapping/source. For strong acceptance, capture **consecutive rendered output frames** with timestamps at the actual render cadence: at 60 fps this is approximately 16.7 ms/frame; at 30 fps, 33.3 ms/frame. This is a sampling recommendation, not a guarantee the effect changes every frame. Capture baseline, trigger/change, motion reversal/stop and recovery in the same sequence.

Sparse .25–1 s HTTP snapshots are useful for obvious changes but cannot certify short transients or latency. HTTP request spacing does not guarantee rendered-frame spacing; record actual timestamps and duplicate frames. Start with the bounded eight-second observation in LIVE-REHEARSAL.md, but **eight seconds is not a proven full native-buffer warmup**. A negative sparse-frame result is inconclusive.

For the separate SP Delay Chain, metadata's 480 rendered frames correspond to 8 s only at 60 fps (16 s at 30 fps); 16-frame RGB offsets correspond to about .267 s at 60 fps. Those calculations explain why a .3 s sample can miss its fine channel movement, but must not be transferred to native DelayRGB.

## Consequence for the rehearsal

Use LIVE-REHEARSAL.md for discovery and safe restoration, with the qualification above: exact Pixel Melt semantics and native delay units remain unknown. Report independently (1) command/native readback, (2) visible effect, (3) evidence of history, and (4) routed behavior. No code change is proposed on the basis of missing source or inconclusive saved samples.
