# 🏗️ System Architecture

## High-Level Flow

```
┌──────────────────────────────────────────────────────────────────┐
│                        USER INPUT                                │
│  (Destination, Dates, Budget, Preferences, Constraints)          │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│                    INTENT ANALYZER NODE                          │
│  • Parse preferences                                             │
│  • Determine retrieval strategy                                  │
│  • Build filters for each knowledge source                       │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│                  PARALLEL RETRIEVAL NODES                        │
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │ Attractions │  │    Food     │  │    Tips     │            │
│  │  Retriever  │  │  Retriever  │  │  Retriever  │            │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘            │
│         │                │                │                     │
│    [FAISS Index]    [FAISS Index]    [FAISS Index]             │
│         │                │                │                     │
└─────────┼────────────────┼────────────────┼─────────────────────┘
          │                │                │
          └────────────────┴────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│                  CONTEXT AGGREGATOR NODE                         │
│  • Merge results from all retrievers                            │
│  • Format as structured context for LLM                         │
│  • Include evidence & metadata                                  │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│                  ITINERARY GENERATOR NODE                        │
│  • Call Ollama LLM with context                                 │
│  • Generate day-by-day plans                                    │
│  • Assign time slots & activities                               │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│                 CONSTRAINT VALIDATOR NODE                        │
│  • Check budget constraints                                     │
│  • Validate time feasibility                                    │
│  • Check walking distances                                      │
│  • Verify opening hours                                         │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                    ┌────────┴────────┐
                    │                 │
                 Valid?            Invalid?
                    │                 │
                    ▼                 ▼
            ┌──────────┐      ┌──────────────┐
            │   END    │      │   REPLAN     │
            │ (Output) │      │ (Iteration)  │
            └──────────┘      └──────┬───────┘
                                     │
                                     └─────► Back to Generator (Max 3x)
```

---

## Component Architecture

### 1. Configuration Layer (`src/config/`)
```
settings.py
   │
   ├─ Environment Variables (.env)
   ├─ Path Management
   ├─ LLM Configuration
   └─ Constraint Defaults
```

### 2. Data Models (`src/models/`)
```
schemas.py
   │
   ├─ UserPreferences
   ├─ Attraction
   ├─ FoodPlace
   ├─ TransportOption
   ├─ ItineraryItem
   ├─ DayPlan
   └─ Itinerary
```

### 3. Utilities (`src/utils/`)
```
embeddings.py          geo.py              time_utils.py
   │                      │                      │
   ├─ EmbeddingModel      ├─ haversine_distance  ├─ is_open_at
   ├─ embed_text          ├─ is_within_radius    ├─ get_next_available
   ├─ embed_texts         ├─ cluster_locations   ├─ is_seasonal_match
   └─ similarity          └─ walking_time        └─ split_time_blocks
```

### 4. Retrieval System (`src/retrievers/`)
```
vector_store.py
   │
   ├─ VectorStore (ABC)
   └─ FAISSVectorStore
         │
         ├─ add_documents()
         ├─ similarity_search()
         ├─ save()
         └─ load()

knowledge_retrievers.py
   │
   ├─ BaseRetriever
   │     │
   │     ├─ retrieve()
   │     └─ _apply_filters()
   │
   ├─ AttractionRetriever
   ├─ FoodRetriever
   ├─ TipsRetriever
   ├─ ItineraryRetriever
   └─ MultiSourceRetriever
         │
         └─ retrieve_all() [Parallel]
```

### 5. LangGraph Workflow (`src/graph/`)
```
state.py
   │
   └─ PlannerState (TypedDict)
         │
         ├─ user_preferences
         ├─ retrieved_contexts
         ├─ draft_itinerary
         ├─ validation_results
         └─ final_itinerary

nodes.py
   │
   ├─ IntentAnalyzerNode
   ├─ ParallelRetrieverNode (x4)
   ├─ ContextAggregatorNode
   ├─ ItineraryGeneratorNode (TODO)
   └─ ConstraintValidatorNode (TODO)

workflow.py
   │
   └─ build_planning_graph()
         │
         └─ StateGraph → Compiled Graph
```

---

## Data Flow Example

### Input:
```python
UserPreferences(
    destinations=["Paris"],
    start_date=2024-06-15,
    end_date=2024-06-17,
    budget_level=BudgetLevel.BUDGET,
    dietary_restrictions=[DietaryRestriction.VEGETARIAN],
    interests=["art", "history"],
)
```

### Step 1: Intent Analysis
```python
{
    "parsed_intent": {
        "destinations": ["Paris"],
        "duration_days": 3,
        "budget_level": "budget",
        "dietary_needs": ["vegetarian"],
        "interests": ["art", "history"]
    },
    "retrieval_strategy": {
        "sources": [ATTRACTIONS, FOOD, TIPS, ITINERARIES],
        "filters": {
            "ATTRACTIONS": {"max_price": 10.0, "required_tags": ["art", "history"]},
            "FOOD": {"dietary_restrictions": ["vegetarian"], "budget_level": "budget"}
        }
    }
}
```

