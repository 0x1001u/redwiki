"""FastAPI application main entry point."""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from src.core.config import settings
from src.core.database import get_db, init_db
from src.models.schemas import (
    KnowledgeCreate,
    KnowledgeUpdate,
    KnowledgeResponse,
    SearchQuery,
    AgentQuery,
    AgentResponse,
    HealthCheck
)
from src.services.knowledge_service import KnowledgeService


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="LLM Wiki-based Knowledge Base for AI Agents",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()
    # Ensure Qdrant collection exists
    from src.services.qdrant_service import qdrant_service
    qdrant_service.ensure_collection()


@app.get("/health", response_model=HealthCheck)
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint."""
    from src.services.qdrant_service import qdrant_service
    from src.services.neo4j_service import neo4j_service
    
    services = {
        "postgres": True,  # If we got here, DB is working
        "qdrant": qdrant_service.health_check(),
        "neo4j": neo4j_service.health_check(),
    }
    
    all_healthy = all(services.values())
    
    return HealthCheck(
        status="healthy" if all_healthy else "degraded",
        version="0.1.0",
        services=services,
        timestamp=datetime.utcnow()
    )


# Knowledge Endpoints
@app.post("/api/v1/knowledge", response_model=KnowledgeResponse, status_code=status.HTTP_201_CREATED)
async def create_knowledge(knowledge: KnowledgeCreate, db: Session = Depends(get_db)):
    """Create a new knowledge entry."""
    service = KnowledgeService(db)
    try:
        return service.create(knowledge)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create knowledge: {str(e)}"
        )


@app.get("/api/v1/knowledge/{entry_id}", response_model=KnowledgeResponse)
async def get_knowledge(entry_id: str, db: Session = Depends(get_db)):
    """Get a knowledge entry by ID."""
    service = KnowledgeService(db)
    result = service.get_by_id(entry_id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Knowledge entry with ID {entry_id} not found"
        )
    
    return result


@app.put("/api/v1/knowledge/{entry_id}", response_model=KnowledgeResponse)
async def update_knowledge(
    entry_id: str,
    update: KnowledgeUpdate,
    db: Session = Depends(get_db)
):
    """Update a knowledge entry."""
    service = KnowledgeService(db)
    result = service.update(entry_id, update)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Knowledge entry with ID {entry_id} not found"
        )
    
    return result


@app.delete("/api/v1/knowledge/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_knowledge(entry_id: str, db: Session = Depends(get_db)):
    """Delete a knowledge entry."""
    service = KnowledgeService(db)
    success = service.delete(entry_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Knowledge entry with ID {entry_id} not found"
        )


@app.post("/api/v1/knowledge/search", response_model=List[dict])
async def search_knowledge(query: SearchQuery, db: Session = Depends(get_db)):
    """Search for knowledge entries."""
    service = KnowledgeService(db)
    results = service.search(
        query=query.query,
        mode=query.mode,
        filters=query.filters,
        limit=query.limit,
        offset=query.offset
    )
    return results


@app.get("/api/v1/knowledge/{entry_id}/relations")
async def get_knowledge_relations(entry_id: str, db: Session = Depends(get_db)):
    """Get relations for a knowledge entry."""
    service = KnowledgeService(db)
    
    # Verify entry exists
    if not service.get_by_id(entry_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Knowledge entry with ID {entry_id} not found"
        )
    
    relations = service.get_relations(entry_id)
    return {"entry_id": entry_id, "relations": relations}


@app.post("/api/v1/knowledge/relations")
async def create_knowledge_relation(
    source_id: str,
    target_id: str,
    relation_type: str,
    weight: float = 1.0,
    db: Session = Depends(get_db)
):
    """Create a relation between two knowledge entries."""
    service = KnowledgeService(db)
    
    try:
        relation = service.create_relation(
            source_id=source_id,
            target_id=target_id,
            relation_type=relation_type,
            weight=weight
        )
        return relation
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create relation: {str(e)}"
        )


# Agent Query Endpoint
@app.post("/api/v1/agent/query", response_model=AgentResponse)
async def agent_query(agent_query: AgentQuery, db: Session = Depends(get_db)):
    """
    Natural language query endpoint for AI Agents.
    
    This endpoint accepts a natural language question and returns:
    - A synthesized answer
    - Source knowledge entries
    - Confidence score
    - Follow-up questions
    - Related topics
    """
    service = KnowledgeService(db)
    
    # Search for relevant knowledge
    search_results = service.search(
        query=agent_query.question,
        mode="hybrid",
        limit=agent_query.max_results
    )
    
    if not search_results:
        return AgentResponse(
            answer="I couldn't find relevant information in the knowledge base to answer your question.",
            sources=[],
            confidence=0.0,
            follow_up_questions=["Could you rephrase your question?", "What specific aspect are you interested in?"],
            related_topics=[]
        )
    
    # Extract top results
    top_results = search_results[:min(5, len(search_results))]
    sources = [result["knowledge"] for result in top_results]
    
    # Calculate average confidence
    avg_confidence = sum(result["score"] for result in top_results) / len(top_results)
    
    # Generate simple answer (in production, this would use an LLM)
    context_parts = []
    for i, result in enumerate(top_results, 1):
        kb = result["knowledge"]
        context_parts.append(f"[{i}] {kb.title}: {kb.content[:200]}...")
    
    answer = f"Based on {len(sources)} relevant knowledge entries:\n\n" + "\n\n".join(context_parts)
    
    # Extract related topics from metadata and tags
    related_topics = set()
    for source in sources:
        if source.tags:
            related_topics.update(source.tags[:3])
        if source.metadata and "domain" in source.metadata:
            related_topics.add(source.metadata["domain"])
    
    # Generate follow-up questions
    follow_ups = []
    if sources:
        first_title = sources[0].title
        follow_ups = [
            f"Tell me more about {first_title}",
            "How does this relate to other concepts?",
            "What are the practical applications?"
        ]
    
    return AgentResponse(
        answer=answer,
        sources=sources,
        confidence=min(avg_confidence, 1.0),
        follow_up_questions=follow_ups,
        related_topics=list(related_topics)[:10]
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
