# Departure readiness status

Started: 2026-09-09. Scope: read-only audit; outputs and staged proposals confined to `sp/show-day/recovery/`.

Examined: `sp/show-day/PLAN.md`. Auditing launcher/dependencies, monitor lifecycle and saved composition/media restoration. No live playback changes, app restarts, OS changes, shared edits or installations authorized for this task.

Checks and findings pending. Cold start and live recovery remain unverified until the coordinator grants/runs a live window.

Early findings: current Portal restored XML has 232 missing path occurrences / 144 unique missing paths; Treehouse has 0 missing across 1,591 path occurrences. These are existence checks, not playback verification. Engine Python and websockets import successfully. Monitor binary uses an absolute Syphon framework search path inside this workspace; copying Heart.app alone is insufficient. Launcher checks listening ports, not service identity, and only builds a missing binary. Focused offline checks next; no live actions.

Completed: offline audit and recovery handoff. Outputs: STATUS.md, PREFLIGHT-RECOVERY.md, MISSING-PATHS.md, PATH-INVENTORY.json, audit_paths.py. All in owned directory; no shared fixes or app changes staged/applied.

Checks actually run: current existence scan of 31 compositions; Python 3.14.6/websockets 17.1 import; native binary linkage; three shell scripts syntax-valid; monitor resume and pointer JavaScript regressions passed; 42 dependency/patch Python tests passed (existing unclosed-file warnings). Portal: 232 missing references / 144 unique literal paths. Treehouse: 0 / 1,591 references. 29 other compositions reference missing OSC shortcut OutputAllMessages.xml. Both Portal/Treehouse named MIDI files exist.

Unverified: cold launch, live service health, native orientation/resolution/reattach, actual sleep/process-pause recovery, current plugin installation completeness, media decoding and hardware mappings, sustained FPS, latest show save. Historical image byte checks not repeated.

Proposed integration: coordinator reads recovery card; verifies/saves today's show composition and companion state, checks installed plugins and optional missing OSC preset, performs one owned live reconnect/resume rehearsal; relinks/selects Portal missing videos only if required. Existing native binary must be explicitly rebuilt after source changes; app-only copying is not portable. No additional workers or recurring tasks created.

Follow-up started: stage launcher-only service fingerprint validation and mocked offline checks; reconcile Portal XML against recorded relink mappings and candidate paths. No shared edits, server connections or process actions planned.

Follow-up complete: staged launcher-identity.patch (only sp/launch.py), launch.proposed.py, stage_launcher.py, test_launcher_identity.py; added FOLLOWUP.md, reconcile_portal.py and PORTAL-RECONCILIATION.json. 13 mocked offline tests passed; git apply --check passed. Expected HTTP page + passive WS status checks reject unrelated/silent services before subsequent startup/open actions; no control commands, shared edits, live endpoint calls or process actions performed.

Portal clarified: all 290 approved recorded video targets exist and are referenced, so no stale pre-relink XML gap found. 144 unresolved identities = 139 historically not found (no exact known-mirror hits) + five existing unapproved candidates. Historical GLK VISUALS V4 FINAL.mov is no longer referenced. Counts including paired VideoFile/value fields are 464 occurrences / 288 literal spellings / 144 normalized paths. No broad scan or relink. Coordinator should review/apply launcher proposal, verify in its live window, and review Portal candidates only if needed. Real service recognition under full show load and playback remain unverified.

Save-manifest follow-up started. Coordinator reports launcher integrated: 13 integrated tests and passive real-service recognition passed. Reading existing patch-save, snapshot, settings and wrapper code; preparing root-only save/backup steps without live actions or copies.

Save-manifest complete: SAVE-MANIFEST.md lists AVC/JSON pair, exact settings companions, wrapper/resource identity preservation, external runtime/media/mapping paths, existing serialized Save setup method, fresh integration backup destination and seven root validation steps. Flags non-atomic pair save, mutable scratch files, preserved-original hash checks and offline-vs-live contract limits. Only read-only code/path inspection performed; no live save/copy/restart/shared edit. Final selected dependency set remains root-owned until its new show save exists.

Final-checklist follow-up complete: FINAL-SAVE-CHECKLIST.md and read-only verify_show_pair.py added. Checklist identifies root scratch L2C108 / id1788780038810 / Heart Capsule Sculpt / Heart Capsule by fresh identity before cleanup; uses existing queued patch_save protocol and fresh-name protection, final pair/contract/live-signature validation and hash-verified companion backup. No live calls, mutations, shared edits or restarts.

Checks: verifier CLI loads; strict current-protocol verifier correctly rejects historical Feedback shaping companion missing effects/dependencies. A temporary owned-directory copy augmented with current required effects/derived dependency fields passes offline integrity checks; deliberately wrong companion filename is rejected. Temporary fixture removed. No final show save verified yet; root must execute with fresh inventories/live readback. No new departure blocker established; selected-show missing assets or actual rehearsal/save failures alone are blockers.

Scratch correction applied: root observed actual clip name/source Heart Capsule, ID1788780038810 at disconnected L2C108, and reports that exact ID cleared. Earlier 'Heart Capsule Sculpt' label was incorrect. FINAL-SAVE-CHECKLIST.md now reflects this and says not to repeat cleanup blindly. verify_show_pair.py no longer matches names; it rejects the exact scratch ID only when a VideoTrack/AudioTrack PrimarySource contains source content. Native empty Clip nodes and empty PrimarySource containers pass. test_scratch_identity.py passed offline cases for retained empty ID, empty container and rejection of nonempty source. No live actions/shared edits performed.
