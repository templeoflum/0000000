# Instrument readiness — offline inventory, September 7, 2026

This is a deterministic inspection of saved files, not a new renderer test. The input snapshot names the composition **Feedback shaping**. It contains **37 populated clips across 8 layers**: **36 performance/routing entries and one diagnostic**. SPEC.md still says 36; this snapshot now contains 37. No clips, bank settings, engine configuration or live state were changed.

Snapshot: `baseline/routing-current.json`, SHA-256 `dd4613053cafe1537edb4509517b74b740403944f0d1b0f296fc6bdee3ecfd8b`. Populated means a nonempty `clip.name.value`, enumerating every layer/column in snapshot order. The snapshot is not a promise that the running composition has remained unchanged. Column addresses and names are bank references; native numeric parameter IDs are intentionally excluded because they change on reload. Durable bindings additionally require source/effect identity and parameter name/occurrence; addresses alone are not global instrument IDs.

## Home and trigger interpretation

Home precedence follows `heart.py:go_home`: an explicitly saved `sweet_home` wins; otherwise SPHeartFeedback uses Turn, a matching atom/name uses sweetspots.json, and other supported instruments get the conservative familiar-name fallback. A stored profile is **not proof of a good rendered Home**. Counts below are profile binding counts, not verified active-drive counts; bindings can disappear as shader parameters change. Existing legacy auto-captured Home entries without `sweet_home` do not count as curated Homes. Current saved Homes for 4d and hybrid are explicitly marked saved, but their artistic quality and migration behavior have not been tested in this audit.

The extractor applies Heart's legacy Drive-before-atom discovery precedence and the engine's explicit SPHeartFeedback registration (which need not appear in atoms.json). Home totals: **14 factory, 17 fallback, 4 none, 2 saved**. Instrument families: **25 Heart atom instrument, 3 static routing/source, 8 legacy relationship instrument, 1 diagnostic**.

Trigger inventory includes clip source and effect parameters typed ParamTrigger/ParamEvent, excluding normal clip launch/selection transport. Presence in the snapshot proves exposure only. Heart's Shuffle action is a relationship mutation, not a history reset; native Shuffle events are not evidence of a universal event-button UI. Hold, layer clear, Motion Home and feedback buffer reset remain distinct. Only SPHeartFeedback currently has a dedicated `feedback_reset` adapter; its precise native single-frame buffer readback remains unverified.

## Performance and routing bank

