import chromadb
from sentence_transformers import SentenceTransformer
import config

def seed():
    print("Seeding ChromaDB with dummy data for verification...")
    client = chromadb.PersistentClient(path=config.CHROMA_PATH)
    collection = client.get_or_create_collection(name="mmr_stats")
    
    model = SentenceTransformer(config.EMBEDDING_MODEL_NAME)
    
    dummy_data = [
        {
            "id": "STAT_6023",
            "title": "Generative AI usage 2024 — Global",
            "excerpt": "Share of enterprises using generative AI rose to 48% in 2024, showing a significant jump from previous years.",
            "industryId": "tech",
            "isPremium": False,
            "chart_type": "line"
        },
        {
            "id": "STAT_4872",
            "title": "Autonomous agents adoption — 2024",
            "excerpt": "Use of autonomous agents in IT automation doubled year-over-year, driven by efficiency needs.",
            "industryId": "tech",
            "isPremium": False,
            "chart_type": "bar"
        },
        {
            "id": "STAT_5130",
            "title": "AI workforce impact 2024",
            "excerpt": "Employers report a 34% increase in demand for ML skills, while manual data entry jobs decline.",
            "industryId": "finance",
            "isPremium": True,
            "chart_type": "pie"
        }
    ]
    
    ids = []
    embeddings = []
    metadatas = []
    documents = []
    
    for item in dummy_data:
        text = f"{item['title']}. {item['excerpt']}"
        ids.append(item['id'])
        embeddings.append(model.encode(text).tolist())
        metadatas.append({
            "statisticId": item['id'],
            "title": item['title'],
            "excerpt": item['excerpt'],
            "isPremium": item['isPremium'],
            "industryId": item['industryId'],
            "chart_type": item['chart_type'],
            "chart_preview": f"http://example.com/{item['id']}.png"
        })
        documents.append(text)
        
    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        metadatas=metadatas,
        documents=documents
    )
    print("Seeding complete.")

if __name__ == "__main__":
    seed()
