# JSON-only performance presets — September 8

The main performance bar now uses Save preset / Apply preset / Undo preset and a
0–30-second transition field. Existing whole-composition patch controls are inside
collapsed Setup / recovery; their Load composition action explicitly reloads Arena.
Old .avc patches remain intact. They are not silently relabeled lightweight presets.

New files live in sp/engine/performance-presets, one JSON per named preset.
Live warp is the first saved example (~32 KB). It contains scoped active adapted
source controls, Heart-owned effect controls, effect envelope targets, and global
motion relationships. Each control records identity, pose, Drive, range, ratio,
multiplier, offset, shape and lock. Tempo, routing, clip activation, fader levels,
and unowned effect parameters are outside this first performance-preset scope.
This is not a complete composition snapshot. Switching to a different source is
still a separate clip action; missing preset targets are reported and skipped.

Apply resolves/validates settings first. Already-owned controls do not make native
ownership calls. Newly owned controls are prepared before the short synchronized
motion commit; unrelated motion continues. Retargeting preserves integrated phase
and blends from current effective settings. The engine runs normally throughout;
no PATCH_OPS, composition save/open, reconnect, or clip relaunch occurs. Runtime
settings persist in one batch after commit, not once per setting. Preset names are
cached for two seconds instead of scanning the filesystem at status cadence.

The native effect envelope retains its existing attack/release settings; the preset
transition duration governs parameter motion. Discrete source choices cannot be
continuously interpolated like a scalar. Undo covers the saved source/effect scope,
not destructive feedback-history changes. Old Home/legacy variation and full setup
paths remain separate implementations; this change does not rewrite all of them.

Validation: 161 Python checks pass (including seven new JSON-preset tests), 24
workspace checks and fader checks pass. Tests cover JSON persistence, phase-preserving
morph, missing targets, invalid settings before ownership, replaced targets and Undo.
Live test altered Cloner End Scale Hi, applied Live warp, and verified restoration
while Arena composition identity stayed identical, connection stayed true, no setup
operation ran, and Heart turns advanced across 27 status samples. Repeated after
batched-persistence change. Original Hi .38 restored through the JSON path after
testing. Native AX verified the new bar, selected Live warp, collapsed setup tools,
Resolume connected and 9 drives running. Engine PID 23308 after final upgrade.

Limits: this verifies no composition interruption, not a claim of universal zero
latency or fully rendered smoothness under any GPU load. Existing legacy presets
still use their original apply path. Scope expansion should reuse this JSON path,
not route performance actions back through full composition recall.
