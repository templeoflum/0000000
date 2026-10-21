# First coherent Figure batch — September 8, 2026

Implemented shared definitions in `sp/engine/instruments.json`, consumed by Heart through `instruments.py`. The first bank contains 3D (Solid), Shell (4D Field), and Seed (imported z33d+). The native source IDs are recorded alongside role, family, primary controls, source framing, Home, routing and review status. Existing atom/relationship/parameter adapters are reused; existing user Homes still take precedence. New controls remain undriven. This is not a migration of legacy Home storage.

## Source framing and motion

Containment applies before the effect stack. No layer mask or downstream cloner constraint was added. Shell's old 4D projection bound could underestimate the subject and truncate it; the corrected phase-independent hypersphere projection bound includes bar/vertex reach, antialiasing reserve and a separate frame margin. It changes source framing, including apparent size at some perspective settings. Size changes remain explicit; framing does not chase each rotational phase. The installed shell resource matches the project source, with its native ID and parameter layout preserved.

The new Homes use the existing pendulum relationship engine. Solid has 13 driven controls; Shell has 18 after Home finishes applying; Seed has six. Source choices/resource counts remain deliberately static. Shell uses eight internal slices at Home instead of the previous approximately 32. This is a chosen starting texture, not a measured GPU savings claim. Source selectors are manual and available.

The Forms picker provides the three sources and an All sources switch. Previous/next follows the selected bank. All imported clips remain in their original slots. Native Heart controls were reloaded and the Forms/All sources/three source buttons were verified through accessibility.

## Actual Soup route

The inspected native snapshot has Figure on layer 5 inside Group 1 with field, delay and glyph. Figure's layer effects are after the source, including Linear Cloner. Sculpt's level clip at L2C1 receives Group 1 (`Input=1:1`); Map at L1C1 receives sculpt (`Input=3:2`). Delay's figure tap uses L5 (`Input=3:5`). Map owns its shader history; native effects on the feedback layer are downstream of that private buffer. Grouped content also contributes through the existing composition structure; this was not rewritten as a different layer layout.

Linear Cloner was exercised on all three Figures. The starting depth stack then connected the existing level/Map route. Cloner controls use Heart's native parameter action so saved Resolume automation does not silently replace the chosen settings. Other imported rack effects remain available.

## Evidence and limits

- 125 engine tests pass, including new role-scoped definition/Home, bank selection, preservation of saved user Homes and unknown-control checks. JavaScript syntax passes.
- `source-checks.json`: 34 source-only GPU cases at 640×360 with nonempty alpha and empty frame borders. Includes Home phase samples, Solid corner cases, Shell sphere/perspective and bar/vertex extremes. Two Shell stress cases compare the radial rejection enabled/disabled with no material pixel difference.
- Native 1920×1080 screenshots and motion readback verify the three sources and their effect-stack output. `native-home-checks.json` captured Shell while Home was still applying (11 drives); `shell-recheck.json` confirms the complete 18-drive Home. These are sampled checks, not exhaustive validation of all manual settings.
- Seed's current fixed native zoom and reviewed Home ranges passed the sampled checks; a global containment proof for arbitrary manual Seed settings is not established. Portrait framing is not certified: the existing shell prepass/output dimension convention needs separate treatment before using portrait compositions.
- No sustained frame-rate claim is made for the new full stack. Primary-control grouping is declared in the definitions but a dedicated simplified primary-control panel is not yet implemented.

## Worker use and recovery

A bounded read-only source review identified the Shell bound defect; deterministic extraction and GPU checks verified it. A short local Qwen3-Coder review was also run and unloaded before rendering. Its claim that bounded controls guarantee Seed containment and its out-of-range zoom test were rejected; it is retained as unverified review evidence in `local-seed-review.json`. No private source was sent to Hermes/cloud endpoints.

Recovery: `Before Figure milestone.avc`, `before-heart.json`, before-config copies, and before-source copies in this folder. Normal composition path remains `~/Documents/Resolume Arena/Compositions/generative soup_16x9_1920x1080_60fps.avc`. Existing prior patches remain available. See the final execution record for saved-patch/recall results.

## Final execution record

Saved **Figure depth**, selected it as Start, then recalled it successfully through Heart. Native dependency/routing checks reached Ready with Map (L1C1), level (L2C1) and 3D (L5C3), their motion and the Figure cloner stack restored. Normal Generative Soup was saved before the recall; recall opens the named patch snapshot. Existing patches and recovery copies remain available. The shell generator was updated alongside the tested source so rebuilding preserves the correction. The current playable revision is ready for visual refinement; broad manual-source envelopes, primary-control presentation and sustained full-stack performance remain open.
