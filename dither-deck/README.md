# the 1-bit dither deck

a playground of black-and-white dither machines: **18 atoms** (S01–S23, single
techniques — S14/S15/S17–S19 are still in the lab) and **9 molecules** (M1–M9,
bonds of atom pairs), all wired to one persistent slider on one persistent
canvas. every state is static; the knob alone moves anything. ink is pinned by
exact-conservation thresholding unless a toy documents its own law (S13's coat
covers 0.26 on purpose).

## run it

open `index.html` in any browser. double-click works — no server, no build,
no dependencies. everything (including both blue-noise masks) is embedded.

## layout

- `index.html` — the unified deck. this is the thing you play with.
- `toys/` — the canonical sources, one standalone file per study:
  - `01.html … 13.html` — the atoms. each opens on its own too.
  - `m*.html` — the molecules, including retired variants (kept as fossils;
    only the ones in the manifest ship in the deck).
  - `deck_slim.html` — the last built deck. **keep it**: the builder reads the
    two blue-noise masks out of it when re-embedding.
  - `build_deck.py` — rebuilds the unified deck from the sources.
  - `embed.py` — injects a blue-noise mask into a toy that has a
    `BNMASKPLACEHOLDER_OLD/NEW` token.
  - `qa.py`, `deckqa.py` — the test harnesses (need playwright, see below).

## rebuild after editing a toy

```
cd toys
python3 build_deck.py        # rewrites toys/deck_slim.html
cp deck_slim.html ../index.html
```

the builder wraps each toy's machine (everything above its rail boilerplate)
in a closure module and mounts all modules on one canvas + one rail.

## add a new toy

copy any atom as a template. the contract the builder needs, verbatim:

- a `<script>` block containing `let k=0` and `function apply(`
- `document.getElementById("scene")` for the canvas (the builder swaps it
  for an offscreen canvas)
- rail boilerplate starting exactly at `const rail=document.getElementById("rail");`
  (the builder cuts there)
- the tail contract: `window.atom={name:"S14", set(t){…}, get(){…}}`
- masks: put `"BNMASKPLACEHOLDER_NEW"` (or `_OLD`) where the mask literal goes
  and run `python3 embed.py deck_slim.html mytoy.html BNMASKPLACEHOLDER_NEW MASK_NEW`

then add the file to `MANIFEST_ATOMS` / `MANIFEST_MOLS` in `build_deck.py`
and rebuild.

## QA (optional)

```
pip install playwright && playwright install chromium
cd toys
python3 qa.py 12 s12 "0,0.5,1"     # one toy: ink per state, 200-step granularity, PNGs to /tmp/qa_shots
python3 deckqa.py                  # whole deck: instant-switch probes, knob persistence
```

the laws the harnesses enforce: ink holds at the toy's stated tone at every k,
and a 200-step sweep flips no more than ~2.5% of the field per step (S12's
whorl rephase is the one documented exception, ≤3.3%).
