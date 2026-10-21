# Reusable source adaptation

Unprofiled sources now use the existing Smart Params engine through source_adapter.py. Authored profiles and user-saved Homes take precedence. Effects retain their existing policies and frame guards.

At Open, choose up to three continuous controls from live metadata, preferring structural then color controls. Park choices, integer controls, seeds/triggers, clocks, camera controls, and Figure placement/scale. Unknown continuous names are provisional candidates. Preserve current ratio, multiplier, phase offset and waveform; use a first exploration window of ±15% of the native-normalized range around the current pose. All parameters remain manually available. This is a general initial policy, not a visual or semantic guarantee.

Capture the first pre-Open pose for recovery in adaptive_homes.json, keyed by role, source identity, clip address and complete parameter schema. Later Open does not overwrite it. Schema changes invalidate that baseline. Captured means observed before Open, not necessarily visually good. Factory Home and global Settle use that baseline; explicitly saved user Homes retain precedence. Native externally-owned modulation is not seized by adaptive Open.

Offline census: 303 clip instances /198 source descriptions.31 authored-profile descriptions,113 additional descriptions with automatic candidates,54 manual/routing/review descriptions. Glyph remains deferred. Census classification is not live acceptance or proof every source is enrolled.

Validation:244 Python tests passed, including input classification, native unit normalization, timing preservation, speed-only parking, persistent baseline reload and schema invalidation. Native pilot: TileIllusion21, SpiralSurface25, TwinRays34, Creation48 automatically selected1–3 controls; readbacks moved, Home disabled drives and recovered captured values. Actual Home/Open outputs reviewed in contact.jpg. Creation remains visually subdued at its starting pose. No new per-source recipes or shader installs used. Full-library visual quality and sustained smoothness remain review work.
