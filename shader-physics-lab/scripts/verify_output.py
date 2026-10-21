#!/usr/bin/env python3
"""
Verification module: Compare rendered output to expected output

Uses Claude's vision capabilities to:
1. Screenshot rendered shader output
2. Load expected output from paper figures
3. Identify visual discrepancies
4. Return structured comparison results

This is the "decision gate" - shader doesn't pass until this returns success.
"""

from pathlib import Path
from PIL import Image
import json

def capture_shader_output(shader_path: Path, duration: float = 5.0) -> Path:
    """
    Render shader and capture screenshot
    
    TODO: Implement with headless browser (Selenium + WebGL)
    - Load shader in viewer.html
    - Let it run for 'duration' seconds
    - Capture frame at key moments
    - Save to verification/screenshots/
    
    Args:
        shader_path: Path to .glsl file
        duration: How long to run before capturing
        
    Returns:
        Path to saved screenshot
    """
    raise NotImplementedError("Implement headless rendering")

def compare_outputs(rendered: Path, expected: Path, criteria: dict) -> dict:
    """
    Use Claude vision to compare rendered vs expected output
    
    TODO: Call Claude API with both images and comparison criteria
    
    Example prompt to Claude:
    "Compare these two images. The first is my rendered output, the second
     is the expected output from the paper. Check for:
     - Smooth rotation vs discrete steps
     - Correct symmetry (6-fold expected)
     - Proper period matching (measure if possible)
     
     Return structured analysis of discrepancies."
    
    Args:
        rendered: Path to screenshot of our output
        expected: Path to paper figure
        criteria: Dict of what to check (from config.json)
        
    Returns:
        {
            "matches": bool,
            "score": float (0-1),
            "discrepancies": [
                {
                    "criterion": "smoothness",
                    "expected": "smooth helical rotation",
                    "observed": "discrete jumps every 60 degrees",
                    "severity": "high"
                }
            ],
            "suggested_fixes": [
                "Increase time step resolution",
                "Check discretization in angle update"
            ]
        }
    """
    raise NotImplementedError("Implement Claude vision comparison")

def verify_shader(shader_name: str, intake_path: Path, config: dict) -> dict:
    """
    Full verification pipeline
    
    1. Render shader
    2. Capture output
    3. Compare to expected output from intake_path/expected-output/
    4. Return structured results
    
    Args:
        shader_name: Name of shader to verify
        intake_path: Original intake folder with expected-output/
        config: Loaded config.json
        
    Returns:
        Verification results dict
    """
    shader_path = Path(f"shaders/{shader_name}.glsl")
    expected_dir = intake_path / "expected-output"
    
    if not expected_dir.exists():
        return {
            "matches": None,
            "error": "No expected output provided - cannot verify"
        }
    
    # Capture our output
    rendered = capture_shader_output(shader_path, config['rendering']['default_duration'])
    
    # Find expected image(s)
    expected_images = list(expected_dir.glob("*.png")) + list(expected_dir.glob("*.jpg"))
    if not expected_images:
        return {
            "matches": None,
            "error": "No images found in expected-output/"
        }
    
    # Compare against each expected image
    results = []
    for expected in expected_images:
        result = compare_outputs(rendered, expected, config['verification'])
        results.append(result)
    
    # Aggregate results - must match at least one expected output
    matches = any(r['matches'] for r in results)
    best_match = max(results, key=lambda r: r.get('score', 0))
    
    return {
        "matches": matches,
        "best_score": best_match['score'],
        "results": results
    }

if __name__ == "__main__":
    # Test verification on existing shader
    import sys
    if len(sys.argv) < 3:
        print("Usage: verify_output.py <shader-name> <intake-path>")
        sys.exit(1)
    
    shader_name = sys.argv[1]
    intake_path = Path(sys.argv[2])
    
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    result = verify_shader(shader_name, intake_path, config)
    print(json.dumps(result, indent=2))
