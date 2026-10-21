# Fluid warp correction — September 8

Donovan rejected Depth study as too slow and jumpy. Its successful commands and
still images did not establish usable performance motion. Do not treat the older
Depth study candidates as artistically accepted.

Confirmed recipe defects: .25 speed combined with 1:2/1:4 ratios made typical
Cloner cycles 32–64 seconds at two bars/120 BPM. Master Rotation inherited a triangle
shape (abrupt velocity reversals) and multiplier 2; End Rotation inherited -1.
Those were accidental inherited settings, not an intentional coordinated recipe.
A native output spot read was 60 FPS/46% Mac GPU when the issue was reported;
this does not rule out intermittent rendering/delivery hitches.

New patches: Fluid warp - 3D, Fluid warp - Shell, Fluid warp - Seed.
Cloner explicitly uses Shape 1 cosine/sway and multiplier +1 on every driven axis.
At speed 1 with two bars, Tail Length, End Scale and Master Rotation have four-second
cycles; End Rotation has a six-second cycle. Offsets 0/.25/.5/.75 distribute the
motion. Widened spacing and rotation excursions create a visibly changing spread.
Source speed is 1. Counts remain static. Source containment settings unchanged;
cloned instances may go offscreen.

Recorded 10-second Heart-state traces and native full-output images for each.
The Shell image shows a broad diagonal repeated-form spread. State traces are at
status cadence, not renderer-frame measurements; do not claim those prove absence
of visual stepping. User playing acceptance is still required. No engine output
cadence change, smoothing filter, or resolution reduction was made.

Original setup was saved and restored after the build. Then Fluid warp - Shell
was selected for immediate user testing, keeping recovery-name.txt available.
Start selection remains unchanged. The new Shell recall completed successfully;
loaded-shell.json records it. Prior candidate snapshots remain available.
