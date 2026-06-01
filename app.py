from flask import Flask, render_template, request, jsonify
from utils import load_verses
from search_engine import (
    build_tfidf_index,
    search_verses,
    semantic_search
)
import os
import json # Added to read metadata directly
from google import genai
import pickle
from sentence_transformers import SentenceTransformer

app = Flask(__name__)

# ==========================================
# AI CONFIGURATION 
# ==========================================
# Consider using os.environ for security in production
GEMINI_API_KEY = "AQ.Ab8RN6KA5scAAtdgGCr1T6OxHcvg7wogQcMjCM_vae458r6jOg" 
client = genai.Client(api_key=GEMINI_API_KEY)

# ==========================================
# 1. Load Data & Build Indices (On Startup)
# ==========================================

print("⏳ Loading Quran data...")
# Load verses for Search functionality
verses = load_verses("quran_complete.json")

if not verses:
    print("❌ CRITICAL ERROR: No verses loaded. Check 'quran_complete.json'.")
else:
    print(f"✅ Loaded {len(verses)} verses successfully.")

# --- Build Tafsir Lookup ---
tafsir_map = {}
for v in verses:
    s_id = v.get('surah_id')
    a_num = v.get('ayah_number')
    if s_id and a_num:
        key = f"{s_id}:{a_num}"
        tafsir_map[key] = v

# --- Build Rich Surah Metadata for Browse Page ---
# We read the JSON file directly again to ensure we get fields like 
# 'name_ar', 'revelation_type', etc. which might be lost in the flattened 'verses' list.
SURAHS_LIST = []
try:
    filepath = "quran_complete.json"
    if not os.path.exists(filepath) and os.path.exists(os.path.join("data", filepath)):
        filepath = os.path.join("data", filepath)
        
    with open(filepath, "r", encoding="utf-8") as f:
        raw_data = json.load(f)
        for s in raw_data.get('surahs', []):
            SURAHS_LIST.append({
                "id": s.get('id'),
                "name": s.get('name_en', 'Unknown'),         # Matches browse.html 'name'
                "ar": s.get('name_ar', 'القرآن'),            # Matches browse.html 'ar'
                "translation": s.get('translation_en', 'The Chapter'), # Matches browse.html 'translation'
                "verses": len(s.get('verses', [])),          # Matches browse.html 'verses'
                "type": s.get('type', 'Meccan').capitalize() # Matches browse.html 'type'
            })
    print(f"✅ Loaded Metadata for {len(SURAHS_LIST)} Surahs.")
except Exception as e:
    print(f"⚠️ Warning: Could not load detailed Surah metadata: {e}")
    # Fallback if file read fails
    SURAHS_LIST = []

# --- Build Search Indices ---
if verses:
    print("⏳ Building TF-IDF index...")
    vectorizer, tfidf_matrix = build_tfidf_index(verses)

    # FIX: Use the builder function from search_engine.py
    # This ensures consistency between generation and loading (using Torch)
    from search_engine import build_semantic_index
    
    print("⏳ Initializing Semantic Search...")
    # This will load 'quran_embeddings.pt' if it exists, or create it if missing/broken
    semantic_model, semantic_embeddings = build_semantic_index(verses)

    if semantic_embeddings is not None:
        print("✅ Semantic Search System Ready!")
    else:
        print("⚠️ Semantic embeddings could not be loaded.")
else:
    vectorizer, tfidf_matrix = None, None
    semantic_model, semantic_embeddings = None, None


# ==========================================
# 2. Application Routes
# ==========================================

@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    query = ""
    mode = "semantic"

    if request.method == 'POST':
        query = request.form.get('query', '').strip()
        mode = request.form.get('mode', 'semantic')

        if query and verses:
            try:
                if mode == 'semantic' and semantic_model and semantic_embeddings is not None:
                    results = semantic_search(query, verses, semantic_model, semantic_embeddings)
                else:
                    results = search_verses(query, verses, vectorizer, tfidf_matrix)
            except Exception as e:
                print(f"❌ Search Error: {e}")

    return render_template('index.html', query=query, results=results, mode=mode)

