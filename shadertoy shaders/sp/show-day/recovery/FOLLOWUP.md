# Launcher identity proposal and Portal reconciliation

## Staged launcher fix

`launcher-identity.patch` changes only `sp/launch.py`. `launch.proposed.py` is the review copy; it must not be launched from this staging directory because the launcher intentionally retains its original ROOT-relative paths. Apply the patch through the coordinator, not by running the review copy. `stage_launcher.py` reproduces the proposal from the shared launcher.

After the existing port/startup checks and before trackpad/build/open actions, the launcher waits briefly for both expected Heart services:

- HTTP `/status.html` must be 200, not redirected, and match the local Heart page exactly. Read length and timeout are bounded; local proxy use is disabled.
- WebSocket 8766 must emit Heart's existing status structure. The probe receives one message and sends **no control commands**. Connection, receive, close and message-size limits are bounded. A held Heart or disconnected Arena is accepted; this does not reinterpret motion state or require Arena output.

An unrelated page, unrelated WebSocket payload, wrong protocol, silent/stopped service or timeout now produces an actionable error and leaves the running session intact. Both original start paths, arguments, partial-port protective error, locking, build behavior and optional trackpad behavior remain unchanged. No process is killed. This checks accidental collisions; it is not authentication, proof of a particular PID, or protection against a process deliberately imitating Heart. Trackpad port identity is outside this narrowly scoped proposal. Exact page matching may conservatively reject a stale/different Heart checkout. A large/stalled status can also fail closed; bounds need confirmation during coordinator rehearsal on the real composition.

Offline verification: **13 tests passed**, covering expected held/disconnected state; unrelated HTTP/WS; redirect/status errors; HTTP/WS timeout; malformed/wrong-type payload; non-WebSocket service; occupied partial pair; existing service reuse; cold-start arguments. All I/O and subprocess actions are mocked. `git apply --check` passed. Neither endpoint was contacted and no app was started/restarted. The shared launcher is unchanged.

## Portal: unresolved assets, not a missed application of the recorded relink

All **290 recorded approved video destinations exist and appear in current restored Portal XML**. None of the missing references has an unapplied entry in `video-relink-report.json`. Thus the remaining failures are not evidence of an outdated pre-relink copy.

Current unresolved video identities reconcile to **139 historically not found + 5 deliberately unapproved candidates = 144**. All five candidate files still exist (three Blender MP4 alternatives, Cyberscape parent-folder candidate, NASA filename-only candidate). They remain candidates; no content equivalence or playback was established and no relinks were made. For the other 139, historical search found no candidate and bounded exact checks under the known `/Users/donovan/work/Visuals` mirror found no file. This means no known local replacement in the examined evidence, not proof they cannot exist elsewhere or on an unmounted disk.

The historical 140 not-found count includes `GLK VISUALS V4 FINAL.mov`, whose original paths are no longer present in the current XML. That explains the one-item difference; no assumption is made about why it was removed.

The first inventory intentionally counted fileName/path/filePath attributes only: 232 missing occurrences / 144 literal paths. This follow-up also reads paired `VideoFile value` fields: **464 missing serialized occurrences / 288 literal spellings / 144 normalized Windows paths**, representing the same 144 unresolved identities. These different denominators are not additional missing videos.

Exact evidence is in `PORTAL-RECONCILIATION.json`, reproducible with `reconcile_portal.py`. Checks use only current XML, recorded destinations/candidates and deterministic exact mirror paths; no broad disk scan. Current playback, clip relevance to the show, alternate file identity and live mappings remain unverified.

Coordinator next step: review/apply the launcher-only patch and run the staged test; validate service recognition in its owned launch/reconnect window. For Portal, select usable clips or explicitly review the five candidates only if needed. No automatic relink is justified by this audit.
