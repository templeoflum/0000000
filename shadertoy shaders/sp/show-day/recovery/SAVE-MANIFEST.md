# Show save and recovery manifest — 2026-09-09

Prepared while the coordinator rehearses. No show save, backup copy or live action was performed by this task. The coordinator reports the launcher identity patch integrated, with 13 integrated tests and passive real-service recognition passing.

Workspace root: `/Users/donovan/work/0000000/shadertoy shaders`.

## Save destination and companion files

Choose a fresh name such as `Heart Departure 20260909 HHMMSS`, replacing HHMMSS with actual local save time. Check that **both** corresponding files and temporary JSON are absent before submitting the save. Existing save code permits overwrite; uniqueness is a required coordinator check, not a built-in guarantee.

The operative pair belongs at:

- `/Users/donovan/work/0000000/shadertoy shaders/sp/engine/patches/<fresh name>.avc`
- `/Users/donovan/work/0000000/shadertoy shaders/sp/engine/patches/<fresh name>.json`

The AVC contains the native composition. Its JSON companion contains version/name/composition filename, bars, Hold state, captured source relationships/slot configurations/poses/drives, Heart-owned effect motion, active clips/levels/bypasses, composition signature and dependency/routing contract. Neither file alone reproduces the full instrument.

Keep these exact existing controller companions with the pair, preserving their filenames under `sp/engine/`:

| Files | Recovery purpose |
|---|---|
| `atoms.json`, `motion.json` | Persisted source slot/global configuration |
| `home.json`, `sweetspots.json` | Saved Homes and factory/rest profiles; preserve user Homes |
| `presets.json`, `armsets.json` | Variations, armed scope and saved arm sets |
| `fx.json` | Effect modes, envelope timing and configuration |
| `surface.json` | Workspace arrangement, banks, Start selection and mirrored pad settings |
| `controls.json`, `native_sources.json`, `instruments.json` | Control/source metadata and instrument definitions |
| Entire `performance-presets/` directory | Named JSON performance states; these supplement the AVC/JSON pair |

Also retain the **matching code version**: `sp/start.sh`, `sp/launch.py`, all engine `.py` modules, `status.html`, `workspace.js`, `workspace.css`, `sp/lab/trackpad/mt_probe.py`, and the monitor code/resources/binary. Easiest small code backup is the controller tree with large environments/media excluded and their dependency locations recorded separately. Preserve existing `sp/engine/patches/` pairs if older setups must remain recoverable. `progress.json`, logs, bytecode and telemetry are evidence/diagnostics rather than required performance state.

`surface.json` is more useful than relying on browser storage: workspace, banks and Start are saved there, and pad changes mirror into it. Still verify pad assignments after reload; no browser-data export has been performed.

## Assets outside the workspace

- **Wire patches:** `/Users/donovan/Documents/Resolume Wire/Patches/<patch name>/` — preserve each selected patch's `.wire` file and its entire `Resource/` directory, including shader `.fs`, textures and any other referenced resource. `Heart Capsule/Heart Capsule.wire` and `Heart Capsule/Resource/` are an inspected example. Identify the actual required set by native plugin IDs in the newly saved AVC and current installed-source/effect inventories, not by display names alone. The patch contract covers active instruments and relevant effect stacks; inspect inactive clips too if their future selection must work. No exact final set can be asserted before the coordinator's save.
- Keep original IDs: `sp/build_wrapper.py` retains an existing wrapper identifier when present but creates a fresh UUID without it. Rebuilding only from `.fs` is **not** an equivalent backup of saved composition bindings.
- **Arena:** `/Applications/Resolume Arena/Arena.app`; preserve required native plugin installations and the current version record. `/Users/donovan/Documents/Resolume Arena/Extra Effects/` exists, but its contents alone do not prove Mac plugin availability; use fresh installed inventories.
- **Mappings/output:** preserve `/Users/donovan/Documents/Resolume Arena/Shortcuts/` and selected files from `/Users/donovan/Documents/Resolume Arena/Preferences/`: `AdvancedOutput.xml`, `SimpleOutput.xml`, `slices.xml`, `midi.xml`, `osc.xml`, `dmx.xml`, `recentLayout.xml`. Record relevant Web Server/output settings separately without exposing credentials. These global settings are not all contained in a composition; do not restore them over a live session automatically.
- **Portal/Treehouse if selected:** restored AVC files at `sp/restored-compositions/portal.avc` and `treehouse.avc`; actual media paths under `/Users/donovan/work/Visuals/`, especially `infra/`; named MIDI files under `/Users/donovan/Documents/Resolume Arena/Shortcuts/MIDI/portal.xml` and `treehouse.xml`. Use PATH-INVENTORY.json and PORTAL-RECONCILIATION.json. Portal still has 139 unresolved identities and five unapproved existing alternatives. Do not copy or relink an entire media library blindly.
- **Runtime:** engine venv at `sp/engine/.venv/` requires external `/opt/homebrew/opt/python@3.14/bin/python3.14`; inspected Python 3.14.6 and websockets 17.1. `sp/monitor/Heart.app` requires the Syphon framework at `/Users/donovan/work/0000000/shadertoy shaders/sp/preview/.venv/lib/python3.12/site-packages/syphon/libs/Syphon.framework`. Its absolute binary search path must remain valid or be rebuilt deliberately. A copied venv/app is not a standalone installer.

