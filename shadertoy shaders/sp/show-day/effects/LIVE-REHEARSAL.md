# Root-only effects rehearsal

Prepared offline, September 9. No live controls executed. Budget: one moving-input pass per effect, then restoration. If the result is inconclusive, retain **unverified** status rather than extending into a settings repair session.

## 1. Discover and snapshot before touching controls

1. Read Arena `GET http://localhost:8080/api/v1/composition` and a fresh state message from Heart `ws://localhost:8766`. Require Heart `arena_connected=true`, matching composition, and an unambiguous currently connected source. Record composition ID/name, selected clips, layer names/IDs, dimensions, all touched native parameters, effect amount/bypass, Heart `hold`, motion/drive state and fade configs under a new root-owned integration evidence directory.
2. Enumerate native effects using `targets.effects(comp)` from `sp/engine/targets.py`. Select native **MTK_PXLMELT at composition scope** and **DelayRGB at layer scope on the layer currently named sculpt**; do not select an imported clip-stack DelayRGB by its display label. Require one candidate per intended scope; stop on ambiguity. Match each native key to fresh Heart `fx` and require `fx.binding[1] == native_effect.id`, matching parameter IDs, and unchanged Heart `instance`.
3. Record `bypassed.id`, `params.Opacity.{id,min,max,value}` and the complete current `params` schema. Pixel Melt must expose `MELT_TRIGGER` as ParamEvent/ParamTrigger; inspect `MELT_LOCK`, `FX_AREA`, `STYLE`, `DRIVER`, `DENSITY`, `TIMESTRETCH`, `MOSHLINES`, `FADETIME`, `WRAP`, `AREA FEATHER`. DelayRGB must expose numeric `R delay`, `G delay`, `B delay`. Stop if the schema differs; do not substitute guessed names or IDs.
4. Every Heart effect command uses the discovered `key` **and** `instance`; recheck binding after reconnect, clip/stack change or error. Use `fx_param` with native values for parameters, `fx_direction` value 1/0 for IN/OUT, or `fx_amount` value 0 for immediate termination. Read back native amount/bypass and changed parameter values through a fresh composition response. A Heart send/flash alone is not native acknowledgment.

Expected September 8 keys were `composition/effect/MTK_PXLMELT~1` and `layer/sculpt~1/effect/DelayRGB~1`; these are search hints, not today's bindings. Native effect IDs **1788780037026** and **1788780036905** in that saved snapshot are stale and must never be replayed. All parameter IDs in saved JSON are equally stale.

## 2. Establish visible moving input and isolate the test

Use a currently available, known playable moving source with a bright asymmetric edge/object on a dark background, preferably a white object that visibly changes position. Confirm movement in the native composition monitor before testing. Source movement must continue if Heart motion is held; do not freeze the only source of motion. Avoid a centered static disk for these temporal checks.

Snapshot before temporarily suppressing interfering effects. Make the intended tested layer visible, unbypassed and not excluded by solo. For DelayRGB, first prove moving input directly at Sculpt; root may use an existing suitable source there or a freshly verified empty scratch slot. Never overwrite a populated slot. Treat direct-input processor success separately from routed-loop success.

Use one effect at a time. Freeze only its changing numeric drives through existing controls, recording prior state; do not use Open/Shuffle or trigger every available event. If shortening fade durations for isolation, save/restore the entire original config. Capture short continuous output if available; otherwise sample at 0, .25, .5, 1, 2, 4 and 8 seconds, explicitly labeling the result **sampled**. Native snapshot endpoint reused by existing scripts: `/composition/monitors/1/snapshot.png`; confirm it shows the intended composition output.

## 3. Pixel Melt: trigger versus ordinary movement