@app.route('/browse')
def browse():
    # Passes the rich metadata list to the template
    return render_template('browse.html', surahs=SURAHS_LIST)

@app.route('/surah/<int:surah_id>')
def surah(surah_id):
    # Find metadata for this specific Surah
    meta = next((s for s in SURAHS_LIST if s['id'] == surah_id), None)
    
    if not meta:
        return "Surah not found", 404
        
    # Filter verses for this Surah
    surah_verses = [v for v in verses if v['surah_id'] == surah_id]
    surah_verses.sort(key=lambda x: x['ayah_number'])

    return render_template('surah.html', surah=meta, verses=surah_verses)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/get_tafsir/<int:surah_id>/<int:ayah_id>')
def get_tafsir(surah_id, ayah_id):
    key = f"{surah_id}:{ayah_id}"
    verse = tafsir_map.get(key)
    if verse:
        en_content = verse.get('tafsir_en') or "<p class='text-gray-500 italic'>No English Tafsir available.</p>"
        ur_content = verse.get('tafsir_ur') or "<p class='text-gray-500 italic'>Urdu Tafsir not available.</p>"
        return jsonify({"en": en_content, "ur": ur_content})
    return jsonify({"error": "Verse not found"}), 404
import time

@app.route('/ask_ai', methods=['POST'])
def ask_ai():
    try:
        user_query = request.form.get('query', '').strip()
        
        # 1. RETRIEVAL: Reduced top_k to 5 to save tokens (prevents 429 error)
        if semantic_model and semantic_embeddings is not None:
            context_results = semantic_search(user_query, verses, semantic_model, semantic_embeddings, top_k=5)
        else:
            context_results = []

        # 2. CONTEXT BUILDING: Shortened Tafsir to keep TPM low
        context_text = ""
        for v, score in context_results:
            context_text += f"--- Surah {v['surah']} ({v['surah_id']}:{v['ayah_number']}) ---\n"
            context_text += f"Verse: {v['english']}\n"
            context_text += f"Tafsir: {v.get('tafsir_en', '')[:600]}\n\n" # Reduced from 1200 to 600

        # 3. STRICT QURANIC SCHOLAR PROMPT
        prompt = f"""
        You are an expert Quranic Scholar. Your task is to provide answer to the user's question. You are helpful assistant for understanding the Quran.
 
        
        User Question: "{user_query}"
        
        Source Material:
        {context_text}
        
        STYLE & FORMAT:
- Clear, calm, and easy to understand
- Use bullet points under headings
- Make it visually structured and readable
- Respond like ChatGPT (friendly, natural)
- Each bullet should be a complete sentence
- Use at least 4 bullets per answer
- Cite all verses as [Surah:Ayah]

RULES:
- Use ONLY the provided Quran verses and Tafsir
- Do NOT include external knowledge
- Expand ideas enough to meet the minimum bullet count
        
        Cite all verses as [Surah:Ayah]. Do not use external history or secular ideas.
        """

        # 4. RETRY LOGIC for Free Tier Quota (429 Errors)
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash", # Higher RPM pool than 2.0-flash
                    contents=prompt,
                    config=genai.types.GenerateContentConfig(
                        temperature=0.6,
                        max_output_tokens=1500 # Allows for long-form generation
                    )
                )
                return jsonify({"answer": response.text})
            except Exception as e:
                if "429" in str(e) and attempt < 2:
                    print(f"⚠️ Quota hit. Retrying in 15 seconds... (Attempt {attempt+1}/3)")
                    time.sleep(15) # Wait for token bucket to refill
                    continue
                else:
                    raise e

    except Exception as e:
        print(f"❌ FINAL AI ERROR: {e}")
        return jsonify({"answer": "### Service Temporarily Limited\nI've hit the free tier quota. Please try again in 1 minute."}), 503
if __name__ == '__main__':
    app.run(debug=False, use_reloader=False, port=5000)