import json
import os

def load_json(filepath):
    """Safely loads a JSON file with UTF-8 encoding."""
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return {}
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return {}

def get_sort_key(key_str):
    """Parses 'Surah:Ayah' keys into integers for accurate numerical sorting."""
    try:
        if isinstance(key_str, str) and ":" in key_str:
            parts = key_str.split(':')
            return int(parts[0]), int(parts[1])
        return (0, 0)
    except (ValueError, IndexError):
        return (0, 0)

def merge_tafsir():
    # Get the directory where THIS script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define paths relative to the script location
    # Going up one level from 'scripts' to 'data'
    data_dir = os.path.abspath(os.path.join(script_dir, ".."))
    
    en_path = os.path.join(data_dir, 'en-tafisr-ibn-kathir.json')
    ur_path = os.path.join(data_dir, 'tafseer-ibn-e-kaseer-urdu.json')
    output_path = os.path.join(data_dir, 'merged_tafsir_ibn_kathir.json')

    print(f"Looking for files in: {data_dir}")
    print("Reading JSON files...")
    en_data = load_json(en_path)
    ur_data = load_json(ur_path)

    if not en_data and not ur_data:
        print("Error: No data found. Please ensure the JSON files are in the 'data' folder.")
        return

    # Union of all keys from both databases
    all_keys = set(en_data.keys()) | set(ur_data.keys())
    
    # Sort keys by Surah and then Ayah number
    sorted_keys = sorted(list(all_keys), key=get_sort_key)

    merged_db = {}
    print(f"Merging {len(sorted_keys)} entries...")

    for key in sorted_keys:
        entry = {}

        # Handle English data
        if key in en_data:
            en_content = en_data[key]
            if isinstance(en_content, dict):
                entry['en'] = en_content.get('text', '')
            else:
                entry['en_ref'] = en_content
        
        # Handle Urdu data
        if key in ur_data:
            ur_content = ur_data[key]
            if isinstance(ur_content, dict):
                entry['ur'] = ur_content.get('text', '')
            else:
                entry['ur_ref'] = ur_content

        if entry:
            merged_db[key] = entry

    print(f"Writing merged database to {output_path}...")
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(merged_db, f, ensure_ascii=False, indent=4)
        print("Done! Database successfully merged.")
    except Exception as e:
        print(f"Failed to save merged file: {e}")

if __name__ == "__main__":
    merge_tafsir()