import requests
import time
import sys

BASE_URL = "http://localhost:8000"

def test_health():
    print("Testing /health...")
    try:
        r = requests.get(f"{BASE_URL}/health")
        if r.status_code == 200:
            print("PASS: /health is OK")
        else:
            print(f"FAIL: /health returned {r.status_code}")
    except Exception as e:
        print(f"FAIL: /health exception: {e}")

def test_search():
    print("Testing /search...")
    payload = {"query": "AI trends", "k": 3}
    try:
        r = requests.post(f"{BASE_URL}/search", json=payload)
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list) and len(data) > 0:
                print("PASS: /search returned results")
                item = data[0]
                # ML-2 verification
                required_keys = ["statisticId", "title", "excerpt", "score", "chart_preview", "isPremium"]
                missing = [k for k in required_keys if k not in item]
                if not missing:
                    print("PASS: Rich metadata present")
                else:
                    print(f"FAIL: Missing metadata keys: {missing}")
                
                # ML-5 verification
                if "score" in item:
                    print(f"PASS: Score present ({item['score']})")
            else:
                print("WARN: /search returned empty list (ensure seed data is valid)")
        else:
            print(f"FAIL: /search returned {r.status_code} - {r.text}")
    except Exception as e:
        print(f"FAIL: /search exception: {e}")

def test_ai_query():
    print("Testing /ai/query...")
    payload = {"query": "Tell me about AI trends"}
    try:
        r = requests.post(f"{BASE_URL}/ai/query", json=payload)
        if r.status_code == 200:
            data = r.json()
            if "answer" in data and "sources" in data:
                print("PASS: /ai/query returned answer and sources")
                # ML-4 Verification (manual check of output string usually, but we check flag existence)
                sources = data["sources"]
                if sources and "isPremium" in sources[0]:
                    print("PASS: Sources contain isPremium flag")
            else:
                print(f"FAIL: Invalid response format: {data.keys()}")
        else:
             print(f"FAIL: /ai/query returned {r.status_code} - {r.text}")
    except Exception as e:
        print(f"FAIL: /ai/query exception: {e}")

if __name__ == "__main__":
    # Wait for server to start
    print("Waiting for server to be ready...")
    for i in range(10):
        try:
            requests.get(f"{BASE_URL}/health")
            break
        except:
            time.sleep(2)
    
    test_health()
    test_search()
    test_ai_query()
