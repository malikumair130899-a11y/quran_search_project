import json
import pickle
from sentence_transformers import SentenceTransformer

DATA_PATH = "data/quran_complete.json"
OUT_PATH = "data/embeddings.pkl"

print("⏳ Loading Quran dataset...")
with open(DATA_PATH, encoding="utf-8") as f:
    data = json.load(f)

texts = []
for s in data["surahs"]:
    for v in s["verses"]:
        # Combine translation + tafsir for better semantic understanding
        en = v.get("english", "")
        tafsir_en = v.get("tafsir_en", "")
        texts.append(en + " " + tafsir_en)

print(f"✅ Loaded {len(texts)} verses")

print("⏳ Loading SentenceTransformer model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

print("⏳ Encoding verses (this takes time ONCE)...")
embeddings = model.encode(texts, show_progress_bar=True)

print("⏳ Saving embeddings to disk...")
with open(OUT_PATH, "wb") as f:
    pickle.dump(embeddings, f)

print("✅ DONE — embeddings saved to data/embeddings.pkl")
