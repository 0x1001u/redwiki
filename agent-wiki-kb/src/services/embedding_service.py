"""Embedding service for generating vector representations."""

from sentence_transformers import SentenceTransformer
from typing import List, Union
from src.core.config import settings
import numpy as np


class EmbeddingService:
    """Service for generating embeddings using BGE-M3 model."""
    
    def __init__(self):
        self.model_name = settings.embedding_model
        self.dimension = settings.embedding_dimension
        self._model = None
    
    @property
    def model(self) -> SentenceTransformer:
        """Lazy load the embedding model."""
        if self._model is None:
            self._model = SentenceTransformer(
                self.model_name,
                trust_remote_code=True
            )
        return self._model
    
    def encode(
        self,
        texts: Union[str, List[str]],
        batch_size: int = 32,
        normalize_embeddings: bool = True,
        show_progress_bar: bool = False
    ) -> Union[np.ndarray, List[np.ndarray]]:
        """
        Encode texts into embeddings.
        
        Args:
            texts: Single text or list of texts to encode
            batch_size: Batch size for encoding
            normalize_embeddings: Whether to normalize embeddings
            show_progress_bar: Whether to show progress bar
            
        Returns:
            Numpy array or list of embeddings
        """
        if isinstance(texts, str):
            texts = [texts]
            single_input = True
        else:
            single_input = False
        
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            normalize_embeddings=normalize_embeddings,
            show_progress_bar=show_progress_bar,
            convert_to_numpy=True
        )
        
        if single_input:
            return embeddings[0]
        return embeddings
    
    def encode_queries(self, queries: Union[str, List[str]]) -> np.ndarray:
        """
        Encode queries with query-specific prompt.
        
        Args:
            queries: Single query or list of queries
            
        Returns:
            Query embeddings
        """
        if isinstance(queries, str):
            queries = [queries]
        
        # BGE-M3 supports query prompt for better retrieval
        query_texts = [f"Represent this question for searching: {q}" for q in queries]
        return self.encode(query_texts, normalize_embeddings=True)
    
    def encode_documents(self, documents: Union[str, List[str]]) -> np.ndarray:
        """
        Encode documents with document-specific prompt.
        
        Args:
            documents: Single document or list of documents
            
        Returns:
            Document embeddings
        """
        if isinstance(documents, str):
            documents = [documents]
        
        # BGE-M3 supports document prompt for better retrieval
        doc_texts = [f"Represent this document for retrieval: {d}" for d in documents]
        return self.encode(doc_texts, normalize_embeddings=True)
    
    def get_dimension(self) -> int:
        """Get embedding dimension."""
        return self.dimension
    
    def similarity(
        self,
        embedding1: np.ndarray,
        embedding2: np.ndarray,
        metric: str = "cosine"
    ) -> float:
        """
        Calculate similarity between two embeddings.
        
        Args:
            embedding1: First embedding
            embedding2: Second embedding
            metric: Similarity metric (cosine, euclidean, dot)
            
        Returns:
            Similarity score
        """
        if metric == "cosine":
            return float(np.dot(embedding1, embedding2))
        elif metric == "euclidean":
            return float(-np.linalg.norm(embedding1 - embedding2))
        elif metric == "dot":
            return float(np.dot(embedding1, embedding2))
        else:
            raise ValueError(f"Unknown metric: {metric}")


# Global instance
embedding_service = EmbeddingService()
