# 🗺️ RAG-Based Travel Planner - Complete Setup

## 📋 Project Summary

**A production-grade, multi-source RAG system for intelligent travel itinerary planning using LangChain, LangGraph, and local LLMs.**

### Key Features
- 🧠 **Multi-source RAG** with separate vector stores
- 🔄 **LangGraph orchestration** with parallel retrieval
- 🎯 **Constraint-aware planning** (budget, dietary, time, distance)
- 📍 **Geospatial intelligence** (clustering, proximity)
- 🕐 **Time-aware** (opening hours, seasonal matching)
- 💰 **Zero-cost** (runs entirely locally)

---

## 🚀 Quick Start

```bash
# 1. Install Ollama and pull a model
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3

# 2. Setup project
git clone <your-repo>
cd travelplanner-rag
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Configure environment
cp .env.template .env

# 4. Ingest sample data
python scripts/ingest_data.py

# 5. Run example
python examples/basic_planner.py

# 6. Test setup
python tests/test_setup.py
```

---

## 📁 Project Structure

```
travelplanner-rag/
├── 📄 README.md                    # Project overview
├── 📄 QUICKSTART.md                # Detailed setup guide
├── 📄 ARCHITECTURE.md              # System design & data flow
├── 📄 NEXT_STEPS.md                # Implementation roadmap
├── 📄 WHAT_YOU_BUILT.md            # Learning summary
│
├── src/
│   ├── config/                     # Configuration management
│   ├── models/                     # Pydantic schemas
│   ├── utils/                      # Embeddings, geo, time utilities
│   ├── retrievers/                 # RAG retrieval logic
│   └── graph/                      # LangGraph workflow
│
├── data/
│   ├── raw/                        # JSON source data
│   │   ├── attractions_paris.json
│   │   └── food_paris.json
│   ├── processed/                  # (Reserved for future use)
│   └── vector_stores/              # FAISS indices (auto-created)
│
├── scripts/
│   └── ingest_data.py              # Data ingestion pipeline
│
├── examples/
│   └── basic_planner.py            # Usage example
│
├── tests/
│   └── test_setup.py               # Verification tests
│
├── main.py                         # CLI entry point
├── requirements.txt                # Python dependencies
└── .env.template                   # Environment config template
```

---

## 🎯 What Works Now

### ✅ Phase 1 Complete
- [x] Project scaffolding
- [x] Configuration system
- [x] Data models (Pydantic)
- [x] Embedding utilities
- [x] Geospatial & time utilities
- [x] Vector store implementation (FAISS)
- [x] Multi-source retrievers with filtering
- [x] LangGraph workflow (retrieval phase)
- [x] Sample data (Paris attractions & food)
- [x] Data ingestion pipeline
- [x] CLI interface
- [x] Example scripts
- [x] Documentation

### Current Capabilities
1. Parse user preferences
2. Determine retrieval strategy
3. Query multiple knowledge sources in parallel
4. Apply budget/dietary/tag filters
5. Aggregate context with evidence
6. Return structured results

---

## 🚧 Phase 2 - Next to Implement

### Priority 1: LLM Integration
- [ ] Create `src/agents/llm_service.py`
- [ ] Implement `ItineraryGeneratorNode`
- [ ] Design prompt templates
- [ ] Parse structured outputs

### Priority 2: Validation & Replanning
- [ ] Create `src/agents/validator.py`
- [ ] Implement `ConstraintValidatorNode`
- [ ] Add replanning logic
- [ ] Complete LangGraph workflow

### Priority 3: More Data
- [ ] Add tips data
- [ ] Add past itineraries
- [ ] Add more cities
- [ ] Expand sample size

### Priority 4: Testing & Polish
- [ ] Unit tests
- [ ] Integration tests
- [ ] Error handling
- [ ] Logging

---

## 📊 Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| LLM | Ollama (Llama3/Mistral) | Local, free, private |
| Embeddings | sentence-transformers | Semantic search |
| Vector DB | FAISS | Fast similarity search |
| Orchestration | LangGraph | State machine workflow |
| Framework | LangChain | RAG primitives |
| Models | Pydantic | Type safety |
| CLI | Typer + Rich | User interface |
| Geo | Custom (Haversine) | Distance calculations |

---

## 🎓 Learning Outcomes

### RAG Concepts
- Multi-source retrieval architecture
- Conditional query routing
- Metadata filtering strategies
- Evidence preservation
- Vector store management

### LangGraph Patterns
- State machine design
- Parallel node execution
- Conditional edges
- Error recovery

### Production Practices
- Modular architecture
- Configuration management
- Type safety with Pydantic
- CLI design
- Documentation

---

## 📖 Documentation Guide

| Document | Purpose | Read When |
|----------|---------|-----------|
| **README.md** | Overview & features | First |
| **QUICKSTART.md** | Step-by-step setup | Setting up |
| **ARCHITECTURE.md** | System design deep-dive | Understanding internals |
| **NEXT_STEPS.md** | Implementation roadmap | Extending project |
| **WHAT_YOU_BUILT.md** | Learning summary & interview prep | Showcasing project |

---

## 🛠️ Common Commands

```bash
# Data Management
python scripts/ingest_data.py              # Ingest data into vector stores

# Running Examples
python examples/basic_planner.py           # Basic retrieval example

# CLI Usage
python main.py plan -d Paris --days 3      # Plan a trip
python main.py interactive                 # Interactive mode
python main.py ingest                      # Ingest via CLI

# Testing
python tests/test_setup.py                 # Verify setup

# Development
pip install -r requirements.txt            # Install dependencies
source venv/bin/activate                   # Activate env (Unix)
venv\Scripts\activate                      # Activate env (Windows)
```

---

## 🐛 Troubleshooting

### Issue: Import errors
```bash
# Make sure you're in project root and venv is activated
cd /path/to/travelplanner-rag
source venv/bin/activate
python -c "import src; print('OK')"
```

### Issue: Ollama connection error
```bash
# Start Ollama server
ollama serve

# Verify it's running
curl http://localhost:11434/api/tags
```

### Issue: No embeddings model
```bash
# First run downloads the model automatically
# Or manually trigger download:
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"
```

### Issue: Vector stores not found
```bash
# Run ingestion first
python scripts/ingest_data.py

# Check if created
ls -la data/vector_stores/
```

---

## 🤝 Contributing

Want to extend this project? See `NEXT_STEPS.md` for ideas:
- Add more retriever types
- Implement LLM generation
- Create web UI with Streamlit
- Add more cities and data
- Build evaluation metrics

---

## 📄 License

MIT License - See LICENSE file

---

## 🙏 Acknowledgments

- LangChain & LangGraph teams
- Ollama for local LLM serving
- sentence-transformers for embeddings
- FAISS for vector search

---

## 📞 Support

- Check documentation files for detailed guides
- Review example scripts for usage patterns
- Run `python tests/test_setup.py` to verify installation
- Refer to `ARCHITECTURE.md` for system internals

---

**Built to learn real RAG, not toy examples.** 🚀

### Ready to Start?

1. Read `QUICKSTART.md` for setup
2. Run `python tests/test_setup.py` to verify
3. Try `python examples/basic_planner.py`
4. Check `NEXT_STEPS.md` for what to build next

**Happy learning!** 🎓✨