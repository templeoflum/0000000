# Retire internal RGB — build complete

Two fresh local artifacts prepared. No installed sources changed, no live calls, no shared engine/UI/metadata edits.

| Variant | Patch | Fresh identifier |
|---|---|---|
| Full history resolution | `sp/patches/Heart Delay Line/Heart Delay Line.wire` | `f19e6915-d501-4224-be36-a1706741a320` |
| Half-width/half-height history | `sp/patches/Heart Delay Performance/Heart Delay Performance.wire` | `ffc8dfb6-e73c-4523-a5f1-475bd1d1b7d4` |

Both remove exactly nodes712–740 (16 RGB frame delays, R/G/B inputs and channel-selection/reassembly) and all their incident connections. Actual typed existing port evidence establishes mixer386 `output` as texture2d; new edge is386.output→2.input. Input-order roots for R/G/B removed. Span floor741 retained. Performance downsampling node742 and edges0.output→742.input0→1.input0 retained verbatim as parsed JSON, including relative resolution[.5,.5].

Controls, in original exposed order: Texture In; Taps; Span; ⚡ Shuffle; ⌂ Home; Glide; φ. Numeric defaults/ranges unchanged: Taps3 (1–6), Span8 (0–16), Glide1 (.1–8). Events remain events. Native Opacity is host-provided and not a removed graph input. Home still selects tap pattern, not buffer clear.

## Verification actually run

`PYTHONDONTWRITEBYTECODE=1 python3 sp/show-day/effects/retire-rgb/build.py`

Passed for both serialized output artifacts:
- Fresh distinct UUIDv4 identifiers, different from both originals.
- Exactly29 nodes removed, no retained node changed.
- Exactly retained connections in original order plus one direct output edge.
- Input-order, graph/UI references and nextNodeId valid; no dangling node references.
- Existing seven multi-input event/control destinations retained exactly; no new conflicts and output has one incoming connection.
- Acyclic topology; all480 remaining Delay nodes reach output; longest path480 delay stages.
- Output ancestor set exactly the original ancestor set minus removed nodes.
- Exhaustive whole-document comparison permits only nodes/connections/input roots and three metadata fields (displayName, identifier, description) to differ. All other JSON fields equal originals, including UI, nextNodeId, version, resolution, settings and retained nodes. JSON whitespace is reserialized; original byte copies retained separately.
- Performance half-resolution node/settings/connections explicitly checked.

An initial verification rejected all multi-input destinations; inspection showed existing event merge inputs in the originals. Verification now requires their exact preservation, rather than incorrectly treating valid existing connections as a new defect.

## Hashes and original evidence

| File | SHA-256 |
|---|---|
| Installed SP Delay Chain / identical original backup | `6d0780c8315e70b62442be812a6a2b429ca497a088c1c7dd819256da6a6de995` |
| Heart Delay Line | `7bbdcc85f8906877b602fe6bfe0c416275c825ebf695145bc5f49e607e1162ec` |
| Installed SP Delay Performance / identical original backup | `b1913bd6e26918e94c8fff3b4dd7cc93eecf58a59903d8da1ce78df41c1f393d` |
| Heart Delay Performance | `b635fcdd95f80958c92d197add33c6c003a947f8b362a1489705ac0087538589` |

Evidence files here: `build.py`, `verification.json`, `SP Delay Chain.original.wire`, `SP Delay Performance.original.wire`, and this STATUS.md. Build is hash-pinned to inspected originals and keeps stable fresh identities on rerun. It aborts if installed original content differs.

Remaining root steps: metadata/UI recognition for both new identifiers, installation, fresh native discovery, active-deck-only migration and live output/controls check. Originals remain available for old compositions. No claim of native compile/render success from offline graph verification.

## USER PAUSED — comparison only

Retirement paused after staged artifacts. Root confirms neither installation nor replacement occurred. Do not migrate on the strength of this build report.

Exact original RGB semantics: mixer386 first composes taps; its result feeds one16-frame history. R/G/B controls each round to an integer0–16 and select a texture from that shared history (0=current mixer). Unpack R731.output0 feeds output red; G735.output1 green; B739.output2 blue; **B739.output3 feeds alpha**. Thus output at pixel x is (M[t-r].r, M[t-g].g, M[t-b].b, M[t-b].a), where r/g/b are rounded frame settings and M is composed tap output. It acts once after tap composition, not independently on each tap. There is no feedback edge into the480-frame tape.

The separate native DelayRGB is a downstream layer-stack processor with its own opacity/bypass/blend context; it acts after clip-level delay processing rather than inside this graph. Its alpha handling, precise delay-unit mapping and interpolation are not established. Therefore native replacement is not proven equivalent, especially alpha-following-B behavior. Internal R/G/B live inside SPDelayChain's opacity blend; native DelayRGB can be independently faded/bypassed. External composition feedback could capture either processed output depending on routing; neither placement demonstrates a change to this graph's feed-forward history itself.
