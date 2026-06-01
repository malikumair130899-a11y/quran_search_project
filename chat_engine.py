# chat_engine.py
from sentence_transformers import SentenceTransformer
import numpy as np
import json

# Load model only once
model = SentenceTransformer('all-MiniLM-L6-v2')

# Load Quran verses
with open('data/quran_with_urdu.json', 'r', encoding='utf-8') as f:
    quran_data = json.load(f)

# Prepare verses
verses = []
corpus = []
for item in quran_data:
    en = item.get("translation", {}).get("en", "")
    ur = item.get("translation", {}).get("ur", "")
    if en:
        verses.append({
            "surah": item["surah"],
            "ayah": item["ayah"],
            "english": en,
            "urdu": ur
        })
        corpus.append(en)

# Embed all English translations
corpus_embeddings = model.encode(corpus, convert_to_tensor=True)

def answer_question(question, top_k=3):
    if not question.strip():
        return []

    query_embedding = model.encode(question, convert_to_tensor=True)
    cosine_scores = np.dot(corpus_embeddings, query_embedding)
    top_indices = np.argsort(cosine_scores)[::-1][:top_k]

    return [verses[i] for i in top_indices]
