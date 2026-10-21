# Queue loss during routine rediscovery

Reproduced persistent manual misses in a mixed four-clip workload: 149/156 targets passed. Seven misses remained at the old native value after another second while Heart reported the new manual base and output. A separate focused repeat passed 36/36, showing why short isolated checks missed the fault.

Cause found in scan rediscovery: every regular three-second scan cleared the output queue and changed its generation, even when the same controllers were retained. The motion loop had already cached a manual value as output; clearing it prevented later delivery and the unchanged value was not emitted again. Rediscovery also briefly emptied the public controller map.

Repair: unchanged controller maps preserve the queue and generation. Actual replacement still invalidates stale queued IDs, atomically publishes the new map, and invalidates surviving slot output caches so their accepted values are emitted again. Existing ownership and native-ID safety remain.

Validation: 214 Python tests pass, including two new regressions for unchanged-scan preservation and actual-replacement cache invalidation. Heart alone was restarted; Arena remained running. The same mixed workload then passed 156/156 live targets at the original 220 ms check interval (before.json / after.json). This is evidence for this race repair, not a blanket guarantee against network disconnects or every untested command path.

Global recovery checks are recorded in recovery.json: Settle → Open → Settle. They inspect reported slot drive states and effect envelope targets/observed values; they are not a full visual-performance rehearsal. The session is left settled after the checks.

Recovery result: 0 → 39 → 0 driven source slots; all amount-bearing effect targets and observed amounts remained off. After final Settle, 45 native source values were unchanged between readbacks 0.75 seconds apart (settled-native.json). Shader-internal clocks can still animate while external parameter drives are settled.
