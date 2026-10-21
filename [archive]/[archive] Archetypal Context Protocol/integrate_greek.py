import json
import os
import glob

# Consolidate all Greek archetypes into a single comprehensive file
output_file = r"C:\Users\User\Documents\0000000\Archetypal Context Protocol\[GR] Greek_Complete.json"
generated_dir = r"C:\Users\User\Documents\0000000\Archetypal Context Protocol\generated_greek"

# Collect all generated archetypes
all_archetypes = []
json_files = glob.glob(os.path.join(generated_dir, "*.json"))

print(f"Integrating {len(json_files)} Greek archetype files...")
print("=" * 80)

for filepath in sorted(json_files):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            archetype = json.load(f)
            all_archetypes.append(archetype)
            print(f"  [X] {archetype['ArchetypeName']}")
    except json.JSONDecodeError as e:
        print(f"  [!] ERROR in {os.path.basename(filepath)}: {e}")
        print(f"      Skipping this file...")

# Create comprehensive Greek system file
greek_system = {
    "SystemName": "Greek Mythology",
    "SystemCode": "GR",
    "Description": "Complete pantheon of ancient Greek mythology including Olympians, Titans, Primordials, minor deities, personifications, and legendary heroes",
    "SchemaVersion": "1.1-ter",
    "TotalArchetypes": len(all_archetypes),
    "Categories": {
        "Olympians": 19,
        "Primordials": 5,
        "Titans": 11,
        "Underworld": 9,
        "Fate_Time": 8,
        "War_Strife": 8,
        "Celestial": 7,
        "Wind_Gods": 4,
        "Personifications": 12,
        "Minor_Gods": 6,
        "Nature_Spirits": 6,
        "Heroes_Legends": 20
    },
    "Archetypes": all_archetypes
}

# Save consolidated file
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(greek_system, f, indent=2, ensure_ascii=False)

print("\n" + "=" * 80)
print(f"Integration Complete!")
print(f"Total Greek Archetypes: {len(all_archetypes)}")
print(f"Saved to: {output_file}")
print(f"File size: {os.path.getsize(output_file) / 1024:.1f} KB")

# Create summary statistics
print("\n" + "=" * 80)
print("Greek Mythology System - COMPLETE")
print("=" * 80)
print("Categories:")
for category, count in greek_system["Categories"].items():
    print(f"  {category.replace('_', ' ')}: {count}")
