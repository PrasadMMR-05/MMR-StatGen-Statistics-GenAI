from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import chroma_client
import generate
import logging
import json
import time

# ML-10: Caching
from cachetools import TTLCache, cached
from cachetools.keys import hashkey

# ML-6: Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="MMR Statistics AI Microservice")

# Initialize Cache (MaxSize=100, TTL=300 seconds)
search_cache = TTLCache(maxsize=100, ttl=300)

class SearchRequest(BaseModel):
    query: str
    k: int = 5
    allowed_industries: Optional[List[str]] = None

class SearchResultItem(BaseModel):
    statisticId: str
    title: str
    excerpt: str
    score: float
    chart_type: str
    chart_preview: Optional[str] = None
    isPremium: bool
    stat_url: str
    # ML-7: Optional reranked flag
    reranked: Optional[bool] = False

class AIQueryRequest(BaseModel):
    query: str
    allowed_industries: Optional[List[str]] = None

# ML-12: Feedback Model
class FeedbackRequest(BaseModel):
    query: str
    rating: int # 1-5
    comment: Optional[str] = None

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    # Wrapper for request logging
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(f"Unhandled exception: {e}")
        # ML-6: Return 500 on unhandled errors
        raise HTTPException(status_code=500, detail="Internal Server Error")

# ML-6: Health endpoint
@app.get("/health")
def health_check():
    return {"status": "ok"}

# Wrapper function for caching (since decorators on instance methods or pydantic args can be tricky, 
# we cache the underlying function call logic).
@cached(cache=search_cache, key=lambda query, k, allowed_industries: hashkey(query, k, tuple(allowed_industries) if allowed_industries else None))
def cached_search(query: str, k: int, allowed_industries: Optional[List[str]]):
    logger.info(f"Cache miss for query: {query}")
    return chroma_client.search_query(
        query=query,
        k=k,
        allowed_industries=allowed_industries
    )

# ML-5: Search endpoint
@app.post("/search", response_model=List[SearchResultItem])
def search(request: SearchRequest):
    try:
        # Use cached function
        results = cached_search(request.query, request.k, request.allowed_industries)
        return results
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ai/query")
def ai_query(request: AIQueryRequest):
    try:
        # 1. Search (using cache indirectly if we called search API, but here we call client directly usually.
        # Let's reuse the cached_search to benefit from caching here too!
        search_results = cached_search(
            query=request.query,
            k=5, 
            allowed_industries=request.allowed_industries
        )
        
        # 2. Generate
        # ML-3: Pass results to generator (it will slice top 3)
        answer = generate.get_answer(request.query, search_results)
        
        return {
            "answer": answer,
            "sources": search_results # Return full sources to UI
        }
    except Exception as e:
        logger.error(f"AI Query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ML-12: Feedback Endpoint
@app.post("/feedback")
def submit_feedback(feedback: FeedbackRequest):
    try:
        # Append to a JSONL file
        entry = {
            "timestamp": time.time(),
            "query": feedback.query,
            "rating": feedback.rating,
            "comment": feedback.comment
        }
        with open("feedback_log.jsonl", "a") as f:
            f.write(json.dumps(entry) + "\n")
            
        logger.info(f"Feedback received for query '{feedback.query}': {feedback.rating}")
        return {"status": "received"}
    except Exception as e:
        logger.error(f"Feedback error: {e}")
        raise HTTPException(status_code=500, detail="Failed to save feedback")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
