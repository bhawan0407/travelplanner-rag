"""Simple test to verify the setup is working."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_imports():
    """Test that all core modules can be imported."""
    print("Testing imports...")
    
    try:
        from src.config import settings
        print("✓ Config module")
        
        from src.models import UserPreferences, BudgetLevel, Attraction
        print("✓ Models module")
        
        from src.utils import get_embedding_model, haversine_distance
        print("✓ Utils module")
        
        from src.retrievers import MultiSourceRetriever, AttractionRetriever
        print("✓ Retrievers module")
        
        from src.graph import PlannerState, planner_graph
        print("✓ Graph module")
        
        print("\n✓ All imports successful!")
        return True
        
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        return False


def test_embeddings():
    """Test embedding generation."""
    print("\nTesting embeddings...")
    
    try:
        from src.utils import get_embedding_model
        
        model = get_embedding_model()
        text = "Paris is a beautiful city"
        embedding = model.embed_text(text)
        
        print(f"✓ Generated embedding: shape={embedding.shape}, dtype={embedding.dtype}")
        
        # Test similarity
        similarity = model.similarity("Paris is great", "Paris is beautiful")
        print(f"✓ Similarity score: {similarity:.4f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Embedding error: {e}")
        return False


def test_geo_utils():
    """Test geospatial utilities."""
    print("\nTesting geo utilities...")
    
    try:
        from src.models import Coordinates
        from src.utils import haversine_distance, is_within_radius
        
        # Eiffel Tower and Louvre
        eiffel = Coordinates(latitude=48.8584, longitude=2.2945)
        louvre = Coordinates(latitude=48.8606, longitude=2.3376)
        
        distance = haversine_distance(eiffel, louvre)
        print(f"✓ Distance Eiffel to Louvre: {distance:.2f} km")
        
        within = is_within_radius(eiffel, louvre, radius_km=5.0)
        print(f"✓ Within 5km: {within}")
        
        return True
        
    except Exception as e:
        print(f"❌ Geo utils error: {e}")
        return False


def test_data_loading():
    """Test loading sample data files."""
    print("\nTesting data loading...")
    
    try:
        import json
        from src.config import settings
        
        attractions_file = settings.data_raw_path / "attractions_paris.json"
        
        if not attractions_file.exists():
            print(f"⚠ Data file not found: {attractions_file}")
            return False
        
        with open(attractions_file) as f:
            data = json.load(f)
        
        print(f"✓ Loaded {len(data)} attractions from {attractions_file.name}")
        
        if data:
            print(f"  Example: {data[0]['name']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Data loading error: {e}")
        return False


def test_vector_store():
    """Test vector store functionality."""
    print("\nTesting vector store...")
    
    try:
        from src.retrievers import FAISSVectorStore
        from src.utils import get_embedding_model
        
        # Create a small test index
        store = FAISSVectorStore(dimension=384)
        embedding_model = get_embedding_model()
        
        texts = ["Paris is beautiful", "Rome has great food", "Tokyo is modern"]
        embeddings = embedding_model.embed_texts(texts)
        metadatas = [{"city": "Paris"}, {"city": "Rome"}, {"city": "Tokyo"}]
        
        store.add_documents(texts, embeddings.tolist(), metadatas)
        print(f"✓ Added {len(texts)} documents to vector store")
        
        # Test search
        query_emb = embedding_model.embed_text("beautiful city")
        results = store.similarity_search(query_emb.tolist(), k=2)
        
        print(f"✓ Search returned {len(results)} results")
        if results:
            print(f"  Top result: {results[0]['text']} (score: {results[0]['score']:.4f})")
        
        return True
        
    except Exception as e:
        print(f"❌ Vector store error: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Travel Planner - Setup Verification")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Embeddings", test_embeddings),
        ("Geo Utils", test_geo_utils),
        ("Data Loading", test_data_loading),
        ("Vector Store", test_vector_store),
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\n❌ Test '{name}' failed with exception: {e}")
            results[name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, passed_test in results.items():
        status = "✓ PASS" if passed_test else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Setup is working correctly.")
    else:
        print("\n⚠ Some tests failed. Check errors above.")
    
    print("=" * 60)


if __name__ == "__main__":
    main()