| Address | Layer | Clip | Family / source or effect identity | Home source / evidence level | Trigger / reset | Evidence |
|---|---|---|---|---|---|---|
| L1C1 | feedback | map | Heart atom instrument / SPChainMap | Factory profile (`SPChainMap`, 6 bindings); per-clip artistic acceptance unknown | No source/effect Trigger or Event exposed; no reset verified | E1 only |
| L1C2 | feedback | texture | Heart atom instrument / SPStudyTexture | Unrefined fallback; familiar motion names only, may have no eligible controls | No source/effect Trigger or Event exposed; no reset verified | E1 only |
| L1C3 | feedback | fold | Heart atom instrument / SPStudyFold | Unrefined fallback; familiar motion names only, may have no eligible controls | No source/effect Trigger or Event exposed; no reset verified | E1 only |
| L1C4 | feedback | level | Heart atom instrument / SPChainLevel | Unrefined fallback; familiar motion names only, may have no eligible controls | No source/effect Trigger or Event exposed; no reset verified | E1 only |
| L1C5 | feedback | pass | static routing/source / Video Router | No discovered Heart motion slots; no motion Home | No source/effect Trigger or Event exposed; no reset verified | E1 only |
| L1C6 | feedback | heart feedback | Heart atom instrument / SPHeartFeedback | Factory Turn (`feedback.py`, 3 bindings); live behaviors reviewed | Reset trails event; dedicated Heart adapter; native delivery + offscreen clear verified | E1; E3 |
| L1C9 | feedback | Flow | legacy relationship instrument / SPLoopFlow, SPLoopColor | Unrefined fallback; familiar motion names only, may have no eligible controls | 14 native Shuffle events; no history-reset contract | E1 only |
| L2C1 | sculpt | level | Heart atom instrument / SPStudyLevel | Factory profile (`SPStudyLevel`, 7 bindings); per-clip artistic acceptance unknown | No source/effect Trigger or Event exposed; no reset verified | E1; E2 |
| L2C2 | sculpt | pass | static routing/source / Video Router | No discovered Heart motion slots; no motion Home | No source/effect Trigger or Event exposed; no reset verified | E1 only |
| L2C3 | sculpt | color | Heart atom instrument / SPStudyColor | Unrefined fallback; familiar motion names only, may have no eligible controls | No source/effect Trigger or Event exposed; no reset verified | E1 only |
| L2C4 | sculpt | mixer | Heart atom instrument / SPStudyMixer | Unrefined fallback; familiar motion names only, may have no eligible controls | No source/effect Trigger or Event exposed; no reset verified | E1 only |
| L2C8 | sculpt | Shape | legacy relationship instrument / SPLoopShape | Unrefined fallback; familiar motion names only, may have no eligible controls | 7 native Shuffle events; no history-reset contract | E1 only |
| L3C1 | field | ground | Heart atom instrument / SP Atom Ground | Factory profile (`SP Atom Ground`, 18 bindings); per-clip artistic acceptance unknown | No source/effect Trigger or Event exposed; no reset verified | E1 only |
| L3C2 | field | room | Heart atom instrument / SP Atom Room | Factory profile (`SP Atom Room`, 24 bindings); per-clip artistic acceptance unknown | No source/effect Trigger or Event exposed; no reset verified | E1 only |
| L3C3 | field | void | Heart atom instrument / SP Atom Void | Factory profile (`SP Atom Void`, 14 bindings); per-clip artistic acceptance unknown | No source/effect Trigger or Event exposed; no reset verified | E1; E2 |
| L3C8 | field | SP Field | legacy relationship instrument / SP Field | Unrefined fallback; familiar motion names only, may have no eligible controls | 7 native Shuffle events; no history-reset contract | E1 only |
| L4C1 | delay | figure | Heart atom instrument / SPDelayChain | Factory profile (`SPDelayChain`, 5 bindings); per-clip artistic acceptance unknown | ⚡ Shuffle; ⌂ Home; φ native events; no verified history-reset contract | E1; E2 |
| L4C2 | delay | field | Heart atom instrument / SPDelayChain | Factory profile (`SPDelayChain`, 5 bindings); per-clip artistic acceptance unknown | ⚡ Shuffle; ⌂ Home; φ native events; no verified history-reset contract | E1 only |
| L4C8 | delay | Color | static routing/source / Feedback | No discovered Heart motion slots; no motion Home | No source/effect Trigger or Event exposed; no reset verified | E1 only |
| L4C12 | delay | figure · light delay | Heart atom instrument / SPDelayPerformance | Factory profile (`SPDelayPerformance`, 5 bindings); per-clip artistic acceptance unknown | ⚡ Shuffle; ⌂ Home; φ native events; no verified history-reset contract | E1 only |
| L5C1 | figure | 1d | Heart atom instrument / SPAtomLine | Unrefined fallback; familiar motion names only, may have no eligible controls | No source/effect Trigger or Event exposed; no reset verified | E1 only |
| L5C2 | figure | 2d | Heart atom instrument / SP Atom Figure 2D | Unrefined fallback; familiar motion names only, may have no eligible controls | No source/effect Trigger or Event exposed; no reset verified | E1 only |
| L5C3 | figure | 3d | Heart atom instrument / SP Atom Solid | Factory profile (`SP Atom Solid`, 18 bindings); per-clip artistic acceptance unknown | No source/effect Trigger or Event exposed; no reset verified | E1 only |
| L5C4 | figure | 4d | Heart atom instrument / SP Atom 4D | Saved Home (`home.json`, 27 stored slots); visual validation unknown | No source/effect Trigger or Event exposed; no reset verified | E1 only |
| L5C5 | figure | shell | Heart atom instrument / SP Atom 4D Field | Factory profile (`SP Atom 4D Field`, 30 bindings); per-clip artistic acceptance unknown | No source/effect Trigger or Event exposed; no reset verified | E1; E2 |
| L5C6 | figure | hybrid | Heart atom instrument / SP Atom Hybrid | Saved Home (`home.json`, 32 stored slots); visual validation unknown | No source/effect Trigger or Event exposed; no reset verified | E1 only |
| L5C8 | figure | Figure 3D SP | legacy relationship instrument / SP Figure 3D | Unrefined fallback; familiar motion names only, may have no eligible controls | 7 native Shuffle events; no history-reset contract | E1 only |
| L5C9 | figure | Figure 2D SP | legacy relationship instrument / SP Figure | Unrefined fallback; familiar motion names only, may have no eligible controls | 7 native Shuffle events; no history-reset contract | E1 only |
| L6C1 | glyph | glyph | Heart atom instrument / SP Atom Glyph | Factory profile (`SP Atom Glyph`, 11 bindings); per-clip artistic acceptance unknown | No source/effect Trigger or Event exposed; no reset verified | E1 only |
| L6C2 | glyph | script | Heart atom instrument / SP Atom Script | Unrefined fallback; familiar motion names only, may have no eligible controls | No source/effect Trigger or Event exposed; no reset verified | E1 only |
| L6C8 | glyph | SP Glyphmass | legacy relationship instrument / SP Glyphmass | Unrefined fallback; familiar motion names only, may have no eligible controls | 7 native Shuffle events; no history-reset contract | E1 only |
| L7C1 | texture | dither | Heart atom instrument / SPAtomDither | Factory profile (`SPAtomDither`, 8 bindings); per-clip artistic acceptance unknown | No source/effect Trigger or Event exposed; no reset verified | E1; E2 |
| L7C2 | texture | texture | Heart atom instrument / SP Atom Texture | Unrefined fallback; familiar motion names only, may have no eligible controls | No source/effect Trigger or Event exposed; no reset verified | E1 only |
| L7C8 | texture | SP Scan | legacy relationship instrument / SP Scan | Unrefined fallback; familiar motion names only, may have no eligible controls | 7 native Shuffle events; no history-reset contract | E1 only |
| L8C1 | grain | grain | Heart atom instrument / SP Atom Grain | Factory profile (`SP Atom Grain`, 4 bindings); per-clip artistic acceptance unknown | No source/effect Trigger or Event exposed; no reset verified | E1 only |
| L8C8 | grain | SP Grain | legacy relationship instrument / SP Grain | Unrefined fallback; familiar motion names only, may have no eligible controls | 7 native Shuffle events; no history-reset contract | E1 only |

