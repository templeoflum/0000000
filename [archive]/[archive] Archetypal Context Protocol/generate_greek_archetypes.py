import json
import os

# Greek archetype definitions
# This will generate entries for the 130 missing Greek archetypes

greek_archetypes = {
    # PRIMORDIALS
    "Gaia": {
        "ArchetypeName": "Gaia",
        "CommonAliases": ["Earth Mother", "Primal Mother", "Terra", "Ge"],
        "ArchetypalFunction": "To embody the earth itself, to birth all life, and to be the foundation of existence.",
        "PrimaryDomain": "Mythic / Natural",
        "ToneOrPolarity": "Nurturing / Primal",
        "SymbolicCore": "The primordial earth, source of all creation and life.",
        "Element": "Earth",
        "Planet": "Earth",
        "Chakra": "Root",
        "Color": "Deep Green, Brown",
        "Animal": "Serpent, Bear",
        "Other": ["Mountain", "Cave", "Fertile Soil", "Grain"],
        "NarrativeFunction": ["Mother", "Creator", "Foundation", "Origin"],
        "ComplementaryArchetypes": ["Uranus ([GR] Sky Father)", "Cronus ([GR] Son/Usurper)"],
        "ShadowForms": ["Devouring Mother", "Vengeful Earth", "Destructive Nature"],
        "CoreTraits": ["Nurturing", "Primal", "Powerful", "Fertile", "Eternal", "Patient"],
        "MBTI": "ISFJ",
        "Enneagram": "9w8",
        "MythicAppearances": ["Theogony (Hesiod)", "Mother of Titans", "Oracle at Delphi"],
        "Description": "The personification of Earth itself, first deity to emerge from Chaos, mother of all."
    },

    "Uranus": {
        "ArchetypeName": "Uranus",
        "CommonAliases": ["Sky Father", "Ouranos", "Starry Heaven", "Caelus"],
        "ArchetypalFunction": "To encompass the heavens, to fertilize the earth, and to hold dominion over the cosmos.",
        "PrimaryDomain": "Mythic / Celestial",
        "ToneOrPolarity": "Distant / Authoritative",
        "SymbolicCore": "The vault of heaven, consciousness detached from earthly concerns.",
        "Element": "Air",
        "Planet": "Uranus",
        "Chakra": "Crown",
        "Color": "Sky Blue, Silver",
        "Animal": "Eagle, Hawk",
        "Other": ["Stars", "Rain", "Sky Dome", "Celestial Sphere"],
        "NarrativeFunction": ["Father", "Sky God", "Progenitor", "Tyrant"],
        "ComplementaryArchetypes": ["Gaia ([GR] Earth Mother)", "Cronus ([GR] Usurper Son)"],
        "ShadowForms": ["Distant Father", "Imprisoner", "Tyrant", "Fearful Authority"],
        "CoreTraits": ["Distant", "Authoritative", "Fearful", "Generative", "Tyrannical"],
        "MBTI": "INTJ",
        "Enneagram": "8w9",
        "MythicAppearances": ["Castration by Cronus", "Father of Titans", "Primordial Sky"],
        "Description": "Personification of the sky, first ruler of the universe, overthrown by his son Cronus."
    },

    "Nyx": {
        "ArchetypeName": "Nyx",
        "CommonAliases": ["Night", "Primordial Night", "Mother of Mysteries", "Nox"],
        "ArchetypalFunction": "To embody night, mystery, and the unknown; to veil the world in darkness.",
        "PrimaryDomain": "Mythic / Cosmic",
        "ToneOrPolarity": "Mysterious / Dark",
        "SymbolicCore": "The primordial darkness, the veil between worlds, the unknown.",
        "Element": "Darkness/Void",
        "Planet": "Dark Moon",
        "Chakra": "Third Eye",
        "Color": "Black, Deep Purple",
        "Animal": "Owl, Bat, Raven",
        "Other": ["Starry Cloak", "Veil", "Shadow", "Night Sky"],
        "NarrativeFunction": ["Mother of Mysteries", "Primordial Force", "Feared Power"],
        "ComplementaryArchetypes": ["Erebus ([GR] Darkness)", "Hemera ([GR] Day)"],
        "ShadowForms": ["Terror of Night", "Unknowable Void", "Consuming Darkness"],
        "CoreTraits": ["Mysterious", "Powerful", "Ancient", "Feared", "Maternal", "Dark"],
        "MBTI": "INFJ",
        "Enneagram": "5w4",
        "MythicAppearances": ["Mother of Sleep and Death", "Even Zeus feared her", "Primordial Night"],
        "Description": "The primordial goddess of night, one of the first beings to exist, even feared by Zeus himself."
    },

    "Erebus": {
        "ArchetypeName": "Erebus",
        "CommonAliases": ["Darkness", "Primordial Darkness", "Shadow", "The Mist"],
        "ArchetypalFunction": "To embody primordial darkness and shadow, the space between earth and underworld.",
        "PrimaryDomain": "Mythic / Cosmic",
        "ToneOrPolarity": "Dark / Primordial",
        "SymbolicCore": "The deep darkness, the void, the shadow realm.",
        "Element": "Darkness/Shadow",
        "Planet": "None (Primordial)",
        "Chakra": "Root",
        "Color": "Black, Dark Gray",
        "Animal": "Shadow creatures",
        "Other": ["Mist", "Void", "Abyss", "Shadowland"],
        "NarrativeFunction": ["Primordial Darkness", "Consort", "Foundation of Shadow"],
        "ComplementaryArchetypes": ["Nyx ([GR] Night)", "Aether ([GR] Light)"],
        "ShadowForms": ["Consuming Void", "Terror", "Emptiness"],
        "CoreTraits": ["Dark", "Primordial", "Silent", "Encompassing", "Ancient"],
        "MBTI": "ISTP",
        "Enneagram": "5w6",
        "MythicAppearances": ["Father of Aether and Hemera", "Primordial Darkness", "The Mist of Hades"],
        "Description": "Personification of deep darkness and shadow, emerged from Chaos, consort of Nyx."
    },

    "Cronus": {
        "ArchetypeName": "Cronus",
        "CommonAliases": ["Kronos", "Time", "The Harvester", "Saturn", "Titan King"],
        "ArchetypalFunction": "To rule through fear and control, to devour the future, to embody inevitable time.",
        "PrimaryDomain": "Mythic / Temporal",
        "ToneOrPolarity": "Tyrannical / Fearful",
        "SymbolicCore": "Time that devours all, the fearful father, the overthrown tyrant.",
        "Element": "Earth/Time",
        "Planet": "Saturn",
        "Chakra": "Solar Plexus",
        "Color": "Dark Gold, Gray",
        "Animal": "Serpent, Harvest creatures",
        "Other": ["Sickle", "Scythe", "Hourglass", "Harvest"],
        "NarrativeFunction": ["King", "Tyrant", "Father", "Devourer"],
        "ComplementaryArchetypes": ["Rhea ([GR] Mother/Queen)", "Zeus ([GR] Usurper Son)"],
        "ShadowForms": ["Devouring Father", "Paranoid Tyrant", "Time's Cruelty"],
        "CoreTraits": ["Tyrannical", "Fearful", "Powerful", "Paranoid", "Inevitable"],
        "MBTI": "ESTJ",
        "Enneagram": "8w7",
        "MythicAppearances": ["Castration of Uranus", "Devouring his children", "Overthrow by Zeus"],
        "Description": "King of the Titans, castrated his father Uranus, devoured his children to prevent overthrow, defeated by Zeus."
    }
}

