#!/usr/bin/env python3
"""
Utility functions for shader physics lab
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

def generate_shader_id(shader_name: str) -> str:
    """Generate unique ID for shader based on name and timestamp"""
    timestamp = datetime.now().isoformat()
    raw = f"{shader_name}_{timestamp}"
    return hashlib.sha256(raw.encode()).hexdigest()[:12]

def parse_shader_metadata(glsl_content: str) -> Dict[str, Any]:
    """
    Extract metadata from GLSL comments
    
    Expected format at top of shader:
    // METADATA: shader-name
    // TAGS: quantum, rotation, crystallization
    // PARAMS: rotation_rate(0.0, 5.0, 0.5), phase_offset(0.0, 6.28, 0.0)
    
    Returns dict with extracted metadata
    """
    metadata = {
        "name": None,
        "tags": [],
        "uniforms": {}
    }
    
    lines = glsl_content.split('\n')
    for line in lines:
        line = line.strip()
        if not line.startswith('//'):
            break  # Stop at first non-comment line
        
        # Parse METADATA
        if line.startswith('// METADATA:'):
            metadata['name'] = line.split(':', 1)[1].strip()
        
        # Parse TAGS
        elif line.startswith('// TAGS:'):
            tags_str = line.split(':', 1)[1].strip()
            metadata['tags'] = [t.strip() for t in tags_str.split(',')]
        
        # Parse PARAMS
        elif line.startswith('// PARAMS:'):
            params_str = line.split(':', 1)[1].strip()
            # Parse: name(min, max, default), name2(min, max, default)
            for param in params_str.split('),'):
                param = param.strip().rstrip(')')
                if '(' not in param:
                    continue
                name, values = param.split('(')
                name = name.strip()
                try:
                    min_val, max_val, default = map(float, values.split(','))
                    metadata['uniforms'][name] = {
                        'min': min_val,
                        'max': max_val,
                        'default': default
                    }
                except ValueError:
                    continue
    
    return metadata

def create_shader_metadata(
    shader_name: str,
    tags: list,
    source_paper: str,
    verified: bool,
    verification_score: float,
    uniforms: dict
) -> dict:
    """
    Create complete metadata JSON for a shader
    
    Returns dict ready to save as {shader_name}.json
    """
    return {
        "name": shader_name,
        "tags": tags,
        "source_paper": source_paper,
        "created": datetime.now().isoformat(),
        "verified": verified,
        "verification_score": verification_score,
        "uniforms": uniforms,
        "id": generate_shader_id(shader_name)
    }

def update_library_index(shader_metadata: dict):
    """
    Add/update shader in the library metadata index
    
    The index (shaders/metadata.json) maintains a list of all shaders
    for fast searching/listing without loading individual files
    """
    index_path = Path("shaders/metadata.json")
    
    if index_path.exists():
        with open(index_path, 'r') as f:
            index = json.load(f)
    else:
        index = {"shaders": []}
    
    # Remove existing entry if updating
    index['shaders'] = [
        s for s in index['shaders']
        if s['name'] != shader_metadata['name']
    ]
    
    # Add new entry
    index['shaders'].append({
        "name": shader_metadata['name'],
        "tags": shader_metadata['tags'],
        "created": shader_metadata['created'],
        "verified": shader_metadata['verified'],
        "source_paper": shader_metadata.get('source_paper', '')
    })
    
    with open(index_path, 'w') as f:
        json.dump(index, f, indent=2)

def extract_uniforms_from_glsl(glsl_content: str) -> dict:
    """
    Parse GLSL to find all uniform declarations
    
    Returns dict of uniform_name: type
    """
    uniforms = {}
    for line in glsl_content.split('\n'):
        line = line.strip()
        if line.startswith('uniform '):
            parts = line.split()
            if len(parts) >= 3:
                uniform_type = parts[1]
                uniform_name = parts[2].rstrip(';')
                uniforms[uniform_name] = uniform_type
    return uniforms

def format_verification_log(
    shader_name: str,
    attempts: list,
    final_result: dict
) -> str:
    """
    Format verification log for saving
    
    Args:
        shader_name: Name of shader being verified
        attempts: List of attempt dicts with results
        final_result: Final verification result
        
    Returns formatted log string
    """
    log = [
        f"Verification Log: {shader_name}",
        f"Timestamp: {datetime.now().isoformat()}",
        f"Total attempts: {len(attempts)}",
        "",
        "=" * 60,
        ""
    ]
    
    for i, attempt in enumerate(attempts, 1):
        log.append(f"Attempt {i}:")
        log.append(f"  Score: {attempt.get('score', 0):.2f}")
        log.append(f"  Matched: {attempt.get('matches', False)}")
        
        if attempt.get('discrepancies'):
            log.append("  Discrepancies:")
            for disc in attempt['discrepancies']:
                log.append(f"    - {disc['criterion']}: {disc['observed']}")
        
        if attempt.get('fixes_applied'):
            log.append("  Fixes applied:")
            for fix in attempt['fixes_applied']:
                log.append(f"    - {fix}")
        log.append("")
    
    log.append("=" * 60)
    log.append(f"Final result: {'PASSED' if final_result['matches'] else 'FAILED'}")
    log.append(f"Best score: {final_result.get('best_score', 0):.2f}")
    
    return '\n'.join(log)

def save_verification_log(shader_name: str, log_content: str):
    """Save verification log to verification/logs/"""
    log_dir = Path("verification/logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = log_dir / f"{shader_name}_{timestamp}.log"
    
    with open(log_path, 'w') as f:
        f.write(log_content)
    
    return log_path
