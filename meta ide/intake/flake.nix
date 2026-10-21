{
  description = "Meta-IDE: Self-auditing research environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    rust-overlay.url = "github:oxalica/rust-overlay";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, rust-overlay, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        overlays = [ (import rust-overlay) ];
        pkgs = import nixpkgs {
          inherit system overlays;
        };
        
        rustToolchain = pkgs.rust-bin.stable.latest.default.override {
          extensions = [ "rust-src" "rust-analyzer" ];
        };
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            # Rust
            rustToolchain
            cargo-watch
            cargo-edit
            
            # Database
            surrealdb
            
            # AI/ML
            # ollama installed separately via their installer
            
            # Build tools
            pkg-config
            openssl
            
            # Version control
            git
            git-lfs
            
            # Optional: GPU support
            vulkan-loader
            vulkan-headers
            
            # Optional: Node for n8n/Flowise
            nodejs_20
          ];
          
          shellHook = ''
            echo "Meta-IDE development environment"
            echo "Run 'cargo run --bin verify-installation' to check setup"
            
            export RUST_BACKTRACE=1
            export SURREAL_USER=root
            export SURREAL_PASS=root
            export SURREAL_DB=meta
          '';
        };
        
        packages.default = pkgs.rustPlatform.buildRustPackage {
          pname = "meta-ide";
          version = "0.1.0";
          src = ./.;
          cargoLock.lockFile = ./Cargo.lock;
        };
      }
    );
}