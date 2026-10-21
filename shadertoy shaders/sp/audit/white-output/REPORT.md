# White-output audit correction

SP Atom Grain L8C1 and SP Field L3C8 are not solid-white rendering failures. Resolume snapshots are RGBA: these sources carry the visible intensity in alpha. The old contact-sheet conversion discarded alpha; the inline image view also concealed that detail. This produced false white/static classifications.

Both original motion captures were composited on black and visually reviewed. Grain shows noise and intensity changes; Field shows changing smooth noise. Mean pixel differences on black are 26.44/255 and 22.56/255 respectively. Fresh neutral-setting captures also show valid Grain and Field signals. No shader or Wire patch was changed. Neutral settings were sent through Heart, with native readbacks captured alongside the images.

The batch 5–11 contact-sheet generators now composite alpha before producing RGB review images and metrics. Raw snapshots are preserved. Rebuilt sheets are corrected artifacts, not a claim of a fresh exhaustive visual review.

The other inspected metrics remain concerning after alpha correction: HypnoWorm black; Melting Fractal one black frame; Klein Bottle 3D dim/static; Color Wheel one black frame; legacy SP Figure nearly invisible. These remain pending repair. See corrected-metrics.json. Torus uses a different capture filename and is not included in that metrics run.
