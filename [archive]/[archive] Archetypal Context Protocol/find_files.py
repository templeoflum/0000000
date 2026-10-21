import os

base_path = r"C:\Users\User\Documents\0000000\Archetypal Context Protocol"

print("Searching for all .docx files...")
for root, dirs, files in os.walk(base_path):
    for file in files:
        if file.endswith('.docx'):
            full_path = os.path.join(root, file)
            print(full_path)
