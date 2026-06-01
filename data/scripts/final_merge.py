import json
import os
from collections import defaultdict

# --- STATIC METADATA FOR 114 SURAHS ---
# This dictionary fills in the missing 'name_ar' and 'type' fields
# that are absent in the flat translation files.
SURAH_META = {
    1: {"name_ar": "الفاتحة", "type": "Meccan"},
    2: {"name_ar": "البقرة", "type": "Medinan"},
    3: {"name_ar": "آل عمران", "type": "Medinan"},
    4: {"name_ar": "النساء", "type": "Medinan"},
    5: {"name_ar": "المائدة", "type": "Medinan"},
    6: {"name_ar": "الأنعام", "type": "Meccan"},
    7: {"name_ar": "الأعراف", "type": "Meccan"},
    8: {"name_ar": "الأنفال", "type": "Medinan"},
    9: {"name_ar": "التوبة", "type": "Medinan"},
    10: {"name_ar": "يونس", "type": "Meccan"},
    11: {"name_ar": "هود", "type": "Meccan"},
    12: {"name_ar": "يوسف", "type": "Meccan"},
    13: {"name_ar": "الرعد", "type": "Medinan"},
    14: {"name_ar": "ابراهيم", "type": "Meccan"},
    15: {"name_ar": "الحجر", "type": "Meccan"},
    16: {"name_ar": "النحل", "type": "Meccan"},
    17: {"name_ar": "الإسراء", "type": "Meccan"},
    18: {"name_ar": "الكهف", "type": "Meccan"},
    19: {"name_ar": "مريم", "type": "Meccan"},
    20: {"name_ar": "طه", "type": "Meccan"},
    21: {"name_ar": "الأنبياء", "type": "Meccan"},
    22: {"name_ar": "الحج", "type": "Medinan"},
    23: {"name_ar": "المؤمنون", "type": "Meccan"},
    24: {"name_ar": "النور", "type": "Medinan"},
    25: {"name_ar": "الفرقان", "type": "Meccan"},
    26: {"name_ar": "الشعراء", "type": "Meccan"},
    27: {"name_ar": "النمل", "type": "Meccan"},
    28: {"name_ar": "القصص", "type": "Meccan"},
    29: {"name_ar": "العنكبوت", "type": "Meccan"},
    30: {"name_ar": "الروم", "type": "Meccan"},
    31: {"name_ar": "لقمان", "type": "Meccan"},
    32: {"name_ar": "السجدة", "type": "Meccan"},
    33: {"name_ar": "الأحزاب", "type": "Medinan"},
    34: {"name_ar": "سبأ", "type": "Meccan"},
    35: {"name_ar": "فاطر", "type": "Meccan"},
    36: {"name_ar": "يس", "type": "Meccan"},
    37: {"name_ar": "الصافات", "type": "Meccan"},
    38: {"name_ar": "ص", "type": "Meccan"},
    39: {"name_ar": "الزمر", "type": "Meccan"},
    40: {"name_ar": "غافر", "type": "Meccan"},
    41: {"name_ar": "فصلت", "type": "Meccan"},
    42: {"name_ar": "الشورى", "type": "Meccan"},
    43: {"name_ar": "الزخرف", "type": "Meccan"},
    44: {"name_ar": "الدخان", "type": "Meccan"},
    45: {"name_ar": "الجاثية", "type": "Meccan"},
    46: {"name_ar": "الأحقاف", "type": "Meccan"},
    47: {"name_ar": "محمد", "type": "Medinan"},
    48: {"name_ar": "الفتح", "type": "Medinan"},
    49: {"name_ar": "الحجرات", "type": "Medinan"},
    50: {"name_ar": "ق", "type": "Meccan"},
    51: {"name_ar": "الذاريات", "type": "Meccan"},
    52: {"name_ar": "الطور", "type": "Meccan"},
    53: {"name_ar": "النجم", "type": "Meccan"},
    54: {"name_ar": "القمر", "type": "Meccan"},
    55: {"name_ar": "الرحمن", "type": "Medinan"},
    56: {"name_ar": "الواقعة", "type": "Meccan"},
    57: {"name_ar": "الحديد", "type": "Medinan"},
    58: {"name_ar": "المجادلة", "type": "Medinan"},
    59: {"name_ar": "الحشر", "type": "Medinan"},
    60: {"name_ar": "الممتحنة", "type": "Medinan"},
    61: {"name_ar": "الصف", "type": "Medinan"},
    62: {"name_ar": "الجمعة", "type": "Medinan"},
    63: {"name_ar": "المنافقون", "type": "Medinan"},
    64: {"name_ar": "التغابن", "type": "Medinan"},
    65: {"name_ar": "الطلاق", "type": "Medinan"},
    66: {"name_ar": "التحريم", "type": "Medinan"},
    67: {"name_ar": "الملك", "type": "Meccan"},
    68: {"name_ar": "القلم", "type": "Meccan"},
    69: {"name_ar": "الحاقة", "type": "Meccan"},
    70: {"name_ar": "المعارج", "type": "Meccan"},
    71: {"name_ar": "نوح", "type": "Meccan"},
    72: {"name_ar": "الجن", "type": "Meccan"},
    73: {"name_ar": "المزمل", "type": "Meccan"},
    74: {"name_ar": "المدثر", "type": "Meccan"},
    75: {"name_ar": "القيامة", "type": "Meccan"},
    76: {"name_ar": "الانسان", "type": "Medinan"},
    77: {"name_ar": "المرسلات", "type": "Meccan"},
    78: {"name_ar": "النبأ", "type": "Meccan"},
    79: {"name_ar": "النازعات", "type": "Meccan"},
    80: {"name_ar": "عبس", "type": "Meccan"},
    81: {"name_ar": "التكوير", "type": "Meccan"},
    82: {"name_ar": "الإنفطار", "type": "Meccan"},
    83: {"name_ar": "المطففين", "type": "Meccan"},
    84: {"name_ar": "الإنشقاق", "type": "Meccan"},
    85: {"name_ar": "البروج", "type": "Meccan"},
    86: {"name_ar": "الطارق", "type": "Meccan"},
    87: {"name_ar": "الأعلى", "type": "Meccan"},
    88: {"name_ar": "الغاشية", "type": "Meccan"},
    89: {"name_ar": "الفجر", "type": "Meccan"},
    90: {"name_ar": "البلد", "type": "Meccan"},
    91: {"name_ar": "الشمس", "type": "Meccan"},
    92: {"name_ar": "الليل", "type": "Meccan"},
    93: {"name_ar": "الضحى", "type": "Meccan"},
    94: {"name_ar": "الشرح", "type": "Meccan"},
    95: {"name_ar": "التين", "type": "Meccan"},
    96: {"name_ar": "العلق", "type": "Meccan"},
    97: {"name_ar": "القدر", "type": "Meccan"},
    98: {"name_ar": "البينة", "type": "Medinan"},
    99: {"name_ar": "الزلزلة", "type": "Medinan"},
    100: {"name_ar": "العاديات", "type": "Meccan"},
    101: {"name_ar": "القارعة", "type": "Meccan"},
    102: {"name_ar": "التكاثر", "type": "Meccan"},
    103: {"name_ar": "العصر", "type": "Meccan"},
    104: {"name_ar": "الهمزة", "type": "Meccan"},
    105: {"name_ar": "الفيل", "type": "Meccan"},
    106: {"name_ar": "قريش", "type": "Meccan"},
    107: {"name_ar": "الماعون", "type": "Meccan"},
    108: {"name_ar": "الكوثر", "type": "Meccan"},
    109: {"name_ar": "الكافرون", "type": "Meccan"},
    110: {"name_ar": "النصر", "type": "Medinan"},
    111: {"name_ar": "المسد", "type": "Meccan"},
    112: {"name_ar": "الإخلاص", "type": "Meccan"},
    113: {"name_ar": "الفلق", "type": "Meccan"},
    114: {"name_ar": "الناس", "type": "Meccan"}
}

