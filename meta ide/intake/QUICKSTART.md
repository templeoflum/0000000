# Quick Start: From Docs to Running System

You now have a complete documentation bundle ready to bootstrap Meta-IDE. Here's how to actually start building.

## What You Have

- **PROTOCOL.md** - Scientific Collaboration Protocol v1.1 (your methodology)
- **STACK.md** - All the open source projects you'll use (with links)
- **SETUP.md** - Installation steps for dependencies
- **ARCHITECTURE.md** - Design philosophy and technical decisions
- **BOOTSTRAP.md** - Implementation roadmap (12-18 hours to MVP)
- **flake.nix** - Nix development environment
- **meta-ide-docs.tar.gz** - Everything bundled for easy transfer

## Immediate Next Steps

### 1. Create Repository (5 minutes)

```bash
# Create new git repo
mkdir meta-ide
cd meta-ide
git init

# Extract docs
tar -xzf ~/Downloads/meta-ide-docs.tar.gz --strip-components=1

# Or manually copy files:
cp ~/Downloads/meta-ide-docs/* .

# Initial commit
git add .
git commit -m "Initial commit: Protocol v1.1 + documentation"
```

### 2. Install Minimal Dependencies (30 minutes)

```bash
# Rust (essential)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env

# Nix (recommended for reproducible builds)
sh <(curl -L https://nixos.org/nix/install) --daemon

# Ollama (for local models)
curl -fsSL https://ollama.com/install.sh | sh

# Pull one model to start
ollama pull deepseek-coder:7b  # Smaller/faster for testing
```

### 3. Start Building (follow BOOTSTRAP.md)

```bash
# Phase 0: Project structure
cargo new --lib core
cd core

# Add dependencies (see BOOTSTRAP.md Phase 0)
cargo add tokio --features full
cargo add serde --features derive
cargo add serde_yaml
cargo add anyhow
# ... (full list in BOOTSTRAP.md)

# Create src directory structure
mkdir -p src/{bin,adapters}

# Start with data models (BOOTSTRAP.md Phase 1)
# Copy type definitions from ARCHITECTURE.md into core/src/lib.rs
```

### 4. First Milestone: Gate Checker

**Goal:** Build a tool that verifies phase deliverables exist and are valid.

**Time:** ~4 hours

**What you'll have:**
- Command line tool that checks if experiment files exist
- Anti-hallucination detection (blocks progression if files are missing)
- Foundation for all other features

**Test it:**
```bash
# Create test experiment manually
mkdir -p experiments/exp_001_test/phase_deliverables

# Write Phase 0 deliverable
cat > experiments/exp_001_test/phase_deliverables/0_hypothesis.yaml << EOF
hypothesis:
  claim: "Gate checker will detect missing files"
  confidence: 0.9
EOF

# Run gate check
cargo run --bin meta-ide -- gate --experiment exp_001_test --phase 0
# Should: PASS (file exists)

# Create Phase 4 with fake file reference
cat > experiments/exp_001_test/phase_deliverables/4_execution.yaml << EOF
outputs:
  - path: "fake.png"
EOF

# Run gate check  
cargo run --bin meta-ide -- gate --experiment exp_001_test --phase 4
# Should: FAIL with "HALLUCINATION DETECTED"
```

## Alternative: Use Claude CLI to Generate Code

If you have Claude CLI installed:

```bash
# In repo root
claude chat

> I'm implementing the Meta-IDE system. Read ARCHITECTURE.md and BOOTSTRAP.md.
> Generate the Rust code for core/src/protocol_enforcer.rs implementing 
> the PhaseGate with exit conditions for Phases 0 and 4.
```

Claude will generate the implementation based on the architecture docs.

## Development Strategy

**Don't build everything at once.** Follow this progression:

1. **Week 1:** Gate checker + manual experiment workflow
   - Create experiments by hand
   - Run gate checks to verify
   - Learn the protocol through doing

2. **Week 2:** Add one model adapter (Ollama OR Anthropic)
   - Model generates Phase 0 deliverables
   - Gate checks validate model output
   - Provenance tracking starts

3. **Week 3:** Automate Phases 1-4
   - Model writes code, runs tests
   - Anti-hallucination checks at every step
   - First complete automated experiment

4. **Week 4:** Add recursive verification
   - Phase completion audits
   - Contamination detection
   - Lineage tracking

## When to Read What

**Starting (now):**
- README.md (this file)
- BOOTSTRAP.md (implementation roadmap)
- STACK.md (what to install)

**Building Phase 0-1:**
- ARCHITECTURE.md (understand the design)
- PROTOCOL.md Sections 1-4 (understand the methodology)

**Building Phase 2-4:**
- PROTOCOL.md Section 7 (verification infrastructure)
- ARCHITECTURE.md (reference as you implement)

**After MVP works:**
- PROTOCOL.md Section 6 (meta-protocol)
- PROTOCOL.md Section 8 (model-agnostic infrastructure)

## Success Metrics

You'll know you're making progress when:

- [ ] Gate checker compiles and runs
- [ ] Can create experiment manually and verify it
- [ ] Gate checker catches missing files (hallucination detection works)
- [ ] Can run one experiment end-to-end (even if manual)
- [ ] Provenance log captures what happened
- [ ] Can re-verify an experiment after completion

## Getting Help

**Stuck on Rust syntax?**
→ Ask Claude to implement specific functions from ARCHITECTURE.md

**Not sure what to build next?**
→ Follow BOOTSTRAP.md phase by phase

**Confused about the protocol?**
→ PROTOCOL.md has detailed examples and evidence from real experiments

**Want to see it working?**
→ Build the gate checker first - it's the foundation for everything else

## The Core Insight

This system is different from typical dev tools because:

**The system audits itself using the same rigor it applies to science.**

Every feature you build will eventually be used to verify itself:
- Gate checker verifies its own deliverables
- Provenance tracker logs its own actions
- Audit system audits its own performance

This creates a feedback loop where the system discovers its own optimal configuration through experimentation, not guesswork.

Start simple. Build evidence. Let the system show you what works.
