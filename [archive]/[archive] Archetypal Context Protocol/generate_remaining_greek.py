import json
import os

# Complete dataset for all remaining 74 Greek archetypes
greek_archetypes_batch2 = {
    # PERSONIFICATION DEITIES (12)
    "Tyche": {
        "CommonAliases": ["Fortune", "Luck", "Fortuna", "Chance"],
        "ArchetypalFunction": "To embody fortune, chance, and the prosperity of cities",
        "SymbolicCore": "The unpredictable wheel of fortune, destiny's randomness",
        "Element": "Air", "Planet": "Jupiter", "Chakra": "Crown",
        "Color": "Gold, White", "Animal": "Winged wheel",
        "Other": ["Cornucopia", "Rudder", "Wheel", "Globe"],
        "NarrativeFunction": ["Fortune-giver", "Chance", "City Protector"],
        "CoreTraits": ["Unpredictable", "Abundant", "Fickle", "Powerful"],
        "MBTI": "ENFP", "Enneagram": "7w8",
        "Description": "Goddess of fortune and chance, controls the destiny of cities and mortals"
    },

    "Peitho": {
        "CommonAliases": ["Persuasion", "Seduction", "Suadela"],
        "ArchetypalFunction": "To embody persuasion, seduction, and charming speech",
        "SymbolicCore": "The power of words to charm and convince",
        "Element": "Air", "Planet": "Venus", "Chakra": "Throat",
        "Color": "Rose Pink", "Animal": "Dove",
        "Other": ["Honeyed words", "Veil", "Mirror"],
        "NarrativeFunction": ["Persuader", "Seductress", "Mediator"],
        "CoreTraits": ["Charming", "Eloquent", "Diplomatic", "Alluring"],
        "MBTI": "ENFJ", "Enneagram": "3w2",
        "Description": "Goddess of persuasion and seductive speech, companion of Aphrodite"
    },

    "Harmonia": {
        "CommonAliases": ["Harmony", "Concordia", "Unity"],
        "ArchetypalFunction": "To bring harmony, unity, and balance to relationships",
        "SymbolicCore": "The reconciliation of opposites, divine harmony",
        "Element": "Air", "Planet": "Venus", "Chakra": "Heart",
        "Color": "Soft Blue, Green", "Animal": "Dove, Swan",
        "Other": ["Lyre", "Scales", "Olive branch"],
        "NarrativeFunction": ["Harmonizer", "Peacemaker", "Unifier"],
        "CoreTraits": ["Balanced", "Peaceful", "Unifying", "Graceful"],
        "MBTI": "INFJ", "Enneagram": "9w1",
        "Description": "Goddess of harmony and concord, daughter of Ares and Aphrodite, reconciling war and love"
    },

    "Philotes": {
        "CommonAliases": ["Affection", "Friendship", "Love"],
        "ArchetypalFunction": "To embody affection, friendship, and love between beings",
        "SymbolicCore": "The bonds of friendship and familial love",
        "Element": "Air", "Planet": "Venus", "Chakra": "Heart",
        "Color": "Warm Pink", "Animal": "Paired doves",
        "Other": ["Clasped hands", "Heart", "Bond"],
        "NarrativeFunction": ["Friend", "Connector", "Love-bringer"],
        "CoreTraits": ["Affectionate", "Warm", "Connecting", "Loyal"],
        "MBTI": "ESFJ", "Enneagram": "2w3",
        "Description": "Personification of affection, friendship, and sexual love"
    },

    "Eleos": {
        "CommonAliases": ["Mercy", "Pity", "Compassion", "Clementia"],
        "ArchetypalFunction": "To embody mercy, compassion, and pity for the suffering",
        "SymbolicCore": "Divine compassion, the softening of justice with mercy",
        "Element": "Water", "Planet": "Moon", "Chakra": "Heart",
        "Color": "Soft White, Blue", "Animal": "Lamb",
        "Other": ["Tears", "Altar of mercy", "Supplicant's branch"],
        "NarrativeFunction": ["Merciful one", "Compassionate", "Protector of supplicants"],
        "CoreTraits": ["Compassionate", "Merciful", "Gentle", "Protective"],
        "MBTI": "INFP", "Enneagram": "2w1",
        "Description": "Spirit of mercy and compassion, had an altar in Athens for supplicants"
    },

    "Eirene": {
        "CommonAliases": ["Peace", "Pax", "Tranquility"],
        "ArchetypalFunction": "To bring peace, prosperity through peace, and end to conflict",
        "SymbolicCore": "The blessed state of peace and its fruits",
        "Element": "Earth", "Planet": "Venus", "Chakra": "Heart",
        "Color": "White, Green", "Animal": "Dove",
        "Other": ["Olive branch", "Cornucopia", "Scepter", "Torch"],
        "NarrativeFunction": ["Peacemaker", "Prosperity-bringer", "Protector"],
        "CoreTraits": ["Peaceful", "Prosperous", "Nurturing", "Calm"],
        "MBTI": "ISFJ", "Enneagram": "9w1",
        "Description": "Goddess of peace, one of the Horae, brings prosperity through peace"
    },

    "Dike": {
        "CommonAliases": ["Justice", "Fair Judgment", "Moral Order"],
        "ArchetypalFunction": "To embody moral justice, fair judgment, and righteous order",
        "SymbolicCore": "Divine justice as moral and ethical principle",
        "Element": "Air", "Planet": "Jupiter", "Chakra": "Third Eye",
        "Color": "Purple, Gold", "Animal": "Scales",
        "Other": ["Scales of justice", "Sword", "Blindfold", "Measuring rod"],
        "NarrativeFunction": ["Judge", "Arbiter", "Upholder of Right"],
        "CoreTraits": ["Just", "Fair", "Moral", "Principled", "Stern"],
        "MBTI": "ISTJ", "Enneagram": "1w9",
        "Description": "Goddess of justice and moral order, one of the Horae, daughter of Zeus and Themis"
    },

    "Metis": {
        "CommonAliases": ["Wisdom", "Cunning Intelligence", "Prudence"],
        "ArchetypalFunction": "To embody cunning wisdom, strategic thought, and prudent counsel",
        "SymbolicCore": "The wisdom that combines intelligence with cunning",
        "Element": "Air", "Planet": "Mercury", "Chakra": "Third Eye",
        "Color": "Silver, Blue", "Animal": "Fox, Serpent",
        "Other": ["Scroll", "Labyrinth", "Mirror"],
        "NarrativeFunction": ["Counselor", "Strategist", "Wise advisor"],
        "CoreTraits": ["Wise", "Cunning", "Strategic", "Prudent", "Clever"],
        "MBTI": "INTJ", "Enneagram": "5w6",
        "Description": "Titaness of wisdom and cunning thought, first wife of Zeus, swallowed to prevent prophecy"
    },

    "Sophrosyne": {
        "CommonAliases": ["Temperance", "Moderation", "Self-control"],
        "ArchetypalFunction": "To embody self-control, moderation, and temperance in all things",
        "SymbolicCore": "The virtue of balanced restraint and self-mastery",
        "Element": "Earth", "Planet": "Saturn", "Chakra": "Solar Plexus",
        "Color": "Pale Blue", "Animal": "Measured creatures",
        "Other": ["Bridle", "Bit", "Measured cup"],
        "NarrativeFunction": ["Moderator", "Self-master", "Restraint"],
        "CoreTraits": ["Moderate", "Controlled", "Balanced", "Restrained", "Disciplined"],
        "MBTI": "ISTJ", "Enneagram": "1w9",
        "Description": "Spirit of moderation, self-control, and temperance, cardinal Greek virtue"
    },

    "Aidos": {
        "CommonAliases": ["Shame", "Modesty", "Reverence", "Honor"],
        "ArchetypalFunction": "To embody shame, modesty, and reverent respect for divine and social order",
        "SymbolicCore": "The moral shame that prevents wrongdoing",
        "Element": "Water", "Planet": "Saturn", "Chakra": "Throat",
        "Color": "Pale Pink, White", "Animal": "Veiled dove",
        "Other": ["Veil", "Downcast eyes", "Modest dress"],
        "NarrativeFunction": ["Conscience", "Moral restraint", "Honor-keeper"],
        "CoreTraits": ["Modest", "Reverent", "Honorable", "Restrained", "Shy"],
        "MBTI": "ISFJ", "Enneagram": "9w1",
        "Description": "Spirit of modesty, shame, and reverence, fled humanity in the Iron Age with Nemesis"
    },

    "Hybris": {
        "CommonAliases": ["Hubris", "Insolence", "Arrogance", "Petulance"],
        "ArchetypalFunction": "To embody excessive pride, arrogance, and violent transgression",
        "SymbolicCore": "The destructive pride that defies gods and natural order",
        "Element": "Fire", "Planet": "Mars", "Chakra": "Solar Plexus (distorted)",
        "Color": "Crimson, Black", "Animal": "Bull, Ram",
        "Other": ["Raised fist", "Crown", "Broken limits"],
        "NarrativeFunction": ["Transgressor", "Arrogant one", "Boundary-breaker"],
        "CoreTraits": ["Arrogant", "Insolent", "Violent", "Prideful", "Destructive"],
        "MBTI": "ESTP", "Enneagram": "8w7",
        "Description": "Spirit of hubris, insolence, and outrageous behavior, leads to divine punishment"
    },

    "Ate": {
        "CommonAliases": ["Delusion", "Ruin", "Folly", "Blind Recklessness"],
        "ArchetypalFunction": "To embody delusion, reckless folly, and the ruin that follows hubris",
        "SymbolicCore": "The madness sent by gods that leads to destruction",
        "Element": "Air (chaotic)", "Planet": "None", "Chakra": "Third Eye (clouded)",
        "Color": "Murky Gray, Red", "Animal": "Moth to flame",
        "Other": ["Blindfold", "Precipice", "Whirlwind"],
        "NarrativeFunction": ["Deluder", "Ruin-bringer", "Madness"],
        "CoreTraits": ["Delusional", "Reckless", "Ruinous", "Blinding", "Destructive"],
        "MBTI": "ENTP", "Enneagram": "7w8",
        "Description": "Goddess of delusion, ruin, and folly, cast from Olympus by Zeus, causes destructive madness"
    },

    # MINOR GODS (6)
    "Priapus": {
        "CommonAliases": ["Fertility God", "Garden Guardian", "Rustic God"],
        "ArchetypalFunction": "To embody male fertility, garden protection, and rustic sexuality",
        "SymbolicCore": "Exaggerated masculine fertility and protective power",
        "Element": "Earth", "Planet": "None", "Chakra": "Sacral",
        "Color": "Red, Brown", "Animal": "Donkey, Goat",
        "Other": ["Sickle", "Oversized phallus", "Fruit basket"],
        "NarrativeFunction": ["Protector", "Fertility god", "Rustic deity"],
        "CoreTraits": ["Fertile", "Protective", "Rustic", "Humorous", "Powerful"],
        "MBTI": "ESTP", "Enneagram": "8w7",
        "Description": "Minor rustic fertility god with exaggerated masculine features, protector of gardens and livestock"
    },

    "Adonis": {
        "CommonAliases": ["Beautiful Youth", "Dying God", "Beloved of Aphrodite"],
        "ArchetypalFunction": "To embody masculine beauty, youth, death and rebirth in nature",
        "SymbolicCore": "The beautiful mortal beloved by goddess, seasonal death and renewal",
        "Element": "Earth", "Planet": "Venus", "Chakra": "Heart",
        "Color": "Rose Red, Green", "Animal": "Boar",
        "Other": ["Anemone flower", "Myrrh tree", "Hunt"],
        "NarrativeFunction": ["Beloved", "Dying god", "Seasonal cycle"],
        "CoreTraits": ["Beautiful", "Youthful", "Passionate", "Tragic", "Cyclical"],
        "MBTI": "ISFP", "Enneagram": "4w3",
        "Description": "Mortal of exceptional beauty, beloved of Aphrodite and Persephone, killed by boar, reborn seasonally"
    },

    "Plutus": {
        "CommonAliases": ["Wealth", "Abundance", "Prosperity"],
        "ArchetypalFunction": "To embody agricultural wealth, abundance, and material prosperity",
        "SymbolicCore": "The wealth that comes from the earth's abundance",
        "Element": "Earth", "Planet": "Jupiter", "Chakra": "Root",
        "Color": "Gold, Green", "Animal": "None",
        "Other": ["Cornucopia", "Grain sheaf", "Gold coins"],
        "NarrativeFunction": ["Wealth-giver", "Abundance", "Prosperity"],
        "CoreTraits": ["Abundant", "Generous", "Prosperous", "Blind (distributes randomly)"],
        "MBTI": "ESFJ", "Enneagram": "2w3",
        "Description": "God of agricultural wealth and abundance, son of Demeter, often depicted as blind"
    },

    "Panacea": {
        "CommonAliases": ["Universal Remedy", "Cure-All", "Healer"],
        "ArchetypalFunction": "To embody universal healing, the cure for all ailments",
        "SymbolicCore": "The remedy that heals all wounds and diseases",
        "Element": "Water", "Planet": "Moon", "Chakra": "Heart",
        "Color": "White, Green", "Animal": "Serpent (healing)",
        "Other": ["Potion", "Bowl", "Herbs", "Medicine jar"],
        "NarrativeFunction": ["Healer", "Medicine-maker", "Cure-bringer"],
        "CoreTraits": ["Healing", "Nurturing", "Compassionate", "Skillful"],
        "MBTI": "INFJ", "Enneagram": "2w1",
        "Description": "Goddess of universal remedy and healing, daughter of Asclepius"
    },

    "Hygieia": {
        "CommonAliases": ["Health", "Hygiene", "Cleanliness", "Salus"],
        "ArchetypalFunction": "To embody health, cleanliness, and sanitation",
        "SymbolicCore": "Preventive health through cleanliness and right living",
        "Element": "Water", "Planet": "Moon", "Chakra": "Solar Plexus",
        "Color": "White, Blue", "Animal": "Serpent (entwined on bowl)",
        "Other": ["Bowl", "Snake", "Water vessel", "Cleaning implements"],
        "NarrativeFunction": ["Health-keeper", "Protector", "Purifier"],
        "CoreTraits": ["Clean", "Orderly", "Protective", "Preventive", "Pure"],
        "MBTI": "ISTJ", "Enneagram": "1w2",
        "Description": "Goddess of health, cleanliness, and sanitation, daughter of Asclepius"
    },

    "Asclepius": {
        "CommonAliases": ["God of Medicine", "Healer", "Physician", "Aesculapius"],
        "ArchetypalFunction": "To embody healing arts, medicine, and the physician's skill",
        "SymbolicCore": "Divine healing through knowledge and skill",
        "Element": "Earth", "Planet": "Sun/Mercury", "Chakra": "Heart",
        "Color": "White, Green", "Animal": "Serpent, Rooster",
        "Other": ["Rod of Asclepius", "Snake-entwined staff", "Herbs"],
        "NarrativeFunction": ["Healer", "Physician", "Teacher"],
        "CoreTraits": ["Healing", "Knowledgeable", "Skillful", "Compassionate", "Powerful"],
        "MBTI": "INFJ", "Enneagram": "5w6",
        "Description": "God of medicine and healing, son of Apollo, raised the dead, struck down by Zeus, became constellation"
    },

    # NATURE SPIRITS (6)
    "Silenus": {
        "CommonAliases": ["Foster-father of Dionysus", "Drunken sage", "Satyr elder"],
        "ArchetypalFunction": "To embody wise drunkenness, rustic wisdom, and divine madness",
        "SymbolicCore": "The wisdom found in intoxication and wild nature",
        "Element": "Earth", "Planet": "None", "Chakra": "Sacral",
        "Color": "Purple, Brown", "Animal": "Donkey, Goat",
        "Other": ["Wine cup", "Thyrsus", "Grape vine"],
        "NarrativeFunction": ["Mentor", "Companion", "Wise fool"],
        "CoreTraits": ["Wise", "Drunk", "Jovial", "Prophetic", "Wild"],
        "MBTI": "ENTP", "Enneagram": "7w8",
        "Description": "Companion and tutor of Dionysus, eldest satyr, possessed prophetic wisdom when drunk"
    },

    "Satyrs": {
        "CommonAliases": ["Nature spirits", "Woodland creatures", "Dionysian followers"],
        "ArchetypalFunction": "To embody wild masculine sexuality, revelry, and untamed nature",
        "SymbolicCore": "The instinctual, lustful, and wild aspects of nature",
        "Element": "Earth", "Planet": "None", "Chakra": "Sacral/Root",
        "Color": "Brown, Green", "Animal": "Goat (half-goat)",
        "Other": ["Pan pipes", "Wine", "Thyrsus"],
        "NarrativeFunction": ["Revelers", "Companions", "Lustful pursuers"],
        "CoreTraits": ["Wild", "Lustful", "Musical", "Playful", "Untamed"],
        "MBTI": "ESFP", "Enneagram": "7w8",
        "Description": "Male nature spirits, half-man half-goat, companions of Dionysus, embodying wild revelry and lust"
    },

    "Nymphs": {
        "CommonAliases": ["Nature spirits", "Maidens of nature", "Divine attendants"],
        "ArchetypalFunction": "To embody feminine beauty, fertility of nature, and natural locations",
        "SymbolicCore": "The living spirit and beauty of natural places",
        "Element": "Water/Earth/Air", "Planet": "Moon/Venus", "Chakra": "Heart/Sacral",
        "Color": "Green, Blue, White", "Animal": "Varies by type",
        "Other": ["Flowing garments", "Flowers", "Streams", "Trees"],
        "NarrativeFunction": ["Attendants", "Lovers", "Protectors of nature"],
        "CoreTraits": ["Beautiful", "Playful", "Alluring", "Nature-bound", "Long-lived"],
        "MBTI": "ISFP", "Enneagram": "4w3",
        "Description": "Female nature spirits inhabiting specific locations, attendants of greater gods"
    },

    "Dryads": {
        "CommonAliases": ["Tree nymphs", "Oak maidens", "Forest spirits"],
        "ArchetypalFunction": "To embody the spirit of trees, forest life, and woodland sanctity",
        "SymbolicCore": "The living soul of trees and forests",
        "Element": "Earth/Wood", "Planet": "Moon", "Chakra": "Heart/Root",
        "Color": "Green, Brown", "Animal": "Deer, birds",
        "Other": ["Oak tree", "Leaves", "Acorns", "Forest"],
        "NarrativeFunction": ["Tree spirits", "Forest guardians", "Nature protectors"],
        "CoreTraits": ["Shy", "Beautiful", "Connected to trees", "Protective", "Gentle"],
        "MBTI": "ISFP", "Enneagram": "9w1",
        "Description": "Tree nymphs, especially of oak trees, lived and died with their tree"
    },

    "Oreads": {
        "CommonAliases": ["Mountain nymphs", "Highland spirits", "Peak maidens"],
        "ArchetypalFunction": "To embody the spirit of mountains, caves, and highland places",
        "SymbolicCore": "The wild freedom and majesty of mountain heights",
        "Element": "Earth/Air", "Planet": "Moon", "Chakra": "Crown/Root",
        "Color": "Gray, White, Sky blue", "Animal": "Mountain goat, eagle",
        "Other": ["Mountain peaks", "Caves", "Echo", "Heights"],
        "NarrativeFunction": ["Mountain spirits", "Companions of Artemis", "Wild maidens"],
        "CoreTraits": ["Wild", "Free", "Athletic", "Independent", "Elusive"],
        "MBTI": "ISTP", "Enneagram": "7w8",
        "Description": "Mountain nymphs, companions of Artemis, embodying wild mountain places"
    },

    "Naiads": {
        "CommonAliases": ["Water nymphs", "Spring maidens", "River spirits"],
        "ArchetypalFunction": "To embody freshwater sources, springs, rivers, and their life-giving power",
        "SymbolicCore": "The feminine flow and nurturing of fresh waters",
        "Element": "Water", "Planet": "Moon", "Chakra": "Sacral/Heart",
        "Color": "Blue, Aqua, Silver", "Animal": "Fish, otter",
        "Other": ["Water vessel", "Reeds", "Flowing hair", "Springs"],
        "NarrativeFunction": ["Water spirits", "Nurturers", "Healers"],
        "CoreTraits": ["Flowing", "Nurturing", "Beautiful", "Healing", "Playful"],
        "MBTI": "INFP", "Enneagram": "2w3",
        "Description": "Freshwater nymphs presiding over springs, fountains, streams, and rivers"
    }
}

