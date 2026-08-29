"""Knowledge base service - orchestrates all storage backends."""

from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from src.models.db_models import KnowledgeEntry as DBKnowledgeEntry
from src.models.schemas import KnowledgeCreate, KnowledgeUpdate, KnowledgeResponse, SchemaType
from src.services.embedding_service import embedding_service
from src.services.qdrant_service import qdrant_service
from src.services.neo4j_service import neo4j_service


class KnowledgeService:
    """Service for managing knowledge entries across all storage backends."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, knowledge: KnowledgeCreate) -> KnowledgeResponse:
        """
        Create a new knowledge entry.
        
        This method:
        1. Creates the entry in PostgreSQL
        2. Generates embedding and stores in Qdrant
        3. Creates node in Neo4j graph
        """
        # Generate ID
        entry_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        # Create database entry
        db_entry = DBKnowledgeEntry(
            id=entry_id,
            title=knowledge.title,
            content=knowledge.content,
            schema_type=knowledge.schema_type.value,
            metadata=knowledge.metadata or {},
            tags=knowledge.tags or [],
            version=knowledge.version,
            source=knowledge.source,
            confidence_score=knowledge.confidence_score,
            created_at=now,
            updated_at=now
        )
        
        self.db.add(db_entry)
        self.db.commit()
        self.db.refresh(db_entry)
        
        try:
            # Generate embedding
            embedding_text = f"{knowledge.title}: {knowledge.content}"
            embedding = embedding_service.encode_documents(embedding_text)
            
            # Store in Qdrant
            vector_payload = {
                "title": knowledge.title,
                "content": knowledge.content,
                "schema_type": knowledge.schema_type.value,
                "tags": knowledge.tags or [],
                "source": knowledge.source,
                "db_id": entry_id
            }
            vector_id = qdrant_service.upsert(
                vector=embedding,
                payload=vector_payload,
                vector_id=f"kb_{entry_id}"
            )
            
            # Create graph node
            graph_node_id = neo4j_service.create_knowledge_node(
                node_id=entry_id,
                title=knowledge.title,
                content=knowledge.content,
                schema_type=knowledge.schema_type.value,
                metadata={
                    **knowledge.metadata,
                    "tags": knowledge.tags or []
                }
            )
            
            # Update database with references
            db_entry.embedding_id = vector_id
            db_entry.graph_node_id = entry_id  # Use same ID for graph
            self.db.commit()
            self.db.refresh(db_entry)
            
        except Exception as e:
            # Rollback on error
            self.db.rollback()
            # Clean up partial creations
            try:
                qdrant_service.delete(f"kb_{entry_id}")
                neo4j_service.delete_node(entry_id)
            except:
                pass
            raise e
        
        return KnowledgeResponse(
            id=db_entry.id,
            title=db_entry.title,
            content=db_entry.content,
            schema_type=SchemaType(db_entry.schema_type),
            metadata=db_entry.metadata,
            tags=db_entry.tags,
            version=db_entry.version,
            source=db_entry.source,
            confidence_score=db_entry.confidence_score,
            created_at=db_entry.created_at,
            updated_at=db_entry.updated_at,
            embedding_id=db_entry.embedding_id,
            graph_node_id=db_entry.graph_node_id
        )
    
    def get_by_id(self, entry_id: str) -> Optional[KnowledgeResponse]:
        """Get a knowledge entry by ID."""
        db_entry = self.db.query(DBKnowledgeEntry).filter(
            DBKnowledgeEntry.id == entry_id
        ).first()
        
        if not db_entry:
            return None
        
        return KnowledgeResponse(
            id=db_entry.id,
            title=db_entry.title,
            content=db_entry.content,
            schema_type=SchemaType(db_entry.schema_type),
            metadata=db_entry.metadata,
            tags=db_entry.tags,
            version=db_entry.version,
            source=db_entry.source,
            confidence_score=db_entry.confidence_score,
            created_at=db_entry.created_at,
            updated_at=db_entry.updated_at,
            embedding_id=db_entry.embedding_id,
            graph_node_id=db_entry.graph_node_id
        )
    
    def update(self, entry_id: str, update: KnowledgeUpdate) -> Optional[KnowledgeResponse]:
        """Update a knowledge entry."""
        db_entry = self.db.query(DBKnowledgeEntry).filter(
            DBKnowledgeEntry.id == entry_id
        ).first()
        
        if not db_entry:
            return None
        
        # Update fields
        update_data = update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "schema_type" and value:
                setattr(db_entry, field, value.value)
            else:
                setattr(db_entry, field, value)
        
        db_entry.updated_at = datetime.utcnow()
        db_entry.version += 1
        
        # Regenerate embedding if content changed
        if "content" in update_data or "title" in update_data:
            try:
                embedding_text = f"{db_entry.title}: {db_entry.content}"
                embedding = embedding_service.encode_documents(embedding_text)
                
                vector_payload = {
                    "title": db_entry.title,
                    "content": db_entry.content,
                    "schema_type": db_entry.schema_type,
                    "tags": db_entry.tags,
                    "source": db_entry.source,
                    "db_id": entry_id
                }
                
                qdrant_service.upsert(
                    vector=embedding,
                    payload=vector_payload,
                    vector_id=db_entry.embedding_id or f"kb_{entry_id}"
                )
                
                # Update graph node
                neo4j_service.create_knowledge_node(
                    node_id=entry_id,
                    title=db_entry.title,
                    content=db_entry.content,
                    schema_type=db_entry.schema_type,
                    metadata={
                        **db_entry.metadata,
                        "tags": db_entry.tags
                    }
                )
            except Exception as e:
                self.db.rollback()
                raise e
        
        self.db.commit()
        self.db.refresh(db_entry)
        
        return KnowledgeResponse(
            id=db_entry.id,
            title=db_entry.title,
            content=db_entry.content,
            schema_type=SchemaType(db_entry.schema_type),
            metadata=db_entry.metadata,
            tags=db_entry.tags,
            version=db_entry.version,
            source=db_entry.source,
            confidence_score=db_entry.confidence_score,
            created_at=db_entry.created_at,
            updated_at=db_entry.updated_at,
            embedding_id=db_entry.embedding_id,
            graph_node_id=db_entry.graph_node_id
        )
    
    def delete(self, entry_id: str) -> bool:
        """Delete a knowledge entry from all backends."""
        db_entry = self.db.query(DBKnowledgeEntry).filter(
            DBKnowledgeEntry.id == entry_id
        ).first()
        
        if not db_entry:
            return False
        
        try:
            # Delete from Qdrant
            if db_entry.embedding_id:
                qdrant_service.delete(db_entry.embedding_id)
            
            # Delete from Neo4j
            if db_entry.graph_node_id:
                neo4j_service.delete_node(db_entry.graph_node_id)
            
            # Delete from PostgreSQL
            self.db.delete(db_entry)
            self.db.commit()
            
            return True
        except Exception as e:
            self.db.rollback()
            raise e
    
    def search(
        self,
        query: str,
        mode: str = "hybrid",
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Search for knowledge entries using specified mode.
        
        Modes:
        - vector: Semantic search using embeddings
        - graph: Graph traversal and pattern matching
        - keyword: Full-text search (to be implemented with Elasticsearch)
        - hybrid: Combine multiple approaches
        """
        results = []
        
        if mode in ["vector", "hybrid"]:
            # Vector search
            query_embedding = embedding_service.encode_queries(query)
            vector_results = qdrant_service.search(
                query_vector=query_embedding,
                limit=limit,
                filters=filters
            )
            
            for result in vector_results:
                entry_id = result["payload"].get("db_id")
                if entry_id:
                    db_entry = self.get_by_id(entry_id)
                    if db_entry:
                        results.append({
                            "knowledge": db_entry,
                            "score": result["score"],
                            "match_type": "vector"
                        })
        
        if mode in ["graph", "hybrid"]:
            # Graph search
            graph_results = neo4j_service.search_nodes(
                query_text=query,
                limit=limit
            )
            
            for result in graph_results:
                entry_id = result["id"]
                db_entry = self.get_by_id(entry_id)
                if db_entry:
                    # Check if already in results
                    existing = next((r for r in results if r["knowledge"].id == entry_id), None)
                    if existing:
                        existing["match_type"] += "+graph"
                    else:
                        results.append({
                            "knowledge": db_entry,
                            "score": 0.8,  # Default score for graph matches
                            "match_type": "graph"
                        })
        
        # Sort by score and apply offset/limit
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[offset:offset + limit]
    
    def get_relations(self, entry_id: str) -> List[Dict[str, Any]]:
        """Get relations for a knowledge entry."""
        return neo4j_service.get_relations(entry_id)
    
    def create_relation(
        self,
        source_id: str,
        target_id: str,
        relation_type: str,
        weight: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a relation between two knowledge entries."""
        # Verify both entries exist
        source = self.get_by_id(source_id)
        target = self.get_by_id(target_id)
        
        if not source or not target:
            raise ValueError("Source or target knowledge entry not found")
        
        return neo4j_service.create_relation(
            source_id=source_id,
            target_id=target_id,
            relation_type=relation_type,
            weight=weight,
            metadata=metadata
        )
