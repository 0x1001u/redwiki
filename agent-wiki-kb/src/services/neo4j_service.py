"""Neo4j graph database service."""

from neo4j import GraphDatabase
from typing import List, Dict, Any, Optional
from src.core.config import settings
import uuid


class Neo4jService:
    """Service for managing knowledge graph in Neo4j."""
    
    def __init__(self):
        self.driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password)
        )
        self.label_knowledge = settings.graph_label_knowledge
        self.label_relation = settings.graph_label_relation
    
    def close(self):
        """Close the driver connection."""
        self.driver.close()
    
    def create_knowledge_node(
        self,
        node_id: str,
        title: str,
        content: str,
        schema_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a knowledge node in the graph.
        
        Args:
            node_id: Unique identifier for the node
            title: Node title
            content: Node content
            schema_type: Type of knowledge (concept, entity, etc.)
            metadata: Additional metadata
            
        Returns:
            Node ID
        """
        with self.driver.session() as session:
            result = session.run(
                f"""
                MERGE (n:{self.label_knowledge} {{id: $node_id}})
                SET n.title = $title,
                    n.content = $content,
                    n.schema_type = $schema_type,
                    n.metadata = $metadata,
                    n.updated_at = datetime()
                RETURN n.id as id
                """,
                node_id=node_id,
                title=title,
                content=content,
                schema_type=schema_type,
                metadata=metadata or {}
            )
            return result.single()["id"]
    
    def create_relation(
        self,
        source_id: str,
        target_id: str,
        relation_type: str,
        weight: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a relation between two knowledge nodes.
        
        Args:
            source_id: Source node ID
            target_id: Target node ID
            relation_type: Type of relation
            weight: Relation weight
            metadata: Additional metadata
            
        Returns:
            Relation information
        """
        with self.driver.session() as session:
            result = session.run(
                f"""
                MATCH (source:{self.label_knowledge} {{id: $source_id}})
                MATCH (target:{self.label_knowledge} {{id: $target_id}})
                MERGE (source)-[r:{self.label_relation} {{
                    type: $relation_type,
                    target_id: $target_id
                }}]->(target)
                SET r.weight = $weight,
                    r.metadata = $metadata,
                    r.created_at = datetime()
                RETURN r
                """,
                source_id=source_id,
                target_id=target_id,
                relation_type=relation_type,
                weight=weight,
                metadata=metadata or {}
            )
            record = result.single()
            if record:
                rel = record["r"]
                return {
                    "source_id": source_id,
                    "target_id": target_id,
                    "relation_type": relation_type,
                    "weight": rel.get("weight", 1.0),
                    "metadata": rel.get("metadata", {})
                }
            return {}
    
    def get_relations(
        self,
        node_id: str,
        direction: str = "both",
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get relations for a knowledge node.
        
        Args:
            node_id: Node ID
            direction: Direction of relations (outgoing, incoming, both)
            limit: Maximum number of relations
            
        Returns:
            List of relations
        """
        with self.driver.session() as session:
            if direction == "outgoing":
                query = f"""
                MATCH (n:{self.label_knowledge} {{id: $node_id}})-[r:{self.label_relation}]->(m:{self.label_knowledge})
                RETURN m.id as target_id, m.title as target_title, 
                       r.type as relation_type, r.weight as weight,
                       r.metadata as metadata
                LIMIT $limit
                """
            elif direction == "incoming":
                query = f"""
                MATCH (m:{self.label_knowledge})-[r:{self.label_relation}]->(n:{self.label_knowledge} {{id: $node_id}})
                RETURN m.id as source_id, m.title as source_title,
                       r.type as relation_type, r.weight as weight,
                       r.metadata as metadata
                LIMIT $limit
                """
            else:  # both
                query = f"""
                MATCH (n:{self.label_knowledge} {{id: $node_id}})-[r:{self.label_relation}]-(m:{self.label_knowledge})
                WHERE n.id <> m.id
                RETURN m.id as connected_id, m.title as connected_title,
                       r.type as relation_type, r.weight as weight,
                       r.metadata as metadata,
                       CASE WHEN EXISTS((n)-[r]->(m)) THEN 'outgoing' ELSE 'incoming' END as direction
                LIMIT $limit
                """
            
            result = session.run(query, node_id=node_id, limit=limit)
            relations = []
            for record in result:
                relations.append(record.data())
            return relations
    
    def search_nodes(
        self,
        query_text: str,
        schema_type: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search for knowledge nodes by text.
        
        Args:
            query_text: Search query
            schema_type: Optional schema type filter
            limit: Maximum results
            
        Returns:
            List of matching nodes
        """
        with self.driver.session() as session:
            if schema_type:
                query = f"""
                MATCH (n:{self.label_knowledge})
                WHERE (n.title CONTAINS $query OR n.content CONTAINS $query)
                  AND n.schema_type = $schema_type
                RETURN n.id as id, n.title as title, n.schema_type as schema_type,
                       n.metadata as metadata
                LIMIT $limit
                """
                result = session.run(
                    query,
                    query=query_text,
                    schema_type=schema_type,
                    limit=limit
                )
            else:
                query = f"""
                MATCH (n:{self.label_knowledge})
                WHERE n.title CONTAINS $query OR n.content CONTAINS $query
                RETURN n.id as id, n.title as title, n.schema_type as schema_type,
                       n.metadata as metadata
                LIMIT $limit
                """
                result = session.run(query, query=query_text, limit=limit)
            
            return [record.data() for record in result]
    
    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get a knowledge node by ID."""
        with self.driver.session() as session:
            result = session.run(
                f"""
                MATCH (n:{self.label_knowledge} {{id: $node_id}})
                RETURN n.id as id, n.title as title, n.content as content,
                       n.schema_type as schema_type, n.metadata as metadata,
                       n.created_at as created_at, n.updated_at as updated_at
                """,
                node_id=node_id
            )
            record = result.single()
            if record:
                return record.data()
            return None
    
    def delete_node(self, node_id: str) -> bool:
        """Delete a knowledge node and its relations."""
        with self.driver.session() as session:
            session.run(
                f"""
                MATCH (n:{self.label_knowledge} {{id: $node_id}})
                DETACH DELETE n
                """,
                node_id=node_id
            )
            return True
    
    def health_check(self) -> bool:
        """Check Neo4j connection health."""
        try:
            with self.driver.session() as session:
                result = session.run("RETURN 1 AS check")
                return result.single() is not None
        except Exception as e:
            print(f"Neo4j health check failed: {e}")
            return False


# Global instance
neo4j_service = Neo4jService()
