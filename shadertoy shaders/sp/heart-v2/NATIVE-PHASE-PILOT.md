# Native ranges and automatic phase control

Resolume owns the look, In/Out and timeline programs. Heart supplies phase. The performer accepted the Shell pilot; the same rule now applies to discovered numeric source, effect and native parameters. There is no hardcoded parameter list or phase opt-in file. The server no longer loads historical imported clip profiles.

## Playing

- Set a parameter to Timeline and pause it in Resolume. Set its In/Out there.
- Heart automatically detects prepared parameters and starts their drives when armed. Drive off holds the phase and stays off through rescans. Unpausing a native timeline releases Heart’s drive; pausing it again prepares and starts a new drive.
- Static parameters remain manually adjustable from Heart. Running timelines and other native animation modes do not become Heart drives. An explicit manual adjustment retains the existing manual-takeover behavior.
- Heart provides Drive, Family, Rate, Amount, Shuffle and typed multipliers, including `0.025`, negative fractions and zero. Bulk Drive affects prepared, unlocked parameters only.
- Low/High show native bounds and are read-only. Native range edits apply directly; Heart does not widen them or apply the bounds a second time. Home and Base/Safe retain relative phase without restoring native In/Out or timeline programs.
- Save clip/effect settings through the normal Resolume composition save. Heart relationships remain runtime controls. Save/reopen was not exercised in this batch.

Detection runs while armed or idle. It inspects at most 96 numeric parameters per pass, prioritizing the selected target and already prepared timelines, with capacity reserved for background discovery. Selected mode changes typically appear within a few seconds; the initial large-composition sweep takes longer. Refresh after adding/reordering layers or effects. Playing clip changes are discovered automatically.

## Transport and limits

The installed REST API does not expose writable phase position. Heart uses the existing localhost OSC input on port 7000. Addresses come from native object structure, effect-name occurrence and parameter names. User-removable effect controls include the native `/effect/` segment; their mix Opacity does not. Permanent Transform controls and source controls use their respective native paths.

Before each bundle, Heart reads the native effect by ID, parameter by ID, or addressed source clip and validates object ID, parameter IDs and hardware limits. Source reads also validate connected state. A changed or missing object stops those outputs and requests discovery. Pending output is cancelled when the binding changes or Heart disarms. Phase drives do not delete phase sources or write physical values.

Effect-by-ID validation does not independently prove the current positional OSC route after a structural reorder. Refresh the catalog after those edits. Validation and send are separate operations and cannot make a concurrent native edit atomic. Shell source routes and the second Figure Transform were verified live; every effect family has not been exercised.

Each Transform phase batch needs one small effect read (about 3.3 KB in this composition). Background discovery uses scoped parameter and active-clip reads. No native WebSocket or recurring full-composition reads were introduced.

Native envelopes remain in the phase path. Manual physical-value entry infers phase linearly from In/Out, so a custom envelope can change the resulting value; readback shows actual native output. Custom envelopes were not part of this live test.

## Evidence · September 12

`checks/native-phase-general/` contains the generic detector tests, isolated surface check, live verification and native snapshots. Figure's second Transform automatically detected Position X and Position Y with −400…400 ranges and Scale with 30…100. Their native values moved within those windows. The first, permanent Transform was unchanged, and the current Spike clip remained loaded.

- Play-to-release measured 1.34 seconds; pause-to-autostart measured 2.38 seconds.
- Explicit Drive off survived repeated detection. Static Rotation Z accepted a manual test value and was restored.
- Both Transforms’ captured native programs, In/Out and static values matched afterward. Three prepared Transform drives were left running in standalone Heart.
- The 157-test backend regression passed, followed by 53 affected checks including seven new generic detection/recovery cases. The isolated compact/wide surface sequence passed disabled unprepared Drive, read-only native bounds, static manual entry and `0.025×` input.
- Live timing: 9.22 ms p95 engine interval, 0.12 ms p95 engine work, 1.03 ms latest output-batch work, 200 ms background scan. These measure controller timing, not rendered frames.

Historical Shell evidence remains in `checks/shell-native-phase/`: ten verified source addresses, narrow/reversed native ranges, Drive off/resume, relaunch, native setting preservation and output cancellation checks. Rendered output and musical feel remain performer acceptance.
