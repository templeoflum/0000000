# Output cadence and rendering checks · September 11–12

The powered idle composition held 60 FPS for the full 20-second sample at 3840×1440. This is actual published composition cadence: 1,200 Syphon frames, 60 in every one-second bucket, 16.665 ms median interval, 17.300 ms p95, and 18.295 ms maximum. There were no gaps above 25 ms. Representative content and simultaneous effects still require their own run.

The sampler listens to the existing Arena **Composition** Syphon server and acquires each shared texture handle. It creates no window, draws nothing, copies no pixels, and makes no Arena writes. Notifications include transport scheduling, so these figures are not isolated GPU timings or proof of projector presentation. It does not distinguish changing pixels from repeatedly published identical content.

Run the compiled sampler after setting the intended load:

```sh
/tmp/heart-output-cadence 20 2 > /tmp/heart-session-build/checks/session-performance-combined.json
```

The arguments are measured seconds and warm-up seconds. Local Syphon IPC needs the same sandbox escalation used for the successful idle capture. Source: `session-performance-output-cadence.m`. The framework is installed under `sp/preview/.venv/lib/python3.12/site-packages/syphon/libs/Syphon.framework`; compile with ARC, Foundation, Metal and that Syphon framework/rpath. No native setting needs changing.

## Script optimization ready for installation

**SP Atom Script** spends most of its default rendering time tracing strokes across empty pixels. The candidate exits with transparent black when the sample lies outside the combined glyph bounds, expanded by stroke radius and the full antialias footprint.

The bound is evaluated after the existing position, size and signed slant transforms, in the same coordinate system used by its stroke-distance function. All 159 complete glyph boxes contain every path vertex. Partial writes remain on those paths; morphs use the union of both complete glyph boxes. Round and flat ends fit within the radius expansion. The shader has a finite `Soft` smoothstep radius, fully included in the bound; it has no separate Glow control. This does not alter stroke shape, writing, softness, alpha, parameter ranges or schema.

The paired comparison passed **324 byte-for-byte RGBA checks**: all 159 glyphs at exact and intermediate morph positions with sampled extreme size, signed position/slant, weight, ends, softness and partial writing; plus full-resolution 1920×1080 and 3840×1440 cases. The check also validates the glyph boxes directly. Images are generated offscreen from the original and candidate shader.

| Scenario | Original median | Candidate median |
|---|---:|---:|
| 1920×1080, defaults | 4.444 ms | 0.773 ms |
| 1920×1080, large Greek glyph | 0.549 ms | 0.305 ms |
| 3840×1440, defaults | 9.719 ms | 0.669 ms |
| 3840×1440, large Greek glyph | 0.849 ms | 0.333 ms |

These are Apple M5 Max offscreen OpenGL screening timings, CPU submission through synchronized GPU completion, excluding output readback. Original/candidate order alternated over 80 paired samples per scenario after 12 warm-ups. Arena and other applications remained open. The improvement is substantial in these cases; these timings are not Arena output FPS.

### Exact install map

`session-performance-script-install.json` records absolute destinations and expected current/candidate hashes. Both the workspace shader and installed Wire resource currently match SHA-256 `96551bd0466a423d78ed13f682dd6784d46d6f62402ebe7bfe293f0123f95e12`.

Copy `session-performance-script-optimized.fs` to these two files after checking their current hash:

- `/Users/donovan/work/0000000/shadertoy shaders/sp/SP Atom Script.fs`
- `/Users/donovan/Documents/Resolume Wire/Patches/SP Atom Script/Resource/SP Atom Script.fs`

Copy `session-performance-make-script.py` to `/Users/donovan/work/0000000/shadertoy shaders/sp/make_script.py` so later regeneration retains the optimization. Read-only evaluation of its template regenerated the exact candidate shader. **Do not run the generator as the install step:** its normal entry point also writes installed resources.

The existing `.wire` node references `Resource/SP Atom Script.fs`. Its input metadata and the ISF header are unchanged. No Wire graph/schema regeneration or `.sp.json` change is needed. Reloading the updated source in Arena and confirming it renders is a separate runtime check. No production files were changed by this audit.

For reproduction, the original, candidate and portable comparison are alongside this report:

```sh
sp/qa/.venv/bin/python /tmp/heart-session-build/checks/session-performance-script-check.py
```

This uses offscreen GPU access and writes `session-performance-script-recheck.json` by default. `--original`, `--candidate`, and `--report` allow explicit paths.

## Other measured costs to retain as options

The earlier September 7 audit measured Hopf Full at 12.65 ms, Balanced at 8.57 ms and Performance at 6.38 ms at 1920×1080. The quality control already exists in a separate installed patch. Fewer volume samples change rendering; do not silently select a lower mode. Script's bound optimization preserves the sampled image instead.

The alternate Delay patch halves only long-history texture width and height. Earlier system GPU activity fell from 51.5% to 38.0%, with softer echoes. That is an explicit visual tradeoff and an older 1920×1080 measurement. The current output has 2.667 times that pixel count. Original timing, taps, full-resolution current frame and short RGB delay remain available. No blanket size, geometry, masks, active effects or layer order changes are justified by the idle result.

## Show-time deferral at the user's direction

The later combined-load sample measured **30.2 FPS over 20 seconds**, with a lowest one-second bucket of **28 FPS**, **37.47 ms p95** frame interval and **44.06 ms maximum**. This does not establish a sustained 30 FPS floor. Evidence: `session-performance-combined.json`; the separate idle result above remains 60 FPS.

Read-only follow-up identified the playing router's original SPDelayChain as the first future isolation candidate: its installed graph contains a 480-frame main texture history plus 16 RGB history frames, now evaluated at 3840×1440. Its contribution to this combined slowdown was **not isolated or measured**. The existing half-resolution-history alternative changes echo softness; no replacement was made. No additional shader optimization was applied during this follow-up.

The user explicitly made output performance the lowest priority with less than one hour before the show. Further investigation, comparisons and performance changes are **deferred at the user's direction** so the remaining work can focus on the rack, recovery and opacity controls.
