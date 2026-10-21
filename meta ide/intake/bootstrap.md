# Bootstrap Implementation Plan

## Objective

Build the minimal viable system that can run ONE experiment following the Scientific Collaboration Protocol, with full provenance tracking and anti-hallucination verification.

## Phase 0: Project Structure
```bash
cargo new --lib core
cd core

# Add dependencies
cargo add tokio --features full
cargo add surrealdb --features kv-rocksdb
cargo add serde --features derive
cargo add serde_json
cargo add serde_yaml
cargo add uuid --features v4
cargo add chrono --features serde
cargo add anyhow
cargo add async-trait
cargo add reqwest --features json  # For API calls
```

Create this structure:
```
core/
├── Cargo.toml
└── src/
    ├── lib.rs
    ├── protocol_enforcer.rs
    ├── provenance.rs
    ├── executor.rs
    ├── auditor.rs
    ├── adapters/
    │   ├── mod.rs
    │   ├── anthropic.rs
    │   ├── ollama.rs
    │   └── human.rs
    └── bin/
        ├── meta-ide.rs
        └── verify-installation.rs
```

## Phase 1: Data Models (1-2 hours)

**File: `core/src/lib.rs`**
```rust
use serde::{Deserialize, Serialize};
use uuid::Uuid;
use chrono::{DateTime, Utc};
use std::path::PathBuf;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Experiment {
    pub id: String,
    pub hypothesis_claim: String,
    pub domain: String,
    pub status: ExperimentStatus,
    pub current_phase: u8,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ExperimentStatus {
    Active,
    Suspended,
    Complete,
    Contaminated,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProvenanceEntry {
    pub id: Uuid,
    pub timestamp: DateTime<Utc>,
    pub experiment_id: String,
    pub phase: u8,
    pub event_type: String,
    pub actor: String,
    pub description: String,
    pub inputs: Vec<PathBuf>,
    pub outputs: Vec<PathBuf>,
    pub verification_hash: Option<String>,
    pub parent_id: Option<Uuid>,
}

// Phase deliverable schemas
// (Generated from YAML schemas, for now can be Value)

pub type PhaseDeliverable = serde_yaml::Value;
```

## Phase 2: Protocol Enforcer (2-3 hours)

**File: `core/src/protocol_enforcer.rs`**
```rust
use anyhow::{Result, bail};
use std::path::{Path, PathBuf};
use crate::PhaseDeliverable;

pub struct PhaseGate {
    pub phase: u8,
    pub schema_path: PathBuf,
}

impl PhaseGate {
    pub fn check_exit_conditions(
        &self,
        experiment_id: &str
    ) -> Result<GateStatus> {
        let deliverable_path = self.get_deliverable_path(experiment_id);
        
        // 1. File must exist
        if !deliverable_path.exists() {
            return Ok(GateStatus::Blocked {
                reason: "Deliverable file does not exist (possible hallucination)".into()
            });
        }
        
        // 2. Must parse as YAML
        let content = std::fs::read_to_string(&deliverable_path)?;
        let deliverable: PhaseDeliverable = serde_yaml::from_str(&content)
            .map_err(|e| anyhow::anyhow!("YAML parse error: {}", e))?;
        
        // 3. Phase-specific gates
        match self.phase {
            0 => self.gate_phase_0(&deliverable),
            4 => self.gate_phase_4(&deliverable),
            // ... etc
            _ => Ok(GateStatus::Open)
        }
    }
    
    fn gate_phase_4(&self, deliverable: &PhaseDeliverable) -> Result<GateStatus> {
        // Verify all claimed outputs actually exist
        let exec_log = deliverable.get("execution_log")
            .and_then(|v| v.as_sequence())
            .ok_or(anyhow::anyhow!("execution_log must be array"))?;
        
        for test_entry in exec_log {
            let outputs = test_entry.get("outputs")
                .and_then(|v| v.as_sequence())
                .ok_or(anyhow::anyhow!("test must have outputs"))?;
            
            for output in outputs {
                let path_str = output.get("path")
                    .and_then(|v| v.as_str())
                    .ok_or(anyhow::anyhow!("output must have path"))?;
                
                let path = Path::new(path_str);
                if !path.exists() {
                    return Ok(GateStatus::Blocked {
                        reason: format!(
                            "HALLUCINATION DETECTED: Output {} does not exist",
                            path_str
                        )
                    });
                }
            }
        }
        
        Ok(GateStatus::Open)
    }
    
    fn get_deliverable_path(&self, experiment_id: &str) -> PathBuf {
        PathBuf::from(format!(
            "experiments/{}/phase_deliverables/{}_{}.yaml",
            experiment_id,
            self.phase,
            self.phase_name()
        ))
    }
    
    fn phase_name(&self) -> &str {
        match self.phase {
            0 => "hypothesis",
            1 => "laboratory",
            2 => "controls",
            3 => "test_design",
            4 => "execution_log",
            5 => "verification_report",
            6 => "interpretation",
            7 => "paper",
            8 => "red_team_report",
            9 => "meta_analysis",
            10 => "review",
            _ => "unknown"
        }
    }
}

#[derive(Debug)]
pub enum GateStatus {
    Open,
    Blocked { reason: String },
}
```

## Phase 3: Provenance Tracker (2 hours)

