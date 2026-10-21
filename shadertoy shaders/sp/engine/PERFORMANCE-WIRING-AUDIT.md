# Heart wiring audit — September 10

Read-only review and six-second local-browser sample. No live settings changed during this audit. This is not a GPU benchmark or an end-to-end input latency measurement.

## Observed
- Two connected sources, 136 effect controllers, 1,026 numeric slots in the current surface state.
- The engine visits every effect motion controller each tick, including parked effects. Target 240Hz; recent logs show 70–80Hz with 128–259ms worst frames. During browser sampling: 133.8Hz and 134.11ms worst frame.
- Full UI snapshot ~773KB. Browser received 31 render calls in six seconds despite nominal 15Hz publishing. Workspace render median 5.3ms, p95 36.3ms. This measures only HeartSurface.render, not the whole legacy onmsg handler or native WebKit.
- Discovery refetches full composition every three seconds plus a follow-up. It separately reads each connected clip, tempo, and layer opacity/bypass/autopilot; the 26-layer composition implies up to ~78 individual layer reads per scan.
- Main motion loop also builds rich UI data: presets, Home descriptions, all effect schemas, all layer clip lists. These run in the same Python process as scanner/ownership and writer threads.
- Surface mutations use one executor. Ownership HTTP requests and configuration persistence can delay later gestures. The last repair removed persistence from the motion lock for shared gestures, but not every older path.
- Legacy shader controls, generic source controls, effect controls and several controller paths coexist. Automatic source discovery already supports native typed controls, but old behavior remains in runtime and UI reporting.
- Delivery coalesces values and limits each parameter to 60Hz. Empty queue does not prove smooth output. max_age uses the latest replacement timestamp, so it does not measure actual inter-delivery gaps.

## What follows from this
The runtime cannot presently guarantee smooth output. The evidence identifies uneven scheduling and excessive work, not one conclusively profiled root cause. Raising update frequency or shortening morph duration does not resolve missed delivery intervals. Browser and engine costs both need attention; GPU saturation is a separate question.

## Repair order
1. Measure actual generation/delivery intervals, command receipt-to-commit time, dropped/coalesced updates and scan duration. Keep instrumentation cheap and bounded. Establish baseline before another rewrite.
2. Make one canonical typed parameter binding: composition generation, native ID, scope, native range/type and live state. Controllers dispatch the same actions. Keep legacy compatibility at discovery, outside the performance loop. Preserve existing Smart Param relationships; no new modulation generator.
3. Remove static discovery, recipe/preset lookup and schema construction from the motion tick. Cache catalog/schema until changes. Separate compact value updates from catalog updates. Do not rebuild hidden controller panels.
4. Schedule only driven or still-transitioning parameters; retain observations/manual reachability for parked controls. Use one authoritative writer and coherent ownership state. Replace broad periodic scans with subscriptions plus bounded reconciliation where supported; verify API capability before changing protocol.
5. Keep claim, persistence and composition operations away from time-critical gestures. Avoid a per-input FIFO backlog; continuous input should retain latest intent, while button press/release ordering remains reliable.
6. Rehearse across multiple unmodified source types and an unfamiliar composition: discovery, manual movement, Open, range, Shuffle, stop/release, clip replacement and controller mapping. Quantify p95/p99 delivery gaps and command response, not average engine Hz alone.

## Behavior contract
- Any exposed numeric parameter may be mapped and driven through the same Smart Param path, converted to its native units only at delivery.
- Choices, booleans and triggers are explicit discrete actions, not continuously interpolated values.
- Effect activation is independent from parameter motion.
- Automatic discovery guarantees access, not a universally attractive visual result. Authored look suggestions are optional and must not restrict the core range/mapping engine.
- Preserve stage/output mapping and existing compositions throughout the repair.
