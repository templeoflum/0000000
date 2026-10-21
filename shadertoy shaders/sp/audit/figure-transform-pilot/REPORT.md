# Figure → shared Transform pilot

First adapted source: `SP Figure Solid Source.fs`, independently installed native UUID `8e016778-0fe3-4b4e-ad29-13b2c019ba09`, Figure slot 7. Original SP Atom Solid source, installed patch and existing clips unchanged.

Removed source X/Y/Size inputs; centered shape uses a fixed proportion of available source space. Shadow offsets, softness and margin scale with the shorter frame dimension. Internal 3D Tumble/Axis remain: they reveal different surfaces and are not equivalent to moving/rotating the finished image. Heart catalog and copied atom relationships exclude removed controls.

The existing native Figure layer Transform is already first (index 0), before Twitch/LUT/cloners; no duplicate effect inserted. Independent live position/scale/rotation changes left all source parameters unchanged after waiting for Home to finish. Native Transform controls are still pixel/native units; resolution-relative control mapping and transform-level containment are not yet implemented.

Nine source GPU renders: landscape640×360, portrait360×640, square512×512, each default/shadow+emboss/shape stress. All nonempty with zero edge alpha. This is sampled verification, not an exhaustive guarantee over all shapes and combinations. See containment.json and check-*.png.

Live chain images: live-source.png, live-transformed.png. Initial current cloner settings did not create discernible repetition; explicitly configured 7 clones, one tail, scale80→45%, tail length.5, no delay, zero rotations/distortion, distribution50%. `live-cloned-configured.png` visibly verifies repeated source geometry allowed offscreen. Pilot left running with Tumble/Morph/Hue driven and Linear Cloner at full amount. Other layer faders/effect amounts parked for isolation; no restoration requested. Test fade timings .15 seconds remain on tested composition/Figure effects.

Next: source-aware normalized Transform control ranges, then adapt Shell and other figure candidates after actual audits. No claim that remaining shader inventory has been converted.
