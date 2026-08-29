"""Qdrant vector database service."""

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    SearchParams,
    CreateCollectionOperationInfo,
)
from typing import List, Dict, Any, Optional
from src.core.config import settings
import uuid
import numpy as np


class QdrantService:
    """Service for managing vector storage in Qdrant."""
    
    def __init__(self):
        self.client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key
        )
        self.collection_name = settings.vector_collection_name
        self.dimension = settings.embedding_dimension
    
    def ensure_collection(self) -> bool:
        """Ensure the knowledge collection exists."""
        try:
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]
            
            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.dimension,
                        distance=Distance.COSINE
                    ),
                    on_disk_payload=True
                )
                # Create indexes for filtering
                self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="schema_type",
                    field_schema="keyword"
                )
                self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="tags",
                    field_schema="keyword"
                )
                return True
            return False
        except Exception as e:
            print(f"Error ensuring collection: {e}")
            return False
    
    def upsert(
        self,
        vector: np.ndarray,
        payload: Dict[str, Any],
        vector_id: Optional[str] = None
    ) -> str:
        """
        Upsert a vector with payload.
        
        Args:
            vector: Embedding vector
            payload: Metadata payload
            vector_id: Optional ID for the vector
            
        Returns:
            Vector ID
        """
        if vector_id is None:
            vector_id = str(uuid.uuid4())
        
        point = PointStruct(
            id=vector_id,
            vector=vector.tolist(),
            payload=payload
        )
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=[point]
        )
        
        return vector_id
    
    def search(
        self,
        query_vector: np.ndarray,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors.
        
        Args:
            query_vector: Query embedding
            limit: Maximum number of results
            filters: Optional filters
            
        Returns:
            List of search results with scores and payloads
        """
        search_params = SearchParams(
            hnsw_ef=128,
            exact=False
        )
        
        # Build filter if provided
        query_filter = None
        if filters:
            conditions = []
            if "schema_type" in filters:
                conditions.append(
                    FieldCondition(
                        key="schema_type",
                        match=MatchValue(value=filters["schema_type"])
                    )
                )
            if "tags" in filters:
                conditions.append(
                    FieldCondition(
                        key="tags",
                        match=MatchValue(value=filters["tags"])
                    )
                )
            if conditions:
                query_filter = Filter(must=conditions)
        
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector.tolist(),
            query_filter=query_filter,
            search_params=search_params,
            limit=limit,
            with_payload=True,
            with_vectors=False
        )
        
        return [
            {
                "id": result.id,
                "score": result.score,
                "payload": result.payload
            }
            for result in results
        ]
    
    def get(self, vector_id: str) -> Optional[Dict[str, Any]]:
        """Get a vector by ID."""
        result = self.client.retrieve(
            collection_name=self.collection_name,
            ids=[vector_id],
            with_payload=True,
            with_vectors=False
        )
        
        if result:
            return {
                "id": result[0].id,
                "payload": result[0].payload
            }
        return None
    
    def delete(self, vector_id: str) -> bool:
        """Delete a vector by ID."""
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=[vector_id]
            )
            return True
        except Exception as e:
            print(f"Error deleting vector: {e}")
            return False
    
    def count(self) -> int:
        """Get total count of vectors."""
        try:
            info = self.client.get_collection(self.collection_name)
            return info.points_count or 0
        except Exception as e:
            print(f"Error counting vectors: {e}")
            return 0
    
    def health_check(self) -> bool:
        """Check Qdrant connection health."""
        try:
            self.client.get_collections()
            return True
        except Exception as e:
            print(f"Qdrant health check failed: {e}")
            return False


# Global instance
qdrant_service = QdrantService()