### Step 2: Parallel Retrieval
```
Query: "Paris art history places to visit"
   ↓
[Embedding] → [384-dim vector]
   ↓
[FAISS Search] → Top 10 attractions
   ↓
[Filter] → max_price ≤ 10, tags include "art" or "history"
   ↓
Results:
  1. Louvre Museum (score: 0.89)
  2. Notre-Dame Cathedral (score: 0.85)
  3. Musée d'Orsay (score: 0.82)
  ...
```

### Step 3: Context Aggregation
```markdown
## Trip Planning Context
Destinations: Paris
Duration: 3 days
Budget: budget

## Available Attractions
1. Louvre Museum - World's largest art museum...
   Score: 0.89
   Metadata: {"admission_fee": 17.0, "duration": 180, "tags": ["art", "museum"]}

2. Notre-Dame Cathedral - Medieval Catholic cathedral...
   Score: 0.85
   Metadata: {"admission_fee": 0.0, "tags": ["architecture", "history", "free"]}
...
```

### Step 4: Generation (TODO)
```python
# LLM Call with context + constraints
itinerary = llm.generate(
    prompt=f"Create 3-day itinerary for Paris with {context}",
    constraints={"daily_budget": 30, "max_walking": 10km}
)
```

### Step 5: Validation (TODO)
```python
validation = {
    "budget_ok": total_cost <= daily_budget * 3,
    "time_ok": all_attractions_open_at_planned_times,
    "distance_ok": walking_distance_per_day <= 10km,
    "needs_replanning": False
}
```

### Output:
```python
Itinerary(
    days=[
        DayPlan(
            date=2024-06-15,
            items=[
                ItineraryItem(
                    time_start=09:00,
                    time_end=12:00,
                    title="Louvre Museum",
                    cost=17.0,
                    evidence=[Evidence(source="Wikivoyage", snippet="...")]
                ),
                ...
            ],
            total_cost=28.0,
            total_walking_km=4.2
        ),
        ...
    ]
)
```

---

## RAG-Specific Architecture

### Why Multiple Vector Stores?

```
Single Index (BAD)                     Multiple Indices (GOOD)
─────────────────                      ─────────────────────────
attractions                            attractions/
food                                      ├─ index.faiss
tips                     VS               ├─ texts.json
transport                                 └─ metadata.json
itineraries                            food/
  │                                       ├─ index.faiss
  └─ All mixed together                   ├─ texts.json
     • Hard to filter                     └─ metadata.json
     • Noise in results                tips/
     • No source-specific logic          ...
```

**Benefits:**
1. **Cleaner retrieval** - No cross-source pollution
2. **Source-specific filtering** - Apply budget filters only to food
3. **Independent updates** - Refresh one source without affecting others
4. **Conditional retrieval** - Only query needed sources

### Embedding Strategy

```
Input Text: "Louvre Museum - World's largest art museum..."
   │
   ▼
[sentence-transformers/all-MiniLM-L6-v2]
   │
   ▼
[384-dimensional vector]
   │
   └─ [0.023, -0.145, 0.678, ..., 0.234]
```

**Why this model?**
- ✅ Fast (CPU-friendly)
- ✅ Semantic understanding
- ✅ Good for short-medium texts
- ✅ Multilingual support

### Retrieval Enhancement

```
Base Query: "Paris vegetarian restaurants"
   │
   ▼
[Embedding]
   │
   ▼
[FAISS L2 Search] → Top 20 results
   │
   ▼
[Post-Processing Filters]
   ├─ dietary_options contains "vegetarian"
   ├─ price_range in ["€", "€€"] (budget filter)
   └─ coordinates within 2km of center
   │
   ▼
[Top 10 Filtered Results]
```

---

## Performance Characteristics

### Time Complexity
- **Embedding generation**: O(n × d) where n = texts, d = model dimension
- **FAISS search**: O(log N) for N documents (approximate)
- **Filtering**: O(k) for k results
- **Total per query**: ~100-500ms (local, CPU)

### Memory Usage
- **Embedding model**: ~80 MB
- **FAISS index** (1000 docs): ~1.5 MB
- **Total runtime**: ~200-300 MB

### Scalability
- **Current**: 100s of attractions/city
- **Scales to**: 10,000s with proper indexing
- **Bottleneck**: LLM generation (not retrieval)

---

## Extension Points

### 1. Add New Knowledge Source
```python
class AccommodationRetriever(BaseRetriever):
    def __init__(self):
        super().__init__(KnowledgeSource.ACCOMMODATION)
    
    def _apply_filters(self, results, filters):
        # Filter by price, location, amenities
        ...
```

### 2. Custom Ranking Logic
```python
def rerank_by_proximity(results, user_location):
    scored = []
    for result in results:
        dist = haversine_distance(user_location, result.coordinates)
        proximity_boost = 1 / (1 + dist)
        result.score = result.score * (1 + proximity_boost)
        scored.append(result)
    return sorted(scored, key=lambda x: x.score, reverse=True)
```

### 3. Hybrid Search
```python
# Combine semantic + keyword search
semantic_results = faiss_search(query_embedding)
keyword_results = bm25_search(query_text)
final_results = ensemble(semantic_results, keyword_results, weights=[0.7, 0.3])
```

---

**This architecture is designed for learning, extending, and production use.** 🚀