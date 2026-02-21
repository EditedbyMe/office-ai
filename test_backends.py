from duckduckgo_search import DDGS
import time

print("Testing DuckDuckGo Search Backends...")

backends = ["html", "lite", "api", "auto"]
query = "microsoft office"

for backend in backends:
    print(f"\n--- Testing backend: {backend} ---")
    try:
        with DDGS() as ddgs:
            # Note: 'api' and 'ecosia' are deprecated/removed in some versions, but 'api' maps to 'auto' often.
            # We'll use the text method.
            results = list(ddgs.text(query, backend=backend, max_results=3))
            
            if results:
                print(f"✅ Success! Found {len(results)} results.")
                print(f"Title: {results[0].get('title')}")
            else:
                print("❌ Failed. Returned empty list.")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    time.sleep(2)
