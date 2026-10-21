# Effects and routing — complete

2026-09-09. Task 2; writes confined to `sp/show-day/effects/`. No live queries/mutations, shared engine edits, composition saves or installations.

## Concrete show gates

- Pixel Melt and RGB Delay temporal functionality remains unverified; moving-input root rehearsal needed.
- Current Feedback/Sculpt/Delay routing needs fresh native + visible verification. Five saved compositions differ: `_route_readback.avc` has 58 router/native-feedback clips, `Feedback checked.avc` 18, `Heart Performance.avc` 17; counts include all decks, not active selections.
- Correction to early status: Linear Cloner runtime protection **is implemented** in newer `figure_guard.py`; `calculated-bounds/REPORT.md` supersedes old cloner-anchor report. Forward/unwarped mode has sampled live evidence. Upstream expansion, external edits and temporal variants remain limited.
- Existing action/readback tests pass; no new code defect proven. No speculative shared patch.

## Produced / checked

- `AUDIT.md`: control/action and per-effect evidence matrix, routing differences, root rehearsal gates.
- `SAVED-INVENTORY.json`, `extraction.txt`: exact saved routing/stack/control extraction from five compositions, hashes, zero-based indices.
- `extract_saved_inventory.py`: repeatable read-only extraction.
- `run_offline_checks.py`, `python-checks.txt`: 117 focused existing tests pass; real network blocked, no bytecode writes.
- `ui-checks.txt`: 34 existing offline DOM checks pass.

Unverified: today's live identities/output/routing, continuous temporal behavior, physical gestures and broad stack combinations. Proposed integration: root reviews AUDIT.md and performs one visible moving-input rehearsal plus reconnect/readback; no shared code integration required by this audit.

## Follow-up preparation — complete

Produced `LIVE-REHEARSAL.md`: ordered fresh binding/parameter discovery; moving-input Pixel Melt and RGB Delay procedures; separate native, visible and routing acceptance; bounded termination/restoration; reuse notes for three existing scripts and their stale IDs/coordinates. Reviewed actual saved native parameter names/ranges and current Heart binding/command code. No live script executed, no shared edits, and no new live runner. Root's next step is the single-owner rehearsal; temporal outcomes remain unverified until then.

## Temporal source inspection — complete

Produced `EXPECTED-TEMPORAL.md`. Native DelayRGB and MTK_PXLMELT readable algorithms were not located in inspected workspace/Resolume/plugin paths; exact native delay units, Pixel Melt lock/trigger timing and minimum observation window remain unknown. Reviewed saved schemas/catalog/preset plus the separate readable SP Delay graph and quality builder; explicitly avoided transferring SP Delay timing to native DelayRGB. Document supplies qualified visual acceptance and recommends consecutive rendered frames (16.7 ms at 60 fps), with sparse snapshots treated as inconclusive for short transients. Read-only inspection only; no live calls, rendering, shared edits or patches.

## Pixel Melt timeout review — complete

Produced `PIXEL-MELT-TIMEOUT.md`. Rehearsal settings are in native range and exactly match all non-opacity values in two earlier successful sampled/full-mix audit records. No source-backed reason proves these maxima cause the timeout. Trigger had not been reached; no post-IN native state was persisted before snapshot failure. Before-state already had Pixel Melt enabled; cleanup confirms zero/bypassed. Advise root to keep it unverified/parked and distinguish snapshot failure from renderer failure if revisiting. No live actions or shared changes.

## Fresh route follow-up — complete

Produced `ROUTE-FOLLOWUP.md`; visually reviewed rgb-review.png and rgb-cleared-4.png and checked phase native readbacks. Direct-input RGB sampled response/recovery now verified by root evidence. Fresh XML/active native clip matching shows Sculpt Input1:1 (previously verified first-group mapping), Input Opacity=true; Delay Input3:5 also opacity-following but semantic endpoint requires native confirmation. Official installed Router help confirms pre/post-fader meaning. Black isolated captures with upstream faders zero do not prove a fault. Minimal next root config: Figure1 + first group1 + Sculpt1, other faders0, source moving, incremental known RGB response; no token edits. No live actions.

## Authorized Melt UI implementation — complete

Per root's explicit expanded file authorization, edited only `sp/engine/workspace.js` and `sp/engine/test_workspace.cjs` in shared code. Rack detects boolean MELT_LOCK and adds Hold melt (`fx_bool_press` / `fx_bool_release`, name MELT_LOCK, exact captured key/instance) and Latch melt (`fx_param`, inverse of fresh native boolean). Latch aria-pressed follows readback without optimistic mutation. MELT_TRIGGER remains its separate one-shot event, labeled Trigger melt.

