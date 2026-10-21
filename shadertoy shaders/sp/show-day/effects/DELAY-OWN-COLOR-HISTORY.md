# Delay's own color / RGB history — corrected scope

The user's requested instrument is **Delay itself**. The earlier proposal to link global ColourLoop and Sculpt DelayRGB was not an adequate restoration and is superseded. This audit does not treat the current stack as proof that the user's earlier Delay color behavior never existed.

## Confirmed: Delay had and still has its own RGB delay

The strongest historical evidence is `sp/audit/20260907-070411/delay-original-live.json`, a saved live **Delay clip named figure**, whose native stack is Transform → SPDelayChain. Its SPDelayChain parameters explicitly include:

| Parameter | September 7 saved native value |
|---|---:|
| Opacity | 1 |
| Taps | 6 |
| Span | 16 |
| Glide | 2.349920001065731 |
| R | 2 |
| G | 3 |
| B | 4 |

This is a self-contained RGB component of Delay, **not** Sculpt's native DelayRGB. The old R2/G3/B4 pose is concrete evidence root can use for a separately reviewed comparison; do not overwrite current settings blindly.

Historical `sp/retired/SP Delay Chain.pre-rgb.wire` has480 Delay nodes and no R/G/B inputs. Compared with that graph, the installed SP Delay Chain has the additional16 Delay nodes712–727, three exposed R/G/B inputs728/732/736, Round→Switch→Unpack branches, and Texture from Channels740. It also adds Span floor741 and changes other older nodes, so this is not claimed to be a pure RGB-only diff.

The installed route is: main delay/tap mixer386 →16-frame RGB history → per-channel switches → separate R/G/B channels → output. R/G/B choose0–16 whole-frame offsets. `sp/qa/build_delay_quality.py` derives SP Delay Performance by changing history texture resolution while preserving these timings and RGB controls. It does not remove color offsets.

## Current exposure problem: own animation controls can be on the source side

Saved `route-final-heart.json` contains Delay source slots **Taps/Span/Glide/R/G/B**. These include normal Heart drive/ratio/range controls. The corresponding SPDelayChain effect-motion slot list is empty because the engine excludes native IDs already represented by source slots; its effect pane falls back to manual numeric controls.

Consequently, steering the user exclusively into “Delay controls” on the effect side can actually hide the **Drive/relationship controls for Delay's own R/G/B animation**. The two panes refer to the same native IDs, but do not present identical controls. Restore/co-locate access to the existing source-owned R/G/B Smart Params instead of sending the user to another layer. Keep one owner per native ID. The available current six slots contain no additional dedicated Hue/Color Loop slot.

Varying these own RGB offsets over moving input produces changing color separation. It is a plausible component of remembered color cycling, but the files do not establish that this is the entirety of the user's intended Color Loop control. In particular, equal/static white input does not acquire palette hue from this stage alone.

## Earlier color-cycling code located

- `sp/make_loops.py:77` authors **SP Loop Color**; installed source at `~/Documents/Resolume Wire/Patches/SP Loop Color/Resource/SP Loop Color.fs`. Own controls are Hue (cyclic, default drive on), Invert, Sat, Bleed. The code derives a cosine palette from luminance and Hue, with `HU*4` giving four palette laps per hue-slot phase; Sat mixes chroma, Bleed samples neighbors, and alpha follows input luminance. This is actual color-cycling code, distinct from native ColourLoop and RGB time offsets.
- `sp/make_chain_studies.py:76` authors **SP Study Color**; installed matching shader exists. Controls include Hue Step in degrees per pass (default3, range−30…30), saturation multiplier and inversion applied inside persistent feedback accumulation. It is not a pure output hue knob or a substitute automatically equivalent to Loop Color.
- Earlier **SP Study Delay** installed graph has only Input, Delay, Transport Time, ISF and Texture Out. Its retired shader `sp/retired/SP Study Delay.fs` has192-frame atlases and one delay-value input; it returns stored RGBA without its own hue/palette operation. This specific located v10 is a time-delay implementation, not the missing combined color instrument.

These sources establish earlier local color-loop building blocks. **I have not located a saved Delay graph wiring Loop Color/Study Color into the Delay instrument**, so exact historical placement (before history, per-tap, or after mix) is unresolved. Do not invent that wiring or infer the user meant a different layer.

## Historical composition / backup coverage

Scanned workspace AVCs and local Resolume composition AVCs for layers named Delay and for SPStudyDelay/SPLoopColor effect references. `DELAY-HISTORICAL-STACKS.json` records exact matching Delay layer/clip stacks and file paths. Located Delay figure/field stacks are Transform→SPDelayChain; light-delay copy uses SPDelayPerformance. Located SPLoopColor composition references are on the saved Flow clip with SPLoopFlow; this locates a preserved component but does not disprove a missing earlier Delay configuration. Also inspected pre-rgb Wire, installed Study Delay and performance graphs, Wire patch backups and generation scripts. No matching earlier combined graph found in this bounded search.

## Minimal corrected root action

1. Remove cross-layer/global shortcuts from the Delay instrument as requested.
2. Make Delay's **own existing R/G/B Smart Params and their drives** accessible alongside Taps/Span/Glide; avoid relegating the user to manual-only effect aliases. Preserve their ownership and values. The saved native R2/G3/B4 pose proves own RGB existed before the current UI confusion.
3. Keep missing dedicated Color Loop recovery open. The native global ColourLoop and Sculpt DelayRGB are not acceptable substitutes. The located SP Loop Color shader is concrete recoverable source, but a faithful restoration of its Delay placement still needs the earlier graph/description of that placement. Root should distinguish this missing evidence from user intent, which is now explicit.

No shared/live edits, installations, rendering or speculative patch performed. This report supersedes the earlier cross-layer navigation recommendation, not the factual current-scope inventory.
