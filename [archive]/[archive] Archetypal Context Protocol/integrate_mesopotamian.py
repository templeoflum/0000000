import json
import os
import glob

# Consolidate all Mesopotamian archetypes
output_file = r"C:\Users\User\Documents\0000000\Archetypal Context Protocol\[ME] Mesopotamian_Complete.json"
generated_dir = r"C:\Users\User\Documents\0000000\Archetypal Context Protocol\generated_mesopotamian"

all_archetypes = []
json_files = glob.glob(os.path.join(generated_dir, "*.json"))

print(f"Integrating {len(json_files)} Mesopotamian archetype files...")
print("=" * 80)

for filepath in sorted(json_files):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            archetype = json.load(f)
            all_archetypes.append(archetype)
            # Show both names if it has Sumerian/Akkadian
            name = archetype['ArchetypeName']
            aliases = archetype.get('CommonAliases', [])
            if aliases and len(aliases) > 0:
                display = f"{name} ({aliases[0]})"
            else:
                display = name
            print(f"  [X] {display}")
    except json.JSONDecodeError as e:
        print(f"  [!] ERROR in {os.path.basename(filepath)}: {e}")
    except Exception as e:
        print(f"  [!] ERROR in {os.path.basename(filepath)}: {e}")

mesopotamian_system = {
    "SystemName": "Mesopotamian Mythology",
    "SystemCode": "ME",
    "Description": "Ancient mythology of Sumer, Akkad, Babylon, and Assyria - one of the oldest recorded mythological systems",
    "SchemaVersion": "1.1-ter",
    "TotalArchetypes": len(all_archetypes),
    "HistoricalPeriods": {
        "Sumerian": "~4500-2000 BCE",
        "Akkadian": "~2334-2154 BCE",
        "Babylonian": "~1894-539 BCE",
        "Assyrian": "~2500-609 BCE"
    },
    "Categories": {
        "Supreme_Creation": 7,
        "Major_Deities": 10,
        "Wisdom_Writing": 4,
        "Heroes_Kings": 5,
        "Dying_Gods": 3,
        "Healing_Magic": 3,
        "Underworld_Death": 2,
        "Demons_Spirits": 3,
        "Monsters_Guardians": 2,
        "Supporting_Figures": 5
    },
    "Archetypes": all_archetypes
}

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(mesopotamian_system, f, indent=2, ensure_ascii=False)

print("\n" + "=" * 80)
print(f"Integration Complete!")
print(f"Total Mesopotamian Archetypes: {len(all_archetypes)}")
print(f"Saved to: {output_file}")
print(f"File size: {os.path.getsize(output_file) / 1024:.1f} KB")

print("\n" + "=" * 80)
print("Mesopotamian Mythology System - COMPLETE")
print("=" * 80)
print("Categories:")
for category, count in mesopotamian_system["Categories"].items():
    print(f"  {category.replace('_', ' ')}: {count}")
