import chroma_client

def verify():
    print("Verifying Re-ranking...")
    try:
        # Search for something that matches the seed data
        results = chroma_client.search_query("AI usage", k=2)
        
        if not results:
            print("FAIL: No results found.")
            return
            
        first = results[0]
        print(f"Top Result: {first.get('title')}")
        print(f"Score: {first.get('score')}")
        
        if first.get('reranked'):
            print("PASS: Result has 'reranked' flag.")
        else:
            print("FAIL: Result missing 'reranked' flag.")
            
    except Exception as e:
        print(f"FAIL: Exception {e}")

if __name__ == "__main__":
    verify()
