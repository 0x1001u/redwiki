"""Configuration management for Agent Wiki KB."""

from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    environment: str = "development"
    app_name: str = "agent-wiki-kb"
    debug: bool = True
    log_level: str = "INFO"
    
    # Database - PostgreSQL
    database_url: str = "postgresql://agentwiki:agentwiki_secret@localhost:5432/agent_wiki_kb"
    postgres_user: str = "agentwiki"
    postgres_password: str = "agentwiki_secret"
    postgres_db: str = "agent_wiki_kb"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    
    # Vector Database - Qdrant
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: Optional[str] = None
    
    # Graph Database - Neo4j
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "agentwiki_secret"
    neo4j_database: str = "neo4j"
    
    # Search Engine - Elasticsearch
    elasticsearch_url: str = "http://localhost:9200"
    elasticsearch_index: str = "agent_wiki_kb"
    
    # Cache & Message Queue - Redis
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"
    
    # Embedding Model
    embedding_model: str = "BAAI/bge-m3"
    embedding_dimension: int = 1024
    rerank_model: str = "BAAI/bge-reranker-v2-m3"
    
    # API Configuration
    api_prefix: str = "/api/v1"
    max_content_length: int = 10485760  # 10MB
    rate_limit_per_minute: int = 60
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Knowledge Base Settings
    default_schema_version: float = 1.0
    max_relations_per_node: int = 100
    vector_collection_name: str = "knowledge_embeddings"
    graph_label_knowledge: str = "Knowledge"
    graph_label_relation: str = "RelatedTo"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()
