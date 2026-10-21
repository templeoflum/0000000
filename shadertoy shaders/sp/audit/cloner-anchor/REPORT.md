# Linear Cloner anchor measurements

Live native Linear Cloner, 1920×1080 output, static centered 100px diagnostic disk. Nine isolated rendered cases; cases.json and numbered PNGs. Original clip preserved; scratch cleared and Figure pilot reconnected afterward.

Observed first-copy bounds:
- Center0: x910–1010 y490–590.
- Center+.5: x1390–1490; Center−.5: x430–530.
- Changing Tail Length .5→1 leaves the first copy unchanged (Clones1).
- Clones7 at Center0 keeps that same first copy and extends tail beyond right edge.
- Center+.5 / Master Rotation90 moves first copy to y970–1070 (x909–1010).

Inference for the tested native configuration: Center displacement is Center × width/2 along Master Rotation. It is not independently normalized to height when rotated vertically. This explains orientation-dependent dead zones.

Required relational guard: compute transformed first-copy center and support bounds, including source Transform, Start Scale and rotation. Intersect the displacement ray with the frame inset by anchor extents and margin. Map Heart Center into that permitted interval. Tail Length and later copies are not subject to this containment constraint. If the anchor itself cannot fit, reduce its scale or flag the unsupported setting; Center alone cannot solve it.

Not yet implemented as a runtime guard. Additional coverage needed for off-center source Transform, nonuniform scale, Distortion, multiple Tails, Reverse and temporal fill modes. No claim that arbitrary combinations are safe. Working demo parked at Center0 following test.
