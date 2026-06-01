import json
import os

def load_verses(filepath="quran_complete.json"):
    """
    Load and flatten Quranic verses from the dataset.
    Returns a list of dictionaries compatible with the app.
    """
    # 1. Locate the file safely
    if not os.path.exists(filepath):
        # Fallback to checking inside a data/ folder if not found in root
        if os.path.exists(os.path.join("data", filepath)):
            filepath = os.path.join("data", filepath)
        else:
            print(f"❌ File not found: {filepath}")
            return []

    # 2. Load JSON content
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Error reading JSON: {e}")
        return []

    verses = []
    
    # 3. Parse hierarchy
    surah_list = data.get("surahs", [])

    for surah in surah_list:
        surah_name = surah.get("name_en", "Unknown")
        surah_ar = surah.get("name_ar", "")      # Capture Arabic Name
        surah_type = surah.get("type", "Meccan") # Capture Revelation Type
        surah_id = surah.get("id", 0)
        
        for verse in surah.get("verses", []):
            # Extract Text
            arabic_text = verse.get("arabic", {}).get("text", "")
            
            # Extract Translations
            translations = verse.get("translations", {})
            english_text = translations.get("en", "")
            urdu_text = translations.get("ur", "")
            
            # Extract Tafsir
            tafsir = verse.get("tafsir", {})
            tafsir_en = tafsir.get("en", "")
            tafsir_ur = tafsir.get("ur", "")

            # Flatten into a single object
            verses.append({
                "surah": surah_name,
                "surah_ar": surah_ar,       # Added for Surah Page
                "surah_type": surah_type,   # Added for Surah Page
                "surah_id": surah_id,
                "ayah_number": verse.get("ayah", 0),
                "text": arabic_text,
                "english": english_text,
                "urdu": urdu_text,
                "tafsir_en": tafsir_en,
                "tafsir_ur": tafsir_ur
            })

    print(f"✅ Successfully loaded {len(verses)} verses from {filepath}")
    return verses