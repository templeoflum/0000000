# Heart — performance tuning handoff

Latest handoff, 11 September 2026. Supersedes `HANDOFF-2026-09-11.md` and historical native-only motion / opacity-pulse rack notes. The user explicitly requested this handoff and a fresh task. The previous task is handing over, not continuing implementation alongside you.

## Current brief

The user says the plumbing is in place and the instrument is looking good. Continue with fine tuning and polish that makes it fluid to perform. Start by inspecting the current standalone interface and tracing one complete playing phrase: **choose content → shape motion → play effects → reset → continue**. Collect friction across that flow, then make a bounded, coherent batch of improvements. Do not restart product planning, controller integration or architecture work.

Priorities are direct navigation, clear states, comfortable controls and musical response. The user wants a compact map, not prose, dropdown mazes or pages of faders. Show useful layers, sources, effects and driven relationships immediately. Keep positions stable and use consistent layer colors. Work by dependencies and constraints, not time blocks. This is an active show build; do not reopen scheduling questions or make a large speculative redesign.

## Read and preserve

- App directory: `/Users/donovan/work/0000000/shadertoy shaders/sp/heart-v2`. Project is not a Git repository; work directly in the saved project.
- Read `AGENTS.md`, this handoff, `AUTHORED-CLIPS.md`, the top of `SHOW-CHECKLIST.md`, and `progress.json`. The checklist retains historical evidence; its old native-only and opacity-envelope descriptions do not override the latest behavior below.
- UI work must use `/Users/donovan/work/skills/_extract/*/legibility-constitution/SKILL.md` and `/Users/donovan/work/skills/_extract/*/narrator-bleed/SKILL.md`. The `*` is a literal directory name. Inform the user when applying the skills. Boustrophedon construction/legibility references are in `../design/heart-surface-language/README.md`; optional visual exploration remains parked.
- **Standalone Heart only. Never open a second live Heart browser panel.** Duplicate surfaces compete. Isolated UI tests must use mocked connections.
- Preserve recovered ranges, authored baseline values, native MIDI mixing, layer order, group membership, masks, geometry and intentional clip transitions. Refresh native identities before changes: the user edits the composition while testing.
- “Clip overlap” means different versions of the same shader in a layer. It does not mean temporal transitions. Do not change transitions to solve it.
- Heart is a generic instrument controller. Layer roles, authored baselines and rack destinations are configuration with exact identity validation, not hardcoded composition names/indexes.
- Grid faders/knobs are already mapped in Resolume. The separate big knob is native master. Hardware work is parked; PS4 would later navigate Heart, and trackpad/custom layout/Grab work is deferred.
- Only two deliberate recovery states, Base and Safe, are wanted. They remain pending. No look library or general preset system. Do not claim complete show acceptance or turn this polish pass into a preset project.

## Installed behavior

### Authored clip motion

The authoritative range reference is `/Users/donovan/Documents/Resolume Arena/Compositions/feedback machine.avc`. Additional references are `generative soup_16x9_1920x1080_60fps.avc` and `feedback machine_16x9_1080p.avc` in that directory. Original and resized Feedback Machine have identical imported Low/High ranges; small timing differences do exist. Reference files were not changed.

`authored.py`, `build_authored.py` and `authored-clips.json` import saved timeline In/Out into ordinary Heart Low/High. Heart approximates timing with musical ratios. The original import matched 178 profiles, 1,089 controls and 321 timelines. The prepared set now has **246 baselines**, including **all 208 current Figure/Field clips**, and 339 motion controls across the complete set. Missing reference controls use explicitly marked current baselines. Matching repaired controls inherit original ranges; Melting Fractal has documented renamed/unit-translated controls. Repaired shaders can differ visually from originals: do not claim exact visual identity across the library.

Configured Figure/Field sources auto-start authored Heart drives on load/revisit. Normal Family, Rate, Shuffle, locks and Drive controls work. **Reset clip** restores the selected clip's baseline controls, ranges and drive configuration. Static defaults have closed ranges, stay out of bulk Drive until a range is opened, and remain manually adjustable using native bounds. Shuffle preserves ranges, Amount and the driven set; bulk Drive skips locked controls without changing their state. Do not restore the old native-only source UI or full-range implicit modulation.

Source follows the actual playing clip. Selecting a layer effect survives clip changes. Shared layer movement remains distinct from authored source motion. Figure uses one shared layer Transform. Central Drives bank provides target/layer relationships and exact-contract pins without widening observation subscriptions.

### Clip navigation

