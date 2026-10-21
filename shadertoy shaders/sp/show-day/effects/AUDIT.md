# Effects, actions and routing audit — September 9, 2026

## Result and show gates

No new shared-code defect was proven in this bounded audit. Existing directional, momentary, readback, ownership, routing-contract and guard regressions pass. This is offline verification plus review of saved live evidence; no current live output was inspected.

1. Keep Pixel Melt and RGB Delay marked **temporal behavior unverified** until root runs a moving-input test. Commands arriving, static frame changes and direct-input processing do not establish their intended temporal effect.
2. Rehearse the selected Feedback → Sculpt → Delay configuration with visible input and fresh native routing readback. Saved files differ; neither old clip counts nor coordinates establish current occupancy.
3. Linear Cloner protection **is implemented**, superseding `sp/audit/cloner-anchor/REPORT.md`. The newer `sp/audit/calculated-bounds/REPORT.md` and current code verify a bounded forward, unwarped mode with sampled output at three aspect ratios. Upstream creative expansion, native direct edits, perspective/reverse/delay/distortion and delivery between separate native writes remain outside a blanket containment guarantee.
4. Release strobe while pointer leaves, focus changes, and connection drops during root's rehearsal. Offline semantics pass; continuous live timing and physical feel were not tested here.

## Control and action matrix

| Control / action | Current implementation and checked evidence | Limits / integration decision |
|---|---|---|
| Numeric effect drives | `heart.EffectMotion`, `targets.controls/convert`; native numeric parameters become existing Smart Params; manual takeover removes native phase source. `test_effect_ownership`, `test_effect_open`, `test_targets` pass. | Availability depends on native schema, current scope and instance; do not call every plugin control a numeric drive. |
| Choice | Validated option strings, picker UI; choice slots can map normalized positions to option lists. Global Open skips choice slots. | Native option lists are authoritative; no invented numeric route decoding. |
| Boolean | Checkbox, strict bool conversion and parameter write. | Linear Cloner guarded mode intentionally parks Reverse / Delay Enabled false. |
| Color | Native color input; validates hex and appends alpha for six-digit RGB. | Manual access exists; not a full native palette/alpha workflow certification. |
| Event / trigger | Rack rows for ParamEvent/ParamTrigger and manual buttons; true POSTs `/trigger`, false does nothing. Captures effect identity; stale/disconnected bindings disabled. | UI flash means sent, not acknowledged or visually effective. Saved LUT and Pixel Melt trigger checks establish access only. |
| IN / OUT | Directional endpoint envelopes; IN holds 1, OUT holds 0; mid-fade reversal preserves current level; repeated same-direction action at endpoint starts from opposite endpoint. Five direction tests pass. | Same-direction endpoint retrigger is intentional; live rapid-action musical feel needs root rehearsal. |
| Strobe Hold | Immediate momentary envelope despite legacy latch/long fade config; multiple owners; final release stops; pointer cancel/lost capture, blur/pagehide and disconnect release paths. Three engine tests and DOM checks pass. | No sampled-frame audit certifies full strobe timing. |
| Opacity ownership | Explicit gesture claims native opacity phase source; validates current identity before applying deferred result. | Existing claim tests cover stale binding and delayed work; no new live stress run. |
| Bypass and readback | Bypass true means disabled. WebSocket subscriptions follow opacity/bypass IDs; stale snapshots/echoes cannot rewind active or pending endpoints. `test_effect_readback` passes. | September 8 Hue test measured external changes at 61–155 ms; historical measurement, not today's latency guarantee. |
| Open / Shuffle / Settle | Global Open skips parked effects; effect-specific recipes preserve structural poses. Shuffle respects drive/ownership/locks; Settle clears effect amounts. | Open is exploration, not enable-all. Saved Homes are not exhaustive for legacy content. |
| Transform / Linear Cloner | Coupled projection, current frame size/source envelope, applied-value publication, frame-relative drive ranges; randomized geometry and manual engine-path checks pass. | Requires recognized Figure keys, frame context and ownership of coupled controls. Other layer/clip clones do not inherit this exact guard. |
| Feedback Reset trails | SPHeartFeedback ParamEvent; excluded from drives; exactly one true trigger POST. Engine reports clear on next rendered frame. | Shader-buffer saved tests show clear/release/fresh-input behavior for the tested instrument. Does not clear every native feedback/delay effect. |
| SP Delay Chain actions | UI specifically recognizes Shuffle/Home/φ ParamEvent controls on named SP Delay Chain. | Presence and trigger schema must match discovered current instrument; this is not DelayRGB temporal verification. |
| Router reconnect / patch recall | Reconnect releases effects, clears output queue and requests discovery; subscriptions recreated. Patch dependency contract checks native source/plugin identity, effect order, dimensions, serialized route settings and fresh post-open snapshot. | Reconnect does not itself select an intended tap or prove rendered feedback. Cannot cancel an already transmitted native request; tests distinguish inflight requests from subsequent operations. |

## Effect rendering matrix

All visual statements below are **saved audit findings**, not a new visual pass. September 8 isolated checks supersede the earlier zero-fader limitation only for direct diagnostic input. Exact serialized controls and native type IDs are in `SAVED-INVENTORY.json`; display names below follow audit terminology.

