import numpy as np
import os
import torch
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# Global variables for caching
_semantic_model = None

def get_semantic_model():
    """Singleton to load the model only once."""
    global _semantic_model
    if _semantic_model is None:
        print("⏳ Loading Semantic Model (all-MiniLM-L6-v2)...")
        _semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
    return _semantic_model

# --- TF-IDF Search ---

def build_tfidf_index(verses):
    """
    Builds the TF-IDF matrix for the English translations.
    Expects 'verses' to be a list of dictionaries.
    """
    # Extract English text from the dictionary
    corpus = [v.get('english', '') for v in verses]
    
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(corpus)
    
    return vectorizer, tfidf_matrix

def search_verses(query, verses, vectorizer, tfidf_matrix, top_k=5):
    """
    Performs Keyword Search (TF-IDF).
    """
    query_vec = vectorizer.transform([query])
    cosine_similarities = cosine_similarity(query_vec, tfidf_matrix).flatten()
    
    # Get top_k indices sorted by score descending
    related_docs_indices = cosine_similarities.argsort()[:-top_k:-1]
    
    results = []
    for i in related_docs_indices:
        score = cosine_similarities[i]
        if score > 0.0:  # Filter out irrelevant results
            results.append((verses[i], score))
            
    return results

# --- Semantic Search ---

def build_semantic_index(verses, cache_file="quran_embeddings.pt"):
    """
    Encodes all verses into embeddings using SentenceTransformer.
    Checks for a local cache file first to speed up startup.
    Expects 'verses' to be a list of dictionaries.
    """
    model = get_semantic_model()
    
    # 1. Check if cache exists
    if os.path.exists(cache_file):
        print(f"✅ Found cached embeddings in '{cache_file}'. Loading...")
        try:
            embeddings = torch.load(cache_file)
            
            # Validation: Ensure embedding count matches verse count
            if len(embeddings) == len(verses):
                print("✅ Embeddings loaded successfully (Cache Hit).")
                return model, embeddings
            else:
                print(f"⚠️ Cache mismatch: {len(embeddings)} embeddings vs {len(verses)} verses. Rebuilding...")
        except Exception as e:
            print(f"⚠️ Error loading cache: {e}. Rebuilding index...")

    # 2. If no cache or mismatch, rebuild index
    # Extract English text
    texts = [v.get('english', '') for v in verses]
    
    print(f"⏳ Encoding {len(texts)} verses for semantic search (First Run Only)...")
    embeddings = model.encode(texts, convert_to_tensor=True)
    
    # 3. Save to file for next time
    try:
        print(f"💾 Saving embeddings to '{cache_file}'...")
        torch.save(embeddings, cache_file)
        print("✅ Semantic Index Built and Cached.")
    except Exception as e:
        print(f"⚠️ Could not save cache: {e}")
    
    return model, embeddings

def semantic_search(query, verses, model, embeddings, top_k=5):
    """
    Performs Semantic Search using vector embeddings.
    """
    from sentence_transformers import util
    
    query_embedding = model.encode(query, convert_to_tensor=True)
    
    # Compute cosine similarities
    cosine_scores = util.cos_sim(query_embedding, embeddings)[0]
    
    # Get top_k results
    # We use argpartition to find the top k indices efficiently
    top_results_indices = np.argpartition(-cosine_scores.cpu(), range(top_k))[0:top_k]
    
    results = []
    for idx in top_results_indices:
        score = cosine_scores[idx].item()
        
        # --- FIX: Add a threshold to filter out irrelevant results ---
        # If the score is too low (e.g. < 0.15), it's likely noise or a default sort order
        if score > 0.15: 
            results.append((verses[idx], score))
    
    # Sort the final filtered results by score descending
    results = sorted(results, key=lambda x: x[1], reverse=True)
        
    return results