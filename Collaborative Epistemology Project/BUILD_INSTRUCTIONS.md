# BUILD INSTRUCTIONS: Collaborative Epistemology Research Infrastructure
**For:** Claude CLI Autonomous Agent  
**Purpose:** Complete project setup from foundation paper  
**Execution Time:** 2-4 hours autonomous work

**CRITICAL CONTEXT:** The foundation paper (main_paper.md) now includes a major theoretical contribution connecting AI hallucination to psychedelic cognition via Huxley's "reducing valve" theory. This parallel is central to understanding why hallucination is intrinsic (not fixable) and why constitutional constraints function as "set and setting." Read Section 2.4 carefully.

---

## PHASE 0: SETUP - Create Full Directory Structure

### Command to Execute:

```bash
mkdir -p collaborative_epistemology_project/{papers/{confidence_accuracy,efficiency_critique,documentation_layer,constitutional_constraints},experiments/{cross_domain_hallucination,collaborative_vs_solo,energy_efficiency,constitutional_effectiveness}/{data,analysis,code,results},agent_swarm/{architecture,proof_of_concept,evaluation,documentation},documentation/{process_notes,decisions,dead_ends,phase_reviews,literature_notes},data/{experimental_results,collected_papers,benchmarks,measurements},resources/{templates,scripts,datasets}}
```

### Verify:
```bash
tree -L 3 collaborative_epistemology_project/
```

---

## PHASE 1: LITERATURE COLLECTION - Find and Store Source Papers

### Papers to Find (use web search, download PDFs if available, or save citations):

**Hallucination Research:**
1. Ji et al. (2023) - "Survey of hallucination in natural language generation"
2. Zhang et al. (2023) - "Siren's song in the AI ocean: A survey on hallucination"
3. Lewis et al. (2020) - "Retrieval-augmented generation for knowledge-intensive NLP"
4. Gao et al. (2023) - "RARR: Researching and revising what language models say"

**Calibration & Confidence:**
5. Kadavath et al. (2022) - "Language models (mostly) know what they know"

**Psychedelic & Consciousness Research:**
6. Huxley, A. (1954) - "The doors of perception" [CRITICAL - theoretical foundation for psychedelic parallel]
7. Leary, T., Metzner, R., & Alpert, R. (1963) - "The psychedelic experience"
8. Carhart-Harris et al. (2014) - "The entropic brain: a theory of conscious states"
9. Pollan, M. (2018) - "How to change your mind" [popular synthesis]

**Energy & Efficiency:**
10. Patterson et al. (2021) - "Carbon emissions and large neural network training"
11. Strubell et al. (2019) - "Energy and policy considerations for deep learning"
12. Raichle & Gusnard (2002) - "Appraising the brain's energy budget"

**Brain & Cognition:**
9. Kandel et al. (2013) - "Principles of neural science" (reference, not download)
10. Friston (2010) - "The free-energy principle"
11. Clark (1998) - "Being there: Putting brain, body, and world together again"
12. Varela et al. (1991) - "The embodied mind"

**Human-AI Interaction:**
13. Zamfirescu-Pereira et al. (2023) - "Why Johnny can't prompt"
14. White et al. (2023) - "A prompt pattern catalog"
15. Noy & Zhang (2023) - "Experimental evidence on productivity effects of generative AI"

**Memory & Learning:**
16. Cowan (2001) - "The magical number 4 in short-term memory"
17. Baddeley (2003) - "Working memory: Looking back and looking forward"
18. Xu & Tenenbaum (2007) - "Word learning as Bayesian inference"

### Storage Instructions:

For each paper:
1. Search for paper title + authors
2. If PDF available: Download to `/data/collected_papers/[author_year].pdf`
3. If not: Create citation file `/data/collected_papers/[author_year]_citation.txt` with:
   - Full citation
   - DOI/URL
   - Abstract
   - Key findings relevant to our work

4. Create index: `/data/collected_papers/INDEX.md` listing all papers with:
   - Citation
   - Relevance to project
   - Key quotes/findings
   - Which sections of main paper cite this

---

## PHASE 2: EXPERIMENT PROTOCOLS - Expand All Four

### For EACH experiment (1-4), create these files:

**In `/experiments/[experiment_name]/`:**

1. **`protocol_detailed.md`** - Complete experimental design
   - Full methodology (can be implemented immediately)
   - Specific datasets/benchmarks to use
   - Exact evaluation metrics with formulas
   - Statistical tests to run
   - Resource requirements with cost estimates
   - Timeline with milestones

2. **`code/requirements.txt`** - Python dependencies needed

3. **`code/data_collection.py`** - Stub for data collection script with:
   - API integrations outlined
   - Data structures defined
   - Error handling planned
   - Comments explaining each section

4. **`code/analysis.py`** - Stub for analysis script with:
   - Statistical tests specified
   - Visualization code outlined
   - Reporting structure

5. **`data/README.md`** - Description of data format and storage

