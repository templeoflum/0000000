#!/usr/bin/env python3
"""
Main entry point: intake folder → verified shader

This is where Claude CLI does the work:
1. Read research materials (PDFs, markdown)
2. Extract equations and expected visual behavior
3. Generate GLSL implementation
4. Verification loop with vision comparison
5. Save to library with metadata

Usage:
    python scripts/process_intake.py intake/optical-centrifuge/ \\
        --name "spinor-helical-rotation" \\
        --tags "quantum,rotation,optical-centrifuge"
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

def load_config():
    """Load config.json settings"""
    with open('config.json', 'r') as f:
        return json.load(f)

def process_intake(intake_path: Path, shader_name: str, tags: list[str]):
    """
    Main processing pipeline - TODO: Implement with Claude CLI
    
    Steps:
    1. Parse intake_path for:
       - PDFs (extract text, figures)
       - equations.md (key mathematical expressions)
       - notes.md (implementation guidance)
       - expected-output/ (reference images for verification)
    
    2. Generate initial shader:
       - Extract equations → GLSL code
       - Identify uniforms to expose
       - Set reasonable parameter ranges
    
    3. Verification loop (max N attempts from config):
       - Render shader output
       - Screenshot result
       - Compare to expected-output/ images
       - If mismatch:
         * Identify visual discrepancies
         * Debug implementation
         * Regenerate shader
       - If match:
         * Save to shaders/
         * Create metadata JSON
         * Exit loop
    
    4. Save verified shader:
       - shaders/{shader_name}.glsl
       - shaders/{shader_name}.json (metadata)
       - verification/logs/{shader_name}.log
    
    Args:
        intake_path: Path to intake folder with research materials
        shader_name: Name for the generated shader
        tags: List of semantic tags
    """
    config = load_config()
    
    print(f"Processing {intake_path} → {shader_name}")
    print(f"Tags: {', '.join(tags)}")
    
    # TODO: Connect to Claude CLI here
    # This is where you'll orchestrate the autonomous generation + verification
    
    # Pseudocode for Claude CLI integration:
    # 
    # 1. Read all files in intake_path
    # 2. Call Claude CLI with prompt:
    #    "Read these research materials and generate a GLSL shader
    #     that implements the key equations. The shader must match
    #     the visual output shown in the expected-output/ folder."
    # 
    # 3. Claude generates shader + enters verification loop
    # 4. Return when verified or max_attempts exceeded
    
    raise NotImplementedError(
        "Connect to Claude CLI here. See README for architecture."
    )

def main():
    parser = argparse.ArgumentParser(
        description='Process research intake into verified shader'
    )
    parser.add_argument(
        'intake_path',
        type=Path,
        help='Path to intake folder with research materials'
    )
    parser.add_argument(
        '--name',
        required=True,
        help='Name for the generated shader'
    )
    parser.add_argument(
        '--tags',
        required=True,
        help='Comma-separated tags (e.g., "quantum,rotation,optical")'
    )
    
    args = parser.parse_args()
    
    if not args.intake_path.exists():
        print(f"Error: {args.intake_path} does not exist")
        sys.exit(1)
    
    tags = [t.strip() for t in args.tags.split(',')]
    
    try:
        process_intake(args.intake_path, args.name, tags)
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
