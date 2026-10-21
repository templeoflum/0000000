# Heart micro TV — design reference and acceptance

## Reference

Sony Design's official **KV-4P1 ESSEN Micro Trinitron Color Monitor (1980)** entry:
https://www.sony.com/en/SonyInfo/design/gallery/KV-4P1/

Sony describes a compact desk/car monitor, square form, extruded anodized silver aluminum, a rod antenna stored along the side, and a screen that lifts from its base. These are design references, not claims that Heart emulates CRT electronics or is a Sony product.

Secondary reference: Sony's KV-9PT50 front/dimension diagram, hosted at https://consolemods.org/wiki/images/1/1a/KV9PT50frontdiagram.pdf . This was found during research; the KV-4P1 official design entry is the selected direction.

## Adaptation

Heart keeps its name. Silver casing, charcoal screen surround, inset trim, a lower control fascia, speaker grille and small stand suggest a physical portable set. All decorative drawing is static outside the video. No scanlines, phosphor effect, glass distortion, glow filter, or cropping is applied to the output.

The detached view has no macOS title bar or traffic lights. It defaults to a small desktop object, approximately 320 points wide. Double-clicking the picture expands to approximately 640 points wide; double-clicking again restores the small frame. Drag the bezel to move it; retain an explicit resize affordance. Pinning, fitting and docking are available in the casing. Resume must remain available while suspended. The normal Heart application menu remains a second route to docking.

The small view prioritizes output and concise live/FPS feedback. Larger geometry can show fuller GPU/resolution information. Expanded information must not cover the image. Always-on-top is the default for the detached TV and remains switchable.

## Acceptance checks

- Transparent borderless window contains only the designed TV shape and its shadow.
- First detach opens small even if previous version saved a large frame.
- Double-click grows to about the former default; second double-click restores exact prior frame.
- Bezel drag and corner resize work without unintentionally engaging Heart's performance pointer capture.
- Controls remain usable at minimum size, including Resume after session suspension.
- Dock/undock retains the same Metal view and Syphon receiver; no extra rendering path.
- Picture retains source aspect ratio and full source resolution. Display scaling is expected in a tiny window.
- Sleep handling adds no wake assertion and no automatic resume.
- Native tests isolate geometry preferences. Live checks record what was actually observed, separately from sustained performance validation.

## MET∃OR / Boustrophedon refinement

User establishes this object as **Heart Monitor**, made by **Boustrophedon Instrument Co.** within the lore. Source authority: `/Users/donovan/work/met3or/CANON.md`, The world / The voice. Visual source: `/Users/donovan/work/met3or/lore/boustrophedon/ft1-pkg/panel/model-ft-1-panel-rev-e.html`, especially panel materials, pushbutton bank and maker-mark SVG. `/Users/donovan/work/met3or/lore/canon-source.md` identifies the canon authority; its linked package README is useful context but the authority resolves dated/serial details.

Selected design vocabulary: aluminum #8f9088 with highlights #a5a69c and shadows #6f7069, engraved warm ink #e7e4d7, dark molded pushbutton caps with a lower mechanical shadow and depressed position when pressed. The maker mark has three alternating arrowed rows. Use the source geometry rather than inventing a replacement. The doctrine is “white sees · gold sounds · red bites”; visual operational feedback belongs in white. No invented serial, calibration stamp, f(t)–1 model designation, or claim that this is the escaped Ser. 0006.

Fit, Dock and Pin are physical controls on the bottom silver fascia, beside the maker/product engraving. The inset instrument-style readout remains in its own dark strip above the silver fascia. This supersedes the initial single-row placement: the user explicitly wants the buttons on the metal, outside the screen surround. The readout has a physical well and restrained glass treatment, while the actual Resolume image remains unchanged. Controls must be real clickable controls with pressed and persistent-state feedback, not painted props.

Small and expanded modes keep separate window rectangles. Expanding stores the current small position/size and restores the most recent expanded rectangle; shrinking stores the current expanded rectangle and restores the small one. Persist both across launches, but start in small mode. Use initial 320×250 and expanded 640×430 defaults only when no valid stored geometry exists. Recover unreachable geometry after display changes without forcing all expansions to screen center.
