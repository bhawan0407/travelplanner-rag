"""Embedding utilities for RAG."""

from typing import List, Optional
from sentence_transformers import SentenceTransformer
import numpy as np

from src.config import settings


class EmbeddingModel:
    """Wrapper for sentence-transformers embedding model."""

    def __init__(self, model_name: Optional[str] = None):
        """Initialize embedding model.
        
        Args:
            model_name: Name of the sentence-transformers model.
                       Defaults to settings.embedding_model.
        """
        self.model_name = model_name or settings.embedding_model
        self._model: Optional[SentenceTransformer] = None

    @property
    def model(self) -> SentenceTransformer:
        """Lazy load the embedding model."""
        if self._model is None:
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def embed_text(self, text: str) -> np.ndarray:
        """Generate embedding for a single text.
        
        Args:
            text: Input text to embed.
            
        Returns:
            Embedding vector as numpy array.
        """
        return self.model.encode(text, convert_to_numpy=True)

    def embed_texts(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed.
            batch_size: Batch size for encoding.
            
        Returns:
            Matrix of embeddings with shape (len(texts), embedding_dim).
        """
        return self.model.encode(
            texts,
            batch_size=batch_size,
            convert_to_numpy=True,
            show_progress_bar=True,
        )

    def similarity(self, text1: str, text2: str) -> float:
        """Calculate cosine similarity between two texts.
        
        Args:
            text1: First text.
            text2: Second text.
            
        Returns:
            Cosine similarity score between 0 and 1.
        """
        emb1 = self.embed_text(text1)
        emb2 = self.embed_text(text2)
        
        # Cosine similarity
        similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        return float(similarity)


# Global embedding model instance
_embedding_model: Optional[EmbeddingModel] = None


def get_embedding_model() -> EmbeddingModel:
    """Get or create global embedding model instance."""
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = EmbeddingModel()
    return _embedding_model