6. **`results/expected_results.md`** - What we predict will happen

### Specific Instructions Per Experiment:

**Experiment 1 (Cross-Domain Hallucination):**
- Find existing cross-domain question datasets (e.g., from TruthfulQA, BigBench)
- Specify exactly which models to test (with API endpoints)
- Define ground truth validation process
- Create example questions in `/data/sample_questions.json`

**Experiment 2 (Collaborative vs Solo):**
- Define 10 example problems in `/data/sample_problems.json`
- Specify expert evaluation rubric
- Create comparison matrix template
- Outline pilot study design

**Experiment 3 (Energy Efficiency):**
- Research existing energy measurement tools
- Specify training setup (model size, dataset, compute)
- Define energy-aware loss function mathematically
- List hardware requirements

**Experiment 4 (Constitutional Effectiveness):**
- Write out all 5 constitutional frameworks in full
- Create 20 example test questions (4 per category)
- Define scoring rubric for appropriateness
- Specify A/B testing methodology

---

## PHASE 3: SPECIALIZED PAPERS - Create Detailed Outlines

### For EACH paper (A-D), create:

**In `/papers/[paper_name]/`:**

1. **`outline_detailed.md`** - Section-by-section structure:
   - Every section heading with 2-3 bullet points of content
   - Key arguments to make
   - Figures/tables needed
   - Citations required (specific papers)
   - Target journal/venue

2. **`related_work.md`** - Literature review notes:
   - Papers to cite in each section
   - How they relate to our work
   - Gaps they leave that we fill

3. **`figures_needed.md`** - List of visualizations:
   - Description of each figure
   - Data required
   - Design specifications

4. **`abstract_draft.md`** - First attempt at abstract

5. **`target_venues.md`** - Where to submit:
   - Primary target
   - Backup options
   - Submission requirements

### Specific Instructions Per Paper:

**Paper A (Confidence-Accuracy Divergence):**
- Technical paper for NeurIPS/ICML/ICLR
- Heavy on experimental results
- Mathematical formalization of divergence
- **Psychedelic parallel as theoretical framework** (Section 2.4 provides foundation)
- Focus on deployment implications
- Argue hallucination is intrinsic, not fixable

**Paper B (Efficiency Critique):**
- Position paper for AI policy venues
- Brain comparison central
- Environmental angle
- Alternative research directions

**Paper C (Documentation Layer):**
- HCI/CHI venue
- Practical methodology paper
- Case studies of use
- Tool development

**Paper D (Constitutional Constraints):**
- AI safety/alignment venue
- User-configurable alignment
- Comparison to company-defined constitutional AI
- Democratization angle

---

## PHASE 4: AGENT SWARM ARCHITECTURE - Technical Specification

**In `/agent_swarm/architecture/`:**

1. **`system_design.md`** - Complete architecture:
   - All 7 layers specified
   - Agent types per layer with capabilities
   - Communication protocols
   - Data flow diagrams
   - Orchestrator design
   - Feedback loop mechanisms

2. **`layer_[1-7]_spec.md`** - Detailed spec per layer:
   - Agent types and responsibilities
   - Input/output formats
   - Decision-making logic
   - Error handling
   - Success criteria

3. **`communication_protocol.md`** - How layers talk:
   - Message formats
   - Routing rules
   - Conflict resolution
   - Synchronization

4. **`proof_of_concept_plan.md`** - Minimal implementation:
   - Pick one domain (e.g., oscilloscope art)
   - Implement 2-3 layers only
   - Test basic functionality
   - Evaluation criteria

**In `/agent_swarm/proof_of_concept/`:**

5. **`code/orchestrator.py`** - Stub with TODO comments

6. **`code/layer_agents.py`** - Stub with example agent

7. **`test_domain.md`** - Oscilloscope art research as test case

---

## PHASE 5: DOCUMENTATION & PROCESS TRACKING

**Create these files:**

1. **`/documentation/process_notes/phase1_build.md`** - Document YOUR process:
   - What you did in what order
   - Decisions you made and why
   - Problems encountered
   - Time spent on each task
   - What was easy vs hard

2. **`/documentation/decisions/resource_requirements.md`** - Flag for human:
   - Total estimated cost for experiments (API calls, compute)
   - Expert access needed
   - Time requirements
   - Budget breakdown

3. **`/documentation/phase_reviews/phase1_review.md`** - Self-assessment:
   - What's complete?
   - What's incomplete?
   - What surprised you?
   - What should be prioritized next?
   - Where do you need human input?

4. **`/resources/templates/experiment_protocol_template.md`** - Reusable template

5. **`/resources/templates/paper_outline_template.md`** - Reusable template

6. **`/resources/scripts/setup_experiment.sh`** - Script to scaffold new experiment

---

## PHASE 6: METADATA & PACKAGING

**Create:**

