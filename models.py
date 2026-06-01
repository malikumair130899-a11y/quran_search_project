import json

class Verse:
    def __init__(self, surah, ayah_number, english, urdu, text="", tafsir_en="", tafsir_ur=""):
        self.surah = surah
        self.ayah_number = ayah_number
        self.english = english
        self.urdu = urdu
        self.text = text  # Arabic verse
        self.tafsir_en = tafsir_en  # English Tafsir (HTML)
        self.tafsir_ur = tafsir_ur  # Urdu Tafsir (HTML/Text)

    def to_dict(self):
        """Converts the Verse object to a dictionary (useful for API responses)."""
        return {
            "surah": self.surah,
            "ayah_number": self.ayah_number,
            "text": self.text,
            "english": self.english,
            "urdu": self.urdu,
            "tafsir_en": self.tafsir_en,
            "tafsir_ur": self.tafsir_ur
        }

def load_quran_data(filepath):
    """
    Loads Quranic verses from the new 'quran_complete.json' format.
    Expects structure: { "surahs": [ { "name_en": "...", "verses": [...] } ] }
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ File not found: {filepath}")
        return []

    verses = []
    
    # Access the list of Surahs from the new structure
    surah_list = data.get("surahs", [])

    for surah in surah_list:
        surah_name = surah.get("name_en", "Unknown")
        
        for verse in surah.get("verses", []):
            # Extract translations safely
            translations = verse.get("translations", {})
            
            # Extract tafsir safely
            tafsir = verse.get("tafsir", {})

            # Create Verse object
            verses.append(
                Verse(
                    surah=surah_name,
                    ayah_number=verse.get("ayah", 0),
                    text=verse.get("arabic", {}).get("text", ""),
                    english=translations.get("en", ""),
                    urdu=translations.get("ur", ""),
                    tafsir_en=tafsir.get("en", ""),
                    tafsir_ur=tafsir.get("ur", "")
                )
            )
            
    return verses