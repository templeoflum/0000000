# Implementation Notes for [Paper Name]

## Paper Overview

**Authors**: 
**Publication**: 
**Key Contribution**: 

## Implementation Strategy

### What to Focus On
- Primary equations: [list equation numbers from paper]
- Key visual signatures: [what should the output look like?]
- Parameter ranges: [physical limits, interesting regimes]

### What to Ignore/Simplify
- Thermal effects (if T→0 limit)
- Secondary perturbations
- Experimental noise/artifacts

## Expected Visual Behavior

### Static View
Description of what a single frame should show.

### Dynamic Evolution
How the system should evolve over time.

### Key Features to Verify
1. [Symmetry property, e.g., "6-fold rotational symmetry"]
2. [Temporal property, e.g., "period of 2.3ns"]
3. [Spatial property, e.g., "exponential decay envelope"]

## Potential Implementation Challenges

- **Challenge**: [e.g., "Stiff differential equation"]
  **Solution**: [e.g., "Use implicit method or reduce time step"]

- **Challenge**: [e.g., "High frequency oscillations aliasing"]
  **Solution**: [e.g., "Ensure sufficient spatial resolution"]

## Reference Figures from Paper

- Figure 2: Shows [description] - use for verification
- Figure 3b: Shows [description] - secondary check
- Figure 5: Quantitative data - extract [specific values]

## Physical Units → Shader Units

Map physical quantities to normalized shader space:
- Time: 1 second = [shader units]
- Length: 1 meter = [shader units]
- Frequency: 1 THz = [shader units]

## Success Criteria

The shader passes verification if:
1. [Specific visual criterion]
2. [Measurable quantitative criterion]
3. [Behavioral criterion]
