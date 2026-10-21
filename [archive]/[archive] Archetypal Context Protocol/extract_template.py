import os
import json

# Read one of the Hero's Journey files to extract the template
base = r"C:\Users\User\Documents\0000000\Archetypal Context Protocol\converted_txt\[MSC] Modern Spiritual and Cultural"

# Find Hero's Journey directory
for root, dirs, files in os.walk(base):
    if "Hero" in root and "Journey" in root:
        for filename in files:
            if "Hero.txt" in filename:
                filepath = os.path.join(root, filename)
                print(f"Reading: {filepath}")

                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Extract JSON
                start = content.find('{')
                if start != -1:
                    # Find matching closing brace
                    brace_count = 0
                    in_json = False
                    json_str = ""

                    for char in content[start:]:
                        if char == '{':
                            brace_count += 1
                            in_json = True
                        elif char == '}':
                            brace_count -= 1

                        json_str += char

                        if in_json and brace_count == 0:
                            break

                    try:
                        parsed = json.loads(json_str)

                        # Save the template
                        output_path = r"C:\Users\User\Documents\0000000\Archetypal Context Protocol\ARCHETYPE_TEMPLATE.json"
                        with open(output_path, 'w', encoding='utf-8') as out:
                            json.dump(parsed, out, indent=2, ensure_ascii=False)

                        print(f"\nTemplate saved to: {output_path}")
                        print(f"\nTemplate Structure:")
                        print(json.dumps(parsed, indent=2, ensure_ascii=False))

                    except Exception as e:
                        print(f"Error parsing JSON: {e}")
                        print(f"JSON string: {json_str[:500]}")

                break
