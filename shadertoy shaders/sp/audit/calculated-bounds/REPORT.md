# Calculated Figure / Linear Cloner bounds

## Implementation

Existing Smart Params remain the sole motion engine. The Figure's added native Transform (Transform~1) and LinearCloner~1 now project their coupled numeric output through frame-relative geometry before writes. Manual writes (including legacy shuffle/undo paths) wait for the same projection. Coupled numeric controls are claimed together. Heart publishes the projected value rather than an unreachable requested value.

The current Solid Source uses a conservative source radius .46×shorter frame dimension. Other sources use half the full-frame diagonal; a nonneutral source Transform disables the tighter known bound. Composition dimensions are refreshed on discovery and a two-second size poll. This is not an instantaneous guarantee during external resolution/stack edits.

Transform: fit the circular scale envelope within a 2% short-side inset, then constrain XY. Uniform/nonuniform scales retain a minimum envelope radius 4% of the short side, avoiding collapse. Z rotation is free; X/Y perspective and AnchorXYZ project to zero in this initial 2D mode. Driven XY maps across currently available travel, not the native ±16384 pixel range. Open generates frame-relative size/position ranges through existing drives.

Linear Cloner: the first-copy envelope includes source size and displacement, transformed start scale, and the input/original envelope to allow Transform opacity blending. Center displacement uses the measured Center×width/2 native law and Master Rotation. Multiple tails / Tail Rotation use an orientation-independent tighter interval. Start Scale is bounded; subsequent tail geometry and length can leave the screen. Reverse, native delay and distortion are parked in this first protected mode. Preceding creative effects or an additional nonneutral Transform produce a review notice because this source-envelope calculation does not describe their expanded output. Changing native controls directly in Resolume outside Heart is not covered by an atomic enforcement guarantee.

## Verification

Geometry tests include 400 randomized scale/position/angle combinations over four aspect ratios, exact native Center mapping, zero-scale floor and an engine-path check proving manual/legacy writes defer until projection. Full engine/UI suite results recorded in the turn.

Live `check_live.py` exercised manual extreme inputs, one-copy cloner anchor, Open, and Shuffle at 1920×1080,1080×1920,1024×1024. Eighteen single-source/anchor samples were nonempty with no edge contact. `pixel-checks.json`, `results.json`, numbered frames and contact.png preserve evidence. These are sampled rendered checks, not a frame-by-frame or exhaustive shader guarantee.

The final `tail-crossing.png` visibly shows an intact first copy with trailing copies exiting the right frame. `minimum-size.png` records a zero-scale request under the strengthened minimum. Landscape output and pilot source render size were returned to1920×1080; guarded Open left running at0.5×. Original shader files/compositions were not overwritten.

## Remaining

Audit remaining Figure source envelopes; test and derive perspective, reverse, distortion and temporal variants instead of silently treating them as contained. A future guard can incorporate preceding effect envelopes; current UI explicitly flags this case. Native delivery is coalesced parameter writes, not a transactional frame-wide batch.
