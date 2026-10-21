# Feedback Machine → Generative Soup: restoring the instrument

Read-only comparison, 2026-09-07. Sources: saved `feedback machine_16x9_1080p.avc`, saved `generative soup_16x9_1920x1080_60fps.avc`, live Soup REST snapshot, Heart source, and [archived MIDI inventory](../archive-study/MIDI.md). No composition or runtime code changed for this comparison.

## Finding

Feedback Machine combined a bank of ready-made behaviors with persistent effect stacks and hands-on navigation. Soup has a more programmable motion foundation, but its performance access and instrument coverage are incomplete. Restore that playable structure before scaling shader imports. Similar parameter names do not establish equivalent feedback behavior.

## Capability comparison

| Capability | Feedback Machine evidence | Soup / Heart today | Work needed |
|---|---|---|---|
| Layer browsing | User recalls dedicated previous/next buttons on every layer. Base clips include rotate, move and scale behaviors. | Previous/next/random handlers already exist and browse populated clips. Their buttons are hidden outside Edit. | Put previous/next beside each layer fader; make clear, bypass and current clip state accessible. Later add curated banks so diagnostic/legacy clips need not interrupt a set. |
| Feedback movement | Native Feedback clips provide RotateLeft/Right, X/Y rotations, scale W/H/in/out and directional movement. | Map, fold, texture and level router clips; separate Flow/Shape legacy loop clips. | Build a small set of named, tuned behavior presets; compare recurrence, rotation, translation and decay visually against the old instrument. |
| Persistent shaping | Base layer has InvertRGB, Blur, Sharpen, Kaleidoscope and four Mirrors. | Map clip contains InvertRGB, Blur and Sharpen; Figure layer has LinearCloner and Mirror. | Expose existing processing first. Decide deliberately which effects should persist across clip changes and where they belong in the feedback path. |
| Feedback color | Fill/color/motion stacks use InvertRGB, HueRotate, DelayRGB and AutoMask. | StudyColor, LoopColor and limited native processing exist on particular clips. | Restore inversion, hue cycling, channel delay and masking as separate musical controls. Do not substitute Colorize; user rejected that aesthetic. |
| Object and background treatment | Object stack includes clones, iteration, mirrors, displacement, distortion, ASCII, infinite zoom, LUT/glitch processing. Background has Twisted, Suckr and FishEye. | Figure has only two non-Transform layer FX; most of the older stack is absent. | Add selected effects in batches after the common effect adapter works. Confirm plugin availability and visual behavior before deciding on shader recreation. |
| Global accents | Composition stack includes stroke, pixel melt, hue, LUT, ColourLoop, Twitch and Strobe. | No corresponding saved Soup composition stack. | A compact performance rack with intentional momentary/latching controls and useful intensity ranges. Preserve effect order. |
| Effect access | Controls were organized around the composition's stacks. Current Default MIDI includes linked Blur/Sharpen bypass. | `discover_fx` only discovers layer/composition effects with Opacity; skips Transform. It does not discover clip/group FX. General effect parameters are not exposed by that rack. | Support clip/layer/group/composition scopes, typed parameters and linked actions. Put layer-relevant controls in the fader cards. |
| One-click musical motion | Archived animated clips supplied ready-made motion; full historical button behavior cannot be recovered from the composition alone. | 32/36 live populated clips recognized; 13 match dedicated factory Home profiles. Saved Home overrides and fallback motion may also exist. | Audit each instrument's active drives, safe ranges, relationships and visible result. Recognition is not readiness. |
| Whole-instrument recall | Clip and stack choices collectively made the patch. | Home applies motion state to a clip; it does not launch the required clips, set layer levels/routing or clear feedback history. | Separate a clip's motion Home from an explicit whole-instrument starting patch and feedback reset. Keep Hold motion distinct from stopping/clearing the rendered feedback. |
| Hardware independence | User's stated requirement: operate without touching Resolume. | Trackpad control, faders, reconnect and motion already exist; coverage is uneven. | Give UI, trackpad and future hardware the same action vocabulary. Rebuild mappings intentionally rather than assuming old positional mappings fit new layers. |

## Structural differences worth preserving

