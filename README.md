# MMR Statistics – AI Search & Generation Microservice

This project implements a FastAPI microservice for searching and generating insights from statistical data using semantic search (ChromaDB) and an LLM-like generation step.

## Features
- **Data Ingestion**: Fetch data from MongoDB (or seed with dummy data) and store embeddings in ChromaDB.
- **Semantic Search**: Text-to-SQL? No, Text-to-Vector! Find relevant statistics using natural language queries.
- **Re-ranking**: Uses Cross-Encoders to refine search results for high precision.
- **AI Analytics**: Generates textual summaries/answers based on search results.
- **caching**: Implements TTL caching for frequent queries.
- **Feedback Loop**: Collects user feedback for MLOps.

## Prerequisites
- Python 3.9+
- MongoDB (optional, for real ingestion)

## Installation

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   .\venv\Scripts\activate   # Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure Environment:
   - Copy `.env.example` (or use defaults) to `.env`.
   - Set `MONGO_URI` if connecting to a real DB.

## Quick Start

You can use the provided batch script to setup, seed, and run everything:

```bash
run_all.bat
```

Or manually:

1. **Seed Data** (if no MongoDB):
   ```bash
   python seed_data.py
   ```
   *OR* **Ingest from Mongo**:
   ```bash
   python ingest.py
   ```

2. **Start Server**:
   ```bash
   uvicorn app:app --reload
   ```

3. **Test API**:
   - Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
   - Run tests: `python test_endpoints.py`

## API Endpoints

- `GET /health` - Health check
- `POST /search` - Semantic search
  - Body: `{"query": "AI trends", "k": 5}`
- `POST /ai/query` - RAG generation
  - Body: `{"query": "Summarize AI adoption"}`
- `POST /feedback` - Submit user feedback

## Project Structure
- `app.py`: Main FastAPI application.
- `chroma_client.py`: Wrapper for ChromaDB interactions and Reranking.
- `ingest.py`: ETL script for MongoDB -> Vector DB.
- `seed_data.py`: Script to populate DB with sample data.
- `config.py`: Configuration management.
