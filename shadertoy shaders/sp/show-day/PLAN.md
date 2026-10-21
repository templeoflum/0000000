# Heart show-day work division — September 9, 2026

Coordinator: existing task “Review current shader workspace”. User leaves today. This handoff overrides obsolete execution priorities in earlier design docs, not their historical evidence. Tasks should distinguish implemented, tested live, sampled only, and unknown. Do not call sampled content fully ready.

## Non-negotiable direction

- Make the existing instrument playable. Existing Smart Params supplies relationships/automation. NO independent generator architecture, preset-system rebuild, telemetry project or cosmetic monitor redesign.
- Keep Soup's eight-layer roles and original composition/shader identities. Shader edits produce separately named sources/wrappers. Original clips and old compositions remain usable.
- Figure source: complete centered subject with breathing room before effects. Shared Figure Transform owns XY/size. Effects/cloner tails may extend offscreen; cloner center must remain useful. Do not crop to fake containment.
- Home/Settle is a settled orientation state. Open explores drives, never enables every effect. Shuffle preserves scope and locks. Strobe is momentary; other effects use directional envelopes/hold semantics.
- Root owns live mutations, installations, shared engine/config changes, app restarts, composition saves and dashboard publishing. No workers independently touch live Resolume or start GPU/local-model batches concurrently. Never change sleep/security/caffeinate settings.
- Use deterministic extraction first. Worker docs: sp/workers/benchmark/RESULTS.md, sp/workers/ollama/README.md, sp/workers/hermes/README.md. Local/cloud workers are optional; review their output. Avoid GPU model contention with performance testing. Never expose credentials in reports.

## Current evidence

- Shared queue-loss fix: mixed live control workload 149/156 before, 156/156 after.
- Narrow-range startup fixed: Checkered 8–32 had 13/40 excursions before (peak509); 40/40 samples within range after. Active range morph remains continuous.
- Last full Python suite:220 passes. A subsequently added navigation test passed with navigation suite4/4; full total should now be221 but has not been rerun. UI script syntax checked; latest navigation UI not pixel-reviewed.
- 14 new Heart copies now available (13 prior plus Capsule). All have factory rest and live Open/Home cycles, 123 distinct rest parameters checked across runs. This does not cover all legacy clips.
- Heart copies bank, Forms bank, All sources, optional Explore figures (21 entries:9 copies +12 reviewed original candidates). Live Explore next/prev73→7→73 passed. No physical relocation yet.
- Repair copies: Figure7 Solid,10 Ring,11 Spike,12 Crystal,13 HypnoWorm,14 Torus,71 Klein Bottle,72 Melting Fractal,73 Capsule. Field4 Quaternion Field,5 Swell,6 Paper Fractal,7 Vector Lattice,9 Concentrip,10 Puls Lattice,11 Ancient Temple,12 Kali Liberation,13 Color Wheel. Always verify live occupancy/identity; addresses are not permanent identities.
- Original black/thin source faults have replacement paths. Older reports still list these as unresolved; read newer repair reports and dashboard overrides.
- Native Heart Monitor and surface already exist. Current last known Heart PID91728; do not rely on stale PID. Live state may change; inspect fresh before acting.

## Full remaining inventory and ownership

