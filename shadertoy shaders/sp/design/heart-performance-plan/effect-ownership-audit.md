# Effect ownership audit and bounded fixes

September 7, 2026. Offline source/tests only; no native requests, restarts, local
inference, or GPU work during the root's live endurance exercise.

Three confirmed issues were corrected:

1. Parameter ID replacement discarded a momentary effect's pre-press amount,
   potentially leaving the full pressed amount stuck after client release.
2. A deferred reconnect return could overwrite a newer manual amount.
3. `release_all` released effect buttons but omitted held preset visits; those
   previously stayed active until disconnect.

Effect continuity now requires both the composition name parameter ID (native
open generation evidence) and effect instance ID to match. A parameter rebind of
that same instance restores the pre-press target, or its newer manual/latch target.
A different generation or different instance takes its native observed state.
Absent identity evidence does not authorize return transfer. Runtime IDs remain
session continuity evidence, never portable patch identity.

Reconnect returns are scoped to that pair and newer manual/press intent clears
stale deferred returns. Entries for effects no longer discovered are discarded.
Surface ownership holds actual Effect objects rather than names alone. Late
releases therefore cannot release another object's newer hold under the same key.
The shared release helper clears ownership before awaits, releases effect holds,
and unwinds preset visits only when the exact clip is still currently discovered;
this avoids stale writes to clips replaced by recall.

11 new tests cover nonzero baseline, both overlapping release orders, repeated
press, unrelated owner release, manual override, latch mode change, reconnect,
parameter ID replacement, newer manual intent, different generation/instance,
and release-all preset/exact-instance cleanup. Full engine discovery: 107 tests
pass. Existing release replacement fixture now includes the native identity
needed to prove continuity. Existing unrelated file ResourceWarnings remain.

Limits: native delivery during the fixes is not yet live-validated. If both native
instance IDs and parameter IDs change without trustworthy continuity evidence,
Heart adopts observed native state instead of guessing an old return. Preset
visits themselves are keyed only by pad, not client; two clients pressing the same
preset pad still share a single visit, so one release may end both. That separate
preset ownership model was not changed. Effect momentary ownership is per client.

## Integration-owner live validation

Fixes loaded after the endurance sample. `effect-ownership-live.json` records passing two-client overlapping holds with a .35 baseline, newer .7 manual intent surviving late release, client disconnect return, and reconnect return. Each settled amount was checked against native Opacity readback. Original effect configuration/amount restored afterward. This does not simulate a full composition replacement while two physical controls are held; generation/instance separation remains covered by isolated tests.
