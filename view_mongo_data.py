import ingest
import json
from bson import json_util

def show_data():
    print("Fetching data using ingest.get_mongo_docs()...")
    docs = ingest.get_mongo_docs()
    
    if not docs:
        print("No documents found.")
        return

    print(f"\n--- Found {len(docs)} documents ---\n")
    # serialization for ObjectId and other BSON types
    print(json_util.dumps(docs, indent=2))

if __name__ == "__main__":
    show_data()
