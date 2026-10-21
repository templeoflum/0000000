# Final show save — root executable checklist

Only root performs live cleanup/save. This task has made no live changes. Root now reports the exact scratch ID cleared after confirming the actual name/source Heart Capsule and disconnected L2C108. Do not repeat cleanup unless fresh evidence requires it. A retained empty slot ID is acceptable; other clips named Heart Capsule must remain usable.

1. **Identify scratch before cleanup.** Fresh GET `/api/v1/composition/layers/2/clips/108` (Arena port 8080). Expected rehearsal scratch: clip id **1788780038810**, name **Heart Capsule**, source description **Heart Capsule**. Confirm all three and correct composition/layer; coordinate alone is insufficient. Existing `integration/rehearsal/rgb.py` also asserts the ID and source before using this scratch. If identity differs, do not delete the new occupant: inspect and locate the known scratch. Restore the intended Sculpt active clip/output before root removes the confirmed scratch. Verify its absence in a fresh composition read and ensure the original Figure Capsule remains usable. No cleanup command is supplied here to avoid acting on stale occupancy.
2. **Settle and freeze selection briefly.** Release momentaries/gestures; choose desired Hold state; wait for transitions and patch operations to finish. Read current composition identity and record epoch time. Pick `Heart Departure 20260909 HHMMSS`; ensure `sp/engine/patches/<name>.avc`, `<name>.json`, `<name>.json.tmp` and the proposed backup directory are absent. Do not reuse Start or an original composition filename.
3. **Use current protocol once.** Heart UI **Setup / recovery → Save setup…**, or send `{"cmd":"patch_save","name":"<name>"}` to the existing Heart socket 8766. This uses the serialized PATCH_OPS path, native preflight/dependency validation, Arena save, and atomic companion JSON replacement. Wait for patch operation completion plus `Saved patch <name>` evidence; a sent command alone is not success. The pair itself is not atomic. Do not change clips during save.
4. **Read-only final checks.** Capture fresh GET `/api/v1/sources`, `/api/v1/effects` and `/api/v1/composition` into root's integration evidence directory. Run the command below using those JSON paths and the recorded epoch time. It parses/checks the pair, matches final native dependencies, compares live signature, checks the known scratch ID has no source content, checks timestamps and records hashes. Require exit code 0; review reported Hold/bars/active layers. If failed, inspect the partial result and save under another fresh name after fixing the actual cause.
5. **Backup verified pair and companions.** Follow SAVE-MANIFEST.md into `sp/show-day/integration/backups/<name>/`, preserving originals and wrapper IDs. Verify destination SHA-256 hashes match; preserve selected media/runtime paths. If choosing Use as Start, do it after verification and include the resulting surface.json. Record actual paths and rehearsal outcome. Do not use `_recovery.avc` as the durable backup.

From the workspace directory (replace angle-bracket placeholders):

```sh
sp/engine/.venv/bin/python -B sp/show-day/recovery/verify_show_pair.py \
  'sp/engine/patches/<name>.avc' \
  --sources 'sp/show-day/integration/<fresh-sources>.json' \
  --effects 'sp/show-day/integration/<fresh-effects>.json' \
  --live 'sp/show-day/integration/<fresh-composition>.json' \
  --after <save-start-epoch-seconds>
```

This verifier imports only offline patches/dependencies helpers, does not contact services and does not write files. It does not perform a reload, verify actual rendered media, prove full inactive-library readiness, or preserve feedback buffers. Runtime IDs may change on reload; XML nonempty scratch ID check supplements, not replaces, fresh live cleanup verification.

Departure blockers are limited to: wrong live target or unresolved scratch identity before cleanup; a save/verification failure; missing dependencies/media required by the **chosen** show set; or an unresolved failure from root's actual rehearsal. Portal's unselected missing videos, optional OSC mapping and untested legacy sources are not automatically show blockers. No new live departure blocker is established by this document-only task.
