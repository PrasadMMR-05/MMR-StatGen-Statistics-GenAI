import sys
import logging
from fastapi.testclient import TestClient
from app import app
import chroma_client

def run():
    with open("verify_result.txt", "w") as f:
        f.write("Starting...\n")
        try:
            # 1. Chroma
            f.write("Testing Chroma...\n")
            results = chroma_client.search_query("AI", k=1)
            f.write(f"Chroma Result: {len(results)} items\n")
            
            # 2. APP
            f.write("Testing App...\n")
            client = TestClient(app)
            r = client.get("/health")
            f.write(f"Health: {r.status_code}\n")
            
            r = client.post("/search", json={"query": "growth", "k": 1})
            f.write(f"Search: {r.status_code} - {len(r.json())} items\n")
            
            r = client.post("/ai/query", json={"query": "test"})
            f.write(f"AI Query: {r.status_code}\n")
            
            f.write("DONE\n")
        except Exception as e:
            f.write(f"Error: {e}\n")

if __name__ == "__main__":
    run()
