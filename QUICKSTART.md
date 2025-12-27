# 🚀 Quick Start Guide

This guide will get you up and running with the RAG-based Travel Planner.

## Prerequisites

- **Python 3.10+**
- **Ollama** (for local LLM)
- **Git**

---

## Step 1: Install Ollama

### macOS/Linux
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Windows
Download from [ollama.com](https://ollama.com/download)

### Pull a Model
```bash
# Pull Llama 3 (recommended)
ollama pull llama3

# OR pull Mistral (faster, smaller)
ollama pull mistral
```

Verify Ollama is running:
```bash
ollama list
```

---

## Step 2: Clone & Setup Project

```bash
# Clone repository
git clone <your-repo-url>
cd travelplanner-rag

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## Step 3: Configure Environment

```bash
# Copy environment template
cp .env.template .env

# Edit .env if needed (optional)
# Default settings work for most cases
```

---

## Step 4: Ingest Sample Data

```bash
# Run data ingestion script
python scripts/ingest_data.py
```

**Expected output:**
```
============================================================
Travel Planner - Data Ingestion
============================================================
Ingesting attractions from data/raw/attractions_paris.json...
Generating embeddings...
Adding to vector store...
Saving vector store...
✓ Ingested 5 attractions
...
============================================================
Ingestion complete!
============================================================
```

---

## Step 5: Run Example

```bash
# Run basic example
python examples/basic_planner.py
```

**This will:**
1. Load vector stores
2. Parse user preferences
3. Run the LangGraph workflow
4. Show retrieved context

---

## Step 6: Use CLI

### Plan a trip (non-interactive)
```bash
python main.py plan --destination "Paris" --days 3 --budget moderate
```

### Interactive mode
```bash
python main.py interactive
```

### Ingest data via CLI
```bash
python main.py ingest
```

---

## Project Structure Overview

```
travelplanner-rag/
├── src/
│   ├── config/         # Settings & configuration
│   ├── models/         # Pydantic data models
│   ├── utils/          # Utilities (embeddings, geo, time)
│   ├── retrievers/     # RAG retrievers for different sources
│   └── graph/          # LangGraph nodes & workflow
├── data/
│   ├── raw/            # Raw JSON data (attractions, food, etc.)
│   └── vector_stores/  # FAISS indices (created after ingestion)
├── examples/           # Usage examples
├── scripts/            # Data ingestion & utilities
└── main.py             # CLI entry point
```

---

## What's Happening Under the Hood?

### 1. **Data Ingestion** (`scripts/ingest_data.py`)
   - Loads JSON data from `data/raw/`
   - Generates embeddings using `sentence-transformers`
   - Stores in FAISS vector indices
   - Saves to `data/vector_stores/`

### 2. **Retrieval** (`src/retrievers/`)
   - Separate retrievers for attractions, food, tips, etc.
   - Filters results based on budget, dietary restrictions, tags
   - Returns top-k most relevant results with metadata

### 3. **LangGraph Workflow** (`src/graph/`)
   - **Intent Analyzer**: Parses user preferences
   - **Parallel Retrievers**: Queries multiple knowledge sources simultaneously
   - **Context Aggregator**: Combines results into structured context
   - **(Coming next)**: Generation & Validation nodes

### 4. **Utilities** (`src/utils/`)
   - **Embeddings**: Converts text to vectors
   - **Geo**: Distance calculations, clustering
   - **Time**: Opening hours, seasonal matching

---

## Next Steps

### Add More Data
Create your own JSON files in `data/raw/` following the format:

**Attractions:**
```json
{
  "id": "unique_id",
  "name": "Attraction Name",
  "description": "...",
  "category": "museum",
  "coordinates": {"latitude": 48.8, "longitude": 2.3},
  "admission_fee": 10.0,
  "tags": ["art", "indoor"]
}
```

**Food:**
```json
{
  "id": "unique_id",
  "name": "Restaurant Name",
  "description": "...",
  "cuisine": ["french"],
  "dietary_options": ["vegetarian"],
  "price_range": "€€",
  "avg_cost_per_person": 20.0
}
```

Then re-run ingestion:
```bash
python scripts/ingest_data.py
```

### Explore the Code

1. Start with `examples/basic_planner.py` to understand the flow
2. Look at `src/graph/workflow.py` to see the LangGraph structure
3. Check `src/retrievers/knowledge_retrievers.py` for RAG logic
4. Modify `src/models/schemas.py` to add new fields

### Extend Functionality

- Add more retriever types (transport, accommodation)
- Implement itinerary generation with LLM
- Add constraint validation logic
- Create a web UI with Streamlit/Gradio

---

## Troubleshooting

### Issue: `ModuleNotFoundError`
**Solution:** Make sure virtual environment is activated and dependencies installed:
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Issue: Ollama connection error
**Solution:** Ensure Ollama is running:
```bash
ollama serve
```

### Issue: No data found
**Solution:** Run ingestion script:
```bash
python scripts/ingest_data.py
```

### Issue: Import errors
**Solution:** Run scripts from project root:
```bash
# From travelplanner-rag/ directory
python examples/basic_planner.py
```

---

## Learn More

- **LangChain Docs**: https://python.langchain.com/
- **LangGraph Guide**: https://langchain-ai.github.io/langgraph/
- **Sentence Transformers**: https://www.sbert.net/
- **FAISS**: https://github.com/facebookresearch/faiss

---

**Ready to build real RAG systems? Start experimenting!** 🚀