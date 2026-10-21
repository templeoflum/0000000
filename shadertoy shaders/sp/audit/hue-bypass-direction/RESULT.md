# Hue Rotate live feedback check — 2026-09-08

Rendered saturation test: Opacity=1 and Sat. Scale=0. Bypass true retained color; bypass false produced grayscale. Native bypass polarity is therefore correct. Original touched values and Heart hold were restored.

Heart previously read effect indicators from the periodic composition snapshot. Added subscriptions for each live effect's bypass and opacity on the existing Arena WebSocket. Subscription updates feed observed state directly; older snapshots cannot overwrite newer feedback, and output echoes cannot rewind active/recent fades. Subscriptions follow current effect identities and reconnect with the writer.

Four external bypass changes matched Heart, measured 61–155 ms after the REST write completed (see live-feedback.json). Heart's own press/release command path then enabled Hue Rotate to opacity 1 with bypass false, and disabled it to opacity 0 with bypass true; both matched native readback (heart-toggle.json). Restored the original off state. 176 Python tests passed.

This verifies the current API-to-Heart state and toggle path. The reported earlier persistent inversion was not independently reproduced; delayed snapshot feedback was a confirmed weakness, not proof of every previous mismatch's cause. No shaders or compositions were edited.
