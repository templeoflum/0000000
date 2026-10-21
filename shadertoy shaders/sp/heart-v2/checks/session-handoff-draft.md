# Session handoff draft · authored motion and effect stacks

Installed: 20 ordinary Heart drives across nine original shader clips. Saved starting values are unchanged; each initial phase matches the saved pose. Family, Rate, Shuffle and Reset clip use the normal Heart controls.

## Starting motion

| Clip | Native clip ID | New motion ranges, in native units |
| --- | --- | --- |
| 1d | 1788149968298 | Position 1 0.458590–0.578590; Position 2 0.460385–0.550385; Angle 0.723369–0.793369 |
| 2d | 1788149968442 | Turn 0.000000–0.125000; Morph 0.000000–0.180000 |
| 3d | 1788149968406 | Tumble 0.433022–0.683022; Axis 0.187773–0.257773 |
| 4d | 1788149968262 | W 0.031493–0.271493 |
| shell | 1788149968226 | Turn 0.839899–0.999899; Morph 0.157583–0.357583 |
| hybrid | 1788149968334 | W -0.406569–-0.206569 |
| ground | 1788405553998 | Travel 0.886924–0.996924; Sway -0.041016–0.118984; Bob -0.447814–-0.327814 |
| room | 1788405554006 | Travel 0.333182–0.493182; Sway -0.879716–-0.759716; Bob -0.591883–-0.471883 |
| void | 1788405553990 | Travel 0.784336–0.944336; Sway -0.044487–0.075513; Bob -0.252202–-0.152202 |

Nominal periods are 48–80 seconds, translated to musical ratios at the current tempo. Ranges surround each saved pose; 2d’s controls retain their zero endpoint.

- All 339 existing timelines, their original ranges, and every other parameter match the preparation hashes. This motion batch leaves counts, quality, mixing, masks and geometry unchanged.
- 4D and Hybrid retain their internally integrated Turn/Spin rates. Line Rate and 2D Flow keep their internal clocks. Shell Turn is a direct position with no internal clock, so it receives Heart motion alongside Morph.
- **1d still has native effect opacity 0.** Its line motions are prepared, but the saved visibility was deliberately preserved. This needs an explicit performer decision rather than silently changing the starting look.
- Offline checks validate nine native bindings, exact starting values and 1,201 bounded waveform samples per added control. Rendered output and musical feel remain separate evidence.

## Effect stacks

The archive review parsed 68 of 69 saved compositions. The truncated `2021 template.avc` could not be parsed. The review covered 90 distinct effect names excluding Transform and kept repeated instances, including differently colored Strobes, distinct.

| Rack row | Stack | Existing native effects | Reason for this combination |
| --- | --- | --- | --- |
| Stage | Cut | Twitch + the black Strobe | Brief breakup and interruption of the Stage image; the black instance is bound by its exact native ID. These effect families occur together in 19 archived chains. |
| Figure | Prism | RadialCloner + MTK_Gradient_Shadow | A split figure with stepped shading. The current cloner uses two clones. These families occur together in five archived chains. |
| Field + video | Split | Linked Twitch + video DelayRGB | Shared breakup across the linked layers, with a delayed color response on video. Existing channel delays are R 0, G 0.15, B 0.3. These families occur together in 44 archived chains. |

Archive counts describe prior combinations, not visual acceptance of the current settings. No effects were inserted or reordered. Active Stage EdgeDetection/Dilate stay outside pulse stacks, preserving the steady Stage look. Groups, duplicates, masks, transforms and shared Figure drives remain intact.

Rows retain LUT On/Off + Decon, Pixel Melt latch, Blok, Melt hit and Twitch. Factor and RGB offsets expose native ColourLoop controls without replacing its Offset timelines. Trigger loops offer 4/4 Kick or alternating Kick/Snare, assigned per row.

## Evidence status

Motion evidence: `checks/session-starting-motion.json`; archive/stack evidence: `checks/session-effect-stacks.json`. Offline checks passed: three for motion, four for rack configuration, ten for the verifier.

**The new live nine-clip exercise was still running when this draft was written.** The latest completed `checks/session-native-verification.json` was an earlier capture failure with no motion checks and successful cleanup. Claim the new run only after its replacement reports `passed: true`, nine clip checks and `restoration.complete: true`. Rack and powered FPS acceptance require their separate evidence files; parameter motion alone establishes neither.

The verifier restores changed clips, programs and levels; keeps tempo untouched; and checks retained layer drive settings. It excludes untouched clip transport/autopilot controls. Relaunched clips resume their saved settings; exact previous oscillator phase is unavailable through the public protocol.

## Remaining performer judgments

1. Should **1d load visibly**, or keep its saved opacity at zero?
2. Play the prepared source motion and Cut/Prism/Split with music, then choose the preferred movement strength and default Kick/Snare assignments. The current configuration is a concrete audition point.
3. Choose the actual **Base** and **Safe** looks to capture for the show. Verification captures are not a substitute for those deliberate choices. Saving the native composition remains a user action.
