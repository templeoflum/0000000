# Shader coverage — native enrollment, batch 1

2026-09-08. Priority: get existing content playable through existing Smart Params. No new modulation engine, shader rewrites, layout work, or preset architecture.

## Composition census

All three open decks inspected through Resolume's live API. Gradient contains 282 populated clips / 177 distinct video source descriptions. Both other decks are empty. These counts include routers and native generators; they are not 177 audited shader files.

208 clips expose numeric/choice source controls. Explicit native enrollment now adds 138 source descriptions, covering 184 clip instances and 1,090 Smart Params slots. Existing registrations and legacy SP controls remain in place. The remaining 74 clips have no eligible numeric source controls in this census; many are routers/feedback entries, not necessarily broken shaders.

`coverage.json` is the per-clip ledger, with exact source labels, parameter types/ranges and separate enrollment / rendered statuses. `deck-*.json` preserve the census inputs. Enrollment is not rendered acceptance.

## Implementation

`sp/engine/native_sources.json` explicitly enrolls native source descriptions. Heart merges missing entries into its existing ATOMS discovery using setdefault; saved settings take precedence. Missing controls use the existing undriven defaults. This makes controls available upon clip launch without enabling all drives or effects. Running atoms.json is not edited offline. Originals and installed shader files were not changed.

Source boolean/color/resource controls are not converted to continuous slots. These remain gaps where applicable (Gradient Bars has a `use columns` boolean). Native source trigger exposure is not certified here. Figure containment and appropriate layer placement are not established by enrollment.

## First rendered batch

| Field slot | Source | Numeric controls checked | Native readbacks | Driven render probe |
|---|---|---:|---:|---|
| L3C16 | ButterflyEffect | 8 | 16/16 | zoom |
| L3C20 | Gradient Bars | 10 | 20/20 | columns |
| L3C22 | Melty Boi | 7 | 14/14 | intensity |

Each numeric control was sent through Heart at normalized .25 and .75, checked in native units against Resolume, then returned to its prior value. Five readbacks of each driven probe varied. Two probe settings and two driven full-output frames per source were captured and visually reviewed (12 images, contact.jpg).

Observed: ButterflyEffect produces a frame-filling interference pattern with visibly different zoom states. Gradient Bars produces broad/full-height grayscale bands with changed column structure. Melty Boi produces a colored central rounded mass with surrounding rings and visibly changing internal distortion. Melty Boi's appearance in this sample does not certify Figure containment over all settings.

Field isolated via layer opacity, composition and Field rack amounts settled to zero. Clip-level effects remain part of the observed output. These are actual output captures, not thumbnails. Sparse samples prove output and parameter changes, not frame-by-frame smoothness, GPU performance, or all-input safety. Native time may continue during manual comparisons.

The first fixed .3-second readback pass missed four requests. Repeating with bounded acknowledgement (up to 1.8 additional seconds) passed all 50. Treat responsiveness as unquantified; do not claim an instantaneous latency pass.

## Quality checks / worker

- 208 engine tests passed (existing file-handle warnings remain).
- Every newly enrolled clip schema instantiated through actual Heart.Clip: 184/184, all expected eligible controls found, 1,090 slots total; persistence mocked to avoid offline state writes.
- Local qwen3:8b extracted three schemas: all six exact control-list checks passed. No visual judgments delegated to that text-only worker; model unloaded before rendering.
- Heart restarted with fresh state preservation, connected after broad enrollment, four active controllers, delivery queue zero at readiness.

Left Field L3C22 Melty Boi running with intensity driven; other layer opacities zero from the isolation checks. No restoration requested by user.

## Next batches

1. Render/check remaining enrolled source families, one source identity at a time, keeping per-instance native schema checks. All untested rows remain untested.
2. Prioritize rich controls: Cuadricula rect, data blocks, RailroadTracks, RetroTechnicolorComputer, SmoothXORi, TruchetDualLevelSpin. Record failures and move on.
3. Audit Figure candidates for edge contact independently, then copy/adapt shader identities as needed; original source → shared guarded Transform → creative stack. Effects can extend beyond frame.
4. Classify the no-numeric-source rows into routing/static generators/missing exposure. Expose boolean/trigger/color controls where required without pretending they are continuous knobs.
5. Use rendered behavior to propose layer moves; enrollment does not imply current placement is correct. Keep GPU tuning and surface polish secondary.
