# Heart Capsule — replacement for the legacy Figure sliver

The original SP Figure clip in Figure 9 had Spin 0.275548, X 0.084477, Y 0.002226, Size 0.311893. Its diagonal plane tumble approaches edge-on near quarter turns; this combination reproduced a near-invisible off-center sliver in a local render (old-edge.png). Native clip Transform was neutral. Original shader, wrapper and clip remain unchanged.

New independent source Heart Capsule installed in Figure 73 (UUID 153ced57-e447-49f6-bc26-27a95492caf3), available in the Heart copies bank. Retains capsule material, outline, relief and shadow rendering. Five native controls: Turn, Outline, Material, Float, Tilt. Existing Heart Smart Params supplies automation. Source XY and size removed; source centered with fixed radius 0.30 of the shorter frame dimension. Shared Figure Transform owns placement/size. Internal tilt is limited to ±60 degrees on both axes, avoiding the edge-on singularity. This intentionally trades full tumbling for a reliably present form; full in-plane Turn is retained.

Validation: 21 local GPU cases over seven tilt positions and landscape/portrait/square dimensions, with varying Turn/Outline/Material and elevated Float, all nonempty with zero edge alpha. Reviewed the actual rendered sheet. Native manual delivery passed 10/10 values across all five controls at 220 ms readback; live Tilt drive varied and two actual composition outputs visibly changed. 217 Python tests pass. These samples do not certify every combination or the full downstream effect stack. The new source has not been added to the engine's proven-bound registry.

Factory Home uses Turn 0, Outline 0, Material .65, Float .15, Tilt .5. Recovery result is recorded in live-remaining.json; captures and scripts are retained in this directory.

Live recovery passed: 5/5 factory values after disturbance and again after Open; 5 drives opened, zero remained after Home, no active amount-bearing effects. Session left on Capsule Home, other layer opacities zero.
