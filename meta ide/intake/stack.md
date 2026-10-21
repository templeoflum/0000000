# Meta-IDE Technology Stack

## Core Infrastructure

### Orchestration & Workflow
- **n8n** - https://github.com/n8n-io/n8n
  - Self-hosted workflow automation
  - Will orchestrate multi-agent coordination
  - Docker deployment: `docker run -it --rm --name n8n -p 5678:5678 n8nio/n8n`

### Data Layer
- **SurrealDB** - https://github.com/surrealdb/surrealdb
  - Graph-relational database for provenance tracking
  - Embedded mode for local experiments
  - `brew install surrealdb/tap/surreal` or `cargo install surrealdb`

- **Qdrant** - https://github.com/qdrant/qdrant
  - Vector database for embeddings (vision verification, semantic search)
  - Rust-native, WGPU-compatible
  - Docker: `docker run -p 6333:6333 qdrant/qdrant`

### Agent Runtime
- **Ollama** - https://github.com/ollama/ollama
  - Local LLM serving (DeepSeek Coder, Llava, etc.)
  - `curl -fsSL https://ollama.com/install.sh | sh`

- **Flowise** - https://github.com/FlowiseAI/Flowise
  - Visual LLM chain builder for prototyping
  - `npm install -g flowise && flowise start`

### Code & Build
- **Nix** - https://nixos.org/download.html
  - Reproducible builds and environment management
  - `sh <(curl -L https://nixos.org/nix/install) --daemon`

- **Rust toolchain**
  - Meta-IDE core will be Rust
  - `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`

### Version Control & Provenance
- **Git** (required)
- **Git LFS** - https://git-lfs.github.com/ (for large artifacts)

## Development Tools

### Code Editor Integration
- **Neovim** + **LSP** (optional, but recommended)
- Alternatively: **Zed** - https://github.com/zed-industries/zed (Rust-based, GPU-accelerated)

### API Development
- **Bruno** - https://github.com/usebruno/bruno
  - Open-source API client for testing MCP endpoints
  - Download from releases: https://github.com/usebruno/bruno/releases

## Vision & Graphics (for your existing workflow)
- **WGPU** - https://github.com/gfx-rs/wgpu (already in your stack)
- **Bevy** - https://github.com/bevyengine/bevy (optional: for procedural generation experiments)

## Minimal Starting Stack

If you want to start minimal and expand:
```bash
# Essential
- Rust + Cargo
- Git
- SurrealDB (embedded mode)
- Ollama (local models)

# Add as needed
- n8n (when multi-agent orchestration required)
- Qdrant (when vision verification needed)
- Flowise (for rapid LLM chain prototyping)
```

## Model Recommendations

### Local (via Ollama)
```bash
ollama pull deepseek-coder:33b   # Code execution agent
ollama pull llava:13b             # Vision verification
ollama pull mistral:7b            # Lightweight planning
```

### API (optional, for comparison)
- Claude Sonnet 4 (critique, planning)
- Claude Haiku 4 (fast execution tasks)

## Repository Structure
```
meta-ide/
├── core/              # Rust core (orchestrator, protocol enforcer)
├── protocols/         # Scientific collaboration protocol definitions
├── experiments/       # Individual experiment directories
├── adapters/          # Model adapter implementations
├── tools/             # Verification tools, vision system
├── nix/               # Nix flake for reproducible builds
└── docs/              # This documentation
```