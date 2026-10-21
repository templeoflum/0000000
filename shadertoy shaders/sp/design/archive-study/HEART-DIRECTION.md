# Heart: a surface for performing relationships

This is a design proposal grounded in the saved compositions, MIDI presets, and existing trackpad studies. The ideas below are not implemented features. The current live composition and controller were left running throughout the archive inspection.

The central opportunity is to make a gesture carry your intention across several parts of the image, with a dependable way back. Your MIDI work already contains the beginnings of that instrument.

## What the archive actually says

Inspected all 68 composition files in the standard Arena composition folder: 67 complete XML parses, one unreadable/truncated entry (`2021 template.avc`, line 34177). Inspected all seven saved MIDI presets, totaling 448 assignments. Full file-by-file stacks are in [COMPOSITIONS.md](COMPOSITIONS.md); individual MIDI targets are in [MIDI.md](MIDI.md); machine-readable evidence is in [inventory.json](inventory.json).

The archives are saved structures, not performance recordings. An installed effect, saved fader level, or repeated template cannot establish how often you used something. Sixty-five readable compositions reference Default, whose current file has only 15 assignments; that does not recover the Default mappings you used years ago. Portal and treehouse have matching named presets, making them stronger references. Physical APC labels and undocumented packed MIDI behavior flags have not been guessed.

| Evidence | What it suggests for Heart |
|---|---|
| 2021–2024 templates repeatedly put transforms, cloning, folding, and texture effects on a group, with color/time treatments on the composition and masks on individual layers. | Preserve scope: a gesture needs an explicit subject, group, or whole-image target. |
| Portal has 114 mappings, including 68 direction assignments addressing 34 targets with paired `<` / `>` choices. Treehouse has 91 mappings, including 58 direction assignments for 29 paired targets. | Effects have a motion and an entrance/exit, not merely an amount. |
| Portal shares previous/next-clip inputs across layers 4, 5, and 6. | A clip change can be an ensemble cue with several named participants. |
| Treehouse shares one input across six layer masters (9–14), and another across six more (3–8). | One gesture can mix a family of layers. Show that family explicitly. |
| Both custom presets share an input between two strobe frequencies. Current Default shares one between Blur and Sharpen bypass. | Coupled controls already belong to your vocabulary. Save and inspect their relationships. |
| Feedback machine separates fill, color, motion, base, mask/background, object, text, and glitch. Its base has Blur → Sharpen → Kaleidoscope → four Mirrors; the object has its own larger treatment chain. | Roles and effect order matter. Give these instruments recognizable identities instead of presenting a flat list of plugins. |
| Generative soup moves much of the work into clip effects and named shader instruments. | An instrument must encompass clip effects, layer effects, group effects, and source parameters through one control model. |

Some preset targets may have become stale. For example, Portal's MIDI preset names Heat, while its saved group stack does not contain a Heat effect. Import should expose unresolved targets rather than silently bind a similar effect. Shared keys can be intentional macros or leftovers; the surface should make that distinction reviewable.

## A preset should remember how to play

A useful Heart preset has three independently recallable parts:

1. **Look:** chosen sources, parameter values, effect states, levels, and ranges.
2. **Motion:** timing relationships, modulation depths, entry and release curves, quantization, and which controls are driven.
3. **Touch:** which roles each lane controls, pickup behavior, gesture depth, and what releasing a finger does.

Recall Look while preserving the current Motion; borrow another Motion while keeping the current palette; change Touch without changing the output. Whole scenes may package all three, but their scope must stay visible. This directly extends your existing practice of bringing one axis to a known good state, locking it, and exploring the rest.

“Return” restores controls and their ownership. It cannot restore the exact prior pixels of a running feedback/delay history. A true visual rewind would need a separate history-capture mechanism and memory budget. Keep motion-phase behavior explicit too: continue, align on the next beat, or restart deliberately.

## The performance surface

Keep the monitor and stable layer bank. Give the selected instrument four large, named touch assignments, six nearby variations, and an always-visible indication of what is currently borrowed or being driven. Show the actual destinations and current values beneath each assignment; the mapping should be inspectable without opening a setup page.

Four lanes remain the reliable core. Each lane can control one parameter, a named group, or a designed macro. Touch claims a lane until release, so crossing a zone boundary does not suddenly take over another parameter. Use relative pickup by default for continuous work and explicit catch/absolute options when useful. Losing a contact briefly should not scramble assignments.

A second, explicitly selected **Explore** mode can turn the pad into a continuous field between two compatible saved looks. X controls the blend. Y controls a separately named quality such as echo depth or texture amount. Both destinations must appear on the surface. Tap to keep an endpoint, hold to visit it, release to return. Extend beyond two endpoints only after the simplest version feels playable.

