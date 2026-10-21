# Stage motion

Perform places Stage motion between the effect rack and Drives. Each section has Family, Mult, Shuffle and an active-drive count. The whole-stage row provides the same controls. Shuffle stage includes the declared stage’s layers and shared effects. Family and Shuffle are disabled without active unlocked prepared drives. Mult remains available for valid scopes so future prepared drives inherit the chosen speed.

The user prepares and pauses native timelines in Resolume. The panel does not change animation mode or ranges. Shuffle uses the existing relationship variation: active unlocked drives change ratios/phase offsets or family assignments, while keeping family, Amount/Rate, multipliers, shapes, native In/Out, native programs and Drive states. Idle and locked parameters stay unchanged.

## Scope

Stages are recognized by the existing native `__stage__` group convention. Actual native group membership determines the whole-stage scope. Section labels and member IDs live under `stage_motion.groups` in `effect-rack.json`; this config stores no parameter ranges or timelines. Current sections: Base, Background, Blades, Squares, Balls, Rings, Outline and Shared effects. A section with a missing or moved member becomes unavailable. The separately placed stage mask and all non-stage layers are outside scope. Unconfigured stages fall back to one section per native member layer.

Shared effects selects only effects and controls on the stage group itself. Layer sections include their native controls, current source and effects, but only prepared active unlocked parameters can change. A stale composition epoch or unknown section is rejected before any shuffle. Regular non-stage Drive-bank behavior is unchanged.

The backend publishes compact counts independently of editor selection. Displaying this panel does not add native subscriptions or periodic full-composition reads. Structural edits still require Refresh as documented for native phase routing.

## Verification · September 12

- Five scope tests cover section/whole-stage boundaries, other stages and outside layers, locked/idle/unprepared controls, changed membership, stale commands, disarm and unwatched summaries.
- 25 motion/detection checks and 31 output/recovery checks passed. The compact/wide mocked Perform sequence includes both Shuffle commands and disabled states.
- Standalone Rings Shuffle changed only its five active relationships. Shuffle stage changed all 16 prepared layer relationships. All 16 native values moved; their ranges, exact paused program objects, multipliers, shapes and Drive states were preserved.
- Latest live controller metrics: 9.3 ms p95 tick interval, 0.45 ms p95 work, 5.48 ms latest output-batch work and 211 ms background scan. Rendered musical feel remains performer acceptance.
- Reload retained the exposed ratio, multiplier, phase offset and shape settings of 31 active prepared parameters. No native timeline was paused or otherwise edited by the installation.

Evidence: `checks/stage-shuffle/`. Native composition saving remains a user action.

## Scoped Family and Mult update

Family assigns distinct positions across the active unlocked prepared members of a section or whole stage. A later section Family action overrides only that section; the whole-stage selector shows Mixed when member families differ. Shuffle preserves the effective family and redistributes its existing positions. An explicit target Family edit clears that target’s stage family assignment.

Stage Mult stacks with Global, source and per-parameter rates. Section Mult also stacks with whole-stage Mult. Native ranges remain in Resolume. See [Motion multipliers](MOTION-MULTIPLIERS.md) for controls and current verification limits.