| Area | Remaining work | Priority | Owner |
|---|---|---|---|
| Show set / shader coverage | Separate usable controls from Speed-only/unsupported controls; identify shortest useful per-source repair batches; establish dependable selection beyond copies | Today | Content task |
| Figure geometry | Candidates still lack full-range containment; GeodesicTiling tight framing, Melty Boi outer rings, edge-contact originals, dim cases | Today for chosen show set; library-wide later | Content task, root validates |
| Field / Texture / Grain | Dark/flat samples (cubes+spheres, Creation, ShaderLamb), noisy Potential Energy, camera overshoot/ocean/portals; distinguish intended visual from actual fault | Today triage; selected fixes | Content task |
| Physical content sorting | Field-like content in Figure; diagnostics interspersed; duplicates; verify settings-preserving copy before relocating, retain old originals | Today useful bank; migration only if safe | Content proposes, root executes |
| Effects controls | Confirm numeric drives, trigger/event/color/choice access, bypass polarity, live readback, rapid IN/OUT, strobe release, envelopes and cancellation | Today | Effects task |
| Feedback / Delay / Sculpt | Confirm tap routing, clone center/dead zones, useful defaults, buffer clear, router reconnect; current library differs from old37-clip baseline | Today | Effects task |
| Core performance | Integrated rehearsal: launch→Home→Open→shuffle→effect→Settle; quick nav across layers; no stale targets; output/source mismatch | Today | Root |
| Surface / gestures | Verify A/B independently drivable, labels stable, scope visible, fader spring/physical-click latch and trackpad mappings; no redesign | Today regressions only | Root with recovery checklist |
| Lifecycle / monitor | Cold start, reconnect, process pause and explicit resume; orientation, detach/dock, source resolution; clean error/status when unavailable | Today | Recovery task, root live |
| Travel package | Launcher resolves paths, dependencies available offline, compositions/media/source patches in known locations, backup and recovery instructions | Today | Recovery task |
| Portal / Treehouse | Original media relinking evidence exists; videos may remain missing, routing/mappings need current verification | Today inventory; enable if needed | Recovery inventories, Effects maps, root tests |
| Legacy Home coverage | New copies tested, many original factory/fallback/saved Homes not rendered/relaunch tested; no automatic overwrite of user Homes | Chosen show set today | Content proposes, root tests |
| Performance tuning | Sustained GPU/FPS acceptance under actual powered show setup; avoid blanket optimization on this unplugged/shared-GPU session | Only obvious blockers today | Root |
| Deferred | Glyph, beatpad/audio mapping, usage telemetry, PBF4/KnobX1 polish, exhaustive combinations, new model orchestration, styling, preset expansion | Later | Nobody today |

## Independent tasks and file boundaries

1. **Heart — Content readiness** owns sp/show-day/content/ only. Read all source/audit data; write CURRENT-INVENTORY.json and PRIORITIES.md with per-source role, actual evidence path, control gaps, replacement, next action. Stage up to two highest-value source repairs in this directory if clearly justified; fresh names only. No installing, shared catalog edits, GPU rendering, live API mutations or bank changes. Prefer finishing useful inventory over broad speculative fixes. Reuse actual render evidence; do not classify on names/thumbnails alone.
2. **Heart — Effects and routing** owns sp/show-day/effects/ only. Inspect current engine/contracts/tests and saved compositions. Deliver matrix of effect controls, trigger access and routing, distinguishing verified facts from stale evidence; stage focused tests/patches in owned directory if a concrete bug is proven. No shared engine edits, live API mutations, composition saves or installations. Flag show blockers before refinements.
3. **Heart — Departure readiness** owns sp/show-day/recovery/ only. Inspect launcher, monitor, dependencies, saved media links/compositions and recovery code. Produce startup/preflight/recovery card and missing-path inventory. Stage narrow fixes if needed. No app restarts, OS settings, broad filesystem copies, live playback changes, shared app edits or credential output.
4. **This task — Integration and live rehearsal** owns shared code/config and sp/show-day/integration/. Review staged proposals, apply fixes serially, run focused tests and single-owner live rehearsal, publish dashboard and current handoff. Root grants explicit live testing windows if delegated later; no simultaneous Arena control.

All tasks must finish with: evidence examined, exact files produced, checks actually run, unverified assumptions, proposed integration step. Report progress only in owned STATUS.md. Shared progress.json/update.py are root-only. No unsupervised recurring tasks.

## Integration sequence / completion gate

1. Receive quick blocker findings from three tasks; pick known usable show set and essential controls.
2. Integrate bounded changes one at a time with focused tests. Snapshot relevant config before live modifications. Do not reopen completed architecture work.
3. One live rehearsal: start/reconnect, Figure + Field selection, driven source/effect, musical timing, all-layer navigation, settle/recover, input release, monitor check. Confirm native state and visible output; physical feel still requires user feedback.
4. Save a clearly named show composition/copy and backup only after verifying correct live composition and authorized scope. Preserve originals. Verify launcher and assets from intended locations.
5. Publish “what works / known limits / recovery” handoff. A full library audit is not a prerequisite to having a reliable show set; untested sources stay explicitly marked.
