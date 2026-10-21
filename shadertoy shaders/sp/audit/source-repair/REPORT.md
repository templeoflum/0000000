# HypnoWorm and Torus control-ready copies

Installed new sources in Figure L5C13 (Heart HypnoWorm) and L5C14 (Heart Torus). Original files, patch identities and clips remain untouched. Native source registration uses the existing Heart control engine.

HypnoWorm: the original patch has fixed color1=white and color2=black, with no exposed color controls. The copy uses the source's original color defaults, exposes six color components plus eight motion/tone controls, and clamps negative color before fractional gamma power. Unused Edge was omitted. Source placement is centered and scale is fixed; shared Figure Transform owns placement and size.

Torus: the original has no input nodes despite shader inputs, so Resolume reports no source controls. The copy exposes structure, animation speed and six color components. It initializes the glow accumulator explicitly; scene time now uses the animation-speed calculation which the original computed but ignored. Camera placement is fixed and framing uses the shorter resolution dimension. The exact cause of the original black live output was not isolated; the new copy is visibly rendering.

Validation: both compile and render locally. Six structural-extreme checks across landscape, portrait and square are nonempty with zero edge alpha; this is sampled framing evidence, not exhaustive proof. Both render visibly in live Resolume captures with alpha composited correctly. Two manual targets and a driven structural parameter passed for each source. All 22 controls were additionally exercised at two manual values; 44/44 targets passed (all-controls.json). These are control and sampled-render checks, not full Home/Settle or continuous-animation certification. Rapid speed changes may still change time phase; avoid treating the speed dial as a guaranteed phase-continuous modulation target.

The conservative framing leaves room for the effect stack. Further visual scale refinement belongs with the shared Figure Transform. No GPU performance claims were made.
