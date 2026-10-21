# Quasicrystal explicit image binding

Ready for main-task integration: `packaging-fixed/SP Toy Quasicrystal Figure 01/`.

The original staged wrapper contains no `toyPoints` cached input, texture constant, incoming connection or image resource node. `build_wrapper.py` enumerates only ISF INPUTS and ignores IMPORTED. The earlier offscreen harness loaded IMPORTED itself, so its successful render did not validate Wire resource binding. Main-task live evidence shows the resulting Arena source is black.

The prepared package replaces IMPORTED with an explicit image input named `toyPoints`. Image node 48 loads `Resource/quasicrystal-points.png` and connects its `output` to ISF node 0's `toyPoints`. The Image node class, version and resource metadata format come from Wire's installed Image documentation patch; straight alpha is true for the existing PNG. This is internal; no Texture In or additional host control is exposed.

The patch identifier, existing input order, all previous connections and control nodes are preserved. The shader body and PNG bytes are unchanged. The original staged package is unchanged; only the new `packaging-fixed` package is prepared. Reproduce with `python3 sp/experiments/toy-shaders/fix_wire_packaging.py`.

Validation: structural assertions passed; glslang 1/1 clean; actual offscreen explicit-input render at 480×480 passed and is pixel-identical to the original imported-image reference (maximum channel difference 0). Evidence: `evidence/packaging-fix.json` and `evidence/explicit-input-home.png`. This validates the shader and intended graph structure, not Wire's loading or Arena output. Main task must load/reload the prepared package and check it in its owned live session. No installed files or live state were changed here; no local models ran.

Do not regenerate this package using the stock wrapper alone: it would replace the fixed image source with a host Texture In and again omit the bundled binding. The isolated fix script applies to the original staged package and can be rerun.


## Main-task integration result

The main task reports that it integrated the fixed package, reloaded L5C75, and confirmed that the isolated Arena output visibly renders the quasicrystal. Live image evidence is `evidence/isolated-75.png` (updated by the main task). This establishes successful image loading and visible output in Arena after the packaging fix. It does not certify sustained frame rate, rotation smoothness, every modulation range, or show readiness. Home verification and final saving remain owned by the main task; this task made no live changes.
