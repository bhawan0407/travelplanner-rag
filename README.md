# 🗺️ RAG-Based Travel Itinerary Planner

> **Constraint-aware, multi-source RAG system for intelligent travel itinerary generation**

A production-grade travel planning system that leverages Retrieval-Augmented Generation (RAG) with LangChain and LangGraph to create evidence-backed, constraint-aware travel itineraries.

## 🎯 Key Features

- **Multi-Source RAG**: Separate vector stores for attractions, food, transport, tips, and past itineraries
- **Constraint-Aware Planning**: Budget, accessibility, dietary restrictions, timing constraints
- **LangGraph Orchestration**: Conditional retrieval with parallel processing and fallback handling
- **Evidence-Backed**: Every recommendation includes source attribution
- **Time & Proximity Aware**: Considers opening hours, seasonal relevance, and walkability
- **Zero Cost**: Runs entirely on local LLMs (Ollama) and free data sources

## 🏗️ Architecture

```
User Input → Intent Analyzer → LangGraph Orchestrator
                                      ↓
                    ┌─────────────────┴─────────────────┐
                    ↓                                   ↓
            Parallel Retrievers                  Constraint Validator
         (Attractions, Food, Transport)               ↓
                    ↓                          Feasibility Check
            Context Aggregator                        ↓
                    ↓                            Replan if needed
            Itinerary Generator                       ↓
                    └─────────────────┬─────────────────┘
                                      ↓
                            Final Day-wise Plan
```

## 📦 Tech Stack

| Component      | Technology                          |
|----------------|-------------------------------------|
| LLM            | Ollama (Llama3 / Mistral)           |
| Embeddings     | sentence-transformers (all-MiniLM)  |
| Vector DB      | FAISS / Chroma                      |
| Orchestration  | LangChain + LangGraph               |
| Data Sources   | Wikivoyage, Kaggle, Custom scrapes  |
| Backend        | Python 3.10+                        |

## 🚀 Quick Start

### Prerequisites

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model
ollama pull llama3
```

### Installation

```bash
# Clone repository
git clone <repo-url>
cd travelplanner-rag

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.template .env
# Edit .env with your configurations
```

### Usage

```bash
# Ingest sample data
python scripts/ingest_data.py

# Run example itinerary generation
python examples/basic_planner.py

# Interactive CLI
python main.py
```

## 📁 Project Structure

```
travelplanner-rag/
├── src/
│   ├── config/              # Configuration management
│   ├── data/                # Data ingestion & processing
│   ├── retrievers/          # RAG retrieval logic
│   ├── graph/               # LangGraph nodes & workflows
│   ├── agents/              # Specialized agents
│   ├── utils/               # Utilities (embeddings, distance, time)
│   └── models/              # Pydantic models
├── data/
│   ├── raw/                 # Raw data sources
│   ├── processed/           # Cleaned data
│   └── vector_stores/       # FAISS/Chroma indices
├── examples/                # Example usage scripts
├── scripts/                 # Data ingestion & setup scripts
├── tests/                   # Unit tests
├── notebooks/               # Jupyter notebooks for exploration
└── main.py                  # CLI entry point
```

## 🎓 Learning Outcomes

This project teaches:

- **Real RAG patterns**: Multi-source, conditional retrieval
- **LangGraph orchestration**: State machines, parallel nodes, fallbacks
- **Constraint optimization**: Time, budget, distance, preferences
- **Evidence-based generation**: Source attribution and verification
- **Production practices**: Modular architecture, testing, error handling

## 📊 Data Sources

- **Attractions**: Wikivoyage, custom datasets
- **Reviews**: Kaggle travel datasets
- **Food**: OpenStreetMap food establishments
- **Transport**: Public transit documentation
- **Past itineraries**: Curated examples

## 🔧 Advanced Features

- [ ] Multi-city optimization
- [ ] Preference learning from feedback
- [ ] Real-time constraint validation
- [ ] Offline "what-if" replanning
- [ ] Export to Google Maps/PDF

## 📝 Example Output

```
Day 1 - Paris (Budget, Vegetarian, Walkable)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Morning (9:00 - 12:00)
├─ Jardin du Luxembourg [FREE]
│  └─ Source: Wikivoyage - "Beautiful free gardens"
├─ Walk to Latin Quarter (15 min)
└─ Panthéon exterior [FREE]

Lunch (12:30 - 13:30)
└─ Café de Flore - Vegetarian options €12-18
   └─ Source: TripAdvisor Review #4523

Afternoon (14:00 - 18:00)
└─ Seine River walk → Île de la Cité [FREE]
   └─ Source: Past itinerary "Budget Paris Day 1"
```

## 🤝 Contributing

Contributions welcome! Please read CONTRIBUTING.md first.

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- LangChain & LangGraph teams
- Wikivoyage contributors
- Open-source travel data community

---

**Built to learn real RAG, not toy examples.**