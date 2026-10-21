import os
import json
import re

base_path = r"C:\Users\User\Documents\0000000\Archetypal Context Protocol\converted_txt"

# Storage for inventory
inventory = {
    "completed": [],
    "incomplete": [],
    "systems": {}
}

def extract_json_entries(content):
    """Extract JSON archetype entries from file content"""
    entries = []
    # Look for JSON objects in the content
    # Pattern: lines starting with { or having "ArchetypeName"
    in_json = False
    current_json = []
    brace_count = 0

    for line in content.split('\n'):
        stripped = line.strip()
        if stripped.startswith('{'):
            in_json = True
            brace_count = stripped.count('{') - stripped.count('}')
            current_json = [line]
        elif in_json:
            current_json.append(line)
            brace_count += stripped.count('{') - stripped.count('}')
            if brace_count <= 0:
                in_json = False
                try:
                    json_str = '\n'.join(current_json)
                    parsed = json.loads(json_str)
                    if 'ArchetypeName' in parsed:
                        entries.append(parsed)
                except:
                    pass
                current_json = []

    return entries

def analyze_mythology_file(filepath, system_code):
    """Analyze a mythology/cultural file for completed vs incomplete"""
    completed = []
    incomplete = []

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Look for "Already done:" and "Need to be done:" sections
        done_match = re.search(r'Already done:(.*?)(?:Need to be done:|$)', content, re.DOTALL)
        need_match = re.search(r'Need to be done:(.*?)(?:$)', content, re.DOTALL)

        if done_match:
            done_section = done_match.group(1)
            # Extract entries like [GR] Zeus
            completed = re.findall(r'\[[\w]+\]\s+([^\n]+)', done_section)

        if need_match:
            need_section = need_match.group(1)
            incomplete = re.findall(r'\[[\w]+\]\s+([^\n]+)', need_section)

    except Exception as e:
        print(f"Error analyzing {filepath}: {e}")

    return completed, incomplete

def main():
    print("=" * 80)
    print("ARCHETYPAL CONTEXT PROTOCOL - COMPLETION INVENTORY")
    print("=" * 80)

    # Analyze Hero's Journey files (JSON format)
    hj_path = os.path.join(base_path, "[MSC] Modern Spiritual and Cultural", "[HJ] Hero's Journey")
    if os.path.exists(hj_path):
        hj_completed = []
        for filename in os.listdir(hj_path):
            if filename.endswith('.txt'):
                filepath = os.path.join(hj_path, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    entries = extract_json_entries(content)
                    for entry in entries:
                        name = entry.get('ArchetypeName', 'Unknown')
                        hj_completed.append(name)

        inventory['systems']['[HJ] Hero\'s Journey'] = {
            'completed': hj_completed,
            'incomplete': [],
            'total_completed': len(hj_completed),
            'total_incomplete': 0
        }
        print(f"\n[HJ] Hero's Journey: {len(hj_completed)} completed, 0 incomplete")
        for name in hj_completed:
            print(f"  [X] {name}")

    # Analyze Archetype JSON Library for completed entries
    json_lib_path = os.path.join(base_path, "Archetype JSON Library.txt")
    if os.path.exists(json_lib_path):
        print(f"\n\nAnalyzing Archetype JSON Library...")
        with open(json_lib_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract archetype names from headers like "Zeus: King of the Gods"
        headers = re.findall(r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*?):\s+', content, re.MULTILINE)
        print(f"Found {len(headers)} detailed entries in JSON Library:")
        for header in headers[:20]:  # Show first 20
            print(f"  [X] {header}")

    # Analyze mythology files
    myth_path = os.path.join(base_path, "[MYTH] Mythological and Cultural")
    if os.path.exists(myth_path):
        print(f"\n\n{'=' * 80}")
        print("MYTHOLOGICAL & CULTURAL SYSTEMS")
        print("=" * 80)

        total_completed = 0
        total_incomplete = 0

        for filename in sorted(os.listdir(myth_path)):
            if filename.endswith('.txt'):
                filepath = os.path.join(myth_path, filename)
                system_code = filename.replace('.txt', '')

                completed, incomplete = analyze_mythology_file(filepath, system_code)

                inventory['systems'][system_code] = {
                    'completed': completed,
                    'incomplete': incomplete,
                    'total_completed': len(completed),
                    'total_incomplete': len(incomplete)
                }

                total_completed += len(completed)
                total_incomplete += len(incomplete)

                print(f"\n{system_code}:")
                print(f"  Completed: {len(completed)}")
                print(f"  Incomplete: {len(incomplete)}")
                if len(incomplete) > 0:
                    print(f"  Completion: {len(completed)/(len(completed)+len(incomplete))*100:.1f}%")

    # Summary
    print(f"\n\n{'=' * 80}")
    print("SUMMARY")
    print("=" * 80)
    print(f"Total Systems: {len(inventory['systems'])}")
    print(f"Total Completed Archetypes: {total_completed}")
    print(f"Total Incomplete Archetypes: {total_incomplete}")
    if total_completed + total_incomplete > 0:
        print(f"Overall Completion: {total_completed/(total_completed+total_incomplete)*100:.1f}%")

    # Save detailed inventory to JSON
    output_file = os.path.join(os.path.dirname(base_path), "INVENTORY_LOG.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(inventory, f, indent=2, ensure_ascii=False)

    print(f"\n\nDetailed inventory saved to: {output_file}")

    # Create human-readable log
    log_file = os.path.join(os.path.dirname(base_path), "COMPLETION_STATUS.md")
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write("# Archetypal Context Protocol - Completion Status\n\n")
        f.write(f"**Last Updated:** {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("## Overall Summary\n\n")
        f.write(f"- **Total Systems:** {len(inventory['systems'])}\n")
        f.write(f"- **Total Completed Archetypes:** {total_completed}\n")
        f.write(f"- **Total Incomplete Archetypes:** {total_incomplete}\n")
        if total_completed + total_incomplete > 0:
            f.write(f"- **Overall Completion:** {total_completed/(total_completed+total_incomplete)*100:.1f}%\n")

        f.write("\n## System-by-System Breakdown\n\n")
        for system_name, data in sorted(inventory['systems'].items()):
            total = data['total_completed'] + data['total_incomplete']
            pct = (data['total_completed'] / total * 100) if total > 0 else 100
            f.write(f"### {system_name}\n\n")
            f.write(f"- **Completed:** {data['total_completed']}\n")
            f.write(f"- **Incomplete:** {data['total_incomplete']}\n")
            f.write(f"- **Completion:** {pct:.1f}%\n\n")

            if data['completed']:
                f.write("**Completed Entries:**\n")
                for entry in data['completed']:
                    f.write(f"- [X] {entry}\n")
                f.write("\n")

            if data['incomplete']:
                f.write("**Incomplete Entries:**\n")
                for entry in data['incomplete'][:10]:  # Show first 10
                    f.write(f"- [ ] {entry}\n")
                if len(data['incomplete']) > 10:
                    f.write(f"- ... and {len(data['incomplete']) - 10} more\n")
                f.write("\n")

    print(f"Human-readable log saved to: {log_file}")

if __name__ == "__main__":
    main()
