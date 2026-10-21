# Saved-path findings — 2026-09-09

Current filesystem existence inventory: 31 saved compositions. Full exact paths and occurrence counts are in `PATH-INVENTORY.json`; rerun `audit_paths.py` with the engine Python to refresh. This checks XML fileName/path/filePath attributes and named shortcut files, not decoding, image-sequence completeness, native plugins, current live composition or routing.

| Saved composition group | Media path occurrences | Missing occurrences / unique literal paths |
|---|---:|---:|
| Restored Portal | 1,381 | 232 / 144 |
| Restored Treehouse | 1,591 | 0 / 0 |
| 25 engine patches, Heart Performance, 3 Soup restoration copies | 0 | 0 / 0 |

Portal missing references are `.mov` files retaining Windows paths. Examples include `hypno recordings/dxv/1-1-2021 01.mov`, `hypno recordings/dxv/1-2-2021 01.mov`, and `youtube rips/dxv/0-9matrix10bt.sleepytom.Pjpeg80_512kb.mov`. The 144 count is unique literal serialized paths, not a reconciled count of unique video identities.

Historical `restored-compositions/README.md` and `video-relink-report.json` record 290 uniquely matched videos relinked, five uncertain candidates and 140 not found. `portal-video-candidates.json` contains search results and alternatives. Those historical identity-based counts are not directly interchangeable with today's XML path count. No uncertain candidate was linked here. Historical byte verification of 2,464 image references was not repeated; today's Treehouse existence result does not establish video playback or hardware mappings.

Portal and Treehouse's named MIDI presets (`portal.xml`, `treehouse.xml`) and their Default keyboard/OSC/DMX files exist under `~/Documents/Resolume Arena/Shortcuts`. Their actual device mappings and routing remain unverified. Across the other 29 compositions, the referenced OSC preset `~/Documents/Resolume Arena/Shortcuts/OSC/OutputAllMessages.xml` is missing. This is a shortcut dependency gap, not proof that REST-based Heart control fails.

## Launcher and recovery findings

- Relative launcher paths resolve correctly; shell syntax passed. Engine Python and websockets are locally usable; native monitor executable and its Syphon framework exist. Native linking confirms the absolute workspace framework dependency. No cold launch was attempted.
- The launcher starts Arena only when engine ports are absent and Arena REST is unavailable. With both Heart ports listening, it skips Arena readiness checking. Port presence does not validate service identity or health. Treat its final “ready” message as service startup evidence only.
- Existing monitor binaries are never rebuilt by the launcher. The monitor README's claim that Open Heart.command rebuilds is stale: it rebuilds only when the binary is missing. Source changes require an explicit coordinator build.
- Native code suspends GPU/client and requests effect release + motion Hold on sleep/session departure. These requests travel through the web socket; disconnection can prevent delivery. Monitor suspension is not proof the engine is held. An OS-paused/killed engine is not automatically resumed by the monitor action or launcher port checks.
- Recovery validates dependency identity and fresh native routing. It cannot restore feedback history; uncertain composition opens and cancellation need inspection rather than presumed rollback. No recovery process was exercised live.
- No shared fix staged: current gaps call for an explicit operational check/rebuild/relink by the coordinator. Port identity hardening is a possible bounded follow-up, not an implemented repair.

## Evidence and checks

Read: PLAN.md; start.sh; launch.py; monitor Open Heart.command/build.sh/README.md/Heart.m; engine heart.py/status.html/dependencies.py/patches.py; restored README and video reports; all inventoried saved XML. Inspected Python symlink, imported dependency versions, native binary linkage and current shortcut/media existence.

Ran: zsh syntax validation of three launcher/build scripts; `test_resume.cjs`; `test_pointer.cjs`; Python `unittest test_dependencies test_patches` — **42 passed**. Tests emitted existing unclosed-file ResourceWarnings. No native Objective-C tests, GPU rendering, network/live API checks, process actions, installs, composition saves, media relinks or shared edits performed.

Integration: coordinator verifies current installed plugins and actual output; chooses/saves today's show setup; exercises one reconnect and explicit resume in its owned live window; handles Portal's missing clips only if needed; checks whether OutputAllMessages is required. Keep all untested sources/playback explicitly unverified.

Follow-up reconciliation: see `FOLLOWUP.md` and `PORTAL-RECONCILIATION.json`. All 290 recorded approved video relinks are present and destinations exist. Remaining 144 identities are 139 historically not found plus five still-existing unapproved candidates. Historical missing GLK VISUALS V4 FINAL.mov is no longer referenced. Including paired VideoFile/value fields doubles serialized counts, not asset identities. A launcher-only identity patch is now staged separately, not applied.