def generate_full_entry(archetype_data):
    """Generate a complete JSON entry from abbreviated data"""
    name = archetype_data["ArchetypeName"]

    return {
        "SchemaVersion": "1.1-ter",
        "ArchetypeName": name,
        "SystemOfOrigin": "GR",
        "CulturalLineage": ["Greek"],
        "CommonAliases": archetype_data.get("CommonAliases", []),
        "SymbolicEssence": {
            "ArchetypalFunction": archetype_data.get("ArchetypalFunction", ""),
            "PrimaryDomain": archetype_data.get("PrimaryDomain", "Mythic"),
            "ToneOrPolarity": archetype_data.get("ToneOrPolarity", ""),
            "SymbolicCore": archetype_data.get("SymbolicCore", ""),
            "Correspondences": {
                "Element": archetype_data.get("Element", ""),
                "Planet": archetype_data.get("Planet", ""),
                "Chakra": archetype_data.get("Chakra", ""),
                "Color": archetype_data.get("Color", ""),
                "Animal": archetype_data.get("Animal", ""),
                "Other": archetype_data.get("Other", [])
            }
        },
        "NarrativeRoles": {
            "NarrativeFunction": archetype_data.get("NarrativeFunction", []),
            "ComplementaryArchetypes": archetype_data.get("ComplementaryArchetypes", []),
            "ShadowForms": archetype_data.get("ShadowForms", []),
            "DevelopmentalArc": [],
            "CyclePhase": archetype_data.get("CyclePhase", "")
        },
        "PsychologicalMapping": {
            "CoreTraits": archetype_data.get("CoreTraits", []),
            "Typologies": {
                "MBTI": archetype_data.get("MBTI", ""),
                "Enneagram": archetype_data.get("Enneagram", ""),
                "Other": ["Ruler", "King", "Father"]
            },
            "SubVariants": archetype_data.get("SubVariants", []),
            "InternalFamily": archetype_data.get("InternalFamily", "")
        },
        "CulturalContext": {
            "Regions": ["Greece", "Mediterranean"],
            "MythicAppearances": archetype_data.get("MythicAppearances", []),
            "ReligiousOrRitualUse": "Ancient Greek religious worship and mythology",
            "HistoricalEvolution": "From oral tradition to written mythology in Hesiod and Homer",
            "SyncreticForms": []
        },
        "SymbolicRepresentation": {
            "SigilOrGlyph": "",
            "ImageryNotes": archetype_data.get("Description", ""),
            "ArtisticExamples": ["Greek pottery", "Classical sculpture", "Renaissance art"],
            "PoeticInvocation": "",
            "DreamForm": ""
        },
        "MetaIntegration": {
            "SystemicLinks": [],
            "SemanticTags": [f"#{name.lower()}", "#greek", "#mythology"],
            "RitualFunction": "",
            "AIPromptSeeds": [],
            "NarrativeHooks": []
        },
        "SyncreticMapping": {
            "Bidirectional": True,
            "Equivalents": []
        },
        "FacetRegistry": []
    }

# Generate first 5 entries
output_dir = r"C:\Users\User\Documents\0000000\Archetypal Context Protocol\generated_greek"
os.makedirs(output_dir, exist_ok=True)

print("Generating Greek archetype entries...")
print("=" * 80)

for name, data in greek_archetypes.items():
    full_entry = generate_full_entry(data)

    output_file = os.path.join(output_dir, f"[GR] {name}.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(full_entry, f, indent=2, ensure_ascii=False)

    print(f"[X] Generated: {name}")

print(f"\n{len(greek_archetypes)} entries generated in: {output_dir}")
print("\nThese are the first 5 Primordial deities. Ready to continue with more.")
