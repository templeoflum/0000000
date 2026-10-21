# Scientific Collaboration Protocol v1.1

**Version:** 1.1  
**Status:** Implementation ready (recursive verification layer untested)  
**Created:** 2026-02-01  
**Authors:** Claude + Hedawn  
**Predecessor:** [scientific_collaboration_protocol_v1.0.md](scientific_collaboration_protocol_v1_0.md)  
**Case study:** Distortion Data Experiment (Experiments 00--05, January 2026)

---

## Version History

- **v0.1** (2026-01-27): Initial draft. Eleven-phase sequential model with YAML provenance tracking. Written after Experiment 01 to codify the methodology that emerged during the [initial exploration](sources/source_conversation.txt) and first experiment.
- **v1.0** (2026-01-28): Revised after executing five experiments. Phases reduced from 11 to 6+3. Provenance simplified to Git. Two new principles added. Verification infrastructure, failure protocol, and human-AI collaboration model rewritten from empirical evidence.
- **v1.1** (2026-02-01): Added recursive verification layer and meta-protocol. Addresses multi-experiment lineage tracking, contamination detection, process hallucination prevention, and system self-optimization. Designed for model-agnostic implementation with local-first data architecture.

---

## 1. Core Principles

### 1.1 Falsification-First

Design tests to fail. Seek disconfirmation. Agreement requires evidence.

Every experiment begins with numbered predictions, each carrying a quantitative pass/fail threshold defined before the code is written. "Does this work?" is not a hypothesis. "This mechanism will achieve similarity >= 0.999 across all tested parameters" is.

### 1.2 Isolation-Before-Integration

One tool, one purpose. Validate in isolation. Combine only after verification.

New modules do not modify existing code. Each experiment adds a self-contained module (composition pattern) so that passing tests for Experiment N remain undisturbed by Experiment N+1.

### 1.3 Defined Deliverables

Each phase has explicit outputs. No phase is complete without its deliverable.

The experiment completeness checklist (Section 4.7) is the operational expression of this principle: if any artifact is missing, the experiment is not done, regardless of whether the code runs.

### 1.4 Provenance Tracking

Every change logged. Every result traceable to its inputs. Every fix documented with before/after.

Git is the provenance system. Structured YAML logs are unnecessary when the repository history records every commit, the DEVLOG records every decision, and the metrics JSON records every measurement. The provenance layer should be as simple as possible while remaining auditable.

### 1.5 Failures Are Findings

*New in v1.0.*

Failed predictions are first-class scientific results, not blockers to be fixed. A prediction that fails with a clear explanation teaches more than one that passes unremarkably.

