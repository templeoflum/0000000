# Figure batch 3 and bounded ring adaptation

2026-09-08. Progress is visible at http://localhost:8765/progress. Current corpus is 283 populated clips: one new source copy was added to an empty slot, with originals retained.

## Original Figure candidates

- L5C20 RainbowRingCubicTwist: 10/10 numeric readbacks. Scale .75 visibly cuts the ring at top/bottom. Original remains available, flagged for Figure use; bounded replacement is L5C10.
- L5C25 Crystal Drops: 15/16 readbacks within the bounded acknowledgement window. Quat W -.5 did not acknowledge; unresolved, not counted as passing. Satellite droplets visibly cross image boundaries in several captures. Needs bounded geometry or a different layer role, not just a camera default.
- L5C38 Spikeball_v2: 16/16 numeric readbacks. FOV .75 cuts spikes at the image edge. Source normalization of a zero quaternion is also an unguarded risk seen in code; not exercised here. Needs an adapted Figure source.

51 full-output samples across the three candidates (baseline, each numeric control .25/.75, driven samples) inspected via contact sheets. Geometry findings include actual edge contact, not thumbnail interpretation. Source camera/scale tests performed with composition and Figure effect amounts settled out. Clip transforms were neutral in inspected source records. Original restored values after individual probes were not all separately acknowledged, so samples are not a strict isolation certificate for every control. Source TIME continues. Sparse captures do not establish continuous smoothness or performance.

Local qwen3:8b schema extraction: all six exact-list checks passed, model unloaded before renders. Original installed sources inspected directly. See local-review.json, live-results.json, contact-*.jpg and frame-metrics.json. Brightness edge threshold is a supporting check, not an alpha/source-bound proof.

## New SP Figure Ring Source

Repo: sp/SP Figure Ring Source.fs
Installed copy: ~/Documents/Resolume Wire/Patches/SP Figure Ring Source/
Wire identity: b156eb75-752c-4458-9811-7cc6d5a5df40
Composition: Figure L5C10, previously empty. Original RainbowRingCubicTwist and its clip remain unchanged.

Removed source scale. Source projection uses the shorter frame dimension, keeping the entire ring inside the frame. The shared Figure Transform owns size/position. Existing four native controls (thickness, twists, rate, gamma) use existing Smart Params. Heart recognizes this source as having a conservative .46-short-side radius, alongside the Solid Source pilot, for its existing shared Transform/Cloner guards.

Analytical support: in ringColor, S is bounded by +/-.08. Outside radial P.x +/- .08001, output is explicitly zero. With thickness in its authored .5–2 range, normalized radius is bounded by (0.333 + .08001/.6)/1.18 < .396 of the shorter side. This is a bound around the geometry, independent of screen aspect, not a viewport-edge clipping mask. The slightly conservative .46 envelope used by Heart leaves additional safety room for its transformations.

First GPU run found a low-gamma full-frame haze: floating-point cancellation outside the theoretical ring support produced tiny nonzero RGB, amplified by gamma .25. Explicit zero outside the analytical support fixed it. No original shader overwritten.

Validation after fix:
- Nine GPU render cases at 640x360, 360x640, 512x512; defaults and parameter extremes including minimum gamma. Each run advanced 121 frames; final alpha edge exactly zero and nonempty geometry in all nine. containment.json.
- Actual Arena live load, four expected controls discovered. Three live thickness/twists readback samples varied; rate .58 and gamma .5 remained fixed. Initial source loading briefly exposed an incomplete schema; test now waits for expected controls rather than accepting a placeholder.
- Four live 1920x1080 output images reviewed, all with interior bounds and no lit edge pixels; ring-live-edges.json. Live baseline roughly x593–1326, y175–904.
- Saved Home pose; Home recall for this new clip was not separately retested. Thickness/twists motion settings persisted through existing per-clip config, but relaunch was not tested for this new copy.
- 208 engine tests passed after dashboard routes and known-source recognition change.

Left L5C10 running, Figure opacity 1, other layer opacities 0, composition/Figure creative effects settled out. No native app restart, sleep changes, original shader edits, or old composition replacement.

## Next work

1. Adapt Spikeball with a bounded source projection and guarded quaternion normalization under a new identity; exercise its shape extremes across aspect ratios.
2. Resolve Crystal Drops' satellite geometry/role rather than hiding excursions with a screen-edge mask.
3. Keep broad shader coverage moving; no current result accepts every shader or all parameter combinations.
4. Intermittent command acknowledgement remains a separate real issue, now also observed once in this batch.
