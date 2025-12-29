import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer, CrossEncoder
import config

# Initialize Chroma Client
# Using persistent client to save data to disk
client = chromadb.PersistentClient(path=config.CHROMA_PATH)
collection = client.get_or_create_collection(name="mmr_stats")

# ML-1: Load the SentenceTransformer model explicitly
print(f"Loading embedding model: {config.EMBEDDING_MODEL_NAME}...")
model = SentenceTransformer(config.EMBEDDING_MODEL_NAME)
print("Model loaded.")

# ML-7: Load CrossEncoder
print("Loading CrossEncoder model...")
# Using a small model for speed
cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2') 
print("CrossEncoder loaded.")

def rerank_results(query, results, top_k):
    """
    Re-ranks a list of results using a Cross-Encoder.
    """
    if not results:
        return []
    
    # Prepare pairs for CrossEncoder
    # We use the excerpt as the document text
    pairs = [[query, res['excerpt']] for res in results]
    scores = cross_encoder.predict(pairs)
    
    # Attach new scores and sort
    for i, res in enumerate(results):
        # CrossEncoder scores are logits (usually), higher is better
        res['score'] = float(scores[i]) 
        res['reranked'] = True
        
    # Sort descending
    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:top_k]

def search_query(query: str, k: int = 5, allowed_industries: list = None):
    """
    Searches the ChromaDB collection for the given query.
    Fetches 3*k candidates and then re-ranks them.
    
    Args:
        query: The user's search query.
        k: Number of results to return.
        allowed_industries: List of industry IDs to filter by.
        
    Returns:
        List of dicts containing rich metadata and scores.
    """
    try:
        # ML-1: Encode the query
        query_embedding = model.encode(query).tolist()
        
        # ML-1: Construct where filter if allowed_industries is provided
        where_filter = None
        if allowed_industries:
            if len(allowed_industries) == 1:
                 where_filter = {"industryId": allowed_industries[0]}
            else:
                where_filter = {"$or": [{"industryId": ind} for ind in allowed_industries]}

        # Perform the query
        # Fetch 3x candidates for re-ranking
        fetch_k = k * 3
        
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=fetch_k,
            where=where_filter
        )

        formatted_results = []
        
        if not results['ids'] or len(results['ids'][0]) == 0:
            return []

        # Iterate through the results
        ids = results['ids'][0]
        metadatas = results['metadatas'][0]
        distances = results['distances'][0]

        for i in range(len(ids)):
            meta = metadatas[i] or {}
            
            # ML-2: Build rich item
            item = {
                "statisticId": ids[i],
                "title": meta.get("title", "Unknown Title"),
                "excerpt": meta.get("excerpt") or meta.get("description", "")[:200], 
                "score": float(distances[i]), # Initial vector distance
                "chart_type": meta.get("chart_type", "unknown"),
                "chart_preview": meta.get("chart_preview"),
                "isPremium": meta.get("isPremium", False), # ML-4 flag
                "accessTier": meta.get("accessTier", "free"),
                "stat_url": meta.get("stat_url") or f"/statistics/{ids[i]}/details",
                "industryId": meta.get("industryId")
            }
            formatted_results.append(item)
            
        # ML-7: Apply Re-ranking
        ranked_results = rerank_results(query, formatted_results, k)
        
        return ranked_results

    except Exception as e:
        print(f"Error in search_query: {e}")
        # ML-6: We will catch this in app.py, but good to log here too.
        raise e
