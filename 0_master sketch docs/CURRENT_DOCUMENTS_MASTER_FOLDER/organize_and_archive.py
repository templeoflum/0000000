#!/usr/bin/env python3
"""
Archive docx files and categorize JSON files into proper folders.
"""

import os
import shutil
import json
from pathlib import Path

BASE_DIR = Path(r"C:/Users/User/Documents/0000000/0_master sketch docs/CURRENT_DOCUMENTS_MASTER_FOLDER")
ARCHIVE_DIR = BASE_DIR / "_archive" / "root_originals"
PARSED_DIR = BASE_DIR / "parsed_output"
UNCATEGORIZED_DIR = PARSED_DIR / "uncategorized"

# Category folders and their keywords/patterns
CATEGORIES = {
    "game_design": {
        "keywords": ["game", "lüm", "lum", "temple", "rpg", "mythos", "miroglyph", "schemataform",
                     "reflecture", "synergy", "verbrato", "sprite", "demo", "roadmap", "engine",
                     "slider", "tuning", "weaver", "resonance system", "dynamic attributes",
                     "story engine", "mnemos", "mirror key", "node", "schematic"],
        "title_patterns": ["Temple of", "MYTHOS", "Miroglyph", "Schemataform", "Reflecture",
                          "Synergy", "Verbrato", "Story engine", "MNEMOS"]
    },
    "design_language": {
        "keywords": ["design language", "aesthetic", "visual", "style", "chrome", "plasticine",
                     "glitch art", "artifice", "filamentum", "symbolic mixing", "mesh codex"],
        "title_patterns": ["Design Language", "Style definition", "Artifice Engine", "Filamentum",
                          "Symbolic Mixing", "M.E.S.H. Codex"]
    },
    "cosmology_metaphysics": {
        "keywords": ["cosmology", "metaphysics", "sphereagonal", "universe-forge", "prakāśa",
                     "tarka", "asparśa", "yoga", "ram palace", "consciousness", "reality",
                     "infinite story", "fractal pilgrim", "personification"],
        "title_patterns": ["Prakāśa", "Tarka", "Asparśa", "RAM PALACE", "Universe-Forge",
                          "Sphereagonal", "Seven_Personifications", "The_Infinite_Story",
                          "The_Fractal_Pilgrim"]
    },
    "ai_intelligence": {
        "keywords": ["ai", "agent", "prompting", "llm", "gpt", "intelligence", "adaptive",
                     "prompt", "canon gpt", "feedback uni", "resonance uni"],
        "title_patterns": ["AI_Prompting", "Adaptive_Intelligence", "agent", "prompting",
                          "canon gpt", "feedback uni", "resonance uni"]
    },
    "worldbuilding": {
        "keywords": ["world", "lore", "talavora", "mythology", "tale", "story", "narrative",
                     "chrono weaver", "fractured resonance", "esoterica"],
        "title_patterns": ["Talavora", "Tale", "Esoterica Library", "Chrono Weaver"]
    },
    "personal_creative": {
        "keywords": ["song", "album", "music", "dj", "sound system", "speaker", "labyrinth",
                     "wings", "hedawn", "liturgies", "personal", "ritual"],
        "title_patterns": ["labyrinth", "song", "DJ Foundations", "sound system", "speaker",
                          "hedawn", "wings", "album"]
    },
    "project_management": {
        "keywords": ["project", "roadmap", "current projects", "grant", "cost", "workflow",
                     "handoff", "next steps"],
        "title_patterns": ["current projects", "grant", "Cost analysis", "workflow", "roadmap"]
    }
}