The protocol does not halt on failure (v0.1's STOP-DOCUMENT-ASSESS-FIX-REVALIDATE-RESUME sequence). Instead, failures are recorded as findings with root-cause analysis and added to the cross-experiment knowledge base. The experiment continues.

### 1.6 Machine Verification Over Manual Review

*New in v1.0.*

Every quantitative claim in prose must be machine-verifiable against a source-of-truth dataset. Humans write prose from memory; memory introduces errors. Machine gates catch these errors structurally, surviving context loss, session restarts, and momentum pressure.

Manual review (including AI vision inspection) remains necessary for layout, formatting, and semantic correctness --- but it is the second tier, not the first.

### 1.7 Recursive Verification and Contamination Detection

*New in v1.1.*

Every phase completion triggers audit of all prior phases. Every experiment completion triggers re-verification of ancestor experiments in its lineage. Contamination propagates downstream and must be detected and contained.

Process hallucinations (claimed actions that didn't occur, artifacts that don't exist) are treated as falsifiable claims subject to the same verification rigor as scientific hypotheses.

The system itself is an experimental subject. Configuration decisions (audit frequency, verification thresholds, model selection) are hypotheses tested through meta-experiments.

---

## 2. Architecture

The protocol operates at four levels:

```
Project Setup (once)
    Build the laboratory: tools, infrastructure, shared library
    |
    v
Experiment Cycle (repeated per experiment)
    Specification -> Implementation -> Execution -> Verification -> Documentation -> Commit
    |   (Recursive verification at each phase boundary)
    |
    v  (after all experiments)
Capstone (once)
    Red Team -> Meta-Analysis -> Decision
    |
    v  (ongoing)
Meta-Protocol (system self-audit)
    Track efficiency, detect contamination, test configurations,
    optimize based on evidence
```

### 2.1 Project Setup

The laboratory is built once and reused across experiments. It includes:
- Build system and shared library (Rust crate, Cargo.toml)
- GPU compute pipeline and CPU reference implementations
- MCP server for tool integration (build, test, verify, inspect)
- Verification scripts (claims, gates)
- Cross-experiment tracking (FINDINGS.md)
- **New in v1.1:** Provenance database (SurrealDB), model adapter layer, audit system

New experiments extend the shared library through composition (new modules, new workbench binaries) without modifying existing code.

### 2.2 Experiment Cycle

Six phases per experiment (Section 4). Each phase produces deliverables and must pass its exit gate before the next phase begins. In practice, Implementation and Execution often overlap: the workbench binary is both the test design and the execution engine.

**New in v1.1:** Phase completion triggers recursive audit (Section 3.3). All prior phase deliverables are re-verified for integrity. Contamination halts progression.

### 2.3 Capstone

Three project-level phases (Section 5) executed after all experiments are complete. The dialectical structure from v0.1 is preserved:

```
Experiments 00-05: THESIS
    Build the case. Generate evidence. Document findings.
    |
    v
Red Team: ANTITHESIS
    External adversarial review. Attack methodology.
    Propose alternatives. The reviewer has no prior
    investment in the outcome.
    |
    v
Meta-Analysis: SYNTHESIS
    Evaluate the critique. Audit the process.
    Integrate valid points. Improve the protocol.
    |
    v
Decision: RESOLUTION
    Archive, iterate, or branch.
```

### 2.4 Meta-Protocol (System Self-Audit)

*New in v1.1.*

The system's own configuration and verification strategies are treated as experimental variables. Through meta-experiments, the system discovers optimal audit frequency, verification thresholds, and model allocation through falsifiable testing rather than theoretical speculation.

See Section 6 for full specification.

---

## 3. Execution Model

### 3.1 Dependencies Determine Order

```
If Phase B depends on Phase A:
    A must complete before B starts

If Phase B does not depend on Phase A:
    A and B may run concurrently
```

Within the experiment cycle, phases are numbered but not rigidly sequential. Implementation and Execution are often interleaved (the workbench binary encodes both the test design and the execution logic). Documentation begins during Implementation (the DEVLOG is written in real time).

### 3.2 The Natural Unit Is the Experiment

v0.1 imposed time bounds and gate checks at each of 11 phases. In practice, the natural unit of work is the experiment. Each experiment runs to completion in one or more sessions, producing a self-contained artifact. The gate check that matters is at the end: all verification gates pass before commit.

### 3.3 Recursive Verification on Phase Completion

*New in v1.1.*

When phase N completes, the system performs a recursive audit:

```
Phase N completes
    ↓
Verify N's deliverable exists and is valid
    ↓
Re-verify phases 0 through N-1:
    - Hash all previous deliverables
    - Compare to stored hashes in provenance DB
    - Check for file modifications/deletions
    - Verify artifact integrity
    ↓
If contamination detected:
    HALT progression
    Log contamination event
    Request rollback decision (human or automated)
    ↓
If audit clean:
    Check phase N exit gate
    ↓
If gate passes:
    Advance to phase N+1
```

**Contamination types:**
- **File hash mismatch:** Deliverable modified after completion
- **Missing artifact:** File deleted or never existed (hallucination)
- **Schema violation:** YAML/JSON no longer parses correctly
- **Dependency invalidation:** Upstream experiment re-verified and failed

**Response protocol:**

```yaml
contamination_detected:
  experiment_id: exp_007
  phase: 4
  contamination_type: file_hash_mismatch
  affected_file: phase_deliverables/2_implementation.md
  stored_hash: sha256:a1b2c3...
  current_hash: sha256:d4e5f6...
  
  options:
    1: rollback_to_phase_2  # Discard phases 3-4, restart from 2
    2: accept_modification  # Update stored hash, continue (requires justification)
    3: invalidate_experiment  # Mark entire experiment as contaminated
```

### 3.4 Experiment Lineage Re-verification

*New in v1.1.*

Upon completing experiment E, the system re-verifies all ancestor experiments in E's dependency lineage:

```
Experiment E completes
    ↓
Query provenance DB: SELECT ancestors WHERE used_by(E)
    ↓
For each ancestor A:
    Re-run verification scripts from A's Phase 4
    Re-check predictions against stored metrics
    ↓
If ancestor verification fails:
    Mark A as contaminated
    Cascade contamination to all descendants
    Generate lineage contamination report
    ↓
If all ancestors pass:
    Commit experiment E
```

**Example cascade:**

```
Exp_003 (contaminated: control data was incorrect)
    ↓ (used results from Exp_003)
Exp_005 (cascade contaminated)
    ↓ (built on Exp_005)
Exp_007 (cascade contaminated)

Action required:
    1. Fix Exp_003 control data
    2. Re-run Exp_003 verification
    3. If Exp_003 now passes:
        Re-verify Exp_005 (may still be valid)
        Re-verify Exp_007 (may still be valid)
    4. Update FINDINGS.md with cascade analysis
```

**Lineage tracking in provenance DB:**

```sql
-- Each experiment records its dependencies
CREATE TABLE experiment_lineage (
    experiment_id TEXT,
    depends_on_experiment TEXT,
    dependency_type TEXT,  -- 'extends', 'uses_control', 'compares_to'
    created_at TIMESTAMP
);

-- Query to find all ancestors
SELECT DISTINCT depends_on_experiment 
FROM experiment_lineage 
WHERE experiment_id = 'exp_007'
UNION
SELECT DISTINCT l2.depends_on_experiment
FROM experiment_lineage l1
JOIN experiment_lineage l2 ON l1.depends_on_experiment = l2.experiment_id
WHERE l1.experiment_id = 'exp_007';
-- (Recursive CTE for full transitive closure)
```

---

## 4. Experiment Phases

### Phase 1: Specification

**Purpose:** Define the hypothesis, predictions, and success criteria before writing any code.

**Depends on:** Nothing (or previous experiment's findings)

**Deliverable:**

```
experiments/exp_NNN_description/
└── spec.md

Contents:
- Hypothesis: one-sentence claim
- Background: what prior work/experiments led here
- Predictions: numbered list with quantitative thresholds
- Controls: what reference data will be used
- Success criteria: which predictions must pass
```

**Exit gate:**

- [ ] `spec.md` exists
- [ ] Contains ≥1 falsifiable prediction with numeric threshold
- [ ] Success criteria explicitly stated (not "see what happens")

**Common failure modes:**

- Stub spec with vague directions ("try different values")
- Predictions without thresholds ("should be better")
- Missing control specification

**Evidence:** See Section 10.6 (Stubs Are Not Plans).

---

### Phase 2: Implementation

**Purpose:** Write code that tests the predictions. Build infrastructure if needed.

**Depends on:** Phase 1

**Deliverable:**

```
experiments/exp_NNN_description/
├── src/bin/workbench_NNN.rs    # Test harness
├── src/modules/exp_NNN.rs      # New functionality (composition pattern)
├── tests/test_exp_NNN.rs       # Unit tests
└── DEVLOG.md                   # Session notes (started here, continues through Phase 5)
```

**Exit gate:**

- [ ] Workbench binary compiles
- [ ] Unit tests pass
- [ ] Code integrates via composition (no modifications to existing modules)
- [ ] DEVLOG documents design decisions

**DEVLOG structure:**

```markdown
# DEVLOG: Experiment NNN

## Session 1 (YYYY-MM-DD)

**Goal:** [What I'm trying to accomplish this session]

**Implementation notes:**
- [Decisions made, alternatives considered]
- [Code structure choices]

**Open questions:**
- [Things to revisit]

## Session 2 (YYYY-MM-DD)
...
```

The DEVLOG is append-only. Each session adds a new section. This becomes the "Methods" narrative for the paper.

---

### Phase 3: Execution

**Purpose:** Run the tests, generate data, record results.

**Depends on:** Phase 2

**Deliverable:**

```
experiments/exp_NNN_description/
└── results/
    ├── metrics.json           # Structured results
    ├── figures/               # Generated plots
    └── logs/                  # Execution logs (if needed)
```

**Exit gate:**

- [ ] `metrics.json` exists and parses
- [ ] Contains results for all predictions from spec
- [ ] Figures referenced in spec are generated
- [ ] **New in v1.1:** All claimed output files verified to exist (anti-hallucination check)

**Anti-hallucination verification:**

The Phase 3 exit gate includes automated file existence checks:

```python
# verify_execution.py
def verify_phase_3(experiment_id):
    spec = load_spec(experiment_id)
    results = load_results(experiment_id)
    
    # Check that every prediction has a result
    for prediction in spec['predictions']:
        if prediction['id'] not in results:
            raise HallucinationError(f"Prediction {prediction['id']} has no result")
    
    # Check that every claimed figure exists
    for figure in spec.get('expected_figures', []):
        path = f"experiments/{experiment_id}/results/figures/{figure}"
        if not os.path.exists(path):
            raise HallucinationError(f"Claimed figure {figure} does not exist")
    
    return True
```

**Metric structure:**

```json
{
  "experiment_id": "exp_005",
  "executed_at": "2026-01-28T15:30:00Z",
  "predictions": {
    "P1": {
      "claim": "Dual encoding survives 50% corruption",
      "threshold": 0.95,
      "measured": 0.00,
      "passed": false
    },
    "P2": { ... }
  },
  "measurements": {
    "similarity_mean": 0.9995,
    "similarity_std": 0.0003,
    ...
  }
}
```

---

### Phase 4: Verification

**Purpose:** Compare results to predictions. Separate PASS/FAIL/AMBIGUOUS.

**Depends on:** Phase 3

**Deliverable:**

```
experiments/exp_NNN_description/
├── claims.json                # Claims manifest (quantitative statements)
└── verification_gates.json    # Gate tracking with hashes
```

**Two-tier verification (from v1.0):**

**Tier 1: Machine verification**
- Quantitative claims checked against `metrics.json`
- Unit tests must pass
- Automated gate script (`verify_gates.py`) exits with code 1 on failure

**Tier 2: Visual inspection**
- Paper PDF layout
- Figure rendering quality
- Hash-tracked: rebuilding artifact invalidates previous inspection

**Exit gate:**

- [ ] All machine gates pass (`verify_gates.py` exits 0)
- [ ] Visual inspection gates tracked in `verification_gates.json`
- [ ] Each prediction categorized: PASS / FAIL / AMBIGUOUS
- [ ] **New in v1.1:** Cross-model consensus on ambiguous results (if available)

**Claims manifest structure:**

```json
{
  "claims": [
    {
      "id": "C1",
      "statement": "Mean similarity across all tests was 0.9995",
      "source_of_truth": "results/metrics.json::similarity_mean",
      "verification": "assert abs(claimed - actual) < 1e-6"
    },
    {
      "id": "C2",
      "statement": "Prediction P1 failed",
      "source_of_truth": "results/metrics.json::predictions.P1.passed",
      "verification": "assert actual == false"
    }
  ]
}
```

**New in v1.1: Cross-model verification for ambiguous cases:**

When a prediction result is AMBIGUOUS (close to threshold, noisy data, subjective interpretation):

```yaml
ambiguous_result:
  prediction: P3
  measured_value: 0.949
  threshold: 0.95
  margin: -0.001  # Just below threshold
  
  verification_strategy: cross_model_consensus
  models_used:
    - anthropic/claude-sonnet-4
    - local/deepseek-coder
    - local/mistral
  
  consensus:
    - model: claude-sonnet-4
      verdict: FAIL
      reasoning: "Value below threshold, measurement uncertainty insufficient to override"
    - model: deepseek-coder
      verdict: AMBIGUOUS
      reasoning: "Within measurement error margin, recommend additional trials"
    - model: mistral
      verdict: FAIL
      reasoning: "Threshold is hard boundary, no ambiguity"
  
  final_verdict: FAIL (2/3 agreement)
  confidence: 0.67
```

---

### Phase 5: Documentation

**Purpose:** Write the experiment as a scientific paper. Update FINDINGS.md.

**Depends on:** Phase 4

**Deliverable:**

```
experiments/exp_NNN_description/
├── paper/
│   ├── paper.tex
│   ├── paper.pdf
│   └── figures/ (symlink to ../results/figures/)
└── FINDINGS.md updates (in project root)
```

**Paper structure:**

```latex
\section{Introduction}
    % From spec.md: hypothesis and background

\section{Methods}
    % From DEVLOG.md: what was implemented and why

\section{Results}
    % From metrics.json: measured values, figures

\section{Discussion}
    % Interpretation: why did predictions pass/fail?
    % From FINDINGS.md: how does this connect to other experiments?

\section{Conclusion}
    % Updated hypothesis or new questions
```

**Exit gate:**

- [ ] Paper compiles to PDF without errors
- [ ] All claims in prose map to `claims.json` entries
- [ ] All figures referenced in paper exist
- [ ] FINDINGS.md updated with new findings (F-numbered)
- [ ] **New in v1.1:** Completeness audit passes (no missing sections, all predictions addressed)

**FINDINGS.md structure:**

```markdown
# Cross-Experiment Findings

## F27: P/1/P duality changes radial mapping but not spatial placement
**From:** Experiment 05, Prediction P1 failure
**Evidence:** Both P and 1/P copies occupy same raster-order rows
**Implication:** Top-half corruption kills both simultaneously
**Related findings:** F12 (dual encoding), F19 (radial addressing)

## F28: ...
```

Each finding gets a number. Papers reference findings by number. FINDINGS.md is the persistent knowledge graph across experiments.

---

### Phase 6: Commit

**Purpose:** Final audit and version control checkpoint.

**Depends on:** Phase 5

**Actions:**

1. Run completeness checklist (Section 4.7)
2. Run all verification gates
3. **New in v1.1:** Run recursive phase audit (verify all prior phase deliverables)
4. Git commit with structured message
5. **New in v1.1:** Trigger lineage re-verification if this experiment has dependencies

**Exit gate:**

- [ ] Completeness checklist: 100%
- [ ] All verification gates: PASS
- [ ] **New in v1.1:** Recursive audit: CLEAN
- [ ] **New in v1.1:** Lineage re-verification: PASS (if applicable)
- [ ] Git commit message follows template

**Commit message template:**

```
Exp NNN: [Short description]

Hypothesis: [One-sentence claim from spec]
Predictions: N passed, M failed, K ambiguous
Key findings: F##, F##, F##

Files modified:
- [List of new/changed files]

Completeness: 100%
Verification: ALL GATES PASS
Recursive audit: CLEAN
```

**New in v1.1: Recursive audit output:**

```
=== Phase Completion Audit: Experiment 007 ===

Phase 0 (Specification):
  Deliverable: experiments/exp_007/spec.md
  Stored hash:  sha256:a1b2c3d4...
  Current hash: sha256:a1b2c3d4...
  Status: ✓ CLEAN

Phase 1 (Implementation):
  Deliverable: experiments/exp_007/src/bin/workbench_007.rs
  Stored hash:  sha256:e5f6g7h8...
  Current hash: sha256:e5f6g7h8...
  Status: ✓ CLEAN

[... all phases checked ...]

Phase 5 (Documentation):
  Deliverable: experiments/exp_007/paper/paper.pdf
  Stored hash:  sha256:i9j0k1l2...
  Current hash: sha256:i9j0k1l2...
  Status: ✓ CLEAN

=== RECURSIVE AUDIT RESULT: CLEAN ===
Safe to proceed with commit.
```

If contamination detected:

```
=== Phase Completion Audit: Experiment 007 ===

Phase 3 (Execution):
  Deliverable: experiments/exp_007/results/metrics.json
  Stored hash:  sha256:m3n4o5p6...
  Current hash: sha256:q7r8s9t0...
  Status: ✗ CONTAMINATION DETECTED

File was modified after phase completion.
Last modification: 2026-02-01 14:23:15
Audit timestamp:   2026-02-01 15:30:00

=== RECURSIVE AUDIT RESULT: CONTAMINATED ===
HALT: Cannot proceed to commit.

Options:
  1. Rollback to Phase 3 and re-execute
  2. Accept modification and update hash (requires justification)
  3. Investigate: git diff to see what changed
```

### 4.7 Experiment Completeness Checklist

**Purpose:** Ensure the experiment is a complete research artifact, not just working code.

**When:** Before final commit (Phase 6)

**Checklist:**

```
Experiment NNN Completeness Audit

Specification:
[ ] spec.md exists
[ ] Contains hypothesis
[ ] Contains ≥1 falsifiable prediction with threshold
[ ] Defines controls

Implementation:
[ ] Workbench binary exists and compiles
[ ] New module added via composition (no modifications to existing code)
[ ] Unit tests exist and pass

Execution:
[ ] results/metrics.json exists and parses
[ ] Contains results for all predictions

Verification:
[ ] claims.json manifest complete
[ ] All machine gates pass
[ ] verification_gates.json tracks inspection gates

Documentation:
[ ] DEVLOG.md documents all sessions
[ ] paper/paper.tex compiles to paper.pdf
[ ] Paper addresses all predictions
[ ] FINDINGS.md updated with new F-numbered findings

Version Control:
[ ] All files git-tracked
[ ] Commit message follows template

NEW IN V1.1:
[ ] Recursive phase audit: CLEAN
[ ] Lineage re-verification: PASS (if applicable)
[ ] Process hallucination check: CLEAN (all claimed files exist)

Completeness: [X / Y]  (must be 100%)
```

**Common audit failures:**

- Paper exists but figures not committed (git-tracked check fails)
- Claims.json incomplete (references metrics not in metrics.json)
- DEVLOG empty or stub (documentation incomplete)
- Verification gates not run (verification_gates.json missing or outdated hashes)

**Fix:** The checklist is executable. The completion percentage is computed, not self-reported.

```python
# verify_completeness.py
def compute_completeness(experiment_id):
    checks = {
        'spec_exists': os.path.exists(f'experiments/{experiment_id}/spec.md'),
        'metrics_exist': os.path.exists(f'experiments/{experiment_id}/results/metrics.json'),
        'paper_compiles': compile_latex(experiment_id),
        'claims_complete': verify_claims(experiment_id),
        'gates_pass': run_verification_gates(experiment_id),
        # ... all checklist items as functions
    }
    
    passed = sum(checks.values())
    total = len(checks)
    
    return passed / total
```

The script exits with code 1 if completeness < 1.0, blocking the commit.

---

## 5. Capstone Phases (Project-Level)

These phases execute once, after all experiments in a project are complete.

### Phase 7: Red Team Review

**Purpose:** External adversarial critique of the entire body of work.

**Depends on:** All experiments complete

**Deliverable:**

```
capstone/
└── red_team_report.md
```

**Process:**

1. Provide red team reviewer with:
   - All experiment papers
   - Raw data (metrics.json, figures)
   - FINDINGS.md
   - Git history (for provenance)

2. Reviewer has no prior exposure to the research process. Fresh perspective.

3. Reviewer identifies:
   - Methodological weaknesses
   - Alternative explanations for results
   - Missing tests or controls
   - Internal inconsistencies
   - What was done well (honest review includes strengths)

**Report structure:**

```markdown
# Red Team Review

## Methodological Critique
- [Issue 1: description, severity, evidence from data]
- [Issue 2: ...]

## Alternative Explanations
- [Claim from papers: alternative interpretation]
- [Distinguishing test: what would differentiate between explanations]

## Missing Elements
- [What should have been tested/controlled/documented]

## Internal Consistency Check
- [Contradictions between data and claims, if any]

## Strengths
- [What the research did well]

## Overall Assessment
[Narrative summary]
```

**Exit gate:**

- [ ] Critique is comprehensive (addresses all experiments)
- [ ] Evidence-based (references specific data, not vague concerns)
- [ ] Honest (includes both strengths and weaknesses)

---

### Phase 8: Meta-Analysis

**Purpose:** Evaluate the red team critique AND audit the process itself.

**Depends on:** Phase 7

**Deliverable:**

```
capstone/
└── meta_analysis.md
```

**Dual audit structure:**

**Part A: Evaluate the Red Team Critique**

- For each critique point: valid, invalid, or partially valid?
- Does the critique contain its own blind spots or overreach?
- What did the opposition miss or misrepresent?

**Part B: Audit the Process**

- Were all phases actually completed as specified?
- Were deliverables generated or hallucinated/skipped?
- Did bias enter anywhere? Where?
- Did the protocol structure help or hinder?
- **New in v1.1:** Did recursive verification catch contamination? Were there false positives?
- What would we change about the protocol itself?

**Part C: Synthesis**

- Which red team points require paper revision?
- Which are acknowledged limitations vs. fatal flaws?
- What protocol improvements feed forward to future projects?
- **New in v1.1:** What system configuration changes are supported by evidence?

**Report structure:**

```markdown
# Meta-Analysis

## Red Team Evaluation

### Valid Critiques
- [Critique ID: reasoning for validity, required action]

### Invalid Critiques
- [Critique ID: reasoning for invalidity, red team's blind spot]

### Partial Critiques
- [Critique ID: what's valid, what's not, resolution]

## Process Audit

### Phase Completion Verification
- [Phase N: completed [yes/no], notes if issues]

### Bias Check
- [Potential bias: source, severity, mitigation]

### Hallucination Check
- [Artifact: verified [yes/no], method]

### Protocol Effectiveness
- [What worked well, what didn't, evidence]

## Synthesis

### Fatal Flaws Found
[Yes/No - if yes, return to which phase]

### Acknowledged Limitations
- [Limitation 1: accepted, documented]
- [Limitation 2: ...]

### Recommended Protocol Changes
- [Change 1: issue it addresses, proposed fix]
- [Change 2: ...]

### Final Hypothesis Status
[CONFIRMED / REFUTED / REFINED / INCONCLUSIVE]

### Confidence Update
Prior: [from experiments]
Posterior: [after meta-analysis]
Reasoning: [what changed and why]
```

**Exit gate:**

- [ ] Every red team point addressed
- [ ] Process audit complete with no unexamined phases
- [ ] Honest assessment of whether findings survive scrutiny
- [ ] **New in v1.1:** System metrics reviewed, configuration changes proposed with justification

---

### Phase 9: Decision

**Purpose:** Explicit decision on next steps and archival.

**Depends on:** Phase 8

**Deliverable:**

```
capstone/
└── decision.md
```

**Decision options:**

- **STOP:** Research complete, no follow-up planned
- **ITERATE:** Repeat with refined hypothesis
- **BRANCH:** New project with new hypothesis

**Report structure:**

```markdown
# Decision

## Hypothesis Resolution
[Is the hypothesis resolved? What new hypotheses emerged?]

## Laboratory Disposition
[Preserve / Discard / Modify infrastructure]

## Artifact Archive
- [File/directory: keep [yes/no], reason]

## Decision
[STOP / ITERATE / BRANCH]

## Next Action
[If not STOP, what specifically happens next]

## Protocol Updates Adopted
- [Improvement from Phase 8: adopted [yes/no], reasoning]

## Reflections
[What worked well? What didn't? What would you change?]
```

**Exit gate:**

- [ ] Explicit decision recorded
- [ ] No open loops
- [ ] Archive plan specified

---

## 6. Meta-Protocol: System Self-Optimization

*New in v1.1.*

The protocol enforcement system itself is subject to experimental verification. Configuration decisions are hypotheses tested through meta-experiments.

### 6.1 Principle

**The system optimizes through experimentation, not speculation.**

Questions like "should we use checkpoint-based or full-cascade auditing?" are not decided theoretically. They are tested:

1. State the hypothesis with falsifiable criteria
2. Run experiments under each configuration
3. Measure efficiency and correctness
4. Adopt the configuration supported by evidence

### 6.2 System Metrics

The protocol enforcement system tracks:

```yaml
system_metrics:
  efficiency:
    - phase_completion_time  # How long each phase takes
    - audit_overhead_ratio   # Time spent auditing vs. progressing
    - false_positive_rate    # Audits that found no contamination
    
  correctness:
    - contamination_detection_rate  # True positives
    - hallucination_catch_rate      # Process hallucinations caught
    - downstream_invalidation_count # Lineage contamination cascades
    
  configuration:
    - audit_strategy  # full_cascade, checkpoint, dependency_aware
    - verification_threshold  # Cross-model consensus threshold
    - model_allocation  # Which models for which capabilities
```

### 6.3 Meta-Experiment Example

**Hypothesis:** "Checkpoint-based auditing with dependency-aware triggers provides adequate contamination detection (≥95%) with less overhead (<40% of full cascade time)."

**Test design:**

```yaml
configurations:
  baseline:
    name: "Full cascade auditing"
    strategy: verify_all_prior_phases_on_every_completion
    
  variant_1:
    name: "Checkpoint-based"
    strategy: verify_at_phase_milestones_only  # Phases 3, 6
    
  variant_2:
    name: "Dependency-aware"
    strategy: verify_only_dependent_phases

contamination_test_cases:
  - inject_modified_deliverable  # Modify Phase 2 file after completion
  - inject_missing_artifact      # Delete claimed output file
  - inject_hash_mismatch         # Corrupt metrics.json
  - inject_lineage_invalidation  # Modify ancestor experiment

measurements:
  - detection_rate: [contaminations caught / contaminations injected]
  - overhead_time: [audit time / total experiment time]
  - false_positive_rate: [audits that flagged clean phases]

success_criteria:
  - detection_rate >= 0.95
  - overhead_time < 0.40 * baseline_overhead
```

**Execution:**

Run 10 experiments under each configuration. Inject 5 contamination cases per experiment (50 total contaminations). Measure detection and overhead.

**Verification:**

```python
def verify_meta_experiment():
    results = load_meta_results()
    
    for config in results['configurations']:
        assert config['detection_rate'] >= 0.95, \
            f"{config['name']} caught only {config['detection_rate']*100}% of contaminations"
        
        if config['name'] != 'baseline':
            assert config['overhead_time'] < 0.40 * results['baseline']['overhead_time'], \
                f"{config['name']} overhead too high"
```

**Documentation:**

Meta-experiment results are documented in `meta_experiments/` directory with the same structure as regular experiments (spec, results, paper).

**Decision:**

If variant passes verification: Update system configuration. If fails: Keep current configuration or design new variant.

### 6.4 Configuration as Code

System configuration is versioned in `config/protocol_config.yaml`:

```yaml
# Protocol Configuration v1.1.0

audit_strategy:
  type: "checkpoint_based"  # full_cascade | checkpoint_based | dependency_aware
  checkpoints: [3, 6]  # Phase numbers where full audit runs
  justification: "Meta-Experiment M001: 96% detection, 35% overhead"
  evidence_file: "meta_experiments/exp_M001_audit_strategies/paper/paper.pdf"

verification:
  consensus_threshold: 0.67  # 2/3 models must agree
  ambiguous_margin: 0.05     # Results within 5% of threshold are ambiguous
  models_for_consensus:
    - "anthropic/claude-sonnet-4"
    - "local/deepseek-coder"
    - "local/mistral"

contamination_response:
  auto_rollback_threshold: 0.95  # Auto-rollback if confidence > 95%
  require_human_review: true     # Always require human confirmation

lineage_verification:
  frequency: "per_experiment"    # per_experiment | every_5_experiments | manual
  depth: "full_transitive"       # full_transitive | immediate_only
```

Each configuration value includes:
- Current setting
- Justification (from which meta-experiment)
- Evidence file (paper documenting the test)

### 6.5 System Self-Audit

The system audits its own performance:

```python
# system_audit.py

def audit_system_performance(time_window_days=30):
    """
    Analyze system performance over last N days.
    Generate report on efficiency and correctness.
    Identify potential improvements.
    """
    
    experiments = load_experiments_in_window(time_window_days)
    
    metrics = {
        'experiments_completed': len(experiments),
        'contaminations_detected': count_contaminations(experiments),
        'false_positives': count_false_positives(experiments),
        'average_overhead': compute_average_overhead(experiments),
        'hallucinations_caught': count_hallucinations(experiments),
    }
    
    # Identify anomalies
    if metrics['false_positives'] > metrics['contaminations_detected']:
        flag_issue("High false positive rate - audit strategy too aggressive")
    
    if metrics['hallucinations_caught'] == 0 and len(experiments) > 10:
        flag_issue("No hallucinations caught - verification may be insufficient")
    
    # Generate recommendations
    recommendations = []
    
    if metrics['average_overhead'] > 0.50:
        recommendations.append({
            'issue': 'High audit overhead',
            'proposed_change': 'Test checkpoint-based strategy',
            'meta_experiment': 'Design M002: Compare current vs. checkpoint'
        })
    
    return {
        'metrics': metrics,
        'recommendations': recommendations,
        'audit_timestamp': datetime.now()
    }
```

This audit runs monthly and generates a report in `system_audits/YYYY-MM.md`.

### 6.6 Improvement Cycle

```
System runs experiments for N weeks
    ↓
Monthly self-audit identifies potential inefficiency
    ↓
Design meta-experiment to test alternative configuration
    ↓
Run meta-experiment with falsifiable criteria
    ↓
If alternative passes: Update config with evidence link
If alternative fails: Keep current config, document why
    ↓
Repeat
```

This creates a feedback loop where the system improves its own infrastructure through the same scientific method it applies to domain experiments.

---

## 7. Verification Infrastructure

### 7.1 Claims Verification

**Purpose:** Catch quantitative errors in prose through machine verification.

**Implementation:**

```
project/
├── experiments/exp_NNN/claims.json
└── tools/verify_claims.py
```

**Claims manifest structure:**

```json
{
  "experiment_id": "exp_005",
  "claims": [
    {
      "id": "C1",
      "statement": "Mean similarity across all 15 tests was 0.9995 ± 0.0003",
      "source_of_truth": "results/metrics.json::similarity_mean",
      "verification": "assert abs(0.9995 - actual) < 1e-6",
      "location": "paper.tex:line_142"
    },
    {
      "id": "C2",
      "statement": "Prediction P1 failed with measured value 0.00",
      "source_of_truth": "results/metrics.json::predictions.P1.measured",
      "verification": "assert actual == 0.00",
      "location": "paper.tex:line_198"
    }
  ]
}
```

**Verification script:**

```python
#!/usr/bin/env python3
# tools/verify_claims.py

import json
import sys

def verify_claims(experiment_id):
    claims = json.load(open(f'experiments/{experiment_id}/claims.json'))
    metrics = json.load(open(f'experiments/{experiment_id}/results/metrics.json'))
    
    failures = []
    
    for claim in claims['claims']:
        source = claim['source_of_truth']
        verification = claim['verification']
        
        # Extract actual value from metrics
        actual = extract_value(metrics, source)
        
        # Run verification assertion
        try:
            exec(verification, {'actual': actual})
        except AssertionError:
            failures.append({
                'claim_id': claim['id'],
                'statement': claim['statement'],
                'expected_verification': verification,
                'actual_value': actual
            })
    
    if failures:
        print("CLAIM VERIFICATION FAILED:")
        for f in failures:
            print(f"  {f['claim_id']}: {f['statement']}")
            print(f"    Actual value: {f['actual_value']}")
        sys.exit(1)
    
    print(f"All {len(claims['claims'])} claims verified successfully")
    sys.exit(0)

if __name__ == '__main__':
    verify_claims(sys.argv[1])
```

**Integration:** Called during Phase 6 (Commit). Part of the completeness checklist.

**Evidence:** See Section 10.3 (Claims Verification Protocol).

### 7.2 Verification Gates

**Purpose:** Track inspection obligations that cannot be fully automated.

**Implementation:**

```
project/
├── experiments/exp_NNN/verification_gates.json
└── tools/verify_gates.py
```

**Gate manifest structure:**

```json
{
  "experiment_id": "exp_005",
  "gates": [
    {
      "id": "G1",
      "type": "machine",
      "description": "All unit tests pass",
      "command": "cargo test --bin workbench_005",
      "status": "PASS",
      "last_run": "2026-01-28T14:30:00Z"
    },
    {
      "id": "G2",
      "type": "machine",
      "description": "Claims verification",
      "command": "python3 tools/verify_claims.py exp_005",
      "status": "PASS",
      "last_run": "2026-01-28T15:00:00Z"
    },
    {
      "id": "G3",
      "type": "inspection",
      "description": "Paper PDF layout check",
      "artifact": "experiments/exp_005/paper/paper.pdf",
      "artifact_hash": "sha256:a1b2c3d4...",
      "status": "INSPECTED",
      "last_inspected": "2026-01-28T15:15:00Z",
      "notes": "No overflow, figures render correctly"
    }
  ]
}
```

**Two-tier design:**

**Tier 1 (machine):** Automated gates that run via shell command. Exit code 0 = pass, non-zero = fail.

**Tier 2 (inspection):** Hash-tracked manual review. Rebuilding the artifact changes the hash, invalidating the previous inspection and requiring re-review.

**Verification script:**

```python
#!/usr/bin/env python3
# tools/verify_gates.py

import json
import subprocess
import hashlib
import sys

def verify_gates(experiment_id):
    gates = json.load(open(f'experiments/{experiment_id}/verification_gates.json'))
    
    failures = []
    
    for gate in gates['gates']:
        if gate['type'] == 'machine':
            # Run automated gate
            result = subprocess.run(gate['command'], shell=True)
            if result.returncode != 0:
                failures.append(f"Machine gate {gate['id']} failed: {gate['description']}")
        
        elif gate['type'] == 'inspection':
            # Check if artifact hash matches
            artifact_path = gate['artifact']
            current_hash = compute_hash(artifact_path)
            
            if current_hash != gate['artifact_hash']:
                failures.append(
                    f"Inspection gate {gate['id']} invalidated: "
                    f"artifact {artifact_path} was rebuilt but not re-inspected"
                )
    
    if failures:
        print("GATE VERIFICATION FAILED:")
        for f in failures:
            print(f"  {f}")
        sys.exit(1)
    
    print(f"All {len(gates['gates'])} gates passed")
    sys.exit(0)

def compute_hash(filepath):
    with open(filepath, 'rb') as f:
        return 'sha256:' + hashlib.sha256(f.read()).hexdigest()

if __name__ == '__main__':
    verify_gates(sys.argv[1])
```

**Hash-based invalidation workflow:**

1. Paper PDF inspected, hash recorded in `verification_gates.json`
2. Figure regenerated (e.g., after data correction)
3. Paper rebuilt → new PDF → hash changes
4. `verify_gates.py` detects hash mismatch → gate FAILS
5. Human re-inspects PDF, updates hash if inspection passes

This enforces the inspection obligation structurally, not through memory.

**Evidence:** See Section 10.4 (Two-Tier Verification Gates).

### 7.3 AI Vision Inspection

**Purpose:** Automated detection of visual artifacts in generated PDFs and figures.

**Implementation:**

AI vision (via API or local multimodal model) inspects paper PDF and figures for:
- Character corruption (backslash artifacts: `\%`, `vs.\`)
- Text clipping (annotations cut off by chart boundaries)
- Table overflow (text extending beyond column width)
- Figure rendering errors

**Capabilities (from v1.0 evidence):**

- **High reliability:** Character-level corruption (unambiguous errors)
- **Lower reliability:** Layout violations requiring understanding of intended structure

**Recommended use:**

- AI vision as **second tier** after programmatic guards
- Programmatic layout guards (e.g., `ylim` headroom, table width checks) as **first tier**
- Vision inspection catches what programmatic guards miss

**Evidence:** See Section 10.8 (AI Vision Capabilities and Limits).

**New in v1.1: Vision-based verification for process hallucinations:**

Vision inspection can also verify that claimed UI states or visual outputs actually occurred:

```python
def verify_visual_claim(claim, screenshot_path):
    """
    Use vision model to verify a claim about visual state.
    
    Example claim: "The workbench UI displayed 'Test P1: FAIL' in red text"
    """
    
    prompt = f"""
    You are verifying a claim about what appears in this screenshot.
    
    Claim: {claim}
    
    Does the screenshot support this claim?
    Respond with:
    - VERIFIED: Claim is clearly supported by visual evidence
    - REFUTED: Visual evidence contradicts the claim
    - AMBIGUOUS: Cannot determine from visual evidence
    
    Include specific details from the screenshot.
    """
    
    response = vision_model.analyze(screenshot_path, prompt)
    
    return {
        'claim': claim,
        'screenshot': screenshot_path,
        'verdict': response.verdict,  # VERIFIED | REFUTED | AMBIGUOUS
        'evidence': response.details
    }
```

---

## 8. Model-Agnostic Collaboration Infrastructure

*New in v1.1.*

The protocol is designed to work with any model that implements the required interface. Local and API-based models are interchangeable.

### 8.1 Model Provider Interface

All models interact through a standardized interface:

```rust
#[async_trait]
pub trait ModelProvider {
    /// Read current phase state and provenance context
    async fn read_phase(&self, exp_id: &str, phase: u8) -> Result<PhaseState>;
    
    /// Propose next action given current state
    async fn propose_action(&self, state: SystemState) -> Result<ActionProposal>;
    
    /// Execute action with full provenance tracking
    async fn execute(&self, action: Action) -> Result<ProvenanceEntry>;
    
    /// Verify output against control
    async fn verify(&self, test: Test, control: Control) -> Result<Verification>;
    
    /// Provide critique (red team function)
    async fn critique(&self, deliverables: Vec<Deliverable>) -> Result<Critique>;
}
```

### 8.2 Model Registry

Different models specialize in different capabilities:

```yaml
# config/model_registry.yaml

models:
  planning:
    provider: "anthropic/claude-opus-4"
    role: "Decompose hypothesis into tests, design experiments"
    
  execution:
    provider: "local/deepseek-coder"
    role: "Write code, run tests, generate data"
    
  verification:
    provider: "local/llava"
    role: "Visual inspection of PDFs and figures"
    
  critique:
    provider: "anthropic/claude-sonnet-4"
    role: "Red team review, find methodological weaknesses"
    
  synthesis:
    provider: "anthropic/claude-sonnet-4"
    role: "Meta-analysis, integrate feedback"
```

The system routes tasks to appropriate models based on capability requirements. Models are swapped without changing the protocol.

### 8.3 Local-First Data Architecture

All experiment data stored locally:

```
project_root/
├── experiments/          # Experiment artifacts
├── .git/                 # Version control (provenance)
├── meta-ide.db          # Local SQLite/SurrealDB
├── config/               # System configuration
└── meta_experiments/     # System self-optimization experiments
```

**No cloud dependencies.** Models access local filesystem and database. API keys (if using API models) stored in environment variables, never committed.

### 8.4 Cross-Model Verification

For ambiguous results, multiple models verify independently:

```rust
pub async fn verify_with_consensus(
    test_output: &Path,
    control: &Path,
    dimension: VerificationDimension,
    models: &[Box<dyn ModelProvider>],
    threshold: f32,
) -> Result<ConsensusVerification> {
    
    let mut verifications = Vec::new();
    
    for model in models {
        let verification = model.verify(
            test_output.into(),
            control.into(),
            dimension.clone()
        ).await?;
        
        verifications.push(verification);
    }
    
    // Calculate agreement
    let pass_count = verifications.iter()
        .filter(|v| v.status == VerificationStatus::Pass)
        .count();
    
    let agreement = pass_count as f32 / verifications.len() as f32;
    
    if agreement < threshold && agreement > (1.0 - threshold) {
        // No clear consensus
        return Ok(ConsensusVerification::Ambiguous {
            individual_results: verifications,
            agreement_ratio: agreement,
        });
    }
    
    let consensus_status = if agreement >= threshold {
        VerificationStatus::Pass
    } else {
        VerificationStatus::Fail
    };
    
    Ok(ConsensusVerification::Agreed {
        status: consensus_status,
        confidence: agreement,
        models_used: models.iter().map(|m| m.name()).collect(),
    })
}
```

**Evidence requirement:** Cross-model verification is itself subject to meta-experimentation. The consensus threshold (currently 0.67) will be validated through meta-experiments comparing single-model vs. multi-model error rates.

---

## 9. Human-AI Collaboration Model

### 9.1 Role Division

**Human:**
- Direction: What to investigate, which hypotheses to test
- Audit: Verify completeness, catch errors the AI misses
- Judgment: Interpret ambiguous results, make final decisions
- Infrastructure: Design verification gates, write checkers

**AI:**
- Implementation: Write code, generate figures, format papers
- Execution: Run tests, collect data, compute metrics
- Analysis: Identify patterns, propose explanations
- Documentation: Convert DEVLOG to paper Methods section

### 9.2 The Key Asymmetry

**From v1.0 evidence (Section 10.7):**

The AI executes efficiently but does not spontaneously audit against external standards. The human audit function is irreplaceable.

**Examples:**

- AI wrote experiment code that passed all tests → Human audited completeness and found documentation 2% complete
- AI generated paper with correct data → Human visual inspection caught table overflow
- AI claimed to verify figures → Human spot-check found text clipping

**Implication:** Trust but verify. The AI is a powerful executor, not an autonomous agent. The human must audit.

**New in v1.1:** Process hallucination detection addresses this asymmetry by making AI claims falsifiable through automated verification.

### 9.3 Context Loss and Infrastructure Resilience

**Problem (from v1.0):**

Obligations that exist only in conversation context are forgotten after compaction or session restart.

**Solution:**

Encode obligations in files, not memory:
- Verification gates tracked in `verification_gates.json`
- Completeness checklist is executable code
- Claims verification is automated
- Exit gates are code, not prose

**Principle:** Machine verification must be context-immune. Anything that depends on someone remembering will eventually be forgotten.

**New in v1.1:** Provenance database provides permanent record of all actions. Even if conversation context is lost, the database shows what happened and when.

---

## 10. Case Study Evidence (v1.0)

[... existing sections 10.1 through 10.9 unchanged ...]

---

## 11. Appendix: What Changed from v1.0

### New Sections

- **Section 1.7:** Principle of Recursive Verification and Contamination Detection
- **Section 2.4:** Meta-Protocol architecture level
- **Section 3.3:** Recursive verification on phase completion
- **Section 3.4:** Experiment lineage re-verification
- **Section 4 (Phase 3, 4, 6):** Anti-hallucination checks in exit gates
- **Section 6:** Meta-Protocol: System Self-Optimization (entire section)
- **Section 8:** Model-Agnostic Collaboration Infrastructure (entire section)

### Updated Sections

- **Section 2.1:** Added provenance database, model adapter layer, audit system
- **Section 2.2:** Added recursive audit requirement
- **Section 4.7:** Added recursive audit and lineage re-verification to completeness checklist
- **Section 7.3:** Added vision-based process hallucination verification

### New Concepts

- **Contamination detection:** Hash-based verification that deliverables haven't been modified after phase completion
- **Lineage re-verification:** Re-verify ancestor experiments when completing dependent experiments
- **Process hallucination:** Claimed actions that didn't occur, verified through file existence checks and provenance coherence
- **Cross-model consensus:** Multiple models verify ambiguous results independently
- **Meta-experiments:** Testing system configuration through falsifiable experiments
- **System self-audit:** Monthly performance analysis with improvement recommendations

### Implementation Status

**v1.0 features:** Battle-tested through 5 experiments (Distortion Data project, January 2026)

**v1.1 features:** Designed based on v1.0 experience but not yet tested in practice. Recursive verification, lineage tracking, and meta-protocol are architecturally sound but unvalidated.

**Next step:** Implement v1.1 features in Meta-IDE system and validate through real experiments.

---

## Document Metadata

**Version:** 1.1  
**Status:** Implementation ready (recursive verification layer untested)  
**Created:** 2026-02-01  
**Authors:** Claude + Hedawn  
**Case study:** Distortion Data Experiment, 6 experiments, January 2026  
**License:** Open for modification and use  
**Changelog:** Added recursive verification, contamination detection, process hallucination prevention, meta-protocol for system self-optimization, and model-agnostic collaboration infrastructure
