# Effect controls, verification, and initial safeguards — 2026-09-08

## Delivered

- Rack event rows expose native ParamEvent/ParamTrigger controls, including LUT MELT/DECON and Pixel Melt actions. Exact effect-instance binding, disconnect disabling, no duplicate pointer+click firing. UI flash means sent, not native acknowledgment. Strobe remains a momentary Hold.
- Existing native Transform targets are separately accessible via the Transform rack mode and A/B selectors. Clip/layer/composition/group scope is named explicitly. No shader edits, effect insertion, reordering, or changes to original composition files. Verified independent Figure layer Position X write 0 → 80 → 0 through Heart with native readback.
- Open uses existing Smart Params with an effect-specific policy shared by per-target and global actions. Cloner scales stay within 20–100%; clone count, tails and delay amount retain their current pose. Iterate holds its three opacity-support controls at 1, preserves other structural settings, and drives only TransformStrength/Iterations (.1–.35) and global Z rotation. Manual controls remain available. These are initial operating safeguards, not a guarantee for arbitrary input/settings combinations.
- Transform Open holds the current pose instead of sweeping native ±16384 position / 0–1000% scale limits. Individual manual and drive controls remain available; source-aware automatic transform bounds remain future work. Existing Figure source framing safeguards remain unchanged; downstream effects may leave the frame.
- Repaired 32 saved controls from the original Feedback Machine values and 21 remaining repeated corrupt values using actual native factory reset/readback. All 53 writes verified. Updated 17 repaired Home poses, with a backup, so Home does not reintroduce those corrupt values.

## Actual visual checks

The first pass was contaminated by concurrent performance; not counted. A second pass exposed long release times contaminating subsequent checks. The isolated pass temporarily used short test fades and restored the user's fade settings afterward.

`isolated-pass/comparison.png` shows 18 before/on/off comparisons using a full-resolution asymmetric diagnostic source directly in Figure, Feedback and Sculpt, with the tested layer visible. Every off image exactly matched its own before image (mean pixel difference zero). Mirrors, LoRez, sharpening and kaleidoscope show visible operation. Several color controls were subsequently repaired again from native defaults.

`guard-pass/comparison.png` captures live guarded Open on Radial Cloner, Linear Cloner and Iterate: moving, nonempty output across the sampled frames, then original input restored. Subsequent Invert RGB and Hue Rotate samples show expected visible color changes. Alpha inversion in the original Feedback/second Sculpt Invert setting intentionally changes transparency and can look like a silhouette.

Native trigger commands were exercised through Heart during the guard pass; a real rack MELT click was separately observed arriving at the engine with the correct key and instance. LUT output visibly changes color. Pixel Melt was subtle on the static diagnostic source; this does not certify its full temporal behavior. Delay RGB needs a dedicated moving-input temporal check; a static image cannot establish channel delay behavior. Feedback/Sculpt checks validate their processors with direct diagnostic input, not every feedback routing configuration.

## Restoration and checks

`guard-pass/restoration-check.json`: original faders, layer bypass/solo, connected clips, hold state, fade configs all matched; temporary diagnostic clip slots cleared. Guarded Open was undone after each effect. Native Transform test restored its original value. Original shaders and composition files untouched.

34 offline DOM checks passed. Full Python suite and targeted Open/discovery tests passed; see final turn result for count. Artifacts include before/after native+Heart snapshots, original-value provenance, write readback logs, Home backup and rendered frames.

## Remaining limitations

No blanket guarantee against dead zones: manually chosen scales, geometry, histories, blend modes, and stacked interactions can still remove visible content. Radial's Transparent delay-fill setting can have history warmup gaps. The source Figure containment rule is distinct from downstream transformations. A separate source-aware framing policy and moving-input Pixel Melt/Delay RGB verification are still needed.
