# Route follow-up — fresh root evidence

Offline review of `sp/show-day/integration/rehearsal/after-native.json`, `routing-current.avc`, `rgb-results.json`, `REPORT.md`, `rgb-review.png` and `rgb-cleared-4.png`. No live calls or changes performed.

## Confirmed observations

The RGB review visibly shows white baseline/zero-delay Capsule and RGB orientations separated at offsets; the cleared frame is white again. JSON agrees: rgb-zero = Opacity1, delays0/0/0, bypassfalse; rgb-offset = 1, 0/.15/.30, false; rgb-cleared = 1, 0/0/0, false. This supports **sampled direct-input processing and return**, not measured latency or routed-loop acceptance.

Active clips from after-native match exactly one clip each by zero-based layer/column in routing-current's active deck. Relevant user-facing addresses below are one-based; revalidate them before use.

| Active clip | Saved source and routing | Semantic status |
|---|---|---|
| Feedback L1C17, FM · Static Rotate Left Z [1.4.1] | VideoSourceFeedback; no explicit Input params. | Native Feedback source. No specific router endpoint established by this serialization. Do not treat as the earlier SPHeartFeedback candidate. |
| Sculpt L2C1, level | CompositionRouterVideoSource, Input=`1:1`; Input Opacity BOOL=true. Input Bypass/Solo omitted. | Prior native verification explicitly mapped `1:1` to **Group 1**: `sp/design/heart-performance-plan/feedback-instrument/remaining-gaps.md`, Priority 2. Fresh group membership matches that record: field/delay/figure/glyph. This is the established mapping usable for the next test; do not generalize token parsing. |
| Delay L4C1, figure | CompositionRouterVideoSource, Input=`3:5`; Input Opacity BOOL=true; Input Bypass/Solo BOOL=false. | Source clip label suggests Figure, but no independent semantic mapping for `3:5` was established in this review. Require native Input dropdown/readback confirmation before naming its endpoint. |
| Figure L5C73, Heart Capsule | GeneratorVideoSource. | Existing visible seed source; root already observed two different poses. |

Fresh native group ID1788405566947 is named `Group #`, opacity1, bypassfalse, solofalse. “Group 1” in the older semantic record means the first group, not a requirement that its editable display name literally equal Group 1. XML has one group with field/delay/figure/glyph as members. Treat the ID as evidence from this snapshot, not a future mutation address.

## Input Opacity semantics

Installed official help at `/Applications/Resolume Arena/docs/help/English.xml:539` explicitly describes Video Router Input Opacity as whether the router takes source opacity into account, a pre-/post-fader toggle. The following entry describes Input Bypass/Solo as whether source bypass/solo are respected. These are **Video Router** entries; the separate Advanced Output slice entries at line1219 are not needed for this conclusion.

Both active routers explicitly serialize Input Opacity as BOOL1, so zeroing their feed's opacity can remove their input. With all member/source faders at zero, Group 1 has no fresh visible seed. The isolated black captures therefore **do not establish a route defect**. Sculpt's omitted bypass/solo setting should be read fresh if needed, not inferred from Delay's explicitly false setting.

## Minimal next live configuration: prove Sculpt with an upstream seed

1. Snapshot fresh current state and bindings. Keep the connected Figure Capsule and Sculpt level clips; no route reassignment, scratch source or composition reload needed. Verify the same one-group membership. Keep Pixel Melt, strobe and unrelated effects zero; preserve their settings for restoration.
2. Set **Figure opacity1, first-group opacity1, Sculpt opacity1**; other layer opacities0. Ensure Figure/group/Sculpt are unbypassed and solo does not exclude them. Keep the source moving via the already-tested Capsule Turn control. Crucially, do **not** mute Figure to isolate Sculpt while Input Opacity remains true.
3. On Sculpt's freshly identified DelayRGB, reuse the just-verified zero-delay versus R0/G.15/B.30 sequence at effect amount1. Expected composition evidence is the new colored delayed orientations correlated with the offsets, returning to the white source when all delays return to zero. The still-visible raw Figure alone is insufficient evidence; the **incremental RGB response** distinguishes Sculpt's routed processing from that raw Figure. If a native Sculpt-layer monitor is available, inspect it as corroboration without relying on a guessed endpoint URL.
4. If raw Figure remains visible but RGB response is absent, inspect the actual Sculpt Input dropdown semantically, clip-level processing/blend, group state and layer opacity before declaring a route fault. Do not repair serialized tokens. Finish with tested effects zero and restore snapshots.

This is the smallest evidence-supported next test: keep the existing Figure feed on, add Sculpt visibility, and reuse its known working processor. No hidden-source/pre-fader toggle change is required.

## Delay and Feedback follow only if needed

- **Delay:** first inspect its actual Input choice in native UI (REST sourceparams are absent in after-native). If it explicitly identifies Figure, keep Figure opacity1 and enable Delay opacity1, with Sculpt/Feedback zero and the group enabled. Prove an incremental known processor response or inspect the native Delay-layer output; seeing the unchanged raw Figure does not independently prove routing. If the dropdown identifies a different input, feed that observed endpoint. Do not set or decode `3:5` by guess.
- **Feedback:** retain current native Feedback clip identity and provide a visible seed before enabling its output. Its absent Input serialization does not establish whether or where it samples composition history. Read the native source description/control UI first; a black history with no seed is inconclusive. Do not use SPHeartFeedback Reset trails or behavior commands on this native source. Root can leave this branch unverified without delaying the bounded Sculpt proof.

## Evidence freshness and limits

`after-native.json` is a saved moment; root REPORT describes subsequent cleanup/end state. Re-discover before acting rather than treating those faders as current. Report explicitly whether acceptance is direct-input, routed Sculpt, routed Delay, or native Feedback. This document upgrades only the direct-input RGB evidence and identifies the established Sculpt feed; it does not certify either untested route branch.
