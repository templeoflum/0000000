# Delay color controls: missing instances versus hidden targets

Read-only audit of `sp/show-day/integration/rehearsal/departure-composition.json`, `route-final-heart.json`, current `workspace.js`, preserved `sp/design/heart-performance-plan/baseline/feedback machine_16x9_1080p.avc`, and the executed merge design in `sp/qa/merge_feedback_into_soup.py`. These are saved native snapshots, not a fresh live query; root must rediscover before changes.

## Finding

**ColourLoop and native DelayRGB exist, but neither is a Delay-layer effect in the inspected current composition.** Selecting Delay source exposes a third implementation's R/G/B controls. The UI's independent source/effect sides can therefore show apparently missing controls even though global/Sculpt instances are available.

| Scope | Native stack / controls | Classification |
|---|---|---|
| Composition | Transform → Stroke Volt → Pixel Melt → HueRotate → **ColourLoop** → LUT Corrupt → Twitch → StrokeDiffuse → Strobe | ColourLoop is present globally. Hidden from a Selected-layer Delay rack, not deleted. |
| Sculpt layer | Transform → InvertRGB → HueRotate → InvertRGB → **DelayRGB** → AutoMask | Native DelayRGB is present here, with Opacity/R delay/G delay/B delay. Hidden from a Delay-only rack. |
| Delay layer | Transform → InvertRGB → AutoMask | Native ColourLoop and DelayRGB are genuinely absent **at this scope**. |
| Delay clip figure / field | Transform → **SPDelayChain** | R/G/B are this graph's 0–16-frame offsets, not native DelayRGB. Source-side Heart slots are Taps, Span, Glide, R, G, B. |

“Color Loop” interpreted here as native **ColourLoop**. The older SPLoopColor is a separate shader/relationship instrument on other clips; it is not an alias for this native effect.

## Why the workspace is confusing

The saved workspace has A=`follow` (selected source), B=`follow-effect`, rack=`composition`, and selectedEffect pointing at Figure LUT. Selecting Delay does not force B to Delay's effect. `openEffect()` changes selectedEffect; `resolve()` follows each side's independent source/effect reference. Rack filtering controls visible rows independently.

`delayEffect()` intentionally exposes only SP Delay Chain's three events beside a Delay source: Shuffle taps / Reset taps / Golden taps. It does not expose native ColourLoop or Sculpt DelayRGB beside that source. Source-side R/G/B slots come from SPDelayChain; the effect-target dropdown separately lists all discovered native effects and their scopes.

Exact existing target keys (rediscover current instances):
- `composition/effect/ColourLoop~1`
- `layer/sculpt~1/effect/DelayRGB~1`
- `layer/delay~1/clip/figure~1/effect/SPDelayChain~1`

## Preserved original order and settings

Feedback Machine original:
- Composition: Transform → Stroke Volt → Pixel Melt → HueRotate → **LUT Corrupt → ColourLoop** → Twitch → StrokeDiffuse → Strobe.
- Original color layer (XML index1): Transform → InvertRGB → **DelayRGB → AutoMask**.
- Original motion layer (index2): Transform → InvertRGB → AutoMask; no ColourLoop/DelayRGB.

`merge_feedback_into_soup.py` explicitly maps original motion to current Delay, and concatenates original fill then color onto Sculpt. The present Delay omission is consistent with that mapping, not proof a copy was accidentally dropped. Original ColourLoop was composition-wide, downstream of the layer stacks. There is **no preserved original Delay-local combined ColourLoop/DelayRGB stack** to restore verbatim.

ColourLoop original inner parameter values, still matching the saved current native values:

| Parameter | Original value |
|---|---:|
| Factor | 0.41950956038903875 |
| Offset | 0.18839808653904605 |
| Red offset | 0.8130941496555285 |
| Green offset | 0.1525905935630703 |
| Blue offset | 0.014859987319111534 |

Original stored opacity=.6310190881808541 and bypass=true; current saved opacity0. Do not restore original opacity automatically or replay its animation timelines. Current Black & White=false is a later native value, absent from this original sparse XML.

Original layer DelayRGB serializes **no inner parameter values**; its native defaults are omitted. Therefore R0/G.15/B.30 cannot be claimed as explicit original layer settings. They are the current restored/verified working native pose in departure-composition.json and root's RGB rehearsal. Keep their provenance distinct. Original DelayRGB type identifier is A152; root must resolve a fresh native instance.

One observed order difference: current composition has **ColourLoop before LUT**, while the original has **LUT before ColourLoop**. Report this difference, but do not silently reverse it: it may reflect subsequent user work, and it is unrelated to controls being hidden.

## Precise minimal proposal

