# Melt controls

Hold melt and Latch melt both address native MELT_LOCK. The existing event remains separate as Trigger melt; it is a one-shot native ParamEvent and is never treated as a held boolean.

Backend tracks temporary boolean holds per connection/parameter, restores the freshly read native baseline on final release, rejects nonboolean controls, clears on disconnect/release-all, ignores stale replacement releases, and lets a newer explicit edit supersede old holds. UI handles pointer, keyboard, cancellation, blur, pagehide, rack disposal and disconnected state; latch readback comes from native state.

227 Python checks and39 offline interface checks pass.10 native checks passed with effect opacity0: press/release, latch preservation, newer edit precedence and disconnect cleanup. Native Heart controls reloaded and Hold/Latch presence plus off-state verified. This validates controls, not Pixel Melt's unresolved earlier rendered snapshot timeout.
