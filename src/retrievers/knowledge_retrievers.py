"""Specialized retrievers for different knowledge sources."""

from typing import List, Dict, Any, Optional
from pathlib import Path
from enum import Enum

from src.retrievers.vector_store import VectorStore, FAISSVectorStore
from src.utils.embeddings import get_embedding_model
from src.config import settings
from src.models import (
    Attraction,
    FoodPlace,
    Evidence,
    DietaryRestriction,
    BudgetLevel,
)


class KnowledgeSource(str, Enum):
    """Types of knowledge sources."""
    ATTRACTIONS = "attractions"
    FOOD = "food"
    TRANSPORT = "transport"
    TIPS = "tips"
    ITINERARIES = "itineraries"


class BaseRetriever:
    """Base retriever for a specific knowledge source."""

    def __init__(
        self,
        source_type: KnowledgeSource,
        vector_store: Optional[VectorStore] = None,
    ):
        """Initialize retriever.
        
        Args:
            source_type: Type of knowledge source.
            vector_store: Vector store instance. If None, creates new FAISS store.
        """
        self.source_type = source_type
        self.vector_store = vector_store or FAISSVectorStore(
            dimension=settings.embedding_dimension
        )
        self.embedding_model = get_embedding_model()
        self.store_path = settings.vector_store_path / source_type.value

    def retrieve(
        self,
        query: str,
        k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant documents.
        
        Args:
            query: Search query.
            k: Number of results to return.
            filters: Optional filters to apply (source-specific).
            
        Returns:
            List of retrieved documents with metadata.
        """
        # Generate query embedding
        query_embedding = self.embedding_model.embed_text(query)
        
        # Retrieve from vector store
        results = self.vector_store.similarity_search(
            query_embedding.tolist(),
            k=k * 2,  # Get more results for filtering
        )
        
        # Apply filters if provided
        if filters:
            results = self._apply_filters(results, filters)
        
        # Trim to k results
        return results[:k]

    def _apply_filters(
        self,
        results: List[Dict[str, Any]],
        filters: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Apply filters to results. Override in subclasses."""
        return results

    def save(self) -> None:
        """Save vector store to disk."""
        self.vector_store.save(self.store_path)

    def load(self) -> bool:
        """Load vector store from disk.
        
        Returns:
            True if loaded successfully, False otherwise.
        """
        if not self.store_path.exists():
            return False
        
        try:
            self.vector_store.load(self.store_path)
            return True
        except Exception as e:
            print(f"Error loading vector store: {e}")
            return False


class AttractionRetriever(BaseRetriever):
    """Retriever for attractions and points of interest."""

    def __init__(self, vector_store: Optional[VectorStore] = None):
        super().__init__(KnowledgeSource.ATTRACTIONS, vector_store)

    def _apply_filters(
        self,
        results: List[Dict[str, Any]],
        filters: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Filter attractions by category, tags, admission fee, etc."""
        filtered = []
        
        for result in results:
            metadata = result.get("metadata", {})
            
            # Filter by budget
            if "max_price" in filters:
                if metadata.get("admission_fee", 0) > filters["max_price"]:
                    continue
            
            # Filter by category
            if "categories" in filters:
                if metadata.get("category") not in filters["categories"]:
                    continue
            
            # Filter by tags
            if "required_tags" in filters:
                tags = metadata.get("tags", [])
                if not all(tag in tags for tag in filters["required_tags"]):
                    continue
            
            # Filter by excluded tags
            if "excluded_tags" in filters:
                tags = metadata.get("tags", [])
                if any(tag in tags for tag in filters["excluded_tags"]):
                    continue
            
            filtered.append(result)
        
        return filtered


class FoodRetriever(BaseRetriever):
    """Retriever for restaurants and food places."""

    def __init__(self, vector_store: Optional[VectorStore] = None):
        super().__init__(KnowledgeSource.FOOD, vector_store)

    def _apply_filters(
        self,
        results: List[Dict[str, Any]],
        filters: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Filter food places by dietary restrictions, price, cuisine, etc."""
        filtered = []
        
        for result in results:
            metadata = result.get("metadata", {})
            
            # Filter by dietary restrictions
            if "dietary_restrictions" in filters:
                available_options = metadata.get("dietary_options", [])
                required = filters["dietary_restrictions"]
                if not any(opt in available_options for opt in required):
                    continue
            
            # Filter by budget
            if "budget_level" in filters:
                budget = filters["budget_level"]
                price_range = metadata.get("price_range", "€€")
                
                if budget == BudgetLevel.BUDGET and price_range not in ["€", "€€"]:
                    continue
                elif budget == BudgetLevel.LUXURY and price_range == "€":
                    continue
            
            # Filter by cuisine
            if "cuisines" in filters:
                available_cuisines = metadata.get("cuisine", [])
                if not any(c in available_cuisines for c in filters["cuisines"]):
                    continue
            
            filtered.append(result)
        
        return filtered


class TipsRetriever(BaseRetriever):
    """Retriever for local tips and travel advice."""

    def __init__(self, vector_store: Optional[VectorStore] = None):
        super().__init__(KnowledgeSource.TIPS, vector_store)


class ItineraryRetriever(BaseRetriever):
    """Retriever for past itineraries."""

    def __init__(self, vector_store: Optional[VectorStore] = None):
        super().__init__(KnowledgeSource.ITINERARIES, vector_store)

    def _apply_filters(
        self,
        results: List[Dict[str, Any]],
        filters: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Filter past itineraries by destination, duration, budget, etc."""
        filtered = []
        
        for result in results:
            metadata = result.get("metadata", {})
            
            # Filter by destination
            if "destination" in filters:
                if metadata.get("destination") != filters["destination"]:
                    continue
            
            # Filter by duration
            if "duration_days" in filters:
                duration = metadata.get("duration_days", 0)
                target = filters["duration_days"]
                # Allow ±1 day flexibility
                if abs(duration - target) > 1:
                    continue
            
            filtered.append(result)
        
        return filtered


class MultiSourceRetriever:
    """Coordinator for retrieving from multiple sources."""

    def __init__(self):
        """Initialize all retrievers."""
        self.attractions = AttractionRetriever()
        self.food = FoodRetriever()
        self.tips = TipsRetriever()
        self.itineraries = ItineraryRetriever()

    def retrieve_all(
        self,
        query: str,
        sources: List[KnowledgeSource],
        k: int = 10,
        filters: Optional[Dict[KnowledgeSource, Dict[str, Any]]] = None,
    ) -> Dict[KnowledgeSource, List[Dict[str, Any]]]:
        """Retrieve from multiple sources in parallel.
        
        Args:
            query: Search query.
            sources: List of sources to query.
            k: Number of results per source.
            filters: Optional filters per source.
            
        Returns:
            Dictionary mapping source to results.
        """
        results = {}
        
        for source in sources:
            retriever = self._get_retriever(source)
            source_filters = filters.get(source) if filters else None
            results[source] = retriever.retrieve(query, k, source_filters)
        
        return results

    def _get_retriever(self, source: KnowledgeSource) -> BaseRetriever:
        """Get retriever for a specific source."""
        mapping = {
            KnowledgeSource.ATTRACTIONS: self.attractions,
            KnowledgeSource.FOOD: self.food,
            KnowledgeSource.TIPS: self.tips,
            KnowledgeSource.ITINERARIES: self.itineraries,
        }
        return mapping[source]

    def load_all(self) -> None:
        """Load all vector stores from disk."""
        self.attractions.load()
        self.food.load()
        self.tips.load()
        self.itineraries.load()