import json
import os
from collections import defaultdict

def merge_quran_datasets():
    """
    Merges Quranic text/translations with Tafsir Ibn Kathir into a single 
    hierarchical JSON file specifically for the AI Search Engine.
    """
    
    # --- Configuration ---
    # Input files (Ensure these match your uploaded filenames)
    quran_path = 'final_quran_translations.json'
    tafsir_path = 'final_quran_tafsir.json'
    
    # Output file
    output_path = 'quran_complete.json'

    print("--- Quran Data Merge Tool ---")

    # 1. Load Quran Data (Flat List Source)
    print(f"Loading Quran text from {quran_path}...")
    if not os.path.exists(quran_path):
        print(f"❌ Error: File '{quran_path}' not found.")
        return
    
    with open(quran_path, 'r', encoding='utf-8') as f:
        quran_data = json.load(f)

    # 2. Load Tafsir Data (Flat List Source)
    print(f"Loading Tafsir from {tafsir_path}...")
    if not os.path.exists(tafsir_path):
        print(f"❌ Error: File '{tafsir_path}' not found. Treating all tafsir as empty.")
        tafsir_data_list = []
    else:
        with open(tafsir_path, 'r', encoding='utf-8') as f:
            tafsir_data_list = json.load(f)

    print("Indexing Tafsir data...")
    # Convert Tafsir list to a Dictionary for fast O(1) lookup
    # Key: "SurahID:AyahID" -> Value: {en, ur}
    tafsir_map = {}
    for item in tafsir_data_list:
        key = f"{item.get('surah_no')}:{item.get('ayah_no')}"
        tafsir_map[key] = {
            "en": item.get("english_tafseer", ""),
            "ur": item.get("urdu_tafseer", "")
        }

    print("Merging datasets...")

    # 3. Initialize Final Structure
    final_output = {
        "metadata": {
            "dataset_name": "Quran with Multilingual Tafseer",
            "tafsir_source": "Ibn Kathir",
            "languages": ["ar", "en", "ur"],
            "version": "1.0"
        },
        "surahs": []
    }

    # 4. Processing Loop
    # Group the flat Quran verses by Surah ID
    surahs_map = defaultdict(list)
    for verse in quran_data:
        s_id = verse.get("surah_no")
        surahs_map[s_id].append(verse)

    # Sort Surahs by ID (1 to 114)
    sorted_ids = sorted(surahs_map.keys())

    for surah_id in sorted_ids:
        verses_list = surahs_map[surah_id]
        # Ensure verses are sorted by Ayah number
        verses_list.sort(key=lambda x: x.get("ayah_no"))

        # Extract Surah metadata from the first verse
        first_verse = verses_list[0]
        surah_name_en = first_verse.get("surah_name", "")
        
        # Construct the Surah Object
        new_surah = {
            "id": surah_id,
            "name_ar": "",  # Arabic name not present in flat source, leaving empty
            "name_en": surah_name_en,
            "type": "Unknown", # Type (Meccan/Medinan) not present in flat source
            "total_verses": len(verses_list),
            "verses": []
        }

        # Process Verses
        for verse in verses_list:
            ayah_id = verse.get("ayah_no")
            
            # Construct lookup key for Tafsir: "SurahID:AyahID"
            tafsir_key = f"{surah_id}:{ayah_id}"
            
            # Fetch Tafsir entry
            t_data = tafsir_map.get(tafsir_key, {})

            # Construct the Verse Object
            new_verse = {
                "ayah": ayah_id,
                
                "arabic": {
                    "text": verse.get("arabic_text", "")
                },

                "translations": {
                    "en": verse.get("english_translation", ""),
                    "ur": verse.get("urdu_translation", "")
                },

                "tafsir": {
                    "source": "Ibn Kathir",
                    "ar": "", # Arabic tafsir not present in source
                    "en": t_data.get("en", ""),
                    "ur": t_data.get("ur", "")
                }
            }

            new_surah["verses"].append(new_verse)

        # Add Surah to Final Output
        final_output["surahs"].append(new_surah)
        
        if surah_id % 10 == 0:
            print(f"Processed Surah {surah_id}...")

    # 5. Write Output
    print(f"Writing merged data to {output_path}...")
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            # ensure_ascii=False is CRITICAL for Arabic/Urdu readability
            json.dump(final_output, f, ensure_ascii=False, indent=2)
        print("✅ Success! 'quran_complete.json' has been created.")
        
    except Exception as e:
        print(f"❌ Error writing file: {e}")

if __name__ == "__main__":
    merge_quran_datasets()