import sys
from utils import load_verses
from search_engine import build_tfidf_index, search_verses

def main():
    print("⏳ Loading Quran Data from quran_complete.json...")
    verses = load_verses()
    
    if not verses:
        print("❌ Failed to load data. Check if 'quran_complete.json' exists.")
        return

    print(f"✅ Loaded {len(verses)} verses.")
    print("⏳ Building Search Index...")
    vectorizer, tfidf_matrix = build_tfidf_index(verses)
    print("✅ System Ready!\n")

    while True:
        try:
            query = input("🔍 Enter search query (or 'q' to quit): ").strip()
        except KeyboardInterrupt:
            print("\nExiting...")
            break

        if query.lower() in ('q', 'quit', 'exit'):
            break
        
        if not query:
            continue

        # Perform Search
        results = search_verses(query, verses, vectorizer, tfidf_matrix, top_k=5)

        if not results:
            print("   No results found.")
        else:
            print(f"\nTop {len(results)} results for '{query}':")
            print("=" * 60)
            
            for i, (verse, score) in enumerate(results, 1):
                # Update: Access dictionary keys instead of object attributes
                surah = verse.get('surah', 'Unknown')
                ayah = verse.get('ayah_number', 0)
                english = verse.get('english', '')
                
                print(f"{i}. Surah {surah} ({ayah}) | Score: {score:.2f}")
                print(f"   {english}")
                print("-" * 60)
        print("\n")

if __name__ == "__main__":
    main()