def find_file(filename):
    """
    Locate file in common paths relative to script or CWD.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    candidates = [
        filename,                                      # CWD (Current Directory)
        os.path.join("data", filename),                # CWD/data
        os.path.join(script_dir, filename),            # Same folder as script
        os.path.join(script_dir, "..", filename),      # Parent of script (e.g., in data/)
        os.path.join(script_dir, "..", "data", filename) # Sibling data folder
    ]
    
    for path in candidates:
        if os.path.exists(path):
            return os.path.normpath(path)
    return filename # Return original to let logic fail with clear error if not found

def merge_quran_datasets():
    """
    Merges Quranic text/translations with Tafsir Ibn Kathir into a single 
    hierarchical JSON file.
    """
    
    print("--- Quran Data Merge Tool (Perfect Version) ---")

    # --- Configuration ---
    # Automatically locate files
    quran_path = find_file('final_quran_translations.json')
    tafsir_path = find_file('final_quran_tafsir.json')
    
    # Output file (Save to 'data' folder if it exists, otherwise current directory)
    output_dir = "data" if os.path.exists("data") else "."
    output_path = os.path.join(output_dir, 'quran_complete.json')

    # 1. Load Quran Data (Flat List Source)
    print(f"Loading Quran text from {quran_path}...")
    if not os.path.exists(quran_path):
        print(f"❌ Error: File '{quran_path}' not found.")
        print("   -> Please ensure 'final_quran_translations.json' is in the 'data' folder or current directory.")
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
        # Ensure IDs are integers for consistent keys
        s = int(item.get('surah_no', 0))
        a = int(item.get('ayah_no', 0))
        key = f"{s}:{a}"
        
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
        # Cast to int to ensure sorting and grouping works correctly
        s_id = int(verse.get("surah_no", 0))
        if s_id > 0:
            surahs_map[s_id].append(verse)

    # Sort Surahs by ID (1 to 114)
    sorted_ids = sorted(surahs_map.keys())

    for surah_id in sorted_ids:
        verses_list = surahs_map[surah_id]
        
        # Ensure verses are sorted by Ayah number
        verses_list.sort(key=lambda x: int(x.get("ayah_no", 0)))

        # Extract Surah metadata from the first verse
        first_verse = verses_list[0]
        surah_name_en = first_verse.get("surah_name", "")
        
        # --- LOOKUP STATIC DATA FOR PERFECTION ---
        # Explicitly cast surah_id to int for safe lookup
        meta = SURAH_META.get(int(surah_id), {"name_ar": "", "type": "Unknown"})
        
        # Construct the Surah Object
        new_surah = {
            "id": surah_id,
            "name_ar": meta["name_ar"],
            "name_en": surah_name_en,
            "type": meta["type"],
            "total_verses": len(verses_list),
            "verses": []
        }

        # Process Verses
        for verse in verses_list:
            ayah_id = int(verse.get("ayah_no", 0))
            
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
                    "ar": "",
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
        print(f"✅ Success! '{output_path}' has been created.")
        print("⚠️  REMINDER: You may need to update 'utils.py' to read this new 'surahs' list structure.")
        
    except Exception as e:
        print(f"❌ Error writing file: {e}")

if __name__ == "__main__":
    merge_quran_datasets()