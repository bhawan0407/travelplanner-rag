"""Base vector store interface."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pathlib import Path
import json


class VectorStore(ABC):
    """Abstract base class for vector stores."""

    @abstractmethod
    def add_documents(
        self,
        texts: List[str],
        embeddings: List[List[float]],
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """Add documents to the vector store.
        
        Args:
            texts: List of text documents.
            embeddings: List of embedding vectors.
            metadatas: Optional metadata for each document.
        """
        pass

    @abstractmethod
    def similarity_search(
        self,
        query_embedding: List[float],
        k: int = 10,
    ) -> List[Dict[str, Any]]:
        """Search for similar documents.
        
        Args:
            query_embedding: Query embedding vector.
            k: Number of results to return.
            
        Returns:
            List of documents with metadata and scores.
        """
        pass

    @abstractmethod
    def save(self, path: Path) -> None:
        """Save the vector store to disk.
        
        Args:
            path: Path to save location.
        """
        pass

    @abstractmethod
    def load(self, path: Path) -> None:
        """Load the vector store from disk.
        
        Args:
            path: Path to load location.
        """
        pass


class FAISSVectorStore(VectorStore):
    """FAISS-based vector store implementation."""

    def __init__(self, dimension: int = 384):
        """Initialize FAISS vector store.
        
        Args:
            dimension: Dimension of embedding vectors.
        """
        import faiss
        
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.texts: List[str] = []
        self.metadatas: List[Dict[str, Any]] = []

    def add_documents(
        self,
        texts: List[str],
        embeddings: List[List[float]],
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """Add documents to FAISS index."""
        import numpy as np
        
        if metadatas is None:
            metadatas = [{} for _ in texts]
        
        embeddings_array = np.array(embeddings).astype('float32')
        self.index.add(embeddings_array)
        self.texts.extend(texts)
        self.metadatas.extend(metadatas)

    def similarity_search(
        self,
        query_embedding: List[float],
        k: int = 10,
    ) -> List[Dict[str, Any]]:
        """Search FAISS index for similar documents."""
        import numpy as np
        
        query_array = np.array([query_embedding]).astype('float32')
        distances, indices = self.index.search(query_array, k)
        
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.texts):
                results.append({
                    "text": self.texts[idx],
                    "metadata": self.metadatas[idx],
                    "score": 1 / (1 + float(distance)),  # Convert distance to similarity
                })
        
        return results

    def save(self, path: Path) -> None:
        """Save FAISS index and metadata."""
        import faiss
        
        path.mkdir(parents=True, exist_ok=True)
        
        # Save FAISS index
        faiss.write_index(self.index, str(path / "index.faiss"))
        
        # Save texts and metadata
        with open(path / "texts.json", "w", encoding="utf-8") as f:
            json.dump(self.texts, f, ensure_ascii=False, indent=2)
        
        with open(path / "metadata.json", "w", encoding="utf-8") as f:
            json.dump(self.metadatas, f, ensure_ascii=False, indent=2)

    def load(self, path: Path) -> None:
        """Load FAISS index and metadata."""
        import faiss
        
        # Load FAISS index
        self.index = faiss.read_index(str(path / "index.faiss"))
        
        # Load texts and metadata
        with open(path / "texts.json", "r", encoding="utf-8") as f:
            self.texts = json.load(f)
        
        with open(path / "metadata.json", "r", encoding="utf-8") as f:
            self.metadatas = json.load(f)