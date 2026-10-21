Phase 1 · core playing workflow

# Heart · first working batch

---

**Overall plan:** [SHOW-CHECKLIST.md](SHOW-CHECKLIST.md). The full feature set remains required; this file defines the next batch only.

- [ ] **Layers:** current clip, previous/next/random/eject, level/visibility and focused clip browsing.
- [ ] **Effects:** a compact scoped rack with bypass, opacity, IN/OUT, momentary and linked actions.
- [ ] **Detail:** A/B follow/pin, parameter settings and enough target/master/hidden state to understand the result.
- [ ] **Operation:** stable mouse and keyboard controls connected to the existing backend actions. Repair necessary backend gaps in the same batch.

**Finish line:** choose content, mix layers and play effects entirely inside Heart while unrelated motion continues.

**Implementation rule:** the UI invokes shared parameter/action commands. Future hardware mappings use the same commands and do not introduce separate instrument behavior.

**Next:** instrument workflows → recall/recovery → complete mouse/keyboard verification → hardware mapping and final play.

**Hardware:** whole Grid and PS4 integration comes last. No controller connection, layout creation or Grab setup is needed to complete this batch.
