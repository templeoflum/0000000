# SP Delay Chain retained-history investigation

Read-only inspection of installed `/Users/donovan/Documents/Resolume Wire/Patches/SP Delay Chain/SP Delay Chain.wire`. Hash and extraction checks: `DELAY-GRAPH-EVIDENCE.json`. No live calls, rendering, graph modifications or reset attempts.

## Concrete graph evidence

- **480 video-frame history stages:** Texture In node0 feeds Delay1, then Delay4… through Delay622. Following only Delay input0 connections reaches exactly 480 successive Delay nodes. Six main tap selectors take 60 history inputs at depths8,16,…480; the last input is node622.
- **16 further RGB frames:** mixer386 feeds Delay712…727, a separate 16-node chain. Switch R730 / G734 / B738 have 17 inputs: current mixed texture plus its 1–16-frame histories. Public R728/G732/B736 have range0–16 and each feeds a Round node before switch selection. RGB values are therefore whole-frame selections, unlike native DelayRGB's unspecified units.
- **Maximum texture-history path = 496 frame stages.** Topological inspection of all 678 nodes found no graph cycles and a longest 496-Delay path to Texture Out2. There is no internal feedback recirculation path in this graph. External input may itself contain history, which this bound cannot remove.
- All 496 Delay nodes have `clock=video`, texture2d input and null time-type. Installed official example `/Applications/Resolume Wire/Documentation/Nodes/77697265-4BEE-483F-9F28-1BA5F21193DB - Delay/77697265-4BEE-483F-9F28-1BA5F21193DB - Delay.wire` explains that texture Delay is one frame. Its general “up to 20 seconds” discussion is for other data types, not 20 seconds per texture node.

## Time units and useful warmup

Main capacity is **480 evaluated video frames**, not an unconditional eight wall-clock seconds. At 60 evaluated frames/s it is 8 s; at30 it is16 s. The full 496-frame path is approximately8.267 s at60,16.533 s at30,20.667 s at24. Rendering pauses/suspension do not count as advancing history; engine-loop FPS is not the relevant rate.

Tap positioning uses Transport Info365 bpm into Divide367 with numerator450, i.e. `450/BPM` tap-grid units per beat. Each grid interval represents8 frames; this expresses `3600/BPM` frames per requested beat, which assumes60 fps for real-time beat correspondence. Selector indices clamp to0–59. Span623 is a public0–16 value (default8); graph metadata describes beats. At120 BPM,16 requested beats reaches480 frames. Below120 BPM a requested16-beat span exceeds available main history and clamps; at a different evaluation FPS its wall-clock relationship changes. This is concrete fixed-60-fps arithmetic, not an adaptive frame-rate conversion.

Glide664 is multiplied by `60/BPM` via665/666 to set six Smooth durations; it is a beat-duration control for tap movement. A separate Span Smooth497 uses .8 as its duration constant. These smooth selector settings; they do not add texture buffers or erase stored frames.

For root's next observation, keep the intended Capsule input and this effect actively evaluating for **more than496 frames**. A practical20-second run suffices only if actual processing remains above about25 fps; otherwise count/estimate the actual rendered cadence and allow longer. Compare early and late samples. Warming while the effect is skipped/bypassed may not advance its graph; host scheduling is not specified by this patch. A raw current Capsule overlay does not prove the Delay input itself receives Capsule, so require eventual Capsule echoes, not just disappearance of Shell.

## Reset / Home behavior

Every Delay node contains an unconnected `reset` trigger constant. **Zero connections target any Delay reset port.** No exposed clear/reset event was found. Exposed events are Shuffle660, Home661 and φ693.

Home661 feeds Random694 fixed at0, which selects the home tap-pattern branch in six Switch nodes697/699/701/703/705/707. φ selects branch1, Shuffle selects branch2 and updates random controls. Transport Play709 and On Change710→Trigger711 also feed the home-pattern selection. None reach Delay resets. Thus **Home is not a buffer clear**, and transport start selecting Home is not proof of fresh history. Turning effect opacity off is an output control, not a wired reset. Do not send SPHeartFeedback Reset trails to this effect.

## Interpretation of root evidence

Viewed `remaining-review.png`: Delay ON visibly contains the prior multicolored Shell-like forms behind white Capsule; subsequent “cleared” sample shows the white source. That label alone does not prove internal buffers were cleared. `remaining-routes.json` confirms Figure1/Delay1 visibility for those three phases. Feedback seeded/history/off panels also visibly agree with root's report, but are a separate native Feedback source.

Retained Shell frames on first re-enable are **consistent with this graph**: there is existing history and no automatic reset connection. It is not enough to prove a bad route. The exact persistence while bypassed/hidden is a host scheduling matter not established by graph inspection. If Shell survives beyond496 actual evaluations with a verified all-Capsule input and no external feedback, investigate the upstream feed or whether this running compiled instance matches the inspected graph. Do not assume the filename alone proves compiled parity.

## Root warmup follow-up

Root reports45 seconds of continued moving-input warmup. Independently viewed `sp/show-day/integration/rehearsal/delay-warmed-on.png`: only white Capsule copies at differing orientations are visible; the prior multicolored Shell is absent. Together with root's unchanged routing, this supports fresh source reaching the Delay and replacement of prior history. It does not measure the exact flush duration or prove45 seconds is necessary. No graph repair is indicated. Operational note: expect retained frames after re-enable; warm with the intended feed, and do not advertise Home as clear.
