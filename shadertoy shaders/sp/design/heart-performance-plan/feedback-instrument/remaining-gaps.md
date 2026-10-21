# Remaining feedback and recall gaps

Read-only audit, September 7, 2026. Sources: root `WORKERS.md`, `../SPEC.md`, `../PROGRESS.md`, `../recall-audit.md`, this directory's live-review evidence, saved `sp/engine/patches/Feedback performance.avc`, and current engine/shader source. No live API calls, renderer mutations, GPU work or inference were performed. Saved snapshot facts below are not a fresh live inventory.

## Priority 1: restore the missing native shaping controls

The reviewed **heart feedback** clip at L1C6 contains Transform and SPHeartFeedback only. Original **map** at L1C1 contains Transform → SPChainMap → InvertRGB → Blur → Sharpen. Consequently, activating the candidate loses the original native inversion and linked Blur/Sharpen controls. `status.html` only creates the pair button when both effects are discovered; `heart.py` already handles the paired action.

Smallest next implementation: copy the native InvertRGB, Blur and Sharpen instances, including useful parameter settings and order, onto the candidate after SPHeartFeedback, initially bypassed. Preserve the original Map and its stack. Validate each effect individually and the pair from Heart, including release/focus loss and return to the pre-test state; then save a separately named reviewed revision. Measure costs after the root's current GPU comparison finishes. This restores output shaping; it does not put those native effects inside shader history. Persisting them across *all* feedback clips is a later placement decision because moving them onto the layer while retaining Map's copies would double-process Map.

## What is implemented versus equivalent

| Capability | Implemented | Remaining distinction/check |
|---|---|---|
| Movement | Per-frame scale, rotation, translation and center; Turn/Drift/Breathe/Fold reviewed live | No controlled same-input comparison against old native Feedback clips; effective speed depends on rendered frame rate. |
| Decay | Gain, floor subtraction and independent RGB multiplication inside history | RGB decay is **not temporal channel delay**. Keep its current accurate name. |
| Hue | Loop Hue modifies stored trails; native layer HueRotate modifies output afterward | Do not call the shader's gray-axis rotation identical to native HueRotate without visual comparison. |
| Inversion | Loop Invert changes nonempty history | Empty pixels remain empty deliberately, unlike unrestricted RGB inversion; native output InvertRGB is missing on the candidate. |
| Detail | Four neighboring history samples provide blur/sharpen around the current read coordinate | Different operator and placement from native Blur + Sharpen; not a replacement for the missing pair. |
| Fold/mirror | Loop Fold blends toward one horizontal fold; native layer Mirror is available | Not the old Kaleidoscope plus four independently controllable Mirrors. |
| Channel delay | Native DelayRGB remains on the feedback layer and was stress-sampled | Output-only, downstream of internal history. No temporal channel-delay history path has been implemented or demonstrated equivalent. |
| Mask | Shader Key controls final alpha from luminance; native layer AutoMask is available | Both are after internal accumulation. No controlled AutoMask/channel selection comparison; neither proves input/history masking. |
| Reset | Native event/counter clears persistent `acc`; offscreen tests verify actual zero and fresh-input recovery | Active native event delivery passed, but precise native buffer readback is not verified. Hold and clear remain separate operations. |

Avoid recreating temporal delay or the entire archived rack speculatively. First compare native output DelayRGB/AutoMask and the restored shaping stack using one fixed source, recorded settings/order, matched dimensions and explicit reset boundaries. Document desired differences before deciding whether a new history buffer or different routing is warranted.

## Priority 2: make routing a checked recall contract

Saved candidate routing is 1920×1080 Video Router → SPHeartFeedback, Input `3:2`; saved sculpt/level is 1920×1080 Video Router → SPStudyLevel, Input `1:1`. Prior native verification recorded those as **sculpt** and **Group 1**, respectively. Group 1 contains field, delay, figure and glyph. The candidate's persistent history is inside SPHeartFeedback; native clip/layer effects process its output. Do not infer arbitrary router enum meanings from those two observed values.

`patches.validate_snapshot` currently checks layer/clip names. `composition_signature` checks dimensions and named source/effect layout. Neither verifies actual router inputs, group membership or installed plugin identity. `heart.patch_recall` opens the snapshot, launches layers in saved order and applies motion once instruments resolve; it has no explicit upstream routing recheck.

Exact next implementation: add a versioned dependency manifest alongside each saved patch with required source/effect native type identifiers, scoped ordered effect instances, source dimensions, semantic router endpoints and group membership. Derive native identifiers from XML `uniqueTypeId` and installed `/sources` and `/effects` inventories (`idstring`); explicitly handle built-in type IDs and prove normalization rather than matching display labels alone. Runtime IDs must remain readback evidence only.

Before any save/open mutation, validate the manifest against the snapshot and current installed inventory. After opening and upstream launches, rediscover and verify those critical relationships before enabling downstream motion. If route readback is unavailable, report unverified rather than silently marking Ready. Missing optional controls can still skip; missing required sources/routes must fail with recovery status. Tests: unavailable Wire identifier, wrong input with identical layout, missing group member, changed dimensions, duplicate name, and successful fresh runtime IDs.

## Priority 3: finish release acceptance without overstating recall

The reviewed candidate is saved as **Feedback performance**; the dedicated Start button still recalls **Start**, an older Map-based patch. Do not overwrite it blindly. Once the revised instrument and routing contract pass, make the intended starting patch explicit while preserving existing recovery saves.

Recall cancellation remains bounded by blocking writes, and an issued native open can finish after cancellation. Follow the existing `../recall-audit.md` plan for request-settlement tracking and nonblocking cancellation intent before claiming safe rapid A/B/manual takeover under slow transport. Repeated successful recall does not test those races.

Remaining gates: controlled old/new visual comparison, full dependency/routing verification, matched performance baseline, and the 20-minute Heart-only performance session. Monitor appearance is accepted and outside this work.