Hold releases on pointerup/cancel/lost capture, keyboard up, local/global blur, pagehide, disconnect and rack disposal/schema/instance change. Stale target presses and disconnected toggles rejected. Pointerdown followed by synthetic click does not duplicate latch or trigger actions. Existing strobe release registry reused; final pagehide disposal also drains held releases.

Checks: `node --check sp/engine/workspace.js` passed; `node sp/engine/test_workspace.cjs` passed **39 offline DOM checks** (34 existing + 5 new). Log: `sp/show-day/effects/melt-ui-checks.txt`. No live app controls, backend edits, CSS edits or other shared file edits. Root owns backend integration and visual/live verification. This implementation does not automatically enable effect opacity when MELT_LOCK changes.

## Installed SP Delay history — complete

Produced `DELAY-HISTORY.md` and `DELAY-GRAPH-EVIDENCE.json`. Exact graph traversal: 480 main texture-frame delays +16 RGB, acyclic, maximum496 stages to output; no connections to any Delay reset. Home chooses tap pattern, not clear. Time arithmetic uses fixed450/BPM grid conversion;8-second main capacity holds at60 evaluated fps only. Initial retained Shell is consistent with unreset/suspended history, not route-fault proof. Advise root >496 actual active evaluations and require fresh Capsule echoes; no live/shared changes. Visually reviewed remaining-review.png and matched layer phase evidence.

Root's45-second warmup follow-up: independently viewed delay-warmed-on.png; white Capsule echoes only, old Shell absent. Fresh feed reaches Delay and previous history was replaced. No graph repair indicated; exact flush time not measured.

## Hands-on Delay control access — complete

Produced `DELAY-CONTROL-ACCESS.md`. ColourLoop exists globally, DelayRGB on Sculpt; neither on Delay layer. Delay source R/G/B are SPDelayChain frame offsets. Original mapping intentionally sends motion stack (Invert/AutoMask) to Delay and fill+color (includes DelayRGB) to Sculpt; no original combined Delay-local ColourLoop/RGB stack exists. Minimal no-stack-change proposal is explicit scoped A/B effect selection/access. Optional new local DelayRGB insertion has original subchain order Invert→DelayRGB→AutoMask; local ColourLoop placement cannot be claimed from original evidence. Exact original ColourLoop values recorded; original layer DelayRGB sparse XML has no explicit inner values. No live/shared changes.

Final navigation proposal added to DELAY-CONTROL-ACCESS.md: source note + Delay controls button pins existing SPDelayChain in B; related scoped RGB delay · Sculpt / ColourLoop · Composition links; source pattern strip moved to effect side only. Saved active inventory has exactly one of each target; native/display name variations and strict uniqueness/stale callback rules documented. A and rack unchanged, no native commands. UI/blackout owner implements; no shared edits by effects audit.

## Final Delay ownership check — complete

Produced DELAY-OWNERSHIP-CHECK.md. Stable deduplication exists in EffectMotion.refresh: numeric IDs already in CLIPS source slots are excluded. Saved Delay source has6 slots, effect motion has0. Open all therefore has no duplicate effect writer in that state; effect manual aliases route through matching source slots. index_slot_owners/claim_slot/current_controller alone do not enforce uniqueness (last-entry index, per-slot claim, object-current check); no captured discovery-race overlap or jitter causation established. Read-only review, no shared/live changes.

## User correction: Delay's own color — complete bounded trace

Produced DELAY-OWN-COLOR-HISTORY.md and DELAY-HISTORICAL-STACKS.json. Supersedes prior cross-layer shortcut recommendation. Concrete September7 native Delay SPDelayChain snapshot has own R2/G3/B4 (plus Taps6/Span16/Glide2.34992); installed graph retains that RGB stage. Current source-owned R/G/B have drive controls while effect aliases can be manual-only, so effect-only navigation may hide own cycling access. Located real SP Loop Color and Study Color cycling shader sources, but no saved combined Delay wiring found; missing dedicated Color Loop remains open rather than dismissed. Read-only, no shared/live changes.

## User resolved ColourLoop scope — historical search stopped

Root owns adding an independent native ColourLoop after existing Delay layer effects; global instance unchanged. Only known mapping gap: saved native schema names are Factor, Offset, Red offset, Green offset, Blue offset (all numeric0–1), Opacity (separate envelope), and Black & White (boolean). It contains no literal Loop Amount or Channel Offset aliases. Do not map Loop Amount to Opacity or collapse three channel offsets into one without native label confirmation. Existing effect discovery should expose all five numeric controls as independent Smart Params on the new layer-local instance; Black & White remains manual. Source-duplicate exclusion does not apply to fresh layer-local parameter IDs. No historical work or shared/live edits continued.
