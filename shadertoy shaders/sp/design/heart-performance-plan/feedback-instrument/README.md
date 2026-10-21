# Heart feedback candidate

The separate **heart feedback** clip is staged at layer 1, column 6 in `Feedback instrument.avc`. The original Map at layer 1, column 1 remains intact and playing. Start/Studio start have not been replaced with this candidate.

`sp/patches/SP Heart Feedback` is a separately identified Wire/ISF instrument. It inherits Map's persistent history and adds hue, inversion, folding, detail and independent RGB decay inside that history path. The existing layer effects still process the output afterward. RGB decay is not a recreation of native Delay RGB's temporal behavior.

The Heart card exposes Turn, Drift, Breathe and Fold starting behaviors, plus Reset trails. Home selects Turn unless a user Home is saved. These are bounded relationship recipes, independent of parameter count; their artistic tuning still needs live review.

Reset trails uses a native trigger and counter. A one-pixel persistent latch remembers the last event seen by the shader. On the next rendered frame, a new counter value clears the actual history buffer. It does not rely on a timed button pulse, and fresh input resumes on the following frame.

Validation: offscreen GPU tests prove nonempty history becomes zero, remains zero for six empty frames, accepts fresh input exactly, and that loop hue changes stored history. Both neutral and combined-effect reset cases pass. Arena exposes the installed Reset trails control as ParamEvent. Thirty engine checks pass. Candidate activation, live behavior tuning, native reset observation and matched full-resolution performance measurements remain pending; these are not covered by the offscreen correctness test.

### Adapter validation follow-up

Real Arena-schema integration exposed and fixed a discovery defect: event parameters were omitted from the instrument's parameter map, making Reset trails inaccessible even though Arena exposed it. Trigger/Event controls now remain available while staying out of continuously driven slots. Tests cover one trigger POST (no numeric write), replacement parameter IDs, all four behavior bounds in native units, and stable relationship binding after parameter reordering or adding an unknown control. The unknown control remains undriven. Thirty-three engine checks now pass.

The repaired adapter successfully delivered a Reset trails event to the **inactive** L1C6 candidate. This verifies live endpoint delivery without replacing the playing Map; it is not a visual observation of the active candidate resetting. Engine update preserved six playing clips and returned connected with an empty delivery queue. Live behavior review and matched performance acceptance still remain.

## September 7 live review update

Candidate is now playing at L1C6 in the separately saved **Feedback performance** patch. **Before feedback review** preserves the prior Map setup. Turn/Drift/Breathe/Fold were exercised and output snapshots retained alongside `behavior-live-checks.json`. Repeated same-composition recall and recall from eight empty layers restored the six instruments and drive counts. This supersedes earlier statements that the candidate was only staged/inactive. Live Reset event delivery passed; native single-frame buffer inspection remains unverified. Full-resolution acquisition sampling passed the one-minute checks in `../performance/README.md`; full release performance acceptance remains open.

## Native output shaping revision

**Feedback shaping** adds Invert RGB → Blur → Sharpen after SPHeartFeedback, copying original Map parameter/mixer values with initial zero opacity and bypass. Original Map and previous reviewed patches remain intact. Each native effect and the linked Blur + Sharpen action passed Heart on/off envelope/bypass checks and were returned off before saving. Sharpen's original Strength is zero; controls are restored but not newly artistically tuned. These are native output effects, distinct from shader Loop Invert/Loop Detail inside history. See `restored-native-shaping.json` and `shaping-live-checks.json`.
