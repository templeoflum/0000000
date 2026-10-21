# Stage frame: Treehouse leaves6 Wire proof of concept

2026-09-10. Prototype is built in the currently open Wire patch, **Heart Treehouse Leaves6 POC**. Saved with explicit user approval to `Heart Treehouse Leaves6 POC/Heart Treehouse Leaves6 POC.wire`; file existence and nonzero size verified.

## Built

- All 107 original leaves6 PNG variants referenced directly from work/Visuals/infra; every file exists and is 1920 x 1440.
- Native image texture bank, random selection with previous/current index buffer, native Luma Key I mixer (numeric mode 25), and 4.920654-second transition.
- Images fit the 1920 x 1080 patch without stretching; resizing follows patch resolution.
- Original section mask, interpreted as inverse alpha (black opaque exterior, transparent interior).
- Section Opacity, Shuffle Now, Auto Shuffle, Transition Seconds, Shuffle Rate (Hz) dashboard controls. Default rate 1/6 Hz.
- No feedback loop, old videos, Arena wrapper installation, or changes to the running Arena composition.

## Checked

- All 107 image resource assignments and bank connections succeeded.
- Live native output shows texture variations changing inside the three small leaves6 regions with transparent surroundings.
- Section Opacity = 0 produces a fully transparent frame; 1 restores output.
- Previous/current indices were corrected using Buffer -> Split and verified as distinct values matching the buffer (15, 87), rather than returning to variant zero.
- Auto Shuffle on/off is connected through On Change to the metronome.

## Still to verify before expanding

- Direct Arena/Wire visual parity, including the original Mask resize semantics and opacity automation. The saved layer's opacity animation has NOT been recreated; the prototype exposes section level manually.
- Manual Shuffle Now button is wired but native trigger testing via the MCP setter is inconclusive (reports null unchanged). Test it in Wire's dashboard.
- Rapid manual retriggers or a shuffle period shorter than transition time can interrupt transitions. No interruption smoothing or trigger guard yet.
- Multi-section memory cost: this implementation preloads textures. It is not a demonstrated scalable memory solution for both full stages.
- Reopen verification remains; saving and file existence are verified. Inactive exploratory nodes remain disconnected; they can be cleaned up later.

The complete source layer XML and dimension audit are in source-audit.json. leaves6-bank.json preserves original slot order and paths. Original compositions and images are untouched.