1. **Restore access first without changing processing:** show/select the existing global ColourLoop and Sculpt DelayRGB as explicitly scoped effect targets. Keep Delay source controls labeled as SP Delay Chain; identify its R/G/B as frame offsets. Pin A/B explicitly to the desired effect keys when controlling these together. If the user wants Delay source alongside a color effect, keep one side on Delay source and explicitly select the other effect on the other side. No native insertion or settings reset is needed for this access path.
2. **If root confirms the intended new scope is Delay-only native RGB:** the smallest source-evidenced addition is a fresh DelayRGB instance between Delay's InvertRGB and AutoMask, reproducing the original color subchain's relative order. Preserve existing SPDelayChain and all old instances. Stage at amount0/bypassed; use current tested R0/G.15/B.30 only as a known working starting pose, not as original XML values. This is a new application of the original subchain to Delay, not restoration of something previously present there.
3. **Do not guess a combined Delay-local ColourLoop order.** The original evidence places ColourLoop globally after LUT, not next to layer DelayRGB. Exposing its existing global target is the only no-guess restoration for that control. Moving/copying it into Delay changes processing scope/order and needs an explicit root design decision informed by the user's intended behavior; this audit supplies no purported original local order.

Root should distinguish “make existing controls visible together” from “apply both processors only to the Delay layer.” The former is already supported by current targets; the latter adds processing. No shared/UI/live edits made in this audit.

## Exact navigation-only implementation proposal for UI owner

No copying, insertion, removal or reorder. Blackout/UI worker owns implementation; this report makes no shared changes.

**Delay source pane:** add a short note “Routed input · Delay” and a button **Delay controls**. It selects the existing active clip SP Delay Chain in Parameters B. Place existing Shuffle taps / Reset taps / Golden taps controls only on the effect pane; this avoids duplicate action strips that imply source and processor are the same target. Retain any actually discovered source-side numeric slots; the saved route-final-heart snapshot contains Taps/Span/Glide/R/G/B on the source as well, so do not state that numbers can never appear there. The navigation should unambiguously identify the full native effect control target regardless of that discovery detail.

**Related shortcuts:** show **RGB delay · Sculpt** and **ColourLoop · Composition**, opening those existing targets in B. They should not be labeled Delay-layer controls. Their scope labels must remain visible after selection. Keep A's source selection and rack scope unchanged; do not trigger any native command.

**B assignment:** a successful click sets `cfg.b={kind:'effect',key:live.key}`, then uses the existing `openEffect(live)` path to set selectedEffect, persist and repaint both parameter panes/rack. `openEffect` alone is insufficient when B is pinned to another target. Respect its existing pointer-lock guard before changing cfg.b. This is an explicit user navigation action, so replacing the prior B pin is intentional; do not silently repin B on every render.

**Current uniqueness and names (saved route-final-heart.json):**

| Shortcut | Matches in saved active Heart inventory | Canonical native key suffix | Native / Heart display names |
|---|---:|---|---|
| Delay controls | 1 | `/effect/SPDelayChain~1` | `SPDelayChain` / `SP Delay Chain` |
| RGB delay · Sculpt | 1 | `/effect/DelayRGB~1` | `DelayRGB` / `Delay RGB` |
| ColourLoop · Composition | 1 | `/effect/ColourLoop~1` | `ColourLoop` / `ColourLoop` |

For Delay controls, require exactly one `scope==='K'` SPDelayChain on the source's layer **and** that source is still the active unique clip for that layer. Require the established three ParamEvent names if reusing `delayEffect()`. Current discovery enumerates active clip effects; don't search inactive copies or take the first matching instance. If the source is a pinned stale/disconnected clip, disable its link. A native basename match from the final key segment is more robust than spacing in display names, but must preserve exact scope and uniqueness.

For the related controls require exactly one `scope==='L'`, current layer name `sculpt`, canonical basename `DelayRGB`; and exactly one `scope==='C'`, canonical basename `ColourLoop`. Exclude clip-specific DelayRGB instances and group scopes. Do not depend on L2/L4 numeric addresses, a `~1` occurrence, or string includes alone; enumerate matches and require length1. Two instances with different occurrences are ambiguous and must not silently choose first. Labels are observed variants, not fuzzy aliases: do not substitute SPLoopColor, HueRotate, SPDelayPerformance or SPDelayChain R/G/B for the requested native effects.

Capture each link's source reference and target `{key,instance}` when built. On click recheck `current(source)`, `current(target)`, connection state, and the scoped uniqueness predicate; if the target was replaced, require fresh UI discovery rather than using its captured ID. Include target key/instance/availability in the pane signature or otherwise refresh shortcuts when effect discovery changes. On missing/ambiguous target, disable with a short reason (“Unavailable” / “Multiple matches”) instead of hiding the scope or opening a different processor.

**Minimum tests:** B changes to exact target while A/rack stay unchanged; each known display-name variation resolves by canonical native basename; duplicate/missing/wrong-scope target disabled; stale source or replaced target rejects old callback; disconnected/pointer-locked action does nothing; source pattern strip not duplicated; navigation sends no effect activation or parameter write. Reuse existing DOM harness, no live test required for the bounded navigation change.