1. **`/README.md`** - Project overview:
   - What this project is
   - How to use it
   - Directory structure explanation
   - Getting started guide
   - Prerequisites

2. **`/CONTRIBUTING.md`** - How others can contribute:
   - Code standards
   - Documentation requirements
   - Review process

3. **`/LICENSE.md`** - Open source license (suggest MIT or Apache 2.0)

4. **`/CITATIONS.bib`** - BibTeX file with all references

5. **`/PROJECT_STATUS.md`** - Current state:
   - What's done
   - What's in progress
   - What's planned
   - Last updated

---

## SUCCESS CRITERIA

After completion, verify:

### ✓ Directory Structure
- [ ] All directories exist
- [ ] Logical organization
- [ ] READMEs in each major directory

### ✓ Literature Collection
- [ ] At least 15 papers found
- [ ] Index created
- [ ] Citations properly formatted
- [ ] Key findings extracted

### ✓ Experimental Protocols
- [ ] All 4 experiments have detailed protocols
- [ ] Code stubs created
- [ ] Data structures defined
- [ ] Resource estimates provided

### ✓ Paper Outlines
- [ ] All 4 papers outlined in detail
- [ ] Related work identified
- [ ] Figures specified
- [ ] Target venues listed

### ✓ Agent Swarm
- [ ] Complete technical specification
- [ ] All 7 layers detailed
- [ ] Proof-of-concept planned
- [ ] Code stubs created

### ✓ Documentation
- [ ] Process documented
- [ ] Decisions flagged
- [ ] Phase review complete
- [ ] Templates created

### ✓ Packaging
- [ ] README clear and comprehensive
- [ ] Project status updated
- [ ] Citations compiled
- [ ] License added

---

## EXECUTION STRATEGY

### Recommended Order:

**Hour 1: Foundation**
1. Create directory structure
2. Start literature collection (parallel process)
3. Create basic README

**Hour 2: Protocols**
1. Expand Experiment 1 protocol fully
2. Stub Experiments 2-4
3. Create code structure for Experiment 1

**Hour 3: Papers & Architecture**
1. Outline Paper A (confidence-accuracy) in detail
2. Stub other paper outlines
3. Create agent swarm architecture spec

**Hour 4: Documentation & Review**
1. Document process
2. Create phase review
3. Flag resource decisions
4. Package everything
5. Final verification

### Parallel Processing:

While creating protocols, also:
- Search for papers (can run in background)
- Download or save citations
- Build literature index

### Quality > Speed:

Better to have:
- 2 complete, detailed experimental protocols
- 2 thorough paper outlines
- 1 well-specified swarm architecture

Than:
- 4 half-baked protocols
- 4 vague outlines
- 1 hand-wavy spec

---

## DELIVERABLE: COMPLETE DOWNLOADABLE PACKAGE

At end, create:

**`collaborative_epistemology_project.zip`** containing:
- All directories and files
- README explaining contents
- Quick start guide
- No broken links or missing files

User should be able to:
1. Download zip
2. Unzip
3. Read README
4. Navigate to any experiment/paper
5. Find complete specifications
6. Start implementation immediately

---

## META-INSTRUCTIONS: TRACK YOUR OWN PROCESS

As you work, observe:

**When you feel confident:**
- Are you actually certain or just generating plausible-sounding content?
- How do you know?
- Document this in process notes

**When you're uncertain:**
- What specifically don't you know?
- What would help you decide?
- Flag for human or mark clearly as tentative

**When you make decisions:**
- What alternatives did you consider?
- Why this choice?
- Document reasoning

**This meta-observation is valuable data about AI epistemic behavior.**

---

## IMPORTANT REMINDERS

### You CAN:
✓ Create complete directory structures  
✓ Search for and download papers  
✓ Generate detailed specifications  
✓ Write code stubs with clear TODOs  
✓ Create comprehensive documentation  
✓ Assess resource requirements  
✓ Flag decisions for humans  

### You CANNOT:
✗ Actually run experiments  
✗ Access paid journal articles (but can find DOIs)  
✗ Train new models  
✗ Make budget decisions  
✗ Submit papers  

### You SHOULD:
✓ Be thorough and detailed  
✓ Document everything  
✓ Be honest about uncertainty  
✓ Create actually implementable specifications  
✓ Think about users who will use this  

### You SHOULD NOT:
✗ Hand-wave implementation details  
✗ Create vague specifications  
✗ Skip documentation  
✗ Assume users know what you know  
✗ Rush to completion  

---

## BEGIN

Read the main paper (`collaborative_epistemology_paper.md`) thoroughly.

Then start with:
1. Create full directory structure
2. Begin literature collection
3. Expand first experimental protocol

Work systematically. Document as you go. Build something real.

**The foundation paper is complete. Now build the infrastructure to continue the work.**

---

**END OF BUILD INSTRUCTIONS**

*This document should be saved as: `/BUILD_INSTRUCTIONS.md` and provided to Claude CLI agent for execution.*