1. At amount 0, capture moving-input baseline. Preserve the recovered current pose initially. Confirm `MELT_LOCK=false` if available; change it only after saving its original value. Do not factory-reset the plugin.
2. Send `{"cmd":"fx_direction","key":K,"instance":I,"value":1}`. Wait for the native Opacity maximum and bypass false, using configured attack plus a bounded allowance; stop after 10 seconds if no endpoint. Record a pre-trigger moving interval.
3. Send exactly once `{"cmd":"fx_param","key":K,"instance":I,"name":"MELT_TRIGGER","value":true}`. Record subsequent motion and native parameter/amount/bypass snapshots. Do not send a false value expecting it to undo an event.
4. Expected visual evidence: a recognizable triggered temporal smear/retained or distorted moving image that differs from the untriggered moving baseline. Mere source movement, brightness change or a successfully delivered event does not pass. Event parameters need not expose persistent readback; report command delivery and visual outcome separately.
5. OUT, then verify native opacity 0/bypass true when bypass-at-zero is enabled, or opacity 0 with the saved bypass policy otherwise. Confirm an ordinary moving source remains visible. If no convincing triggered effect appears, mark Pixel Melt **unverified** and stop this branch. The saved recovered pose (`FX_AREA=2`, `MOSHLINES=1`) is evidence to compare against, not authorization to replay unrelated saved values.

## 4. RGB Delay: distinguish real channel history

1. With visible moving input directly at Sculpt and amount 0, save all three delays. Through `fx_param`, set all to native 0 **only if current ranges admit 0**. IN and capture the zero-delay control.
2. Set native `R delay=0`, `G delay=.15`, `B delay=.30` only if each fresh range admits it; these values were valid in the saved native schema. Do not describe them as seconds: native temporal units were not established by this audit. Capture movement over eight seconds.
3. Expected: colored channel edges occupy distinct earlier positions of the same moving subject; the separation changes with movement rather than being a fixed color tint. Return G/B to 0 and verify separation collapses after history settles. If effect remains ambiguous, keep **unverified**; do not increase blindly to maximum.
4. OUT and confirm the moving source persists. Restore three saved delay values. Only after direct-input success, reconnect the intended saved Sculpt/Delay tap by fresh discovery and repeat briefly with visible routed input. Record native router `Input` semantic option/value and `Input Opacity` / `Input Bypass/Solo` where present. Never decode saved `3:5`, `3:4` or `1:1` tokens into endpoints by guess. Direct-input success does not pass this routing step.

## 5. Safe termination and final readback

On timeout, identity change, unexpected black output or loss of connection: stop further triggers and test-setting writes. If still connected to the same binding, send immediate `fx_amount=0` to the tested effect and release any held strobe. If disconnected, reconnect through the root recovery procedure and rediscover before any restoration; never use old IDs against a new composition.

Restore saved connected clips (or clear the connection only if originally empty), faders, solo/bypass, touched numeric/manual/drive settings, fade config, effect target/amount and Heart hold. Revalidate each identity before writing. Remove only scratch content whose exact identity is still the one created by this rehearsal. Fetch fresh native + Heart state and compare every touched reversible field with the snapshot; record any mismatch instead of claiming restoration succeeded.

Trigger events and accumulated native history are not reversible. `Reset trails` applies only to a currently discovered SPHeartFeedback instance exposing that ParamEvent, and clears on the next rendered frame; do not assume it clears Pixel Melt or DelayRGB buffers. No composition save, plugin reset or unrelated source change is necessary to conclude this rehearsal. Leave a visible known source with test effects at zero if restoring the original state is unsafe; report that departure explicitly.

## Reuse existing scripts as patterns, not launch commands

| Existing file | Reusable parts | Must change before reuse |
|---|---|---|
| `sp/audit/effects-live-20260908/check_final_three.py` | Heart reader/send helper, native effect lookup, monitor capture, before/after snapshots. | Hardcodes Figure layer 5 / `layers[4]`; restores old native IDs without identity checks; uses legacy press/release and only three short samples; resumes old results/output directory. |
| `sp/audit/trigger-and-effects-20260908/guard-pass/check_remaining.py` | Empty-slot preflight, schema enumeration, per-case native readback and finally-block structure. | Hardcodes layers 5/1/2; static diagnostic cannot pass temporal tests; fires **all** events; refreshes instance by key without proving native identity; scratch deletion uses a substring; writes into old audit evidence. Do not execute unchanged. |
| `sp/qa/review_feedback_live.py` | Existing feedback behavior/reset command shape and capture endpoint. | Hardcodes L1C6 / `heart feedback`; no restoration finally block. The audited newer saved inventory lacks that old named slot. Not a general routing/reset rehearsal. |

Checks for this preparation: read the three scripts, current command/discovery code and saved Pixel Melt/DelayRGB schemas. No scripts above were run and no new live runner is supplied. Root should adapt only necessary helpers into its own bounded rehearsal or operate the existing surface with the same discovery/restoration gates.
