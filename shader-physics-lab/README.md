# Shader Physics Lab

AI-assisted shader development with autonomous verification. Translate physics papers into GLSL with visual validation.

## Core Philosophy

1. **Research-driven**: You provide papers/equations → Claude implements
2. **Self-verifying**: Claude checks its own output against paper figures
3. **Library-focused**: Store and recall shaders semantically, not iterative presets

## Workflow

### 1. Prepare Research Intake

```bash
intake/optical-centrifuge/
├── macphail-bartley-2026.pdf
├── equations.md              # Extract key math (Claude can help)
├── expected-output/
│   └── figure-2-helical.png  # Screenshot from paper
└── notes.md                  # "Focus on equation 3, ignore thermal terms"
```

### 2. Generate Shader

```bash
python scripts/process_intake.py intake/optical-centrifuge/ \
  --name "spinor-helical-rotation" \
  --tags "quantum,rotation,optical-centrifuge"
```

**What happens:**
- Claude reads intake materials
- Extracts equations and implementation strategy
- Generates GLSL with exposed uniforms
- Enters verification loop:
  - Renders output
  - Compares to paper figures
  - If mismatch: debugs and regenerates
  - If match: saves to library
- Creates slider UI with reasonable ranges

### 3. Load & Interact

```bash
# List library
python scripts/shader_manager.py list --tags quantum

# Load shader in viewer
python -m http.server 8000
# Open: http://localhost:8000/src/viewer.html?shader=spinor-helical-rotation
```

### 4. Iterate or Create New

```bash
# New shader from different research
python scripts/process_intake.py intake/schrodinger-wave-packet/

# Original shader still in library, load by name
```

## Verification Decision Gate

Claude won't save a shader until it passes visual verification:

```python
VERIFICATION_CRITERIA = {
    "structure": ["smooth", "no artifacts", "correct symmetry"],
    "dynamics": ["expected periodicity", "stable evolution"],
    "quantitative": ["measure key values against paper"]
}
```

Max 10 attempts before flagging for manual review.

## Setup

```bash
pip install -r requirements.txt
```

Requires:
- Claude CLI configured
- Browser with WebGL support
- (Optional) LaTeX for equation rendering

## File Formats

### equations.md
```markdown
## Key Equations

### Equation 3: Torque Coupling
τ = -∂U/∂θ where U = -μE cos(θ - φ(t))

- μ: molecular polarizability (use 1.5 × 10⁻³⁰ C·m)
- φ(t): rotating laser polarization angle = ωt
- ω: rotation frequency (variable, ~THz range)

### Implementation notes
Discretize as: θ[n+1] = θ[n] + (τ/I)Δt
Use Runge-Kutta 4 for stability
```

### notes.md
```markdown
## Implementation Strategy

Focus on the adiabatic regime (slow rotation).
Ignore thermal fluctuations for now - paper uses T→0 limit.
The key visual signature is smooth helical alignment.

## Expected Behavior

Should see spiral pattern rotating with period matching equation 7.
If you see discrete jumps, the time step is too large.
```

## Shader Metadata

Each shader in `shaders/` has accompanying JSON:

```json
{
  "name": "spinor-helical-rotation",
  "tags": ["quantum", "rotation", "optical-centrifuge"],
  "source_paper": "intake/optical-centrifuge/macphail-bartley-2026.pdf",
  "created": "2026-01-30T12:34:56Z",
  "verified": true,
  "verification_score": 0.94,
  "uniforms": {
    "rotation_rate": {"min": 0.0, "max": 5.0, "default": 1.2},
    "phase_offset": {"min": 0.0, "max": 6.28, "default": 0.0}
  }
}
```

## Architecture

**No human in the loop during verification**: Claude screenshots its output, compares to paper figures, identifies discrepancies, fixes autonomously.

**Failure = debug log**: If verification fails after N attempts, dump detailed log showing what didn't match and what was tried.

**Semantic library**: "Show me all interference-based shaders" not "shader_v23_final_REAL.glsl"

## TODO - Populate These

- [ ] `scripts/process_intake.py` - Main generation loop with Claude CLI
- [ ] `scripts/verify_output.py` - Vision comparison logic
- [ ] `src/viewer.html` - WebGL viewer + dat.GUI integration
- [ ] `src/shader-template.glsl` - Base shader structure
- [ ] Complete `config.json` with system defaults

## Design Principles (Asparśa Yoga Alignment)

- **Prakāśa**: Perceive the physics without claiming ownership of the math
- **Tarka**: Trace contradictions between expected and rendered output
- **Nivṛtti**: Pause generation when visual verification fails
- **Māyāvāda**: The shader is a map, not the physics itself
- **Ārēka**: Some equations are too sacred to approximate—preserve their exact form
