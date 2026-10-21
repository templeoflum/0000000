> **Correction:** all thumbnail-derived placement proposals below are unvalidated hypotheses, not an accepted content audit. See ../live-inventory-pilot/ for the subsequent live pilot. “Discovery” counts cover recognized source OR clip-effect sections, not guaranteed source adapters.

# Content discussion — inventory first

Read-only snapshot of running **Fluid warp - Shell**, selected deck **Gradient**, September 8, 2026. 281 populated entries, including 245 named FM imports. No clips were launched, moved, renamed, or deleted. This is the currently exposed deck; other decks and saved compositions remain outside this inventory. See INVENTORY.md for every clip and effect stack, inventory.json for source parameter names, composition.json for raw readback, and heart.json for controller state.

## Likely placement changes to discuss

- **L6C40 CloudVortex, Glyph → Field:** cached thumbnail shows a cloud tunnel covering the frame. Exposes rate, loops, radius, roto and turbulance. Strong candidate for spatial/background content rather than glyph detail.
- **L6C48 Abstract Field, Glyph → Field:** cached thumbnail shows a broad textured field; exposes Octaves, Amplitude, Density.
- **L6C42 CosmicJourney, Glyph → Field or Texture:** thumbnail is a screen-filling colored pattern; final role depends on how it is played.
- **L5C65 Gradient Bars, Figure → Field or a utility/pattern bank:** thumbnail reaches the edges, unlike the intended contained Figure source. Also exists at L3C20 and L6C64. Compare settings before consolidating.
- **L6C60 Balls and Springs, Glyph → Figure candidate:** source describes elastic balls in a rotating box and thumbnail agrees. Needs background/alpha and containment work before promotion; not an automatic move.

Thumbnails show stored poses, not range-wide containment or live correctness.

## Concrete cleanup and stack questions

- **L7C24 “FM · Edge Detection [1.8.10]”** is a Video Router with only Transform. The named Edge Detection effect is absent. L7C22 has EdgeDetection. This is a real name/stack inconsistency, not merely an artistic classification question.
- **L7C16 MTK_Filmschool_1.2** has that effect twice, on either side of Transform. May be deliberate; compare before removing anything.
- **SP State Test:** L5C62, L5C66, L8C9. **Test Card:** L6C26, L6C61. Diagnostics should be visibly separate from performance navigation unless deliberately used as material.
- **Glyph has ten Gradient entries (L6C27–36)** plus Color Wheel, Checkered, Spiral, Lines and four consecutive Sine Wave entries. Field also has a large appended basic-generator bank (L3C93–108); Grain contains Lines, Checkered and Spiral. These are candidate families/variants rather than a meaningful linear performance order.
- **Metaballs:** L5C15/63/70; **Hopf fibers SP:** L5C61/64; **Gentle Rings SP:** L3C92/96; plus Multi Cube, quaternion slerp, ocean waves and other repeated sources. Repeated source identity does not mean identical settings. Preserve variants until compared.
- Imported names retain old deck/layer/column codes; those codes no longer describe current addresses. Early curated material and FM import banks are separated by empty columns, then mixed utility material is appended at the end.

## Cases to leave alone pending actual performance testing

- **L5C39 Quantum Carpets:** despite the name, its stored thumbnail is a small central form with room around it. Its original JSON describes a nonlinear Schrödinger simulation. Do not reclassify just because “carpet” sounds like a field.
- **L3C38 Klein bottle figure 8 immersion** is a full-frame color mapping in both source code and thumbnail; **L5C52 Klein Bottle (3D)** is a tiny raymarched object. Their different layer assignments make sense.

## Controller coverage gap

Offline inspection follows Heart's current allparams / atom_sections discovery, without constructing or activating clips:

- 25 entries have an atom/adapter section.
- 12 have legacy named Drive controls.
- 244 have neither source-discovery path. Of these, **182 already expose numeric source controls** that could be adapted.

These are clip-entry counts, not unique shader counts. Routers and utilities are included. Layer/clip effects may still be controllable separately. “Discovered” is not a claim of musical readiness, visual correctness, dependency completeness, or acceptable FPS.

## Proposed discussion order

1. Confirm the spatial roles of the named placement candidates.
2. Decide how utility generators, diagnostics and intentional variants should appear in navigation.
3. Resolve Edge Detection and duplicated effect-stack questions.
4. Select the first compatibility batch from the 182 unadapted entries with existing numeric controls, prioritizing desired content rather than alphabetic order.

No reorganization should occur until this discussion. The raw JSON is an audit snapshot, not a native composition backup for a future rearrangement.
