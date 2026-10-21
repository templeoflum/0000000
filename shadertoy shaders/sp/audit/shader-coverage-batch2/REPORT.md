# Shader coverage — batch 2

2026-09-08. Six native shaders tested through existing Heart Smart Params. Original shader files and composition layout preserved. This is a rendered/control pass and a restrained starting configuration, not exhaustive shader acceptance or a frame-rate certificate.

| Field clip | Source | Numeric checks | Starting drives |
|---|---|---:|---|
| L3C17 | Cuadricula rect | 20 | warp + rotate |
| L3C18 | data blocks | 26 | shift + density |
| L3C28 | RailroadTracks | 14 | curve1 + intensity |
| L3C31 | RetroTechnicolorComputer | 16 | hue + saturation |
| L3C32 | SmoothXORi | 18 | intensity + tint |
| L3C33 | TruchetDualLevelSpin | 22 | thickness + glow |

## Delivered

- Calm Home pose saved for each clip, using the existing Home mechanism. Previous Homes backed up to homes-before.json.
- Restrained drive ranges and two-control combinations configured through existing Smart Params. Open retains its full-exploration behavior; these are starting combinations, not a change to Open.
- Final choices persisted per clip; relaunch-results.json verifies which drives survive leaving/relaunching.
- Exact native poses and drive ranges in relaunch-results.json; intermediate tuning, acknowledgement and Home checks in tuning-results.json.
- No new modulation engine, preset system, production UI changes, shader rewrites, or layer moves.

## Verification and limitations

All 58 numeric controls were tested at normalized .25 and .75 through Heart and read back in Resolume's native units. First pass: 114/116 acknowledged within the bounded window. RailroadTracks curve1 freq .75 and RetroTechnicolorComputer size .25 did not; both passed targeted resends during tuning (recorded in tuning-results.json). These misses remain in live-results.json and are an unresolved intermittent delivery/acknowledgement issue. Do not claim every command is reliably instantaneous.

Tuning set and acknowledged all 58 Home values. Home returned 58/58 values and stopped every Heart drive. Both selected drivers varied in native readback for all six sources. Source-internal TIME motion continues at Home where present; Home stops Heart modulation rather than freezing the shader's internal clock.

36 full-output PNGs from the control pass and 24 initial tuning PNGs were visually reviewed. The tuned Truchet brightness was subsequently revised and captured separately. Clip effects remain in the output chain; composition/Field effects settled out, only Field visible. These are rendered snapshots, not thumbnails, but sparse sampling does not establish frame-by-frame smoothness. No GPU stress conclusions, resolution sweep, or Figure containment guarantee.

Local qwen3:8b extracted six schemas, passing all 12 exact control-list checks; unloaded before rendering. Source code independently inspected for the six installed ISF resources. No visual conclusion delegated to the text-only worker.

## What the rendered checks showed

- Cuadricula: graphic monochrome tiles and curved grids. Warp and tile rotation provide strong structural motion; lower tile count makes the starting pose legible. Rotation .25/.75 can look similar because the rectangles are symmetric; numeric acknowledgement alone is not distinct visual behavior.
- Data blocks: horizontal digital/noise bars; shift changes stripe occupancy and density changes coverage. Keep grid, seed and rate steady for the first motion combination. The polar boolean is still outside continuous Smart Params; curve controls depend on that mode.
- RailroadTracks: a receding track with a clearly readable horizon, steering and brightness. Modest curve amplitude and a steady travel speed preserve the scene.
- RetroTechnicolorComputer: block grid with color variation. Keep size/matrix steady. The installed source explicitly rounds TIME-based progression and floors size, so stepping is inherent to this shader, not automatically Heart jitter. Starting hue/saturation changes do not promise continuous geometry.
- SmoothXORi: layered square/noise textures. Intensity changes occupancy/brightness, tint changes color; steady scroll/rate/seed avoids extra instability. The source uses floor/fract/hash structure, so it is not a pure continuous warp.
- Truchet: curved tiled contours. Thickness and glow provide a readable pair; equal fixed spin x/y avoids the extra scaling introduced by using cos(TIME*x) and sin(TIME*y) at unequal rates. Final thickness .32, glow .75; driven thickness .22–.42 and glow .6–.85. This is a source-informed setting, not a rewritten or exhaustively proven shader.

The TIME-multiplied speed controls in several inspected sources can jump phase when changed. This explains a class of chaotic behavior, but is not a proven diagnosis of Melty Boi specifically. User feedback supports intensity-only for Melty Boi; its file/settings were not changed in this batch.

## Next

Continue the enrollment ledger, prioritizing a Figure batch with full source/containment checks and clearly separating field-like candidates. Record discrete/glitch shaders as such instead of promising every source can provide continuous geometry. Boolean/trigger/color exposure and intermittent command acknowledgement remain explicit gaps. Do not return to broad surface polish while content coverage remains incomplete.
