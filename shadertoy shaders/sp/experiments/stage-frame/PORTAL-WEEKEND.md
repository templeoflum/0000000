# Portal weekend test

Use Heart Portal Weekend.avc in this folder.

- Layer 9, column 3: Heart Portal Stream, active. All 853 original image variants, 16 sections, lossless QuickTime Animation banks. 32 video samplers replace 853 image loaders. Native patch graph reduced from 1179 to 342 nodes.
- Layer 10: Portal stage mask. Column 1 full, column 2 wings, column 3 donut. Full is active at opacity 1 with Alpha blending. These are the original 3840x2160 mask PNGs sized to the current 1920x1080 composition. Mask remains above the whole composition and blocks the outer region and center opening.
- Both layers ignore column launches, so normal content changes do not switch the stage or mask.
- Old heavyweight Portal and Treehouse test clips were cleared from this composition; original patch files and earlier compositions remain archived. Treehouse work is deferred.

Validation: streaming source opened in Arena successfully in a 9.54-second end-to-end MCP request, versus original timeout loads. This includes tool overhead and is not an isolated codec benchmark. Composition snapshot confirms masking; layer motion capture confirms evolving frames. A decoded middle frame matches its original RGBA PNG byte for byte. No output-device or Advanced Output routing was changed.

Still outstanding: original outline/detail generators and group effects parity, performance tuning on the actual projector setup. Indexed media is stored in portal-stream-banks alongside this note and is referenced by absolute path; keep that directory in place.

## Superseded by native Portal recovery

The indexed Wire source failed live acceptance: user reported 7 FPS and discontinuous fades. Do not use Heart Portal Stream for the show.

Current replacement: `Heart Portal Native.avc`. It retains Heart's original eight layers, adds native Portal image sections on layers 9–24, the original outline/detail bank on layer 25, and stage masks on layer 26. All 853 image variants plus 14 outline/detail clips are present; referenced media exists. Native layer blends, transition mixers, transition durations, opacity envelopes and random autopilot are copied from the original Portal composition. Stage clip processing is sized to 1920×720 inside Heart's current 1920×1080 canvas, preserving aspect ratio. Output routing was not changed.

Live checks: all 16 image sections launch and autopilot changes clips; output snapshot shows the stage silhouette and center hole. Original group effects are retained. Outline bank is available but idle. Performance FPS and smoothness still need live confirmation; do not claim acceptance from snapshots. Opening a composition starts content idle; native stage layers were launched in the live session. Saving this subsequent playback state was blocked by automatic approval review pending explicit user approval.

Heart UI now separates Instrument and Portal stage banks in Layer faders (also scopes Play's clip rows). Eight instrument faders remain the default, Portal uses a scrolling two-column stage bank. Existing 50 UI interaction checks pass; real browser checks confirm 8 instrument / 18 stage entries and no page errors. Controls reloaded in the native Heart app.
