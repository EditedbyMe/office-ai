from ddgs import DDGS
import time

print("Testing DDGS (new package) Backends...")

# ddgs might have different initialization or methods
try:
    with DDGS() as ddgs:
        print("Initialized DDGS successfully")
        
        # Test basic text search
        print("\n--- Testing text search ---")
        results = list(ddgs.text("microsoft office", max_results=3))
        
        if results:
             print(f"✅ Success! Found {len(results)} results.")
             print(f"Title: {results[0].get('title')}")
             print(f"URL: {results[0].get('href')}")
        else:
             print("❌ Failed. Returned empty list.")

except Exception as e:
    print(f"❌ Error: {e}")
