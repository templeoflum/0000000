import os

base_path = r"C:\Users\User\Documents\0000000\Archetypal Context Protocol"
test_file = os.path.join(base_path, "[MSC] Modern Spiritual and Cultural", "[HJ] Hero's Journey", "[HJ] Hero.docx")

print(f"Looking for: {test_file}")
print(f"File exists: {os.path.exists(test_file)}")
print(f"Is file: {os.path.isfile(test_file)}")

# List what's actually in the directory
hero_journey_dir = os.path.join(base_path, "[MSC] Modern Spiritual and Cultural", "[HJ] Hero's Journey")
if os.path.exists(hero_journey_dir):
    print(f"\nContents of {hero_journey_dir}:")
    for item in os.listdir(hero_journey_dir):
        print(f"  - {item}")
