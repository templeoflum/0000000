# Clip starting points

Figure and Field now start with ordinary Heart drives. Saved timeline In/Out values from **feedback machine.avc** become Heart Low/High. Heart approximates the original timing with musical ratios; Family, Rate, Shuffle, locks and range dragging remain available. **Reset clip** restores that clip's starting controls and ranges. Revisiting a clip starts it from that baseline.

Static controls retain their baseline values and stay out of bulk Drive until a range is opened. Their value sliders still allow manual adjustment. Shared layer movement, MIDI mixing, masks and clip transitions remain separate.

The compact grid shows one entry per shader: **63 Figure / 106 Field**. A count button opens its versions. Previous, Next and Random step between shader families. All 208 native slots remain available; original variants and materially different repaired shaders have not been deleted or collapsed into one program.

The reference import contains 178 matched programs and 321 original timelines. The prepared set now covers 246 clip baselines, including all 208 current Figure/Field clips, with 339 motion controls across the complete set. Controls absent from the saved files use an explicitly marked current baseline. Matching controls in repaired copies inherit original values/ranges. Heart Melting Fractal uses documented renamed controls; its Fold Offset interval is translated into, and limited by, the repaired shader's geometry range. These repaired sources already differ visually from their originals.

The original and resized Feedback Machine files have identical imported Low/High ranges. The original file is now the reference. Baselines validate source/effect identities and parameter types/limits before writing; they do not reconstruct missing effects or change native layer organization.

## Rack

- **LUT on/off** controls whether LUT Corrupt is enabled. **Decon** fires its native event only while enabled; it does not change opacity or bypass.
- **Pixel Melt on/off** controls MTK_PXLMELT's native MELT_LOCK latch. The effect stays enabled at full opacity when the latch is released.
- **Color** retains each row's ColourLoop control. **Clear** switches LUT off, releases Melt and clears Color. Field + video remain linked through Heart.
- **Tap** and Downbeat continue to control native tempo.

## Verification

- 97 backend tests passed; six affected launch tests passed after fixing stale eject status.
- Compact/wide mocked UI checks cover normal motion controls, grouped variants, separate LUT enable/trigger, Melt latch, keyboard repeat and offline guards.
- All 246 prepared baselines validated against current native parameter identities.
- Live parameter checks and their exact coverage are recorded in `checks/deep-clean-live.json`. Rendered acceptance of the entire library remains open; Figure's native mixing opacity was zero during output inspection.

Historical native-only Shuffle and opacity-pulse tests are superseded by this behavior. Reference compositions on disk were not modified. The working Resolume composition has not been saved by this task.
