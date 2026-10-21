# Ongoing motion ownership — September 7, 2026

## Findings and implemented correction

The initial numeric-slot takeover checked Resolume's phase source once. Ordinary refresh reused a schema-stable Clip, never checked that phase source again, preserved the old manual pose, and left Heart's writer enabled if someone subsequently selected native animation in Resolume. A saved resume entry could also set `drive=True` after takeover had correctly marked a parameter external or unverified.

After the integration owner's approval, this pass added `sp/engine/ownership.py` and integrated it with `heart.py` and `delivery.py`. No live renderer tests were performed by this worker.

- A separate daemon observes native phase sources through read-only GETs. It does not run on the 240 Hz motion loop and never sends a native takeover request itself.
- The request ceiling is 20 GETs/second, one request in flight, a one-second HTTP timeout, and at least one second between probes of the same target. Four priority opportunities for moving/driven Heart-owned slots alternate with one opportunity for other numeric slots; oldest observation wins within each lane. Empty lanes lend their opportunity to the other lane.
- The observer pauses during queued/running patch work and while disconnected. It skips choice controls and explicit claims in flight.
- A response must still belong to the exact live Clip and Slot objects, the same parameter ID, output generation and explicit-claim epoch. Those conditions are checked again under the slot ownership lock. Late responses cannot release a replaced control or undo a newer manual/Home claim.
- Confirmed non-static native motion sets `owner=resolume`, clears Heart's drive flag, drops that target's queued value and stops subsequent writes. Other queued manual values survive. The WebSocket send path also checks the cached owner immediately before submission, so a value already removed from the queue is skipped if its owner was released meanwhile.
- Native static readback does **not** automatically reclaim a released or unverified slot. Reclaim is an explicit performer action.
- Existing refresh stores the normalized observed native value. External/unverified readouts publish that observation instead of the simulated Heart pose. Resume state cannot re-enable a foreign-owned drive flag.
- Every explicit claim advances an epoch. Discrete numeric Home/preset/drive-on actions additionally force the native phase source to static even when the cached owner says Heart. Choices do not receive phase-source DELETEs. Continuous manual motion uses cached ownership to avoid a DELETE per drag sample.
- Release/reclaim invalidates the previous-output cache, so returning to an identical Heart value after native automation still transmits that value.

## Latency and boundaries

This is bounded polling, not immediate event notification. With healthy fast responses, moving targets share roughly 16 priority requests/second and other numeric targets roughly four/second, with unused capacity borrowed between lanes. Coverage time grows with target count. A single target is not rechecked more often than once per second. The initial takeover still performs its existing one-time check.

Under the configured one-second timeout and scheduler sleep, a conservative lane sweep bound is roughly `5.25 × ceil(priority_count / 4)` seconds for priority targets and `5.25 × other_count` seconds for the other lane, plus the per-target minimum interval and thread scheduling overhead. Failed reads do not prove an external owner; they preserve the current ownership and increment the observer's error count. Disconnection/patch suspension and repeated failures mean there is no unconditional detection deadline. These are request-budget bounds, not measured live latency or a GPU-performance claim.

A command already submitted to Resolume cannot be unsent. The send-time gate prevents future submissions after detection; it cannot retract an in-flight message. Continuous manual dragging may briefly use a cached Heart owner until observation catches a new external animation; discrete Home/drive-on has an explicit forced takeover path. This observer covers native phase-source changes; separately re-enabling a shader's internal Drive boolean is not treated as a native phase-source change by this worker.

## Validation

`cd sp/engine && .venv/bin/python -m unittest discover`

Result at handoff: **70 tests pass**, including **21 ownership tests**. Tests cover initial ownership/failures, forced cached-owner reclaim, choice exclusion, resume ownership, native readout values, epoch/ID/generation/object invalidation, per-target queue dropping, send-time ownership gating, priority fairness, rate cap, pause behavior and no automatic reclaim. Existing state-serialization tests now mock explicit ownership claim because preset application intentionally performs native I/O; dedicated ownership tests verify that I/O separately.

An initial run of the older serialization tests reached the newly forced claim path without its new mock and was blocked by the filesystem/network sandbox before connecting. The fixtures were corrected and all subsequent tests are isolated; no renderer state was changed by this worker. Existing unclosed-file ResourceWarnings remain unrelated to these assertions.

Live acceptance belongs to the integration owner: enable native animation on one currently driven numeric control, observe Heart release and readout following; restore static and verify no automatic reclaim; invoke explicit Home/drive-on and verify native ownership returns to Heart. Repeat across reconnect and a Clip/ID replacement, then measure performance with the observer enabled.
