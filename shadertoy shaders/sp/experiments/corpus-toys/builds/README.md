# First corpus Field batch

Two fresh source names: **Heart Barberpole Field** and **Heart Stepping Feet Field**. Matching `.fs` and `.sp.json` are ready for the main task to wrap/install. No texture resources or input images required. `build.py` reads existing `sp_header.py`/`sp.glsl` without calling installing emit; output stays here. Manifest records source hashes and controls.

| Source | Slot | Home | Behavior |
|---|---|---:|---|
| Barberpole | phase | .5 | cyclic true, shape0 (rotate), Drive false |
| Barberpole | aperture | 0 | normalized tall→wide, Drive false |
| Barberpole | contrast | 1 | normalized grating visibility against paper, Drive false |
| Stepping Feet | phase | .5 | cyclic true, shape0 (rotate), Drive false |
| Stepping Feet | stripes | 1 | original stripe contrast→flat-gray proof, Drive false |

Every scalar is 0–1 with existing Smart Param companions. Home is still; both feet are visible centrally. Main task owns Open, native identities, bank, Home storage and integration. Phase=0/1 is a repeating grating period for Barberpole and a complete offscreen-to-offscreen crossing for Feet. The feet share **one computed pos** and fixed opposite luminances; there is no separate motion control per bar.

Barberpole preserves the 48-unit diagonal grating, 24-unit stripe width, source colors, 3-unit frame, and aperture width120→420/height400→100. Aperture never changes actual grating direction. The reveal proof is omitted to keep the requested three controls; contrast is the explicitly requested extension and does not move the mask. Opaque paper remains throughout the Field.

Stepping Feet preserves stripe period72, bar96×46, source vertical positions96/198, fixed bar luminances232/34, and stripe luminances blending150→26/238 (rounded like the source). Full horizontal travel adapts to the actual frame width so the bars enter and leave together at any aspect. Comparison rail is omitted. The Field is fully opaque, including stripes=0.

Projection uses short-side units (520 for Barberpole,340 for Feet), keeping angles and sizes aspect-correct. Source backgrounds extend to cover any host frame. This is intentionally a Field adaptation; motion units/time are controlled by the existing heart rather than retaining independent timestamp speeds (.045 and .07px/ms in the HTML).

Validation: project glslang lint **2/2 clean**. Existing offscreen harness `sp/experiments/toy-shaders/render_pilot.py` compiled both shaders with actual OpenGL and rendered four 640×360 samples sequentially. `evidence/contact-sheet.jpg` was visually inspected. Both feet have identical horizontal changed-pixel spans in Home and flat-gray samples; every sample has alpha255 everywhere. Details in `evidence/validation.json`. No Wire/Arena import, live Heart modulation, performance or smoothness claim is made by this builder.


## Confirmed live Barberpole rectangle correction

The main task found that the original vector rectangle helper rendered a constant extra horizontal width in Arena despite correct Aperture readback and shader bytes: aperture0 was about857×837px. The isolated scalar diagnostic replaced vector half-size/abs/max calculations with scalar halfWidth/halfHeight and four edge smoothsteps. The main task confirmed aperture0 now renders the expected tall shape, about255×837px including frame. This establishes the live correction; a specific compiler defect has not been independently isolated beyond the expression replacement. Aperture1 inspection and final runtime acceptance remain with the main task.

The scalar calculation is now in `build.py` and canonical `Heart Barberpole Field.fs`; all other geometry, inputs and defaults remain unchanged. Stepping Feet is unchanged. The main task's installed wrapper temporarily references `Resource/Heart Barberpole Field.scalar-diagnostic.fs` to force resource reload; retain that file in today's package. This task did not regenerate staged/installed wrappers. Earlier offscreen image evidence predates this expression correction; the updated canonical shader was compile-checked without a new render batch. This is not a certification of sustained performance or smoothness.
