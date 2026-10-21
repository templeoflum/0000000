# Heart departure card — 2026-09-09

Offline audit complete; cold start, actual reconnect, sleep/resume, native playback and sustained show FPS still require coordinator rehearsal.

## Start / preflight

1. Keep the existing workspace at `/Users/donovan/work/0000000/shadertoy shaders`. Open the intended composition in Arena; check its identity and eight-layer show layout before controlling it. The launcher does **not** choose or restore a show composition.
2. Run `sp/start.sh` or double-click `sp/monitor/Open Heart.command`. They resolve paths relative to themselves. The launcher starts missing services and opens the native Heart window; it does not restart existing services. Arena Web Server must answer on port 8080; Heart uses 8765/8766, trackpad uses 8770 (lab HTTP 8769).
3. Confirm Heart reports connected, the selected layer/source matches Arena, and native output is the intended image. Enable Arena **Composition** Syphon output. Use **Fit** for complete output; **1:1** may crop when the pane is smaller than the source. Verify upright orientation, expected source dimensions, detach/dock and pointer Escape release.
4. Verify Hold/Resume motion, Home/Settle, then a modest Open, scoped shuffle and momentary effect release. Home coverage is source-specific. Hold stops Heart parameter motion; shader time and feedback can still evolve.
5. Coordinator saves a clearly named, verified show composition plus matching Heart settings before departure. A patch's `.avc` and `.json` belong together. Do not assume historical `Start.avc` or `_recovery.avc` is today's selected show set.

## Recover

| Symptom | Action |
|---|---|
| Pointer grabbed | Escape; switching apps/windows also releases native capture. Check any held effect released. |
| Controls disconnected | Wait for automatic Heart socket retry (~0.8 s). If Arena is available, use **Reconnect** to release effects, clear pending values and rediscover targets. Confirm identity/readback before driving. |
| Monitor PAUSED, covered window | Reveal the window; covered/minimized output pauses drawing. |
| Monitor paused after sleep/session change | Activate Heart and explicitly choose **Resume monitor**. Then choose **Resume motion** when ready. Waking alone does not resume the monitor; motion resume also bridges to monitor resume when connected. |
| No source / STALE | Check Arena is producing Composition Syphon output. The monitor retries an invalid/missing client every second; a valid client with no new frames reports STALE. Resume does not restart Arena. |
| Engine absent | Reopen the launcher after checking Arena. One occupied Heart port causes a protective error; both occupied ports are assumed to be Heart without identity validation. Do not kill processes based on this card. |
| Blank/stale web controls | Native **Reload controls** reloads the surface; check engine availability first. Reopening the launcher is not a browser reload or a rebuild of an existing app. |
| Composition recall fails | Read the full status and inspect Arena. Confirmed failures may roll back saved controllable state; cancellation or an unconfirmed open deliberately does not auto-rollback. Feedback history cannot be restored. Avoid repeated blind recalls. |

**Load composition / Start is disruptive**, not a reconnect. Recall checks installed dependencies, saves `_recovery.avc`, opens/verifies the composition, checks fresh native routing and restores control relationships. `_recovery.avc` is overwritten by later recalls and is not a durable backup of engine state.

## Keep available offline

- Entire `sp` controller folder, engine environment, settings JSON files, `performance-presets/`, paired `engine/patches/*.avc` + `.json`, shader sources/wrappers and the approved show copy.
- Homebrew Python 3.14 at `/opt/homebrew/opt/python@3.14/bin/python3.14`; the engine virtual environment links outside the workspace. Python 3.14.6 and websockets 17.1 imported in this audit.
- `sp/monitor/Heart.app` **and** `sp/preview/.venv/lib/python3.12/site-packages/syphon/libs/Syphon.framework`. The binary has an absolute search path there. Moving the app/workspace requires a coordinator rebuild; copying the app alone is insufficient. Apple compiler is needed only to rebuild.
- Installed Arena at `/Applications/Resolume Arena/Arena.app`, its installed native plugins, user shortcuts and output configuration. Source `.fs` files alone do not prove plugins are installed. Trackpad additionally depends on macOS's private MultitouchSupport framework; mouse controls are the documented fallback.
- Portal/Treehouse restored copies in `sp/restored-compositions/`; media under `/Users/donovan/work/Visuals`, especially `infra`. Preserve original Documents compositions. See MISSING-PATHS.md before selecting Portal videos.

Do not change OS sleep/security settings or restart processes as part of this checklist audit. The coordinator owns live rehearsal, saves, relinks and any integration.
