"""Source-identity navigation; never move or replace composition clips."""
COPIES={
 'Heart Hering Field',
 'Heart Fraser Spiral Field',
 'Heart Cafe Wall Field',
 'Heart Pinna Brelstaff Figure',
 'Heart Barberpole Field','Heart Stepping Feet Field',
 'Heart Capsule',
 'Heart Melting Fractal',
 'Heart Klein Bottle',
 'Heart Color Wheel',
 'Heart HypnoWorm','Heart Torus','Heart Quaternion Field','Heart Quaternion Swell',
 'Heart Paper Fractal','Heart Vector Lattice','Heart Concentrip','Heart Puls Lattice',
 'Heart Ancient Temple','Heart Kali Liberation','SP Figure Ring Source',
 'SP Figure Spike Source','SP Figure Crystal Source','SP Figure Solid Source',
}
NOTES={
 'HypnoWorm':'Original: black-output issue; use Heart HypnoWorm.',
 'Torus thingy':'Original: no exposed controls; use Heart Torus.',
 'Melting Fractal':'Review: fold settings can produce blank output.',
 'Klein Bottle (3D)':'Review: dim/static output in the sampled settings.',
 'Color Wheel':'Original: negative warp is negative gain; use Heart Color Wheel.',
 'SP Figure':'Original: edge-on tilt and source placement can hide it; use Heart Capsule.',
 'Heart Kali Liberation':'Controls checked; Field staging. Figure containment not verified.',
}
# Actual composition captures: shader-coverage-batch8, output-sheet-0..3.
# This is an exploration list, never a containment certification.
FIGURE_CANDIDATES={
 'z33d+','DimensionMorphingTopography','MagicLougie','GeodesicTiling',
 'SpaceSpore','4D Voronoi + Hopf Fibration','16 Dimensional Julia (Sedenion)',
 'Barth Sextic Surfaces','curved surface','Hopf + Poincare',
 'Quantum Zappy Sphere','Quaternion Averaging',
}
NOTES.update({
 'Melting Fractal':'Original: blank fold states; use Heart Melting Fractal.',
 'Klein Bottle (3D)':'Original: dim output; use Heart Klein Bottle.',
 'Crystal Drops':'Original: droplets cross edges; use SP Figure Crystal Source.',
 'Spikeball_v2':'Original: spikes cross edges; use SP Figure Spike Source.',
 'RainbowRingCubicTwist':'Original: frame contact; use SP Figure Ring Source.',
 'SP State Test':'Diagnostic source; not a performance instrument.',
 'Gradient Bars':'Full-frame bars; Field/Texture candidate.',
 'Tunnelines':'Full-frame pattern; Field candidate.',
 'Rings':'Sampled rings reach frame edges; Field candidate.',
 'Metaballs':'Sampled scattered balls reach edges; Field candidate.',
 'Hopf fibers SP':'Sampled full-frame close-up; Field candidate.',
})
def exploration(clips,role):
 if role.strip().lower()!='figure':return []
 return [c for c in clips if c.get('source') in FIGURE_CANDIDATES or c.get('heart_copy')]
def annotate(clips):
 return [dict(c,heart_copy=c.get('source') in COPIES,note=NOTES.get(c.get('source'),'')) for c in clips]
def candidates(layer):
 bank=layer.get('bank')
 if bank=='explore':return layer.get('explore',[])
 return layer.get('heart_copies',[]) if bank=='heart' else layer.get('forms',[]) if bank=='forms' else layer.get('clips',[])
