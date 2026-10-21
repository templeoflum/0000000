# Heart · surface language

Reference collection · 11 September 2026

Status: parked. The user's latest priority is backend and controller functionality first. This collection and its proposed visual specimen are optional polish after the functional build; they do not gate backend work.

Heart is a Boustrophedon precision instrument for performing generative instruments. Its construction, visual hierarchy and response must express the same care. This collection grounds F0 in the user's existing design work and a small set of manufacturer sources. It is a design brief, not evidence that the new surface is implemented or show-ready.

[Open the reference board](reference-board.html).

## House sources

| Source | Study | Transfer to Heart |
|---|---|---|
| [Boustrophedon Rev E panel](/Users/donovan/work/met3or/lore/boustrophedon/ft1-pkg/panel/model-ft-1-panel-rev-e.html) | Metal, dark glass, control families, three-row maker mark | A coherent material hierarchy. Active controls and observed values have distinct forms. |
| [Board I](/Users/donovan/work/met3or/lore/boustrophedon/ft1-pkg/studies/ft-1-studies.html) | Selector legends, silkscreen, type metrics, zoning | Layout depends on the actual font and actual label lengths. Bundle any chosen typeface; verify fallback and offline rendering. |
| [Board II](/Users/donovan/work/met3or/lore/boustrophedon/ft1-pkg/studies/ft-1-studies-ii.html) | Tektronix rate scales; ARP signal-flow study | Keep the useful range and current value visible. Draw relationships selectively, at the point they clarify control. |
| [Board III](/Users/donovan/work/met3or/lore/boustrophedon/ft1-pkg/studies/ft-1-studies-iii.html) | Ink doctrine, true-scale detail, provenance | Color has a defined job; small details must survive at working size. Preserve the canonical mark exactly. |
| [Board V](/Users/donovan/work/met3or/lore/boustrophedon/ft1-pkg/studies/ft-1-studies-v.html) | Value hierarchy, eye path, crowded bottom rail | Give the primary gesture visual weight. Budget space for navigation and state from the start. |
| [Heart Monitor source](../../monitor/Heart.m) | Accepted aluminum fascia, inset readout, molded caps | Immediate family continuity. Reference image is the existing offline Resume specimen, not live output or a fresh performance measurement. |

The Boustrophedon source lives within the MET∃OR archive. Heart inherits the maker's instrument grammar; MET∃OR's release rules, letter geometry, serial story and mathematical palette do not become Heart application rules. The canonical f(t)–1 ink doctrine has specific PLOT/VOICE/hazard meanings. Heart must define its own truthful operational meanings before reusing those accents.

## External references

These are visual and interaction readings of primary sources, not claims that Heart meets a hardware manufacturing certification.

| Source | Specific reference | Heart application |
|---|---|---|
| [Nagra IV-S](https://www.nagraaudio.com/product/nagra-iv-s/) | Distinct control shapes, prominent selector, meter and scale placed at the action | Recognize continuous controls, modes, triggers and readouts through shape and placement. The large Rate/Intensity control earns its size. |
| [ARP 2600 M](https://www.korg.com/us/products/synthesizers/arp2600_m/) and [manual](https://www.korg.com/us/support/download/product/0/877/) | Repeated fader geometry, local labels and drawn signal relationships | Keep four-fader/eight-pad layouts spatially stable. Show actual target membership and routing; printed lines must describe real relationships. |
| [Tektronix 465/465B manual](https://www.tek.com/en/manual/465b-instruction-manual) | Reference family for calibrated ranges and grouped controls; already interpreted in Boustrophedon Board II | Test the large knob with a visible ratio scale and a fixed value readout. This collection uses the local Board II study; the manufacturer's 200 MB manual was not inspected in full. |
| [Braun color doctrine](https://www.braun-audio.com/en-KR/stories/design/braun-colour-choices/) | Neutral field, color reserved for information | Keep state colors scarce, stable and paired with a label or shape. |

The board displays Nagra and Korg photographs from their original manufacturer hosts, with attribution and source links. They require network access. The Boustrophedon and Heart images are local renders. House references remain available offline.

## Proposed construction rules

1. **Material hierarchy.** Warm aluminum structure, graphite working fields, dark readout wells. Raised or inset treatment indicates how a thing operates. One consistent light direction and restrained depth. Essential labels must remain readable without texture, shadow or glow.
2. **A small parts vocabulary.** Reuse the same fader, pad, momentary key, latched switch, selector, numeric readout and group boundary everywhere. Pressed, held, focused, disabled, unresolved and active states are deliberate specimens of those parts. A trigger and a latch cannot look identical while idle and differ only after a surprise.
3. **A measured grid.** Shared baselines, spacing increments, line weights and control travel. Gain density by alignment and removing redundant containers and prose. Reserve adequate hit areas and visible room around controls used together. Four faders and two rows of four pads must retain their physical map.
4. **Legends with useful precision.** Short fixed legends may use the house condensed face. Dynamic names use a legible system sans. Numbers use tabular figures and meaningful units/precision. Do not scale a hardware drawing down until its labels fit; redraw for the native viewport. Low-contrast engraving and overlapping legends in reference drawings are defects to improve.
5. **Operational color.** Prototype a neutral structure, one motion/acquisition accent, and a distinct exception/action accent. Scope and state must also be readable through text, marker shape or position. Color values and exact meanings remain provisional until the state specimens are reviewed.
6. **Truthful motion and state.** A grabbed control gives immediate local feedback; command, observed value and pending state remain distinguishable where the backend supports them. Navigation never moves a held destination. No ambient animation, whole-page rearrangement or decorative motion in the performance field.

Apply the [Legibility Constitution](/Users/donovan/work/skills/_extract/*/legibility-constitution/SKILL.md) and [Narrator Bleed](/Users/donovan/work/skills/_extract/*/narrator-bleed/SKILL.md). Metal stays silent: labels, units, maps and necessary state belong on the instrument. Explanatory prose belongs in the reference/inspection layer.

## Next design dependency

Build one actual-size working specimen before spreading the visual language through the application: four simultaneous level controls, eight pads in their alternate mode, the Rate/Intensity control, one FX IN/OUT pair, and a compact target/ownership readout. Use two interchangeable configurations, including a generic stage-opacity/content/feedback performance layout and a non-stage instrument layout.

Compare two material balances within that same geometry: aluminum-led and graphite-led. They test contrast and hierarchy without changing the control map. Judge through playing: destination recognition, simultaneous gestures, pickup, release, layout swap and recovery. PS4, trackpad and MIDI all refer to the same visible actions.

The specimen is ready to propagate when its longest realistic labels fit, fonts work offline, essential text and boundaries have measured contrast, control state is unambiguous without color, and expansions/reloads cannot move the playing map. Test it in the actual native window with the actual input devices. A rendered reference board alone does not meet those conditions.

## Collection record

- `assets/bic-panel.png` and `assets/bic-rate.png`: local renders of the unchanged canonical Rev E drawing.
- `assets/bic-legends.png`: local render of Board I's silkscreen study.
- `assets/bic-layout.png`: local render of Board V's eye-path study.
- `assets/heart-monitor.png`: existing offline Heart Monitor Resume specimen from this workspace.
- Manufacturer image URLs and page links are recorded in `reference-board.html`.
- `sources/model-ft-1-panel-rev-e.html`: an unchanged local copy of the canonical source drawing for reference-board access.

Source drawings, the native monitor and the performance surface were not edited for this collection.