def categorize_json(filename, content=None):
    """Determine category for a JSON file based on name and content."""
    name_lower = filename.lower()

    # Skip index and report files
    if filename in ["_index.json", "cleanup_report.json", "consolidation_report.json"]:
        return None

    # Check each category
    scores = {cat: 0 for cat in CATEGORIES}

    for category, rules in CATEGORIES.items():
        # Check title patterns
        for pattern in rules["title_patterns"]:
            if pattern.lower() in name_lower:
                scores[category] += 3

        # Check keywords in filename
        for keyword in rules["keywords"]:
            if keyword.lower() in name_lower:
                scores[category] += 2

        # Check content if available
        if content:
            content_str = json.dumps(content).lower() if isinstance(content, dict) else str(content).lower()
            for keyword in rules["keywords"]:
                if keyword.lower() in content_str[:2000]:  # First 2000 chars
                    scores[category] += 1

    # Return highest scoring category
    if max(scores.values()) > 0:
        return max(scores, key=scores.get)
    return None

def archive_docx_files():
    """Move docx files to archive if JSON version exists."""
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    archived = []
    no_json = []

    docx_files = list(BASE_DIR.glob("*.docx"))

    for docx_path in docx_files:
        stem = docx_path.stem
        # Check if JSON exists in parsed_output (any subfolder)
        json_exists = False
        for json_path in PARSED_DIR.rglob(f"{stem}.json"):
            json_exists = True
            break

        if json_exists:
            dest = ARCHIVE_DIR / docx_path.name
            shutil.move(str(docx_path), str(dest))
            archived.append(docx_path.name)
        else:
            no_json.append(docx_path.name)

    return archived, no_json

def categorize_uncategorized_jsons():
    """Move JSON files from uncategorized to proper category folders."""
    if not UNCATEGORIZED_DIR.exists():
        return [], []

    moved = []
    stayed = []

    for json_path in UNCATEGORIZED_DIR.glob("*.json"):
        if json_path.name in ["_index.json", "cleanup_report.json", "consolidation_report.json"]:
            continue

        # Try to read content for better categorization
        content = None
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
        except:
            pass

        category = categorize_json(json_path.name, content)

        if category:
            dest_dir = PARSED_DIR / category
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest_path = dest_dir / json_path.name

            # Don't overwrite existing files
            if not dest_path.exists():
                shutil.move(str(json_path), str(dest_path))
                moved.append((json_path.name, category))
            else:
                stayed.append((json_path.name, f"already exists in {category}"))
        else:
            stayed.append((json_path.name, "no category match"))

    return moved, stayed

def main():
    print("=" * 60)
    print("ARCHIVE AND CATEGORIZATION REPORT")
    print("=" * 60)

    # Archive docx files
    print("\n1. ARCHIVING DOCX FILES")
    print("-" * 40)
    archived, no_json = archive_docx_files()

    print(f"   Archived {len(archived)} docx files to _archive/root_originals/")
    for f in archived[:10]:
        print(f"      [OK] {f}")
    if len(archived) > 10:
        print(f"      ... and {len(archived) - 10} more")

    if no_json:
        print(f"\n   {len(no_json)} docx files kept (no JSON version found):")
        for f in no_json:
            print(f"      ! {f}")

    # Categorize JSON files
    print("\n2. CATEGORIZING JSON FILES")
    print("-" * 40)
    moved, stayed = categorize_uncategorized_jsons()

    print(f"   Moved {len(moved)} files to category folders:")
    for f, cat in moved:
        print(f"      [OK] {f} -> {cat}/")

    if stayed:
        print(f"\n   {len(stayed)} files remained uncategorized:")
        for f, reason in stayed[:10]:
            print(f"      - {f} ({reason})")
        if len(stayed) > 10:
            print(f"      ... and {len(stayed) - 10} more")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"   Docx archived: {len(archived)}")
    print(f"   Docx kept: {len(no_json)}")
    print(f"   JSON categorized: {len(moved)}")
    print(f"   JSON uncategorized: {len(stayed)}")

    # Write report
    report = {
        "archived_docx": archived,
        "kept_docx": no_json,
        "categorized_json": [(f, c) for f, c in moved],
        "uncategorized_json": [(f, r) for f, r in stayed]
    }

    with open(BASE_DIR / "organize_report.json", 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    print(f"\n   Report saved to: organize_report.json")

if __name__ == "__main__":
    main()
