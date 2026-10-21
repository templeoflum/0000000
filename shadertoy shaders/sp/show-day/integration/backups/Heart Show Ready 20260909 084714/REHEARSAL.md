# Temporal rehearsal — current results

Fresh Heart/native bindings checked. Direct-input test uses a new Heart Capsule in previously empty Sculpt108, id1788780038810. Original sources/clips preserved. Capsule Turn changed every ~80ms; eight native output samples per completed phase. Capture requests are sparse and not fixed rendered-frame cadence.

RGB Delay: baseline/zero-delay input stayed white; G=.15/B=.30 produced distinct RGB orientations along the rotating capsule; returning all delays to0 returned white. Actual images reviewed. Native opacity1/bypassfalse matched the active phases; final effect opacity0/bypasstrue. This passes sampled direct-input visual response and recovery, not exact latency or the existing routed loop. Native units remain unspecified.

Pixel Melt: first output snapshot timed out after IN, before MELT_TRIGGER. No trigger was sent. Cleanup completed; connected state recovered and both tested effects were zero. Not a proven renderer crash or parameter fault. Effects worker found the same pose in earlier successful samples; no speculative settings fix applied. Remains unverified.

Routing: Figure source itself changes with the two poses; isolated current Sculpt/Delay/Feedback showed black while all upstream opacities were0. Fresh native routing-current.avc retained for exact route inspection; Input Opacity is serialized on some routes. This cannot certify a broken route. Existing route assignments were not changed.

End state: original Sculpt1 selected; Figure73 Home visible at opacity1; other faders0, test effects off. Test RGB delay values restored to original0/.15/.30. Global Settle used, so no claim of exact restoration of all prior performance motion/effect states (Pixel Melt had originally been on). Scratch Sculpt108 remains parked for review; do not include it in a final show save without review. No final show-save acceptance yet.

## Routed rehearsal follow-up

Sculpt: current Figure Capsule at opacity1 plus Sculpt1 produces RGB offsets; zero delays clears offsets. Full-resolution samples in routed-review.png. Earlier isolated black was inconclusive because input fader was zero.

Delay: SP Delay Chain produced retained Shell history initially. After45 seconds with moving Capsule, delay-warmed-on.png shows only current Capsule echoes. Installed graph audit confirms up to496 evaluated frames retained; no clear is wired and Home resets tap pattern only. Current feed and effect off recovery sampled successfully; exact latency not measured.

Native Feedback: visible Capsule seed at Feedback.85; history persists when Figure lowers to0; lowering Feedback to0 clears output. remaining-review.png.

Performance navigation: Heart bank next/previous/random passed; Open produced changing values without enabling parked effects. Rehearsal caught global harmonic Shuffle reverted by routine scan. Fix delegated; acceptance and departure save waiting on corrected retest.

Scratch L2C108 id1788780038810 was named Heart Capsule in both previous and fresh native reads (earlier manifest name was wrong). Cleared exact ID, verified empty with no video; native empty slot retains ID. Original Figure L5C73 preserved.

Global motion refresh repair integrated: existing motion/control stores retain Open depth, Shuffle relationship and per-slot settings, and global speed. Legacy source settings use native configuration writes; native Drive remains off.230 Python tests pass, including three real-refresh/reconstruction regressions. Heart restarted with current state; live replay pending.

Live repaired replay PASSED: bank-scoped next/previous/random; changing driven values after Open; parked effects remain off; harmonic Shuffle survives refresh; Settle stops all Heart-owned source drives and fades amount effects off. Evidence performance-results.json.

Saved departure pair: Heart Departure 20260909 070659. Native AVC and Heart JSON parsed, required dependency contract passed, saved/live signature matches, rehearsal scratch content absent. This is a verified save, not a cold-start or reload test. Pixel Melt earlier snapshot timeout remains unverified; current Hold/Latch native control checks passed.

## Show Ready save and reopen — 2026-09-09

Preserved both RGB stages: internal channel delays before ColourLoop, native Layer RGB after ColourLoop. Updated Heart labels and helper text; 47 interface checks passed, controls reloaded. No installed shader graphs retired.

Saved Heart Show Ready 20260909 082918, preserving current performance settings. Pair and dependency verification passed. Existing setup recovery reopened it successfully in 30.18 seconds: composition signature, active clips, layer levels/bypasses, source drive flags, phrase/Hold and both RGB stages matched. Additional comparison found no mismatches in saved instrument global settings or effect drive flags. Evidence: reopen-result.json, reopen-state.json and reopen-native.json. reopened-output.png confirms visible rendered output after recovery; it does not measure frame cadence. Full application/OS cold start remains untested.

Local recovery snapshot updated with this report and reopen evidence, with file hashes refreshed. Prior departure pair remains available. Next: audition the two toy shader pilots; remaining transition jitter is not declared fixed.

## Toy pilot live audition

Transit installed at Figure 74; Quasicrystal at Figure 75. Heart discovered Phase/Impact and Turn/Reveal and native values changed across three live samples. Transit visible in composite and isolated output. Quasicrystal initially rendered black: original wrapper omitted the imported image connection. Worker prepared an explicit internal Image-node connection; after integration/reload actual isolated Arena output is visible. Existing artwork and control identities preserved. Both authored still Home poses passed native readback after allowing the configured three-second morph to complete (the initial two-second Transit check was premature).

Evidence under sp/experiments/toy-shaders/evidence: live-results.json, isolated-74.png, isolated-75.png, transit-home-native.json, quasicrystal-home-native.json, packaging-fix.json. Sampled rendering/control response is verified; sustained cadence and exhaustive parameter-range behavior are not certified. Quasicrystal fixed output was checked at a still pose.

Capsule restored active and fader levels restored. Find pilots in Figure → All sources, slots 74/75; existing curated bank unchanged. Saved Heart Show Ready 20260909 084714; pair/dependency checks pass. This latest pair has not been reopened; 082918 remains the previously reopened recovery baseline.