`clip-library.json` groups **208 native slots into 169 visible shader families**: 63 Figure / 106 Field. A family count button exposes versions; Previous/Next/Random advance families. Full native clips remain accessible. **No native clips were deleted**, and no new Resolume groups were made. Originals and materially different repairs remain available.

### Performance rack

`effect-rack.json` has Stage, Figure and Field + video rows. Field and video are two existing layers linked through Heart, preserving MIDI and native organization.

- **LUT On/Off** enables/disables LUT Corrupt separately. **Decon** fires its native event only while enabled. It never auto-enables LUT or pulses opacity; always-on LUT changes color.
- **Pixel Melt** means MTK_PXLMELT, not LUT MELT. Toggle the native boolean `MELT_LOCK`. The underlying effect stays enabled at opacity 1 when released.
- Color controls native ColourLoop opacity. Existing Offset timelines retain different row phases; Field/video stay matched.
- Clear disables LUT, releases Melt and clears Color. All linked members must validate; a missing member disables the row.
- Tap uses native Tap tempo; Downbeat uses native Resync.

The new rack uses `rack_control` enable/trigger/latch/clear actions. Legacy `effect_hit` still exists for older generic features but is not the new rack's behavior.

## Runtime and verification

Heart HTTP: `http://127.0.0.1:8875`; Heart WebSocket: `ws://127.0.0.1:8876`; Arena REST: `http://127.0.0.1:8080/api/v1`. The standalone app bundle ID is `co.boustrophedon.heart-v2-surface`. Python from the app directory is `../engine/.venv/bin/python`; Node is `/Users/donovan/.local/bin/node`. Playwright is available at `/Users/donovan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright`.

Last verified session: connected and armed, Hold off, ten pre-existing Figure LinearCloner layer drives restored, plus the active source's drives. BPM was 120; do not reset it. Figure's native mixing opacity was **zero**, controlled by the user's mixer. Do not treat this as a broken shader and change their faders. Figure was selected, Rack open, and the test Melt latch was released. This is historical state; inspect fresh before relying on it.

**Never open Arena's native WebSocket.** It previously produced 365 MB of unsolicited catalogs in eight seconds and severe memory/timing problems. Keep small HTTP by-ID output up to 120 Hz, bounded scoped observation (at most 256 IDs), and light active-clip discovery. No periodic full-composition reads while armed. One deliberate snapshot for an identity audit is different from polling. Keep v1 `heart.py --all` off. Do not restart the memory investigation absent new evidence.

Evidence is in `checks/`:

- `deep-clean-live.json`: six live launches/revisits and all three rack rows passed. Tested exact Heart bounds, bounded native values, motion, shuffle preserving bounds, and baseline initialization on revisit. This is parameter/output transport evidence, not rendered acceptance of every shader.
- `deep-clean-range-import.json`, `deep-clean-preinstall-native.json`, `original-feedback-reference-diff.json`: import coverage/fallbacks and all 246 baseline identity validations.
- `deep-clean-backend-tests.log`: 97 backend checks passed. Six affected launch checks passed after the stale-eject fix.
- `test_clean_surface.cjs`: mocked compact 639×734 and wide 1440×900 interface checks cover motion controls, reset, families/versions, nine rack buttons, independent actions, keyboard repeat, offline guards and stable layout. The older authored/rack surface test files now wrap this test.
- Native standalone Figure Pixel Melt click was verified against latch/opacity/bypass and released afterward. Full-library visual and musical acceptance remains open.

Preserve the pending-eject reconciliation fix in `server.py`: `if catalog.pop('_changed', True) or e.launches:`. An unchanged empty-layer scan still must settle an eject; otherwise the next launch can falsely fail confirmation. `test_playing_runtime.py` covers it.

Backend restarts need deliberate state capture/restoration. Historical helpers `/tmp/capture-heart-authored-final.py` and `/tmp/restore-heart-authored-final.py` capture generic drives/locks/groups, disarm, stop the exact server, then restore without overwriting newly authored source defaults. Inspect scripts and fresh runtime before using; do not blindly restart a playing session. The live composition has **not been saved** by this task. Native saving remains a user action.

## Next task

Inspect the actual standalone surface and current files, make a short friction list across the complete playing phrase, and implement the highest-value coherent polish batch using existing actions. Keep recovered behavior stable. Validate changed interactions in mocked UI and relevant native/standalone paths; do not rerun the whole live test matrix without reason. Update the visible checklist and progress with what actually passed, keeping Base/Safe and full-output acceptance honestly open.