| Scope / effects | Strongest saved evidence | Readiness limit |
|---|---|---|
| Composition Stroke Volt, Hue Rotate, LUT Corrupt, ColourLoop, Twitch, StrokeDiffuse | `sp/audit/effects-live-20260908/REPORT.md`: recognizable output after recovered settings; native amounts/bypass checked. | Sampled visuals, not sustained combinations or temporal smoothness. |
| Composition Pixel Melt | Above audit and `sp/audit/trigger-and-effects-20260908/REPORT.md`: native MELT sent, rack click reached intended instance. | No convincing temporal melt established. |
| Composition Strobe | Native activation/release plus sampled attenuation; current momentary tests pass. | Full temporal behavior not certified. |
| Figure LUT, Infinite Zoom, Displace, Distortion, ASCII, Gradient Shadow | September 8 recovered output recognizable. | Aggressive full-mix looks; not universally safe settings. |
| Figure Linear / Radial Cloner / Iterate | Trigger audit guarded Open yielded moving nonempty samples; newer calculated bounds protect Linear first copy and Figure Transform. | Radial/Iterate recipes are provisional; temporal fill warmup and arbitrary manual/stack settings remain gaps. |
| Figure Mirrors / LoRez | Trigger audit isolated asymmetric diagnostic establishes visible operation and exact before/off match. | Earlier centered-source uncertainty is superseded for these tested cases only. |
| Figure Twitch | Native values restored, activation/readback checked. | Convincing temporal behavior remains unverified. |
| Feedback InvertRGB / Blur / Sharpen / Kaleidoscope / Mirrors | Trigger audit 18 isolated before/on/off processor checks and followup Invert/Hue checks. | Direct input, not all feedback-loop configurations. Alpha inversion may intentionally change silhouette. |
| Sculpt InvertRGB / Hue / AutoMask | Same direct-input audit. | Does not establish all current routes or interaction with feedback history. |
| Sculpt DelayRGB | Static/direct input and control access only. | Moving-input channel delay check required. |
| Field Twisted ×2 / Suckr / FishEye; Delay InvertRGB / AutoMask | Present in saved `_route_readback.avc` stack extraction. | No blanket rendering certification from the audited effects passes. |
| Glyph | Present in saved file; excluded by plan. | Deferred. |

## Saved routing and composition differences

`SAVED-INVENTORY.json` contains SHA-256 hashes, layer stacks, typed serialized effect controls, and every router/native-feedback clip in **all decks**, using zero-based XML indices. Extraction records exact serialized Input tokens without assuming their native meaning or current live selection. The human summary is `extraction.txt`.

- `_route_readback.avc`: eight layers in order feedback, sculpt, field, delay, figure, glyph, texture, grain; 58 router/native-feedback clips across saved decks. This file includes imported FM copies absent from the earlier small baseline. Its scratch name does not prove it is the currently loaded composition.
- `Feedback checked.avc`: eight layers, 18 router/native-feedback clips. Includes `heart feedback` on layer index 0 / column 5 with serialized Input `3:2`; that named router is absent from extracted `_route_readback.avc`. Do not assume the older special-instrument slot is currently available.
- `Heart Performance.avc`: eight layers, 17 router/native-feedback clips. Ordinary saved taps include feedback map/texture/fold/level/pass Input `3:2`, sculpt level `1:1`, sculpt pass/color `3:3`, delay figure `3:5` and field `3:4`. Delay taps explicitly save Input Opacity=1 and Input Bypass/Solo=0. These are serialization facts, not independently decoded endpoint labels.
- `portal.avc`: 23 layers; `treehouse.avc`: 20 layers. Both contain eight native Feedback clips on layer index 0, named 1 - in through 8 - in/out spiral. These are VideoSourceFeedback, not explicit CompositionRouter Input-choice routes. Their absent Params do not prove a particular tap endpoint. Routing/playability still requires current native and visible verification after media recovery.

## Evidence and checks actually run

- Read current `heart.py`, `workspace.js`, `targets.py`, `effect_open.py`, `figure_guard.py`, `feedback.py`, `dependencies.py`, plus focused existing tests.
- Read saved effects, trigger, Hue, cloner-anchor and calculated-bounds reports; saved feedback-buffer result JSON. This audit does not independently re-render or re-review every referenced image.
- Parsed the five saved compositions listed above with deterministic XML extraction, retaining hashes and exact route settings.
- `run_offline_checks.py`: **117 tests passed** in 3.299 seconds. Real socket connections were prohibited and bytecode writes disabled. Full output: `python-checks.txt`.
- Existing workspace test harness: **34 offline DOM checks passed**. Full output: `ui-checks.txt`. This is not a browser pixel review.
- No new regression/patch staged against the shared engine because no new concrete defect was demonstrated. The bounded read-only extractor and network-blocked test runner are staged under this task directory for repeatability.

## Proposed integration

Root should review these gates, choose one visible moving Figure input, and verify the actual loaded composition/identities before actions. Exercise IN→OUT→IN mid-fade, strobe press/release/focus loss, native external bypass readback, LUT/Pixel Melt trigger, Feedback/Sculpt with visible levels, RGB Delay with moving input, feedback reset on the instrument that actually exposes it, and reconnect/recall with fresh serialized route and rendered-output checks. Preserve/recover selected clips, amounts, bypass, fade configuration and source state. Do not promote unverified temporal effects into the dependable set merely because command transport succeeds.