Feedback Machine's first four layers are fill/color/motion/base; Soup's first four are feedback/sculpt/field/delay. This is not a one-to-one layer migration. Effects must be placed according to which signal should circulate through them, rather than copying their old layer number. Old native Feedback sources, Video Routers and shader-owned persistent buffers may have different recurrence and reset semantics.

The old base clip bank is especially useful as a design reference: each clip is a behavior you can play. Soup can retain that immediacy while letting a behavior contain motion relationships, speeds and ranges. Presets should bind semantic roles and scoped parameter identities, not parameter count or transient Resolume IDs. Missing controls should be reported/skipped, and newly discovered controls should start still. Repeated parameter names across effect instances need distinct identities: Heart currently takes the first matching atom parameter name.

Do not port the entire old rack at once. Some source dimensions inside the 1080p archive still read 2352 × 672. Stored effects are not proof they were all enabled together, installed now, or inexpensive. Existing system-wide GPU readings also do not establish Resolume's individual cost.

## Proposed implementation batches

1. **Complete the current surface.** Visible per-layer previous/next; expose existing native clip effects; clear connection/current-clip state; verify reconnect through reload and clip changes. Keep the eight-fader arrangement. This restores access before introducing new processing.
2. **One complete feedback instrument.** Establish routing explicitly, then tune map movement, decay/level, linked Blur/Sharpen, inversion and fold/mirror. Add hue/channel-delay/mask behavior from the old stack where needed. Provide a reliable starting patch, animated Home and explicit reset. Validate each addition visually and measure output FPS under the same render conditions.
3. **Figure plus background.** Give their sources and effects consistent performance controls and meaningful Homes. Start with clone/mirror/displacement and one background treatment. Check that color controls affect the intended stage, rather than merely changing numbers.
4. **Expand shader families in small batches.** For each shader document its role, exposed controls, parameter types, motion ownership, useful ranges, Home, routing assumptions, reset behavior and measured cost. Validate one complete instrument before multiplying imports. The existing parameter-loop relationship library is the reference; do not invent another partial catalog.
5. **Recall and hardware mappings.** Build semantic whole-patch recall and map the stable actions to PBF4/KnobX1, then restore Portal/Treehouse against those identities. This is distinct from reinstating the removed bottom variations UI. Worker assistance follows [WORKERS.md](../../../WORKERS.md); factory-floor integration remains future work.

## Functional acceptance

From Heart alone: start a known working patch; browse every performance layer; shape feedback and color; access relevant effects; invoke visibly useful motion; adjust speed; hold motion; clear/reset deliberately; recall the patch; and recover after a Resolume reload. No stale parameter writes, silent missing controls or accidental double animation. Each shader/effect batch must meet an agreed output-FPS target at the actual composition resolution, with GPU measurements taken under comparable background load.

## Evidence and limits

- [Machine-readable inventory](inventory.json): saved stacks, source settings and live control coverage. Saved XML has 245 source-bearing clips across Feedback Machine's decks versus 36 in saved Soup; counts are not unique shaders or functional instruments. Excluding Transform, there are 93 saved effect instances versus 20. Live Soup also contains the newer light-delay variant.
- [Comparison script](compare_compositions.py): uses Heart's recognition logic. Run with `sp/engine/.venv/bin/python`; reads the captured `/tmp/heart-comparison-live.json` for live coverage. Refresh that read-only REST snapshot before rerunning on another session.
- `sp/engine/status.html:91`: navigation hidden in performance mode; `heart.py:639`: navigation already implemented.
- `sp/engine/heart.py:531`: effect-discovery scope; `:374`: Home behavior; `:169`: atom discovery and first-name-wins parameter identity.
- Both compositions reference MIDI preset **Default**, rather than embedding the historical mappings. The current Default contains 15 assignments: eight layer levels, four Mirror bypasses, InvertRGB bypass, and Blur/Sharpen sharing an input. It does not recover the full historical controller. Other presets exist, but cannot be assumed to be Feedback Machine's missing mapping.
- Router source settings are encoded in saved XML; live sourceparams were absent for the inspected Video Routers. Their exact inputs must be verified before moving effects. This review did not switch compositions or replay the archived feedback behaviors.
