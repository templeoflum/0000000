# Delay source/effect ownership — bounded read-only risk check

## Conclusion

**The inspected stable state does not have duplicate source/effect motion writers for Delay.** The actual deduplication is in `EffectMotion.refresh()`, not in `index_slot_owners()`, `claim_slot()` or `current_controller()`. Shared native parameter IDs exposed by two UI panes do not alone establish competing writes or explain the reported jitter.

## Exact evidence

1. `heart.Clip` explicitly discovers sourceparams **plus SP effect params**. For SP Delay Chain, the source controller's Taps/Span/Glide/R/G/B are intentionally aliases for parameters of the clip's native SPDelayChain effect.
2. `EffectMotion.refresh()` builds `source_ids={sl.ids.get('') for c in CLIPS.values() for sl in c.slots}` and skips a numeric effect parameter when `p.get('id') in source_ids`. It removes old effect slots excluded from the new list, discards their queued values and refreshes the effect instance when its slot list changes.
3. Saved `sp/show-day/integration/rehearsal/route-final-heart.json` corroborates that exclusion: Delay source has six slots Taps/Span/Glide/R/G/B, all owner=heart; the unique `layer/delay~1/clip/figure~1/effect/SPDelayChain~1` has `motion.slots=[]`. There are no effect-side Smart Param slots to compete in that saved state.
4. `play_all()` enumerates both current source and effect controllers, but acts only on each controller's `slots`. Thus stable Open all can open the six source slots; the duplicate effect parameter listing contributes no numeric motion slots. It also skips parked effect controllers. Source slots are not gated by that effect-controller skip, so source-side Delay drives may still be active while native effect opacity is parked; this is a distinct behavior, not duplicate ownership.
5. Current effect pane can still show native manual numeric controls because `workspace.buildParameters()` falls back over `c.params` when no widget exists. `heart.manual_parameter()` searches motion controllers for matching IDs, claims the matching slot, sets drive=false and updates its manual pose; the normal source writer then follows that manual value. Seeing knobs on both panes is not proof the effect has independent drive slots.
6. Normal scan ordering calls `publish_discovered_clips(live)` before later `discover_fx(comp,comp_started)`; the latter refreshes effect motion against the published source slots.

## What the named ownership helpers do and do not guarantee

- `index_slot_owners()` is a dict comprehension keyed by native ID, across sources then effects. **If duplicates did exist**, the last slot would overwrite the earlier entry; it does not reject, merge or remove duplicate slots.
- `ownership_allows_write(pid)` checks the indexed slot's Heart ownership and claim-inflight state. It does not identify which controller produced a queued value.
- `claim_slot(sl)` locks/claims that particular Slot and deletes the native phase source. It does not arbitrate another Slot with the same native ID.
- `current_controller(c)` checks controller object membership in CLIPS/FX, not unique parameter ownership. Both controllers could be current if duplicate slots were constructed.
- `_step_motion()` gates output on per-slot ownership/current controller; the latest-value queue coalesces by parameter ID. Coalescing is last-value delivery, not duplicate-controller arbitration.

Therefore these helpers alone do **not** establish a universal single-writer invariant. Correct stable behavior relies on the source-ID exclusion in effect refresh. Publishing changed source controllers and refreshing effects are not one combined atomic operation in the shown scan path; this read-only review does not prove every transient discovery/replacement interleaving is duplicate-free. No such transient was captured in the supplied evidence, and no live race was reproduced here.

## Root decision

No duplicate-writer patch is justified by the saved Delay state. Keep navigation scopes honest and avoid presenting a manual effect alias as a second independently driven instrument. If jitter continues, capture simultaneous source slots, effect motion slots and the current native parameter IDs during the actual event; a concrete overlap in active slots is the missing evidence. UI display duplication, engine-loop FPS or shared params dictionaries are insufficient. Investigating that transient invariant can be bounded later; this review performed no live calls, execution tests, rendering or shared edits.