## Diagnostic, kept separate from performance sources

| Address | Layer | Clip | Family / source | Home | Trigger / reset | Evidence |
|---|---|---|---|---|---|---|
| L8C9 | grain | SP State Test | diagnostic / SP State Test | No discovered Heart motion slots; no motion Home | No source/effect Trigger or Event exposed; no reset verified | E1 only |

SP State Test is retained exactly where it is. This report separates its validation role without hiding, removing or rewriting its bank entry. Pass-through/router clips may also be intentionally static; missing drives do not make them broken. L4C8 Color is reported as the snapshot exposes it (Feedback source, no discovered Heart motion controls), not assumed to be an active color instrument because of its label.

## Evidence and limits

- **E1 — inventory only:** `baseline/routing-current.json`, `sp/engine/{atoms,home,sweetspots}.json`, `heart.py` discovery/Home/reset code and `feedback.py`. This validates saved schema and implemented selection rules; it does not validate live rendering, installed dependency availability for inactive clips, route semantics or GPU cost.
- **E2 — selected operating setup:** `PROGRESS.md`, `feedback-instrument/repeated-recall-live.json`, and `dependency-live-checks.json` record restoring the six-instrument setup. This supports recall of level/void/delay-figure/shell/dither with heart feedback. It does not prove factory Home artistry for each or full library readiness. Some recalled layers have zero level or no active drives.
- **E3 — feedback-specific:** `feedback-instrument/behavior-live-checks.json`, output snapshots, `feedback-buffer-tests.json`, `ownership-live.json`, and `feedback-instrument/shaping-live-checks.json` record behavior review, offscreen persistent-buffer clear, native reset delivery, ownership and effect envelopes. Native RGB decay is not temporal DelayRGB equivalence. Output effects are downstream of shader history.
- `performance/README.md` holds short acquisition/system-GPU measurements. No per-clip cost is assigned in this matrix. Sources that share a family are not presumed to share cost or output quality. The ongoing sustained test is outside this frozen offline audit.
- `dependency-contract.md` describes scoped routing and dependency validation for recalled active instruments. It does not certify every inactive bank clip; each first-batch instrument needs its own fresh route/dependency check.
- Home storage is currently keyed by clip name. Names repeat across layers (`level`, `texture`, `pass`); a future manually saved Home could collide across unrelated instruments. Stable parameter identity checks help avoid applying invalid controls but do not make a shared name a unique Home namespace. Record and test this before expanding saved Homes across the bank.

## Recommended first source batch after phases 0–4

Refine five existing sources before importing a larger set: **L3C1 ground, L3C2 room, L5C3 3d, L5C2 2d, L6C2 script**. Ground/room/3d already have factory profiles and address previously reported Home concerns; 2d/script still rely on fallback, so they exercise migration to a real instrument contract. This is an ordering recommendation based on control gaps and user priorities, not a performance ranking.

For each, freeze source identity/version and route dependencies; map actual exposed parameter roles, ranges and cyclic behavior; choose a bounded visibly moving Home plus deliberate manual controls; preserve unknown controls undriven; test Home/hold/recall and ID replacement; define reset only if the source owns persistent history; render meaningful extremes and measure isolated full-resolution cost. Accept or reject each independently. Retain legacy Figure 2D SP / Figure 3D SP as comparison instruments, and compare the lighter delay candidate separately before making it a default. Portal/Treehouse relationship integration follows the existing relationship documentation; this inventory does not substitute a guessed mapping.
