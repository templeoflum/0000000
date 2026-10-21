# Heart · steady motion delivery

September 12, 2026

The performer reported visible jumps in Resolume during steady playback. Ordinary p95 frame-age reports looked healthy, so this pass recorded every outgoing OSC packet and reused the native identity readbacks already performed by Heart. It added no native subscriptions or polling. The optional diagnostic captures a bounded window and removes its wrappers afterward.

The first trace captured a 56.95 ms gap in motion sampling and a matching 56.84 ms gap in delivered values across the driven destinations. This was not just a slow parameter readback: the returned frame itself was fresh after the stall. A saved-library snapshot took roughly 44 ms to copy, and full JSON encoding added about 14 ms. The persistence update had moved file I/O into a thread while leaving the full snapshot copy on the timing thread; even threaded JSON encoding can hold Python's interpreter lock.

`MotionMemory` now replaces only changed records and publishes immutable snapshots. `MotionWriter` sends small, coalesced changes to a separate process. That process owns full-file serialization and atomic replacement. Acknowledgements preserve edits made during an in-flight save, and orderly cancellation waits for the acknowledged write. Failed saves remain pending for retry. A representative edit required 1,452 bytes and about 0.013 ms of preparation instead of copying a 2.9 MB history.

The initial save-worker comparison still showed shorter gaps during clusters of background clip changes. Heart had also accumulated roughly 14,000 untouched default parameter records. Defaults are now implicit; configured controls and explicit Drive choices remain in history. Existing files are compacted on load without dropping meaningful settings. Returning a configured control to its defaults removes its obsolete override. The measured cache reduced from about 3.3 MB of JSON to 276 KB, with 202 relevant targets retained. Routine catalogue reconciliation skips repeated work for unchanged controls and calculates valid motion scopes once per update.

The discovery worker now coalesces publications across 8 ms. Simultaneous layer changes become one coherent catalogue patch, retaining every changed layer and applying removals/replacements in order. Generation changes cancel queued publications. Identity validation keys also canonicalize member order, so reordering an unchanged drive set does not discard its valid lease.

The installed comparison delivered 6,894 packets over 20 seconds to 39 addresses. After the initial eight seconds, the reported routes had approximately 10.8 ms p95 intervals and 1.8–1.9 ms p95 frame age. Recent engine history in the overlapping window had a maximum gap of 14.71 ms; steady reconciliation peaked at 5.82 ms. However, this trace also caught a 201.63 ms interruption across the output while Heart continued producing fresh frames. Delivery reports show expired identity leases for all 39 drives during that interval. Successful existing native reads reached 136 ms; failed reads are not recorded by this trace, so it does not determine the full duration or cause of the native/API interruption. This is an unresolved delivery issue, not a smoothness pass. Retain the generation/version fences and bounded leases while investigating; do not mask it by silently expanding the stale-route window.

Verification is under `checks/motion-jitter/`:

- `baseline/` contains the original per-packet trace and its analysis.
- `save-worker-pass/` contains the intermediate comparison; it is not a claim that smoothness was already complete.
- `compact-pass/` contains the 40.51 ms intermediate comparison before discovery batching.
- `backend-batched.txt` records all 157 affected backend checks passing, including coalescing, generation changes, lease retention, persistence failure/retry, clip revisit and full process restart.
- `save-benchmark.json` and `compact-benchmark.json` record bounded-change and catalogue costs.
- Current `delivery-trace.json`, `engine-trace.json` and `analysis.json` contain the latest installed comparison.

The motion clock, native endpoints and paused timeline ownership remain unchanged. Diagnostics report real delivery gaps, and Heart's ordinary state now includes maximum tick/work times as well as p95. Outbound control timing does not establish the rendered frame cadence or replace performer acceptance.

The controller direction is now quick selection of the existing beat performance: tap tempo, set downbeat, choose kick/snare effects, switch between straight 4/4 and alternating kick/snare, and Run/Stop. The earlier proposal for direct button-played Hit/Hold envelopes was not accepted. Controller mappings are separate from this timing correction.
