# the vision — read this before the code

you are holding a deck of 1-bit machines. two colors, one 680² canvas, one
slider. no animation, no interaction but the knob. within those limits the
ambition is total: **push the boundaries of what is possible in this medium.**
this document is the philosophy. the README is the plumbing. if you only
read one file, read this one.

## what we are looking at

everything here should look like **a chemical reaction happening in TV
static** — a strange etch-a-sketch speaking on its own. the territory:

- reaction-diffusion, Turing patterns, slime mold
- pareidolia — optical illusions of depth and form, patterns that aren't
  really there
- animal stripes and spots appearing out of noise
- fingerprints, whorls, deltas
- moiré, interference, fields that shimmer with implied motion while
  standing perfectly still

but — and this is the whole trick — **the maths must be rigorously true to
its own identity and function, and the signal must pass through clear and
felt.** the leopard spots are not a drawing of leopard spots: they are the
Gray–Scott reaction-diffusion equations (Turing's 1952 mechanism, Pearson's
spot regime) integrated honestly, and the coat *emerges*. the fingerprint is
not clip-art: it is the stream function of flow past a cylinder with
circulation, and the arch, the deltas and the whorl *emerge* — the finger's
own taxonomy falling out of one line of fluid dynamics. the worms are real
Floyd–Steinberg error diffusion; the pinstripes are a real leaky error
carry; the screens are real screens. we never fake the phenomenon. we build
the honest machine and let the phenomenon arrive.

when the math and the story disagree, the math wins and the header gets
corrected. (this happened: M7's header once claimed ink conservation
"emerged" along its axis; measurement showed the oscillator just hovers at
threshold. the correction is in the file. rigor over story, always.)

## the one law of feel

**as many distinctive, standout patterns as possible as you move the
slider. DISTINCT pattern recognition and wide variety — that is what makes
them pop and be felt.**

every machine earns its place by producing states you can name at a glance:
pinstripes, worms, rosettes, whorls, mazes, combs. the slider must traverse
genuinely different territories — never shades of the same texture. if two
states look alike, one of them is wrong. if a molecule looks like its atom,
the bond isn't bonding. this law has killed more versions than any other;
it is the certification instrument.

## the discipline

these laws are not style. they are what keeps the signal felt.

1. **static states.** nothing moves on its own — no drift, no pulse, no
   animation loop. the knob alone moves anything. a 1-bit field that stands
   still lets the eye do the moving; that is where the pareidolia lives.

2. **one slider, one stage, no resets.** the deck is a single runtime:
   one canvas, one k, instant switching. you change the *view*, never the
   *state*. the image never disappears — comparison is the instrument, and
   you cannot compare with a blank.

3. **pure maths only.** real algorithms from printing and physics:
   Floyd–Steinberg, Bayer nests, AM halftone rulings, blue-noise masks,
   distance transforms, potential flow, reaction-diffusion. no drawn
   textures, no random noise posing as pattern. if a toy claims Turing,
   it integrates the equations.

4. **ink conservation.** the 45th-percentile law (atom 02's): every state
   is thresholded so the ink holds exactly at its tone while the pattern
   reorganizes. variety comes from structure, not from fading. a toy may
   break the law only by declaring its own — S13's coat covers 0.26
   because that is the cover-fraction of a cat's rosettes, and the header
   says so.

5. **granularity: micro discrete, macro continuous.** a 1/200 k-step may
   flip no more than ~2.5% of the field. metamorphosis pours through the
   blue-noise order — a reaction front, never a jump. machines with
   chaotic feedback (the error-carry family) are quantized to stops and
   dissolved between them; that is documented in their headers. the one
   standing exception is S12's whorl rephase (≤3.3% — a phase wrap no stop
   spacing can subdivide), also documented.

6. **honest headers.** every toy's comment block carries its maths, its
   calibrations, its deviations and its dead ends. the headers *are* the
   documentation. read them before the code; keep them current when you
   change the machine.

## how to judge

the certification instrument is the eye — yours, then anyone's you hand
the deck to. the method:

- **drag slowly.** states must stand still and stay distinct. mid-states
  should read as *reaction*, not mush.
- **compare with the slider held.** flip views at one k. sameness is a
  bug; "slightly more defined" is a verdict worth keeping (that is how the
  NEW mask became the deck's default floor).
- **name what you see.** if you can say "pinstripes", "cow hide",
  "fingerprint", the machine is passing signal. "sphere warp" was a
  verdict, and it rebuilt S12 from scratch.
- **variations are born only from felt need.** never fork a machine to
  decorate it; fork it because you felt a difference or a lack.

## the working method

the loop that built everything in this deck:

1. **prototype offline first.** numpy, small grids, many regimes. verify
   the pattern is *recognizable* before any browser is involved. (S13 went
   through: wrong morphogen polarity, coarsening instabilities, the wrong
   diffusion scale, before the leopard stood still.)
2. **build the toy honest.** embed the machine, threshold by the
   conservation law, quantize chaos into stops, dissolve between them in
   blue-noise order.
3. **QA numerically.** `qa.py` measures ink at every state and the
   200-step granularity; `deckqa.py` proves instant switching and knob
   persistence. the laws are enforced by measurement, not intention.
4. **then the felt verdict.** numbers pass the machine; the eye certifies
   it. both gates are required.

## where the vision lives in the code

a guided tour, in reading order:

- `toys/02.html` — the conservation law. everything inherits from it.
- `toys/08.html` — the blue-noise floor and the leaky carry. the deck's
  soil and its first personality.
- `toys/09.html` — the error kernel done right, and the note on grain:
  why it deviates from 08 and why that was the correct call.
- `toys/m7.html` — the bond idea: two certified parents, one axis of
  where-the-error-may-go, and a journey of distinct states between them.
- `toys/12.html` — the fingerprint: potential flow, honest about its one
  granularity exception.
- `toys/13.html` — the coat: Turing's mechanism, honest about showing the
  birth of the pattern and not its death.

## where it goes next

the medium is nowhere near exhausted. open fronts: the stripe and labyrinth
regimes of the reaction (zebra, maze), bonds between the flow field and the
diffusion field, deeper masks, machines nobody has named yet. the rule for
all of it is the same: build the honest machine, verify the phenomenon is
recognizable, keep the states static, make the slider travel. the boundary
of the medium is wherever the next rigorous machine produces a state
nobody has felt before.