def generate_full_entry(name, data):
    """Generate complete JSON entry"""
    return {
        "SchemaVersion": "1.1-ter",
        "ArchetypeName": name,
        "SystemOfOrigin": "GR",
        "CulturalLineage": ["Greek"],
        "CommonAliases": data.get("CommonAliases", []),
        "SymbolicEssence": {
            "ArchetypalFunction": data.get("ArchetypalFunction", ""),
            "PrimaryDomain": "Mythic",
            "ToneOrPolarity": "",
            "SymbolicCore": data.get("SymbolicCore", ""),
            "Correspondences": {
                "Element": data.get("Element", ""),
                "Planet": data.get("Planet", ""),
                "Chakra": data.get("Chakra", ""),
                "Color": data.get("Color", ""),
                "Animal": data.get("Animal", ""),
                "Other": data.get("Other", [])
            }
        },
        "NarrativeRoles": {
            "NarrativeFunction": data.get("NarrativeFunction", []),
            "ComplementaryArchetypes": [],
            "ShadowForms": [],
            "DevelopmentalArc": [],
            "CyclePhase": ""
        },
        "PsychologicalMapping": {
            "CoreTraits": data.get("CoreTraits", []),
            "Typologies": {
                "MBTI": data.get("MBTI", ""),
                "Enneagram": data.get("Enneagram", ""),
                "Other": []
            },
            "SubVariants": [],
            "InternalFamily": ""
        },
        "CulturalContext": {
            "Regions": ["Greece", "Mediterranean"],
            "MythicAppearances": [],
            "ReligiousOrRitualUse": "Ancient Greek religious worship and mythology",
            "HistoricalEvolution": "From oral tradition to written mythology",
            "SyncreticForms": []
        },
        "SymbolicRepresentation": {
            "SigilOrGlyph": "",
            "ImageryNotes": data.get("Description", ""),
            "ArtisticExamples": ["Greek pottery", "Classical sculpture"],
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

# Generate entries
output_dir = r"C:\Users\User\Documents\0000000\Archetypal Context Protocol\generated_greek"
os.makedirs(output_dir, exist_ok=True)

count = 0
for name, data in greek_archetypes_batch2.items():
    entry = generate_full_entry(name, data)
    output_file = os.path.join(output_dir, f"[GR] {name}.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(entry, f, indent=2, ensure_ascii=False)
    count += 1
    print(f"[X] Generated: {name}")

print(f"\n{count} additional entries generated")
print(f"Total in generated_greek: Check directory for count")
