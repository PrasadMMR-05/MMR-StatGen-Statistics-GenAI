import sys
import logging
from fastapi.testclient import TestClient
from app import app
import chroma_client

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_verification():
    print("Starting In-Process Verification...")
    
    # 1. Verify Chroma Client directly
    print("\n[1] Testing Chroma Client Logic...")
    try:
        results = chroma_client.search_query("AI trends", k=1)
        if results:
            print("PASS: chroma_client.search_query returned results.")
            print(f"   Sample: {results[0].get('title')} (Premium: {results[0].get('isPremium')})")
        else:
            print("WARN: chroma_client.search_query returned empty list.")
    except Exception as e:
        print(f"FAIL: chroma_client error: {e}")

    # 2. Verify API endpoints via TestClient (bypasses uvicorn)
    print("\n[2] Testing FastAPI Endpoints (TestClient)...")
    client = TestClient(app)
    
    # Health
    try:
        r = client.get("/health")
        if r.status_code == 200:
            print("PASS: /health OK")
        else:
            print(f"FAIL: /health {r.status_code}")
    except Exception as e:
        print(f"FAIL: /health exception {e}")

    # Search
    try:
        r = client.post("/search", json={"query": "growth", "k": 2})
        if r.status_code == 200:
            data = r.json()
            if len(data) > 0:
                print("PASS: /search OK")
            else:
                print("PASS: /search OK (empty results)")
        else:
            print(f"FAIL: /search {r.status_code} - {r.text}")
    except Exception as e:
        print(f"FAIL: /search exception {e}")

    # AI Query
    try:
        r = client.post("/ai/query", json={"query": "Summarize AI adoption"})
        if r.status_code == 200:
            data = r.json()
            if "answer" in data:
                print("PASS: /ai/query OK")
                print(f"   Answer snippet: {data['answer'][:50]}...")
            else:
                 print(f"FAIL: /ai/query response missing 'answer': {data.keys()}")
        else:
            print(f"FAIL: /ai/query {r.status_code} - {r.text}")
    except Exception as e:
        print(f"FAIL: /ai/query exception {e}")

if __name__ == "__main__":
    run_verification()