**File: `core/src/provenance.rs`**
```rust
use crate::ProvenanceEntry;
use anyhow::Result;
use std::path::PathBuf;
use uuid::Uuid;
use chrono::Utc;

pub struct ProvenanceTracker {
    db_path: PathBuf,
}

impl ProvenanceTracker {
    pub fn new(db_path: PathBuf) -> Self {
        Self { db_path }
    }
    
    pub async fn log_event(
        &self,
        experiment_id: String,
        phase: u8,
        event_type: String,
        actor: String,
        description: String,
        inputs: Vec<PathBuf>,
        outputs: Vec<PathBuf>,
        parent_id: Option<Uuid>,
    ) -> Result<Uuid> {
        let entry = ProvenanceEntry {
            id: Uuid::new_v4(),
            timestamp: Utc::now(),
            experiment_id,
            phase,
            event_type,
            actor,
            description,
            inputs,
            outputs,
            verification_hash: None, // Computed later
            parent_id,
        };
        
        // Write to JSONL file
        self.append_to_log(&entry)?;
        
        // TODO: Also write to SurrealDB
        
        Ok(entry.id)
    }
    
    fn append_to_log(&self, entry: &ProvenanceEntry) -> Result<()> {
        use std::io::Write;
        
        let log_path = self.db_path.join("provenance/event_log.jsonl");
        let json = serde_json::to_string(entry)?;
        
        let mut file = std::fs::OpenOptions::new()
            .create(true)
            .append(true)
            .open(log_path)?;
        
        writeln!(file, "{}", json)?;
        Ok(())
    }
}
```

## Phase 4: Minimal CLI (1 hour)

**File: `core/src/bin/meta-ide.rs`**
```rust
use clap::{Parser, Subcommand};

#[derive(Parser)]
#[command(name = "meta-ide")]
#[command(about = "Self-auditing research environment")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Create new experiment
    New {
        /// Experiment name
        name: String,
    },
    /// Execute a phase
    Execute {
        #[arg(short, long)]
        experiment: String,
        #[arg(short, long)]
        phase: u8,
    },
    /// Check phase gate
    Gate {
        #[arg(short, long)]
        experiment: String,
        #[arg(short, long)]
        phase: u8,
    },
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    let cli = Cli::parse();
    
    match cli.command {
        Commands::New { name } => {
            println!("Creating experiment: {}", name);
            // TODO: Create experiment directory structure
        }
        Commands::Execute { experiment, phase } => {
            println!("Executing phase {} for {}", phase, experiment);
            // TODO: Run phase execution
        }
        Commands::Gate { experiment, phase } => {
            println!("Checking gate for phase {} in {}", phase, experiment);
            // TODO: Run gate check
        }
    }
    
    Ok(())
}
```

## Phase 5: First Test Run

Create a manual experiment to verify the system:
```bash
# 1. Create experiment directory
mkdir -p experiments/exp_001_bootstrap_test/{phase_deliverables,artifacts,provenance,journal}

# 2. Write Phase 0 deliverable manually
cat > experiments/exp_001_bootstrap_test/phase_deliverables/0_hypothesis.yaml << EOF
hypothesis:
  claim: "The phase gate enforcer will correctly detect hallucinated output files"
  definitions:
    hallucinated_output: "A file path claimed in deliverable but not present on filesystem"
    correct_detection: "Gate returns Blocked status with hallucination error message"
  falsification: "If gate allows progression despite missing file, hypothesis is false"
  domain: "software_verification"
  confidence: 0.9
  confidence_reasoning: "This is a deterministic file system check"
EOF

# 3. Run gate check
cargo run --bin meta-ide -- gate --experiment exp_001_bootstrap_test --phase 0

# Expected: Gate opens (file exists and is valid YAML)

# 4. Test hallucination detection - create Phase 4 deliverable with fake output
cat > experiments/exp_001_bootstrap_test/phase_deliverables/4_execution_log.yaml << EOF
execution_log:
  - test_id: T1
    outputs:
      - path: "experiments/exp_001_bootstrap_test/artifacts/fake_file.png"
EOF

# 5. Run gate check
cargo run --bin meta-ide -- gate --experiment exp_001_bootstrap_test --phase 4

# Expected: Gate blocks with "HALLUCINATION DETECTED"
```

## Phase 6: Iterate

Once basic gate checking works:
1. Add model adapter (Ollama local or Anthropic API)
2. Have model generate Phase 0 deliverable
3. Verify with gate
4. Add Phase 1 (laboratory selection)
5. Repeat

## Claude CLI Integration

Use Claude to generate code:
```bash
# In repo root
claude --file ARCHITECTURE.md --file PROTOCOL.md \
  "Implement the auditor.rs module with phase completion audit logic. \
   It should re-hash all previous deliverables and check for contamination."

# Or interactive
claude chat
> Read ARCHITECTURE.md and implement protocol_enforcer.rs phase gates 0-3
```

## Success Criteria

**System is minimally functional when:**
- [ ] Can create experiment directory structure
- [ ] Can write/read phase deliverables
- [ ] Phase gates detect missing files (hallucination detection)
- [ ] Provenance log records events
- [ ] Can run one complete experiment (Phases 0-6) manually
- [ ] Audit system detects if deliverable modified after gate passed

## Time Estimate

- Phase 0-2: 4-6 hours (data models, enforcer, provenance)
- Phase 3-4: 2-3 hours (executor basics, CLI)
- Phase 5: 1-2 hours (manual testing)
- Phase 6: Ongoing iteration

**Total to minimal viable: ~8-12 hours of focused work**

## What NOT to Build Yet

- Multi-model consensus
- Vision verification
- n8n integration
- Full SurrealDB queries
- Lineage re-verification

**Build the simplest thing that enforces the protocol.** Add complexity only when experiments demand it.