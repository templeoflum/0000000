# First corpus Field batch — integration

Built from canonical toy-factory code, not MET3OR. Sources: Heart Barberpole Field (Field14), Heart Stepping Feet Field (Field109). Existing source identities preserved. Existing Smart Params only, Phase cyclic/linear, both bars share one phase. Opaque scene backgrounds preserve the contrast context. Home profiles: Phase.5, Aperture0/Contrast1 and Stripes1.

Builds: both glslang and offscreen OpenGL compilation passed; rendered samples reviewed. Navigation tests4/4 passed. Heart discovered3/2 controls; native Phase changed across three samples after Open. Home switches all drives off.

Found during actual runtime checks: cyclic Phase can settle about.094 past its intended Home during the existing engine's drive fade (rot keeps integrating while manual compensation is fixed). A later Home from still reaches.5. This is an existing engine recovery limitation, not fixed here. Do not claim exact moving-to-Home phase recovery.

Barberpole original vector rectangle helper produced incorrect live horizontal extent despite correct native Aperture readback. Scalar helper probe being verified; keep current acceptance result separate below. Stepping Feet live rendered aligned bars against its stripe background, and direct static positions plus native drive samples were collected. API output snapshots are vertically opposite the offscreen harness; no global monitor changes made.

Live scripts restore prior active Field clip and fader levels in finally. Evidence: drive-results.json, results.json, aperture-results.json and PNGs. No sustained frame-rate benchmark or broad library certification.

Final: scalar rectangle edges fixed actual Arena aperture dimensions. Tall ~255×837; wide ~878×214 at1920×1080, including outline. Both actual images reviewed. Native source controls and Home-to-still checks passed; the moving-to-Home phase offset described above remains. Field → Heart copies includes14 Barberpole and109 Stepping Feet; bank verified from live Heart state. Saved Heart Show Ready 20260909 092915, composition/companion pair integrity and dependencies PASS. Latest setup not reopen-tested; previous082918 remains reopen-tested baseline.
