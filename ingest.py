import os
import pymongo
import logging
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import config

# ML-6: Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_mongo_docs():
    """
    Fetches documents from MongoDB.
    """
    try:
        client = pymongo.MongoClient(config.MONGO_URI, serverSelectionTimeoutMS=2000)
        db = client[config.DB_NAME]
        collection = db[config.COLLECTION_NAME]
        # Check connection
        client.server_info() 
        logger.info(f"Connected to MongoDB: {config.MONGO_URI}")
        return list(collection.find({}))
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        # Allow the script to proceed if we want to support a "no-mongo" mode,
        # otherwise re-raise or return empty.
        # For the task ML-6 ("If Mongo not available... log stacktrace"), we log and return empty.
        return []

def ingest_data():
    try:
        logger.info("Starting ingestion...")
        
        # 1. Fetch data
        docs = get_mongo_docs()
        if not docs:
            logger.warning("No documents found directly from MongoDB (or connection failed).")
            # Optional: Insert mock data if DB is empty for demonstration purposes?
            # The prompt implies we should expect failure if Mongo isn't there, 
            # but to "Acceptance: A local curl to POST /search ... returns top k results", 
            # we might need SOME data.
            # I will assume the user has a DB or expects empty results if no DB.
            return

        # 2. Initialize Chroma & Model
        # We can import from chroma_client to ensure consistency, but ingest is often standalone.
        # Let's use the config constants.
        client = chromadb.PersistentClient(path=config.CHROMA_PATH)
        collection = client.get_or_create_collection(name="mmr_stats")
        
        logger.info(f"Loading model {config.EMBEDDING_MODEL_NAME}...")
        model = SentenceTransformer(config.EMBEDDING_MODEL_NAME)
        
        ids = []
        embeddings = []
        metadatas = []
        documents = []

        for doc in docs:
            try:
                # Validate/Extract fields
                stat_id = str(doc.get("statisticId", doc.get("_id")))
                title = doc.get("title", "")
                text = f"{title}. {doc.get('excerpt', '')}"
                
                # Metadata
                # Metadata validation helper
                def safe_str(val):
                    if val is None:
                        return ""
                    if isinstance(val, (str, int, float, bool)):
                        return str(val)
                    return str(val)

                meta = {
                    "statisticId": stat_id,
                    "title": title,
                    "excerpt": safe_str(doc.get("excerpt", "")),
                    "description": safe_str(doc.get("description", "")),
                    "chart_type": safe_str(doc.get("chart_type", "unknown")),
                    "chart_preview": safe_str(doc.get("chart_preview", "")),
                    "isPremium": bool(doc.get("isPremium", False)),
                    "stat_url": safe_str(doc.get("stat_url", "")),
                    "industryId": safe_str(doc.get("industryId", "resource-tech")), # default valid industry
                    "accessTier": safe_str(doc.get("accessTier", "free"))
                }
                
                # Embed
                emb = model.encode(text).tolist()
                
                ids.append(stat_id)
                embeddings.append(emb)
                metadatas.append(meta)
                documents.append(text)
                
            except Exception as doc_e:
                logger.error(f"Skipping document due to error: {doc_e}")
                continue
        
        if ids:
            logger.info(f"Upserting {len(ids)} documents into Chroma...")
            collection.upsert(
                ids=ids,
                embeddings=embeddings,
                metadatas=metadatas,
                documents=documents
            )
            logger.info("Ingestion complete.")
        else:
            logger.info("No documents to upsert.")

    except Exception as e:
        logger.error(f"Critical error during ingestion: {e}")
        raise e

if __name__ == "__main__":
    ingest_data()