Two-finger spread and rotation are candidates for richer expression: widen the image's structure, rotate a shared motion relationship, or change the distance between two looks. Latch the gesture's participants and baseline at onset; adding or lifting fingers must not cause a discontinuity. Ordinary fader playing must never accidentally switch into this mode.

## Phrases: the step beyond a conventional controller

Start by creating named performances from old gestures, for example:

- **Fold inward:** mirror amount rises while cloner spread narrows; return keeps the selected source and color intact.
- **Leave a ghost:** reduce fresh input while increasing the chosen echo treatment within tested limits; release restores those controls along a deliberate curve.
- **Surface break:** a selected combination of edge, dither, and color treatment enters together; the figure's motion remains untouched.

These are authored macro proposals, not validated ranges or claims about existing effects. Their targets and limits must be learned on the current composition.

Each phrase can have an entrance, a held region that you can steer, and a release. Quantize the entrance or return when useful; allow immediate release for a mistake. Save a performed control trajectory in beat-relative time, then loop or overdub it with a bounded event budget. The distinctive part is being able to take over a moving phrase with your fingers and hand it back smoothly.

A scene morph should interpolate compatible continuous controls. Blend modes, clip selection, bypass switches, and routing changes need explicit switch points or prepared crossfades. Do not numerically interpolate identifiers. Parameter interpolation is not automatically a perceptually smooth image transition.

## Routing and ownership

Bind a phrase to roles such as figure, echo, or finish, then resolve those roles to current Arena parameters. Preserve concrete effect instance identity when there are four Mirrors. If a required role is missing, mark it unresolved and keep that phrase unavailable until repaired.

Define one owner for every controlled parameter at a time: direct touch, visiting preset/phrase, ongoing modulation, or base state. Takeover and return must be predictable, including overlapping fingers and held presets. Show who owns a value. Avoid having Arena animation and Heart repeatedly overwrite each other.

Initially, “routing” should mean assigning control to existing, prepared signal paths. Live changes to video feedback topology, effect order, or source allocation are more expensive and potentially disruptive; offer those as prepared scene choices with clear transitions after validation.

## What the trackpad supports

The saved August 30 findings report approximately 125 Hz contact frames, up to 11 contacts observed, position jitter around 0.07–0.09 mm, and four fixed zones that felt workable. The probe exposes position, velocity, contact size, ellipse shape/angle, and contact state. The lab computes centroid, spread, and pair angle; the lane study compares rank, fixed zones, and tracked contacts.

These are previous recorded measurements, not new calibration in this audit. Contact IDs recycle; they are not reliable identities for anatomical fingers. Use position/history and a conservative reassignment policy. The current probe also combines callbacks from all devices without retaining device identity, so multi-trackpad expansion requires a device-aware model first.

Contact size/density is not calibrated finger pressure. Treat it as an optional coarse expression or sensitivity modifier after calibration, not a precise pressure fader. Finger angle is useful mainly with deliberate rolling. Hover was not a dependable channel. The private multitouch framework remains a compatibility dependency.

## Surpassing the APC40 in practice

The APC's advantages are physical landmarks, independent simultaneous controls, and visible status. Heart needs stable layouts, large targets, trustworthy pickup, clear ownership, and recovery that can be used without searching. More gesture types alone do not improve the instrument.

The gain comes from named relationships, recoverable exploration, preset parts that can be recombined, and a gesture that performs several coordinated changes. Keep performance controls in place while editing their assignments. Preserve access to essential mix, clip navigation, tempo, hold, and return regardless of the selected instrument.

GPU use and output FPS should inform preparation. Label measured expensive phrases and test combinations at actual output resolution. Prebuild compatible effect paths; avoid allocating textures, compiling shaders, or changing stacks at the instant of a gesture. Never silently reduce quality during a performance. Any explicit lightweight variant should remain a performer choice.

## First playable slice

Build four named macro lanes and extend the existing variation system to save their target sets, motion, and release behavior. Translate a small selection of Portal/Treehouse actions into those lanes. Add one two-look Explore field on the selected instrument. This is enough to evaluate whether the controller feels more expressive before expanding the gesture vocabulary.

Acceptance should be hands-on: touch down without a jump; control several lanes without reassignment; visit and return from overlapping variations; interrupt a phrase smoothly; release capture during a mistake; recover from a probe disconnect; reopen a scene with resolved roles; run demanding combinations while watching actual output FPS. Compare it against a familiar APC performance passage, not a count of features.
