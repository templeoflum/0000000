# Generative Soup — Feedback Machine bank restored

Active composition and normal saved file: `~/Documents/Resolume Arena/Compositions/generative soup_16x9_1920x1080_60fps.avc`. A matching working copy is in this folder. Recovery: `Soup latest before merge.avc`.

Soup retains its eight layers, group structure, existing clip slots, levels and router references. All 245 source-bearing clips from both populated Feedback Machine decks are appended from column 15 onward in the current Soup deck; Heart navigation can reach them without switching decks. Imported names start with `FM ·`; bracketed coordinates identify their original deck/layer/column and distinguish repeated names.

| Reference role | Soup destination |
|---|---|
| Base feedback shaping | feedback rack |
| Fill and color treatment | sculpt rack, preserving both stacks' internal order |
| Background | field |
| Motion treatment | delay rack; native feedback movement clips browse on feedback |
| Object | figure |
| Text and forms | glyph |
| Glitch clips | texture |
| Test sources | field, figure, glyph or grain |

All 43 reference layer/composition rack instances are represented. Existing Figure Linear Cloner and first Mirror were retained in the reference order; additional effects start bypassed with their saved parameters intact. Imported clip effects and native transport automation are preserved. Explicit glitch router taps were remapped from the old text layer to Soup's glyph layer. Imported source dimensions are 1920×1080.

Verification: all 159 external plugin identifiers available in Arena; native save/readback confirms all 245 imported shader/clip-effect identities and their order; eight Soup layers and 43 Heart rack controls present; Heart reconnected with motion unheld. MTK_Worleyz and z33d+ were played, captured at 1920×1080 and visually inspected, then cleared to restore the prior idle scene. All-shader artistic and sustained performance validation has not been performed.

This restores the reference library and processing tools within Soup. Native Feedback clips and Soup's shader-owned feedback history have different recurrence semantics; moving output effects does not insert them inside a shader's private history buffer. New shaders retain original controls/animation; individually tuned Heart Homes remain a subsequent instrument-design task. No speculative motion recipes were applied to the imported bank.

Machine-readable details: `merge-report.json`, `dependency-check.json`, `native-validation.json`, `playback-check.json`. The one-time builder is `sp/qa/merge_feedback_into_soup.py`; rerunning it uses the pre-merge snapshot and would discard later edits, so do not rerun against new work without a fresh migration plan.
