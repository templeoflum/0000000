# Pilot switching and complete motion recall — September 8

User authorized live pilot switching with a fresh recovery patch and restoration.
The first save failed before switching because native VideoSourceFeedback was not
supported by dependency validation. Added the exact FEEDBACK_SRC mapping, evidenced
by installed source inventory and native XML. Required source inventory checks remain
active. Regression covers installed/missing Feedback. 154 Python checks pass.
Loaded via state-preserving engine restart (PID 22219).

Fresh save / Figure depth recall / three pilot checks / recovery recall completed.
Final recovery patch: see recovery-name.txt. Original Start choice was not replaced.
The saved recovery includes three adapted sources and Linear Cloner motion as well
as native composition clips, routing, levels and effects.

Twelve-second motion samples after each clip activation settled:
- 3D: Tumble, Morph and Hue moved; Morph covered approximately .18–.72.
- Shell: Turn, Spin and Hue moved.
- Seed: rot angle, mx and my moved; mx covered .28–.40, my .4401–.56.

Home rests and remains unchanged. These checks explicitly enabled selected drives
following factory Home; they did not redefine Home as an animation preset. No full
Open/count sweep or arbitrary placement-range expansion was performed.

`restore-comparison.json` verifies exact matching drive flags, ratios, multipliers,
offsets, shapes, limits, locks, cyclic settings and global relationships for all
three adapted source targets and the driven Linear Cloner target. Its 12 drives
returned, with the same tempo and Hold state. Animated instantaneous values/phases
are not expected to match a previous timestamp.

A native monitor spot read during playback showed 1920×1080, 60 FPS and 52% Mac GPU.
This is not sustained performance certification or visual/artistic approval of
all combinations. Earlier isolated source containment evidence still applies only
to its sampled ranges. The current pass verifies delivery/motion and recovery, not
an exhaustive visual tuning of the complete stack.

Initial test script incorrectly required the transient literal Applying status;
recall publishes descriptive intermediate stages. Fixed it to observe operation
activity. Initial immediate-after-launch commands also correctly hit instance
replacement guards; final samples allow discovery to settle before sending.

Next: review useful Cloner/Sculpt/Feedback relationships visually and preserve a
reviewed performance patch before expanding the next 3–5-source family. Native
Feedback recall is now unblocked for existing imported clips.