## Existing save method and its limits

Use Heart **Setup / recovery → Save setup…** with the fresh name; this dispatches `{"cmd":"patch_save","name":"<fresh name>"}` through Heart's existing serialized operation queue. Avoid importing the running engine into another process or independently calling its save function.

`sp/engine/heart.py:1285` (`patch_save`) captures controller/layer state; fetches installed source/effect inventories; calls `capture_native_snapshot` on `_save_preflight.avc`; builds/checks the native dependency/routing contract; saves the new AVC through Arena's `/composition/save`; writes the JSON companion via a temporary file and atomic replace. `capture_native_snapshot` removes its previous scratch file before requesting a fresh save and restores the visible composition name only if the composition ID still matches. This is existing project code, not a new save implementation.

Important bounds: `_save_preflight.avc` is a deliberately reused scratch path. The final pair is not written as one atomic transaction, and save success alone does not prove final AVC freshness/parseability or that no external composition change occurred during save. Leave selection/motion controls untouched during this short operation, wait for completion, and validate the final pair. The final save may change Arena's visible composition name/path; inspect it rather than assuming it stayed unchanged. No load/restart is needed to save.

Do **not** select Load composition, recall Start, overwrite an original Documents composition, or set a new Home to make this backup. Changing Start selection is optional and should occur only after the fresh pair is verified. `_recovery.avc`, `_route_readback.avc` and `_save_preflight.avc` are overwritten scratch files, not durable backups. Feedback history, transient held input, undo history and exact continuous transport phase are not reproducibly restored by the pair.

## Backup location and validation

Recommended new backup directory, created by the coordinator only:

`/Users/donovan/work/0000000/shadertoy shaders/sp/show-day/integration/backups/<fresh name>/`

Keep the validated AVC/JSON pair, `engine-config/` companions, selected wrapper folders/resources, a file list with SHA-256 hashes, runtime/version/path notes, and the rehearsal result here. Use a fresh directory and fail if it already exists. This small local backup protects against accidental edits; it is not protection against losing the laptop. A second existing travel drive/location can receive the verified package when the user/coordinator identifies it; no external destination is assumed here. Large media remain in place with exact path inventory unless specifically required for travel.

Specific coordinator steps:

1. Confirm live composition identity, settled intended source/layer selection, released momentaries, no clip transition and no active patch operation. Record the fresh state/signature and current installed inventories. Choose the desired saved Hold state deliberately.
2. Check the fresh output pair and backup directory do not exist. Record a pre-save timestamp and hashes of any originals whose preservation is being asserted.
3. Submit one **Save setup** using the existing queue. Wait for its completed status; on error, inspect any partial pair before retrying with another fresh name. Do not blindly retry over existing files.
4. Confirm both files exist, are nonempty and newer than the start time. Parse XML and JSON; check JSON version/name/composition filename, source/effect states, bars/Hold and active layer selection. Run `patches.validate_snapshot(avc, data['layers'])`; rebuild/compare the dependency contract against the final AVC using `dependencies.validate_contract(data['dependencies'], avc, sources=fresh_sources, effects=fresh_effects)` for an **offline** check. Compare fresh live `composition_signature` to the saved signature. Treat any mismatch as a failed save, not as permission to overwrite originals.
5. Check expected native IDs, dimensions, ordered layers/effects and all required media/shortcut paths. An offline contract pass is not post-reload routing or playback verification. Keep the owned live rehearsal result separate; any disruptive restore rehearsal must remain coordinator-controlled.
6. With gestures idle, snapshot companion JSON files and verify parsing. Hash before/after copying to detect files changed by persistence during the copy; retry only those changing files after a quiet interval. Copy into the fresh backup directory and verify destination hashes. Hash selected wrapper resources as well. Do not copy live temporary/lock files as state.
7. Verify protected originals' hashes unchanged; record the actual saved pair, backup location, asset exceptions and unverified recovery limits in the integration handoff. If choosing **Use as Start**, do it now and recopy the resulting `surface.json` into the backup.

Checks for this manifest: read-only inspection of save/recall, settings persistence, performance-preset and wrapper code; bounded directory/file-name inspection of Arena preferences and a Heart wrapper. No save/copy/restore test was run here. Root's reported launcher test results are attributed above rather than claimed as this task's tests.
