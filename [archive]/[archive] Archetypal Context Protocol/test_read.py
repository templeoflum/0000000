import os

test_path = r"C:\Users\User\Documents\0000000\Archetypal Context Protocol\converted_txt\[MSC] Modern Spiritual and Cultural\[HJ] Hero's Journey\[HJ] Hero.txt"
print(f"Testing: {test_path}")
print(f"Exists: {os.path.exists(test_path)}")

# Try to find it
base = r"C:\Users\User\Documents\0000000\Archetypal Context Protocol\converted_txt"
for root, dirs, files in os.walk(base):
    for f in files:
        if "Hero" in f and "Journey" in root:
            full_path = os.path.join(root, f)
            print(f"\nFound: {full_path}")
            # Read first 50 lines
            with open(full_path, 'r', encoding='utf-8') as file:
                for i, line in enumerate(file):
                    if i < 50:
                        print(line.rstrip())
                    else:
                        break
