# Recall reliability audit — September 7, 2026

Scope: phase 4 completion, cancellation, missing targets and recovery. This audit used isolated test files and mocked renderer calls. It made no live API/UI calls, ran no models, and did not modify the performance composition. `sp/WORKERS.md` does not exist; the root `WORKERS.md` was read instead.

## Corrected in this pass

1. **Already-open snapshot could be falsely confirmed.** `patches.open_verified` previously accepted an unchanged name/layout after half a second even while the new open request was still pending. Recalling the same patch was the direct trigger. It now reads pre-request state and requires either an acknowledged request plus matching layout, or a newly observed root-parameter-ID generation / transition from a different snapshot followed by stable matching readback. Runtime IDs are evidence of a new load only; they are not persisted as target identities. A repeated same-name snapshot with unchanged IDs and no acknowledgement remains unconfirmed instead of being reported successful. Cancellation is checked again in the request thread before issuing the POST.

2. **Queued work was invisible to manual cancellation and writer gates.** `Operations.busy` now covers queued, running and cancelled-but-not-drained jobs. The existing `active` attribute still describes a running worker. The main engine integration owner changed manual cancellation, save availability and motion/effect writer gates to use `busy`. A superseded worker cannot clear newer pending work or overwrite its status with an old failure.

3. **Operation status publication could block the motion loop.** Both `busy` and `snapshot()` read nonblocking status fields. A test holds the operation write lock around a blocked mock renderer call and verifies that status still publishes. The snapshot is observational; individual fields can reflect adjacent transitions and are not an authorization boundary. Token checks remain locked for writes.

4. **Explicit target identity mismatch could fall back to a coincident display name.** The main engine integration owner corrected `heart.apply_state`: explicit identities require unique matching identities; display-name fallback is reserved for legacy entries that contain no identity. Missing/ambiguous controls remain reported and skipped. Their three new tests cover this independently in `test_heart.py`.

5. **Recovery could overwrite manual bars/hold after cancellation.** The main engine integration owner moved the final recovery `STATE.update` inside `PATCH_OPS.write`. The audit now tests cancellation at the end of rollback: the performer's new settings survive and cancellation propagates.

## Confirmed recovery behavior

The real `heart.patch_recall` coordinator is exercised with temporary snapshot/JSON files and a fake renderer:

- A critical missing layer fails before recovery save or composition open.
- An apply failure attempts the recovery snapshot and reports restored controllable state.
- A second failure during recovery reports `recovery incomplete` instead of success.
- Cancellation while finishing recovery cannot overwrite subsequent bars/hold settings.

Open tests separately cover acknowledged same-snapshot load, pending HTTP with new root IDs, transition from another composition, unchanged stale readback rejection, wrong composition/layout rejection and cancellation before/after issuing a request.

## Remaining phase 4 limits — not a completed release gate

### Blocking writes delay manual cancellation

`Operations.write` holds its lock throughout the supplied function (`patches.py`, `Operations.write`). `heart.patch_recall` supplies whole `apply_state` calls, which can perform multiple synchronous renderer writes. `cancel()` must wait for that function to return, and it is invoked from the surface command handler. Thus cancellation discards subsequent writes but cannot currently guarantee immediate manual takeover during a slow HTTP request or multi-parameter apply. A deterministic test documents this latency boundary.

Smallest safe next direction: retain serialized mutation ordering, move cancellation intent onto a nonblocking token path, check it between individual parameter writes, and asynchronously defer the manual command until the current unavoidable renderer write has settled. Simply releasing the lock around an entire apply function would create interleaving and is not a safe fix.

### An issued native open cannot be revoked

`open_verified` issues the HTTP request in a daemon thread. Cancellation stops verification/remaining Heart steps, but the native request may finish later; it may also outlive the serialized worker and overlap a later open. The test `test_cancel_after_request_stops_polling_not_the_inflight_post` demonstrates this precisely. The cancellation status no longer promises that the currently rendered state is guaranteed to remain unchanged.

Next corrective step: track renderer-request settlement separately from recall-token cancellation; keep new opens serialized behind unresolved opens, and do not claim manual takeover is safe until the mutation boundary is known. A transport timeout is not proof that the native application abandoned the operation.

### Critical dependency/routing preflight is incomplete

`validate_snapshot` validates saved layer/clip names in the selected deck. `composition_signature` validates dimensions, named layer/group/effect layout and clip source descriptions. Neither validates installed-source availability or the actual router input/control values before mutation. The full native snapshot carries those values, but successful structural open verification is not proof that every routing dependency resolved correctly. Current integration still needs the source/routing compatibility and post-launch routing checks promised by phase 4.

Smallest next direction: capture a versioned manifest of required native source/effect identifiers and critical routing relationships, validate availability before opening, then recheck resolved routes after launches. Preserve optional-control skipping separately from critical dependency failures.

## Validation

`cd sp/engine && .venv/bin/python -m unittest test_patches test_heart test_targets`

Result at this handoff: **46 tests pass**, including **18 recall tests**. Existing unclosed-home-file ResourceWarnings remain; they are unrelated to these assertions. No GPU/performance claim is made from these offline tests. Rapid native A/B recall, cancellation during a real pending open, disconnect during recovery and the full sustained performance gate remain integration work.
