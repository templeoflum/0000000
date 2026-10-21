# Heart Melting Fractal

New copy installed in Figure L5C72 and Heart copies. Original L5C50 and source remain intact.

Confirmed empty geometry at original fold-range endpoints in local rendering. The new full-travel Fold Offset maps internally to -0.4..-0.2. Twenty-four endpoint/phase/twist combinations retained visible geometry; four additional portrait/square cases stayed inside the frame. This is sampled evidence, not an exhaustive guarantee.

The original rotation matrix mixes rotation with axial scaling and can collapse geometry; the copy uses orthogonal rotations and maps Twist Amount to rotation angle. Camera distance is fixed within the march range, and the image uses the shorter resolution dimension. Ray hits now require actual convergence rather than treating iteration exhaustion as a hit. Background glow is excluded from the source alpha so effects own any trails outside the figure. Glow Strength now scales the visible surface glow, with display gamma applied for readability. These changes alter the original's appearance; it is preserved separately.

Animation Speed and Orbit Speed were actually phase selectors (TIME multiplied by zero). They are labeled Fold Phase and Orbit Phase. Existing Heart Smart Params drive those phases; no clock/generator architecture was added.

Live validation: seven controls discovered; 14/14 manual native targets passed. Driven Fold Phase varied and paired live output images visibly change between distinct folded forms. Geometry and frame checks are in cases.json and aspects.json. Home/Settle, long continuous sweeps, every orbit/roll combination and a formal support bound remain unverified. This source has not been added to the engine's proven-bound registry.
