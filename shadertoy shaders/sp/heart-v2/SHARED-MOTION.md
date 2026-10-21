# Heart · shared motion

Motion contract · September 12, 2026

Resolume owns the parameter endpoints and timeline programs. A paused Timeline prepares a numeric parameter for Heart.

## Controls

| Control | Behavior |
|---|---|
| Amount | Fraction of the native range traversed by a drive. Source Amount scales each parameter’s Amount. |
| Range offset | Position of the sweep inside that range: start, center or end. |
| Phase offset | Timing relative to the other drives. |
| Mult | Phase distance travelled per beat, with a continuous transition between rates. |

The normalized output is `(1 - amount) * range_offset + amount * waveform`. Amount and Range offset run from zero to one. At full Amount, the complete native range is used. At zero Amount, Range offset selects a stationary position. Native reversed and equal endpoints retain their meaning.

The source editor replaces the disabled Low/High fields with Amount and Range offset. Resolume’s current endpoints are available on the value field’s tooltip. The existing ratio, fractional Mult, phase offset and shape controls remain in place.

## Clock

One monotonic beat transport supplies every motion interval and rack beat. One cycle at 1× and ratio 1:1 remains 32 beats.

Global, group, section and layer factors accumulate shared phase distance. Each source/effect accumulates its own Mult from that distance. Parameter ratios and multipliers consume the source interval. Rate changes integrate smoothly; they never multiply an already accumulated phase by a new speed.

Fixed rates share interval calculations. Changing rates are integrated across their transition boundaries, including scheduler stalls. Elapsed musical time is retained. Rendering resumes at the current phase instead of replaying missed frames.

Prepared drives keep their clock when Drive is off. A newly prepared parameter joins its source’s accumulated timing, including earlier Mult changes. New clips join their layer’s running relationships and enter from their native position over 150 ms.

Hold freezes motion phase and its transitions. The beat transport and effect releases continue. Downbeat resets the shared phase explicitly. Base/Safe restores scoped controls while the current native-phase clocks continue. Ancestor multipliers are restored only when the return includes every target they affect.

## Discovery and delivery

A persistent discovery process separates active clips from animation inspection. Catalogue patches carry changed targets and layer activity. In the live stage sample, a patch was about 10 KB; the complete catalogue was 1.17 MB. Independent clip changes do not invalidate unrelated mode inspections. Selected layers receive priority. Changed clips retire their outgoing bindings immediately and receive priority preparation checks. Native In/Out edits preserve existing Heart drive contracts.

Background inspection is bounded. Static controls become drives after their paused Timeline is detected. Prepared metadata expires after six seconds without renewal. Unknown structural changes require Refresh. Full-composition reads occur at startup and deliberate Refresh; panel reconnects use the current cache.

The timing loop publishes a single replaceable frame. Transport backpressure replaces older frames without delaying the clock. Delivery uses one frame’s sample for every ready destination. OSC bundles split at a 1,200-byte packet budget.

Identity checks refresh separately, with four concurrent reads, a 200 ms lease and a 180 ms request timeout. A failed or expired destination stops receiving frames while other valid destinations continue. Frames older than 100 ms are discarded. Native mode changes and binding generations retire stale routes. Heart launch fencing and the blocked-frame starvation fix remain in place.

“Waiting” indicates pending delivery or expired preparation. Delivery metrics describe outbound control frames; they do not measure Resolume’s rendered frame cadence.

## Verification

Evidence is stored in `checks/shared-clock/`:

- Backend regressions cover clock continuity, late preparation, independent controls, native mode handoff, recovery, scoped multipliers and output stalls.
- The complete server, discovery and bridge processes run against a fake Resolume for external clip changes and native range edits.
- Mocked compact/wide interface checks cover Amount, Range offset, fractional Mult, keyboard access and stable rows.
- Native installation and delivery records distinguish observed output from performer acceptance.

The complete show feature roadmap remains in SHOW-CHECKLIST.md. Hardware mapping remains a separate integration step.

## Installed evidence

The affected backend suite passed 130 checks. Compact/wide mocked controls passed, and the updated controls are visible in standalone Heart. Thirty-nine matching drive settings were restored.

Live sampling recorded 37,479 outbound updates over approximately eight seconds. Frame age was 3.37 ms at p95; the timing interval was 9.81 ms at p95. No destinations were waiting and no errors were reported. The sampled stage Level traversed 0.3101 while its paused timeline program remained identical.

The first installation exposed whole-catalogue overhead during native stage autoplay. Incremental catalogue updates resolved that regression before final verification. Clip-switch latency is covered by the isolated full-pipeline test; live musical feel remains performer acceptance.
