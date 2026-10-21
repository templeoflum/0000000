import json
import os

# Heroes and mythological figures - final batch
greek_heroes = {
    "Psyche": {
        "CommonAliases": ["Soul", "Butterfly maiden", "Beloved of Eros"],
        "ArchetypalFunction": "To embody the soul's journey through trials to divine love",
        "SymbolicCore": "The mortal soul seeking union with divine love",
        "Element": "Air", "Planet": "Venus", "Chakra": "Heart",
        "Color": "Iridescent, Pink", "Animal": "Butterfly",
        "Other": ["Lamp", "Oil jar", "Butterfly wings"],
        "NarrativeFunction": ["Questing soul", "Bride", "Initiate"],
        "CoreTraits": ["Curious", "Determined", "Beautiful", "Questing", "Transforming"],
        "MBTI": "INFP", "Enneagram": "4w5",
        "Description": "Mortal woman of surpassing beauty, wife of Eros, underwent trials, became goddess of the soul"
    },

    "Hebe": {
        "CommonAliases": ["Youth", "Cupbearer", "Juventas"],
        "ArchetypalFunction": "To embody eternal youth, vitality, and rejuvenation",
        "SymbolicCore": "The bloom of youth that never fades",
        "Element": "Air", "Planet": "Venus/Jupiter", "Chakra": "Heart",
        "Color": "Fresh pink, Spring green", "Animal": "Young dove",
        "Other": ["Cup of nectar", "Fountain of youth", "Fresh flowers"],
        "NarrativeFunction": ["Cupbearer", "Eternal youth", "Bride of Heracles"],
        "CoreTraits": ["Youthful", "Vital", "Joyful", "Fresh", "Radiant"],
        "MBTI": "ESFP", "Enneagram": "7w6",
        "Description": "Goddess of youth, daughter of Zeus and Hera, cupbearer to the gods, wife of deified Heracles"
    },

    "Ganymede": {
        "CommonAliases": ["Zeus's cupbearer", "Divine youth", "Aquarius"],
        "ArchetypalFunction": "To embody divine beauty, immortalized youth, and elevated service",
        "SymbolicCore": "The mortal elevated to immortal service through beauty",
        "Element": "Air/Water", "Planet": "Jupiter", "Chakra": "Crown",
        "Color": "Sky blue, Gold", "Animal": "Eagle",
        "Other": ["Cup", "Eagle (Zeus's form)", "Wine pitcher"],
        "NarrativeFunction": ["Cupbearer", "Divine beloved", "Constellation"],
        "CoreTraits": ["Beautiful", "Youthful", "Elevated", "Serving", "Immortalized"],
        "MBTI": "ISFP", "Enneagram": "4w3",
        "Description": "Most beautiful of mortals, abducted by Zeus as eagle, became immortal cupbearer, constellation Aquarius"
    },

    "Narcissus": {
        "CommonAliases": ["Self-lover", "Beautiful youth", "Flower-transformed"],
        "ArchetypalFunction": "To embody self-love, vanity, and the tragedy of self-absorption",
        "SymbolicCore": "The soul trapped in self-reflection, unable to love another",
        "Element": "Water", "Planet": "Venus (distorted)", "Chakra": "Solar Plexus",
        "Color": "White, Yellow", "Animal": "Reflection",
        "Other": ["Mirror", "Pool", "Narcissus flower", "Reflection"],
        "NarrativeFunction": ["Tragic figure", "Self-absorbed", "Transformation"],
        "CoreTraits": ["Beautiful", "Vain", "Self-absorbed", "Tragic", "Transformed"],
        "MBTI": "ISFP", "Enneagram": "3w4",
        "Description": "Beautiful youth who rejected all love, fell in love with his own reflection, died gazing at it, became flower"
    },

    "Echo": {
        "CommonAliases": ["Nymph of sound", "Repeater", "Fading voice"],
        "ArchetypalFunction": "To embody unrequited love, loss of voice, and the tragedy of repetition",
        "SymbolicCore": "The voice that can only repeat, never originate",
        "Element": "Air", "Planet": "None", "Chakra": "Throat (blocked)",
        "Color": "Fading colors", "Animal": "Echo bird",
        "Other": ["Mountains (for echo)", "Fading form", "Voice"],
        "NarrativeFunction": ["Tragic lover", "Cursed one", "Repeater"],
        "CoreTraits": ["Talkative (then silenced)", "Loving", "Rejected", "Fading", "Repeating"],
        "MBTI": "ENFP", "Enneagram": "2w3",
        "Description": "Mountain nymph cursed to only repeat others' words, loved Narcissus unrequited, faded to only voice"
    },

    "Galatea": {
        "CommonAliases": ["Living statue", "Ivory maiden", "Beloved sculpture"],
        "ArchetypalFunction": "To embody the ideal brought to life, art become flesh through love",
        "SymbolicCore": "The perfect creation animated by divine grace and love",
        "Element": "Earth", "Planet": "Venus", "Chakra": "Heart",
        "Color": "Ivory white, Rose", "Animal": "Dove",
        "Other": ["Sculpture", "Ivory", "Transformation", "Breath of life"],
        "NarrativeFunction": ["Ideal made real", "Beloved", "Creation come alive"],
        "CoreTraits": ["Perfect", "Beautiful", "Animated", "Grateful", "Loving"],
        "MBTI": "ISFJ", "Enneagram": "2w1",
        "Description": "Ivory statue created by Pygmalion, brought to life by Aphrodite, embodiment of ideal woman"
    },

    "Pygmalion": {
        "CommonAliases": ["Sculptor king", "Creator of ideal", "Artist lover"],
        "ArchetypalFunction": "To embody artistic devotion, creation of the ideal, and love of one's work",
        "SymbolicCore": "The artist who falls in love with his own creation",
        "Element": "Earth", "Planet": "Venus", "Chakra": "Heart/Sacral",
        "Color": "Marble white, Artist's palette", "Animal": "None",
        "Other": ["Chisel", "Sculpture", "Ivory", "Tools"],
        "NarrativeFunction": ["Artist", "Creator", "Devotee"],
        "CoreTraits": ["Artistic", "Devoted", "Idealistic", "Passionate", "Creative"],
        "MBTI": "INFP", "Enneagram": "4w5",
        "Description": "King and sculptor who carved ideal woman from ivory, fell in love with it, Aphrodite brought it to life"
    },

    "Hermaphroditus": {
        "CommonAliases": ["Dual-gendered", "United form", "Child of Hermes and Aphrodite"],
        "ArchetypalFunction": "To embody the union of masculine and feminine, dual nature",
        "SymbolicCore": "The sacred marriage of opposites in one form",
        "Element": "Water", "Planet": "Mercury/Venus", "Chakra": "Sacral",
        "Color": "Merged pink and blue", "Animal": "Dual creatures",
        "Other": ["Pool", "Merged form", "Unity symbol"],
        "NarrativeFunction": ["United being", "Transformation", "Duality"],
        "CoreTraits": ["Dual-natured", "Beautiful", "Transformed", "United", "Complete"],
        "MBTI": "INFP", "Enneagram": "4w5",
        "Description": "Son of Hermes and Aphrodite, merged with water nymph Salmacis, became dual-gendered being"
    },

    "Hyacinthus": {
        "CommonAliases": ["Beloved of Apollo", "Flower youth", "Spartan prince"],
        "ArchetypalFunction": "To embody beautiful youth, divine love, and tragic accidental death",
        "SymbolicCore": "The beautiful mortal beloved by gods, transformed in death",
        "Element": "Air/Earth", "Planet": "Sun", "Chakra": "Heart",
        "Color": "Purple, Blue", "Animal": "None",
        "Other": ["Discus", "Hyacinth flower", "Blood drops", "AI AI (flower marking)"],
        "NarrativeFunction": ["Beloved", "Tragic youth", "Transformed"],
        "CoreTraits": ["Beautiful", "Athletic", "Beloved", "Tragic", "Commemorated"],
        "MBTI": "ESFP", "Enneagram": "3w2",
        "Description": "Beautiful Spartan prince, beloved of Apollo, killed accidentally by discus, became hyacinth flower"
    },

    "Ariadne": {
        "CommonAliases": ["Mistress of the Labyrinth", "Theseus's helper", "Bride of Dionysus"],
        "ArchetypalFunction": "To embody helpful wisdom, betrayal and abandonment, and divine redemption",
        "SymbolicCore": "The wise helper who is betrayed but finds greater love",
        "Element": "Earth", "Planet": "Venus", "Chakra": "Heart",
        "Color": "Red, Purple", "Animal": "None",
        "Other": ["Thread ball", "Crown of stars", "Labyrinth"],
        "NarrativeFunction": ["Helper", "Betrayed lover", "Divine bride"],
        "CoreTraits": ["Wise", "Helpful", "Betrayed", "Resilient", "Elevated"],
        "MBTI": "INFJ", "Enneagram": "2w1",
        "Description": "Princess of Crete, gave Theseus thread to escape Labyrinth, abandoned by him, became wife of Dionysus"
    },

    "Daedalus": {
        "CommonAliases": ["Master craftsman", "Inventor", "Architect of the Labyrinth"],
        "ArchetypalFunction": "To embody supreme craftsmanship, innovation, and the dangers of invention",
        "SymbolicCore": "The brilliant mind whose creations bring both wonder and tragedy",
        "Element": "Air/Earth", "Planet": "Mercury", "Chakra": "Throat/Third Eye",
        "Color": "Bronze, Sky blue", "Animal": "None",
        "Other": ["Wings", "Tools", "Labyrinth", "Wax and feathers"],
        "NarrativeFunction": ["Inventor", "Craftsman", "Tragic father"],
        "CoreTraits": ["Brilliant", "Inventive", "Skillful", "Tragic", "Warning"],
        "MBTI": "INTP", "Enneagram": "5w6",
        "Description": "Greatest craftsman and inventor, built Labyrinth, created wings for escape, lost son Icarus to hubris"
    },

    "Icarus": {
        "CommonAliases": ["Fallen flyer", "Over-reacher", "Warned youth"],
        "ArchetypalFunction": "To embody youthful hubris, ignoring wise counsel, and tragic overreach",
        "SymbolicCore": "The youth who flies too close to the sun despite warnings",
        "Element": "Air/Fire", "Planet": "Sun (destructive)", "Chakra": "Solar Plexus",
        "Color": "Sky blue turning to fire", "Animal": "Falling bird",
        "Other": ["Wax wings", "Melted feathers", "The sun", "The sea"],
        "NarrativeFunction": ["Tragic youth", "Warning tale", "Hubris victim"],
        "CoreTraits": ["Youthful", "Ambitious", "Reckless", "Disobedient", "Tragic"],
        "MBTI": "ENFP", "Enneagram": "7w8",
        "Description": "Son of Daedalus, flew on wax wings, ignored warning, flew too close to sun, fell to death in sea"
    },

    "Theseus": {
        "CommonAliases": ["Hero of Athens", "Minotaur slayer", "King of Athens"],
        "ArchetypalFunction": "To embody heroic strength, cunning, and the founding hero of civilization",
        "SymbolicCore": "The hero who defeats monsters and founds civic order",
        "Element": "Earth/Fire", "Planet": "Mars", "Chakra": "Solar Plexus",
        "Color": "Royal blue, Bronze", "Animal": "Bull",
        "Other": ["Sword", "Thread", "Ship (with sails)", "Crown"],
        "NarrativeFunction": ["Hero", "Monster-slayer", "King", "Founder"],
        "CoreTraits": ["Heroic", "Strong", "Cunning", "Brave", "Flawed"],
        "MBTI": "ESTP", "Enneagram": "8w7",
        "Description": "Greatest Athenian hero, slew Minotaur, unified Attica, became king, complex moral character"
    },

    "Minotaur": {
        "CommonAliases": ["Bull of Minos", "Asterion", "Labyrinth beast"],
        "ArchetypalFunction": "To embody monstrous appetite, shameful secrets, and the beast within",
        "SymbolicCore": "The monster at the center of the labyrinth of shame",
        "Element": "Earth", "Planet": "Mars", "Chakra": "Root (distorted)",
        "Color": "Blood red, Dark brown", "Animal": "Bull (half)",
        "Other": ["Labyrinth", "Maze", "Horns", "Human sacrifice"],
        "NarrativeFunction": ["Monster", "Secret shame", "Sacrifice-devourer"],
        "CoreTraits": ["Monstrous", "Hungry", "Trapped", "Tragic", "Shameful"],
        "MBTI": "ISTP", "Enneagram": "8w9",
        "Description": "Half-man half-bull monster, offspring of Pasiphae and bull, imprisoned in Labyrinth, slain by Theseus"
    },

    "Medea": {
        "CommonAliases": ["Sorceress", "Betrayer", "Vengeful wife"],
        "ArchetypalFunction": "To embody magical power, passionate love turned to destructive vengeance",
        "SymbolicCore": "The wronged woman whose power destroys all she once loved",
        "Element": "Fire/Water", "Planet": "Mars/Pluto", "Chakra": "Solar Plexus/Sacral",
        "Color": "Deep crimson, Black", "Animal": "Dragon, Serpent",
        "Other": ["Cauldron", "Poisons", "Dragon chariot", "Knife"],
        "NarrativeFunction": ["Sorceress", "Helper", "Betrayer", "Avenger"],
        "CoreTraits": ["Powerful", "Passionate", "Vengeful", "Tragic", "Destructive"],
        "MBTI": "INTJ", "Enneagram": "8w7",
        "Description": "Powerful sorceress, helped Jason get Golden Fleece, betrayed by him, murdered their children in revenge"
    },

    "Circe": {
        "CommonAliases": ["Witch", "Enchantress", "Transformer"],
        "ArchetypalFunction": "To embody transformation magic, feminine power, and dangerous hospitality",
        "SymbolicCore": "The witch who transforms men into their true natures",
        "Element": "Water/Earth", "Planet": "Moon/Venus", "Chakra": "Sacral/Throat",
        "Color": "Purple, Green", "Animal": "Pig, Lion, Wolf",
        "Other": ["Wand", "Potion", "Loom", "Island"],
        "NarrativeFunction": ["Enchantress", "Transformer", "Dangerous host", "Lover"],
        "CoreTraits": ["Powerful", "Magical", "Transformative", "Dangerous", "Alluring"],
        "MBTI": "INTJ", "Enneagram": "8w9",
        "Description": "Powerful witch-goddess, transformed men into animals, held Odysseus for a year, mother of several heroes"
    },

    "Calypso": {
        "CommonAliases": ["Concealer", "Island nymph", "Divine captor"],
        "ArchetypalFunction": "To embody seductive captivity, offered immortality, and lonely longing",
        "SymbolicCore": "The beautiful captor offering paradise prison",
        "Element": "Water", "Planet": "Moon", "Chakra": "Heart",
        "Color": "Sea blue, Silver", "Animal": "Sea birds",
        "Other": ["Island", "Loom", "Cave", "Immortality offer"],
        "NarrativeFunction": ["Captor", "Lover", "Immortality-offerer"],
        "CoreTraits": ["Beautiful", "Lonely", "Captivating", "Immortal", "Longing"],
        "MBTI": "INFP", "Enneagram": "4w5",
        "Description": "Sea nymph, held Odysseus captive for seven years, offered immortality, forced to release him by Zeus"
    },

    "Cassandra": {
        "CommonAliases": ["Prophetess", "Unbelieved seer", "Cursed prophet"],
        "ArchetypalFunction": "To embody true prophecy never believed, the tragedy of unheeded wisdom",
        "SymbolicCore": "The voice of truth that no one believes",
        "Element": "Air", "Planet": "Saturn", "Chakra": "Third Eye/Throat",
        "Color": "Dark purple, Gray", "Animal": "Owl (unheard)",
        "Other": ["Temple", "Laurel", "Vision", "Cassandra complex"],
        "NarrativeFunction": ["Prophet", "Warner", "Tragic seer", "Victim"],
        "CoreTraits": ["Prophetic", "Unbelieved", "Tragic", "Truth-telling", "Cursed"],
        "MBTI": "INFJ", "Enneagram": "5w4",
        "Description": "Trojan princess, Apollo's priestess, cursed to prophesy truth but never be believed, enslaved after Troy's fall"
    },

    "Orpheus": {
        "CommonAliases": ["Divine musician", "Lyre-player", "Argonaut"],
        "ArchetypalFunction": "To embody divine music, power of art, and the tragedy of looking back",
        "SymbolicCore": "The artist who can move even death but cannot resist looking back",
        "Element": "Air", "Planet": "Venus/Mercury", "Chakra": "Throat/Heart",
        "Color": "Golden, Silver", "Animal": "Nightingale, Lyre bird",
        "Other": ["Lyre", "Music", "Descent to underworld", "Looking back"],
        "NarrativeFunction": ["Divine musician", "Lover", "Tragic hero", "Shaman"],
        "CoreTraits": ["Musical", "Loving", "Tragic", "Powerful", "Doomed"],
        "MBTI": "INFP", "Enneagram": "4w5",
        "Description": "Greatest musician, charmed all with music, descended to Hades for Eurydice, looked back and lost her forever"
    },

    "Eurydice": {
        "CommonAliases": ["Lost bride", "Wood nymph", "Orpheus's love"],
        "ArchetypalFunction": "To embody tragic love, untimely death, and the lost beloved",
        "SymbolicCore": "The beloved lost at the threshold of salvation",
        "Element": "Earth", "Planet": "Pluto", "Chakra": "Root",
        "Color": "Pale white, Fading", "Animal": "None",
        "Other": ["Snake bite", "Fading form", "Threshold", "Hades"],
        "NarrativeFunction": ["Tragic bride", "Lost beloved", "Shade"],
        "CoreTraits": ["Beautiful", "Tragic", "Loving", "Lost", "Fading"],
        "MBTI": "ISFP", "Enneagram": "9w1",
        "Description": "Dryad bride of Orpheus, died from snake bite on wedding day, almost rescued from Hades, lost when he looked back"
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
            "ReligiousOrRitualUse": "Ancient Greek mythology and legend",
            "HistoricalEvolution": "From oral tradition to written mythology",
            "SyncreticForms": []
        },
        "SymbolicRepresentation": {
            "SigilOrGlyph": "",
            "ImageryNotes": data.get("Description", ""),
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

# Generate entries
output_dir = r"C:\Users\User\Documents\0000000\Archetypal Context Protocol\generated_greek"
os.makedirs(output_dir, exist_ok=True)

count = 0
for name, data in greek_heroes.items():
    entry = generate_full_entry(name, data)
    output_file = os.path.join(output_dir, f"[GR] {name}.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(entry, f, indent=2, ensure_ascii=False)
    count += 1
    print(f"[X] Generated: {name}")

print(f"\n{count} hero/mythological figure entries generated")
print("Checking total...")

import glob
total = len(glob.glob(os.path.join(output_dir, "*.json")))
print(f"Total Greek archetypes generated: {total}")
