# Color Wheel black-output range repair

New Heart Color Wheel is installed at Field L3C13 and included in Heart copies. Original Color Wheel remains untouched at L3C94.

The original warp parameter multiplies final RGB by values from -200 to +200: it is gain, not spatial warp. Negative gain explains black output for otherwise positive RGB. The copy labels it Gain and exposes .1–2 instead. Hue rotation, repeats, center brightness and saturation controls have useful bounded ranges; saturation interpolation is clamped to avoid extrapolating negative RGB. Position is fixed at its original center. Original attribution is retained.

All six controls passed two manual native targets (12/12), and a Heart hue drive varied with visibly changing live output. Three local cases rendered. High gain with pale saturation can still wash to white; low gain is deliberately dark. This does not guarantee every simultaneous parameter combination is aesthetically useful. Home/Settle and full live-range sweeps remain separate checks.

Other findings, not yet repaired: Melting Fractal's so-called animation/orbit speed parameters actually select phases (TIME is multiplied by zero). Its non-orthogonal rotation-mix matrix changes distance estimates, and its camera range can put the origin beyond the 50-unit march limit. These require a separate copy and controlled tests, not a blind range clamp. Klein Bottle also has quaternion ordering/zero-normalization and refraction-ray issues requiring separate investigation. No changes made to either source this turn.
