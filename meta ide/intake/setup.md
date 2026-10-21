# Setup Instructions

## Prerequisites

- macOS/Linux (Windows via WSL2)
- 16GB+ RAM recommended
- Docker (for optional containerized services)
- Claude CLI or API key (for bootstrapping orchestration)

## Phase 0: Environment Setup

### 1. Install Core Dependencies
```bash
# Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env

# Nix (for reproducible builds)
sh <(curl -L https://nixos.org/nix/install) --daemon

# Git LFS
git lfs install

# SurrealDB
cargo install surrealdb --features storage-rocksdb

# Ollama
curl -fsSL https://ollama.com/install.sh | sh
```

### 2. Clone Meta-IDE Repository
```bash
git clone <your-repo-url> meta-ide
cd meta-ide
```

### 3. Initialize with Nix Flake
```bash
# Create flake.nix (see below)
nix develop  # Enter development shell with all dependencies
```

### 4. Pull Local Models
```bash
ollama pull deepseek-coder:33b
ollama pull llava:13b
ollama pull mistral:7b
```

### 5. Initialize Database
```bash
# Start SurrealDB
surreal start --log trace --user root --pass root file://meta-ide.db

# In another terminal, initialize schema
surreal import --conn http://localhost:8000 --user root --pass root --ns experiments --db meta schema/init.surql
```

## Phase 1: Bootstrap with Claude CLI

### Install Claude CLI
```bash
npm install -g @anthropic-ai/claude-cli
# or
brew install anthropic-ai/claude/claude
```

### Configure
```bash
claude configure
# Enter API key when prompted
```

### Bootstrap the System
```bash
# This will use Claude to:
# 1. Read ARCHITECTURE.md and PROTOCOL.md
# 2. Generate initial Rust project structure
# 3. Set up experiment scaffolding
# 4. Create first meta-experiment (testing the bootstrap process itself)

claude --project meta-ide bootstrap
```

**Manual alternative if CLI not available:**
```bash
# Create initial structure manually
mkdir -p core/src experiments protocols adapters tools
cargo init core
```

## Phase 2: First Experiment (Meta: Testing the Bootstrap)
```bash
# Create experiment
./scripts/new_experiment.sh "bootstrap_verification"

# This creates:
# experiments/exp_001_bootstrap_verification/
# ├── experiment.db
# ├── phase_deliverables/
# ├── artifacts/
# ├── journal/
# └── provenance/
```

## Phase 3: Verify Installation
```bash
# Run verification script
cargo run --bin verify-installation

# Expected output:
# ✓ Rust toolchain: 1.75+
# ✓ SurrealDB: Running on :8000
# ✓ Ollama: Running, models available
# ✓ Git LFS: Installed
# ✓ Experiment template: Valid
```

## Development Workflow

### Start Services
```bash
# Terminal 1: SurrealDB
surreal start --user root --pass root file://meta-ide.db

# Terminal 2: Ollama (runs as daemon, usually already running)
# Terminal 3: Your work
cd meta-ide
nix develop  # Or cargo build
```

### Run an Experiment
```bash
# Create new experiment
cargo run --bin meta-ide -- new-experiment "shader_distortion_test"

# Execute phases
cargo run --bin meta-ide -- execute --experiment exp_002_shader_distortion_test --phase 0

# Or let orchestrator run automatically
cargo run --bin meta-ide -- auto --experiment exp_002_shader_distortion_test
```

### Query Provenance
```bash
# Via CLI
surreal sql --conn http://localhost:8000 --user root --pass root --ns experiments --db meta

# Query
SELECT * FROM provenance WHERE experiment_id = 'exp_002' ORDER BY timestamp;
```

## Troubleshooting

### SurrealDB won't start
```bash
# Check if port 8000 in use
lsof -i :8000
# Kill if needed, or change port in config
```

### Ollama model not found
```bash
ollama list  # Check installed models
ollama pull <model-name>  # Install missing model
```

### Nix build fails
```bash
# Clear cache
nix-collect-garbage
# Rebuild
nix develop --refresh
```

## Next Steps

1. Read `PROTOCOL.md` - Understand the scientific collaboration workflow
2. Read `ARCHITECTURE.md` - Understand system design decisions
3. Run first meta-experiment: `cargo run --bin meta-ide -- tutorial`
4. Review `experiments/exp_001_bootstrap_verification/` to see protocol in action