#!/usr/bin/env python3
"""
Shader library management: list, search, load, delete shaders

Semantic operations on the shader library:
- List all shaders with optional tag filtering
- Search by tags or description
- Load shader metadata
- Delete shader (with confirmation)
"""

import json
import sys
from pathlib import Path
from typing import List, Optional

def load_library_metadata() -> dict:
    """Load the shader library metadata index"""
    metadata_path = Path("shaders/metadata.json")
    if not metadata_path.exists():
        return {"shaders": []}
    
    with open(metadata_path, 'r') as f:
        return json.load(f)

def save_library_metadata(metadata: dict):
    """Save updated metadata index"""
    with open("shaders/metadata.json", 'w') as f:
        json.dump(metadata, f, indent=2)

def list_shaders(tags: Optional[List[str]] = None):
    """
    List all shaders, optionally filtered by tags
    
    Args:
        tags: Optional list of tags to filter by (OR logic)
    """
    metadata = load_library_metadata()
    shaders = metadata.get("shaders", [])
    
    if tags:
        tags_lower = [t.lower() for t in tags]
        shaders = [
            s for s in shaders
            if any(tag in [t.lower() for t in s.get("tags", [])] for tag in tags_lower)
        ]
    
    if not shaders:
        print("No shaders found")
        return
    
    print(f"\nFound {len(shaders)} shader(s):\n")
    for shader in shaders:
        print(f"  {shader['name']}")
        print(f"    Tags: {', '.join(shader.get('tags', []))}")
        print(f"    Created: {shader.get('created', 'unknown')}")
        print(f"    Verified: {shader.get('verified', False)}")
        if shader.get('source_paper'):
            print(f"    Source: {shader['source_paper']}")
        print()

def search_shaders(query: str):
    """
    Semantic search through shader library
    
    TODO: Implement proper semantic search with Claude
    For now, simple string matching in name/tags
    """
    metadata = load_library_metadata()
    shaders = metadata.get("shaders", [])
    
    query_lower = query.lower()
    matches = [
        s for s in shaders
        if query_lower in s['name'].lower() or
           any(query_lower in tag.lower() for tag in s.get('tags', []))
    ]
    
    if not matches:
        print(f"No shaders matching '{query}'")
        return
    
    print(f"\nFound {len(matches)} match(es) for '{query}':\n")
    for shader in matches:
        print(f"  {shader['name']}")
        print(f"    Tags: {', '.join(shader.get('tags', []))}")
        print()

def get_shader_info(shader_name: str):
    """Display detailed info about a specific shader"""
    shader_path = Path(f"shaders/{shader_name}.json")
    if not shader_path.exists():
        print(f"Shader '{shader_name}' not found")
        return
    
    with open(shader_path, 'r') as f:
        info = json.load(f)
    
    print(f"\nShader: {info['name']}")
    print(f"Tags: {', '.join(info['tags'])}")
    print(f"Created: {info['created']}")
    print(f"Verified: {info['verified']}")
    if info.get('verification_score'):
        print(f"Verification score: {info['verification_score']:.2f}")
    print(f"\nSource: {info.get('source_paper', 'unknown')}")
    
    print("\nUniforms:")
    for name, params in info.get('uniforms', {}).items():
        print(f"  {name}:")
        print(f"    Range: [{params['min']}, {params['max']}]")
        print(f"    Default: {params['default']}")

def delete_shader(shader_name: str, force: bool = False):
    """
    Delete a shader from the library
    
    Args:
        shader_name: Name of shader to delete
        force: Skip confirmation prompt
    """
    shader_glsl = Path(f"shaders/{shader_name}.glsl")
    shader_json = Path(f"shaders/{shader_name}.json")
    
    if not shader_glsl.exists():
        print(f"Shader '{shader_name}' not found")
        return
    
    if not force:
        response = input(f"Delete '{shader_name}'? [y/N] ")
        if response.lower() != 'y':
            print("Cancelled")
            return
    
    # Remove files
    shader_glsl.unlink()
    shader_json.unlink()
    
    # Update metadata index
    metadata = load_library_metadata()
    metadata['shaders'] = [
        s for s in metadata.get('shaders', [])
        if s['name'] != shader_name
    ]
    save_library_metadata(metadata)
    
    print(f"Deleted '{shader_name}'")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Manage shader library')
    subparsers = parser.add_subparsers(dest='command', help='Command')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List shaders')
    list_parser.add_argument('--tags', help='Filter by tags (comma-separated)')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search shaders')
    search_parser.add_argument('query', help='Search query')
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Show shader details')
    info_parser.add_argument('name', help='Shader name')
    
    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete shader')
    delete_parser.add_argument('name', help='Shader name')
    delete_parser.add_argument('--force', action='store_true', help='Skip confirmation')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.command == 'list':
        tags = [t.strip() for t in args.tags.split(',')] if args.tags else None
        list_shaders(tags)
    elif args.command == 'search':
        search_shaders(args.query)
    elif args.command == 'info':
        get_shader_info(args.name)
    elif args.command == 'delete':
        delete_shader(args.name, args.force)

if __name__ == "__main__":
    main()
