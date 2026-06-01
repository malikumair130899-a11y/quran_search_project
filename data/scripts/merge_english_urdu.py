import json

# Load English dataset (quran.json)
with open("data/quran.json", "r", encoding="utf-8") as f:
    english_quran = json.load(f)

# Load Urdu dataset (quran_ur.json)
with open("data/quran_ur.json", "r", encoding="utf-8") as f:
    urdu_quran = json.load(f)

# Merge datasets
merged_quran = []

for surah_en, surah_ur in zip(english_quran, urdu_quran):
    merged_surah = {
        "id": surah_en["id"],
        "name": surah_en["name"],
        "transliteration": surah_en.get("transliteration", ""),
        "translation": surah_en["translation"],  # English surah name
        "type": surah_en["type"],
        "total_verses": surah_en["total_verses"],
        "verses": []
    }

    for verse_en, verse_ur in zip(surah_en["verses"], surah_ur["verses"]):
        merged_surah["verses"].append({
            "id": verse_en["id"],
            "text": verse_en["text"],
            "english": verse_en["translation"],
            "urdu": verse_ur["translation"]
        })

    merged_quran.append(merged_surah)

# Save merged dataset as quran_with_urdu.json
with open("data/quran_with_urdu.json", "w", encoding="utf-8") as f:
    json.dump(merged_quran, f, ensure_ascii=False, indent=2)

print("✅ Merged English and Urdu successfully into quran_with_urdu.json")
