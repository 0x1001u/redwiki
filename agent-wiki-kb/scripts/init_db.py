#!/usr/bin/env python3
"""Database initialization script."""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.database import init_db, engine, Base
from src.services.qdrant_service import qdrant_service
from src.services.neo4j_service import neo4j_service


def main():
    """Initialize all databases and services."""
    print("Initializing Agent Wiki KB databases...")
    
    # Initialize PostgreSQL
    print("\n1. Initializing PostgreSQL...")
    try:
        init_db()
        print("   ✓ PostgreSQL tables created successfully")
    except Exception as e:
        print(f"   ✗ PostgreSQL initialization failed: {e}")
        return False
    
    # Initialize Qdrant
    print("\n2. Initializing Qdrant vector database...")
    try:
        collection_created = qdrant_service.ensure_collection()
        if collection_created:
            print("   ✓ Qdrant collection created successfully")
        else:
            print("   ✓ Qdrant collection already exists")
    except Exception as e:
        print(f"   ✗ Qdrant initialization failed: {e}")
        return False
    
    # Initialize Neo4j
    print("\n3. Initializing Neo4j graph database...")
    try:
        if neo4j_service.health_check():
            print("   ✓ Neo4j connection successful")
        else:
            print("   ✗ Neo4j connection failed")
            return False
    except Exception as e:
        print(f"   ✗ Neo4j initialization failed: {e}")
        return False
    
    print("\n" + "="*50)
    print("✓ All databases initialized successfully!")
    print("="*50)
    print("\nNext steps:")
    print("1. Start the API server: uvicorn src.api.main:app --reload")
    print("2. Access API docs: http://localhost:8000/docs")
    print("3. Create your first knowledge entry via POST /api/v1/knowledge")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
