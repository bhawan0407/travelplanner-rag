"""Data ingestion script to populate vector stores."""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any
from tqdm import tqdm

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config import settings
from src.utils.embeddings import get_embedding_model
from src.retrievers import (
    AttractionRetriever,
    FoodRetriever,
    KnowledgeSource,
)


def load_json_data(file_path: Path) -> List[Dict[str, Any]]:
    """Load JSON data from file.
    
    Args:
        file_path: Path to JSON file.
        
    Returns:
        List of data items.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def ingest_attractions(data_file: Path) -> None:
    """Ingest attraction data into vector store.
    
    Args:
        data_file: Path to attractions JSON file.
    """
    print(f"Ingesting attractions from {data_file}...")
    
    # Load data
    attractions = load_json_data(data_file)
    
    # Prepare texts and metadata
    texts = []
    metadatas = []
    
    for attraction in attractions:
        # Create searchable text
        text = f"{attraction['name']}. {attraction['description']} "
        text += f"Category: {attraction['category']}. "
        if attraction.get('tags'):
            text += f"Tags: {', '.join(attraction['tags'])}. "
        
        texts.append(text)
        
        # Store metadata
        metadata = {
            "id": attraction["id"],
            "name": attraction["name"],
            "category": attraction["category"],
            "admission_fee": attraction.get("admission_fee", 0.0),
            "duration_minutes": attraction.get("duration_minutes", 60),
            "tags": attraction.get("tags", []),
            "coordinates": attraction.get("coordinates", {}),
        }
        metadatas.append(metadata)
    
    # Generate embeddings
    print("Generating embeddings...")
    embedding_model = get_embedding_model()
    embeddings = embedding_model.embed_texts(texts)
    
    # Add to vector store
    print("Adding to vector store...")
    retriever = AttractionRetriever()
    retriever.vector_store.add_documents(
        texts=texts,
        embeddings=embeddings.tolist(),
        metadatas=metadatas,
    )
    
    # Save
    print("Saving vector store...")
    retriever.save()
    print(f"✓ Ingested {len(attractions)} attractions")


def ingest_food(data_file: Path) -> None:
    """Ingest food place data into vector store.
    
    Args:
        data_file: Path to food JSON file.
    """
    print(f"Ingesting food places from {data_file}...")
    
    # Load data
    food_places = load_json_data(data_file)
    
    # Prepare texts and metadata
    texts = []
    metadatas = []
    
    for place in food_places:
        # Create searchable text
        text = f"{place['name']}. {place['description']} "
        text += f"Cuisine: {', '.join(place.get('cuisine', []))}. "
        text += f"Dietary options: {', '.join(place.get('dietary_options', []))}. "
        text += f"Price range: {place.get('price_range', '€€')}."
        
        texts.append(text)
        
        # Store metadata
        metadata = {
            "id": place["id"],
            "name": place["name"],
            "cuisine": place.get("cuisine", []),
            "dietary_options": place.get("dietary_options", []),
            "price_range": place.get("price_range", "€€"),
            "avg_cost_per_person": place.get("avg_cost_per_person", 15.0),
            "coordinates": place.get("coordinates", {}),
        }
        metadatas.append(metadata)
    
    # Generate embeddings
    print("Generating embeddings...")
    embedding_model = get_embedding_model()
    embeddings = embedding_model.embed_texts(texts)
    
    # Add to vector store
    print("Adding to vector store...")
    retriever = FoodRetriever()
    retriever.vector_store.add_documents(
        texts=texts,
        embeddings=embeddings.tolist(),
        metadatas=metadatas,
    )
    
    # Save
    print("Saving vector store...")
    retriever.save()
    print(f"✓ Ingested {len(food_places)} food places")


def main():
    """Main ingestion script."""
    print("=" * 60)
    print("Travel Planner - Data Ingestion")
    print("=" * 60)
    
    # Ensure directories exist
    settings.ensure_directories()
    
    # Ingest attractions
    attractions_file = settings.data_raw_path / "attractions_paris.json"
    if attractions_file.exists():
        ingest_attractions(attractions_file)
    else:
        print(f"⚠ Attractions file not found: {attractions_file}")
    
    # Ingest food
    food_file = settings.data_raw_path / "food_paris.json"
    if food_file.exists():
        ingest_food(food_file)
    else:
        print(f"⚠ Food file not found: {food_file}")
    
    print("\n" + "=" * 60)
    print("Ingestion complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()