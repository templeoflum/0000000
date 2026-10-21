# Motion multipliers · September 12

Global Mult is directly below the header alongside 60, 70, 120 and 140 BPM buttons. Source editors and each Drive-bank target have Mult buttons. Drive-bank layer and native group headers have independent Mult controls. Stage sections and the whole-stage row have Family, Mult and Shuffle.

Every Mult control offers ¼×, ½×, 1×, 2× and 4× plus a typed value from 0.001× to 64×, including 0.025×. Changes ease over one beat using the BPM at the moment of the change. Changing a multiplier during a transition starts from the current speed; phase is not reset. The displayed multiplier is that control’s own requested setting. Cycle readouts include all applicable factors.

Global × native group × layer × stage section scales the target’s existing speed, family ratio and per-parameter multiplier. A whole-stage multiplier is its native group multiplier and is counted only once. Scoped multipliers follow native membership across clip changes and clear on composition changes. They are runtime performance settings; no saved-motion-bookmark system was added. Global Mult changes Heart drive clocks. It does not change native BPM or the timing of effect-hit envelopes and rack loops. BPM buttons use the existing native tempo command.

Stage Family spreads family positions across active unlocked prepared members. Changing Family does not change their own multipliers, shapes, depth or ranges. A section can override a whole-stage Family; the aggregate selector then shows Mixed. Shuffle keeps those families and reshuffles their positions and phase offsets. A direct target Family edit replaces that target’s stage assignment. The performer prepares and pauses all native timelines.

## Shader address correction

Heart detected the four paused quaternion timelines on 4D Voronoi correctly, but its previous address sanitization removed `+`. It also removed parentheses from 16 Dimensional Julia (Sedenion). Resolume retains those characters. `osc_key` now preserves them for discovered source/effect/parameter addresses. Native probes on both Quat W controls confirmed delivery at the corrected paths and restored the starting phase (float32 precision). A second restored Julia probe used the actual bridge bundle format successfully. No native ranges or programs were changed.

## Stale-frame output stall

A separate live discrepancy exposed a worker stall during clip changes. After an identity check rejected an unavailable phase destination, later queued frames for that blocked version could remain pending forever. The already-set wake event let the worker spin without yielding, starving commands and eventually blocking Heart’s output pipe. Heart’s displayed drive flags could remain on while native output was stationary.

The worker now drops blocked phase frames, removes stale pending entries and yields when rescheduling remaining work. The old behavior was reproduced against a mock native server; it timed out reading a subsequent command. The corrected test processes that command and delivers again after a fresh binding. All 31 output/recovery checks passed after this fix.

## Verification

- 68 affected backend checks passed, including one-beat easing, changing speed during a transition, independent multiplicative scopes, 0.025 precision, native membership, stale commands, stage Family distribution, locks and phase output.
- Both mocked surface suites passed at compact and wide sizes. They exercise source presets, stage Family and Mult/custom entry, all four BPM commands, independent displayed values, and disabled states.
- Installed in standalone Heart. Reload restored exposed ratio, multiplier, phase offset and shape settings for 31 active prepared parameters. All 16 stage layer drives remain detected. The actual standalone view shows the new enabled controls.
- The first read-only sample found stationary output and led to the worker fix above. After the corrected worker was installed, an existing Rings level moved by 0.02393 within its saved range, its exact paused timeline program was unchanged, and 14,280 native updates were delivered during the check. Tick p95 was 9.74 ms and work p95 0.32 ms. Evidence: `checks/motion-multipliers/after-worker-fix.json`.
- Automatic approval review blocked a live Global ½× click, citing its all-motion scope and lack of a paired restore in that action. Live Mult/Family/BPM changes were therefore not exercised; musical feel and performer acceptance remain open. Mocked interaction and backend timing are verified.

Evidence: `checks/motion-multipliers/`. No native timeline pausing, composition saving, geometry edits or MIDI remapping was performed.
