# Narrow-range drive startup

Reproduced on Checkered, Field 97, Num X native range 1–100000. Starting from inactive full limits, set manual 16, narrow Lo/Hi to native 8/32, then enable the drive. Before the change, 13 of 40 live readbacks exceeded the requested range; maximum 509.023. Once the three-second morph finished the range behaved correctly. An already-established narrow range also passed, explaining why isolated checks could miss this transition.

Cause: effective bounds were interpolating from the inactive old full range at the same time drive amount faded from zero to one. Their product produced a large temporary excursion even with a manual starting point inside the new limits.

Fix in Slot.retarget: when the current effective drive contribution is exactly zero, adopt the new Lo/Hi in the transition start. Inactive bounds cannot affect current output. A running or fading-out drive still retains its continuous range morph; manual pose, phase and drive fade are unchanged. This is not a hard clamp on every transition, and a manual starting value outside the range still transitions into it.

Validation: a deterministic startup regression failed before the fix (peak 18666.166) and passes afterward; two additional tests preserve active-range continuity and fade-out behavior. All 220 Python tests pass. Same live wide-to-narrow procedure afterward: 40/40 native samples within 8–32 (after.json), sampled every approximately 200 ms for eight seconds. Sampling is not a measurement of every rendered frame. Original scripts and before/after readbacks retained. No shader or composition source edits.

Heart restarted alone, Resolume remained running. Test drive stopped and Num X left at 16; Figure Capsule remains the visible layer, Field opacity zero.
